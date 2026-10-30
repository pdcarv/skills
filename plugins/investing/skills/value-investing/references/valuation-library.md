# Valuation Library

Canonical models, selection rules, parameter guidance, and cross-checks. Loaded for Deep Dives and any model-building task. Mathematical notation uses LaTeX; in delivered `.xlsx` models, every formula cell must trace to a labeled assumption cell.

## Table of Contents

1. Model Selection Rules
2. FCFF DCF (workhorse)
3. Reverse DCF / Expectations Investing
4. EVA and Residual Income
5. Customer-Based Corporate Valuation (CBCV)
6. Owner Earnings & Hard-Numbers Anchors
7. Multiples (pricing, not valuation)
8. Uncertainty Treatment
9. Cross-Check Discipline

---

## 1. Model Selection Rules

Choose by company lifecycle and information availability — not by habit. Multiple models are usually warranted; the user's standing preference is pros/cons of each applicable model, not a single anointed one.

| Company profile | Primary model | Secondary / cross-check |
|-----------------|--------------|--------------------------|
| Mature, stable FCF, moderate growth | FCFF DCF | EVA (same answer, different lens — see §4 equivalence), owner earnings yield |
| High-quality compounder (ROCE ≫ WACC) | FCFF DCF with explicit CAP | Residual income (isolates the value of the moat), Smith's source-of-return arithmetic |
| Subscription / repeat-purchase business with cohort disclosure | CBCV | Reverse DCF on the implied customer economics |
| Young growth, pre-stable-margin | Lifecycle DCF (revenue-driven, survival-weighted) | Mauboussin TAM + base-rate plausibility test |
| Financials | Residual income / excess returns on equity | Dividend discount as sanity check (FCFF ill-defined for banks) |
| Asset-heavy, cyclical | Normalized-earnings DCF (mid-cycle) | Klarman hard anchors: replacement cost, private-market value |
| Distressed / declining | Liquidation & asset value, scenario-weighted | Going-concern DCF only as one branch of the tree |
| Any company, always | — | Reverse DCF (§3) is run on EVERY Deep Dive regardless of primary model |

---

## 2. FCFF DCF (workhorse)

Compute it with `scripts/valuation.py` (cases, mid-year discounting, terminal-value share, exit-multiple cross-check, sensitivity grids); never by hand in prose.

$$V_0 = \sum_{t=1}^{n} \frac{FCFF_t}{(1+WACC)^t} + \frac{TV_n}{(1+WACC)^n}, \qquad TV_n = \frac{FCFF_{n+1}}{WACC - g_\infty}$$

with $FCFF_t = NOPAT_t - \Delta IC_t$ and the **consistency identity that gets audited on every model**:

$$g_t = RR_t \times ROIC_t \quad\Longleftrightarrow\quad \Delta IC_t = \frac{g_t}{ROIC_t}\, NOPAT_t$$

Growth assumed without the reinvestment to fund it is the single most common DCF error; Damodaran rejects the model outright if the identity is violated.

**Parameter guidance:**
- $WACC$: bottom-up beta from the business mix, current ERP and risk-free rate (pull Damodaran's current data pages via search — never quote remembered values), debt cost from current traded yields or rating
- $g_\infty \le r_f$ of the valuation currency; terminal ROIC → WACC unless a durable moat is argued explicitly, in which case the terminal $ROIC > WACC$ spread must be defended in words (Smith and Mauboussin co-own this defense)
- Explicit forecast horizon = the defensible Competitive Advantage Period, not a reflexive 5 or 10 years
- **Mandatory disclosure:** terminal value as % of total value. Above ~75%, the valuation is mostly a terminal assumption wearing a forecast costume — say so.

**Failure modes:** cyclical peak/trough earnings extrapolated as steady-state; currency mismatch between cash flows and discount rate; stock-based compensation ignored in FCFF; buyback-driven EPS growth confused with business growth.

---

## 3. Reverse DCF / Expectations Investing

`scripts/valuation.py` solves for constant growth with margin and ROIC held fixed whenever `price` is given.

Run on every Deep Dive. Invert §2: hold the structure, solve for the assumption set $\{g, m, CAP\}$ that makes model value equal the current price.

$$\text{Find } \{g, m, CAP\} : V_0(g, m, CAP \mid WACC) = P_0$$

Then test plausibility against base rates: for the company's revenue size band, what fraction of companies historically achieved the implied growth for the implied duration? Cite the distribution (Mauboussin's Base Rate Book or equivalent large-sample study).

**Output format:** "The current price of €X implies roughly Y% revenue CAGR for Z years at W% operating margin. Companies of this size achieved that in approximately P% of historical cases." This is the expectations verdict that anchors Phase 4.

**Failure modes:** non-uniqueness (many assumption sets fit one price — report the most economically plausible set and say others exist); using sell-side consensus as the "market expectation" when price and consensus disagree.

---

## 4. EVA and Residual Income

$$EVA_t = NOPAT_t - WACC \times IC_{t-1} = (ROIC_t - WACC)\, IC_{t-1}$$

$$V_0 = IC_0 + \sum_{t=1}^{\infty} \frac{EVA_t}{(1+WACC)^t}$$

