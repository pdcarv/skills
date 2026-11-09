---
name: refactor
description: >-
  Cleans up working code once its tests are green: finds complexity hotspots with CRAP scores
  (cyclomatic complexity plus coverage, via a bundled script that reads lcov, Cobertura,
  JaCoCo or Go cover profiles), dead code and abstractions left from earlier iterations,
  then proposes changes as before-and-after code samples ranked by how much easier the code
  becomes for a human to read. Prefers design patterns the codebase already uses, proposes an
  abstraction only for three or more repeats, runs the full suite after every change, and
  loops until each proposal is implemented or ruled out with the user. Use when a feature
  is done and green, when asked to clean up, simplify, refactor, reduce complexity, find
  CRAP or dead code, or as phase 4 of deliver.
license: MIT
metadata:
  category: "programming/quality"
  sources: "see Sources section"
---

# Refactor

Make working code easier for the next person to read and change, without changing what it does. Agents follow indirection and long functions easily; people hold about four chunks in working memory at once (Cowan), so every extra file, layer or flag they must keep in mind while reading a flow has a cost. Measure where the complexity is, propose specific changes with code, let the user choose, and prove after each change that behaviour did not move.

**Side effects:** reads the code and writes coverage reports to the project's usual output paths; edits source files only for proposals the user approved. Runs the test suite, coverage and `scripts/crap.py`. Installs `lizard` (or a dead-code tool) only after the user approves. Never stages, commits, pushes, or uses git to undo a change.

## When to use

- A feature works and its tests are green, and the code grew through several iterations.
- The user asks to clean up, simplify, refactor, reduce complexity, or find CRAP or dead code.
- Phase 4 of `deliver`.

## When not to use

- Tests are red or missing for the code in question: fix or add tests first (`deliver` phase 3, or `tdd`).
- Behaviour must change too: that is a feature; refactor before or after it, never in the same step.
- A one-off review of someone else's diff: `review` covers simplification findings as Nits.

## Inputs to gather

- The scope: changed and new files (`git diff --name-only <base>` plus untracked files from `git status --porcelain --untracked-files=all`, since uncommitted new files never show in a diff), or the module the user names.
- The test command, and a green baseline run with its counts. Stop if it is red.
- A coverage report in a format `scripts/crap.py` reads (`references/coverage.md` lists the commands per language).
- The patterns the codebase already uses, with one example path each (see Procedure step 4).
- The style brief from `deliver`, pasted into every implementer brief. Standalone, write one the same way: the repo's style guide rules that matter here, the pattern file to copy, the principles, and the commands.

## Procedure

1. **Baseline.** Run the full suite; record counts. If anything is red, stop and report.
2. **Measure.** Produce coverage for the scope, then run:
   `python3 <this skill's folder>/scripts/crap.py --coverage <report> <paths>` (add `--json` to keep the numbers).
   If `lizard` is missing, the script says so; ask before installing it. Record the table.
