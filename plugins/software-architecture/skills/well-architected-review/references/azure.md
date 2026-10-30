# Azure Well-Architected review

Source: Microsoft Learn, "Azure Well-Architected Framework pillars" (ms.date 2025-01-22).

## Pillars (5)

Reliability, security, cost optimization, operational excellence, performance efficiency. Each pillar has a Design principles page and a Tradeoffs page; cite the Tradeoffs page when recording a deliberate trade-off between pillars.

## Review mechanism

1. **Assessment.** Start the Azure Well-Architected Review self-assessment at https://learn.microsoft.com/en-us/assessments/azure-architecture-review/ . The user (or the review owner) completes it; the agent prepares evidence for each answer.
2. **Telemetry.** Azure Advisor gives telemetry-based recommendations per pillar, and the Advisor score can be broken down by pillar. Pull the recommendations for the workload's subscriptions and attach each relevant one to a finding with its recommendation ID. Reading Advisor is read-only; applying a recommendation is a change and needs approval.
3. Merge assessment answers and Advisor recommendations into the main skill's findings table; where they disagree, the evidence decides.

A separate page, "Use Well Architected Framework assessments in Azure Advisor" (https://learn.microsoft.com/en-us/azure/advisor/advisor-assessments), exists but was not read; check it if the user wants the assessment run from inside Advisor.

## Not verified (do not claim)

- The assessment's question structure and scoring.
- Azure design-review checklists per pillar.
- Any ranking of most commonly found issues.

## Related verified Azure facts

- Region pairs are not an HA or DR mechanism; some are one-directional; many newer regions have none: `blast-radius-review` (references/azure.md).
- Safe deployment practice (OE:11): bake time in hours and days, halt on any end-user health alert, pre-defined emergency path: `safe-rollout` (programming plugin).
