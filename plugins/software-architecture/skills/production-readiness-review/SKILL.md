---
name: production-readiness-review
description: >-
  Runs a Google SRE-style Production Readiness Review (PRR) before a launch or an
  operational handover: agree goals and an SLO, analyse the service against a checklist
  (architecture and dependencies; instrumentation, metrics and monitoring; emergency
  response; capacity planning; change management; performance), review past incidents,
  and produce a readiness report with prioritised gaps, owners and a handover plan. Use
  when asked "are we ready to launch?", "is this production-ready?", for a PRR, launch
  readiness review, operational readiness review, go-live checklist, or before SRE or an
  ops team takes over a service.
license: MIT
metadata:
  category: "software-architecture/launch"
  sources: "see Sources section"
---

# Production readiness review

Check that a service meets accepted production standards, that its owners are ready to run it, and that the expected number and severity of incidents goes down before launch rather than after. The procedure follows the six PRR phases in Google's SRE book and its checklist areas, extended with the launch-checklist areas from the SRE book's chapter on reliable launches. The deliverable is a readiness report: one row per area with status, evidence, gap, owner and priority.

## When to use

- Before a launch, a major feature going live, or a big traffic change.
- Before an operations or SRE team takes over on-call for a service.
- Early, at design or build time: the SRE book argues for engaging early, when fixes are cheapest.

## When not to use

- The design is not written yet: `design-doc` first, then PRR at build time.
- A single concern needs a deep dive: retries and overload (`timeout-retry-overload-review`), AZ/Region failure (`blast-radius-review`), rollout mechanics (`safe-rollout`, programming plugin), SLO alerting (`slo-burn-rate-alerts`, oncall-incident plugin). Call them from inside the PRR.
- A cloud framework review is what is being asked for: `well-architected-review`.

## Inputs to gather

- Service description, design doc, architecture diagram and the list of dependencies (internal and external).
- The proposed SLO (or SLA) and the user-facing SLIs; the launch date and expected traffic.
- Dashboards, alerts, runbooks and the on-call rota.
- Past incidents and postmortems for this service and close relatives.
- Load test results, capacity plan, rollout plan and rollback plan.
- Who the reviewers are, who owns the service, and who will own operations after handover.

## Procedure

