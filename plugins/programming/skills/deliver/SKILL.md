---
name: deliver
description: >-
  Orchestrates a change from problem to hardened, documented code in gated phases: define
  (grill to an unambiguous SPEC.md, data model first, module diagram), slice and build
  (vertical deliverables, parallel fresh-context agents sharing one style brief), test
  (spec-blind tests, one behaviour each, every path, mutation testing), refactor, harden and
  document. The orchestrator delegates all implementation, stops for approval at every phase
  boundary and never commits. Use when the user wants a feature or change built end to end
  with agents, hands over a ticket or spec to implement, says "deliver", "run the workflow"
  or names a phase ("phase 3", "do the cleanup phase"), or resumes a SPEC.md with unticked slices.
license: MIT
metadata:
  category: "programming/workflow"
  sources: "see Sources section"
---

# Deliver

The team's main workflow for building software with agents. You are the orchestrator: you hold the spec, the plan and the shared brief, you hand each piece of work to an agent with a fresh context, and you check what comes back. The user approves every phase boundary. Two rules run through every phase: make the smallest change that meets the spec, and write code for a human reader, who holds far fewer things in working memory than an agent and loses the thread with each jump to another file.

**Side effects:** writes SPEC.md (through `grill`), DELIVERY.md beside it (the phase log), code, tests and docs in the user's working tree, and runs the project's tests, coverage, linters and analyzers. Sends repository code to subagents; may web-search for the language's style guide. Installs a tool (lizard, a mutation tester, a scanner) only after the user approves. Never stages, commits, pushes, opens a PR or changes git history: the user commits.

## When to use

- Building a feature, behaviour change or small project with agents, from a ticket, a spec or a one-line idea.
- The user asks for the full workflow, or for one phase of it.
- Resuming: SPEC.md exists and its slices table has unticked rows, or DELIVERY.md names a next phase.

## When not to use

- A one-file change with one obvious approach: make it, run the tests, report. (`grill` sizes it as small.)
- A bug whose cause is unknown: `diagnose` first, then come back with the cause.
- The same mechanical change across many units: `migrate`.
- Reviewing someone's existing change: `review`.

## Inputs to gather

Read before asking anything; never ask what the repository answers.

- `CLAUDE.md` or `AGENTS.md`, README, CONTRIBUTING, CI config, Makefile or package scripts, and the code around the change.
- Which tools are already available. For every tool a phase needs (coverage, mutation tester, complexity, scanners), run `command -v <tool>` or `<tool> --version` first, including the project's virtualenv and tool runners. Propose an install only for what is missing.
- The project's test, coverage, lint, format and analyzer commands. Run the full suite once and record the baseline: command, counts, pre-existing failures. Record `git rev-parse HEAD` and `git status --short` so you can show at the end that nothing was committed.
- The style guide: the repo's own (STYLE.md, CONTRIBUTING, linter and formatter config) first; if there is none, the language's guide from `references/toolbox.md`, confirmed by a web search for its current URL. Record which one, and why.
- The document the user gave (ticket, issue, spec), if any.
- That the skills it runs are installed: `grill`, `refactor`, `harden` (programming plugin) and `system-docs` (documentation plugin). `grill` is required: without it, stop and say so. If another is missing, say which phase cannot run before starting.

## Procedure

**Gate rule, every phase.** End each phase with a gate message (template in Output): what was done, the evidence (commands and results), what is open, and the proposed next phase with its plan. Then wait. Do not start the next phase without approval. When the user names a phase, check its entry condition first (for example, phase 4 needs a green suite) and say if it does not hold.

**State rule, every phase.** Keep the delivery's state in files, not in your context. Once a gate is approved, append the phase's entry to DELIVERY.md (template in Output) and tell the user the next phase can start in a fresh session (`/clear`, then `/deliver continue`). When resuming, read SPEC.md and DELIVERY.md, and only the code the next phase needs; never ask what DELIVERY.md records.

**Lean rule, every phase.** Your context is re-read on every step, so keep it small. Run commands with quiet output and read only the failures. Agents read files and diffs and return short reports; read code yourself only where a report points.

**Delegation rule, every phase.** Implementation, test writing, pen-testing and reviewing are done by subagents with fresh context, never in your own context. Your context holds the spec, the plan and the evidence. A subagent knows only its brief, so build each brief from the templates in `references/briefs.md` and paste the same **style brief** into every one of them.

