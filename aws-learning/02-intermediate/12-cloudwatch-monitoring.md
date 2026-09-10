# CloudWatch Monitoring

## Overview

Amazon CloudWatch is AWS's native monitoring and observability service. It collects metrics, logs, and events from AWS resources and applications, and lets you visualize, alarm on, and react to them.

## 📖 Understanding CloudWatch (Intuition First)

Think of CloudWatch as the dashboard and warning-light system of your car, but for your entire AWS environment. Your car constantly measures dozens of things — speed, fuel, engine temperature, oil pressure — displays them on the dashboard, and lights up a warning when something crosses a safe threshold. You don't stare at the gauges every second; you trust that if something goes wrong, a light will flash and get your attention. CloudWatch does exactly this for your cloud: it continuously measures your resources and applications, shows them on dashboards, and raises alarms when something needs attention.

The reason CloudWatch exists is that you cannot manage what you cannot see. In the cloud, you have servers, databases, load balancers, and functions you never physically touch — they live in AWS data centers. Without monitoring, a server could be running out of memory, a database could be maxing its connections, or an application could be throwing errors, and you'd have no idea until customers complained. CloudWatch is the eyes and ears that make an invisible, remote infrastructure observable.

CloudWatch works on a few core building blocks. **Metrics** are the numbers over time — CPU utilization, request count, latency — the "gauges" on your dashboard. **Alarms** watch a metric and trigger an action when it crosses a threshold — the "warning lights." **Logs** capture the detailed text output from your applications and services — the "black box recorder" you review after an event. And **Events/EventBridge** let you react to changes in your environment automatically — like the car automatically calling for help after a crash.

A key idea is that CloudWatch isn't just passive watching — it's the trigger for **automation**. An alarm doesn't just email you; it can automatically scale up your servers when CPU is high, restart an unhealthy instance, or invoke a Lambda function to remediate an issue. This turns monitoring from "a human notices and reacts" into "the system notices and heals itself," which is essential at cloud scale where no team can watch everything manually.

The mindset CloudWatch encourages is that monitoring should be designed in from the start, not bolted on after an outage. The metrics, alarms, and dashboards you set up are what stand between a minor blip and a major incident — because the difference between resolving a problem in two minutes versus two hours usually comes down to whether you could *see* it happening.

---

## Core CloudWatch Components

```
1. METRICS — numeric data points over time (CPU%, request count, latency)
2. ALARMS — watch a metric, trigger actions when a threshold is crossed
3. LOGS — collect, store, and search log data from apps/services
4. DASHBOARDS — visualize metrics and logs in one place
5. EVENTS / EventBridge — react to state changes automatically
6. AGENTS — CloudWatch Agent collects OS-level + custom metrics/logs
```

## Metrics

```
- AWS services publish metrics automatically (EC2 CPU, ELB requests, RDS connections)
- Metrics have: namespace, name, dimensions, timestamp, value, unit
- Standard resolution: 1-minute; high resolution: down to 1 second
- Custom metrics: your app can publish its own business metrics
```

```bash
# Publish a custom metric
aws cloudwatch put-metric-data \
  --namespace "MyApp" \
  --metric-name "ActiveUsers" \
  --value 1250 \
  --unit Count

# Get metric statistics
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-1234567890 \
  --start-time 2026-08-10T00:00:00Z \
  --end-time 2026-08-10T23:59:59Z \
  --period 3600 \
  --statistics Average
```

## Alarms

```
An alarm watches ONE metric and has three states:
  OK             — metric within threshold
  ALARM          — metric breached threshold
  INSUFFICIENT_DATA — not enough data yet

Alarm actions can:
  - Send an SNS notification (email/Slack/PagerDuty)
  - Trigger Auto Scaling (scale up/down)
  - Stop/terminate/reboot an EC2 instance
  - Invoke a Lambda function (auto-remediation)
```

```bash
# Alarm: notify + scale when CPU > 80% for 5 minutes
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu \
  --alarm-description "CPU above 80%" \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-1234567890 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:ops-alerts
```

### Composite Alarms
```
Combine multiple alarms with AND/OR logic to reduce noise:
  "Alert only if (high CPU) AND (high latency)"
  — avoids paging on a CPU spike that doesn't actually hurt users.
```

## Logs

```
CloudWatch Logs:
  - Log Groups   — a container (e.g., per application)
  - Log Streams  — a sequence of log events (e.g., per instance)
  - Retention    — set how long logs are kept (cost control)

Logs Insights — query logs with a purpose-built query language.
```

```sql
-- CloudWatch Logs Insights query: top errors
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)
| sort @timestamp desc
```

## Dashboards

```
- Custom visual dashboards combining metrics from many services
- Widgets: line/stacked graphs, numbers, gauges, logs, alarm status
- Share one dashboard across the team as a single source of truth
```

## The Four Golden Signals in CloudWatch

```
Latency    → TargetResponseTime (ALB), Duration (Lambda)
Traffic    → RequestCount (ALB), Invocations (Lambda)
Errors     → HTTPCode_Target_5XX_Count, Errors (Lambda)
Saturation → CPUUtilization, MemoryUtilization, connection counts
```

## CloudWatch Agent (for deeper metrics)

```
By default, EC2 reports CPU, network, disk I/O — but NOT memory or disk %.
Install the CloudWatch Agent to collect:
  - Memory utilization
  - Disk space used
  - Custom application logs
  - Process-level metrics
```

## Related Services

