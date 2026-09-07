# Router

This file is the only always-loaded doc. It routes; it is not the rulebook.
Do not expand it with policies, history, or project detail.

## First Move

- If the user message or a task file contains `read_set`, explicit paths, or
  "read only", read exactly those first and treat them as the task-local source
  of truth. They narrow retrieval scope; they do not override current explicit
  user instructions or expand permissions.
- For ordinary bounded work, read no operating docs by default. Inspect only
  the smallest task-relevant set of code, tests, configuration, and project
  documentation needed to complete the work correctly.
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
  authoritative readback for important mutations. A passing check remains valid
  until relevant inputs or state change; do not rerun it merely to reconfirm the
  result or because the task is ending.
- Finished nontrivial work that advances the canonical ongoing thread: update
  `docs/STATE.md` (snapshot, not diary). Bounded or parallel work should report
  continuity information instead unless it was explicitly assigned state
  ownership. Add reusable lessons to `docs/MEMORY_LEDGER.md` only if truly
  reusable.

## Hard Boundaries (ask the user first unless already authorized)

Spending money; destructively deleting or replacing pre-existing user work in a
way that may discard unrelated changes; sending private data to an external
service; taking a public-facing action; changing the operating rules in `docs/`.
Ordinary edits required by the assigned task are not destructive overwrite.
Everything else inside the authorized task: proceed without asking.