### Phase 1: Define

1. **Read the code first** (Inputs). Write down what it already settles (types, naming, error handling, the file to copy as the pattern) so the interview skips those questions.
2. **Get a document.** If the user gave none, propose creating SPEC.md. Either way, run `grill` with the document or request as input; it owns the interview, the data model, the module diagram and the slices. Tell it four things that differ from its standalone use, because this workflow continues where `grill` would stop:
   - Size the change as at least medium, so the spec always has a data model, a module diagram, acceptance checks and a slices table.
   - Each slice's gate is the command that runs its acceptance checks, not a TDD seam: tests are written in Phase 3, from the spec.
   - Ask only what the code cannot answer. Put scope defaults (edge, empty and error cases) into the playback for the user to correct, not into separate questions.
   - Skip the fresh-session hand-off at the end; Phase 2 follows here, with fresh agents.
3. **Check the design started from data.** Before approving, confirm SPEC.md has the data model (inferred from existing models and the requirements) and the module diagram, and that the user saw and adjusted both during the interview. Do not ask for the same approval twice.
4. **No blind spots.** Before asking for approval, list every assumption you are still making. Each one becomes a confirmed decision or an Open question with an owner.
5. **Gate:** SPEC.md approved. The gate message carries the Phase 2 slice and parallelism plan for approval.

### Phase 2: Slice and build

1. **Slice by deliverable.** Each slice is vertical (something a user or a test can observe on its own), small, and independent where possible (INVEST). Order slices by risk: the most uncertain part first, or a walking skeleton through every module first when the risk is integration. Each slice is the smallest change that passes its acceptance checks; anything not needed for them is out.
2. **Map overlap.** For each slice, list the files and interfaces it creates or changes and the slices it depends on. Slices with disjoint file sets and no dependency run in parallel; the rest run in order. When parallel slices share a new type or interface, define it first in a short sequential "contract" step, so agents build against the same shape.
3. **Write the style brief once** (`references/briefs.md`) and save it at the top of DELIVERY.md: the guide and its handful of rules that matter here, conventions observed in the code, the pattern file to copy, the principles (smallest change, no speculative abstraction, no new dependency without approval), and the exact test, lint and format commands.
4. **Fan out.** One implementer agent per slice, parallel slices in the same turn. Each brief gives the slice, its acceptance checks, the files it may and may not touch, the style brief, and its done condition: its own checks pass, lint is clean on its files, and it reports the files it changed. Parallel agents share one working tree, so none of them runs the full suite: each would see the others' half-finished work fail.
5. **Integrate each wave yourself.** Run the full suite and the linters. List every changed and new file (`git status --porcelain --untracked-files=all`; nothing is staged, so new files never show in `git diff`) and check each is inside its slice's allowed files. Give the full diff (`git diff HEAD` plus the new files) to a fresh verifier agent (`references/briefs.md`) with the slices' acceptance checks and allowed files; it reports, with file:line, anything outside scope, any unrequested feature and any check not met. Read the code yourself only where it points. Send problems back to a fresh agent with the failing output; do not patch them in your own context. Tick the slice in SPEC.md with its verification line.
6. **Iterate per deliverable when it helps.** If slices are deliverables the user wants to see before the next ones are built, stop after each wave with a short gate.
7. **Gate:** all slices ticked, suite green against the baseline.

### Phase 3: Test

1. **Learn the test conventions.** Find the frameworks, layout, helpers, and which kinds of test the project uses. Some projects use only end-to-end tests; follow the convention. If the change needs a kind the project does not use (for example unit tests in an e2e-only repo), ask before writing any.
2. **Spec-blind pass.** Fresh test agents, one per module where they do not overlap, get the SPEC.md acceptance checks, the public signatures (not the function bodies), the test conventions and the style brief. Tests written while looking at the implementation tend to confirm its bugs. Rules for every test are in `references/testing.md`: one story or assumption per test, named as the behaviour, literal expected values, no logic.
3. **Path pass.** Run coverage with branch coverage on the changed code. Give a fresh agent the list of uncovered lines and branches; it adds one behaviour test per path. A path no test can reach is reported as possible dead code for Phase 4, not forced with a contorted test.
4. **Triage failures.** A new failing test is either a bug or a wrong test. Decide with evidence from the spec. Bugs go to a fresh implementer with the failing test, and the test stays unchanged. If the spec does not settle it, ask the user.
5. **Mutation testing.** Run the project's mutation tool, scoped to the changed files (`references/testing.md` has the tools and scoping flags). Give the surviving mutants to a fresh test agent, which adds the test that kills each one or explains why it is equivalent. If no tool is installed, or scoping needs a config entry, propose it and wait.
6. **Gate:** suite green, every changed function's paths covered or the exclusion justified, the mutation score, and surviving mutants explained.

