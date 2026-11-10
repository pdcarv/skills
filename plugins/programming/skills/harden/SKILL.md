---
name: harden
description: >-
  Hardens a finished change before it ships: runs every formatter, linter, type checker and
  analyzer the project has, plus dependency and security scanners, then fans out
  fresh-context pen-test agents over the change's attack surface (OWASP-based lenses) and
  repeated independent review passes for nil and null cases, pointer and ownership errors,
  logic and boundary errors, error paths and concurrency. Every finding needs a reproduction
  before it is reported; verified findings are fixed with a regression test each. Works only
  on the local checkout, never against deployed systems. Use when a change is about to
  be merged or released, when asked to harden, security-review, pen-test, audit or "find what's wrong with" a
  change, or as phase 5 of deliver.
license: MIT
metadata:
  category: "programming/quality"
  sources: "see Sources section"
---

# Harden

Find what is still wrong with a change while it is cheap to fix. Three layers, cheapest first: the tools the project already trusts, then pen-test agents that attack the change, then review agents that read it for defects. Agents asked to find problems report some whether or not they exist, so nothing is reported until it is reproduced; and because one pass misses things, review runs in rounds until a round finds nothing new.

**Side effects:** runs the project's linters, analyzers, tests and scanners; spawns subagents with read access to the repository; exploit and reproduction attempts run against a local build only, in a scratch copy of the working tree (a `git worktree` would check out HEAD and miss the uncommitted change) that is removed afterwards. Formatter and lint fixes in the changed code are applied, since they enforce the project's own rules, and listed in the report; every other fix goes into the user's tree only for findings the user approved. Installs a scanner only after the user approves. Never targets a deployed or third-party system, never stages, commits or pushes.

## When to use

- A change is implemented and tested, before merge or release.
- The user asks to harden, security-review, pen-test or audit a change.
- Phase 5 of `deliver`.

## When not to use

- Reviewing someone else's PR to approve or reject it: `review` (it has the verdict and comment etiquette; this skill reuses its verification rule).
- Timeouts, retries and overload on remote calls: `resilience`, then come back.
- Testing a live system you do not own or have no written permission to test: out of scope.

## Inputs to gather

