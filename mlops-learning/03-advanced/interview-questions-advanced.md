# MLOps Interview Questions - Advanced Level

Comprehensive advanced interview questions covering model monitoring, drift detection, feature stores, distributed training, and production MLOps at scale.

---

## System Design Questions

### Q1: Design a complete MLOps platform for a large e-commerce company processing 10M predictions/day.

**Answer:**

**Requirements Analysis:**
- 10M predictions/day ≈ 115 predictions/second
- High availability (99.99% uptime)
- Low latency (<100ms p99)
- Multiple models (recommendation, fraud, search)
- Continuous retraining
- Model versioning and rollback
- Monitoring and alerting

**Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway Layer                        │
│  (Load Balancer, Rate Limiting, Authentication)             │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴──────────────┐
        │                           │
┌───────▼───────┐         ┌─────────▼──────────┐
│ Model Serving │         │  Feature Store     │
│  (KServe)     │◄────────│   (Feast)          │
│ - Autoscaling │         │ - Online features  │
│ - A/B testing │         │ - Low latency      │
└───────┬───────┘         └────────────────────┘
        │
┌───────▼────────────────────────────────────────┐
│          Model Registry (MLflow)               │
│ - Version management                           │
│ - Lineage tracking                             │
│ - Stage transitions                            │
└───────┬────────────────────────────────────────┘
        │
┌───────▼────────────────────────────────────────┐
│    Training Pipeline (Kubeflow/Airflow)       │
│ - Scheduled retraining                         │
│ - Data validation                              │
│ - Model training                               │
│ - Model validation                             │
└───────┬────────────────────────────────────────┘
        │
┌───────▼────────────────────────────────────────┐
│      Data Lake (S3) + Warehouse (Snowflake)   │
│ - Training data                                │
│ - Feature data                                 │
│ - Prediction logs                              │
└────────────────────────────────────────────────┘
```


**Component Details:**

1. **Model Serving Layer (KServe)**:
```python
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: fraud-detector
spec:
  predictor:
    minReplicas: 5
    maxReplicas: 50
    scaleTarget: 70  # CPU utilization
    sklearn:
      storageUri: "s3://models/fraud-detector"
      resources:
        requests:
          cpu: "1"
          memory: "2Gi"
        limits:
          cpu: "2"
          memory: "4Gi"
  canaryTrafficPercent: 10  # For A/B testing
```

2. **Feature Store (Feast)**:
```python
# Real-time feature serving
from feast import FeatureStore

store = FeatureStore(repo_path=".")

# Sub-10ms feature retrieval
features = store.get_online_features(
    features=[
        "user_features:total_purchases_30d",
        "user_features:avg_order_value",
        "product_features:popularity_score"
    ],
    entity_rows=[{"user_id": user_id, "product_id": product_id}]
).to_dict()
```

3. **Monitoring Stack**:
```yaml
# Prometheus + Grafana + ELK Stack
Metrics:
  - Prediction latency (p50, p95, p99)
  - Throughput (predictions/sec)
  - Model accuracy (when labels available)
  - Data drift scores
  - Resource utilization

Alerts:
  - Latency > 100ms for 5 minutes
  - Error rate > 1% for 2 minutes
  - Data drift detected
  - Model accuracy < 85%
```

4. **CI/CD Pipeline**:
```yaml
# GitHub Actions + Argo CD
Stages:
  1. Data validation (Great Expectations)
  2. Model training (Kubeflow Pipeline)
  3. Model testing (unit + integration)
  4. Model registration (MLflow)
  5. Canary deployment (10% traffic)
  6. Monitor canary (24 hours)
  7. Gradual rollout (10% → 50% → 100%)
```

**Scalability Considerations:**
- Horizontal pod autoscaling for serving
- Model caching for frequently used models
- Feature pre-computation and caching
- Database read replicas for feature store
- CDN for static model artifacts

**Cost Optimization:**
- Spot instances for training
- Auto-scaling down during low traffic
- Model compression (quantization)
- Feature caching to reduce DB queries
- Batch prediction for non-realtime use cases

**Estimated Costs (AWS):**
- Serving: $5K/month (100 pods average)
- Training: $3K/month (scheduled + on-demand)
- Storage: $2K/month (models + features)
- Monitoring: $1K/month (Prometheus + Grafana)
- **Total: ~$11K/month**

---

### Q2: How would you handle model drift in production and implement automated retraining?

**Answer:**

**Drift Detection Strategy:**

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset
import pandas as pd

class DriftDetector:
    def __init__(self, reference_data, threshold=0.1):
        self.reference_data = reference_data
        self.threshold = threshold
    
    def detect_data_drift(self, current_data):
        """Detect if input features have drifted"""
        report = Report(metrics=[DataDriftPreset()])
        
        report.run(
            reference_data=self.reference_data,
            current_data=current_data
        )
        
        result = report.as_dict()
        drift_detected = result['metrics'][0]['result']['dataset_drift']
        drifted_features = [
            feature['column_name'] 
            for feature in result['metrics'][0]['result']['drift_by_columns'].values()
            if feature['drift_detected']
        ]
        
        return drift_detected, drifted_features
    
    def detect_prediction_drift(self, predictions_last_week, predictions_this_week):
        """Detect if prediction distribution has changed"""
        from scipy.stats import ks_2samp
        
        statistic, pvalue = ks_2samp(predictions_last_week, predictions_this_week)
        
        drift_detected = pvalue < 0.05  # Statistical significance
        return drift_detected, statistic, pvalue
    
    def detect_performance_degradation(self, current_metrics, baseline_metrics):
        """Check if model performance has degraded"""
        degradation = {}
        
        for metric, value in current_metrics.items():
            baseline = baseline_metrics[metric]
            if value < baseline - self.threshold:
                degradation[metric] = {
                    'current': value,
                    'baseline': baseline,
                    'drop': baseline - value
                }
        
        return len(degradation) > 0, degradation

# Usage
detector = DriftDetector(reference_data=training_data)

# Run daily
def daily_drift_check():
    current_data = get_production_data_last_24h()
    
    # Check data drift
    data_drift, drifted_features = detector.detect_data_drift(current_data)
    
    if data_drift:
        alert(f"⚠️ Data drift detected in features: {drifted_features}")
        trigger_retraining()
```

**Automated Retraining Pipeline:**

```python
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'mlops-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'retries': 1,
}

dag = DAG(
    'automated_model_retraining',
    default_args=default_args,
    description='Automated drift detection and retraining',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
)

def check_retraining_triggers():
    """Decide if retraining is needed"""
    triggers = []
    
    # 1. Check data drift
    if check_data_drift():
        triggers.append('data_drift')
    
    # 2. Check performance degradation
    current_accuracy = get_recent_model_accuracy()
    if current_accuracy < BASELINE_ACCURACY - 0.05:
        triggers.append('performance_drop')
    
    # 3. Check time since last training
    days_since_training = get_days_since_last_training()
    if days_since_training > 30:
        triggers.append('scheduled')
    
    # 4. Check new data availability
    new_samples = count_new_labeled_data()
    if new_samples > 10000:
        triggers.append('new_data')
    
    if triggers:
        log_retraining_trigger(triggers)
        return 'retrain_model'
    else:
        return 'skip_retraining'

def extract_training_data():
    """Extract and prepare training data"""
    # Get recent data (last 90 days)
    data = fetch_production_data(days=90)
    
    # Get labels (from feedback loop)
    labels = fetch_labels(data['prediction_ids'])
    
    # Combine and save
    training_data = pd.merge(data, labels, on='prediction_id')
    training_data.to_parquet('/data/training_data.parquet')

def train_new_model():
    """Train model with new data"""
    data = pd.read_parquet('/data/training_data.parquet')
    
    X_train, X_test, y_train, y_test = train_test_split(
        data.drop('target', axis=1),
        data['target'],
        test_size=0.2
    )
    
    with mlflow.start_run(run_name=f"retrain_{datetime.now().strftime('%Y%m%d')}"):
        # Train
        model = train_model(X_train, y_train)
        
        # Evaluate
        metrics = evaluate_model(model, X_test, y_test)
        
        # Log
        mlflow.log_params(model.get_params())
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, "model")
        
        # Save model version
        model_version = mlflow.register_model(
            f"runs:/{mlflow.active_run().info.run_id}/model",
            "production_model"
        )
        
        return model_version.version

def validate_new_model():
    """Validate new model against production"""
    new_model = load_model_from_registry("production_model", stage="None")
    prod_model = load_model_from_registry("production_model", stage="Production")
    
    # Holdout test set
    test_data = load_holdout_test_set()
    
    new_metrics = evaluate_model(new_model, test_data)
    prod_metrics = evaluate_model(prod_model, test_data)
    
    # Compare
    improvement = new_metrics['accuracy'] - prod_metrics['accuracy']
    
    if improvement > 0.01:  # 1% improvement
        log_validation_success(new_metrics, prod_metrics)
        return 'deploy_to_staging'
    else:
        log_validation_failure(new_metrics, prod_metrics)
        return 'skip_deployment'

def deploy_to_staging():
    """Deploy to staging environment"""
    latest_version = get_latest_model_version("production_model")
    
    # Transition to Staging
    client = MlflowClient()
    client.transition_model_version_stage(
        name="production_model",
        version=latest_version,
        stage="Staging"
    )
    
    # Update staging deployment
    update_k8s_deployment(
        namespace="staging",
        deployment="model-service",
        model_version=latest_version
    )

def run_ab_test():
    """Run A/B test in production"""
    # Route 10% traffic to new model
    setup_traffic_split(
        model_a_stage="Production",
        model_b_stage="Staging",
        split_ratio=(90, 10)
    )
    
    # Wait 24 hours for data collection
    time.sleep(24 * 3600)
    
    # Analyze results
    results = analyze_ab_test()
    
    if results['model_b_better'] and results['p_value'] < 0.05:
        return 'promote_to_production'
    else:
        return 'rollback_staging'

def promote_to_production():
    """Promote staging model to production"""
    staging_version = get_model_version("production_model", stage="Staging")
    
    # Archive old production model
    prod_version = get_model_version("production_model", stage="Production")
    transition_to_archived(prod_version)
    
    # Promote staging to production
    client = MlflowClient()
    client.transition_model_version_stage(
        name="production_model",
        version=staging_version,
        stage="Production"
    )
    
    # Gradual rollout
    for traffic_percent in [25, 50, 75, 100]:
        update_traffic_split(production_traffic=traffic_percent)
        time.sleep(3600)  # Wait 1 hour between increases
        check_error_rates()  # Rollback if errors spike

# Define tasks
check_triggers = BranchPythonOperator(
    task_id='check_retraining_triggers',
    python_callable=check_retraining_triggers,
    dag=dag,
)

extract_data = PythonOperator(
    task_id='retrain_model',
    python_callable=extract_training_data,
    dag=dag,
)

train = PythonOperator(
    task_id='train_new_model',
    python_callable=train_new_model,
    dag=dag,
)

validate = BranchPythonOperator(
    task_id='validate_new_model',
    python_callable=validate_new_model,
    dag=dag,
)

staging_deploy = PythonOperator(
    task_id='deploy_to_staging',
    python_callable=deploy_to_staging,
    dag=dag,
)

ab_test = BranchPythonOperator(
    task_id='run_ab_test',
    python_callable=run_ab_test,
    dag=dag,
)

promote = PythonOperator(
    task_id='promote_to_production',
    python_callable=promote_to_production,
    dag=dag,
)

skip_retrain = PythonOperator(
    task_id='skip_retraining',
    python_callable=lambda: print("No retraining needed"),
    dag=dag,
)

skip_deploy = PythonOperator(
    task_id='skip_deployment',
    python_callable=lambda: print("Model validation failed"),
    dag=dag,
)

rollback = PythonOperator(
    task_id='rollback_staging',
    python_callable=lambda: print("A/B test failed, rolling back"),
    dag=dag,
)

# Define workflow
check_triggers >> [extract_data, skip_retrain]
extract_data >> train >> validate
validate >> [staging_deploy, skip_deploy]
staging_deploy >> ab_test
ab_test >> [promote, rollback]
```

**Monitoring Dashboard:**
```python
# Grafana dashboard config
{
  "panels": [
    {
      "title": "Data Drift Score",
      "target": "data_drift_score",
      "alert": {
        "threshold": 0.1,
        "message": "Data drift detected - retraining triggered"
      }
    },
    {
      "title": "Model Accuracy (Last 7 Days)",
      "target": "model_accuracy_7d",
      "alert": {
        "threshold": 0.85,
        "message": "Model accuracy dropped below baseline"
      }
    },
    {
      "title": "Days Since Last Retraining",
      "target": "days_since_retraining",
      "alert": {
        "threshold": 30,
        "message": "Scheduled retraining due"
      }
    },
    {
      "title": "Retraining Pipeline Status",
      "target": "airflow_dag_status{dag_id='automated_model_retraining'}"
    }
  ]
}
```

