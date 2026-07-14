# First AIOps Implementation

## Learning Objectives
- Build your first AIOps project
- Implement basic anomaly detection
- Set up automated alerting
- Create a simple AIOps dashboard

---

## Project Overview

We'll build a simple but complete AIOps system that:
1. Collects metrics from a web application
2. Detects anomalies using machine learning
3. Sends alerts when issues are detected
4. Displays insights on a dashboard

---

## Architecture

```
Web Application
    ↓
Metrics Collection (Prometheus)
    ↓
Data Processing (Python)
    ↓
Anomaly Detection (Isolation Forest)
    ↓
Alert Manager
    ↓
Dashboard (Grafana)
```

---

## Step 1: Setup Environment

### Install Required Tools
```bash
# Create virtual environment
python -m venv aiops-env
source aiops-env/bin/activate  # On Windows: aiops-env\Scripts\activate

# Install Python packages
pip install prometheus-client flask pandas scikit-learn requests

# Install Prometheus (download from prometheus.io)
# Install Grafana (download from grafana.com)
```

---

## Step 2: Create Sample Application

### Simple Flask Application with Metrics
```python
# app.py
from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import random
import time

app = Flask(__name__)

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration'
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

error_rate = Gauge(
    'error_rate',
    'Current error rate'
)

@app.route('/')
def home():
    start = time.time()
    
    # Simulate some work
    time.sleep(random.uniform(0.1, 0.5))
    
    # Randomly inject errors
    if random.random() < 0.1:  # 10% error rate
        request_count.labels(method='GET', endpoint='/', status='500').inc()
        duration = time.time() - start
        request_duration.observe(duration)
        return jsonify({"error": "Internal server error"}), 500
    
    request_count.labels(method='GET', endpoint='/', status='200').inc()
    duration = time.time() - start
    request_duration.observe(duration)
    
    return jsonify({"message": "Hello, AIOps!"})

@app.route('/metrics')
def metrics():
    """Expose metrics for Prometheus"""
    return generate_latest()

@app.route('/load')
def simulate_load():
    """Simulate high load"""
    # Update active users
    active_users.set(random.randint(50, 200))
    
    # Update error rate
    error_rate.set(random.uniform(0, 0.5))
    
    return jsonify({"status": "load simulated"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Run the Application
```bash
python app.py
```

---

## Step 3: Configure Prometheus

### prometheus.yml
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'flask_app'
    static_configs:
      - targets: ['localhost:8080']
```

### Start Prometheus
```bash
./prometheus --config.file=prometheus.yml
```

Access Prometheus at: http://localhost:9090

---

## Step 4: Implement Anomaly Detection

### anomaly_detector.py
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from prometheus_api_client import PrometheusConnect
import time
from datetime import datetime, timedelta

