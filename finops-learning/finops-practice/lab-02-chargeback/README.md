# Team Chargeback System

**Lab Objective**: Hands-on practice with FinOps concepts

---

## Overview

This lab will guide you through implementing team chargeback system in a real AWS environment.

**Prerequisites:**
- AWS account with billing access
- AWS CLI configured
- Basic Python knowledge

**Time Required**: 60-90 minutes

---

## Lab Steps

### Step 1: Environment Setup
```bash
pip install boto3 pandas
aws configure   # needs Cost Explorer + tagging read access
```
Ensure your resources are tagged with a `Team` cost-allocation tag, and that the tag is **activated** in Billing → Cost Allocation Tags.

### Step 2: Implementation — Allocate Cost by Team
```python
import boto3

ce = boto3.client("ce")

def cost_by_team(start, end):
    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "TAG", "Key": "Team"}],   # allocate by Team tag
    )
    print(f"═══ Chargeback: {start} to {end} ═══")
    for group in resp["ResultsByTime"][0]["Groups"]:
        team = group["Keys"][0].split("$")[-1] or "untagged"
        cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
        print(f"  {team:20} ${cost:>10,.2f}")

cost_by_team("2026-08-01", "2026-08-31")
```

### Step 3: Verification
- Confirm the total across teams matches your total bill
- Check the "untagged" bucket — high untagged cost means poor tagging hygiene
- Cross-check one team's number against Cost Explorer filtered by that tag

### Step 4: Optimization
- Drive down the **untagged** portion by enforcing tags (AWS Config rule)
- Split shared costs (e.g., NAT, logging) fairly across teams
- Decide **showback** (inform teams) vs **chargeback** (actually bill them)

---

## Expected Outcomes

After completing this lab, you will:
- Allocate AWS cost to teams using cost-allocation tags
- Produce a per-team chargeback/showback report
- Understand the impact of untagged resources on allocation accuracy

---

## 🎯 Interview Quick Points
- **Showback** = show teams their cost; **chargeback** = actually bill them
- Allocation depends on **cost-allocation tags** being applied AND activated
- Untagged resources are the enemy of accurate chargeback
- Shared costs (NAT, logging, cluster) need a fair split rule
- Group Cost Explorer by TAG to allocate; group by LINKED_ACCOUNT for account-based chargeback
