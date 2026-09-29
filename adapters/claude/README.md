# Claude Code Adapter

Wires this kit into Claude Code without copying the operating docs. Claude Code
reads `CLAUDE.md`, not the kit's root `AGENTS.md`, so a thin `CLAUDE.md` imports
the router and adds only what is Claude-specific.

## Files

| File | Goes to | Role |
|---|---|---|
| `CLAUDE.md.template` | project root `CLAUDE.md`, or `~/.claude/CLAUDE.md` for all projects | imports the router, sets paths and working style |
| `agents/worker.md` | `.claude/agents/` or `~/.claude/agents/` | example bounded worker sub-agent with a fixed model and effort |
| `settings.hooks.json` | merge into `.claude/settings.json` or `~/.claude/settings.json` | runs `tools/docs_hook.py` after edits |

## Setup

1. Copy the kit as usual (router `AGENTS.md`, `docs/`, `tools/`).
2. Copy `CLAUDE.md.template` to `CLAUDE.md` and replace `<KIT_DIR>` with the
   folder that holds the kit's `AGENTS.md`. In a project root use `AGENTS.md`
   directly (`@AGENTS.md`).
3. Optional: copy `agents/worker.md` and adjust `model` / `effort`.
4. Merge `settings.hooks.json` into your settings. For a global install, replace
   `$CLAUDE_PROJECT_DIR` with the absolute kit folder.
5. Run `python3 tools/check_docs.py --extra <path to CLAUDE.md>` and confirm
   `RESULT: PASS`.

## Global Install Notes

If you keep one kit folder for all projects (`~/.claude/CLAUDE.md` imports it):

- Router lines such as "read `docs/STATE.md`" refer to the kit folder, not the
  current project. Tell Claude that project work uses the project's own state
  file, and keep project rules in the project (`CLAUDE.md` or
  `.claude/rules/`).
- Claude Code reads a folder's `AGENTS.md` only when no `CLAUDE.md` exists
  there. In a repo shared with Codex, keep `AGENTS.md` canonical and add a
  `CLAUDE.md` that starts with `@AGENTS.md` only when Claude needs extras.
- Pass `CLAUDE.md` and agent files to the checker with `--extra` so they stay
  under the 3KB cap.
