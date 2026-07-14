# AIOps Interview Questions - Basics Level

Comprehensive interview questions covering AIOps fundamentals, use cases, data collection, observability, and first implementations.

---

## What is AIOps?

### Q1: What is AIOps and why is it needed?

**Answer:**

**AIOps** (Artificial Intelligence for IT Operations) is the application of machine learning and data science techniques to IT operations data to automate and enhance IT operations processes.

**Why it's needed:**
1. **Alert Fatigue**: Modern systems generate thousands of alerts daily
2. **Complexity**: Distributed systems are too complex for manual monitoring
3. **Speed**: Human response time can't match system scale
4. **Predictability**: Need to predict failures before they occur
5. **Cost**: Reduce operational costs through automation

**Traditional Monitoring vs AIOps:**
- Traditional: Manual analysis, reactive, threshold-based
- AIOps: AI-driven, proactive, pattern-based

---

### Q2: Explain the key components of an AIOps platform.

**Answer:**

```
Data Sources → Ingestion → Processing → AI/ML → Actions
```

**1. Data Ingestion Layer:**
- Collect logs, metrics, traces, events
- Multiple sources (APM, logs, infrastructure)

**2. Data Processing Layer:**
- Normalization and enrichment
- Correlation and aggregation

**3. AI/ML Analysis Layer:**
- Anomaly detection
- Pattern recognition
- Root cause analysis
- Predictive analytics

**4. Insights & Actions Layer:**
- Dashboards and visualizations
- Alert generation
- Automated remediation

**5. Feedback Loop:**
- Continuous learning
- Model improvement
- Human-in-the-loop validation

---

### Q3: What are the main use cases for AIOps?

**Answer:**

**1. Anomaly Detection**
- Automatically detect unusual patterns in metrics
- Example: CPU spike detection before capacity issues

**2. Alert Correlation**
- Group related alerts into incidents
- Reduce alert noise by 80-90%

**3. Root Cause Analysis**
- Automatically identify failure causes
- Reduce MTTR from hours to minutes

**4. Predictive Analytics**
- Forecast capacity needs
- Predict failures before they occur

**5. Automated Remediation**
- Auto-restart failed services
- Scale resources automatically

**6. Performance Optimization**
- Identify bottlenecks
- Optimize resource allocation

---

## Data Collection & Integration

### Q4: What types of data does AIOps collect and why?

**Answer:**

**1. Time Series Metrics:**
```python
{
  "timestamp": "2024-01-15T10:00:00Z",
  "metric": "cpu.usage",
  "value": 75.5,
  "host": "server-01"
}
```
- **Why**: Track system health and performance over time

**2. Log Data:**
```json
{
  "timestamp": "2024-01-15T10:00:00Z",
  "level": "ERROR",
  "service": "payment-service",
  "message": "Payment failed: timeout"
}
```
- **Why**: Understand what happened and why

**3. Trace Data:**
```json
{
  "trace_id": "abc-123",
  "spans": [
    {"operation": "api_request", "duration_ms": 250}
  ]
}
```
- **Why**: Track request flow through distributed systems

**4. Event Data:**
```json
{
  "type": "deployment",
  "service": "api-gateway",
  "version": "v2.1.0"
}
```
- **Why**: Correlate changes with incidents

**5. Topology Data:**
- Service dependencies
- Network relationships
- **Why**: Understand system architecture for RCA

---

### Q5: Explain push-based vs pull-based data collection.

**Answer:**

**Pull-Based (Prometheus Model):**
```yaml
# Prometheus scrapes metrics
scrape_configs:
  - job_name: 'my-app'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8080']
```

**Advantages:**
- Central control of what to scrape
- Service discovery
- Better for batch processing

**Disadvantages:**
- Network overhead
- Firewall issues

**Push-Based (StatsD Model):**
```python
# Application pushes metrics
statsd.incr('api.requests')
statsd.timing('api.response_time', 250)
```

**Advantages:**
- No firewall issues
- Real-time data
- Application controls what to send

**Disadvantages:**
- Applications need modification
- Network reliability concerns

**Best Practice**: Use both depending on the use case.

---

### Q6: How do you handle high-volume data in AIOps?

**Answer:**

**1. Sampling:**
```python
# Smart sampling
def should_sample(data):
    # Always sample errors
    if data['level'] == 'ERROR':
        return True
    
    # Always sample anomalies
    if is_anomaly(data):
        return True
    
    # Sample 10% of normal traffic
    return random.random() < 0.1
```

