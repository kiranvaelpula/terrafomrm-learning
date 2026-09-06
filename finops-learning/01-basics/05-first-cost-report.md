# Building Your First Cost Report

## Overview

A cost report turns raw billing data into an actionable story. This chapter builds a simple, repeatable report from AWS cost data.

---

## 📖 Understanding Your First Cost Report (Intuition First)

A cost report is to your cloud bill what a fitness tracker's weekly summary is to your daily steps. The raw data is already there — every charge, every resource — but it's overwhelming and shapeless until someone organizes it into a story: here's what you spent, here's how it compares to last time, here's what's trending up, and here's what to do about it. Your first cost report is about turning noise into that story.

The reason a *report* matters more than raw data is attention. Nobody logs into a billing console every day, but a report lands in front of the right people at the right cadence and answers the three questions they actually care about: **How much did we spend? Is that normal? What should we do?** A good report is opinionated — it doesn't just dump numbers, it highlights the finding and recommends an action.

A useful mental model is the **inverted pyramid** from journalism. Lead with the headline (total spend, versus budget, versus last month). Then the key findings (the spike, the surprise service, the orphaned resources). Then the supporting detail (per-service and per-team breakdowns) for those who want to dig in. Executives read the top; engineers read the bottom; both are served by one document.

The first report you build should be **simple and repeatable**, not comprehensive. It's better to ship a five-line summary that goes out every Monday than a beautiful 40-page analysis that runs once and never again. Consistency is what lets people spot trends — the same shape of report week after week trains the eye to notice when something changes.

Finally, a cost report is only valuable if it drives a decision. Every report should end with **actions and owners**: "S3 grew 40% — add lifecycle policies (owner: platform team)." Without that, a report is just interesting trivia. With it, the report becomes the heartbeat of your FinOps practice — the recurring moment where visibility turns into action.

---

## Report Structure (Inverted Pyramid)

```
┌────────────────────────────────────────┐
│ HEADLINE                                 │
│ Total: $47,200 | Budget: $50K | +8% MoM  │  ← executives read this
├────────────────────────────────────────┤
│ KEY FINDINGS                             │
│ • S3 up 40% — no lifecycle policies      │
│ • 12 idle volumes ($340/mo waste)        │
│ • Anomaly: data transfer spike Aug 14    │
├────────────────────────────────────────┤
│ DETAIL (per-service, per-team breakdown) │  ← engineers read this
└────────────────────────────────────────┘
```

## Building the Report in Python

```python
import boto3
from datetime import datetime, timedelta

ce = boto3.client("ce")

def build_cost_report(start, end):
    # Total cost + breakdown by service
    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    services = []
    total = 0.0
    for group in resp["ResultsByTime"][0]["Groups"]:
        name = group["Keys"][0]
        cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
        if cost > 0:
            services.append((name, cost))
            total += cost

    services.sort(key=lambda x: x[1], reverse=True)

    # Build the report
    print(f"═══ Cost Report: {start} to {end} ═══")
    print(f"TOTAL: ${total:,.2f}\n")
    print("Top services:")
    for name, cost in services[:10]:
        pct = cost / total * 100
        print(f"  {name:40} ${cost:>10,.2f}  ({pct:.1f}%)")

    return total, services

build_cost_report("2026-08-01", "2026-08-31")
```

## Adding Month-over-Month Comparison

```python
def month_over_month():
    this_month, _ = build_cost_report("2026-08-01", "2026-08-31")
    last_month, _ = build_cost_report("2026-07-01", "2026-07-31")
    change = (this_month - last_month) / last_month * 100
    trend = "📈 up" if change > 0 else "📉 down"
    print(f"\nMoM change: {trend} {abs(change):.1f}%")
```

## Automating Delivery (Weekly Email/Slack)

```python
# Schedule via Lambda + EventBridge (cron weekly), send to Slack
import requests

def send_report(report_text, webhook):
    requests.post(webhook, json={"text": f"```{report_text}```"})

# EventBridge rule: cron(0 9 ? * MON *)  → 9 AM every Monday
```

## Make It Actionable

```
Every report should end with ACTIONS + OWNERS:

  Action Items:
  □ Add S3 lifecycle policies (owner: platform team) — save ~$800/mo
  □ Delete 12 idle volumes (owner: infra team) — save $340/mo
  □ Investigate Aug 14 transfer spike (owner: on-call)
```

## Best Practices

- Keep the first report **simple** — a 5-line summary beats a 40-page analysis nobody reads
- **Consistent format** each period so the eye learns to spot changes
- **Group by tag** (team/project) once tagging is in place
- Include **budget vs actual** and a **forecast**
- **Automate delivery** so it reaches people without manual effort
- Always end with **actions and owners**

---

## 🎯 Interview Quick Points

- A cost report turns raw billing data into a **story**: how much, is it normal, what to do
- Structure it like an **inverted pyramid**: headline → key findings → supporting detail
- The headline should always include **total spend, vs budget, and vs last period**
- Make the first report **simple and repeatable** — consistency beats comprehensiveness for spotting trends
- Every report must end with **actions and owners**, or it's just trivia
- Source the data from **Cost Explorer API** or **Cost and Usage Reports (CUR)**; group by service and by tag
- Serve multiple audiences in one doc: **executives read the top, engineers read the bottom**
- Automate delivery on a **regular cadence** (e.g., weekly email) so it reaches people without effort
- Call out **anomalies and orphaned/idle resources** explicitly — these are the quickest wins
- Include a **month-over-month trend and forecast**, not just a snapshot
- Tie spend to **business context** where possible (e.g., cost per customer) to show value, not just numbers
- A recurring report is the **heartbeat of FinOps** — the moment visibility becomes action
