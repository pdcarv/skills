---
name: blast-radius-review
description: >-
  Reviews an architecture or DR plan for blast radius: static stability (pre-provisioned
  capacity for AZ or Region loss, constant-work config refresh with a cached last-known-good
  value, no failure-only fallback paths), control-plane vs data-plane recovery dependencies,
  cloud fault-isolation boundaries (AWS partitional services, GCP zonal/regional/global
  scope, Azure region pairs), cell-based architecture (fit test, sizing, router, partition
  key, mapping, migration) and shuffle sharding. Use for architecture or DR reviews, "what
  happens if an AZ/Region fails?", multi-tenant or noisy-neighbour design, "should we use
  cells?", failover runbooks, or post-incident actions to reduce scope of impact.
license: MIT
metadata:
  category: "software-architecture/resilience"
  sources: "see Sources section"
---

# Blast-radius review

Decide how much of the system and how many customers a single failure can hurt, and whether recovery depends on anything that may itself be down. The review applies four lenses in order: static stability, control-plane vs data-plane dependencies, the cloud's fault-isolation boundaries, and partitioning (cells and shuffle sharding). It ends with a ranked list of findings, each a proposal.

## When to use

- Architecture, DR or multi-region design review.
- A failover or recovery runbook is being written or audited.
- A multi-tenant service where one tenant, one bad deploy or one poison request can take everyone down.
- A postmortem action item says "reduce blast radius" or "survive AZ loss".

## When not to use

- Per-call timeouts, retries and load shedding: `timeout-retry-overload-review`.
- Rollout mechanics (one-box, waves, bake times): `safe-rollout` (programming plugin). This skill only checks that deploys follow the isolation units it finds.
- Live incident: `mitigate-first` (oncall-incident plugin).

## Inputs to gather

- Component inventory: every service, data store, queue, cache, router, DNS and identity dependency, with where it runs (zone, region, global) and how many zones or regions.
- Peak load and current capacity per zone or region; autoscaling configuration.
- Recovery and failover runbooks, and any code paths that run only on failure (fallbacks, cache bypasses, "refresh on error").
- How configuration and secrets are fetched at runtime and at startup.
- Tenancy model: how requests map to tenants, largest tenant's share of load, existing sharding.
- Cloud(s) in use; then load the matching file in `references/` (`aws.md`, `gcp.md`, `azure.md`). For cell design detail, load `references/cells.md`.

## Procedure

1. **Map failure scopes.** For each component record its scope (zonal, regional, multi-region, global) and the failure it must survive. Evidence: deployment config, not diagrams alone. On GCP every Compute Engine resource is global, regional or zonal, and that scope is its failure domain.
2. **Static stability: capacity.** The workload should run in one normal mode; behaving differently under failure (bimodal behaviour) is the anti-pattern. Check that each zone or region already has the capacity to carry the load if one is lost, rather than launching it during the failure. Flag these anti-patterns:
   - assuming resources can always be provisioned;
   - acquiring resources dynamically during a failure;
   - provisioning across zones only after a failure;
   - applying static stability to compute only (data stores, caches and read replicas need it too; size read replicas per zone or region to cover the loss of one).
   More zones reduce the extra capacity needed. Evidence: per-zone capacity vs peak, with the arithmetic.
3. **Static stability: configuration.** Configuration should refresh on a fixed cadence (constant work) and, when a refresh fails, keep the cached value and raise an alarm, not trigger a full refresh. Clients must not bypass the cache on failure. Flag startup paths that cannot start without a live dependency.
4. **Failure-only code paths.** Search for code that runs only when something else fails: fallbacks to a second dependency, cache bypass, degraded modes. Fallback is hard to test, can fail itself, can add unpredictable load and can hide latent bugs for years. For each one propose, in order of preference: make the primary path more reliable; let callers retry; push data to consumers instead of having them pull; or turn the fallback into failover by exercising both paths routinely. Also flag retries or timeouts that act as a hidden fallback.
5. **Control plane vs data plane.** Classify every recovery and failover step. Control plane = create, read/describe, update, delete and list (CRUDL) resource APIs, typically complex orchestration. Data plane = the service's primary function (serving traffic, storing and retrieving data), deliberately simpler and less likely to fail. Any recovery step that launches, creates, scales, edits policy or changes DNS through a console is a control-plane dependency; flag it and propose a pre-provisioned or data-plane alternative. On AWS, see `references/aws.md` for partitional services whose control planes live in a single Region.
6. **Cloud isolation boundaries.** Apply the cloud reference file:
   - AWS: partitional control-plane homes, break-glass credentials, Route 53 ARC endpoint handling.
   - GCP: resource scope, and quota scope (zonal usage can consume a shared regional quota, which matters for failover headroom).
   - Azure: region pairs are not an HA or DR mechanism; some pairs are one-directional; many newer regions have no pair.
7. **Partitioning: cells.** Run the fit test in `references/cells.md`. If cells fit, check partition key, cell size, router, mapping with override table, migration, cell-aware observability and per-cell failure-mode analysis. The impact arithmetic: with N equal cells, one cell failing affects about 1/N of requests (10 cells = 10%, 100 cells = 1%). Frame the choice with the whitepaper's question: is it better for all customers to see a 5% failure rate, or 5% of customers to see 100%?
8. **Partitioning: shuffle sharding.** For noisy or abusive tenants on a shared fleet, compute the options:
   - plain sharding into S shards: one bad shard hurts about 1/S of customers;
   - shuffle sharding with N workers and k per tenant: C(N,k) combinations, so one bad tenant's exact combination is shared by about 1/C(N,k) of tenants. Example: N = 8, k = 2 gives 28 combinations, about 1/28 impact vs 1/4 for four plain shards (the source calls it 7x better).
   Require that clients are fault-tolerant and retry across the shard's workers; without retries there is no benefit. Shuffle sharding can be used inside a cell but not across cells, and is trickier for stateful components.
