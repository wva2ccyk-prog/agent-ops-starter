# State: Document similarity analysis

## Goal

Find similar documents in the institution's document set and deliver a list of similar pairs or groups, with the
reason and a confidence for each, that the user can stand behind. Real task the result serves: not named
(ask the user: plagiarism check, duplicate-project check, or something else).

## Progress

- S1 Criteria: next (what "similar" means, threshold, outputs; `WORKFLOW.md` step 1)
- S2 Text extraction with coverage count: later
- S3 Local scoring and candidate pairs: later
- S4 Candidate pair comparison tables: later
- S5 Verification: later
- S6 Whole-set interpretation and report draft: later
- S7 Conclusion and report: later

## Now

- Nothing started. Fill the open decisions first.

## Next

- Ask the user the S1 questions in `WORKFLOW.md` step 1 and record the answers in `DECISIONS.md`.

## Open decisions

- Document classification (public / non-public / restricted, personal data): decides which steps may use external
  models (`SECURITY.md`).
- File formats and count (HWP, PDF, scanned): decides the extraction tools.
- Meaning of "similar" and the threshold.

## Watch out

- Extraction silently drops files (HWP, scanned PDF, tables). Count before trusting any score.
- A model asked to "find similar documents" over the whole set will miss most of them; it only judges candidates.

Last updated: <YYYY-MM-DD>
