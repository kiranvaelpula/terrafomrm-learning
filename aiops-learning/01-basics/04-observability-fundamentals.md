# Observability Fundamentals

## Learning Objectives
- Understand the three pillars of observability
- Differentiate observability from monitoring
- Implement observability best practices
- Build observable systems for AIOps

---

## What is Observability?

**Observability** is the ability to understand the internal state of a system by examining its external outputs.

### Monitoring vs Observability

| Aspect | Monitoring | Observability |
|--------|-----------|---------------|
| **Approach** | Known unknowns | Unknown unknowns |
| **Questions** | Pre-defined | Ad-hoc |
| **Metrics** | Dashboards, alerts | Exploration, correlation |
| **Scope** | "Is it working?" | "Why is it broken?" |
| **Data** | Aggregated | High-cardinality, raw |

**Example:**
- **Monitoring**: "Is CPU > 80%?" → Alert
- **Observability**: "Why is this request slow?" → Investigate traces, logs, metrics

---

## The Three Pillars of Observability

### 1. Metrics (What is happening?)
Time-series numerical data showing system state over time.

```python
# Example metrics
{
  "timestamp": "2024-01-15T10:00:00Z",
  "metrics": {
    "cpu_usage_percent": 75.5,
    "memory_usage_mb": 2048,
    "request_rate": 1500,
    "error_rate": 0.02,
    "response_time_p95": 250
  }
}
```

**Key Metrics to Track:**
- **RED Method** (Requests, Errors, Duration)
- **USE Method** (Utilization, Saturation, Errors)
- **Four Golden Signals** (Latency, Traffic, Errors, Saturation)

### 2. Logs (What happened?)
Discrete events with contextual information.

```json
{
  "timestamp": "2024-01-15T10:00:00.123Z",
  "level": "ERROR",
  "service": "payment-service",
  "trace_id": "abc-123-def-456",
  "span_id": "span-789",
  "message": "Payment processing failed",
  "error": "Connection timeout to payment gateway",
  "user_id": "user-12345",
  "transaction_id": "tx-67890",
  "duration_ms": 5000
}
```

**Structured Logging Best Practices:**
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'service': 'my-service',
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add custom fields
        if hasattr(record, 'trace_id'):
            log_data['trace_id'] = record.trace_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        return json.dumps(log_data)

# Configure logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# Usage
logger.info("Payment processed", extra={
    'trace_id': 'abc-123',
    'user_id': 'user-456',
    'amount': 99.99
})
```

### 3. Traces (How did it happen?)
End-to-end journey of requests through distributed systems.

```json
{
  "trace_id": "abc-123-def-456",
  "spans": [
    {
      "span_id": "span-1",
      "parent_span_id": null,
      "operation": "api_request",
      "service": "api-gateway",
      "start_time": "2024-01-15T10:00:00.000Z",
      "duration_ms": 250,
      "tags": {
        "http.method": "POST",
        "http.url": "/api/payment",
        "http.status_code": 200
      }
    },
    {
      "span_id": "span-2",
      "parent_span_id": "span-1",
      "operation": "process_payment",
      "service": "payment-service",
      "start_time": "2024-01-15T10:00:00.050Z",
      "duration_ms": 150,
      "tags": {
        "payment.amount": 99.99,
        "payment.method": "credit_card"
      }
    },
    {
      "span_id": "span-3",
      "parent_span_id": "span-2",
      "operation": "db_query",
      "service": "database",
      "start_time": "2024-01-15T10:00:00.100Z",
      "duration_ms": 50,
      "tags": {
        "db.type": "postgresql",
        "db.statement": "INSERT INTO transactions..."
      }
    }
  ]
}
```

**Distributed Tracing Implementation:**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Setup
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Instrument application
@tracer.start_as_current_span("process_payment")
def process_payment(user_id, amount):
    span = trace.get_current_span()
    
    # Add attributes
    span.set_attribute("user.id", user_id)
    span.set_attribute("payment.amount", amount)
    
    try:
        # Call payment gateway
        with tracer.start_as_current_span("call_payment_gateway"):
            result = payment_gateway.charge(amount)
        
        # Save to database
        with tracer.start_as_current_span("save_transaction"):
            db.save(result)
        
        span.set_attribute("payment.status", "success")
        return result
        
    except Exception as e:
        span.set_attribute("error", True)
        span.record_exception(e)
        raise
```

---

## Implementing Observability

### 1. Metrics Collection with Prometheus

