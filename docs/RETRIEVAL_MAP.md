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
RETRIEVAL_MAP|docs/RETRIEVAL_MAP.md|this resolver

## Rules For This File

- Pointer rows only. Never paste content, history, or summaries here.
- One NAME → one file. No duplicate names, no duplicate paths.
- When a doc moves, change only its row; other docs keep the same NAME token.