**2. Batching:**
```python
# Batch data for efficient processing
batcher = DataBatcher(batch_size=1000, flush_interval=5)

for data in stream:
    batcher.add(data)
    # Auto-flushes when full or timeout
```

**3. Aggregation:**
- Pre-aggregate metrics at source
- Use rollups for historical data

**4. Data Tiering:**
- Hot: Recent data (high resolution)
- Warm: Last 30 days (medium resolution)
- Cold: Historical (aggregated)

---

## Observability Fundamentals

### Q7: What's the difference between monitoring and observability?

**Answer:**

| Aspect | Monitoring | Observability |
|--------|-----------|---------------|
| **Focus** | Known issues | Unknown issues |
| **Questions** | "Is it working?" | "Why is it broken?" |
| **Approach** | Dashboards, alerts | Exploration, investigation |
| **Data** | Aggregated metrics | High-cardinality, raw data |
| **Proactive** | Reactive | Proactive |

**Example:**

**Monitoring Question:**
- "Is CPU usage > 80%?" → Alert

**Observability Question:**
- "Why is this specific user's request slow?"
- Need to: Check traces → Correlate logs → Check metrics

**Key Insight**: Monitoring tells you **what** is broken. Observability helps you understand **why**.

---

### Q8: Explain the three pillars of observability.

**Answer:**

**1. Metrics (What is happening?)**
- Time-series numerical data
- Examples: CPU usage, request rate, error rate

```python
# Expose metrics
request_count.labels(method='GET', endpoint='/api').inc()
request_duration.observe(0.250)
```

**2. Logs (What happened?)**
- Discrete events with context
- Examples: Error messages, audit logs

```python
logger.info("Payment processed", extra={
    'user_id': 'user-123',
    'amount': 99.99,
    'trace_id': 'abc-123'
})
```

**3. Traces (How did it happen?)**
- Request journey through services
- Shows service dependencies

```python
@tracer.start_as_current_span("process_payment")
def process_payment(amount):
    # Automatically tracked
    return gateway.charge(amount)
```

**Correlation**: Link all three using trace_id:
```
Trace ID: abc-123
  ↓
Metrics with trace_id context
  ↓
Logs with trace_id field
  ↓
Complete story of the request
```

---

### Q9: How do you implement distributed tracing?

**Answer:**

**Using OpenTelemetry:**

**1. Setup:**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.jaeger import JaegerExporter

# Configure tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Setup exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831
)
```

**2. Instrument Code:**
```python
@tracer.start_as_current_span("process_order")
def process_order(order_id):
    span = trace.get_current_span()
    span.set_attribute("order.id", order_id)
    
    # Call payment service
    with tracer.start_as_current_span("charge_payment"):
        payment = charge_customer(order_id)
    
    # Call inventory service
    with tracer.start_as_current_span("update_inventory"):
        inventory.decrement(order_id)
    
    return result
```

**3. Context Propagation:**
```python
# Propagate trace context to downstream services
headers = {}
inject(headers)  # Adds trace context to headers

response = requests.post(
    'http://downstream-service/api',
    json=data,
    headers=headers  # Trace continues
)
```

**Benefits:**
- See request flow across services
- Identify bottlenecks
- Understand dependencies

---

### Q10: What are the key metrics for observability (RED/USE methods)?

**Answer:**

**RED Method (for requests/services):**

**R - Rate:**
```python
request_rate = rate(http_requests_total[1m])
```
- Requests per second

**E - Errors:**
```python
error_rate = rate(http_requests_total{status="500"}[1m])
```
- Failed requests per second

**D - Duration:**
```python
p95_latency = histogram_quantile(0.95, http_duration_bucket)
```
- Response time (P50, P95, P99)

**USE Method (for resources):**

**U - Utilization:**
```python
cpu_utilization = 100 - idle_cpu_percentage
```
- Percentage of time resource is busy

**S - Saturation:**
```python
queue_length = avg(queue_size)
```
- Amount of work resource can't process

**E - Errors:**
```python
disk_errors = rate(disk_error_count[1m])
```
- Error count

**Four Golden Signals (Google SRE):**
1. Latency (request duration)
2. Traffic (request rate)
3. Errors (error rate)
4. Saturation (resource usage)

---

## First AIOps Implementation

### Q11: How would you build a simple anomaly detection system?

**Answer:**

**Step-by-step implementation:**

**1. Collect Data:**
```python
from prometheus_api_client import PrometheusConnect

prom = PrometheusConnect(url='http://localhost:9090')

