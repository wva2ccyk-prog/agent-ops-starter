#!/usr/bin/env python3
"""Re-verify a GPT Pro run delivered as units (doc:WORKER_GPTPRO "Unit delivery").

Reads every `units/<id>/evidence.json` from the run's index branch, then per unit:
  static  base == pin, head is the branch tip and descends from base, changed files == declared files,
          protected globs untouched, UI files only when the profile lets Pro write UI, size, deploy impact listed
  tests   declared tests fail on base (unit's test files copied in) and pass on head; selections pass on head
  merge   every pair of independent units merges cleanly (git merge-tree)
Prints a Markdown table (exit 1 if any unit fails); `--json` also writes the full result. Nothing is pushed or committed.

  gptpro_units.py check --repo REPO --index origin/reference/RUN-out --folder reference/RUN/out \
      --config CONFIG.json [--units u01,u03] [--static-only] [--json OUT.json] [--tmp DIR]

CONFIG.json (per project):
  {"pin": "<sha>", "protected": ["src/core/payments.py"], "ui_globs": ["static/**"],
   "pro_writes_ui": false, "test_globs": ["tests/**"], "max_changed_lines": 400,
   "runners": {"pytest": "{python} -m pytest -q -p no:cacheprovider {targets}", "node": "node --test {targets}"},
   "fail_codes": {"pytest": [1], "node": [1]}, "vars": {"python": "/abs/.venv/bin/python"},
   "env_set": {"PYTHONPATH": "{wt}/toolkit"}, "env_unset": ["TEST_DATABASE_URL"], "timeout_s": 1800}
  On Windows runners execute through cmd (shell=True): use "C:/abs/.venv/Scripts/python.exe" in vars.
"""
from __future__ import annotations

import argparse
import fnmatch
import itertools
import json
import os
import shlex
import subprocess
import sys
import tempfile

REQUIRED = ["id", "type", "branch", "base", "head", "files", "tests", "impact", "unverified", "owner_decision"]
TYPES = {"defect", "feature", "docs", "spec"}


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r


def match(path, globs):
    return any(fnmatch.fnmatch(path, g) for g in globs)


def load_units(repo, index, folder, only):
    names = git(repo, "ls-tree", "-r", "--name-only", index, f"{folder}/units").stdout.split()
    units = []
    for n in sorted(names):
        if not n.endswith("/evidence.json"):
            continue
        u = json.loads(git(repo, "show", f"{index}:{n}").stdout)
        if not only or u.get("id") in only:
            units.append(u)
    return units


def static_check(repo, u, cfg):
    errs = [f"missing field {k}" for k in REQUIRED if k not in u]
    if errs:
        return errs
    if u["type"] not in TYPES:
        errs.append(f"type {u['type']!r}")
    if u["base"] != cfg["pin"]:
        errs.append("base != pin")
    tip = git(repo, "rev-parse", "--verify", "-q", f"origin/{u['branch']}", check=False).stdout.strip()
    if not tip:
        return errs + ["branch missing on origin"]
    if tip != u["head"]:
        errs.append("head != branch tip")
    if git(repo, "merge-base", "--is-ancestor", u["base"], tip, check=False).returncode:
        errs.append("head does not descend from base")
    changed = set(git(repo, "diff", "--name-only", u["base"], tip).stdout.split())
    declared = set(u["files"])
    if changed != declared:
        errs.append(f"files differ: undeclared {sorted(changed - declared)} unchanged {sorted(declared - changed)}")
    hit = sorted(p for p in changed if match(p, cfg.get("protected", [])))
    if hit:
        errs.append(f"protected touched {hit}")
    ui = sorted(p for p in changed if match(p, cfg.get("ui_globs", [])))
    if ui and not cfg.get("pro_writes_ui", True):
        errs.append(f"UI files written by Pro {ui} (profile: spec + failing test only)")
    lines = 0
    for row in git(repo, "diff", "--numstat", u["base"], tip).stdout.splitlines():
        a, d, _ = row.split("\t", 2)
        lines += int(a) + int(d) if a.isdigit() and d.isdigit() else 0
    if lines > cfg.get("max_changed_lines", 10**9):
        errs.append(f"size {lines} lines > {cfg['max_changed_lines']}")
    if u["type"] in {"defect", "feature"} and not u["tests"]:
        errs.append("no tests declared")
    return errs


