# Lab 01: SLO & Error Budget Calculator

## 🎯 Objective
Build a tool that tracks an SLO, calculates the error budget, and reports burn rate — the foundation of SRE decision-making.

## 📋 Prerequisites
```bash
python3 --version   # no external libs needed
```

## 🧪 Steps

### Step 1: Calculate error budget from an SLO
Run `slo_calculator.py`. See how a 99.9% SLO translates to ~43 min/month of allowed downtime.

### Step 2: Track budget consumption
Feed in actual availability and see how much budget remains.

### Step 3: Compute burn rate
See how fast the budget is being consumed and whether to alert.

## ✅ Expected Output
```
SLO: 99.9% | Window: 30 days
Total error budget: 43.2 minutes
Consumed: 21.6 min | Remaining: 21.6 min (50%)
Status: HEALTHY — ship freely
Burn rate: 1.0x (sustainable)
```

## 🏋️ Exercises
1. Add multiple SLOs (availability + latency) tracked together
2. Implement multi-window burn-rate alerting (fast burn vs slow burn)
3. Read real availability data from a CSV of daily uptime
4. Add an error-budget policy that recommends actions per budget level

## 🔑 Key Concepts Practiced
- SLO → error budget math
- Budget consumption tracking
- Burn rate and burn-rate alerting
- Error budget policy decisions
