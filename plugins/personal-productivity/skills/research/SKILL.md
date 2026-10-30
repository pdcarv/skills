---
name: research
description: >-
  Investigates a question and leaves a short, durable research note: verdict first, findings
  with dated sources, options ruled out with reasons, and open unknowns. Frames the question
  and the decision it feeds, scales effort to the question (inline for small ones, parallel
  research subagents with fixed briefs for broad ones), keeps cited findings, inferences and
  gaps apart, verifies load-bearing claims independently, and saves the note to
  docs/research/ in a repository or the user's notes folder otherwise. Use when asked to
  research, investigate, compare or evaluate a library, approach, product, service or
  question whose answer will be reused, for codebase archaeology, or before a decision that
  needs evidence.
license: MIT
metadata:
  category: "personal-productivity/knowledge"
  sources: "see Sources section"
---

# Research

Turn a question into a note that a later planning session, decision or reader can use without redoing the work. The note answers the question; it is not a diary of the search. Broad questions are split across parallel research subagents that each write their findings to a file, while the coordinating agent only plans, briefs and distils, which keeps its context clean (the orchestrator-worker pattern Anthropic describes for its own research system).

## When to use

- A library, tool, approach, product or service needs comparing before a choice.
- A question about the codebase or a system needs archaeology across many files or history.
- A decision (an ADR, a spec, a purchase) needs evidence first.
- The answer will be needed again by another session, person or decision.

## When not to use

- The answer only matters for one small task: answer it inline and move on.
- The decision itself is the question: research first, then record the decision with `architecture-decision-record` (software-architecture).
- A design with real trade-offs needs writing up: feed this note into `design-doc` (software-architecture).

## Inputs to gather

- The question in one sentence, and the decision it feeds. Ask once if either is unclear; ask nothing whose answer would not change the research.
- Constraints to carry into every search: time window, region, version, population, budget.
- Earlier notes on the same topic in `docs/research/` or the notes folder. Build on them; never overwrite them.
- For codebase questions: the relevant source files, read for real, with `file:line` for every claim.
- Where the note should live. Inside a repository: `docs/research/`. Otherwise: the user's notes folder (ask once). Never read a folder the user marks private.

## Procedure

1. **Frame it.** State the question, the decision it feeds and the constraints in two or three lines and confirm. If the answer would only serve one small task, say so and answer inline.
2. **Scale the effort to the question.** Record the choice:
   - Quick (one fact, one source type): research it yourself, about 3-10 tool calls.
   - Standard (a comparison, a few facets): 2-4 parallel research subagents, about 10-15 tool calls each.
   - Broad (many entities, regions or sources): one subagent per independent slice.
   Multi-agent research costs many times the tokens of a single agent, so use it only when the answer is worth it.
3. **Decompose.** Split the question into sub-questions that do not overlap and together cover it. Drop any sub-question an earlier note already answers.
4. **Brief each subagent the same way**, and launch them in parallel:
   - Objective and the key questions to answer.
   - Sources to prefer (primary: official docs, papers, source repositories, filings, changelogs).
   - Constraints from step 1, verbatim.
   - A tool-call budget and the stop rule: stop when the questions are answered or new searches add nothing.
   - The exact file to write, in a working folder outside the repository and the notes folder, and the note format in step 5. Ask for a short reply, not the findings.
