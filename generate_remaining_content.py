#!/usr/bin/env python3
"""
Script to generate remaining content files for all three knowledge bases
"""

import os

# Content templates for each file
CONTENT_MAP = {
    # DevSecOps Basics
    "devsecops-learning/01-basics/03-threat-modeling.md": """# Threat Modeling

## What is Threat Modeling?

Threat modeling is a structured approach to identifying and addressing security threats during the design phase.

## STRIDE Methodology

- **S**poofing: Identity impersonation
- **T**ampering: Data modification
- **R**epudiation: Denying actions
- **I**nformation Disclosure: Data exposure
- **D**enial of Service: Service disruption
- **E**levation of Privilege: Unauthorized access

## Example Threat Model

```yaml
Application: E-commerce Platform

Assets:
  - Customer PII
  - Payment information
  - Order history

Threats:
  SQL_Injection:
    severity: HIGH
    attack_vector: "Unsanitized input in search"
    mitigation: "Parameterized queries, input validation"
  
  XSS:
    severity: MEDIUM
    attack_vector: "User-generated product reviews"
    mitigation: "Output encoding, CSP headers"
  
  Authentication_Bypass:
    severity: CRITICAL
    attack_vector: "Weak password reset flow"
    mitigation: "MFA, secure token generation"
```

## Creating a Threat Model

1. **Identify Assets**: What needs protection?
2. **Create Architecture Diagram**: How components interact
3. **Identify Threats**: Use STRIDE for each component
4. **Rate Risks**: Likelihood × Impact
5. **Define Mitigations**: Security controls for each threat
6. **Validate**: Test mitigations effectiveness

## Tools

- Microsoft Threat Modeling Tool
- OWASP Threat Dragon
- IriusRisk
- ThreatModeler

## Next Steps

Continue to [Security Tools Overview](04-security-tools-overview.md)
""",

    "devsecops-learning/01-basics/04-security-tools-overview.md": """# Security Tools Overview

## Categories of Security Tools

### 1. SAST (Static Application Security Testing)

Analyzes source code for vulnerabilities.

**Tools**:
- **SonarQube**: Multi-language, CI/CD integration
- **Semgrep**: Fast, customizable rules
- **Checkmarx**: Enterprise-grade
- **Bandit**: Python-specific

**Usage**:
```bash
# Semgrep
semgrep --config=auto .

# Bandit (Python)
bandit -r . -f json -o report.json
```

### 2. DAST (Dynamic Application Security Testing)

Tests running applications.

**Tools**:
- **OWASP ZAP**: Free, automation-friendly
- **Burp Suite**: Professional pentesting
- **Acunetix**: Web vulnerability scanner

**Usage**:
```bash
# OWASP ZAP baseline scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://example.com
```

### 3. SCA (Software Composition Analysis)

Scans dependencies for known vulnerabilities.

**Tools**:
- **Snyk**: Developer-first, multi-language
- **WhiteSource**: Enterprise license compliance
- **OWASP Dependency-Check**: Open-source
- **Safety** (Python), **npm audit** (Node.js)

**Usage**:
```bash
# npm audit
npm audit --audit-level=high

# Snyk
snyk test
```

### 4. Container Security

Scans container images.

**Tools**:
- **Trivy**: Fast, comprehensive
- **Anchore**: Policy-based
- **Clair**: CoreOS project
- **Aqua Security**: Commercial platform

**Usage**:
```bash
# Trivy
trivy image nginx:latest
```

### 5. Secrets Detection

Finds hardcoded credentials.

**Tools**:
- **git-secrets**: AWS-focused
- **TruffleHog**: Entropy-based detection
- **GitLeaks**: Fast, configurable
- **detect-secrets**: Yelp's tool

**Usage**:
```bash
# TruffleHog
trufflehog filesystem /path/to/repo
```

### 6. Infrastructure Security

Scans IaC for misconfigurations.

**Tools**:
- **tfsec**: Terraform scanner
- **Checkov**: Multi-platform (Terraform, K8s, etc.)
- **kube-score**: Kubernetes manifests
- **Terrascan**: Policy as code

**Usage**:
```bash
# tfsec
tfsec .

# Checkov
checkov -d .
```

## Choosing the Right Tools

Consider:
- **Language/Stack**: Tool must support your technology
- **Integration**: CI/CD compatibility
- **False Positives**: Low noise is critical
- **Speed**: Fast feedback loops
- **Cost**: Open-source vs commercial

## Tool Integration Example

```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: SAST - Semgrep
        uses: returntocorp/semgrep-action@v1
      
      - name: SCA - npm audit
        run: npm audit
      
      - name: Secrets - TruffleHog
        uses: trufflesecurity/trufflehog@main
      
      - name: Container - Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
```

## Next Steps

Continue to [First Security Scan](05-first-security-scan.md)
""",

    "devsecops-learning/01-basics/05-first-security-scan.md": """# First Security Scan

## Quick Security Scan Guide

Let's scan a simple application and find vulnerabilities.

## Step 1: Install Tools

```bash
# Install Trivy (container scanning)
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh

# Install Semgrep (SAST)
pip install semgrep

# Install Safety (Python dependencies)
pip install safety
```

## Step 2: Create Sample Vulnerable App

```python
# app.py - Intentionally vulnerable
from flask import Flask, request
import sqlite3

app = Flask(__name__)

# Vulnerability 1: Hardcoded credentials
DB_PASSWORD = "SuperSecret123!"

# Vulnerability 2: SQL Injection
@app.route('/user/<username>')
def get_user(username):
    conn = sqlite3.connect('users.db')
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return str(conn.execute(query).fetchone())

# Vulnerability 3: Command Injection
@app.route('/ping')
def ping():
    host = request.args.get('host')
    import os
    return os.popen(f'ping -c 1 {host}').read()

if __name__ == '__main__':
    app.run(debug=True)  # Vulnerability 4: Debug mode in production
```

## Step 3: Scan with Semgrep

```bash
semgrep --config=auto app.py
```

**Expected Output**:
```
Findings:
1. SQL Injection in get_user() - HIGH severity
2. Command Injection in ping() - HIGH severity
3. Hardcoded password - MEDIUM severity
4. Debug mode enabled - LOW severity
```

## Step 4: Create Dockerfile

```dockerfile
# Dockerfile - Intentionally vulnerable
FROM ubuntu:18.04  # Old version

USER root  # Running as root

RUN apt-get update && apt-get install -y python3

COPY app.py /app/
RUN chmod 777 /app/app.py  # Too permissive

CMD ["python3", "/app/app.py"]
```

## Step 5: Scan Container

```bash
docker build -t vulnerable-app .
trivy image vulnerable-app
```

**Expected Output**:
```
Total: 234 vulnerabilities (CRITICAL:45, HIGH:89, MEDIUM:100)

CVE-2021-44228: Apache Log4j Remote Code Execution
Severity: CRITICAL
Fixed Version: Update to latest
```

## Step 6: Fix Vulnerabilities

**Fixed app.py**:
```python
from flask import Flask, request
import sqlite3
import os

app = Flask(__name__)

# Fix 1: Use environment variables
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Fix 2: Parameterized query
@app.route('/user/<username>')
def get_user(username):
    conn = sqlite3.connect('users.db')
    query = "SELECT * FROM users WHERE username = ?"
    return str(conn.execute(query, (username,)).fetchone())

# Fix 3: Input validation + subprocess
@app.route('/ping')
def ping():
    import re
    import subprocess
    
    host = request.args.get('host')
    if not re.match(r'^[a-zA-Z0-9.-]+$', host):
        return "Invalid host", 400
    
    result = subprocess.run(['ping', '-c', '1', host], 
                          capture_output=True, text=True)
    return result.stdout

if __name__ == '__main__':
    # Fix 4: Disable debug in production
    debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
    app.run(debug=debug_mode)
```

**Fixed Dockerfile**:
```dockerfile
FROM python:3.11-slim  # Latest stable version

RUN useradd -m appuser  # Create non-root user
USER appuser

WORKDIR /app
COPY --chown=appuser:appuser app.py .

CMD ["python3", "app.py"]
```

## Step 7: Re-scan

```bash
# Re-scan code
semgrep --config=auto app.py
# Result: 0 findings ✅

# Re-scan container
docker build -t secure-app .
trivy image --severity HIGH,CRITICAL secure-app
# Result: 0 critical/high vulnerabilities ✅
```

## Key Takeaways

1. **Scan Early**: Find issues during development
2. **Fix Systematically**: Address root causes
3. **Verify Fixes**: Re-scan after fixing
4. **Automate**: Integrate scans into CI/CD
5. **Continuous**: Security is ongoing, not one-time

## Next Steps

- Complete practice labs in `devsecops-practice/`
- Review [Interview Questions](interview-questions-basics.md)
- Move to [Intermediate Topics](../02-intermediate/)
""",

    # AIOps Basics - Fixed comma
    "aiops-learning/01-basics/interview-questions-basics.md": """# AIOps Interview Questions - Basics

## Conceptual Questions

### Q1: What is AIOps and how does it differ from traditional IT operations?

**Answer**: AIOps (AI for IT Operations) applies machine learning and data science to IT operations.

**Key Differences**:

| Traditional Ops | AIOps |
|----------------|-------|
| Rule-based alerts | ML-based anomaly detection |
| Manual log analysis | Automated pattern recognition |
| Human correlates events | AI correlates automatically |
| Reactive | Proactive & predictive |
| Limited scale | Unlimited scale |

**Example**:
```
Traditional: 1000 alerts → Human investigates → 2 hours to resolve
AIOps: 1000 alerts → AI correlates to 1 root cause → 5 minutes to resolve
```

---

### Q2: Explain the main use cases for AIOps.

**Answer**:

**1. Anomaly Detection**
```python
# Detect unusual CPU spike
normal_range = [30-50%]
current = 95%  # Anomaly!
```

**2. Root Cause Analysis**
```
API errors → Trace dependencies → Find: Database connection pool full
```

**3. Alert Correlation**
```
50 alerts → AI groups → 1 incident: "Database overload"
```

**4. Predictive Analytics**
```
Disk usage trend → Predict: "Will be full in 7 days"
```

**5. Automated Remediation**
```
High memory → AI diagnoses → Auto-restart service
```

---

### Q3: What types of data does AIOps analyze?

**Answer**:

**1. Metrics (Time Series)**
- CPU, memory, disk, network
- Application performance metrics
- Business metrics (transactions/sec)

**2. Logs**
- Application logs
- System logs
- Security logs

**3. Traces**
- Distributed tracing data
- Request flows
- Latency breakdowns

**4. Events**
- Alerts from monitoring systems
- Change events (deployments, config changes)
- Incidents and tickets

**5. Topology**
- Service dependencies
- Infrastructure relationships
- Network topology

**Example Integration**:
```python
aiops_data = {
    'metrics': prometheus.query('cpu_usage'),
    'logs': elasticsearch.search('ERROR'),
    'traces': jaeger.get_trace(trace_id),
    'events': pagerduty.get_incidents(),
    'topology': service_mesh.get_dependencies()
}

insights = aiops.analyze(aiops_data)
```

---

### Q4: What is anomaly detection and why is it important?

**Answer**: Anomaly detection identifies unusual patterns that deviate from normal behavior.

**Why Important**:
- Detect issues before they become incidents
- No need to set static thresholds
- Adapts to changing patterns
- Reduces alert noise

**Types of Anomalies**:

**1. Point Anomaly**
```
Normal CPU: 40-50%
Anomaly: Sudden spike to 95%
```

**2. Contextual Anomaly**
```
High traffic at 2 PM = Normal
High traffic at 2 AM = Anomaly
```

**3. Collective Anomaly**
```
Gradual memory leak over days
```

**Detection Methods**:
```python
# Statistical
z_score = (value - mean) / std_dev
is_anomaly = abs(z_score) > 3

# Machine Learning
model = IsolationForest()
model.fit(historical_data)
is_anomaly = model.predict(current_data)
```

---

### Q5: What is the difference between reactive and proactive operations?

**Answer**:

**Reactive Operations** (Traditional):
```
1. User reports issue
2. Ops team alerted
3. Investigation begins
4. Root cause found
5. Fixed
MTTR: 2-4 hours
```

**Proactive Operations** (AIOps):
```
1. AI detects anomaly
2. Predicts future impact
3. Auto-remediates or alerts
4. Issue prevented
MTTD: < 5 minutes
```

**Example**:

**Reactive**:
```
09:00: Disk 95% full
10:00: Service crashes
11:00: Customer complaints
12:00: Team investigates
14:00: Disk cleaned up
Result: 2 hours downtime
```

**Proactive (AIOps)**:
```
Day -7: AI predicts "Disk will be full in 7 days"
Day -6: Auto-cleanup scheduled
Day -5: Old logs archived
Day 0: No issue
Result: 0 downtime
```

---

## Practical Questions

### Q6: How would you implement basic anomaly detection for CPU metrics?

**Answer**:

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

# Step 1: Collect historical data
cpu_data = pd.read_csv('cpu_metrics.csv')
# Columns: timestamp, cpu_percent

# Step 2: Train anomaly detector
model = IsolationForest(
    contamination=0.05,  # Expect 5% anomalies
    random_state=42
)

X = cpu_data[['cpu_percent']].values
model.fit(X)

# Step 3: Detect anomalies in new data
current_cpu = [[95.0]]  # Current reading
prediction = model.predict(current_cpu)

if prediction[0] == -1:
    print("🚨 CPU Anomaly Detected!")
    alert_team()
    investigate_processes()
else:
    print("✅ CPU normal")

# Step 4: Get anomaly score
score = model.score_samples(current_cpu)
print(f"Anomaly score: {score[0]:.2f}")
# Lower score = more anomalous
```

---

### Q7: How would you correlate multiple alerts to reduce noise?

**Answer**:

```python
from datetime import datetime, timedelta

class AlertCorrelator:
    def __init__(self, time_window=60):
        self.time_window = time_window  # seconds
        self.dependency_graph = load_dependencies()
    
    def correlate_alerts(self, alerts):
        """Group related alerts into incidents"""
        incidents = []
        processed = set()
        
        for alert in alerts:
            if alert['id'] in processed:
                continue
            
            # Find related alerts
            related = self.find_related(alert, alerts)
            
            if related:
                # Create incident
                incident = {
                    'id': generate_id(),
                    'root_cause': self.identify_root(related),
                    'affected_services': [a['service'] for a in related],
                    'severity': max(a['severity'] for a in related),
                    'start_time': min(a['timestamp'] for a in related),
                    'alerts': related
                }
                incidents.append(incident)
                processed.update(a['id'] for a in related)
        
        return incidents
    
    def find_related(self, alert, all_alerts):
        """Find alerts related by time and dependencies"""
        related = [alert]
        
        for other in all_alerts:
            # Same time window?
            time_diff = abs(
                (alert['timestamp'] - other['timestamp']).total_seconds()
            )
            
            if time_diff > self.time_window:
                continue
            
            # Related services?
            if self.are_services_related(
                alert['service'],
                other['service']
            ):
                related.append(other)
        
        return related
    
    def identify_root(self, alerts):
        """Find root cause from related alerts"""
        # Service that others depend on
        for alert in alerts:
            dependencies = self.dependency_graph[alert['service']]
            if all(a['service'] in dependencies for a in alerts 
                   if a != alert):
                return alert['service']
        
        # Earliest alert
        return min(alerts, key=lambda a: a['timestamp'])['service']

# Usage
correlator = AlertCorrelator(time_window=60)

alerts = [
    {'id': 1, 'service': 'database', 'severity': 'HIGH', 
     'timestamp': datetime.now()},
    {'id': 2, 'service': 'api-gateway', 'severity': 'HIGH',
     'timestamp': datetime.now() + timedelta(seconds=10)},
    {'id': 3, 'service': 'user-service', 'severity': 'MEDIUM',
     'timestamp': datetime.now() + timedelta(seconds=15)},
]

incidents = correlator.correlate_alerts(alerts)
# Result: 1 incident instead of 3 alerts
print(f"Reduced {len(alerts)} alerts to {len(incidents)} incident(s)")
```

---

### Q8: How do you detect data drift in production?

**Answer**:

```python
from scipy import stats
import numpy as np

def detect_data_drift(reference_data, current_data):
    """Detect if data distribution has changed"""
    
    drift_report = {}
    
    for feature in reference_data.columns:
        ref_values = reference_data[feature]
        curr_values = current_data[feature]
        
        # Kolmogorov-Smirnov test
        statistic, p_value = stats.ks_2samp(ref_values, curr_values)
        
        # Drift detected if p < 0.05
        has_drift = p_value < 0.05
        
        drift_report[feature] = {
            'drift_detected': has_drift,
            'ks_statistic': statistic,
            'p_value': p_value,
            'severity': 'HIGH' if statistic > 0.2 else 'MEDIUM' if statistic > 0.1 else 'LOW'
        }
        
        if has_drift:
            print(f"⚠️ Drift detected in {feature}")
            print(f"   KS statistic: {statistic:.3f}")
            print(f"   Reference mean: {ref_values.mean():.2f}")
            print(f"   Current mean: {curr_values.mean():.2f}")
    
    return drift_report

# Usage
import pandas as pd

# Training data distribution
reference = pd.read_csv('training_data.csv')

# Current production data
current = pd.read_csv('production_data.csv')

drift = detect_data_drift(reference, current)

if any(d['drift_detected'] for d in drift.values()):
    send_alert("Data drift detected - consider retraining")
```

---

### Q9: How would you implement log pattern recognition?

**Answer**:

```python
import re
from collections import Counter

class LogPatternDetector:
    def __init__(self):
        self.error_patterns = {
            'connection_timeout': r'timeout|timed out|connection refused',
            'out_of_memory': r'OutOfMemory|OOM|memory exhausted',
            'null_pointer': r'NullPointer|AttributeError|None has no attribute',
            'permission_denied': r'permission denied|access denied|forbidden',
            'disk_full': r'no space left|disk full|write failed'
        }
    
    def analyze_logs(self, log_file):
        """Find error patterns in logs"""
        errors = Counter()
        error_details = []
        
        with open(log_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                # Check each pattern
                for error_type, pattern in self.error_patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        errors[error_type] += 1
                        error_details.append({
                            'line': line_num,
                            'type': error_type,
                            'message': line.strip()
                        })
        
        return {
            'summary': dict(errors),
            'details': error_details,
            'total_errors': sum(errors.values())
        }
    
    def detect_error_spike(self, log_file, threshold=10):
        """Detect unusual error rate"""
        errors_per_minute = Counter()
        
        with open(log_file, 'r') as f:
            for line in f:
                # Extract timestamp (assuming ISO format)
                match = re.search(r'\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}', line)
                if match and ('ERROR' in line or 'FATAL' in line):
                    minute = match.group()
                    errors_per_minute[minute] += 1
        
        # Find spikes
        spikes = {
            time: count 
            for time, count in errors_per_minute.items()
            if count > threshold
        }
        
        return spikes

# Usage
detector = LogPatternDetector()

# Analyze logs
results = detector.analyze_logs('/var/log/app.log')

print(f"Found {results['total_errors']} errors:")
for error_type, count in results['summary'].items():
    print(f"  {error_type}: {count}")

# Detect spikes
spikes = detector.detect_error_spike('/var/log/app.log')
if spikes:
    print(f"\\n⚠️ Error spikes detected:")
    for time, count in spikes.items():
        print(f"  {time}: {count} errors")
```

---

### Q10: How would you implement automated remediation?

**Answer**:

```python
import subprocess
import time

class AutoRemediation:
    def __init__(self):
        self.remediation_playbooks = {
            'high_cpu': self.scale_service,
            'high_memory': self.restart_service,
            'disk_full': self.cleanup_logs,
            'service_down': self.restart_service
        }
    
    def remediate(self, incident):
        """Execute automated remediation"""
        issue_type = incident['type']
        service = incident['service']
        
        if issue_type not in self.remediation_playbooks:
            print(f"No playbook for {issue_type}, escalating to human")
            return False
        
        print(f"🔧 Attempting auto-remediation for {issue_type}")
        
        try:
            # Execute remediation
            result = self.remediation_playbooks[issue_type](service)
            
            # Wait for system to stabilize
            time.sleep(30)
            
            # Verify remediation worked
            if self.verify_resolution(service, issue_type):
                print(f"✅ Auto-remediation successful")
                self.log_success(incident, result)
                return True
            else:
                print(f"❌ Remediation didn't resolve issue")
                self.escalate_to_human(incident)
                return False
        
        except Exception as e:
            print(f"❌ Remediation failed: {e}")
            self.escalate_to_human(incident)
            return False
    
    def scale_service(self, service):
        """Scale service horizontally"""
        current_replicas = self.get_replica_count(service)
        new_replicas = current_replicas + 2
        
        subprocess.run([
            'kubectl', 'scale', 'deployment', service,
            f'--replicas={new_replicas}'
        ], check=True)
        
        return f"Scaled from {current_replicas} to {new_replicas}"
    
    def restart_service(self, service):
        """Restart service"""
        subprocess.run([
            'kubectl', 'rollout', 'restart', f'deployment/{service}'
        ], check=True)
        
        # Wait for rollout
        subprocess.run([
            'kubectl', 'rollout', 'status', f'deployment/{service}'
        ], check=True)
        
        return f"Service {service} restarted"
    
    def cleanup_logs(self, service):
        """Clean up old logs"""
        # Find old log files
        result = subprocess.run([
            'find', '/var/log', '-name', '*.log',
            '-mtime', '+7', '-delete'
        ], capture_output=True, text=True, check=True)
        
        return f"Cleaned up old logs"
    
    def verify_resolution(self, service, issue_type):
        """Check if issue is resolved"""
        if issue_type == 'high_cpu':
            cpu = self.get_cpu_usage(service)
            return cpu < 80
        elif issue_type == 'service_down':
            return self.is_service_healthy(service)
        return True

# Usage
remediator = AutoRemediation()

incident = {
    'type': 'high_cpu',
    'service': 'api-gateway',
    'severity': 'HIGH'
}

success = remediator.remediate(incident)
if success:
    print("Issue resolved automatically")
else:
    print("Human intervention required")
```

---

## Quick Answer Questions

### Q11: What is MTTD?

**Answer**: Mean Time To Detect - Average time to detect an issue after it occurs. AIOps reduces from hours to minutes.

### Q12: What is MTTR?

**Answer**: Mean Time To Resolve - Average time to resolve an issue. AIOps reduces through automated RCA and remediation.

### Q13: Name three AIOps platforms.

**Answer**:
1. **Datadog** - Full observability with AI
2. **Dynatrace** - AI-powered APM
3. **Splunk** - Log analytics with ML

### Q14: What is the difference between metrics and logs?

**Answer**:
- **Metrics**: Numerical measurements over time (CPU, latency)
- **Logs**: Text records of events (error messages, transactions)

### Q15: What is a false positive in anomaly detection?

**Answer**: When AI incorrectly identifies normal behavior as an anomaly. High false positive rate causes alert fatigue.

---

## Tips for AIOps Interviews

1. **Understand ML Basics**: Know common algorithms (Isolation Forest, LSTM)
2. **Practical Experience**: Have examples of anomaly detection
3. **Tool Knowledge**: Familiar with Prometheus, ELK, Grafana
4. **Business Impact**: Connect technical solutions to business outcomes
5. **Balance**: Know when AI helps vs when humans are needed

---

**Next Level**: Ready for intermediate? Check out [Intermediate Interview Questions](../02-intermediate/interview-questions-intermediate.md)
""",
}

def create_file(filepath, content):
    """Create a file with content"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {filepath}")

def main():
    """Generate all content files"""
    print("🚀 Generating remaining content files...\n")
    
    for filepath, content in CONTENT_MAP.items():
        try:
            create_file(filepath, content)
        except Exception as e:
            print(f"❌ Error creating {filepath}: {e}")
    
    print(f"\n✅ Created {len(CONTENT_MAP)} content files successfully!")
    print("\n📝 Files created:")
    for filepath in CONTENT_MAP.keys():
        print(f"   - {filepath}")

if __name__ == "__main__":
    main()
