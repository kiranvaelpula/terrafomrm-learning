# Log Analysis & Pattern Recognition

## Learning Objectives
- Understand log analysis fundamentals for AIOps
- Implement pattern recognition in logs
- Extract insights from unstructured log data
- Build automated log analysis pipelines

---

## Why Log Analysis in AIOps?

Logs contain critical information about system behavior, errors, and security events. AIOps uses ML to:
- Automatically detect patterns and anomalies
- Identify error signatures
- Correlate logs across systems
- Predict issues before they occur

---

## Types of Logs

### 1. Application Logs
```python
# Example application log
2024-01-15 10:23:45 INFO [UserService] User login successful: user_id=12345
2024-01-15 10:23:47 ERROR [PaymentService] Payment failed: transaction_id=tx_789, error=timeout
2024-01-15 10:23:48 WARN [CacheService] Cache miss rate high: 45%
```

### 2. System Logs
```bash
# /var/log/syslog
Jan 15 10:23:45 server01 kernel: [12345.678] Out of memory: Kill process 1234 (java)
Jan 15 10:23:46 server01 systemd[1]: mysql.service: Failed with result 'exit-code'
```

### 3. Security Logs
```
# Access logs
192.168.1.100 - - [15/Jan/2024:10:23:45 +0000] "GET /api/users HTTP/1.1" 200 1234
192.168.1.200 - - [15/Jan/2024:10:23:46 +0000] "POST /admin/login HTTP/1.1" 401 0
```

---

## Log Parsing and Structuring

### Using Regular Expressions
```python
import re
from datetime import datetime

def parse_log_line(log_line):
    """Parse common log format"""
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+) \[(\w+)\] (.+)'
    
    match = re.match(pattern, log_line)
    if match:
        return {
            'timestamp': datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S'),
            'level': match.group(2),
            'service': match.group(3),
            'message': match.group(4)
        }
    return None

# Example usage
log = "2024-01-15 10:23:45 ERROR [PaymentService] Payment failed: timeout"
parsed = parse_log_line(log)
print(parsed)
# Output: {
#   'timestamp': datetime(2024, 1, 15, 10, 23, 45),
#   'level': 'ERROR',
#   'service': 'PaymentService',
#   'message': 'Payment failed: timeout'
# }
```

### Using Grok Patterns (Logstash)
```ruby
# Grok pattern for application logs
filter {
  grok {
    match => {
      "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} \[%{WORD:service}\] %{GREEDYDATA:message}"
    }
  }
  
  date {
    match => [ "timestamp", "yyyy-MM-dd HH:mm:ss" ]
  }
}
```

---

## Pattern Recognition in Logs

### 1. Error Pattern Detection
```python
from collections import Counter
import pandas as pd

def detect_error_patterns(logs_df, window='1H'):
    """Detect recurring error patterns"""
    
    # Filter error logs
    errors = logs_df[logs_df['level'] == 'ERROR']
    
    # Group by time window
    errors['time_bucket'] = errors['timestamp'].dt.floor(window)
    
    # Extract error signature
    errors['error_signature'] = errors['message'].apply(extract_error_signature)
    
    # Count patterns
    pattern_counts = errors.groupby(['time_bucket', 'error_signature']).size()
    
    # Identify spikes
    avg_count = pattern_counts.mean()
    std_count = pattern_counts.std()
    
    spikes = pattern_counts[pattern_counts > avg_count + 2*std_count]
    
    return spikes

def extract_error_signature(message):
    """Extract error signature by removing variable parts"""
    import re
    
    # Replace numbers with placeholder
    signature = re.sub(r'\d+', 'N', message)
    
    # Replace UUIDs
    signature = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 
                      'UUID', signature, flags=re.IGNORECASE)
    
    # Replace IP addresses
    signature = re.sub(r'\d+\.\d+\.\d+\.\d+', 'IP', signature)
    
    return signature

# Example usage
logs_df = pd.DataFrame({
    'timestamp': pd.date_range('2024-01-15', periods=100, freq='1min'),
    'level': ['ERROR']*100,
    'message': [
        'Database connection timeout to 192.168.1.100:5432',
        'Database connection timeout to 192.168.1.101:5432',
        'Payment failed for transaction tx_12345',
        # ... more logs
    ]
})

error_patterns = detect_error_patterns(logs_df)
print("Error spikes detected:")
print(error_patterns)
```

