# Unit Economics for Cloud

## Overview

Unit economics divides total cloud cost by a business metric (customer, order, request) to reveal true efficiency — the most important FinOps concept.

---

## 📖 Understanding Unit Economics for Cloud (Intuition First)

Unit economics is the practice of dividing your total cloud cost by something the business actually cares about — a customer, an order, an API call — to get a "cost per unit." Think of it like a restaurant knowing the food cost of a single dish rather than just its total grocery bill. The grocery total tells you what you spent; the cost-per-dish tells you whether the menu is profitable and where to raise prices or cut portions.

The reason this matters is that a growing cloud bill is only scary without context. If your bill went up 40% but you served twice as many customers, your *efficiency actually improved* — each customer now costs less to serve. Total spend can't reveal that; cost per unit can. It turns "we're spending more" (alarming) into "we're spending less per customer" (reassuring) — the same data, a completely different story.

Choosing the right unit is the crux. It has to be a number the business already tracks and cares about: cost per monthly active user for SaaS, cost per transaction for e-commerce, cost per thousand requests for an API platform. A good unit lets a non-technical executive instantly judge whether growth is healthy. A purely technical unit (cost per container) fails that test.

The real value shows up in the **trend line**. One number in isolation is meaningless; a sequence — "$0.20 → $0.17 → $0.14 per transaction over a quarter" — tells a crisp story of engineering discipline paying off. It also reframes optimization work from vague "cost cutting" into measurable business improvement that leadership can celebrate and fund.

Ultimately, unit economics is the bridge between infrastructure and strategy. When engineering can say "at today's cost per user we break even at 3M users, and here's how to lower that threshold," cloud decisions become business decisions. That's the whole point: making technical spend legible in the language executives use to run the company.

---

## The Core Formula

```
Unit Cost = Total Cloud Cost / Number of Business Units

Examples:
  SaaS:       $500K / 50,000 users        = $10 per user/month
  E-commerce: $200K / 2,000,000 orders    = $0.10 per order
  API:        $80K  / 800M requests       = $0.0001 per request
```

## Why It Beats Total Spend

```
Scenario: bill went from $1M → $1.4M (up 40%). Panic?

Add context (units):
  Before: $1M / 100K customers = $10.00/customer
  After:  $1.4M / 200K customers = $7.00/customer

Efficiency IMPROVED 30% per customer, even though the total rose.
Total spend alone would have told the wrong story.
```

## Choosing the Right Unit

```
Good units (business cares, executives understand):
  - Cost per monthly active user (SaaS)
  - Cost per transaction/order (e-commerce)
  - Cost per 1,000 API requests (platform)
  - Cost per GB processed (data pipeline)

Bad units (too technical, no business meaning):
  - Cost per container
  - Cost per CPU hour
```

## Calculating Unit Cost (example)

```python
import boto3

def cost_per_customer(month_start, month_end, active_customers):
    ce = boto3.client("ce")
    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": month_start, "End": month_end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
    )
    total = float(resp["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"])
    unit_cost = total / active_customers
    print(f"Total: ${total:,.0f} | Customers: {active_customers:,} | "
          f"Cost/customer: ${unit_cost:.2f}")
    return unit_cost

cost_per_customer("2026-08-01", "2026-08-31", active_customers=200_000)
```

## Using Unit Economics

```
- Track the TREND over time (is cost/unit going down as you scale?)
- Compare across products/features (which are efficient?)
- Tie to pricing (are you charging enough to cover unit cost + margin?)
- Set targets (e.g., reduce cost/customer by 15% this year)
```

> This is a companion summary. For the full deep-dive with allocation
> and margin analysis, see [Unit Economics](05-unit-economics.md).

---

## 🎯 Interview Quick Points

- **Unit economics** = total cloud cost ÷ a business unit (user, transaction, request, GB)
- It gives context a total bill can't: rising spend can still mean **improving efficiency per unit**
- Pick a **business-meaningful unit** — cost per MAU (SaaS), per order (e-commerce), per 1K requests (API)
- The **trend over time** matters far more than any single snapshot
- Include **all** relevant costs (infra + payment fees + third-party APIs) for a true unit cost
- Use it to find **breakeven points** and judge whether growth is profitable
- Present it to executives in **business terms**: margin, cost as % of revenue, breakeven volume
- Segment by **customer tier** to see which segments actually make money
- It reframes optimization as **measurable business impact**, not vague cost cutting
- Common levers to improve unit cost: **caching, right-sizing, Graviton/ARM, and commitment discounts**
- It's how engineering demonstrates value and earns a **seat at the strategy table**
- Watch for **fixed vs variable** costs — at low volume, fixed overhead inflates the per-unit number
