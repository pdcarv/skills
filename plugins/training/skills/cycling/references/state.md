# State

The athlete's data lives in `state/` (a link to `<private-folder>/training/cycling/state/`).
This file defines every file that may exist there, which procedure may write it,
and its schema.

## Contents

- Rules
- Provenance on every value
- Files: profile, screening, tests, plan, sessions, wellness, conditions,
  changelog, open-questions, contradictions

## Rules

1. **Created lazily.** A file is created the first time a procedure has a real
   value to put in it. Never create an empty file, a template, or a placeholder.
2. **Only the named writer writes.** Each file below lists the procedures
   allowed to write it. Any other procedure reads it only.
3. **Only what was given or computed.** A value enters state because the rider
   said it this session (`STATED`), a script computed it (`COMPUTED`/`DERIVED`),
   or a test with a recorded protocol measured it (`MEASURED`). Never from model
   memory, never from an earlier conversation that is not in state.
4. **Append, do not overwrite history.** Superseded values stay, marked with
   `superseded_by` and a date. A plan change creates a new plan version.
5. **Report every write.** End each procedure with the files and fields written.
6. **Schema version.** Every file starts with `schema_version: 1`.

## Provenance on every value

```yaml
value: 225
unit: W
source: STATED | MEASURED | DERIVED | COMPUTED
date: 2026-10-30
method: "how it was obtained; for MEASURED, the test id in tests.yaml"
```

Anything derived inherits the weakest provenance of its inputs.

---

## `profile.yaml` — written by: plan; adapt (availability changes only)

```yaml
schema_version: 1
athlete: {sex, age, mass, height}            # each with provenance
goals:
  - {event, date, priority: A|B|C, demands: "duration, terrain, format"}
history:
  training_age_years: ...
  recent_volume_h_per_week: ...               # last 8-12 weeks, STATED or COMPUTED
  what_worked: "rider's account, e.g. structured vs unstructured blocks"
  what_did_not: ...
availability:
  hours_per_week: ...
  fixed_days: ...                             # days that cannot move
  indoor_outdoor: ...
equipment:
  bikes: [{name, crank_mm, power_meter}]
  trainer: ...
  data_sources: [power, hr_strap, hrv_device, ...]
preferences: {session_types_liked, session_types_avoided, adherence_notes}
```

## `screening.yaml` — written by: plan; adapt

Screening flags risk and routes to a clinician. It never diagnoses.

```yaml
schema_version: 1
screened: 2026-10-30
cardiac_warning_signs: {present: false, detail: null, referred: null}
energy_availability_flags:                    # warning signs only; REDs is diagnosed by a clinician
  present: false
  items: []                                   # e.g. menstrual changes, recurrent illness, bone injury
  referred: null
injuries_and_limitations:
  - {id: L-001, description, since, status: active|managed|resolved,
     constraint_on_training: "what it rules out", cleared_by: null}
medications_relevant_to_training: []
life_stress: {level: low|moderate|high, source, date}
```

## `tests.yaml` — written by: plan (test plan); review (when a session is a test)

The protocol is part of the result. Results from different protocols are not
compared.

```yaml
schema_version: 1
protocols:
  - id: TP-durability-1
    kind: durability | step_test | cp | mlss | ramp
    definition: "warm-up, efforts, work dose kJ, intensity, fuelling g/h, environment"
    fixed_on: 2026-10-30
tests:
  - id: T-001
    protocol: TP-durability-1
    date: ...
    results: {...}                            # COMPUTED by the named script
    script_run: R-03                          # manifest run id
    conditions: {temperature_c, fuelling_g_h, sleep_h, notes}
```

## `plan.yaml` — written by: plan; review and adapt only through a changelog entry

```yaml
schema_version: 1
current_version: 3
versions:
  - version: 3
    created: 2026-11-12
    reason: "C-007 in changelog.yaml"
    anchors: {lt1: T-001, cp: T-002}          # test ids, never bare numbers
    intensity_distribution: {model: pyramidal, reason, evidence_level, contested: true}
    macrocycle: [{phase, start, end, goal}]
    blocks:
      - id: B-02
        start: ...
        weeks: 4
        goal: ...
        rationale: "five-part WHAT/WHY/EVIDENCE/CONTESTED/CHANGES IF"
        weeks_detail:
          - week: 1
            sessions:
              - {id: S-02-1-1, day, type, duration_min, targets: "zone or W from zones.py run",
                 planned_rpe, purpose, fuelling_g_h}
    taper: {start, length_days, volume_reduction_pct, pattern: progressive|step}
    success_criteria: ["measurable outcome tied to a test protocol"]
```

## `sessions/YYYY-MM-DD-<slug>.yaml` — written by: review

One file per session the rider logs.

```yaml
schema_version: 1
date: ...
planned: S-02-1-1 | null                      # null = unplanned session
executed:
  duration_min: ...
  external: {avg_w, np_w, work_kj, if, tss, anchor_kind}
  internal: {avg_hr, rpe, srpe_au, decoupling_pct}
  intensity_distribution: {z1_pct, z2_pct, z3_pct, method: hr_time_in_zone | session_goal | power}
  conditions: {temperature_c, indoor, fuelling_g_h, gut_tolerance}
compliance: {metric, pct, band}               # load.py
rpe_vs_planned: ...
wellness_same_day: {sleep_h, soreness, stress, mood}   # only if the rider gave them
notes: "rider's words"
script_runs: [R-01, R-02]
decision: continue | adjust_next | adjust_week | adapt | refer
changelog_entry: C-008 | null
```

## `wellness/YYYY-MM.yaml` — written by: review, only once the rider supplies daily data

One record per local date. Partial records are fine.

```yaml
schema_version: 1
days:
  2026-11-03: {rmssd_ms, resting_hr, sleep_h, sleep_quality, soreness, fatigue, stress, mood}
hrv_protocol: {device, position, time: "on waking", transform: ln, baseline_days: 28,
               window: 7, band_sd: 0.5, baseline_mode: fixed}
```

## `conditions.yaml` — written by: adapt

```yaml
schema_version: 1
episodes:
  - id: E-001
    kind: illness | injury | travel | heat | altitude | life_stress | missed_training
    raised: 2026-11-20
    detail: "rider's words"
    severity: "for illness: above_neck | regional | systemic"
    milestones:
      return_to_participation: null           # first session back
      return_to_full_load: null               # pre-episode type, intensity, duration, frequency
    referral: null
    status: open | closed
    changelog_entries: [C-009]
```

## `changelog.yaml` — written by: review; adapt

Every plan change and every off-bike prescription, with whether it was done.

```yaml
schema_version: 1
entries:
  - id: C-008
    date: ...
    kind: plan_change | prescription
    trigger: "session file, condition id, or rider request"
    change: "what changed, from plan version N to N+1"
    rule: "the rule in review.md or adapt.md that applied"
    evidence: "citation and level, or 'convention'"
    reverses_if: "observation that would undo it"
    executed: true | false | partial | unknown  # prescriptions only; unknown blocks re-prescribing
```

## `open-questions.yaml` — written by: any procedure, when a question blocks a decision

```yaml
schema_version: 1
questions:
  - {id: Q-001, question, raised, blocks: [decision], closes_when, status: open|closed}
```

## `contradictions.yaml` — written by: any procedure, for athlete-level conflicts only

For conflicts in this athlete's data (a STATED value against a MEASURED one,
two tests that disagree). Contested science lives in `frameworks.md`, not here.

```yaml
schema_version: 1
items:
  - {id: K-001, conflict, sources: [T-001, "STATED 2026-10-30"], resolution: null}
```
