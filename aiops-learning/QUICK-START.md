# AIOps Quick Start Guide

Get started with AIOps in 30 minutes!

## 🎯 Goal
Set up anomaly detection, log analysis, and automated alerting for your infrastructure.

## Prerequisites
- Python 3.8+ installed
- Docker (for sample services)
- Basic understanding of monitoring concepts

## Step 1: Install AIOps Tools (5 mins)

```bash
# Create virtual environment
python -m venv aiops-env
source aiops-env/bin/activate  # Windows: aiops-env\Scripts\activate

# Install core packages
pip install prometheus-client pandas numpy scikit-learn
pip install prophet  # Time series forecasting
pip install elasticsearch  # Log analysis
pip install grafana-api  # Visualization
```

## Step 2: Anomaly Detection Setup (5 mins)

Create `anomaly_detector.py`:

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta

class AnomalyDetector:
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        
    def fit(self, data):
        """Train on historical data"""
        self.model.fit(data)
        
    def detect(self, data):
        """Detect anomalies in new data"""
        predictions = self.model.predict(data)
        # -1 for anomalies, 1 for normal
        return predictions == -1
        
    def score(self, data):
        """Get anomaly scores"""
        return self.model.score_samples(data)

# Example: CPU usage anomaly detection
def detect_cpu_anomalies():
    # Generate sample CPU metrics
    np.random.seed(42)
    normal_cpu = np.random.normal(40, 10, 1000)
    anomalies = np.random.normal(90, 5, 50)
    cpu_data = np.concatenate([normal_cpu, anomalies])
    
    # Reshape for sklearn
    X = cpu_data.reshape(-1, 1)
    
    # Train detector
    detector = AnomalyDetector(contamination=0.05)
    detector.fit(X[:1000])  # Train on normal data
    
    # Detect anomalies
    is_anomaly = detector.detect(X)
    anomaly_scores = detector.score(X)
    
    # Create results DataFrame
    results = pd.DataFrame({
        'timestamp': pd.date_range(start='2026-07-01', periods=len(cpu_data), freq='1min'),
        'cpu_usage': cpu_data,
        'is_anomaly': is_anomaly,
        'anomaly_score': anomaly_scores
    })
    
    print(f"✅ Detected {is_anomaly.sum()} anomalies out of {len(cpu_data)} data points")
    print(results[results['is_anomaly']].head())
    
    return results

if __name__ == "__main__":
    detect_cpu_anomalies()
```

Run it:
```bash
python anomaly_detector.py
```

## Step 3: Log Pattern Analysis (5 mins)

Create `log_analyzer.py`:

```python
import re
from collections import Counter
from datetime import datetime

class LogAnalyzer:
    def __init__(self):
        self.error_patterns = {
            'connection_error': r'Connection (refused|timeout|failed)',
            'memory_error': r'OutOfMemory|MemoryError',
            'null_pointer': r'NullPointerException|AttributeError',
            'timeout': r'timeout|timed out',
            'http_5xx': r'HTTP [5]\d{2}',
        }
        
    def analyze_logs(self, log_file):
        """Analyze log file for patterns"""
        errors = Counter()
        timestamps = []
        
        with open(log_file, 'r') as f:
            for line in f:
                # Extract timestamp (assuming ISO format)
                ts_match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', line)
                if ts_match:
                    timestamps.append(ts_match.group())
                
                # Check for error patterns
                for error_type, pattern in self.error_patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        errors[error_type] += 1
        
        return {
            'total_errors': sum(errors.values()),
            'error_breakdown': dict(errors),
            'time_range': {
                'start': timestamps[0] if timestamps else None,
                'end': timestamps[-1] if timestamps else None
            }
        }
    
    def detect_error_spike(self, log_file, threshold=10):
        """Detect error spikes in time windows"""
        # Simple example: count errors per minute
        errors_per_minute = Counter()
        
        with open(log_file, 'r') as f:
            for line in f:
                if 'ERROR' in line or 'error' in line:
                    ts_match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', line)
                    if ts_match:
                        minute = ts_match.group()
                        errors_per_minute[minute] += 1
        
        # Find spikes
        spikes = {time: count for time, count in errors_per_minute.items() 
                  if count > threshold}
        
        return spikes

# Example usage
def analyze_sample_logs():
    # Create sample log file
    sample_logs = """
2026-07-13T10:00:00 INFO Application started
2026-07-13T10:01:00 ERROR Connection timeout to database
2026-07-13T10:01:30 ERROR Connection timeout to database
2026-07-13T10:02:00 WARN High memory usage detected
2026-07-13T10:03:00 ERROR HTTP 503 Service Unavailable
2026-07-13T10:03:15 ERROR HTTP 502 Bad Gateway
2026-07-13T10:04:00 ERROR OutOfMemoryError in service
2026-07-13T10:05:00 INFO Service restarted
    """
    
    with open('sample.log', 'w') as f:
        f.write(sample_logs)
    
    # Analyze
    analyzer = LogAnalyzer()
    results = analyzer.analyze_logs('sample.log')
    
    print("✅ Log Analysis Complete")
    print(f"Total Errors: {results['total_errors']}")
    print(f"Error Breakdown: {results['error_breakdown']}")
    
    spikes = analyzer.detect_error_spike('sample.log', threshold=1)
    print(f"Error Spikes: {len(spikes)} time windows")
    
