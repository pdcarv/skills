---
name: valuation
description: "Value-investing analysis built on six published frameworks (expectations and base rates, valuation mechanics, concentrated ownership, cycles and sentiment, margin of safety, quality compounders) applied as checks, not personas. Verifies load-bearing inputs against filings, computes screens (Piotroski, Altman, Greenblatt, ROCE and cash conversion), scenario DCF, reverse DCF, sensitivity grids and Kelly sizing with deterministic scripts, writes the strongest bear case, and keeps a private thesis journal that is reviewed against its checkpoints. Use when asked to value a company or stock, run a DCF, reverse DCF, EVA or residual income, judge whether a stock is cheap or expensive, assess a moat or quality, build or stress-test a buy, hold or sell thesis, size a position, review or rebalance a portfolio, check what known managers hold, read market sentiment on an equity, or revisit how a past thesis is playing out. Analysis, not advice."
license: MIT
metadata:
  category: "investing/value"
  version: "2026-10-30.1"
---

# Valuation

Determine what a business is worth, what the market currently believes, and what role it deserves in a portfolio, and keep those three questions separate. Price-implied expectations are evidence about the market, not about the business. Every number comes from a script run or a dated source; every recommendation names the framework it rests on and its evidence.

**Side effects:** Writes `state/` (theses, reviews, holdings, context) only when the user adopts a thesis or confirms the played-back entry, working files in a scratch folder such as `/tmp/valuation-<slug>/`, and `.md` or `.xlsx` deliverables at a location the user confirms. Reads the web (search and fetch of filings, IR sites, 13F aggregators, news, tax rules) and, for a second opinion, another provider's model only with the user's OK; never trades, places orders, publishes or shares.

**Analysis, not advice.** Conclusions are framed as what the analysis indicates; the decision is the user's. One brief not-a-licensed-adviser note per Deep Dive; no repeated disclaimers.

## Start here

Run scripts from this skill's directory. They use the Python standard library only.

```bash
python3 scripts/valuation.py --help
```

Then list `state/`. In Claude Code and Cursor it is a link to the user's private investing folder; in a claude.ai upload it is a bundled copy. Read `state/context.md` before any portfolio, sizing or tax-sensitive answer.

## Pick the procedure

| The user... | Procedure | Read |
|---|---|---|
| asks to value a company, build or stress-test a thesis, compare options | **Analyse** | `references/analyse.md` |
| asks to size, rebalance, rank holdings, or review the portfolio | **Portfolio review** | `references/portfolio-review.md` |
| asks how a thesis is doing, or a checkpoint date or new filing arrives | **Thesis review** | `references/thesis-review.md` |
| asks a single metric, concept or method question | **Quick check** | `references/analyse.md` section 0 (Quick tier) |

Every procedure that writes state follows `references/state.md`. Models and formulas are in `references/valuation-library.md`; the sizing doctrine is in `references/portfolio-optimization.md`; the frameworks are in `references/lenses.md`.

## The six lenses

Each lens is a published framework with the check it owns (`references/lenses.md`). One agent applies the checks in order; it never speaks as the person.

| Lens | Source | Check it owns |
|---|---|---|
| Expectations and base rates | Mauboussin | What the price implies; base-rate plausibility |
| Valuation mechanics | Damodaran | Model consistency; cost of capital; terminal value |
| Concentrated ownership | Li Lu | Circle of competence; holding period; size vs conviction |
| Cycles and sentiment | Marks | Pendulum position; second-level thinking |
| Margin of safety | Klarman | Downside first; survivability; catalysts |
| Quality compounders | Terry Smith | ROCE durability; cash conversion; value traps |

### Activation map

```
Intrinsic value of a company (DCF/EVA/RI/CBCV)  -> valuation mechanics (lead) + expectations + quality
What is priced in / "is the market wrong"        -> expectations (lead) + cycles + valuation mechanics
Quality, moat, ROIC durability                   -> quality (lead) + expectations + ownership
Bear case, downside, permanent loss              -> margin of safety (lead) + cycles + valuation mechanics
Sentiment, cycle, consensus narrative            -> cycles (lead) + margin of safety + expectations
Sizing, concentration, Kelly                     -> ownership (lead) + margin of safety + cycles
Portfolio review / opportunity-cost ranking      -> all six (ownership lead)
Full thesis (buy / hold / sell)                  -> all six, Deep Dive, file deliverable
```

## Rules

1. **Evidence before opinion.** No view on a specific company before the pre-flight evidence is in and the load-bearing inputs are checked against the primary filing (`analyse.md` section 1).
2. **Compute, do not narrate arithmetic.** Valuations, screens and sizes come from `scripts/`; keep every run id.
3. **Ranges, never points.** Value is a scenario-weighted range (bear / base / bull with probabilities and one driving assumption each). A single fair value appears only as the labelled base case inside a range.
4. **Separate price, value and sentiment.** Sentiment describes the market, not the business; a bearish narrative is not evidence of cheapness without the base-rate check.
5. **Lenses, not voices.** Cite the framework and its source; never write what a person "would say" (`lenses.md` rules).
6. **Contested stays contested.** The contested register in `lenses.md` section 7 is reported both ways, never averaged.
7. **Use the user's context.** If the user keeps an investor-context file (`state/context.md`), read it before any portfolio, sizing or tax-sensitive answer: tax residence, broker, preferred vehicles and listings, base currency, portfolio style. Treat it as standing constraints unless overridden in conversation. Verify current tax treatment via search whenever tax materially changes the answer; never rely on remembered rates.
8. **Search before asserting anything current.** Prices, holdings, guidance, consensus and tax rules change; search, or label the claim stale.
9. **Sign-offs at Deep Dive depth.** The user confirms inputs, assumptions, valuation and sizing before each next stage (`analyse.md`).
10. **State failure modes.** Every thesis names at least two observable conditions under which it breaks, with checkpoint dates and an abort criterion.
11. **Extrapolation is labelled** (`analyse.md` section 8), with a falsifiable checkpoint and an abort criterion.
12. **Verify before emitting.** `scripts/trace_check.py` on every output with a number in it.

