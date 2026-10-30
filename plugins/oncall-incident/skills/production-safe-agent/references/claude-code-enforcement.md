# Claude Code enforcement for production-safe agents (optional)

Load this only when the agent runs in Claude Code. It shows how to turn the rules in SKILL.md into harness-enforced controls. Everything here comes from the Claude Code docs as read on 2026-10-27; behaviour and version numbers change, so check the current docs (links at the end) before relying on any of it. Placeholders in angle brackets (`<prod-cli>`, `<prod-ops-server>`) must be replaced with your real tool names. Scripts marked `# unverified` are adaptations of documented patterns, not copies of official examples; test them before use.

## Contents

1. Why enforce
2. Permission rules
3. Permission modes
4. PreToolUse hooks
5. Sandbox
6. Managed settings
7. Checking what is active
8. Limits to remember

## 1. Why enforce

Anthropic's best-practices page separates advisory instructions (prompts, CLAUDE.md, skills) from controls the harness enforces (hooks, deny rules, managed settings). A rule that must never be broken, such as "no destructive production action without approval", belongs in the enforced layer. Keep the enforced set small; the docs suggest that a very long list of hooks and rules is mostly preferences.

## 2. Permission rules

- Rules live under `permissions.allow`, `permissions.ask` and `permissions.deny` in settings files. Evaluation order is deny, then ask, then allow; the first match wins regardless of how specific a rule is.
- Syntax: `Tool` or `Tool(specifier)`. Documented forms include `Bash(npm run *)`, `Read(./.env)`, `WebFetch(domain:example.com)`, `mcp__server__*` and `mcp__server__tool`.
- A bare tool-name deny such as `Bash` removes the tool from Claude's context entirely.
- Put the `*` after the subcommand: `Bash(git * main)` matches every git subcommand, including `-c`. Rules match command text, so test each rule against the command forms your team actually types (for example with global flags before the subcommand).
- Allow globs on MCP tools must be anchored to a literal `mcp__<server>__` prefix.
- `deny` and `ask` rules in project settings apply immediately; `allow` rules wait until the folder is trusted.
- Built-in read-only Bash commands (`ls`, `cat`, `grep`, `find`, read-only git and others) never prompt, and that set is not configurable.

