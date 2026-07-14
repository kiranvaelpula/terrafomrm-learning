# Root Cause Analysis (RCA) with AI

## Overview

Automated Root Cause Analysis uses AI to quickly identify the underlying cause of incidents by analyzing dependencies, timelines, metrics, and logs.

## RCA Fundamentals

### Traditional RCA vs AI-Powered RCA

**Traditional RCA**:
```
Incident → Manual investigation → Check logs → 
Check metrics → Ask teams → Find root cause
Time: 2-4 hours
```

**AI-Powered RCA**:
```
Incident → AI analyzes all data → Root cause identified
Time: < 5 minutes
```

## Dependency-Based RCA

### Service Dependency Graph
```python
class ServiceDependencyGraph:
    def __init__(self):
        self.graph = {
            'api-gateway': ['auth-service', 'payment-api', 'user-api'],
            'payment-api': ['database', 'redis-cache', 'payment-processor'],
            'user-api': ['database', 'redis-cache'],
            'auth-service': ['database', 'ldap-server']
        }
    
    def get_dependencies(self, service):
        """Get all dependencies of a service"""
        return self.graph.get(service, [])
    
    def get_dependents(self, service):
        """Get services that depend on this service"""
        dependents = []
        for svc, deps in self.graph.items():
            if service in deps:
                dependents.append(svc)
        return dependents
    
    def find_root_service(self, affected_services):
        """Find the root service causing cascading failures"""
        # Service that others depend on
        for service in affected_services:
            dependencies = self.get_dependencies(service)
            
            # If all other affected services depend on this one
            if all(svc in dependencies for svc in affected_services if svc != service):
                return service
        
        # If no clear root, return service with most dependents
        max_dependents = 0
        root = None
        for service in affected_services:
            deps_count = len(self.get_dependents(service))
            if deps_count > max_dependents:
                max_dependents = deps_count
                root = service
        
        return root

# Usage
graph = ServiceDependencyGraph()

# Incident: Multiple services failing
affected = ['api-gateway', 'payment-api', 'user-api']

root_service = graph.find_root_service(affected)
print(f"Root service: {root_service}")  # Output: database
```

## Timeline-Based RCA

### Event Timeline Analysis
```python
from datetime import datetime, timedelta

class TimelineAnalyzer:
    def __init__(self):
        self.events = []
    
    def add_event(self, timestamp, service, event_type, details):
        """Add event to timeline"""
        self.events.append({
            'timestamp': timestamp,
            'service': service,
            'type': event_type,
            'details': details
        })
    
    def analyze_timeline(self, incident_start):
        """Find first failure and related events"""
        # Sort events by time
        sorted_events = sorted(self.events, key=lambda e: e['timestamp'])
        
        # Find events around incident start (±5 minutes)
        window_start = incident_start - timedelta(minutes=5)
        window_end = incident_start + timedelta(minutes=5)
        
        relevant_events = [
            e for e in sorted_events
            if window_start <= e['timestamp'] <= window_end
        ]
        
        if not relevant_events:
            return None
        
        # First failure is likely the root cause
        first_failure = relevant_events[0]
        
        # Find correlated events
        correlated = [
            e for e in relevant_events
            if (e['timestamp'] - first_failure['timestamp']).total_seconds() < 60
        ]
        
        return {
            'root_event': first_failure,
            'correlated_events': correlated,
            'timeline': relevant_events
        }

# Usage
analyzer = TimelineAnalyzer()

# Add events
analyzer.add_event(
    datetime(2026, 7, 13, 10, 0, 0),
    'database',
    'connection_pool_full',
    {'connections': 1000, 'max': 1000}
)

analyzer.add_event(
    datetime(2026, 7, 13, 10, 0, 15),
    'payment-api',
    'timeout',
    {'timeout': '5s'}
)

analyzer.add_event(
    datetime(2026, 7, 13, 10, 0, 30),
    'api-gateway',
    '503_errors',
    {'error_rate': 0.95}
)

# Analyze
result = analyzer.analyze_timeline(datetime(2026, 7, 13, 10, 0, 0))
print(f"Root event: {result['root_event']['service']} - {result['root_event']['type']}")
```

## Metrics Correlation RCA

