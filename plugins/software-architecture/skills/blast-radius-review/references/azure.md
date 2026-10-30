# Azure fault isolation detail

Sources: Microsoft Learn "Azure region pairs and nonpaired regions" (ms.date 2025-03-19, last updated 2026-10-15) and the Azure blog "Advancing safe deployment practices" (5 Feb 2020). Region lists change; check the current page.

## What region pairs give you

- Prioritised recovery of one region per pair in a geography-wide outage.
- Staggered (sequential) planned updates across the pair.
- Data residency: almost all pairs are in the same geography.

## What they do not give you

- Pairing does not by itself make a workload more resilient. Customers must build their own HA and DR.
- Only a small number of Azure services use pairs, mainly geo-redundant (GRS) storage.
- Microsoft-managed GRS failover happens only in catastrophic situations, after repeated recovery attempts fail. Do not accept a design that relies on it as the primary DR mechanism.

## One-directional pairs (examples on the page, Oct 2026)

- Brazil South pairs with South Central US, but not the reverse.
- West US 3 pairs with East US, while East US pairs with West US.
- West India pairs with South India, while South India pairs with Central India.

For these, confirm which region the DR plan actually targets.

## Nonpaired regions (listed Oct 2026; check current)

Chile Central, Mexico Central, Austria East, Belgium Central, Denmark East, Italy North, Poland Central, Spain Central, Israel Central, Qatar Central, Indonesia Central, Malaysia West, New Zealand North. These rely on availability zones as their main redundancy; any cross-region replication is the customer's to build.

## Review checks

1. Does the design assume a pair the region does not have?
2. Does it assume pair failover is automatic?
3. For one-directional pairs, is the DR target region the right one?
4. In nonpaired regions, are critical components zone-redundant, and is cross-region replication customer-managed and tested?

## Deploy isolation

Azure's own safe deployment practice rolls out one AZ at a time within a region and deploys a region before its paired region. Check that the workload's own pipeline follows the same units (`safe-rollout`, programming plugin).

## Not covered by the sources (do not improvise)

- Availability zone overview: zone-redundant vs zonal deployments.
- Whether logical zone numbers map to different physical zones per subscription: **not verified**; do not assume either way.
- Azure Well-Architected reliability pillar content.
