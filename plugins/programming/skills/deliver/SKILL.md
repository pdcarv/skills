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
  or names a phase ("phase 3", "do the cleanup phase"), or resumes a DELIVERY.md with unticked slices.
license: MIT
metadata:
  category: "programming/workflow"
  sources: "see Sources section"
---

# Deliver

The team's main workflow for building software with agents. You are the orchestrator: you hold the spec, the plan and the shared brief, you hand each piece of work to an agent with a fresh context, and you check what comes back. The user approves every phase boundary. Two rules run through every phase: make the smallest change that meets the spec, and write code for a human reader.

**Side effects:** writes SPEC.md (through `grill`), DELIVERY.md beside it (the phase log), code, tests and docs in the user's working tree, and runs the project's tests, coverage, linters and analyzers. Sends repository code to subagents; may web-search for the language's style guide. Installs a tool only when the user chooses that over the alternative offered. Never stages, commits, pushes, opens a PR or changes git history: the user commits.

## When to use

- Building a feature, behaviour change or small project with agents, from a ticket, a spec or a one-line idea.
- The user asks for the full workflow, or for one phase of it.
- Resuming: DELIVERY.md has unticked slices or names a next phase.

## When not to use

- A one-file change with one obvious approach: make it, run the tests, report.
- A bug whose cause is unknown: `diagnose` first, then come back with the cause.
- The same mechanical change across many units: `migrate`.
- Reviewing someone's existing change: `review`.

## Inputs to gather

Read before asking anything; never ask what the repository answers.

- `CLAUDE.md` or `AGENTS.md`, README, CONTRIBUTING, CI config, Makefile or package scripts, and the code around the change.
- Tools the phases need: look on PATH as well as in the repo, since dev tools are often installed but undeclared. Record what you found in DELIVERY.md. Never install one first; ask at the phase that needs it.
- The project's test, coverage, lint, format and analyzer commands. Run the full suite once and record the baseline: command, counts, pre-existing failures. Record `git rev-parse HEAD` and `git status --short` so you can show at the end that nothing was committed.
- The style guide: the repo's own (STYLE.md, CONTRIBUTING, linter and formatter config) first; if there is none, the language's guide from `references/toolbox.md` (web-search only if its URL there fails). Record which one, and why.
- The document the user gave (ticket, issue, spec), if any.
- That the skills it runs are installed: `grill`, `refactor`, `harden` (programming plugin) and `system-docs` (documentation plugin). `grill` is required: without it, stop and say so. If another is missing, say which phase cannot run before starting.

## Procedure

**Gate rule, every phase.** End each phase with a gate message (template in Output): what was done, the evidence (commands and results), what is open, and the proposed next phase with its plan. Then wait. Do not start the next phase without approval. When the user names a phase, check its entry condition first: the previous phase's entry is in DELIVERY.md and its evidence still holds when re-run. Say if it does not hold. "Green" means no failures beyond the baseline's.

**State rule, every phase.** Keep the delivery's state in files, not in your context. Once a gate is approved, append the phase's entry to DELIVERY.md (template in Output), then start the next phase in this session. Two exceptions: after logging Phase 4 and after logging Gate 5a, stop and tell the user to start a fresh session (`/clear`, then `/deliver continue`). Harden's rounds, and then its fixes, each need a clean context. When resuming, read SPEC.md and DELIVERY.md, and only the code the next phase needs; never ask what DELIVERY.md records. End a message with "Approve to continue?" only in the gate report; ask anything else within a phase as a plain question.

**Lean rule, every phase.** Your context is re-read on every step, so keep it small. Run commands with quiet output and read only the failures. Agents read files and diffs and return short reports; read code yourself only where a report points.

**Delegation rule, every phase.** Implementation, test writing, mutation runs, pen-testing and reviewing are done by subagents with fresh context, never in your own context. Your context holds the spec, the plan and the evidence. A subagent knows only its brief, so build each brief from the templates in `references/briefs.md` and paste the same **style brief** into every brief for an agent that writes code or tests. Name the model in each brief where the tool allows: mid tier for writing code and tests, running tools and the harden lenses; top tier for verifiers.

**Two failed fixes, stop.** When two fix attempts at the same failure fail, write the premise they share in one sentence and take it to the user before a third.

### Phase 1: Define

1. **Run `grill`** with the user's document or request. Tell it every acceptance check needs a command (Phase 3 turns them into tests), and to skip its "build in a fresh session" hand-off: the State rule covers that.
2. **Add the design to SPEC.md:** the data model (from existing models and the behaviour) and a module diagram. Draft the slices and parallel waves (Phase 2 steps 1–2) for the gate.
3. **Gate:** SPEC.md approved with its data model and diagram; slice plan approved, every acceptance check in exactly one slice. Record the slices in DELIVERY.md.

### Phase 2: Slice and build

