# Method
How claims are sourced, how confidence is computed, what is checked before
emission, and how to say "unknown". These are the rules that make the domain
material in `frameworks.md` and `protocols.md` usable without drifting into
confident invention.

## Contents

- Provenance and the evidence ledger
- Working files (outside state)
- Deterministic confidence calibration
- Evidence levels in the five-part explanation
- The verification gate
- Research decomposition, budgets and stop rules
- Abstention
- Persona fidelity

---

## Provenance and the evidence ledger

Every atomic claim in any output carries exactly one provenance type. All other
protocols key off this field.

## Provenance types

| Type | Meaning | May carry a citation? | Max confidence (P3) |
|---|---|---|---|
| `RETRIEVED` | Traceable to an artifact fetched this session | Yes — URL + retrieval date required | Level 5 |
| `COMPUTED` | Output of a deterministic script | No — carries run ID instead | Level 5 |
| `STATED` | Asserted by the user this session | No | Level 3 |
| `STORED` | Read from state files; inherits its own original provenance | Inherited | Inherited |
| `RECALLED` | From model weights, unverified | **No — never** | Level 2 |

### The root rule

> A claim either has a retrieved artifact behind it, or it is prose reasoning.
> `RECALLED` content may never carry an (Author, Year) citation, a DOI, a
> journal name, an effect size, a sample size, or a p-value.

Writing `(Rønnestad et al., 2015, Scand J Med Sci Sports)` without having fetched
that paper this session manufactures an authority signal. This is the single most
damaging failure mode in the system, and the rule exists so it becomes
*mechanically detectable* rather than a matter of the agent's judgement.

`RECALLED` is permitted — it is how ordinary reasoning happens. It renders with an
explicit inline marker and is capped at Level 2 confidence.

### STATED is not MEASURED

A user saying "my FTP is 280" produces a `STATED` profile value with
`method: unknown`. It becomes `MEASURED` only when a test result with a stated
protocol exists. Anything derived from a `STATED` value inherits the weaker
provenance. A common error starts here (a 20-minute power carried forward as
FTP), so it is enforced, not advised.

## Ledger schema

One YAML file per investigation, written while researching, read by the three
checks and by the verification gate. It is a working file, not athlete state
(see Working files).

```yaml
- id: L-0142
  claim: "Heavy strength training improves cycling efficiency in trained cyclists."
  provenance: RETRIEVED
  source:
    url: https://pmc.ncbi.nlm.nih.gov/articles/PMC12881108/
    retrieved: 2026-08-28
    title: "Heavy strength training effects on physiological determinants..."
    doi: 10.1007/s00421-025-05883-2
  anchor: "significant effect on cycling efficiency"   # <15 words, for re-verification
  design: {type: meta-analysis, n: 262, studies: 17, certainty: low}
  effect: {metric: cycling_efficiency, es: 0.353, ci: null, p: 0.012}
  population: {level: trained, vo2max_mean: 61.25, mass_mean: 72.28, sex: mixed}
  domain: strength_for_cycling      # keys into frameworks.md volatility table
  published: 2025-07-09
  replication: single               # single | replicated | contested
  transfer:
    verdict: partial                # yes | partial | no
    reason: "cohort mean mass 72 kg vs this athlete's; ES may not scale linearly"
  contested_by: []                  # ids of contradicting rows -> triggers P5
```

### Field notes

**`anchor`** is a short verbatim span (under 15 words) that lets a later session
or the user re-verify the claim against the source without re-reading it. It is
the only place verbatim source text is permitted. One anchor per source, ever.

**`transfer`** closes the elite-to-amateur error class. The agent must state the
population delta rather than let it pass silently. `verdict: no` means the row
may inform reasoning but may not support a prescription.

