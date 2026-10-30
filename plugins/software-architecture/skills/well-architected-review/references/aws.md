# AWS Well-Architected review

Source: AWS Well-Architected Tool user guide, "Tutorial" (read 2026-10-28). The console flow below is from that page. WA Tool CLI and API commands (for example `create-workload`) were **not verified** in this library's sources; do not script them from memory.

## Pillars (6)

Operational excellence, security, reliability, performance efficiency, cost optimization, sustainability.

## Review flow in the WA Tool

1. **Define the workload.** Required: name, description, review owner, environment, Regions (non-AWS regions are allowed). Optional: account IDs, architecture diagram, Trusted Advisor integration, Jira integration.
2. **Apply a profile and lens.** A profile is optional. The AWS Well-Architected Framework lens is selected by default; add other lenses if they apply.
3. **Answer each question.** Select the best practices the workload follows. Mark a question or best practice not applicable with a reason in Notes; notes appear in the report.
4. **Save a milestone and generate a report.** The PDF shows the workload state, the number of risks and suggested improvements.
5. **Review the improvement plan.** High-risk items are listed first, then medium-risk. Set Improvement status under Properties.
6. **Improve and measure.** Update answers as fixes land, save a new milestone, and compare milestones.

The tutorial page does not state a review cadence and does not use the abbreviations "HRI" or "MRI"; say "high-risk item" and "medium-risk item".

## Who does what

- Creating the workload and answering questions in the WA Tool writes to the user's account. Offer to prepare answers and evidence; let the review owner enter them, or get explicit approval before the agent does.
- The agent's own evidence gathering stays read-only (configs, IaC, metrics, logs).

## Verified best practice to anchor the reliability pillar

REL11-BP05 (static stability): single normal mode, capacity pre-provisioned for AZ or Region loss, constant-work configuration refresh with a cached value and alarm, read replicas sized per AZ, and REL11-BP04 (rely on the data plane during recovery). Use `blast-radius-review` to assess it.

## Not verified (do not claim)

- The full best-practice ID list per pillar.
- WA Tool CLI/API syntax.
- Any ranking of most commonly found risks.