### Correlate Metrics to Find Root Cause
```python
import pandas as pd
from scipy.stats import pearsonr

class MetricsCorrelationRCA:
    def __init__(self, metrics_df):
        self.metrics = metrics_df
        self.correlation_matrix = metrics_df.corr()
    
    def find_root_cause_metric(self, target_metric, threshold=0.7):
        """Find metrics highly correlated with target metric"""
        correlations = self.correlation_matrix[target_metric].abs()
        
        # Exclude self-correlation
        correlations = correlations[correlations.index != target_metric]
        
        # Find highly correlated metrics
        high_correlation = correlations[correlations > threshold]
        
        return high_correlation.sort_values(ascending=False)
    
    def analyze_incident(self, incident_time, affected_metric):
        """Analyze metrics around incident time"""
        # Get metrics around incident (±30 minutes)
        start = incident_time - pd.Timedelta(minutes=30)
        end = incident_time + pd.Timedelta(minutes=30)
        
        incident_metrics = self.metrics[start:end]
        
        # Find what changed significantly
        before = self.metrics[start:incident_time].mean()
        after = self.metrics[incident_time:end].mean()
        
        changes = ((after - before) / before * 100).abs()
        significant_changes = changes[changes > 20].sort_values(ascending=False)
        
        # Correlate with affected metric
        correlations = self.find_root_cause_metric(affected_metric)
        
        # Root cause candidates: high correlation + significant change
        candidates = []
        for metric in correlations.index:
            if metric in significant_changes.index:
                candidates.append({
                    'metric': metric,
                    'correlation': correlations[metric],
                    'change_percent': significant_changes[metric]
                })
        
        return candidates

# Usage
# Metrics: timestamp, cpu, memory, disk_io, network, db_connections, latency
metrics_df = pd.read_csv('metrics.csv', index_col='timestamp', parse_dates=True)

rca = MetricsCorrelationRCA(metrics_df)

# Incident: High latency
incident_time = pd.Timestamp('2026-07-13 10:00:00')
candidates = rca.analyze_incident(incident_time, 'latency')

print("Root cause candidates:")
for candidate in candidates:
    print(f"  {candidate['metric']}: {candidate['correlation']:.2f} correlation, "
          f"{candidate['change_percent']:.1f}% change")

# Output:
# Root cause candidates:
#   db_connections: 0.89 correlation, 95.2% change
#   disk_io: 0.75 correlation, 45.3% change
```

## Log-Based RCA

### Analyze Logs for Root Cause
```python
import re
from collections import Counter

class LogBasedRCA:
    def __init__(self):
        self.error_patterns = {
            'connection_timeout': r'timeout|connection refused',
            'out_of_memory': r'OutOfMemory|OOM',
            'database_error': r'database.*error|sql.*exception',
            'permission_denied': r'permission denied|access denied',
            'file_not_found': r'no such file|file not found'
        }
    
    def analyze_logs(self, log_file, incident_start, incident_end):
        """Analyze logs during incident timeframe"""
        errors = Counter()
        first_errors = {}
        
        with open(log_file, 'r') as f:
            for line in f:
                # Extract timestamp
                ts_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
                if not ts_match:
                    continue
                
                timestamp = pd.Timestamp(ts_match.group(1))
                
                # Check if in incident timeframe
                if not (incident_start <= timestamp <= incident_end):
                    continue
                
                # Check for error patterns
                for error_type, pattern in self.error_patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        errors[error_type] += 1
                        
                        # Track first occurrence
                        if error_type not in first_errors:
                            first_errors[error_type] = {
                                'timestamp': timestamp,
                                'line': line.strip()
                            }
        
        # Root cause is likely the first error
        if first_errors:
            root_error = min(first_errors.items(), 
                           key=lambda x: x[1]['timestamp'])
            
            return {
                'root_cause': root_error[0],
                'first_occurrence': root_error[1],
                'error_counts': dict(errors),
                'all_errors': first_errors
            }
        
        return None

# Usage
rca = LogBasedRCA()

result = rca.analyze_logs(
    '/var/log/application.log',
    pd.Timestamp('2026-07-13 09:59:00'),
    pd.Timestamp('2026-07-13 10:05:00')
)

if result:
    print(f"Root cause: {result['root_cause']}")
    print(f"First seen: {result['first_occurrence']['timestamp']}")
    print(f"Log line: {result['first_occurrence']['line']}")
```

## Machine Learning RCA

### AI Model for RCA
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

class MLBasedRCA:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.label_encoder = LabelEncoder()
        self.feature_names = None
    
    def train(self, historical_incidents):
        """
        Train on historical incidents
        historical_incidents: DataFrame with features and 'root_cause' column
        """
        # Prepare features
        X = historical_incidents.drop('root_cause', axis=1)
        y = historical_incidents['root_cause']
        
        self.feature_names = X.columns.tolist()
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Train
        self.model.fit(X, y_encoded)
        
        return self
    
    def predict_root_cause(self, incident_features):
        """Predict root cause for new incident"""
        # Ensure correct feature order
        X = incident_features[self.feature_names]
        
        # Predict
        prediction = self.model.predict([X])[0]
        probabilities = self.model.predict_proba([X])[0]
        
        # Decode prediction
        root_cause = self.label_encoder.inverse_transform([prediction])[0]
        confidence = probabilities.max()
        
        # Get top 3 candidates
        top_3_indices = probabilities.argsort()[-3:][::-1]
        top_3_causes = [
            {
                'cause': self.label_encoder.inverse_transform([idx])[0],
                'confidence': probabilities[idx]
            }
            for idx in top_3_indices
        ]
        
        return {
            'root_cause': root_cause,
            'confidence': confidence,
            'top_candidates': top_3_causes
        }
    
    def get_feature_importance(self):
        """Get most important features for RCA"""
        importances = self.model.feature_importances_
        
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        return feature_importance

# Usage
# Historical data with features and known root causes
historical = pd.read_csv('historical_incidents.csv')

