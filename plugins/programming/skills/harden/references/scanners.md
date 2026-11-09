# Scanners by language

Run what the project already configures first. Propose any scanner below that the project does not have, and run it only after the user approves (installing a tool changes their environment). Versions are those seen in Nov 2026; check the current docs.

| Language | Dependency vulnerabilities | Static security analysis |
|---|---|---|
| Python | `pip-audit` (or `pip-audit -r requirements.txt`; `-s osv` uses the OSV database) | `bandit -r <path>` |
| Go | `govulncheck ./...` (reports only vulnerable code the program can reach; may still give false positives) | `gosec ./...` |
| JS / TS | `npm audit` (`--audit-level=<sev>` only sets the exit threshold) | Semgrep |
| Rust | `cargo audit` (RustSec database) | Clippy lints |
| Any | | `semgrep scan --config auto` (add `--error` to fail on findings) |

Rules:

- Scan the changed code and the dependencies it adds. Report findings in unchanged code as pre-existing, not as part of this change.
- A scanner finding is a lead, not a verified finding. Reproduce it or trace it to reachable code before it goes in the report, like any other finding.
- Never run `npm audit fix` or any auto-fix that rewrites dependency files without approval. Propose the upgrade.
