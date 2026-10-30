# programming

Process skills for building and shipping changes with agents. Each skill works in Claude Code and Cursor; tool-specific commands appear only as labelled, optional shortcuts.

| Skill | Use it for |
|---|---|
| `spec-interview` | Multiple-choice interview until requirements are unambiguous, then SPEC.md with goals, non-goals and executable acceptance checks. Skipped for small changes. |
| `red-green-tdd` | Tests that assert behaviour, a confirmed red run, tests committed first, implementation without editing tests, full suite green, then a real exercise of the feature. |
| `code-review-standard` | Google's code-health standard (order of authority, `Nit:`, escalation), a fresh-context reviewer scoped to correctness, verified findings, and how to receive review. |
| `safe-rollout` | Rollout plan: pre-prod and compatibility stages, one-box or canary vs control, waves, bake times with minimum traffic, auto-rollback, blockers and windows, two-phase format changes, flags, dark launch, expand/contract and online schema tools. |
| `large-scale-migration` | Judge-first migration: parity harness proven to fail, rulebook, gap inventory, shakedown then discard, three-unit trial, fan-out, rulebook fixes for repeated findings. |

Typical order: `spec-interview`, then `red-green-tdd`, then `code-review-standard`, then `safe-rollout`. `large-scale-migration` wraps the same loop for many units at once.

Related skills in other plugins: `systematic-debugging` (debugging-performance), `design-doc` and `blast-radius-review` (software-architecture), `mitigate-first` (oncall-incident).

Every production action in these skills (deploy, promote, roll back, flag flip, schema migration, merge) is written as a proposal for a human to approve. Numbers such as bake times and case-study results are examples with their source and date, not rules.

License: MIT
