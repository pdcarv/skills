# Review: after every session the rider logs

Reads the plan, computes what happened, compares it with what was planned, and
decides whether anything changes. Writes `sessions/<date>-<slug>.yaml`, a
`wellness/` record if the rider gave daily data, a `tests.yaml` result if the
session was a test, and a `changelog.yaml` entry only if something changed.

## Contents

- 1 Ingest
- 2 Data quality
- 3 Compute
- 4 Read the context
- 5 Decide
- 6 Explain and write
- Gotchas

## 1. Ingest

Accept whatever the rider provides: a FIT/CSV export, a platform summary, or a
description. Ask for session RPE (0-10) if it is missing; it is the cheapest
valid internal-load measure. Ask for how the session felt and anything unusual
(heat, fuelling, sleep, stress) in one question, not a questionnaire.

Match the session to the planned session in `plan.yaml` by date and type. An
unmatched session is `planned: null`, not an error.

## 2. Data quality

Before computing, check: power and HR present and plausible; dropouts; a
different bike or crank length from the planned one; indoor vs outdoor; HR
source (strap vs optical). Record any issue in the session notes and drop the
metrics it invalidates rather than reporting them. A missing stream or field is
`unavailable`: never a fail, never estimated, never counted as complete.

## 3. Compute

Run the scripts and keep every run id:

- `scripts/load.py` with the power file: NP, IF, TSS (anchored on measured
  LT2; FTP only as a flagged fallback), work in kJ.
- `scripts/load.py --rpe --minutes`: sRPE. Add `--planned-rpe` for the
  perceived-vs-planned mismatch.
- `scripts/load.py --planned --completed --metric`: compliance on the metric the
  session was planned in (usually duration; kJ or TSS for structured work).
- `scripts/load.py --decoupling` for steady rides longer than about an hour.
- Executed intensity distribution, stating the method (HR time in zone,
  session goal, or power). Methods disagree, especially for short hard efforts.
- `scripts/hrv.py` only if `wellness/` has daily RMSSD; it reports
  `baseline_incomplete` until the baseline exists.
- If the session was a test, the matching test script and protocol.
- `scripts/gate.py` once per interval type with a power target: the executed
  power of each work rep, and `target_w`, `reps`, `ceiling` and `start_reps`
  from the session's `intervals` in `plan.yaml` (if missing, say so and use
  planned reps as the ceiling), and `--prior-misses` from the `gate` rows of this block's earlier session
  files; an earlier session with no `gate` row gets its own `gate.py` run from
  its laps. Never judge a target by eye or with ad-hoc code.

## 4. Read the context

- **Recent execution, not just today.** Compare planned vs executed for the
  hard sessions of the last 7-14 days. A target missed in two or more sessions
  is a finding even when today's session was easy or on target. Read it from
  the `gate` rows of those session files. Check the
  coming week's targets against what the rider recently held for the same
  duration.
- **External vs internal.** Planned power with a higher-than-usual HR or RPE,
  or lower power at the usual RPE, can signal fatigue. One session is a data
  point; look for the same direction across two or three.
- **Decoupling** above about 5% on a steady ride is read only after excluding
  heat, dehydration and under-fuelling.
- **Wellness and life stress** the rider reported.
- **HRV status** (inside / below / above band) as one input, never alone.
- **Trends:** CTL/ATL/TSB, monotony and ACWR may be shown as descriptive trends
  over the last weeks. They never decide (SKILL.md, non-negotiable 7).

## 5. Decide

Choose the smallest response that fits the evidence. Each decision names the
rule that applied.

| Decision | When |
|---|---|
| **Continue** | Compliance green or yellow for a reason the rider gave; internal response as expected |
| **Adjust next session** | One session with a clear mismatch (RPE ≥2 above plan, HR elevated at planned power, poor sleep or high stress) |
| **Adjust the week** | The same mismatch across 2-3 sessions, the same target missed in 2-3 sessions (hold or recalibrate it), HRV below band for the rolling week, or repeated orange/red compliance |
| **Go to Adapt** | The rider reports illness, injury, travel, heat, or missed days, and wants the plan adapted (`references/adapt.md`) |
| **Refer** | Any cardiac warning sign, a suspected injury, or low energy availability warning signs |

Rules that are conventions (the compliance bands, the 2-point RPE flag, the
5% decoupling benchmark, the HRV band) are labelled as conventions. A missed
session is not made up by adding its load to later sessions.

### Progression gate (interval targets)

Push by default; back off only on performance evidence. `scripts/gate.py`
applies this table per interval type, comparing the mean of the work reps with
the target:

| Result | Next time |
|---|---|
| Mean at or above target −2%, no rep below −5% | **Progress one step:** add a rep up to the block's ceiling; at the ceiling, raise the target 2-3% and return to the starting rep count |
| Mean −2% to −5%, or a rep below −5% | **Hold** the target |
| Mean below −5%, or a miss today after a miss in an earlier session at the same target | **Recalibrate** to the mean of the reps held |

- Volume progresses by adding reps inside a 3:1 block (Almquist 2022:
  4→5→6 × 5 min). At matched load, interval order made no difference
  (Sylta 2016). The 2% and 5% bands and the 2-3% step are conventions.
- Back off (cut intensity or volume, or add rest) only when targets within
  recent capacity fail in 2+ sessions with no explanation (heat, fuelling,
  sleep), or a benchmark falls beyond noise. Never on HR, HRV or CTL/TSB
  alone (Meeusen 2013). A dip right after a planned hard block is expected:
  hold, do not de-load.
- Benchmark change, single retest of 20-min power: under 3% is noise, 3-7%
  probable, above 7% real (CV 2.9%, Borszcz 2020; band derived). A first
  test reads about 1% low (Hopkins 2001).
- Write each target as a process goal ("each 3-min rep at 320 W, first rep
  no harder than the rest"), with the outcome goal as context; process goals
  had the largest effects in sport (Williamson 2022). Check the last review's
  if-then plan at the next review.

A change goes through the three checks (SKILL.md) before it is proposed, and
the rider approves it before `plan.yaml` changes.

## 6. Explain and write

Tell the rider, in this order: what happened (numbers with their notes), how it
compares with the plan, what it means (five-part explanation for any change),
and what the next session is. For each interval type, one line: the gate
verdict and the next target, as a process goal. Overriding a verdict (heat,
illness, a taper before a test) names the reason. State a miss or a poor
result plainly, first, with its numbers; do not soften it.

Write the session file (`sessions/<date>-<slug>.yaml`: the logged session, its
computed metrics and their run ids), the wellness record if given, and, if the
rider approved a change, a new plan version plus its changelog entry. Run
`scripts/verify_output.py --draft <summary> --manifest <manifest>` on the
summary; add `--ledger` only when it cites studies. Report the files written.

## Gotchas

- **Reacting to one number.** A single high RPE or low HRV morning is noise
  until it repeats or the rider explains it.
- **Compliance as quality.** Green duration compliance says nothing about
  whether the intervals were hit. Check the intervals separately.
- **Optical HR in decoupling.** Wrist HR is too noisy for drift; say so.
- **TSB as a readiness score.** It is a model output with no demonstrated
  predictive validity; never "you are fresh, so go hard" on TSB alone.
- **Writing state the rider did not give.** If a field is missing, leave it
  out; do not infer sleep, stress or fuelling.