**Application Instrumentation:**
```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)

# Instrument code
def handle_request(method, endpoint):
    active_connections.inc()
    
    start = time.time()
    try:
        # Process request
        result = process(method, endpoint)
        status = 200
        return result
    except Exception as e:
        status = 500
        raise
    finally:
        duration = time.time() - start
        
        # Record metrics
        request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        active_connections.dec()

# Expose metrics
start_http_server(8000)
```

### 2. Log Aggregation with ELK Stack

**Filebeat Configuration:**
```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/app/*.log
    json.keys_under_root: true
    json.add_error_key: true
    fields:
      service: my-application
      environment: production

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "app-logs-%{+yyyy.MM.dd}"

processors:
  - add_host_metadata: ~
  - add_cloud_metadata: ~
```

**Logstash Pipeline:**
```ruby
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  json {
    source => "message"
  }
  
  # Parse timestamp
  date {
    match => [ "timestamp", "ISO8601" ]
    target => "@timestamp"
  }
  
  # Extract error details
  if [level] == "ERROR" {
    mutate {
      add_tag => ["error"]
    }
  }
  
  # Grok for unstructured logs
  grok {
    match => { "message" => "%{COMBINEDAPACHELOG}" }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }
}
```

### 3. Distributed Tracing Setup

**Jaeger Deployment:**
```yaml
# docker-compose.yml
version: '3'
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"  # UI
      - "14268:14268"
      - "9411:9411"
    environment:
      - COLLECTOR_ZIPKIN_HTTP_PORT=9411
```

---

## Correlation: Tying it All Together

### Unified Observability
```python
import logging
from opentelemetry import trace

class ObservableApp:
    """Application with full observability"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tracer = trace.get_tracer(__name__)
    
    def process_request(self, request_id, user_id):
        """Process request with full observability"""
        
        # Start trace
        with self.tracer.start_as_current_span("process_request") as span:
            # Add trace context to logs
            trace_id = format(span.get_span_context().trace_id, '032x')
            
            # Structured logging with trace context
            self.logger.info(
                "Processing request",
                extra={
                    'trace_id': trace_id,
                    'request_id': request_id,
                    'user_id': user_id
                }
            )
            
            # Add span attributes
            span.set_attribute("request.id", request_id)
            span.set_attribute("user.id", user_id)
            
            try:
                # Business logic
                result = self.do_work(request_id)
                
                # Record success metrics
                request_count.labels(status='success').inc()
                
                self.logger.info(
                    "Request completed",
                    extra={
                        'trace_id': trace_id,
                        'request_id': request_id,
                        'duration_ms': span.elapsed_time
                    }
                )
                
                return result
                
            except Exception as e:
                # Record error
                span.set_attribute("error", True)
                span.record_exception(e)
                
                request_count.labels(status='error').inc()
                
                self.logger.error(
                    "Request failed",
                    extra={
                        'trace_id': trace_id,
                        'request_id': request_id,
                        'error': str(e)
                    },
                    exc_info=True
                )
                raise
```

### Query Across All Three Pillars

```python
def investigate_slow_request(trace_id):
    """Investigate using metrics, logs, and traces"""
    
    # 1. Get trace details
    trace = jaeger_client.get_trace(trace_id)
    
    print(f"Trace Duration: {trace['duration_ms']}ms")
    print(f"Spans: {len(trace['spans'])}")
    
    # Find slowest span
    slowest_span = max(trace['spans'], key=lambda s: s['duration_ms'])
    print(f"Slowest operation: {slowest_span['operation']} ({slowest_span['duration_ms']}ms)")
    
    # 2. Get related logs
    logs = elasticsearch.search(
        index='logs-*',
        body={
            'query': {
                'match': {'trace_id': trace_id}
            },
            'sort': [{'@timestamp': 'asc'}]
        }
    )
    
    print(f"\nRelated logs:")
    for log in logs['hits']['hits']:
        print(f"  [{log['_source']['level']}] {log['_source']['message']}")
    
    # 3. Get metrics at the time
    time_range = {
        'start': trace['start_time'],
        'end': trace['end_time']
    }
    
    metrics = prometheus.query_range(
        query='rate(http_request_duration_seconds_sum[1m])',
        start=time_range['start'],
        end=time_range['end']
    )
    
    print(f"\nAverage latency during request: {metrics['avg']}s")
    
    # 4. Generate report
    return {
        'trace': trace,
        'logs': logs,
        'metrics': metrics,
        'analysis': analyze_patterns(trace, logs, metrics)
    }
```

