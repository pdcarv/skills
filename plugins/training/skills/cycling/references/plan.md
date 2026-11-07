# Plan: interview → screening → tests → plan

Builds or rebuilds the training plan. Writes `profile.yaml`, `screening.yaml`,
`tests.yaml` (protocols) and `plan.yaml`, and only with what the rider said or a
script computed (`references/state.md`).

## Contents

- 1 Load what exists
- 2 Interview
- 3 Screening and hard stops
- 4 Anchors and tests
- 5 Design the plan
- 6 Check, choose, write
- Gotchas

## 1. Load what exists

Read every file in `state/`. If a plan exists, this is a rebuild: read its
changelog and the last four weeks of sessions first, and ask only about what
has changed.

## 2. Interview

One question at a time. Give your recommended answer and why, as multiple
choice where the options are known, and allow "other". Never ask what state
already answers. Tag each answer `STATED` with today's date.

Order, most upstream first:

1. **Goal.** Target event(s): date, priority (A/B/C), duration, terrain, format.
   If there is no event, the goal as a measurable outcome.
2. **History.** Training age; the last 8-12 weeks of volume (hours, and
   sessions per week); longest recent ride; what has worked before and what has
   not, including whether structured or unstructured blocks went better. If
   the rider reports that unstructured riding beat a structured plan, record
   it under `history.what_worked` and treat it as evidence about load, volume
   or intensity, not as an anecdote to override.
3. **Availability.** Hours per week the rider can sustain, not hope for; fixed
   days; indoor vs outdoor; travel in the plan window.
4. **Health screening** (section 3).
5. **Equipment and data.** Power meter(s) and crank lengths (they affect
   comparisons between bikes), trainer, HR strap or optical, HRV device, the
   platform the data comes from.
6. **Existing tests.** Any lactate, CP, ramp or durability test, with its
   protocol. A number without a protocol is `STATED`.
7. **Preferences.** Sessions liked and avoided; what makes the rider skip
   sessions; when in the day and week training actually happens.

**Stop rule:** stop when no remaining question would change the plan. Before
asking for a missing value, check whether the plan would differ across its
plausible range (`references/method.md`, sensitivity test); ask only if it
would.

Play back the answers in a short summary and get confirmation before writing
`profile.yaml`.

## 3. Screening and hard stops

Screening flags risk; it never diagnoses.

- **Cardiac warning signs** (chest pain or pressure on exertion, fainting,
  palpitations, unusual breathlessness, a family history of sudden cardiac
  death): stop the procedure and refer to a physician before any training plan.
- **Low energy availability warning signs** (unintended weight loss, menstrual
  changes, recurrent illness or bone stress injury, persistent fatigue, low
  libido): record them in `energy_availability_flags` and refer. There is no
  single diagnostic test, and the IOC's REDs assessment tool is for clinicians,
  so the skill does not score or diagnose (`unverified`, see frameworks.md).
- **Injuries and limitations:** each becomes an `injuries_and_limitations`
  entry with what it rules out. An active injury that changes how the rider
  moves is referred, and the plan trains around it only once cleared.
- **Life stress and travel** count as load (IOC load consensus): record the
  level and source.

Play back the screening answers in a short summary and get confirmation before
writing `screening.yaml`.

## 4. Anchors and tests

Zones come only from measured thresholds (`frameworks.md`, zone anchoring):
LT1 (or VT1) for the top of the easy zone, CP or a verified MLSS for the
heavy/severe boundary. FTP and percentages of maximum are fallbacks, flagged as
such, never the anchor.

- **No measured anchors:** the plan's first block is a test block. Choose the
  protocols from `references/protocols.md` (step test, CP efforts, durability),
  play them back, and once the rider confirms, write them to `tests.yaml` as
  fixed protocols.
- **Durability:** fix the protocol now (work dose in kJ, intensity, fuelling,
  environment). Results from a different protocol are not comparable.
- **Measured anchors exist:** compute zones with `scripts/zones.py` and keep
  the run id; never hand-scale a zone.

## 5. Design the plan

Work from the target event backwards.

1. **Intensity distribution.** Choose from training status and history, not
   doctrine. Pyramidal and polarized do not differ on average; polarized may
   help VO2max in short blocks or highly trained athletes. Label the choice
   contested, with its evidence level.
2. **Volume.** Start from demonstrated recent volume, not stated capacity.
   Progress from what the rider has actually absorbed.
3. **Periodisation.** Macrocycle phases to the A-event; blocks of 3-6 weeks
   with one primary goal each; a recovery week rhythm the rider has tolerated.
4. **Durability work** for events longer than the rider's usual rides: quality
   placed after accumulated work, at most one such session a week.
5. **Strength:** optional, heavy and twice weekly where time allows, separated
   from hard riding; evidence level shown (frameworks.md).
6. **Fuelling:** session carbohydrate targets matched to the work
   (`scripts/energy.py`); 90 g/h is the default ceiling, above it is contested
   and needs gut training first.
7. **Taper** for each A-event: about 2 weeks (21 days or less), volume cut
   41-60%, progressively, intensity and session frequency kept.

Build **two or three candidate structures** that differ only on contested
points (for example distribution, or volume progression). Do not generate
candidates that differ on settled points.

## 6. Check, choose, write

1. Run each candidate through the three checks in order: `roles/adaptation.md`,
   `roles/tolerance.md`, `roles/execution.md`. A Tolerance hard-floor failure
   removes the candidate.
2. Compare survivors with `scripts/search_sim.py` (`ramp`, `robust`, `wbal`)
   where the numbers decide; otherwise compare ordinally and say so.
3. Present the candidates to the rider, each with the five-part explanation
   (SKILL.md) and the trade-off between them. The rider chooses.
4. Write `plan.yaml` version 1 (or N+1 on a rebuild, with a changelog entry).
   Every session target comes from a `zones.py` run id.
5. Run `scripts/verify_output.py` on the plan summary before showing it.
6. Report the files written.

## Gotchas

- **Interview as a form.** Asking every question regardless of the answers so
  far wastes the rider's attention. Skip what is settled; go deep where the
  answer changes the plan.
- **Stated capacity.** "I can do 15 hours" is not demonstrated load. Build from
  the last 8-12 weeks.
- **Polarized by default.** It is the most published distribution, not the
  best-supported one for every athlete.
- **Zones from a number without a protocol.** That is a `STATED` value; the
  zones inherit it and the plan should say so.
- **A plan the rider cannot see the reason for.** Every block carries its
  rationale; a plan without one cannot be adapted later.
