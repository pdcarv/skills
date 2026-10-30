# Check 2: Tolerance

The second of three checks applied, in order, to every proposal. It asks: does
this keep the risk of injury, illness, low energy availability and
non-functional overreaching acceptable? It is not the "say no" check: a plan
that produces no adaptation has failed too.

## Objective

Minimise the probability of injury, illness, low energy availability or
non-functional overreaching across the block, subject to the plan still being a
training plan.

## Evidence to look for

Adverse events, dropout rates, injury and illness incidence, contraindications,
energy availability, overreaching markers, and how fast adaptations decay when a
stimulus stops.

## Frames

Energy availability, concurrent-training interference, load and monitoring,
illness and return to training, heat and altitude. See
`references/frameworks.md`.

## Hard floors (not tradeable)

These outrank any performance gain. A proposal that breaches one is removed.

- **Cardiac or systemic warning signs** get a medical referral, not a training
  change.
- **Low energy availability warning signs** get a referral; energy availability
  below 30 kcal/kg FFM (from `scripts/energy.py`) is a clinical flag, not a
  training variable.
- **An active injury or illness** in `screening.yaml` or `conditions.yaml` is a
  constraint on the plan until it is cleared or closed.
- **Return to full load after illness** only through the steps in
  `references/adapt.md`.

## Checklist

- Quantify risk the way Adaptation quantifies gain: incidence, population,
  timeframe. "This is risky" is not a position.
- Separate the reversible from the irreversible. A blunted block costs weeks;
  a tendon can cost a season. Argue proportionally.
- Name the monitoring signal that would detect harm early (`references/review.md`)
  and the observation that would stop the plan.
- Distinguish acute cost from chronic cost. Some sessions are meant to feel bad.

## Biases to correct for

You will over-weight rare harms, because case reports are memorable and
adaptation is invisible.

- **Under-training has failure modes too:** detraining, lost durability, an
  unready athlete on race day. Name them when you argue for less.
- **"Contested as a predictor" cuts both ways.** ACWR and monotony are weak
  evidence for restricting training as well as for permitting it.
- **Removing more than half of the plan candidates** usually means you are
  applying preferences, not floors.

## Output

```
TOLERANCE
  Verdict:          PASS | PASS WITH MONITORING | REMOVE (name the floor)
  Risk mechanism:   <how the harm would occur>
  Magnitude:        <incidence or effect + population + ledger ids + confidence>
  Reversibility:    <weeks / months / permanent>
  Monitoring signal:<what detects it early, and how often>
  Abort criterion:  <the observation that stops the plan>
```
