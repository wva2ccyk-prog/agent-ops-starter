# APPLY: instructions for the Claude that installs this pack

You (Claude, usually Opus) are adapting this pack to the user's own computer and work. It came from another person's
setup (coding-heavy, macOS); the user here works on Windows, does office work, and already has Claude Code, Codex (GPT)
and agy (Gemini). Judge what fits; perfection is not expected. Report in Korean, briefly.

## What this pack is

An add-on to `agent-ops-starter` (router, STATE, handoffs, docs checker). It adds one thing: Claude as the lead
calling GPT, agy and GPT Pro when the user asks ("GPT 불러서 시켜"). Using GPT or agy on their own keeps working
through the starter's router.

Paths below are relative to `addons/claude-lead/`. Installing copies them into the kit folder (`<KIT_DIR>`, where
the starter's root `AGENTS.md`, `docs/` and `tools/` go), merging with the starter's folders.

## Required (install these)

| Item | Goes to | Adapt |
| --- | --- | --- |
| starter kit (this repository's root) | `<KIT_DIR>` | install first, per the root README |
| `docs/EXTERNAL_WORKERS.md`, `WORKER_CODEX.md`, `WORKER_AGY.md`, `WORKER_GPTPRO.md`, `PROJECTS.md` | `<KIT_DIR>/docs/` | keep rules; adjust examples to the user's work |
| `docs/RETRIEVAL_MAP.md` | replaces the starter's | keep rows for every doc you install, remove rows for docs you skip |
| `adapters/claude/CLAUDE.md.template` | `~/.claude/CLAUDE.md` | fill `<KIT_DIR>`, `<RUNTIME_DIR>`; keep under 3KB |
| `adapters/claude/agents/*.md` | `~/.claude/agents/` | check each `model:` id exists for this account |
| `projects/_template/` | `<KIT_DIR>/projects/` | as is |

## Optional (only if the user wants it)

- `projects/doc-similarity/`: example project for the user's current task (similarity analysis of a large set of
  public-institution documents). Fill its `STATE.md` open decisions with the user before any work.
- `adapters/claude/settings.windows.example.json`: docs-check hook and a finish beep; merge into `~/.claude/settings.json`.
- `adapters/agy/AGENTS.md.template`: lets agy alone follow the same router; find where this agy version reads global
  instructions.
- `optional/ORCHESTRATION.md` (lead dispatches to several workers), `optional/REVIEW_GATES.md` (review standards,
  coding-oriented), `optional/GPTPRO_CODE_REPOS.md` + `optional/tools/gptpro_units.py` (GPT Pro on Git repos). To adopt
  one: move it into `docs/`, add a RETRIEVAL_MAP row, add a trigger line to `CLAUDE.md`.

## Check on this computer

1. `codex --version`; one short `codex exec -m gpt-6.2-sol` call. `agy models` shows `gemini-4-neon-high` and
   `gemini-4-neon-xhigh`; one short call. A model that fails: tell the user, do not substitute.
2. Which shell Claude Code's Bash tool uses (Git Bash or PowerShell); keep the matching command forms in
   `WORKER_CODEX.md` and `WORKER_AGY.md`, drop the others if you like.
3. Hook command: `python`, `py -3` or `python3`, whichever runs here.
4. In `<KIT_DIR>`: `python tools/check_docs.py --extra ~/.claude/CLAUDE.md` → `RESULT: PASS`.

## Keep as is (these came from real failures)

- External workers only when the user names one; worker named without a model → propose the recommended one in one
  line and wait for OK; never swap models silently; the author never reviews its own work.
- Before the first send of any file to GPT, agy or GPT Pro, name the file and service and get the user's OK.
  Institution documents: follow `projects/doc-similarity/SECURITY.md` and the institution's own AI policy.
- Worker output is input: check it against the source before calling it done.

## Free to change

Model recommendation table examples, wording, paths, which optional parts to install, and anything coding-specific
that does not help this user.
