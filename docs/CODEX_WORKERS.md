# Codex Workers

Personal reusable defaults for explicitly requested Codex worker work. Read only
on that trigger; this is not a default workflow for ordinary tasks or other CLIs.

## Authorization And Selection

The user chooses sub-agent versus separate-session execution. Do not switch modes
or start either merely because it would help. One request authorizes one worker;
multiple workers require explicit plural/parallel/team language. Rule maintenance
or discussion of workers does not authorize dispatch.

| Initial route | Model / effort | Assigned work |
| --- | --- | --- |
| Default | `gpt-5.6-luna` / `max` | Bounded implementation or investigation with clear scope and verifiable completion |
| Context | `gpt-5.6-terra` / `xhigh` | Finding the correct change boundary across modules, interfaces, dependencies, or unfamiliar repository context |

Difficulty alone does not select Terra. Keep unresolved requirements, architecture,
authority, and high-consequence decisions with the assigning task. Other models
require explicit user naming; preserve requested effort. Check supported settings
in the current environment rather than assuming availability on a new computer.
Unavailable models or failed work do not authorize substitution, automatic upward
escalation, or changing an existing task's model. Report the cause and proposed
change for user direction. Repair an unclear packet within the approved scope.

## Shared Packet

Use `doc:HANDOFF_TEMPLATE`; include exact working root, owned files or subsystem,
needed context, acceptance checks, result path, and completion/blocker conditions.
Do not assume a fresh worker inherits conversation history or local instructions.
Include a ban on re-delegation unless the user explicitly authorizes it. Preserve
others' changes and serialize overlapping edits. A parallel-work request alone
does not authorize nested delegation.

Reuse accessible valid verification rather than repeating it. Review decisive
results and integration effects; a worker's self-report is not acceptance.

## Internal Sub-Agents

Use the available collaboration tools and selected model/effort. Where supported,
use a self-contained packet with no history fork or only necessary recent turns;
do not accidentally inherit the parent's expensive model through a full fork.
Follow the current tool schema. Keep tightly coupled work and final integration
with the assigning task.

## Separate Sessions

1. Add the exact return task ID/host and one result-file path to the packet.
   Use observable identities, not model names or approximate title matches.
2. Reuse a user-designated or registered execution task only when its settings and
   scope match. Do not overwrite a control-task route or silently change settings.
   New-session requests authorize creation using the selected model and current
   app project/environment rules; an existing-task transfer does not authorize
   creating a replacement. Ask only for missing identity/settings decisions.
3. Send the packet once through available task tools. If the environment lacks
   them, return the ready-to-paste packet for manual use. For CLI queue delivery,
   verify local `codex queue --help` first and pass arguments safely. An uncertain
   send must be resolved before retrying; never duplicate an active assignment.
4. Report dispatched versus completed accurately. Perform any tool-required
   startup check, then end the dispatch turn without repeated progress polling
   unless the user asks to wait. Do not create a recurring monitor.
5. Instruct the worker to write the result and send one concise completion message
   to the exact return task: outcome, artifact path, decisive checks, and blockers.
   This return is authorized only for the assigned work. If messaging is unavailable,
   leave the artifact for manual retrieval and report the delivery limitation.
6. Receiving the result permits reviewing the assigned result, not launching a
   new job, automatic retries, or changing project policy. Keep project coordination
   in that project rather than making a global control task its standing supervisor.

## Local State

Keep session IDs, host IDs, settings evidence, delivery status, packets, and results
in a machine/project-local runtime location outside the starter's active `docs/`.
Do not commit live routing state, personal absolute paths, or credentials into the
starter. Configure exact task routes explicitly on each new computer; do not
discover or register unrelated tasks automatically. Requested settings alone do
not prove the worker's effective runtime settings.
