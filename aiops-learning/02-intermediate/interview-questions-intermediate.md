# AIOps Interview Questions - Intermediate

## Anomaly Detection Questions

### Q1: Explain the difference between Isolation Forest and One-Class SVM for anomaly detection.

**Answer**:

**Isolation Forest**:
- Based on decision trees
- Isolates anomalies by random partitioning
- Fast and efficient for high-dimensional data
- Works well with large datasets
- Less sensitive to hyperparameters

**One-Class SVM**:
- Based on support vector machines
- Finds decision boundary around normal data
- Better for low-dimensional data
- Can be slow on large datasets
- More sensitive to kernel choice and parameters

**When to use each**:
```python
# Isolation Forest: Large dataset, many features
if data_size > 100_000 and num_features > 10:
    detector = IsolationForest(contamination=0.05)

# One-Class SVM: Small dataset, few features, complex boundaries
else:
    detector = OneClassSVM(nu=0.05, kernel='rbf')
```

---

### Q2: How do you handle seasonality in time series anomaly detection?

**Answer**:

**Method 1: Prophet**
```python
from prophet import Prophet

# Automatically handles daily/weekly/yearly seasonality
model = Prophet(
    daily_seasonality=True,
    weekly_seasonality=True,
    yearly_seasonality=False
)

model.fit(df)
forecast = model.predict(df)

# Anomalies outside confidence bounds
anomalies = (df['y'] < forecast['yhat_lower']) | (df['y'] > forecast['yhat_upper'])
```

**Method 2: STL Decomposition**
```python
from statsmodels.tsa.seasonal import STL

# Decompose into trend, seasonal, residual
stl = STL(data, seasonal=13)
result = stl.fit()

# Detect anomalies in residuals
residuals = result.resid
threshold = 3 * residuals.std()
anomalies = abs(residuals) > threshold
```

**Method 3: Remove Seasonality First**
```python
# Calculate seasonal baseline (e.g., average for each hour of week)
df['hour_of_week'] = df.index.dayofweek * 24 + df.index.hour
seasonal_baseline = df.groupby('hour_of_week')['value'].mean()

# Remove seasonality
df['deseasonalized'] = df['value'] - df['hour_of_week'].map(seasonal_baseline)

# Detect anomalies in deseasonalized data
detector = IsolationForest()
anomalies = detector.fit_predict(df[['deseasonalized']])
```

---

### Q3: How would you reduce false positives in anomaly detection?

**Answer**:

**1. Ensemble Methods**
```python
class EnsembleAnomalyDetector:
    def __init__(self):
        self.models = [
            IsolationForest(contamination=0.05),
            OneClassSVM(nu=0.05),
            LocalOutlierFactor(contamination=0.05, novelty=True)
        ]
        self.voting_threshold = 2  # Require 2/3 agreement
    
    def fit(self, X):
        for model in self.models:
            model.fit(X)
        return self
    
    def predict(self, X):
        votes = sum(model.predict(X) == -1 for model in self.models)
        return votes >= self.voting_threshold
```

**2. Contextual Filtering**
```python
def filter_false_positives(anomalies, context):
    """Filter anomalies based on context"""
    filtered = []
    
    for anomaly in anomalies:
        # Ignore anomalies during known maintenance windows
        if is_maintenance_window(anomaly['timestamp']):
            continue
        
        # Ignore anomalies during deployments
        if recent_deployment(anomaly['service'], anomaly['timestamp']):
            continue
        
        # Ignore if correlated metric is also anomalous (expected)
        if correlated_metric_anomalous(anomaly):
            continue
        
        filtered.append(anomaly)
    
    return filtered
```

**3. Adaptive Thresholding**
```python
# Adjust threshold based on false positive feedback
class AdaptiveDetector:
    def __init__(self):
        self.contamination = 0.05
        self.false_positive_rate = 0.0
    
    def update_from_feedback(self, was_false_positive):
        if was_false_positive:
            self.false_positive_rate += 0.01
            self.contamination = max(0.01, self.contamination - 0.005)
        else:
            self.contamination = min(0.1, self.contamination + 0.001)
```

**4. Multi-Window Analysis**
```python
def multi_window_detection(data, windows=[10, 30, 60]):
    """Detect only if anomalous across multiple time windows"""
    anomaly_votes = 0
    
    for window in windows:
        detector = IsolationForest()
        detector.fit(data[-window:])
        if detector.predict([data[-1]])[0] == -1:
            anomaly_votes += 1
    
    # Require anomaly in at least 2 windows
    return anomaly_votes >= 2
```

