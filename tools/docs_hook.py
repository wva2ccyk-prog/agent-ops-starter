#!/usr/bin/env python3
"""Post-tool-use size check for edits to this kit's operating rules.

The hook accepts Codex or Claude Code JSON on stdin. Unknown or malformed
payloads trigger a check, so an unrecognized tool cannot silently bypass it.
Repeat --extra for always-loaded files outside docs/ that also need a 3KB cap.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def watched_file(value: str, extras: set[Path]) -> bool:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve()
    return path == ROOT / "AGENTS.md" or path in extras or path == ROOT / "docs" or (ROOT / "docs") in path.parents


def should_check(event: object, extras: set[Path]) -> bool:
    if not isinstance(event, dict):
        return True
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return True
    for key in ("file_path", "notebook_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return watched_file(value, extras)
    command = tool_input.get("command")
    if isinstance(command, str):
        # Shell and patch commands: check only when the text names a rules path,
        # so ordinary project commands do not repeat near-cap warnings.
        markers = ["AGENTS.md", "docs/", "docs\\"] + [path.name for path in extras]
        return any(marker in command for marker in markers)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extra", action="append", default=[], metavar="FILE")
    args = parser.parse_args()
    extras = {Path(value).expanduser().resolve() for value in args.extra}
    try:
        event = json.load(sys.stdin)
    except (ValueError, UnicodeError):
        event = None
    if not should_check(event, extras):
        return 0

    command = [sys.executable, str(ROOT / "tools" / "check_docs.py"), "--root", str(ROOT)]
    for path in sorted(extras):
        command.extend(("--extra", str(path)))
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0 or "WARN:" in result.stdout:
        sys.stderr.write("Docs check after this edit:\n")
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
