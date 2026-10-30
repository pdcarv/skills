---
name: large-scale-migration
description: >-
  Runs a large mechanical code migration (language port, framework or major-version upgrade,
  API deprecation, test-framework switch) with agents, judge first: build a parity harness
  that runs the same checks against old and new code and prove it fails on broken code,
  write a translation rulebook, a dependency-ordered work queue and a gap inventory, do a
  shakedown run and discard it, trial the exact prompt on three units, then fan out
  implement-judge-review loops and fix the rulebook (not the files) whenever a finding
  repeats. Use when asked to migrate, port, upgrade or codemod many files, packages or
  services, or to plan or rescue a migration that agents are doing in parallel.
license: MIT
metadata:
  category: "programming/large-changes"
  sources: "see Sources section"
---

# Large-scale migration

Migrations are where agents have the strongest published wins, and every one of those wins rested on an objective oracle (a test suite, snapshots, a compiler) plus human-built process around it. Anthropic's July 2026 recipe puts the oracle first and treats the loop, not the code, as the thing to fix. This skill follows that recipe. All numbers from case studies are the companies' own reports; see [references/case-studies.md](references/case-studies.md).

## When to use

- The same transformation applies to tens to thousands of files, packages or services.
- Porting between languages or frameworks, or a major-version upgrade across many apps.
- Planning a migration, or a running migration is producing inconsistent or regressing output.

## When not to use

- A refactor of a handful of files: use `red-green-tdd` and normal review.
- No objective oracle exists and none can be built: stop and build tests first; fanning out without a judge produces unverifiable output.
- The work is mostly redesign rather than translation: write a design doc (`design-doc`, software-architecture) and migrate only the mechanical part.

## Inputs to gather

- The unit of work (file, module, package, service) and the full list of units.
- Available oracles: test suite, snapshot tests, compiler, type checker, linter, end-to-end scenarios. Run them on the old code and record the baseline.
- Dependency order between units.
- Budget: tokens or money, and wall-clock time. Review capacity: how many PRs or units a human can review per day.
- Execution environment: sandbox or container, allowed tools, credentials, where branches and PRs go, who merges.

## Procedure

1. **Build the judge.** A harness that runs the same checks against old and new code and compares results (parity). Reuse what exists: Armin Ronacher's Go port reused the Rust project's snapshot files as the oracle. If there are no tests, have the agent build them from real-world scenarios and review those tests yourself.
2. **Prove the judge can fail.** Break the new code on purpose (wrong return value, dropped branch, changed escaping) and confirm the judge reports it. Record the command and output. A judge that has never failed is not evidence.
3. **Plan and inventory.** Write three artifacts:
   - Rulebook: old pattern to new pattern, idioms, naming, error handling, each with a small example, versioned in the repo.
   - Work queue on disk: units in dependency order, each with a status (todo, in progress, passed judge, reviewed, merged, manual). On-disk state makes the run resumable.
   - Gap inventory: code that needs redesign rather than translation. Route these to humans; keep them out of the fan-out.
