# Starter Architecture Audit — Verified Recommendation

## Baseline

Source: `wva2ccyk-prog/agent-ops-starter@9256ad2372f3770bd16697827646dae192e3980c`.

Actual inspected sizes:

- always-read `AGENTS.md`: 1,273 bytes
- one-level `docs/RETRIEVAL_MAP.md`: 884 bytes
- resume path (`AGENTS.md` + `STATE.md`): 1,782 bytes
- maintenance path (`AGENTS.md` + `OPERATING_PRINCIPLES.md`): 3,980 bytes

The default architecture is already near the clean-sheet result: one thin router, one direct resolver, one current snapshot, one reusable memory ledger, one handoff template, and deterministic checks. Production-scale governance would add concepts before it solves a demonstrated Starter problem.

## Frozen verdict

`MINOR CHANGE`: preserve the read path and improve only deterministic integrity checking. Optional scoped maps remain a future escape hatch, not the default.

## Implemented change

Both checker implementations now:

- fail when `AGENTS.md` or `docs/RETRIEVAL_MAP.md` is missing;
- fail on missing resolver targets, duplicate names, duplicate paths, and unresolved `doc:` tokens;
- **fail by default** when an active Markdown file under `docs/` is absent from the resolver;
- accept an explicit migration-only orphan downgrade (`--allow-orphans` or `-AllowOrphans`);
- report row/doc/error/warning counts and the active orphan mode;
- carry a self-test proving that strict mode catches an orphan and migration mode downgrades only that condition.

No startup document, resolver row, state format, memory format, or handoff format changed.

## Scaling simulation

`starter_scaling_sweep.csv` varies 1/3/5/10/20 projects and 5/10/20/30/50/100 active docs per project under a declared synthetic row-size model. The current single resolver remains the default for one project. Scoped routing becomes an optional escape hatch only after several unrelated project scopes make one flat map materially larger than the local target set.

This is a sizing model, not evidence that public users currently need sharding.

## Verification

- Python checker compile: PASS.
- Python checker self-test: PASS, seven expected detections.
- Clean five-row Starter fixture: PASS in strict mode.
- Added unregistered `docs/ORPHAN.md`: strict mode FAIL, migration mode PASS with one warning.
- PowerShell static sanity: PASS for balanced delimiters and here-string markers.
- PowerShell runtime execution: NOT RUN because `pwsh`/Windows PowerShell was unavailable in the audit container.

## Recommendation

Review and merge this checker-only Draft PR if the default contract is intentional: active docs must be reachable. Do not transfer Production project managers, review-session topology, provider routing, handoff registries, task-lane maps, conversation-memory subsystems, or private runtime paths into Starter core.
