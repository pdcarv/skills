# Google Cloud Well-Architected review

Source: Google Cloud Well-Architected Framework landing page (last updated and reviewed 2026-10-13).

## Pillars (6) and perspectives

Pillars: operational excellence; security, privacy and compliance; reliability; cost optimization; performance optimization; sustainability.

Cross-pillar perspectives: AI/ML, and financial services. Apply a perspective when the workload is an AI/ML system or a financial-services workload.

## Review mechanism

- The framework page describes **no formal review process or tool**. Do not invent a console flow.
- Google recommends **per-pillar agent skills** for AI agents, named `google-cloud-waf-*`, one per pillar. Per the page, each contains a pillar overview, the relevant products, assessment questions and a validation checklist.
- Install command as printed on Google's page (the `google/skills` repository itself was not inspected for this library):
  ```
  npx skills add google/skills --skill SKILL_NAME
  ```
  This installs third-party instructions into the agent environment. Propose it to the user with the exact skill names they want; do not run it without approval.
- If the user installs them, use their assessment questions and validation checklists as the per-pillar question set in step 3 of the main procedure, and keep this skill's evidence, ranking and improvement-plan format.
- If not, use the framework's pillar pages directly and cite the page for each question you ask.

## Other suggestions on the page

- DORA software-delivery metrics as evidence for operational excellence.
- Maintained architecture documentation (see `design-doc` and `architecture-decision-record`).

## Not verified (do not claim)

- Whether the framework was previously called the "Architecture Framework": the page read does not mention a former name.
- Active Assist or Recommender as part of the review: the page does not mention them.
- Pillar-level content, including the reliability pillar; read the current pillar pages.
- Any ranking of most commonly found issues.

## Related verified Google Cloud facts

- Resource scope (global, regional, zonal) is the failure domain: `blast-radius-review` (references/gcp.md).
