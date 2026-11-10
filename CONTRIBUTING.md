# Authoring rules for this library

Every skill in this repo follows these rules so it loads in Claude Code, Cursor and other Agent Skills tools without edits.

## Layout

```text
plugins/<plugin>/skills/<skill-name>/
  SKILL.md              # required
  references/*.md       # optional, one level deep, loaded on demand
  scripts/*             # optional, only for steps that must run the same way every time
```

### Domain plugins (`training`, `investing`)

Skills in these plugins are stateful and self-contained, so two layout rules relax:

- Extra folders are allowed, for example `roles/` (reasoning stances) and `state/`.
- The body section order below is not required. Frontmatter and portability rules still apply, and `scripts/check_skill.py` skips only the section check for these plugins.

Personal data never enters git. `state/` is a link to a private folder outside the repository, chosen by each user, and is listed in `.gitignore`. Development-only files (test suites, fixtures) live in `plugins/<plugin>/tests/<skill>/`, outside the skill folder.

## Frontmatter (portable subset of the Agent Skills spec only)

```yaml
---
name: skill-name          # 1-64 chars, lowercase letters, digits, hyphens; must equal the folder name
description: >-           # <= 1024 chars, third person: what it does AND when to use it, with trigger words
  ...
license: MIT
metadata:
  category: "<plugin>/<subcategory>"
  sources: "see Sources section"
---
```

- Do not use tool-specific fields (`context`, `paths`, `disable-model-invocation`, `allowed-tools`). The spec validator rejects some of them, and claude.ai uploads accept only spec fields.
- Names never contain "claude" or "anthropic".

## Body structure (keep SKILL.md under 500 lines; aim for 60-200)

1. `# Title` and a one-paragraph purpose.
2. `## When to use` / `## When not to use` (short bullets).
3. `## Inputs to gather` (what to ask or look up before starting).
4. `## Procedure` (numbered steps; imperative; each step says what evidence to collect).
5. `## Verification` (how the agent proves the output is right before saying done).
6. `## Gotchas` (the non-obvious failure modes experts know; this section carries the most value).
7. `## Output` (the exact shape of what to hand back: template or checklist).
8. `## Sources` (links to the public primary sources the procedure is based on, with dates).

## Content rules

- Every factual claim, command, query or number must trace to a public primary source listed, with its date, in the skill's Sources section. If you could not confirm a command, label it `# unverified` in the skill or leave it out.
- Numeric cloud limits change. Never state one as a rule. Write "check the current value in <doc>" and, if useful, give the value seen with its doc date as an example.
- Safety: investigation is read-only first. Any command that changes production state (deploy, rollback, delete, scale, IAM change, purge) is presented as a proposal for a human to approve, never run by default.
- Side effects outside production follow the same rule. A skill never tells the agent to:
  - run git writes: commit, push, merge, rebase, tag, stage (`git add`), stash, reset, `checkout --`, `clean`, branch deletion;
  - post, send, publish, comment, approve, page or file a ticket;
  - turn off permission prompts (`--permission-mode dontAsk`, `--dangerously-skip-permissions`) for an unattended run the user has not approved.

  Write these as drafts, proposed commands or a plan for the user to run or approve. Running the project's tests, linters, type checks and builds is expected. When a check needs a temporary change (a proposed fix, a bisect patch), make it in a throwaway `git worktree`, never in the user's tree.
- Writes beyond the deliverable the user asked for are confirmed first. That covers files in the user's repo or home folder, agent instruction files (CLAUDE.md, AGENTS.md, rules, settings, hooks, memory) and private `state/`. Name the path and play back what will be written.
- State side effects up front. Each SKILL.md has a `**Side effects:**` line right after the purpose paragraph. It says what the skill writes and where, which external services it reads (web search, cloud or monitoring CLIs, connectors, package downloads, other models), and what it never does. `scripts/check_skill.py` fails a skill without it, and warns on side-effect commands with no gate word on the same line.
- No quotes longer than 15 words; at most one per source. Paraphrase templates.
- Public sources only. Never present anything as internal or confidential knowledge.
- Write for an expert agent: skip what the model already knows; spend words on procedure, decision points and gotchas.
