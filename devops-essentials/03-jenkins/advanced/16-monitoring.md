# Jenkins Monitoring and Observability

## Overview

Monitoring Jenkins is critical for maintaining healthy CI/CD pipelines. Track metrics, logs, and performance to identify bottlenecks, prevent failures, and ensure optimal operation.

## Why Monitor Jenkins?

### Key Metrics to Track

**Performance:**
- Build queue length
- Build duration trends
- Agent utilization
- Disk space usage

**Reliability:**
- Build success/failure rates
- Plugin health
- Agent connectivity
- System resource usage

**Security:**
- Failed login attempts
- Permission changes
- Credential access logs

## Prometheus Integration

### Installation

**Install Plugin:**
1. Navigate to Manage Jenkins → Manage Plugins
2. Install "Prometheus metrics plugin"
3. Restart Jenkins

**Configure:**
Manage Jenkins → Configure System → Prometheus

- Enable metrics endpoint
- Configure authentication (optional)
- Set namespace: `jenkins`

### Metrics Endpoint

Access at: `http://jenkins.example.com/prometheus/`

**Available metrics:**
```
# Build metrics
jenkins_builds_duration_milliseconds_summary
jenkins_builds_success_build_count_total
jenkins_builds_failed_build_count_total
jenkins_builds_running_build_count

# Queue metrics
jenkins_queue_size_value
jenkins_queue_blocked_value
jenkins_queue_buildable_value

# Executor metrics
jenkins_executor_count_value
jenkins_executor_in_use_value
jenkins_executor_free_value

# Node metrics
jenkins_node_count_value
jenkins_node_online_value
jenkins_node_offline_value

# Plugin metrics
jenkins_plugins_active
jenkins_plugins_failed
jenkins_plugins_inactive
```

### Prometheus Configuration

**prometheus.yml:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'jenkins'
    metrics_path: '/prometheus'
    static_configs:
      - targets: ['jenkins.example.com:8080']
    basic_auth:
      username: 'prometheus'
      password: 'your-token'
```

## Grafana Dashboards

### Setup Grafana

```bash
# Using Docker
docker run -d \
  --name=grafana \
  -p 3000:3000 \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  grafana/grafana
```

### Add Prometheus Data Source

1. Navigate to Configuration → Data Sources
2. Add Prometheus
3. URL: `http://prometheus:9090`
4. Save & Test

### Import Jenkins Dashboard

**Use community dashboard:**
- Dashboard ID: `9964` (Jenkins Performance and Health Overview)
- Or create custom dashboard

### Custom Dashboard Panels

**1. Build Success Rate:**
```promql
rate(jenkins_builds_success_build_count_total[5m]) /
(rate(jenkins_builds_success_build_count_total[5m]) +
 rate(jenkins_builds_failed_build_count_total[5m])) * 100
```

**2. Average Build Duration:**
```promql
rate(jenkins_builds_duration_milliseconds_summary_sum[5m]) /
rate(jenkins_builds_duration_milliseconds_summary_count[5m]) / 1000
```

**3. Queue Length:**
```promql
jenkins_queue_size_value
```

**4. Agent Utilization:**
```promql
(jenkins_executor_in_use_value / jenkins_executor_count_value) * 100
```

**5. Failed Builds:**
```promql
increase(jenkins_builds_failed_build_count_total[1h])
```

### Complete Dashboard JSON

