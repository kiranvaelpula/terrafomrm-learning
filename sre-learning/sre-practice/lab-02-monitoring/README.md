# Lab 02: Monitoring & the Four Golden Signals

## 🎯 Objective
Instrument a simple web service with the Four Golden Signals (latency, traffic, errors, saturation) using Prometheus metrics.

## 📋 Prerequisites
```bash
pip install flask prometheus-client
```

## 🧪 Steps

### Step 1: Run the instrumented service
Run `app.py`. It exposes a web endpoint and a `/metrics` endpoint for Prometheus.

### Step 2: Generate traffic
Hit the endpoint repeatedly and watch the metrics change.

### Step 3: View the metrics
Open `http://localhost:5000/metrics` — see request counts, latency histogram, and error counts.

### Step 4: Write an alert rule
See `alerts.yml` for an SLO-based burn-rate alert.

## ✅ Expected Output
```
# At /metrics:
http_requests_total{status="success"} 1450
http_requests_total{status="error"} 12
http_request_duration_seconds_bucket{le="0.3"} 1400
```

## 🏋️ Exercises
1. Add a saturation metric (simulated CPU/queue depth)
2. Add latency percentile tracking (p50, p95, p99)
3. Wire up a real Prometheus + Grafana with Docker Compose
4. Create a dashboard showing all Four Golden Signals

## 🔑 Key Concepts Practiced
- Four Golden Signals (latency, traffic, errors, saturation)
- Prometheus instrumentation (Counter, Histogram, Gauge)
- SLO-based alerting rules
- The RED method (Rate, Errors, Duration)
