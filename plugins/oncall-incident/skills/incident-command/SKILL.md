---
name: incident-command
description: >-
  Declares, runs and hands off a production incident using Google SRE incident
  management practice and PagerDuty's open-source severity scale and response
  roles. Covers the declare/don't-declare decision, severity choice (when unsure,
  pick the higher one), role assignment, a live incident-state document, status
  update cadence and handoff of command. Use when a page fires, a user reports an
  outage or degradation, or someone asks "is this an incident?", "what SEV is
  this?", "who is IC?", "write a status update", "start an incident doc", or
  "hand off incident command". Coordination only: choosing the technical
  mitigation is mitigate-first, and root cause is systematic-debugging.
license: MIT
metadata:
  category: "oncall-incident/response"
  sources: "see Sources section"
---

# Incident Command

Turn a confused, many-voices production problem into a coordinated response: decide whether it is an incident, pick a severity, put one named person in command, keep one live state document current, communicate on a predictable rhythm, and transfer command cleanly. The agent acts as scribe, planner and drafter for the humans. It is never the Incident Commander (IC) and never changes the system on its own.

## When to use

- A page fired, an SLO burn alert tripped, or a customer or colleague reports breakage.
- Someone is unsure whether to declare, or which severity to choose.
- An incident is running and needs a state doc, a status update, a role roster or an IC handoff.

## When not to use

- Choosing or proposing a mitigation: use `mitigate-first`.
- Finding the root cause: use the `systematic-debugging` skill (debugging-performance plugin).
- After resolution: use `blameless-postmortem`.

## Inputs to gather

- What is broken, how it shows (alert link, error text, customer report), and when it started, with time zone.
- Whether customers can see it, and roughly how many are affected.
- Which teams own the affected services and dependencies.
- The org's own severity scale and paging policy. If one exists, use it and map to it; the PagerDuty scale below is the fallback.
- Who is on call, the incident channel or tool in use, and who owns external comms (status page). Never invent names; ask.

## Procedure

1. **Decide whether to declare.** Declare if any of these holds (Google SRE):
   - a second team is needed to fix it;
   - the outage is visible to customers;
   - it is still unsolved after an hour of concentrated analysis.
   Evidence: which criterion is met, with the link that shows it. If none is met, record that and set a check-back time; the one-hour clock is easy to lose track of.

2. **Pick a severity.** Use the org scale, or this paraphrase of PagerDuty's:

   | SEV | Meaning | Example signals | Response |
   |---|---|---|---|
   | 1 | Critical; public notification, executive liaison | Widespread impact, SLA breach, customer data exposure | Major incident: page an IC, full response |
   | 2 | Critical; many customers heavily affected | Core pipeline or web app badly degraded; major-incident monitoring impaired | Major incident: page an IC, full response |
   | 3 | Stability or minor customer impact needing an owner now | Partial loss of function; no redundancy left | High-urgency page; roll back if tied to a recent deploy; watch for escalation |
   | 4 | Minor, no customer impact | Single host failed; delayed job | Low-urgency page |
   | 5 | Cosmetic | — | Ticket |

   When unsure between two levels, take the higher one and move on. Severity is revisited in the postmortem, not debated now. Evidence: one line saying why this level.

3. **Assign roles, one name each.** One IC per incident. Small incidents may combine roles in one person.

   | Role | Owns | Source |
   |---|---|---|
   | Incident Commander | Overall state; assigns roles; holds any role not delegated; collects options and decides; approves external comms; starts and assigns the postmortem | Google, PagerDuty |
   | Operations / Resolver (SME) | The only people who change the system during the incident; report in Condition / Actions / Needs form | Google, PagerDuty |
   | Communication / Liaisons | Periodic updates. Customer liaison drafts external comms from templates and posts only after IC approval; internal liaison pages SMEs and handles stakeholders | Google, PagerDuty |
   | Planning | Files bugs, arranges handoffs, tracks how the system has diverged from normal so it can be reverted | Google |
   | Scribe / Deputy | Scribe logs actions and status; deputy is a trained IC on hot standby who tracks timers and roll-call | PagerDuty |

   The IC delegates all repair work. The agent may fill Scribe or Planning support duties and draft comms; it never holds IC or Operations.

4. **Open the command post.** One recognised channel (with a bot logging to it if available, for the postmortem) and one live incident-state document from the template in Output. Put the most important facts at the top. Evidence: channel and doc links posted in each other.

