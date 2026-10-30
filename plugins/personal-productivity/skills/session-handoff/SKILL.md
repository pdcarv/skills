---
name: session-handoff
description: >-
  Writes a standalone handoff file that lets a fresh agent session, another agent or a
  person continue the work without the original conversation: goal and done-condition,
  current state (branch, commits, uncommitted changes), decisions with reasons, what was
  tried and failed, open questions, next steps, and verification status with the exact
  commands and results. Leaves the repository in a clean, resumable state and tests the
  file with a fresh reader. Use when the context is getting long or polluted, after two
  failed corrections, before ending, pausing or switching sessions, when moving work to
  another machine, cloud session or teammate, or when asked to hand off, write a
  handoff, save progress or summarise state for later.
license: MIT
metadata:
  category: "personal-productivity/knowledge"
  sources: "see Sources section"
---

# Session handoff

A long session holds state that disappears when it ends: why a path was chosen, what was already tried, which tests were actually run. Compaction keeps some of it but, in Anthropic's own harness experiments, does not always pass clear instructions to the next session. A handoff file puts that state on disk, where a fresh session or a teammate can pick it up. The community `handoff` skills (Matt Pocock; Every's `ce-handoff`) write one standalone document with goal, state, decisions, files touched, open questions and next steps; Anthropic's long-running-agent harnesses add a progress log, clean commits and a start-of-session check. This skill combines them.

## When to use

- The session is long, drifting, or has had two failed corrections. Anthropic's guidance is to start fresh rather than make a third correction; the handoff carries what was learned.
- Pausing work overnight or across days, or before the session ends.
- Moving work to another machine, a cloud session, another agent or a teammate.
- Switching to a different task in the same repo.
- Forking or parking a non-code thread (planning, research, a personal decision) to continue on a clean context.

## When not to use

- Handing off incident command during an outage: use `incident-command` (oncall-incident), which needs a live briefing and explicit acknowledgment.
- Recording a lesson that should change future behaviour on every task: use `compound-learnings`.

## Inputs to gather

- The original request, spec or issue, in the user's words if possible.
- Repository state: current branch, recent commits, uncommitted and untracked files, stashes, worktrees.
- What was run to verify the work so far, with the outputs actually seen in this session.
- Decisions made and alternatives rejected, from the conversation.
- Where the handoff goes. For a fresh session on the same machine, outside the repository (for example `/tmp/handoffs/`), since a handoff is session glue, not a record. For another machine, a cloud session or a teammate, the project's handoff folder or a file sent to them. Also where the project keeps plans and progress logs.
- Who receives it (fresh agent session, a named person) and whether they have the same access.

## Procedure

**First, put anything durable in its home.** Decisions, research findings, plan or spec updates and lessons belong in the plan, research note, ADR or rules file, written before the handoff (or name the skill that writes them). The handoff carries only what the next session needs to continue.

1. **State the goal and the done-condition.** One paragraph for the goal; then the check that proves it is done, as a command or observable result where possible. If none exists, say so; it is the first open question.
2. **Capture the repository state.** Branch, last commit, uncommitted changes and untracked files, other worktrees or stashes. Never commit; commits are the user's. List work in progress so the next session can reconcile it. Never discard changes to get a clean tree; list them instead.
3. **Record the verification status honestly.** For each check: the exact command, when it was run, and the result seen (pass, fail with the key error line, or not run). Mark anything claimed earlier in the session but not re-run since the last edit as unverified.
4. **List decisions with reasons.** Each decision, the alternative rejected and why. Include constraints the user stated in conversation that are not written anywhere else.
5. **List what was tried and failed.** The approach, how it failed, and the evidence. Anthropic and Cursor advise resetting rather than piling up corrections; Armin Ronacher keeps failed attempts in context so the model does not repeat them. A short "tried and failed" section gives the reset both benefits.
6. **List open questions.** Unknowns, blocked items and questions only the user can answer, each with who can answer it.
7. **Write the next steps.** Ordered, small, each with the file or area and how to check it worked. The first step should be doable without reading anything but this file and the files it names.
8. **Point to files, do not paste them.** List files touched or important to read, with one line each on why. Link the spec, plan or issue rather than copying them.
9. **Add a start-of-session check.** Tell the next reader what to run first to confirm the state matches the handoff (for example the test command or a smoke test). Anthropic's harness starts each session with a smoke test to catch breakage left by earlier sessions.
10. **Save the file** in the place chosen above, with project, slug and date in the name, and tell the user the path. Writing the handoff changes nothing else: no plan, spec or committed file is edited as part of it. Do not include secrets, tokens, credentials, or content from folders the user marks private; reference where they live instead.
11. **Test it with a fresh reader.** If you can start a fresh session or a subagent with no access to this conversation, give it only the handoff file and ask it to state the goal, the done-condition and the first next step. Fix any gap it reveals. (This check is a suggested practice, not from the cited sources.)