**Key Decisions:**
- Drift threshold: 0.1 (KS statistic)
- Performance threshold: 5% accuracy drop
- Retraining frequency: Maximum 30 days
- A/B test duration: 24 hours
- Statistical significance: p < 0.05
- Rollout strategy: Gradual (25% → 50% → 75% → 100%)

---

### Q3: Design a feature store architecture for real-time and batch ML workloads.

**Answer:**

**Architecture:**

```
┌──────────────────────────────────────────────────────────────┐
│                    Feature Engineering                        │
│  (Spark/Flink jobs, compute features from raw data)          │
└────────────┬─────────────────────────────┬───────────────────┘
             │                             │
             │ Batch                       │ Stream
             ▼                             ▼
┌────────────────────────┐    ┌──────────────────────────────┐
│   Offline Feature      │    │  Online Feature Store        │
│   Store (S3/Snowflake) │    │  (Redis/DynamoDB)            │
│                        │    │                              │
│ - Historical features  │    │ - Real-time features         │
│ - Point-in-time joins  │    │ - Sub-10ms latency           │
│ - Training data        │    │ - High throughput            │
└────────────┬───────────┘    └──────────┬───────────────────┘
             │                           │
             │ Training                  │ Inference
             ▼                           ▼
    ┌────────────────┐          ┌──────────────────┐
    │ Model Training │          │  Model Serving   │
    │  (Kubeflow)    │          │   (KServe)       │
    └────────────────┘          └──────────────────┘
```

**Implementation (Feast):**

```python
# feature_repo/features.py
from feast import Entity, Feature, FeatureView, FileSource, ValueType
from feast.infra.offline_stores.snowflake_source import SnowflakeSource
from feast.infra.online_stores.redis import RedisOnlineStoreConfig
from datetime import timedelta

# Define entities
user = Entity(
    name="user",
    join_keys=["user_id"],
    description="User entity"
)

product = Entity(
    name="product",
    join_keys=["product_id"],
    description="Product entity"
)

# Offline source (Snowflake for historical data)
user_features_source = SnowflakeSource(
    database="ML_DB",
    schema="FEATURES",
    table="USER_FEATURES",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

# Feature view for user features
user_feature_view = FeatureView(
    name="user_features",
    entities=[user],
    ttl=timedelta(days=1),
    schema=[
        Feature(name="total_purchases_30d", dtype=ValueType.INT64),
        Feature(name="total_purchases_90d", dtype=ValueType.INT64),
        Feature(name="avg_order_value_30d", dtype=ValueType.DOUBLE),
        Feature(name="avg_order_value_90d", dtype=ValueType.DOUBLE),
        Feature(name="days_since_last_purchase", dtype=ValueType.INT64),
        Feature(name="favorite_category", dtype=ValueType.STRING),
        Feature(name="customer_lifetime_value", dtype=ValueType.DOUBLE),
    ],
    online=True,  # Enable online serving
    source=user_features_source,
    tags={"team": "recommendations"},
)

# Stream source for real-time features
from feast.data_source import PushSource

realtime_user_source = PushSource(
    name="realtime_user_features",
    batch_source=user_features_source,
)

# Real-time feature view
from feast import PushMode

realtime_user_features = FeatureView(
    name="realtime_user_features",
    entities=[user],
    ttl=timedelta(minutes=10),
    schema=[
        Feature(name="session_page_views", dtype=ValueType.INT64),
        Feature(name="session_duration_seconds", dtype=ValueType.INT64),
        Feature(name="items_in_cart", dtype=ValueType.INT64),
    ],
    online=True,
    source=realtime_user_source,
    tags={"team": "realtime"},
)
```

**Feature Store Configuration:**

```yaml
# feature_store.yaml
project: ecommerce_ml
registry: s3://ml-feature-registry/registry.db
provider: aws
online_store:
  type: redis
  connection_string: "redis-cluster.production.svc.cluster.local:6379"
  redis_type: redis_cluster
offline_store:
  type: snowflake
  account: mycompany
  user: feast_user
  database: ML_DB
  warehouse: FEAST_WH
  role: FEAST_ROLE
```

**Training Usage (Batch/Historical Features):**

```python
from feast import FeatureStore
import pandas as pd

store = FeatureStore(repo_path="feature_repo/")

# Training data: entity IDs and timestamps
entity_df = pd.DataFrame({
    "user_id": [1001, 1002, 1003],
    "product_id": [5001, 5002, 5003],
    "event_timestamp": [
        datetime(2026, 7, 1, 10, 0, 0),
        datetime(2026, 7, 1, 11, 0, 0),
        datetime(2026, 7, 1, 12, 0, 0),
    ]
})

# Get historical features (point-in-time correct)
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "user_features:total_purchases_30d",
        "user_features:avg_order_value_30d",
        "user_features:customer_lifetime_value",
        "product_features:popularity_score",
        "product_features:avg_rating",
    ],
).to_df()

# Train model
X = training_df.drop(['user_id', 'product_id', 'event_timestamp', 'target'], axis=1)
y = training_df['target']
model.fit(X, y)
```

**Inference Usage (Online/Real-time Features):**

```python
from feast import FeatureStore

store = FeatureStore(repo_path="feature_repo/")

# Real-time prediction endpoint
@app.post("/recommend")
async def recommend(user_id: int, product_id: int):
    # Get features from online store (sub-10ms)
    features = store.get_online_features(
        features=[
            "user_features:total_purchases_30d",
            "user_features:avg_order_value_30d",
            "realtime_user_features:session_page_views",
            "realtime_user_features:items_in_cart",
            "product_features:popularity_score",
        ],
        entity_rows=[{
            "user_id": user_id,
            "product_id": product_id
        }]
    ).to_dict()
    
    # Make prediction
    prediction = model.predict([list(features.values())])
    
    return {"recommendation_score": float(prediction[0])}
```

**Feature Materialization (Batch to Online):**

```python
# Materialize features from offline to online store
from datetime import datetime, timedelta

# Materialize last 7 days of features
store.materialize(
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now()
)

# Schedule daily materialization
from airflow import DAG
from airflow.operators.bash import BashOperator

dag = DAG(
    'feature_materialization',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
)

materialize = BashOperator(
    task_id='materialize_features',
    bash_command='feast materialize-incremental $(date -d "yesterday" +%Y-%m-%d)T00:00:00 $(date +%Y-%m-%d)T00:00:00',
    dag=dag,
)
```

**Streaming Features (Real-time Updates):**

```python
from feast import FeatureStore
import asyncio

store = FeatureStore(repo_path="feature_repo/")

# Kafka consumer for real-time feature updates
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'user-events',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    event = message.value
    
    # Compute real-time features
    features = {
        "user_id": event['user_id'],
        "session_page_views": event['page_view_count'],
        "session_duration_seconds": event['session_duration'],
        "items_in_cart": event['cart_items'],
    }
    
    # Push to online store
    store.push(
        push_source_name="realtime_user_features",
        df=pd.DataFrame([features]),
    )
```

**Feature Monitoring:**

```python
from feast import FeatureStore
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

def monitor_feature_drift():
    """Monitor feature distributions for drift"""
    store = FeatureStore(repo_path="feature_repo/")
    
    # Get training reference data
    reference_data = store.get_historical_features(
        entity_df=training_entities,
        features=feature_list
    ).to_df()
    
    # Get recent production data
    current_data = store.get_historical_features(
        entity_df=production_entities_last_7d,
        features=feature_list
    ).to_df()
    
    # Detect drift
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference_data, current_data=current_data)
    
    if report.as_dict()['metrics'][0]['result']['dataset_drift']:
        alert("Feature drift detected!")

# Schedule drift detection
schedule.every().day.at("02:00").do(monitor_feature_drift)
```

**Performance Optimization:**

```python
# Redis cluster configuration for high throughput
redis_cluster_config = {
    "cluster_enabled": True,
    "cluster_nodes": [
        {"host": "redis-node-1", "port": 6379},
        {"host": "redis-node-2", "port": 6379},
        {"host": "redis-node-3", "port": 6379},
    ],
    "max_connections": 1000,
    "socket_timeout": 0.1,  # 100ms timeout
    "socket_connect_timeout": 0.1,
}

# Feature caching layer
from functools import lru_cache
from datetime import datetime, timedelta

class FeatureCache:
    def __init__(self, ttl_seconds=60):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, entity_key):
        if entity_key in self.cache:
            features, timestamp = self.cache[entity_key]
            if (datetime.now() - timestamp).seconds < self.ttl:
                return features
        return None
    
    def set(self, entity_key, features):
        self.cache[entity_key] = (features, datetime.now())

feature_cache = FeatureCache(ttl_seconds=60)

@app.post("/predict")
async def predict_with_cache(user_id: int):
    # Check cache first
    cached_features = feature_cache.get(user_id)
    
    if cached_features:
        features = cached_features
    else:
        # Fetch from feature store
        features = store.get_online_features(
            features=feature_list,
            entity_rows=[{"user_id": user_id}]
        ).to_dict()
        
        # Update cache
        feature_cache.set(user_id, features)
    
    return model.predict([list(features.values())])
```

**Key Design Decisions:**
- **Offline Store**: Snowflake (scalable, SQL-based)
- **Online Store**: Redis Cluster (low latency, high throughput)
- **Streaming**: Kafka + Flink for real-time features
- **Materialization**: Daily batch + real-time push
- **Caching**: Application-level cache (60s TTL)
- **Monitoring**: Evidently for drift detection

**Benefits:**
- ✅ Training/serving consistency (same features)
- ✅ Feature reuse across models
- ✅ Point-in-time correctness for training
- ✅ Sub-10ms online serving
- ✅ Feature versioning and lineage
- ✅ Centralized feature governance

---

## Technical Deep-Dive Questions

### Q4: Explain model serving optimizations for reducing latency from 500ms to <50ms.

**Answer:**

**Latency Breakdown Analysis:**
```
Total Latency: 500ms
├── Feature Retrieval: 200ms (40%)
├── Model Inference: 250ms (50%)
├── Pre/Post Processing: 30ms (6%)
└── Network Overhead: 20ms (4%)
```

**Optimization Strategy:**

**1. Feature Retrieval Optimization (200ms → 20ms)**

```python
# Before: Sequential DB queries
def get_features_slow(user_id):
    user_features = db.query(f"SELECT * FROM user_features WHERE id={user_id}")
    order_features = db.query(f"SELECT * FROM order_features WHERE user_id={user_id}")
    product_features = db.query(f"SELECT * FROM product_features...")
    # Total: 200ms (3 queries × ~65ms each)

# After: Redis + batch fetching
import redis
from redis.cluster import RedisCluster

redis_client = RedisCluster(
    startup_nodes=[{"host": "redis", "port": 6379}],
    decode_responses=True,
    socket_connect_timeout=0.01,
    socket_timeout=0.01
)

def get_features_fast(user_id):
    # Single pipeline request
    pipe = redis_client.pipeline()
    pipe.hgetall(f"user:{user_id}")
    pipe.hgetall(f"orders:{user_id}")
    pipe.hgetall(f"products:{user_id}")
    results = pipe.execute()  # ~20ms for all
    
    return parse_features(results)

# Additional: Application-level cache
from cachetools import TTLCache

feature_cache = TTLCache(maxsize=10000, ttl=60)  # 60s TTL

def get_features_cached(user_id):
    if user_id in feature_cache:
        return feature_cache[user_id]
    
    features = get_features_fast(user_id)
    feature_cache[user_id] = features
    return features
```

**2. Model Inference Optimization (250ms → 15ms)**

```python
# Model Quantization (FP32 → INT8)
import torch

# Before: FP32 model (250ms)
model = torch.load('model.pth')

# After: INT8 quantized model (50ms)
quantized_model = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear},
    dtype=torch.qint8
)

# ONNX Runtime for faster inference
import onnxruntime as ort

# Convert to ONNX
torch.onnx.export(model, dummy_input, "model.onnx")

# Load with ONNX Runtime
session = ort.InferenceSession(
    "model.onnx",
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)

def predict_onnx(features):
    input_name = session.get_inputs()[0].name
    result = session.run(None, {input_name: features})
    return result[0]  # ~15ms with ONNX + INT8
```

**3. Batch Prediction for Multiple Requests**

