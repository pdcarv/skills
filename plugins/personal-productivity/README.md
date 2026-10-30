# personal-productivity

Writing, career and knowledge skills for engineers who work with agents. Each skill works in Claude Code and Cursor; tool-specific features appear only as optional extras.

| Skill | Use it for |
|---|---|
| `narrative-memo` | Amazon-style narrative memos (purpose, background, initiatives, risks and dependencies, appendices, data-backed claims, revision loop, silent-read meeting), short weekly status updates from evidence, and GitLab's async pre-send check. |
| `brag-document` | Julia Evans's brag document and two-step workshop: the agent gathers evidence from sources the user names and flags unstated impact; the user verifies every item. |
| `research` | Investigate a question and leave a short note: verdict first, dated sources, options ruled out, open unknowns. Scales from inline answers to parallel research subagents with fixed briefs, keeps findings, inferences and gaps apart, and verifies load-bearing claims independently. |
| `session-handoff` | A standalone handoff file (goal, state, decisions, failed attempts, open questions, next steps, verification status) that a fresh session or a person can resume from. |
| `compound-learnings` | After a task, route each lesson to the smallest durable place (enforced check, instruction-file line, scoped rule, skill Gotcha, tool, or retrieved `docs/solutions/` note) without bloating always-on instructions. |

Typical flow: `research` before a decision that needs evidence; `session-handoff` when work pauses; `compound-learnings` when it finishes; weekly updates from `narrative-memo` feed `brag-document`.

Related skills in other plugins: `code-review-standard` and `safe-rollout` (programming), `design-doc`, `working-backwards-prfaq` and `architecture-decision-record` (software-architecture), `incident-command` and `blameless-postmortem` (oncall-incident).

Anything sent to other people (descriptions, memos, updates, brag documents) is a draft for the user to check; shared instruction-file and hook changes are proposals for a human to approve.

License: MIT
