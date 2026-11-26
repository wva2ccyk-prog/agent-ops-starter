# External Workers

Shared rules and registry for workers outside Claude (other CLIs and ChatGPT). Read when the user names a worker
("GPT 불러서 시켜", "agy한테 맡겨") or a project has an adopted role for one. Claude's own sub-agents live in
`~/.claude/agents/`, not here.

## Rules (always)

- Call a worker only when the current request names it, or a standing role is recorded in that project's
  `DECISIONS.md`. Availability, task difficulty or a failed attempt does not authorize a call.
- Authorization stays within that task and role. Follow-up calls on the same thread are allowed; a new job, extra
  reviewer, model substitution or standing default needs the user's word.
- Worker named but no model or effort: propose the recommended choice from "Choosing a model" in one line
  (e.g. "GPT sol high로 엑셀 정리 맡길게요. 진행할까요?") and run it after the user confirms.
- Never swap the model or raise effort without the user's word. The author never reviews its own output.
- Packets send content to the worker's provider: Codex and GPT Pro to OpenAI; agy to Google. Work files are often
  company documents: before the first send of a file, name the file and the provider and get the user's OK, unless
  the user already said that file may go there. Never include credentials, customer personal data or anything outside
  the task's scope.

## Registry

| Worker | Surface | Models | Use |
| --- | --- | --- | --- |
| `codex-worker` | `codex exec`, `doc:WORKER_CODEX` | `gpt-6.2-sol` (default); `gpt-6.2-astra` only when named | doing the work on files from a packet |
| `codex-reviewer` | `codex exec`, `doc:WORKER_CODEX` | `gpt-6.2-sol` xhigh, fresh session; `gpt-6.2-astra` only when named | checking a result, a plan or numbers |
| `agy-neon` | `agy -p`, `doc:WORKER_AGY` | `gemini-4-neon-high`, `gemini-4-neon-xhigh` | research, reading, summaries, second opinion |
| `gpt-pro` | ChatGPT (the user runs it), `doc:WORKER_GPTPRO` | GPT Pro | one large bundled job |

Check once per computer that each model answers (`codex exec` test call, `agy models`); a model that fails is
reported to the user, not replaced.

## Choosing a model (recommended, not fixed)

These say what each model suits; the user's word always wins.

| Model | Suits | Avoid |
| --- | --- | --- |
| Claude (lead) | deciding what to do, final review, client-facing tone, a conclusion drawn from many sources | long mechanical work |
| `sonnet-worker` | a scoped draft or edit: one report section, an email draft, filling a form | unclear asks |
| `haiku-worker` | mechanical work a check can judge: uniform formatting, bulk rename/replace, table conversion | anything needing judgment |
| `opus-worker` (when named) | independent review of another worker's output; wording and tone | routine work |
| GPT sol, high | work done on files: cleaning and converting spreadsheets, batch-processing many files, scripts for repeated chores | tone/visual work (layout, slides look) |
| GPT sol, xhigh (reviewer) | checking a report's logic, calculations and numbers against sources, reviewing a plan | its own output |
| GPT astra (when named) | as the user directs | default use |
| agy Neon, high | web research (prices, trends, products), long PDF/minutes summaries, scanned pages and table images, two-document comparison tables, first drafts | final approval, open "what is wrong?" questions |
| agy Neon, xhigh | a second opinion beside GPT, design/plan consults, reviewer when GPT is unavailable and the user agrees | first-pass research (use high) |
| GPT Pro | one large job: a whole long report reviewed, a big data set analysed, a bundle of proposal drafts; collect pending asks into one run | several small questions |

## Sessions

- Resume the same task's fix rounds and reviewer delta rounds in the same session. New tasks and first reviews start
  fresh, never in the author's session.
- When a run stops (credits, sign-in, crash), keep partial output and logs; an unfinished report is no verdict. Tell
  the user; never switch accounts, move credentials or silently change the worker.
- In the task's record keep one restart checkpoint: task and role; worker/model/effort; working folder; packet,
  result and log paths; PID and session ID if known; what is done; next authorized step.

## Packet

Build from `doc:HANDOFF_TEMPLATE`. The worker receives a self-contained packet stating:

- absolute working folder, the exact input files and the exact result path;
- "Do not spawn sub-agents or delegate further.";
- "Stop only for a concrete blocker, a decision only the user can make, or an irreversible action; otherwise make a
  reversible assumption, state it, and finish.";
- "Your final message stands alone: no labels or shorthand defined only in your working notes.";
- a `## Checks` section with how the result is judged. Office work: every claim has a source link, numbers match the
  source file, every input item is covered (count them). Code work: the named tests to add and run, once; no full
  suite unless the packet asks.

Reviewer packets name the files or plan to check and ask for: what the work is for (one paragraph); findings with
severity, location and a concrete failure scenario; BLOCKING only for a defect the work introduced or exposed;
weak evidence reported as non-blocking with what would prove it. An empty blocking list is a valid result.

### Bulk reading

- Size the input first (files, KB). Over about 20 files or 50 KB: split into chunks of about 50 KB, run one chunk
  first to see time and format, then the rest in parallel.
- Ask for a table with fixed columns and fixed choices; count and merge by script, not by the worker.
- Check the result against the source (every input covered, copied fields match) before using it.

## Acceptance

- Worker output is input. Check decisive evidence (file readback, numbers against the source, test result) before
  reporting done, and judge review findings rather than applying all of them.
- Report one line per call: worker, model/effort, packet path, result path.
