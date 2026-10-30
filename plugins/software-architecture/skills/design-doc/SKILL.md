---
name: design-doc
description: >-
  Writes or reviews a Google-style software design doc: context and scope, goals and
  non-goals, the actual design (system-context diagram, API sketch, data storage
  trade-offs), alternatives considered, and cross-cutting concerns (security, privacy,
  observability). Decides first whether a doc is worth writing at all, and whether a 1-3
  page mini design doc or a full 10-20 page doc fits. Use when asked to write, draft,
  outline, critique or review a design doc, technical design, system design proposal,
  RFC or architecture proposal, or when a change has real trade-offs and no written
  design yet. Review mode returns line-level findings against the same structure.
license: MIT
metadata:
  category: "software-architecture/design-and-decisions"
  sources: "see Sources section"
---

# Design doc

Produce (or review) an informal document, written by the main authors before coding starts, that records the high-level strategy and the key decisions, with the emphasis on the trade-offs considered. The structure follows Malte Ubl's public description of design docs at Google. The format is deliberately flexible: the sections below are the default, not a form to fill in. The doc's value is catching design problems while changes are still cheap.

## When to use

- A new system, service or significant change where several approaches are plausible and the choice has trade-offs.
- Someone asks for a design doc, technical design, RFC or "write up the architecture" before implementation.
- Someone shares a draft design and asks for a review or critique.

## When not to use

- The solution is clear and has few trade-offs, or the doc would only be an implementation manual. Say so and suggest code, a short PR description, or an ADR (`architecture-decision-record`).
- The problem is well understood and a fast prototype would settle the question sooner. Suggest the prototype.
- The open question is whether to build the product at all, or for whom: use `working-backwards-prfaq` first.
- One decision needs recording, not a whole design: `architecture-decision-record`.

## Inputs to gather

- The problem in one or two sentences, and who asked for the work.
- Existing systems the design touches: repos, service names, current diagrams, earlier design docs and ADRs.
- Constraints: deadlines, budgets, compliance or privacy requirements, platforms that are fixed.
- How reversible the main decisions are (one-way vs two-way door; see `architecture-decision-record`).
- Co-authors and intended reviewers, and how review happens in this team (comment threads or a design review meeting).
- For review mode: the draft itself and what kind of feedback is wanted.

## Procedure

### Write mode

1. **Decide whether to write it.** If the solution is obvious with few trade-offs, stop and propose the lighter artefact. Record the reason in your reply. Evidence: the list of options you considered and why they do or do not differ materially.
2. **Pick the size.** Default to a 1-3 page mini design doc for incremental work. Use a full doc (about 10-20 pages) for larger projects. If the work would need more than that, split it into smaller problems, each with its own doc. A practical heuristic (an inference in the source notes, not Google policy): reversible decisions get a mini doc; one-way-door decisions get a full doc plus a review meeting.
3. **Context and scope.** Write objective background: what exists, what is changing in the world around it, and the boundary of this design. Do not turn it into a requirements list.
4. **Goals and non-goals.** Goals as short bullets. Non-goals are things that could reasonably have been goals but are deliberately excluded; each one should be something a reader might otherwise assume is in scope.
5. **The actual design.** Start with an overview, then detail. Include what helps the reader judge trade-offs:
   - a system-context diagram showing the new system among its neighbours;
   - an API sketch (shape and key operations), not pasted interface definitions;
   - data storage, focused on trade-offs (access patterns, consistency, growth), not full schemas;
   - code or pseudo-code only for novel algorithms;
   - how constrained the solution space is (fixed platform vs open choice), because it changes how much the alternatives matter.
6. **Alternatives considered.** The source calls this one of the most important sections. For each serious alternative, state what it is, what it would do better, and why the chosen design wins on the trade-offs that matter here. Include "do nothing" when it is a real option.
7. **Cross-cutting concerns.** Cover security, privacy and observability at minimum. Google requires a separate privacy design doc and review; if the user's organisation has a privacy or security review, name it and link it rather than inventing one. Useful additions from this plugin: a resilience note (timeouts, retries, AZ-loss headroom; see `timeout-retry-overload-review` and `blast-radius-review`).
8. **Check length and fit.** Count pages against the size chosen in step 2. If a section is mostly detail an implementer needs but a reviewer does not, cut it or move it to an appendix.
9. **Set up the lifecycle.** Add a status line and a revision log. Plan review (comment threads or a design review meeting), state that the doc will be updated in place when the design changes during implementation, and put a revisit date 1-2 years out to judge how the decisions held up.
10. **Write the summary last and label the evidence.** Every number in the design (latency, cost, capacity, scale) carries its source or measurement, or is marked as an estimate. A claim that is neither moves to Open questions.