---

## Observability for Different Components

### 1. API Observability
```python
from flask import Flask, request
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)

# Auto-instrument Flask
FlaskInstrumentor().instrument_app(app)

@app.before_request
def before_request():
    # Add request ID
    request.request_id = generate_request_id()
    
    # Log request
    logger.info("Request received", extra={
        'request_id': request.request_id,
        'method': request.method,
        'path': request.path,
        'user_agent': request.headers.get('User-Agent')
    })

@app.after_request
def after_request(response):
    # Log response
    logger.info("Request completed", extra={
        'request_id': request.request_id,
        'status_code': response.status_code,
        'content_length': response.content_length
    })
    
    return response

@app.errorhandler(Exception)
def handle_error(error):
    logger.error("Request failed", extra={
        'request_id': request.request_id,
        'error': str(error)
    }, exc_info=True)
    
    return {"error": "Internal server error"}, 500
```

### 2. Database Observability
```python
from sqlalchemy import event, create_engine
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    
    # Log query
    logger.debug("Executing query", extra={
        'query': statement,
        'parameters': parameters
    })

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop()
    
    # Record metrics
    db_query_duration.observe(total)
    
    # Log slow queries
    if total > 1.0:  # 1 second
        logger.warning("Slow query detected", extra={
            'query': statement,
            'duration_seconds': total
        })
```

### 3. Message Queue Observability
```python
from kafka import KafkaProducer, KafkaConsumer

class ObservableKafkaProducer:
    """Kafka producer with observability"""
    
    def __init__(self, bootstrap_servers):
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        self.tracer = trace.get_tracer(__name__)
    
    def send(self, topic, message):
        with self.tracer.start_as_current_span(f"kafka_produce_{topic}") as span:
            span.set_attribute("messaging.system", "kafka")
            span.set_attribute("messaging.destination", topic)
            
            start = time.time()
            try:
                future = self.producer.send(topic, message)
                result = future.get(timeout=10)
                
                duration = time.time() - start
                kafka_produce_duration.labels(topic=topic).observe(duration)
                
                logger.info("Message sent", extra={
                    'topic': topic,
                    'partition': result.partition,
                    'offset': result.offset
                })
                
                return result
                
            except Exception as e:
                span.record_exception(e)
                logger.error("Failed to send message", extra={
                    'topic': topic,
                    'error': str(e)
                })
                raise
```

---

## Observability Best Practices

### 1. High-Cardinality Data
```python
# ❌ Bad: Too many unique label values
request_count.labels(user_id=user_id).inc()  # Millions of users!

# ✅ Good: Use tags in traces/logs instead
span.set_attribute("user.id", user_id)
logger.info("Request", extra={'user_id': user_id})
```

### 2. Sampling Strategy
```python
class SmartSampler:
    """Intelligent trace sampling"""
    
    def should_sample(self, request):
        # Always sample errors
        if request.error:
            return True
        
        # Always sample slow requests
        if request.duration > 1000:  # 1 second
            return True
        
        # Sample 1% of normal traffic
        return random.random() < 0.01
```

### 3. Context Propagation
```python
import requests
from opentelemetry.propagate import inject

def call_downstream_service(url, data):
    """Call service with trace context"""
    
    # Create headers
    headers = {}
    
    # Inject trace context into headers
    inject(headers)
    
    # Make request
    response = requests.post(url, json=data, headers=headers)
    
    return response
```

---

## Observability Tools Stack

### Complete Stack Example
```yaml
# docker-compose.yml
version: '3'

services:
  # Metrics
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
  
  # Logs
  elasticsearch:
    image: elasticsearch:8.5.0
    ports:
      - "9200:9200"
    environment:
      - discovery.type=single-node
  
  kibana:
    image: kibana:8.5.0
    ports:
      - "5601:5601"
  
  # Traces
  jaeger:
    image: jaegertracing/all-in-one
    ports:
      - "16686:16686"
      - "6831:6831/udp"
```

---

## Summary

Observability enables you to:
- Understand system behavior in production
- Debug complex distributed systems
- Detect and diagnose issues quickly
- Make data-driven decisions

**Key Principles:**
1. **Instrument everything** - metrics, logs, traces
2. **Structure your data** - use consistent formats
3. **Correlate signals** - link metrics, logs, traces
4. **Sample intelligently** - balance cost and visibility
5. **Make it actionable** - observability drives AIOps

---

**Next**: [First AIOps Implementation →](05-first-aiops-implementation.md)
