# Error Budgets

## Overview

An error budget is the amount of unreliability you're allowed before breaching your SLO. It's SRE's most powerful and distinctive idea — it turns reliability into a currency you can spend.

## 📖 Understanding Error Budgets (Intuition First)

Here's the tension every engineering org lives with: developers want to ship features fast (which risks breaking things), and operations wants stability (which means shipping less). These two goals fight forever — until error budgets resolve the fight with a number.

The insight is simple. If your SLO is 99.9% availability, then you're *allowed* to be down 0.1% of the time. That 0.1% isn't failure — it's a **budget**. Think of it like a monthly spending allowance. You have, say, 43 minutes of "allowed downtime" this month. You can spend that budget however you like: on risky feature launches, on experiments, on planned maintenance. As long as you haven't run out, you're free to move fast.

This flips the whole conversation. Instead of Ops saying "no, too risky" and Dev saying "ship it anyway," both look at the same dashboard: *how much error budget is left?* Budget remaining? Ship freely, take risks, launch that feature. Budget exhausted? Stop shipping risky changes and focus on reliability until the budget recovers. The number decides, not the loudest voice in the room.

The beauty is that it aligns incentives. Developers now *care* about reliability because breaking things burns the budget they need to ship features. And reliability work gets prioritized automatically — not because someone insisted, but because the budget ran out. It's a self-regulating system that keeps you both fast AND reliable.

It also reframes failure in a healthy way. A little downtime isn't a disaster to be punished — it's expected, budgeted-for, and fine, as long as you stay within budget. This removes fear and blame, and lets teams take the calculated risks that innovation requires.

---

## The Math

```
Error Budget = 100% - SLO

SLO = 99.9%  →  Error budget = 0.1%

Over 30 days (43,200 minutes):
  0.1% × 43,200 = 43.2 minutes of allowed "downtime"/errors per month

SLO = 99.95%  →  0.05%  →  21.6 minutes/month
SLO = 99.99%  →  0.01%  →  4.32 minutes/month
```

## How Error Budgets Drive Decisions

```
┌─────────────────────────────────────────────┐
│  Budget REMAINING (healthy)                   │
│  → Ship features, take risks, experiment      │
│  → Fast release cadence                       │
├─────────────────────────────────────────────┤
│  Budget LOW (running out)                     │
│  → Slow down risky changes                    │
│  → Add extra testing/review                   │
├─────────────────────────────────────────────┤
│  Budget EXHAUSTED (SLO breached)              │
│  → FREEZE risky releases                      │
│  → Focus 100% on reliability until recovered  │
└─────────────────────────────────────────────┘
```

## Error Budget Policy

A written agreement (between dev and SRE) on what happens at each budget level:

```
Example policy:
- Budget > 50% remaining: normal operations, ship freely
- Budget 10-50%: proceed with caution, extra review on risky changes
- Budget < 10%: only reliability fixes and low-risk changes
- Budget exhausted: feature freeze until budget recovers
  (agreed IN ADVANCE, so it's not a fight in the moment)
```

## Calculating Error Budget Burn

```python
def error_budget_status(slo, actual_availability, window_minutes=43200):
    """Show how much error budget is left."""
    total_budget = (100 - slo) / 100 * window_minutes    # allowed bad minutes
    consumed = (100 - actual_availability) / 100 * window_minutes
    remaining = total_budget - consumed
    remaining_pct = (remaining / total_budget) * 100 if total_budget else 0

    print(f"Total budget:    {total_budget:.1f} min")
    print(f"Consumed:        {consumed:.1f} min")
    print(f"Remaining:       {remaining:.1f} min ({remaining_pct:.0f}%)")

    if remaining <= 0:
        print("Status: EXHAUSTED — freeze risky releases")
    elif remaining_pct < 10:
        print("Status: LOW — caution")
    else:
        print("Status: HEALTHY — ship freely")

error_budget_status(slo=99.9, actual_availability=99.95)
```

## Burn Rate

```
Burn rate = how FAST you're consuming the budget.

1x burn rate = consuming budget exactly at the SLO threshold
10x burn rate = burning 10x faster → will exhaust budget quickly → ALERT!

Fast burn (e.g., 14x over 1 hour) → page immediately (major incident)
Slow burn (e.g., 2x over 6 hours)  → ticket, investigate soon

This is the modern, SLO-based approach to alerting — alert on burn
rate, not on every metric blip.
```

---

## 🎯 Interview Quick Points

- Error budget = 100% − SLO (the allowed amount of unreliability)
- It turns reliability into a **budget you can spend** on risk/features
- Resolves the **dev-velocity vs ops-stability tension** with a number, not arguments
- Budget remaining → ship fast; budget exhausted → freeze risky releases
- **Error budget policy** is agreed IN ADVANCE so it's not a fight during a crisis
- Aligns incentives: devs care about reliability because breakage burns their budget
- Reframes small failures as expected/budgeted, not disasters — reduces blame
- **Burn rate** = how fast you're consuming budget; alert on fast burn
- SLO-based **burn-rate alerting** is superior to alerting on every metric spike
- 99.9% SLO ≈ 43 min/month of error budget

## Next Steps

Continue to [Monitoring & Observability](04-monitoring-observability.md).
