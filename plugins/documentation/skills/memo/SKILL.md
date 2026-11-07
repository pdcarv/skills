---
name: memo
description: >-
  Writes or reviews written communication meant to replace slides and meetings: an
  Amazon-style narrative memo (purpose with scope, background readable cold, a few
  initiatives each with plan, expected outcome, derivation and tracking, then risks and
  dependencies, with detail in appendices and every claim tied to data), a short
  plain-text weekly status update built from the week's evidence ("snippets", as a
  former Googler describes them), or an async message checked before sending. Includes a revision loop
  (draft, colleague review, time away, re-edit) and a silent-read meeting plan. Use when
  asked for a 6-pager, narrative, planning or annual plan doc, business memo, pre-read,
  weekly update, status report, snippets, or to tighten a long message before posting.
license: MIT
metadata:
  category: "documentation/writing"
  sources: "see Sources section"
---

# Memo

Narrative writing forces the author to connect claims into an argument, which slides let you skip. This skill produces three shapes of the same discipline: a narrative memo read silently at the start of a meeting, a short weekly status update, and an async message that can stand on its own. The memo structure comes from an AWS-published planning-narrative guide; the meeting and revision practices come from Bezos's 2017 shareholder letter (read through press coverage, so secondary) and Amazon's own description of its PR/FAQ meetings. The snippet practice is documented only by a former Googler, not by Google.

**Side effects:** writes drafts, and appends confirmed weekly updates to a log at a location the user names. Reads the code host, ticket tracker and docs, plus sent mail and calendar only if the user grants access. Never sends, posts or comments; the user does.

## When to use

- A planning narrative, annual or quarterly plan, "6-pager", business memo or meeting pre-read.
- A weekly status update, "snippets" or a running log of what you did.
- A long message, request or announcement that should work without a meeting.

## When not to use

- A technical design with trade-offs: use `design-doc` (documentation).
- Recording one decision: use `adr` (documentation).
- Incident status updates during an outage: out of scope; they follow the incident's own cadence and channel.
- A self-review or promotion record: use `brag`.

## Inputs to gather

- Mode: memo, weekly update, or async message.
- Audience and the decision or action wanted from them.
- For a memo: the data behind each claim (metrics, dashboards, customer evidence, costs), the planning period, known risks and dependencies, any team template.
- For a weekly update: the week's merged and authored PRs and commits, closed tickets, docs written, sent mail and calendar, if the user grants access.
- For an async message: the thread or issue it belongs to and what the reader already knows.

## Procedure

### A. Narrative memo

1. **Fix the purpose first.** One paragraph: why the memo exists, what the reader should decide or know, and what is in and out of scope. If you cannot state the decision wanted, stop and ask.
2. **Write the background for a cold reader.** Someone with no prior context must understand it. Define terms and give the current numbers.
3. **Write a few initiatives.** For each: the goal; a step-by-step plan; the expected outcome; how that outcome was derived (the model or data behind the number); how progress will be tracked. The AWS guide asks for a few goals, not a long list.
4. **Write risks and dependencies.** For each: what could go wrong or who you need, likelihood or evidence, and the mitigation or ask.
5. **Move detail to appendices.** The AWS guide caps the body at six pages plus reasonable appendices and says not to game margins or fonts. Use the team's own limit if it has one. Amazon describes length limits as forcing distilled thinking, so cutting is part of the work, not formatting.
6. **Tie every claim to data.** Scan the draft for speculation and soft words ("should", "we believe", "likely", "significant") and either attach the internal or external data point or delete the claim. Evidence: a claim-to-source table (Output, A).
7. **Run the revision loop.** Bezos describes great memos as written and rewritten, shared with colleagues, set aside for a couple of days, then edited again, often taking a week or more. You can play the colleague: re-read as a sceptical reader and list the questions a reader would write in the margin, then fix the draft. You cannot replace the time away; tell the user to schedule it before the final edit.
8. **Plan the meeting if there is one.** The AWS guide's planning meeting: print the memo, read silently (15 minutes in its example), go around the room for comments, then iterate or execute, and revisit the document during the year. Amazon's PR/FAQ meetings also open with silent reading and have the most senior people speak last. Prepare a comment-collection template rather than a summary, so the meeting reacts to the document.

### B. Weekly status update (snippets)

1. **Gather the week's evidence before writing.** Code check-ins, merged and reviewed PRs, closed tickets, docs, sent mail and calendar if the user grants access. The former Googler reviews check-ins, sent email and the calendar to recall forgotten work, including by-products such as docs and tests; PRs, tickets and docs extend the same idea.
2. **List accomplishments.** One line each, linked to its evidence. Add blockers and next week's focus only if the team wants them.
3. **Write it as short plain text.** Snippets were a free-form text field mailed as a digest; the author argues rigid formats add useless bookkeeping.
4. **Have the user confirm** every line; the user sends it. The agent sees artifacts, not outcomes.
5. **Append to a running log** once the user has confirmed, at a location the user names (for example `snippets.md` with dated entries). The same log feeds `brag` later.

### C. Async message check

Before posting a long message, request or announcement, apply GitLab's pre-send check:
1. Is the format right for the channel and reader?
2. Does the reader have the context needed, without a meeting?
3. Is it clear and kind?
4. Does it include next steps or resources?
5. Is it documented somewhere findable later (the issue, PR or doc), not only in chat?

Recommend moving to a synchronous call when there have been several back-and-forths on one matter, the topic is time-sensitive, or people are talking past each other. After any call, draft the outcome for the user to post in the related issue or doc.

## Verification

