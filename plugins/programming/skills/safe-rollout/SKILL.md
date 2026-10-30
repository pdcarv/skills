---
name: safe-rollout
description: >-
  Builds a production rollout plan for a code, config, data-format or schema change: pre-prod
  and compatibility stages, a one-box or canary compared against a control, waves ordered by
  blast radius, explicit bake times with a minimum traffic volume, alarms with automatic
  rollback, deploy blockers and time windows, two-phase (prepare then activate) changes so
  rollback stays safe, feature flags with a safe default and a removal date, dark launches,
  and expand/contract schema migrations with online schema tools and their limits. Use when
  shipping a change to production, writing or reviewing a CD pipeline or rollout plan, asked
  "is this deploy safe?" or "can we roll this back?", changing a serialisation format, wire
  protocol, config semantics or database schema, or adding a feature flag or kill switch.
  Not for stopping live impact from a change already in production (mitigate-first).
license: MIT
metadata:
  category: "programming/delivery"
  sources: "see Sources section"
---

# Safe rollout

Most outages start with a change. The Google SRE Book (text dated early 2016) puts it at roughly 70% of outages due to changes in a live system, and pairs that with three practices: progressive rollout, fast and accurate detection, and safe rollback. This skill turns those into a written plan built from AWS's, Google's and Azure's published deployment procedures. The agent writes and checks the plan; every production action in it (deploy, promote, roll back, flip a flag, run a migration) is a proposal for a human to approve, never something the agent runs by default.

## When to use

- Any change heading to production: binary, config, data format, schema, flag.
- Writing or reviewing a deployment pipeline or rollout plan.
- A PR that changes what is written to storage or the wire (serialisation format, message schema, protocol field, timing contract such as a heartbeat interval).
- Adding, rolling out or removing a feature flag or kill switch.

## When not to use

- Users are affected right now: use `mitigate-first` (oncall-incident) to stop the bleeding, then come back.
- Designing cells, shuffle sharding or static stability: use `blast-radius-review` (software-architecture).
- Judging whether the code is correct: use `code-review-standard`.

## Inputs to gather

Read-only investigation first: read pipeline config, dashboards and alarm definitions; change nothing.

- What changes, and whether old code can read everything new code writes (data, messages, config, cache entries).
- Topology: regions, AZs, cells, hosts per service; which region has the least and most traffic.
- Traffic per stage, so you can tell how long a bake needs to reach a minimum request count.
- Existing SLIs, alarms and dashboards; whether alarms can be scoped to canary hosts.
- The rollback mechanism (previous immutable artifact? config revert? flag?) and whether it has been tested.
- Deploy tooling, blockers and windows already in place; on-call coverage for the rollout period.
- For schema changes: database engine, table size, replicas, foreign keys and triggers.

## Procedure

1. **Classify the change.** Record type (binary, config, data format, schema, flag) and reversibility. Decide which of steps 8-11 apply: an incompatible format means two-phase deploy; a schema change means expand/contract; user-visible behaviour means a flag; a re-implemented backend may suit a dark launch.
2. **Pre-production.** Require a production-like stage (same deployment configuration, monitoring, alarms and synthetic canaries) and a compatibility check that runs new code beside old (AWS uses a one-box in the pre-prod gamma stage, and a "Zeta" stage that calls only production endpoints). Note which of these exist and which are missing.
3. **First production unit: one-box or canary.**
   - AWS: one host, container or small share of invocations, serving at most 10% of a region's or AZ's traffic, with alarms scoped to that traffic.
   - Google: compare the canary against a control population over the same period, never before against after. Run one canary at a time. Pick a few metrics (perhaps no more than a dozen) ranked by user impact, starting from SLIs: error ratio and latency; exclude 4xx such as 404 and noisy machine metrics such as CPU. Each metric's interval must be no longer than the canary.
   - Promote, pause, roll back or escalate to a human based on canary-versus-control divergence, and also check absolute SLOs because both groups can drift together.
4. **Waves by blast radius.** Write each stage's scope:
   - Within a region, rolling batches of at most 33% of hosts so at least 66% stays healthy; capacity must survive losing one AZ (AWS).
   - Wave 1: one low-traffic region; wave 2: one high-traffic region; then widening groups. AWS gives 3 regions, then up to 12, then the rest as examples, one AZ or cell per region per step.
   - Azure's equivalent: a canary region pair, a pilot across diverse hardware, then broad rollout one AZ at a time and a region before its paired region.
5. **Bake times: explicit duration plus minimum traffic per stage.** The team sets the numbers; cite where they came from. Published examples:
   - AWS: at least 1 h after each one-box, at least 12 h after the first regional wave, 2-4 h after later waves, about 4-5 business days to reach all regions; bake also needs a minimum traffic volume, for example at least 100 requests to a "create" API.
   - AWS (continuous delivery article): an example gate of 3,000 positive data points with no negative ones.
   - Azure Well-Architected: measure bake in hours and days, not minutes, and lengthen it per group to cover time zones and usage patterns. Azure publishes no durations.
   - Google Workbook worked example: a 30-minute canary; duration should be long enough to represent the full deployment, shorter at higher request rates.
