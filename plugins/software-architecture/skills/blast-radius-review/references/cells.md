# Cell-based architecture review

Source: AWS whitepaper "Reducing the Scope of Impact with Cell-Based Architecture" (initial publication 20 Sep 2023), plus the shuffle-sharding article for the relationship between the two. The whitepaper gives no numeric maximum cell size; size is left to each service.

## Vocabulary

- **Cell:** a complete copy of the workload that operates independently, shares no state with other cells, and handles a subset of requests.
- **Cell router:** the thinnest possible layer; it only routes, using the partition key, and presents one endpoint to clients.
- **Control plane:** provisions and de-provisions cells and migrates customers between them.

## 1. Fit test

Cells tend to fit when:
- downtime has a large customer impact;
- the workload is critical financial-services infrastructure;
- the system is ultra-scale;
- recovery objectives are very tight (the whitepaper cites RPO under 5 s and RTO under 30 s);
- multi-tenant service where some tenants need a dedicated cell.

Weigh against the costs the whitepaper lists: architectural complexity, infrastructure cost, specialised tooling, and investment in a routing layer. The whitepaper says cells are not a good fit for every workload. Record the decision as an ADR (`architecture-decision-record`); tenant partitioning is close to a one-way door.

Rule of thumb from the source notes (an inference combining the two AWS sources): cells bound damage from bad deploys and poison pills (correlated, systemic failure); shuffle sharding bounds damage from one noisy or abusive tenant on a shared fleet. They combine, with shuffle sharding inside each cell.

## 2. Partition key

- Must align with the grain of the service: natural subdivisions with minimal cross-grain interaction.
- Should be easy to extract from most API calls.
- Add a second dimension if a single customer can outgrow a cell.
- Cross-cell work (for example scatter-gather) goes back through the router. Cells must not call each other.

## 3. Sizing

Three opposing forces: a cell must be big enough for the largest workload, small enough to test at full scale and stay below account limits, and big enough for economies of scale.

Practices:
- Test the largest workload a cell can hold; it should match the largest workload one customer can send.
- Know each cell's limits in TPS, number of tenants and GB transferred or stored.
- Define more than one scaling dimension so a customer who outgrows a cell can get a dedicated one (the whitepaper's example threshold is 10K TPS).
- Find limits with load shedding, load tests or chaos tests.
- Rate-limit at the router (for example API Gateway throttling or token buckets).
- Observe per cell: capacity, used capacity, per-tenant share, account quotas. Keep a gap between quotas and peak usage. Rebalance by migrating tenants when one key comes to dominate a cell.

## 4. Multi-AZ vs single-AZ cells

- Single-AZ cells can detect and mitigate per-AZ problems, but need three routers, zonal endpoints and DR.
- Multi-AZ cells are simpler but give less control over gray failures.
- Either way, cells are not designed as failover domains.

## 5. Router rules

- As simple as possible, minimal business logic.
- Dispatching isolated between cells; keeps working for other cells when one cell is unreachable.
- Fast and reliable; efficient key mapping (for example a cryptographic hash plus modular arithmetic).
- Statically stable: keeps routing if the control plane, the config store or an AZ is down (the whitepaper names S3 as an example dependency).
- It is the only shared component; make it cellular where possible.

Implementations the whitepaper names (AWS): Route 53 with a DNS record per tenant; API Gateway with DynamoDB; a compute fleet holding an in-memory mapping loaded from S3 and refreshed on change; a queue or stream consumer (SQS or MSK) for non-HTTP traffic.

## 6. Key-to-cell mapping

| Scheme | Trade-off |
|---|---|
| Full mapping table | Most control; a table to keep available |
| Prefix or range mapping | Simple; hot-cell risk |
| Naive modulo of a hash | Even spread; changing the cell count reshuffles every tenant |
| Consistent hashing | Commonly tens of thousands of logical buckets mapped to fewer cells; fewer moves on resize |

Always keep an **override table** to pin keys for testing, quarantine or heavy tenants.

## 7. Migration

Stateful cells almost certainly need online migration. Build it on day one. Steps: clone as a non-authoritative copy, make the new copy authoritative, redirect from the old location, forget the old data.

## 8. Operations

- Observability must be cell-aware: every request traceable to its cell.
- Deploy in waves, cell by cell or by set of cells, with rollback on failure. The first cell can be a canary cell; each cell can have its own canary with synthetic traffic.
- Related Well-Architected practices named in the whitepaper: REL08-BP05, OPS05-BP10, OPS06-BP01, OPS06-BP07, OPS06-BP08 (not read in this library's sources).

## 9. Starting point

1. The current stack is cell zero: put a router in front of it and shift traffic gradually.
2. Start with multiple cells on day one.
3. Build a migration mechanism on day one.
4. Do a failure-mode analysis per cell.

## Checklist

- [ ] Fit test recorded, with costs
- [ ] Partition key matches the service grain; second dimension for oversized tenants
- [ ] Largest tenant tested at full scale in one cell; per-cell limits known
- [ ] Mapping scheme chosen; override table exists
- [ ] Router thin and statically stable
- [ ] Multi-AZ vs single-AZ decided; cells not used as failover domains
- [ ] Online migration path exists
- [ ] Observability is cell-aware
- [ ] Deploys go cell by cell with a canary cell
- [ ] Per-cell failure-mode analysis done; shuffle sharding considered inside cells
