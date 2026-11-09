# documentation

Writing skills: design docs and ADRs for decisions, runbooks for on-call, memos and status updates for communication, brag documents for reviews, and learnings that route lessons into agent instructions. Anything sent to other people is a draft for the user to check; shared instruction-file and hook changes are proposals for a human to approve.

| Skill | Use it for |
|---|---|
| `design-doc` | Write or review a Google-style design doc (context, goals and non-goals, design, alternatives, cross-cutting concerns) |
| `adr` | Record a decision as a Nygard ADR, with process sized by one-way vs two-way door |
| `runbook` | Write a `<service>-debugging` runbook: symptoms, read-only checks, mitigations, escalation |
| `memo` | Amazon-style narrative memos (purpose, background, initiatives, risks and dependencies, appendices, data-backed claims, revision loop, silent-read meeting), short weekly status updates from evidence, and GitLab's async pre-send check. |
| `brag` | Julia Evans's brag document and two-step workshop: the agent gathers evidence from sources the user names and flags unstated impact; the user verifies every item. |
| `learnings` | After a task, route each lesson to the smallest durable place (enforced check, instruction-file line, scoped rule, skill Gotcha, tool, or retrieved `docs/solutions/` note) without bloating always-on instructions. |

Typical flow: `design-doc` for how, then `adr` for individual decisions over time; weekly updates from `memo` feed `brag`; `learnings` when a task finishes.

Related skills in other plugins: `grill`, `review`, `research` and `diagnose` (programming), `create-slo` (sre).

Numeric limits and prices are examples with the date they were read; always check the current value. Facts come only from the library's research notes; where the notes had nothing, the skill says so.

License: MIT
