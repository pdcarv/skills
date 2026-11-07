# hyperscaler-skills

Every skill uses only the portable Agent Skills frontmatter (`name`, `description`, `license`, `metadata`), so the same folders load in Claude Code, Cursor and other tools that read `SKILL.md`.

| Plugin | Skills |
|---|---|
| `documentation` | design-doc, adr, memo, runbook, brag, learnings |
| `programming` | grill, tdd, review, migrate, resilience, research, handoff |
| `debugging-performance` | diagnose |
| `sre` | create-slo, team-toil |
| `training` | cycling |
| `investing` | valuation |

See `TAXONOMY.md` for subcategories and `CONTRIBUTING.md` for the authoring rules.

## Install

**Claude Code** (from a local clone or a Git host):

```bash
claude plugin marketplace add ./hyperscaler-skills        # or <owner>/<repo> once pushed
claude plugin install sre@hyperscaler-skills  # repeat per plugin you want
```

Enable only the plugins you need: every enabled skill's name and description sits in context on every turn.

**Cursor**: Cursor loads skills from `.claude/skills/` as well as `.cursor/skills/` and `.agents/skills/`. Copy the skill folders you want into one of those directories in your repo (or `~/.cursor/skills/` for all projects). Cursor 2.5+ can also install plugins with `/add-plugin`.

```bash
mkdir -p .claude/skills
cp -r hyperscaler-skills/plugins/sre/skills/* .claude/skills/
```

## Ground rules baked into every skill

- **Public sources only.** Each skill ends with its sources and their dates.
- **Read-only first.** Any action that changes production is written as a proposal for a human to approve.
- **No hard-coded cloud limits.** Quotas, defaults and prices change, so skills give the value seen with its doc date and tell the agent to check the current one.
- **Unverified means labelled.** Commands or facts the research could not confirm carry an `unverified` label.

## Validate

```bash
for p in plugins/*; do claude plugin validate --strict "$p"; done
claude plugin validate .claude-plugin/marketplace.json
```
