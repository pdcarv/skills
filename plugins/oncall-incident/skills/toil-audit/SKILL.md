---
name: toil-audit
description: >-
  Inventories a team's operational work, classifies it against Google SRE's
  definition of toil (manual, repetitive, automatable, tactical, no enduring
  value, scales linearly with growth), measures toil against the 50% cap, and
  ranks candidates for automation or elimination. Use when someone asks what to
  automate, reviews on-call load or interrupt work, says the team is drowning in
  tickets or pages, plans reliability engineering time, or asks "how much toil
  do we have?".
license: MIT
metadata:
  category: "oncall-incident/reliability"
  sources: "see Sources section"
---

# Toil Audit

Find the operational work that grows with the service and returns nothing lasting, measure how much of the team's time it takes, and rank what to automate or design away first. Google's SRE book defines toil by six traits and caps it at 50% of each SRE's time, with the rest spent on engineering that reduces future toil. This skill turns that into an evidence-based inventory and a ranked plan.

## When to use

- Quarterly or periodic on-call load review; planning an automation backlog.
- A team reports too many tickets, pages or manual requests.
- Deciding whether an engineer's or rotation's operational load is sustainable.

## When not to use

- Paging noise caused by alert design: use `slo-burn-rate-alerts` first; it removes pages rather than automating responses to them.
- Building the automation itself, if it acts on production: follow `production-safe-agent`.

## Inputs to gather

- The audit period (for example the last quarter) and the people or rotation in scope.
- Data sources: ticket queue exports, paging history, on-call handoff notes, incident docs, chat request channels, runbook execution logs, any time tracking.
- Each person's approximate working hours in the period (to compute shares).
- Growth drivers: expected growth in traffic, customers, services or regions.

## Procedure

1. **Inventory recurring operational tasks.** Group the raw items (tickets, pages, requests) into task types. For each: trigger, frequency in the period, typical hands-on time per occurrence, who does it, and what makes it grow. Evidence: the query or export each count came from.

2. **Classify each task against the six traits.** Mark yes or no for each:
   - manual (a human does it by hand);
   - repetitive (done again and again, not once);
   - automatable (a machine could do it);
   - tactical (interrupt-driven and reactive, not planned);
   - no enduring value (the service is no better afterwards);
   - O(n) with growth (effort scales with service size or traffic).
   The more traits a task has, the more toil-like it is. Using the trait count as a ranking signal is this skill's convention, not Google's.

3. **Remove what is not toil.** Exclude overhead (meetings, hiring, planning, admin), first-time or novel work, and grungy work with lasting value (for example cleaning up alert configuration). Record the reason for each exclusion so the totals can be audited.

4. **Measure toil share.** Per person or rotation: toil hours / total working hours in the period. Flag anyone above 50%, and anyone trending toward it as growth drivers kick in. Evidence: the arithmetic, with assumptions (estimated minutes per task) marked as estimates.

5. **Rank candidates.** For each toil task estimate:
   - hours per period now, and projected after expected growth (O(n) tasks grow);
   - effort to automate or eliminate;
   - risk of the fix: does the automation act on production? If so it needs the guardrails in `production-safe-agent`.
   Prefer eliminating a task by design change (stop the thing needing to be done) over scripting the manual steps. Order by hours saved over the next period relative to effort, with risk as a tiebreaker.

6. **Propose the plan.** Top items with owner, approach (eliminate / automate / self-service / alert redesign), expected hours saved, and the measurement that will show it worked. Confirm the top items with the people who do the work; they know the hidden steps.

## Verification

- Totals reconcile: task hours sum to the toil total; toil plus excluded work does not exceed total hours.
- Every count traces to an export or query; every estimate is labelled as one.
- Every exclusion has a reason; no meeting or one-off project is counted as toil.
- The 50% check is done per person or rotation, not only as a team average.
- Top-ranked items were sanity-checked with at least one person who does the work.

## Gotchas

- **Calling all ops work toil.** Overhead and novel problem-solving are not toil; counting them inflates the number and loses credibility.
- **Grungy but valuable work.** Cleaning up alert configuration is unpleasant but has lasting value; it is not toil.
- **Team averages hide hot spots.** One person on a heavy rotation can be far above 50% while the team average looks fine.
- **Ignoring growth.** O(n) tasks that are small now become dominant as the service grows; rank on projected hours, not just today's.
- **Under-reported interrupts.** Quick chat requests and "can you just" pings rarely reach the ticket queue. Sample chat channels and handoff notes.
- **Automating a page instead of fixing the alert.** If a page needs no human action, change the alerting (SLO-based alerts) rather than scripting an acknowledgment.
- **Automation that touches production unsafely.** Scripts that restart, scale or delete need risk labels, approval and logging like any other production action.
- **50% is a ceiling, not a target.** The rest of the time is meant for engineering that reduces future toil.

## Output

```markdown
# Toil audit: <team / rotation>, <period>
Data sources: <exports/queries>   People in scope: <n>   Assumptions: <estimates used>

## Toil share
| Person / rotation | Total hours | Toil hours | Toil % | Above 50%? |

## Inventory
| Task | Trigger | Freq/period | Min/occurrence | Hours/period | Manual | Repetitive | Automatable | Tactical | No enduring value | O(n) | Traits (of 6) |

## Excluded (not toil)
| Item | Reason (overhead / novel / lasting value) |

## Ranked candidates
| Rank | Task | Hours now | Hours after growth | Approach (eliminate/automate/self-service/alert fix) | Effort | Touches prod? | Owner | Success measure |
```

## Sources

- Google SRE Book (2016), ch. 5 "Eliminating Toil" (six traits, what is not toil, 50% cap). https://sre.google/sre-book/eliminating-toil/ (read Oct 2026)
- Google SRE Workbook, ch. 5 "Alerting on SLOs" (alerts that fire while the SLO is met). https://sre.google/workbook/alerting-on-slos/ (read Oct 2026)
- Google Cloud blog, "How Google SREs use Gemini CLI to solve real-world outages", 22 Jan 2026 (risk-labelled tools and approval for production automation). https://cloud.google.com/blog/topics/developers-practitioners/how-google-sres-use-gemini-cli-to-solve-real-world-outages