---

## Log Analysis Questions

### Q4: How do you perform log clustering to find common error patterns?

**Answer**:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
import re

class LogClusterer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english'
        )
    
    def preprocess_log(self, log_line):
        """Clean log message"""
        # Remove timestamps
        log_line = re.sub(r'\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}', '', log_line)
        # Remove IPs
        log_line = re.sub(r'\\d+\\.\\d+\\.\\d+\\.\\d+', 'IP', log_line)
        # Remove UUIDs
        log_line = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 'UUID', log_line)
        # Remove numbers
        log_line = re.sub(r'\\d+', 'NUM', log_line)
        
        return log_line
    
    def cluster_logs(self, log_lines):
        """Cluster similar log messages"""
        # Preprocess
        cleaned = [self.preprocess_log(log) for log in log_lines]
        
        # Vectorize
        X = self.vectorizer.fit_transform(cleaned)
        
        # Cluster
        clustering = DBSCAN(eps=0.5, min_samples=5)
        labels = clustering.fit_predict(X)
        
        # Group by cluster
        clusters = {}
        for idx, label in enumerate(labels):
            if label == -1:  # Noise
                continue
            
            if label not in clusters:
                clusters[label] = []
            clusters[label].append({
                'original': log_lines[idx],
                'cleaned': cleaned[idx]
            })
        
        # Find representative message for each cluster
        patterns = {}
        for label, logs in clusters.items():
            # Most common cleaned message
            from collections import Counter
            most_common = Counter(log['cleaned'] for log in logs).most_common(1)[0][0]
            
            patterns[label] = {
                'pattern': most_common,
                'count': len(logs),
                'examples': [log['original'] for log in logs[:3]]
            }
        
        return patterns

# Usage
clusterer = LogClusterer()

error_logs = [
    "2026-07-13T10:00:00 ERROR Connection timeout to database db-001 after 5000ms",
    "2026-07-13T10:00:15 ERROR Connection timeout to database db-002 after 5000ms",
    "2026-07-13T10:01:00 ERROR OutOfMemory exception in service payment-api",
    "2026-07-13T10:01:30 ERROR Connection timeout to database db-001 after 5000ms"
]

patterns = clusterer.cluster_logs(error_logs)

for cluster_id, info in patterns.items():
    print(f"Pattern {cluster_id}: {info['count']} occurrences")
    print(f"  Template: {info['pattern']}")
    print(f"  Examples: {info['examples'][0]}")
```

---

### Q5: How do you correlate alerts to reduce alert fatigue?

**Answer**:

```python
from datetime import datetime, timedelta

class AlertCorrelationEngine:
    def __init__(self, time_window=60, dependency_graph=None):
        self.time_window = time_window  # seconds
        self.dependency_graph = dependency_graph or {}
    
    def correlate_alerts(self, alerts):
        """Group related alerts into incidents"""
        # Sort by time
        sorted_alerts = sorted(alerts, key=lambda a: a['timestamp'])
        
        incidents = []
        processed = set()
        
        for alert in sorted_alerts:
            if alert['id'] in processed:
                continue
            
            # Find related alerts
            related = self._find_related_alerts(alert, sorted_alerts)
            
            # Mark as processed
            processed.update(a['id'] for a in related)
            
            # Create incident
            incident = {
                'id': self._generate_incident_id(),
                'alerts': related,
                'root_cause': self._identify_root_cause(related),
                'affected_services': list(set(a['service'] for a in related)),
                'severity': max(a['severity'] for a in related, key=lambda s: self._severity_value(s)),
                'start_time': min(a['timestamp'] for a in related),
                'end_time': max(a['timestamp'] for a in related)
            }
            
            incidents.append(incident)
        
        return incidents
    
    def _find_related_alerts(self, alert, all_alerts):
        """Find alerts related by time and dependency"""
        related = [alert]
        
        for other in all_alerts:
            if other['id'] == alert['id']:
                continue
            
            # Check time window
            time_diff = abs((other['timestamp'] - alert['timestamp']).total_seconds())
            if time_diff > self.time_window:
                continue
            
            # Check if services are related
            if self._are_services_related(alert['service'], other['service']):
                related.append(other)
        
        return related
    
    def _are_services_related(self, service1, service2):
        """Check if services have dependency relationship"""
        # Direct dependency
        if service2 in self.dependency_graph.get(service1, []):
            return True
        
        # Reverse dependency
        if service1 in self.dependency_graph.get(service2, []):
            return True
        
        # Common dependency
        deps1 = set(self.dependency_graph.get(service1, []))
        deps2 = set(self.dependency_graph.get(service2, []))
        if deps1 & deps2:  # Intersection
            return True
        
        return False
    
    def _identify_root_cause(self, related_alerts):
        """Identify root cause from related alerts"""
        # Find first alert
        first_alert = min(related_alerts, key=lambda a: a['timestamp'])
        
        # Check if it's a dependency of others
        first_service = first_alert['service']
        other_services = [a['service'] for a in related_alerts if a != first_alert]
        
        if all(svc in self.dependency_graph.get(first_service, []) 
               for svc in other_services):
            return {
                'service': first_service,
                'type': first_alert['type'],
                'confidence': 0.9
            }
        
        return {
            'service': first_service,
            'type': first_alert['type'],
            'confidence': 0.7
        }
    
    def _severity_value(self, severity):
        """Convert severity to numeric value"""
        mapping = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        return mapping.get(severity, 0)
    
    def _generate_incident_id(self):
        import uuid
        return f"INC-{uuid.uuid4().hex[:8]}"

