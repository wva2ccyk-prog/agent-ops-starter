# Retrieval Map

Single resolver for active operating docs under `docs/`. Cross-doc pointers use
`doc:<NAME>`; resolve the NAME here, then open only that file. Register each new
active Markdown doc under `docs/` with one row. Root or nested `AGENTS.md` files
and Skills use their own loading mechanisms and are outside this resolver.

Row format: NAME|relative/path.md|one-line role

## Resolver Table

OPERATING_PRINCIPLES|docs/OPERATING_PRINCIPLES.md|core rules: intake gate, diet protocol, boundaries
STATE|docs/STATE.md|current-work snapshot; resume context
MEMORY_LEDGER|docs/MEMORY_LEDGER.md|reusable lessons only
HANDOFF_TEMPLATE|docs/HANDOFF_TEMPLATE.md|task instruction template for bounded work
SESSION_HANDOFF|docs/SESSION_HANDOFF.md|leave/resume a session handoff; dated files filed per project
CODEX_WORKERS|docs/CODEX_WORKERS.md|explicit Codex worker selection and separate-session dispatch
CODEX_WAITING|docs/CODEX_WAITING.md|completion-aware Codex waits and optional shell-job notifications
EXTERNAL_WORKERS|docs/EXTERNAL_WORKERS.md|Claude-led external workers (GPT/Codex, agy, GPT Pro): rules, registry, choosing a model, packets, acceptance
WORKER_CODEX|docs/WORKER_CODEX.md|Codex (GPT) worker and reviewer commands when Claude leads; Windows forms
WORKER_AGY|docs/WORKER_AGY.md|agy (Gemini Neon) commands: high for research and reading, xhigh for second opinions
WORKER_GPTPRO|docs/WORKER_GPTPRO.md|GPT Pro (user-run in ChatGPT): prompts, unit delivery spec, profiles, unit check and adoption
PROJECTS|docs/PROJECTS.md|when work becomes a project: spine (projects/<name>), placement, resume order, common working rules
RETRIEVAL_MAP|docs/RETRIEVAL_MAP.md|this resolver

## Rules For This File

- Pointer rows only. Never paste content, history, or summaries here.
- One NAME → one file. No duplicate names, no duplicate paths.
- When a doc moves, change only its row; other docs keep the same NAME token.
