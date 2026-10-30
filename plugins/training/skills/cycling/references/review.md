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
metrics it invalidates rather than reporting them.

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

## 4. Read the context

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
| **Adjust the week** | The same mismatch across 2-3 sessions, HRV below band for the rolling week, or repeated orange/red compliance |
| **Go to Adapt** | The rider reports illness, injury, travel, heat, or missed days, and wants the plan adapted (`references/adapt.md`) |
| **Refer** | Any cardiac warning sign, a suspected injury, or low energy availability warning signs |

Rules that are conventions (the compliance bands, the 2-point RPE flag, the
5% decoupling benchmark, the HRV band) are labelled as conventions. A missed
session is not made up by adding its load to later sessions.

A change goes through the three checks (SKILL.md) before it is proposed, and
the rider approves it before `plan.yaml` changes.

## 6. Explain and write

Tell the rider, in this order: what happened (numbers with their notes), how it
compares with the plan, what it means (five-part explanation for any change),
and what the next session is.

Write the session file, the wellness record if given, and, if the rider
approved a change, a new plan version plus its changelog entry. Run
`scripts/verify_output.py` on the summary. Report the files written.

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
