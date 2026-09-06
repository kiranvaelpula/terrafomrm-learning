# AWS Cost Management Basics

## Overview

Understanding how AWS charges you — the cost dimensions, pricing models, and where waste hides — is the foundation of all FinOps.

---

## 📖 Understanding AWS Cost Management (Intuition First)

Think of your AWS bill like a giant utility bill for a building where every tenant uses electricity, water, and gas differently. Some services charge you like electricity — by the hour something is switched on (EC2 instances). Others charge like water — by the volume you store or move (S3 storage, data transfer). And some charge like a metered toll — a tiny fee every time you make a request (Lambda invocations, API calls). Understanding AWS costs starts with knowing which "meter" each service runs on.

The reason this matters is that the same workload can cost wildly different amounts depending on *how* you consume it, not just *how much*. Leaving a big instance running overnight is like leaving the heat on in an empty building. Storing every log forever in the most expensive tier is like renting a climate-controlled vault for old newspapers. The bill isn't high because AWS is expensive — it's high because the consumption pattern is inefficient.

AWS bills on a **pay-as-you-go** model, which is the whole point of the cloud: you trade the certainty of owning hardware for the flexibility of paying only for what you use. But flexibility cuts both ways. Without attention, "pay for what you use" quietly becomes "pay for what you forgot to turn off." That gap between provisioned and actually-used capacity is where most cloud waste hides.

The main cost dimensions to internalize are **compute** (running instances and containers), **storage** (data at rest), **data transfer** (data moving between regions or out to the internet — often the surprise on the bill), and **managed services** (databases, queues, functions that bundle infrastructure into a per-use price). Almost every optimization technique maps back to reducing one of these four.

The mental shift AWS cost management asks for is simple: treat cost as a first-class engineering signal, right next to latency and error rate. Once you can read the meters and see which resources are running, most savings come from turning off what you don't need and right-sizing what you do.

---

## The Four Cost Dimensions

```
1. COMPUTE — running instances/containers (billed per hour/second)
   EC2, ECS, EKS, Lambda, Fargate

2. STORAGE — data at rest (billed per GB/month)
   S3, EBS, EFS, RDS storage, snapshots

3. DATA TRANSFER — data moving (the surprise on bills)
   Internet egress (expensive), cross-region, cross-AZ

4. MANAGED SERVICES — bundled per-use pricing
   RDS, DynamoDB, SQS, API Gateway, etc.
```

## Pricing Models (Compute)

| Model | Discount | Trade-off | Best for |
|-------|----------|-----------|----------|
| On-Demand | None | Most flexible, most expensive | Spiky/unpredictable workloads |
| Savings Plans | Up to ~72% | 1 or 3-yr commitment | Steady baseline usage |
| Reserved Instances | Up to ~72% | Commit to instance family | Stable, predictable workloads |
| Spot | Up to ~90% | Can be reclaimed anytime | Fault-tolerant, batch, training |

## Storage Tiers (S3 example)

```
S3 Standard        → frequent access, most expensive
S3 Standard-IA     → infrequent access, cheaper storage + retrieval fee
S3 Glacier         → archive, very cheap, minutes-hours to retrieve
S3 Glacier Deep    → deepest archive, cheapest, hours to retrieve

Use lifecycle policies to auto-transition old data to cheaper tiers.
```

## Quick Cost Check

```bash
# This month's cost by service
aws ce get-cost-and-usage \
  --time-period Start=2026-08-01,End=2026-08-31 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# Set a budget alert so you're never surprised
aws budgets create-budget --account-id 123456789012 \
  --budget '{"BudgetName":"monthly","BudgetLimit":{"Amount":"1000","Unit":"USD"},"TimeUnit":"MONTHLY","BudgetType":"COST"}'
```

> For deeper coverage of tagging and Cost Explorer, see
> [Cost Visibility & Tagging](03-cost-visibility-tagging.md) and
> [AWS Cost Explorer](04-aws-cost-explorer.md).

---

## 🎯 Interview Quick Points

- AWS uses a **pay-as-you-go** model — you trade owning hardware for paying only for what you consume
- The four core cost dimensions: **compute, storage, data transfer, and managed services**
- **Data transfer** (especially egress to the internet and cross-region) is the most common "surprise" on a bill
- Different services meter differently: EC2 by the hour, S3 by volume, Lambda per invocation
- Most waste comes from the gap between **provisioned** and **actually-used** capacity
- The two highest-leverage basic actions: **turn off what you don't need** and **right-size what you do**
- **On-demand** is flexible but priciest; **Reserved Instances / Savings Plans** trade commitment for discount; **Spot** trades reliability for up to ~90% off
- Storage tiers (S3 Standard → IA → Glacier → Deep Archive) let you match cost to access frequency
- **Tagging** is the prerequisite for attributing AWS costs to teams, environments, and projects
- Treat cost as a **first-class engineering signal**, alongside latency and error rate
- The **AWS Free Tier** helps you learn, but always set a budget alert to avoid accidental charges
- Consolidated billing across an AWS Organization aggregates usage for bigger volume discounts