class AIOpsAnomalyDetector:
    """Simple AIOps anomaly detection system"""
    
    def __init__(self, prometheus_url='http://localhost:9090'):
        self.prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False
    
    def collect_metrics(self, metric_name, duration='1h'):
        """Collect metrics from Prometheus"""
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        
        # Query Prometheus
        metric_data = self.prom.get_metric_range_data(
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time,
        )
        
        if not metric_data:
            return pd.DataFrame()
        
        # Convert to DataFrame
        values = []
        timestamps = []
        
        for datapoint in metric_data[0]['values']:
            timestamps.append(pd.to_datetime(datapoint[0], unit='s'))
            values.append(float(datapoint[1]))
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'value': values
        })
        
        return df
    
    def engineer_features(self, df):
        """Create features for anomaly detection"""
        
        if df.empty:
            return df
        
        df = df.copy()
        
        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Rolling statistics
        df['rolling_mean'] = df['value'].rolling(window=10, min_periods=1).mean()
        df['rolling_std'] = df['value'].rolling(window=10, min_periods=1).std()
        
        # Rate of change
        df['rate_of_change'] = df['value'].diff()
        
        # Fill NaN values
        df.fillna(method='bfill', inplace=True)
        df.fillna(method='ffill', inplace=True)
        
        return df
    
    def train(self, df):
        """Train anomaly detection model"""
        
        if df.empty or len(df) < 10:
            print("Not enough data to train")
            return False
        
        df = self.engineer_features(df)
        
        # Select features for training
        feature_columns = ['value', 'hour', 'day_of_week', 'is_weekend',
                          'rolling_mean', 'rolling_std', 'rate_of_change']
        
        X = df[feature_columns].values
        
        # Train model
        self.model.fit(X)
        self.is_trained = True
        
        print(f"Model trained on {len(df)} data points")
        return True
    
    def detect_anomalies(self, df):
        """Detect anomalies in new data"""
        
        if not self.is_trained:
            print("Model not trained yet")
            return df
        
        if df.empty:
            return df
        
        df = self.engineer_features(df)
        
        # Select features
        feature_columns = ['value', 'hour', 'day_of_week', 'is_weekend',
                          'rolling_mean', 'rolling_std', 'rate_of_change']
        
        X = df[feature_columns].values
        
        # Predict anomalies
        predictions = self.model.predict(X)
        df['is_anomaly'] = predictions == -1
        
        # Calculate anomaly score
        scores = self.model.score_samples(X)
        df['anomaly_score'] = scores
        
        return df
    
    def run_continuous_detection(self, metric_name, check_interval=60):
        """Continuously monitor and detect anomalies"""
        
        print(f"Starting continuous anomaly detection for {metric_name}")
        print("Training initial model...")
        
        # Initial training
        training_data = self.collect_metrics(metric_name, duration='1h')
        self.train(training_data)
        
        print("Starting monitoring...")
        
        while True:
            try:
                # Collect recent data
                recent_data = self.collect_metrics(metric_name, duration='15m')
                
                if not recent_data.empty:
                    # Detect anomalies
                    results = self.detect_anomalies(recent_data)
                    
                    # Check for anomalies
                    anomalies = results[results['is_anomaly'] == True]
                    
                    if not anomalies.empty:
                        self.alert_anomalies(metric_name, anomalies)
                    else:
                        print(f"[{datetime.now()}] No anomalies detected")
                
                # Wait before next check
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"Error in detection loop: {e}")
                time.sleep(check_interval)
    
    def alert_anomalies(self, metric_name, anomalies):
        """Send alerts for detected anomalies"""
        
        print(f"\n{'='*60}")
        print(f"⚠️  ANOMALY DETECTED in {metric_name}")
        print(f"{'='*60}")
        print(f"Time: {anomalies.iloc[0]['timestamp']}")
        print(f"Value: {anomalies.iloc[0]['value']:.2f}")
        print(f"Anomaly Score: {anomalies.iloc[0]['anomaly_score']:.4f}")
        print(f"Rolling Mean: {anomalies.iloc[0]['rolling_mean']:.2f}")
        print(f"{'='*60}\n")
        
        # In production, send to Slack, PagerDuty, etc.
        self.send_to_slack(metric_name, anomalies)
    
    def send_to_slack(self, metric_name, anomalies):
        """Send alert to Slack (example)"""
        # Uncomment and configure with your Slack webhook
        # import requests
        # webhook_url = "YOUR_SLACK_WEBHOOK_URL"
        # message = {
        #     "text": f"Anomaly detected in {metric_name}",
        #     "attachments": [{
        #         "color": "danger",
        #         "fields": [
        #             {"title": "Value", "value": str(anomalies.iloc[0]['value'])},
        #             {"title": "Time", "value": str(anomalies.iloc[0]['timestamp'])}
        #         ]
        #     }]
        # }
        # requests.post(webhook_url, json=message)
        pass

# Usage
if __name__ == '__main__':
    detector = AIOpsAnomalyDetector()
    
    # Monitor request duration
    detector.run_continuous_detection(
        metric_name='http_request_duration_seconds',
        check_interval=30  # Check every 30 seconds
    )
```

### Run the Detector
```bash
# Install prometheus API client
pip install prometheus-api-client

# Run detector
python anomaly_detector.py
```

---

## Step 5: Generate Test Traffic

### load_generator.py
```python
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor

def send_request():
    """Send a request to the application"""
    try:
        response = requests.get('http://localhost:8080/')
        return response.status_code
    except Exception as e:
        return None

def simulate_normal_traffic(duration_seconds=300, requests_per_second=10):
    """Simulate normal traffic"""
    print(f"Generating normal traffic: {requests_per_second} req/s for {duration_seconds}s")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        end_time = time.time() + duration_seconds
        
        while time.time() < end_time:
            futures = []
            for _ in range(requests_per_second):
                futures.append(executor.submit(send_request))
            
            time.sleep(1)
    
    print("Normal traffic completed")

def simulate_anomaly(duration_seconds=60, requests_per_second=100):
    """Simulate anomalous traffic (spike)"""
    print(f"⚠️  Generating anomalous traffic: {requests_per_second} req/s for {duration_seconds}s")
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        end_time = time.time() + duration_seconds
        
        while time.time() < end_time:
            futures = []
            for _ in range(requests_per_second):
                futures.append(executor.submit(send_request))
            
            time.sleep(1)
    
    print("Anomalous traffic completed")

if __name__ == '__main__':
    # Simulate normal traffic
    simulate_normal_traffic(duration_seconds=120, requests_per_second=10)
    
    # Wait a bit
    time.sleep(10)
    
    # Simulate anomaly
    simulate_anomaly(duration_seconds=30, requests_per_second=50)
    
    # Return to normal
    time.sleep(10)
    simulate_normal_traffic(duration_seconds=120, requests_per_second=10)
