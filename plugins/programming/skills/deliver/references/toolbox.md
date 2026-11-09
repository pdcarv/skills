# Toolbox: style guides and commands per language

Use this when the repository has no style guide of its own, and to fill the commands in the style brief. Prefer what the repo already configures (CI, Makefile, pre-commit, package scripts) over anything here. Confirm a guide's current URL with a web search before you cite it in a brief. Versions and URLs change.

## Contents

- Style guide by language
- Format and lint commands
- Coverage commands (also read by `refactor`)

## Style guide by language

| Language | Guide when the repo has none | Notes |
|---|---|---|
| Python | PEP 8 (peps.python.org/pep-0008) | Formatting is usually enforced by `ruff format` or black; follow the configured tool over PEP 8 details. |
| Go | Effective Go (go.dev/doc/effective_go) plus Go Code Review Comments (go.dev/wiki/CodeReviewComments) | Effective Go predates generics and modules and is not updated; the Code Review Comments page fills gaps. `gofmt` is not optional. |
| TypeScript | Google TypeScript Style Guide (google.github.io/styleguide/tsguide.html) | |
| Java, C++, Shell, others | Google style guides index (google.github.io/styleguide) | |
| Rust | Rust API Guidelines (rust-lang.github.io/api-guidelines), `rustfmt`, Clippy | |

Pick three to six rules that matter for this change (naming, error handling, function size, imports, comments) for the style brief. A whole guide pasted into a brief is ignored.

## Format and lint commands

| Language | Format | Lint |
|---|---|---|
| Python | `ruff format` | `ruff check` |
| Go | `gofmt -l .` / `go fmt ./...` | `golangci-lint run` |
| Rust | `cargo fmt` | `cargo clippy` |
| JS / TS | project's prettier config | project's eslint config |

## Coverage commands (also read by `refactor`)

| Language | Command | Report `refactor/scripts/crap.py` reads |
|---|---|---|
| Python | `coverage run --branch -m pytest` (or `-m unittest`), then `coverage lcov -o lcov.info` or `coverage xml` | lcov or Cobertura XML |
| Go | `go test -coverprofile=coverage.out ./...` | Go cover profile, read directly |
| JS / TS (Jest) | `jest --coverage` (lcov is on by default) | `coverage/lcov.info` |
| JS / TS (Vitest) | `vitest run --coverage --coverage.reporter=lcov` (lcov is not a default reporter) | `coverage/lcov.info` |
| Java | JaCoCo `jacoco:report` | `jacoco.xml` (JaCoCo's own format) |
| Rust | `cargo llvm-cov --lcov --output-path lcov.info` | lcov |
