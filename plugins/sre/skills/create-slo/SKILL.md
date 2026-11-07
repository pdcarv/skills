---
name: create-slo
description: >-
  Defines SLIs, SLOs and error budgets for a service and generates multiwindow,
  multi-burn-rate alert rules (Google SRE Workbook method) in a tool-neutral
  form that can be translated to Prometheus, Cloud Monitoring, CloudWatch, Azure
  Monitor, Datadog or similar. Includes the budget arithmetic, the
  page/page/ticket table, the 1/12 short-window rule and low-traffic caveats.
  Use when someone asks to set up or fix SLO alerts, define an SLO or error
  budget, compute a burn rate, or complains of too many, too few, noisy or late
  pages for a service.
license: MIT
metadata:
  category: "sre/reliability"
  sources: "see Sources section"
---

# Create SLO

Alert on how fast a service is spending its error budget, not on raw error rates. The SRE Workbook compares six alerting approaches and recommends multiwindow, multi-burn-rate alerts: they page quickly for fast burns, open tickets for slow ones, stop firing soon after recovery, and rarely fire while the SLO is still being met. This skill produces the SLO definition, the budget arithmetic, and alert definitions in a neutral form that the user's monitoring tool can implement.

**Side effects:** Writes the SLO definition, budget arithmetic and alert rules, handed back to the user; reads SLI history through the user's monitoring tool only when backtesting with access given. Never creates, changes or deletes SLOs or alerts in the monitoring tool.

## When to use

- Defining or revising an SLO, error budget or SLO-based alerting for a service.
- Pages are noisy (fire while users are fine), late (big outages page slowly) or sticky (keep firing long after recovery).

## When not to use

- Alerts on causes such as CPU or disk with no user-facing SLO: start by defining the SLI here, or treat them as tickets and dashboards.
- Choosing the SLO target itself is a product decision; this skill computes consequences but the owner chooses.

## Inputs to gather

- The user-facing service and its request path; what "good" means to a user (success, and fast enough).
- Where the SLI can be measured (load balancer, service metrics, client/synthetic) and its query language.
- Traffic volume over a typical period, including the quietest hours.
- The SLO target and period the owners want (for example 99.9% over 30 days), and any existing SLO documents.
- Paging policy: what may page a human, what should be a ticket.

## Procedure

1. **Choose the SLI.** Express it as a ratio: good events / valid events. Use RED as the checklist: request rate (the denominator), errors (availability SLI), duration (latency SLI, as "fraction of requests faster than X", measured from the distribution, not the average). Evidence: the exact numerator and denominator queries, and what is excluded from "valid".

2. **Fix the SLO and compute the error budget.** Budget = 1 − SLO over the period. For 99.9% over 30 days, the budget is 0.1% of requests, the same as about 43.2 minutes of total outage (derived: 30 × 24 × 60 × 0.001). Record the target and period as the owner's decision.

3. **Use burn rate as the alert variable.** Burn rate = observed error rate / (1 − SLO). A constant 0.1% error rate against a 99.9% SLO is burn rate 1: the budget lasts exactly the period. Budget consumed in a window = burn rate × window / period.

4. **Emit the three-row alert set.** Google's recommended parameters for a 99.9% / 30-day SLO:

   | Severity | Burn rate | Long window | Short window | Budget consumed when it fires | Error-rate threshold at 99.9% (derived) |
   |---|---|---|---|---|---|
   | Page | 14.4 | 1 hour | 5 minutes | 2% | 1.44% |
   | Page | 6 | 6 hours | 30 minutes | 5% | 0.6% |
   | Ticket | 1 | 3 days | 6 hours | 10% | 0.1% |

   Each row fires only when both windows exceed the burn rate. The short window is 1/12 of the long one; its job is to make the alert stop soon after the problem is fixed.

5. **Adapt to other targets and periods.** Keep the budget fractions (2%, 5%, 10%) and windows, and recompute burn rate = budget fraction × period / long window. Check: 0.02 × 720 h / 1 h = 14.4. The error-rate threshold is burn rate × (1 − SLO). For a different SLO target with the same 30-day period, the burn rates stay the same and only the thresholds move.

