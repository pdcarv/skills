# Testing rules and mutation tools

Read in Phase 3. The rules apply to every test an agent writes; paste the "Rules for every test" block into each test brief.

## Contents

- Rules for every test
- Example: story test vs logic test
- Coverage of every path
- Mutation testing: tools and commands
- Reading the mutation result

## Rules for every test

- **One story or assumption per test.** A test checks one behaviour, such as "a done task is never overdue". If its name needs "and", split it.
- **Name it as the behaviour**, not the method: `test_a_done_task_is_never_overdue`, not `test_is_overdue_2`.
- **Literal inputs and expected values.** Write `assert total == Decimal("32.00")`, not a recomputation of the formula. A test that repeats the implementation's arithmetic repeats its bugs (Kuefler, "Don't Put Logic in Tests").
- **No logic in the test body**: no loops, conditionals, string building or computed expectations. If setup needs logic, move it to a small, obviously correct helper.
- **Through the public interface** the spec names: the function, endpoint or CLI. Do not test private helpers, and do not mock the unit under test.
- **Smallest test that proves the point.** Only the setup this behaviour needs; shared fixtures only where the project already uses them.
- **Follow the project's conventions**: its framework, file layout, fixtures and kinds of test. If the project uses only end-to-end tests, write end-to-end tests unless the user agreed otherwise.

## Example: story test vs logic test

Logic test (avoid):

```python
def test_discounts():
    for code, rate in [("SAVE10", 0.10), ("BULK", 0.20)]:
        cart = make_cart()
        expected = cart.subtotal() * (1 - rate) + cart.shipping()
        assert cart.total(code) == round(expected, 2)
```

Story tests (prefer):

```python
def test_save10_takes_10_percent_off_items_not_shipping():
    cart = Cart(); cart.add("A", "30.00")
    assert cart.total("SAVE10") == Decimal("32.00")

def test_free_shipping_uses_the_discounted_subtotal():
    cart = Cart(); cart.add("A", "55.00")
    assert cart.total("SAVE10") == Decimal("54.50")
```

The first test recomputes the answer, hides two behaviours in a loop, and passes if the rate table and the code share a mistake. Each story test states one fact a reader can check by hand.

## Coverage of every path

- Run with branch coverage where the tool supports it (coverage.py `--branch`; Go's `-covermode=count` gives statements, not branches). Scope the report to the changed files.
- Every uncovered line or branch in changed code ends up as one of: a new behaviour test; "unreachable, possible dead code" (sent to Phase 4); or an exclusion with a reason the user accepted.
- Coverage shows what ran, not what was checked. A suite can reach 100% with weak assertions; mutation testing measures whether the tests notice a change.

## Mutation testing: tools and commands

Default: use a tool only if it is already installed; otherwise mutate by hand (SKILL.md, Phase 3 step 5).

| Language | Tool | Run | Scope to the change |
|---|---|---|---|
| Python | mutmut | `mutmut run`, then `mutmut browse` (Linux and macOS; Windows only via WSL) | `paths_to_mutate` in `[tool.mutmut]` (a config entry: propose it) |
| JS / TS | StrykerJS | `npx stryker run` if installed (setting it up runs `npm init stryker`, which edits `package.json`: propose it) | `--mutate "<file>:<lines>"` (check the current docs) |
| C# | Stryker.NET | see stryker-mutator.io | see docs |
| Scala | Stryker4s | see stryker-mutator.io | see docs |
| Java | PIT | `mvn test-compile org.pitest:pitest-maven:mutationCoverage` (report in `target/pit-reports/`) | `-DtargetClasses=<classes>` (unverified) |
| Rust | cargo-mutants | `cargo mutants` | `--in-diff <diff file>` (new files are not in `git diff`: scope those by path) |
| PHP | Infection | see infection.github.io | see docs |
| Go | gremlins (`gremlins unleash`) or go-mutesting forks | | No clearly maintained tool as of Nov 2026; gremlins is pre-1.0 and aimed at small modules. Say so before proposing one. |

Installing any of these, or adding a config entry to scope one, changes the user's environment or repo: propose it and wait.

## Reading the mutation result

- **Mutation score** is the share of mutants the tests kill. Infection's MSI also counts timeouts and fatal errors as killed, and reports a "covered code" score that leaves out lines no test runs.
- Look at **surviving mutants in the changed code** only. Google runs mutation testing on the diff and skips "arid" lines (logging and similar) to keep the result useful in code review.
- For each surviving mutant, either add the behaviour test that kills it, or record why it is equivalent (no input can tell the mutant from the original).
- Report the score before and after the new tests, and the list of equivalent mutants.
