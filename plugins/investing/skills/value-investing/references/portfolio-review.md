# Portfolio review

Re-ranks the holdings, re-certifies conviction, checks hidden concentration, and proposes target weights against the do-nothing case. Reads `state/holdings.yaml` and `state/context.md`; writes a review entry in `state/reviews.md` and, only if the user supplies new positions, updates `state/holdings.yaml`.

## Contents

- 1 Load
- 2 Refresh each holding
- 3 Rank by opportunity cost
- 4 Re-certify conviction
- 5 Check concentration
- 6 Reconcile and size
- 7 Action list
- 8 Write and verify
- Gotchas

## 1. Load

Read `state/holdings.yaml` (positions, cost basis, purchase dates), `state/context.md` and the open theses in `state/theses/`. If there is no holdings file, ask the user for the positions; write them only after they confirm.

## 2. Refresh each holding

An abbreviated pre-flight per name (`analyse.md` section 1): price, last results, material news, and the input checks for price, diluted shares and net debt. Where a thesis exists, note which of its checkpoints have come due (`thesis-review.md`).

## 3. Rank by opportunity cost

Rank holdings, cash and any candidates the user names by annualised expected return from today's price to the P50 value (`portfolio-optimization.md` section 2), adjusted for the P10 loss, the conviction tier and the tax cost of switching under the user's tax residence (verify the current rate by search). A holding's importance is its rank stability across bear, base and bull re-rankings. Label the holdings that persist only by incumbency and tax friction: they are the honest trim candidates.

## 4. Re-certify conviction

For each holding, rerun the checks that move tiers: ROCE trend and cash conversion (`scripts/screens.py`), what today's price implies (`scripts/valuation.py` reverse DCF), and a refreshed worst case. A tier is demoted when the evidence that earned it has weakened, not when the price has fallen.

## 5. Check concentration

Run the challenger diagnostics in `portfolio-optimization.md` section 3: the correlation dendrogram (which holdings the market treats as one bet), each holding's share of risk against its share of capital, and the fundamental clusters (shared customers, input costs, regulation, currency). Clustered worst cases make the survivability cap bind on the cluster, not on the names.

## 6. Reconcile and size

For each holding, run `scripts/sizing.py` from its current scenario tree and tier. Reconcile primary and challenger sizings with the procedure in `portfolio-optimization.md` section 4 and show the three-column table: primary, challenger, adopted, with a one-line reason wherever adopted differs from primary.

## 7. Action list

Each proposed move with its tax cost, the cash it frees or needs, and the case for doing nothing argued seriously: the quality lens defaults to inaction, and turnover must out-argue it. The user decides; the review proposes.

## 8. Write and verify

Append a dated entry to `state/reviews.md` (schema in `state.md`): ranking, tier changes and their evidence, concentration findings, the adopted weights and the decisions the user took. Run `scripts/trace_check.py` on the summary. For a spreadsheet deliverable, follow the rules in `analyse.md` section 10.

## Gotchas

- **Tax friction as a reason never to sell.** The hurdle is real but finite; compute it rather than invoking it.
- **Familiarity mistaken for conviction.** Long-held names drift into higher tiers by endowment, not evidence.
- **Independent-looking theses that are one bet.** Five businesses exposed to the same capex cycle are one position.
- **Writing holdings the user did not give.** Holdings come only from the user or their broker statement, confirmed.