rca_model = MLBasedRCA()
rca_model.train(historical)

# New incident
incident_features = {
    'cpu_spike': 1,
    'memory_spike': 0,
    'disk_full': 0,
    'network_saturation': 0,
    'db_connections_high': 1,
    'error_rate_high': 1,
    'deployment_recent': 0
}

result = rca_model.predict_root_cause(pd.Series(incident_features))

print(f"Predicted root cause: {result['root_cause']}")
print(f"Confidence: {result['confidence']:.2%}")
print("\nTop candidates:")
for candidate in result['top_candidates']:
    print(f"  {candidate['cause']}: {candidate['confidence']:.2%}")
```

## Complete RCA System

### Integrated RCA Engine
```python
class IntegratedRCAEngine:
    def __init__(self):
        self.dependency_graph = ServiceDependencyGraph()
        self.timeline_analyzer = TimelineAnalyzer()
        self.metrics_rca = None
        self.log_rca = LogBasedRCA()
        self.ml_rca = None
    
    def analyze_incident(self, incident):
        """Complete RCA analysis"""
        results = {}
        
        # 1. Dependency analysis
        affected_services = incident['affected_services']
        root_service = self.dependency_graph.find_root_service(affected_services)
        results['root_service'] = root_service
        
        # 2. Timeline analysis
        timeline = self.timeline_analyzer.analyze_timeline(incident['start_time'])
        if timeline:
            results['root_event'] = timeline['root_event']
        
        # 3. Metrics correlation
        if self.metrics_rca:
            metric_candidates = self.metrics_rca.analyze_incident(
                incident['start_time'],
                incident['primary_symptom']
            )
            results['metric_candidates'] = metric_candidates
        
        # 4. Log analysis
        log_result = self.log_rca.analyze_logs(
            incident['log_file'],
            incident['start_time'] - timedelta(minutes=5),
            incident['start_time'] + timedelta(minutes=5)
        )
        if log_result:
            results['log_root_cause'] = log_result['root_cause']
        
        # 5. ML prediction
        if self.ml_rca:
            ml_result = self.ml_rca.predict_root_cause(incident['features'])
            results['ml_prediction'] = ml_result
        
        # 6. Synthesize findings
        root_cause = self._synthesize_findings(results)
        
        return {
            'root_cause': root_cause,
            'evidence': results,
            'confidence': self._calculate_confidence(results)
        }
    
    def _synthesize_findings(self, results):
        """Combine findings from different methods"""
        # Weight different sources
        weights = {
            'root_service': 0.3,
            'root_event': 0.2,
            'log_root_cause': 0.2,
            'ml_prediction': 0.3
        }
        
        # Simple voting mechanism (can be more sophisticated)
        votes = {}
        
        if 'root_service' in results:
            cause = f"{results['root_service']}_failure"
            votes[cause] = votes.get(cause, 0) + weights['root_service']
        
        if 'log_root_cause' in results:
            cause = results['log_root_cause']
            votes[cause] = votes.get(cause, 0) + weights['log_root_cause']
        
        if 'ml_prediction' in results:
            cause = results['ml_prediction']['root_cause']
            votes[cause] = votes.get(cause, 0) + weights['ml_prediction']
        
        # Return cause with highest vote
        if votes:
            return max(votes, key=votes.get)
        
        return 'unknown'
    
    def _calculate_confidence(self, results):
        """Calculate confidence in RCA"""
        # More evidence sources = higher confidence
        evidence_count = len(results)
        base_confidence = min(evidence_count * 0.25, 1.0)
        
        # Boost if multiple sources agree
        if 'ml_prediction' in results:
            base_confidence = max(base_confidence, 
                                 results['ml_prediction']['confidence'])
        
        return base_confidence

# Usage
engine = IntegratedRCAEngine()

incident = {
    'affected_services': ['api-gateway', 'payment-api', 'user-api'],
    'start_time': datetime(2026, 7, 13, 10, 0, 0),
    'primary_symptom': 'latency',
    'log_file': '/var/log/application.log',
    'features': {
        'cpu_spike': 0,
        'memory_spike': 0,
        'db_connections_high': 1,
        'error_rate_high': 1
    }
}

result = engine.analyze_incident(incident)

print(f"Root Cause: {result['root_cause']}")
print(f"Confidence: {result['confidence']:.0%}")
print("\nEvidence:")
for key, value in result['evidence'].items():
    print(f"  {key}: {value}")
```

## Best Practices

1. **Use Multiple Data Sources**: Combine logs, metrics, traces, and events
2. **Weight by Reliability**: Some sources are more reliable than others
3. **Time Windows**: Look at data before and after incident
4. **Dependencies Matter**: Always consider service relationships
5. **Learn from History**: Use ML on past incidents
6. **Confidence Scores**: Always provide confidence levels
7. **Human Validation**: Keep humans in the loop initially

## Next Steps

Continue to [Predictive Analytics](09-predictive-analytics.md)

---

**Key Takeaway**: Effective RCA combines multiple analysis methods and data sources to quickly identify root causes with high confidence.
