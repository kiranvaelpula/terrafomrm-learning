# Data Collection & Integration

## Learning Objectives
- Understand data sources for AIOps
- Implement data collection strategies
- Integrate multiple monitoring tools
- Build data ingestion pipelines

---

## Why Data Collection Matters in AIOps

AIOps relies on comprehensive data from across your IT infrastructure:
- **Logs**: Application and system logs
- **Metrics**: Performance metrics (CPU, memory, latency)
- **Traces**: Distributed tracing data
- **Events**: Alerts, deployments, incidents
- **Topology**: Service dependencies and relationships

---

## Types of Data for AIOps

### 1. Time Series Metrics
```python
# Example: CPU usage metrics
{
  "timestamp": "2024-01-15T10:00:00Z",
  "metric": "cpu.usage",
  "value": 75.5,
  "host": "server-01",
  "tags": {
    "environment": "production",
    "region": "us-east-1"
  }
}
```

### 2. Log Data
```json
{
  "timestamp": "2024-01-15T10:00:00Z",
  "level": "ERROR",
  "service": "payment-service",
  "message": "Payment processing failed: timeout",
  "trace_id": "abc-123-def-456"
}
```

### 3. Trace Data
```json
{
  "trace_id": "abc-123-def-456",
  "span_id": "span-001",
  "operation": "process_payment",
  "duration_ms": 250,
  "tags": {
    "http.method": "POST",
    "http.status_code": 500
  }
}
```

### 4. Events
```json
{
  "timestamp": "2024-01-15T10:00:00Z",
  "type": "deployment",
  "service": "api-gateway",
  "version": "v2.1.0",
  "status": "completed"
}
```

---

## Data Sources

### Infrastructure Monitoring
- **Prometheus**: Metrics collection
- **Nagios/Icinga**: Infrastructure monitoring
- **CloudWatch**: AWS monitoring
- **Azure Monitor**: Azure monitoring
- **Google Cloud Monitoring**: GCP monitoring

### Application Performance Monitoring (APM)
- **Datadog**: Full-stack observability
- **New Relic**: Application monitoring
- **Dynatrace**: AI-powered monitoring
- **AppDynamics**: Business monitoring

### Log Management
- **Elasticsearch (ELK)**: Log aggregation
- **Splunk**: Log analytics
- **Loki**: Log aggregation
- **Fluentd**: Log forwarding

### Tracing
- **Jaeger**: Distributed tracing
- **Zipkin**: Tracing system
- **AWS X-Ray**: Application tracing
- **OpenTelemetry**: Unified observability

---

## Data Collection Methods

### 1. Pull-Based Collection (Prometheus)

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'application'
    static_configs:
      - targets: ['localhost:8080']
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

```python
# Example: Expose metrics for Prometheus
from prometheus_client import start_http_server, Counter, Gauge
import time

# Define metrics
requests_total = Counter('http_requests_total', 'Total HTTP requests')
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage')

# Expose metrics
start_http_server(8000)

# Update metrics
while True:
    requests_total.inc()
    cpu_usage.set(get_cpu_usage())
    time.sleep(1)
```

### 2. Push-Based Collection (StatsD)

```python
# Example: Push metrics to StatsD
from statsd import StatsClient

statsd = StatsClient('localhost', 8125)

# Send metrics
statsd.incr('api.requests')
statsd.timing('api.response_time', 250)
statsd.gauge('cpu.usage', 75.5)
```

### 3. Log Collection with Fluentd

```xml
<!-- fluentd.conf -->
<source>
  @type tail
  path /var/log/app/*.log
  pos_file /var/log/td-agent/app.log.pos
  tag app.logs
  <parse>
    @type json
    time_key timestamp
    time_format %Y-%m-%dT%H:%M:%S.%NZ
  </parse>
</source>

<match app.logs>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name app-logs
  type_name _doc
</match>
```

### 4. Trace Collection with OpenTelemetry

```python
# Example: Instrument application with OpenTelemetry
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Instrument code
@tracer.start_as_current_span("process_payment")
def process_payment(amount):
    span = trace.get_current_span()
    span.set_attribute("payment.amount", amount)
    
    # Your code here
    result = charge_card(amount)
    
    span.set_attribute("payment.status", result.status)
    return result
```

---

## Building a Data Ingestion Pipeline

### Complete Pipeline Architecture
```
Data Sources → Collection Agents → Message Queue → Processing → Storage → AIOps
```

### Implementation Example

