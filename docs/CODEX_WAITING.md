# Codex Completion And Waiting

Read for Codex sub-agent waits or long-running shell jobs. This optional workflow
does not authorize delegation, commands, new sessions, or model changes. Preserve
the current runtime's tool schemas and higher-priority communication requirements.

## Native Sub-Agents

Add this reporting requirement to the worker packet: do not send start/progress
messages to the parent; return the result in the final answer. Send an intermediate
parent message only for a blocker or question requiring the parent's decision.
This concerns parent messages, not user-facing updates required by the runtime.

The parent does independent work first, then uses the native completion-aware
wait with an explicit timeout. Use up to 60000 ms when the runtime discourages
longer blocking calls; otherwise choose a longer supported interval appropriate
to the task. Completion can end the wait early: timeout is an upper bound, not
a mandatory delay. Do not replace a completion-aware wait with a fixed sleep.

Do not repeatedly list agents, reread unchanged output, or ask for status. After
a timeout, inspect only evidence needed to distinguish failure from continued
work, then wait again. A timeout alone does not prove a worker is stalled. Required
user updates do not require extra status queries or messages to the worker.

## Long Shell Jobs

For an already-authorized shell job, `tools/run_and_notify.py` can save the result
and queue one completion message to the originating Codex session. It runs the
command directly, without a shell, captures stdout/stderr to files, and saves
`result.json` before attempting notification. It records delivery diagnostics in
`notification.json`. Failed jobs and launch errors also produce a notification
attempt. A failed or ambiguous queue send is not automatically retried.

First run `codex queue --help` in the target environment. Verify delivery on the
actual session/server: CLI support and an accepted queue item alone do not prove
that the receiving session will resume. Use an explicit session UUID or the
launching runtime's `CODEX_THREAD_ID`; never discover a destination by guessing.

```sh
python3 tools/run_and_notify.py --thread <SESSION_UUID> \
  --output-dir /absolute/runtime/unique-job -- <command> <arguments>
```

Choose a new output directory outside the starter's active docs and Git-tracked
content. An existing directory is rejected before launching a job, preventing
accidental reuse. The command inherits the launcher's working directory and
environment; treat its output as private until reviewed. The helper has no job
timeout: use a bounded command with its own termination behavior.

For a long job, detach the helper using the platform's supported process launcher,
redirect its launcher output to Runtime, and preserve its PID/result location.
Once independent parent work ends, end the turn and consume the completion
message when delivered. Read the saved result once; do not replace model polling
with a loop that rereads files. This does not override a runtime requirement to
remain active. If queue delivery cannot be verified, report the limitation and
use a supported native wait or manual result retrieval instead of promising
automatic continuation. No background model or recurring automation is needed.

`codex queue` adds an input to an existing session. It does not by itself manage
native sub-agent lifecycles, start an external job, or guarantee delivery while
the app is closed, in goal mode, or through a different server.

## Minimal Verification

For native workers, run one small authorized worker with no intermediate parent
messages. Confirm a completion-aware wait returns on its final result before the
requested timeout, without repeated status queries. Use the user's chosen model
and effort; a simple delivery test does not establish suitability for larger work.

For the helper, run `python3 tools/test_run_and_notify.py`. Then perform one real
queue smoke test in the target environment and confirm the message is received
and the result read after the parent turn ends. Record job success, queue
acceptance, and actual receipt separately. Do not include machine paths, session
IDs, or raw logs in this portable repository. Reduced polling is observable;
token/quota savings require a separate usage measurement.
