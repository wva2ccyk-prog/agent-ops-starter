# Codex (GPT) worker

Command reference for `codex-worker` and `codex-reviewer` when Claude is the lead (`doc:EXTERNAL_WORKERS` holds
authorization, registry, sessions, packets and acceptance). Provider: OpenAI. Using Codex on its own needs none of
this: Codex reads the kit's root `AGENTS.md` (`doc:CODEX_WORKERS` covers Codex's own sub-agents).

## Setup check (once per computer)

- `codex --version` runs from the shell Claude uses, and the account is signed in.
- A one-line `codex exec -m gpt-6.2-sol` succeeds (and `gpt-6.2-astra` if you use it). A model that fails is reported,
  not replaced.
- Note the shell: on Windows, Claude Code's Bash tool usually runs Git Bash, so the bash forms below work there;
  the PowerShell forms are for a PowerShell terminal.

## Commands

- Models: `gpt-6.2-sol` by default; `gpt-6.2-astra` only when the user names it. Effort: high for doing the work,
  xhigh for review (`doc:EXTERNAL_WORKERS` Choosing a model).
- Office use: Codex is the worker that works directly on files: spreadsheet cleanup and conversion (it writes and
  runs small Python scripts), batch renaming and merging, extracting tables from many files. Name the input files
  and the output file; ask it to keep originals untouched.
- Worker: `codex exec -m <model> -c model_reasoning_effort=<effort> -s <sandbox> -C <dir> --skip-git-repo-check
  -o <result.md> - < <packet.md>`
- Pass the packet on stdin from a file as above, not as an argument: a background `exec` with an open stdin waits
  forever on "Reading additional input from stdin".
- Sandbox: `workspace-write` by default; `danger-full-access` only when the user chooses it. A sandbox can block
  `.git` writes, localhost and some system calls; a worker that needs them reports a blocker.
- Workers leave the originals and any git state untouched; the lead reviews and keeps or commits the result.
- In `## Checks` also say "nothing else": these models verify widely unless told not to.
- Start the packet with `This thread is a work thread. Read this packet first and execute now.`
- Always pass `-m`, `-c model_reasoning_effort` and `-s` as the user named them; never rely on a config default.
- Redirect stdout/stderr to `log.txt` beside the result. Its header lines (`model:`, `sandbox:`, `reasoning effort:`,
  `session id:`) are the evidence of the route; the model's own answer about its settings is not.

## Reviewer

- The same command with the reviewer's model and effort. The first review starts a fresh session, never the
  author's. Delta rounds resume the reviewer's session. Do not loop reviews on your own.
- Effort guide: medium for surveys, high for tracing one cause, xhigh for several interacting causes; the user's word
  decides.

## Resume

- `codex exec resume --skip-git-repo-check -m <model> -c model_reasoning_effort=<effort>
  -c sandbox_mode='"<sandbox>"' <session id> - < <prompt.md>` from the original directory.
- Resume does not inherit model, sandbox or extra dirs: pass them again and check the log header every time.
- Never resume under another model or a lower effort: start fresh with the packet and the partial outputs.

## Long runs

- Start detached so the run survives the Claude session, and give the Bash call a timeout of 15 minutes or more.
- Git Bash: `nohup codex exec ... - < packet.md > log.txt 2>&1 &` then `echo $!` for the PID.
- PowerShell: `$p = Start-Process codex -ArgumentList 'exec','-m','<model>',... ,'-' -RedirectStandardInput packet.md
  -RedirectStandardOutput log.txt -RedirectStandardError err.txt -NoNewWindow -PassThru; $p.Id`.
- Check it by PID only: Git Bash `kill -0 <pid>`; PowerShell `Get-Process -Id <pid>`. Watch the log for
  `out of credits`, `could not be refreshed`, `sign in again`, not for a bare `ERROR` or `401`.
- Credits or sign-in failure: record the restart checkpoint (`doc:EXTERNAL_WORKERS`), tell the user and wait. Account
  switching is the user's action.
