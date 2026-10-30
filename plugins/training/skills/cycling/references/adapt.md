# Adapt: disruptions the rider raises

Runs only when the rider raises a condition and asks for the plan to adapt.
Writes `conditions.yaml`, the changelog entry and the new plan version, and
`screening.yaml` when the condition is a health matter.

## Contents

- 1 Record the condition
- 2 Apply the matching rule
- 3 Check, propose, write
- Rules by condition
- Gotchas

## 1. Record the condition

Ask only what the rule needs: what happened, since when, how severe, and what
the rider can do now. Record the episode in `conditions.yaml` in the rider's
words.

## 2. Apply the matching rule

Find the condition below. Each rule carries its evidence level; anything marked
`unverified` was extracted from a source but not checked this session and must
be retrieved before it is cited.

## 3. Check, propose, write

Run the proposed change through the three checks, present it with the
five-part explanation and get the rider's approval. Then write the changelog
entry and the new plan version, and set the episode's milestones. Report the
files written. The episode stays open until `return_to_full_load` is reached.

---

## Rules by condition

### Illness (acute respiratory and similar)

Source: IOC consensus on acute respiratory illness in athletes, 2023
(`unverified` detail below; retrieve before citing).

1. **Grade severity by symptoms:** above the neck only, regional, or systemic
   (fever, body aches, chest symptoms, gastrointestinal). Systemic symptoms
   mean no training and, if severe or persistent, a referral.
2. **Return in steps.** Before resuming moderate or hard training, a graded
   exercise challenge (easy, short), with the response watched over the next
   24 hours. Progress only if symptoms do not return.
3. **Two milestones:** return to participation (the first session back) and
   return to full load (pre-illness type, intensity, duration and frequency).
   Record both.
4. The "neck check" rule rests on expert opinion only. It may be mentioned as
   such, not as evidence.
5. Planning horizon: most episodes cost little training time and symptoms last
   about a week on average (`unverified`).

### Missed training

1. **Do not make up missed load.** Resume from the current week of the plan,
   not from where the rider left off, and do not add the missed sessions on top.
2. **Short break (up to about 4 weeks):** expect measurable fitness loss within
   about two weeks (VO2max roughly 7% after 12 days in one classic study,
   `unverified`). For breaks over about two weeks, reduce the next week's
   volume and intensity and re-test before trusting old zones.
3. **Longer than 4 weeks:** treat as a rebuild. Run the Plan procedure's
   anchors step again.
4. **Repeated missed sessions** are an Execution finding, not a fitness one:
   reduce or restructure (`roles/execution.md`).

### Heat and travel to a hot event

1. Heat acclimatisation is the most important intervention for performance in
   the heat: repeated exercise-heat exposures over about 1-2 weeks before the
   event (`unverified`).
2. Start hot sessions well hydrated and limit dehydration; add hydration to the
   session plan.
3. Flag early-season hot events and mass-participation events in heat for a
   rider who is not acclimatised.
4. Travel across time zones and long travel days count as load; lighten the
   day of and after travel.

### Altitude

No evidence was verified for amateur altitude rules. State that, give only
general caution, and record an open question if a plan depends on it.

### Injury

1. Refer any injury that changes how the rider moves, causes pain that worsens
   during or after riding, or follows a crash.
2. Train around it only once cleared, within the constraint the clinician set,
   recorded in `screening.yaml`.

### Low energy availability

Warning signs end the procedure with a referral (`references/plan.md`,
screening). The skill does not adjust fuelling or volume to treat suspected
low energy availability on its own.

### Life stress

Psychological load and poor sleep count as load (IOC load consensus 2016).
Reduce intensity before volume, keep the sessions the rider values, and
re-check after a week.

### Approaching an A-event

Apply the taper rule: about 2 weeks, volume cut 41-60% progressively,
intensity and session frequency kept (Bosquet 2007; Wang 2023).

---

## Gotchas

- **Adapting without being asked.** If the rider mentions a cold in passing,
  ask whether they want the plan adapted; do not change it unprompted.
- **Making up lost sessions.** It stacks load exactly when fitness is lowest.
- **One milestone for illness.** "Back on the bike" is not "back to full
  training"; the gap is where relapses happen.
- **Treating a health flag as a training problem.** Referral comes first.