1. **Slice by deliverable.** Each slice is vertical (a user or a test can observe it on its own), covers the acceptance checks of one goal, and is independent where possible. Order slices by risk: the most uncertain part first, or a walking skeleton through every module first when the risk is integration. Each slice is the smallest change that passes its acceptance checks; anything not needed for them is out.
2. **Map overlap.** For each slice, list the files and interfaces it creates or changes and the slices it depends on. Slices with disjoint file sets and no dependency run in parallel; the rest run in order. When parallel slices share a new type or interface, define it first in a short sequential "contract" step, so agents build against the same shape.
3. **Write the style brief once** (`references/briefs.md`) and save it at the top of DELIVERY.md: the guide and its handful of rules that matter here, conventions observed in the code, the pattern file to copy, the principles (smallest change, no speculative abstraction, no new dependency without approval), and the exact test, lint and format commands.
4. **Fan out.** One implementer agent per slice, parallel slices in the same turn. Each brief gives the slice, its acceptance checks, the files it may and may not touch, the style brief, and its done condition: its own checks pass, lint is clean on its files, and it reports the files it changed. Parallel agents share one working tree, so none of them runs the full suite: each would see the others' half-finished work fail.
5. **Integrate each wave yourself.** Run the full suite and the linters. List every changed and new file (`git status --porcelain --untracked-files=all`; nothing is staged, so new files never show in `git diff`) and check each is inside its slice's allowed files. Give this wave's diff and new files to a fresh verifier agent (`references/briefs.md`) with the slices' acceptance checks and allowed files; it reports, with file:line, anything outside scope, any unrequested feature and any check not met. Read the code yourself only where it points. Send problems back to the slice's implementer with the failing output (resume it where the tool allows, otherwise a fresh agent); do not patch them in your own context. Tick the slice in DELIVERY.md with its verification line.
6. **Wave gates on request.** If the user asked to see slices before later ones are built, gate after that wave (no new session).
7. **Gate:** all slices ticked, suite green against the baseline.

### Phase 3: Test

1. **Learn the test conventions.** Find the frameworks, layout, helpers, and which kinds of test the project uses. Some projects use only end-to-end tests; follow the convention. If the change needs a kind the project does not use (for example unit tests in an e2e-only repo), ask before writing any.
2. **Spec-blind pass.** Fresh test agents, one per module (modules that share test files share an agent), get the SPEC.md acceptance checks, the public signatures (not the function bodies), the test conventions and the style brief. Tests written while looking at the implementation tend to confirm its bugs. Rules for every test are in `references/testing.md`: one story or assumption per test, named as the behaviour, literal expected values, no logic. Each test cites the number of the acceptance check it covers.
3. **Branch pass.** Run branch coverage on the changed code (statement coverage where the language has none; say so). Give a fresh agent the uncovered lines and branches; it adds one behaviour test per branch. A branch no test can reach is reported as possible dead code for Phase 4, not forced with a contorted test.
4. **Triage failures.** A new failing test is either a bug or a wrong test. Decide with evidence from the spec. Bugs go to a fresh implementer with the failing test, and the test stays unchanged. If the spec does not settle it, ask the user.
5. **Mutation testing.** A fresh agent runs the tool recorded in Inputs on the changed code, in a scratch copy (scoping config goes in the copy), and replies with only the score and the survivors. If there is none, ask: "Install <tool>, or have an agent run mutation testing?" For an agent run, a fresh test agent in a scratch copy makes up to 30 mutants on covered, non-logging changed lines, decision points first, from these kinds: boundary, negated condition, and/or swap, arithmetic swap, constant ±1 or 0, removed call, default return, removed raise or throw. It runs that module's tests after each change and reports killed and survived per kind. Either way, a fresh test agent kills each survivor or explains why it is equivalent: no observable change, error messages included.
6. **Gate:** suite green, every acceptance check with a test, every changed branch covered, unreachable (sent to Phase 4) or excluded with the user's agreement; the mutation score, each survivor killed or marked equivalent with its reason.

### Phase 4: Refactor

Once tests are green, run `refactor` on the changed code, including new files, and give it the style brief for its implementers. **Gate:** every proposal implemented or ruled out by the user; suite green against the baseline with no test deleted, skipped or weakened; mutation re-run on the functions changed since the last run, plus its survivors.

### Phase 5: Harden

Run `harden` with the style brief. It has two gates, each logged to DELIVERY.md. **Gate 5a** (Harden findings): verified findings with reproductions and proposed fixes, approved. **Gate 5b** (Harden fixes): verified findings fixed with regression tests, the rest listed with their reason; mutation re-run as in Phase 4.

### Phase 6: Document

Run `system-docs` (documentation plugin): core concepts first, then diagrams of how the parts interact, with sequence diagrams where the process logic is complicated. **Gate:** the user approves the doc.

### Phase 7: Hand back

Report using the final template in Output. List the changed files. Pending actions. Summarize the changes. Analyze considerations when deploying, possible impacts. Never commit, stage or push.

## Verification

At each gate, show the items that apply to the phases done so far; in the final report, all of them:

- The full suite against the baseline: counts, and no new skips, xfails or ignores.
- Every slice ticked in DELIVERY.md with how it was verified; every changed or new file (`git status --porcelain --untracked-files=all`) inside some slice's allowed files.
- One style brief, pasted the same into every code- or test-writing brief (say how many agents got it).
- DELIVERY.md has an entry for every approved phase.
- Tests: each one is named as a behaviour and contains no loops, conditionals or computed expected values; branch coverage of the changed code; the mutation score, each survivor killed or marked equivalent.
- `git rev-parse HEAD` unchanged from the start and nothing staged by you (`git diff --staged` empty, or exactly what the user staged).

## Gotchas

- **Parallel agents on shared files.** Two agents editing the same file or inventing the same interface produce conflicts that look like they work. Anthropic notes that coding has fewer truly parallel tasks than research. Map file overlap first and define shared contracts before fanning out.
- **Untracked files.** Nothing is staged during the workflow, so new files never appear in `git diff`. Every check of what changed uses `git status --porcelain --untracked-files=all` as well.
- **Silent gates.** A hurried user still gets a gate; it can be three lines.
- **Cost.** State the planned number of agents in the Phase 1 gate; multi-agent work costs many times a single chat.

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
Tools: <tool: command | missing | unfit (why)>   Style guide: <which, why>   Start status: <git status --short, or clean>

## Slices
| # | Slice | Acceptance checks | Allowed files | Depends on | Done |

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