```python
# data_ingestion_pipeline.py
from kafka import KafkaProducer, KafkaConsumer
from elasticsearch import Elasticsearch
import json
from datetime import datetime

class DataIngestionPipeline:
    """Complete data ingestion pipeline for AIOps"""
    
    def __init__(self):
        # Kafka producer for data ingestion
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Elasticsearch for storage
        self.es = Elasticsearch(['http://localhost:9200'])
    
    def collect_metrics(self, source, metrics):
        """Collect and send metrics to Kafka"""
        data = {
            'type': 'metric',
            'source': source,
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': metrics
        }
        
        self.producer.send('metrics-topic', value=data)
        print(f"Sent metrics from {source}")
    
    def collect_logs(self, source, log_entry):
        """Collect and send logs to Kafka"""
        data = {
            'type': 'log',
            'source': source,
            'timestamp': datetime.utcnow().isoformat(),
            'log': log_entry
        }
        
        self.producer.send('logs-topic', value=data)
        print(f"Sent log from {source}")
    
    def collect_traces(self, trace_data):
        """Collect and send traces to Kafka"""
        data = {
            'type': 'trace',
            'timestamp': datetime.utcnow().isoformat(),
            'trace': trace_data
        }
        
        self.producer.send('traces-topic', value=data)
        print(f"Sent trace {trace_data.get('trace_id')}")
    
    def process_and_store(self):
        """Process data from Kafka and store in Elasticsearch"""
        consumer = KafkaConsumer(
            'metrics-topic',
            'logs-topic',
            'traces-topic',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        for message in consumer:
            data = message.value
            data_type = data.get('type')
            
            # Store in appropriate Elasticsearch index
            index_name = f"{data_type}s-{datetime.now():%Y.%m.%d}"
            
            self.es.index(
                index=index_name,
                document=data
            )
            
            print(f"Stored {data_type} in {index_name}")

# Usage
pipeline = DataIngestionPipeline()

# Collect metrics
pipeline.collect_metrics('server-01', {
    'cpu_usage': 75.5,
    'memory_usage': 60.2,
    'disk_io': 1024
})

# Collect logs
pipeline.collect_logs('app-service', {
    'level': 'ERROR',
    'message': 'Connection timeout',
    'trace_id': 'abc-123'
})

# Collect traces
pipeline.collect_traces({
    'trace_id': 'abc-123',
    'spans': [
        {'span_id': '1', 'operation': 'http_request', 'duration_ms': 250}
    ]
})
```

---

## Data Enrichment

### Adding Context to Data
```python
def enrich_log_data(log_entry):
    """Enrich log data with additional context"""
    
    # Add environment info
    log_entry['environment'] = get_environment()
    
    # Add service topology
    log_entry['dependencies'] = get_service_dependencies(log_entry['service'])
    
    # Add metadata
    log_entry['region'] = get_region()
    log_entry['cluster'] = get_cluster()
    
    # Correlate with metrics
    if 'host' in log_entry:
        log_entry['host_metrics'] = get_current_metrics(log_entry['host'])
    
    return log_entry

def get_service_dependencies(service_name):
    """Get service dependencies from service mesh"""
    # Query service mesh for dependencies
    dependencies = {
        'upstream': ['api-gateway'],
        'downstream': ['database', 'cache']
    }
    return dependencies
```

---

## Data Quality and Validation

### Validate Incoming Data
```python
from pydantic import BaseModel, validator
from datetime import datetime

class MetricData(BaseModel):
    """Schema for metric data"""
    timestamp: datetime
    metric_name: str
    value: float
    host: str
    tags: dict = {}
    
    @validator('value')
    def value_must_be_valid(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Metric value must be between 0 and 100')
        return v
    
    @validator('timestamp')
    def timestamp_not_future(cls, v):
        if v > datetime.utcnow():
            raise ValueError('Timestamp cannot be in the future')
        return v

# Usage
try:
    metric = MetricData(
        timestamp=datetime.utcnow(),
        metric_name='cpu.usage',
        value=75.5,
        host='server-01',
        tags={'env': 'production'}
    )
    # Process valid metric
except ValueError as e:
    print(f"Invalid metric data: {e}")
```

---

## Handling High Volume Data

### Sampling Strategy
```python
import random

class DataSampler:
    """Sample high-volume data intelligently"""
    
    def __init__(self, sample_rate=0.1):
        self.sample_rate = sample_rate
    
    def should_sample(self, data):
        """Decide if data point should be sampled"""
        
        # Always sample errors
        if data.get('level') == 'ERROR':
            return True
        
        # Always sample anomalies
        if self.is_anomaly(data):
            return True
        
        # Sample normal data based on rate
        return random.random() < self.sample_rate
    
    def is_anomaly(self, data):
        """Check if data point is anomalous"""
        # Simple threshold-based check
        if 'value' in data:
            return data['value'] > 90 or data['value'] < 10
        return False

# Usage
sampler = DataSampler(sample_rate=0.1)

for data_point in data_stream:
    if sampler.should_sample(data_point):
        process_data(data_point)
```

