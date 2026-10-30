---
name: mitigate-first
description: >-
  Stops customer impact before the root cause is known. Ranks suspect recent
  changes (deploys, config pushes, feature-flag flips, infrastructure and
  capacity changes) by time correlation and blast-radius match, then proposes one
  of the generic mitigations (rollback, data rollback, degrade, upsize, block
  list, drain, quarantine, restart) with preconditions, risk label, verification
  and revert steps. Every mitigation is a proposal that a human approves. Use
  when there is active customer impact, or someone asks "stop the bleeding",
  "should we roll back?", "what changed?", "which deploy broke this?", "drain the
  region?", or "how do we mitigate this now?". Not for root-cause work once
  impact has stopped (systematic-debugging) or for incident roles and comms
  (incident-command).
license: MIT
metadata:
  category: "oncall-incident/response"
  sources: "see Sources section"
---

# Mitigate First

During an outage the first job is to make the system work as well as it can, not to explain it. This skill gathers just enough evidence to classify the failure, ranks the recent changes most likely to be involved, and proposes the generic mitigation with the best chance of ending impact quickly and reversibly. Diagnosis continues afterwards. The agent investigates read-only and proposes; humans approve and execute.

## When to use

- Customers are affected now, or an SLO is burning fast.
- The question is "what changed?" or "should we roll back / drain / scale up?".

## When not to use

- No active impact and time to investigate: use the `systematic-debugging` skill.
- Running the incident itself (roles, comms): use `incident-command`.
- Rollout design for future changes: use the `safe-rollout` skill (programming plugin).

## Inputs to gather

- The signal showing impact (alert, SLI graph, error text) and the onset time with time zone.
- Scope: which regions, zones, cells, hosts, customers, endpoints or queries are affected, and which comparable ones are not.
- Change sources for the window: deploy history, config repo history, feature-flag audit log, infrastructure/IaC applies, capacity changes, cloud audit logs, upstream provider status.
- The service's pre-built mitigations (runbook, production readiness review) and the org's approval policy (who approves, two-person rules, peak-hour limits).

## Procedure

1. **Bound the impact.** For the user-facing service and each hop, read rate, errors and duration as a distribution (RED). Find the first hop where errors or latency changed, and the onset minute. Then split by location, version, customer and endpoint to separate affected from unaffected. Evidence: graph links with the time window and the affected/unaffected split.

2. **Preserve evidence before anything changes.** Mitigations such as restart, rollback and drain destroy state. Record the links, snapshot or export the relevant logs, and note the timestamps now.

3. **List what touched it last.** Collect every change in a window before onset (start wide, for example several hours, then narrow): binary deploys, config pushes, flag flips, schema or data migrations, infrastructure and capacity changes, dependency changes, traffic or load shifts. Cloud audit trails help for infrastructure:
   - GCP Admin Activity audit logs are always on: `gcloud logging read 'logName="projects/PROJECT_ID/logs/cloudaudit.googleapis.com%2Factivity"'`
   - AWS CloudTrail, example for ALB target deregistration: `aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=DeregisterTargets --start-time <t0> --end-time <t1>` `# unverified`
   Narrow deterministically before ranking: drop changes whose owner, code path or dependency graph cannot reach the affected service. This mirrors Meta's retriever, which cut thousands of candidates to a few hundred before any model ranked them.

