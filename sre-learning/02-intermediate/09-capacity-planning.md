# Capacity Planning

## Overview

Capacity planning ensures a system has enough resources to meet demand reliably and cost-effectively — not too little (outages) and not too much (wasted money).

## 📖 Understanding Capacity Planning (Intuition First)

Think about planning a restaurant's seating and staff. Too few tables and cooks, and you turn away customers and get bad reviews (an outage). Too many, and you're paying for empty chairs and idle staff (wasted cost). And it changes constantly — a quiet Tuesday needs far less than a Friday night or a holiday. Capacity planning is answering, continuously: *how much do we need to handle demand well, without overpaying?*

For systems, the same balance applies to CPU, memory, storage, network, and instance counts. Under-provision and you get slow responses, errors, and outages when traffic spikes. Over-provision and you burn money on resources sitting idle. The art is matching capacity to actual demand — with enough headroom to absorb spikes and failures, but not so much that you're lighting money on fire.

What makes it genuinely hard is that demand is **uncertain and changing.** Traffic grows as your product succeeds, spikes during launches or sales (Black Friday), and has daily and weekly rhythms. So capacity planning isn't a one-time calculation — it's a continuous forecasting exercise. You look at historical growth, model future demand, add headroom for the unexpected, and revisit regularly as reality diverges from the forecast.

The cloud changed this dramatically. In the old data-center world, you had to buy servers months ahead and guess — over-provisioning was the only safe choice. In the cloud, **auto-scaling** lets capacity follow demand in near-real-time: add instances when traffic rises, remove them when it falls. This shifts capacity planning from "buy enough for peak forever" to "set the right scaling rules and headroom." But auto-scaling isn't magic — it has limits (scaling takes time, some resources can't scale instantly), so you still plan.

The SRE angle ties capacity directly to reliability: **running out of capacity is a reliability failure.** A service that falls over under load has failed its SLO just as surely as one with a bug. So SREs treat capacity as a first-class reliability concern — forecasting demand, load-testing to find limits, setting autoscaling with headroom, and planning for both organic growth and sudden spikes.

---

## Key Concepts

```
DEMAND     — how much load (requests/sec, users, data)
CAPACITY   — how much the system can handle
HEADROOM   — buffer above expected demand (for spikes + failures)
UTILIZATION — how much of capacity is currently used

Goal: capacity = peak demand + headroom, adjusted continuously
```

## Types of Scaling

```
VERTICAL (scale up):    bigger instance (more CPU/RAM)
                        Simple, but has a ceiling and downtime to resize

HORIZONTAL (scale out): more instances
                        Scales further, no single-instance limit (preferred)

AUTO-SCALING:           add/remove instances automatically based on metrics
                        Follows demand in near-real-time
```

## Capacity Planning Process

```
1. MEASURE current usage (CPU, memory, requests, latency at load)
2. FORECAST future demand (growth trend + known events)
3. LOAD TEST to find the breaking point (how much can one instance handle?)
4. CALCULATE needed capacity = forecast demand / per-instance capacity
5. ADD HEADROOM for spikes and failures (e.g., N+2 redundancy)
6. CONFIGURE autoscaling with the right thresholds
7. MONITOR and REVISIT as reality diverges from forecast
```

## Headroom & Redundancy

```
N     — exactly enough for current load (no safety margin — risky)
N+1   — one extra (survives losing one instance)
N+2   — two extra (survives losing one during maintenance of another)

Also keep headroom for TRAFFIC SPIKES (autoscaling takes time to react).
Common target: run at ~50-70% utilization, leaving room to absorb spikes.
```

## Forecasting Demand (example)

```python
from prophet import Prophet
import pandas as pd

# Historical daily request volume
df = pd.DataFrame({
    "ds": pd.date_range("2026-01-01", periods=180, freq="D"),
    "y": historical_daily_requests,
})

model = Prophet()
model.fit(df)

# Forecast next 90 days
future = model.make_future_dataframe(periods=90)
forecast = model.predict(future)

peak_forecast = forecast["yhat_upper"].max()   # upper bound = plan for this
print(f"Forecast peak demand: {peak_forecast:,.0f} requests/day")

# Capacity needed
per_instance_capacity = 50000  # from load testing
instances_needed = (peak_forecast / per_instance_capacity)
instances_with_headroom = int(instances_needed * 1.3) + 1   # 30% headroom + N+1
print(f"Instances needed (with headroom): {instances_with_headroom}")
```

## Auto-Scaling Configuration (example)

```yaml
# Kubernetes Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: payment-service
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: payment-service
  minReplicas: 3          # never below N+2 for HA
  maxReplicas: 20         # ceiling to cap cost
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60   # scale up before hitting limits
```

## Load Testing

```
Find the breaking point BEFORE production does:
- Tools: k6, JMeter, Locust, Gatling
- Ramp up load until latency/errors degrade → that's your per-instance limit
- Test failure scenarios (what happens when an instance dies under load?)
- Run "game days" simulating peak events (Black Friday rehearsal)
```

---

## 🎯 Interview Quick Points

- Capacity planning balances **too little (outages) vs too much (wasted cost)**
- Analogy: restaurant seating/staff — match to demand with a buffer
- **Running out of capacity is a reliability failure** — SREs own it
- Horizontal scaling (more instances) is preferred over vertical (bigger instance)
- **Auto-scaling** follows demand in near-real-time — but it takes time to react, so keep headroom
- Process: measure → forecast → load test → calculate → add headroom → autoscale → revisit
- **Headroom**: N+1/N+2 redundancy plus spike buffer (run at ~50-70% utilization)
- **Load testing** finds the breaking point before production does
- Forecast with historical trends + known events (launches, sales)
- Cloud shifted planning from "buy for peak forever" to "set scaling rules + headroom"

## Next Steps

Continue to [Reliability Patterns](../03-advanced/10-reliability-patterns.md).
