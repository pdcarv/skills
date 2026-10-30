---
name: working-backwards-prfaq
description: >-
  Drafts and reviews an Amazon-style Working Backwards PR/FAQ: a customer-focused press
  release under one page plus an FAQ of at most five pages that includes a candid
  assessment of cost and difficulty, then prepares the silent-reading review meeting.
  Use when asked to pitch, propose, justify or evaluate a new product, feature, service
  or initiative before building it, to "work backwards from the customer", to write a
  PR/FAQ or launch press release for a product idea, or to stress-test
  whether an idea is meaningfully better than what exists. Not for technical designs.
license: MIT
metadata:
  category: "software-architecture/design-and-decisions"
  sources: "see Sources section"
---

# Working Backwards PR/FAQ

Start from the customer experience and work backward to what should be built. The artefact is a short press release (PR) written as if the product had launched, plus an FAQ that answers the hard questions, including how difficult and expensive it will be. It is reviewed in a meeting that opens with silent reading. Most PR/FAQs are not approved, and that is the point: it is cheap to kill an idea on paper.

## When to use

- A new product, feature or internal platform is being proposed and the "who is it for and why will they care" question is not settled.
- Someone wants to pitch or evaluate an idea before committing engineers.
- An existing PR/FAQ needs a critique before a review meeting.

## When not to use

- The product decision is made and the question is how to build it: `design-doc`.
- One technical choice needs recording: `architecture-decision-record`.
- A status update or general narrative memo (the Amazon six-page narrative format was not verified in this library's sources; do not imitate it from memory).

## Inputs to gather

- The target customer (external user, developer, internal team) and their current way of solving the problem.
- Evidence of the problem: support tickets, user research, usage data, quotes the user is allowed to share.
- What exists today, from competitors or in-house, so the "so what?" test has something to compare against.
- Known constraints and rough cost: teams, dependencies, timeline, technical risk.
- Who will review it, and whether the team runs a reading meeting.

## Procedure

1. **Name the customer and the problem** in plain language before writing anything else. If you cannot, stop and ask; the PR cannot be written without them.
2. **Draft the press release.** A few paragraphs, always under one page, written from the customer's point of view and about the customer experience, not the technology. It should make clear who the customer is, what problem they have, what the new experience is, and why it is better than what they do today. Avoid internal jargon, architecture and roadmap detail. (This content list is this library's paraphrase of "focused on the customer experience"; the source excerpt gives no section template.)
3. **Apply the "so what?" test.** For every benefit claimed, ask whether it is meaningfully better than what exists. Write down the comparison. Cut or rewrite claims that fail. If nothing survives, say so: that is a valid result.
4. **Draft the FAQ (at most 5 pages).** Cover:
   - customer-experience details the PR left out: who exactly, how they get it, what happens in edge cases, what it costs them;
   - a candid assessment of how hard and how expensive it will be to build: dependencies, unknowns, the riskiest assumption, rough team size and time;
   - the strongest objections a sceptical reviewer would raise, each with an honest answer, including "we don't know yet".
5. **Check lengths.** PR under one page; FAQ within 5 pages. Brevity is deliberate: the limit forces distilled thinking rather than showing all the work. Cut before adding appendices.
6. **Iterate.** Expect many drafts (the source reports teams often writing 10 or more and meeting senior leaders 5 or more times). Keep a short changelog so reviewers see what moved.
7. **Prepare the review meeting.** Produce the pre-read and a facilitation note:
   - one hour, opening with silent reading of the document;
   - general feedback next, with the most senior people speaking last;
   - then line-by-line discussion;
   - close with minutes and a list of revisions.
   When acting as the reviewer's assistant, collect line-by-line comments before writing any summary, so the summary reflects the comments rather than anchoring them.
8. **Record the outcome.** Approved, revise, or not approved. Treat "not approved" as a success of the process, not a failure. If approved, keep the PR/FAQ as a living document and hand off to `design-doc`.

## Verification

- The PR fits on one page and never mentions internal systems, architecture or team structure.
- The customer and the problem are named in the first paragraph of the PR.
- Every claimed benefit has a written "so what?" comparison against an existing option.
- The FAQ is at most 5 pages and contains an explicit cost and difficulty section with the riskiest assumption named.
- Hard questions have honest answers; none is answered with marketing language.
- The meeting note follows the reading-meeting order (silent read, general feedback with seniors last, line by line, minutes).

## Gotchas

- **Technology-first PRs.** A press release that describes the architecture is a design doc in disguise. Rewrite from the customer's side or stop.
- **Soft FAQ.** An FAQ that only answers friendly questions fails the purpose. The candid cost and difficulty assessment is required, not optional.
- **Approval as the goal.** The process is built so that most PR/FAQs are not approved. Do not tune the document to get a yes; tune it to make the decision clear.
- **Copying templates.** Do not reproduce the book's or any company's template text. Paraphrase the structure for the user's context.
- **Unverified details.** Internal vs external FAQ splits, bar raisers, single-threaded leaders and the six-page narrative format are not covered by this library's sources. Do not present them as part of the method.
- **Over-length as thoroughness.** Exceeding the limits signals undistilled thinking, not rigour.

## Output

```markdown
# PR/FAQ: <working product name>
Draft <n> - <date> - Authors: ...

## Press release (under one page)
<a few paragraphs, customer's point of view>

## "So what?" check (working notes; remove before the meeting if the team prefers)
| Claimed benefit | Today's alternative | Meaningfully better? | Evidence (source, or "assumption") |

## FAQ (at most 5 pages)
### Customer questions
**Q:** ... **A:** ...
### Cost and difficulty (candid assessment)
- Riskiest assumption: ... (evidence so far: ..., or none)
- Each estimate marked measured, sourced or assumed
- Dependencies and unknowns: ...
- Rough team and time: ...
### Hard questions
**Q:** ... **A:** ...

## Review meeting plan
- 60 min: silent read -> general feedback (most senior last) -> line by line -> minutes and revisions
- Decision recorded: approved | revise | not approved
## Changelog
```

## Sources

- Colin Bryar and Bill Carr, *Working Backwards* (2021), book excerpt "An insider look at Amazon's culture and processes" on About Amazon (PR length, FAQ length, so-what test, meeting mechanics, draft counts, most not approved, living document), read Oct 2026: https://www.aboutamazon.com/md/news/workplace/an-insider-look-at-amazons-culture-and-processes
