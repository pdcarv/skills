---
name: learnings
description: >-
  After a task, turns what went wrong or had to be corrected into the smallest durable
  fix in the right place: an enforced check (hook, deny rule, linter, test) for rules
  that must never be broken, one line in AGENTS.md, CLAUDE.md or a Cursor rule for
  non-obvious conventions, a path-scoped rule, a Gotchas line in a skill, a small tool,
  or a solution note in a retrieved lessons folder (docs/solutions/) that is not loaded
  on every task. Guards against instruction bloat, since research found repository
  context files generally do not raise task success and do raise cost. Use when a
  non-trivial fix or feature is done, after the agent repeated a mistake or needed the
  same correction twice, when the user says "remember this", "add this to CLAUDE.md",
  "write a rule" or "compound", or when reviewing or pruning agent instruction files.
license: MIT
metadata:
  category: "documentation/knowledge"
  sources: "see Sources section"
---

# Learnings

Every's compound-engineering loop ends each task with a "compound" step: record what was learned so the next task is easier. Practitioners agree on the core move (turn each repeated mistake into a persistent artifact: an AGENTS.md or CLAUDE.md line, a rule, a tool or a hook), but always-on instructions cost tokens on every task and the evidence that they help is weak. So this skill decides, per lesson, whether it deserves to persist at all and, if so, in the cheapest place that will actually change behaviour. No published measurement shows that the compound loop pays off; treat it as a practice to evaluate, not a proven gain.

**Side effects:** writes instruction files, rules, hooks, settings, skill Gotchas and lessons notes only after the user approves the proposed diff. Reads the project's instruction surfaces, and may re-run a task in a fresh session or throwaway worktree. Never commits or pushes.

## When to use

- A non-trivial fix or feature just finished and something non-obvious was learned.
- The agent made the same mistake twice, or the user had to correct the same thing twice.
- Right after the user corrects the agent's behaviour or a wrong assumption, to decide whether the correction should persist.
- The user says "remember this", "add this to CLAUDE.md/AGENTS.md", "make a rule" or "compound".
- Instruction files feel long, contradictory or ignored and need pruning.

## When not to use

- Continuing the same task in a new session: use `handoff`.
- Writing a whole new procedure: write it as a new skill following the library's `CONTRIBUTING.md`, then come back to link it.
- Writing up an incident for the organisation: out of scope; that is a postmortem, not a lesson for the agent.

## Inputs to gather

