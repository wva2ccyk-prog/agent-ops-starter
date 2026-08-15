# Codex Activation Plane experiment

This is a **Codex-specific experiment**, intentionally outside `docs/` and outside the starter's default read path. It does not change `AGENTS.md`, the retrieval map, or any default behavior merely by existing in this repository.

The goal is to test one narrow idea: keep the starter's canonical files small and lazy-loaded, but use Codex lifecycle hooks to wake the right pointer before the model has a chance to miss it.

## What it does

`UserPromptSubmit` runs one local, deterministic router. It never injects rule bodies. It emits only turn-scoped `doc:NAME` references such as `doc:OPERATING_PRINCIPLES` or `doc:STATE`, which the existing starter router can resolve normally.

The same process records only **approval categories** for the current turn. It does not store raw prompts or chat summaries.

`PreToolUse` inspects high-consequence tool actions (external writes, destructive commands, spending, and private-data egress). If the matching category was not explicitly authorized by the user in the same turn, the hook returns `deny` with a short reason. If it was authorized, the hook is silent; it never returns `allow`, so Codex's native sandbox and permission policy remain in force.

This uses `deny` rather than `ask` because current Codex source exposes an `ask` enum in the schema but rejects `PreToolUse permissionDecision:ask` in the runtime output parser.

## Why this is not a default starter feature

The starter is intentionally CLI-neutral and minimal. Adding Codex-specific hooks globally without a measured rule-miss would violate its own Intake Gate. This folder is therefore a runnable candidate for evaluation, not standing policy.

## Test

```bash
python experiments/codex-activation-plane/activation_router.py --self-test \
  --rules experiments/codex-activation-plane/activation_rules.json \
  --fixtures experiments/codex-activation-plane/activation_fixtures.json
```

No third-party dependencies or network access are required.

## Trial install in Codex

1. Copy `activation_router.py`, `activation_rules.json`, and `activation_fixtures.json` to `$CODEX_HOME/hooks/`.
2. Adapt `hooks.json.example` to `$CODEX_HOME/hooks.json`. On Windows, replace `%USERPROFILE%` with the actual profile path if the hook runner does not expand it in quoted command text.
3. Start Codex and review/trust the hook if Codex asks.
4. Run the self-test before relying on it.
5. Start in observation mode by keeping the guard rules but exercising only the fixtures; promote new triggers only after a real miss or measured gap.

## Design constraints

- Activation metadata is **not authority**. Canonical docs win.
- One hook command handles all prompt matching; Codex's UserPromptSubmit matcher is not used as a semantic router.
- No raw prompt logging.
- No model call in the hot path.
- No automatic `allow` decisions.
- Runtime/config errors fail open to the existing Codex policy; the hook is not a sandbox and must not be treated as one.
- Every trigger or guard change should arrive with at least one positive and one negative fixture.