### Batching for Efficiency
```python
class DataBatcher:
    """Batch data for efficient processing"""
    
    def __init__(self, batch_size=1000, flush_interval=5):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch = []
        self.last_flush = time.time()
    
    def add(self, data):
        """Add data to batch"""
        self.batch.append(data)
        
        # Flush if batch is full or time elapsed
        if len(self.batch) >= self.batch_size or \
           time.time() - self.last_flush >= self.flush_interval:
            self.flush()
    
    def flush(self):
        """Process and clear batch"""
        if self.batch:
            process_batch(self.batch)
            self.batch = []
            self.last_flush = time.time()

# Usage
batcher = DataBatcher(batch_size=1000, flush_interval=5)

for data in data_stream:
    batcher.add(data)
```

---

## Multi-Source Data Integration

### Unified Data Collection
```python
class UnifiedDataCollector:
    """Collect data from multiple sources"""
    
    def __init__(self):
        self.collectors = {
            'prometheus': PrometheusCollector(),
            'elasticsearch': ElasticsearchCollector(),
            'jaeger': JaegerCollector()
        }
    
    def collect_all(self, time_range):
        """Collect data from all sources"""
        unified_data = {
            'metrics': [],
            'logs': [],
            'traces': []
        }
        
        # Collect metrics from Prometheus
        unified_data['metrics'] = self.collectors['prometheus'].query(
            'up', time_range
        )
        
        # Collect logs from Elasticsearch
        unified_data['logs'] = self.collectors['elasticsearch'].search(
            index='logs-*', time_range=time_range
        )
        
        # Collect traces from Jaeger
        unified_data['traces'] = self.collectors['jaeger'].get_traces(
            service='my-service', time_range=time_range
        )
        
        return unified_data
    
    def correlate_data(self, unified_data):
        """Correlate data across sources using trace IDs"""
        correlated = {}
        
        for trace in unified_data['traces']:
            trace_id = trace['trace_id']
            
            correlated[trace_id] = {
                'trace': trace,
                'logs': [l for l in unified_data['logs'] 
                        if l.get('trace_id') == trace_id],
                'metrics': self.get_metrics_for_trace(trace, unified_data['metrics'])
            }
        
        return correlated
```

---

## Data Storage Strategies

### Time Series Database (InfluxDB)
```python
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Connect to InfluxDB
client = InfluxDBClient(
    url="http://localhost:8086",
    token="my-token",
    org="my-org"
)

write_api = client.write_api(write_options=SYNCHRONOUS)

# Write metric data
point = Point("cpu_usage") \
    .tag("host", "server-01") \
    .tag("region", "us-east-1") \
    .field("value", 75.5) \
    .time(datetime.utcnow())

write_api.write(bucket="metrics", record=point)

# Query data
query_api = client.query_api()
query = '''
from(bucket: "metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "cpu_usage")
  |> filter(fn: (r) => r.host == "server-01")
'''

result = query_api.query(query)
```

---

## Monitoring Data Collection

### Health Checks
```python
def check_data_pipeline_health():
    """Monitor data pipeline health"""
    
    health = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Check Kafka connectivity
    try:
        producer.list_topics(timeout=5)
        health['checks']['kafka'] = 'healthy'
    except Exception as e:
        health['checks']['kafka'] = f'unhealthy: {e}'
        health['status'] = 'unhealthy'
    
    # Check Elasticsearch
    try:
        es.ping()
        health['checks']['elasticsearch'] = 'healthy'
    except Exception as e:
        health['checks']['elasticsearch'] = f'unhealthy: {e}'
        health['status'] = 'unhealthy'
    
    # Check data freshness
    latest_data = es.search(index='metrics-*', size=1, sort='@timestamp:desc')
    if latest_data['hits']['hits']:
        latest_timestamp = latest_data['hits']['hits'][0]['_source']['@timestamp']
        age = (datetime.utcnow() - parse_timestamp(latest_timestamp)).seconds
        
        if age > 300:  # 5 minutes
            health['checks']['data_freshness'] = f'stale: {age}s old'
            health['status'] = 'degraded'
        else:
            health['checks']['data_freshness'] = f'fresh: {age}s old'
    
    return health
```

---

## Best Practices

1. **Use Standard Formats**: JSON, Protobuf for data interchange
2. **Add Timestamps**: Always include timestamps in UTC
3. **Include Context**: Add tags/labels for filtering
4. **Implement Backpressure**: Handle data volume spikes
5. **Monitor Pipeline**: Track data flow and latency
6. **Validate Data**: Ensure data quality at ingestion
7. **Handle Failures**: Implement retry logic and dead letter queues
8. **Secure Data**: Encrypt sensitive information
9. **Optimize Storage**: Use appropriate retention policies
10. **Document Schema**: Maintain data format documentation

---

## Summary

Effective data collection for AIOps requires:
- Multiple data source integration
- Robust ingestion pipelines
- Data enrichment and validation
- Efficient storage strategies
- Monitoring and health checks

---

**Next**: [Observability Fundamentals →](04-observability-fundamentals.md)
