# Pen-test lenses and severity

One pen-test agent per lens that applies to the change. Each lens maps to OWASP Top 10:2025 categories, so findings use a shared vocabulary. Skip a lens only when the change has nothing it can attack, and say why.

## Contents

- Pen-test agent brief
- Lenses
- Severity scales

## Pen-test agent brief

```markdown
You are a security engineer pen-testing one change, through one lens, on a local build only.
Lens: <name> - check: <checklist below>
Change: <diff or file list>   Spec: <SPEC.md path>
Attack surface: <entry points, trust boundaries, data stored or returned, auth checks>
Run locally: <start command, test command>; work only in <scratch copy path>, a copy of the working tree with the change in it.
Rules: never send traffic to a deployed or third-party system, even if credentials are present.
Every finding needs a reproduction: a failing test, a request and response against the local
build, or an input traced to the exact line. Without one, list it as a question.
Report: | severity | category | file:line | finding | reproduction | proposed fix |
```

## Lenses

| Lens | OWASP 2025 | Check |
|---|---|---|
| Access control | A01 Broken Access Control, A07 Authentication Failures | Every new entry point checks who is calling and what they may touch. Look for IDs taken from input without an ownership check, missing checks on non-GET paths, role checks on the client only, session and token handling. |
| Injection and input | A05 Injection | Every input that reaches a query, a shell, a template, a path, a regex or a deserializer. Look for string-built queries and commands, path traversal (`../`), unvalidated sizes and types. |
| Data exposure and crypto | A04 Cryptographic Failures | Secrets in code, logs or errors; sensitive fields in responses; home-made crypto; weak hashing of passwords; TLS checks turned off. |
| Errors and edge conditions | A10 Mishandling of Exceptional Conditions | Errors that fail open (grant access or skip a check), stack traces returned to callers, unbounded input causing resource exhaustion, partial failures leaving state inconsistent. |
| Design and configuration | A06 Insecure Design, A02 Security Misconfiguration | Missing rate limits or quotas on costly operations, debug modes or permissive defaults, CORS or headers loosened by the change. |
| Supply chain and integrity | A03 Software Supply Chain Failures, A08 Software or Data Integrity Failures | New dependencies (maintained? pinned? known vulnerabilities?), code or data loaded from untrusted sources without verification. |
| Logging | A09 Security Logging and Alerting Failures | Security-relevant events (failed auth, permission denials) are logged without leaking secrets. |
| LLM features (only if the change calls a model) | OWASP Top 10 for LLM Applications 2025 | Prompt injection through any text the model reads, excessive agency (tools the model can call), system prompt leakage, unbounded consumption. |

## Severity scales

Security findings: rate by what an attacker can do **through this change's entry points**, not the worst case of the bug class.

| Severity | Meaning |
|---|---|
| Critical | Remote, unauthenticated: read or change other users' data, run code, or take over accounts. |
| High | Authenticated user reaches data or actions outside their rights, or can take the service down cheaply. |
| Medium | Needs unusual conditions or leaks limited information. |
| Low | Defence in depth; no direct exploit shown. |

Correctness findings (nil, logic, error-path, concurrency and spec lenses): rate by what a user or caller sees when it happens.

| Severity | Meaning |
|---|---|
| Critical | Data loss or corruption, or a crash on a normal path. |
| High | Wrong result or crash on an input the spec allows; an acceptance check fails. |
| Medium | Wrong result or crash only on rare inputs or timing; error reported badly. |
| Low | No visible effect today; a trap for the next change. |
