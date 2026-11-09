# Coverage reports for crap.py

`scripts/crap.py` reads one coverage report and detects its format from the content. Generate the report from the repository root, so its paths match the source paths you pass to the script.

| Language | Produce the report | Format |
|---|---|---|
| Python | `coverage run --branch -m pytest` (or `-m unittest discover`), then `coverage lcov -o lcov.info` or `coverage xml` | lcov / Cobertura XML |
| Go | `go test -coverprofile=coverage.out ./...` | Go cover profile (no converter needed) |
| JS / TS (Jest) | `jest --coverage` | `coverage/lcov.info` |
| JS / TS (Vitest) | `vitest run --coverage --coverage.reporter=lcov` | `coverage/lcov.info` |
| Java | JaCoCo `jacoco:report` | `target/site/jacoco/jacoco.xml` |
| Rust | `cargo llvm-cov --lcov --output-path lcov.info` | lcov |

Then run: `python3 <this skill's folder>/scripts/crap.py --coverage <report> <source paths>`.

How the script measures:

- Complexity is lizard's cyclomatic complexity per function. lizard supports C/C++, C#, Go, Java, JavaScript/TypeScript, Kotlin, PHP, Python, Ruby, Rust, Scala, Swift and others.
- Coverage is line coverage over the function's lines, excluding the signature line. Savoia's original CRAP used basis-path coverage, so scores here are an approximation; they rank hotspots well, but don't read too much into small differences.
- A function whose file is not in the report gets 0% coverage and is counted under "without coverage data". If tested files show up there, the paths in the report don't match the source paths: regenerate the report from the repo root.
- Run it from the repository root: reports such as coverage.py's lcov use repo-relative paths, and a bare file name in the report only matches a file at the current directory's top level.
- Byte-identical files are all scored (lizard's own directory walk would drop all but one, and copies are what a cleanup looks for). Inside a git repository the file list comes from `git ls-files`, so ignored files are skipped.
- An empty or unreadable report, or a path with no functions, exits with code 1 instead of printing a table of n/a.
- The threshold defaults to 30, as in crap4j. Use `--json` to keep the numbers for the before and after comparison.
