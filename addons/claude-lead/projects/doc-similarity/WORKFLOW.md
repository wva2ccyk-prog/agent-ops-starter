# Workflow: document similarity analysis

Seven steps. Each step names the recommended worker (`doc:EXTERNAL_WORKERS` Choosing a model); the user's word
overrides. Steps marked LOCAL send no document content outside this computer. Paths below are under the project
runtime folder (`README.md` `Runtime:`).

| Step | Work | Recommended | Leaves the computer |
| --- | --- | --- | --- |
| 1 Criteria | define "similar", threshold, outputs | Claude lead with the user | nothing |
| 2 Extraction | files to plain text, coverage count | GPT sol high, script run locally | LOCAL |
| 3 Candidates | score all pairs, keep top candidates | GPT sol high, script run locally | LOCAL |
| 4 Pair tables | compare each candidate pair in a fixed table | agy Neon high | candidate pairs, after `SECURITY.md` |
| 5 Verification | check scripts, threshold, samples, missed pairs | GPT sol xhigh (fresh); Neon xhigh second opinion | code and a few samples |
| 6 Whole-set view | patterns across groups, report draft | GPT Pro | aggregates and short excerpts |
| 7 Conclusion | final judgment and report | Claude lead | nothing |

## 1. Criteria (Claude with the user)

Ask and record in `DECISIONS.md`:
- What counts as similar: copied sentences, same structure or template, same topic or project, or several of these.
- Unit of comparison: whole document, section, or paragraph.
- What the result is for (plagiarism check, duplicate projects, grouping) and who reads it.
- Output: a list of pairs or groups; score cutoff; what each row must show.
- Classification of the set (`SECURITY.md` §1).

## 2. Extraction (Codex, local)

Packet asks for a script, run on this computer, that:
- converts every file to UTF-8 text in `text/` with the same base name (HWP: an HWP-to-text tool such as `hwp5txt` or
  LibreOffice conversion; PDF: a text extractor; scanned pages: local OCR, or step 4's model only if `SECURITY.md`
  allows);
- writes `coverage.csv`: file, format, pages or size, extracted characters, status (ok / empty / failed / scanned).
Checks: number of rows in `coverage.csv` equals the number of source files; every `empty` or `failed` file is listed
for the user. Do not continue to step 3 while unexplained gaps remain.

## 3. Candidates (Codex, local)

Packet asks for a script that normalizes text (spacing, numbering, boilerplate headers the user names) and scores all
pairs with a local method fitting step 1: character or word n-gram overlap (MinHash for large sets) for copying,
TF-IDF cosine for topic. Output `pairs.csv`: doc_a, doc_b, score, method, top shared passages (short). Keep the top
pairs above the threshold plus a band just below it for step 5. No cloud embedding API unless `SECURITY.md` allows it.

## 4. Pair tables (agy Neon high)

Only for pairs whose documents passed `SECURITY.md`. Chunks of about 50 KB per call; one chunk first to check format.
Ask for one row per pair with fixed columns and fixed choices:

| doc_a | doc_b | similarity type (copy / structure / topic / none) | shared parts (quote, ≤ 3) | differences (≤ 3) | confidence (high / medium / low) |

Merge by script; check every pair sent came back once.

## 5. Verification (GPT sol xhigh, fresh session)

- Review the step 2–3 scripts against step 1 criteria and the threshold.
- Recompute 10–20 sampled pairs by hand or by script and compare with `pairs.csv`.
- Missed pairs: take a random sample of pairs below the band and confirm none should have passed.
- Neon xhigh may give a second opinion on contested pairs. The author of a step never approves it.

## 6. Whole-set view (GPT Pro)

One run with `pairs.csv`, the step 4 tables and group counts (`doc:WORKER_GPTPRO` Office run). Ask for patterns per
group, borderline cases, and a report draft with every claim pointing to a pair or file. Send excerpts only as far as
`SECURITY.md` allows.

## 7. Conclusion (Claude)

Write the final list and report; mark where a person must confirm (low confidence, borderline scores, scanned files).
Update `STATE.md`.