| Service | Purpose |
|---------|---------|
| CloudWatch | Metrics, alarms, logs, dashboards |
| CloudWatch Logs Insights | Query and analyze logs |
| CloudWatch Synthetics | Canary tests (simulate user journeys) |
| CloudWatch RUM | Real user monitoring (browser) |
| X-Ray | Distributed tracing (request paths) |
| EventBridge | Event bus for reacting to changes |
| CloudTrail | API audit logging (who did what) — NOT the same as CloudWatch |

**Common interview point:** CloudWatch = performance/operational monitoring; CloudTrail = API audit trail (governance/security). Don't confuse them.

## CloudWatch Agent — Detailed Setup

The default EC2 metrics are hypervisor-level (CPU, network, disk I/O) but NOT what's happening *inside* the OS (memory, disk usage, processes). The CloudWatch Agent fills that gap.

```bash
# 1. Install the agent (Amazon Linux)
sudo yum install -y amazon-cloudwatch-agent

# 2. Configure it (wizard generates a config file)
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard

# 3. Start the agent with your config
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json -s
```

```json
// Example agent config — collect memory, disk, and app logs
{
  "metrics": {
    "metrics_collected": {
      "mem":  {"measurement": ["mem_used_percent"]},
      "disk": {"measurement": ["used_percent"], "resources": ["/"]}
    }
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [{
          "file_path": "/var/log/myapp/app.log",
          "log_group_name": "myapp-logs",
          "log_stream_name": "{instance_id}"
        }]
      }
    }
  }
}
```

## Logs Insights — More Query Examples

```sql
-- Count errors by 5-minute buckets
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() as errors by bin(5m)
| sort @timestamp desc

-- Average latency from a structured (JSON) log field
fields @timestamp, duration
| filter ispresent(duration)
| stats avg(duration), max(duration), pct(duration, 99) by bin(1m)

-- Top 10 slowest requests
fields @timestamp, url, duration
| sort duration desc
| limit 10

-- Find all logs for one request (trace correlation)
fields @timestamp, @message
| filter trace_id = "abc-123-def"
| sort @timestamp asc
```

## Metric Filters (turn logs into metrics)

```bash
# Create a metric from a log pattern — count 500 errors in logs,
# then you can alarm on that metric.
aws logs put-metric-filter \
  --log-group-name myapp-logs \
  --filter-name Count500Errors \
  --filter-pattern '"HTTP 500"' \
  --metric-transformations \
    metricName=Http500Count,metricNamespace=MyApp,metricValue=1
```

## Dashboards as Code

```python
import boto3, json

cloudwatch = boto3.client("cloudwatch")

dashboard = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "title": "ALB Golden Signals",
                "metrics": [
                    ["AWS/ApplicationELB", "TargetResponseTime", {"stat": "p99"}],
                    [".", "RequestCount", {"stat": "Sum"}],
                    [".", "HTTPCode_Target_5XX_Count", {"stat": "Sum"}],
                ],
                "period": 300,
                "region": "us-east-1",
            },
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName="ProdOverview",
    DashboardBody=json.dumps(dashboard),
)
# Version-control this → reproducible, reviewable dashboards
```

## CloudWatch Synthetics (Canaries)

```
Canaries are scripts that run on a schedule to SIMULATE user journeys
(e.g., "log in, add to cart, checkout") and alert if the flow breaks —
BEFORE real users hit the problem.

- Catches issues even when there's no traffic
- Monitors from the user's perspective (end-to-end)
- Written in Node.js/Python, run on a schedule
```

## CloudWatch RUM (Real User Monitoring)

```
RUM collects performance data from REAL users' browsers:
  - Page load times, JavaScript errors, Core Web Vitals
  - Broken down by browser, device, geography
Complements server-side metrics with the actual client experience.
```

## Anomaly Detection

```
CloudWatch can learn a metric's normal pattern (including daily/weekly
cycles) using ML, then alarm when it deviates — instead of a fixed threshold.

Useful when "normal" varies (e.g., high daytime traffic, low at night)
and a static threshold would either miss issues or false-alarm.
```

## Cost Considerations

```
CloudWatch charges for: custom metrics, dashboards, alarms, logs ingested/stored, and API requests.
Control cost by:
  - Setting log retention (don't keep logs forever)
  - Using metric filters instead of storing everything
  - Consolidating alarms (composite alarms)
  - Sampling high-volume logs
  - Using standard-resolution metrics unless you truly need 1-second
```

---

## 🎯 Interview Quick Points

- CloudWatch = AWS's native monitoring/observability (metrics, alarms, logs, dashboards, events)
- Analogy: the dashboard + warning lights of your car, for your whole AWS environment
- **Metrics** = numbers over time; AWS services publish many automatically
- **Alarms** watch a metric and trigger actions (notify, scale, reboot, invoke Lambda)
- Alarm states: OK, ALARM, INSUFFICIENT_DATA
- Alarms enable **auto-remediation** — monitoring that triggers automation, not just alerts
- EC2 does NOT report memory or disk % by default — install the **CloudWatch Agent** for those
- **Logs Insights** lets you query logs with a query language
- **Composite alarms** combine conditions (AND/OR) to reduce alert noise
- Map the **Four Golden Signals** (latency, traffic, errors, saturation) to CloudWatch metrics
- **CloudWatch = performance monitoring; CloudTrail = API audit logging** (don't confuse them)
- Control cost via log retention, metric filters, and consolidated alarms

## Next Steps

Continue to [CloudFormation Basics](13-cloudformation-basics.md).