### Phase 4: Refactor

Propose it once tests are green. Run `refactor` on the changed code, including new files, and give it the style brief for every implementer it spawns: CRAP hotspots, dead code from earlier iterations, patterns the codebase already uses, abstractions only at three or more repeats, every proposal with a before and after code sample, and the full suite after each change. **Gate:** every proposal implemented or ruled out by the user.

### Phase 5: Harden

Run `harden` with the style brief for its fix-up agents: linters and analyzers, parallel pen-test agents on the change's attack surface, and repeated independent review passes for nil cases, pointers, logic and error paths, with every finding verified before it is reported. **Gate:** verified findings fixed with regression tests, the rest explained.

### Phase 6: Document

Run `system-docs` (documentation plugin): core concepts first, then diagrams of how the parts interact, with sequence diagrams where the process logic is complicated. **Gate:** the user approves the doc.

### Phase 7: Hand back

Report using the final template in Output. List the changed files. Draft the commit message or messages and the `git add` paths **for the user to run**. Never commit, stage or push.

## Verification

Before each gate, and in the final report, show:

- The full suite against the baseline: counts, and no new skips, xfails or ignores.
- Every slice ticked in SPEC.md with how it was verified; every changed or new file (`git status --porcelain --untracked-files=all`) inside some slice's allowed files.
- One style brief, pasted the same into every brief (say how many agents got it).
- DELIVERY.md has an entry for every approved phase.
- Tests: each one is named as a behaviour and contains no loops, conditionals or computed expected values; branch coverage of the changed code; the mutation score with surviving mutants explained.
- `git rev-parse HEAD` unchanged from the start and nothing staged by you (`git diff --staged` empty, or exactly what the user staged).

## Gotchas

- **Interviewing before reading.** Every question the code could answer costs the user attention and trust.
- **Thin briefs.** Subagents start from zero. Anthropic found vague one-line subagent tasks caused duplicated work and gaps; each brief needs the objective, the output format, the tools and the boundaries. "Follow the style guide" is not a brief; paste the rules.
- **Parallel agents on shared files.** Two agents editing the same file or inventing the same interface produce conflicts that look like they work. Anthropic notes that coding has fewer truly parallel tasks than research. Map file overlap first, define shared contracts before fanning out, and run in sequence whenever in doubt.
- **Orchestrator doing the work.** Implementing in your own context fills it with detail and leaves no fresh eyes to check the result.
- **Tests that confirm bugs.** Tests generated after the model saw faulty code caught fewer faults (14%) than tests written from the specification alone (25%) in a 2026 study. Keep the first test pass spec-blind.
- **Coverage is not effectiveness.** Full coverage with weak assertions passes on broken code.
- **Test-first rituals.** In the agent studies so far, prompting agents to write tests first did not improve correctness or mutation scores and cost several times the tokens. What helped was where the tests came from, so this workflow implements first and tests from the spec.
- **Untracked files.** Nothing is staged during the workflow, so new files never appear in `git diff`. Every check of what changed uses `git status --porcelain --untracked-files=all` as well.
- **Big slices.** A slice too large to review in one sitting is a slice to split. Size the fan-out to what the user can review, not to what agents can produce.
- **Silent gates.** A hurried user still gets a gate; it can be three lines.
- **Cost.** Multi-agent work spends many times the tokens of a single chat. Say so in the Phase 1 gate when the plan has many parallel agents.

## Output

Gate message:

```markdown
## Phase <n> done: <name>
Evidence: `<command>` -> <result>; ...
Changed: <files or slices>
Open: <questions, risks, deferred items, or none>
Next: Phase <n+1> <name>. Plan: <slices and parallel waves | proposals | agents and lenses>
Approve to continue?
```

DELIVERY.md (append one entry per approved phase):