9. **Deploys follow the isolation units.** Check that changes roll out cell by cell (a canary cell first) and one AZ or cell per region at a time, and on Azure a region before its paired region. Hand rollout detail to `safe-rollout`.
10. **Rank and write findings.** Rank by customers affected times likelihood, and mark each finding's fix as a proposal. Capacity additions, failover changes, DNS or routing changes and IAM changes all need human approval.

## Verification

- Every component in the inventory has a scope, a failure it must survive, and a statically-stable yes/no with evidence.
- Every recovery step is classified control plane or data plane; every control-plane step is a finding or has a stated reason it is acceptable.
- Capacity findings show the arithmetic (peak load, per-zone capacity, zones remaining after one is lost).
- Shuffle-shard and cell numbers show N, k or cell count and the formula used.
- Cloud-specific claims cite the reference file and carry its "check current" caveats.

## Gotchas

- **Autoscaling is not headroom.** Scaling out during an AZ failure is a control-plane call at the worst moment. Pre-provision.
- **Load shedding can hide missing headroom.** A service that sheds gracefully may look fine in a game day while lacking the capacity to survive AZ loss (see `timeout-retry-overload-review`).
- **Static stability beyond compute.** Single-zone storage classes (the AWS source names S3 One Zone-IA) are not statically stable against zone loss.
- **Cells are not failover domains.** The whitepaper is explicit; do not design a cell to absorb another cell's traffic.
- **Cross-cell calls** reintroduce shared fate. Scatter-gather goes back through the router; cells never call each other.
- **The router is the one shared component.** Keep it thin and statically stable, and make it cellular where possible.
- **Shuffle sharding without retries** gives no isolation; a client pinned to one failed worker still fails.
- **Route 53 shard count is unverified.** The source describes 2,048 virtual name servers with 4 per domain. The Japanese locale page renders the number of shards as about 730 million, but C(2048,4) is about 7.3 x 10^11 (about 730 billion). The English original was not readable; do not quote either figure as AWS's.
- **Azure pairs are not DR.** Microsoft-managed geo-failover (for example GRS storage) happens only in catastrophic cases. Customers build their own HA and DR.

## Output

```markdown
## Blast-radius review: <system>   Date: <date>   Clouds: <...>

### Component inventory
| Component | Scope (zonal/regional/global) | Must survive | Statically stable? | Recovery depends on control plane? | Evidence |

### Capacity after losing one <AZ/Region>
| Tier | Peak | Capacity per zone | Zones left | Remaining capacity | OK? |

### Failure-only paths
| Path | Trigger | Tested how often | Proposal (improve primary / push / failover) |

### Partitioning
- Cells: fit = yes/no (reasons); key = ...; cell count/size = ...; router = ...; override table = ...; migration = ...
- Shuffle sharding: N=..., k=..., C(N,k)=..., clients retry = yes/no

### Findings (ranked)
| # | Finding | Customers affected | Likelihood | Proposal (needs approval) |
```

## Sources

- AWS Well-Architected, REL11-BP05 "Use static stability to prevent bimodal behavior" (single mode, pre-provisioning, anti-patterns, constant work, read replicas, S3 One Zone-IA), read Oct 2026: https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_withstand_component_failures_static_stability.md
- AWS whitepaper "AWS Fault Isolation Boundaries": control planes and data planes; static stability; Appendix A partitional services (no visible publication date; read 2026-10-28): https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/control-planes-and-data-planes.html , https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/static-stability.html , https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/appendix-a---partitional-service-guidance.html
- Lumigo (Yan Cui), summary of the Builders' Library article "Avoiding fallback in distributed systems" (secondary source; original not read): https://lumigo.io/blog/amazon-builders-library-in-focus-3-avoiding-fallback-in-distributed-systems
- AWS whitepaper "Reducing the Scope of Impact with Cell-Based Architecture", initial publication 20 Sep 2023: https://docs.aws.amazon.com/pdfs/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/reducing-scope-of-impact-with-cell-based-architecture.pdf
- Colm MacCarthaigh, "Workload isolation using shuffle-sharding", Amazon Builders' Library (read via the Japanese locale page; original date not shown): https://aws.amazon.com/jp/builders-library/workload-isolation-using-shuffle-sharding/
- Google Cloud, "Global, regional, and zonal resources", read 2026-10-28: https://docs.cloud.google.com/compute/docs/regions-zones/global-regional-zonal-resources
- Microsoft Learn, "Azure region pairs and nonpaired regions", last updated 2026-10-15: https://learn.microsoft.com/en-us/azure/reliability/regions-paired
- Clare Liguori, "Automating safe, hands-off deployments", Amazon Builders' Library (one AZ or cell per region per step; DE locale page), first published June 2020: https://aws.amazon.com/de/builders-library/automating-safe-hands-off-deployments/
- Microsoft Azure blog, "Advancing safe deployment practices", 5 Feb 2020 (one AZ at a time, region before its pair): https://azure.microsoft.com/en-us/blog/advancing-safe-deployment-practices/