**`replication: contested`** requires the topic to be in the contested register
of `frameworks.md` (contested science) or in `state/contradictions.yaml`
(a conflict in this athlete's data), and sets `do_not_assert` behaviour.

**`domain`** must be a key in `frameworks.md`; it determines the staleness
threshold applied in the RECENCY check (P4).

## Working files (outside state)

The evidence ledger, the compute manifest, drafts and the verify-keys file are
working files for one procedure run. Keep them in a working folder outside
`state/` (for example `/tmp/cycling-<slug>/`), never in the athlete's state:
the state rule in SKILL.md allows only the files in `references/state.md`.

## Compute manifest

`COMPUTED` claims reference `manifest.json`, written by every script run:

```json
{
  "runs": [
    {"id": "R-01", "script": "power_duration.py", "inputs_hash": "…",
     "timestamp": "2026-08-28T14:02:11Z",
     "outputs": {"cp_w": 250.0, "w_prime_j": 36000, "subset_sd_w": 8.4}}
  ]
}
```

Every number that appears in an output must be locatable in either a ledger row
or a manifest run. The verifier enforces this; there is no honour system.

## Escape hatch

Numbers that are genuinely neither retrieved nor computed — a session count, a
week index, an illustrative round figure — are declared inline and audited:

```markdown
<!-- allow: 12 reason=week index, structural not empirical -->
```

Every allow-comment appears in the verifier report. If a draft needs many of them,
that is itself the finding.

---

## Deterministic confidence calibration

Confidence is computed from evidence properties, never asserted from fluency.
This replaces all three prior taxonomies (High/Medium/Low, Level 1–5 as a free
choice, and ± bands) with one rubric evaluated by the verifier.

```
score = design_weight × population_match × replication × recency_factor

design_weight     meta-analysis / systematic review 1.00
                  RCT 0.85 · crossover 0.80 · cohort 0.60
                  consensus 0.50 · practitioner 0.30 · n-of-1 0.15 · unknown 0.20

population_match  transfer.verdict yes 1.00 · partial 0.70 · no 0.40

replication       replicated 1.00 · single 0.60 · contested 0.35

recency_factor    within volatility window (or recency_checked today) 1.00
                  stale 0.50

  ≥0.80 → Level 5      0.60–0.79 → Level 4      0.40–0.59 → Level 3
  0.20–0.39 → Level 2  <0.20 → Level 1

Then cap by provenance: RECALLED ≤ 2 · STATED ≤ 3 · others ≤ 5.
```

## Language bound to each level

| Level | Permitted phrasing |
|---|---|
| 5 | "This will…" / "The evidence clearly shows…" |
| 4 | "This is very likely to…" / "Strong evidence supports…" |
| 3 | "This is likely to…" / "Available evidence suggests…" |
| 2 | "This may…" / "Preliminary evidence hints…" |
| 1 | "It is unclear whether…" / "No reliable data exists for…" |

## Consequences worth stating plainly

- A large, well-conducted meta-analysis in the wrong population **cannot** reach
  Level 5. Design quality does not launder a transfer problem.
- A `RECALLED` claim is structurally capped at Level 2 no matter how confident
  the model is. This is the point.
- A single n=20 cohort that transfers perfectly scores 0.60 × 1.00 × 0.60 = 0.36
  → Level 2. That reads as harsh until you remember it is one small study.
- A contested claim drops replication to 0.35, which usually costs a full
  level. Disagreement in the literature is supposed to cost confidence.

## Evidence levels in the five-part explanation

The EVIDENCE line of every recommendation (SKILL.md) names the design using the
same order as `design_weight`: meta-analysis or systematic review > RCT >
crossover > cohort or observational > consensus > practitioner or expert
opinion > n-of-1 > convention. "Convention" marks rules adopted for
practicality (compliance bands, the 5% decoupling benchmark, the HRV band),
which carry no validation and say so.

---

## The verification gate

Two layers. The mechanical layer runs first because it is free, deterministic,
and catches the failure classes a model cannot reliably self-police.

## Layer 1 — mechanical audit (`scripts/verify_output.py`)

Non-optional for any output containing a numeric prescription, a threshold, a
dose, or a citation. Exploratory conversation is exempt.

```bash
W=/tmp/cycling-<slug>          # working folder, outside state/
python3 scripts/verify_output.py \
  --draft $W/draft.md --ledger $W/ledger.yaml \
  --manifest $W/manifest.json --profile $W/verify-keys.yaml \
  --frameworks frameworks.yaml --session-date $(date +%F)
```

`verify-keys.yaml` is built for the run from the current anchors (the test
results `plan.yaml` points to), so the gate can catch a draft that contradicts
them:

```yaml
verify_keys:
  anchors.lt1:
    aliases: ["LT1"]
    value: 225
    unit: " W"
```

Exit 1 blocks emission. The agent revises and re-runs; it does not argue with
the gate. If the agent believes the gate is wrong, the correct move is to fix the
ledger (add the missing row) or the draft (remove the unsupported claim) — never
to bypass the check.

| Check | Blocks on |
|---|---|
| `NUMERIC` | a number with no ledger row, manifest run, profile value, or allow-comment |
| `CITATION` | an (Author, Year) with no RETRIEVED row + URL; a RECALLED row carrying source/effect data |
| `CONFIDENCE` | an asserted level that differs from the P3 rubric; a bare "Confidence Level N" with no ledger anchor |
| `RECENCY` | a high-volatility row past its staleness window without `recency_checked` |
| `QUOTE` | any span ≥15 words; more than one anchor per source |
| `UNITS` | a quantity outside its physiological plausibility band |
| `PROFILE` | a value contradicting a current anchor in verify-keys with no supersede block |

### Annotation syntax the draft must use

```markdown
[[L-0142 L3]]                                  confidence anchored to a ledger row
<!-- allow: 24 reason=structural session count, not empirical -->
<!-- supersede: thresholds.lt2_indoor reason=new step test 2026-01-15 -->
```

## Layer 2 — chain-of-verification

Mechanical checks catch fabrication. They do not catch being wrong. So:

```
1. draft
2. derive 3–7 verification questions from the draft's load-bearing claims
3. answer each INDEPENDENTLY, from sources only, WITH THE DRAFT WITHHELD
4. diff answers against draft
5. revise / demote confidence / mark contested
```

**Step 3's independence is the entire mechanism.** A verifier that reads the
draft first will rationalise it rather than test it. In practice this means a
separate subagent (ideally a different model) that receives the questions and
the ledger but not the prose. This is the one place a second agent earns its
cost: multi-agent debate on one model often does no better than a single
agent, while an independent check or a different model does help.

A load-bearing claim is one where being wrong changes the recommendation. Do not
generate verification questions for scaffolding.

## What the gate deliberately does not do

It does not check whether the reasoning is good, whether the recommendation is
wise, or whether the right question was asked. It checks that every assertion is
attached to something real. Those are different problems and conflating them
produces false confidence in the gate.

---

## Research decomposition, budgets and stop rules

## Why decomposition is the diversity mechanism

Three checks run by the same model, on the same context, produce correlated
output. Persona labels do not decorrelate them; they only make the correlation
harder to see. Diversity has to come from **different evidence**, which means
different queries, one partition per check.

```
Adaptation  → effect sizes, mechanisms, dose–response curves, ceiling effects,
              time-to-effect, what the intervention actually changes
Tolerance   → adverse events, dropout rates, injury incidence, contraindications,
              RED-S / energy availability, overreaching markers, decay kinetics
Execution   → adherence and compliance data, dose-transferability from elite to
              amateur cohorts, real-world implementation studies, time cost
```

Each check searches its own partition and records its rows with the check's
name, so the ledger shows which evidence supported which check.

## Budget

| Depth | Searches | Ledger rows expected | CoVe |
|---|---|---|---|
| Quick | 0–2 | 0–3 | skipped unless numeric |
| Standard | 3–8 | 4–12 | 3 questions |
| Deep | 8–20 | 12–40 | 5–7 questions |

## Stop rules

```
SATURATION   stop when two consecutive searches return no new ledger rows
COVERAGE     before EMIT, every load-bearing claim must map to ≥1 ledger row
             unmet → search again, or ABSTAIN on that sub-claim (P8)
ESCALATION   budget exhausted with coverage unmet → emit the partial answer plus
             an explicit gap list

NEVER        fill a coverage gap with RECALLED content
```

The last line is the one that matters. Running out of budget is a normal outcome
and produces an honest partial answer. Silently substituting recalled content
produces a complete-looking answer that is wrong in an undetectable way.

## Query construction

- Search for the **primary study**, not the summary. If a review is the only
  retrievable artifact, record `design: systematic-review` honestly rather than
  citing the primary paper it describes as though it were fetched.
- Include the population qualifier in the query ("trained cyclists", "amateur")
  so the transfer verdict can be filled from the abstract rather than guessed.
- For any `volatility: high` domain, one query must be recency-bounded
  (current year and the one before) regardless of what else is searched.

---

## Abstention

A system with no way to say "unknown" will hallucinate under pressure. Abstention
therefore has a defined shape rather than being an absence.

```
UNRESOLVED: <the specific question, stated precisely>
  What would settle it:  <experiment, measurement, or source>
  Best available proxy:  <claim + confidence level, or "none">
  Cost of proceeding:    <what breaks if we act without it>
```

Abstaining on a sub-claim is not abstaining on the answer. Emit everything that
is supported and abstain narrowly.

## When abstention is mandatory

- Coverage unmet after the search budget is exhausted (P7).
- A claim is contested (`frameworks.md` register or `state/contradictions.yaml`)
  — present both positions instead.
- A prescription would depend on a `STATED` value that has never been measured,
  and the prescription is sensitive to that value across its plausible range.
- A `transfer.verdict: no` row is the only support for a recommendation.

## The STATED / MEASURED boundary

> "My FTP is 280" enters the profile as `STATED`, `method: unknown`.
> It becomes `MEASURED` only when a test result with a stated protocol exists.

Anything derived from a `STATED` value inherits the weaker provenance, and the
verifier caps its confidence at Level 3. This exists because a common numeric
error — a 20-minute power carried forward as FTP through an entire set of
derived targets — begins as an unmarked user assertion promoted to a
measurement by nothing more than repetition.

## Sensitivity test before asking

Symmetrically: before *requesting* a missing field, check whether the answer
changes across its plausible range. If the recommendation is identical at the
10th and 90th percentile of the unknown, state the assumption inline and
proceed. Ask only for fields whose absence would flip the answer.

---

## Persona fidelity

## The problem with emulation

Asking a model to speak as a named researcher raises hallucination probability.
It licenses the generation of *X-shaped sentences*, and "shaped like X" is
precisely the failure mode. The persona must operate as a **retrieval
constraint**, not a generation licence.

## The rule

```
A named-researcher voice may assert ONLY:
  (a) positions traceable to a RETRIEVED artifact authored by that person, or
  (b) direct application of a framework listed in frameworks.yaml,
      carrying its primary citation.

Everything else is emitted by the ROLE, not the person:

  YES  "The Adaptation check, reasoning from the six-zone metabolic framework…"
  NO   "San Millán would say…"

Speculation about what a researcher "would say" is prohibited outright.
Where their published position is genuinely unknown on the question, the
correct output is: "<name> has not published on this."
```

## What this preserves

The value of a researcher panel was never the impersonation. It was that
Seiler's polarized hierarchy and Bakken's lactate-controlled double-threshold
genuinely disagree, and that the disagreement is informative. That survives
intact: the lenses are listed in `frameworks.md`, the checks invoke them by
name, and live disagreements sit in its contested register rather than being
resolved by whichever voice sounded more confident.

The evidence points the same way. Expert personas in prompts did not reliably
improve factual accuracy (162 roles, 2,410 questions; Zheng et al., EMNLP
Findings 2024) and lowered accuracy on knowledge benchmarks in later preprints,
with longer biographical personas doing more damage.

## What it removes

- Invented positions attributed to real people.
- Rhetorical authority substituting for evidence ("Bakken would tell you…").
- The illusion of six independent experts where there is one model.

## Voice register

Checks speak in ordinary technical prose. They do not perform. A light coaching
tone toward the rider is fine; the tone is not the mechanism for being right.
