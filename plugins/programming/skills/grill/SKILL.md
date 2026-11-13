---
name: grill
description: >-
  Interviews the user in rounds of multiple-choice questions until the requirements are
  unambiguous, then writes SPEC.md with goals, non-goals and acceptance criteria written as
  checks an agent can run. Use when the user proposes a feature, refactor or plan before code
  is written, the request is vague or has several reasonable readings, the user says "grill
  me", "interview me" or "write a spec", or before starting a long or background agent run.
license: MIT
metadata:
  category: "programming/planning"
  sources: "see Sources section"
---

# Grill

Interview the user relentlessly until you reach a shared understanding, then record it in SPEC.md as acceptance criteria.

**Side effects:** writes SPEC.md (or the path the user names); never commits, pushes or posts.

## When to use

- A new feature, behaviour change or refactor is proposed and no code exists yet.
- The request has more than one reasonable reading, or misses error, empty or edge cases.
- The work will be built in a fresh session, by another agent, or unattended.

## When not to use

- Small or familiar changes with one obvious approach: restate the goal and done-check in one or two lines in chat and proceed.

## Inputs to gather

Whatever the user has already given you, in the conversation or in material they point to. Anything else you can look up is found during the walk, when a node needs it.

## Procedure

Walk the decision tree breadth-first, one frontier per round, until the frontier is empty.

1. **Start at the root: the premise.** Is this the right problem, and would a smaller change do?
2. **Walk the frontier.** The frontier is every open node that does not depend on an unsettled answer. The premise blocks only the nodes that depend on it, so the first round asks the premise together with everything else you can already ask. At each frontier node, decide what it needs:
   - **A fact**, anything you could look up instead of asking: find it yourself, with a sub-agent in a fresh context for anything beyond a quick read; never ask the user. Only that node's descendants wait for the answer.
   - **A decision**: put it to the user this round, with concrete options, your recommended option with a one-line reason, and "other".
3. **Expand.** After each round, play back the decisions in two or three lines, then expand each settled node: ask what it leaves open, including anything the user may want to forbid, cap or phase in, and add those questions as its children. Return to step 2.
4. **Stop when the frontier is empty.** Every branch visited, nothing silently assumed. Anything the user cannot answer goes under Open questions with an owner.
5. **Write SPEC.md** following Output.
6. **For unattended or handed-off work**, also state what the agent may touch, what stops it (turn or budget cap), and where the result goes.
7. **Get explicit approval**, then build from SPEC.md in a fresh session and review against it. If a decision changes during the build, edit SPEC.md in place.

## Output

SPEC.md is read by the people who approve the change and by the agent that builds it. Write it for someone who was not in the interview.

- **Plain prose first.** Short paragraphs and lists; a table only to compare options.
- **Reading order:** what changes and why; goals and non-goals; terms; behaviour; acceptance checks; open questions.
- **Terms.** For each word the user used for a concept specific to this project, give one or two sentences in their words saying what it is, not what it does, and list the words to avoid. Use each term the same way everywhere else. Leave out general programming concepts.
- **Behaviour.** One statement per case the interview settled, concrete enough to test: the situation, and what happens. Include error and empty cases.
- **Decisions keep their reason:** what was chosen over what, and why, in one sentence.
- **Acceptance checks.** Write each as "When ..., then ...", followed by the command or test that proves it, or "manual:" with the evidence that proves it.
- **Pattern to follow:** name an existing file the builder should copy, if one exists.
- **Build order**, only if the work has several steps: each step with the check that proves it.
- **Open questions** name who answers them.

## Sources

- Anthropic, Claude Code best practices (interview until a spec can be written; build in a fresh session; review against the same spec), read Oct 2026: https://code.claude.com/docs/en/best-practices
- Matt Pocock, `grilling` skill (design tree, rounds of questions on the frontier, recommended answers), read Nov 2026: https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md
- Malte Ubl, "Design Docs at Google" (goals and non-goals; update the doc when the design changes), 6 Jul 2020: https://www.industrialempathy.com/posts/design-docs-at-google/