6. **Alarms and automatic rollback.** List per-service high-severity alarms: fault rate, P50/P90/P99 latency, CPU, memory, disk, errors in logs, failing health checks, plus anomaly detection for requests dropping to zero. Combine them with canary alarms into an aggregate alarm. Rollback reverts to the previous immutable artifact (verified by checksum) and stays armed during bake, not only during rollout. Azure adds: halt immediately on any end-user health alert, and include usage metrics so user silence does not hide a problem.
7. **Blockers, windows and the emergency path.**
   - No production deploy while the team's aggregate alarm is firing; also check company-wide alarms such as a major-event alarm.
   - Deploy only inside windows that exclude nights, weekends and holidays, and often Fridays and late afternoons. Windows too small let changes pile up; too large prolongs incidents.
   - Document the override for shipping a high-severity fix, and a pre-defined emergency path: who approves, which gates are shortened, how monitoring stays active.
   - If an artifact is known bad, block it in the pipeline; deleting the package does not stop pipelines that already include it.
8. **Rollback-safe format changes (two-phase deploy).** If old code cannot read what new code writes:
   1. Prepare: deploy a version that reads the new format but still writes the old one.
   2. Wait a backout period (AWS: usually a few days).
   3. Activate: deploy a version that writes the new format.
   4. Backfill existing data, and only then remove old-format reading.
   Verify every host updated at the end of each phase. Roll forward readers before writers; roll back writers before readers. Test it with several hosts across AZs: deploy to about half the fleet, then all, then roll back fully, each long enough for every API, workflow and batch job to run once.
9. **Feature flags.** For each flag record:
   - Type and lifetime (Hodgson): release (days to weeks, static), experiment (hours to weeks, per request), ops / kill switch (some long-lived; must flip without a deploy), permissioning (can last years).
   - Default value = the safe state (feature off or degraded). Under OpenFeature, the default is what callers get on any evaluation error, so the default is also the failure mode.
   - Exposure plan: Google's launch guidance grows exposure to a limited group, usually 1-10%, with each change revertible independently and immediately.
   - Owner, expiry date, removal ticket, and a time-bomb test that fails after expiry. Cap the number of active flags.
   - Tests: the expected production configuration, and the fallback with new flags off (off means legacy behaviour).
10. **Dark launch, where it fits.** For back-end behaviour behind interactions users do not choose, call the new path from existing flows behind a flag and hide its output, to measure load before launch. For a re-implementation, run old and new, compare, and return only the old result. Check hidden calls for side effects (writes, billing); that check is an inference, as the source covers performance only. For features users opt into, use a canary instead.
11. **Schema changes: expand/contract.** Never ship a backward-incompatible schema change in one step. Follow the sequence and the online schema tool guidance in [references/schema-migrations.md](references/schema-migrations.md), and write data-rollback steps explicitly, since stateful rollback is the hard case.
12. **Write the plan** with the template in Output and hand it to a human. Present each production step as a proposed command or pipeline action awaiting approval.

## Verification

Run this lint over the finished plan and report each item as pass, fail or not applicable, with the line of the plan that satisfies it:

- Pre-prod has a production-like stage and a new-beside-old compatibility check.
- A one-box or canary stage exists, is at most 10% of a region or AZ, has alarms scoped to it, and is compared against a control.
- Batches keep at least 66% capacity; wave 1 is one low-traffic region; one AZ or cell per region per step.
- Every stage has an explicit bake duration and a minimum request count, each with its source; none measured in minutes without justification.
- Alarms cover faults, P50/P90/P99 latency, resources, log errors, health checks and zero traffic; rollback is automatic and armed during bake.
- Blockers, windows, the override and the emergency path are written down.
- Any format change is two-phase with a backout period; any schema change is expand/contract with a contract date.
- Every flag has a type, a safe default, an owner, an expiry and a removal ticket.
- No step tells the agent to execute a production change itself.

## Gotchas

