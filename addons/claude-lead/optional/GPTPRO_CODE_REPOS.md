# GPT Pro on code repositories (optional)

Add-on to `docs/WORKER_GPTPRO.md`.

Use this instead of the office run when the job is on a Git repository and ChatGPT has the GitHub connector with
write access.

- Inputs go on a `reference/*` brief branch (local paths and account values replaced by placeholders); the prompt pins
  the exact commit (PIN). Pro reads and writes GitHub directly. No pull requests.
- Run kinds: audit + units; design + units (Pro designs inside a lead-written scope brief that fixes scope, order,
  out-of-scope and constraints, marks extras `optional`); bulk implementation of well-specified units.
- Plan runs per milestone when work is a project (`doc:PROJECTS`): typically one at its start and one at its exit.

### Unit delivery (paste into the prompt's delivery spec)

1. Audit reports and an index on `reference/<run>-out`, folder `reference/<run>/out/`: the requested report files,
   `UNITS.md` (one table: unit, type, severity, before deploy, changed lines, depends_on, evidence result, owner
   decision needed) and per unit `units/<id>/UNIT.md` + `units/<id>/evidence.json`.
2. One branch per unit, `reference/<run>-<id>` (`<id>` = `u01-<slug>`), based on PIN, holding only that unit's change.
   One defect, one feature or one doc change per unit; a unit needing another names it in `depends_on` and is based
   on that unit's branch. Types: `defect`, `feature`, `docs`, `spec` (spec = no product code: behaviour spec + a
   failing test, for areas the profile keeps from Pro).
3. `UNIT.md` fields: user-visible scenario; owner-rule check (every listed rule: touched yes/no + why); files;
   alternatives (only where an owner rule is in tension; at most 2, each with evidence); what it could break; deploy
   impact (schema/migration, env/config, API or stored-data contract, new dependency, prompt, UI, extra model calls or
   latency); rollback; what was not verified (live model, device, host, PostgreSQL, real browser).
4. `evidence.json`: `id, type, severity, before_deploy, branch, base (=PIN), head (unit tip sha), depends_on, files
   (exact changed paths), tests [{runner, ids, expect_before: "fail"}], selection [{runner, paths}], impact,
   unverified, owner_decision`. Every defect/feature test fails on PIN for the stated reason and passes on the unit;
   tests are deterministic, offline, no sleeps. Include the before/after logs and exact commands in the unit folder.
5. A finding without a safe minimal change is reported in the audit only (no unit). Never touch files the profile marks
   protected.

### Profiles (the project names its profile + modifiers once; its values go in a config file)

| Case | Pro writes | Lead side |
|---|---|---|
| Base: code repo with tests | defect / feature / docs units with code + tests | check script, adopt per card |
| + UI owned by Claude | UI work as `spec` units only (spec + failing UI/browser test, no UI code) | lead implements UI from the spec |
| + UI open to Pro | UI code units with DOM/browser tests and a screenshot or render log | lead walks the real UI before merge |
| + weak or no tests | first unit adds characterization tests of current behaviour; later units build on it | adopt the test unit first |
| + frozen or safety areas | no code in protected files; alternatives with evidence; `owner_decision: true` | owner decides from the card |
| + behaviour needs live model / device / host | unit plus an eval or walk script the lead can run; marked unverified | lead runs it before adopting |
| + infra / deploy | checklist and dry-run scripts only; nothing applies changes | lead uses them in the runbook |
| Docs or research only (no code) | doc-change units with a source citation per claim | lead checks citations |

### Verify and adopt

- Treat everything as unverified input. Run `optional/tools/gptpro_units.py check` with the project config: it rejects a unit
  whose base, head or file list disagrees with its evidence, that touches protected or (profile) UI files, whose tests
  do not fail on PIN and pass on the unit, or that conflicts with another independent unit.
- Audit claims without a unit: a narrow factual check by a read-only worker before use.
- Adopt PASS units by their card: one PR per unit (rebased on current main), normal review gate and CI; `feature` and
  `owner_decision` units go to the owner as a short table first. Discard or re-scope FAIL units; fix them with the
  project's implementation worker, never with another Pro run.
