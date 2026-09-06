# Real-World MLOps Project

## Overview

This guide walks through building a complete, production-ready ML system from scratch, incorporating all MLOps best practices.

## 📖 Understanding the Full MLOps Picture (Intuition First)

Every individual topic in this course — experiment tracking, versioning, serving, monitoring, drift detection — is a single instrument. This capstone is the full orchestra playing together. In isolation, each practice seems like overhead; assembled into a working system, you finally see *why* they exist and how they interlock. A recommendation model that trains, deploys, serves millions of predictions, notices when it's decaying, and retrains itself — that's the payoff for all the discipline.

The reason to study a complete project is that the *connections between stages* are where real systems succeed or fail. A model that trains beautifully but has no serving path is useless. A serving system with no monitoring is a time bomb. A monitoring system that detects drift but has no retraining pipeline just generates anxiety. The end-to-end view forces you to build the *whole loop* — data → features → training → validation → deployment → serving → monitoring → back to retraining — so the system sustains itself rather than requiring constant manual intervention.

This project (an e-commerce recommendation system) is deliberately realistic: high scale (millions of users, millions of daily interactions), real business stakes (recommendations drive revenue), and real operational pressure (predictions must be fast and always available). Those constraints force the architectural decisions — why you need a feature store (consistency at scale), why you need real-time serving (users won't wait), why you need drift detection (tastes change constantly), and why you need automated retraining (you can't manually retrain daily).

Think of this as the exam that tests whether the individual lessons stuck. As you read it, keep asking: *which practice is being applied here, and what would break if it were missing?* That's the mindset that turns a collection of MLOps techniques into the ability to design a production ML system end-to-end.

## Project: E-commerce Recommendation System

**Business Goal:** Recommend products to increase sales  
**ML Task:** Collaborative filtering + content-based recommendations  
**Scale:** 1M users, 100K products, 10M interactions/day

## Architecture

```
Data Pipeline → Feature Store → Training Pipeline → Model Registry
                                        ↓
Production API ← Deployment Pipeline ← Model Validation
     ↓
Monitoring & Feedback Loop → Retraining Trigger
```

## Implementation Phases

### Phase 1: Data Infrastructure (Week 1-2)

**1. Data Ingestion**
```python
# airflow/dags/data_ingestion.py
from airflow import DAG
from airflow.operators.python import PythonOperator

def ingest_user_interactions():
    # Pull from production database
    interactions = fetch_from_db(
        query="SELECT * FROM user_interactions WHERE date >= '{{ ds }}'"
    )
    
    # Validate
    validate_data(interactions)
    
    # Save to data lake
    interactions.to_parquet(f's3://data-lake/interactions/{{ ds }}.parquet')

dag = DAG('data_ingestion', schedule_interval='@daily')
ingest_task = PythonOperator(task_id='ingest', python_callable=ingest_user_interactions)
```

**2. Feature Engineering**
```python
# features/user_features.py
def create_user_features(interactions_df):
    user_features = interactions_df.groupby('user_id').agg({
        'product_id': 'count',  # Total interactions
        'rating': 'mean',        # Average rating
        'timestamp': 'max'       # Last activity
    }).rename(columns={
        'product_id': 'interaction_count',
        'rating': 'avg_rating',
        'timestamp': 'last_activity_date'
    })
    
    # Add time-based features
    user_features['days_since_last_activity'] = (
        pd.Timestamp.now() - user_features['last_activity_date']
    ).dt.days
    
    return user_features
```

**3. Feature Store Setup**
```python
# feast/features.py
from feast import Entity, Feature, FeatureView, FileSource

user = Entity(name="user", value_type=ValueType.INT64)

user_features_view = FeatureView(
    name="user_features",
    entities=["user"],
    features=[
        Feature(name="interaction_count", dtype=ValueType.INT64),
        Feature(name="avg_rating", dtype=ValueType.DOUBLE),
        Feature(name="days_since_last_activity", dtype=ValueType.INT64)
    ],
    source=FileSource(path="s3://features/user_features.parquet")
)
```

### Phase 2: Model Development (Week 3-4)

**1. Training Pipeline**
```python
# src/train.py
import mlflow

def train_recommendation_model():
    mlflow.set_experiment("recommendation-model")
    
    with mlflow.start_run():
        # Load features
        training_data = feature_store.get_historical_features(...)
        
        # Train collaborative filtering model
        model = train_als_model(training_data)
        
        # Evaluate
        metrics = evaluate_model(model, test_data)
        mlflow.log_metrics(metrics)
        
        # Log model
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name="recommendation-model"
        )
        
        return model, metrics
```

