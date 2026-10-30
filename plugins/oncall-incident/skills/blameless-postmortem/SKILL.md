---
name: blameless-postmortem
description: >-
  Drafts a blameless postmortem or Amazon-style Correction of Errors (COE) after
  an incident: checks whether one is required, builds a timestamped timeline from
  chat, alerts and change logs, asks "how" questions at critical junctures
  instead of stopping at a single root cause or "human error", answers the
  detect/diagnose/mitigate-faster questions, and writes action items with owner,
  priority and due date. Use when an incident is resolved, or someone asks for a
  postmortem, post-incident review, PIR, COE, incident report, retro, 5 Whys,
  lessons learned, or follow-up action items.
license: MIT
metadata:
  category: "oncall-incident/learning"
  sources: "see Sources section"
---

# Blameless Postmortem

Produce a postmortem that makes the next incident shorter or rarer. The structure follows the AWS COE (summary, impact, timeline, metrics, detection/diagnosis/mitigation questions, analysis, action items) and Google's blameless postmortem culture and review criteria. The analysis follows John Allspaw's "Infinite Hows" critique: gather each participant's account, ask "how" rather than "why", and describe several contributing factors rather than one constructed root cause.

## When to use

- An incident is resolved (impact ended, system back to normal) and a postmortem trigger is met.
- Someone asks for a COE, PIR, incident report, retro or action items.

## When not to use

- The incident is still active: use `incident-command` and `mitigate-first`. COEs are written after resolution.
- A routine, fully automated recovery with no trigger met (but any stakeholder may still request one).

## Inputs to gather

- The live incident doc, channel log (and logging-bot output), alert history and pages.
- Dashboards for the affected SLIs covering before, during and after.
- Change history for the window: deploys, config, flags, infrastructure.
- Tickets, customer reports, and the count of affected customers if known.
- Names and roles of participants, and their availability for short interviews.
- The org's own postmortem template, severity scale and review process, if any. Map to them rather than replacing them.

## Procedure

1. **Confirm a postmortem is warranted.** Google's triggers: user-visible downtime or degradation beyond a threshold; any data loss; on-call intervention such as rollback or rerouting; resolution time beyond a threshold; a monitoring failure (the issue was found by a human). Use the org's thresholds; if none exist, say so and recommend defining them in advance. Evidence: the trigger and the data showing it.

2. **Build the timeline from records, not memory.** Merge chat, alerts, deploy logs and graphs into timestamped bullets in one stated time zone. Mark key moments: first impact, first detection, declaration, each hypothesis, each mitigation proposed/approved/executed, impact end, recovery confirmed. Note gaps between them (time to detect, time to mitigate). Evidence: a source link per bullet.

3. **Collect second stories before showing the data.** For each key participant, draft interview questions for a human facilitator. Collect each account first, without replaying graphs or logs that would bias memory; then summarise it back and get confirmation. The agent never invents or paraphrases an account it was not given.

4. **Find the critical junctures and ask "how".** Junctures are points where a decision, a missing signal or a surprise shaped the outcome. Probe each with questions like:
   - What were you seeing, and what did you expect to see?
   - What knowledge or past experience did you draw on?
   - What were you trying to achieve? Were there competing goals or time pressure?
   - Did you ask for help, and how did that go?
   - How could this change have been made very hard to deploy by accident?

5. **Answer the COE incident questions.**
   - Detection: when and how did we learn of the impact? How could we detect it sooner?
   - Diagnosis: what was the cause? Was a deployment in progress? How could we diagnose faster?
   - Mitigation: when did impact end? How was recovery confirmed? How could we mitigate faster?

6. **Write the analysis as contributing factors.** List the conditions that together allowed the incident, including technical, process, tooling and organisational ones, and the factors that limited the damage. If the org requires 5 Whys, run it, but follow more than one chain: each "why" can branch, and where you stop is a choice. Never end a chain at "human error"; ask how the system made that action easy, likely or invisible. Mark each contributing factor with its evidence: a timeline entry, log or graph, an interview account (say whose), or "inference". Factors that aren't confirmed go to the facilitator's open questions, not into the analysis.

