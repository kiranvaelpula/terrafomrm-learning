# AIOps at Scale

Learn how to build and operate AIOps platforms that handle enterprise-scale data volumes, multiple teams, and thousands of services.

---

## Challenges at Scale

### Data Volume Challenges

**Small Scale (1-10 services)**:
- 10K metrics/second
- 1GB logs/day
- 100 traces/second

**Enterprise Scale (1000+ services)**:
- 10M+ metrics/second
- 10TB+ logs/day
- 1M+ traces/second

**Problems**:
1. Storage costs become prohibitive
2. Query latency increases
3. ML training takes hours/days
4. Real-time processing difficult

---

## Scalable Data Architecture

### 1. Data Pipeline Architecture

```
                    ┌─────────────┐
                    │   Services  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Agents    │ (Collect metrics/logs/traces)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Kafka     │ (Message queue)
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐  ┌──▼──────┐  ┌▼──────────┐
       │   Stream    │  │  Batch  │  │   Store   │
       │ Processing  │  │  Store  │  │  (S3/GCS) │
       └──────┬──────┘  └──┬──────┘  └───────────┘
              │            │
       ┌──────▼──────┐  ┌──▼──────┐
       │   AIOps     │  │   ML    │
       │  Real-time  │  │Training │
       └─────────────┘  └─────────┘
```

### 2. Kafka for Data Ingestion

```python
from kafka import KafkaProducer, KafkaConsumer
import json

# Producer: Collect and send metrics
class MetricsProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='snappy',
            batch_size=16384,  # Batch for efficiency
            linger_ms=10  # Wait up to 10ms to batch
        )
    
    def send_metric(self, metric):
        """Send metric to appropriate topic"""
        topic = f"metrics.{metric['service']}"
        self.producer.send(topic, value=metric)
    
    def send_batch(self, metrics):
        """Send multiple metrics efficiently"""
        for metric in metrics:
            self.send_metric(metric)
        self.producer.flush()

# Consumer: Process metrics in real-time
class MetricsConsumer:
    def __init__(self, group_id='aiops-processor'):
        self.consumer = KafkaConsumer(
            'metrics.*',  # Subscribe to all metric topics
            bootstrap_servers=['kafka:9092'],
            group_id=group_id,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
    
    def process_stream(self):
        """Process metrics in real-time"""
        for message in self.consumer:
            metric = message.value
            
            # Process metric
            self.detect_anomaly(metric)
            self.update_aggregates(metric)
            
    def detect_anomaly(self, metric):
        """Real-time anomaly detection"""
        features = extract_features(metric)
        if model.predict([features])[0] == -1:
            alert_anomaly(metric)

# Usage
producer = MetricsProducer()
consumer = MetricsConsumer()

# Send metrics
producer.send_batch(collected_metrics)

# Process in separate thread
import threading
thread = threading.Thread(target=consumer.process_stream)
thread.start()
```

---

### 3. Stream Processing with Apache Flink

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.common import Time

# Setup Flink environment
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(10)  # Scale horizontally

# Read from Kafka
metrics_stream = env.add_source(
    FlinkKafkaConsumer(
        topics=['metrics'],
        properties={'bootstrap.servers': 'kafka:9092'}
    )
)

# Real-time aggregation
aggregated = metrics_stream \
    .key_by(lambda x: x['service']) \
    .window(TumblingEventTimeWindows.of(Time.minutes(1))) \
    .aggregate(MetricAggregator())

# Anomaly detection
anomalies = aggregated \
    .map(lambda x: detect_anomaly(x)) \
    .filter(lambda x: x['is_anomaly'])

# Alert on anomalies
anomalies.add_sink(AlertSink())

# Execute
env.execute("AIOps Real-time Processing")
```

---

## Scalable Storage Strategy

### 1. Time-Series Database (Prometheus/Victoria Metrics)

```python
# victoria_metrics_config.py

import requests

class VictoriaMetricsClient:
    def __init__(self, url='http://victoriametrics:8428'):
        self.url = url
    
    def write_metrics(self, metrics):
        """Write metrics in Prometheus format"""
        lines = []
        for metric in metrics:
            labels = ','.join(f'{k}="{v}"' for k, v in metric['labels'].items())
            line = f"{metric['name']}{{{labels}}} {metric['value']} {metric['timestamp']}"
            lines.append(line)
        
        response = requests.post(
            f"{self.url}/api/v1/import/prometheus",
            data='\n'.join(lines)
        )
        return response.status_code == 204
    
    def query(self, query, start, end):
        """Query metrics with PromQL"""
        response = requests.get(
            f"{self.url}/api/v1/query_range",
            params={
                'query': query,
                'start': start,
                'end': end,
                'step': '1m'
            }
        )
        return response.json()

