---
name: code-review-standard
description: >-
  Reviews a code change against the Google Engineering Practices review standard (approve once the
  change definitely improves overall code health; facts over style guide over engineering
  principles over consistency; "Nit:" for optional comments; an escalation ladder), adds a
  fresh-context reviewer scoped to correctness and stated requirements, and verifies every
  finding before it is reported because LLM reviewers over-reject correct code. Also covers
  receiving review: check each comment against the code, propose fixes for what holds, push back
  with evidence on what does not. Produces a report and drafts; never posts, approves, edits
  or commits. Use when asked to review a PR, CL, diff or branch, before
  merging agent-written code, or when review comments arrive on your own change.
license: MIT
metadata:
  category: "programming/quality"
  sources: "see Sources section"
---

# Code review standard

A review has one job: decide whether this change leaves the codebase healthier, and say exactly what must change if it does not. Google's standard gives the decision rule and the order of authority for settling disagreements. Agent practice adds two things: an independent reviewer that never saw the author's reasoning, and a verification gate on findings, because reviewers prompted to find problems find some whether or not they exist.

The skill is read-only toward the pull request and the user's working tree. It never posts comments, submits an approval or change request, edits files, commits or pushes. Running the project's tests, linters, type checks and build is expected; any change needed to run a check (such as trying a proposed fix) happens in a throwaway worktree or copy. It hands back a report and drafts; the human decides what to post, approve or apply.

## When to use

- Reviewing a pull request, CL, diff or branch, yours or someone else's, human- or agent-written.
- A final check before merging agent-written work.
- Review comments arrived on your change and you must respond (see Procedure, part B).

## When not to use

- No code yet, only a design: use `design-doc` (software-architecture).
- The question is how to ship safely, not whether the code is right: use `safe-rollout`.
- A bug investigation: use `systematic-debugging` (debugging-performance).

## Inputs to gather

- The diff, and the base branch it applies to. For uncommitted work, the working tree: `git diff`, `git diff --staged` and untracked files.
- The stated requirements: issue, SPEC.md, PR description. Review against these, not against what you would have built.
- The project's style guide, linters and agent rules (`CLAUDE.md` or `AGENTS.md`); those rules are review criteria too.
- Test results and the author's evidence (test output, screenshots). Run the tests yourself if you can.
- Size: files and lines changed, and whether unrelated concerns are mixed.

## Procedure

### A. Reviewing a change

