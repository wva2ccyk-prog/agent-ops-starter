---
name: chatgpt-collaboration
description: Use when the user asks Codex to collaborate with ChatGPT, GPT Thinking High, or GPT Pro through the Codex in-app browser. Codex remains the final planner, local operator, and acceptance authority.
---

# ChatGPT Collaboration

Use the Codex in-app browser. Do not substitute an external browser relay.

## Start

1. Open ChatGPT in the in-app browser.
2. Select the ChatGPT project that best matches the task. Use a normal new chat
   only when no project is relevant.
3. Create a clean chat instead of reusing an unrelated or context-heavy chat.
4. Name it `YYYY-MM-DD | concise task summary`.
5. Use Thinking High for normal collaboration. Use Pro only for broad,
   high-value review or when the user explicitly requests it.
6. Never spend Pro capacity on a route smoke test.

If the requested project or model cannot be verified, stop before sending and
report the boundary instead of silently choosing another route.

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