**2. Model Validation**
```python
# tests/test_model.py
def test_model_performance():
    model = load_model()
    test_data = load_test_data()
    
    # Performance tests
    precision_at_k = calculate_precision_at_k(model, test_data, k=10)
    assert precision_at_k > 0.15, f"Precision@10 too low: {precision_at_k}"
    
    # Latency test
    latency = measure_prediction_latency(model)
    assert latency < 100, f"Latency too high: {latency}ms"
    
    # Coverage test
    coverage = calculate_catalog_coverage(model)
    assert coverage > 0.80, f"Coverage too low: {coverage}"
```

### Phase 3: Deployment (Week 5-6)

**1. API Implementation**
```python
# src/api/main.py
from fastapi import FastAPI
import mlflow

app = FastAPI()
model = mlflow.pyfunc.load_model("models:/recommendation-model/Production")

@app.post("/recommend")
async def recommend(user_id: int, num_recommendations: int = 10):
    # Get user features from feature store
    features = feature_store.get_online_features(
        entity_rows=[{"user": user_id}],
        features=["user_features:*"]
    )
    
    # Get recommendations
    recommendations = model.predict(features)[:num_recommendations]
    
    # Log for monitoring
    log_recommendation(user_id, recommendations)
    
    return {"user_id": user_id, "recommendations": recommendations}
```

**2. Kubernetes Deployment**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recommendation-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: myregistry/recommendation-api:v1
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: recommendation-api-hpa
spec:
  scaleTargetRef:
    name: recommendation-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 70
```

### Phase 4: Monitoring (Week 7)

**1. Performance Monitoring**
```python
# src/monitoring/metrics.py
from prometheus_client import Counter, Histogram

recommendation_requests = Counter('recommendation_requests_total', 
                                  'Total recommendation requests')
recommendation_latency = Histogram('recommendation_latency_seconds',
                                   'Recommendation latency')
click_through_rate = Gauge('recommendation_ctr', 
                          'Click-through rate')

@app.post("/recommend")
@recommendation_latency.time()
async def recommend(user_id: int):
    recommendation_requests.inc()
    # ... recommendation logic ...
```

**2. Drift Detection**
```python
# src/monitoring/drift_detection.py
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

def check_drift_daily():
    # Get yesterday's data
    current_data = load_production_data(date='yesterday')
    
    # Compare with training data
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=training_data, current_data=current_data)
    
    if report.as_dict()['metrics'][0]['result']['dataset_drift']:
        alert_team("Data drift detected!")
        trigger_retraining()
```

### Phase 5: CI/CD (Week 8)

```yaml
# .github/workflows/ml-pipeline.yml
name: ML Pipeline

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * 0'  # Weekly

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest tests/
  
  train:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Train model
        run: python src/train.py
      - name: Validate model
        run: python tests/validate_model.py
  
  deploy:
    needs: train
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: kubectl apply -f k8s/staging/
      - name: Run integration tests
        run: pytest tests/integration/
      - name: Deploy to production
        run: kubectl apply -f k8s/production/
```

## Lessons Learned

### What Worked Well
✅ Feature store eliminated training-serving skew  
✅ Automated retraining kept model fresh  
✅ Gradual rollout caught issues early  
✅ Monitoring detected drift before impact  
✅ CI/CD accelerated iteration

### Challenges
❌ Initial feature store setup took longer than expected  
❌ Cold start problem for new users  
❌ Scaling feature computation for real-time  
❌ Balancing model complexity vs. latency

### Solutions Implemented
✅ Batch precompute features for known users  
✅ Fallback to popularity for cold start  
✅ Caching layer for frequently requested features  
✅ A/B tested simpler vs complex models

## Business Impact

- **Revenue:** +15% from better recommendations
- **Engagement:** +25% click-through rate
- **Efficiency:** 90% reduction in manual work
- **Reliability:** 99.9% uptime achieved

## Key Takeaways

✅ Start with MVP, iterate based on impact  
✅ Invest in infrastructure early  
✅ Monitor everything from day one  
✅ Automate tedious tasks  
✅ Balance complexity with maintainability  
✅ Measure business metrics, not just ML metrics

## 🎯 Interview Quick Points

- A real MLOps system is the full loop: data → features → training → validation → deployment → serving → monitoring → retraining
- Individual practices only make sense assembled into a working end-to-end system
- The **connections between stages** are where systems succeed or fail
- A model with no serving path is useless; serving with no monitoring is a time bomb
- Build the whole self-sustaining loop so the system doesn't need constant manual intervention
- Scale and business stakes force the architecture (feature store, real-time serving, drift detection, auto-retraining)
- Always measure **business metrics** (revenue, conversions), not just ML metrics
- Start with an MVP, prove impact, then add sophistication
- For each component, ask "what would break if this were missing?"
- This capstone tests whether the individual MLOps lessons connect into system design

---

**Practice:** [Lab 10 - End-to-End Project](../mlops-practice/lab-10-e2e-project/)