# Retention and downsampling configuration
"""
# victoriametrics-config.yaml
retentionPeriod: 365d  # Keep 1 year

# Downsample for long-term storage
# 1m resolution for 30 days
# 5m resolution for 90 days  
# 1h resolution for 1 year
"""

vm_client = VictoriaMetricsClient()

# Write 10M metrics efficiently
vm_client.write_metrics(batch_of_10_million_metrics)
```

---

### 2. Log Storage (Elasticsearch/Loki)

```python
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

class ScalableLogStorage:
    def __init__(self):
        self.es = Elasticsearch(['http://elasticsearch:9200'])
        
        # Create index template with ILM
        self.create_index_template()
    
    def create_index_template(self):
        """Create template with Index Lifecycle Management"""
        template = {
            "index_patterns": ["logs-*"],
            "settings": {
                "number_of_shards": 5,
                "number_of_replicas": 1,
                "index.lifecycle.name": "logs-policy",
                "index.lifecycle.rollover_alias": "logs"
            },
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "service": {"type": "keyword"},
                    "level": {"type": "keyword"},
                    "message": {"type": "text"},
                    "trace_id": {"type": "keyword"}
                }
            }
        }
        self.es.indices.put_template(name="logs-template", body=template)
    
    def create_ilm_policy(self):
        """Create ILM policy for automatic data management"""
        policy = {
            "policy": {
                "phases": {
                    "hot": {
                        "actions": {
                            "rollover": {
                                "max_size": "50GB",
                                "max_age": "1d"
                            }
                        }
                    },
                    "warm": {
                        "min_age": "7d",
                        "actions": {
                            "forcemerge": {"max_num_segments": 1},
                            "shrink": {"number_of_shards": 1}
                        }
                    },
                    "cold": {
                        "min_age": "30d",
                        "actions": {
                            "freeze": {}
                        }
                    },
                    "delete": {
                        "min_age": "90d",
                        "actions": {
                            "delete": {}
                        }
                    }
                }
            }
        }
        self.es.ilm.put_lifecycle(policy="logs-policy", body=policy)
    
    def bulk_index_logs(self, logs):
        """Index logs in bulk"""
        actions = [
            {
                "_index": "logs",
                "_source": log
            }
            for log in logs
        ]
        
        success, failed = bulk(self.es, actions)
        return success, failed

# Usage
storage = ScalableLogStorage()
storage.create_ilm_policy()

# Index 1M logs efficiently
storage.bulk_index_logs(one_million_logs)
```

---

## Scalable ML Training

### 1. Distributed Training with Ray

```python
import ray
from ray import train
from ray.train import ScalingConfig
from sklearn.ensemble import RandomForestClassifier

ray.init(address='auto')  # Connect to Ray cluster

@ray.remote
def train_model_partition(data_partition):
    """Train on data partition"""
    model = RandomForestClassifier(n_estimators=100)
    model.fit(data_partition['X'], data_partition['y'])
    return model

def distributed_training(data):
    """Train model on distributed data"""
    # Partition data across workers
    num_workers = 10
    partitions = partition_data(data, num_workers)
    
    # Train in parallel
    futures = [
        train_model_partition.remote(partition)
        for partition in partitions
    ]
    
    # Collect models
    models = ray.get(futures)
    
    # Ensemble models
    final_model = EnsembleModel(models)
    return final_model

# Train on 100GB of data distributed across cluster
final_model = distributed_training(large_dataset)
```

---

### 2. Feature Engineering at Scale with Spark

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, avg, stddev

# Initialize Spark
spark = SparkSession.builder \
    .appName("AIOps Feature Engineering") \
    .config("spark.executor.instances", "20") \
    .config("spark.executor.memory", "8g") \
    .getOrCreate()

# Read metrics from S3/HDFS
metrics_df = spark.read \
    .parquet("s3://aiops-data/metrics/") \
    .where("timestamp > '2024-01-01'")

# Feature engineering
features_df = metrics_df \
    .groupBy(
        "service",
        window("timestamp", "5 minutes")
    ) \
    .agg(
        avg("cpu_usage").alias("avg_cpu"),
        stddev("cpu_usage").alias("std_cpu"),
        avg("memory_usage").alias("avg_memory"),
        avg("latency_ms").alias("avg_latency")
    )

# Add time-based features
from pyspark.sql.functions import hour, dayofweek

features_df = features_df \
    .withColumn("hour", hour(col("window.start"))) \
    .withColumn("day_of_week", dayofweek(col("window.start")))

# Write features for training
features_df.write \
    .partitionBy("date") \
    .parquet("s3://aiops-data/features/")

print(f"Processed {features_df.count():,} feature records")
```