6. **Check for low traffic.** Compute requests per period N and allowed failures N × (1 − SLO). Example from the Workbook: at 10 requests per hour, a 30-day 99.9% SLO allows only about 7 failures, and a single failure uses 13.9% of the budget. A single failed request in a quiet hour is then a 10% error rate (derived), far above the 1.44% page threshold, so the fast-burn rule pages on one failure. If allowed failures are this small, propose one or more of:
   - synthetic traffic to raise the request count;
   - combining small services that share a failure domain into one SLO;
   - product changes: client retries with exponential backoff and jitter, fallbacks;
   - lowering the SLO or lengthening the window (the owner's call).

7. **Write the definitions** in the Output form, one SLO block and three alert rules, then translate to the user's tool if asked. Keep thresholds as parameters derived from the SLO, not hand-typed constants.

8. **Backtest if history exists.** Replay past weeks of the SLI through the rules: count how many pages and tickets would have fired, and check that known incidents would have paged and quiet periods would not.

## Verification

- Recompute each row: burn rate × long window / period gives 2%, 5% and 10%; each short window is the long window / 12 (60/12 = 5 min, 6 h/12 = 30 min, 72 h/12 = 6 h).
- Detection-time check (derived): for a sudden error rate e, the long window crosses the threshold after about long window × threshold / e. For a total outage at 99.9%, the 1-hour rule needs 1.44% of an hour, under a minute.
- Reset-time check: after recovery, a paging alert should clear within roughly its short window.
- Low-traffic check done and recorded (allowed failures per period stated).
- No rule uses a `for:`/duration clause as its main control.
- Thresholds in the translated rules match the table for the chosen SLO.

## Gotchas

- **Threshold equal to the SLO.** Alerting whenever the error rate exceeds the SLO over a short window fires constantly; the Workbook counts up to 144 alerts a day while the SLO is still met.
- **One long window.** A 36-hour window catches slow burns but keeps firing for about 36 hours after a fix.
- **Duration clauses.** Adding `for:` makes a 100% outage alert after the same hour as a 0.2% one. Not recommended as the main control.
- **Single burn-rate alert.** A lone 1-hour alert at 36x never fires for a 35x burn, which still empties a 30-day budget in about 20.5 hours.
- **Multiple burn rates without suppression.** Several rules fire for one incident; configure the tool's grouping or inhibition so one incident yields one page.
- **Averages for latency.** An average hides the tail; base the latency SLI on the distribution.
- **Low traffic.** Quiet services page on single failures. Fix the traffic or the SLO design, not the alert threshold alone.
- **Too many parameters.** The recommended scheme has many knobs; generate them from the SLO with a formula so they stay consistent when the target changes.

## Output

Tool-neutral SLO and alert definitions:

```yaml
slo:
  service: <service>
  sli:
    kind: availability            # or latency
    good: <query for good events>   # latency: requests with duration <= <threshold>
    valid: <query for valid events>
  target: 0.999
  period: 30d
  error_budget: 0.001             # 1 - target; ~43.2 min of full outage per 30d
  traffic_check: {requests_per_period: <N>, allowed_failures: <N * 0.001>, low_traffic: <true|false>}

definitions:
  error_rate(w): 1 - good(w) / valid(w)
  burn_rate(w): error_rate(w) / (1 - target)

alerts:
  - name: <service>-slo-burn-fast
    condition: burn_rate(1h) > 14.4 AND burn_rate(5m) > 14.4
    route: page
    budget_consumed_at_fire: 2%
  - name: <service>-slo-burn-medium
    condition: burn_rate(6h) > 6 AND burn_rate(30m) > 6
    route: page
    budget_consumed_at_fire: 5%
  - name: <service>-slo-burn-slow
    condition: burn_rate(3d) > 1 AND burn_rate(6h) > 1
    route: ticket
    budget_consumed_at_fire: 10%
notes:
  - suppress slower rules while a faster rule for the same SLO is firing
  - low-traffic mitigation chosen: <none | synthetic traffic | grouping | retries/fallbacks | SLO change>
```

Also hand back: the backtest result (alerts per week, incidents caught or missed) or "no history available".

## Sources

- Google SRE Workbook, ch. 5 "Alerting on SLOs" (burn rate, six approaches, recommended table, 1/12 rule, low-traffic options). https://sre.google/workbook/alerting-on-slos/ (read Oct 2026)
- Grafana Labs, "The RED Method: How to instrument your services", Aug 2018 (rate, errors, duration distribution). https://grafana.com/blog/2018/08/02/the-red-method-how-to-instrument-your-services/