```json
{
  "dashboard": {
    "title": "Jenkins Monitoring",
    "panels": [
      {
        "title": "Build Success Rate",
        "targets": [
          {
            "expr": "rate(jenkins_builds_success_build_count_total[5m]) / (rate(jenkins_builds_success_build_count_total[5m]) + rate(jenkins_builds_failed_build_count_total[5m])) * 100"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Active Executors",
        "targets": [
          {
            "expr": "jenkins_executor_in_use_value"
          }
        ],
        "type": "stat"
      },
      {
        "title": "Queue Length",
        "targets": [
          {
            "expr": "jenkins_queue_size_value"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

## Alerting with Alertmanager

### Alert Rules

**prometheus-rules.yml:**
```yaml
groups:
  - name: jenkins_alerts
    interval: 30s
    rules:
      - alert: JenkinsDown
        expr: up{job="jenkins"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Jenkins is down"
          description: "Jenkins has been down for more than 2 minutes"
      
      - alert: HighBuildFailureRate
        expr: |
          (rate(jenkins_builds_failed_build_count_total[5m]) /
           (rate(jenkins_builds_success_build_count_total[5m]) +
            rate(jenkins_builds_failed_build_count_total[5m]))) > 0.2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High build failure rate"
          description: "Build failure rate is above 20% for 10 minutes"
      
      - alert: LongQueueLength
        expr: jenkins_queue_size_value > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Long build queue"
          description: "Queue has more than 10 items for 5 minutes"
      
      - alert: LowDiskSpace
        expr: jenkins_disk_usage_bytes / jenkins_disk_total_bytes > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space on Jenkins"
          description: "Disk usage is above 90%"
      
      - alert: AgentOffline
        expr: jenkins_node_offline_value > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Jenkins agent offline"
          description: "{{ $value }} agents are offline"
```

### Alertmanager Configuration

**alertmanager.yml:**
```yaml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'slack-notifications'
  
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true
    
    - match:
        severity: warning
      receiver: 'slack-notifications'

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#jenkins-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true
  
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'your-pagerduty-key'
        description: '{{ .GroupLabels.alertname }}'
```

## Logging

### Centralized Logging with ELK

**Filebeat Configuration:**

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/jenkins/*.log
    fields:
      type: jenkins
    multiline:
      pattern: '^\d{4}-\d{2}-\d{2}'
      negate: true
      match: after

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "jenkins-logs-%{+yyyy.MM.dd}"

setup.kibana:
  host: "kibana:5601"
```

### Logstash Pipeline

```ruby
# jenkins-pipeline.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][type] == "jenkins" {
    grok {
      match => {
        "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{JAVACLASS:class} %{GREEDYDATA:message}"
      }
    }
    
    date {
      match => [ "timestamp", "yyyy-MM-dd HH:mm:ss.SSS" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "jenkins-logs-%{+YYYY.MM.dd}"
  }
}
```

### Kibana Queries

**Find failed builds:**
```
fields.type:jenkins AND level:ERROR AND "Build failed"
```

**Plugin errors:**
```
fields.type:jenkins AND "PluginException"
```

**Security events:**
```
fields.type:jenkins AND (failed AND login OR "Access denied")
```

## Application Performance Monitoring

### New Relic Integration

**Install plugin:** New Relic Deployment Notifier

**Configure in pipeline:**
```groovy
pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                sh './deploy.sh'
                
                newRelicDeploymentMarker(
                    apiKey: credentials('newrelic-api-key'),
                    applicationId: '12345',
                    description: "Deploy ${env.BUILD_NUMBER}",
                    revision: env.GIT_COMMIT,
                    user: env.BUILD_USER
                )
            }
        }
    }
}
```

### Datadog Integration

**Install plugin:** Datadog Plugin

**Configure:**
```groovy
pipeline {
    agent any
    
    options {
        datadog(
            collectLogs: true,
            tags: ["service:jenkins", "env:prod"]
        )
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
    }
}
```

## Custom Metrics in Pipelines

### Pipeline Metrics

```groovy
@Library('monitoring-lib') _

pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                script {
                    def startTime = System.currentTimeMillis()
                    
                    sh 'mvn clean package'
                    
                    def duration = System.currentTimeMillis() - startTime
                    
                    // Send custom metric
                    sendMetric(
                        name: 'build_duration',
                        value: duration,
                        tags: [
                            "project:${env.JOB_NAME}",
                            "branch:${env.BRANCH_NAME}"
                        ]
                    )
                }
            }
        }
    }
}
```

### StatsD Integration

**vars/sendMetric.groovy:**
```groovy
def call(Map config) {
    def statsdHost = env.STATSD_HOST ?: 'statsd.example.com'
    def statsdPort = env.STATSD_PORT ?: '8125'
    
    def metricName = config.name
    def metricValue = config.value
    def metricType = config.type ?: 'gauge'
    def tags = config.tags?.join(',') ?: ''
    
    sh """
        echo "${metricName}:${metricValue}|${metricType}|#${tags}" | \
        nc -u -w1 ${statsdHost} ${statsdPort}
    """
}
```

## Health Checks

### Jenkins Health Check Endpoint

**Access:**
- API: `http://jenkins.example.com/api/json`
- Health: `http://jenkins.example.com/metrics/currentUser/healthcheck`

### Custom Health Check Script

**healthcheck.groovy:**
```groovy
import jenkins.model.Jenkins
import hudson.model.Computer

def jenkins = Jenkins.getInstance()

// Check if Jenkins is ready
if (!jenkins.isQuietingDown() && !jenkins.isTerminating()) {
    println "Jenkins is HEALTHY"
    
    // Check agents
    def offlineAgents = Computer.all().findAll { !it.isOnline() }
    if (offlineAgents) {
        println "WARNING: ${offlineAgents.size()} agents offline"
    }
    
    // Check disk space
    def disk = jenkins.getRootPath().act(new hudson.FilePath.FileCallable<Long>() {
        Long invoke(File f, hudson.remoting.VirtualChannel channel) {
            return f.getFreeSpace()
        }
    })
    
    if (disk < 1024 * 1024 * 1024) {  // Less than 1GB
        println "WARNING: Low disk space"
    }
    
    return 0  // Healthy
} else {
    println "Jenkins is UNHEALTHY"
    return 1  // Unhealthy
}
```

### Kubernetes Liveness/Readiness

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
spec:
  template:
    spec:
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts
        ports:
        - containerPort: 8080
        livenessProbe:
          httpGet:
            path: /login
            port: 8080
          initialDelaySeconds: 90
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 5
        readinessProbe:
          httpGet:
            path: /login
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
```

## Distributed Tracing

### OpenTelemetry Integration

**Install plugin:** OpenTelemetry Plugin

**Configure:**
```groovy
pipeline {
    agent any
    
    options {
        openTelemetry {
            serviceName = 'jenkins'
            endpoint = 'http://otel-collector:4317'
        }
    }
    
    stages {
        stage('Build') {
            steps {
                script {
                    withSpan('maven-build') {
                        sh 'mvn clean package'
                    }
                }
            }
        }
        
        stage('Test') {
            steps {
                script {
                    withSpan('test-execution') {
                        sh 'mvn test'
                    }
                }
            }
        }
    }
}
```

## Performance Tuning

### Monitor These Metrics

**1. Build Queue Time:**
```promql
jenkins_builds_waiting_duration_milliseconds
```

**2. Agent Connection Time:**
```promql
jenkins_node_connection_latency_milliseconds
```

**3. Plugin Load Time:**
```promql
jenkins_plugins_duration_milliseconds_summary
```

**4. GC Pause Time:**
```promql
jvm_gc_pause_seconds_sum
```

### Optimization Alerts

```yaml
- alert: SlowBuilds
  expr: |
    avg(rate(jenkins_builds_duration_milliseconds_summary_sum[1h]) /
        rate(jenkins_builds_duration_milliseconds_summary_count[1h])) > 600000
  annotations:
    description: "Average build time exceeded 10 minutes"

- alert: HighGCTime
  expr: rate(jvm_gc_pause_seconds_sum[5m]) > 0.1
  annotations:
    description: "GC time is more than 10% of total time"
```

## Best Practices

### 1. Monitor Proactively

Set up alerts before issues occur:
```yaml
- High failure rates
- Long queue times
- Disk space warnings
- Agent failures
```

### 2. Use Appropriate Retention

```groovy
pipeline {
    options {
        buildDiscarder(logRotator(
            numToKeepStr: '30',
            artifactNumToKeepStr: '10'
        ))
    }
}
```

### 3. Tag Everything

```groovy
sendMetric(
    name: 'deployment',
    value: 1,
    tags: [
        "env:${ENV}",
        "service:${SERVICE}",
        "version:${VERSION}",
        "team:platform"
    ]
)
```

### 4. Create Dashboards for Teams

- Executive: High-level metrics
- Development: Build metrics
- Operations: Infrastructure health
- Security: Audit logs

### 5. Regular Reviews

Schedule monthly reviews of:
- Dashboard effectiveness
- Alert fatigue
- Metric coverage
- Performance trends

## Troubleshooting

### High CPU Usage

**Check metrics:**
```promql
rate(process_cpu_seconds_total{job="jenkins"}[5m]) * 100
```

**Common causes:**
- Too many concurrent builds
- Heavy plugins
- Insufficient resources

**Solutions:**
- Add more agents
- Optimize pipelines
- Disable unused plugins

### Memory Leaks

**Monitor:**
```promql
jvm_memory_used_bytes / jvm_memory_max_bytes
```

**Solutions:**
- Increase heap size
- Fix plugin leaks
- Regular restarts

### Slow Builds

**Track:**
```promql
jenkins_builds_duration_milliseconds_summary
```

**Investigate:**
- Checkout time
- Dependency downloads
- Test execution
- Artifact archiving

## Real-World Dashboard

**Complete monitoring setup:**

```yaml
# docker-compose.yml
version: '3'
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards
  
  alertmanager:
    image: prom/alertmanager
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "9093:9093"
```

## Summary

Effective Jenkins monitoring requires:
- Prometheus for metrics collection
- Grafana for visualization
- Alertmanager for notifications
- Centralized logging (ELK/Loki)
- Custom metrics in pipelines
- Health checks and tracing

**Key metrics:**
- Build success rate
- Build duration
- Queue length
- Agent utilization
- Disk space
- System resources

## Next Steps

- **Blue Ocean** → Modern Jenkins UI
- **Performance Optimization** → Tune Jenkins
- **Enterprise Patterns** → Scale for large teams

---

**Previous:** [Security](15-security.md)  
**Next:** [Blue Ocean](17-blue-ocean.md)
