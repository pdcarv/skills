# investing

Investing analysis skills. They produce analysis, not financial advice.

| Skill | Use it for |
|---|---|
| `valuation` | Analyse a company or thesis (filing-verified inputs, Piotroski/Altman/Greenblatt/quality screens, scenario and reverse DCF with sensitivity grids, six framework checks, a written bear case, staged sign-off), size positions (fractional Kelly, conviction bands, survivability cap), review the portfolio, and review recorded theses against their checkpoints. |

## Setup

The skill keeps your private data (investor context, holdings, theses, reviews) in a folder outside this repository and reaches it through a `state/` link that git ignores:

```bash
mkdir -p <private-folder>/investing/state
ln -s <private-folder>/investing/state plugins/investing/skills/valuation/state
```

Replace `<private-folder>` with a folder outside this repository that only you can read.

Put your standing constraints (tax residence, broker and venues, base currency, portfolio style, tolerable drawdown) in `state/context.md`. Everything else is created by the skill's procedures, only when there is something to record.

## Tests

The scripts use the Python standard library only:

```bash
python3 plugins/investing/tests/valuation/test_scripts.py
```

License: MIT
