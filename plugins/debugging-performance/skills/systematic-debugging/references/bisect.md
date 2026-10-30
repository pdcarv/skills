# git bisect for regressions

Load this when there is a known good revision, a known bad revision, and a check that can decide good or bad without a human. Bisect is a binary search over history; it finds the first bad commit, which is evidence for the root cause, not the root cause itself.

## Manual flow

```bash
git bisect start
git bisect bad                 # current HEAD is bad
git bisect good <good-rev>     # last known good commit or tag
# git checks out a midpoint; test it, then mark it:
git bisect good                # or: git bisect bad / git bisect skip
# ...repeat until git names the first bad commit
git bisect log                 # record of every decision (save it in the debug log)
git bisect visualize --stat    # remaining suspects
git bisect reset               # return to the original branch; always do this
```

Use `git bisect skip` for a revision that cannot be tested (it does not build, the test cannot run). If many revisions are skipped around the culprit, expect a less precise answer and check the named range by hand.

## Automated flow: `git bisect run`

```bash
git bisect start
git bisect bad <bad-rev>
git bisect good <good-rev>
git bisect run /path/outside/repo/check.sh
git bisect log > /path/outside/repo/bisect.log
git bisect reset
```

Exit codes the command must return:

| Exit code | Meaning to bisect |
|---|---|
| 0 | good |
| 1-127, except 125 | bad |
| 125 | this revision cannot be tested; skip it |
| anything else (128 and above) | abort the whole bisect |

`exit(-1)` comes out as 255 and aborts the run. Any tool in the script that can exit above 127 will abort the bisect instead of marking the commit bad; map its status explicitly.

### Template check script

Keep the script outside the tracked tree (or untracked) so every checkout runs the same check.

```bash
#!/usr/bin/env bash
# check.sh: exit 0 = good, 1 = bad, 125 = cannot test
set -u
make build >/dev/null 2>&1 || exit 125      # build failure is not the bug
run_the_failing_test                          # the reproduction test from the main procedure
status=$?
if [ "$status" -eq 0 ]; then exit 0; else exit 1; fi
```

Replace `make build` and `run_the_failing_test` with the project's real commands. Normalising the status to 0 or 1 avoids accidental aborts from unusual exit codes.

### Applying a temporary patch

If the reproduction test does not exist in old revisions, or old revisions need a small fix to build, the script may apply a temporary patch before testing. It must then restore the tree (for example `git checkout -- .` or `git stash`-style reversal of exactly what it applied) and exit with the real test status. A script that leaves the tree dirty breaks the next checkout.

## Performance regressions: custom terms

"Good" and "bad" read badly for speed. Use custom terms:

```bash
git bisect start --term-old fast --term-new slow
git bisect slow <slow-rev>    # unverified: marking syntax with custom terms is not in the source notes
git bisect fast <fast-rev>    # unverified: same
git bisect run /path/outside/repo/perf-check.sh
```

With `git bisect run`, exit code 0 should map to the old term (`fast`) and 1-127 except 125 to the new term (`slow`). Inferred: the source notes give exit codes only for good/bad; test on a known pair first.

Writing a reliable perf check:

1. Measure the known fast and known slow revisions first, several runs each, on the same machine and with the same input. If the two distributions overlap, the check cannot decide and bisect will produce a wrong answer; make the benchmark more specific before bisecting.
2. Set the threshold between the two distributions, not at the fast value.
3. In the script, run the benchmark several times and compare the median (not a single run) to the threshold.
4. Exit 125 when the build fails or the benchmark errors, never 0 or 1.
5. Keep the machine quiet; background load during one step will mislabel that commit.

## Gotchas

- Bisect assumes one transition from old to new. If the regression came and went, or two changes each contributed, the answer will be one of them; re-verify by testing the named commit and its parent directly.
- Flaky tests mislabel commits. Run the check several times per revision inside the script and decide by majority, or fix the flakiness first.
- Dependency or environment drift (lockfiles, generated code, caches) can make old revisions fail for unrelated reasons; that is a 125, not a 1.
- Always finish with `git bisect reset`, and save `git bisect log` before resetting so the decisions are reproducible.

## Source

- git-bisect documentation, git/git master, read Oct 2026: https://raw.githubusercontent.com/git/git/master/Documentation/git-bisect.adoc
