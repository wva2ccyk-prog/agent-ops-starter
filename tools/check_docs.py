#!/usr/bin/env python3
"""Monthly integrity check for the starter kit docs. Read-only.

Cross-platform twin of ``check_docs.ps1``. By default it fails on malformed
resolver-table rows, resolver rows that escape the active ``docs/`` corpus or
do not resolve to files, duplicate names/paths, unresolved ``doc:`` tokens, a
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
from pathlib import Path, PurePosixPath

ROW_RE = re.compile(r"^([A-Z0-9_]+)\|([^|]+)\|([^|]+)$")
DOC_TOKEN_RE = re.compile(r"doc:([A-Z0-9_]+)")
DRIVE_RE = re.compile(r"^[A-Za-z]:")
ROUTER_MAX_BYTES = 4 * 1024
DOC_MAX_BYTES = 15 * 1024
RESOLVER_TABLE_HEADING = "## Resolver Table"


def parse_resolver_table(map_text: str) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Parse only the resolver table and report malformed nonblank table rows."""
    rows: list[tuple[str, str, str]] = []
    errors: list[str] = []
    in_table = False
    saw_table = False
    for line_no, raw in enumerate(map_text.splitlines(), 1):
        line = raw.strip()
        if line == RESOLVER_TABLE_HEADING:
            in_table = True
            saw_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if not in_table or not line:
            continue
        match = ROW_RE.fullmatch(line)
        if not match:
            errors.append(f"malformed resolver row at line {line_no}: {line}")
            continue
        name, rel, role = match.group(1), match.group(2).strip(), match.group(3).strip()
        if not rel or not role:
            errors.append(f"malformed resolver row at line {line_no}: {line}")
            continue
        rows.append((name, rel, role))
    if not saw_table:
        errors.append(f"resolver table heading missing: {RESOLVER_TABLE_HEADING}")
    return rows, errors


def parse_rows(map_text: str) -> list[tuple[str, str, str]]:
    """Compatibility helper returning only valid resolver-table rows."""
    return parse_resolver_table(map_text)[0]


def normalize_resolver_path(rel: str) -> str | None:
    """Return a canonical docs-local path, or None when the row can escape."""
    normalized = rel.strip().replace("\\", "/")
    if not normalized or normalized.startswith("/") or DRIVE_RE.match(normalized):
        return None
    parts = PurePosixPath(normalized).parts
    if ".." in parts or not parts or parts[0] != "docs":
        return None
    canonical = PurePosixPath(*[part for part in parts if part not in ("", ".")]).as_posix()
    if not canonical.startswith("docs/"):
        return None
    return canonical


def check(root: Path, *, allow_orphans: bool = False) -> tuple[list[str], list[str], int, int]:
    errors: list[str] = []
    warnings: list[str] = []

    router = root / "AGENTS.md"
    if not router.is_file():
        errors.append("AGENTS.md missing")

    map_path = root / "docs" / "RETRIEVAL_MAP.md"
    if not map_path.is_file():
        return errors + ["docs/RETRIEVAL_MAP.md missing"], warnings, 0, 0

    rows, parse_errors = parse_resolver_table(map_path.read_text(encoding="utf-8", errors="replace"))
    errors.extend(parse_errors)
    if not rows:
        errors.append("no resolver rows found in RETRIEVAL_MAP.md")

    seen_name: set[str] = set()
    seen_path: set[str] = set()
    for name, rel, _role in rows:
        safe_rel = normalize_resolver_path(rel)
        if safe_rel is None:
            errors.append(f"unsafe resolver path (must stay under docs/): {name} -> {rel}")
        elif not (root / safe_rel).is_file():
            errors.append(f"resolver row points to missing file: {name} -> {safe_rel}")

        if name in seen_name:
            errors.append(f"duplicate NAME: {name}")
        seen_name.add(name)

        path_key = safe_rel if safe_rel is not None else rel.replace("\\", "/")
        if path_key in seen_path:
            errors.append(f"duplicate path: {path_key}")
        seen_path.add(path_key)

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


def make_broken_fixture(root: Path, outside: Path) -> None:
    (root / "docs").mkdir()
    (root / "docs" / "DIR_TARGET").mkdir()
    (root / "AGENTS.md").write_text("router. see doc:GHOST\n", encoding="utf-8")
    (root / "docs" / "REAL.md").write_text("real doc\n", encoding="utf-8")
    (root / "docs" / "ORPHAN.md").write_text("not registered\n", encoding="utf-8")
    outside.write_text("outside active corpus\n", encoding="utf-8")
    (root / "docs" / "RETRIEVAL_MAP.md").write_text(
        "# Retrieval Map\n\n"
        "## Resolver Table\n"
        "REAL|docs/REAL.md|a real row\n"
        "GONE|docs/MISSING.md|points at nothing\n"
        "REAL|docs/OTHER.md|duplicate name\n"
        "OTHER|docs/REAL.md|duplicate path\n"
        "DIRECTORY|docs/DIR_TARGET|directory is not a file target\n"
        "ESCAPE|../outside.md|existing file outside repository\n"
        f"ABSOLUTE|{outside.resolve().as_posix()}|existing absolute file outside repository\n"
        "DRIVE|C:\\absolute\\outside.md|drive-root path\n"
        "BROKEN_TOO_FEW|docs/REAL.md\n"
        "BROKEN_TOO_MANY|docs/REAL.md|role|extra\n"
        "RETRIEVAL_MAP|docs/RETRIEVAL_MAP.md|this resolver\n\n"
        "## Rules For This File\n",
        encoding="utf-8",
    )


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        root = sandbox / "repo"
        root.mkdir()
        outside = sandbox / "outside.md"
        make_broken_fixture(root, outside)
        errors, warnings, _, _ = check(root)
        joined = " | ".join(errors + warnings)
        migration_errors, migration_warnings, _, _ = check(root, allow_orphans=True)
        migration_joined = " | ".join(migration_errors + migration_warnings)
        expectations = {
            "missing file": "missing file: GONE" in joined,
            "directory target": "missing file: DIRECTORY" in joined,
            "malformed too few": "malformed resolver row" in joined and "BROKEN_TOO_FEW" in joined,
            "malformed too many": "malformed resolver row" in joined and "BROKEN_TOO_MANY" in joined,
            "duplicate NAME": "duplicate NAME: REAL" in joined,
            "duplicate path": "duplicate path: docs/REAL.md" in joined,
            "unresolved doc token": "unresolved doc token doc:GHOST" in joined,
            "strict orphan error": any("ORPHAN.md" in item for item in errors),
            "migration orphan warning": any("ORPHAN.md" in item for item in migration_warnings)
            and not any("ORPHAN.md" in item for item in migration_errors),
            "mode preserves other errors": "missing file: GONE" in migration_joined
            and "BROKEN_TOO_FEW" in migration_joined,
            "reject parent escape": "unsafe resolver path" in joined and "ESCAPE -> ../outside.md" in joined,
            "reject absolute path": "unsafe resolver path" in joined and "ABSOLUTE ->" in joined,
            "reject drive-root path": "unsafe resolver path" in joined and "DRIVE -> C:" in joined,
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
