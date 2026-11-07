---
name: adr
description: >-
  Records an architecture or technical decision as a Nygard-style ADR (title with ID,
  context, decision, status, consequences), after first classifying it as a one-way door
  (consequential, effectively irreversible) or a two-way door (reversible) and scaling
  the process to match. Use when asked to write, record, log, supersede or deprecate an
  ADR or architecture decision, to document why a technology, pattern or vendor was
  chosen, or to decide how much review a decision needs ("is this a one-way door?",
  "how much process does this need?"). Also flags two-way-door decisions being run
  through a heavyweight process.
license: MIT
metadata:
  category: "documentation/design-and-decisions"
  sources: "see Sources section"
---

# ADR

Capture one decision in a short, append-only record so future readers know what was decided, why, and with what consequences. Before writing, classify the decision by reversibility: reversible decisions should be made fast by a small group and recorded lightly; irreversible ones deserve a slow, deliberate process with wide consultation. The ADR format follows Michael Nygard's 2011 proposal (via a secondary summary; see Sources).

**Side effects:** Writes one new ADR file in the repo at a path and number the user confirms, and edits a superseded ADR's status only on approval. No external reads beyond the repo; never merges, commits or changes an ADR's status to accepted.

## When to use

- A technology, pattern, vendor, data store, protocol or boundary has been chosen (or is about to be) and the reasoning should outlive the people in the room.
- A previous decision is being reversed or replaced.
- Someone asks how much process a decision deserves.

## When not to use

- Several interlocking decisions and a whole system need designing: `design-doc` (ADRs can then record individual decisions as they are made).
- Trivial, local choices that a code comment or PR description covers.

## Inputs to gather

- The decision in one sentence, and the options considered.
- The forces: technical, political, social and project constraints, including ones that conflict.
- The cost and time to reverse the decision if it proves wrong (data migrations, contracts, public APIs, team skills).
- Existing ADRs in the repo: look for an ADR folder and its numbering and file-name convention, and any ADR this one supersedes or relates to.
- Who decides and who must be consulted.

## Procedure

1. **Classify the door.** Ask: if this is wrong, can we undo it, and at what cost?
   - **Two-way door (Type 2, reversible):** decide quickly; an individual or small group with good judgment decides. Record a lightweight ADR (one page or less).
   - **One-way door (Type 1, consequential and effectively irreversible):** slow, deliberate decision with wide consultation. Pair the ADR with a full design doc and review meeting (`design-doc`).
   Record the classification and the reversal cost you estimated. Evidence: the concrete things that would have to change to reverse it.
2. **Check for process mismatch.** If a two-way-door decision is stuck in a heavy, Type 1 style process, say so: at scale that mismatch causes slowness, unthinking risk aversion and too little experimentation. Optionally note the heuristic Farnam Street attributes to Bezos of deciding with about 70% of the information you wish you had (the letter it comes from is unverified).
3. **Number and title it.** Next free ID in the repo's sequence plus a short noun phrase, for example "ADR 9: LDAP for multitenant integration". Follow the repo's existing file-naming convention if one exists.
4. **Write Context** as the forces at play, stated neutrally. Include the conflicting ones; an ADR whose context has no tension usually hides the real reason.
5. **Write Decision** in active voice: "We will ...". One decision per ADR.
6. **Set Status:** proposed or accepted; later deprecated or superseded. When superseding, add a link both ways (new ADR "supersedes ADR n"; old ADR status "superseded by ADR m"). Propose the old ADR's status change and write it once the user approves.
7. **Write Consequences:** all of them, positive, negative and neutral. Include what becomes easier, what becomes harder, what new work it creates, and the conditions under which the decision should be revisited.
8. **Add the door tag and a review-by date.** This library adds two fields to Nygard's five: the Type 1/Type 2 tag from step 1, and a revisit date (the design-doc source suggests looking back after 1-2 years to judge how decisions held up).
9. **Propose, do not merge.** Confirm the path and number with the user, then write the file and present it for the decider's acceptance; changing Status to accepted is their call.

## Verification

- The door classification names a concrete reversal cost, not just "hard" or "easy".
- Process weight matches the door: a Type 2 ADR is short; a Type 1 decision links to a design doc and lists who was consulted.
- Context lists forces, including at least one that argues against the decision.
- Decision is one active-voice statement.
- Consequences include at least one negative or neutral item.
- Any superseded ADR is updated with a back-link; no accepted ADR's Decision text was rewritten.

## Gotchas

- **Editing history.** Accepted ADRs are an append-only log. Change direction by writing a new ADR and marking the old one superseded; do not rewrite the old decision.
- **Consequences that are all upside** signal advocacy, not a record. Readers trust ADRs that admit costs.
- **Bundling.** Several decisions in one ADR cannot be superseded independently. Split them.
- **Overweight process for reversible choices** is the common failure at scale, not the rare one. Default to light unless reversal is genuinely expensive.
- **Hidden one-way doors.** Public API shapes, data formats written to durable storage, vendor contracts and tenant partitioning keys are often treated as reversible and are not. Check them explicitly in step 1.
- **Source status.** Nygard's original post was not read; the section list comes from the arc42 FAQ summary. The Bezos material comes via Farnam Street's quotation of the 2015 letter.

## Output

```markdown
# ADR <n>: <short noun-phrase title>

- Status: proposed | accepted | deprecated | superseded by ADR <m>
- Date: <yyyy-mm-dd>   Deciders: ...   Consulted: ...
- Door: Type 1 (one-way) | Type 2 (two-way) - reversal cost: <concrete>
- Revisit by: <date>
- Supersedes / related: ADR <k>

## Context
<forces at play, including conflicting ones>

## Decision
We will ...

## Consequences
- Positive: ...
- Negative: ...
- Neutral: ...
- Revisit if: ...
```

## Sources

- arc42 FAQ C-9-3 (summary of Michael Nygard, "Documenting Architecture Decisions", Nov 2011: title with ID, context, decision, status, consequences; superseded links), read Oct 2026: https://faq.arc42.org/questions/C-9-3/
- Farnam Street, "Reversible and Irreversible Decisions" (Bezos 2015 shareholder letter on Type 1 and Type 2 decisions; 70% heuristic, attribution unverified), read Oct 2026: https://fs.blog/reversible-irreversible-decisions/
- Malte Ubl, "Design Docs at Google", 6 July 2020 (revisit decisions after 1-2 years): https://www.industrialempathy.com/posts/design-docs-at-google/
