---
name: red-green-tdd
description: >-
  Runs a strict test-first loop for agents: write tests that assert behaviour through the
  public interface, run them and confirm they fail for the right reason (red), stage the
  tests, implement until they pass without editing the tests (green), then refactor and run
  the full suite. Guards against the documented agent failure modes: tests that print values
  instead of asserting, tests that already pass, dropped or weakened tests, and suppressed
  errors. Use when implementing a feature or a bug fix whose cause is known (find an
  unknown cause first with systematic-debugging), when the user says "TDD", "red/green",
  "test first" or "write the tests first", when a spec has acceptance criteria to turn into
  tests, or before handing implementation to another agent or session.
license: MIT
metadata:
  category: "programming/quality"
  sources: "see Sources section"
---

# Red/green TDD

Give the implementing agent a target it cannot argue with: tests that fail now, fail for the reason the feature is missing, and pass only when the behaviour exists. The confirmed red step is what makes the green step mean something. Simon Willison's version of the risk: skip the red run and "you risk building a test that passes already." Research on SWE-bench agents (2026) adds the second risk: agent-written tests are mostly value-printing observation with few real assertions, so test count says little about correctness.

## When to use

- Implementing a feature or behaviour change with a clear expected input and output.
- Fixing a bug: the failing test is the reproduction (pair with `systematic-debugging` in debugging-performance for finding the cause).
- Turning SPEC.md acceptance criteria into executable checks, or executing a spec's slices in a fresh build session (see `spec-interview`).
- Splitting work so one agent or session writes tests and another writes the code.

## When not to use

- Exploratory spikes whose output will be thrown away; write the tests when the design settles.
- Pure UI look-and-feel with no assertable behaviour: use screenshot comparison as the check instead, and still turn any bug you find into a test.
- The project has no runnable test harness at all: first agree with the user on adding one, since that is a separate change.

## Inputs to gather

- The exact command to run the whole suite and a single test. Run the suite once before changing anything and record the pass/fail baseline, including pre-existing failures.
- Existing tests near the code: style, fixtures, helpers, where new tests belong.
- The behaviour to build, as input/output pairs or acceptance criteria. If none exist, get them from the user or from `spec-interview` first.
- The public interface the tests will call. Tests go through it, not through private helpers.
- Whether mocks are acceptable. Default to none for the unit under test; mock only true external boundaries the project already mocks.

## Procedure

1. **Baseline.** Run the full suite. Record the command, the counts, and any failures that exist before you start, so they are not later blamed on or hidden by your change.
2. **Write the tests from behaviour.** One test per behaviour or input/output pair, through the public interface. Each test must contain a relational assertion on the outcome (equals, raises, status code, state after the call). Printing a value is observation, not a test. Cover the error and edge cases named in the spec, not cases that cannot occur.
3. **Run them: confirm red.** Every new test must fail. Read each failure message and check it fails because the behaviour is missing (assertion mismatch, not-implemented error), not because of an import error, typo, wrong fixture or wrong path. A test that passes now is either testing nothing or the behaviour already exists; investigate before continuing.
4. **Stage the tests on their own.** Stage only the test files (`git add <test paths>`); never commit, since commits are the user's. Any later edit to them then shows in `git diff -- <test paths>`. State the rule to the implementer: implement without modifying these tests.
5. **Implement the minimum to go green.** Write only what the failing tests require. Run the new tests after each meaningful change. When one passes, run the full suite.
6. **Never edit a test to make it pass.** If a test looks wrong, stop and say why with evidence (spec line, user decision). Change it only after the user agrees, and record the reason in the handover. Never delete, skip, weaken an assertion, widen a tolerance, or mark a test expected-to-fail to get green.
7. **Fix root causes, not error messages.** For build, type or lint errors, fix the cause; do not suppress the warning, add a blanket ignore, or catch and discard the exception.
8. **Refactor on green.** Improve structure with the tests unchanged and the suite green after each step.
9. **Exercise it for real.** Passing tests are not proof the code works. Run the feature once the way a user would (a `python -c` call, a demo script, a dev server plus curl, a browser screenshot) and record the output. Any bug found becomes a new red test, then green.
10. **Repeat** steps 2-9 one behaviour (or a small group) at a time rather than writing the whole suite up front.
11. **If stuck,** after two failed attempts at the same failure, restart from a clean context with a sharper prompt (the failing test name, the message, what was tried) rather than a third correction in the same session.

Optional enforcement, tool-specific: in Claude Code, a `Stop` hook that runs the test command and exits 2 on failure keeps the agent working until green (default cap 8 consecutive blocks); `/goal <condition>` re-checks a condition after each turn. In Cursor, a stop hook in `.cursor/hooks.json` can re-prompt until a scratchpad says DONE, capped at 5 iterations. Both only enforce green; steps 3 and 6 still need checking by you.

### Executing a spec's slices

