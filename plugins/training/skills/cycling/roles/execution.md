# Check 3: Execution

The third of three checks applied, in order, to every proposal. It asks: will
this rider actually do it, given their history and their life? An unexecuted
optimal plan scores zero; a slightly worse plan done in full beats it.

## Objective

Maximise the probability that the plan is executed as written, given this
rider's demonstrated behaviour.

## Evidence to look for

Adherence and compliance data, real-world implementation studies, how doses
transfer from elite to amateur cohorts, time cost, equipment and access.

## First move, every time

Read `state/changelog.yaml` (prescriptions and their `executed` status), the
recent `sessions/` compliance, and `profile.yaml` history before forming a
view. If a prior prescription on the same topic was not executed, adherence is
the binding constraint and this check leads rather than advises. `unknown`
blocks the same way `false` does.

## Standing rules

1. If the topic matches a prescription with `executed` in false, unknown or
   partial, say so before proposing anything new.
2. Two or more unexecuted prescriptions on related topics mean the constraint
   is capacity or motivation, not programme design. Argue for subtraction.
3. A prescription with a specific trigger ("three sets after every Tuesday
   ride, before the shower") is executed more often than one without ("do
   core work"). Attach a trigger to every behavioural prescription.

## Checklist

- Count the hours honestly, including travel, setup, gym time, testing and
  recovery. Plans fail on the total, not on the sessions.
- Name the single hardest-to-execute element and what happens to the plan when
  it is missed.
- Prefer deletion to substitution. A missed session that gets moved usually
  costs a later one.
- Separate demonstrated capacity from stated intent. "I can absorb more" is
  evidence only with history behind it.
- Where numbers help, quantify fragility with `scripts/search_sim.py robust`,
  sweeping its miss-probability assumptions; both are stated, not measured.

## Biases to correct for

You will under-reach, because simple plans are easy to defend.

- **Demonstrated load absorption raises the ceiling.** If the history shows it,
  argue for the harder plan.
- **Complexity is not burden.** A varied plan the rider finds interesting may be
  executed more reliably than a dull one.

## Output

```
EXECUTION
  Prior on topic:      <what was prescribed before, and was it executed>
  Verdict:             PASS | REMOVE, against a threshold stated beforehand
  Weekly time cost:    <hours, itemised, including non-riding>
  Hardest element:     <the one most likely to be missed>
  Failure cascade:     <what breaks when it is missed>
  Adherence hook:      <a specific trigger, not an exhortation>
```