5. **Run the response loop.** Priorities, in order: stop the damage, restore service, preserve evidence. On each cycle:
   - Collect resolver reports in Condition / Actions / Needs form and update the doc's Current state.
   - Log every system change with time, who, what, and how to revert it (Planning's divergence list).
   - Hand mitigation choices to `mitigate-first`; each is a proposal the IC approves.
   - Periodically ask whether there is an alternative not yet considered, and whether the IC is overloaded and should hand off or ask for help.
   - Re-check severity when impact changes. Per PagerDuty's rule, when unsure use the higher severity and don't debate it mid-incident.

6. **Communicate on a fixed rhythm.** Agree an update interval at declaration, put "next update at" in every update, and keep it even when nothing changed. Internal and external updates use the templates in Output. External text goes to the IC for approval before anyone posts it.

7. **Hand off command explicitly.** At shift end or when the IC is overloaded:
   - brief the incoming IC fully, using the handoff template;
   - wait for an explicit acknowledgment ("I have command") before the outgoing IC leaves;
   - announce the new IC in the channel and update the doc header.

8. **Close.** When impact has ended and recovery is confirmed on the signal that showed the impact, record the end time, list what is still diverged from normal (temporary mitigations to unwind), and have the IC assign a postmortem owner. Then run `blameless-postmortem`.

## Verification

- The doc header has every field filled: severity with reason, IC, roles, start time with time zone, impact, next update time.
- Every logged change has time, actor, approval and a revert note. Nothing in the channel describes a change that is missing from the log.
- Each role has exactly one name; the IC is not also a resolver on a major incident.
- Every external update has a recorded IC approval.
- Any handoff shows an explicit acknowledgment in the channel.
- No end-user identifiers in the doc (it becomes postmortem input).

## Gotchas

- **The IC starts debugging.** Once the IC is heads-down in a terminal, nobody holds the overall state. PagerDuty's rule: "the Incident Commander is NOT a resolver."
- **Severity debates.** Arguing SEV-2 vs SEV-3 burns the first minutes. Take the higher, revisit later.
- **Changes from outside Operations.** Well-meaning people "just trying something" confound every test and leave changes nobody can revert. Route all changes through Ops and the log.
- **Stale state doc.** Google calls keeping it current the IC's most important job. A doc that lags the channel makes handoffs and status updates wrong.
- **Silent handoff.** Leaving without an acknowledgment means nobody is in command, often during the worst hours.
- **Slow-burn problems never get declared.** The one-hour-of-analysis criterion exists for these; set the timer at first look.
- **Assuming last time's cause.** Similar symptoms tempt teams to repeat a past fix; Google lists this as a troubleshooting pitfall. Treat it as one hypothesis among several.
- **Times without zones.** Mixed local times break the timeline. Use one zone, stated in the header.
- **Agent overreach.** The agent drafts, logs and proposes. It does not page people, post externally or touch production without a human's explicit instruction.

## Output

Live incident-state document (most important information first):

```markdown
# INCIDENT <id>: <one-line symptom>   STATUS: ACTIVE | MITIGATED | RESOLVED
Severity: SEV-<n> (why: <one line>)          Declared: <time, TZ> by <name>
IC: <name>   Deputy: <name>   Ops lead: <name>   Comms: <name>   Scribe: <name>
Channel: <link>   Next update due: <time, TZ>

## Current state (rewrite every cycle)
Impact: <who/what is affected, how many, since when>
Leading hypothesis: <text> (confidence: low/med/high)
Mitigation in progress: <action, approved by, started at>
Needs: <people, access, decisions>

## Divergence from normal (unwind after the incident)
| Time | Change | By | Approved by | How to revert | Reverted? |

## Timeline (append-only, TZ: <zone>)
- <time> <event / observation / decision> (<source link>)

## Open questions and next steps
- [ ] <item> (owner)
```

Status update (internal):

```text
[SEV-<n>] <service>: <impact in user terms>. Since <time TZ>.
Now: <what is being done>. Customer impact: <ongoing/reduced/ended>.
Next update: <time TZ>. IC: <name>.
```

IC handoff brief (read to the incoming IC, then wait for acknowledgment):

```text
Severity and impact now: ...
Timeline highlights: ...
What has been tried (and results, including negatives): ...
Current mitigation and how to revert it: ...
Divergence list status: ...
Roles and who is doing what: ...
Pending decisions / comms due: ...
```

## Sources

- Google SRE Book (2016), ch. 14 "Managing Incidents": roles, command post, live doc, handoff, declaration criteria, best practices. https://sre.google/sre-book/incident-response/ (read Oct 2026)
- Google SRE Book (2016), ch. 12 "Effective Troubleshooting": pitfalls, change logging. https://sre.google/sre-book/effective-troubleshooting/ (read Oct 2026)
- Google SRE Book (2016), ch. 15 "Postmortem Culture": no end-user identifiers. https://sre.google/sre-book/postmortem-culture/ (read Oct 2026)
- PagerDuty Incident Response docs, "Severity Levels". https://response.pagerduty.com/before/severity_levels/ (read Oct 2026)
- PagerDuty Incident Response docs, "Different Roles". https://response.pagerduty.com/before/different_roles/ (read Oct 2026)
