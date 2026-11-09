---
name: resilience
description: >-
  Audits each remote call path for timeouts, retries, backoff, retry budgets,
  idempotency and load shedding: timeouts derived from a chosen false-timeout percentile,
  retries at one layer only, token-bucket retry budgets, capped exponential backoff with
  jitter, idempotency keys on mutating endpoints, and overload rules (goodput, priorities,
  deadline propagation, bounded queues, cheap rejections). Use when reviewing a client,
  SDK configuration, service mesh or service call path for resilience, designing a
  mutating or payment API, after a retry storm, cascading failure or thundering herd, or
  when asked "how will this behave under overload?". Produces a findings table per call
  path.
license: MIT
metadata:
  category: "programming/resilience"
  sources: "see Sources section"
---

# Resilience

Walk every remote call in a path and check it against the AWS Builders' Library rules for timeouts, retries and backoff, Stripe's idempotency-key contract, and the Builders' Library load-shedding rules. Retries are selfish: each one spends shared capacity to improve one caller's odds, so the review is mostly about bounding them. The output is one findings table per call path, with every change written as a proposal.

**Side effects:** Returns the findings tables and writes no files. Reads code, client, SDK and mesh config, latency metrics and the libraries' docs for default values, all read-only; never changes timeouts, retries, shedding or routing.

## When to use

- Design or code review of a service, client library, SDK configuration, proxy or mesh retry policy.
- A new mutating API (create, charge, send) that clients will retry.
- After an incident where load spiked with errors, retries multiplied, or periodic jobs synchronised.
- Before a launch, to check call paths under overload.

## When not to use

- AZ, Region or tenant blast radius rather than per-call behaviour: out of scope.

## Inputs to gather

- The call graph for each user-facing operation: every hop, including calls to processes on the same host, sidecars, proxies, load balancers and queues.
- For each hop: connect timeout, request timeout, retry count, backoff settings, and who retries (application code, SDK, mesh, load balancer, queue redelivery). Read the actual config, not the intended one.
- The downstream latency distribution per hop (p50, p99, p99.9), not averages.
- Whether each operation is idempotent, and whether mutating endpoints accept an idempotency key.
- Load test results past the breaking point, if any, and the service's traffic priority classes.
- SDK names and versions in use (defaults differ by SDK and version).

## Procedure