### 2. Log Template Mining
```python
from drain3 import TemplateMiner

class LogTemplateMiner:
    """Mine log templates using Drain algorithm"""
    
    def __init__(self):
        self.template_miner = TemplateMiner()
    
    def add_log(self, log_message):
        """Process and add log message"""
        result = self.template_miner.add_log_message(log_message)
        return result
    
    def get_templates(self):
        """Get discovered templates"""
        templates = []
        for cluster in self.template_miner.drain.clusters:
            templates.append({
                'template': ' '.join(cluster.log_template_tokens),
                'count': cluster.size
            })
        return templates

# Usage
miner = LogTemplateMiner()

logs = [
    "User 123 logged in from IP 192.168.1.1",
    "User 456 logged in from IP 192.168.1.2",
    "Failed login attempt for user 789",
    "Failed login attempt for user 101",
    "Database query took 5.2 seconds",
    "Database query took 3.8 seconds"
]

for log in logs:
    miner.add_log(log)

templates = miner.get_templates()
print("Discovered templates:")
for t in templates:
    print(f"Template: {t['template']}, Count: {t['count']}")

# Output:
# Template: User <*> logged in from IP <*>, Count: 2
# Template: Failed login attempt for user <*>, Count: 2
# Template: Database query took <*> seconds, Count: 2
```

---

## Log Clustering and Analysis

### K-Means Clustering on Log Features
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

