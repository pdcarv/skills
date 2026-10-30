# Google Cloud fault isolation detail

Sources: "Global, regional, and zonal resources" (Compute Engine docs, read 2026-10-28) and "Cloud Quotas overview" (page updated 2026-10-22). Coverage in this library's notes is thin; the gaps are listed below.

## Resource scope is the failure domain

- Every Compute Engine resource is global, regional or zonal. Examples from the page: images are global; regional static IP addresses are regional.
- Spreading across zones isolates the workload from many infrastructure, hardware and software failures. Spreading across regions gives more independence.

Review checks:
1. For every stateful component, record whether it is zonal, regional or multi-region, and whether that was a deliberate choice.
2. A zonal component on the critical path of a "regional" service makes the service zonal for that failure.

## Quota scope matters for failover headroom

- Quotas apply at project, folder or organization level, and are global, regional or zonal.
- Zonal usage can also consume a shared regional quota. When planning to absorb a zone's load in the remaining zones, check that the regional quota has room for the extra capacity, not just the zonal one.
- Within a project, quota is shared across all applications.

## Not covered by the sources (do not improvise)

- The Google Cloud Well-Architected reliability pillar content.
- Deployment archetypes (zonal, regional, multi-regional, global, hybrid).
- Zonal vs regional Persistent Disk, global VPC and regional subnet details.
- Cloud SQL HA and failover, Spanner, GKE topology.

When these matter, read the current Google Cloud docs and cite them in the review.
