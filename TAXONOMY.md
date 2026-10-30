# Taxonomy

Seven plugins, one per major category. Teams enable only the plugins they need, because every enabled skill's description is loaded into context on every turn.

Cloud-specific detail lives in per-cloud reference files (`references/aws.md`, `references/gcp.md`, `references/azure.md`) inside each skill, loaded only when needed.

| Plugin | Subcategory | Skill | One-line purpose |
|---|---|---|---|
| software-architecture | Design and decisions | design-doc | Write or review a Google-style design doc |
| software-architecture | Design and decisions | working-backwards-prfaq | Draft an Amazon PR/FAQ before building |
| software-architecture | Design and decisions | architecture-decision-record | Record a decision as an ADR, sized by one-way vs two-way door |
| software-architecture | Resilience | timeout-retry-overload-review | Audit timeouts, retries, backoff, budgets, idempotency and load shedding |
| software-architecture | Resilience | blast-radius-review | Review static stability, fault isolation boundaries, cells and DR |
| software-architecture | Cloud reviews | well-architected-review | Run a Well-Architected review on AWS, GCP or Azure |
| software-architecture | Launch | production-readiness-review | Google-style PRR before a launch |
| programming | Planning | spec-interview | Interview the user until a spec is unambiguous, then write SPEC.md |
| programming | Quality | red-green-tdd | Test-first loop with a confirmed failing test |
| programming | Quality | code-review-standard | Review a change to Google's code-health standard, and respond to review |
| programming | Delivery | safe-rollout | Ship a change with canaries, waves, flags and expand/contract migrations |
| programming | Large changes | large-scale-migration | Judge-first, rulebook-driven migration fan-out |
| debugging-performance | Method | systematic-debugging | Root cause before fix, with runtime evidence and bisect |
| oncall-incident | Response | incident-command | Declare, run and hand off an incident |
| oncall-incident | Response | mitigate-first | Stop the bleeding with generic mitigations; rank suspect changes |
| oncall-incident | Learning | blameless-postmortem | Draft a postmortem / COE |
| oncall-incident | Reliability | slo-burn-rate-alerts | Define SLOs and multiwindow burn-rate alerts |
| oncall-incident | Reliability | runbook-author | Write a service debugging runbook |
| oncall-incident | Reliability | toil-audit | Find and rank toil to automate |
| oncall-incident | Guardrails | production-safe-agent | Rules for any agent touching production |
| personal-productivity | Writing | narrative-memo | Write an Amazon-style narrative or status update |
| personal-productivity | Career | brag-document | Keep a running record of impact for reviews and promotion |
| personal-productivity | Knowledge | research | Investigate a question and leave a verdict-first, sourced research note |
| personal-productivity | Knowledge | session-handoff | Hand off a session's state to a fresh session or person |
| personal-productivity | Knowledge | compound-learnings | Turn a finished task's lessons into durable instructions |
| training | Cycling | cycling | Plan interview, per-session review and adaptation for one road cyclist |
| investing | Equities | value-investing | Analyse, size and review equity theses with six framework checks and deterministic scripts |
