# agy (Gemini Neon) worker

Command reference for `agy-neon` when Claude is the lead (`doc:EXTERNAL_WORKERS` holds the rules, registry and model
choice). Provider: Google. Using agy on its own needs none of this: agy reads the kit's router through its own entry
file (`adapters/agy/`).

## Setup check (once per computer)

- `agy --version` runs from the shell Claude uses, and `agy models` lists `gemini-4-neon-high` and
  `gemini-4-neon-xhigh`.
- One short read-only call with each succeeds. A model that fails is reported to the user, not replaced.

## Commands

- Run from the working folder; add other needed folders with `--add-dir`.
- Always pass the model with `--model`; a CLI default does not decide the model.
- Read-only research, reading or summary, answer on stdout:
  `agy --model gemini-4-neon-high --mode plan --sandbox --print-timeout 40m -p "$(cat packet.md)" > result.md 2> log.txt`
  (web research works in this mode).
- Work that edits files: `--mode accept-edits --sandbox`, own copy of the files, the packet names the allowed files.
  No mode flag is NOT read-only: it can run shell commands and read other files. Give exact, existing input paths.
  `--dangerously-skip-permissions` only when the user asks.
- With `--mode accept-edits` it can also run shell commands (git included): the packet says whether it may.
- Set `--print-timeout` to fit the task (default 5m) and a matching Bash timeout.
- Check a running agy by PID only (Git Bash `kill -0 <pid>`; PowerShell `Get-Process -Id <pid>`). A process listing
  can show its servers' arguments, including keys: never paste process listings.

## Neon high: reading and research

A wide reader that gathers; the lead judges.
- Web research (prices, trends, products, versions). Links are often bare home pages and some claims are wrong:
  verify every claim that drives a decision.
- Long-document reading: summaries and exact quotes from long PDFs, minutes, manuals, logs.
- Images: what a scanned page, chart or table image shows.
- Fixed-criterion cross-checks: "list every place document A states X and what document B says about X".
- First drafts of prose (notices, summaries, emails); the lead checks facts and tone.
- Phrase every task as a list or table to fill, not an open question ("anything wrong?").

## Neon xhigh: second opinion

- Consults on a plan or a draft's logic, checking a list of findings, long careful reading: `--mode plan --sandbox`,
  ask for plain file paths and a length limit, verify each claim that drives a decision.
- Second review beside GPT on important work, or the reviewer when GPT is unavailable and the user agrees; it misses
  some findings the main reviewer finds.
- Never the only approval of a final deliverable.
