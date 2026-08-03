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

## ⏭️ Next: [Module 16: Advanced Scheduling](../03-advanced/16-advanced-scheduling.md)