```

### Run Load Generator
```bash
python load_generator.py
```

---

## Step 6: Create Dashboard

### Configure Grafana

1. **Add Prometheus Data Source**
   - Go to Configuration → Data Sources
   - Add Prometheus
   - URL: http://localhost:9090

2. **Create Dashboard**

```json
{
  "dashboard": {
    "title": "AIOps Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[1m])"
          }
        ]
      },
      {
        "title": "Request Duration P95",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=\"500\"}[1m])"
          }
        ]
      },
      {
        "title": "Active Users",
        "targets": [
          {
            "expr": "active_users"
          }
        ]
      }
    ]
  }
}
```

---

## Step 7: Enhanced Alerting

### alert_manager.py
```python
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

class AlertManager:
    """Manage and send alerts"""
    
    def __init__(self):
        self.alert_history = []
        self.alert_threshold = 3  # Number of anomalies before alerting
        self.alert_window = 300  # Time window in seconds
    
    def should_alert(self, anomalies):
        """Determine if we should send an alert"""
        
        # Count recent alerts
        recent_time = datetime.now().timestamp() - self.alert_window
        recent_alerts = [a for a in self.alert_history 
                        if a['timestamp'] > recent_time]
        
        if len(recent_alerts) >= self.alert_threshold:
            return True
        
        return False
    
    def send_email_alert(self, subject, body):
        """Send email alert"""
        
        # Configure your email settings
        sender = "alerts@aiops.com"
        receivers = ["ops-team@company.com"]
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ", ".join(receivers)
        
        # Uncomment to actually send
        # try:
        #     smtp = smtplib.SMTP('localhost')
        #     smtp.send_message(msg)
        #     smtp.quit()
        #     print("Alert email sent")
        # except Exception as e:
        #     print(f"Failed to send email: {e}")
    
    def create_incident(self, anomaly_data):
        """Create incident ticket (e.g., in Jira, PagerDuty)"""
        
        incident = {
            'title': f"Anomaly Detected: {anomaly_data['metric_name']}",
            'severity': 'high',
            'description': f"Anomalous behavior detected at {anomaly_data['timestamp']}",
            'timestamp': datetime.now()
        }
        
        print(f"Incident created: {incident['title']}")
        
        # In production, integrate with ticketing system
        # jira.create_issue(...)
        # pagerduty.trigger_incident(...)
        
        return incident
```

---

## Complete System Integration

### main.py
```python
import threading
from app import app as flask_app
from anomaly_detector import AIOpsAnomalyDetector

def run_flask_app():
    """Run Flask application"""
    flask_app.run(host='0.0.0.0', port=8080)

def run_anomaly_detection():
    """Run anomaly detection"""
    detector = AIOpsAnomalyDetector()
    detector.run_continuous_detection('http_request_duration_seconds')

if __name__ == '__main__':
    # Start Flask app in separate thread
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    # Wait for app to start
    import time
    time.sleep(2)
    
    # Start anomaly detection
    run_anomaly_detection()
```

---

## Testing Your AIOps System

### Test Script
```bash
#!/bin/bash

echo "Starting AIOps System Test..."

# 1. Start Prometheus
echo "Starting Prometheus..."
./prometheus --config.file=prometheus.yml &
PROM_PID=$!

# 2. Start application with anomaly detection
echo "Starting application..."
python main.py &
APP_PID=$!

# Wait for services to start
sleep 5

# 3. Generate test traffic
echo "Generating test traffic..."
python load_generator.py

# 4. Check results
echo "Checking Prometheus metrics..."
curl http://localhost:9090/api/v1/query?query=http_requests_total

echo ""
echo "Test complete!"
echo "- Prometheus UI: http://localhost:9090"
echo "- Application metrics: http://localhost:8080/metrics"
echo "- Grafana: http://localhost:3000"

# Keep running
wait
```

---

## Next Steps

### Enhancements to Try:

1. **Add More ML Models**
   - LSTM for time series
   - AutoEncoders for multi-dimensional anomalies
   - Prophet for forecasting

2. **Improve Alerting**
   - Integrate with Slack/Teams
   - Add alert suppression
   - Implement escalation policies

3. **Add More Data Sources**
   - Application logs
   - Distributed traces
   - Infrastructure metrics

4. **Build Advanced Features**
   - Automated root cause analysis
   - Predictive maintenance
   - Auto-remediation

---

## Summary

You've built a complete AIOps system with:
- ✅ Metrics collection
- ✅ Anomaly detection with ML
- ✅ Automated alerting
- ✅ Monitoring dashboard

This foundation can be extended to handle:
- Multiple services
- Complex distributed systems
- Advanced ML models
- Automated remediation

---

**Next**: [Intermediate Topics →](../02-intermediate/06-anomaly-detection.md)
