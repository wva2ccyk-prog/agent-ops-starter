# GPT Pro (user-run)

The user runs GPT Pro in ChatGPT; Claude writes the prompt and checks the output. `doc:EXTERNAL_WORKERS` holds the
shared rules and acceptance. Provider: OpenAI.

## When to use it

- One large job that benefits from long careful thinking: a whole long report reviewed, a big data set analysed, a
  bundle of proposal or plan drafts, a market or policy survey with sources.
- Each run is counted per request and can take very large jobs: collect pending asks into one run instead of many
  small ones. Do not message a running job (each message counts).
- Pro never decides scope; the lead (with the user) owns the plan and keeps or discards each part of the answer.

## Office run (default)

1. Claude lists the input files. The user approves sending them (company documents go to OpenAI). Remove or mask
   customer personal data and anything outside the job.
2. Claude writes ONE prompt with separated sections: goal and audience; inputs (file names as attached); the tasks,
   numbered; constraints (tone, length per part, language); the delivery spec. Prompt in English unless the output
   must be Korean; ask for the output language explicitly.
3. Delivery spec: exact output files or sections and their order; a table format where results are compared; a
   source or file-and-page citation for every factual claim and number; a short "not verified / assumptions" list.
   Cap only low-value counts, never the total size.
4. The user attaches the files in ChatGPT, pastes the prompt, and brings back the answer and any files.
5. Claude checks it before use: numbers against the source files, every requested task answered, citations open to
   what they claim (spot-check, then a narrow check by a worker for claims that drive a decision).

## Code repositories

For work on a Git repository (GitHub connector, unit branches, automatic unit checks) see
`optional/GPTPRO_CODE_REPOS.md` and `optional/tools/gptpro_units.py`; adopt them only when needed.
