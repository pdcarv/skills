---
name: brag
description: >-
  Builds or updates a brag document, a running record of the user's work and its impact,
  using Julia Evans's sections (goals, projects with contribution and impact,
  collaboration and mentorship, design and documentation, company building, learning,
  outside work, and "fuzzy work" as goal, actions and effects) and her two-step
  brag workshop: gather the period's work from evidence, then critique each item for
  unstated impact. The agent collects evidence from merged PRs, reviews, design docs,
  tickets, incidents and status logs the user names; the user verifies every item and
  supplies the numbers. Use when asked to update a brag doc, prepare for a performance
  review, self-review, promotion or calibration, list accomplishments for a manager, or
  catch up on what was done this half or year.
license: MIT
metadata:
  category: "documentation/career"
  sources: "see Sources section"
---

# Brag

A brag document keeps an accurate, evidence-linked list of work and what it changed. Julia Evans's version has fixed sections and a two-step workshop: first gather everything, then go through it with someone who asks "and what happened because of that?". An agent is good at the gathering (it can read PR history and docs quickly) and at the critique, but it cannot know impact, invisible work or confidential context. The user verifies every line.

**Side effects:** writes the brag doc and its shareable copy at a location the user chooses. Reads the code host, ticket tracker and doc folders the user names and grants access to. Never shares, sends, posts or commits it.

## When to use

- Periodic update of a brag doc (every couple of weeks, or one session every 6-12 months).
- Preparing a self-review, performance review, promotion case or a briefing for a new manager.
- Turning a log of weekly status updates into a half-year or year summary.

## When not to use

- Writing this week's status update: use `memo` (weekly update mode); its log feeds this skill.
- A company-specific promotion packet with a mandated template: follow that template. No public big-tech promo-packet format was found for this library, so do not invent one; this skill can supply the evidence underneath it.

## Inputs to gather

- The period to cover and the existing brag doc, if any.
- Where the evidence lives, as named by the user: code host and username, repos, ticket tracker, design-doc folders, incident reports, the snippets or status log. Use only sources the user names and grants access to.
- This year's goals and next year's (from the user, OKRs or the last review).
- Who will read it (manager, peer reviewers, promotion committee) and anything that must not appear (confidential projects, customer names).

## Procedure

1. **Set up the document.** If none exists, ask the user where to create it (outside any shared repo by default, since it holds personal data), then create it with the sections in Output. If one exists, read it and note the last period covered.
2. **Gather evidence for the period (workshop step 1).** Evans's workshop spends 1-2 hours reviewing the last six months of PRs, tickets and design docs; the agent does the mechanical part:
   - merged PRs authored, and significant reviews given, from the repos the user named;
   - design docs, RFCs and runbooks written or substantially reviewed;
   - closed tickets and epics;
   - incidents where the user was responder, commander or postmortem author;
   - the weekly snippets log, if one exists.
   Evidence: a raw list, one line per item, each with a link and date.
3. **Cluster into projects.** Group related PRs and docs into the projects they served. A project entry is the unit a reader cares about; individual PRs are evidence beneath it.
4. **Sort into sections.** Projects; collaboration and mentorship; design and documentation; company building (recruiting, interviewing, processes); what you learned; outside work; fuzzy work. For fuzzy work (glue work, unblocking, cleanup with no single artefact), write the goal, the actions taken and their effects.
5. **Ask for what the agent cannot see.** Mentoring, interviews, hallway unblocking, cross-team influence and outside work rarely leave an artifact. Ask the user directly, section by section.
6. **Critique each item for unstated impact (workshop step 2).** The workshop pairs for about an hour with a partner who flags items like "I shipped $feature" that never say what changed. For each project, mark what is missing: the user's specific contribution, the impact (with a number where one exists), and what happened after launch. Write these as questions, not guesses.
7. **Get answers and verification from the user.** Every line is confirmed, corrected or removed by the user. Numbers come from the user or a source they point to; never estimate impact.
8. **Write it accurately.** Evans's guidance is that you do not have to make the work sound better than it is. Plain statements of contribution and effect, no inflation.
9. **Produce the shareable version.** A copy for the manager or reviewers with confidential items removed or generalised, and the goals section at the top.

## Verification

- Every item links to evidence or is marked "user-reported" (for work with no artifact).
- Every project states the user's contribution, the impact or "impact not yet known", and what happened after launch.
- No number appears that the user did not supply or confirm.
- Each fuzzy-work entry has goal, actions and effects.
- The user has confirmed every line; nothing from an unconfirmed source remains.
- The shareable version contains nothing the user marked as private.

## Gotchas

- **PR count is not impact.** A list of 40 merged PRs tells a reviewer nothing. Cluster into projects (step 3) and state what changed for users, the team or the business.
- **The agent cannot see invisible work.** Mentoring, interviewing, incident support and process work often leave no PR. If you only mine the code host, the doc under-reports exactly that work, which is why Evans gives it its own sections. Ask (step 5).
- **Inflation.** Evans says the document does not need to make work sound better than it is; it needs to be accurate. Agents drift toward promotional wording; strip it.
- **Invented numbers.** An agent asked for "impact" will produce plausible percentages. Ask questions instead and leave gaps visible until the user fills them.
- **Credit for team work.** Co-authored and reviewed work needs the user's specific part stated ("designed the schema", "reviewed and caught X"), not the team's whole outcome.
- **Waiting until review season.** Evans prefers one long session every 6-12 months; others update every couple of weeks. Either way, an evidence log kept weekly (snippets) makes the session fast.
- **Access scope.** Only read sources the user names. Do not pull private channels or other people's documents to find praise.

## Output

```markdown
# Brag document: <name>, <period>
Last updated: <date>

## Goals
- This year: <goal> | Next year: <goal>

## Projects
### <Project>
- Contribution: <what the user specifically did>
- Impact: <what changed, with number and source> | impact not yet known
- After launch: <adoption, follow-ups, incidents avoided>
- Evidence: <PR/doc/ticket links>

## Collaboration and mentorship
- <who, what, effect> (user-reported | link)

## Design and documentation
- <doc, decision it drove> (link)

## Company building
- <recruiting, interviews, processes>

## What I learned
- <skill or domain, how it was used>

## Outside work
- <talks, open source, writing>

## Fuzzy work
- Goal: <...> Actions: <...> Effects: <...>

<!-- Working notes, not shared -->
Open questions for the user: <project: missing contribution/impact/after-launch>
Items removed for the shareable version: <list>
```

## Sources

- Julia Evans, brag documents post, jvns.ca, 28 Jun 2019 (sections, fuzzy work, cadence, sharing with manager, accuracy, two-step brag workshop): https://jvns.ca/blog/brag-documents/
- mtlynch.io (a former Googler), weekly snippets as an evidence-based status log, 25 Jun 2019, updated 2025: https://mtlynch.io/status-updates-to-nobody
