# skills

Personal Agent Skills library, packaged as a Claude Code plugin marketplace owned by `pdcarv`: 6 plugins, 18 skills. README.md covers install, TAXONOMY.md the categories, CONTRIBUTING.md the authoring rules (read it before writing or editing a skill).

## Layout

- `.claude-plugin/marketplace.json`: lists every plugin with `source: ./plugins/<name>`.
- `plugins/<plugin>/.claude-plugin/plugin.json`: name, version, description, license, author. `--strict` validation fails without `author`.
- `plugins/<plugin>/skills/<skill>/SKILL.md`: the folder name must equal the frontmatter `name`.
- `references/` and `scripts/` sit one level under a skill. Per-cloud detail goes in `references/aws.md`, `gcp.md`, `azure.md`, not in SKILL.md.

## Commands

```bash
# validate every plugin and the marketplace
for p in plugins/*; do claude plugin validate --strict "$p"; done
claude plugin validate .claude-plugin/marketplace.json

# lint skills against CONTRIBUTING.md (stdlib only)
python3 scripts/check_skill.py plugins/*/skills/*

# use the library locally
claude plugin marketplace add <path to your clone>
claude plugin install sre@hyperscaler-skills
```

## Rules that are easy to miss

- Frontmatter uses only `name`, `description`, `license`, `metadata`. Tool-specific fields break portability to Cursor and claude.ai.
- Every enabled skill's description is loaded on every turn. Keep descriptions tight and re-check cost with `claude plugin details <plugin>@hyperscaler-skills` after editing them.
- Facts need a public source with its date in the skill's Sources section. Mark anything you could not confirm `unverified`. Never state a cloud quota or default as fixed: give the value seen, its doc date, and "check the current value".
- Actions that change production are written as proposals for a human to approve.
- When adding or renaming a skill, update TAXONOMY.md and the README.md table in the same change.
