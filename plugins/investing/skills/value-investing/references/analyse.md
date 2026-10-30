# Analyse: a company, a thesis or a methodology question

The main procedure. It gathers dated evidence, verifies the inputs a valuation rests on, computes screens and valuations with the scripts, runs the six lens checks in order, writes the strongest bear case, and ends in a verdict or an explicit split. The user signs off at four stages before the next one starts.

Work in a folder outside the repository and outside `state/` (for example `/tmp/value-investing-<slug>/`) for `manifest.json`, `sources.json`, model inputs and drafts.

## Contents

- 0 Triage
- 1 Evidence pre-flight and input checks (sign-off 1: inputs)
- 2 Screens
- 3 Model choice and scenarios (sign-off 2: assumptions)
- 4 Valuation (sign-off 3: valuation)
- 5 The six checks
- 6 Bear case
- 7 Verdict, split and sizing (sign-off 4: sizing)
- 8 Extrapolation clause
- 9 Comparing options
- 10 Deliverables
- 11 Thesis journal
- 12 Verify before emitting
- 13 Investor context
- Gotchas

---

## 0. Triage

### Depth tier

| Tier | Trigger | Pre-flight scope | Sign-offs |
|------|---------|------------------|-----------|
| Quick Check | One well-defined question, one lead lens | Price and headline scan (skip manager positioning unless asked) | None; state assumptions inline |
| Standard Analysis | Several lenses, moderate complexity | Sections 1.1-1.5 | Inputs and valuation |
| Deep Dive | Full thesis, model build, methodology comparison | Sections 1.1-1.5 plus the primary filing | All four |

Escalate, never silently downgrade: if a Quick Check uncovers a live controversy (an earnings miss, thesis-relevant news), say the question warrants Standard depth and ask, or proceed and say why.

### Lead lens

Use the activation map in SKILL.md and name the lenses not used, with the reason ("margin of safety not used: pure methodology question").

### Constraints

Read `state/context.md` (tax residence, broker and venues, base currency, portfolio style) and `state/holdings.yaml` if they exist. Ask for any missing constraint that would change the answer before going further.

---

## 1. Evidence pre-flight and input checks

Mandatory for any company-specific question. Record every datum in `sources.json` with `label`, `value`, `source` (URL or filing reference) and `as_of`.

### 1.1 News and filings

- Search the company name with recent news and the latest results: guidance changes, management changes, M&A, regulatory events.
- For Deep Dives, fetch the latest annual or interim report or the earnings release from the IR site or the filing repository (SEC EDGAR for US filers; the officially appointed mechanism for EU filers).
- Record the report date, the period covered and the headline figures (revenue, operating income, FCF, net debt, share count).

### 1.2 Manager positioning

- Search 13F aggregators (Dataroma, WhaleWisdom) and recent fund letters mentioning the name.
- Record which recognised value managers hold, added, trimmed or exited, with the filing quarter.
- **Staleness label, always:** 13F data is at least 45 days old, long-only, US-listed equities only, and shows positions, not theses. It is sentiment evidence, never thesis evidence.

### 1.3 Sentiment

- Analyst consensus and target range against the current price; short interest and its trend; the prevailing narrative in one line.
- Current multiples against the company's own 5-10 year history.

### 1.4 Price and market data

- Current price, market cap, diluted shares, net debt or net cash, listing currency and revenue currency.
- The liquid listing on the user's preferred venues (from `state/context.md`).

### 1.5 Input checks (before any model)

Valuations break on extraction and arithmetic far more than on theory. Check each load-bearing input against the primary filing or the exchange, not an aggregator:

| Input | Check |
|---|---|
| Price | Exchange or broker quote with timestamp |
| Diluted shares | Latest filing; include options, RSUs and convertibles; note buybacks since |
| Net debt or net cash | Sign is right; leases treated consistently with EBIT; cash not double-counted |
| Latest FCF | CFO minus capex from the cash-flow statement; stock-based compensation noted |
| Tax rate | Effective rate inside a plausible band for the jurisdiction; explain if not |
| Margin history | 3-5 years of operating margin; flag one-offs and cyclical peaks |

An input that cannot be confirmed is labelled `unverified`. A Deep Dive cannot rest on an unverified load-bearing input: ask the user for it or stop at Standard depth.

Open the answer with the evidence block:

```
EVIDENCE (as of <date>)
Price / Mkt cap:        ... (source, URL)
Last reported period:   ... key figures ...
Material news:          ...
Manager positioning:    ... (13F quarter noted)
Sentiment:              consensus ..., short interest ..., narrative "..."
Input checks:           price ✓  shares ✓  net debt ✓  FCF ✓  tax ✓  margins ✓  (or unverified: ...)
Data gaps:              ...
```

If web access is unavailable, say so, label everything "stale as of training cutoff", and offer a methodology-only answer instead of a Deep Dive.

**Sign-off 1 (inputs):** show the evidence block and the input checks; continue only when the user confirms or corrects them.