if __name__ == "__main__":
    analyze_sample_logs()
```

## Step 4: Predictive Analytics (5 mins)

Create `predictor.py`:

```python
from prophet import Prophet
import pandas as pd
import numpy as np

class ResourcePredictor:
    def __init__(self):
        self.model = None
        
    def train(self, historical_data):
        """Train on historical resource usage"""
        # Prophet expects 'ds' and 'y' columns
        df = pd.DataFrame({
            'ds': historical_data['timestamp'],
            'y': historical_data['value']
        })
        
        self.model = Prophet(
            changepoint_prior_scale=0.05,
            seasonality_mode='multiplicative'
        )
        self.model.fit(df)
        
    def predict(self, periods=24):
        """Predict future resource usage"""
        future = self.model.make_future_dataframe(periods=periods, freq='H')
        forecast = self.model.predict(future)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

# Example: Predict CPU usage
def predict_cpu_usage():
    # Generate sample historical data (30 days hourly)
    dates = pd.date_range(start='2026-06-13', end='2026-07-13', freq='H')
    
    # Simulate CPU usage with trend and seasonality
    trend = np.linspace(40, 60, len(dates))
    seasonality = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 24)
    noise = np.random.normal(0, 5, len(dates))
    cpu_usage = trend + seasonality + noise
    
    historical_data = pd.DataFrame({
        'timestamp': dates,
        'value': cpu_usage
    })
    
    # Train predictor
    predictor = ResourcePredictor()
    predictor.train(historical_data)
    
    # Predict next 24 hours
    forecast = predictor.predict(periods=24)
    
    print("✅ CPU Usage Prediction Complete")
    print(forecast.tail(10))
    
    # Alert if prediction exceeds threshold
    max_predicted = forecast['yhat'].tail(24).max()
    if max_predicted > 80:
        print(f"⚠️ ALERT: Predicted CPU usage will reach {max_predicted:.1f}%")
    
    return forecast

if __name__ == "__main__":
    predict_cpu_usage()
```

## Step 5: Automated Alerting (5 mins)

Create `alert_system.py`:

```python
import smtplib
from email.message import EmailMessage
from dataclasses import dataclass
from enum import Enum
from typing import List

class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

@dataclass
class Alert:
    title: str
    message: str
    severity: Severity
    source: str
    metrics: dict

class AlertManager:
    def __init__(self):
        self.alert_history = []
        self.suppression_rules = {}
        
    def send_alert(self, alert: Alert):
        """Send alert based on severity"""
        self.alert_history.append(alert)
        
        if self._should_suppress(alert):
            print(f"🔕 Alert suppressed: {alert.title}")
            return
        
        if alert.severity == Severity.CRITICAL:
            self._send_critical_alert(alert)
        elif alert.severity == Severity.WARNING:
            self._send_warning_alert(alert)
        else:
            self._log_info_alert(alert)
    
    def _should_suppress(self, alert: Alert) -> bool:
        """Check if alert should be suppressed"""
        # Simple suppression: don't send same alert twice in 5 minutes
        recent_alerts = [a for a in self.alert_history[-10:] 
                        if a.title == alert.title]
        return len(recent_alerts) > 1
    
    def _send_critical_alert(self, alert: Alert):
        print(f"🚨 CRITICAL: {alert.title}")
        print(f"   Source: {alert.source}")
        print(f"   Message: {alert.message}")
        print(f"   Metrics: {alert.metrics}")
        # In production: send to PagerDuty, Slack, etc.
    
    def _send_warning_alert(self, alert: Alert):
        print(f"⚠️ WARNING: {alert.title}")
        print(f"   {alert.message}")
    
    def _log_info_alert(self, alert: Alert):
        print(f"ℹ️ INFO: {alert.title}")
    
    def correlate_alerts(self, alerts: List[Alert]) -> List[Alert]:
        """Group related alerts"""
        # Simple correlation by source
        grouped = {}
        for alert in alerts:
            if alert.source not in grouped:
                grouped[alert.source] = []
            grouped[alert.source].append(alert)
        
        # Create summary alerts for groups
        correlated = []
        for source, group in grouped.items():
            if len(group) > 3:
                correlated.append(Alert(
                    title=f"Multiple issues detected on {source}",
                    message=f"{len(group)} alerts detected",
                    severity=max(a.severity for a in group),
                    source=source,
                    metrics={'alert_count': len(group)}
                ))
            else:
                correlated.extend(group)
        
        return correlated