Equity-side residual income (for financials, with $r_E$ and book equity $B$):

$$V_0^{E} = B_0 + \sum_{t=1}^{\infty} \frac{(ROE_t - r_E)\,B_{t-1}}{(1+r_E)^t}$$

**Why the skill uses it despite formal equivalence to DCF:** the decomposition makes the moat visible. $V_0 - IC_0$ is the market's payment for future excess returns; comparing it to the skill's defensible CAP is a direct moat-pricing test. It also disciplines terminal assumptions: fade $ROIC \to WACC$ and the residual term goes to zero by construction.

**Failure modes:** invested capital distorted by goodwill from past M&A (decide and disclose: ROIC with and without goodwill answer different questions — operating quality vs management's capital-allocation record); operating leases and capitalized R&D inconsistencies between NOPAT and IC.

---

## 5. Customer-Based Corporate Valuation (CBCV)

For businesses where the revenue engine is acquire-retain-monetize (subscription, repeat-purchase, marketplaces). Per McCarthy–Fader (2017, *Journal of Marketing Research*; 2018, *JAMS*): build revenue bottom-up from customer behavior instead of top-down growth rates.

Components:

$$CLV = \sum_{t=0}^{\infty} \frac{m_t \cdot r^t}{(1+d)^t} - CAC \qquad \text{(simple geometric-retention form)}$$

with cohort-level refinements: acquisition curve $A_t$ (often Bass-diffusion-shaped against TAM), retention curve $r_t$ by cohort age (shifted-beta-geometric where individual heterogeneity matters), monetization ramp $m_t$ per surviving customer. Corporate value = discounted sum over existing cohorts + value of future cohorts − fixed costs, taxes, capital intensity (i.e., CBCV replaces the revenue line of the DCF, not the DCF).

**Data reality (this is the usual binding constraint):** few companies disclose cohort tables. When working from aggregate disclosures (subscriber counts, ARPU, churn or its proxies), the parameter inference is an `EXTRAPOLATION` under Phase 5 — name the proxy chain (e.g., "retention inferred from net adds and gross adds guidance") and the checkpoint that validates it.

**Failure modes:** survivorship in blended ARPU (mix shift mistaken for monetization growth); contractual vs non-contractual churn definitions mixed; CAC reported on a marketing-only basis while sales headcount sits in opex.

---

## 6. Owner Earnings & Hard-Numbers Anchors

Cash conversion, ROCE and interest cover come from `scripts/screens.py` (`quality`).

The Klarman/Smith side of the reconciliation rule. Compute at minimum:

- **Owner earnings** (Buffett, 1986 letter): reported earnings + D&A ± non-cash items − maintenance capex (estimate maintenance vs growth capex explicitly; disclose the split method). Owner-earnings yield $= OE / EV$ compared against the user's hurdle and against bond yields.
- **Cash conversion:** FCF / net income over 5–10 years (Smith's earnings-are-real test; persistent < 80% demands an explanation)
- **Hard anchors where applicable:** net current asset value, tangible book, replacement cost, recent private-market / take-private transaction multiples for comparable assets

These anchor the §9 cross-check; a DCF value far above all hard anchors is not wrong, but it is a claim about the future that must be argued, not assumed.

---

## 7. Multiples (pricing, not valuation)

Multiples are used in two legitimate ways only: (a) Phase 0 sentiment measurement (current multiple vs own history vs sector), and (b) reverse-engineering — every multiple is a compressed DCF:

$$\frac{P}{E} = \frac{\text{payout}\times(1+g)}{r_E - g} \qquad \frac{EV}{EBIT} \approx \frac{(1-\tau)(1 - g/ROIC)}{WACC - g}$$

Use the decomposition to ask what growth/return assumptions a peer multiple smuggles in. A multiple is never the skill's value estimate. Damodaran's terminology is enforced: comparing multiples is *pricing*; the skill's job is *valuation*.

---

## 8. Uncertainty Treatment

Per the user's standing preference: probabilistic ranges and confidence statements, never single points.

- **Default:** 3-scenario tree (bear/base/bull) with stated probabilities and ONE named driving assumption per scenario; scenario-weighted expected value plus the full range
- **Deep Dives on input-sensitive names:** identify the 2–3 inputs with the largest $\partial V/\partial x$, present a sensitivity table over their plausible ranges; Monte Carlo only when the user asks or when interaction effects make the scenario tree misleading (then: state distributions assumed per input and report P10/P50/P90)
- **Klarman overlay:** independent of the distribution, report the worst defensible case in € per share and the loss at the proposed position size — survivability is checked against the loss, not the variance
- The margin of safety is then a statement, not a slogan: current price vs P10 value and vs the hard anchors of §6

---

## 9. Cross-Check Discipline

Every Deep Dive valuation reports, in one table:

| Lens | Value / verdict |
|------|-----------------|
| Primary model (per §1 selection) | bear / base / bull, probabilities |
| Reverse DCF | what price implies + base-rate percentile |
| Hard anchors (§6) | owner-earnings yield, asset/transaction anchors where applicable |
| Reconciliation | required if primary vs hard anchors diverge > ~30% — name the responsible input |

A valuation that survives all three lenses with the disagreements explained is the skill's product. A valuation from one lens is a draft.