1. **Engagement.** Agree the goals with the owning team: the SLO or SLA, planned design changes, launch date and what "ready" means. Name the reviewers (Google assigns one to three SREs). Evidence: written goals and SLO.
2. **Analysis: run the checklist.** For each area, collect evidence and mark Ready, Gap or Unknown:
   - **Architecture and inter-service dependencies:** dependency list with each one's failure behaviour; external dependencies; integration points. Deep dives: `blast-radius-review`, `timeout-retry-overload-review`.
   - **Instrumentation, metrics and monitoring:** SLIs measured, dashboards, alerts tied to the SLO, logs and traces sufficient to debug. Deep dive: `slo-burn-rate-alerts`.
   - **Emergency response:** on-call rota, runbooks, escalation path, rollback and other mitigations practised. Deep dive: `runbook-author`.
   - **Capacity planning:** load test at expected peak and beyond (load testing is required for most launches in Google's launch chapter), headroom for zone loss, quotas. Some launches saw traffic up to 15 times the estimate; ask what happens at a multiple of forecast.
   - **Change management:** progressive rollout, detection signals defined before rollout, tested rollback. The SRE book's introduction attributes roughly 70% of outages to changes in a live system (text as of early 2016). Deep dive: `safe-rollout`.
   - **Performance:** availability, latency and efficiency against the SLO.
   - **Launch-specific areas** from the launch checklist: client behaviour (clients back off exponentially, jitter scheduled requests, and accept server-side control of sync and retry intervals), failure modes, processes and automation, development process, rollout planning.
3. **Review past incidents and postmortems.** For each, check that the action items are done or tracked, and whether the same failure mode could recur at launch scale. Evidence: links and status.
4. **Improvements and refactoring.** Turn every Gap into an item with a priority, owner and date. Prioritise and negotiate them with the owning team; the PRR does not unilaterally assign work. Mark launch-blocking items explicitly.
5. **Training.** List the material the receiving team needs: a design overview, a request-flow deep dive, the production setup, and hands-on exercises (for example a game day or rollback drill).
6. **Onboarding (handover).** Plan a gradual transfer of operations, change management and access, with the development team as backup during the transition. Write the stages and the criteria for each.
7. **Continuous improvement.** Define how lessons from changes and incidents flow back to the development team (postmortem reviews, `blameless-postmortem`), and when the PRR is revisited.
8. **Write the readiness report** (Output). Give an overall verdict: ready, ready with conditions (named blocking items), or not ready.

## Verification

- Every checklist area has a status and at least one piece of evidence (link, config, dashboard, test result), or is marked Unknown with what is missing.
- The SLO is written down and agreed; monitoring and alerts reference it.
- Every Gap has an owner (a name from the user, or "TBD - ask"), a priority and a date; blocking gaps are marked.
- Past incidents were reviewed, with action-item status.
- The handover plan has stages and criteria, and the development team is named as backup.
- No production change was made during the review; fixes are proposals.

## Gotchas

- **Late PRRs are expensive.** Findings at launch week become waivers. Run a light pass at design time and a full one before launch.
- **Unknown is not Ready.** Missing evidence is a gap in itself: an untested rollback or an alert nobody has seen fire.
- **Owners are not the agent's to assign.** Ask; record "TBD - ask" rather than guessing names.
- **Load tests at forecast only** miss the launches that overshoot. Test the knee and the behaviour past it (`timeout-retry-overload-review`).
- **Platform controls vs app logic.** Google moved many readiness controls (load shedding, monitoring, traffic management) into SRE-supported frameworks, while developers own application logic. If the organisation has a standard framework or platform, check the service uses it rather than re-reviewing each control by hand.
- **Dark launches** are a readiness tool: exercising a new backend with hidden results reveals load problems before users depend on it. Suggest one where traffic risk is high.
- **Generic checklist drift.** Google's PRR uses a service-specific checklist. Tailor the areas to the service; do not pad the report with items that do not apply.

## Output

```markdown
## Production readiness review: <service>   Launch/handover date: <...>   Review date: <...>
Reviewers: <...>   Service owners: <...>   Receiving team: <...>
SLO agreed: <SLI, target, window>   Verdict: ready | ready with conditions | not ready
Summary: <3-5 sentences: the verdict, the blocking gaps by name, what must happen before
launch, and the next review date>

### Readiness by area
| Area | Status (Ready/Gap/Unknown) | Evidence | Gap | Owner | Priority | Due | Blocks launch? |
|---|---|---|---|---|---|---|---|
| Architecture and dependencies | | | | | | | |
| Instrumentation, metrics, monitoring | | | | | | | |
| Emergency response | | | | | | | |
| Capacity planning | | | | | | | |
| Change management | | | | | | | |
| Performance | | | | | | | |
| Client behaviour / failure modes / rollout planning | | | | | | | |

### Past incidents reviewed
| Incident/postmortem | Recurrence risk at launch | Action items status |

### Training plan
### Handover plan (stages, criteria, dev team as backup)
### Continuous improvement loop and next review date
```

## Sources

- Google SRE book, ch. 32 "The Evolving SRE Engagement Model" (PRR objectives, six phases, checklist areas, early engagement, dark launches, production-ready frameworks), 2016, read Oct 2026: https://sre.google/sre-book/evolving-sre-engagement-model/
- Google SRE book, ch. 27 "Reliable Product Launches at Scale" (launch checklist areas, load testing, 15x traffic example, client backoff and jitter), 2017: https://sre.google/sre-book/reliable-product-launches/
- Martin Fowler, "Dark Launching", 29 Apr 2020 (hidden calls from existing flows to measure load): https://martinfowler.com/bliki/DarkLaunching.html
- Google SRE book, ch. 1 "Introduction" (roughly 70% of outages due to changes; progressive rollout, detection, rollback), text as of early 2016, 2017: https://sre.google/sre-book/introduction/