- Memo: purpose names the decision and the scope; background reads cold; each initiative has plan, expected outcome, derivation and tracking; risks and dependencies exist.
- Memo: body within the agreed length; detail sits in appendices.
- Memo: headings state findings or outcomes, so a reader skimming only the headings gets the argument.
- Memo: every factual claim appears in the claim-to-source table; no unsupported "should".
- Memo: the user has the revision schedule (colleague review, time away, re-edit).
- Weekly update: every line links to evidence and the user confirmed it.
- Async message: all five checks pass, or the message recommends a sync with the trigger named.

## Gotchas

- **Unverified "6-pager rules".** "No bullets", a mandatory tenets section at the top, an FAQ appendix and specific font or margin rules circulate widely but were not found in any Amazon primary source. Do not present them as Amazon rules; use them only if the user's team has adopted them. Amazon's careers site does say tenets are part of its culture, so offer a tenets section as optional.
- **Bezos quotes are secondary.** The letter was read through press coverage (CNBC, Banking Exchange), not the primary text. Attribute accordingly.
- **The memo has no single author.** Bezos's letter says the memo is from the whole team; draft without a byline if the team follows that.
- **Fluent but wrong.** LLM drafts sound reasonable while being inaccurate, and a weak early section makes later sections weak (Larson's experience co-writing strategy with an LLM). The human edits each section down to what they can vouch for and checks every external claim.
- **Data-free initiatives.** An expected outcome without its derivation is a guess. Readers will ask how the number was made; answer it in the memo or appendix.
- **Background that argues.** The background must be readable cold and factual (the AWS guide wants facts, not speculation). Make the case in the initiatives.
- **Status updates from memory.** Memory-based updates miss by-products and over-weight the last two days. Gather evidence first (B1).
- **Chat is not a record.** Stripe (secondary source) treats Slack as non-durable and moves important information into findable documents; GitLab records outcomes in the related issue, which it prefers over shared docs for searchability. Put the final version where it can be found.
- **Snippets are not a Google-documented practice.** Present the format as one former Googler's account.

## Output

A. Memo:

```markdown
# <Title>
<Team, date. No author byline if the team writes as a team.>

## Purpose
<Why this memo, the decision wanted, in scope, out of scope.>
## Background
<Context a cold reader needs, with current numbers.>
## Initiatives
### 1. <Goal stated as the outcome, e.g. "Cut checkout p99 to 300 ms by Q3">
Plan: <steps>. Expected outcome: <number/result>. Derived from: <data, model>.
Tracking: <metric, cadence, owner>.
## Risks and dependencies
| Risk or dependency | Evidence | Mitigation or ask |
## Appendices
A. <Data tables, method, detail moved out of the body>

<!-- Not part of the memo -->
Claim-to-source table: | Claim | Source (data, date) |
Revision plan: colleague review by <date>; set aside until <date>; final edit <date>.
Meeting: silent read <N> min; comment template attached; revisit on <date>.
```

B. Weekly update (plain text):

```text
Week of <date>
- <Accomplishment> (<link>)
- <By-product: doc, tests, review> (<link>)
Blocked on: <item, owner>          (optional)
Next week: <focus>                 (optional)
```

C. Async check result:

```markdown
Format: ok | change to <...>   Context: ok | add <...>   Clear and kind: ok | <edit>
Next steps/resources: ok | add <...>   Findable: ok | post in <issue/doc>
Recommend sync: no | yes, because <trigger>
```

## Sources

- Richard Howard, "Startup advice: how to write a narrative", AWS Startups Blog, 25 Sep 2019 (purpose, background, initiatives, risks and dependencies; six pages plus appendices; facts not speculation; 15-minute read and go-round; revisit during the year): https://aws.amazon.com/blogs/startups/startup-advice-how-to-write-a-narrative
- CNBC, "What Jeff Bezos learned from requiring 6-page memos at Amazon", 23 Apr 2018 (2017 shareholder letter via press: no PowerPoint, silent reading, memo quality varies widely): https://www.cnbc.com/2018/04/23/what-jeff-bezos-learned-from-requiring-6-page-memos-at-amazon.html
- Banking Exchange, "Handstands and six-page memos from Amazon", undated (same letter, secondary: a week or more, rewrite, share, set aside, no author name): https://www.bankingexchange.com/management-topics/duties/item/7527-handstands-ans-six-page-memos-from-amazon
- About Amazon, "An insider look at Amazon's culture and processes" (excerpt from Bryar and Carr's *Working Backwards*, 2021; length limits force distilled thinking; PR/FAQ meetings open with silent reading, senior people speak last), read Oct 2026: https://www.aboutamazon.com/md/news/workplace/an-insider-look-at-amazons-culture-and-processes
- Amazon Jobs, Principal Engineering Community tenets (tenets as part of Amazon culture), read Oct 2026: https://www.amazon.jobs/content/en/teams/principal-engineering/tenets
- mtlynch.io (a former Googler), status updates post, 25 Jun 2019, updated 2025 (snippets as a former Googler describes them; evidence-based weekly procedure): https://mtlynch.io/status-updates-to-nobody
- GitLab Handbook, "Asynchronous communication", modified 24 Jun 2026 (pre-send checklist, sync triggers, record outcomes in the issue): https://handbook.gitlab.com/handbook/company/culture/all-remote/asynchronous/
- Gergely Orosz, Pragmatic Engineer, Stripe writing culture, 23 Jan 2024, partly paywalled, secondary (durable documents over Slack): https://newsletter.pragmaticengineer.com/i/140970283/writing-culture
- Will Larson, "Co-writing strategy with an LLM", lethain.com, 15 Mar 2025 (human vouches for each section; fluent-but-wrong output; compounding errors): https://lethain.com/ces-ai-cowriting-with-an-llm/
