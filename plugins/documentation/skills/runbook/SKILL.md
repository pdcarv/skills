---
name: runbook
description: >-
  Writes or reviews a service debugging runbook (a "<service>-debugging"
  runbook or skill) structured as symptoms, read-only checks, pre-approved
  generic mitigations and escalation, with each mitigation carrying a risk
  label, approval policy, verification step and rollback step. Use when someone
  asks to write, update or review a runbook, playbook, on-call guide,
  troubleshooting guide or "<service>-debugging" skill, or when a postmortem
  action item says "update the runbook".
license: MIT
metadata:
  category: "documentation/reliability"
  sources: "see Sources section"
---

# Runbook

Produce a runbook that a tired on-call engineer, or an agent, can follow during an incident without guessing. Investigation steps come first and are read-only; mitigations are drawn from the service's pre-approved generic set and are written as proposals with risk, approval, verification and rollback. The structure below is a synthesis from Google's generic mitigations and ProdAgent playbooks, AWS COE action items and Anthropic's runbook-style skills. No public source read for this library defines a runbook content standard, so treat the template as a reasoned default, not a quoted standard.

**Side effects:** Writes the runbook (and a `<service>-debugging` skill only if the user asks) to a path the user confirms; reads the alert definitions, dashboards, logs, change systems and postmortems the user points to. Never runs a mitigation, changes alerts or production, or publishes the runbook.

## When to use

- A service has alerts but no runbook, or the runbook is stale.
- A postmortem produced an "update runbook" action item.
- Packaging a service's debugging knowledge as an agent skill (`<service>-debugging`).

## When not to use

- Live incident in progress: out of scope; write or update the runbook after the incident.
- Defining the alerts themselves: use `create-slo`.

## Inputs to gather

- Service name, owners, on-call rotation, escalation contacts (names and handles from the user; never invented).
- Every alert that can page for the service, with its SLI and dashboard links.
- Where logs, metrics and traces live, and the exact query syntax the team uses.
- Dependencies (upstream and downstream) and their owners.
- Change systems: deploy tool, config repo, feature-flag service, infrastructure-as-code, cloud audit logs.
- Existing mitigations from the production readiness review or past incidents, and whether each has been drilled.
- The last few postmortems for the service: symptoms seen, what worked, what misled responders.

## Procedure

1. **List symptoms, not causes.** One entry per alert or recurring user-visible symptom. For each, write the trigger (alert link) and an impact check: how to confirm users are affected and how many. Evidence: the alert definition and a dashboard link per symptom.

2. **Write read-only checks for each symptom.** Order them from broad to narrow:
   - RED on the service and each hop: rate, errors, duration distribution; find the first hop where it changed.
   - USE on that hop's resources: errors first, then utilization, then saturation.
   - What touched it last: deploys, config, flags, infrastructure changes and load shifts in the window, with graphs annotated by change times.
   - Audit trail queries for infrastructure changes (for example GCP Admin Activity logs, which are always on).
   Each check states the exact query or command, what healthy looks like, and what an abnormal result points to next. Prefer data-plane evidence (logs, metrics, access logs) over control-plane calls.

3. **Attach mitigations from the generic set.** For each symptom, list only mitigations that are already built and tested for this service: rollback, data rollback, degrade, upsize, block list, drain, quarantine, restart. For each, write:
   - preconditions (for example: drain only if the service is multi-homed and other locations have capacity);
   - exact parameters, with variables to fill from the alert context;
   - risk label: safe, reversible or destructive;
   - approval policy (who approves; peak-hour limits; two-person rule);
   - verification step (which SLI should recover, how fast);
   - rollback step for the mitigation itself;
   - when it was last drilled.

4. **Flag control-plane dependencies.** Mark any step that needs a control-plane API during recovery (launching instances, editing IAM or org policies, changing DNS through a console). In a regional or provider event these may be unavailable; note the statically stable alternative if one exists, and pre-export any data the step needs.

5. **Write escalation.** When to escalate (declare criteria: second team needed, customer-visible, or unsolved after an hour), to whom, and how. Link the team's incident process.

6. **List evidence to preserve** before any mitigation: which logs, dumps or snapshots, and where they go.

7. **Add a Gotchas section** seeded from past postmortems: misleading graphs, known red herrings, checks that need special permissions. Append to it after every incident.

8. **Package as a skill only if the user asks.** Confirm the path first. Name it `<service>-debugging`; put long query catalogues in `references/` and any deterministic data-gathering in `scripts/`. Its description should name the service and its alert names as trigger words.