1. **Inventory call paths.** List every remote call per operation in a table. Evidence: file and line, or config key, for each timeout and retry setting found. Mark "default" where nothing is set and look up the library's default.
2. **Timeouts present.** Every remote call needs both a connect timeout and a request timeout, including calls to the same host. Missing timeout = finding.
3. **Timeout values.** Pick an acceptable false-timeout rate and set the timeout at the matching downstream latency percentile; for example 0.1% maps to p99.9. Add worst-case network latency for internet clients. Add padding when p99.9 is close to p50. Evidence: the percentile used and its measured value.
4. **What the timer covers.** Check whether DNS lookup, connection setup or TLS handshakes count toward the timeout. In the source's example, a 20 ms timeout failed after every deployment because new connections' setup counted against it; the fix was to open connections at process startup.
5. **Retry layers and amplification.** Count the layers that retry on the path and multiply their attempt counts. Five layers retrying three times each gives 3^5 = 243x load on the bottom dependency. Retries belong at one layer only. Count hidden retriers: AWS SDKs retry by default (under the opt-in 2026 retry behaviour: 3 attempts in standard mode, 4 for DynamoDB, per the AWS retry doc read 2026-10-28; pre-2026 defaults are not in this library's sources; check the current value), and the Cosmos DB SDK typically retries a 429 up to about nine times (Microsoft doc dated 2026-05-29; check current).
6. **Retry budget.** Require a local token bucket that lets calls retry freely while tokens remain, then only at a fixed rate. The AWS SDKs have done this since 2016. The source author prefers token buckets to circuit breakers because breakers add modal behaviour that is hard to test. For AWS SDKs, note whether the 2026 retry behaviour is opted in (`AWS_NEW_RETRIES_2026=true`), because quota costs and backoff timing differ; see the AWS retry doc for current numbers.
7. **What is retried.** Retry only idempotent operations, or APIs that take an idempotency token (EC2 RunInstances is the source's example). Retry server errors and throttling, not client errors such as validation or access denied.
8. **Backoff and jitter.** Require exponential backoff capped at a maximum delay, with a limited number of attempts, plus jitter. The AWS SDKs document full jitter as `delay = random(0,1) x min(cap, base x 2^attempt)`. Also jitter timers, periodic jobs and delayed work, which cluster at the top of the minute or midnight; for scheduled work use a consistent per-host offset so patterns are reproducible.
9. **Idempotency keys on mutating endpoints** (Stripe's API contract as the reference design):
   - Client sends a key on POST; recommend V4 UUIDs or other high-entropy random strings, never sensitive data such as email addresses. (Stripe caps keys at 255 characters; set your own limit.)
   - Server saves the status code and body of the first request once endpoint execution begins; retries with the same key return the saved response, including 500 errors.
   - Reusing a key with different parameters is an error.
   - Requests that fail validation, or conflict with a concurrent request using the same key, are not saved and can be retried.
   - Keys are retained for a defined period (Stripe: may be pruned once at least 24 hours old).
   - GET and DELETE are idempotent by definition, so keys are unnecessary there.
   Evidence: where the key is stored, the TTL, the mismatch error, and concurrent-request handling.
10. **Overload behaviour.** Check, and record evidence for each:
    - **Measured knee:** a load test past the breaking point exists; goodput plateaus rather than collapses. Track goodput and client-perceived availability; when median latency equals the client timeout, about half of requests fail.
    - **Priorities:** load-balancer health checks first, then traffic ranked by business criticality; serve completion calls (end) ahead of new work (start), and later pagination pages ahead of first pages.
    - **Deadlines:** client deadlines propagate across hops; work that can no longer succeed is dropped.
    - **Bounded work:** paginated APIs, capped queue sizes, requests discarded after waiting too long; consider LIFO where the protocol allows; fail fast rather than surge queues.
    - **Cheap rejections:** reject as early and cheaply as possible, in layers (proxy connection limits, OS-level controls, gateway and WAF).
    - **Visibility:** every rejection logged with client, operation and reason; alarm on shedding volume; shed requests excluded from latency metrics.
    - **Interactions:** shedding must not block autoscaling or hide a shortfall of AZ-failure headroom.
11. **Hidden fallback.** Flag retries or timeouts that switch to a different code path or dependency on failure; that is a fallback in disguise.
12. **Write findings and proposals.** One table per call path (Output). Any change to timeouts, retry counts, shedding or routing in production is a proposal for a human to approve.

## Verification

- Every hop in every listed path has a row with connect timeout, request timeout, retrier and attempt count, each with a file/config citation or "default (<library>, <version>)".
- Each timeout finding names the percentile and the measured latency it was compared with.
- Amplification is computed as the product of attempts across layers, with the layers named.
- Each retried operation is marked idempotent, key-protected, or a finding.
- Overload checks each have evidence or an explicit "no evidence found".
- No change was applied; all are proposals.

## Gotchas

- **Defaults are retries.** SDKs, meshes, load balancers and queue redelivery all retry without anyone writing a loop. Count them.
- **Same-host calls need timeouts too.** A sidecar or local daemon that hangs blocks the caller like any remote service.
- **Timeouts from averages** fail a large share of requests. Use a percentile from a distribution.
- **Connection setup inside the timer** turns every deploy or scale-out into a failure spike.
- **Jitter only on retries** leaves cron and periodic refreshes synchronised; the source example had EBS and Lambda clients spiking together on one-minute intervals until they were jittered.
- **Idempotency keys that store nothing on 5xx** let a retry repeat a half-done side effect. Stripe saves the 500 too.
- **Shed requests in latency metrics** make latency look better while users fail.
- **Circuit breakers as the only control** add a hard-to-test mode switch; prefer a budget.
- **Retry-number drift.** AWS retry numbers changed with the 2026 behaviour, and pre-2026 standard-mode token costs were not verified. Read the SDK doc for the version in use.

## Output

```markdown
## Timeout/retry/overload review: <service or operation>
Scope: <paths reviewed>   Evidence: <repos, configs, dashboards, load tests>

### Path: <operation> (client -> A -> B -> DB)
| Hop | Check | Current (source) | Expected | Finding | Severity | Proposed change |
|---|---|---|---|---|---|---|
| A->B | request timeout | 5s (config.yaml:12) | ~p99.9 of B = 800ms + padding | too loose, holds threads | medium | set to ... |
| A->B | retries | 3 (SDK default) | one layer only | B also retries x3 -> 9x | high | disable at A |
| ... | idempotency key | none on POST /charge | key + saved response | duplicate charges on retry | high | ... |
| ... | load shedding | unbounded queue | bounded, discard stale | collapse past knee | high | ... |

Amplification on this path: <a> x <b> x ... = <n>x

### Overload summary
- Knee measured: yes/no (<link>)  - Priorities defined: ...  - Deadlines propagated: ...

### Proposals (need human approval)
1. ...
```

Severity is this skill's convention: high = can multiply load or duplicate side effects; medium = wrong value or missing budget; low = hygiene.

## Sources

- Marc Brooker, "Timeouts, retries and backoff with jitter", Amazon Builders' Library, 5 Dec 2019 (percentile timeouts, connection setup example, single-layer retries and 3^5 example, token bucket since 2016, idempotency tokens, capped backoff, jitter on periodic work, per-host jitter): https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter
- "Using load shedding to avoid overload", Amazon Builders' Library, 5 Dec 2019 (knee, goodput, priorities, deadlines, bounded queues, cheap layered rejections, metrics and autoscaling interactions): https://builder.aws.com/content/3Eun1EEyX6p2e3VYNyRLSJzLuMV/using-load-shedding-to-avoid-overload
- AWS SDKs and Tools, "Retry behavior" (modes, default attempts, full-jitter formula, 2026 opt-in), doc read 2026-10-28: https://docs.aws.amazon.com/general/latest/gr/api-retries.html
- Stripe API reference, "Idempotent requests" (key format, saved responses, 24-hour pruning, mismatch and concurrency rules, v2 behaviour), read Oct 2026: https://docs.stripe.com/api/idempotent_requests.md
- Microsoft, "Diagnose and troubleshoot request rate too large (429)" for Cosmos DB (SDK retries about nine times), ms.date 2026-05-29: https://docs.azure.cn/en-us/cosmos-db/troubleshoot-request-rate-too-large
- Lumigo (Yan Cui), summary of the Builders' Library article "Avoiding fallback in distributed systems" (hidden fallback; secondary source, original not read, date not recorded: unverified): https://lumigo.io/blog/amazon-builders-library-in-focus-3-avoiding-fallback-in-distributed-systems