---

## 2. Screens

Run `scripts/screens.py` with the filing figures (keep the run id): Piotroski F-score, Altman Z (original for manufacturers, Z'' otherwise), Greenblatt earnings yield and return on capital, and the quality screen (ROCE, gross margin, interest cover, multi-year cash conversion). The screens feed the checks in section 5; they are evidence, not a verdict. For banks and insurers, skip them and use residual income and regulatory capital measures.

---

## 3. Model choice and scenarios

- Pick the primary and cross-check models from `valuation-library.md` section 1. A reverse DCF runs on every Deep Dive.
- Build bear, base and bull cases. Each names **one** driving assumption and states it as a story in words ("the base case means margins reach the best competitor's level by year 5") before it becomes a number.
- Attach probabilities to the cases, and say where each comes from.

**Sign-off 2 (assumptions):** show the cases, their driving assumptions and probabilities; continue when the user confirms.

---

## 4. Valuation

- Run `scripts/valuation.py` on the model inputs (keep the run id). It enforces growth = reinvestment rate × ROIC, rejects terminal growth at or above WACC, reports terminal value as a share of EV, cross-checks an exit multiple, weights the scenarios, solves the reverse DCF and builds the sensitivity grids.
- Read every note the script returns. Terminal value above 75% of EV means the valuation is mostly a terminal assumption: say so.
- Compute the hard-numbers anchors (owner earnings yield, asset or transaction anchors) from `valuation-library.md` section 6.
- Fill the cross-check table (`valuation-library.md` section 9). If the primary value and the hard anchors differ by more than about 30%, a reconciliation paragraph is mandatory: name the input responsible (usually the competitive-advantage period, the terminal assumptions, or cyclically adjusted vs current earnings) and say which side the evidence supports.

**Sign-off 3 (valuation):** show the scenario values, the weighted value, the range, the reverse-DCF verdict and the sensitivity grids; continue when the user confirms.

---

## 5. The six checks

One agent applies the six lens checks in this order. Each check is a short bullet diff of 3-5 bullets, not paragraphs, and uses the screen and script outputs rather than judging by eye.

| Check | Lens | Question forced |
|-------|------|-----------------|
| Consistency | Valuation mechanics | Growth, reinvestment and ROIC consistent? Terminal value share? Cost of capital current, not remembered? |
| Expectations | Expectations and base rates | What does the price imply? Which base-rate distribution does the thesis sit in, and at what percentile? |
| Permanent loss | Margin of safety | Worst defensible case per share? Is the proposed size survivable if it hits? Who is selling and why? |
| Quality and traps | Quality compounders | ROCE above WACC and durable, or decaying? Cash conversion confirms earnings? Cheap plus declining returns plus a turnaround story? |
| Competence and size | Concentrated ownership | Can the 10-year competitive landscape be explained to a sceptic? Does conviction evidence justify the size? |
| Second-level | Cycles and sentiment | Where is the pendulum on this name? Is the view second-level, or consensus or mere contrarianism? |

Tag every disagreement with its source:

- **E (evidence):** the checks weight different data; resolve it with more pre-flight work if the tier allows.
- **R (risk definition):** permanent loss vs variance vs tracking error; not resolvable; present both.
- **H (horizon):** reversion over 2 years vs compounding over 10; not resolvable; present both with the horizon named.
- **F (framework):** a genuine methodological split (contested register, `lenses.md` section 7); present both.

For a second opinion, run the same checks on a different model with the evidence and the cases but not this draft. A debate between voices on one model adds cost, not accuracy.

---

## 6. Bear case

Before the verdict, write the strongest case against the position as if arguing the short:

- The two or three things that must be true for the bear case, and how plausible each is against base rates.
- Who is selling today and why they might be right.
- A pre-mortem: assume the position lost 40% in two years; write the most likely story of how.

If the bear case is stronger than the bull case on evidence, the verdict says so.

---

## 7. Verdict, split and sizing

### Consensus (no R, H or F split remains)

State, answer first:

- The verdict in one line, then the intrinsic value range: bear / base / bull with probabilities and the driving assumption for each.
- The expectations verdict: what the price implies against what the evidence defends.
- Portfolio role: core compounder, opportunistic value, special situation, or avoid.
- The falsification block: "this thesis is wrong if..." with at least two observable conditions, the checkpoint dates and the abort criterion.

### Split (an R, H or F conflict remains)

Never average across it. Present each position, its lens, the conflict tag and the assumption that drives it; the decision the user actually faces, stated as a trade-off; and what evidence would move it.

### Sizing

Run `scripts/sizing.py` on the scenario tree (returns from today's price to each case's value), the conviction tier and the user's tolerable drawdown. Report the adopted size, the binding constraint and the fragility probe. The doctrine is in `portfolio-optimization.md`.

**Sign-off 4 (sizing):** show the size and what binds it; the user decides.

