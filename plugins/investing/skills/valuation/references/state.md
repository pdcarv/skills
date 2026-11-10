# State

The user's private investing data lives in `state/` (a link to a private folder outside the repository; in a claude.ai upload, a bundled copy). This file defines every file that may exist there, which procedure may write it, and its shape.

## Rules

1. **Created lazily.** A file is created the first time a procedure has real content for it. No templates, no placeholders.
2. **Only the named writer writes.** Every other procedure reads it only.
3. **Only what the user gave or a script computed.** Holdings and context come from the user or a document they supply, confirmed; never from memory or an earlier conversation that is not in state.
4. **Append, do not overwrite history.** Theses gain review sections; reviews gain entries; superseded values stay with a date.
5. **Working files stay out.** Manifests, `sources.json`, model inputs and drafts belong in a working folder outside `state/`.
6. **Report every write** at the end of the procedure: file and what changed.

## `context.md` — written by: the user; any procedure only when the user states a lasting change and confirms

Free text with the standing constraints: tax residence and regime, broker and preferred venues, preferred vehicles, base currency, portfolio style and horizon, the drawdown the user can hold through.

## `holdings.yaml` — written by: portfolio review; thesis review (decision changes only)

```yaml
schema_version: 1
as_of: 2026-10-30
base_currency: <ISO code>
positions:
  - ticker: ...
    listing: ...            # venue and currency
    shares: ...
    cost_basis: ...         # per share, base currency
    opened: YYYY-MM-DD
    tier: core | standard | opportunistic | tracking
    thesis: theses/<ticker>-<date>.md | null
cash: ...
source: "user statement YYYY-MM-DD"
```

## `theses/<ticker>-<YYYY-MM-DD>.md` — written by: analyse (creates); thesis review (appends)

```markdown
# Thesis: <company> (<ticker>)   Date: YYYY-MM-DD   Status: open | closed

## Claim
<one paragraph, answer first>

## Cases
| Case | Probability | Driving assumption | Value per share | Run id |
|---|---|---|---|---|

Expected outcome: <weighted value, horizon, expected annual return>
Reverse DCF at entry: <implied growth> (run id)

## Checkpoints
| # | Observable | Due | Hit if |
|---|---|---|---|
Abort criterion: <observation that reverts the thesis>

## Pre-mortem
<the most likely story of a 40% loss>

## Decision
Size: <adopted, binding constraint, run id>   Tier: ...   Decided by: user, YYYY-MM-DD

## Review YYYY-MM-DD
<appended by thesis-review.md>
```

## `reviews.md` — written by: portfolio review

Dated entries, newest last: the ranking, tier changes with their evidence, concentration findings, adopted weights, and the decisions the user took.