```markdown
# Delivery log: <feature>
Spec: SPEC.md   Baseline: `<cmd>` <p/f/s>   Start HEAD: <hash>

## Style brief
<the style brief, verbatim>

## Phase <n>: <name> (approved <date>)
Evidence: `<command>` -> <result>; ...
Numbers: <every figure this gate produced: tests p/f/s, branch coverage, mutation score, CRAP top 3, findings per round and lens; or none>
Decisions: <what the user decided at this gate>
Open: <questions, risks, deferred items, or none>
Next: Phase <n+1> <name>
```

Final report:

```markdown
## Delivered: <feature>
Spec: SPEC.md (approved <date>); slices <n>/<n> ticked
Tests: baseline <p/f/s> -> now <p/f/s>; branch coverage of changed code <x%>; mutation score <y%>
Refactor: <implemented / ruled out>; CRAP max before -> after
Hardening: <verified findings fixed> / <dropped, with reason>
Docs: <path>
Not done: <anything skipped, with reason, or none>
Files changed: <list>
For you to run: git add <paths> && git commit -m "<drafted message>"
```

## Sources

- Agile Manifesto, principles behind it (deliver working software frequently; simplicity, the art of maximising work not done), 2001: https://agilemanifesto.org/principles.html
- Bill Wake, "INVEST in Good Stories, and SMART Tasks", 17 Aug 2003: https://xp123.com/?p=67
- Henrik Kniberg and Alistair Cockburn, Elephant Carpaccio facilitation guide (thin slices, each visible to the user), 11 Jul 2013: https://docs.google.com/document/d/1TCuuu-8Mm14oxsOnlk8DqfZAA1cvtYu9WGv67Yj_sSk/pub
- Anthropic, "How we built our multi-agent research system" (briefs need objective, output format, tools and boundaries; vague tasks duplicated work; about 15x the tokens of chat; a poor fit when agents share context or depend on each other, as much coding does), 13 Jun 2025: https://www.anthropic.com/engineering/multi-agent-research-system
- Anthropic, Claude Code subagents (own context window, no conversation history, only a summary returns), read Nov 2026: https://code.claude.com/docs/en/sub-agents
- Erik Kuefler, "Testing on the Toilet: Don't Put Logic in Tests", Google Testing Blog, 31 Jul 2014: https://testing.googleblog.com/2014/07/testing-on-toilet-dont-put-logic-in.html
- Petrović and Ivanković, "State of Mutation Testing at Google" (diff-based, skips arid lines, surfaced in code review), ICSE-SEIP 2018: https://research.google/pubs/state-of-mutation-testing-at-google/
- Mutation tools, read Nov 2026: mutmut 3.8.1 https://github.com/boxed/mutmut ; StrykerJS https://stryker-mutator.io/docs/stryker-js/getting-started/ ; PIT https://pitest.org/quickstart/maven ; cargo-mutants 27.1.0 https://docs.rs/crate/cargo-mutants/latest/source/NEWS.md ; gremlins https://github.com/go-gremlins/gremlins ; Infection MSI https://infection.github.io/guide
- Style guides, read Nov 2026: PEP 8 https://peps.python.org/pep-0008/ ; Effective Go (written for the 2009 release, not updated) https://go.dev/doc/effective_go ; Go Code Review Comments https://go.dev/wiki/CodeReviewComments ; Google style guides https://google.github.io/styleguide/ ; Rust API Guidelines https://rust-lang.github.io/api-guidelines/
- Tool docs, read Nov 2026: ruff https://docs.astral.sh/ruff/ ; golangci-lint https://golangci-lint.run/ ; Jest coverage reporters https://jestjs.io/docs/configuration ; Vitest coverage https://vitest.dev/config/coverage ; cargo-llvm-cov https://github.com/taiki-e/cargo-llvm-cov
- Konstantinou, Tambon, Papadakis, "On the risk of coding before testing" (14% vs 25% fault detection; confounded by conversation history), arXiv 2607.05139, Jul 2026: https://arxiv.org/html/2607.05139v1
- Birgitta Böckeler, "TDD inside the agent loop - theater or actual value?" (small exploratory study: no correctness or mutation-score gain, 3-8.5x tokens), martinfowler.com, modified 10 Aug 2026: https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html
- Chen et al., "Rethinking the Value of Agent-Generated Tests" (test-writing prompts moved SWE-bench outcomes by at most 2.6 points), arXiv 2602.07900 v2, Apr 2026: https://arxiv.org/html/2602.07900v2
