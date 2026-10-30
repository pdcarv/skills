# software-architecture

Design-stage and review-stage practices from Google, Amazon and the three hyperscalers' Well-Architected frameworks. The design skills chain naturally: PR/FAQ (why, for whom) → design doc (how, and the alternatives) → ADRs (individual decisions over time) → production readiness review (fit for production). Reviews are read-only; every production or billing change they find is written as a proposal for a human to approve.

| Skill | Use it for |
|---|---|
| `design-doc` | Write or review a Google-style design doc (context, goals and non-goals, design, alternatives, cross-cutting concerns) |
| `working-backwards-prfaq` | Draft and review an Amazon-style PR/FAQ before building a product or feature |
| `architecture-decision-record` | Record a decision as a Nygard ADR, with process sized by one-way vs two-way door |
| `timeout-retry-overload-review` | Audit timeouts, retries, backoff, retry budgets, idempotency keys and load shedding per call path |
| `blast-radius-review` | Review static stability, control vs data plane dependencies, fault isolation, cells and shuffle sharding |
| `well-architected-review` | Run a Well-Architected review on AWS, Google Cloud or Azure |
| `production-readiness-review` | Google-style PRR before a launch or ownership handover |

Cloud-specific detail lives in each skill's `references/` folder. Numeric limits and prices are examples with the date they were read; always check the current value. Facts come only from the library's research notes; where the notes had nothing, the skill says so.
