# programming

Process skills for building and shipping changes with agents. Each skill works in Claude Code and Cursor; tool-specific commands appear only as labelled, optional shortcuts.

| Skill | Use it for |
|---|---|
| `grill` | Multiple-choice interview until requirements are unambiguous, then SPEC.md with goals, non-goals and executable acceptance checks. Skipped for small changes. |
| `tdd` | Tests that assert behaviour, a confirmed red run, tests committed first, implementation without editing tests, full suite green, then a real exercise of the feature. |
| `review` | Google's code-health standard (order of authority, `Nit:`, escalation), a fresh-context reviewer scoped to correctness, verified findings, and how to receive review. |
| `migrate` | Judge-first migration: parity harness proven to fail, rulebook, gap inventory, shakedown then discard, three-unit trial, fan-out, rulebook fixes for repeated findings. |
| `resilience` | Audit timeouts, retries, backoff, retry budgets, idempotency keys and load shedding per call path |
| `research` | Investigate a question and leave a short note: verdict first, dated sources, options ruled out, open unknowns. Scales from inline answers to parallel research subagents with fixed briefs, keeps findings, inferences and gaps apart, and verifies load-bearing claims independently. |
| `handoff` | A standalone handoff file (goal, state, decisions, failed attempts, open questions, next steps, verification status) that a fresh session or a person can resume from. |
| `diagnose` | Root cause before fix: hypothesis and evidence loop, failing reproduction test, temporary runtime instrumentation, `git bisect run` for regressions (including performance, with custom terms). Stops after three failed fixes. |

Typical order: `grill`, then `tdd`, then `review`. `migrate` wraps the same loop for many units at once. `research` before a decision that needs evidence; `resilience` for each remote call path; `handoff` when work pauses. `diagnose` when a bug's cause is unknown, before `tdd`.

Related skills in other plugins: `design-doc`, `adr` and `learnings` (documentation).

No skill here acts on production: the agent works in the local repository, test and CI output, and scratch files. Numbers such as case-study results are examples with their source and date, not rules.

License: MIT