1. **Check size and scope first.** If the change mixes unrelated concerns or is too large to read carefully, ask for it to be split before line-by-line review. Small changes are easier to review and cheaper to roll back (SRE Workbook; Willison's PR conventions; DORA lists small batches among its AI capabilities). Google's small-CL guidance: about 100 lines is usually reasonable and about 1000 usually too large, file spread counts too (200 lines across 50 files is usually too large), and a reviewer may reject a change for size alone.
2. **Check intent.** Does the change do what the requirements say, and only that? A well-built feature nobody asked for can still be rejected.
3. **Check evidence.** Read the PR description critically (agents write plausible ones) and run or inspect the tests. Missing evidence of the author's own verification is itself a finding.
4. **Read with depth proportional to risk.** Read load-bearing code (protocols, runtime, data handling, business logic) line by line; skim peripheral code such as styling. For each area, check correctness, tests that assert behaviour, and, before production, the AWS-style checklist items: monitoring coverage, resource impact, alarm behaviour and rollback safety. For a mutating API endpoint, check idempotency: client key, stored first response, error on key reuse with different parameters, concurrent requests. Only once the correctness findings are settled, make a simplification pass: code that duplicates something already in the repository (reuse it), needless indirection, dead code, speculative generality, and changes outside the requirements (flag them for removal). Simplification findings are Nits unless they hide a defect.
5. **Run an independent reviewer in a fresh context.** Give it only the diff and the requirements, read-only tools plus the project's test and lint commands, and this scope: report gaps that affect correctness or the stated requirements; skip style. It must not see the authoring conversation, so it judges the code, not the author's reasoning. Optional, tool-specific: Claude Code `/code-review` without `--comment` or `--fix`, or a subagent with `tools: Read, Grep, Glob, Bash` limited to the test and lint commands; Cursor Agent Review or Bugbot; or a second session or a different model.
6. **Verify every finding before reporting it** (yours and the reviewer's). Reproduce it: write or run a test that fails, trace the input that triggers it, or point to the exact line and value. Run the project's tests, linters and type checks as needed. Where a fix is proposed, apply it in a throwaway worktree or copy (`git worktree add`), run the tests there, then remove it. Drop findings you cannot substantiate, or downgrade them to questions.
7. **Label each comment.**
   - Blocking: must change before approval, with its justification.
   - `Nit:` optional polish or education; never blocks.
   - Question: you need information, not a change.
8. **Justify blocking comments by Google's order of authority:** (1) technical facts and data; (2) the style guide, which is absolute on style (outside it, follow existing style, else accept the author's choice); (3) engineering principles, not taste (if the author shows options are equally valid, accept theirs); (4) consistency with the codebase, unless that worsens code health. A preference with none of these behind it is a Nit at most.
9. **Recommend a verdict.** Recommend approval when the change definitely improves overall code health, even if it is not perfect. Do not recommend approving a change that worsens code health except in an emergency. Do not hold a change for days over small imperfections. Hand back the report and wait: the user decides what gets posted, approved or applied. If a finding reflects a rule worth keeping, suggest `compound-learnings` (personal-productivity).
10. **Resolve disagreement on the ladder:** seek consensus using these rules; then a call or meeting, with the outcome recorded as a comment on the change; then escalate to the team, tech lead, code owner or manager. Never let a change stall because author and reviewer disagree.

### B. Receiving review

1. **List every comment** with its location, including bot and AI-reviewer comments.
2. **Verify each before acting.** Read the referenced code, reproduce the claimed problem (run the test, trace the case), and check it against the requirements. Do not agree performatively and do not apply a fix you have not confirmed is needed.
3. **Classify:** accept; push back; or ask for clarification.
4. **Push back with evidence,** using the same order of authority: test output, data, the style-guide rule, the spec line, or a demonstration that the alternatives are equally valid. Be specific and short.
5. **Propose a change for each accepted comment:** a focused patch, with a test where behaviour changes, confirmed in a throwaway worktree with the full suite run there. Hand the patches to the user to apply.
6. **Do not over-apply.** Fixing everything a reviewer flags, especially AI reviewers, adds needless abstraction, defensive code and tests for impossible cases. Fix what you verified.
7. **Draft a reply for each thread:** the proposed change or why not (evidence), for the user to post. Suggest recording the outcome of any call on the change itself.

## Verification

- Every blocking comment cites a fact, rule or principle and points to file:line.
- Every reported defect has a reproduction (failing test, input trace, or executed fix) or is phrased as a question.
- The fresh-context reviewer's output was triaged, not forwarded raw; dropped findings are listed with the reason.
- The verdict states which way code health moves and why.
- Correctness findings were settled before the simplification pass; simplification findings are Nits unless they hide a defect.
- When receiving review: every comment has a drafted reply, and the suite was green in the throwaway worktree with the proposed patches applied.
- Nothing was posted, approved, edited in the user's tree, committed or pushed.

## Gotchas

- **Reviewers over-report.** Anthropic's docs warn that a reviewer asked to find gaps usually reports some even when the work is sound. In a Feb 2026 study, GPT-4o falsely rejected correct code 26.2% (HumanEval) and 35.9% (MBPP) of the time with a minimal prompt, rising to 73.2% and 87.9% with a richer judge-justify-fix prompt. More elaborate review prompts made it worse.
- **Executing the fix is the best filter found.** In the same study, running the reviewer's proposed fix against tests cut average false rejection from 54.8% to 16.3% on HumanEval. Cursor's Bugbot used multiple passes with majority voting plus a validator model for the same reason.
- **Self-preference bias is contested.** One 2026 study across 20 models found judges favour their own outputs; another found authoring models rejected verified-good fixes at about the same rate as fresh models. Neither tested code. A fresh-context reviewer is cheap insurance either way.
- **Style as a blocker.** Outside the style guide, style is preference. Blocking on it slows teams and teaches authors to ignore review.
- **Perfection as the bar.** The standard is "better", not "perfect". Remaining improvements go in Nits or follow-up issues.
- **Trusting the description.** Agent-written PR descriptions can claim tests or behaviour that do not exist. Check claims against the diff and the test run.
- **Review capacity is the real limit.** Agent output can exceed what humans can review; Armin Ronacher notes slop PRs take a minute to make and an hour to review. Ask for smaller changes rather than skimming.
- **Rubber-stamping AI review.** Vendor figures such as reviewer bug-catch rates are self-reported without published method. Humans remain accountable for what merges; some projects (e.g. Ghostty) require the human to understand all submitted code.

## Output

Review report:

```markdown
## Review: <change title>
Recommended verdict: approve | approve with nits | request changes
Code health: improves | neutral | worsens, because <one line>
Scope/size: <ok | split into: ...>
Evidence checked: <tests run, output>

### Blocking
1. <file:line> <problem>. Justification: <fact | style guide rule | principle | consistency>. Repro: <test/trace>. Suggested fix: <...>

### Nits (style and simplification)
- Nit: <file:line> <suggestion>

### Questions
- <file:line> <question>

### Fresh-context reviewer findings dropped
- <finding> - dropped: <not reproducible | out of scope | style>
```

Receiving-review response:

```markdown
| # | Comment (file:line) | Verified? (how) | Decision | Proposed change / evidence | Draft reply |
|---|---|---|---|---|---|
| 1 | ... | reproduced with test X | accept | patch below; suite green in worktree | ... |
| 2 | ... | could not reproduce: <output> | push back | <evidence> | ... |
```

Follow the table with one patch per accepted comment, for the user to apply.

## Sources

- Google Engineering Practices, "Small CLs" (size heuristic, file spread, rejection for size), repo HEAD 2024-09-18: https://google.github.io/eng-practices/review/developer/small-cls.html
- Google Engineering Practices, "The Standard of Code Review" (code-health rule, order of authority, Nit:, conflict ladder), read Oct 2026: https://google.github.io/eng-practices/review/reviewer/standard.md
- Anthropic, Claude Code best practices (fresh-context reviewer; review against the spec, report gaps not style; reviewers always find something; over-applying findings), current docs read Oct 2026: https://code.claude.com/docs/en/best-practices
- Jin & Chen, LLM-as-reviewer overcorrection, arXiv 2603.00539, 28 Feb 2026: https://arxiv.org/pdf/2603.00539
- Cursor, "Building a better Bugbot" (multi-pass voting, validator), Jon Kaplan, 15 Jan 2026: https://cursor.com/blog/building-bugbot
- Yang et al., self-preference in LLM judges, arXiv 2604.22891 (Apr 2026, v4 Jun 2026): https://arxiv.org/abs/2604.22891
- Guey & Bougault, revision resistance, arXiv 2606.20093, Jun 2026: https://arxiv.org/abs/2606.20093
- Jesse Vincent, obra/superpowers `receiving-code-review` (verify feedback, no performative agreement), read Oct 2026: https://claudeskills.info/skills/obra/superpowers/
- Simon Willison, "Anti-patterns" (small PRs, read the agent's PR description, include evidence of your review), ~4 Mar 2026: https://simonwillison.net/guides/agentic-engineering-patterns/anti-patterns/
- Thorsten Ball, "How I Prompt" (review depth by how load-bearing the code is), 29 Jul 2026: https://thorstenball.com/talks/how-i-prompt/
- Armin Ronacher, "Agent Psychosis", 18 Jan 2026: https://lucumr.pocoo.org/2026/1/18/agent-psychosis/ and "The Final Bottleneck", 13 Feb 2026: https://lucumr.pocoo.org/2026/2/13/the-final-bottleneck/
- AWS Builders' Library, "Automating safe, hands-off deployments" (code review gate and checklist), German locale page, first published Jun 2020: https://aws.amazon.com/de/builders-library/automating-safe-hands-off-deployments/
- Stripe API reference, idempotent requests, read Oct 2026: https://docs.stripe.com/api/idempotent_requests.md
- Google SRE Workbook, "Canarying Releases" (small deployments are cheaper to roll back): https://sre.google/workbook/canarying-releases/
- DORA 2025 State of AI-assisted Software Development (small batches), via InfoQ, 29 Sep 2025: https://www.infoq.com/news/2025/09/dora-state-of-ai-in-dev-2025
- Ghostty AI_POLICY.md, read Oct 2026: https://github.com/ghostty-org/ghostty/blob/main/AI_POLICY.md
