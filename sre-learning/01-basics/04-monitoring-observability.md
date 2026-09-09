# Monitoring & Observability

## Overview

Monitoring and observability let SREs understand what their systems are doing. You cannot maintain reliability for something you can't see.

## 📖 Understanding Monitoring & Observability (Intuition First)

Think of your car's dashboard. The speedometer, fuel gauge, and temperature light are **monitoring** — they track known things you decided in advance to watch. They answer "known questions": Am I speeding? Is the tank empty? Is the engine overheating? Monitoring is great when you already know what could go wrong.

But now imagine a weird new noise from the engine that no dashboard light explains. You need to open the hood, probe around, and investigate an *unknown* problem. That ability to ask arbitrary new questions about your system — to explore the "unknown unknowns" — is **observability**. Monitoring tells you *that* something is wrong; observability helps you figure out *why*.

The distinction matters more than ever because modern systems are absurdly complex — hundreds of microservices, containers appearing and vanishing, distributed across regions. You literally cannot predict every failure mode in advance to set up a dashboard for it. So you instrument your systems to emit rich data, and observability tools let you slice and explore that data to answer questions you never anticipated.

Observability rests on **three pillars**: metrics (numbers over time — "CPU is 90%"), logs (discrete events — "user X got error Y at time Z"), and traces (the journey of one request across all services — "this request spent 800ms in the payment service"). Metrics tell you something's wrong, logs tell you what happened, and traces tell you where in the tangle of services it happened. Together they turn a mysterious outage into a solvable puzzle.

The SRE mindset here is crucial: you don't bolt on monitoring after something breaks. You **design observability in from the start**, because in a 3 AM incident, the difference between resolving it in 5 minutes versus 5 hours is entirely whether you can *see* what your system is doing.

---

## Monitoring vs Observability

| Aspect | Monitoring | Observability |
|--------|-----------|---------------|
| Answers | Known questions | Unknown questions |
| Approach | Pre-defined dashboards/alerts | Ad-hoc exploration |
| "Is it broken?" | ✅ | ✅ |
| "WHY is it broken?" | Limited | ✅ |
| Data | Aggregated metrics | High-cardinality, rich |

## The Three Pillars of Observability

```
1. METRICS — numbers over time (aggregated)
   "Request rate: 5000/s, error rate: 0.2%, p99 latency: 250ms"
   Tools: Prometheus, CloudWatch, Datadog

2. LOGS — discrete timestamped events
   "[14:30:01] ERROR payment-svc: DB connection timeout, trace=abc123"
   Tools: ELK, Loki, Splunk, CloudWatch Logs

3. TRACES — the path of ONE request across services
   "Request abc123: gateway(10ms) → auth(20ms) → payment(800ms!) → db(50ms)"
   Tools: Jaeger, Zipkin, AWS X-Ray, OpenTelemetry
```

## The Four Golden Signals (Google SRE)

The four metrics to monitor for ANY user-facing system:

```
1. LATENCY   — how long requests take (watch p50, p95, p99)
2. TRAFFIC   — how much demand (requests/sec)
3. ERRORS    — rate of failed requests
4. SATURATION — how "full" the system is (CPU, memory, disk, queue depth)

If you can only monitor four things, monitor these.
```

## RED and USE Methods

```
RED (for services/requests):
  Rate       — requests per second
  Errors     — failed requests
  Duration   — latency distribution

USE (for resources):
  Utilization — % busy (CPU, memory)
  Saturation  — how much extra work is queued
  Errors      — error count
```

## Example: Prometheus Metric + Alert

```python
# Instrument your app
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('http_requests_total', 'Total requests', ['status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Latency')

@REQUEST_LATENCY.time()
def handle_request(req):
    try:
        result = process(req)
        REQUEST_COUNT.labels(status='success').inc()
        return result
    except Exception:
        REQUEST_COUNT.labels(status='error').inc()
        raise
```

```yaml
# Alert on SLO burn rate (Prometheus alerting rule)
groups:
- name: slo_alerts
  rules:
  - alert: HighErrorRate
    expr: |
      sum(rate(http_requests_total{status="error"}[5m]))
      / sum(rate(http_requests_total[5m])) > 0.01
    for: 5m
    labels:
      severity: page
    annotations:
      summary: "Error rate above 1% for 5 minutes"
```

## Good Alerting Principles

```
- Alert on SYMPTOMS (users affected), not causes (one server's CPU)
- Alert on SLO burn rate, not every metric blip
- Every alert should be ACTIONABLE (if you can't act, it's noise)
- Avoid alert fatigue — too many alerts = ignored alerts
- Page for urgent; ticket for non-urgent
```

---

## 🎯 Interview Quick Points

- **Monitoring** = known questions (dashboards/alerts); **observability** = unknown questions (exploration)
- Monitoring says *that* it's broken; observability helps find *why*
- **Three pillars**: metrics (numbers), logs (events), traces (request journeys)
- **Four Golden Signals**: Latency, Traffic, Errors, Saturation
- **RED** (Rate, Errors, Duration) for services; **USE** (Utilization, Saturation, Errors) for resources
- Alert on **symptoms** (user impact), not causes; alert on **SLO burn rate**
- Every alert must be **actionable** — non-actionable alerts cause fatigue
- Watch latency percentiles (p95, p99), not just averages — averages hide pain
- Design observability in from the start, not after an outage
- Tools: Prometheus/Grafana (metrics), ELK/Loki (logs), Jaeger/X-Ray (traces), OpenTelemetry (unified)

## Next Steps

Continue to [Toil & Automation](05-toil-and-automation.md).