9. **Tabletop it.** Walk one past incident through the runbook. Every point where the responder would have had to guess is a defect to fix.

## Verification

- Every check is read-only, has an exact command or query, and states the healthy result.
- Every mitigation has preconditions, risk label, approval policy, verification and rollback; none is executable without approval.
- No secrets, tokens or end-user data in the runbook.
- Links resolve; named contacts were supplied by the user.
- The tabletop walk-through finds no step that needs knowledge not written down.
- Control-plane-dependent steps are marked.

## Gotchas

- **Mitigation-first runbooks that skip evidence.** "Restart it" as step one destroys the state needed to diagnose. Preserve evidence, then mitigate.
- **Un-drilled mitigations.** A rollback or degraded mode that has never been exercised has unknown side effects. Record the last drill date and schedule drills.
- **Drain on a single-homed service.** Draining only helps when traffic has somewhere else to go, and does nothing if the bad release is everywhere.
- **Checks without expected values.** "Look at the CPU graph" is not a check. State the threshold or shape that means trouble.
- **Missing log coverage.** In GCP, Data Access audit logs are off by default except for BigQuery, and reading them needs `roles/logging.privateLogViewer` rather than `roles/logging.viewer`. A "who read this?" check may return nothing for that reason, not because nothing happened.
- **Control-plane steps in a regional event.** Steps that launch capacity or edit policy may fail exactly when needed.
- **Stale runbooks.** Tie updates to postmortem action items and to the Gotchas append step.
- **Agent context, not agent authority.** A runbook used as agent context guides investigation; the risk labels and approval policy still govern every action.

## Output

```markdown
# <service>-debugging runbook
Owners: <team>  On-call: <rotation link>  Last reviewed: <date>  Last drilled: <date>
Dashboards: <links>   Logs: <where + query syntax>   Traces: <where>
Dependencies: <upstream/downstream + owners>
Change sources: <deploy tool, config repo, flag service, IaC, audit logs>

## Symptom: <alert name or user-visible symptom>
Trigger: <alert link>   Impact check: <query; what "users affected" looks like>

### Read-only checks (in order)
1. <check>: `<command or query>` | healthy: <...> | if abnormal: go to <check/mitigation>
2. What touched it last: `<deploy/config/flag/audit query>` | window: <...>

### Mitigations (proposals; require approval)
| Mitigation | Preconditions | Parameters | Risk | Approval | Verify | Roll back | Last drilled |
|---|---|---|---|---|---|---|---|

### Evidence to preserve first
- <logs/dumps/snapshots and where to put them>

### Escalate when
- <criteria> -> <who, how>

## Gotchas
- <misleading signal / red herring / permission needed> (added after <incident id>)
```

## Sources

- Jennifer Mace, "Generic mitigations", O'Reilly, 15 Dec 2020 (generic set; list in PRR, standardise, drill). https://www.oreilly.com/content/generic-mitigations/
- Google Cloud blog, "How Google SREs use Gemini CLI to solve real-world outages", 22 Jan 2026 (parameterised playbooks with verification and rollback, risk labels, human approval). https://cloud.google.com/blog/topics/developers-practitioners/how-google-sres-use-gemini-cli-to-solve-real-world-outages
- Google SRE Book (2016), ch. 12 "Effective Troubleshooting" and ch. 14 "Managing Incidents". https://sre.google/sre-book/effective-troubleshooting/ , https://sre.google/sre-book/incident-response/ (read Oct 2026)
- AWS Cloud Operations blog, "Creating a Correction of Errors document", 6 Nov 2023, updated 23 Jun 2025 ("update runbook" action items). https://aws.amazon.com/blogs/mt/creating-a-correction-of-errors-document/
- Claude blog, "How Anthropic teams use Claude Code", 24 Jul 2025 (markdown runbooks as agent context). https://claude.com/blog/how-anthropic-teams-use-claude-code
- Thariq Shihipar on Claude Code skills, 17 Mar 2026, via YouMind mirror (runbook skill category, `<service>-debugging`, Gotchas sections). https://youmind.com/ar/landing/x-viral-articles/claude-code-skills-guide
- Brendan Gregg, "The USE Method" (updated 24 Aug 2017). https://brendangregg.com/usemethod.html ; Grafana Labs, "The RED Method", Aug 2018. https://grafana.com/blog/2018/08/02/the-red-method-how-to-instrument-your-services/
- AWS Fault Isolation Boundaries whitepaper, "Static stability" (undated, read Oct 2026). https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/static-stability.html
- GCP Cloud Audit Logs overview (updated 2026-10-26). https://docs.cloud.google.com/logging/docs/audit
