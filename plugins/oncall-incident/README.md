# oncall-incident

Skills for running incidents, learning from them, and keeping on-call sustainable. Built from public Google SRE, AWS, PagerDuty, Meta and Learning-from-Incidents sources (each skill lists its sources with dates). Every production-changing step is a proposal for a human to approve.

| Skill | Subcategory | Use it to |
|---|---|---|
| `incident-command` | Response | Declare, run and hand off an incident (severity, roles, live doc, comms) |
| `mitigate-first` | Response | Stop the bleeding with generic mitigations; rank suspect recent changes |
| `blameless-postmortem` | Learning | Draft a blameless postmortem / COE with owned, dated action items |
| `slo-burn-rate-alerts` | Reliability | Define SLOs and multiwindow, multi-burn-rate alerts |
| `runbook-author` | Reliability | Write a `<service>-debugging` runbook: symptoms, read-only checks, mitigations, escalation |
| `toil-audit` | Reliability | Find, measure and rank toil to automate or eliminate |
| `production-safe-agent` | Guardrails | Rules for any agent touching production; optional Claude Code enforcement reference |

Related skills in other plugins: `safe-rollout` (programming); root cause after mitigation: `systematic-debugging` (debugging-performance).
