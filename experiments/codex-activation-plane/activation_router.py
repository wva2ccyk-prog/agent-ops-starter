#!/usr/bin/env python3
"""Deterministic Codex activation/enforcement hook.

UserPromptSubmit:
- selects small canonical doc:NAME references from prompt signals
- records only approval categories (never raw prompt text) for the current turn
- injects routing hints, never policy bodies

PreToolUse:
- detects a small set of high-consequence action classes
- if the user did not explicitly authorize the class in the current turn, denies
  the tool call with a short reason so the agent can obtain explicit approval
- if authorized, emits nothing; native Codex permission policy remains in force

No network access and no third-party dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

VERSION = 1
STATE_TTL_SECONDS = 48 * 60 * 60
DEFAULT_MAX_REFS = 4

def _debug(message: str) -> None:
    if os.environ.get("CODEX_ACTIVATION_DEBUG") == "1": print(f"activation-router: {message}", file=sys.stderr)

def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle: return json.load(handle)

def _rules_path() -> Path:
    override = os.environ.get("CODEX_ACTIVATION_RULES")
    return Path(override) if override else Path(__file__).with_name("activation_rules.json")

def _fixtures_path() -> Path: return Path(__file__).with_name("activation_fixtures.json")

def _validate_rules(rules: dict[str, Any]) -> None:
    if int(rules.get("version", 0)) != VERSION: raise ValueError(f"unsupported rules version: {rules.get('version')!r}")
    max_refs = int(rules.get("max_refs", DEFAULT_MAX_REFS))
    if not 1 <= max_refs <= 8: raise ValueError("max_refs must be between 1 and 8")
    approval_categories_defined = {str(r.get("category", "")) for r in rules.get("approval_rules", []) if r.get("category")}
    seen_ids: set[str] = set()
    pattern_keys=("prompt_any","prompt_all","prompt_none","tool_name_any","input_any","input_all","input_none")
    for section in ("activation_rules","approval_rules","guard_rules"):
        for index, rule in enumerate(rules.get(section, [])):
            if not isinstance(rule, dict): raise ValueError(f"{section}[{index}] must be an object")
            rule_id=str(rule.get("id") or f"{section}:{rule.get('category', index)}")
            scoped=f"{section}:{rule_id}"
            if scoped in seen_ids: raise ValueError(f"duplicate rule id: {rule_id}")
            seen_ids.add(scoped)
            for key in pattern_keys:
                for pattern in rule.get(key, []): re.compile(str(pattern), flags=re.IGNORECASE|re.UNICODE)
            if section=="activation_rules":
                refs=list(rule.get("refs", []))
                if not refs or any(not str(ref).startswith("doc:") for ref in refs): raise ValueError(f"activation rule {rule_id} must point only to doc:NAME refs")
            if section=="guard_rules" and str(rule.get("category", "")) not in approval_categories_defined: raise ValueError(f"guard rule {rule_id} uses category without approval rule")

def _compile_any(patterns:list[str], text:str)->bool: return any(re.search(p,text,flags=re.IGNORECASE|re.UNICODE) for p in patterns)

def _matches(rule:dict[str,Any], prompt:str)->bool:
    any_p=rule.get("prompt_any",[]); all_p=rule.get("prompt_all",[]); none_p=rule.get("prompt_none",[])
    if any_p and not _compile_any(any_p,prompt): return False
    if all_p and not all(_compile_any([p],prompt) for p in all_p): return False
    if none_p and _compile_any(none_p,prompt): return False
    return bool(any_p or all_p)

def activation_refs(prompt:str,rules:dict[str,Any])->list[str]:
    hits=[]
    for order,rule in enumerate(rules.get("activation_rules",[])):
        if _matches(rule,prompt): hits.append((int(rule.get("priority",0)),-order,list(rule.get("refs",[]))))
    hits.sort(reverse=True); refs=[]; seen=set(); limit=int(rules.get("max_refs",DEFAULT_MAX_REFS))
    for _,_,candidates in hits:
        for ref in candidates:
            if ref not in seen:
                seen.add(ref); refs.append(ref)
                if len(refs)>=limit: return refs
    return refs

def approval_categories(prompt:str,rules:dict[str,Any])->set[str]:
    return {str(r["category"]) for r in rules.get("approval_rules",[]) if _matches(r,prompt)}

def _serialized_input(value:Any)->str:
    try: return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    except Exception: return str(value)

def _guard_matches(rule:dict[str,Any],tool_name:str,tool_input:Any)->bool:
    names=list(rule.get("tool_name_any",[])); any_p=list(rule.get("input_any",[])); all_p=list(rule.get("input_all",[])); none_p=list(rule.get("input_none",[])); serialized=_serialized_input(tool_input)
    if names and not _compile_any(names,tool_name): return False
    if any_p and not _compile_any(any_p,serialized): return False
    if all_p and not all(_compile_any([p],serialized) for p in all_p): return False
    if none_p and _compile_any(none_p,serialized): return False
    return bool(names or any_p or all_p)

def guard_categories(tool_name:str,tool_input:Any,rules:dict[str,Any])->list[tuple[str,str]]:
    hits=[]
    for order,rule in enumerate(rules.get("guard_rules",[])):
        if _guard_matches(rule,tool_name,tool_input): hits.append((int(rule.get("priority",0)),-order,str(rule["category"]),str(rule.get("id",rule["category"]))))
    hits.sort(reverse=True); result=[]; seen=set()
    for _,_,category,rule_id in hits:
        if category not in seen: seen.add(category); result.append((category,rule_id))
    return result

def _state_root()->Path:
    override=os.environ.get("CODEX_ACTIVATION_STATE_DIR")
    return Path(override) if override else Path(tempfile.gettempdir())/"codex-activation-plane-v1"

def _stable_key(value:Any)->str: return hashlib.sha256(str(value or "missing").encode("utf-8",errors="replace")).hexdigest()[:20]

def _state_path(event:dict[str,Any])->Path: return _state_root()/_stable_key(event.get("session_id") or event.get("sessionId"))/f"{_stable_key(event.get('turn_id') or event.get('turnId'))}.json"

def _prune_state(root:Path)->None:
    if not root.exists(): return
    cutoff=time.time()-STATE_TTL_SECONDS
    try:
        for path in root.rglob("*.json"):
            try:
                if path.stat().st_mtime<cutoff: path.unlink(missing_ok=True)
            except OSError: pass
        for d in sorted((p for p in root.rglob("*") if p.is_dir()),reverse=True):
            try: d.rmdir()
            except OSError: pass
    except OSError: pass

def _write_state(event:dict[str,Any],approved:set[str])->None:
    path=_state_path(event)
    try:
        path.parent.mkdir(parents=True,exist_ok=True); payload={"version":VERSION,"created_at":int(time.time()),"approvals":sorted(approved)}; tmp=path.with_suffix(".tmp"); tmp.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")),encoding="utf-8"); os.replace(tmp,path)
    except OSError as exc: _debug(f"state write failed: {exc}")

def _read_state(event:dict[str,Any])->set[str]:
    try:
        payload=_load_json(_state_path(event))
        if int(payload.get("version",0))!=VERSION or int(payload.get("created_at",0))<time.time()-STATE_TTL_SECONDS: return set()
        return {str(x) for x in payload.get("approvals",[])}
    except (OSError,ValueError,TypeError,json.JSONDecodeError): return set()

def _activation_context(refs:list[str])->str:
    lines=["[ACTIVATION]","Mechanical routing hint only; canonical documents remain authoritative.","Treat these as turn-scoped required_refs and resolve them through the existing router:"]+[f"- {r}" for r in refs]+["[/ACTIVATION]"]
    return "\n".join(lines)

def handle_user_prompt(event:dict[str,Any],rules:dict[str,Any])->dict[str,Any]|None:
    prompt=str(event.get("prompt","")); _write_state(event,approval_categories(prompt,rules)); refs=activation_refs(prompt,rules)
    return {"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":_activation_context(refs)}} if refs else None

def handle_pre_tool(event:dict[str,Any],rules:dict[str,Any])->dict[str,Any]|None:
    tool_name=str(event.get("tool_name") or event.get("toolName") or ""); tool_input=event.get("tool_input",event.get("toolInput",{})); guards=guard_categories(tool_name,tool_input,rules)
    if not guards: return None
    approved=_read_state(event); missing=[(c,r) for c,r in guards if c not in approved]
    if not missing: return None
    categories=", ".join(c for c,_ in missing); rule_ids=", ".join(r for _,r in missing); reason=f"Explicit user authorization is required in the current turn for boundary category: {categories}. Matched guard(s): {rule_ids}. Ask for that authorization, then retry; native Codex permissions still apply."
    return {"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":reason}}

def _dispatch(event:dict[str,Any],rules:dict[str,Any])->dict[str,Any]|None:
    name=str(event.get("hook_event_name") or event.get("hookEventName") or "")
    if name=="UserPromptSubmit": return handle_user_prompt(event,rules)
    if name=="PreToolUse": return handle_pre_tool(event,rules)
    return None

def _self_test(rules:dict[str,Any],fixtures:list[dict[str,Any]])->int:
    failures=[]
    for case in fixtures:
        cid=str(case.get("id","unnamed")); prompt=str(case.get("prompt","")); got_refs=activation_refs(prompt,rules); exp_refs=list(case.get("expected_refs",[]))
        if got_refs!=exp_refs: failures.append(f"{cid}: refs expected={exp_refs!r} got={got_refs!r}")
        got_app=sorted(approval_categories(prompt,rules)); exp_app=sorted(str(x) for x in case.get("expected_approvals",[]))
        if got_app!=exp_app: failures.append(f"{cid}: approvals expected={exp_app!r} got={got_app!r}")
        if "tool_name" in case:
            guards=[c for c,_ in guard_categories(str(case["tool_name"]),case.get("tool_input",{}),rules)]; exp_guards=list(case.get("expected_guards",[]))
            if guards!=exp_guards: failures.append(f"{cid}: guards expected={exp_guards!r} got={guards!r}")
            got_decision="deny" if [c for c in guards if c not in set(got_app)] else "silent"; exp_decision=str(case.get("expected_decision","silent"))
            if got_decision!=exp_decision: failures.append(f"{cid}: decision expected={exp_decision!r} got={got_decision!r}")
    if failures:
        print(f"SELF-TEST FAIL ({len(failures)} failure(s))"); [print(f"- {f}") for f in failures]; return 1
    print(f"SELF-TEST PASS ({len(fixtures)} fixture(s))"); return 0

def main()->int:
    parser=argparse.ArgumentParser(description="Codex activation/enforcement hook"); parser.add_argument("--self-test",action="store_true"); parser.add_argument("--rules",type=Path,default=None); parser.add_argument("--fixtures",type=Path,default=None); args=parser.parse_args(); rules_path=args.rules or _rules_path()
    try: rules=_load_json(rules_path); _validate_rules(rules)
    except Exception as exc:
        if args.self_test: print(f"SELF-TEST FAIL: cannot load rules: {exc}"); return 1
        _debug(f"rules load failed: {exc}"); return 0
    if args.self_test:
        try: fixtures=_load_json(args.fixtures or _fixtures_path())
        except Exception as exc: print(f"SELF-TEST FAIL: cannot load fixtures: {exc}"); return 1
        return _self_test(rules,fixtures)
    _prune_state(_state_root())
    try:
        event=json.load(sys.stdin); output=_dispatch(event,rules)
        if output is not None: json.dump(output,sys.stdout,ensure_ascii=False,separators=(",",":")); sys.stdout.write("\n")
    except Exception as exc: _debug(f"runtime failure: {exc}"); return 0
    return 0

if __name__=="__main__": raise SystemExit(main())
