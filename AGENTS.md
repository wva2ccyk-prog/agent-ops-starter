# Router

This file is the only always-loaded doc. It routes; it is not the rulebook.
Do not expand it with policies, history, or project detail.

## First Move

- If the user message or a task file contains `read_set`, explicit paths, or
  "read only", read exactly those first and treat them as the authority for
  the turn.
- For ordinary bounded work, read no docs. Inspect only the files directly
  implicated by the task, then do the work.
- To resume prior work: read `docs/STATE.md`.
- For rule/system/maintenance work: read `docs/OPERATING_PRINCIPLES.md` first.
- To find any other doc: resolve its NAME in `docs/RETRIEVAL_MAP.md`, then open
  only that file. Resolving a name never authorizes opening related docs.

## Defaults

- Keep visible output compact: result, path, blocker. No long narration.
- For build, change, or fix requests, implement after the minimum inspection
  needed for scope and safety. Do not turn routine implementation into a
  separate planning, review, evidence, or validation-infrastructure phase
  unless the task requires it.
- Success needs evidence, not self-report. Run the narrowest relevant checks,
  exercise one representative real flow when practical, and verify
  authoritative readback for important mutations.
- Finished nontrivial work: update `docs/STATE.md` (snapshot, not diary);
  add reusable lessons to `docs/MEMORY_LEDGER.md` only if truly reusable.

## Hard Boundaries (ask the user first)

Spending money; deleting or overwriting things you did not create; sending
private data anywhere; anything public-facing; changing the rules in `docs/`.
Everything else inside the given task: proceed without asking.
