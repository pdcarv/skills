# Check 1: Adaptation

The first of three checks applied, in order, to every proposal. It asks one
question: is this the largest expected gain at the target event for the time it
costs? It is an objective, not a voice.

## Objective

Maximise expected performance gain at the A-event, given the athlete's current
state and the time remaining. Where two options have similar expected gain,
prefer the one with the shorter time-to-effect and the larger evidence base.

## Evidence to look for

Effect sizes, mechanisms, dose-response, ceiling effects, time-to-effect, and
what an intervention actually changes. Adverse events belong to Tolerance and
adherence to Execution; keeping the searches separate is what makes the three
checks look at different evidence rather than restating one retrieval.

## Frames

Metabolic and threshold, distribution and periodisation, durability, strength,
fuelling, tapering. See `references/frameworks.md`. A frame name is not a
citation.

## Checklist

- Quantify or abstain. "This improves performance" is not a position; an effect
  size with a population and a confidence level is.
- Name the mechanism. An effect with no mechanism is a correlation not yet
  interrogated.
- Separate a ceiling from an execution gap before prescribing. Most perceived
  limits in an athlete with a few years of structured training are the latter.
- State what the proposal costs in training time and what it displaces.

## Biases to correct for

You will over-value intensity and novelty, because both are heavily published.

- **Volume and economy are under-published relative to their effect.** Early in
  a structured training career, aerobic economy usually has more headroom than
  VO2max, and economy is volume-driven.
- **Fresh threshold is a proxy, not the target.** For a long event the decisive
  quality is power late, measured fatigued (durability).
- **A professional protocol is a hypothesis about amateurs, not a finding.**

## Output

```
ADAPTATION
  Claim:            <the recommendation, one sentence>
  Mechanism:        <why it works>
  Expected effect:  <magnitude + population + ledger ids + confidence level>
  Displaces:        <what it replaces or crowds out>
  Fails when:       <two specific conditions>
  Falsifiable test: <what the athlete would observe in 4-8 weeks>
  Abort criterion:  <the observation that reverts it>
```

Every number must exist in a ledger row or a manifest run before you write it.
If it does not, run the script or abstain.

When comparing plan candidates, score one thing: the expected change in the
plan's success criterion. Where two candidates differ by less than the
uncertainty of the model separating them, they are tied; say so.
