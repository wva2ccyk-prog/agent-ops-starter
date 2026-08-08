#!/usr/bin/env python3
"""Monthly integrity check for the starter kit docs. Read-only.

Cross-platform twin of ``check_docs.ps1``. By default it fails on resolver rows
that do not resolve, duplicate names/paths, unresolved ``doc:`` tokens, a
missing router, and active Markdown files under ``docs/`` that are absent from
the resolver. ``--allow-orphans`` is an explicit migration escape hatch that
downgrades only the orphan condition to WARN.

Run:       python3 tools/check_docs.py
Migration: python3 tools/check_docs.py --allow-orphans
Self-test: python3 tools/check_docs.py --self-test
"""
from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path

ROW_RE = re.compile(r"^([A-Z0-9_]+)\|([^|]+)\|(.+)$")
DOC_TOKEN_RE = re.compile(r"doc:([A-Z0-9_]+)")
ROUTER_MAX_BYTES = 4 * 1024
DOC_MAX_BYTES = 15 * 1024


def parse_rows(map_text: str) -> list[tuple[str, str, str]]:
    rows = []
    for line in map_text.splitlines():
        match = ROW_RE.match(line.strip())
        if match:
            rows.append((match.group(1), match.group(2).strip(), match.group(3).strip()))
    return rows


def check(root: Path, *, allow_orphans: bool = False) -> tuple[list[str], list[str], int, int]:
    errors: list[str] = []
    warnings: list[str] = []

    router = root / "AGENTS.md"
    if not router.is_file():
        errors.append("AGENTS.md missing")

    map_path = root / "docs" / "RETRIEVAL_MAP.md"
    if not map_path.is_file():
        return errors + ["docs/RETRIEVAL_MAP.md missing"], warnings, 0, 0

    rows = parse_rows(map_path.read_text(encoding="utf-8", errors="replace"))
    if not rows:
        errors.append("no resolver rows found in RETRIEVAL_MAP.md")

    seen_name: set[str] = set()
    seen_path: set[str] = set()
    for name, rel, _role in rows:
        if not (root / rel).is_file():
            errors.append(f"resolver row points to missing file: {name} -> {rel}")
        if name in seen_name:
            errors.append(f"duplicate NAME: {name}")
        seen_name.add(name)
        if rel in seen_path:
            errors.append(f"duplicate path: {rel}")
        seen_path.add(rel)

    docs_root = root / "docs"
    doc_files = sorted(p for p in docs_root.rglob("*.md") if p.is_file()) if docs_root.is_dir() else []
    for path in doc_files:
        rel = path.relative_to(root).as_posix()
        if rel not in seen_path:
            message = f"orphan doc (not in resolver): {rel}"
            (warnings if allow_orphans else errors).append(message)

    for path in ([router] if router.is_file() else []) + doc_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in DOC_TOKEN_RE.finditer(text):
            token = match.group(1)
            if token not in seen_name:
                errors.append(f"unresolved doc token doc:{token} in {path.name}")

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


def run(root: Path, *, allow_orphans: bool = False) -> int:
    errors, warnings, row_count, doc_count = check(root, allow_orphans=allow_orphans)
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARN: {item}")
    print(f"rows={row_count} docs={doc_count} errors={len(errors)} warnings={len(warnings)}")
    print("orphan_mode=" + ("migration-warning" if allow_orphans else "strict-error"))
    if errors:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


def make_broken_fixture(root: Path) -> None:
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


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_broken_fixture(root)
        errors, warnings, _, _ = check(root)
        joined = " | ".join(errors + warnings)
        migration_errors, migration_warnings, _, _ = check(root, allow_orphans=True)
        migration_joined = " | ".join(migration_errors + migration_warnings)
        expectations = {
            "missing file": "missing file: GONE" in joined,
            "duplicate NAME": "duplicate NAME: REAL" in joined,
            "duplicate path": "duplicate path: docs/REAL.md" in joined,
            "unresolved doc token": "unresolved doc token doc:GHOST" in joined,
            "strict orphan error": any("ORPHAN.md" in item for item in errors),
            "migration orphan warning": any("ORPHAN.md" in item for item in migration_warnings)
            and not any("ORPHAN.md" in item for item in migration_errors),
            "mode preserves other errors": "missing file: GONE" in migration_joined,
        }
        for label, fired in expectations.items():
            print(f"  [{'OK' if fired else 'MISS'}] {label}")
        missed = [key for key, hit in expectations.items() if not hit]
        print(f"self_test_checks={len(expectations)} missed={len(missed)}")
        print("SELF-TEST: " + ("PASS" if not missed else "FAIL"))
        return 0 if not missed else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--allow-orphans", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    return run(Path(args.root).resolve(), allow_orphans=args.allow_orphans)


if __name__ == "__main__":
    raise SystemExit(main())