```python
from collections import deque
import asyncio

class BatchPredictor:
    def __init__(self, model, max_batch_size=32, max_wait_ms=10):
        self.model = model
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        self.queue = deque()
        self.pending_responses = {}
        
        # Start batch processor
        asyncio.create_task(self.process_batches())
    
    async def predict(self, request_id, features):
        """Queue prediction request"""
        future = asyncio.Future()
        self.queue.append((request_id, features, future))
        return await future
    
    async def process_batches(self):
        """Process requests in batches"""
        while True:
            if len(self.queue) == 0:
                await asyncio.sleep(0.001)
                continue
            
            # Collect batch
            batch = []
            request_ids = []
            futures = []
            
            start_time = time.time()
            while len(batch) < self.max_batch_size and self.queue:
                if (time.time() - start_time) * 1000 > self.max_wait_ms:
                    break
                    
                request_id, features, future = self.queue.popleft()
                batch.append(features)
                request_ids.append(request_id)
                futures.append(future)
            
            # Batch inference (much faster)
            predictions = self.model.predict(np.array(batch))
            
            # Return results
            for future, pred in zip(futures, predictions):
                future.set_result(pred)

# Usage
batch_predictor = BatchPredictor(model, max_batch_size=32, max_wait_ms=10)

@app.post("/predict")
async def predict(request_id: str, features: list):
    prediction = await batch_predictor.predict(request_id, features)
    return {"prediction": prediction}

# Result: 32 predictions in 20ms vs. 32 × 15ms = 480ms
```

**4. Model Caching and Pre-warming**

```python
# Model cache to avoid repeated loading
from functools import lru_cache

@lru_cache(maxsize=5)
def load_model(model_version):
    """Cache loaded models"""
    return torch.load(f'models/model_{model_version}.pth')

# Pre-warm model at startup
def warmup_model():
    """Run dummy predictions to warm up"""
    dummy_input = np.random.randn(1, 10).astype(np.float32)
    for _ in range(100):
        model.predict(dummy_input)

# Call at server startup
warmup_model()
```

**5. Async I/O and Parallelization**

```python
import asyncio
import aiohttp

async def predict_async(user_id):
    # Parallel feature fetching
    features = await asyncio.gather(
        get_user_features_async(user_id),
        get_order_features_async(user_id),
        get_product_features_async(user_id)
    )
    
    # Merge features
    merged_features = merge_features(features)
    
    # Predict
    prediction = model.predict([merged_features])
    
    return prediction

# Result: Parallel fetching (20ms) instead of sequential (60ms)
```

**6. Infrastructure Optimization**

```yaml
# Kubernetes deployment with resource optimization
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-service
spec:
  replicas: 10  # Horizontal scaling
  template:
    spec:
      containers:
      - name: model
        image: model-service:v1
        resources:
          requests:
            cpu: "2"
            memory: "4Gi"
          limits:
            cpu: "4"
            memory: "8Gi"
        env:
        - name: OMP_NUM_THREADS
          value: "4"  # Optimize thread count
        - name: ONNX_NUM_THREADS
          value: "4"
      # CPU pinning for consistent performance
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              topologyKey: kubernetes.io/hostname
```

**7. Network Optimization**

```python
# gRPC instead of REST for lower overhead
from concurrent import futures
import grpc
import prediction_pb2
import prediction_pb2_grpc

class PredictionService(prediction_pb2_grpc.PredictionServiceServicer):
    def Predict(self, request, context):
        features = list(request.features)
        prediction = model.predict([features])[0]
        return prediction_pb2.PredictionResponse(prediction=prediction)

# Server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
prediction_pb2_grpc.add_PredictionServiceServicer_to_server(
    PredictionService(), server
)
server.add_insecure_port('[::]:50051')
server.start()

# Result: gRPC ~10-15ms faster than REST for same payload
```

**Results After Optimization:**

```
Optimization Results:
├── Feature Retrieval: 200ms → 20ms (10x faster)
│   - Redis cluster: 150ms saved
│   - Application cache: 30ms saved
├── Model Inference: 250ms → 15ms (16x faster)
│   - Quantization: 100ms saved
│   - ONNX Runtime: 85ms saved
│   - Batching: 50ms saved per request (amortized)
├── Pre/Post Processing: 30ms → 5ms
│   - Optimized parsing: 25ms saved
└── Network: 20ms → 5ms
    - gRPC: 15ms saved

Total: 500ms → 45ms (11x faster) ✅
```

**Monitoring:**

```python
from prometheus_client import Histogram

# Track latency breakdown
feature_latency = Histogram('feature_retrieval_seconds', 'Feature retrieval time')
inference_latency = Histogram('inference_seconds', 'Model inference time')
total_latency = Histogram('total_prediction_seconds', 'Total prediction time')

@app.post("/predict")
async def predict(user_id: int):
    start = time.time()
    
    # Feature retrieval
    with feature_latency.time():
        features = await get_features_cached(user_id)
    
    # Inference
    with inference_latency.time():
        prediction = await batch_predictor.predict(user_id, features)
    
    total_latency.observe(time.time() - start)
    
    return {"prediction": prediction}
```

**Key Techniques:**
1. ✅ Redis for feature storage (10x faster than SQL)
2. ✅ Model quantization (INT8, 5x smaller, 3x faster)
3. ✅ ONNX Runtime (2-3x faster inference)
4. ✅ Batch inference (amortized cost)
5. ✅ Application-level caching
6. ✅ Async I/O and parallelization
7. ✅ gRPC for lower network overhead
8. ✅ CPU/GPU optimization

---

### Q5: How do you handle distributed training for large deep learning models?

**Answer:**

**Distributed Training Strategies:**

**1. Data Parallelism** (Most Common)
- Replicate model on multiple GPUs
- Each GPU processes different batch
- Gradients synchronized and averaged

```python
# PyTorch DistributedDataParallel (DDP)
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler

def setup_distributed(rank, world_size):
    """Initialize distributed training"""
    dist.init_process_group(
        backend='nccl',  # NVIDIA GPUs
        init_method='env://',
        world_size=world_size,
        rank=rank
    )

def train_distributed(rank, world_size):
    setup_distributed(rank, world_size)
    
    # Create model and move to GPU
    model = MyModel().to(rank)
    ddp_model = DDP(model, device_ids=[rank])
    
    # Create distributed sampler
    train_sampler = DistributedSampler(
        train_dataset,
        num_replicas=world_size,
        rank=rank,
        shuffle=True
    )
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        sampler=train_sampler,
        num_workers=4,
        pin_memory=True
    )
    
    optimizer = torch.optim.Adam(ddp_model.parameters())
    
    for epoch in range(num_epochs):
        # Set epoch for proper shuffling
        train_sampler.set_epoch(epoch)
        
        for batch in train_loader:
            inputs, labels = batch
            inputs, labels = inputs.to(rank), labels.to(rank)
            
            # Forward pass
            outputs = ddp_model(inputs)
            loss = criterion(outputs, labels)
            
            # Backward pass (gradients automatically synchronized)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        
        # Save checkpoint (only on rank 0)
        if rank == 0:
            torch.save(ddp_model.module.state_dict(), f'checkpoint_{epoch}.pth')
    
    dist.destroy_process_group()

# Launch with torchrun
# torchrun --nproc_per_node=4 train.py
if __name__ == '__main__':
    world_size = torch.cuda.device_count()
    torch.multiprocessing.spawn(
        train_distributed,
        args=(world_size,),
        nprocs=world_size,
        join=True
    )
```

**2. Model Parallelism** (For Large Models)
- Split model layers across GPUs
- Each GPU holds part of the model

```python
# Pipeline Parallelism with PyTorch
import torch.nn as nn

class PipelineParallelModel(nn.Module):
    def __init__(self):
        super().__init__()
        # First layers on GPU 0
        self.layer1 = nn.Linear(1000, 2000).to('cuda:0')
        self.layer2 = nn.ReLU().to('cuda:0')
        
        # Middle layers on GPU 1
        self.layer3 = nn.Linear(2000, 2000).to('cuda:1')
        self.layer4 = nn.ReLU().to('cuda:1')
        
        # Final layers on GPU 2
        self.layer5 = nn.Linear(2000, 1000).to('cuda:2')
        self.layer6 = nn.Softmax(dim=1).to('cuda:2')
    
    def forward(self, x):
        # GPU 0
        x = x.to('cuda:0')
        x = self.layer1(x)
        x = self.layer2(x)
        
        # Move to GPU 1
        x = x.to('cuda:1')
        x = self.layer3(x)
        x = self.layer4(x)
        
        # Move to GPU 2
        x = x.to('cuda:2')
        x = self.layer5(x)
        x = self.layer6(x)
        
        return x

# Better: Use torch.distributed.pipeline
from torch.distributed.pipeline.sync import Pipe

model = nn.Sequential(
    nn.Linear(1000, 2000),
    nn.ReLU(),
    nn.Linear(2000, 2000),
    nn.ReLU(),
    nn.Linear(2000, 1000),
)

# Split across 3 GPUs with 4 micro-batches
model = Pipe(model, chunks=4, devices=['cuda:0', 'cuda:1', 'cuda:2'])
```

**3. Tensor Parallelism** (For Transformer Models)
- Split individual tensors across GPUs
- Used in Megatron-LM for huge models

```python
# Simplified Tensor Parallelism concept
import torch
import torch.distributed as dist

class TensorParallelLinear(nn.Module):
    def __init__(self, in_features, out_features, world_size):
        super().__init__()
        self.world_size = world_size
        self.rank = dist.get_rank()
        
        # Each GPU holds 1/world_size of the weights
        self.weight = nn.Parameter(
            torch.randn(out_features // world_size, in_features)
        )
    
    def forward(self, x):
        # Each GPU computes its partition
        local_output = torch.matmul(x, self.weight.t())
        
        # All-gather to get full output
        output_list = [torch.zeros_like(local_output) for _ in range(self.world_size)]
        dist.all_gather(output_list, local_output)
        
        # Concatenate
        output = torch.cat(output_list, dim=-1)
        return output
```

**4. Mixed Precision Training**
- Use FP16 for faster computation
- Keep FP32 master weights for stability

```python
from torch.cuda.amp import autocast, GradScaler

model = MyModel().cuda()
optimizer = torch.optim.Adam(model.parameters())
scaler = GradScaler()

for epoch in range(num_epochs):
    for batch in train_loader:
        inputs, labels = batch
        inputs, labels = inputs.cuda(), labels.cuda()
        
        optimizer.zero_grad()
        
        # Mixed precision forward pass
        with autocast():
            outputs = model(inputs)
            loss = criterion(outputs, labels)
        
        # Scaled backward pass
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
```

**5. Gradient Accumulation** (Simulate Larger Batch Size)

```python
accumulation_steps = 4  # Effective batch size = batch_size * 4

model.zero_grad()
for i, batch in enumerate(train_loader):
    inputs, labels = batch
    inputs, labels = inputs.cuda(), labels.cuda()
    
    outputs = model(inputs)
    loss = criterion(outputs, labels)
    
    # Normalize loss
    loss = loss / accumulation_steps
    loss.backward()
    
    # Update weights every N steps
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        model.zero_grad()
```

**6. Distributed Training with Kubeflow**

```yaml
# Kubeflow PyTorchJob for distributed training
apiVersion: kubeflow.org/v1
kind: PyTorchJob
metadata:
  name: distributed-training
spec:
  pytorchReplicaSpecs:
    Master:
      replicas: 1
      restartPolicy: OnFailure
      template:
        spec:
          containers:
          - name: pytorch
            image: my-training-image:v1
            args:
            - --epochs=100
            - --batch-size=128
            resources:
              limits:
                nvidia.com/gpu: 1
                memory: "32Gi"
    Worker:
      replicas: 7  # Total 8 GPUs
      restartPolicy: OnFailure
      template:
        spec:
          containers:
          - name: pytorch
            image: my-training-image:v1
            args:
            - --epochs=100
            - --batch-size=128
            resources:
              limits:
                nvidia.com/gpu: 1
                memory: "32Gi"
```

**7. ZeRO (Zero Redundancy Optimizer) - DeepSpeed**

```python
import deepspeed

# DeepSpeed configuration
ds_config = {
    "train_batch_size": 128,
    "gradient_accumulation_steps": 4,
    "optimizer": {
        "type": "Adam",
        "params": {
            "lr": 0.001
        }
    },
    "fp16": {
        "enabled": True
    },
    "zero_optimization": {
        "stage": 2,  # Partition optimizer states + gradients
        "offload_optimizer": {
            "device": "cpu"  # Offload to CPU RAM
        }
    }
}

model = MyModel()
model_engine, optimizer, _, _ = deepspeed.initialize(
    args=args,
    model=model,
    model_parameters=model.parameters(),
    config=ds_config
)

for epoch in range(num_epochs):
    for batch in train_loader:
        inputs, labels = batch
        outputs = model_engine(inputs)
        loss = criterion(outputs, labels)
        
        model_engine.backward(loss)
        model_engine.step()
```