4. **Rank the suspects.** Score each remaining change on the rubric below (this rubric is this skill's synthesis, inspired by Meta's published approach; it is not Meta's algorithm). With many candidates, rank in batches of at most 20 and carry the best forward until a top 5 remains.

   | Factor | Strong match | Weak or no match |
   |---|---|---|
   | Time correlation | Change reached the affected scope minutes before onset; impact grew as the rollout progressed | Landed long before onset, or after it |
   | Blast-radius match | Change's footprint covers exactly the affected scope and not the unaffected scope | Change is everywhere but impact is local, or vice versa |
   | Path | Touches the failing hop or its direct dependency | Unrelated service, no dependency path |
   | Signal fit | The change plausibly produces the observed symptom (errors vs latency vs saturation) | Mechanism does not fit the symptom |

   For each of the top 5, write the evidence and a confidence level. If no candidate is better than weak, say "no confident suspect" instead of naming one; Meta withholds low-confidence answers for this reason.

5. **Classify the failure just enough to choose.** Answer: is it everywhere or localized? Tied to one change? Load-driven? Driven by one input, user or key? Is stored data damaged? This decides which mitigations can work.

6. **Choose a mitigation.** From the table, pick the one that fits the classification with the least destructive risk. The generic set (Mace) is used without understanding the outage fully; restart and add-capacity appear in Google's Gemini CLI closed set.

   | Mitigation | Use when | Preconditions and checks | Default risk label |
   |---|---|---|---|
   | Rollback | A suspect binary or config change correlates with onset | A known-good version exists; the rollback path has been tested; any data or schema change in between confirmed compatible by its owner | Reversible |
   | Data rollback | Stored data was corrupted | A restore point predating the damage; writes after it are understood and accounted for | Destructive (treat as such by default) |
   | Degrade | Overload or a failing non-critical feature | A degraded mode already built and tested; never build one mid-outage | Reversible |
   | Upsize | Capacity or load driven, not a bad release | Adds replicas; depends on control-plane calls and quota during the event; useless against a bad release everywhere or a retry storm | Reversible |
   | Block list | A query of death or an abusive user | The offending pattern is identified precisely enough to block without collateral | Reversible |
   | Drain | Impact is localized to one location | The service is multi-homed and the remaining locations can take the load | Reversible |
   | Quarantine | A hot row, user or stream drives the failure | The hot item is identified; isolating it leaves the rest serving | Reversible |
   | Restart | Suspected bad process state | Evidence preserved first; if restart fails and only this job fails, suspect binary or config instead | Reversible, but loses in-memory state |

   Reverting a recent flag flip or config push is the rollback pattern applied to that change. Mace's article does not list flag disable separately.

7. **Write the proposal and stop.** Use the proposal block in Output: exact action and parameters, scope, risk label, policy check (peak traffic, two-person rule), expected effect, verification signal, revert step. Do not execute. Wait for explicit approval from the IC or the approver the org names. Approval covers that one action only.

8. **Verify after a human executes it.** Watch the same SLI that showed impact, at the scope that was affected. Agree in advance how long to wait. If it does not improve, propose reverting the mitigation and move to the next candidate. Log the result, positive or negative, in the incident doc's divergence list.

9. **Hand over to diagnosis.** Once impact has stopped, the proximate fix stands and root-cause work proceeds without time pressure (`systematic-debugging`). Track time to mitigate separately from time to fix.

## Verification

- The affected/unaffected split is backed by graphs, not by one report.
- Each top-5 suspect has a timestamp, scope, path and evidence link; a human can reproduce the reasoning from those alone.
- The chosen mitigation's preconditions are checked one by one, with evidence (for example, multi-homing and spare capacity confirmed before proposing a drain).
- The proposal names a verification signal and a revert step before approval is requested.
- After execution, recovery is shown on the original SLI, not inferred from the action completing.

## Gotchas

- **Diagnosing too long.** Proximate fixes need not wait for root cause. Mace: "You don't need to fully understand your outage to use it."
- **Draining when the bad release is everywhere.** Draining one location does nothing if every location runs the bad version. Check the scope split first.
- **Upsizing into a retry storm.** With 5 layers each retrying 3 times, backend load can rise 243 times. Added replicas feed the storm; block list or degrade usually works better.
- **Upsize depends on the control plane.** Launching capacity calls control-plane APIs, which are more failure-prone than data planes and may be impaired in a regional event. Prefer mitigations that need no control-plane call when the provider is degraded.
- **Restart destroys evidence.** Snapshot first. A restart that does not help, while sibling jobs are healthy, points at binary or config.
- **Spurious correlation.** Something always deployed recently, and more metrics produce more coincidences. Require scope and path match, not just timing.
- **Ranking accuracy is modest.** Meta's backtest found the root cause in the top 5 for 42% of web-monorepo investigations. Present suspects as hypotheses for humans to validate.
- **Rollback across a data or schema change.** If a migration landed between the known-good version and now, have the owner confirm the old version can run against the current data before proposing the rollback.
- **Un-drilled mitigations.** A rollback or degraded mode never exercised may have unknown side effects. Say so in the proposal's risk line.
- **Unlogged changes.** Every mitigation is a divergence from normal and must be unwound later; if it is not in the log, it will be forgotten.

## Output

Suspect changes (top 5, or "no confident suspect"):

```markdown
| # | Change (link) | Type | Landed (TZ) | Scope | Path to failing hop | Evidence | Confidence |
|---|---|---|---|---|---|---|---|
| 1 | ... | deploy/config/flag/infra | ... | ... | ... | ... | high/med/low |
Excluded during narrowing: <count> changes (reason: no owner or dependency path)
```

Mitigation proposal (one per action; requires explicit approval):

```text
PROPOSED ACTION: <rollback|data rollback|degrade|upsize|block list|drain|quarantine|restart> <exact target and parameters>
Why: <failure classification + top suspect + evidence links>
Scope / blast radius: <instances/cells/zones/regions/customers touched>
Risk label: safe | reversible | destructive   Drilled before: yes/no/unknown
Policy check: peak traffic? <y/n>  two-person approval needed? <y/n>  other: <...>
Expected effect: <which SLI should recover, at which scope, within how long>
Verify by: <query/graph>          Revert by: <exact step>
Evidence preserved: <links/snapshots>
Approval: PENDING (approver: <name/role>)
```

## Sources

- Jennifer Mace, "Generic mitigations", O'Reilly, 15 Dec 2020. https://www.oreilly.com/content/generic-mitigations/
- Google SRE Book (2016), ch. 12 "Effective Troubleshooting" (stop the bleeding, what touched it last, pitfalls). https://sre.google/sre-book/effective-troubleshooting/ (read Oct 2026)
- Meta Engineering, "Leveraging AI for efficient incident response", 24 Jun 2024. https://engineering.fb.com/2024/06/24/data-infrastructure/leveraging-ai-for-efficient-incident-response/
- Google Cloud blog, "How Google SREs use Gemini CLI to solve real-world outages", 22 Jan 2026. https://cloud.google.com/blog/topics/developers-practitioners/how-google-sres-use-gemini-cli-to-solve-real-world-outages
- Grafana Labs, "The RED method", Aug 2018. https://grafana.com/blog/2018/08/02/the-red-method-how-to-instrument-your-services/
- Marc Brooker, "Timeouts, retries, and backoff with jitter", Amazon Builders' Library, 5 Dec 2019. https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter
- AWS Fault Isolation Boundaries whitepaper, "Control planes and data planes" (undated, read Oct 2026). https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/control-planes-and-data-planes.html
- GCP Cloud Audit Logs overview (updated 2026-10-26). https://docs.cloud.google.com/logging/docs/audit
- AWS re:Post Knowledge Center, ALB 502 troubleshooting (CloudTrail `DeregisterTargets`). https://repost.aws/knowledge-center/elb-alb-troubleshoot-502-errors (read Oct 2026)