7. **Write action items.** Each one has a priority, an owner and a due date, and improves prevention, detection/diagnosis, or mitigation/resolution. Typical items: update a runbook, add a metric or alert, add input validation, change a development policy, make a mitigation drillable. File each as a bug or ticket at the priority it deserves and link it.

8. **Revisit severity.** Severity was chosen fast during the incident; check it against the final impact and record any change.

9. **Write the Summary last.** It must stand alone for a senior reader: what happened, impact, time to detect, how it was mitigated, and what prevents recurrence.

10. **Scrub and share.** Remove anything that identifies end users. Keep the language blameless: describe actions and context, not character. Route the draft to a reviewer; no postmortem is left unreviewed. Then share it as widely as the org allows.

## Verification

Run the Google reviewer checklist on the draft before calling it done:

- Was the key incident data collected (timeline sources linked, graphs attached)?
- Is the impact assessment complete (who, how many, how long, start and end with time zone, data loss)?
- Is the analysis deep enough: several contributing factors, none ending at "human error"?
- Is the action plan appropriate: every item has owner, priority, due date and a filed ticket, and the priorities match the impact?
- Has it been, or will it be, shared?

Also check: every timeline bullet has a source; detect/diagnose/mitigate questions all answered; no end-user identifiers; no sentence assigns blame to a named person.

## Gotchas

- **The linear 5 Whys chain.** Allspaw's critique: the chain is artificial, root cause is constructed by where you stop, and "why" questions drift toward "who". Prefer "how" questions and several factors.
- **Hindsight and outcome bias.** Knowing the ending makes the right choice look obvious. Describe what people could see at the time.
- **Single cause for failure, many for success.** If the write-up credits luck or skill for limiting damage, the same multi-factor lens applies to the failure.
- **Interviewing with the graphs open.** Showing data first rewrites people's memory of what they saw. Collect the account first.
- **Action items without owners or dates.** They do not get done. COE treats action items as the main output.
- **Only prevention items.** Detection and mitigation-speed items often pay off sooner; the COE questions exist to surface them.
- **Writing during the incident.** Write the COE after the workload is back to normal; draft notes during the incident are fine.
- **Agent-drafted causes stated as fact.** Generated root-cause text is a hypothesis until a responder confirms it with evidence.
- **Unverified template sections.** Do not claim a document follows Google's or Microsoft's internal template; their exact headings are not public in the sources used here.

## Output

Fill [references/postmortem-template.md](references/postmortem-template.md). Hand back:

1. The completed postmortem document.
2. A list of open questions for the facilitator (accounts still to collect, facts not yet confirmed).
3. The action-item table with ticket links, or "ticket not yet filed" per item.
4. The reviewer checklist with each item marked pass or open.

## Sources

- AWS Cloud Operations blog, "Creating a Correction of Errors document" (Ossa & Hanley, 6 Nov 2023, updated 23 Jun 2025). https://aws.amazon.com/blogs/mt/creating-a-correction-of-errors-document/
- Google SRE Book (2016), ch. 15 "Postmortem Culture: Learning from Failure" (triggers, blameless, review checklist, privacy). https://sre.google/sre-book/postmortem-culture/ (read Oct 2026)
- John Allspaw, "The Infinite Hows (or, the Dangers of the Five Whys)", Kitchen Soap, 14 Nov 2014. https://www.kitchensoap.com/2014/11/14/the-infinite-hows-or-the-dangers-of-the-five-whys/
- PagerDuty Incident Response docs, "Severity Levels" (revisit severity in the postmortem). https://response.pagerduty.com/before/severity_levels/ (read Oct 2026)
- Google Cloud blog, "How Google SREs use Gemini CLI to solve real-world outages", 22 Jan 2026 (timeline and postmortem drafting, action items filed as bugs). https://cloud.google.com/blog/topics/developers-practitioners/how-google-sres-use-gemini-cli-to-solve-real-world-outages
