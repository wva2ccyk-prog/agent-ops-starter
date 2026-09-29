# Session Handoff

Create or resume a handoff so a new session (another account, machine, or a
fresh context) continues without reading the old chat. Read only when the user
asks to leave or resume a handoff.

## Where It Lives

One new file per handoff, named `YYYYMMDD-HHMM-<task-slug>.md`, filed by scope
so no single folder collects everything:

- Project work: the project's own `handoffs/` folder (or its existing handoff
  location). When the handoff must reach another machine, commit it with the
  project's work.
- Work not tied to a project (only when this kit is installed globally): the
  kit folder's `handoffs/`.

Never write a project's handoff into another project or the global folder.
Keep `handoffs/` outside `docs/`: handoffs are not active operating docs.

## Create

Write the handoff, return its path, and stop. Do not continue the task.

Include, compact English, under 8KB:

- task name and approved scope
- current stage and completed checkpoints
- evidence paths (accepted; rejected or superseded)
- uncommitted changes and anything half-applied
- exact next command or first file to inspect
- forbidden scope expansions and stop conditions
- blockers and open questions
- continuity: reply language, tone, and recent user corrections that must
  survive the move

A handoff is incomplete if the next session would need the user to re-explain
scope, tone, or return conditions.

## Resume

1. Pick the file: the path the user gives, else the newest file (by name) in
   the current project's `handoffs/`, else the newest in the global folder.
2. Read only that file first. Do not read old chats or other handoffs. Open
   only the files the next action needs.
3. If it is stale, contradictory, or missing a path it depends on, report the
   exact gap and stop.
4. Otherwise confirm in one short status (current task, approved scope, next
   action, stop conditions) and continue within the approved scope.
