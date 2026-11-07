# Portfolio Optimization

Sizing doctrine and the optimization toolset. Loaded for any sizing, concentration, portfolio-review, or construction question.

**Doctrine (set by the user, standing):** Kelly-informed concentration is primary; mean-variance-family optimization is the challenger. The two define risk differently — permanent capital loss vs return variance — and therefore can legitimately disagree. When they do, the skill reports both sizings, names the risk definition behind each, and does not average them.

## Table of Contents

1. The Primary Framework: Kelly-Informed Concentration
2. Opportunity-Cost Ranking (the portfolio-role question)
3. The Challenger Toolset: MPT, Black-Litterman, HRP, Risk Parity, Factor Lens
4. Reconciliation Procedure
5. Portfolio Review Protocol
6. Failure Modes of Each Framework

---

## 1. The Primary Framework: Kelly-Informed Concentration

### 1.1 The Kelly criterion

For a binary-outcome simplification (odds $b$, win probability $p$, $q = 1-p$):

$$f^* = \frac{bp - q}{b}$$

For continuous outcomes, the growth-optimal fraction is approximately

$$f^* \approx \frac{\mu - r}{\sigma^2}$$

where $\mu - r$ is the expected excess return of the position and $\sigma^2$ its variance — with the immediate caveat that for the value investor, the inputs come from the Phase 4 scenario tree (probabilities × scenario returns), not from historical price volatility.

Compute the growth-optimal fraction, the fractional size, the band and the survivability cap with `scripts/sizing.py`.

### 1.2 Fractional Kelly is mandatory

Full Kelly is never used. Reasons, in order of importance:

1. **Estimation error dominates.** $f^*$ is hypersensitive to $p$ and $b$, which are estimates. Overestimating edge under full Kelly produces overbetting, and overbetting is asymmetrically punished: betting $2f^*$ yields zero long-run growth with brutal drawdowns.
2. **Drawdown tolerance.** Full Kelly accepts drawdowns most humans (and all clients) abandon strategies during. Half-Kelly gives up ~25% of growth rate for ~50% of the variance — almost always the right trade.
3. **Correlated books.** Kelly per-position assumes independence; a concentrated value book holds correlated business risks (see §3.5 factor lens), so the aggregate must be scaled down further.

**Default: quarter- to half-Kelly,** with the fraction tied to conviction evidence (below).

### 1.3 Conviction-tiered sizing bands

The Li Lu test determines which band a position may occupy; Kelly arithmetic positions it within the band; the Klarman survivability check caps it.

| Tier | Evidence required | Band (of equities NAV) |
|------|-------------------|------------------------|
| Core conviction | Inside circle of competence; 10-year ownership answer is yes; passes Smith quality screen AND price below P50 value; thesis survived full cross-examination | 8–15% |
| Standard position | Clear thesis, one open question from cross-examination; price below P50 value | 4–8% |
| Opportunistic / special situation | Klarman-style: hard-anchor downside protection + identified catalyst; quality screen may fail | 2–5%, catalyst-dated |
| Tracking / research | Thesis incomplete; position exists to force attention | ≤1% |
| Outside circle of competence | — | 0%, regardless of apparent cheapness |

**Survivability cap (Klarman, binding):** position size × worst-defensible-case loss ≤ the portfolio drawdown the user can hold through without forced action. If the cap binds below the Kelly fraction, the cap wins; say so.

**Tree-audit rule (Mauboussin, standing):** when sizing rests on a user-supplied scenario tree, the Kelly arithmetic is run on the tree as given, but two audits are always offered or applied: (a) base-rate check on each branch's implied business outcome, and (b) tail completeness — does the worst branch reflect the worst *defensible* case for this industry, or a truncated one? Kelly is hypersensitive to exactly these inputs; auditing them is not optional courtesy, it is where the method's failure mode lives.

**Cycle modifier (Marks, ±):** pendulum position shifts the *aggregate* offense/defense (cash level, gross exposure), not individual intrinsic values. State the modifier separately so the user sees value judgment and cycle judgment unbundled.

---

## 2. Opportunity-Cost Ranking (the portfolio-role question)

"How important is this company to the portfolio?" is answered by Munger-style opportunity-cost ranking, not in isolation:

1. Rank all holdings + candidates + cash by expected return from current price to P50 value over the holding horizon, annualized:
$$E[r_i] \approx \left(\frac{V_{P50,i}}{P_i}\right)^{1/T} - 1 + y_i \quad (y_i:\ \text{shareholder yield})$$
2. Adjust each for: downside (P10 loss), conviction tier, and tax friction of switching (capital-gains tax on realized gains under the user's tax residence — switching has a hurdle; compute it; verify the current rate via search)
3. A holding's "importance" = its rank stability: a core compounder ranks high across bear/base/bull re-rankings; a marginal holding ranks high only in one scenario
4. The actionable output: which positions every marginal euro should flow to, and which holdings persist only by incumbency + tax friction (label these explicitly — they are the honest trim candidates)

---

## 3. The Challenger Toolset

Used diagnostically on the book the primary framework proposes. Never used as the allocator under the standing doctrine — but its findings can force the primary sizing to change (see §4).

### 3.1 Mean-variance (Markowitz)

$$\max_w \; w^\top\mu - \frac{\lambda}{2} w^\top\Sigma w$$

Diagnostic use: feed the skill's scenario-derived $\mu$ and a fundamentals-aware $\Sigma$ (see 3.5) and compare the MV weights to the conviction-tier weights. Large gaps localize where the concentrated book is making an implicit variance bet — which is fine, but it should be explicit.

Why it is not the allocator here: error maximization (Michaud) — MV amplifies estimation error in $\mu$; variance-as-risk contradicts the skill's risk definition; and historical $\Sigma$ encodes price co-movement, not business co-dependence.

### 3.2 Black-Litterman

$$\mu_{BL} = \left[(\tau\Sigma)^{-1} + P^\top\Omega^{-1}P\right]^{-1}\left[(\tau\Sigma)^{-1}\Pi + P^\top\Omega^{-1}Q\right]$$

The honest bridge between the two worlds: market-implied equilibrium returns $\Pi$ blended with the skill's views $(P, Q)$ at confidence $\Omega$. Diagnostic use: it forces the skill to state numerical confidence in each view — a useful discipline — and shows how much the book's tilt depends on view confidence. If a position only earns its size at implausibly high $\Omega^{-1}$, Mauboussin's base-rate check has been violated somewhere.

### 3.3 Hierarchical Risk Parity (López de Prado, 2016, *J. Portfolio Management*)

Clusters assets by correlation distance, allocates inverse-variance within the hierarchy; no matrix inversion, robust to estimation error. Diagnostic use: the dendrogram is the valuable artifact — it reveals which holdings the *market* treats as the same bet. If three "independent" theses cluster tightly, the book holds one position in three wrappers.

### 3.4 Risk parity / risk contribution

Marginal risk contribution per holding:

$$RC_i = w_i \frac{(\Sigma w)_i}{\sqrt{w^\top \Sigma w}}$$

Diagnostic use: report each holding's share of portfolio risk vs share of capital. A 10% capital position contributing 35% of risk should be a deliberate choice, not a surprise.

### 3.5 Factor & fundamental-correlation lens

Two correlation views, both reported:
- **Price-based:** factor regression (market, size, value, quality, momentum; rates/credit where relevant) — what the book looks like to the market
- **Fundamentals-based (preferred):** shared business drivers — same end-customer demand, same input costs, same regulatory regime, same FX pair. Built qualitatively by the checks; this is where "diversified" books holding five businesses exposed to the same capex cycle get caught.

---

## 4. Reconciliation Procedure

When primary (Kelly/conviction) and challenger sizings disagree materially (> ~1.5× on any position, or aggregate risk concentration flagged by 3.3–3.5):

1. **Name the risk definition behind each number** (permanent loss vs variance). If the gap is purely definitional, present both sizings with the user's choice framed: "this is a question about whether interim variance constrains you (leverage, liquidity needs, temperament), not about the businesses."
2. **Check for information, not just definition.** The challenger findings that DO override the primary sizing:
   - Fundamental-correlation clustering (3.5): conviction tiers were assigned per-position assuming independence that does not exist → scale the cluster, not the names
   - Survivability cap breach at the aggregate level: clustered worst cases co-occur → Klarman cap re-binds on the cluster sum
   - Black-Litterman confidence audit (3.2): a sizing that requires confidence the cross-examination did not establish → demote the tier
3. **Output:** final sizing table with three columns — primary sizing, challenger sizing, adopted sizing — and a one-line reason wherever adopted ≠ primary.

---

## 5. Portfolio Review Protocol

The step-by-step procedure is in `portfolio-review.md`.

---

## 6. Failure Modes of Each Framework

| Framework | Fails when |
|-----------|------------|
| Kelly (even fractional) | Edge estimates are correlated with each other (same analyst bias in every $p$); regime change invalidates the scenario tree faster than the review cycle catches it |
| Conviction tiers | Conviction measured by familiarity instead of evidence (endowment effect on long-held names); circle of competence quietly expands to wherever the opportunities are |
| Opportunity-cost ranking | Tax friction used as a rationalization to never sell (the hurdle is real but finite — compute it, don't invoke it) |
| Mean-variance | Garbage-in $\mu$; unstable $\Sigma^{-1}$; corner solutions |
| Black-Litterman | False precision in $\Omega$; equilibrium prior inappropriate for a concentrated absolute-return book |
| HRP | Correlation estimated over a calm window; clusters reshuffle exactly in the crises where they matter |
| Risk parity | Variance ≠ risk for the value investor; structurally overweights low-vol at any price |
| Factor lens | Factor definitions drift; a "quality" loading can be a crowded trade, not a safety attribute (Marks: perceived safety is where risk hides) |
