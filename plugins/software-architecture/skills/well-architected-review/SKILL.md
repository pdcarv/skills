---
name: well-architected-review
description: >-
  Runs a Well-Architected review of a workload on AWS (Well-Architected Tool, six pillars,
  improvement plan of high- and medium-risk items, milestones), Google Cloud (Well-Architected
  Framework, six pillars plus AI/ML and financial-services perspectives, Google's own
  per-pillar agent skills) or Azure (five pillars, Azure Well-Architected Review assessment
  plus Azure Advisor recommendations and score by pillar). Use when asked for a
  Well-Architected review, WAR, WAFR, architecture review against a cloud framework,
  pillar assessment, Advisor score review, or "is this workload well-architected?".
  Produces per-pillar findings ranked by risk, an improvement plan with owners, and a
  re-assessment milestone.
license: MIT
metadata:
  category: "software-architecture/cloud-reviews"
  sources: "see Sources section"
---

# Well-Architected review

Review one workload against its cloud's Well-Architected framework, using the cloud's own pillar names and review mechanism. The shape is the same on every cloud: scope the workload, answer per-pillar questions with evidence, rank risks, build an improvement plan, and set a milestone to re-assess. The mechanisms differ: AWS has a native tool, Azure pairs a questionnaire with Advisor telemetry, and Google publishes the framework plus per-pillar agent skills but no formal review process.

## When to use

- A team asks for a Well-Architected review, a pillar-by-pillar architecture assessment, or a re-assessment after changes.
- An Advisor score or WA Tool risk count needs explaining and turning into a plan.
- A launch or audit requires evidence of a framework review.

## When not to use

- A focused question that another skill answers in depth: AZ/Region failure (`blast-radius-review`), retries and overload (`timeout-retry-overload-review`), launch readiness (`production-readiness-review`). Use those as deep dives from inside this review.
- A design that does not exist yet: `design-doc` first.

## Inputs to gather

- Workload scope: name, description, owner, environment (production or not), regions, accounts/projects/subscriptions, architecture diagram.
- Which cloud(s); for multi-cloud, run one review per cloud and framework.
- Access the reviewer has: WA Tool console access (AWS), Advisor access (Azure), read access to configs and dashboards. Reviews are read-only.
- Business priorities and known trade-offs, so pillar tensions (for example cost vs reliability) can be judged.
- Any previous review, milestone or improvement plan.

## Procedure

1. **Scope the workload.** Write down name, description, review owner, environment and regions. One review = one workload; split sprawling estates.
2. **Pick the framework and load the cloud reference.** `references/aws.md`, `references/gcp.md` or `references/azure.md`. Use that cloud's pillar names verbatim in the report:
   - AWS (6): operational excellence, security, reliability, performance efficiency, cost optimization, sustainability.
   - Google Cloud (6): operational excellence; security, privacy and compliance; reliability; cost optimization; performance optimization; sustainability. Plus AI/ML and financial-services perspectives where relevant.
   - Azure (5): reliability, security, cost optimization, operational excellence, performance efficiency.
3. **Gather evidence per pillar.** For each pillar, answer the framework's questions (WA Tool questions on AWS; the assessment on Azure; the pillar's assessment questions on Google Cloud) from evidence: configs, IaC, dashboards, runbooks, incident history. Mark "not applicable" only with a written reason. Where this library has a verified deep-dive, use it:
   - static stability, fault isolation, AZ-loss headroom: `blast-radius-review` (AWS REL11-BP05 is the verified best practice behind it);
   - timeouts, retries, load shedding: `timeout-retry-overload-review`;
   - monitoring, emergency response, change management: `production-readiness-review`.
4. **Add telemetry where the cloud provides it.** Azure Advisor recommendations by pillar and the Advisor score by pillar; AWS WA Tool optional Trusted Advisor integration. Telemetry supplements the questions; it does not replace them.
5. **Rank risks.** Use high and medium risk, high first, as the AWS improvement plan does. For each risk record the pillar, the evidence, the impact, and the proposed improvement.
6. **Build the improvement plan.** Each item gets an owner (ask the user; never invent a name), a target date and a status. Every item that changes production, IAM, networking or spend is a proposal for a human to approve.
7. **Record a milestone.** Save the state (AWS: a WA Tool milestone and PDF report; elsewhere: a dated copy of the report) and set when to re-assess and compare.

## Verification

- Pillar names match the chosen cloud's framework exactly.
- Every pillar has findings or an explicit "no risks found" with the evidence checked.
- Every "not applicable" has a reason.
- Every risk cites evidence (file, config, metric, Advisor recommendation ID, WA Tool question).
- No finding is presented as a "top common issue" or industry ranking.
- Every improvement item has an owner field (filled by the user or "TBD - ask") and a date.

## Gotchas

- **No vendor "top findings" list.** None of the three vendors publishes a frequency ranking of common findings in the sources this library verified. Do not claim one, and do not pad the report with generic best practices that lack workload evidence.
- **Pillar names differ.** "Performance efficiency" (AWS, Azure) vs "performance optimization" (Google); "security" vs "security, privacy and compliance" (Google). Mixing them makes the report look like it used the wrong framework.
- **Advisor is not the review.** Advisor recommendations are telemetry-based and cover what Advisor can see; design questions (DR plans, runbooks, team practices) still need the assessment.
- **Google has no formal review tool.** Do not describe a Google Cloud "review tool" or console flow; the framework page describes none. Google instead recommends its per-pillar agent skills, which an agent can use if the user installs them.
- **Installing third-party skills changes the agent's environment.** Propose the install command and let the user run it; the `google/skills` repository was not inspected for this library.
- **Pillar tensions.** Static-stability headroom looks like waste to a cost reviewer. Record the trade-off rather than flagging both.
- **Unverified tooling.** AWS WA Tool CLI/API commands and the Azure assessment's question structure and scoring were not verified; use the console flows described in the references.

## Output

```markdown
## Well-Architected review: <workload>   Cloud/framework: <...>   Date: <...>
Scope: <description, environment, regions, accounts/projects/subscriptions>   Review owner: <...>
Previous milestone: <date or none>

### Summary by pillar
| Pillar (cloud's name) | High risks | Medium risks | Notes |

### Findings
| # | Pillar | Risk (high/medium) | Finding | Evidence | Impact | Proposed improvement |

### Improvement plan
| # | Item | Owner | Target date | Status | Needs approval? |

### Not applicable (with reasons)
### Next milestone / re-assessment: <date>
```

## Sources

- AWS Well-Architected Tool user guide, tutorial (define workload, lens, answer questions, milestone and report, improvement plan with high then medium risks; six pillars), read 2026-10-28: https://docs.aws.amazon.com/wellarchitected/latest/userguide/tutorial.html
- AWS Well-Architected, REL11-BP05 static stability, read Oct 2026: https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_withstand_component_failures_static_stability.md
- Google Cloud Well-Architected Framework (six pillars, two perspectives, per-pillar agent skills), last updated 2026-10-13: https://docs.cloud.google.com/architecture/framework
- Microsoft Learn, Azure Well-Architected Framework pillars (five pillars, Well-Architected Review assessment, Advisor by pillar), ms.date 2025-01-22: https://learn.microsoft.com/en-us/azure/well-architected/pillars
