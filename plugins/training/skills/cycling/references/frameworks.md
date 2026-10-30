# Scholar lenses

The research the skill reasons from, as **citable frameworks**. A lens is a
named analytical position, the people whose work it rests on, its evidence
level and its status. The three checks reach into this file. A lens is **not a
voice to perform**: researchers are cited, never impersonated (persona fidelity
in `references/method.md`). Experiments with expert personas found no reliable
accuracy gain and some loss on knowledge tasks, which is why.

Machine-readable domain tags and staleness windows live in `frameworks.yaml`.

**How to read an entry**

```
**Lens** — whose work · evidence: <level> · status: settled | contested | unverified · `domain: x`
```

- **Evidence level:** meta-analysis > RCT > observational > consensus > expert
  opinion > convention.
- **Status:** `contested` means present both sides, every time. `unverified`
  means the claim was extracted from a source but not checked; retrieve it
  before citing.
- A lens name is not a citation. Retrieve the source in-session before quoting
  an effect size or writing (Author, Year) in output.

## Contents

- Contested register
- Thresholds and zones
- Intensity distribution and periodisation
- Load and monitoring
- Durability
- Strength and concurrent training
- Fuelling and energy availability
- Tapering
- Illness, detraining and return
- Environment
- Psychology and adherence
- Declared, not yet sourced
- Rules for using this file

---

## Contested register

These are live disagreements in the literature. Present both positions; do not
assert one.

| Topic | One side | Other side |
|---|---|---|
| Polarized vs pyramidal distribution | Polarized may raise VO2max more in short blocks or highly trained athletes | No average difference in VO2max or time trial across 13 studies (IPD network meta-analysis, 2025) |
| Short vs long VO2max intervals | 30/15 short intervals beat effort-matched long intervals (2014/2015) | Did not replicate (2020); time near VO2max as a surrogate is disputed |
| Carbohydrate above 90 g/h | Higher oxidation at 120 g/h in small studies | No direct evidence of better performance; current guidelines stop at 90 g/h |
| ACWR as an injury predictor | Some reviews report support | Others find spikes unrelated to injury; heterogeneous load measures |
| HRV-guided vs predefined training | Within-group gains and fewer non-responders | Between-group differences small and non-significant (2021 meta-analyses) |

---

## Thresholds and zones

**Zone anchoring on measured thresholds** — Jamnick, Pettitt, Granata, Pyne &
Bishop (Sports Med 2020) · evidence: systematic review · status: settled on
direction · `domain: threshold_determination`. Fixed percentages of maximum
(%VO2max, %HRmax, %max power) give variable responses and do not place athletes
in the same domain. LT1/VT1 has support as the moderate/heavy boundary; CP has
the best support for heavy/severe. The evidence concerns acute responses, not
long-term adaptation.

**FTP is not a threshold** — Wong, Burnley, Mauger, Sun & Hopker (J Sports Sci
2023) · evidence: small experimental (n=13) · status: settled on direction ·
`domain: threshold_determination`. Time to exhaustion at FTP was about 34 min,
and FTP should not be treated as the heavy/severe boundary or as one-hour power.
This is why `zones.py` treats FTP as a flagged fallback.

**Critical power / W′** — Jones, Vanhatalo, Skiba · evidence: experimental,
replicated · status: settled · `domain: threshold_determination`. CP as the
asymptote of the power-duration relation, W′ the finite work above it. CP sits
slightly above MLSS with wide individual agreement limits and depends on the
prediction-trial protocol. Two-point fits carry no residual information;
`power_duration.py` reports subset spread for this reason.

**Six-zone metabolic model** — San Millán · evidence: observational and
practitioner · status: unverified · `domain: threshold_determination`. Zones by
substrate use and lactate kinetics; LT1 as the endurance ceiling.

**Continuous field individualisation** — Bu · evidence: expert opinion ·
status: unverified · `domain: threshold_determination`. Measure the athlete
rather than infer from population norms.

## Intensity distribution and periodisation

**Intensity distribution (TID) network meta-analysis** — Rosenblat et al., incl.
Seiler (Sports Med 2025) · evidence: IPD network meta-analysis (13 studies,
n=348) · status: contested · `domain: training_distribution`. No average
difference between polarized and pyramidal for VO2max or time trial. A
subgroup result suggests competitive athletes may gain more VO2max from
polarized and recreational athletes from pyramidal: a hypothesis, not a rule.

