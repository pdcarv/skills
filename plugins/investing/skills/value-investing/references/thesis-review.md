# Thesis review

Revisits a recorded thesis when one of its checkpoints comes due, when a new filing lands, or when the user asks how it is going. It judges the reasoning, not the outcome: a good decision can lose money and a bad one can make it, so the question is which assumptions held and whether the process was sound. Reads `state/theses/<ticker>-<date>.md`; appends a review section to the same file and, if the decision changes, notes it there and in `state/holdings.yaml` when the user confirms.

## Contents

- 1 Load the thesis
- 2 Gather what is new
- 3 Score each checkpoint
- 4 Separate luck from judgement
- 5 Decide
- 6 Write and verify
- Gotchas

## 1. Load the thesis

Read the thesis file: the claim, the cases and their probabilities, the expected outcome, the checkpoints with dates, the abort criterion, the pre-mortem, the size and the decision. Do not reread the original reasoning as if it were evidence; it is the hypothesis under test.

## 2. Gather what is new

An abbreviated pre-flight (`analyse.md` section 1) covering what has changed since the thesis date: results, guidance, capital allocation, management, the competitive landscape, and the price. Run the input checks on anything that feeds a checkpoint.

## 3. Score each checkpoint

For every checkpoint due: the observable it named, what was observed (with source and date), and one of hit, missed or not yet measurable. Check the abort criterion explicitly. If it has been met, say so first.

## 4. Separate luck from judgement

For each assumption that drove the cases:

| Assumption | Held? | Evidence | Was it a reasonable call at the time, given what was knowable? |
|---|---|---|---|

Then ask:

- Did the pre-mortem name what actually went wrong? If so, was it under-weighted?
- Did the price move for a reason the thesis covered, or for an unrelated one (market, rates, sector flows)? An unrelated move is neither confirmation nor refutation.
- Would the same process, with the same information, make the same decision again?

Record a process lesson only when it would change a future analysis; route durable lessons with `compound-learnings` (personal-productivity).

## 5. Decide

- **Abort criterion met:** recommend exiting or resizing, stating the criterion and the evidence.
- **Checkpoints hit, value intact:** hold; refresh the cases and the reverse DCF (`scripts/valuation.py`) at today's price.
- **Mixed:** state which part of the thesis survives, rerun `scripts/sizing.py` on the revised tree, and let the user decide.
- **Thesis broken but price attractive for other reasons:** that is a new thesis; run `analyse.md` from the start rather than patching the old one.

## 6. Write and verify

Append a dated `## Review <YYYY-MM-DD>` section to the thesis file: checkpoints scored, the assumptions table, the decision and any next checkpoint. Run `scripts/trace_check.py` on the summary before showing it.

## Gotchas

- **Resulting.** Judging the decision by the outcome alone teaches the wrong lesson; the assumptions table is the antidote.
- **Moving the goalposts.** Rewriting a missed checkpoint into a later date without saying so turns a thesis into a hope. A changed checkpoint is recorded as changed, with the reason.
- **Reviewing only the losers.** Review winners too; a winning thesis with broken assumptions is luck.
