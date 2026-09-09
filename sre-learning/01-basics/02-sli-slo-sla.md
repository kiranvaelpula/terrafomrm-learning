# SLIs, SLOs, and SLAs

## Overview

SLIs, SLOs, and SLAs are the foundation of SRE — they turn "reliability" from a vague feeling into a measurable, agreed-upon target.

## 📖 Understanding SLIs, SLOs, and SLAs (Intuition First)

Imagine you run a pizza delivery business. You need a way to talk about "good service" that isn't just vibes. So you create three related things:

- An **SLI** (Service Level Indicator) is the *measurement* — "what percentage of pizzas arrived within 30 minutes?" It's the actual number you track: 97%.
- An **SLO** (Service Level Objective) is your *internal target* — "we aim to deliver 95% of pizzas within 30 minutes." It's the goal you hold yourselves to.
- An **SLA** (Service Level Agreement) is a *contractual promise to customers with consequences* — "if fewer than 90% arrive on time this month, you get a refund." Break it, and you pay.

The relationship is deliberate: **SLA < SLO < actual performance.** You promise customers less (SLA: 90%) than you target internally (SLO: 95%) so there's a safety buffer before you ever break a contract. You'd rather your team panics at the 95% internal line long before customers are affected at the 90% contractual line.

Why does this matter so much in SRE? Because reliability is meaningless without a number. "The system should be reliable" leads to endless arguments — one engineer thinks 99% is fine, another insists on 99.999%. An SLO ends the argument: *this* is our target, measured *this* way. Every decision — do we ship this risky feature? do we page someone at 3 AM? — can now be answered with data against the SLO instead of opinion.

The subtle genius is that the SLO defines what "reliable enough" means for *your* users specifically. A banking transaction needs far higher reliability than a "recommended for you" widget. SLOs force you to decide, per service, how good is good enough — and then everything else (alerting, error budgets, prioritization) flows from that one decision.

---

## The Three Terms Precisely

| Term | What it is | Audience | Example |
|------|-----------|----------|---------|
| **SLI** | The measurement (actual metric) | Internal | 99.95% of requests succeeded |
| **SLO** | The internal target | Internal | 99.9% of requests should succeed |
| **SLA** | Contractual promise + penalty | External (customers) | 99.5% or you get credits |

```
Relationship (with safety buffers):
  SLA (99.5%)  <  SLO (99.9%)  <  Actual/SLI (99.95%)
  promise less    target more     achieve most
```

## Common SLI Types

```
Availability:  % of successful requests
Latency:       % of requests faster than X ms
Throughput:    requests handled per second
Error rate:    % of failed requests
Durability:    % of data not lost (storage)
Correctness:   % of correct responses
```

## Writing a Good SLO

```
Formula: [X%] of [events] over [time window] meet [threshold]

Examples:
  "99.9% of HTTP requests over 30 days return in < 300ms"
  "99.95% of API calls over 28 days succeed (non-5xx)"

Good SLOs are:
- User-centric (measure what users experience)
- Measurable (from real data)
- Achievable (not 100%)
- Time-bounded (a rolling window)
```

## The "Nines" of Availability

```
99%      = ~3.65 days downtime/year   ("two nines")
99.9%    = ~8.76 hours/year           ("three nines")
99.95%   = ~4.38 hours/year
99.99%   = ~52.6 minutes/year         ("four nines")
99.999%  = ~5.26 minutes/year         ("five nines")

Each extra nine costs exponentially more. Pick what users need,
not the most nines possible.
```

## Measuring an SLI (example)

```python
def calculate_availability_sli(total_requests, successful_requests):
    """Availability SLI = successful / total."""
    return (successful_requests / total_requests) * 100

# From your metrics (e.g., Prometheus)
sli = calculate_availability_sli(total_requests=1_000_000,
                                 successful_requests=999_200)
print(f"Availability SLI: {sli:.3f}%")   # 99.920%

# Compare to SLO
SLO = 99.9
print("Meeting SLO" if sli >= SLO else "SLO BREACH")
```

---

## 🎯 Interview Quick Points

- **SLI** = the measurement, **SLO** = internal target, **SLA** = external contract with penalties
- The relationship: **SLA < SLO < actual performance** (buffer before breaking contracts)
- SLOs turn "reliable" from opinion into a **measurable, agreed number**
- Good SLOs are **user-centric, measurable, achievable, and time-bounded**
- SLO format: "X% of events over a window meet a threshold"
- Common SLIs: availability, latency, error rate, throughput, durability
- Know the "nines": 99.9% ≈ 8.76 hrs/year down; each nine costs exponentially more
- Pick reliability based on **what users need**, not the most nines possible
- The SLO drives everything downstream: error budgets, alerting, prioritization
- SLAs usually have financial penalties (credits/refunds); SLOs don't

## Next Steps

Continue to [Error Budgets](03-error-budgets.md).