# Usage
dependency_graph = {
    'api-gateway': ['auth-service', 'payment-api', 'user-api'],
    'payment-api': ['database', 'redis'],
    'user-api': ['database', 'redis']
}

engine = AlertCorrelationEngine(
    time_window=60,
    dependency_graph=dependency_graph
)

alerts = [
    {'id': 1, 'timestamp': datetime(2026, 7, 13, 10, 0, 0), 
     'service': 'database', 'type': 'high_connections', 'severity': 'HIGH'},
    {'id': 2, 'timestamp': datetime(2026, 7, 13, 10, 0, 15), 
     'service': 'payment-api', 'type': 'timeout', 'severity': 'HIGH'},
    {'id': 3, 'timestamp': datetime(2026, 7, 13, 10, 0, 30), 
     'service': 'user-api', 'type': 'timeout', 'severity': 'MEDIUM'},
    {'id': 4, 'timestamp': datetime(2026, 7, 13, 10, 0, 45), 
     'service': 'api-gateway', 'type': '503_errors', 'severity': 'CRITICAL'}
]

incidents = engine.correlate_alerts(alerts)

print(f"Reduced {len(alerts)} alerts to {len(incidents)} incident(s)")
for incident in incidents:
    print(f"\nIncident {incident['id']}:")
    print(f"  Root cause: {incident['root_cause']['service']} - {incident['root_cause']['type']}")
    print(f"  Affected: {', '.join(incident['affected_services'])}")
    print(f"  Severity: {incident['severity']}")
    print(f"  Alert count: {len(incident['alerts'])}")
```

---

## Root Cause Analysis Questions

### Q6: Describe a multi-method approach to RCA.

**Answer**: Combine multiple analysis techniques for robust RCA:

**1. Dependency Analysis**
- Map service dependencies
- Find root service in failure chain

**2. Timeline Analysis**
- Order events chronologically
- Identify first failure

**3. Metrics Correlation**
- Correlate metrics with symptoms
- Find metrics that changed significantly

**4. Log Analysis**
- Parse logs for error patterns
- Find first error occurrence

**5. ML Prediction**
- Train on historical incidents
- Predict root cause based on patterns

**Integration**:
```python
class IntegratedRCA:
    def analyze(self, incident):
        results = {
            'dependency': self.dependency_analysis(incident),
            'timeline': self.timeline_analysis(incident),
            'metrics': self.metrics_analysis(incident),
            'logs': self.log_analysis(incident),
            'ml': self.ml_prediction(incident)
        }
        
        # Weighted voting
        weights = {
            'dependency': 0.25,
            'timeline': 0.15,
            'metrics': 0.20,
            'logs': 0.20,
            'ml': 0.20
        }
        
        root_cause = self.synthesize(results, weights)
        confidence = self.calculate_confidence(results)
        
        return {
            'root_cause': root_cause,
            'confidence': confidence,
            'evidence': results
        }
```

---

## Predictive Analytics Questions

### Q7: How would you predict disk space exhaustion?

**Answer**:

```python
from prophet import Prophet
import pandas as pd

