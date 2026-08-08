# Starter Architecture Verdict — Frozen Before Implementation

- Frozen analysis source: `wva2ccyk-prog/Codex@bac8ac11770074de94ec8a3373cd3d9480f00b11`
- Starter source inspected: `wva2ccyk-prog/agent-ops-starter@9256ad2372f3770bd16697827646dae192e3980c`
- This file was committed before any Starter implementation change.
- Repository bytes are measured. Token counts use 4 bytes/token. Workload/error assumptions are sensitivity inputs, not production telemetry.
- Implementation may falsify this verdict, but any contradiction must be recorded separately rather than editing the frozen decision.

## Verdict

**MINOR CHANGE**

## Winning architecture

Keep the current one-level, file-based Starter architecture and everyday read path. Improve only deterministic integrity checking and documentation precision. Treat scoped/multi-project resolver sharding as an optional future escape hatch, not default core.

## Why this wins

- `AGENTS.md` is only 1,273 bytes and is the sole always-read file.
- The one-level resolver is 884 bytes.
- Resume is approximately 1,782 bytes; rule/maintenance work is approximately 3,980 bytes.
- Ordinary bounded work does not pay for state, memory, handoff, or principles.
- A clean-sheet design converges on the same small pieces: thin router, current snapshot, one-level lookup, bounded handoff, and deterministic checks.
- Production's long-lived Project Thread, review-session topology, provider routes, global resolver, and private runtime paths solve Production-scale problems and would be pure concept tax here.

## Change now

- Make an unregistered active Markdown file under `docs/` a deterministic error by default.
- Provide an explicit migration escape hatch that downgrades only orphan findings to warnings.
- Keep Python and PowerShell checkers behaviorally aligned.
- Strengthen self-tests so the checker proves missing core files, duplicate resolver names/paths, broken resolver paths, and orphan behavior.
- Clarify the README without changing the ordinary read path.

## Do not change now

- Do not add project PM sessions, disposable-review governance, provider routing, task lanes, global tokens, vector memory, project registries, daemons, databases, or automatic multi-agent machinery.
- Do not split the resolver for single-project users.
- Do not copy Production-specific operator relay rules or workstation paths.
- Do not add recurring manual synchronization beyond the existing retrieval-map row.

## Expected effect

- Zero change to normal bootstrap bytes, hops, and concepts.
- Better recovery because an orphaned active file cannot silently fall outside retrieval.
- Small checker-LOC increase; no new runtime service.

## Major risks

- Users may keep intentional drafts under `docs/`; the explicit escape hatch must cover migration without weakening the default contract.
- Python and PowerShell parity can drift without executing both self-tests in CI or periodic review.
- Strictness may expose existing orphan files in customized downstream copies; that is a migration signal, not a reason to keep silent failure as the default.

## Confidence

**0.91** that the core should remain unchanged and the checker-only change is the smallest useful winner.

## Unknowns

- Future users with many unrelated projects may eventually need scoped maps.
- PowerShell runtime parity depends on an environment with `pwsh` or Windows PowerShell.
- Public users' draft-storage habits are not telemetry-backed.

# Transfer Matrix — Frozen

| Production finding/change | Production decision | Starter classification | Reason |
| --- | --- | --- | --- |
| Thin canonical L0 router | Keep | TRANSFER TO CORE | Starter already implements it. |
| Explicit read-set precedence | Keep | TRANSFER TO CORE | Avoids needless map reads. |
| Deterministic exact-candidate checker | Add | TRANSFER TO CORE | Executable evidence beats prose compliance. |
| Compact handoff rather than transcript replay | Keep | TRANSFER TO CORE | Starter already has the right-sized template. |
| Scoped direct manifests | Pilot where co-read is measured | OPTIONAL ESCAPE HATCH | Useful only after unrelated scopes make one map materially costly. |
| Resolver sharding | Scale-dependent | OPTIONAL ESCAPE HATCH | Current 884-byte map is far below a demonstrated threshold. |
| Selector budgets | Add in Production | OPTIONAL ESCAPE HATCH | Starter has no nested selector tree today. |
| Long-lived Project Thread as PM | Keep in Production | EXAMPLE ONLY | Advanced multi-project pattern, not default Starter machinery. |
| Disposable gate review session | Keep in Production | EXAMPLE ONLY | Useful governance example, not core. |
| Prompt assets are non-authoritative | Enforce in Production | EXAMPLE ONLY | Keep the principle; do not add a prompt library. |
| Standing Global Main | Narrow in Production | PRODUCTION ONLY | Starter has no global control-plane problem. |
| Model/provider routing tables | Keep only where operationally required | PRODUCTION ONLY | Breaks model-independent minimalism. |
| Project registry | Reject as new Production component | REJECT | Adds concept and synchronization tax without demonstrated need. |
| Vector/RAG memory | Reject absent stronger evidence | REJECT | Staleness, authority, deletion, and audit costs exceed shown benefit. |
| Database/daemon agent framework | Reject | REJECT | Turns the Starter into an infrastructure project. |

# Freeze Attestation

No Starter source, documentation, checker, or default-branch file had been changed on this branch when this verdict was committed. The branch existed only as a pointer to `master` before this file.
