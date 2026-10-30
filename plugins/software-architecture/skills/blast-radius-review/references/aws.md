# AWS fault isolation detail

Sources: AWS Fault Isolation Boundaries whitepaper (pages show no publication date; read 2026-10-28), AWS Well-Architected REL11-BP05, and the shuffle-sharding Builders' Library article (Japanese locale page). Region placements of control planes can change; check the current whitepaper before relying on them.

## Control plane vs data plane examples (from the whitepaper)

| Control plane (avoid in recovery) | Data plane (safe to rely on) |
|---|---|
| EC2 `RunInstances` | A running EC2 instance |
| Creating an S3 bucket | S3 Get/Put |
| Describing an SQS queue | EBS reads and writes |
| | Route 53 DNS answers and health checks |

Running EC2 instances, VPCs, S3 objects and EBS volumes keep working without control-plane access. Relying on the EC2 control plane to launch replacements during an AZ failure adds a recovery dependency; pre-provisioning across AZs removes it. Well-Architected REL11-BP04 names the practice: rely on the data plane, not the control plane, during recovery.

## Partitional services (global services whose control plane sits in one Region)

As read 2026-10-28; check the current whitepaper Appendix A:
- AWS Account Management and AWS Organizations: control plane in us-east-1.
- AWS Network Manager: us-west-2.
- IAM, Route 53 ARC and Route 53 Private DNS: the page read did not state a Region. CloudFront and public Route 53 are in Appendix B, which was not read.

Review checks:
- Flag any runbook step that calls a control-plane API (launch instances, create users, edit SCPs, change DNS records through the console, scale up). Flag it twice if the service is partitional.
- **IAM:** during an IAM control-plane impairment, authentication and authorization for existing principals continue, and STS does not depend on the IAM control plane. Pre-create break-glass credentials; do not plan to create them during an event.
- **Organizations:** SCPs and tag policies keep being evaluated during a control-plane impairment. Do not plan to edit SCPs during recovery; instead reference IdP session tags in static SCP conditions (the whitepaper's example uses `aws:PrincipalTag/failover-admin`).
- **Account Management:** account creation depends on us-east-1; pre-provision failover accounts.
- **Route 53 ARC:** hard-code or bookmark the five Regional cluster endpoints, avoid `DescribeCluster` during failover, and use the CLI or SDK rather than the console. Documented form (a production change: propose it in the runbook, never run it from a review):
  ```
  aws route53-recovery-cluster update-routing-control-state \
    --routing-control-arn <arn> --routing-control-state Off \
    --endpoint-url <regional cluster endpoint>
  ```
- **Network Manager:** export CloudWatch `AWS/Network Manager` metrics to S3 on a schedule and use the export as failover input, rather than querying a control plane during recovery.

## Static stability specifics (REL11-BP05)

- Provision enough capacity in each AZ or Region to carry the load if one is lost.
- Size read replicas per AZ or Region to cover the loss of a zone.
- S3 One Zone-IA is not statically stable.
- More AZs reduce the extra capacity needed (losing one of three leaves two thirds; losing one of two leaves half).

## Shuffle sharding on AWS

- Route 53 uses 2,048 virtual name servers with 4 assigned per customer domain; any two customer domains share at most 2 name servers. The total shard count is **unverified**: the Japanese page renders it as about 730 million, while C(2048,4) is about 7.3 x 10^11 (about 730 billion).
- Route 53's open-source **Infima** library implements shuffle sharding. A recursive variant shards at multiple layers.
- The article says shuffle sharding usually needs no additional cost.

## Deploy isolation (Builders' Library, hands-off deployments)

Each production step deploys to only one AZ or cell per Region. Wave 1 is a single low-traffic Region; wave 2 a single high-traffic Region. Rollout detail lives in `safe-rollout` (programming plugin).
