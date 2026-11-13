---
name: diagnose
description: >-
  Finds the root cause of a bug before any fix is written, using a hypothesis-and-evidence
  loop, a failing reproduction test, temporary runtime instrumentation (instrument,
  reproduce, analyse, fix, verify, remove) and git bisect for regressions. Use when a test
  fails, a bug is reported, behaviour is unexpected, "it used to work", a fix did not hold,
  a race, timing or async bug reproduces but cannot be explained by reading the code, or a
  performance regression appeared between two known versions. Stops after three failed
  fixes and raises the architecture question with the human. Not for bugs whose cause is
  already known (tdd).
license: MIT
metadata:
  category: "programming/method"
  sources: "see Sources section"
---

# Diagnose

Turn "it's broken" into a confirmed root cause, a failing test that proves it, one targeted fix, and a clean tree. The rule this skill enforces: no fix without root-cause investigation first. Every step produces evidence that the next step depends on; a guess is never promoted to a fix without it.

**Side effects:** Writes the reproduction test and, after the user's approval, temporary marked instrumentation and the fix in the user's working tree, a debug log in a scratch file, and runs bisect in a throwaway `git worktree` under a scratch directory; Never stages, commits or pushes, never posts to a ticket or change description, and never changes production.

## When to use

- A test fails, a bug is reported, or behaviour differs from what is expected.
- A bug reproduces but reading the code does not explain it: races, timing, async ordering, leaks.
- A regression: it worked at a known version or commit and fails now (functional or performance).
- A previous fix did not hold, or several attempts have already failed.

## When not to use

- The cause is already known: write the failing test and fix it with `tdd`.

## Inputs to gather

- The full error text and stack trace, verbatim, not a paraphrase.
- Expected behaviour, actual behaviour, and exact reproduction steps or command. Ask whether the failure is intermittent and how often it happens.
- The last known good version, commit, build or date, if any.
- What touched it last: recent commits (`git log`, `git diff`), dependency bumps, config, environment, data or load changes.
- The project's exact test command and how to run a single test.
- Where the failure was seen (local, CI, staging, production) and whether it reproduces locally or in CI, the only places the agent runs or instruments code.

## Procedure

