# Postmortem / COE template

Section order follows the AWS COE structure, with the analysis section reworked along Allspaw's "Infinite Hows" lines. Write the Summary last. Use one time zone throughout and state it. Include no end-user identifiers.

```markdown
# Postmortem: <short title>   Incident: <id>   Status: DRAFT | IN REVIEW | FINAL
Authors: <names>   Reviewer: <name>   Date: <YYYY-MM-DD>
Severity: during incident SEV-<n> / after review SEV-<n> (reason for any change)
Trigger(s) met: <user-visible impact | data loss | on-call intervention | long resolution | monitoring miss | requested by <role>>

## 1. Summary  (write last; must stand alone for a senior reader)
<What happened, who was affected, how long, time to detect, how it was mitigated,
what will prevent or shorten a recurrence. 4-6 sentences.>

## 2. Impact
- Customer effect: <what users experienced, in user terms>
- Scope: <customers / requests / regions affected; how counted>
- Start: <YYYY-MM-DD HH:MM TZ>   End: <YYYY-MM-DD HH:MM TZ>   Duration: <...>
- Data loss: <none | description>
- SLO / error budget consumed: <if known>

## 3. Timeline  (TZ: <zone>; one source link per line)
- <HH:MM> <event>  [source]
- ...
Key intervals: time to detect <...>, time to declare <...>, time to mitigate <...>, time to resolve <...>

## 4. Metrics
<Graphs of the affected SLIs before, during and after, with change events annotated.>

## 5. Incident questions
### Detection
- When and how did we learn of the impact? Was it an alert or a human?
- How could we detect it sooner?
### Diagnosis
- What caused it (see section 6)? Was a deployment in progress?
- How could we diagnose faster?
### Mitigation
- When did impact end, and how was recovery confirmed?
- How could we mitigate faster? Was a generic mitigation available and drilled?

## 6. Contributing factors and critical junctures
### Participant accounts
<Per participant (by role): their account, summarised and confirmed by them.>
### Critical junctures
| Time | Juncture | What people saw and expected | Goals / pressures | What made it hard |
|---|---|---|---|---|
### Contributing factors
- <Technical, process, tooling, organisational conditions that together allowed this>
### What limited the damage
- <Factors that helped: detection that worked, mitigations that worked, people and tools>
### (Optional) 5 Whys
<Only if the org requires it. Show branches, not one chain; no chain ends at "human error".>

## 7. Action items  (the main output)
| # | Action | Type (prevent / detect-diagnose / mitigate-resolve) | Priority | Owner | Due date | Ticket |
|---|---|---|---|---|---|---|

## 8. Review checklist
- [ ] Key incident data collected and linked
- [ ] Impact assessment complete
- [ ] Analysis deep enough (several factors; no "human error" end point)
- [ ] Action items appropriate, owned, dated, filed at the right priority
- [ ] Shared with <audience>
```