# Get CPU metrics
metric_data = prom.get_metric_range_data(
    metric_name='cpu_usage',
    start_time=start,
    end_time=end
)
```

**2. Engineer Features:**
```python
def engineer_features(df):
    # Time-based features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    
    # Rolling statistics
    df['rolling_mean'] = df['value'].rolling(window=10).mean()
    df['rolling_std'] = df['value'].rolling(window=10).std()
    
    # Rate of change
    df['rate_of_change'] = df['value'].diff()
    
    return df
```

**3. Train Model:**
```python
from sklearn.ensemble import IsolationForest

# Prepare features
features = ['value', 'hour', 'rolling_mean', 'rolling_std']
X = df[features].values

# Train Isolation Forest
model = IsolationForest(contamination=0.1)
model.fit(X)
```

**4. Detect Anomalies:**
```python
# Predict on new data
predictions = model.predict(new_data)
anomalies = new_data[predictions == -1]

if not anomalies.empty:
    alert("Anomaly detected!", anomalies)
```

**5. Alert:**
```python
def alert(message, data):
    # Send to Slack
    requests.post(webhook_url, json={
        'text': f"⚠️ {message}",
        'value': data['value'].iloc[0],
        'timestamp': data['timestamp'].iloc[0]
    })
```

---

### Q12: What ML algorithms are commonly used in AIOps?

**Answer:**

**1. Anomaly Detection:**

**Isolation Forest:**
```python
from sklearn.ensemble import IsolationForest

model = IsolationForest(contamination=0.1)
model.fit(historical_data)
anomalies = model.predict(new_data)
```
- **Use**: Detect unusual patterns in metrics
- **Pro**: Works well with high-dimensional data
- **Con**: Needs sufficient training data

**One-Class SVM:**
```python
from sklearn.svm import OneClassSVM

model = OneClassSVM(nu=0.1)
model.fit(normal_data)
```
- **Use**: When you have only normal data
- **Pro**: Good for small datasets
- **Con**: Computationally expensive

**2. Forecasting:**

**ARIMA:**
```python
from statsmodels.tsa.arima.model import ARIMA

model = ARIMA(data, order=(1,1,1))
forecast = model.fit().forecast(steps=24)
```
- **Use**: Time series prediction
- **Pro**: Statistical foundation
- **Con**: Assumes stationarity

**Prophet:**
```python
from prophet import Prophet

model = Prophet()
model.fit(df)
forecast = model.predict(future)
```
- **Use**: Capacity planning, trend analysis
- **Pro**: Handles seasonality well
- **Con**: Needs sufficient historical data

**3. Clustering:**

**K-Means:**
```python
from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=5)
clusters = kmeans.fit_predict(log_features)
```
- **Use**: Group similar logs/incidents
- **Pro**: Simple and fast
- **Con**: Need to know cluster count

**4. Classification:**

**Random Forest:**
```python
from sklearn.ensemble import RandomForestClassifier

clf = RandomForestClassifier()
clf.fit(X_train, y_train)
incident_type = clf.predict(new_incident)
```
- **Use**: Classify incident types
- **Pro**: Handles non-linear data
- **Con**: Can overfit

---

### Q13: How do you evaluate an AIOps system's performance?

**Answer:**

**1. Operational Metrics:**

```yaml
MTTD (Mean Time To Detect):
  target: < 5 minutes
  current: 3 minutes
  
MTTR (Mean Time To Resolve):
  target: < 30 minutes
  current: 25 minutes

Alert Noise Reduction:
  before: 10,000 alerts/day
  after: 500 alerts/day
  reduction: 95%

False Positive Rate:
  target: < 5%
  current: 3%

Incident Prevention:
  incidents_prevented: 45/month
  potential_downtime_saved: 120 hours
```

**2. ML Model Metrics:**

```python
from sklearn.metrics import precision_recall_fscore_support

# For anomaly detection
precision, recall, f1, _ = precision_recall_fscore_support(
    y_true, y_pred, average='binary'
)

print(f"Precision: {precision:.2f}")  # How many alerts are real?
print(f"Recall: {recall:.2f}")        # How many real issues detected?
print(f"F1 Score: {f1:.2f}")          # Balanced metric
```

**3. Business Metrics:**

```yaml
Cost Savings:
  manual_hours_saved: 200 hours/month
  cost_per_hour: $100
  monthly_savings: $20,000

Availability Improvement:
  before: 99.5%
  after: 99.95%
  additional_uptime: 0.45%

Customer Satisfaction:
  before: 3.5/5
  after: 4.5/5