### Non-code handoffs

For planning, research or a personal thread with no repository: skip steps 2, 3 and 9. Record "Conclusions so far" (settled points not to re-litigate) and "Ruled out" (options abandoned, with why) in place of Decisions and Tried and failed, and list pointers to notes and links in place of files. Several fresh sessions may start from the same file to fork the thread.

## Verification

- A reader with only the file and the repository can state the goal, the done-condition and the first next step.
- Every verification line has a command and a result or "not run"; nothing is described as passing without an observed run.
- Repository state in the file matches the repository now (branch, last commit, list of uncommitted files).
- Decisions and failed attempts each carry a reason or evidence.
- No secrets in the file.
- Durable conclusions were saved to their home first, and writing the handoff changed no other file.
- For a human recipient: the user has confirmed who receives it, and the recipient has acknowledged it.

## Gotchas

- **Relying on compaction.** Automatic compaction preserves continuity but not necessarily the instructions the next session needs. When the work will continue in a new context, write the handoff before the context is lost.
- **"Tests pass" without a run.** A handoff that repeats an earlier claim spreads it to the next session. Step 3 asks for the command and output, or "not run".
- **Pasting instead of pointing.** A handoff that copies the spec and diffs becomes as long as the context it replaces. Link files; summarise only decisions and state.
- **Missing the "why".** The next session can read the code but not the reasoning. Decisions without reasons get re-litigated or silently reversed.
- **Dirty or half-applied state.** Uncommitted edits on a different machine or worktree are invisible to the recipient. List them in the handoff file.
- **Model-specific habits.** Anthropic reports that one model generation wrapped up early near its perceived context limit ("context anxiety") and needed resets, while later generations ran long sessions with compaction. Decide whether to reset on the evidence of drift, not on habit.
- **Handoff to a person is not a file drop.** For a teammate, send the file and confirm they have read it and have the needed access; incident handoffs in particular need explicit acknowledgment.
- **Tool features are optional extras.** Claude Code can resume a session linked to a PR (`claude --from-pr <number>`) or move a cloud session to the terminal (`--teleport`); Cursor can pull earlier chats into context with `@Chats`. These help, but a plain file works in every tool and for people.

## Output

Save as `<handoff dir>/<YYYY-MM-DD>-<slug>.md`:

```markdown
# Handoff: <task>
Date: <date>   From: <session/person>   To: <fresh session | name>
Pick up with: <skill to run first, e.g. red-green-tdd, systematic-debugging, research, or none>

## Goal
<one paragraph>
Done when: <command or observable result> | unknown (see open questions)

## State
Branch: <branch>   Last commit: <sha> <first line>
Uncommitted: <files, or "none">   Other worktrees/stashes: <...>

## Verification status
| Check | Command | Last run | Result |
|---|---|---|---|
| unit tests | <cmd> | <time, after last edit?> | pass / fail: <key line> / not run |

## Decisions
- <decision> - chosen over <alternative> because <reason>

## Tried and failed
- <approach> - failed because <evidence>

## Open questions
- <question> - who can answer: <user/name>

## Next steps
1. <step> - in <file/area> - check: <how to know it worked>

## Files to read
- <path> - <why>

## Start here
Run <command>; expect <result>. If it differs, stop and reconcile before continuing.
```

## Sources

- Matt Pocock, `mattpocock/skills` `handoff` skill (aggregator listing; standalone handoff document), read Oct 2026: https://skills.sh
- Every, compound-engineering plugin, `ce-handoff` skill, read Oct 2026: https://github.com/EveryInc/compound-engineering-plugin
- Anthropic Engineering, effective harnesses for long-running agents post, 26 Nov 2025 (compaction alone insufficient; progress log, clean-state commits, start-of-session smoke test): https://anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Anthropic Engineering, harness design for long-running apps post, 24 Mar 2026 (compaction vs reset trade-off; reset needs a detailed handoff artifact; context anxiety varies by model): https://anthropic.com/engineering/harness-design-long-running-apps
- Anthropic, Claude Code best practices (start fresh after two failed corrections), read Oct 2026: https://code.claude.com/docs/en/best-practices
- Anthropic, Claude Code common workflows (`--from-pr` resumes the linked session), read Oct 2026: https://code.claude.com/docs/en/common-workflows.md
- Anthropic, Claude Code on the web (`--teleport`), read Oct 2026: https://code.claude.com/docs/en/claude-code-on-the-web.md
- Lee Robinson, "Best practices for coding with agents", Cursor, 9 Jan 2026 (when to start a new chat; `@Chats`): https://cursor.com/blog/agent-best-practices
- Armin Ronacher, "A Year of Vibes", 22 Dec 2025 (keep failed attempts so models do not repeat them): https://lucumr.pocoo.org/2025/12/22/a-year-of-vibes/
- Google SRE Book, "Managing Incidents" (live handoff with explicit acknowledgment): https://sre.google/sre-book/incident-response/