- The change: `git diff HEAD` plus the new files from `git status --porcelain --untracked-files=all` (nothing is staged, so new files never show in the diff and would drop out of the attack surface). Also the SPEC.md or ticket, the test command with a green baseline, and the style brief from `deliver` for fix-up agents (standalone: write one from the repo's style guide).
- Every quality tool the project configures: CI workflow files, Makefile, pre-commit config, package scripts, `pyproject.toml`, `.golangci.yml`, `eslint` config. These are the commands to run, with the project's settings.
- Scanners available per language (`references/scanners.md`).
- The attack surface of the change: entry points (HTTP handlers, CLI args, message consumers, file and env inputs), trust boundaries crossed, data stored or returned, auth checks involved, new dependencies.

## Procedure

1. **Project tools first.** Run every formatter, linter, type checker and analyzer the project configures, with its own settings. Fix findings in the changed code through a fresh implementer agent with the style brief. Report pre-existing findings outside the change; do not fix them in this change. Never edit tool config or add ignore comments to make a finding go away.
2. **Scanners.** Check which scanners are already available (`command -v`, `--version`, the project's virtualenv) before proposing any. Run the dependency and static security scanners the project has. Propose the standard ones for the language that it lacks (`references/scanners.md`) and run them only on approval.
3. **Map the attack surface** (Inputs) and choose the pen-test lenses that apply. The lens list and what each checks is in `references/security.md`; skip lenses with nothing to attack and say why. Running in a fresh session does not shrink the surface: start from every lens in the list and every review lens in step 5, and name each skipped one with its reason in the report.
4. **Pen-test agents in parallel**, one lens each, fresh context. Give each: the diff, the attack-surface map, its lens and checklist, the local run and test commands, and the rule that every finding needs a reproduction (a failing test, a request and response against the local build, or an input trace to the exact line). They work only in a scratch copy of the working tree (`cp -R` or `rsync` to a temp directory), so exploits and payloads never land in the user's tree.
5. **Review agents in parallel**, fresh context, one lens each: (a) nil, null, None, empty and zero values; pointers, references, ownership and lifetimes; (b) logic: conditions, boundaries, off-by-one, ordering, units, state transitions; (c) error paths: every error checked, propagated with context, resources released, partial failure leaves consistent state; (d) concurrency: shared state, races, deadlocks, idempotency on retry; (e) the spec: every acceptance check met, nothing extra. Give each the diff, SPEC.md and its lens, and ask for an exhaustive list with file:line and a reproduction.
6. **Verify every finding** before it counts, yours and the agents' (as in `review`): give the merged list to a fresh verifier agent (`deliver`'s `references/briefs.md`, or a brief with the same rules), which reproduces each one with a failing test or trace in a scratch copy and returns confirmed or not reproduced, with the evidence. Re-run a reproduction yourself only when the verdict is unclear. Merge duplicates. Drop what you cannot reproduce, or keep it as a question. Record the agent that found it, so repeat findings across agents are visible.
7. **Run another round** of steps 4-6 with new agents, told which findings already exist so they look elsewhere. Run at least two rounds. Stop when a round adds no new verified finding, or after three rounds; report which.
8. **Present verified findings** with severity (`references/security.md` has one scale for security and one for correctness) and a proposed fix each. On approval, fresh implementer agents fix them, each with a regression test that failed before the fix. Re-run the suite, linters and scanners.

## Verification

- Every project tool ran: command and result listed; zero new findings in changed code, or each one explained.
- Each reported finding has a reproduction that failed before its fix and passes after.
- Dropped findings are listed with the reason (not reproducible, out of scope, by design).
- The round log: findings per round, and why the rounds stopped.
- At least two rounds ran. Scratch copies removed; suite green against the baseline; nothing staged or committed.

## Gotchas

- **Unverified findings.** LLM reviewers over-report; in one 2026 study richer review prompts made false rejections worse. Running the reproduction is the filter.
- **One pass, one model, one lens.** A single reviewer misses whole classes of defects. Several independent lenses and rounds, merged and verified, find more and keep false positives out.
- **Silencing instead of fixing.** Adding `# noqa`, `//nolint`, `@SuppressWarnings` or loosening config makes the tool pass and hides the defect.
- **Pen-testing the wrong target.** Exploits run against the local build only. A test against production or a third-party service is out of scope even if credentials are present.
- **Exploit code left behind.** Exploit tests and payload files stay in the scratch copy; regression tests in the real tree assert the safe behaviour, not the attack.
- **Fixing pre-existing problems inside the change.** It mixes concerns and makes the change hard to review. Report them as follow-ups.
- **Severity inflation.** Rate by what an attacker can actually do through this change's entry points, not by the worst case of the bug class.

## Output

```markdown
## Hardening: <change>
Project tools: `<cmd>` -> <result>; ...
Scanners: `<cmd>` -> <result>; proposed but not run: <list>
Attack surface: <entry points and trust boundaries>
Lenses run: pen-test <list>; review <list>; rounds <n> (stopped because <no new findings | cap>)

| # | Severity | Lens | file:line | Finding | Reproduction | Proposed fix | Status |
|---|---|---|---|---|---|---|---|

Dropped: <finding - reason>
Pre-existing, not fixed here: <list>
After fixes: suite <p/f/s>; tools clean: <yes / list>
```

## Sources

- OWASP Top 10:2025 (A01 Broken Access Control ... A10 Mishandling of Exceptional Conditions); release candidate 6 Nov 2025, final release date unverified: https://owasp.org/Top10/2025/
- OWASP Top 10 for LLM Applications 2025, read Nov 2026: https://genai.owasp.org/llmrisk/LLM10/
- OWASP ASVS 5.0.0 (latest stable; May 2025 per a secondary source), read Nov 2026: https://owasp.org/www-project-ASVS/
- OWASP Web Security Testing Guide v4.2 (3 Dec 2020; v5 in development): https://owasp.org/www-project-web-security-testing-guide/
- MITRE CWE Top 25 (2025 list, page updated 29 Jan 2026): https://cwe.mitre.org/top25/
- Semgrep CLI reference, read Nov 2026: https://semgrep.dev/docs/cli-reference
- npm audit docs (v11), read Nov 2026: https://docs.npmjs.com/cli/v11/commands/npm-audit/
- pip-audit (PyPA), v2.10, read Nov 2026: https://github.com/pypa/pip-audit
- govulncheck v1.9.0, 11 Oct 2026: https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck
- cargo-audit 0.22.2, 5 Jun 2026: https://github.com/rustsec/rustsec/tree/main/cargo-audit
- Jin & Chen, LLM-as-reviewer overcorrection (richer review prompts raised false rejections; executing the proposed fix cut them), arXiv 2603.00539, 28 Feb 2026: https://arxiv.org/pdf/2603.00539
- Cursor, "Building a better Bugbot" (several review passes with voting, then a validator), 15 Jan 2026: https://cursor.com/blog/building-bugbot
- Anthropic, Claude Code best practices (fresh-context reviewer; reviewers asked for gaps usually report some), read Oct 2026: https://code.claude.com/docs/en/best-practices