def cluster_logs(log_messages, n_clusters=5):
    """Cluster similar log messages"""
    
    # Convert logs to TF-IDF features
    vectorizer = TfidfVectorizer(
        max_features=100,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    features = vectorizer.fit_transform(log_messages)
    
    # Cluster logs
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(features)
    
    # Get representative logs for each cluster
    cluster_centers = kmeans.cluster_centers_
    
    results = []
    for i in range(n_clusters):
        cluster_logs = [log for j, log in enumerate(log_messages) if clusters[j] == i]
        
        # Find log closest to center
        cluster_indices = np.where(clusters == i)[0]
        if len(cluster_indices) > 0:
            distances = kmeans.transform(features[cluster_indices])[:, i]
            representative_idx = cluster_indices[distances.argmin()]
            representative = log_messages[representative_idx]
        else:
            representative = ""
        
        results.append({
            'cluster_id': i,
            'size': len(cluster_logs),
            'representative': representative,
            'samples': cluster_logs[:3]  # First 3 samples
        })
    
    return results

# Example
logs = [
    "Database connection timeout",
    "Database query slow",
    "DB connection failed",
    "User authentication failed",
    "Login attempt failed",
    "Invalid credentials",
    "Memory usage high",
    "CPU utilization exceeded",
    "Disk space low"
]

clusters = cluster_logs(logs, n_clusters=3)
for cluster in clusters:
    print(f"\nCluster {cluster['cluster_id']} ({cluster['size']} logs)")
    print(f"Representative: {cluster['representative']}")
    print(f"Samples: {cluster['samples']}")
```

---

## Anomaly Detection in Logs

### Log Volume Anomalies
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def detect_log_volume_anomalies(logs_df, window='5min'):
    """Detect unusual log volume patterns"""
    
    # Count logs per time window
    log_counts = logs_df.set_index('timestamp').resample(window).size()
    
    # Create features
    log_counts_df = pd.DataFrame({
        'count': log_counts,
        'hour': log_counts.index.hour,
        'day_of_week': log_counts.index.dayofweek
    })
    
    # Train Isolation Forest
    iso_forest = IsolationForest(contamination=0.1, random_state=42)
    log_counts_df['anomaly'] = iso_forest.fit_predict(log_counts_df[['count', 'hour', 'day_of_week']])
    
    # Get anomalies
    anomalies = log_counts_df[log_counts_df['anomaly'] == -1]
    
    return anomalies

# Usage
logs_df = pd.DataFrame({
    'timestamp': pd.date_range('2024-01-15', periods=1000, freq='1min'),
    'message': ['log message'] * 1000
})

anomalies = detect_log_volume_anomalies(logs_df)
print(f"Found {len(anomalies)} anomalous time windows")
```

### Rare Event Detection
```python
def detect_rare_events(logs_df, threshold_percentile=95):
    """Detect rarely occurring log patterns"""
    
    # Extract log signatures
    logs_df['signature'] = logs_df['message'].apply(extract_error_signature)
    
    # Count occurrences
    signature_counts = logs_df['signature'].value_counts()
    
    # Calculate threshold
    threshold = np.percentile(signature_counts.values, threshold_percentile)
    
    # Find rare events
    rare_signatures = signature_counts[signature_counts >= threshold]
    
    rare_events = logs_df[logs_df['signature'].isin(rare_signatures.index)]
    
    return rare_events, rare_signatures

# Usage
rare_events, rare_sigs = detect_rare_events(logs_df)
print(f"Rare signatures:\n{rare_sigs}")
```

---

## Log Correlation Across Services

### Time-based Correlation
```python
def correlate_logs_across_services(logs_dict, time_window='1s'):
    """
    Correlate logs from multiple services within time window
    
    logs_dict: {'service_name': DataFrame with 'timestamp' and 'message'}
    """
    
    all_logs = []
    
    # Combine logs from all services
    for service, df in logs_dict.items():
        df = df.copy()
        df['service'] = service
        all_logs.append(df)
    
    combined = pd.concat(all_logs, ignore_index=True)
    combined = combined.sort_values('timestamp')
    
    # Create time buckets
    combined['time_bucket'] = combined['timestamp'].dt.floor(time_window)
    
    # Group by time bucket
    correlations = []
    for bucket, group in combined.groupby('time_bucket'):
        if len(group) > 1:
            services_involved = group['service'].unique()
            correlations.append({
                'timestamp': bucket,
                'services': list(services_involved),
                'log_count': len(group),
                'messages': group['message'].tolist()
            })
    
    return pd.DataFrame(correlations)

# Example
logs_dict = {
    'web-server': pd.DataFrame({
        'timestamp': pd.to_datetime(['2024-01-15 10:00:00', '2024-01-15 10:00:00.5']),
        'message': ['Request received', 'Response sent']
    }),
    'app-server': pd.DataFrame({
        'timestamp': pd.to_datetime(['2024-01-15 10:00:00.2', '2024-01-15 10:00:00.4']),
        'message': ['Processing request', 'Query database']
    }),
    'database': pd.DataFrame({
        'timestamp': pd.to_datetime(['2024-01-15 10:00:00.3']),
        'message': ['Query executed']
    })
}

correlations = correlate_logs_across_services(logs_dict, time_window='1s')
print(correlations)
```

---

## Automated Log Analysis Pipeline

### Complete Pipeline
```python
import logging
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta

class LogAnalysisPipeline:
    """Automated log analysis pipeline"""
    
    def __init__(self, es_host='localhost:9200'):
        self.es = Elasticsearch([es_host])
        self.template_miner = LogTemplateMiner()
        
    def collect_logs(self, index, time_range='1h'):
        """Collect logs from Elasticsearch"""
        query = {
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": f"now-{time_range}",
                        "lte": "now"
                    }
                }
            }
        }
        
        result = self.es.search(index=index, body=query, size=10000)
        
        logs = []
        for hit in result['hits']['hits']:
            logs.append(hit['_source'])
        
        return pd.DataFrame(logs)
    
    def analyze_logs(self, logs_df):
        """Perform comprehensive log analysis"""
        
        results = {
            'timestamp': datetime.now(),
            'total_logs': len(logs_df),
            'error_count': 0,
            'warning_count': 0,
            'anomalies': [],
            'patterns': [],
            'rare_events': []
        }
        
        # Count by level
        if 'level' in logs_df.columns:
            results['error_count'] = len(logs_df[logs_df['level'] == 'ERROR'])
            results['warning_count'] = len(logs_df[logs_df['level'] == 'WARN'])
        
        # Detect anomalies
        anomalies = detect_log_volume_anomalies(logs_df)
        results['anomalies'] = anomalies.to_dict('records')
        
        # Mine patterns
        for message in logs_df['message'].head(1000):  # Sample for performance
            self.template_miner.add_log(message)
        
        results['patterns'] = self.template_miner.get_templates()
        
        # Detect rare events
        rare_events, _ = detect_rare_events(logs_df)
        results['rare_events'] = rare_events.head(10).to_dict('records')
        
        return results
    
    def generate_alert(self, analysis_results):
        """Generate alerts based on analysis"""
        
        alerts = []
        
        # Error threshold
        if analysis_results['error_count'] > 100:
            alerts.append({
                'severity': 'HIGH',
                'message': f"High error rate detected: {analysis_results['error_count']} errors"
            })
        
        # Anomaly detection
        if len(analysis_results['anomalies']) > 0:
            alerts.append({
                'severity': 'MEDIUM',
                'message': f"Detected {len(analysis_results['anomalies'])} anomalous time windows"
            })
        
        return alerts
    
    def run(self, index='logs-*'):
        """Run complete pipeline"""
        
        # Collect logs
        logs_df = self.collect_logs(index)
        
        # Analyze
        results = self.analyze_logs(logs_df)
        
        # Generate alerts
        alerts = self.generate_alert(results)
        
        # Log results
        logging.info(f"Analyzed {results['total_logs']} logs")
        logging.info(f"Found {results['error_count']} errors, {results['warning_count']} warnings")
        
        for alert in alerts:
            logging.warning(f"{alert['severity']}: {alert['message']}")
        
        return results, alerts

# Usage
pipeline = LogAnalysisPipeline()
results, alerts = pipeline.run(index='app-logs-*')
```

---

## Visualization and Reporting

### Generate Log Analysis Report
```python
import matplotlib.pyplot as plt
import seaborn as sns

def generate_log_report(logs_df, output_file='log_report.html'):
    """Generate visual log analysis report"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. Log volume over time
    log_volume = logs_df.set_index('timestamp').resample('5min').size()
    axes[0, 0].plot(log_volume.index, log_volume.values)
    axes[0, 0].set_title('Log Volume Over Time')
    axes[0, 0].set_xlabel('Time')
    axes[0, 0].set_ylabel('Log Count')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # 2. Log level distribution
    level_counts = logs_df['level'].value_counts()
    axes[0, 1].bar(level_counts.index, level_counts.values)
    axes[0, 1].set_title('Log Level Distribution')
    axes[0, 1].set_xlabel('Level')
    axes[0, 1].set_ylabel('Count')
    
    # 3. Top services by log volume
    if 'service' in logs_df.columns:
        service_counts = logs_df['service'].value_counts().head(10)
        axes[1, 0].barh(service_counts.index, service_counts.values)
        axes[1, 0].set_title('Top 10 Services by Log Volume')
        axes[1, 0].set_xlabel('Log Count')
    
    # 4. Error rate over time
    error_logs = logs_df[logs_df['level'] == 'ERROR']
    error_rate = error_logs.set_index('timestamp').resample('5min').size()
    axes[1, 1].plot(error_rate.index, error_rate.values, color='red')
    axes[1, 1].set_title('Error Rate Over Time')
    axes[1, 1].set_xlabel('Time')
    axes[1, 1].set_ylabel('Error Count')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('log_analysis.png')
    
    # Generate HTML report
    html = f"""
    <html>
    <head><title>Log Analysis Report</title></head>
    <body>
        <h1>Log Analysis Report</h1>
        <p>Generated: {datetime.now()}</p>
        <p>Total Logs: {len(logs_df)}</p>
        <p>Time Range: {logs_df['timestamp'].min()} to {logs_df['timestamp'].max()}</p>
        <img src="log_analysis.png" />
    </body>
    </html>
    """
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"Report generated: {output_file}")
```

---

## Best Practices

1. **Structured Logging**: Use JSON format for easy parsing
2. **Consistent Format**: Standardize log formats across services
3. **Correlation IDs**: Add request IDs for tracing
4. **Contextual Information**: Include relevant metadata
5. **Log Sampling**: Sample high-volume logs for analysis
6. **Retention Policies**: Balance storage cost vs analysis needs
7. **Real-time Processing**: Stream logs for immediate analysis
8. **Privacy**: Mask sensitive information (PII, credentials)

---

## Summary

Log analysis is crucial for AIOps:
- Parse and structure logs for analysis
- Use ML for pattern recognition
- Detect anomalies in log volume and content
- Correlate logs across services
- Build automated pipelines
- Generate actionable insights

---

**Next**: [Root Cause Analysis →](08-root-cause-analysis.md)