3. **Find where the complexity is.** Read, in order: functions above CRAP 30 (complex and poorly tested: risky to touch, so a fresh test agent adds behaviour tests for them first, under the same rules as `deliver` Phase 3); functions with high complexity but high coverage (safe to change, still hard to read); then the code itself for: dead code (unused functions, unreachable branches reported by testing, flags and parameters nothing sets, commented-out code, leftovers from abandoned approaches, modules not in the spec's module diagram); abstractions with one implementation or one caller; and indirection a reader must chase across files for a simple flow. Use the project's dead-code tool if it has one.
4. **Inventory the team's patterns.** Search the codebase for the patterns it already uses (table-driven dispatch, strategy objects, repository or service layers, builders, middleware chains, result types) and note one example path for each. Proposals use these first: the team already knows how to read them. Propose a pattern the codebase does not use only when nothing familiar fits, and say it is new.
5. **Check repetition before abstracting.** Propose an abstraction only when the same shape appears at least three times **and** the copies change for the same reason. Two copies, or copies that will diverge, stay duplicated: the wrong abstraction costs more than duplication.
6. **Write proposals** using the template in Output. Each has a before and after code sample from the real code, the metric it moves (CRAP, complexity, lines, files a reader must open), the readability cost, and the risk. Rank by benefit to a reader per unit of risk. Prefer, in this order: delete dead code; inline needless indirection; rename; guard clauses and early returns; extract a well-named function in the same file; replace a conditional chain with a lookup table; then a pattern from step 4.
7. **Present all proposals at once** and let the user choose. Record each as approved, rejected (with the user's reason) or deferred.
8. **Apply one approved proposal at a time**, each through a fresh implementer agent with the style brief, however small: you keep the measurements and the review, the agent makes the edit. After each one, run the full suite. If it goes red, undo that edit by restoring the previous code with an edit (never `git checkout`, `reset` or `stash`), report it, and move on.
9. **Re-measure** after the batch: run `scripts/crap.py` again and show the before and after for every function touched.
10. **Loop** steps 3-9 until you and the user have implemented or ruled out every proposal and you find nothing new worth proposing.

## Verification

- Green suite after every applied change, with counts equal to the baseline plus any tests added in step 3 (none deleted, skipped or weakened).
- Before and after CRAP table for every touched function.
- Every proposal has real before and after code and a recorded decision.
- Every abstraction proposed points to its three or more call sites.
- No behaviour change: no test edited except to follow a rename the user approved.

## Gotchas

- **Refactoring untested code.** A high CRAP score means change is risky; without tests, a refactoring can change behaviour unnoticed.
- **Patterns as decoration.** A Strategy with one strategy or a Factory with one product adds a file and a jump for no gain. Count implementations before proposing.
- **Indirection that agents like and people don't.** Many tiny functions across many files read fine to an agent and lose a human reader. Measure "files to open to follow this flow", not just function length.
- **DRY taken too far.** Merging code that merely looks alike couples things that change for different reasons. The rule of three plus "same reason to change" is the guard.
- **Proposals without code.** "Extract a service" cannot be judged. A before and after sample from the actual code can.
- **Batching changes between test runs.** When several edits land together and the suite goes red, you cannot tell which one broke it.
- **Coverage paths that don't match.** If `crap.py` reports "without coverage data" for files you know are tested, the report paths differ from the source paths; regenerate the report from the repo root.

## Output

Proposal (one per item):

```markdown
### R<n>: <one-line change>  (<file:line>)
Why: <metric: CRAP 42 -> ~8 / complexity 12 -> 4 / files to follow the flow 5 -> 2>
Pattern: <existing pattern and its example path | none | new: <name>, because ...>
Before:
<code from the file>
After:
<proposed code>
Readability cost: <new names, files or jumps a reader must learn, or none>
Risk: <low/medium/high: what could change behaviour, and which test guards it>
Decision: approved | rejected (<reason>) | deferred
```

Summary:

```markdown
## Refactor: <scope>
Baseline: `<cmd>` <p/f/s>   After: <p/f/s>
CRAP above 30: <n before> -> <n after>; worst: <fn> <before> -> <after>
Applied: R1, R3 ...   Rejected: R2 (<reason>) ...   Deferred: ...
Dead code removed: <list>
```

## Sources

- Alberto Savoia, "This Code is CRAP" (CRAP1 = comp^2 x (1 - cov/100)^3 + comp; above 30 counts as crappy; created with Bob Evans in 2007; crap4j used basis-path coverage), Google Testing Blog, 22 Feb 2011: https://testing.googleblog.com/2011/02/this-code-is-crap.html
- lizard, Terry Yin (per-function cyclomatic complexity for 25+ languages; Python API with start and end lines), v1.25.1, 7 Nov 2026: https://github.com/terryyin/lizard
- coverage.py, `coverage xml` (Cobertura) and `coverage lcov`, docs v7.17, read Nov 2026: https://coverage.readthedocs.io/en/latest/commands/cmd_xml.html
- Rob Pike, "The cover story" (Go cover profiles), 2 Dec 2013: https://go.dev/blog/cover
- JaCoCo report goal (its own XML format), read Nov 2026: https://www.jacoco.org/jacoco/trunk/doc/report-mojo.html
- Sandi Metz, "The Wrong Abstraction" (duplication is far cheaper than the wrong abstraction; inline it back, then re-extract), 20 Jan 2016: https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction
- Rule of three, credited to Don Roberts in Fowler et al., Refactoring (1999); attribution seen via Wikipedia, book text not checked: unverified.
- Nelson Cowan, "The magical number 4 in short-term memory" (about four chunks, range three to five), Behavioral and Brain Sciences 24(1), 2001: https://memory.psych.missouri.edu/assets/doc/articles/2001/cowan-bbs-2001.pdf
- Kent Beck, Tidy First? (keep structural changes apart from behaviour changes), O'Reilly, Oct 2023: https://www.oreilly.com/library/view/tidy-first/9781098151232/
- Google Engineering Practices, "What to look for in a code review" (too complex means readers cannot understand it quickly; over-engineering), read Nov 2026: https://google.github.io/eng-practices/review/reviewer/looking-for.html
- refactoring.guru, code smells catalogue (Bloaters, Dispensables, Couplers, ...), read Nov 2026: https://refactoring.guru/refactoring/smells
