# Protocols

Canonical session structures and test procedures. The Plan procedure picks
test protocols from here and fixes them in `state/tests.yaml`.

Intensities are expressed as fractions of **measured LT2**, not of FTP. Convert
with `scripts/zones.py`, which emits these as `session_targets_w`. Where CP has
been measured, check the targets against it: CP has the better support as the
heavy/severe boundary (`frameworks.md`, thresholds and zones).

Where a protocol is contested, it is marked and listed in the contested register
of `frameworks.md`. Do not present a contested protocol as settled.

## Contents

- Testing: lactate step test, MLSS verification, critical power, durability, aerobic decoupling
- Sessions: sub-threshold, threshold / over-under, VO2max short and long, torque, endurance, fatigued-state quality
- Strength
- Environmental: heat, altitude
- Fuelling

---

## Testing

### Lactate step test
4-minute stages, fixed cadence 80–85 rpm, resting sample first, 20 W increments
from a start well below expected LT1. Sample in the final 30 s of each stage.

Stage duration is itself a disagreement: 8-minute stages give a cleaner steady
state and better LT1 resolution; 3–4-minute stages are practical and preferred
where the priority is LT2 and the full HR-power map. 4 minutes is the standing
compromise. LT1 carries proportionally higher relative error than LT2 because
the absolute lactate differences at low intensity are small.

Standardise or the result is noise: time of day, caffeine dose, prior 48 h load,
pre-test meal, fan, cadence, sampling site. A novice sampler inflates later
stages more than early ones, which artificially steepens the curve and drags
apparent thresholds downward.

### MLSS verification
30-minute constant-power efforts on separate days, bracketing the step-test LT2.
Steady state confirmed when lactate rises less than 1.0 mmol/L between minute 10
and minute 30. The tiebreaker when fixed-threshold and baseline-plus-delta
methods disagree.

### Critical power
Two to five maximal efforts of 2–15 minutes, on separate days, fully rested.
Efforts longer than 20 minutes bias CP low. `power_duration.py` reports subset
spread; a large spread means the fit is not usable as a planning anchor.

### Durability test
Standardised warm-up, fresh 5-min and 20-min maximal efforts. Separate day: same
warm-up, then steady riding at ~80% of fresh 20-min power to a target work dose,
then repeat both efforts. 1000 kJ is the amateur-validated dose; 2500 kJ has
published percentile references for trained cohorts.

Decay is only comparable at matched kJ and under the same protocol. Record the
protocol (work dose, intensity, fuelling, environment) in `tests.yaml` and run
with `durability.py`. Until a durability result exists, no durability target
may be prescribed.

### Aerobic decoupling
Power:HR first half versus second half of a long steady ride. Free, computed
from rides already being done. Under 5% is the conventional well-adapted
benchmark. Confounded by heat, hydration and underfuelling, all of which must be
excluded before reading it as durability.

---

## Sessions

### Sub-threshold (double-threshold family)
90–98% LT2, 3–5 × 10–20 min, lactate held in a target band rather than a power
target. Accumulates threshold time at a cost that permits repetition. The
originating protocol presumes a large chronic base; at amateur volume, run it as
a single session rather than twice in a day, and validate before repeating.

### Threshold / over-under
Over 105–107% LT2, under 88% LT2, alternating 2–3 min blocks, 3–4 × 12–20 min
total. Trains lactate clearance rather than tolerance.

### VO2max — short intervals
30 s at 110–118% LT2, 15 s easy, 13 reps per set, 3 sets, 3 min between sets.
Keep the legs turning through the 15 s.

### VO2max — long intervals
4–5 × 4–6 min at 108–112% LT2, 2.5–3 min recovery.

**Contested: the choice between these two.** The effort-matched
superiority of short intervals did not survive replication, and time-near-VO2max
as a surrogate for adaptation is disputed. Present both; select on rider
tolerance and session context, not on a claimed superiority.

### Torque / strength-endurance
82–88% LT2 at 50–60 rpm, 3–5 × 8–12 min. Low cadence raises peak pedal force;
contraindicated where a knee or patellar tendon issue is active.

### Endurance
LT1 −5 to −10%, with the ceiling set by measured LT1 rather than a percentage of
FTP. The most under-prescribed session in an amateur plan and the one that
drives economy.

### Fatigued-state quality
Quality work placed after 2000–2500 kJ of accumulated riding rather than fresh.
The session that trains the quality a long event actually selects for. Costs
more recovery than its TSS suggests; one per week at most.

---

## Strength

Heavy load at or above 80% 1RM, 2×/week, maintained in season. Half squat
4 × 4–6, single-leg leg press, single-leg hip flexion, ankle plantar flexion.

The KPI is **fatigued efficiency and late-race power**, not fresh threshold,
and the plan's test battery should reflect it.
Nothing in the meta-analytic moderator data supports longer blocks or higher
frequency.

Separate strength from hard riding by at least 6 h, ideally onto an easy or rest
day. Upper-body work does not interfere with the same day's riding.

---

## Environmental

### Heat
Before a hot event, acclimatise with repeated exercise-heat exposures over about
1-2 weeks; start hot sessions hydrated (`frameworks.md`, environment). Beyond
that, dose-response, not a block. Adaptation scales with exposure count and duration;
haematological gains decay within roughly one to three weeks of stimulus
removal, so it is a maintenance commitment. Sessions replace endurance work, not
quality work, and are contraindicated in the 48 h before a VO2max or threshold
session.

### Altitude
Live-high-train-low, with iron status checked before the camp — deficiency gates
the erythropoietic response.

---

## Fuelling

Carbohydrate per hour by duration, as a band rather than a point
(`energy.py --cho-plan`). Above 90 g/h is contested (`frameworks.md`):

| Duration | g/h band | Note |
|---|---|---|
| <1 h | 0–30 | optional for trained athletes |
| 1–2 h | 30–60 | glucose-only transport sufficient |
| 2–3 h | 60–90 | multiple transportable CHO indicated |
| 3 h+ | 60–90 | 90 is the default ceiling; above it only after gut training, presented as contested, and the argument is energy balance rather than performance |

Gut training is progressive exposure in training, never first use on race day.

Availability matched to session intent: high for threshold, VO2max and fatigued-
state work; low-availability sessions restricted to endurance work whose
adaptive signal does not depend on glycolytic flux.

Energy availability floor: 45 kcal/kg FFM/day as the working target, 30 as the
clinical flag. `energy.py` computes it. This constraint outranks the plan.
