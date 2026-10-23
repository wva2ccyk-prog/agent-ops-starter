# Session Handoff

Create or resume a handoff so a new session (another account, machine, or a
fresh context) continues without reading the old chat. Read only when the user
asks to leave or resume a handoff.

## Where It Lives

One new file per handoff, named `YYYYMMDD-HHMM-<task-slug>.md`, filed by scope
so no single folder collects everything:

- Project work: the project's own `handoffs/` folder (or its existing handoff
  location). When the handoff must reach another machine, commit it with the
  project's work. Keep current files in `handoffs/active/`; move superseded
  files to `handoffs/done/` (30-day Diet candidates under
  `doc:OPERATING_PRINCIPLES`). Existing equivalent locations may be reused.
- Work not tied to a project (only when this kit is installed globally): the
  kit folder's `handoffs/`.

Never write a project's handoff into another project or the global folder.
Keep `handoffs/` outside `docs/`: handoffs are not active operating docs.

## Create

Write the handoff, return its path, and stop. Do not continue the task.

First update project STATE so its goal, progress, and next action stand
alone. STATE plus the project's fixed, checkable list (milestone exits,
requirements/acceptance, or runbook) is the source of truth. The handoff is only
the session delta; do not duplicate the goal map or standing rules. For long
work without such a list, record an open risk.

Count prior handoffs for the current milestone, active and done. If this would
be the third or later and the milestone is still open, do not write another:
tell the owner in two lines what keeps it open and ask whether direction holds.
Use recorded counts and exact milestone references; missing count evidence is
a gap to report, never a reason to reset the count.

Open with ★ purpose: the end state this work serves (not only the next task),
in the owner's words when available. Follow with Premises (1–3 assumptions the
plan rests on) and Rethink signals (evidence the direction is wrong → stop and
ask the owner).

Include, compact English, under 8KB:

- project STATE and fixed-list paths, current milestone ID, handoff number
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

1. Pick the provided path, else the newest file by name in the project's
   `handoffs/active/` (or existing current location), else the global folder.
2. Read project STATE and its fixed checkable list, then the handoff. No
   project: the handoff alone. Do not read old chats or done handoffs. Open
   only files needed for the premise check and next action.
3. Place the next action on STATE's current milestone. STATE and canonical
   project docs win over the handoff. If stale, contradictory, serving no open
   milestone, or missing a required path, report the exact gap and stop.
4. Check Premises against STATE, the repo, and newer evidence. If a premise
   fails, a Rethink signal is visible, or either field is absent, report it in
   two lines and ask the owner before continuing. Do not repair direction
   silently. For long work, a missing fixed list remains an open risk.
5. Otherwise confirm in Korean and continue within the approved scope:

```text
핸드오프 확인.
- 목표: (최종 상태)
- 진행 위치: (현재 / 남은 마일스톤 / 이 마일스톤 핸드오프 N번째)
- 전제 확인: (유지 / 깨짐 → 멈춤)
- 현재 작업:
- 승인 범위:
- 다음 작업:
- 멈출 조건:
바로 진행합니다.
```