4. **Shakedown, then discard.** Migrate a representative slice, study what went wrong, update the rulebook and prompt, and throw the output away. Front-load human time here; it is the cheapest point to change the process.
5. **Trial on three units.** Run the exact fan-out prompt on three units, review all three by hand against the judge and rulebook, fix the prompt, and only then run the rest.
6. **Fan out.** Per unit: implement, run the judge, review, fix, with a per-unit iteration cap. Anthropic suggests smaller models to implement and larger ones to review. Run validation in a fixed order and feed each failure back (Airbnb's pipeline: refactor, then fix test errors, then lint, then type-check). Options, tool-specific and optional:
   - Claude Code `/batch <instruction>` splits a mechanical change into 5-30 units, each in its own worktree with its own PR.
   - Claude Code headless loop (`--bare` skips local config discovery and needs an API key, not OAuth login):
     ```bash
     while read -r unit; do
       claude --bare -p "Migrate $unit following RULEBOOK.md. Run <judge command>. Reply OK or FAIL." \
         --allowedTools "<minimal tool list>" --permission-mode dontAsk --max-turns 20
     done < queue.txt
     ```
   - Cursor: one cloud agent per app or library, each opening a PR.
   Run unattended work in a sandbox with turn and budget caps, and protect the main branch; merging stays a human action.
7. **When a finding repeats, fix the rulebook.** If reviewers flag the same issue in more than one unit, change the rulebook or prompt and re-run the affected units. Do not patch files one by one.
8. **Use failures as queues.** Collect compiler errors, crashes and parity failures, group them by root cause, fix the cause in the rulebook or shared code, then do a single controlled rebuild instead of piecemeal reruns.
9. **Guard semantics.** Diff test files on every unit: agents drop "must fail" tests, weaken assertions, or change semantics (Ronacher's port regressed HTML escaping and `range` semantics until steered back). Any test removed or skipped is a finding.
10. **Finish the long tail by hand.** Expect humans to complete the last few percent (Airbnb fixed under 100 of about 3.5k files by hand). Track these as `manual` in the queue.
11. **Review patterns, then merge in reviewable chunks.** After the rulebook settles, review a sample per rule and every unit that needed manual fixes. Size parallelism to review capacity, not agent capacity.
12. **Ship it like any other change.** Use `safe-rollout` for deployment, and watch for post-merge regressions (Bun reported 19 after merge, all fixed).

## Verification

- Judge failure proof: output of the judge failing on deliberately broken code.
- Baseline vs final: the full existing suite and the parity harness pass on the new code, with counts matching the baseline.
- No tests removed, skipped or weakened: `git diff` on test paths reviewed, exceptions listed with approval.
- Work queue: every unit is merged or explicitly `manual` with an owner; none silently missing.
- Rulebook: versioned, and every repeated review finding maps to a rulebook change.
- Spend recorded against the budget.

## Gotchas

- **A judge that cannot fail.** Step 2 is the one most often skipped and the one that makes the rest meaningful.
- **Fixing files instead of the process.** The same mistake then appears in hundreds of units. Anthropic's line: you don't fix the code, you fix the loop that produced it.
- **Scaling an untested prompt.** Skipping the shakedown and three-unit trial multiplies prompt bugs by the number of units.
- **Redesign hidden in translation.** Units that need new design fail repeatedly in the loop and burn budget. Move them to the gap inventory.
- **Retries vs prompt tuning.** Airbnb's engineers found brute-force retries with error feedback more effective than prompt engineering for the long tail, with some files needing 50-100 retries. Cap retries and send what remains to humans.
- **Weak agent tests.** If the agent writes the oracle, review it: agent-written tests are often value-printing rather than asserting.
- **Cost.** Anthropic notes large migrations still cost tens to hundreds of thousands of dollars in tokens. Set `--max-budget-usd` or the equivalent and watch spend per unit.
- **Unattended headless runs and trust.** Without `--bare`, `claude -p` runs project hooks and `.mcp.json` servers even in an untrusted folder, with no trust dialog. Use `--bare` with explicit settings for untrusted repos and CI.
- **Worktrees lack local files.** New worktrees miss gitignored files and installed dependencies; Claude Code's `.worktreeinclude` copies listed files.
- **Headline savings are self-reported.** Counterfactual baselines ("5 years of work", "$6M") come from the beneficiary or vendor and are probably inflated; no independent audit of post-migration defect rates was found for any of the published cases.

## Output

Migration plan, kept in the repo and updated as the run progresses:

```markdown
# Migration: <from> -> <to>
Units: <n> <files|packages|services>   Budget: <tokens/$>   Reviewer capacity: <units/day>

## Judge
- Command: `<parity harness command>`
- Baseline on old code: <pass/fail counts>
- Proven to fail on broken code: <what was broken, output excerpt, date>

## Rulebook
- Path: RULEBOOK.md (version <n>)
- Changes since last version: <rule added/changed, triggered by finding #>

## Gap inventory (human redesign)
| Unit | Why not mechanical | Owner |

## Shakedown and trial
- Shakedown slice: <units>, discarded; rulebook changes: ...
- Trial units: <u1, u2, u3>; result: <pass/fail per unit>; prompt changes: ...

## Queue status
| Status | Count |
|---|---|
| todo / in progress / passed judge / reviewed / merged / manual | ... |

## Repeated findings -> rulebook fixes
| Finding | Units affected | Rulebook change | Re-run done |

## Spend and regressions
- Spend to date: <tokens/$>   Post-merge regressions: <n, links>
```

## Sources

- Anthropic, "AI code migration" (judge first, rulebook, gap inventory, shakedown then discard, on-disk queue, fix the rulebook on repeated findings, failures as queues; Bun and Python-to-TypeScript case studies), 16 Jul 2026: https://claude.com/blog/ai-code-migration
- Anthropic, Claude Code best practices (headless fan-out tried on three files first; `/batch`; unattended-run checklist), current docs read Oct 2026: https://code.claude.com/docs/en/best-practices
- Claude Code headless docs (`--bare`, `-p` trust behaviour, `--max-budget-usd`), read Oct 2026: https://code.claude.com/docs/en/headless.md
- Claude Code worktrees docs (`.worktreeinclude`), read Oct 2026: https://code.claude.com/docs/en/worktrees.md
- Armin Ronacher, "Porting MiniJinja to Go With an Agent", 14 Jan 2026: https://lucumr.pocoo.org/2026/1/14/minijinja-go-port/
- InfoQ, Airbnb Enzyme to React Testing Library migration, 28 Mar 2025: https://www.infoq.com/news/2025/03/airbnb-llm-test-migration/
- Gergely Orosz, The Pulse (Pragmatic Engineer) on migrations with AI, 27 Aug 2026 (updated 22 Oct 2026): https://blog.pragmaticengineer.com/the-pulse-we-need-to-talk-about-migrations-with-ai/
- Cursor, Navan customer story (one cloud agent per app or library), 16 Oct 2026: https://cursor.com/blog/navan
- Chen, Sun et al., agent test writing on SWE-bench Verified, arXiv 2602.07900 v2, 9 Apr 2026: https://arxiv.org/html/2602.07900v2
- Armin Ronacher, "The Final Bottleneck" (review capacity), 13 Feb 2026: https://lucumr.pocoo.org/2026/2/13/the-final-bottleneck/