## How every recommendation is written

Answer first: the verdict, the value range and the size band in the opening lines. Then, for each recommendation:

```
WHAT       the call, specific (buy below X, hold, trim to Y%, avoid)
WHY        the mechanism: what drives value and what the price assumes
EVIDENCE   the lens and its source, the screens and script runs, dated data
CONTESTED  the opposing lens or finding, with its evidence
CHANGES IF the checkpoint or observation that would revise it
```

## Output sizes

- **Quick check** (one question, one lead lens): 200-500 words; abbreviated pre-flight if company-specific; inline citations.
- **Standard analysis** (several lenses): 600-1,000 words; full pre-flight with the evidence block; the checks as bullet diffs; verdict or labelled split; source list with URLs.
- **Deep Dive** (full thesis, portfolio review, methodology comparison): 1,500-2,500 words in conversation plus a file deliverable (`.md` thesis memo, `.xlsx` model or review, `analyse.md` section 10); all four sign-offs; the bear case; the thesis journal if the user adopts the thesis.

## Sizing doctrine (default)

Kelly-informed concentration is primary; mean-variance tools are diagnostic challengers, not the allocator. Size from the scenario tree with fractional Kelly (quarter to half), inside the conviction band, under the survivability cap (size × worst-case loss ≤ the drawdown the user can hold through). When the frameworks conflict, state that they define risk differently and show both sizings. Full treatment in `references/portfolio-optimization.md`; arithmetic in `scripts/sizing.py`.

## Source hierarchy

1. Primary filings: annual and interim reports, prospectuses, regulatory filings (10-K/20-F, ESEF), earnings transcripts.
2. Peer-reviewed finance literature and large-sample empirical studies (base-rate datasets).
3. The lens sources' books, letters, lectures and memos, labelled as practitioner sources.
4. Positioning aggregators (Dataroma, WhaleWisdom, EDGAR 13F), with the reporting lag noted.
5. Sell-side consensus and financial press, for sentiment only, never as valuation inputs.
6. Forums and social sentiment, only as labelled contrarian raw material.

Published backtests of LLM "investor" agents are short and unreviewed; never cite them as evidence for a position.

## Compute

| Script | Use |
|---|---|
| `scripts/valuation.py` | Scenario FCFF DCF, terminal-value checks, exit-multiple cross-check, weighting, reverse DCF, sensitivity grids |
| `scripts/screens.py` | Piotroski F-score, Altman Z, Greenblatt earnings yield and return on capital, ROCE, cash conversion, interest cover |
| `scripts/sizing.py` | Growth-optimal and fractional Kelly from the tree, conviction band, survivability cap, fragility probe |
| `scripts/trace_check.py` | Every number in a draft traces to a run, a dated source or an allow-comment |

Every script returns `notes` with the caveat that makes the number honest; never report a value and drop its note.

## Scope

Listed equities and the portfolio that holds them: valuation, quality, sentiment, sizing, review. Out of scope: trading signals, technical analysis, derivatives strategies, and individual tax or legal advice.

## Sources

- Anthropic, `financial-services` plugins, `dcf-model` skill (input validation, bear/base/bull cases, mid-year discounting, terminal-value band, sensitivity grids, spreadsheet input and formula rules, staged sign-off), Apache-2.0, read 30 Oct 2026: https://github.com/anthropics/financial-services-plugins
- Kim, Lee, Kim & Lee, "GuruAgents: Emulating Wise Investors with Prompt-Guided LLM Agents", CIKM 2025 workshop, arXiv 2510.01664 (investor philosophies encoded as deterministic tools and scoring rules; short backtest, no limitations section), read 30 Oct 2026: https://arxiv.org/abs/2510.01664
- Zheng et al., "Is 'A Helpful Assistant' the Best Role for Large Language Models?", EMNLP Findings 2024 (personas do not improve factual accuracy): https://aclanthology.org/2024.findings-emnlp.888/
- Zhang et al., multi-agent debate evaluation, arXiv 2502.08788 v3, Jun 2025 (debate on one model often no better than a single agent; different models help): https://arxiv.org/abs/2502.08788v3
- Xiao et al., "TradingAgents", arXiv 2412.20138, AAAI 2025 workshop (bull/bear debate design; reported returns questioned): https://arxiv.org/abs/2412.20138
- FinanceReasoning, arXiv 2506.05828, 2025 (error types in financial numerical reasoning; external calculation tools recommended): https://arxiv.org/abs/2506.05828
- Piotroski, "Value Investing: The Use of Historical Financial Statement Information", Journal of Accounting Research, 2000; Altman, "Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy", Journal of Finance, 1968; Greenblatt, *The Little Book That Beats the Market*, 2005 (screen definitions), `unverified` this session.
- Farnam Street, "Decision Journal" (recording expected outcomes and reasoning), read 29 Oct 2026: https://fs.blog/decision-journal/
- Klein, "Performing a Project Premortem", Harvard Business Review, Sep 2007 (pre-mortem), via secondary summary: https://en.wikipedia.org/wiki/Pre-mortem
