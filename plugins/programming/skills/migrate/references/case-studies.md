# Migration case studies (all self-reported unless marked)

Loaded from `migrate`. Use these to set expectations and to argue for the judge-first process, not as benchmarks. Every figure below comes from the company or vendor that did or sold the work. No independent audit of post-migration defect rates was found for any of them.

| Case | What | Reported result | Label | Notes |
|---|---|---|---|---|
| Bun (Zig to Rust) | Language port | About 1M lines in under two weeks; 100% of the existing suite passing before merge; 19 post-merge regressions, all fixed; about 5.9B uncached input and 690M output tokens, about $165k at API prices | Self-reported (Anthropic) | **Conflict:** Pragmatic Engineer reports about 530k LOC in 2 weeks for $165K. The line count differs between sources. |
| Python to TypeScript (Mike Krieger) | Language port | About 165k lines over a weekend with 12 subagents and a 7-scenario parity harness | Self-reported (Anthropic) | Shows a small scenario harness can serve as the judge. |
| MiniJinja Rust to Go (Armin Ronacher) | Library port | About 10 h agent time (about 3 supervised), about 45 min active human time, 34 prompts, about 2.2M tokens, about $60 | Self-reported (author) | Rust snapshot files reused as the oracle; ported lexer, then parser, then runtime; agent dropped "must fail" tests and regressed escaping until steered back. |
| Airbnb (Enzyme to React Testing Library) | Test migration | Nearly 3.5k test files in about 6 weeks vs an estimated 1.5 years by hand; 75% done in 4 hours with a 10-iteration cap; 97% after 4 days; under 100 files fixed by hand; long-tail files needed 50-100 retries; prompts of 40k-100k tokens | Self-reported (via InfoQ) | Pipeline: refactor, fix Jest errors, lint, tsc, feeding errors back each time. Brute-force retries beat prompt engineering. Used Claude 3.7 Sonnet. |
| Uber (JUnit 4 to JUnit 5) | Test migration | About 600k tests across 15M LOC by two engineers in four months, 1.25M lines modified | Self-reported (via Pragmatic Engineer) | |
| Asana (Enzyme to RTL, via OpenAI Codex) | Test migration | "5 years of engineering work in 2 weeks", about $12K vs a roughly $6M staffing estimate | Self-reported by the vendor about a customer | Orosz: the $6M is a back-of-envelope estimate, probably too high; "5 years" was a projected end date for low-priority work. |
| Navan (Spring Boot 4 upgrade, via Cursor) | Framework upgrade | About 1 week vs over a month two years earlier; one cloud agent per app or library (8 apps, 15 libraries) | Self-reported (vendor-published customer story) | Same human and AI review, tests and staging as other changes; engineers owned the merge. |
| Google | Code migration | Agents plus engineers finished 6x faster than engineers alone a year earlier | Self-reported (Sundar Pichai, Apr 2026) | No baseline details given. |

## What the cases have in common

Orosz's reading of these migrations (Aug-Oct 2026): engineers still planned the work, designed the verification loops and finished the last few percent by hand, and the savings have not been shown to generalise beyond these projects. Each success had a mechanical transformation, an automated oracle, many retries, and human cleanup of the tail.

## Sources

- Anthropic, "AI code migration", 16 Jul 2026: https://claude.com/blog/ai-code-migration
- Armin Ronacher, "Porting MiniJinja to Go With an Agent", 14 Jan 2026: https://lucumr.pocoo.org/2026/1/14/minijinja-go-port/
- InfoQ, Airbnb LLM test migration, 28 Mar 2025: https://www.infoq.com/news/2025/03/airbnb-llm-test-migration/
- Gergely Orosz, The Pulse (Pragmatic Engineer) on migrations with AI, 27 Aug 2026, updated 22 Oct 2026: https://blog.pragmaticengineer.com/the-pulse-we-need-to-talk-about-migrations-with-ai/
- Cursor, Navan customer story, 16 Oct 2026: https://cursor.com/blog/navan
- ETV Bharat on Sundar Pichai's 22 Apr 2026 post, 27 Apr 2026: https://www.etvbharat.com/en/technology/sundar-pichai-says-75-percent-of-new-code-at-google-is-generated-by-ai-enn26042705700
