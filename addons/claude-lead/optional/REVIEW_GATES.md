# Review Gates

Common evidence and review principles. Read when writing a worker or reviewer
packet, judging a review, or making a done claim. Project-specific scripts,
fixtures, replay commands, defect taxonomies and consult timing belong in the
project's adopted procedure.
Two ideas adapted from pstack (`blast-radius`, `principle-prove-it-works`, MIT).

## 1. Key-fact proof (every review)

The reviewer first states in one paragraph what the change is for (from the
packet or PR body). Then it names the one to three facts the change's safety
rests on (an invariant, a caller or reader outside the diff, a shape of data on
disk) and proves each as far as it goes cheaply, reporting the level reached:

1. stated (worthless alone)
2. file:line pointed at
3. failure walked step by step and shown not to happen
4. ran an existing test or command that fails loudly if the fact is false

A key fact about risky behaviour (persistence, locking, sending, money,
deletion, auth, concurrency) that stops at level 1 or 2 is a blocking finding.
The packet names which areas count as risky for the project.

Bound: at most three key facts; stop each at the cheapest level that settles
it; never rerun a check that already passed just to reconfirm it.

## 2. Prove it before "done" (every worker and the lead)

- Read the real state and the full exit code before reporting success (merged,
  sent, started, passed). A truncated tail (`| tail -1`) or your own echo
  proves nothing.
- A failing check proves something only when its failure content is the
  disagreement you predicted: quote the assertion's diff, not the assertion.
- For each fact you relied on, name the record it came from.
- Office work: a number is proven by the source cell or page it came from; a summary or
  table by counting the source items it covers; a claim from the web by the page it
  links to, opened.
- Use the project's adopted acceptance checks for the changed behaviour. When
  indirect callers make a replay necessary, name it in that project's procedure.
  Keep valid evidence until its relevant inputs change; do not duplicate a passed
  check solely because another phase began.

## 3. Acceptance mapping (projects that adopt a spec)

Map accepted requirements to reachable checks in the project's existing acceptance
record. Projects that adopt requirement IDs also define their ID checks there. A
new project needs an explicit acceptance path.

## 4. Fix rounds and review strength

- The lead triages each REVISE once: adopted rule and concrete failure, introduced
  or exposed versus inherited, defect class and affected siblings, and overlap with
  the prior fix. No adopted rule means a proposal; an inherited defect is carried,
  not silently turned into a new fix obligation. Reproduce on the base when that
  distinction is uncertain. Oscillation returns to the adopted contract.
- Fix the class and its affected siblings. Keep a reviewer's reproducer as a
  regression or oracle in the behaviour's existing test module. Evidence must
  demonstrate the asserted failure, not merely name a test.
- A project's adopted procedure owns required design/class consults and launch
  checks, including their trigger and evaluation. This common doc adds no mandatory
  pre-worker or second-REVISE model call.
- Automate objective bookkeeping where an existing check can measure it. Duplicate
  reviewer checks of passing metadata add no evidence. Size overruns are a lead
  record; a demonstrated behavioural failure or violated adopted contract remains
  reviewable regardless of the size report.
- Match review to risk. Projects name Tier A areas and any exceptions:
  - A: persistence, locking, lineage/currentness, sends, money, deletion, auth, credentials and
    safety gates: full semantic review, one feature slice or defect class per PR;
    split planned changes above about 800 product lines.
  - B: bounded connector options, CLI/output and CI tooling: one review, then lead
    verification of its fixes.
  - C: docs, additive tests and mechanically equivalent moves: CI plus lead check.
  Existing-test edits/removals and uncertain classifications need semantic review.
  A normative-spec change follows the project's adopted rule. Reuse a reviewed
  product head for a non-behaviour delta only where the project explicitly allows
  that route; the final verdict and CI still identify the exact head.
- Extra reviewers require the owner's adopted route.

## 5. Review scope (every reviewer packet)

Every reviewer packet states these rules; the report tags each BLOCKING item
`in-diff` or `caller:<path>`.

- Look for: correctness and stability defects (data loss, wrong result,
  crash, hang, unsafe state), clearly inefficient behaviour with a concrete
  cost (repeated I/O or model calls, unbounded work), and duplicated code that
  can drift apart. Not style, naming, or a working structure that could be
  shaped differently.
- First review: BLOCKING only for a defect the change introduces or exposes,
  on a changed line or on a caller, reader or sibling path whose behaviour the
  change alters (name the path). A defect already on the base branch that the
  change does not touch is NON-BLOCKING `inherited`; the lead carries it.
- Delta review: new BLOCKING only on lines changed since the previous reviewed
  head, or a sibling of an earlier finding. Anything else is NON-BLOCKING
  `outside-delta` for the lead to carry or schedule.
- Weak evidence: report it as NON-BLOCKING with what would prove it, never as
  BLOCKING; an empty BLOCKING list is a valid result.
- Bookkeeping: a finding whose fix changes no product
  behaviour and no test's assertion (a name, a label, a declaration line, a
  metadata field) is NON-BLOCKING `bookkeeping`; a report with only such
  findings is ACCEPT. The lead fixes or carries it. A field a tool already
  checks is not re-checked by the reviewer.