```

**4. ROI Calculation:**

```python
# Annual ROI
investment = 100000  # Platform cost
savings = {
    'reduced_downtime': 500000,
    'automation': 200000,
    'faster_resolution': 150000
}

total_savings = sum(savings.values())
roi = (total_savings - investment) / investment * 100

print(f"ROI: {roi}%")  # 750%
```

---

## Best Practices

### Q14: What are the key best practices for implementing AIOps?

**Answer:**

**1. Start Small:**
- Begin with one use case (e.g., anomaly detection)
- Prove value before expanding
- Example: Start with CPU anomaly detection on 10 servers

**2. Ensure Data Quality:**
```python
def validate_data(metrics):
    # Check for missing values
    if metrics.isnull().sum() > len(metrics) * 0.1:
        alert("High missing data rate")
    
    # Check for staleness
    latest = metrics['timestamp'].max()
    if (datetime.now() - latest).seconds > 300:
        alert("Stale data")
    
    # Check for outliers
    outliers = detect_outliers(metrics['value'])
    if len(outliers) > 0:
        log("Outliers detected", outliers)
```

**3. Implement Feedback Loops:**
```python
class FeedbackLoop:
    def collect_feedback(self, alert_id, was_real):
        """Learn from human feedback"""
        self.feedback_db.insert({
            'alert_id': alert_id,
            'was_real': was_real,
            'timestamp': datetime.now()
        })
    
    def retrain_model(self):
        """Retrain with feedback"""
        feedback = self.feedback_db.get_recent(days=30)
        
        # Adjust contamination based on false positive rate
        fp_rate = sum(not f['was_real'] for f in feedback) / len(feedback)
        
        if fp_rate > 0.1:
            self.model.contamination *= 0.9  # Reduce sensitivity
        
        self.model.fit(new_training_data)
```

**4. Maintain Human-in-the-Loop:**
- Don't automate everything immediately
- Let humans validate critical actions
- Build trust gradually

**5. Monitor the Monitor:**
```python
def check_aiops_health():
    """Monitor AIOps system itself"""
    checks = {
        'data_freshness': check_data_freshness(),
        'model_accuracy': check_model_accuracy(),
        'alert_rate': check_alert_rate(),
        'processing_latency': check_latency()
    }
    
    if any(not v for v in checks.values()):
        alert("AIOps system degraded", checks)
```

**6. Document and Share:**
- Document what works and what doesn't
- Share findings with team
- Create runbooks for common scenarios

---

### Q15: What challenges might you face when implementing AIOps?

**Answer:**

**1. Data Quality Issues:**
```python
# Challenge: Missing or inconsistent data
# Solution: Data validation and imputation

def handle_missing_data(df):
    # Forward fill for short gaps
    df = df.fillna(method='ffill', limit=3)
    
    # Interpolate for longer gaps
    df = df.interpolate(method='linear')
    
    # Drop if still missing
    df = df.dropna()
    
    return df
```

**2. Alert Fatigue:**
```python
# Challenge: Too many alerts
# Solution: Alert grouping and suppression

class AlertManager:
    def should_alert(self, anomaly):
        # Suppress duplicates
        if self.is_duplicate(anomaly):
            return False
        
        # Group related alerts
        if self.can_group(anomaly):
            self.add_to_group(anomaly)
            return False
        
        # Rate limit
        if self.alert_count_today() > 50:
            return False
        
        return True
```

**3. Model Drift:**
```python
# Challenge: Models become less accurate over time
# Solution: Continuous monitoring and retraining

def monitor_model_performance():
    recent_accuracy = calculate_accuracy(last_30_days)
    baseline_accuracy = 0.95
    
    if recent_accuracy < baseline_accuracy * 0.9:
        alert("Model drift detected")
        trigger_retraining()
```

**4. Integration Complexity:**
- Multiple data sources
- Different formats
- Legacy systems

**Solution**: Use standard protocols (OpenTelemetry, Prometheus)

**5. Organizational Resistance:**
- "We've always done it this way"
- Fear of automation
- Lack of ML expertise

**Solution**: 
- Start with quick wins
- Provide training
- Show clear ROI

---

## Summary

Key takeaways for AIOps basics:
- AIOps applies ML to IT operations data
- Collect metrics, logs, traces, and events
- Observability is more than monitoring
- Start with simple anomaly detection
- Measure success with MTTD, MTTR, false positives
- Implement feedback loops
- Monitor the monitor

---

**Next Level**: [Intermediate Interview Questions →](../02-intermediate/interview-questions-intermediate.md)