1. **Write the problem report.** Record expected vs actual behaviour and reproduction steps in a debug log (a scratch file; for the ticket, draft the text for the user to post). Every later hypothesis, test and result goes in the same log with a timestamp, including negative results.
2. **Read the evidence completely.** Read the whole error and every frame of the stack trace. Note the first frame in your code, the exact values involved, and any earlier warnings in the same log.
3. **Reproduce reliably.** Run the reproduction yourself. For an intermittent bug, run it in a loop several times and record the pass/fail ratio; that ratio is your baseline for verification later. If you cannot reproduce, collect more data (step 7) instead of guessing.
4. **Encode the reproduction as a failing test.** Write the smallest test that fails for the reported reason, run it, and confirm it fails with the expected message, not for an unrelated reason such as a typo or missing fixture. Before touching the implementation, tell the user which test file(s) to stage (do not stage or commit them yourself; git state is the user's), and do not edit the test to make it pass later. This test is the pass/fail check the rest of the work is judged against (see `tdd` in the programming plugin for the full loop).
5. **Check what touched it last.** Compare against the last known good state: `git diff <good>..HEAD`, dependency lockfile changes, config and environment differences. If there is a known good commit and the test from step 4 can run unattended, propose a bisect to the user and, once they agree, run it in a throwaway `git worktree` so their checkout and HEAD are untouched: see [references/bisect.md](references/bisect.md). A bisect result is evidence, not yet a root cause.
6. **Localise.**
   - In a multi-component path, with the user's approval (step 7), log what enters and leaves each component boundary, run once, and find the first boundary where the data is wrong.
   - Trace the bad value backward from where it is observed to where it was first produced; fix at the source, not where it surfaced.
   - Find similar code that works. Read the reference implementation completely and list every difference, however small.
   - Simplify and reduce: feed known inputs at an interface and shrink the case until removing anything makes the bug disappear.
7. **Collect runtime evidence when reading is not enough:**
   1. Write down several competing hypotheses.
   2. For each, draft log statements that would confirm or refute it. Tag every line with a unique marker (for example `DBG-7f3a H1`) and log the values, thread or task identity, and timestamps the hypothesis depends on.
   3. Ask before adding any: show the user the files, the lines and the marker, and wait for their OK. Further instrumentation needs a new OK.
   4. Reproduce using the exact steps; run intermittent bugs several times.
   5. Analyse the output and keep only the hypotheses the evidence supports. Record the refuted ones.
   Adding logging outside your local or test environment is a change; propose it to a human rather than shipping it yourself, and prefer existing levers such as raising log verbosity on the fly or sampling.
8. **Test one hypothesis at a time.** State it as "I think X is the root cause because Y". Pick the most probable and simplest first, weighed by risk. Design the test so its outcomes are mutually exclusive (one result confirms, the other refutes). Change one variable, observe, record. If refuted, form a new hypothesis; never stack a second change on top of the first.
9. **Confirm the root cause before fixing.** State to the user: the root cause (the mechanism, not just the location), the evidence that confirms it, and the proposed fix with its blast radius. Wait for explicit approval before writing the fix. Skip this gate only when the user has explicitly delegated the fix ("fix it, don't ask"); say that you are skipping it.
10. **Fix the root cause once.** Make a single change at the source identified in step 6 or 8. No "while I'm here" refactors, no defensive changes elsewhere in the same change. Report other problems found along the way to the user, one sentence each; do not fix them in this change. Run the failing test (it must now pass), then the full suite.
11. **Apply the three-fix rule.** If three or more fixes have failed, stop. Do not attempt a fourth. Write up what each attempt assumed and why it failed, and ask the human whether the design itself is wrong (shared state, wrong abstraction, wrong ownership of the data). Repeated failures in different places usually point at architecture, not at the next line of code.
12. **Remove the instrumentation.** Search for your marker (`git grep -n 'DBG-7f3a'`) and delete every added line. Confirm `git diff` contains only the test and the fix.
13. **Record the lesson.** Add the root cause, the refuted hypotheses and anything a future reader would otherwise rediscover to the debug log, and draft the same for the ticket or change description for the user to post.

## Verification

- The test from step 4 failed before the fix and passes after it, run by you, with the output captured.
- The user approved all instrumentation before it was added.
- The user approved the root cause before the fix (or explicitly delegated it), other problems found are listed rather than fixed, and nothing was staged or committed.
- The original reproduction steps no longer reproduce. For an intermittent bug, the loop from step 3 now passes every run, with enough runs that the old failure rate would have shown at least one failure.
- The full test suite passes, or any pre-existing failures are listed as unrelated with evidence.
- `git grep` for the instrumentation marker returns nothing.
- The root-cause statement explains every observed symptom, including the ones you did not fix directly. If one symptom is unexplained, you are not done.
- For a bisected regression, the fix is checked against the first bad commit's diff and explains why that commit broke it.

## Gotchas

- **Red-flag thoughts.** "Quick fix for now", "just try changing X", "one more fix attempt" mean you have skipped investigation. Go back to step 6.
- **Instrumentation changes the bug.** Verbose logging alters timing and can hide or create races. If adding logs makes the bug vanish, that itself is evidence of a timing dependency; log less and note the effect in the debug log.
- **Spurious correlation.** The more metrics and log lines you look at, the more coincidences you find. A hypothesis must predict an outcome before you test it.
- **"Same as last time".** Assuming a past cause has recurred is a documented troubleshooting pitfall. Check it like any other hypothesis.
- **Improbable theories first.** Exotic explanations are a documented pitfall. Test the probable and simple explanations first, and only reach for "the toolchain or a dependency is wrong" when the evidence leaves nothing else.
- **Chasing symptoms.** A downstream error, a timeout, or a retry log is often a symptom of the real failure further up. Trace backward (step 6) before treating it as the cause.
- **The test that proves nothing.** A reproduction test that fails because of a setup mistake will "pass" after any change. Confirm the failure message matches the bug.
- **Fixing in the wrong layer.** Patching where the bad value surfaced (a null check, a retry, a catch-all) hides the bug and moves it. Fix where the value is produced.
- **Leftover instrumentation.** Debug logging left in place leaks data and noise into production. Removal is a required step, not cleanup.
- **Agent loops.** If two corrections in a row have not helped, the context is probably wrong. Restart with a sharper problem statement (symptom, location, reproduce command, intermittent or not) rather than issuing a third correction.
- **"No root cause found".** Treat this as "investigation incomplete" until every boundary in the path has been instrumented and every difference from working code has been checked. If the evidence shows the cause is truly environmental, timing-dependent or external, document what you investigated, add appropriate handling and propose monitoring.

## Output

Hand back this report:

```markdown
## Bug: <one-line symptom>
- Expected / actual: ...
- Reproduction: <command or steps>; failure rate before fix: <n/m runs>
- Last known good: <commit/version or "unknown">; bisect result: <first bad commit or "not run">

## Root cause
<one paragraph: what is wrong, where it originates (file:line), why it produces every observed symptom>

## Evidence
| # | Hypothesis | Test | Result |
|---|---|---|---|
| H1 | ... | ... | refuted / confirmed |

## Fix
- Change: <file(s), one sentence>
- Reproduction test: <test name>, failed before, passes after (output attached)
- Full suite: <pass / list of unrelated failures>
- Instrumentation removed: <marker> not found by git grep

## Open questions / follow-ups
- <architecture concerns if the three-fix rule fired; anything not explained>
```

## Sources

- obra/superpowers, `systematic-debugging` SKILL.md (four phases, three-fix rule, red flags), main branch, read Oct 2026: https://raw.githubusercontent.com/obra/superpowers/main/skills/systematic-debugging/SKILL.md
- Cursor docs, Debug Mode (hypotheses, instrumentation, user reproduction, analysis, fix, removal; Cursor 2.2 per search results only), read Oct 2026: https://cursor.com/docs/agent/debug-mode
- Cursor, "Best practices for coding with agents" (commit failing tests first and do not modify them), 9 Jan 2026: https://cursor.com/blog/agent-best-practices
- Anthropic, Claude Code best practices (symptom plus location plus failing reproduction test; give a pass/fail check), current docs read Oct 2026: https://code.claude.com/docs/en/best-practices
- Anthropic, Claude Code common workflows (share the reproduce command, say whether intermittent), read Oct 2026: https://code.claude.com/docs/en/common-workflows.md
- Google SRE book, ch. 12 "Effective Troubleshooting" (hypothetico-deductive loop, simplify and reduce, what touched it last, pitfalls, negative results, mutually exclusive tests), read Oct 2026: https://sre.google/sre-book/effective-troubleshooting/
- git-bisect documentation, git/git master, read Oct 2026: https://raw.githubusercontent.com/git/git/master/Documentation/git-bisect.adoc
