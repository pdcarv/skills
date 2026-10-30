# Zero-downtime schema migrations

Loaded from `safe-rollout` step 11. Covers the expand/contract sequence and online schema change tools for large MySQL tables. Postgres equivalents (for example pg-osc or `CREATE INDEX CONCURRENTLY`) were not researched for this library; do not apply the MySQL tool guidance to them.

## Expand / migrate / contract (parallel change)

Danilo Sato's parallel change has three phases: expand (add the new version alongside the old), migrate (move clients over incrementally; usually the longest phase), contract (remove the old version once nothing uses it). Code can be released at any phase.

Applied to a column change, combining Sato, AWS's two-phase deployment and Azure's note on stateful rollback (a synthesis; no single source gives this exact list):

| # | Step | Separately deployable | Rollback safe because |
|---|---|---|---|
| 1 | Add the new nullable column, table or field (expand) | yes | old code ignores it |
| 2 | Deploy code that reads both and tolerates both (prepare) | yes | still writes old |
| 3 | Deploy code that writes new, or both (activate) | yes | step-2 code can read new |
| 4 | Backfill existing rows | yes (batch job) | old column still present |
| 5 | Switch reads to new, ideally behind a flag | yes | flag off restores old reads |
| 6 | Wait out the backout period | - | nothing removed yet |
| 7 | Stop writing old | yes | reads already on new |
| 8 | Drop the old column (contract) | yes | last step; needs a restore plan, not a code rollback |

Rules:
- Each row is its own release with its own verification. Never combine steps 1 and 8 in one deploy.
- Put an owner and a date on step 8. An unfinished contract phase leaves two schemas and two code paths, which is worse than the start.
- Mitigations Sato lists for the in-between period: deprecation notes, TODOs, and a client-side flag to choose the version.
- Write down data-rollback instructions for every step that changes stored data; Azure's guidance calls stateful and schema rollback the complex case.

## Serialisation hygiene (AWS rollback-safety article)

- Use an established framework (JSON, Protocol Buffers, Cap'n Proto, FlatBuffers).
- Give the serialiser an explicit version independent of the build version; store it with the data and emit it as a metric.
- Do not serialise data structures you do not control, such as JDK collection classes.
- Preserve unknown attributes when rewriting data; this can make a two-phase deployment unnecessary.

## Online schema change on large MySQL tables

A blocking `ALTER` on a large table is itself an outage risk. Use an online tool and present the run as a proposal for a human to start and to release the cut-over.

### gh-ost (GitHub; README describes it as GA)

How it works: creates a ghost table, copies rows in chunks, connects as a fake replica (preferably to a real replica) and applies binlog row events for the table asynchronously. At cut-over it locks the original table for writes, drains the backlog and swaps atomically; on failure it returns to the pre-cut-over state.

Controls named in its docs:
- Throttling on replication lag, on `max-load`, or by interactive command; while throttled it writes nothing to the ghost table.
- `--postpone-cut-over-flag-file`: cut-over waits while the file exists, so a human releases it.
- `--test-on-replica`: runs the migration on a replica and stops for checksum comparison. Run this first.
- Interactive status and reconfiguration over a unix socket or TCP; hooks.
- Use release builds, not master, in production.

Prerequisites and limits (from a fork mirror of the upstream requirements doc; re-check upstream before relying on them):
- Row-based binlog with `FULL` row image on at least one server, preferably a replica, whose schema matches the master's.
- Privileges: ALTER, CREATE, DELETE, DROP, INDEX, INSERT, LOCK TABLES, SELECT, TRIGGER, UPDATE, plus SUPER + REPLICATION SLAVE or REPLICATION CLIENT + REPLICATION SLAVE.
- The table must share a PRIMARY KEY or other UNIQUE KEY before and after, with no NULLs in it.
- Not supported: foreign keys, triggers, MySQL 5.7 generated and JSON columns, FEDERATED tables, active-active master-master, multisource replication via a replica.
- Managed databases: the doc says RDS and Cloud SQL are not supported. That statement may be stale (fork snapshot) and is unverified for 2026; check the current upstream doc.

### pt-online-schema-change (Percona), as described by gh-ost's design doc

Adds AFTER INSERT/UPDATE/DELETE triggers that copy changes to the ghost table in the same transaction. That allows a simple atomic rename but couples write load (roughly doubling writes on the migrated table), adds lock contention, and cannot be paused independently. This description comes from a competitor's design doc; Percona's own documentation was not read.

### Choosing

- Table has foreign keys or triggers: gh-ost cannot run; pt-osc is the option (with the trade-offs above).
- Otherwise prefer gh-ost for throttling, pausing and a human-released cut-over.
- Either way: test on a replica, throttle on replication lag, schedule inside the deploy window, and keep the data-rollback plan next to the run.

## Sources

- Danilo Sato, "ParallelChange", martinfowler.com, 13 May 2014: https://www.martinfowler.com/bliki/ParallelChange.html
- AWS Builders' Library, "Ensuring rollback safety during deployments" (German locale page, original date unverified): https://aws.amazon.com/de/builders-library/ensuring-rollback-safety-during-deployments/
- Azure Well-Architected OE:11, last updated 2026-06-17: https://learn.microsoft.com/hr-hr/azure/well-architected/operational-excellence/safe-deployments
- github/gh-ost README: https://github.com/github/gh-ost
- gh-ost triggerless design doc: https://GitHub.com/github/gh-ost/blob/master/doc/triggerless-design.md
- gh-ost requirements and limitations (fork mirror of upstream doc): https://github.com/jacobbednarz/gh-ost/blob/master/doc/requirements-and-limitations.md
