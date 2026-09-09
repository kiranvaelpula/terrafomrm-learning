#!/usr/bin/env python3
"""
Lab 02: A Flask service instrumented with the Four Golden Signals.
Run, generate traffic, then view /metrics.
"""

import time
import random
from flask import Flask
from prometheus_client import Counter, Histogram, Gauge, generate_latest

app = Flask(__name__)

# ── Four Golden Signals as Prometheus metrics ──
# TRAFFIC + ERRORS
REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["status"])
# LATENCY (histogram → percentiles)
LATENCY = Histogram("http_request_duration_seconds", "Request latency")
# SATURATION (simulated queue depth)
SATURATION = Gauge("queue_depth", "Current work queue depth")


@app.route("/")
@LATENCY.time()                      # automatically records latency
def index():
    # Simulate variable work + occasional errors
    processing_time = random.uniform(0.05, 0.4)
    time.sleep(processing_time)
    SATURATION.set(random.randint(0, 20))   # simulate queue depth

    if random.random() < 0.02:              # ~2% error rate
        REQUESTS.labels(status="error").inc()
        return "Internal Server Error", 500

    REQUESTS.labels(status="success").inc()
    return "OK"


@app.route("/metrics")
def metrics():
    """Prometheus scrapes this endpoint."""
    return generate_latest(), 200, {"Content-Type": "text/plain"}


if __name__ == "__main__":
    print("Service on http://localhost:5000")
    print("Metrics on http://localhost:5000/metrics")
    print("Generate traffic:  for i in $(seq 100); do curl -s localhost:5000 >/dev/null; done")
    app.run(port=5000)