- **Before/after comparisons.** Time of day is a confounder; compare canary against control over the same window.
- **Stacked or contaminated canaries.** Two canaries at once, or a canary sharing backends, stores or clients with the control, muddies the signal.
- **A bake with no traffic proves nothing.** An overnight bake on a quiet region can pass without exercising the change. Gate on request count, not only on time.
- **Metric interval longer than the canary.** An hourly metric cannot judge a 30-minute canary.
- **Aggregate-only metrics.** Fleet-wide error rates hide a bad canary; split by canary and control.
- **minimumHealthyHosts.** CodeDeploy's setting can mark a deployment successful before every host has updated, which breaks the two-phase assumption that all hosts run the prepare version.
- **One server in test.** With a single host per service every deploy is atomic, so mixed-version bugs never show up until production.
- **Expand without contract.** If the contract phase never happens, you end up worse off than before: two schemas, two code paths. Put a date and an owner on it.
- **Flag default chosen for convenience.** A kill switch whose default is "on" fails open when the flag service is unreachable.
- **Flag debt.** Hodgson cites Knight Capital's $460 million loss as the warning about stale toggles.
- **Alternatives have costs.** Blue/green roughly doubles resources; synthetic load covers state poorly and is dangerous for billing-type systems; teeing traffic misleads in stateful systems.
- **Unverified dates.** The AWS Builders' Library articles were read on translated locale pages; original publication dates for the continuous-delivery and rollback-safety articles are unverified, and the wave sizes are AWS's examples, not current AWS-wide policy.

## Output

Hand back a filled rollout plan:

```markdown
# Rollout plan: <change> (<PR/ticket>)
Owner: <name>   On-call during rollout: <name>   Status: proposed (awaiting approval)

## Change
- Type: binary | config | data format | schema | flag    Reversible by artifact rollback: yes/no
- Old code reads new data: yes/no -> two-phase needed: yes/no
- Risk notes: <what could break, who is affected>

## Pre-production
| Stage | Exists? | Same config/alarms as prod? | New-beside-old tested? |

## Production stages
| # | Scope (region/AZ/cell/hosts) | Traffic share | Bake time (source) | Min traffic | Promote if | Roll back if |
|---|---|---|---|---|---|---|
| 1 | one-box, <region> | <=10% of AZ | <1 h (AWS example)> | <n requests> | canary vs control within <x> | aggregate alarm |
| 2 | wave 1: <low-traffic region>, one AZ at a time | ... | ... | ... | ... | ... |

## Detection and rollback
- Canary metrics (SLI-based, <= about 12): ...
- Aggregate alarm members: fault rate, P50/P90/P99, CPU, memory, disk, log errors, health checks, zero-traffic
- Rollback mechanism: <previous artifact / config revert / flag off>; tested on: <date or "not yet">
- Data rollback steps (stateful changes): ...

## Blockers and windows
- Blocks on: team aggregate alarm, <company-wide alarm>   Windows: <days/hours>
- Override for Sev fixes: <who>   Emergency path: <approver, gates shortened, monitoring kept>

## Two-phase / schema phases (if any)
| Phase | Deploys | Rollback safe because | Backout period | Done when |

## Flags
| Key | Type | Default (safe state) | Exposure steps | Owner | Expiry | Removal ticket |

## Proposed actions for human approval
1. <exact pipeline action or command>, run by <person>, after <condition>
```

## Sources

- AWS Builders' Library, "Automating safe, hands-off deployments", Clare Liguori, first published Jun 2020 (German locale page read Oct 2026; no direct quotes taken): https://aws.amazon.com/de/builders-library/automating-safe-hands-off-deployments/
- AWS Builders' Library, "Going faster with continuous delivery", Mark Mansour, original date unverified (German locale page read Oct 2026): https://aws.amazon.com/de/builders-library/going-faster-with-continuous-delivery/
- AWS Builders' Library, "Ensuring rollback safety during deployments", Sandeep Pokkunuri, original date unverified (German locale page read Oct 2026): https://aws.amazon.com/de/builders-library/ensuring-rollback-safety-during-deployments/
- Google SRE Book, ch. 1 Introduction (roughly 70% of outages from changes; text early 2016, published 2017): https://sre.google/sre-book/introduction/
- Google SRE Workbook, "Canarying Releases": https://sre.google/workbook/canarying-releases/
- Google SRE Book, ch. 27 "Reliable Product Launches at Scale" (staged rollout; flag framework, 1-10% exposure), 2017: https://sre.google/sre-book/reliable-product-launches/
- Azure blog, "Advancing safe deployment practices", Mark Russinovich, 5 Feb 2020: https://azure.microsoft.com/en-us/blog/advancing-safe-deployment-practices/
- Azure Well-Architected, OE:11 "Recommendations for safe deployment practices", last updated 2026-06-17: https://learn.microsoft.com/hr-hr/azure/well-architected/operational-excellence/safe-deployments
- Pete Hodgson, "Feature Toggles (aka Feature Flags)", martinfowler.com, revised 9 Oct 2017: https://www.martinfowler.com/articles/feature-toggles.html
- Martin Fowler, "Dark Launching", 29 Apr 2020: https://martinfowler.com/bliki/DarkLaunching.html
- OpenFeature, Evaluation API (default value returned on error), read Oct 2026: https://openfeature.dev/docs/reference/concepts/evaluation-api
- Schema migration sources are listed in references/schema-migrations.md.