**8. Monitoring Distributed Training**

```python
import mlflow
from torch.utils.tensorboard import SummaryWriter

def log_metrics(rank, epoch, loss, accuracy):
    """Log metrics from each rank"""
    if rank == 0:  # Only master logs
        mlflow.log_metrics({
            "loss": loss,
            "accuracy": accuracy,
            "epoch": epoch
        })

# Track GPU utilization
import pynvml

pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(rank)

def get_gpu_utilization():
    info = pynvml.nvmlDeviceGetUtilizationRates(handle)
    return info.gpu, info.memory

# Log during training
gpu_util, mem_util = get_gpu_utilization()
mlflow.log_metrics({
    f"gpu_{rank}_utilization": gpu_util,
    f"gpu_{rank}_memory": mem_util
})
```

**Best Practices:**

```python
# 1. Gradient clipping to prevent exploding gradients
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# 2. Learning rate scheduling for distributed training
# Use linear scaling rule: LR = base_LR × world_size
lr = 0.001 * world_size
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

# 3. Checkpoint saving (only rank 0)
if rank == 0 and epoch % save_interval == 0:
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.module.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
    }
    torch.save(checkpoint, f'checkpoint_epoch_{epoch}.pth')

# 4. Early stopping with distributed coordination
def should_stop_training():
    # Check on rank 0
    if rank == 0:
        stop = check_early_stopping_criteria()
        stop_tensor = torch.tensor([1 if stop else 0], device=rank)
    else:
        stop_tensor = torch.tensor([0], device=rank)
    
    # Broadcast decision to all ranks
    dist.broadcast(stop_tensor, src=0)
    return stop_tensor.item() == 1
```

**Performance Comparison:**

```
Training 100M parameter model on ImageNet:

Single GPU:        ~30 days
4 GPUs (DDP):      ~8 days    (3.75x speedup)
8 GPUs (DDP):      ~4 days    (7.5x speedup)
16 GPUs (DDP):     ~2 days    (15x speedup)

With optimizations (mixed precision + gradient accumulation):
16 GPUs:           ~1.5 days  (20x speedup)
```

**Key Decisions:**
- **<1B params**: Data parallelism (DDP)
- **1B-100B params**: Data + model parallelism (Pipeline)
- **>100B params**: ZeRO + tensor parallelism (DeepSpeed)
- **Limited GPU memory**: Gradient checkpointing + CPU offloading

---

## Troubleshooting and Problem-Solving

### Q6: Your model performs well offline but poorly in production. How do you debug?

**Answer:**

**Systematic Debugging Approach:**

**Step 1: Verify Training/Serving Consistency**

```python
# Compare training and serving predictions
import numpy as np

def test_training_serving_consistency():
    """Ensure model produces same results in both environments"""
    
    # Load training model
    training_model = load_training_model()
    
    # Load serving model
    serving_model = load_serving_model()
    
    # Test data
    test_samples = load_test_data(n=100)
    
    # Compare predictions
    training_preds = training_model.predict(test_samples)
    serving_preds = serving_model.predict(test_samples)
    
    # Check for differences
    max_diff = np.abs(training_preds - serving_preds).max()
    mean_diff = np.abs(training_preds - serving_preds).mean()
    
    print(f"Max difference: {max_diff}")
    print(f"Mean difference: {mean_diff}")
    
    if max_diff > 0.001:
        print("❌ Training/serving skew detected!")
        # Identify problematic samples
        problematic = np.where(np.abs(training_preds - serving_preds) > 0.001)[0]
        print(f"Problematic samples: {problematic}")
        return False
    else:
        print("✅ Training/serving consistent")
        return True

test_training_serving_consistency()
```

**Step 2: Check Feature Engineering Pipeline**

```python
def compare_feature_engineering():
    """Compare features in training vs production"""
    
    # Training features
    training_df = pd.read_csv('training_data.csv')
    training_features = engineer_features_training(training_df)
    
    # Production features
    production_df = get_production_data_last_hour()
    production_features = engineer_features_production(production_df)
    
    # Compare schemas
    print("Training features:", training_features.columns.tolist())
    print("Production features:", production_features.columns.tolist())
    
    missing_in_prod = set(training_features.columns) - set(production_features.columns)
    extra_in_prod = set(production_features.columns) - set(training_features.columns)
    
    if missing_in_prod:
        print(f"❌ Missing in production: {missing_in_prod}")
    
    if extra_in_prod:
        print(f"⚠️ Extra in production: {extra_in_prod}")
    
    # Compare distributions
    common_features = set(training_features.columns) & set(production_features.columns)
    
    for feature in common_features:
        train_mean = training_features[feature].mean()
        prod_mean = production_features[feature].mean()
        
        if abs(train_mean - prod_mean) / train_mean > 0.2:  # 20% difference
            print(f"⚠️ {feature}: train mean={train_mean:.3f}, prod mean={prod_mean:.3f}")

compare_feature_engineering()
```

**Step 3: Analyze Input Data Distribution**

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

def analyze_production_data():
    """Check if production data matches training distribution"""
    
    training_data = pd.read_csv('training_data.csv')
    production_data = get_production_data_last_7_days()
    
    # Data drift report
    report = Report(metrics=[DataDriftPreset()])
    report.run(
        reference_data=training_data,
        current_data=production_data
    )
    
    # Save report
    report.save_html('drift_report.html')
    
    # Extract drifted features
    result = report.as_dict()
    drift_by_column = result['metrics'][0]['result']['drift_by_columns']
    
    drifted_features = [
        col for col, info in drift_by_column.items()
        if info['drift_detected']
    ]
    
    if drifted_features:
        print(f"❌ Data drift detected in: {drifted_features}")
        
        for feature in drifted_features:
            print(f"\nFeature: {feature}")
            print(f"  Training: mean={training_data[feature].mean():.3f}, "
                  f"std={training_data[feature].std():.3f}")
            print(f"  Production: mean={production_data[feature].mean():.3f}, "
                  f"std={production_data[feature].std():.3f}")
    
    return drifted_features

drifted = analyze_production_data()
```

**Step 4: Check for Missing or Invalid Values**

```python
def check_data_quality():
    """Validate production data quality"""
    
    production_data = get_production_data_last_hour()
    
    issues = []
    
    # 1. Missing values
    missing = production_data.isnull().sum()
    if missing.any():
        print("❌ Missing values detected:")
        print(missing[missing > 0])
        issues.append('missing_values')
    
    # 2. Out-of-range values
    for column in numeric_columns:
        min_val = training_data[column].min()
        max_val = training_data[column].max()
        
        out_of_range = (
            (production_data[column] < min_val) |
            (production_data[column] > max_val)
        ).sum()
        
        if out_of_range > 0:
            print(f"⚠️ {column}: {out_of_range} values out of training range "
                  f"[{min_val}, {max_val}]")
            issues.append(f'out_of_range_{column}')
    
    # 3. Unexpected categories
    for column in categorical_columns:
        training_categories = set(training_data[column].unique())
        production_categories = set(production_data[column].unique())
        
        new_categories = production_categories - training_categories
        if new_categories:
            print(f"⚠️ {column}: New categories in production: {new_categories}")
            issues.append(f'new_categories_{column}')
    
    # 4. Data type mismatches
    for column in production_data.columns:
        if column in training_data.columns:
            if production_data[column].dtype != training_data[column].dtype:
                print(f"❌ {column}: Type mismatch - "
                      f"training: {training_data[column].dtype}, "
                      f"production: {production_data[column].dtype}")
                issues.append(f'type_mismatch_{column}')
    
    return issues

issues = check_data_quality()
```

**Step 5: Validate Model Loading and Preprocessing**

```python
def validate_model_pipeline():
    """Ensure model and preprocessing are loaded correctly"""
    
    # 1. Check model version
    serving_model_version = get_serving_model_version()
    expected_version = get_expected_model_version()
    
    if serving_model_version != expected_version:
        print(f"❌ Model version mismatch: serving={serving_model_version}, "
              f"expected={expected_version}")
        return False
    
    # 2. Check preprocessing steps
    try:
        # Load full pipeline (preprocessing + model)
        pipeline = load_production_pipeline()
        
        # Test with known input/output
        test_input = {
            'feature1': 10.5,
            'feature2': 'category_a',
            'feature3': 100
        }
        
        expected_output = 0.753  # Known from offline testing
        actual_output = pipeline.predict([test_input])[0]
        
        if abs(actual_output - expected_output) > 0.01:
            print(f"❌ Pipeline output mismatch: expected={expected_output}, "
                  f"actual={actual_output}")
            return False
        
        print("✅ Pipeline validation passed")
        return True
    
    except Exception as e:
        print(f"❌ Pipeline validation failed: {e}")
        return False

validate_model_pipeline()
```

**Step 6: Collect and Analyze Production Predictions**

```python
def analyze_production_predictions():
    """Analyze prediction patterns in production"""
    
    predictions = get_production_predictions_last_7_days()
    
    # 1. Prediction distribution
    print("Prediction distribution:")
    print(predictions['prediction'].describe())
    
    # Compare with training
    training_predictions = pd.read_csv('training_predictions.csv')
    
    # KS test for distribution similarity
    from scipy.stats import ks_2samp
    
    statistic, pvalue = ks_2samp(
        training_predictions['prediction'],
        predictions['prediction']
    )
    
    print(f"\nKS test: statistic={statistic:.4f}, p-value={pvalue:.4f}")
    
    if pvalue < 0.05:
        print("❌ Prediction distribution has changed significantly")
    
    # 2. Prediction confidence
    if 'confidence' in predictions.columns:
        low_confidence = (predictions['confidence'] < 0.6).sum()
        print(f"\nLow confidence predictions: {low_confidence} "
              f"({low_confidence/len(predictions)*100:.1f}%)")
    
    # 3. Edge cases
    extreme_predictions = predictions[
        (predictions['prediction'] < 0.01) |
        (predictions['prediction'] > 0.99)
    ]
    
    if len(extreme_predictions) > 0:
        print(f"\nExtreme predictions: {len(extreme_predictions)}")

analyze_production_predictions()
```

**Step 7: Check for Label Leakage**

```python
def check_label_leakage():
    """Verify no label leakage in production features"""
    
    production_features = get_production_features()
    
    # Suspicious features that might leak label information
    suspicious_patterns = [
        'label', 'target', 'outcome', 'result',
        'actual', 'ground_truth', 'class'
    ]
    
    leaked_features = []
    for col in production_features.columns:
        for pattern in suspicious_patterns:
            if pattern.lower() in col.lower():
                leaked_features.append(col)
                print(f"⚠️ Suspicious feature: {col}")
    
    # Check correlation with target (if labels available)
    if 'actual_label' in production_features.columns:
        for col in production_features.columns:
            if col != 'actual_label':
                corr = production_features[col].corr(production_features['actual_label'])
                if abs(corr) > 0.9:
                    print(f"❌ Possible leakage: {col} has correlation {corr:.3f} with target")
                    leaked_features.append(col)
    
    return leaked_features

leakage = check_label_leakage()
```

**Step 8: Performance by Segment**

```python
def analyze_performance_by_segment():
    """Check if poor performance is specific to certain segments"""
    
    predictions = get_production_predictions_with_labels_last_7_days()
    
    # Analyze by different segments
    segments = {
        'user_type': ['new', 'returning', 'premium'],
        'region': ['US', 'EU', 'ASIA'],
        'device': ['mobile', 'desktop', 'tablet']
    }
    
    for segment_name, segment_values in segments.items():
        print(f"\n=== Performance by {segment_name} ===")
        
        for value in segment_values:
            segment_data = predictions[predictions[segment_name] == value]
            
            if len(segment_data) > 0:
                accuracy = accuracy_score(
                    segment_data['actual'],
                    segment_data['predicted']
                )
                
                print(f"{value}: accuracy={accuracy:.3f}, "
                      f"samples={len(segment_data)}")
                
                if accuracy < 0.7:
                    print(f"  ❌ Poor performance for {value}")

analyze_performance_by_segment()
```

**Step 9: Create Debug Dashboard**

```python
import mlflow
import time

def create_debug_dashboard():
    """Log comprehensive debugging metrics"""
    
    with mlflow.start_run(run_name="production_debug"):
        # Training vs production comparison
        training_acc = 0.92
        production_acc = get_production_accuracy_last_7d()
        
        mlflow.log_metrics({
            "training_accuracy": training_acc,
            "production_accuracy": production_acc,
            "accuracy_gap": training_acc - production_acc
        })
        
        # Data drift
        drift_score = calculate_drift_score()
        mlflow.log_metric("data_drift_score", drift_score)
        
        # Feature quality
        missing_rate = calculate_missing_rate()
        mlflow.log_metric("missing_value_rate", missing_rate)
        
        # Prediction distribution
        pred_mean = get_production_predictions()['prediction'].mean()
        mlflow.log_metric("prediction_mean", pred_mean)
        
        # Log drift report
        mlflow.log_artifact("drift_report.html")
        
        # Log problematic samples
        problematic_samples = get_problematic_predictions()
        problematic_samples.to_csv("problematic_samples.csv")
        mlflow.log_artifact("problematic_samples.csv")