---

## Horizontal Scaling Patterns

### 1. Microservices Architecture

```yaml
# docker-compose-scale.yaml

version: '3.8'

services:
  # API Gateway
  api-gateway:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
  
  # Anomaly Detection Service (scaled)
  anomaly-detector:
    image: aiops/anomaly-detector:latest
    deploy:
      replicas: 10  # Scale horizontally
      resources:
        limits:
          cpus: '1'
          memory: 2G
    environment:
      - MODEL_PATH=/models/anomaly_detector
      - KAFKA_BROKERS=kafka:9092
  
  # Root Cause Analysis Service (scaled)
  rca-service:
    image: aiops/rca-service:latest
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '2'
          memory: 4G
  
  # Prediction Service (scaled)
  prediction-service:
    image: aiops/prediction-service:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

### 2. Load Balancing

```python
# load_balancer.py

from fastapi import FastAPI, Request
import httpx
import random

app = FastAPI()

# Backend services
BACKENDS = [
    "http://anomaly-detector-1:8000",
    "http://anomaly-detector-2:8000",
    "http://anomaly-detector-3:8000",
]

class LoadBalancer:
    def __init__(self):
        self.backends = BACKENDS
        self.current = 0  # For round-robin
        self.health_status = {b: True for b in BACKENDS}
    
    async def check_health(self):
        """Check backend health"""
        for backend in self.backends:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{backend}/health", timeout=1.0)
                    self.health_status[backend] = response.status_code == 200
            except:
                self.health_status[backend] = False
    
    def get_backend_round_robin(self):
        """Round-robin load balancing"""
        healthy_backends = [
            b for b in self.backends 
            if self.health_status[b]
        ]
        
        if not healthy_backends:
            raise Exception("No healthy backends")
        
        backend = healthy_backends[self.current % len(healthy_backends)]
        self.current += 1
        return backend
    
    def get_backend_least_connections(self):
        """Least connections load balancing"""
        # Track connections per backend
        return min(
            self.backends,
            key=lambda b: connection_count.get(b, 0)
        )

lb = LoadBalancer()

@app.post("/predict")
async def predict(request: Request):
    """Forward request to backend"""
    backend = lb.get_backend_round_robin()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{backend}/predict",
            json=await request.json()
        )
        return response.json()
```

---

## Caching Strategies

### 1. Redis for Feature Caching

```python
import redis
import pickle
from functools import wraps

class FeatureCache:
    def __init__(self):
        self.redis = redis.Redis(
            host='redis-cluster',
            port=6379,
            decode_responses=False
        )
        self.ttl = 3600  # 1 hour
    
    def cache_features(self, func):
        """Decorator to cache features"""
        @wraps(func)
        def wrapper(entity_id, *args, **kwargs):
            # Check cache
            cache_key = f"features:{entity_id}"
            cached = self.redis.get(cache_key)
            
            if cached:
                return pickle.loads(cached)
            
            # Compute features
            features = func(entity_id, *args, **kwargs)
            
            # Store in cache
            self.redis.setex(
                cache_key,
                self.ttl,
                pickle.dumps(features)
            )
            
            return features
        return wrapper

cache = FeatureCache()

@cache.cache_features
def compute_features(entity_id):
    """Expensive feature computation"""
    # This only runs if not in cache
    return expensive_feature_engineering(entity_id)

# First call: computes features (slow)
features1 = compute_features("service-123")

# Second call: returns from cache (fast)
features2 = compute_features("service-123")
```

---

### 2. Model Prediction Caching

```python
class PredictionCache:
    def __init__(self):
        self.cache = {}
        self.max_size = 10000
        self.ttl = 300  # 5 minutes
    
    def get_cache_key(self, features):
        """Create cache key from features"""
        return hash(tuple(features))
    
    def get(self, features):
        """Get cached prediction"""
        key = self.get_cache_key(features)
        
        if key in self.cache:
            prediction, timestamp = self.cache[key]
            
            # Check if expired
            if time.time() - timestamp < self.ttl:
                return prediction
            else:
                del self.cache[key]
        
        return None
    
    def set(self, features, prediction):
        """Cache prediction"""
        key = self.get_cache_key(features)
        
        # Evict old entries if cache full
        if len(self.cache) >= self.max_size:
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k][1]
            )
            del self.cache[oldest_key]
        
        self.cache[key] = (prediction, time.time())

# Usage
pred_cache = PredictionCache()

