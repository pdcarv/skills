# debugging-performance

Skills for finding why something is broken or slow, with evidence before any fix.

| Skill | Use it for |
|---|---|
| `systematic-debugging` | Root cause before fix: hypothesis and evidence loop, failing reproduction test, temporary runtime instrumentation, `git bisect run` for regressions (including performance, with custom terms). Stops after three failed fixes. |

Related skills in other plugins: `mitigate-first` and `production-safe-agent` (oncall-incident), `timeout-retry-overload-review` (software-architecture), `red-green-tdd` (programming).

All investigation is read-only by default. Anything that changes production state, including granting `SYS_PTRACE` or root to profile, is presented as a proposal for a human to approve.

License: MIT
