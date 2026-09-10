# Module 15: Monitoring & Logging

## Why Monitoring?

If you can't see what's happening inside your cluster, you can't fix problems before users notice them. Monitoring gives you visibility into resource usage, application health, and performance.

**What you need to monitor:**
- **Nodes** — CPU, memory, disk, network (is the machine healthy?)
- **Pods** — resource usage, restart count, status (is my app healthy?)
- **Applications** — request rate, error rate, latency (is my app performing well?)

**The monitoring stack in Kubernetes:**
- **Metrics Server** — basic CPU/memory metrics (built-in)
- **Prometheus** — full metrics collection, alerting, time-series database
- **Grafana** — dashboards and visualization
- **Loki** — log aggregation (like Elasticsearch but lighter)
- **Alertmanager** — sends alerts to Slack, email, PagerDuty

---

## 📖 Understanding Monitoring & Logging (Intuition First)

Running a cluster without monitoring is like flying a plane with the cockpit windows painted over and all the instruments removed. Everything might be fine — or an engine might be on fire — and you'd have no way to know until passengers start screaming. Monitoring gives you the instruments: the gauges, warning lights, and black-box recorder that let you understand what's happening inside your systems *before* users feel the pain.

Observability rests on three complementary "pillars," and understanding the difference is key. **Metrics** are numbers over time — CPU at 80%, 200 requests per second, 1.2% error rate. They're cheap to store and perfect for dashboards and alerts ("wake me if errors exceed 5%"). **Logs** are timestamped text events — the detailed story of what each component did, essential for digging into *why* something broke. **Traces** follow a single request as it hops across many services, showing you where time was spent. Metrics tell you *something* is wrong, logs and traces tell you *what and why*.

For metrics, the dominant model is **Prometheus**, and its defining trait is that it *pulls* rather than waits to be pushed. Prometheus periodically scrapes a `/metrics` endpoint that each app exposes, storing the results in a time-series database. This pull model is why you configure a **ServiceMonitor** to tell Prometheus *where* to scrape — you point it at your services, and it comes and collects. **Grafana** then turns that data into human-friendly dashboards, and **Alertmanager** routes alerts to Slack, email, or PagerDuty when a rule trips.

A crucial subtlety with alerting is the `for:` duration. You don't want to be paged the instant CPU blips to 90% for one second — that's noise. Good alerts require a condition to hold *for* several minutes before firing, filtering out transient spikes and keeping alerts meaningful. This is the difference between an on-call rotation people can live with and one that burns everyone out.

Finally, logs need aggregation because pods are ephemeral — when a pod dies, its logs die with it unless you've shipped them somewhere. A log collector like **Promtail** or **Fluent Bit** runs on every node (often as a DaemonSet), scoops up container logs, and forwards them to a central store like **Loki** or Elasticsearch, where you can search across your whole fleet. Together, metrics + logs + traces give you the full instrument panel to keep a cluster healthy.

---

## 📊 Metrics Server

The lightweight built-in option. Gives you `kubectl top` commands.

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# View node resource usage
kubectl top nodes

# View pod resource usage
kubectl top pods
kubectl top pods --all-namespaces
kubectl top pods --sort-by=memory    # Find memory hogs
```

**When to use:** Quick checks, HPA (autoscaling needs metrics-server). Not for historical data or alerting.

---

## 🔥 Prometheus & Grafana

The industry-standard monitoring stack for Kubernetes.

**Prometheus** = collects and stores metrics (time-series database)
**Grafana** = visualizes metrics with dashboards
**Alertmanager** = fires alerts when things go wrong

```bash
# Add Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install the full stack (Prometheus + Grafana + Alertmanager + Node Exporter)
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Check installation
kubectl get pods -n monitoring

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# http://localhost:3000
# Username: admin
# Password: prom-operator

# Access Prometheus
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
```

**What you get out of the box:** Pre-built dashboards for nodes, pods, cluster overview, and alerting rules for common issues (node down, pod crash looping, disk full).

---

## 📝 Custom ServiceMonitor

To monitor YOUR application, tell Prometheus where to scrape metrics from:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: app-metrics
  namespace: monitoring
  labels:
    release: prometheus       # Must match Prometheus selector
spec:
  selector:
    matchLabels:
      app: myapp              # Find services with this label
  namespaceSelector:
    matchNames:
    - production
  endpoints:
  - port: metrics             # Scrape the "metrics" port
    interval: 30s             # Every 30 seconds
    path: /metrics            # At this path
```

**In plain English:** "Every 30 seconds, Prometheus should hit the `/metrics` endpoint on any service labeled `app: myapp` in the production namespace."

**Your app needs to expose a /metrics endpoint** in Prometheus format. Most frameworks have libraries for this (prom-client for Node.js, micrometer for Java, prometheus_client for Python).

---

## 🚨 Alert Rules

Fire alerts when things go wrong:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: app-alerts
  namespace: monitoring
  labels:
    release: prometheus
spec:
  groups:
  - name: app-rules
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      for: 5m                    # Must be true for 5 minutes
      labels:
        severity: critical
      annotations:
        summary: "Error rate above 5% for 5 minutes"

    - alert: PodCrashLooping
      expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Pod {{ $labels.pod }} is restarting frequently"
```

---

## 📋 Logging with Loki

**Why Loki?** Prometheus handles metrics (numbers), but you also need logs (text) to debug issues.

```bash
# Install Loki + Promtail (log collector)
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set promtail.enabled=true

# Add Loki as a datasource in Grafana
# URL: http://loki.monitoring.svc:3100
```

Then in Grafana, you can query logs with LogQL:
```
{namespace="production", app="backend"} |= "error"
```

"Show me all logs from the backend app in production that contain the word 'error'."

---

## Quick Reference

| Tool | Purpose | Type |
|---|---|---|
| Metrics Server | Basic CPU/memory | Metrics |
| Prometheus | Full metrics collection + alerting | Metrics |
| Grafana | Visualization dashboards | Dashboards |
| Alertmanager | Alert routing (Slack, email) | Alerting |
| Loki | Log aggregation | Logs |
| Promtail/FluentBit | Log collection from pods | Log shipper |
| Jaeger/Tempo | Distributed tracing | Traces |

---

## 🎯 Interview Quick Points

- Observability has **three pillars**: metrics (numbers), logs (text events), and traces (request paths)
- **Metrics Server** provides basic CPU/memory for `kubectl top` and is required by the HPA — not for history or alerting
- **Prometheus** is the standard metrics system; it **pulls** by scraping `/metrics` endpoints and stores time-series data
- Apps must **expose a `/metrics` endpoint** (via client libraries) for Prometheus to scrape
- A **ServiceMonitor** tells Prometheus which services/ports/paths to scrape and how often
- **Grafana** visualizes metrics; **Alertmanager** routes alerts to Slack/email/PagerDuty
- The **kube-prometheus-stack** Helm chart bundles Prometheus + Grafana + Alertmanager + Node Exporter with prebuilt dashboards
- Alert rules use the `for:` duration to require a condition to persist, avoiding noisy false alarms
- **Loki** aggregates logs (lightweight, label-based); queried with **LogQL** in Grafana
- Log collectors (**Promtail, Fluent Bit, Fluentd**) usually run as **DaemonSets**, one per node
- Ship logs off-node because pods are ephemeral and their logs vanish when they die
- **Jaeger/Tempo** handle distributed tracing to pinpoint latency across microservices

---

## ⏭️ Next: [Module 16: Advanced Scheduling](../03-advanced/16-advanced-scheduling.md)
