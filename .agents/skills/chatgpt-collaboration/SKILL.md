---
name: chatgpt-collaboration
description: Use when the user asks Codex to collaborate with ChatGPT, GPT Thinking High, or GPT Pro through the Codex in-app browser. Codex remains the final planner, local operator, and acceptance authority.
---

# ChatGPT Collaboration

Use the Codex in-app browser. Do not substitute an external browser relay
(a CDP bridge, a standalone Playwright runner, or a browser-automation CLI). If
the in-app browser is unavailable, report that boundary instead of installing a
relay to work around it.

## Start

1. Open ChatGPT in the in-app browser. Prefer claiming an already-open
   `https://chatgpt.com/` tab over opening a duplicate. From a cold state, with
   no tabs open, opening a new tab works and the login session persists, so never
   ask the user to open the browser first.
2. Select the ChatGPT project that best matches the task. Use a normal new chat
   only when no project is relevant.
3. Create a clean chat instead of reusing an unrelated or context-heavy chat.
4. Name it `YYYY-MM-DD | concise task summary`.
5. Use Thinking High for normal collaboration. Use Pro only for broad,
   high-value review or when the user explicitly requests it.
6. Never spend Pro capacity on a route smoke test.

If the requested project or model cannot be verified, stop before sending and
report the boundary instead of silently choosing another route.

The composer's model control is a button labeled with the current tier, not a
model name. Labels are localized: for example, English uses `High`, `Extra
High`, and `Pro`, while the Korean UI uses `높음`, `매우 높음`, and `Pro`. A
loose match can select the wrong tier, so match the visible label exactly.
Confirm the checked item before sending, then confirm the tier the answer itself
reports; an unconfirmed tier is not evidence for the requested one.

## Send

For a small self-contained question, send a compact prompt directly.

For broad review, multi-file analysis, or project-direction work, create and
upload one curated ZIP packet containing:

- `00_READ_ME_FIRST.md`: goal, context, review questions, authority split,
  privacy boundary, and required output;
- a manifest of included and excluded files, with hashes when exact inputs
  affect acceptance;
- the implementation, project authority documents, roadmap, and evidence
  actually needed for the review.

Exclude caches, dependencies, duplicate outputs, credentials, browser profiles,
unrelated history, and raw private data. Upload private files only when the user
has explicitly authorized those files and ChatGPT as the destination.

Record the conversation URL (`https://chatgpt.com/c/<id>`) right after sending.
It is the durable handle for the consult: reopening it recovers the finished
answer even after the tab closes or the automation session resets.

## Wait

A long answer can run for tens of minutes, and you do not need to estimate how
long. Block on the completion signal rather than sampling on a timer:

- the latest assistant turn's copy action becoming visible (for example,
  `Copy response` or `응답 복사`) is the completion signal;
- streaming hides the composer buttons, so their absence means "still working";
- waiting sends nothing to ChatGPT, so a slow run costs local calls, not
  subscription capacity.

Do not use a sentinel token, growing text, or network-request completion as the
finish test. Each one fires while generation is still in progress. Read the
finished answer from the rendered response text; a copy-to-clipboard button may
be a signal only and not actually populate the clipboard.

Past roughly twenty minutes, stop holding the session open. Persist the
conversation URL, sleep until later, then reopen the URL and check the signal
once. Never resend a prompt because generation is slow.

`scripts/poll.md` has the runnable version for the Codex in-app browser: a
blocking wait helper, call budgets, recovery by URL, and the measurements behind
each rejected approach. Read it when actually waiting on a long run.

## Resolve

After each response, identify unresolved claims, missing evidence, and material
differences. Send one compact follow-up focused on those differences. Continue
until no material disagreement remains.

Do not force cosmetic consensus. Stop and surface a residual issue when it
requires user judgment, depends on unavailable evidence, or repeats without new
evidence. Codex records the final decision and remains responsible for local
edits and validation.

Wait quietly while ChatGPT is working. Do not emit repetitive heartbeat or
elapsed-time updates, and do not resend merely because generation is slow.

For decision-grade work, save the final ChatGPT response beside the packet
before Codex reduces and applies it.