---

## 8. Extrapolation clause

Permitted when the question outruns the published frameworks. All four requirements, no exceptions:

1. A block labelled `EXTRAPOLATION`.
2. Built from at least two lenses' frameworks in combination (name them).
3. A falsifiable checkpoint: the observable (KPI, filing line, guidance metric) that confirms or kills it within 2-4 quarters.
4. An abort criterion: the observation at which the thesis is reverted.

Typical uses: CBCV without disclosed cohort data (state the proxy chain), valuing a pre-FCF business with the lifecycle and TAM machinery, sizing an asset type the lenses never wrote about by mapping it onto their risk frameworks.

---

## 9. Comparing options

When the user compares discrete options (company A vs B, listing X vs Y, trim H1 vs H2), produce a weighted matrix:

| Criterion | Weight | Evidence |
|-----------|--------|----------|
| Business quality (ROCE durability, moat) | 0.25 | Quality and expectations checks, `screens.py` |
| Valuation gap (price vs value range) | 0.25 | `valuation.py` |
| Downside protection (worst-case loss, balance sheet) | 0.20 | Permanent-loss check, Altman Z |
| Conviction and circle of competence | 0.15 | Competence check |
| Sentiment and cycle asymmetry | 0.15 | Second-level check |

Weights are defaults; restate them and let the user adjust. Score 1-5 per cell with a one-line justification. The matrix ranks options for discussion; it does not replace section 7.

---

## 10. Deliverables

- **Thesis memo (`.md`)** for theses: answer first, then the evidence block, the cases, the cross-check table, the checks, the bear case, the verdict and the falsification block.
- **Spreadsheet (`.xlsx`)** for valuation models and portfolio reviews:
  - every derived cell is a live formula; only raw historicals, assumption drivers and market data are typed in;
  - typed inputs in blue with a source comment (source and date) on each;
  - the case selector drives one consolidation column; the sensitivity grids are full recalculations with the base case in the centre;
  - recalculate and confirm zero formula errors before handing it over.
- **Comparison widget** for option comparisons, when the environment supports it.

---

## 11. Thesis journal

Only when the user adopts a thesis or asks for it to be recorded, write `state/theses/<ticker>-<YYYY-MM-DD>.md` (schema in `state.md`): the claim, the cases and probabilities, the expected outcome, the checkpoints and abort criterion, the pre-mortem, the size and its binding constraint, and the decision. The journal is what `thesis-review.md` reads later.

---

## 12. Verify before emitting

Run `scripts/trace_check.py --draft <draft> --manifest <manifest> --sources sources.json` on any output with a number in it. Every number must trace to a script run, a dated source or an allow-comment. Fix the draft or the sources, never the check. Then cite: books, letters and memos are labelled as practitioner sources; empirical claims cite the study or dataset; everything from the pre-flight has a URL and a date.

---

## 13. Investor context

Read the user's investor-context file (`state/context.md`, SKILL.md rule 7) for standing constraints: tax residence and regime, preferred vehicles (for example fund-domicile rules), execution venue and broker, base currency, and portfolio style. Without one, ask for tax residence and base currency before any answer where tax or currency changes the conclusion.

- **Tax:** capital-gains and dividend taxation, withholding-tax treaties, and accumulating-vs-distributing fund treatment all materially affect net returns, and they change. **Verify current rates and rules via search whenever tax changes the conclusion; never rely on remembered rates.** Report results gross and net where the difference matters (dividend-heavy theses, fund domicile choices, short vs long holding treatment).
- **Vehicles:** flag product-availability or disclosure-document issues for funds domiciled outside the user's region.
- **Execution:** when a company lists in several venues, identify the liquid line on the user's preferred venues and in their base currency.
- **Currency:** state the FX exposure of every thesis explicitly (listing currency ≠ revenue currency ≠ cost currency).
- **Portfolio style:** apply the sizing doctrine in `portfolio-optimization.md` as the user's context file directs.

The skill surfaces the tax and structure consequences of an analysis; it does not provide individual tax advice, and says so once when tax is material.

---

## Gotchas

- **Aggregator numbers in the model.** Share counts and net debt from screeners are often stale or undiluted. Section 1.5 exists because extraction errors are the most common way an LLM valuation goes wrong.
- **Arithmetic in prose.** A DCF computed in sentences drifts. Every number comes from a script run.
- **Growth without reinvestment.** The script enforces the identity; a hand-built model must too.
- **A terminal value doing all the work.** Over 75% of EV is a claim about the far future; say it plainly.
- **Cloning 13Fs.** Manager positions are 45+ days old and say nothing about the thesis.
- **Persona drift.** Writing "as Klarman" invites invented positions. Name the lens and its source instead.
- **Backtested agents as evidence.** Published LLM-investor backtests are short and unreviewed; never cite one as support for a position.
- **Skipping sign-offs at Deep Dive depth.** A wrong input confirmed late costs the whole analysis.