### Review mode

1. Read the whole draft once before commenting.
2. Check each section in the Verification list below and record a finding for each miss, citing the line or heading.
3. Check whether the doc should exist at all (Write step 1) and whether its size fits (Write step 2).
4. Separate blocking findings (missing alternatives, a design that does not meet a stated goal, an unaddressed cross-cutting concern) from optional polish; prefix polish with "Nit:".
5. Hand back findings in the Output format; do not rewrite the doc unless asked.

## Verification

- Context and scope reads as background, not as a list of requirements.
- Every non-goal is something a reasonable reader might have assumed was a goal.
- The design section starts with an overview; there is a system-context diagram or a stated reason it is not needed.
- APIs are sketched, not pasted; storage is discussed as trade-offs, not full schemas.
- Alternatives considered has at least one real alternative with the reason it lost; none is a strawman.
- Security, privacy and observability are each addressed or explicitly marked not applicable with a reason.
- Length matches the chosen size (mini about 1-3 pages, full about 10-20); oversized work is split.
- Status, authors, reviewers and a revisit date are present.
- The Summary alone tells a reviewer what is proposed, the main trade-off, and what is still open.
- Every number is sourced, measured or marked as an estimate.

## Gotchas

- **The doc that should not exist.** A doc that only restates an obvious implementation costs reviewer time and adds nothing. Saying "skip the doc" is a valid outcome of this skill.
- **Requirements creep into context.** Context that lists "the system shall..." items hides the background reviewers need to judge trade-offs.
- **Non-goals that are just negated goals** ("must not lose data") add nothing. Non-goals earn their place by ruling out plausible scope.
- **Alternatives written after the fact** tend to be strawmen. Write them while the decision is still open and give each its strongest case.
- **Amendments fragment the record.** When implementation changes the design, edit the doc in place and log the change instead of appending addenda.
- **Pasted interfaces and schemas** bury the decisions. Keep them in code; keep the doc on trade-offs.
- **Source status.** The structure comes from a long-time Google engineer's public post, not an official Google page. Do not present it as Google policy, and do not claim internal Google templates.

## Output

Write mode returns the doc in this shape (drop or merge sections when the mini size calls for it):

```markdown
# <Design title>
Status: draft | in review | approved | implemented | superseded   Authors: ...   Reviewers: ...
Last updated: <date>   Revisit by: <date 1-2 years out>

## Summary
<3-5 sentences, written last: the problem, the proposed design, the main trade-off,
and what is decided vs still open. A reviewer who reads only this knows what is asked.>

## Context and scope
## Goals
## Non-goals
## Design
### Overview
### System context (diagram)
### APIs (sketch)
### Data storage (trade-offs)
### Degree of constraint
## Alternatives considered
| Alternative | Better at | Why not chosen |
## Cross-cutting concerns
- Security: ...   - Privacy: ... (link separate privacy review if your org requires one)
- Observability: ...   - Resilience: ...
## Open questions
## Revision log
```

Review mode returns:

```markdown
## Design doc review: <title>
Verdict: ready for review meeting | needs another draft | should not be a design doc (use <artefact>)
### Blocking
- [<section/line>] <finding> -> <suggested fix>
### Nits
- Nit: [<section/line>] ...
### Missing sections
- ...
```

## Sources

- Malte Ubl, "Design Docs at Google", Industrial Empathy, 6 July 2020 (sections, length guidance, mini design docs, when not to write one, lifecycle and revisit advice): https://www.industrialempathy.com/posts/design-docs-at-google/
- Farnam Street, "Reversible and Irreversible Decisions" (quoting Bezos's 2015 shareholder letter on Type 1 and Type 2 decisions), read Oct 2026: https://fs.blog/reversible-irreversible-decisions/
- Google eng-practices, "The Standard of Code Review" ("Nit:" convention for optional comments), read Oct 2026: https://google.github.io/eng-practices/review/reviewer/standard.md
