# Projects

When work turns into a project: where records go, how to resume, and the working rules every project shares. Read
when the user starts long work, names a project, or file placement is unclear. Not needed for one-off tasks.

## Classify at intake

- One-off: bounded task; output in `<RUNTIME_DIR>/<task>/`, report in chat.
- Project: long work needing state and decisions to resume. Promote a one-off at 5 handoffs, 30 days, a resume that
  needs state plus decisions, or the user's word.

## Where things go

- Project records: `projects/<name>/` in this kit folder, copied from `projects/_template/`.
- Files, scripts, output and scratch: `<RUNTIME_DIR>/<Name>/`. Originals stay where they are.
- Secrets never go in either place; refer to them by environment variable name or file path only.

## Project spine (`projects/<name>/`)

- `README.md` (4KB): purpose; `Runtime:` path; read order; project docs; project rules that override this file.
- `STATE.md` (6KB): overwrite the current snapshot. `Goal` (2–4 lines in the user's words, with the real task the
  result serves); `Progress` (milestone map, one line each: done/now/next/later); `Now`; `Next`; `Open decisions`;
  `Watch out`; `Last updated`. It must stand alone; no history.
- `DECISIONS.md` (10KB): still-active user decisions, one line each: date / decision / pointer. Replaced lines move to
  `archive/` without a pointer.
- `handoffs/active/`: newest 1–2 notes; older ones in `handoffs/done/` (`doc:SESSION_HANDOFF`).
- Working docs (a workflow, a checklist) may sit beside these when README lists them; each under 10KB, current only.
  Example: `projects/doc-similarity/`.
- The goal in STATE is the user's: quote it, never rewrite it without the user's word.

## Resume order

Live facts (files, running jobs) → README → STATE → DECISIONS → newest active handoff. Live reads establish facts;
the user's decisions establish scope. Ask only when intent or direction is unclear.

## Common working rules

- Precedence: the user's newest word > the project's `DECISIONS.md` > this file. Whoever finds a conflict fixes the
  older text and notes it in STATE.
- Build against something real: connect a source, tool or file format only when a real one is at hand; one small real
  run right after the first working slice, before polishing.
- Accepting a run: first count the source items the output does not cover; then a check by someone other than the
  author. The lead's own sample is not acceptance.
- Large files: search first and read only the needed ranges; tail logs, never read them whole.
- Long waits (workers, long runs): start them detached and check back at least hourly by PID and log errors.
- User away: take the lead's recommended option, record it in STATE `Open decisions` as `lead pick (date)`; it becomes
  a decision only when the user confirms.
- Worker credits or quota run out: tell the user and wait; never move the work to another worker silently.
- Spending, sending private data, installs and public actions need the user unless the project's `DECISIONS.md`
  records a standing permission.
- When the user says to remember something, ask whether it belongs in a rule doc or the project's DECISIONS or STATE,
  and write it there.