def predict_disk_exhaustion(historical_usage):
    """Predict when disk will be full"""
    # Prepare data
    df = pd.DataFrame({
        'ds': historical_usage['timestamp'],
        'y': historical_usage['disk_usage_percent']
    })
    
    # Train Prophet
    model = Prophet(
        changepoint_prior_scale=0.05,
        yearly_seasonality=False
    )
    model.fit(df)
    
    # Forecast next 30 days
    future = model.make_future_dataframe(periods=30, freq='D')
    forecast = model.predict(future)
    
    # Find when it crosses 95% threshold
    future_forecast = forecast[forecast['ds'] > df['ds'].max()]
    critical_threshold = 95
    
    will_exceed = future_forecast[future_forecast['yhat'] > critical_threshold]
    
    if not will_exceed.empty:
        first_exceed = will_exceed.iloc[0]
        days_until_full = (first_exceed['ds'] - pd.Timestamp.now()).days
        
        return {
            'will_exceed': True,
            'days_until_full': days_until_full,
            'predicted_usage': first_exceed['yhat'],
            'exceed_date': first_exceed['ds'],
            'action': 'provision_storage' if days_until_full < 7 else 'schedule_cleanup'
        }
    
    return {
        'will_exceed': False,
        'status': 'OK for next 30 days'
    }

# Usage
historical = pd.read_csv('disk_usage_history.csv')
prediction = predict_disk_exhaustion(historical)

if prediction['will_exceed']:
    print(f"⚠️ Disk will reach 95% in {prediction['days_until_full']} days")
    print(f"   Action: {prediction['action']}")
    
    # Auto-remediate
    if prediction['days_until_full'] < 7:
        provision_additional_storage(size='100GB')
```

---

### Q8: How do you detect concept drift in production models?

**Answer**:

```python
from scipy.stats import ks_2samp
import numpy as np

class DriftDetector:
    def __init__(self, reference_data):
        self.reference_data = reference_data
        self.drift_threshold = 0.05  # p-value threshold
    
    def detect_drift(self, current_data):
        """Detect if data distribution has changed"""
        drift_report = {}
        
        for feature in self.reference_data.columns:
            ref_values = self.reference_data[feature]
            curr_values = current_data[feature]
            
            # Kolmogorov-Smirnov test
            statistic, p_value = ks_2samp(ref_values, curr_values)
            
            has_drift = p_value < self.drift_threshold
            
            drift_report[feature] = {
                'drift_detected': has_drift,
                'ks_statistic': statistic,
                'p_value': p_value,
                'severity': self._categorize_drift(statistic)
            }
        
        # Overall drift decision
        drifted_features = [f for f, d in drift_report.items() 
                           if d['drift_detected']]
        
        return {
            'dataset_drift': len(drifted_features) > 0,
            'drifted_features': drifted_features,
            'drift_details': drift_report,
            'recommendation': self._get_recommendation(drifted_features)
        }
    
    def _categorize_drift(self, ks_statistic):
        """Categorize drift severity"""
        if ks_statistic > 0.3:
            return 'HIGH'
        elif ks_statistic > 0.15:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_recommendation(self, drifted_features):
        """Recommend action based on drift"""
        if len(drifted_features) > 5:
            return 'RETRAIN_IMMEDIATELY'
        elif len(drifted_features) > 2:
            return 'SCHEDULE_RETRAINING'
        elif len(drifted_features) > 0:
            return 'MONITOR_CLOSELY'
        else:
            return 'NO_ACTION_NEEDED'

# Usage
# Reference data (training data)
reference = pd.read_csv('training_data.csv')

# Current production data
current = pd.read_csv('production_data_last_week.csv')

detector = DriftDetector(reference)
result = detector.detect_drift(current)

if result['dataset_drift']:
    print(f"⚠️ Data drift detected in {len(result['drifted_features'])} features")
    print(f"   Drifted features: {', '.join(result['drifted_features'])}")
    print(f"   Recommendation: {result['recommendation']}")
    
    if result['recommendation'] == 'RETRAIN_IMMEDIATELY':
        trigger_model_retraining()
```

---

## Quick Answer Questions

### Q9: What's the difference between data drift and concept drift?

**Answer**:
- **Data Drift**: Input feature distributions change (P(X) changes)
- **Concept Drift**: Relationship between features and target changes (P(Y|X) changes)

Example:
- Data drift: Customer ages shift from 20-30 to 40-50
- Concept drift: Buying behavior changes (same age, different purchases)

### Q10: Name three methods to reduce MTTR.

**Answer**:
1. **Automated RCA**: AI identifies root cause in < 5 minutes
2. **Alert Correlation**: Reduce noise, focus on real issues
3. **Automated Remediation**: Auto-fix common problems

---

**Next Level**: Ready for advanced? Check [Advanced Interview Questions](../03-advanced/interview-questions-advanced.md)
