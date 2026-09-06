# Complete FinOps Dashboard

**Lab Objective**: Hands-on practice with FinOps concepts

---

## Overview

This lab will guide you through implementing complete finops dashboard in a real AWS environment.

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
aws configure   # Cost Explorer read access
```
This capstone lab combines tagging, allocation, unit economics, and automation into one dashboard/report.

### Step 2: Implementation — Pull the Key Metrics
```python
import boto3

ce = boto3.client("ce")

def dashboard(start, end, active_customers):
    # 1. Total spend
    total_resp = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY", Metrics=["UnblendedCost"])
    total = float(total_resp["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"])

    # 2. By service
    svc_resp = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY", Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}])

    # 3. Unit economics
    cost_per_customer = total / active_customers

    print("═══════════ FinOps Dashboard ═══════════")
    print(f"Total spend:       ${total:,.2f}")
    print(f"Cost per customer: ${cost_per_customer:.2f}")
    print("\nTop services:")
    services = sorted(
        [(g["Keys"][0], float(g["Metrics"]["UnblendedCost"]["Amount"]))
         for g in svc_resp["ResultsByTime"][0]["Groups"]],
        key=lambda x: x[1], reverse=True)
    for name, cost in services[:8]:
        print(f"  {name:35} ${cost:>10,.2f}")

dashboard("2026-08-01", "2026-08-31", active_customers=200_000)
```

### Step 3: Verification
- Total matches your bill; unit cost matches your customer count
- Service breakdown sums to the total
- Optionally visualize with QuickSight, Grafana, or a Cost Explorer dashboard

### Step 4: Optimization
- Add month-over-month trend and a forecast
- Add per-team allocation (group by Team tag)
- Flag anomalies and idle resources automatically
- Schedule the dashboard to publish weekly (Lambda + EventBridge + Slack)

---

## Expected Outcomes

After completing this lab, you will:
- Build an end-to-end FinOps dashboard combining spend, allocation, and unit economics
- Present cost data as an actionable story for both execs and engineers
- Have a repeatable, automatable reporting foundation

---

## 🎯 Interview Quick Points
- A complete FinOps dashboard shows **total spend, per-service, per-team, and unit economics** together
- Serve both audiences: **headline for execs, detail for engineers**
- Always include **trend + forecast**, not just a snapshot
- Automate delivery on a **regular cadence** so it drives action
- The dashboard is the **heartbeat of FinOps** — where visibility becomes decisions