**Polarized 80/20 hierarchy** — Seiler · evidence: observational (descriptions
of elite practice) · status: contested · `domain: training_distribution`. Most
well-trained athletes train pyramidally; some world-class athletes use
polarized blocks in certain phases (Stöggl & Sperlich, Front Physiol 2015;
Oliveira, Boppre & Fonseca, Sports Med 2024).

**How TID is measured changes the label** — status: settled ·
`domain: training_distribution`. The same programme can be polarized by session
goal and pyramidal by HR time in zone. Always state the method.

**Lactate-controlled double threshold** — Bakken · evidence: practitioner ·
status: unverified for amateurs · `domain: training_distribution`. Presumes a
large chronic base; amateur transferability is the open question.

**Block periodisation** — Issurin; Rønnestad's HIT-block application ·
evidence: RCT (small) and practitioner · status: unverified ·
`domain: training_distribution`.

**Short vs long intervals** — Rønnestad · status: contested (see register) ·
`domain: interval_format`.

## Load and monitoring

**Load management as injury and illness control** — Soligard et al., IOC
consensus (BJSM 2016) · evidence: consensus · status: settled on direction ·
`domain: load_monitoring`. Poor load management is a major risk factor for
injury. Load includes rapid changes in training, congested competition,
psychological load and travel. Prescribing and monitoring are linked tasks.

**Session RPE, monotony, strain** — Foster · evidence: validation studies ·
status: sRPE valid and reliable (`unverified` detail); monotony and strain are
descriptive · `domain: load_monitoring`. sRPE = RPE × minutes. Planned and
perceived intensity often disagree, so the mismatch is tracked.

**Fitness-fatigue model limits (CTL/ATL/TSB)** — Banister (model); Marchal et
al. (Sci Rep 2025), Ceddia, Bondell & Taylor (J Quant Anal Sports 2026),
Ferguson (thesis 2014) · evidence: modelling and small observational ·
status: settled on direction · `domain: load_monitoring`. The model is
ill-conditioned and overfits; the fatigue term adds no cross-validated
prediction; TrainingPeaks fitness, fatigue and form did not usefully predict
race power; optimised literally it gives no taper. Show as trends, never as
triggers.

**ACWR** — status: contested (see register) · `domain: load_monitoring`.
`load.py` reports it with that caveat.

**HRV-guided training** — Plews & Buchheit (rolling-mean method); Javaloyes et
al. (IJSPP 2019, cyclists); Manresa-Rocamora et al. (IJERPH 2021) and Düking et
al. (JSAMS 2021) meta-analyses · evidence: meta-analysis of small RCTs ·
status: contested · `domain: load_monitoring`. Small, non-significant gains over
predefined training; possibly fewer non-responders. The working convention: a
baseline of about 4 weeks, then a 7-day rolling RMSSD mean against a personal
band. Index, baseline method and band width are unsettled. `hrv.py`.

**Aerobic decoupling** — evidence: convention · status: settled as a
descriptive measure · `domain: durability`. Power:HR drift on a long steady
effort; confounded by heat, hydration and under-fuelling before it says
anything about durability. Under 5% is a convention.

## Durability

**Durability as a fourth dimension** — Maunder et al. (Sports Med 2021); Jones
(J Physiol 2024); Hunter, Maunder, Jones, Gallo & Muniz-Pumares (Exp Physiol
2025) · evidence: reviews and experimental · status: settled ·
`domain: durability`. The deterioration of physiological variables and
performance over prolonged exercise is distinct from fresh thresholds. The
fatiguing protocol changes the result, so fix and record each athlete's
protocol (work dose, intensity, fuelling, environment).

**Efficiency decline over prolonged effort** — status: settled ·
`domain: durability`. Interventions that show nothing fresh may show up
fatigued; a strength block's KPI is fatigued power.

## Strength and concurrent training

**Heavy strength for endurance cyclists** — Rønnestad, Mujika; Vikmoen et al. ·
evidence: RCTs and meta-analysis · status: settled on direction, `unverified`
detail · `domain: strength_for_cycling`. Heavy loads twice weekly, kept in
season. Effects land on efficiency (including late in long rides) and anaerobic
power, not VO2max. One trial in well-trained female athletes found lower oxygen
uptake and HR in the last two hours of a 180-min ride after 11 weeks.

**Concurrent training interference** — Coffey, Hawley · evidence: umbrella
reviews · status: unverified · `domain: concurrent_training`. Aerobic capacity
is largely spared; separate strength from hard riding.

**Force-velocity profiling** — Samozino · status: unverified ·
`domain: strength_for_cycling`.