def predict_with_cache(features):
    # Check cache first
    cached = pred_cache.get(features)
    if cached is not None:
        return cached
    
    # Compute prediction
    prediction = model.predict([features])[0]
    
    # Cache result
    pred_cache.set(features, prediction)
    
    return prediction
```

---

## Multi-Tenancy Architecture

### 1. Data Isolation

```python
class MultiTenantAIOps:
    def __init__(self):
        self.models = {}  # Tenant-specific models
        self.data_stores = {}  # Tenant-specific data
    
    def get_tenant_model(self, tenant_id):
        """Get model for specific tenant"""
        if tenant_id not in self.models:
            # Load tenant-specific model
            model_path = f"/models/{tenant_id}/anomaly_detector"
            self.models[tenant_id] = load_model(model_path)
        
        return self.models[tenant_id]
    
    def predict(self, tenant_id, features):
        """Make tenant-specific prediction"""
        model = self.get_tenant_model(tenant_id)
        return model.predict([features])
    
    def get_tenant_metrics(self, tenant_id, start, end):
        """Query tenant-specific metrics"""
        # Metrics stored in separate indices per tenant
        index = f"metrics-{tenant_id}"
        return self.es.search(index=index, body={
            "query": {
                "range": {
                    "timestamp": {"gte": start, "lte": end}
                }
            }
        })

# Usage
aiops = MultiTenantAIOps()

# Each tenant has isolated data and models
prediction_tenant_a = aiops.predict("tenant-a", features)
prediction_tenant_b = aiops.predict("tenant-b", features)
```

---

## Performance Optimization

### 1. Batch Prediction

```python
class BatchPredictor:
    def __init__(self, model, batch_size=1000):
        self.model = model
        self.batch_size = batch_size
        self.queue = []
    
    async def add_to_queue(self, entity_id, features):
        """Add prediction request to queue"""
        future = asyncio.Future()
        self.queue.append((entity_id, features, future))
        
        # Process batch if full
        if len(self.queue) >= self.batch_size:
            await self.process_batch()
        
        return await future
    
    async def process_batch(self):
        """Process accumulated requests in batch"""
        if not self.queue:
            return
        
        # Extract features
        batch_features = [item[1] for item in self.queue]
        
        # Batch prediction (much faster)
        predictions = self.model.predict(batch_features)
        
        # Return results
        for (entity_id, _, future), prediction in zip(self.queue, predictions):
            future.set_result(prediction)
        
        self.queue = []

# Usage
predictor = BatchPredictor(model)

# Multiple concurrent requests batched automatically
predictions = await asyncio.gather(
    predictor.add_to_queue("service-1", features1),
    predictor.add_to_queue("service-2", features2),
    predictor.add_to_queue("service-3", features3),
    # ... 1000 requests batched together
)
```

---

## Monitoring AIOps at Scale

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
predictions_total = Counter(
    'aiops_predictions_total',
    'Total predictions made',
    ['tenant', 'model', 'result']
)

prediction_latency = Histogram(
    'aiops_prediction_latency_seconds',
    'Prediction latency',
    buckets=[.001, .005, .01, .05, .1, .5, 1.0, 5.0]
)

active_tenants = Gauge(
    'aiops_active_tenants',
    'Number of active tenants'
)

data_ingestion_rate = Counter(
    'aiops_data_points_ingested_total',
    'Total data points ingested',
    ['data_type']
)

class MonitoredAIOps:
    def __init__(self):
        self.model = load_model()
    
    @prediction_latency.time()
    def predict(self, tenant_id, features):
        """Make prediction with monitoring"""
        start = time.time()
        
        try:
            prediction = self.model.predict([features])[0]
            result = 'anomaly' if prediction == -1 else 'normal'
            
            predictions_total.labels(
                tenant=tenant_id,
                model='anomaly_detector',
                result=result
            ).inc()
            
            return prediction
            
        except Exception as e:
            predictions_total.labels(
                tenant=tenant_id,
                model='anomaly_detector',
                result='error'
            ).inc()
            raise
```

---

## Summary

Key strategies for scaling AIOps:

1. **Data Pipeline**: Use Kafka + Stream processing
2. **Storage**: Time-series DB + Elasticsearch with ILM
3. **Training**: Distributed with Ray/Spark
4. **Serving**: Horizontal scaling + load balancing
5. **Caching**: Redis for features and predictions
6. **Multi-tenancy**: Isolate data and models per tenant
7. **Optimization**: Batch processing, caching
8. **Monitoring**: Track all metrics

**Next**: [AIOps Security and Privacy →](19-aiops-security-privacy.md)