- What happened: the mistake or correction, with the evidence (diff, failing command, the user's correction in their words).
- Whether it has happened before: search existing instruction files, rules, skills and the lessons folder for the topic.
- The project's instruction surfaces and their sizes: AGENTS.md / CLAUDE.md (root and nested), CLAUDE.local.md, `.claude/rules/` or `.cursor/rules/`, skills, hooks and settings, linters and tests, a lessons folder such as `docs/solutions/`.
- Who shares each surface (personal vs committed for the team) and who approves changes to shared ones.

## Procedure

1. **List candidate lessons.** For each: what went wrong, the root cause, the fix, and what would have prevented it. Evidence: the diff, command output or quoted correction for each.
2. **Drop what does not need to persist.** Remove a lesson if the agent can find it by reading the code, if it was a one-off, or if it is something the model already does by default. Anthropic's test for CLAUDE.md is whether Claude could find it in the code or would otherwise have to rediscover it each session; Cursor adds rules only after a repeated mistake.
3. **Route each surviving lesson to one place** (first match wins):

   | The lesson is... | Put it in | Why |
   |---|---|---|
   | A must-never or must-always rule that a machine can check | Hook, deny rule, linter or test | Instruction files and skills are advisory; hooks and settings are enforced by the harness |
   | A missing capability that caused the mistake (no way to see the UI, a noisy test runner) | A small tool or script, referenced from the instruction file | Mitchell Hashimoto turns agent mistakes into AGENTS.md fixes or tools |
   | How the agent should behave with this user in every project | User-level instructions (`~/.claude/CLAUDE.md`, Cursor user rules) | Applies everywhere; when it could be global or repo-only, ask which |
   | A non-obvious convention that applies to most tasks in the repo | One line in AGENTS.md / CLAUDE.md, or a Cursor rule | Exact commands, misleading code areas, decisions made outside the repo, anything corrected twice |
   | A fact about the system or domain that one file does not reveal (an invariant, terminology, architecture) | The repo's domain notes, for example `docs/CONTEXT.md` | Read when relevant, not loaded every turn |
   | A decision between alternatives, with consequences | An ADR (`adr`, documentation) | Keeps the reason, not just the outcome |
   | A convention for one area of the code | Path-scoped rule (`.claude/rules/*.md` with `paths:`, or a scoped Cursor rule) or a nested AGENTS.md / CLAUDE.md | Loads only when that area is touched |
   | A failure mode of an existing procedure | One line in that skill's Gotchas section | Gotchas are the highest-signal part of a skill |
   | A step-by-step procedure that recurs | A new skill (see `CONTRIBUTING.md`) | Loads on demand, not every turn |
   | A specific problem and its solution, rarely relevant | A note in the lessons folder (`docs/solutions/<slug>.md`) | Retrieved when relevant instead of loaded every task |
   | A personal preference for this repo only | CLAUDE.local.md | Keeps the shared file for the team |
   | A personal fact or preference outside software work | The user's own profile notes (ask where) | Keeps agent rules about agent behaviour |

4. **Write the smallest version.** One line per convention in instruction files: state the rule and, if not obvious, the reason in a clause. No emphasis words; Anthropic lists ALL-CAPS and "IMPORTANT" as obsolete. For a lessons note use the template in Output: problem, symptoms, root cause, fix, prevention, tags. Generalise to the pattern, not the incident: "Use `bun`, not `npm`", not "in the auth fix, npm was used by mistake". If the target `CLAUDE.md` or `AGENTS.md` has no structure yet, start it with two headings, Commands and Rules, one line per entry.
5. **Check for duplicates and conflicts.** Search the target and its neighbours for the same topic. Merge rather than add; resolve contradictions rather than stacking a newer line on an older one.
6. **Check the budget.** Anthropic's memory guide suggests keeping each CLAUDE.md under about 200 lines; Boris Cherny's team CLAUDE.md was about 2.5k tokens. If the file is near its limit, propose removing or moving a line for each one you add. If enforced rules and hooks are piling up, Anthropic's docs suggest most of them are preferences; propose deleting hooks that only encode taste. Removals go in the step-7 diff, never applied directly.
7. **Propose, do not silently commit, shared changes.** Committed instruction files, rules, hooks and settings affect everyone on the repo. Present them as a diff for the user (and, for team files, a reviewer) to approve. Personal files can be edited directly only when the user asked for that specific change in this turn; otherwise propose them too. Before writing, show the exact lines and where they will go in one sentence; after writing, return to the task in progress. Never run `git commit`.
8. **Test the lesson where you can.** Re-run the task or a reduced version in a fresh session or throwaway worktree with the new instruction or check in place, without repeating the original task's state changes, and confirm the original mistake does not recur. For a hook or test, show it failing on the bad case. (The fresh-session re-run is a suggested check, not from the cited sources.)
9. **Escalate repeated misses.** If an instruction-file line keeps being ignored, do not add emphasis; move it to an enforced check (step 3, first row).

## Verification

- Each persisted lesson cites the evidence that triggered it.
- Each lesson lives in exactly one place, chosen by the routing table, with the reason stated.
- No new line duplicates or contradicts an existing one.
- Instruction files stay within budget; the net line change is reported.
- Shared-file changes are presented as a diff awaiting approval, not committed.
- For enforced checks, a run showing the check catching the bad case is attached.

## Gotchas

- **More context is not more success.** Gloaguen et al. (arXiv, Feb 2026) found repository context files generally did not improve task success on SWE-bench-style tasks and raised inference cost by over 20%; repository overviews did not help, and files were mainly useful for non-standard practices. A smaller study (Lulla et al., 2026) found AGENTS.md cut median wall-clock time by about 29% and output tokens by about 17%, without fully evaluating correctness. Read together: keep files short and about non-obvious conventions, not codebase tours.
- **Instruction bloat is a named anti-pattern.** Thoughtworks' Technology Radar (Vol. 34, via a secondary summary) puts "agent instruction bloat" on Caution. Anthropic's docs also retire describing architecture in CLAUDE.md.
- **No measured payoff for the compound loop.** The review of Every's plugin states that no published measurement shows the loop's payoff, and the plugin itself costs about 2,989 always-on tokens. Evaluate it on your own tasks before adopting it team-wide.
- **Retrieval beats always-on for specific lessons.** Every writes solutions to `docs/solutions/` and has later plans retrieve from it. A rare lesson in CLAUDE.md costs tokens on every task to help one.
- **Lessons written in the heat of the moment overfit.** "Never use library X" after one bad call becomes a wrong rule later. State the condition under which the lesson applies. (General advice; not from this library's sources.)
- **Emphasis is not enforcement.** If a line keeps being missed, move it to a hook or test (step 9) instead of capitalising it.
- **"Remember this" may go to auto memory.** In Claude Code, telling Claude to remember something writes to its auto-memory folder, not CLAUDE.md. Say which file you changed.
- **Compaction keeps some files and not others.** Claude Code re-injects the root CLAUDE.md and unscoped rules after compaction, but path-scoped rules and nested files reload only on demand. Put rules that must always hold at the root or unscoped.
- **Fix the process, not the instance.** In Anthropic's migration guidance, a finding that a reviewer repeats is fixed in the rulebook, not file by file. The same applies here: repeated review findings belong in a rule or check.

## Output

Report to the user:

```markdown
## Compound learnings: <task>
| # | Lesson (evidence) | Decision | Target | Change |
|---|---|---|---|---|
| 1 | <mistake, link to diff/output> | persist | hook in .claude/settings.json | diff below, needs approval |
| 2 | <...> | drop: discoverable from code | - | - |
| 3 | <...> | persist | docs/solutions/<slug>.md | new file, needs approval |
Instruction-file budget: CLAUDE.md <before> -> <after> lines
Tested: <fresh-session re-run or check output> | not tested: <reason>
```

Lessons note (`docs/solutions/<slug>.md`):

```markdown
# <Problem in one line>
Tags: <area>, <tool>, <error string>
Date: <date>   Related: <PR/issue>
## Symptoms
<what you see, exact error text for search>
## Root cause
<one paragraph>
## Fix
<what changed, link>
## Prevention
<check, rule or test added, or "none: rare">
## Applies when
<conditions; when this lesson does NOT apply>
```

## Sources

- Every, compound-engineering plugin (`ce-compound` writes learnings to `docs/solutions/`), read Oct 2026: https://github.com/EveryInc/compound-engineering-plugin
- developertoolkit.ai, compound engineering principle page, checked 26 Sep 2026 (retrieved lessons store; about 2,989 always-on tokens; no published measurement of payoff; cites Gloaguen et al.): https://developertoolkit.ai/en/method/principles/compound-engineering/
- Gloaguen, Mündler, Müller, Raychev, Vechev, context files and coding-agent success, arXiv 2602.11988, 12 Feb 2026: https://arxiv.org/abs/2602.11988v1
- Lulla, Treude, Baltes et al., AGENTS.md efficiency study, ICSE JAWs 2026, arXiv 2601.20404 v2, 30 Mar 2026: https://arxiv.org/pdf/2601.20404
- Thoughtworks Technology Radar Vol. 34 (Apr 2026), via secondary digest: https://agentic-ai.readthedocs.io/en/latest/AgenticTechStack/thoughtworks-radar-vol34/
- Anthropic, Claude Code best practices (CLAUDE.md content test, advisory vs enforced, delete preference hooks, obsolete emphasis), read Oct 2026: https://code.claude.com/docs/en/best-practices
- Anthropic, Claude Code memory docs (under 200 lines, rules with `paths:`, CLAUDE.local.md, auto memory), read Oct 2026: https://code.claude.com/docs/en/memory.md
- Anthropic, Claude Code context window docs (what survives compaction), read Oct 2026: https://code.claude.com/docs/en/context-window.md
- Lee Robinson, "Best practices for coding with agents", Cursor, 9 Jan 2026 (rules only after a repeated mistake; no style guides in rules): https://cursor.com/blog/agent-best-practices
- Mitchell Hashimoto, "My AI Adoption Journey", 5 Feb 2026 (harness engineering: mistakes become AGENTS.md fixes or tools): https://mitchellh.com/writing/my-ai-adoption-journey
- InfoQ on Boris Cherny's workflow, 10 Jan 2026 (team CLAUDE.md about 2.5k tokens; learnings added from PRs): https://infoq.com/news/2026/01/claude-code-creator-workflow/
- Thariq Shihipar on skills, 17 Mar 2026, via YouMind mirror (Gotchas as the highest-signal section): https://youmind.com/ar/landing/x-viral-articles/claude-code-skills-guide
- Anthropic, "AI code migration", 16 Jul 2026 (fix the rulebook when a reviewer repeats a finding): https://claude.com/blog/ai-code-migration