# Example usage
def demo_alert_system():
    manager = AlertManager()
    
    # Create sample alerts
    alerts = [
        Alert(
            title="High CPU Usage",
            message="CPU usage exceeded 90% for 5 minutes",
            severity=Severity.WARNING,
            source="web-server-01",
            metrics={'cpu': 92, 'duration': 300}
        ),
        Alert(
            title="Service Unavailable",
            message="Service health check failed",
            severity=Severity.CRITICAL,
            source="api-service",
            metrics={'status_code': 503, 'attempts': 3}
        ),
        Alert(
            title="Disk Space Low",
            message="Disk usage at 85%",
            severity=Severity.INFO,
            source="web-server-01",
            metrics={'disk_usage': 85}
        )
    ]
    
    # Process alerts
    for alert in alerts:
        manager.send_alert(alert)
    
    print("\n✅ Alert System Demo Complete")

if __name__ == "__main__":
    demo_alert_system()
```

## Step 6: Complete AIOps Pipeline (5 mins)

Create `aiops_pipeline.py`:

```python
from anomaly_detector import AnomalyDetector
from log_analyzer import LogAnalyzer
from predictor import ResourcePredictor
from alert_system import AlertManager, Alert, Severity
import pandas as pd
import numpy as np

class AIOPsPipeline:
    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.log_analyzer = LogAnalyzer()
        self.predictor = ResourcePredictor()
        self.alert_manager = AlertManager()
    
    def run_monitoring_cycle(self):
        """Execute complete AIOps monitoring cycle"""
        print("🚀 Starting AIOps Pipeline...")
        
        # 1. Collect current metrics
        current_metrics = self._collect_metrics()
        
        # 2. Detect anomalies
        anomalies = self._check_anomalies(current_metrics)
        
        # 3. Analyze logs
        log_insights = self._analyze_logs()
        
        # 4. Predict future issues
        predictions = self._predict_capacity()
        
        # 5. Generate and correlate alerts
        alerts = self._generate_alerts(anomalies, log_insights, predictions)
        
        # 6. Take action
        self._auto_remediate(alerts)
        
        print("✅ AIOps Pipeline Complete")
        
    def _collect_metrics(self):
        """Simulate metric collection"""
        return {
            'cpu': np.random.normal(60, 15),
            'memory': np.random.normal(70, 10),
            'disk_io': np.random.normal(50, 20)
        }
    
    def _check_anomalies(self, metrics):
        """Check for anomalies in metrics"""
        anomalies = []
        for metric, value in metrics.items():
            if value > 90:
                anomalies.append({
                    'metric': metric,
                    'value': value,
                    'threshold': 90
                })
        return anomalies
    
    def _analyze_logs(self):
        """Analyze application logs"""
        # In production: read from actual log source
        return {'error_count': 0, 'patterns': []}
    
    def _predict_capacity(self):
        """Predict resource capacity needs"""
        # Simplified prediction
        return {'cpu_forecast': 75, 'memory_forecast': 80}
    
    def _generate_alerts(self, anomalies, log_insights, predictions):
        """Generate alerts from findings"""
        alerts = []
        
        for anomaly in anomalies:
            alerts.append(Alert(
                title=f"Anomaly Detected: {anomaly['metric']}",
                message=f"{anomaly['metric']} at {anomaly['value']:.1f}%",
                severity=Severity.WARNING,
                source="aiops-pipeline",
                metrics=anomaly
            ))
        
        if predictions['cpu_forecast'] > 90:
            alerts.append(Alert(
                title="Predicted Capacity Issue",
                message="CPU will exceed capacity within 24h",
                severity=Severity.WARNING,
                source="predictor",
                metrics=predictions
            ))
        
        return alerts
    
    def _auto_remediate(self, alerts):
        """Attempt automated remediation"""
        for alert in alerts:
            self.alert_manager.send_alert(alert)
            
            # Example auto-remediation
            if "CPU" in alert.title and alert.severity == Severity.WARNING:
                print("🔧 Auto-remediation: Scaling up resources...")

if __name__ == "__main__":
    pipeline = AIOPsPipeline()
    pipeline.run_monitoring_cycle()
```

## 🎓 What You've Learned

✅ Anomaly detection for metrics
✅ Log pattern analysis
✅ Predictive analytics
✅ Intelligent alerting
✅ Alert correlation
✅ End-to-end AIOps pipeline

## Next Steps

1. **Explore Basics**: Read [What is AIOps](01-basics/01-what-is-aiops.md)
2. **Deep Dive**: Learn about [Root Cause Analysis](02-intermediate/08-root-cause-analysis.md)
3. **Practice**: Work through exercises in `aiops-practice/`
4. **Build**: Create production AIOps solution

## Common Issues & Solutions

### Issue: High false positive rate
```python
# Adjust contamination parameter
detector = AnomalyDetector(contamination=0.01)  # Lower value
```

### Issue: Prophet installation fails
```bash
# Install dependencies first
pip install pystan==2.19.1.1
pip install prophet
```

### Issue: Memory usage too high
```python
# Use sampling for large datasets
sample_data = data.sample(frac=0.1)
```

## Useful Resources

- [Prophet Documentation](https://facebook.github.io/prophet/)
- [scikit-learn Anomaly Detection](https://scikit-learn.org/stable/modules/outlier_detection.html)
- [Elasticsearch ML](https://www.elastic.co/what-is/elasticsearch-machine-learning)

---
Ready to dive deeper? Start with [01-basics](01-basics/)!
