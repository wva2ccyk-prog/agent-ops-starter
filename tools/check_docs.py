#!/usr/bin/env python3
"""Monthly integrity check for the starter kit docs. Read-only.

Cross-platform twin of `check_docs.ps1` (same checks, same output shape), so
macOS/Linux users do not have to port it themselves.

FAIL on: resolver rows that don't resolve, duplicate names/paths, unresolved
`doc:` tokens. WARN only: orphan docs, size budgets.

Run:  python3 tools/check_docs.py
Self-test (proves the checks actually fire):
      python3 tools/check_docs.py --self-test
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

ROW_RE = re.compile(r"^([A-Z0-9_]+)\|([^|]+)\|(.+)$")
DOC_TOKEN_RE = re.compile(r"doc:([A-Z0-9_]+)")
ROUTER_MAX_BYTES = 4 * 1024
DOC_MAX_BYTES = 15 * 1024


def parse_rows(map_text):
    """Return (name, relative_path, role) for each resolver table row."""
    rows = []
    for line in map_text.splitlines():
        match = ROW_RE.match(line.strip())
        if match:
            rows.append((match.group(1), match.group(2).strip(), match.group(3).strip()))
    return rows


def check(root):
    errors = []
    warnings = []

    map_path = root / "docs" / "RETRIEVAL_MAP.md"
    if not map_path.is_file():
        return ["docs/RETRIEVAL_MAP.md missing"], [], 0, 0

    rows = parse_rows(map_path.read_text(encoding="utf-8", errors="replace"))
    if not rows:
        errors.append("no resolver rows found in RETRIEVAL_MAP.md")

    seen_name = set()
    seen_path = set()
    for name, rel, _role in rows:
        if not (root / rel).is_file():
            errors.append("resolver row points to missing file: %s -> %s" % (name, rel))
        if name in seen_name:
            errors.append("duplicate NAME: %s" % name)
        seen_name.add(name)
        if rel in seen_path:
            errors.append("duplicate path: %s" % rel)
        seen_path.add(rel)

    doc_files = sorted(p for p in (root / "docs").rglob("*.md") if p.is_file())
    for path in doc_files:
        rel = path.relative_to(root).as_posix()
        if rel not in seen_path:
            warnings.append("orphan doc (not in resolver): %s" % rel)

    router = root / "AGENTS.md"
    for path in ([router] if router.is_file() else []) + doc_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in DOC_TOKEN_RE.finditer(text):
            token = match.group(1)
            if token not in seen_name:
                errors.append("unresolved doc token doc:%s in %s" % (token, path.name))

    if router.is_file() and router.stat().st_size > ROUTER_MAX_BYTES:
        warnings.append(
            "AGENTS.md over 4KB (%.1fKB) - it should route, not legislate"
            % (router.stat().st_size / 1024)
        )
    for path in doc_files:
        if path.stat().st_size > DOC_MAX_BYTES:
            warnings.append(
                "doc over 15KB: %s (%.1fKB) - split or diet"
                % (path.name, path.stat().st_size / 1024)
            )

    return errors, warnings, len(rows), len(doc_files)


def run(root):
    errors, warnings, row_count, doc_count = check(root)
    for item in errors:
        print("ERROR: %s" % item)
    for item in warnings:
        print("WARN: %s" % item)
    print(
        "rows=%d docs=%d errors=%d warnings=%d"
        % (row_count, doc_count, len(errors), len(warnings))
    )
    if errors:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


def self_test():
    """Build a deliberately broken kit in a temp dir; confirm each check fires."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "docs").mkdir()
        (root / "AGENTS.md").write_text("router. see doc:GHOST\n", encoding="utf-8")
        (root / "docs" / "REAL.md").write_text("real doc\n", encoding="utf-8")
        (root / "docs" / "ORPHAN.md").write_text("not registered\n", encoding="utf-8")
        (root / "docs" / "RETRIEVAL_MAP.md").write_text(
            "REAL|docs/REAL.md|a real row\n"
            "GONE|docs/MISSING.md|points at nothing\n"
            "REAL|docs/OTHER.md|duplicate name\n"
            "OTHER|docs/REAL.md|duplicate path\n"
            "RETRIEVAL_MAP|docs/RETRIEVAL_MAP.md|this resolver\n",
            encoding="utf-8",
        )
        errors, warnings, _, _ = check(root)
        joined = " | ".join(errors + warnings)
        expectations = {
            "missing file": "missing file: GONE" in joined,
            "duplicate NAME": "duplicate NAME: REAL" in joined,
            "duplicate path": "duplicate path: docs/REAL.md" in joined,
            "unresolved doc token": "unresolved doc token doc:GHOST" in joined,
            "orphan doc": "orphan doc" in joined and "ORPHAN.md" in joined,
        }
        for label, fired in expectations.items():
            print("  [%s] %s" % ("OK" if fired else "MISS", label))
        missed = [k for k, v in expectations.items() if not v]
        print("self_test_checks=%d missed=%d" % (len(expectations), len(missed)))
        print("SELF-TEST: " + ("PASS" if not missed else "FAIL"))
        return 0 if not missed else 1


def main():
    if "--self-test" in sys.argv[1:]:
        return self_test()
    return run(Path(__file__).resolve().parent.parent)


if __name__ == "__main__":
    raise SystemExit(main())