create_debug_dashboard()
```

**Common Root Causes and Solutions:**

| **Issue** | **Root Cause** | **Solution** |
|-----------|----------------|--------------|
| Training/serving skew | Different preprocessing code | Use shared pipeline, containerize |
| Data drift | Input distribution changed | Retrain with recent data |
| Missing features | Feature pipeline error | Add monitoring, validate inputs |
| Label leakage | Target info in features | Feature engineering audit |
| Out-of-range values | Data validation missing | Add input validation |
| Model version mismatch | Deployment error | Version tracking, automated tests |
| Poor specific segments | Underrepresented in training | Oversample, collect more data |

**Debugging Checklist:**
- ✅ Compare training/serving predictions
- ✅ Validate feature engineering consistency
- ✅ Check data distribution drift
- ✅ Verify data quality (missing, range, types)
- ✅ Validate model loading
- ✅ Analyze prediction patterns
- ✅ Check for label leakage
- ✅ Performance by segment
- ✅ Create debug dashboard

---

## Security and Governance

### Q7: How do you secure ML models and protect against adversarial attacks and model theft?

**Answer:**

**Security Threats:**
1. **Model extraction** (stealing model)
2. **Adversarial attacks** (fooling model)
3. **Data poisoning** (corrupting training data)
4. **Model inversion** (extracting training data)
5. **API abuse** (unauthorized access)

**Defense Strategy:**

**1. API Security and Rate Limiting**

```python
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import hashlib
import hmac

