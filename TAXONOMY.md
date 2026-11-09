# Taxonomy

Five plugins, one per major category. Teams enable only the plugins they need, because every enabled skill's description is loaded into context on every turn.

Cloud-specific detail lives in per-cloud reference files (`references/aws.md`, `references/gcp.md`, `references/azure.md`) inside each skill, loaded only when needed.

| Plugin | Subcategory | Skill | One-line purpose |
|---|---|---|---|
| documentation | Design and decisions | design-doc | Write or review a Google-style design doc |
| documentation | Design and decisions | adr | Record a decision as an ADR, sized by one-way vs two-way door |
| documentation | Reliability | runbook | Write a service debugging runbook |
| documentation | Writing | memo | Write an Amazon-style narrative or status update |
| documentation | Career | brag | Keep a running record of impact for reviews and promotion |
| documentation | Knowledge | learnings | Turn a finished task's lessons into durable instructions |
| programming | Planning | grill | Interview the user until a spec is unambiguous, then write SPEC.md |
| programming | Quality | tdd | Test-first loop with a confirmed failing test |
| programming | Quality | review | Review a change to Google's code-health standard, and respond to review |
| programming | Large changes | migrate | Judge-first, rulebook-driven migration fan-out |
| programming | Resilience | resilience | Audit timeouts, retries, backoff, budgets, idempotency and load shedding |
| programming | Knowledge | research | Investigate a question and leave a verdict-first, sourced research note |
| programming | Knowledge | handoff | Hand off a session's state to a fresh session or person |
| programming | Method | diagnose | Root cause before fix, with runtime evidence and bisect |
| sre | Reliability | create-slo | Define SLOs and multiwindow burn-rate alerts |
| sre | Reliability | team-toil | Find and rank toil to automate |
| training | Cycling | cycling | Plan interview, per-session review and adaptation for one road cyclist |
| investing | Equities | valuation | Analyse, size and review equity theses with six framework checks and deterministic scripts |
