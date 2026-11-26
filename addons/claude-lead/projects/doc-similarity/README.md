# Document similarity analysis (example project)

Purpose: find similar documents in a large set of public-institution documents and report which ones are similar,
how, and how sure we are. This is a filled example of `projects/_template/`; adjust it to the real job.

Runtime: <RUNTIME_DIR>/DocSimilarity/   (extracted text, scores, tables, reports; originals stay where they are)
Repo: none

## Read order

1. `STATE.md` (current position)
2. `DECISIONS.md` (active decisions)
3. `SECURITY.md` before anything leaves this computer
4. `WORKFLOW.md` for the step being worked on
5. newest file in `handoffs/active/`

## Project docs

- `WORKFLOW.md`: steps 1–7, who does each step, packets and table columns
- `SECURITY.md`: checklist for sending institution documents to any AI service (Korean, for the user too)

## Project rules (override `doc:PROJECTS` common rules where they differ)

- Document contents go to an external model only after `SECURITY.md` is passed for that batch.
- Pair scoring over the whole set is done by a local script, never by asking a model to read every pair.
- A run is accepted only after counting, per source file, what the output does not cover.