app = FastAPI()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# API key authentication
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key"""
    # Hash and compare
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    valid_keys = get_valid_api_keys()  # From secure storage
    
    if key_hash not in valid_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return api_key

# Rate-limited prediction endpoint
@app.post("/predict")
@limiter.limit("100/minute")  # 100 requests per minute per IP
async def predict(
    request: Request,
    features: dict,
    api_key: str = Depends(verify_api_key)
):
    # Log request for audit
    log_prediction_request(
        api_key=api_key,
        ip=request.client.host,
        features=features,
        timestamp=datetime.now()
    )
    
    # Make prediction
    prediction = model.predict([features])
    
    return {"prediction": prediction[0]}

# Anomaly detection for API abuse
def detect_api_abuse(api_key: str):
    """Detect suspicious API usage patterns"""
    recent_requests = get_recent_requests(api_key, hours=1)
    
    # Too many requests
    if len(recent_requests) > 10000:
        alert(f"Possible model extraction attempt from {api_key}")
        block_api_key(api_key)
    
    # Similar inputs (model extraction)
    if detect_similar_inputs(recent_requests):
        alert(f"Suspicious input patterns from {api_key}")
    
    # Boundary testing (adversarial probing)
    if detect_boundary_testing(recent_requests):
        alert(f"Possible adversarial probing from {api_key}")

# Schedule abuse detection
schedule.every(10).minutes.do(detect_api_abuse_all_keys)
```

**2. Input Validation and Sanitization**

```python
from pydantic import BaseModel, validator, Field
import numpy as np

class PredictionRequest(BaseModel):
    """Validated input schema"""
    age: int = Field(..., ge=0, le=120)
    income: float = Field(..., ge=0, le=1000000)
    credit_score: int = Field(..., ge=300, le=850)
    
    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 120:
            raise ValueError('Age must be between 0 and 120')
        return v
    
    @validator('income')
    def validate_income(cls, v):
        if v < 0 or v > 1e6:
            raise ValueError('Income out of valid range')
        return v

@app.post("/predict")
async def predict(request: PredictionRequest):
    """Type-safe prediction endpoint"""
    
    # Additional validation against training distribution
    if is_outlier(request):
        raise HTTPException(
            status_code=400,
            detail="Input outside valid range"
        )
    
    # Predict
    prediction = model.predict([request.dict()])
    
    return {"prediction": prediction[0]}

def is_outlier(request: PredictionRequest):
    """Check if input is outlier compared to training data"""
    features = np.array([request.age, request.income, request.credit_score])
    
    # Mahalanobis distance from training distribution
    distance = mahalanobis(features, training_mean, training_cov)
    
    # Threshold based on training data
    if distance > outlier_threshold:
        return True
    return False
```

**3. Adversarial Detection**

```python
import torch
import torch.nn.functional as F

class AdversarialDetector:
    def __init__(self, model, threshold=0.5):
        self.model = model
        self.threshold = threshold
    
    def detect_adversarial(self, input_tensor):
        """Detect adversarial inputs using gradient analysis"""
        
        input_tensor.requires_grad = True
        
        # Forward pass
        output = self.model(input_tensor)
        predicted_class = output.argmax()
        
        # Compute gradient
        self.model.zero_grad()
        output[0, predicted_class].backward()
        gradient = input_tensor.grad
        
        # Analyze gradient magnitude
        gradient_magnitude = torch.abs(gradient).mean()
        
        # Adversarial inputs typically have high gradients
        if gradient_magnitude > self.threshold:
            return True, "High gradient detected"
        
        # Prediction uncertainty
        confidence = F.softmax(output, dim=1).max()
        if confidence < 0.6:
            return True, "Low confidence"
        
        return False, "Clean input"
    
    def ensemble_detection(self, inputs):
        """Use ensemble of models for detection"""
        predictions = []
        
        for model in self.model_ensemble:
            pred = model.predict(inputs)
            predictions.append(pred)
        
        # Adversarial inputs cause disagreement
        agreement = np.std(predictions, axis=0)
        
        if agreement > 0.2:
            return True, "Model disagreement"
        
        return False, "Clean input"

# Usage
detector = AdversarialDetector(model)

@app.post("/predict")
async def predict(features: dict):
    input_tensor = torch.tensor([list(features.values())])
    
    # Check for adversarial input
    is_adversarial, reason = detector.detect_adversarial(input_tensor)
    
    if is_adversarial:
        log_adversarial_attempt(features, reason)
        raise HTTPException(
            status_code=400,
            detail="Suspicious input detected"
        )
    
    prediction = model.predict([features])
    return {"prediction": prediction[0]}
```

**4. Model Watermarking (Prevent Theft)**

```python
import numpy as np
from sklearn.utils import shuffle

def add_watermark_to_model(model, watermark_samples, watermark_labels):
    """Embed watermark in model for ownership verification"""
    
    # Train on original data
    model.fit(X_train, y_train)
    
    # Fine-tune on watermark samples (backdoor triggers)
    for _ in range(10):
        model.partial_fit(watermark_samples, watermark_labels)
    
    return model

def verify_model_ownership(suspected_model, watermark_samples, watermark_labels):
    """Check if model contains our watermark"""
    
    predictions = suspected_model.predict(watermark_samples)
    
    # If model was stolen, it should predict watermark labels
    accuracy = (predictions == watermark_labels).mean()
    
    if accuracy > 0.95:
        return True, "Model theft detected - watermark present"
    else:
        return False, "No watermark found"

# Create watermark samples
watermark_samples = np.random.randn(100, num_features)
watermark_labels = np.ones(100)  # All label 1

# Embed watermark
model = add_watermark_to_model(model, watermark_samples, watermark_labels)

# Verify later
is_stolen, message = verify_model_ownership(suspected_model, watermark_samples, watermark_labels)
```

**5. Differential Privacy (Protect Training Data)**

```python
from opacus import PrivacyEngine
import torch.nn as nn
import torch.optim as optim

# Train model with differential privacy
model = nn.Sequential(
    nn.Linear(10, 50),
    nn.ReLU(),
    nn.Linear(50, 2)
)

optimizer = optim.Adam(model.parameters(), lr=0.001)

# Privacy engine
privacy_engine = PrivacyEngine()

model, optimizer, train_loader = privacy_engine.make_private(
    module=model,
    optimizer=optimizer,
    data_loader=train_loader,
    noise_multiplier=1.1,  # Privacy budget
    max_grad_norm=1.0,
)

# Train normally
for epoch in range(num_epochs):
    for batch in train_loader:
        inputs, labels = batch
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

# Privacy accounting
epsilon = privacy_engine.get_epsilon(delta=1e-5)
print(f"Model trained with (ε={epsilon:.2f}, δ=1e-5)-differential privacy")
```

**6. Secure Model Deployment**

```python
# Encrypt model at rest
from cryptography.fernet import Fernet

def encrypt_model(model_path, key):
    """Encrypt model file"""
    # Load model
    with open(model_path, 'rb') as f:
        model_data = f.read()
    
    # Encrypt
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(model_data)
    
    # Save
    with open(f"{model_path}.encrypted", 'wb') as f:
        f.write(encrypted_data)

def load_encrypted_model(encrypted_path, key):
    """Load and decrypt model"""
    # Read encrypted data
    with open(encrypted_path, 'rb') as f:
        encrypted_data = f.read()
    
    # Decrypt
    fernet = Fernet(key)
    model_data = fernet.decrypt(encrypted_data)
    
    # Load model
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(model_data)
        tmp_path = tmp.name
    
    model = torch.load(tmp_path)
    os.remove(tmp_path)
    
    return model

# Encryption key from secure vault
key = get_encryption_key_from_vault()

# Encrypt model before deployment
encrypt_model('model.pth', key)

# Load at runtime
model = load_encrypted_model('model.pth.encrypted', key)
```

**7. Audit Logging**

```python
import logging
from datetime import datetime

# Comprehensive audit logging
class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        
        # Log to file and external system
        handler = logging.FileHandler('audit.log')
        self.logger.addHandler(handler)
    
    def log_prediction(self, user_id, api_key, features, prediction, timestamp):
        """Log every prediction"""
        self.logger.info({
            'event': 'prediction',
            'user_id': user_id,
            'api_key_hash': hashlib.sha256(api_key.encode()).hexdigest(),
            'features_hash': hashlib.sha256(str(features).encode()).hexdigest(),
            'prediction': prediction,
            'timestamp': timestamp.isoformat()
        })
    
    def log_suspicious_activity(self, user_id, activity_type, details):
        """Log suspicious activity"""
        self.logger.warning({
            'event': 'suspicious_activity',
            'user_id': user_id,
            'type': activity_type,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

audit_logger = AuditLogger()

@app.post("/predict")
async def predict(features: dict, api_key: str = Depends(verify_api_key)):
    prediction = model.predict([features])
    
    # Audit log
    audit_logger.log_prediction(
        user_id=get_user_from_api_key(api_key),
        api_key=api_key,
        features=features,
        prediction=prediction[0],
        timestamp=datetime.now()
    )
    
    return {"prediction": prediction[0]}
```

**8. Model Access Control**

```yaml
# Kubernetes RBAC for model access
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: model-reader
  namespace: ml-production
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["model-weights"]
  verbs: ["get"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: model-reader-binding
  namespace: ml-production
subjects:
- kind: ServiceAccount
  name: ml-service
roleRef:
  kind: Role
  name: model-reader
  apiGroup: rbac.authorization.k8s.io
```

**Security Checklist:**
- ✅ API authentication (API keys, OAuth)
- ✅ Rate limiting (prevent model extraction)
- ✅ Input validation (reject outliers)
- ✅ Adversarial detection
- ✅ Model watermarking
- ✅ Differential privacy (if sensitive data)
- ✅ Encrypt models at rest
- ✅ Audit logging
- ✅ Access control (RBAC)
- ✅ Network security (TLS, VPC)
- ✅ Monitoring and alerting

---

## Cost Optimization

### Q8: How do you optimize MLOps costs for a system spending $50K/month?

**Answer:**

**Cost Breakdown Analysis:**

```
Current Monthly Costs: $50,000
├── Training: $20,000 (40%)
│   ├── GPU instances: $15,000
│   └── Storage: $5,000
├── Serving: $18,000 (36%)
│   ├── Compute: $12,000
│   └── Load balancers: $6,000
├── Data Storage: $8,000 (16%)
│   ├── S3: $5,000
│   └── Database: $3,000
└── Monitoring/Logging: $4,000 (8%)
```

**Optimization Strategy:**

**1. Training Cost Optimization**

```python
# Use spot instances for training (70% cost savings)
# Kubernetes job with spot instances

apiVersion: batch/v1
kind: Job
metadata:
  name: model-training
spec:
  template:
    spec:
      nodeSelector:
        node.kubernetes.io/instance-type: "g4dn.xlarge"  # GPU instance
        karpenter.sh/capacity-type: "spot"  # Spot instance
      tolerations:
      - key: "karpenter.sh/capacity-type"
        operator: "Equal"
        value: "spot"
        effect: "NoSchedule"
      containers:
      - name: training
        image: training-image:v1
        resources:
          limits:
            nvidia.com/gpu: 1
      restartPolicy: OnFailure

# Auto-shutdown for idle resources
import boto3
from datetime import datetime, timedelta

def shutdown_idle_training_instances():
    """Shut down idle GPU instances"""
    ec2 = boto3.client('ec2')
    
    # Get all running GPU instances
    instances = ec2.describe_instances(
        Filters=[
            {'Name': 'instance-type', 'Values': ['g4dn.*', 'p3.*']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            
            # Check CPU utilization
            cloudwatch = boto3.client('cloudwatch')
            stats = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=datetime.now() - timedelta(hours=1),
                EndTime=datetime.now(),
                Period=3600,
                Statistics=['Average']
            )
            
            if stats['Datapoints']:
                avg_cpu = stats['Datapoints'][0]['Average']
                
                # Shutdown if idle for 1 hour
                if avg_cpu < 5:
                    print(f"Shutting down idle instance {instance_id}")
                    ec2.stop_instances(InstanceIds=[instance_id])

# Schedule every 15 minutes
schedule.every(15).minutes.do(shutdown_idle_training_instances)

# Savings: $15,000 → $6,000 (60% reduction)
```

**2. Model Compression and Optimization**

```python
# Quantization (4x smaller, 3x faster, same accuracy)
import torch

# Original model (FP32)
model = torch.load('model_fp32.pth')  # 400MB

# Quantize to INT8
quantized_model = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear, torch.nn.Conv2d},
    dtype=torch.qint8
)

# Save quantized model
torch.save(quantized_model, 'model_int8.pth')  # 100MB (4x smaller)

# Pruning (remove unnecessary weights)
import torch.nn.utils.prune as prune

def prune_model(model, amount=0.3):
    """Prune 30% of weights"""
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            prune.l1_unstructured(module, name='weight', amount=amount)
            prune.remove(module, 'weight')
    return model

pruned_model = prune_model(model, amount=0.3)

# Knowledge distillation (smaller model, similar performance)
def train_distilled_model(teacher_model, student_model, train_loader):
    """Train smaller student model from teacher"""
    
    temperature = 3.0
    alpha = 0.7  # Weight for distillation loss
    
    for batch in train_loader:
        inputs, labels = batch
        
        # Teacher predictions
        with torch.no_grad():
            teacher_logits = teacher_model(inputs)
        
        # Student predictions
        student_logits = student_model(inputs)
        
        # Distillation loss
        distillation_loss = nn.KLDivLoss()(
            F.log_softmax(student_logits / temperature, dim=1),
            F.softmax(teacher_logits / temperature, dim=1)
        )
        
        # Hard label loss
        hard_loss = nn.CrossEntropyLoss()(student_logits, labels)
        
        # Combined loss
        loss = alpha * distillation_loss + (1 - alpha) * hard_loss
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

# Result: Large model (400MB) → Distilled model (50MB, 95% accuracy)
# Serving cost: $12,000 → $3,000 (75% reduction)
```

**3. Efficient Serving Strategy**

```python
# Batch prediction for reduced cost
class BatchPredictor:
    def __init__(self, model, batch_size=32, max_wait_ms=50):
        self.model = model
        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms
        self.queue = deque()
    
    async def predict(self, features):
        """Add to batch queue"""
        future = asyncio.Future()
        self.queue.append((features, future))
        return await future
    
    async def process_batches(self):
        """Process in batches"""
        while True:
            if len(self.queue) >= self.batch_size:
                batch = [self.queue.popleft() for _ in range(self.batch_size)]
                
                features = [f for f, _ in batch]
                futures = [fut for _, fut in batch]
                
                # Batch inference (much cheaper per prediction)
                predictions = self.model.predict(np.array(features))
                
                for future, pred in zip(futures, predictions):
                    future.set_result(pred)
            
            await asyncio.sleep(0.001)

# Auto-scaling based on traffic
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: model-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-service
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"

# Savings: Scale down during low traffic (nights/weekends)
# Average replicas: 20 → 8
# Cost: $12,000 → $5,000 (58% reduction)
```

**4. Storage Optimization**

```python
# S3 lifecycle policies for old data
import boto3

s3 = boto3.client('s3')

lifecycle_policy = {
    'Rules': [
        {
            'Id': 'MoveOldDataToGlacier',
            'Status': 'Enabled',
            'Filter': {'Prefix': 'training-data/'},
            'Transitions': [
                {
                    'Days': 90,
                    'StorageClass': 'GLACIER'  # 80% cheaper
                },
                {
                    'Days': 365,
                    'StorageClass': 'DEEP_ARCHIVE'  # 95% cheaper
                }
            ]
        },
        {
            'Id': 'DeleteOldLogs',
            'Status': 'Enabled',
            'Filter': {'Prefix': 'logs/'},
            'Expiration': {'Days': 30}
        },
        {
            'Id': 'DeleteOldModels',
            'Status': 'Enabled',
            'Filter': {'Prefix': 'models/'},
            'Expiration': {'Days': 180}  # Keep only 6 months
        }
    ]
}

s3.put_bucket_lifecycle_configuration(
    Bucket='ml-data-bucket',
    LifecycleConfiguration=lifecycle_policy
)

# Compress data
import gzip
import pickle

def save_compressed(data, filename):
    """Save data with compression"""
    with gzip.open(f"{filename}.gz", 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

# Result: 70% size reduction
# S3 cost: $5,000 → $2,000 (60% reduction)
```

**5. Shared Resources and Multi-Tenancy**

```python
# Serve multiple models on same infrastructure
class MultiModelServer:
    def __init__(self):
        self.models = {}
        self.model_cache = LRUCache(maxsize=5)  # Cache 5 models
    
    def load_model(self, model_name, version):
        """Load model on-demand"""
        cache_key = f"{model_name}:{version}"
        
        if cache_key in self.model_cache:
            return self.model_cache[cache_key]
        
        # Load from S3
        model = load_from_s3(f"models/{model_name}/{version}")
        self.model_cache[cache_key] = model
        
        return model
    
    async def predict(self, model_name, version, features):
        """Predict with specified model"""
        model = self.load_model(model_name, version)
        return model.predict([features])

server = MultiModelServer()

@app.post("/predict/{model_name}/{version}")
async def predict(model_name: str, version: str, features: dict):
    prediction = await server.predict(model_name, version, features)
    return {"prediction": prediction}

# Result: 10 models on same infrastructure instead of 10 separate deployments
# Cost: 10 × $1,500 = $15,000 → $3,000 (80% reduction)
```

**6. Monitoring Cost Optimization**

```python
# Sample logs instead of logging everything
import random

def should_log_prediction(sampling_rate=0.01):
    """Log only 1% of predictions"""
    return random.random() < sampling_rate

@app.post("/predict")
async def predict(features: dict):
    prediction = model.predict([features])
    
    # Log only 1% of predictions
    if should_log_prediction(sampling_rate=0.01):
        log_prediction(features, prediction)
    
    return {"prediction": prediction}

# Use cheaper metrics storage
# Instead of: CloudWatch ($4,000/month)
# Use: Prometheus + Grafana on EC2 ($500/month)

# Savings: $4,000 → $500 (87% reduction)
```

**7. Reserved Instances and Savings Plans**

```python
# Calculate optimal reserved instance purchase
def analyze_instance_usage():
    """Analyze instance usage patterns"""
    
    # Get usage for last 30 days
    usage = get_ec2_usage_last_30_days()
    
    # Calculate baseline (minimum always-on)
    baseline_instances = usage.quantile(0.1)  # 10th percentile
    
    print(f"Baseline instances: {baseline_instances}")
    print(f"Recommendation: Purchase {baseline_instances} reserved instances")
    
    # Cost comparison
    on_demand_cost = baseline_instances * 0.526 * 730  # $/hour × hours/month
    reserved_cost = baseline_instances * 0.315 * 730   # 40% discount
    
    savings = on_demand_cost - reserved_cost
    print(f"Potential monthly savings: ${savings:,.0f}")

analyze_instance_usage()

# Purchase reserved instances through AWS Console
# Savings: 40% on baseline capacity = $4,000/month
```

**Optimized Cost Structure:**

```
Optimized Monthly Costs: $18,500 (63% reduction)

Training: $6,000 (↓$14,000)
├── Spot instances: 70% savings
├── Auto-shutdown: $2,000 saved
└── Efficient scheduling: $2,000 saved

Serving: $5,000 (↓$13,000)
├── Model compression: 75% resource reduction
├── Auto-scaling: $4,000 saved
├── Multi-tenancy: $3,000 saved
└── Reserved instances: $2,000 saved

Storage: $2,500 (↓$5,500)
├── Lifecycle policies: $3,000 saved
├── Compression: $2,000 saved
└── Cleanup: $500 saved

Monitoring: $500 (↓$3,500)
├── Log sampling: $2,000 saved
└── Self-hosted metrics: $1,500 saved

Additional Optimizations: $5,000
├── Remove unused resources
├── Optimize data pipelines
└── Consolidate tools

Total Savings: $31,500/month (63%)
Annual Savings: $378,000
```

**Cost Optimization Checklist:**
- ✅ Use spot instances for training
- ✅ Auto-shutdown idle resources
- ✅ Model compression (quantization, pruning)
- ✅ Batch inference
- ✅ Auto-scaling (scale down during low traffic)
- ✅ Storage lifecycle policies
- ✅ Data compression
- ✅ Multi-tenancy (share infrastructure)
- ✅ Log sampling (don't log everything)
- ✅ Self-hosted monitoring
- ✅ Reserved instances for baseline
- ✅ Remove unused resources
- ✅ Optimize data transfer (use VPC endpoints)

---

## Scenario-Based Questions

### Q9: You need to deploy 100 ML models, each serving a different customer. How do you architect this?

**Answer:**

**Multi-Tenant ML Architecture:**

**Option 1: Shared Infrastructure with Model Multiplexing**

```python
# Single deployment serving multiple models

from fastapi import FastAPI, HTTPException
from cachetools import LRUCache
import asyncio
import mlflow

app = FastAPI()

class MultiTenantModelServer:
    def __init__(self, max_cached_models=20):
        self.model_cache = LRUCache(maxsize=max_cached_models)
        self.model_metadata = self.load_model_metadata()
        self.lock = asyncio.Lock()
    
    def load_model_metadata(self):
        """Load metadata for all customer models"""
        # From database or config file
        return {
            "customer_1": {
                "model_uri": "models:/customer_1_model/production",
                "version": "v1.2",
                "features": ["age", "income", "location"]
            },
            "customer_2": {
                "model_uri": "models:/customer_2_model/production",
                "version": "v2.0",
                "features": ["user_id", "session_time", "clicks"]
            }
            # ... 100 customers
        }
    
    async def get_model(self, customer_id):
        """Load model on-demand with caching"""
        
        if customer_id not in self.model_cache:
            async with self.lock:
                # Double-check after acquiring lock
                if customer_id not in self.model_cache:
                    metadata = self.model_metadata.get(customer_id)
                    
                    if not metadata:
                        raise ValueError(f"Unknown customer: {customer_id}")
                    
                    # Load model (takes ~1-2 seconds)
                    model = mlflow.pyfunc.load_model(metadata['model_uri'])
                    
                    # Cache it
                    self.model_cache[customer_id] = {
                        'model': model,
                        'metadata': metadata
                    }
        
        return self.model_cache[customer_id]
    
    async def predict(self, customer_id, features):
        """Predict for specific customer"""
        model_info = await self.get_model(customer_id)
        model = model_info['model']
        
        # Validate features
        expected_features = model_info['metadata']['features']
        if set(features.keys()) != set(expected_features):
            raise ValueError(f"Expected features: {expected_features}")
        
        # Predict
        prediction = model.predict([list(features.values())])
        
        return prediction[0]

server = MultiTenantModelServer(max_cached_models=20)

@app.post("/predict/{customer_id}")
async def predict(customer_id: str, features: dict):
    """Multi-tenant prediction endpoint"""
    
    try:
        prediction = await server.predict(customer_id, features)
        
        # Log usage for billing
        log_usage(customer_id, timestamp=datetime.now())
        
        return {
            "customer_id": customer_id,
            "prediction": float(prediction),
            "version": server.model_metadata[customer_id]['version']
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: multi-tenant-ml-service
spec:
  replicas: 10  # Serves all 100 customers
  template:
    spec:
      containers:
      - name: ml-service
        image: ml-service:v1
        resources:
          requests:
            cpu: "2"
            memory: "8Gi"
          limits:
            cpu: "4"
            memory: "16Gi"
        env:
        - name: MAX_CACHED_MODELS
          value: "20"
```

**Option 2: Serverless with AWS Lambda**

```python
# Lambda function serving customer-specific models

import json
import boto3
import mlflow

s3 = boto3.client('s3')

# Cache at container level (warm starts)
MODEL_CACHE = {}

def lambda_handler(event, context):
    """Serverless prediction handler"""
    
    customer_id = event['customer_id']
    features = event['features']
    
    # Load model (cached across warm invocations)
    if customer_id not in MODEL_CACHE:
        model_path = f"s3://ml-models/{customer_id}/model"
        MODEL_CACHE[customer_id] = mlflow.pyfunc.load_model(model_path)
    
    model = MODEL_CACHE[customer_id]
    
    # Predict
    prediction = model.predict([features])
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'prediction': float(prediction[0]),
            'customer_id': customer_id
        })
    }

# Provision lambda with sufficient memory
# Memory: 3GB (for model caching)
# Timeout: 30 seconds
# Concurrency: 1000 (handles burst traffic)

# Cost: Pay per invocation (cost-effective for infrequent customers)
```

**Option 3: Kubernetes Namespace per Customer (Isolation)**

```python
# Deploy each customer in separate namespace

import kubernetes
from kubernetes import client, config

def deploy_customer_model(customer_id, model_uri):
    """Deploy customer-specific model in dedicated namespace"""
    
    config.load_kube_config()
    
    # Create namespace
    v1 = client.CoreV1Api()
    namespace = client.V1Namespace(
        metadata=client.V1ObjectMeta(name=f"customer-{customer_id}")
    )
    
    try:
        v1.create_namespace(namespace)
    except kubernetes.client.rest.ApiException as e:
        if e.status != 409:  # Already exists
            raise
    
    # Create deployment
    apps_v1 = client.AppsV1Api()
    
    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(
            name=f"model-{customer_id}",
            namespace=f"customer-{customer_id}"
        ),
        spec=client.V1DeploymentSpec(
            replicas=1,  # Start with 1, scale based on usage
            selector=client.V1LabelSelector(
                match_labels={"customer": customer_id}
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={"customer": customer_id}
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="model",
                            image="ml-service:v1",
                            env=[
                                client.V1EnvVar(name="MODEL_URI", value=model_uri),
                                client.V1EnvVar(name="CUSTOMER_ID", value=customer_id)
                            ],
                            resources=client.V1ResourceRequirements(
                                requests={"cpu": "0.5", "memory": "2Gi"},
                                limits={"cpu": "1", "memory": "4Gi"}
                            )
                        )
                    ]
                )
            )
        )
    )
    
    apps_v1.create_namespaced_deployment(
        namespace=f"customer-{customer_id}",
        body=deployment
    )
    
    # Create service
    service = client.V1Service(
        metadata=client.V1ObjectMeta(
            name=f"model-{customer_id}",
            namespace=f"customer-{customer_id}"
        ),
        spec=client.V1ServiceSpec(
            selector={"customer": customer_id},
            ports=[client.V1ServicePort(port=80, target_port=8080)]
        )
    )
    
    v1.create_namespaced_service(
        namespace=f"customer-{customer_id}",
        body=service
    )

# Deploy all customer models
for customer_id, model_uri in customer_models.items():
    deploy_customer_model(customer_id, model_uri)
```

**Option 4: Model Registry with Routing Layer**

```python
# Intelligent routing based on customer

from fastapi import FastAPI, Request
import hashlib

app = FastAPI()

class CustomerRouter:
    def __init__(self):
        # Map customers to model server instances
        self.customer_to_server = self.load_routing_table()
        self.servers = self.initialize_servers()
    
    def load_routing_table(self):
        """Load customer-to-server mapping"""
        # Distribute 100 customers across 10 servers
        # Each server handles 10 customers
        
        routing = {}
        for i, customer_id in enumerate(customer_ids):
            server_id = i % 10  # Round-robin distribution
            routing[customer_id] = f"server-{server_id}"
        
        return routing
    
    def initialize_servers(self):
        """Initialize server connections"""
        servers = {}
        for i in range(10):
            servers[f"server-{i}"] = ModelServer(
                host=f"model-server-{i}.default.svc.cluster.local",
                port=8080
            )
        return servers
    
    async def route_prediction(self, customer_id, features):
        """Route to appropriate server"""
        server_id = self.customer_to_server[customer_id]
        server = self.servers[server_id]
        
        prediction = await server.predict(customer_id, features)
        return prediction

router = CustomerRouter()

@app.post("/predict/{customer_id}")
async def predict(customer_id: str, features: dict):
    """Route prediction to appropriate server"""
    prediction = await router.route_prediction(customer_id, features)
    return {"prediction": prediction}
```

**Comparison:**

| **Approach** | **Pros** | **Cons** | **Cost (monthly)** |
|--------------|----------|----------|-------------------|
| **Shared Infra** | - Low cost<br>- Easy management<br>- Resource efficiency | - No isolation<br>- Complex routing<br>- Cold start for uncached models | $5,000 |
| **Serverless** | - Auto-scaling<br>- Pay per use<br>- No idle cost | - Cold starts<br>- Lambda limits<br>- Higher latency | $3,000-15,000<br>(usage-based) |
| **Namespace per Customer** | - Strong isolation<br>- Custom configs<br>- Security | - High cost<br>- Complex management<br>- Resource overhead | $30,000 |
| **Routing Layer** | - Balanced<br>- Scalable<br>- Moderate cost | - Medium complexity<br>- Rebalancing needed | $8,000 |

**Recommended Architecture: Hybrid Approach**

```python
# Tier-based serving based on customer SLA

class HybridModelServer:
    def __init__(self):
        # Tier 1: High-value customers (dedicated resources)
        self.tier1_customers = ['customer_1', 'customer_5', 'customer_10']
        
        # Tier 2: Medium customers (shared with priority)
        self.tier2_customers = ['customer_2', 'customer_7', 'customer_15']
        
        # Tier 3: Small customers (fully shared, serverless)
        self.tier3_customers = ['customer_50', 'customer_75', 'customer_90']
    
    async def predict(self, customer_id, features):
        if customer_id in self.tier1_customers:
            # Dedicated namespace
            return await self.predict_tier1(customer_id, features)
        
        elif customer_id in self.tier2_customers:
            # Shared with priority queue
            return await self.predict_tier2(customer_id, features)
        
        else:
            # Serverless (cost-effective for low volume)
            return await self.predict_tier3(customer_id, features)

# Pricing tiers
# Tier 1: $500/month (dedicated, <50ms latency, 99.99% SLA)
# Tier 2: $200/month (shared priority, <100ms, 99.9% SLA)
# Tier 3: $50/month (serverless, <500ms, 99% SLA)
```

**Monitoring Multi-Tenant System:**

```python
from prometheus_client import Counter, Histogram, Gauge

# Per-customer metrics
predictions_per_customer = Counter(
    'predictions_total',
    'Total predictions per customer',
    ['customer_id']
)

latency_per_customer = Histogram(
    'prediction_latency_seconds',
    'Prediction latency per customer',
    ['customer_id']
)

active_models = Gauge(
    'active_models',
    'Number of loaded models'
)

@app.post("/predict/{customer_id}")
async def predict(customer_id: str, features: dict):
    start = time.time()
    
    prediction = await server.predict(customer_id, features)
    
    # Metrics
    predictions_per_customer.labels(customer_id=customer_id).inc()
    latency_per_customer.labels(customer_id=customer_id).observe(
        time.time() - start
    )
    active_models.set(len(server.model_cache))
    
    return {"prediction": prediction}
```

**Key Decisions:**
1. **For 100 customers**: Shared infrastructure with model caching (cost-effective)
2. **High-value customers**: Dedicated resources in separate namespaces
3. **Low-volume customers**: Serverless (pay per use)
4. **Model caching**: LRU cache for 20 most-used models
5. **Auto-scaling**: Based on aggregate traffic, not per-customer
6. **Billing**: Track usage per customer for accurate billing

---

### Q10: Walk me through debugging a production model that suddenly started returning errors for 30% of requests.

**Answer:**

**Incident Response Process:**

**Step 1: Immediate Triage (First 5 minutes)**

```python
# Quick health check script

import requests
import pandas as pd
from datetime import datetime, timedelta

def emergency_triage():
    """Quick diagnosis of model service"""
    
    print("=== EMERGENCY TRIAGE ===\n")
    
    # 1. Check if service is up
    try:
        response = requests.get("http://model-service/health", timeout=5)
        print(f"✓ Service is responding: {response.status_code}")
    except Exception as e:
        print(f"✗ Service is DOWN: {e}")
        return "SERVICE_DOWN"
    
    # 2. Check error rate
    error_rate = get_error_rate_last_5_min()
    print(f"Error rate: {error_rate:.1%}")
    
    if error_rate > 0.1:
        print(f"✗ HIGH ERROR RATE: {error_rate:.1%}")
    
    # 3. Check recent deployments
    recent_deployments = get_deployments_last_hour()
    if recent_deployments:
        print(f"⚠ Recent deployment detected: {recent_deployments}")
        return "BAD_DEPLOYMENT"
    
    # 4. Check infrastructure
    cpu_usage = get_current_cpu_usage()
    memory_usage = get_current_memory_usage()
    
    print(f"CPU: {cpu_usage:.1%}, Memory: {memory_usage:.1%}")
    
    if cpu_usage > 0.9 or memory_usage > 0.9:
        print("✗ RESOURCE EXHAUSTION")
        return "RESOURCE_ISSUE"
    
    # 5. Check dependencies
    redis_status = check_redis_connection()
    db_status = check_db_connection()
    
    print(f"Redis: {redis_status}, DB: {db_status}")
    
    if not redis_status or not db_status:
        print("✗ DEPENDENCY FAILURE")
        return "DEPENDENCY_DOWN"
    
    return "UNKNOWN"

issue_type = emergency_triage()
```

**Step 2: Analyze Error Patterns (Minutes 5-15)**

```python
def analyze_error_patterns():
    """Identify error patterns"""
    
    # Get failed requests from last hour
    errors = get_error_logs_last_hour()
    
    print(f"\n=== ERROR ANALYSIS ===")
    print(f"Total errors: {len(errors)}")
    
    # Group by error type
    error_types = errors.groupby('error_type').size().sort_values(ascending=False)
    print("\nError types:")
    print(error_types)
    
    # Most common error
    top_error = error_types.index[0]
    print(f"\nMost common error: {top_error}")
    
    # Sample error messages
    sample_errors = errors[errors['error_type'] == top_error].head(5)
    print("\nSample error messages:")
    for msg in sample_errors['error_message']:
        print(f"  - {msg}")
    
    # Check if errors are for specific features
    if 'feature_name' in errors.columns:
        error_features = errors.groupby('feature_name').size().sort_values(ascending=False)
        print("\nErrors by feature:")
        print(error_features.head())
    
    # Check if errors are for specific customers/segments
    if 'customer_id' in errors.columns:
        error_customers = errors.groupby('customer_id').size().sort_values(ascending=False)
        print("\nTop customers with errors:")
        print(error_customers.head())
    
    # Timeline of errors
    errors['hour'] = pd.to_datetime(errors['timestamp']).dt.hour
    errors_by_hour = errors.groupby('hour').size()
    
    print("\nError timeline:")
    print(errors_by_hour)
    
    return errors, top_error

errors_df, top_error = analyze_error_patterns()
```

**Step 3: Compare Failed vs Successful Requests**

```python
def compare_failed_vs_successful():
    """Compare characteristics of failed vs successful requests"""
    
    # Get successful requests
    successful = get_successful_requests_last_hour()
    failed = get_failed_requests_last_hour()
    
    print("\n=== FAILED VS SUCCESSFUL COMPARISON ===")
    
    # Compare input distributions
    for feature in ['age', 'income', 'credit_score']:
        if feature in failed.columns:
            print(f"\n{feature}:")
            print(f"  Failed: mean={failed[feature].mean():.2f}, "
                  f"std={failed[feature].std():.2f}, "
                  f"min={failed[feature].min():.2f}, "
                  f"max={failed[feature].max():.2f}")
            
            print(f"  Success: mean={successful[feature].mean():.2f}, "
                  f"std={successful[feature].std():.2f}, "
                  f"min={successful[feature].min():.2f}, "
                  f"max={successful[feature].max():.2f}")
            
            # Check for out-of-range values
            if failed[feature].min() < successful[feature].min() - 100:
                print(f"  ⚠ Failed requests have unusually low {feature}")
            
            if failed[feature].max() > successful[feature].max() + 100:
                print(f"  ⚠ Failed requests have unusually high {feature}")
    
    # Check for missing values
    print("\nMissing values:")
    print(f"  Failed: {failed.isnull().sum().sum()}")
    print(f"  Success: {successful.isnull().sum().sum()}")
    
    # Check data types
    print("\nData type mismatches:")
    for col in failed.columns:
        if col in successful.columns:
            if failed[col].dtype != successful[col].dtype:
                print(f"  {col}: Failed={failed[col].dtype}, "
                      f"Success={successful[col].dtype}")

compare_failed_vs_successful()
```

**Step 4: Check Recent Changes**

```python
def check_recent_changes():
    """Identify recent changes that might cause issues"""
    
    print("\n=== RECENT CHANGES ===")
    
    # 1. Code deployments
    deployments = get_deployments_last_24h()
    if deployments:
        print(f"\nRecent deployments:")
        for dep in deployments:
            print(f"  - {dep['time']}: {dep['version']} by {dep['user']}")
    
    # 2. Model updates
    model_changes = get_model_version_changes_last_24h()
    if model_changes:
        print(f"\nModel version changes:")
        for change in model_changes:
            print(f"  - {change['time']}: {change['old_version']} → "
                  f"{change['new_version']}")
    
    # 3. Feature engineering changes
    feature_changes = get_feature_pipeline_changes_last_24h()
    if feature_changes:
        print(f"\nFeature pipeline changes:")
        for change in feature_changes:
            print(f"  - {change['time']}: {change['description']}")
    
    # 4. Dependency updates
    dependency_changes = get_dependency_updates_last_24h()
    if dependency_changes:
        print(f"\nDependency updates:")
        for dep in dependency_changes:
            print(f"  - {dep['package']}: {dep['old_version']} → "
                  f"{dep['new_version']}")
    
    # 5. Infrastructure changes
    infra_changes = get_infrastructure_changes_last_24h()
    if infra_changes:
        print(f"\nInfrastructure changes:")
        for change in infra_changes:
            print(f"  - {change['time']}: {change['description']}")
    
    # 6. Data pipeline changes
    data_changes = get_data_pipeline_changes_last_24h()
    if data_changes:
        print(f"\nData pipeline changes:")
        for change in data_changes:
            print(f"  - {change['time']}: {change['description']}")

check_recent_changes()
```

**Step 5: Reproduce the Error**

```python
def reproduce_error():
    """Try to reproduce the error locally"""
    
    print("\n=== ERROR REPRODUCTION ===")
    
    # Get a failed request
    failed_request = get_failed_request_sample()
    
    print(f"Failed request ID: {failed_request['request_id']}")
    print(f"Timestamp: {failed_request['timestamp']}")
    print(f"Features: {failed_request['features']}")
    print(f"Error: {failed_request['error']}")
    
    # Try to reproduce locally
    try:
        # Load production model
        model = load_production_model()
        
        # Prepare features
        features = failed_request['features']
        
        # Make prediction
        prediction = model.predict([features])
        
        print(f"✓ Reproduced successfully. Prediction: {prediction}")
        
    except Exception as e:
        print(f"✗ Error reproduced: {type(e).__name__}: {e}")
        
        # Detailed error analysis
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())
        
        # Check specific issues
        if "KeyError" in str(e):
            print("\n⚠ Missing feature in input")
            print(f"Expected features: {model.feature_names_}")
            print(f"Provided features: {list(features.keys())}")
            
            missing = set(model.feature_names_) - set(features.keys())
            extra = set(features.keys()) - set(model.feature_names_)
            
            if missing:
                print(f"Missing features: {missing}")
            if extra:
                print(f"Extra features: {extra}")
        
        elif "ValueError" in str(e):
            print("\n⚠ Invalid feature value")
            for feature, value in features.items():
                print(f"  {feature}: {value} (type: {type(value)})")
        
        elif "TypeError" in str(e):
            print("\n⚠ Type mismatch")
        
        return e

error = reproduce_error()
```

**Step 6: Immediate Mitigation**

```python
def apply_immediate_mitigation(issue_type):
    """Apply quick fix to restore service"""
    
    print("\n=== IMMEDIATE MITIGATION ===")
    
    if issue_type == "BAD_DEPLOYMENT":
        print("Rolling back to previous version...")
        
        # Kubernetes rollback
        import subprocess
        result = subprocess.run(
            ['kubectl', 'rollout', 'undo', 'deployment/model-service'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Rollback successful")
        else:
            print(f"✗ Rollback failed: {result.stderr}")
    
    elif issue_type == "RESOURCE_ISSUE":
        print("Scaling up resources...")
        
        # Scale up deployment
        subprocess.run([
            'kubectl', 'scale', 'deployment/model-service',
            '--replicas=20'
        ])
        
        print("✓ Scaled to 20 replicas")
    
    elif issue_type == "DEPENDENCY_DOWN":
        print("Restarting dependencies...")
        
        # Restart Redis
        subprocess.run([
            'kubectl', 'rollout', 'restart', 'deployment/redis'
        ])
        
        print("✓ Redis restarted")
    
    elif "KeyError" in str(issue_type):
        print("Adding input validation and fallback...")
        
        # Deploy hotfix with better error handling
        deploy_hotfix_with_validation()
        
        print("✓ Hotfix deployed")
    
    # Monitor error rate
    print("\nMonitoring error rate...")
    for i in range(5):
        time.sleep(60)  # Wait 1 minute
        error_rate = get_error_rate_last_5_min()
        print(f"  Minute {i+1}: Error rate = {error_rate:.1%}")
        
        if error_rate < 0.01:  # Less than 1%
            print("\n✓ Error rate back to normal")
            return True
    
    print("\n⚠ Error rate still elevated")
    return False

success = apply_immediate_mitigation(issue_type)
```

**Step 7: Root Cause Analysis**

```python
def root_cause_analysis():
    """Detailed root cause investigation"""
    
    print("\n=== ROOT CAUSE ANALYSIS ===")
    
    # Timeline reconstruction
    print("\nTimeline:")
    
    events = [
        {"time": "14:00", "event": "Service running normally"},
        {"time": "14:30", "event": "Feature pipeline updated"},
        {"time": "14:35", "event": "Error rate starts increasing"},
        {"time": "14:40", "event": "Error rate reaches 30%"},
        {"time": "14:45", "event": "Rollback initiated"},
        {"time": "14:50", "event": "Error rate back to normal"},
    ]
    
    for event in events:
        print(f"  {event['time']}: {event['event']}")
    
    # Root cause
    print("\nRoot Cause:")
    print("  Feature pipeline update changed feature names:")
    print("  - 'user_age' was renamed to 'age'")
    print("  - Model still expects 'user_age'")
    print("  - 30% of requests came through new pipeline")
    
    # Impact
    print("\nImpact:")
    print("  - 30% of requests failed for 15 minutes")
    print("  - ~4,500 failed predictions")
    print("  - No financial loss (errors caught)")
    
    # Prevention
    print("\nPrevention:")
    print("  1. Add schema validation before deployment")
    print("  2. Implement feature name mapping layer")
    print("  3. Add integration tests for feature pipeline changes")
    print("  4. Implement gradual rollout (canary deployment)")

root_cause_analysis()
```

**Step 8: Post-Incident Actions**

```python
def post_incident_actions():
    """Actions to prevent recurrence"""
    
    print("\n=== POST-INCIDENT ACTIONS ===")
    
    # 1. Add schema validation
    print("\n1. Adding schema validation...")
    
    from pydantic import BaseModel, create_model
    
    # Generate schema from model
    feature_names = model.feature_names_in_
    feature_types = {name: float for name in feature_names}
    
    PredictionRequest = create_model('PredictionRequest', **feature_types)
    
    @app.post("/predict")
    def predict_with_validation(request: PredictionRequest):
        """Validated prediction endpoint"""
        prediction = model.predict([request.dict()])
        return {"prediction": prediction[0]}
    
    # 2. Add feature name mapping
    print("2. Adding feature name mapping...")
    
    FEATURE_NAME_MAPPING = {
        'age': 'user_age',  # New name → old name
        'income': 'user_income',
    }
    
    def map_feature_names(features):
        """Map feature names to expected names"""
        mapped = {}
        for key, value in features.items():
            mapped_key = FEATURE_NAME_MAPPING.get(key, key)
            mapped[mapped_key] = value
        return mapped
    
    # 3. Add integration tests
    print("3. Adding integration tests...")
    
    def test_feature_pipeline_integration():
        """Test feature pipeline produces correct schema"""
        
        # Get sample from feature pipeline
        sample_features = feature_pipeline.transform(sample_data)
        
        # Check schema
        expected_features = set(model.feature_names_in_)
        actual_features = set(sample_features.keys())
        
        assert expected_features == actual_features, \
            f"Schema mismatch: {expected_features} vs {actual_features}"
    
    # 4. Implement canary deployment
    print("4. Implementing canary deployment...")
    
    # See previous answers for canary deployment code
    
    # 5. Create runbook
    print("5. Creating incident runbook...")
    
    runbook = """
    # Model Service Incident Runbook
    
    ## High Error Rate (>10%)
    
    1. Check recent deployments: `kubectl rollout history deployment/model-service`
    2. If recent deployment, rollback: `kubectl rollout undo deployment/model-service`
    3. Check error logs: `kubectl logs deployment/model-service | grep ERROR`
    4. Check dependencies: `kubectl get pods | grep redis`
    5. Escalate if not resolved in 15 minutes
    
    ## Service Down
    
    1. Check pod status: `kubectl get pods -l app=model-service`
    2. Restart: `kubectl rollout restart deployment/model-service`
    3. Check events: `kubectl get events --sort-by='.lastTimestamp'`
    4. Scale up if resource issue: `kubectl scale deployment/model-service --replicas=20`
    
    ## Contact
    
    - Oncall: #ml-oncall Slack channel
    - Escalation: ML Team Lead
    """
    
    with open('incident_runbook.md', 'w') as f:
        f.write(runbook)
    
    print("✓ Post-incident actions completed")

post_incident_actions()
```

**Incident Summary:**

```
INCIDENT REPORT
===============

Incident ID: INC-2026-0714-001
Severity: P1 (High)
Duration: 15 minutes
Impact: 30% error rate, ~4,500 failed requests

Timeline:
- 14:30: Feature pipeline updated (renamed features)
- 14:35: Error rate starts increasing
- 14:40: Alert triggered, oncall paged
- 14:45: Root cause identified, rollback initiated
- 14:50: Service restored

Root Cause:
- Feature pipeline renamed 'user_age' → 'age'
- Model still expected 'user_age'
- No schema validation caught the mismatch

Immediate Fix:
- Rolled back feature pipeline update

Long-term Fix:
- Added schema validation
- Implemented feature name mapping
- Added integration tests
- Implemented canary deployments
- Created incident runbook

Lessons Learned:
- Need schema validation before deployment
- Feature changes require model coordination
- Integration tests should cover schema
- Gradual rollouts catch issues early
```

---

## Interview Tips

### How to Approach Advanced MLOps Questions

1. **Start with Clarifying Questions**:
   - Scale (requests/day, data size, number of models)
   - SLA requirements (latency, availability)
   - Budget constraints
   - Existing infrastructure

2. **Think Systematically**:
   - Don't jump to solutions
   - Consider trade-offs
   - Think about monitoring and observability
   - Consider failure modes

3. **Show Production Experience**:
   - Mention real tools (MLflow, Kubeflow, Feast)
   - Discuss trade-offs you've made
   - Share war stories (what went wrong and how you fixed it)
   - Explain monitoring and alerting

4. **Demonstrate Problem-Solving**:
   - Walk through your thought process
   - Consider multiple solutions
   - Evaluate trade-offs
   - Think about edge cases

5. **Business Awareness**:
   - Connect technical decisions to business impact
   - Discuss cost optimization
   - Mention user experience
   - Consider team dynamics

---

## Additional Resources

- **MLflow Documentation**: https://mlflow.org/docs/latest/index.html
- **Kubeflow**: https://www.kubeflow.org/
- **Feast (Feature Store)**: https://feast.dev/
- **Evidently (Monitoring)**: https://evidentlyai.com/
- **KServe (Model Serving)**: https://kserve.github.io/website/
- **AWS SageMaker**: https://aws.amazon.com/sagemaker/
- **Google Vertex AI**: https://cloud.google.com/vertex-ai
- **Azure ML**: https://azure.microsoft.com/en-us/services/machine-learning/

---

**Previous**: [Intermediate Questions](../02-intermediate/interview-questions-intermediate.md)  
**Up Next**: [Real-World Project](20-real-world-project.md)

