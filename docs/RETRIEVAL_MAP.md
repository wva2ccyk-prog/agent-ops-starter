# Retrieval Map

Single resolver for doc names. Cross-doc pointers use `doc:<NAME>`; resolve the
NAME here, open only that one file. A doc not listed here does not exist for
the model — register every new doc with one row.

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