Pattern for a production-capable session (adapt names; the structure follows the documented team settings example):

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "ask": [
      "mcp__<prod-ops-server>__*",
      "Bash(<prod-cli> <mutating-subcommand> *)",
      "Bash(git push *)"
    ],
    "deny": [
      "mcp__<prod-ops-server>__<destructive-tool>",
      "Bash(<prod-cli> <destructive-subcommand> *)",
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./secrets/**)"
    ]
  }
}
```

Map the SKILL.md labels: destructive tools in `deny` (a human runs them outside the agent, or a dedicated approved workflow does), reversible and safe tools in `ask` so each call prompts, read-only tools in `allow` only when they truly cannot change state.

## 3. Permission modes

| Mode | Use for production work |
|---|---|
| `plan` | Read-only exploration until a plan is approved. Good default for investigation. |
| `default` (Manual) | Prompts on first use of each tool. |
| `acceptEdits` | Auto-accepts file edits and simple file commands in the working directories; no effect on production tools beyond that. |
| `auto` | A background classifier reviews actions; it drops broad allow rules such as `Bash(*)` on entry and falls back to prompting after 3 consecutive or 20 total blocks. The docs say it does not guarantee safety. |
| `dontAsk` | Auto-denies anything that would prompt; meant for CI with explicit allowed tools. |
| `bypassPermissions` | Skips prompts. The docs position it for disposable containers only. Never with production credentials. |

Deny rules hold in every mode. Admins can set `disableBypassPermissionsMode` and `disableAutoMode` to `"disable"` in managed settings. `auto` and `bypassPermissions` as `permissions.defaultMode` are ignored in project and local settings.

## 4. PreToolUse hooks

- Hooks are configured as event, then matcher group, then handlers. Matchers take an exact tool name, a `|` list such as `Edit|Write`, or a regex such as `mcp__memory__.*`. The optional `if` field takes permission-rule syntax.
- Exit code 2 blocks the call and feeds stderr back to Claude. Exit code 1 is non-blocking, a common mistake for policy hooks. A JSON object on stdout with `hookSpecificOutput.permissionDecision` set to `allow`, `deny`, `ask` or `defer` gives structured control.
- `"onFailure": "block"` makes hook failures and timeouts block (v2.1.295+ per the docs read).
- Hooks run outside the sandbox.

Documented shape (from the team settings example):

```json
{"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh"}]}]}}
```

The docs' destructive-command example prints this when the command contains `rm -rf`:

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"..."}}
```

Adapted guard for production commands (`# unverified`: built from the documented stdin fields `tool_name` and `tool_input` and the JSON decision above; extend the pattern list for your tools):

```bash
#!/usr/bin/env bash
# unverified: adaptation of the documented PreToolUse deny pattern
input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')
if printf '%s' "$cmd" | grep -Eq '<prod-cli> (<destructive-subcommand>|<other-subcommand>)'; then
  printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Destructive production command: propose it for human execution instead."}}'
  exit 0
fi
exit 0
```

Adapted audit-log hook (`# unverified`): Anthropic reports logging skill usage with a PreToolUse hook; the same event can append every production tool call to an audit file.

```json
{"hooks":{"PreToolUse":[{"matcher":"Bash|mcp__<prod-ops-server>__.*","hooks":[{"type":"command","command":"${CLAUDE_PROJECT_DIR}/.claude/hooks/audit-log.sh"}]}]}}
```

```bash
#!/usr/bin/env bash
# unverified: appends the hook's stdin JSON (session_id, tool_name, tool_input, ...) to an audit log
jq -c '{ts: (now|todate), session: .session_id, tool: .tool_name, input: .tool_input}' >> "${CLAUDE_PROJECT_DIR}/.claude/audit/tool-calls.jsonl"
exit 0
```

A PreToolUse log records what was attempted, not whether it was approved or succeeded; keep the human-readable audit entries from SKILL.md as well.

## 5. Sandbox

- Enable with `/sandbox` or `sandbox.enabled: true`. Linux and WSL2 need `bubblewrap` and `socat`; macOS uses Seatbelt; native Windows is not sandboxed. Set `sandbox.failIfUnavailable: true` so startup fails instead of silently running unsandboxed.
- Coverage: Bash, PowerShell and Monitor commands and their children. Not covered: file tools, MCP servers and hooks. Production MCP tools therefore need permission rules, not the sandbox.
- Network goes through a local proxy with a domain allowlist (`sandbox.network.allowedDomains`). Tools that are not proxy-aware, such as plain `ssh` and database drivers, cannot connect. The metadata IP 169.254.169.254 is refused by default.
- Reads are allowed across most of the machine (including `~/.ssh`) unless restricted with `filesystem.denyRead`. `sandbox.credentials` can mask secrets.
- Managed hardening: `allowUnsandboxedCommands: false`, `allowManagedDomainsOnly`.

## 6. Managed settings

- File-based managed settings: `/etc/claude-code/managed-settings.json` on Linux and WSL, `/Library/Application Support/ClaudeCode/managed-settings.json` on macOS, `C:\Program Files\ClaudeCode\managed-settings.json` on Windows, plus optional `managed-settings.d/*.json` drop-ins whose `permissions.deny` lists are unioned.
- `allowManagedPermissionRulesOnly` and `allowManagedHooksOnly` stop users and projects from weakening the rules.
- Cloud sessions in Anthropic-hosted environments read only server-managed settings, not a device's managed file.
- A managed file that is not valid JSON makes Claude Code refuse to start; validate before deploying.

Documented minimal managed example:

```json
{"permissions":{"deny":["Read(./.env)","Read(./secrets/**)"],"disableBypassPermissionsMode":"disable"},
 "allowManagedPermissionRulesOnly":true}
```

## 7. Checking what is active

- `/status` shows the setting sources in effect.
- `/permissions` manages and lists rules; `/hooks` is a read-only browser of configured hooks.
- `claude doctor` lists rejected settings entries.

## 8. Limits to remember

- Denying `WebFetch` does not stop `curl` through Bash; the sandbox network allowlist closes that gap.
- Checkpoints and `/rewind` do not cover files changed by Bash, and never cover remote production state.
- `disableAllHooks: true` turns hooks off but does not override managed hooks.

## Sources

- Claude Code docs, read 2026-10-27: Settings https://code.claude.com/docs/en/settings.md ; Permissions https://code.claude.com/docs/en/permissions ; Permission modes https://code.claude.com/docs/en/permission-modes.md ; Hooks reference https://code.claude.com/docs/en/hooks ; Hooks guide https://code.claude.com/docs/en/hooks-guide.md ; Sandboxing https://code.claude.com/docs/en/sandboxing ; Example settings files https://code.claude.com/docs/en/settings-example.md ; Deploy managed settings https://code.claude.com/docs/en/managed-settings.md ; Admin setup https://code.claude.com/docs/en/admin-setup.md ; Best practices https://code.claude.com/docs/en/best-practices
- Thariq Shihipar on Claude Code skills (PreToolUse logging hook), 17 Mar 2026, via YouMind mirror. https://youmind.com/ar/landing/x-viral-articles/claude-code-skills-guide
