# Operating Principles

Core rules for keeping this system alive long-term. Read when doing rule,
maintenance, or system work — not for ordinary tasks.

## Intake Gate (before adding any rule or doc)

A new prose rule requires one of: an observed failure, a measured gap, or a
user decision it encodes. "Seems useful" does not qualify.

Before writing it, ask in order:

1. Can this be a **script or check** instead? (strongest instrument)
2. Can this be a **required field in a template** instead? (medium)
3. Only then write prose (weakest — models follow prose least reliably).

New docs must be registered in `doc:RETRIEVAL_MAP` or they do not exist.
Keep state (things that change) and rules (things that don't) in separate
files — mixed files go stale as a whole.

Task-specific guidance gets its own registered doc, loaded on its trigger.
Never fold it into a doc that unrelated work already reads: a tool endpoint or
domain rule buried in a general doc is paid for on every turn that opens it.

## Diet Protocol (removing rules/docs without the keep-all/delete-all failure)

Models are poorly calibrated at absolute "is this important?" judgments.
Never ask for binary keep/delete over a corpus. Instead:

1. **Rank, don't judge**: list candidates least-valuable-first, each with one
   citable signal (never used, duplicated elsewhere, stale date, no reference
   from the resolver or any doc). No signal, no candidacy.
2. **Quota**: at most 10 items per pass. Repeat later rather than purging once.
3. **Propose and apply separately**: the ranked list goes to the user for
   approval before anything is deleted.
4. **Archive by default** (move out of the active path); hard delete is the
   exception.

## Unattended Runs

Any scheduled/automated model run is proposal-only: it writes findings and
suggestions to files; it never edits rules, state, or the resolver. Canonical
edits happen only in a session the user is watching.

## Memory Consolidation

Raw work logs stay out of the read path. Periodically distill them into
`doc:MEMORY_LEDGER` entries (reusable lessons) and `doc:STATE` (current
snapshot), then archive the raw material. Do not let the ledger become a
diary — one entry per lesson, delete entries that stop being true.

## Escalate To The User

Money/billing; deleting or overwriting pre-existing work; sending private data
to any external service; public-facing actions; changing rules in `docs/`;
contradictory evidence you cannot resolve. Everything else inside an assigned
task: decide and proceed.

## Done Means Stop

If the monthly check passes and nothing measurably changed, do not "improve"
the system. Unprompted refactors of rules are drift, not progress.
