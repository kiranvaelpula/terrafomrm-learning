# Multi-Account FinOps Strategy

## Overview

Large organizations run many AWS accounts. Managing cost across them requires consolidated billing, cross-account visibility, and centralized governance via AWS Organizations.

---

## 📖 Understanding Multi-Account FinOps (Intuition First)

A multi-account setup is like a company giving each department its own bank account instead of everyone sharing one. It sounds like more paperwork, but it's actually cleaner: each department's spending is naturally separated, one team can't accidentally spend another's budget, and the finance team gets a tidy roll-up of all accounts through a single master statement. In AWS, that master statement is **consolidated billing** under an AWS Organization, and the separate accounts are how large companies keep hundreds of teams from stepping on each other.

The reason organizations move to many accounts is that **accounts are the strongest boundary AWS offers** — for security, for blast-radius containment, and, importantly, for cost. When each team, environment, or product lives in its own account, cost allocation becomes almost free: the account *is* the boundary, so you don't even need perfect tagging to know who spent what. This is why account-based allocation is a favorite of large enterprises.

But this cleanliness comes at the cost of **complexity**, and that's the central tension of multi-account FinOps. Hundreds of accounts mean hundreds of places to set budgets, apply guardrails, and check for waste. You can't log into each one manually. So the discipline becomes managing the *fleet* centrally: organization-wide tag policies, Service Control Policies (SCPs) to prevent expensive misconfigurations, and cross-account automation that sweeps for waste everywhere at once.

A subtle but hugely valuable benefit is **commitment sharing**. Under consolidated billing, a Reserved Instance or Savings Plan bought in one account can automatically apply its discount to matching usage in *other* accounts. This means you plan commitments at the organization level against total baseline usage, rather than fragmenting purchases account by account — a major source of savings and a common thing to get wrong.

The overarching mental model is **hub and spoke**: a central "payer" or management account provides shared services, billing, and governance (the hub), while workload accounts (the spokes) run the actual applications within the guardrails. Multi-account FinOps is the art of getting the isolation benefits of separate accounts while avoiding the chaos — through centralized visibility, shared commitments, and automated governance across the whole tree.

---

## Why Multiple Accounts?

```
Separate accounts provide natural boundaries for:
- Environments (prod / staging / dev)
- Teams / business units
- Security isolation (blast radius)
- Cost allocation (per-account = per-team billing)

But this creates a challenge: how do you see and control cost
across dozens or hundreds of accounts?
```

## AWS Organizations & Consolidated Billing

```
                Management Account (payer)
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   Prod OU         Non-Prod OU      Sandbox OU
   ├─ prod-app     ├─ dev-app       └─ experiments
   └─ prod-data    └─ staging-app

Consolidated Billing benefits:
- ONE bill for all accounts
- Volume discounts aggregated across accounts (tiered pricing)
- RIs / Savings Plans SHARED across all accounts automatically
- Centralized cost allocation and reporting
```

## Cross-Account Cost Visibility

```python
import boto3

# Cost Explorer at the Organization level (run in management account)
ce = boto3.client("ce")

response = ce.get_cost_and_usage(
    TimePeriod={"Start": "2026-08-01", "End": "2026-08-31"},
    Granularity="MONTHLY",
    Metrics=["UnblendedCost"],
    GroupBy=[{"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"}]  # cost per account
)

for group in response["ResultsByTime"][0]["Groups"]:
    account = group["Keys"][0]
    cost = group["Metrics"]["UnblendedCost"]["Amount"]
    print(f"Account {account}: ${float(cost):.2f}")
```

## Governance with SCPs (Service Control Policies)

```json
// Attached to an OU — applies to ALL accounts under it
// Example: prevent leaving the org's approved regions
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "NotAction": ["iam:*", "organizations:*", "route53:*"],
    "Resource": "*",
    "Condition": {
      "StringNotEquals": {
        "aws:RequestedRegion": ["us-east-1", "us-west-2"]
      }
    }
  }]
}
// Stops resources (and cost) sprawling into unexpected regions.
```

## Cost Allocation Across Accounts

```
Two levels of allocation:
1. ACCOUNT level — each account maps to a team/BU (natural chargeback)
2. TAG level — within accounts, tags allocate to projects/features

Activate cost allocation tags in the management account so they
appear in Cost Explorer and Cost and Usage Reports (CUR) org-wide.
```

## RI / Savings Plan Sharing

```
By default, commitment discounts are SHARED across all accounts in the org:
- Buy Savings Plans centrally in the management account
- Unused commitment in one account applies to usage in another
- Maximizes utilization (fewer wasted commitments)

You CAN turn off sharing per-account if a team funds its own commitments.
```

## Best Practices

- **Standardize account structure** (OUs by environment + business unit)
- **Enforce tagging** consistently across all accounts
- **Centralize commitment purchasing** for maximum sharing/utilization
- **Use SCPs** as guardrails (regions, instance types, required tags)
- **Aggregate reporting** via CUR + Athena or a FinOps tool
- **Per-account budgets and anomaly detection** for early warning

## Common Pitfalls

- **Account sprawl** — accounts created without governance become cost black holes
- **Inconsistent tagging** across accounts breaks allocation
- **Commitment silos** — not sharing RIs/SPs leaves discounts unused
- **No central visibility** — can't optimize what you can't see

---

## 🎯 Interview Quick Points

- Multi-account setups give each team/env/product its own AWS account — the **strongest boundary** AWS offers
- **Consolidated billing** under an AWS Organization rolls all accounts into one bill and aggregates discounts
- **Account = boundary** makes cost allocation almost free without needing perfect tagging
- The trade-off is **complexity** — hundreds of accounts means managing the fleet centrally, not one by one
- Govern centrally with **tag policies, Service Control Policies (SCPs), and cross-account automation**
- **Commitment sharing**: an RI/Savings Plan in one account auto-applies to matching usage in others
- Plan commitments at the **organization level** against total baseline, not fragmented per account
- Use a **hub-and-spoke** model: management/payer account for billing + governance, workload accounts for apps
- Aggregate cost data centrally (CUR to a central S3, org-wide Cost Explorer) for fleet-wide visibility
- Watch for **account sprawl** — every account needs budgets, guardrails, and cleanup automation
- Landing zones / Control Tower help **standardize** new accounts with cost guardrails from day one
- The goal: **isolation benefits of separate accounts without the chaos** — via central visibility and automation
