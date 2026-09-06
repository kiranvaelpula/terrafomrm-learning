# Unit Economics Dashboard

**Lab Objective**: Hands-on practice with FinOps concepts

---

## Overview

This lab will guide you through implementing unit economics dashboard in a real AWS environment.

**Prerequisites:**
- AWS account with billing access
- AWS CLI configured
- Basic Python knowledge

**Time Required**: 60-90 minutes

---

## Lab Steps

### Step 1: Environment Setup
```bash
pip install boto3
aws configure   # Cost Explorer read access
```
Decide your business unit (e.g., active customers, orders, API requests) and how you'll get that number (from your app DB or analytics).

### Step 2: Implementation — Calculate Cost per Unit
```python
import boto3

ce = boto3.client("ce")

def cost_per_unit(start, end, units, unit_name="customer"):
    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
    )
    total = float(resp["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"])
    unit_cost = total / units
    print(f"Total: ${total:,.0f} | {units:,} {unit_name}s | "
          f"${unit_cost:.4f} per {unit_name}")
    return unit_cost

cost_per_unit("2026-08-01", "2026-08-31", units=200_000, unit_name="customer")
```

### Step 3: Verification — Track the Trend
```python
# Compare unit cost across months — is it going DOWN as you scale?
for month, (start, end, users) in {
    "Jun": ("2026-06-01","2026-06-30",150_000),
    "Jul": ("2026-07-01","2026-07-31",175_000),
    "Aug": ("2026-08-01","2026-08-31",200_000),
}.items():
    uc = cost_per_unit(start, end, users)
    print(f"{month}: ${uc:.4f}/customer")
# Healthy sign: unit cost decreasing as customers increase
```

### Step 4: Optimization
- If unit cost is rising as you scale → investigate inefficiency
- Break down unit cost by feature/product to find expensive areas
- Tie unit cost to pricing to confirm healthy gross margin

---

## Expected Outcomes

After completing this lab, you will:
- Calculate cost per business unit (customer/order/request)
- Track unit-cost trends over time
- Explain why unit economics beats total-spend as a health metric

---

## 🎯 Interview Quick Points
- Unit cost = total cloud cost / business units (customers, orders, requests)
- Reveals efficiency that total spend hides (bill up 40% but cost/customer down = good)
- Choose a unit the **business** understands, not a technical one
- Track the **trend** — unit cost should fall as you scale efficiently
- Ties cost directly to **pricing and gross margin**