5. **Collect notes in one format.** For each key question: a one-line takeaway; cited findings, each with source and date; inferences, labelled as such; gaps. A finding with no source moves to gaps. Conflicting sources are written down as a conflict, not silently resolved. "No reliable source found" is a finding.
6. **Judge the sources.** Prefer primary sources over aggregators and search-optimised pages. Treat speculative wording ("could", "may", forecasts in the future tense), unnamed sources and general qualifiers as weak. Record each source's date or version, since staleness is how notes rot.
7. **Fill gaps once.** If a gap would make the answer wrong, run one more round for that gap only. Say "one gap round, then I write" before starting it. Never start a second.
8. **Verify the load-bearing claims.** List the claims whose being wrong would change the verdict. Check each against its source independently: ideally a separate subagent, or a different model, given the claims and sources but not the draft. Mark each claim verified, refuted or `unverified`, and report how many of each.
9. **Write the note** in the Output shape. Verdict first. Findings as answers. Drop any claim without a source; five sourced claims beat twenty half-sourced ones. Put every open unknown in its own section, never inside prose.
10. **Hand over.** Give the path and a summary of three to five sentences. If the note feeds a decision, name the next skill (`architecture-decision-record`, `design-doc` or `spec-interview`). Delete the working folder once the note holds what matters.

## Verification

Before calling the note done, confirm:

- The first lines answer the question asked, and the decision it feeds is named.
- Every finding has a source with a date or version, or a `file:line` for codebase claims.
- Inferences are labelled; nothing inferred is presented as found.
- The verification count is stated: verified, refuted, `unverified`.
- Ruled-out options each carry a reason.
- Open unknowns are listed, each with how it could be found out.
- The note is a new file; no earlier note was overwritten.

## Gotchas

- **Researching what the code already says.** For codebase questions, read the source; "the code does X" (cited) and "I infer X" (labelled) are different claims.
- **Fan-out for a one-fact question.** Parallel subagents for a lookup waste tokens and time; step 2 exists to stop it.
- **Vague briefs.** Without an objective, sources and boundaries, subagents duplicate each other's searches and leave gaps between them.
- **Relaying findings through the coordinator.** Findings passed back in replies get compressed and lost; subagents write files, the coordinator reads them.
- **Silent verification limits.** A verification step that ran out of budget leaves most claims unchecked; the count in step 8 makes that visible.
- **Citing the primary through a review.** If only a review was read, cite the review and say so.
- **Search-optimised pages over primary sources.** Agents drift toward content farms unless told to prefer primary sources.
- **A process diary instead of answers.** "First I searched..." belongs nowhere in the note.
- **Working files left behind.** Notes from subagents and drafts go in a working folder, not the repository or the notes folder.

## Output

Save as `docs/research/YYYY-MM-DD-<slug>.md` in a repository, or `<notes folder>/research/YYYY-MM-DD-<slug>.md` otherwise:

```markdown
# Research: <topic>

- **Date:** YYYY-MM-DD
- **Question:** <the question, one sentence>
- **Feeds:** <the decision or task this informs>
- **Verdict:** <one-line answer>
- **Verification:** <n> verified, <n> refuted, <n> unverified
- **Builds on:** <earlier note path, or none>

## Findings

<Answers, grouped by sub-question. Each claim with its source and date, or file:line.
Inferences marked "Inference:".>

## Ruled out

- **<option or hypothesis>** — why it was rejected, with the evidence.

## Open unknowns

- <what is still not known> — how it could be found out.

## Sources

- <title>, <publisher or author>, <date or version>: <URL or path>
```

## Sources

- Anthropic Engineering, "How we built our multi-agent research system", 13 Jun 2025 (orchestrator-worker pattern; subagent briefs with objective, output format, tools and boundaries; effort scaling by query complexity; parallel subagents; subagent outputs stored outside the coordinator; source-quality heuristics against content farms; multi-agent token cost and poor fit for tightly coupled work): https://www.anthropic.com/engineering/multi-agent-research-system
- Zhang et al., multi-agent debate evaluation, arXiv 2502.08788 v3, Jun 2025 (debate on one model often no better than a single agent; heterogeneous models help), used for the independent-verification step: https://arxiv.org/abs/2502.08788v3
- Dhuliawala et al., "Chain-of-Verification Reduces Hallucination in Large Language Models", arXiv 2309.11495, Sep 2023 (verification questions answered independently of the draft), `unverified` this session: https://arxiv.org/abs/2309.11495