def run(cfg, wt, runner, targets):
    tmpl = cfg["runners"][runner]
    vars_ = {**cfg.get("vars", {}), "wt": wt}
    cmd = tmpl.format(**{k: shlex.quote(v) for k, v in vars_.items()},
                      targets=" ".join(shlex.quote(t) for t in targets))
    env = {k: v for k, v in os.environ.items() if k not in set(cfg.get("env_unset", []))}
    env.update({k: v.format(**vars_) for k, v in cfg.get("env_set", {}).items()})
    try:
        r = subprocess.run(cmd, shell=True, cwd=wt, env=env, capture_output=True, text=True,
                           timeout=cfg.get("timeout_s", 1800))
    except subprocess.TimeoutExpired:
        return None, "timeout"
    tail = (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]
    return r.returncode, tail[0][:160]


def test_check(repo, u, cfg, tmp):
    errs, notes = [], []
    base_wt, head_wt = tempfile.mkdtemp(dir=tmp), tempfile.mkdtemp(dir=tmp)
    git(repo, "worktree", "add", "--detach", "-f", base_wt, u["base"])
    git(repo, "worktree", "add", "--detach", "-f", head_wt, u["head"])
    try:
        test_files = [f for f in u["files"] if match(f, cfg.get("test_globs", ["tests/**"]))]
        if test_files:
            git(base_wt, "checkout", u["head"], "--", *test_files)
        for t in u["tests"]:
            fail_codes = cfg.get("fail_codes", {}).get(t["runner"], [1])
            if t.get("expect_before") == "fail":
                rc, tail = run(cfg, base_wt, t["runner"], t["ids"])
                if rc not in fail_codes:
                    errs.append(f"before: expected test failure, rc={rc} ({tail})")
            rc, tail = run(cfg, head_wt, t["runner"], t["ids"])
            if rc != 0:
                errs.append(f"after: rc={rc} ({tail})")
        for s in u.get("selection", []):
            rc, tail = run(cfg, head_wt, s["runner"], s["paths"])
            (notes if rc == 0 else errs).append(f"selection {s['runner']}: rc={rc} ({tail})")
    finally:
        for wt in (base_wt, head_wt):
            git(repo, "worktree", "remove", "--force", wt, check=False)
    return errs, notes


def merge_check(repo, units):
    by_id = {u["id"]: u for u in units}
    out = {}
    for a, b in itertools.combinations(units, 2):
        if b["id"] in a.get("depends_on", []) or a["id"] in b.get("depends_on", []):
            continue
        r = git(repo, "merge-tree", "--write-tree", "--name-only", a["head"], b["head"], check=False)
        if r.returncode:
            files = r.stdout.split("\n\n", 1)[0].splitlines()[1:]
            out.setdefault(a["id"], []).append(f"conflicts with {b['id']} {files}")
            out.setdefault(b["id"], []).append(f"conflicts with {a['id']} {files}")
    missing = {u["id"]: [f"depends_on unknown {d}" for d in u.get("depends_on", []) if d not in by_id] for u in units}
    for k, v in missing.items():
        out.setdefault(k, []).extend(v)
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--repo", required=True)
    c.add_argument("--index", required=True)
    c.add_argument("--folder", required=True)
    c.add_argument("--config", required=True)
    c.add_argument("--units", default="")
    c.add_argument("--static-only", action="store_true")
    c.add_argument("--json")
    c.add_argument("--tmp")
    a = ap.parse_args()
    cfg = json.load(open(a.config))
    git(a.repo, "fetch", "-q", "origin")
    units = load_units(a.repo, a.index, a.folder, set(filter(None, a.units.split(","))))
    if not units:
        sys.exit("no units found")
    merges = merge_check(a.repo, units)
    results = []
    for u in units:
        errs = static_check(a.repo, u, cfg)
        notes = []
        if not errs and not a.static_only:
            e, notes = test_check(a.repo, u, cfg, a.tmp)
            errs += e
        errs += merges.get(u.get("id"), [])
        results.append({"id": u.get("id"), "type": u.get("type"), "severity": u.get("severity", ""),
                        "before_deploy": u.get("before_deploy"), "owner_decision": u.get("owner_decision"),
                        "status": "FAIL" if errs else "PASS", "errors": errs, "notes": notes,
                        "impact": u.get("impact"), "unverified": u.get("unverified")})
    print("| unit | type | sev | before deploy | owner | status | why |\n|---|---|---|---|---|---|---|")
    for r in results:
        why = "; ".join(r["errors"]) or "; ".join(r["notes"])
        print(f"| {r['id']} | {r['type']} | {r['severity']} | {r['before_deploy']} | {r['owner_decision']} "
              f"| {r['status']} | {why} |")
    if a.json:
        json.dump(results, open(a.json, "w"), ensure_ascii=False, indent=2)
    sys.exit(1 if any(r["status"] == "FAIL" for r in results) else 0)


if __name__ == "__main__":
    main()