## Fuelling and energy availability

**Fuel for the work required** — Burke, Hawley · evidence: reviews · status:
settled on direction · `domain: nutrition_periodisation`. Carbohydrate matched
to each session's demands; train-low strategies show limited performance
benefit.

**In-ride carbohydrate** — Jeukendrup; recent reviews (Sports Med 2025) ·
evidence: reviews of small studies · status: contested above 90 g/h ·
`domain: cho_dosing`. Up to about 60 g/h from a single source; 60-90 g/h with
multiple transportable carbohydrates; 90 g/h is the default ceiling. Higher
doses raise gut-symptom risk; gut training over about 2 weeks reduces it.
`energy.py` returns a band.

**Energy availability and REDs** — Mountjoy et al., IOC consensus (BJSM 2023) ·
evidence: consensus · status: settled · `domain: red_s`. No single diagnostic
test; the IOC REDs CAT2 tool is for clinicians. The skill screens for warning
signs and refers. Energy availability below 30 kcal/kg FFM is a clinical flag.

## Tapering

**Taper** — Bosquet et al. (MSSE 2007, 27 studies); Wang et al. (PLoS One 2023,
14 studies); Mujika · evidence: meta-analysis · status: settled ·
`domain: tapering`. About 2 weeks (21 days or less; 8-14 days had the best
estimate); volume cut 41-60%, preferably progressively; intensity and session
frequency kept. A pre-taper overload may add benefit. Mixed sports, not
cyclists alone.

## Illness, detraining and return

**Graded return after respiratory illness** — IOC consensus (BJSM 2023) ·
evidence: consensus · status: `unverified` detail · `domain: illness_return`.
Grade severity by symptoms; a graded exercise challenge with the response
watched for 24 hours; return to participation and return to full load as
separate milestones. The "neck check" is expert opinion only.

**Detraining** — Coyle (classic studies); recent review (Sports Med) ·
evidence: observational, mostly male · status: `unverified` ·
`domain: illness_return`. VO2max falls measurably within about two weeks of
stopping. Breaks of 4 weeks or less count as short-term.

## Environment

**Heat acclimatisation** — Racinais et al. (consensus 2015); Périard ·
evidence: consensus · status: `unverified` detail · `domain: heat_protocols`.
The most important intervention for performance in the heat: repeated
exercise-heat exposure over about 1-2 weeks. Start hydrated; cooling strategies
help. Adaptations decay within weeks, so it is a maintenance commitment.

**Altitude / live-high train-low** — Levine, Stray-Gundersen · evidence: RCTs
in trained athletes · status: unverified for amateurs · `domain: altitude`.
Iron status gates the response.

## Psychology and adherence

**Psychobiological model** — Marcora · status: unverified ·
`domain: psychological_skills`. Perceived effort as the proximal limiter.

**Implementation intentions** — Gollwitzer · status: unverified ·
`domain: psychological_skills`. If-then plans as an adherence mechanism; the
Execution check's main lever.

---

## Declared, not yet sourced

A check reaching for one of these abstains at Level 1 until a source is
retrieved in-session. Fail loudly rather than improvise coaching prose.

- **Sleep duration and extension** · `domain: sleep`
- **Recovery modality interference** (cold water immersion after strength) ·
  `domain: recovery_modalities`
- **Psychological skills training** and **stress and coping** ·
  `domain: psychological_skills`
- **Inspiratory muscle training** · `domain: respiratory_training`
- **Stretching and mobility** (position tolerance, not performance) ·
  `domain: mobility`
- **Legal ergogenic aids** (caffeine, nitrate, bicarbonate, creatine) ·
  `domain: ergogenic_aids`
- **Skills and racecraft** (practitioner tier, capped at Level 2) ·
  `domain: skills_expertise`
- **Responder variance** for heat and altitude · `domain: altitude`
- **Body composition trajectory** against the energy-availability floor ·
  `domain: red_s`

---

## Rules for using this file

1. A lens name is not a citation. Retrieve the primary source before asserting
   an effect size, and record it in the evidence ledger.
2. A `contested` lens is presented with both sides, every time.
3. Do not attribute a position to a named person beyond what this file records
   as theirs. Never write what someone "would say".
4. Lenses are conceptual anchors with long half-lives. **Effect sizes are not.**
   The staleness windows in `frameworks.yaml` apply to the numbers.
5. Teach through the lenses: when a recommendation rests on a lens, name it,
   its evidence level and its status in the five-part explanation.