- Load only the spec, `CLAUDE.md` or `AGENTS.md`, and the files its "Context for the build session" names. If that is not enough to build a slice, stop and say so: it is a gap in the spec, not a licence to improvise.
- Work in slice order. TDD slices: steps 2-9 against the named seam. E2E slices (glue, UI, config): make the change, then run the exact command or flow the slice names and record what it showed. "It compiles" is not verification.
- After each slice: run the relevant suite, tick the slice in the spec, and state in one line what was verified.
- Report problems outside the spec's scope to the user, one sentence each. They go back through `spec-interview`, not into this diff.
- If a slice grows well beyond its description, stop and say so.
- If the context is getting heavy or the work must pause, write a handoff with `session-handoff` (personal-productivity) and continue in a fresh session.
- When every slice is ticked, set the spec's status to done, summarise how each slice was verified, and recommend a review with `code-review-standard` before the user commits.

## Verification

Show, do not assert:

- The red run: command and output with each new test failing for the expected reason.
- The staged diff containing only the tests, made before implementation.
- `git diff -- <test paths>` is empty, or every test change has user agreement with its reason recorded.
- The green run of the new tests and of the full suite, with counts compared to the baseline. No new skips, xfails or ignore markers (`git diff` search for skip, only, xfail, ignore and the project's equivalents).
- Every new test has at least one assertion on behaviour; none is print-only.
- The manual exercise output from step 9.
- When executing a spec: every slice is ticked with its verification line, and nothing outside the spec's scope changed.

## Gotchas

- **Tests that pass already.** Without the red run, a test may check something already true, or check nothing. This is the single most common way TDD silently fails with agents.
- **Observation instead of assertion.** A 2026 study of SWE-bench Verified runs found agent tests were mostly value-printing; relational assertions were only about 3-8% of assertions, and how often an agent wrote tests was not linked to whether it solved the task. Count assertions, not tests.
- **Failing for the wrong reason.** A red caused by a missing import or bad fixture turns green after any change. Read the failure message.
- **Dropped or weakened tests.** In Armin Ronacher's agent-driven port, the agent dropped "must fail" tests and regressed semantics until steered back. Kent Beck lists disabled tests and unrequested features as warning signs in augmented coding (from a summary of his essay). Diff the test files every time.
- **Mocks that test the mock.** Mocking the unit under test proves the mock works. Cursor's TDD recipe says explicitly to state there are no mocks.
- **Tests through private internals.** They break on every refactor and pin implementation, not behaviour. Go through the public interface.
- **Tests for impossible cases.** Anthropic notes that chasing every reviewer finding produces tests for cases that cannot happen. Test the specified behaviour and real edges.
- **Self-grading.** The writer of the code is biased toward its own work. Where possible, one agent or session writes the tests and another writes the code, or a fresh-context reviewer checks the tests against the spec.
- **Pre-existing failures.** Without the baseline in step 1, a red suite at the end cannot be attributed. Never "fix" an unrelated failing test as part of this change.
- **Green is not done.** Willison's agentic manual testing point: tests can pass while the feature is unusable. Step 9 is required.

## Output

Hand back:

```markdown
## TDD report: <behaviour>
- Baseline: `<suite command>` -> <passed>/<failed>/<skipped> (pre-existing failures: <list or none>)
- Tests added: <file::test names>, each asserting <what>
- Red run: `<command>` -> all new tests failed; reasons: <assertion mismatch / not implemented>
- Tests staged: <paths> (unchanged since staging: yes / changed with approval: <reason>)
- Green run: new tests pass; full suite <passed>/<failed>/<skipped> vs baseline
- New skips/xfails/ignores: none
- Manual exercise: <command and observed output or screenshot>
- Follow-ups: <bugs found and turned into tests, open questions>
- Slices: <n of m ticked>; out-of-scope findings reported: <list or none>
```

## Sources

- Simon Willison, "Red/green TDD", Agentic Engineering Patterns, ~23 Feb 2026: https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/
- Simon Willison, "First run the tests", ~24 Feb 2026: https://simonwillison.net/guides/agentic-engineering-patterns/first-run-the-tests/
- Simon Willison, "Agentic manual testing", ~6 Mar 2026: https://simonwillison.net/guides/agentic-engineering-patterns/agentic-manual-testing/
- Cursor, "Best practices for coding with agents" (tests from input/output pairs, no mocks, confirm fail, commit tests, implement without modifying them; grind hook), Lee Robinson, 9 Jan 2026: https://cursor.com/blog/agent-best-practices
- Anthropic, Claude Code best practices (failing reproduction test first; fix root cause, do not suppress errors; Stop hook and `/goal`; separate writer and reviewer; over-applying review findings; reset after two failed corrections), current docs read Oct 2026: https://code.claude.com/docs/en/best-practices
- Chen, Sun et al., agent test writing on SWE-bench Verified, arXiv 2602.07900 v2, 9 Apr 2026: https://arxiv.org/html/2602.07900v2
- Matt Pocock, `tdd` skill (one test at a time through public interfaces), aggregator description read Oct 2026: https://vibeindex.ai/collection/mattpocock/skills
- Jesse Vincent, obra/superpowers `test-driven-development` (strict red-green-refactor), README read Oct 2026: https://github.com/obra/superpowers
- Armin Ronacher, "Porting MiniJinja to Go With an Agent", 14 Jan 2026: https://lucumr.pocoo.org/2026/1/14/minijinja-go-port/
- Kent Beck, "Augmented Coding: Beyond the Vibes" (summary page only), 25 Jun 2025: https://kentbeck.com/summaries/augmented-coding-beyond-the-vibes/
