# MLOps Interview Questions - Intermediate Level

Comprehensive interview questions covering feature engineering, model versioning, deployment strategies, and more.

---

## Feature Engineering and Pipelines

### Q1: How do you ensure reproducible feature engineering in production?

**Answer:**

Use sklearn pipelines to encapsulate all feature transformations:

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer

# Define transformations
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Combine
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Full pipeline
ml_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('model', RandomForestClassifier())
])

# Train
ml_pipeline.fit(X_train, y_train)

# Save entire pipeline
joblib.dump(ml_pipeline, 'model_pipeline.pkl')

# Load and predict (all transformations applied automatically)
pipeline = joblib.load('model_pipeline.pkl')
predictions = pipeline.predict(new_data)
```

**Key Points:**
- All transformations in one pipeline
- Consistent train/serve transformations
- Versioned with the model
- No training/serving skew

---

### Q2: What is training/serving skew and how do you prevent it?

**Answer:**

**Training/Serving Skew** occurs when feature transformations differ between training and production.

**Example Problem:**
```python
# Training
df['age_squared'] = df['age'] ** 2
df['income_log'] = np.log(df['income'] + 1)
model.fit(df[features], target)

# Production (someone forgot the +1!)
df['income_log'] = np.log(df['income'])  # BUG!
predictions = model.predict(df[features])
```

**Solutions:**

1. **Use Pipelines** (best):
```python
class LogTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_copy = X.copy()
        X_copy['income_log'] = np.log(X_copy['income'] + 1)
        return X_copy

pipeline = Pipeline([
    ('log_transform', LogTransformer()),
    ('model', model)
])
```

2. **Feature Store**:
- Centralize feature definitions
- Same code for training and serving
- Version features with models

3. **Testing**:
```python
def test_feature_consistency():
    train_features = pipeline.transform(train_data)
    prod_features = pipeline.transform(prod_data)
    
    assert train_features.columns.equals(prod_features.columns)
    assert train_features.dtypes.equals(prod_features.dtypes)
```

---


## Model Versioning and Registry

### Q3: Explain model versioning best practices and implementation with MLflow.

**Answer:**

**Versioning Strategy:**
```
model_name/
├── v1.0.0  (production)
├── v1.1.0  (staging)
└── v2.0.0  (development)
```

**Implementation:**
```python
import mlflow
from mlflow.tracking import MlflowClient

# Train and register model
with mlflow.start_run(run_name="fraud_detection_v1"):
    # Train model
    model.fit(X_train, y_train)
    
    # Log parameters
    mlflow.log_params({
        "n_estimators": 100,
        "max_depth": 10,
        "feature_set": "v1.0"
    })
    
    # Log metrics
    mlflow.log_metrics({
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall
    })
    
    # Register model
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name="fraud_detection"
    )

# Promote to production
client = MlflowClient()

# Get latest version
latest_version = client.get_latest_versions("fraud_detection", stages=["None"])[0]

# Transition to production
client.transition_model_version_stage(
    name="fraud_detection",
    version=latest_version.version,
    stage="Production"
)
```

**Best Practices:**
- Semantic versioning (major.minor.patch)
- Tag models with metadata
- Track lineage (data, code, hyperparameters)
- Automated testing before promotion
- Gradual rollout to production

---

### Q4: How do you implement A/B testing for ML models?

**Answer:**

**Architecture:**
```
User Request
    ↓
Load Balancer
    ↓
┌────────────────┬────────────────┐
│  Model A (70%) │  Model B (30%) │
└────────────────┴────────────────┘
         ↓               ↓
    Prediction      Prediction
         ↓               ↓
    Metrics DB  ←───────┘
```

**Implementation:**
```python
from fastapi import FastAPI
import random
import mlflow.pyfunc

app = FastAPI()

# Load models
model_a = mlflow.pyfunc.load_model("models:/fraud_detection/Production")
model_b = mlflow.pyfunc.load_model("models:/fraud_detection/Staging")

@app.post("/predict")
async def predict(features: dict):
    # A/B split (70/30)
    use_model_b = random.random() < 0.30
    
    if use_model_b:
        model_version = "B"
        prediction = model_b.predict([features])
    else:
        model_version = "A"
        prediction = model_a.predict([features])
    
    # Log for analysis
    log_prediction(
        features=features,
        prediction=prediction,
        model_version=model_version
    )
    
    return {
        "prediction": prediction[0],
        "model_version": model_version
    }

def log_prediction(features, prediction, model_version):
    """Log predictions for analysis"""
    # Store in database/data warehouse
    db.insert({
        'timestamp': datetime.now(),
        'features': features,
        'prediction': prediction,
        'model_version': model_version
    })
```

**Analysis:**
```python
import pandas as pd
from scipy import stats

# Get metrics for both models
df = pd.read_sql("SELECT * FROM predictions WHERE timestamp > NOW() - INTERVAL '7 days'")

model_a_metrics = df[df['model_version'] == 'A']['accuracy'].mean()
model_b_metrics = df[df['model_version'] == 'B']['accuracy'].mean()

# Statistical significance test
t_stat, p_value = stats.ttest_ind(
    df[df['model_version'] == 'A']['accuracy'],
    df[df['model_version'] == 'B']['accuracy']
)

if p_value < 0.05 and model_b_metrics > model_a_metrics:
    print("✅ Model B is significantly better! Promote to production.")
else:
    print("⚠️ No significant improvement. Keep Model A.")
```

---

## Model Deployment

### Q5: Compare different model deployment strategies (Blue-Green, Canary, Shadow).

**Answer:**

**1. Blue-Green Deployment:**
- Two identical environments
- Switch traffic instantly
- Easy rollback

```yaml
# Kubernetes Blue-Green
apiVersion: v1
kind: Service
metadata:
  name: model-service
spec:
  selector:
    app: model
    version: blue  # Switch to 'green' for deployment
  ports:
  - port: 80
    targetPort: 8080

---
# Blue deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: model
      version: blue
  template:
    metadata:
      labels:
        app: model
        version: blue
    spec:
      containers:
      - name: model
        image: model:v1.0

---
# Green deployment (new version)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: model
      version: green
  template:
    metadata:
      labels:
        app: model
        version: green
    spec:
      containers:
      - name: model
        image: model:v2.0
```

**2. Canary Deployment:**
- Gradual rollout
- Monitor metrics
- Increase traffic slowly

```yaml
# Using Istio VirtualService
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: model-service
spec:
  hosts:
  - model-service
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: model-service
        subset: v2
  - route:
    - destination:
        host: model-service
        subset: v1
      weight: 90
    - destination:
        host: model-service
        subset: v2
      weight: 10  # Start with 10%, gradually increase
```

**3. Shadow Deployment:**
- New model receives copy of traffic
- Predictions not returned to users
- Compare performance without risk

```python
@app.post("/predict")
async def predict(features: dict):
    # Primary prediction
    primary_prediction = model_v1.predict([features])
    
    # Shadow prediction (async, don't wait)
    asyncio.create_task(
        shadow_predict(features, model_v2)
    )
    
    return {"prediction": primary_prediction}

async def shadow_predict(features, model):
    """Shadow prediction for comparison"""
    shadow_prediction = model.predict([features])
    
    # Log for comparison
    log_shadow_prediction(
        features=features,
        shadow_prediction=shadow_prediction,
        model_version="v2"
    )
```

**Comparison:**

| Strategy | Risk | Rollback | Use Case |
|----------|------|----------|----------|
| Blue-Green | Low | Instant | Full confidence in new version |
| Canary | Very Low | Easy | Gradual validation |
| Shadow | None | N/A | Testing without user impact |

---

### Q6: How do you monitor ML models in production?

**Answer:**

**Key Metrics to Monitor:**

1. **Model Performance:**
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
prediction_counter = Counter('predictions_total', 'Total predictions')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')
model_accuracy = Gauge('model_accuracy', 'Model accuracy')

@app.post("/predict")
async def predict(features: dict):
    start_time = time.time()
    
    prediction = model.predict([features])
    
    # Update metrics
    prediction_counter.inc()
    prediction_latency.observe(time.time() - start_time)
    
    return {"prediction": prediction}
```

2. **Data Drift Detection:**
```python
from evidently import ColumnMapping
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report

def detect_data_drift(reference_data, current_data):
    """Detect if input data distribution has changed"""
    
    report = Report(metrics=[DataDriftPreset()])
    
    report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=ColumnMapping()
    )
    
    drift_detected = report.as_dict()['metrics'][0]['result']['dataset_drift']
    
    if drift_detected:
        alert("Data drift detected! Model may need retraining.")
    
    return drift_detected
```

3. **Model Drift Detection:**
```python
def detect_model_drift(y_true, y_pred, threshold=0.05):
    """Detect if model performance has degraded"""
    
    current_accuracy = accuracy_score(y_true, y_pred)
    
    # Compare to baseline
    if current_accuracy < baseline_accuracy - threshold:
        alert(f"Model drift detected! Accuracy dropped from {baseline_accuracy} to {current_accuracy}")
        return True
    
    return False
```

4. **Complete Monitoring Pipeline:**
```python
import mlflow
from datetime import datetime, timedelta

def monitor_model():
    """Periodic model monitoring"""
    
    # Get recent predictions
    recent_data = get_predictions_last_24h()
    
    # Check data drift
    reference_data = load_training_data()
    drift = detect_data_drift(reference_data, recent_data)
    
    # Check performance (if labels available)
    if labels_available(recent_data):
        y_true = recent_data['actual']
        y_pred = recent_data['predicted']
        
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        
        # Log to MLflow
        with mlflow.start_run(run_name=f"monitoring_{datetime.now()}"):
            mlflow.log_metrics({
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "data_drift": int(drift)
            })
        
        # Alert if performance degraded
        if accuracy < 0.85:
            alert(f"Model performance dropped to {accuracy}")
    
    # Check system metrics
    check_latency()
    check_error_rate()
    check_resource_usage()

# Schedule monitoring
schedule.every(1).hours.do(monitor_model)
```

**Monitoring Dashboard (Grafana):**
```yaml
# grafana-dashboard.json
{
  "panels": [
    {
      "title": "Predictions per Second",
      "targets": [{"expr": "rate(predictions_total[5m])"}]
    },
    {
      "title": "Prediction Latency P95",
      "targets": [{"expr": "histogram_quantile(0.95, prediction_latency_seconds)"}]
    },
    {
      "title": "Model Accuracy",
      "targets": [{"expr": "model_accuracy"}]
    },
    {
      "title": "Data Drift Score",
      "targets": [{"expr": "data_drift_score"}]
    }
  ]
}
```

---

## CI/CD for ML

### Q7: Design a complete CI/CD pipeline for ML models.

**Answer:**

```yaml
# .github/workflows/ml-pipeline.yml
name: ML CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:

env:
  MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}

jobs:
  # Data Validation
  data-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install great-expectations pandas
      
      - name: Validate data schema
        run: |
          python scripts/validate_data.py
      
      - name: Check data quality
        run: |
          great_expectations checkpoint run data_quality_checkpoint
  
  # Model Training
  train-model:
    needs: data-validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Train model
        run: |
          python train.py
      
      - name: Log to MLflow
        run: |
          python log_model.py
      
      - name: Save artifacts
        uses: actions/upload-artifact@v3
        with:
          name: model
          path: models/
  
  # Model Testing
  test-model:
    needs: train-model
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Download model
        uses: actions/download-artifact@v3
        with:
          name: model
          path: models/
      
      - name: Run unit tests
        run: |
          pytest tests/unit/
      
      - name: Run integration tests
        run: |
          pytest tests/integration/
      
      - name: Validate model performance
        run: |
          python validate_model.py
      
      - name: Check model fairness
        run: |
          python check_fairness.py
  
  # Build Container
  build-container:
    needs: test-model
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Download model
        uses: actions/download-artifact@v3
        with:
          name: model
          path: models/
      
      - name: Build Docker image
        run: |
          docker build -t model-service:${{ github.sha }} .
      
      - name: Scan image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: model-service:${{ github.sha }}
          exit-code: '1'
          severity: 'CRITICAL,HIGH'
      
      - name: Push to registry
        run: |
          docker push model-service:${{ github.sha }}
  
  # Deploy to Staging
  deploy-staging:
    needs: build-container
    runs-on: ubuntu-latest
    environment:
      name: staging
    steps:
      - name: Deploy to staging
        run: |
          kubectl set image deployment/model-service \
            model-service=model-service:${{ github.sha }} \
            -n staging
      
      - name: Run smoke tests
        run: |
          python tests/smoke_tests.py --env staging
  
  # A/B Testing
  ab-test:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - name: Start A/B test
        run: |
          python scripts/start_ab_test.py \
            --model-a production \
            --model-b staging \
            --traffic-split 90:10
      
      - name: Monitor A/B test
        run: |
          python scripts/monitor_ab_test.py --duration 24h
  
  # Deploy to Production
  deploy-production:
    needs: ab-test
    runs-on: ubuntu-latest
    environment:
      name: production
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Canary deployment
        run: |
          kubectl set image deployment/model-service-canary \
            model-service=model-service:${{ github.sha }} \
            -n production
      
      - name: Monitor canary
        run: |
          python scripts/monitor_canary.py --duration 1h
      
      - name: Promote to production
        run: |
          kubectl set image deployment/model-service \
            model-service=model-service:${{ github.sha }} \
            -n production
```

**Key Components:**
1. Data validation
2. Model training and logging
3. Automated testing (unit, integration, performance)
4. Container build and security scan
5. Staged deployment (staging → A/B test → canary → production)
6. Monitoring and rollback

---

## Bonus Questions

### Q8: How do you handle model retraining in production?

**Answer:**

**Automated Retraining Pipeline:**

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'model_retraining',
    default_args=default_args,
    description='Automated model retraining',
    schedule_interval='@weekly',  # or trigger-based
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

def check_if_retraining_needed():
    """Decide if retraining is needed"""
    # Check model performance
    current_performance = get_current_model_performance()
    
    # Check data drift
    drift_detected = check_data_drift()
    
    # Check time since last training
    days_since_training = get_days_since_last_training()
    
    if current_performance < 0.85 or drift_detected or days_since_training > 30:
        return True
    return False

def extract_training_data():
    """Extract latest training data"""
    # Get data from last 90 days
    data = fetch_data_from_warehouse(days=90)
    save_to_staging(data)

def train_new_model():
    """Train new model"""
    data = load_from_staging()
    
    with mlflow.start_run():
        model = train_model(data)
        
        # Register new version
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name="fraud_detection"
        )

def validate_new_model():
    """Validate new model against production"""
    new_model = load_latest_model()
    prod_model = load_production_model()
    
    test_data = load_test_data()
    
    new_performance = evaluate(new_model, test_data)
    prod_performance = evaluate(prod_model, test_data)
    
    if new_performance > prod_performance:
        return True
    return False

def promote_to_production():
    """Promote model to production"""
    client = MlflowClient()
    
    latest_version = client.get_latest_versions("fraud_detection", stages=["None"])[0]
    
    client.transition_model_version_stage(
        name="fraud_detection",
        version=latest_version.version,
        stage="Production"
    )

# Define tasks
check_task = PythonOperator(
    task_id='check_retraining_needed',
    python_callable=check_if_retraining_needed,
    dag=dag,
)

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_training_data,
    dag=dag,
)

train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_new_model,
    dag=dag,
)

validate_task = PythonOperator(
    task_id='validate_model',
    python_callable=validate_new_model,
    dag=dag,
)

promote_task = PythonOperator(
    task_id='promote_to_production',
    python_callable=promote_to_production,
    dag=dag,
)

# Define workflow
check_task >> extract_task >> train_task >> validate_task >> promote_task
```

**Trigger-based Retraining:**
- Performance drops below threshold
- Data drift detected
- Scheduled (weekly/monthly)
- Manual trigger

---

### Q9: Explain feature stores and their importance in MLOps.

**Answer:**

**Feature Store** is a centralized repository for storing, managing, and serving ML features.

**Why Feature Stores?**
1. **Consistency**: Same features for training and serving
2. **Reusability**: Share features across models
3. **Versioning**: Track feature changes
4. **Performance**: Pre-computed features

**Implementation with Feast:**

```python
from feast import FeatureStore, Entity, FeatureView, Field
from feast.types import Float32, Int64
from datetime import timedelta

# Define entity
user = Entity(
    name="user",
    join_keys=["user_id"],
    description="User entity"
)

# Define feature view
user_features = FeatureView(
    name="user_transaction_features",
    entities=[user],
    ttl=timedelta(days=1),
    schema=[
        Field(name="transaction_count_7d", dtype=Int64),
        Field(name="avg_transaction_amount_7d", dtype=Float32),
        Field(name="max_transaction_amount_7d", dtype=Float32),
    ],
    online=True,
    source=# data source definition
)

# Initialize feature store
store = FeatureStore(repo_path=".")

# Training: Get historical features
training_df = store.get_historical_features(
    entity_df=entities_df,
    features=[
        "user_transaction_features:transaction_count_7d",
        "user_transaction_features:avg_transaction_amount_7d",
    ],
).to_df()

# Serving: Get online features
features = store.get_online_features(
    features=[
        "user_transaction_features:transaction_count_7d",
        "user_transaction_features:avg_transaction_amount_7d",
    ],
    entity_rows=[{"user_id": 12345}],
).to_dict()
```

**Benefits:**
- No training/serving skew
- Fast feature serving (<10ms)
- Feature discovery and reuse
- Point-in-time correctness
- Feature monitoring

---

### Q10: How do you ensure ML model reproducibility?

**Answer:**

**1. Version Everything:**
```python
# requirements.txt with exact versions
numpy==1.24.3
pandas==2.0.2
scikit-learn==1.3.0
mlflow==2.4.1
```

**2. Set Random Seeds:**
```python
import random
import numpy as np
import tensorflow as tf

def set_seeds(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)
```

**3. Track Lineage:**
```python
with mlflow.start_run():
    # Log data version
    mlflow.log_param("data_version", data_version)
    mlflow.log_param("data_hash", compute_hash(data))
    
    # Log code version
    mlflow.log_param("git_commit", git_commit_hash)
    
    # Log all hyperparameters
    mlflow.log_params(hyperparameters)
    
    # Log environment
    mlflow.log_artifact("requirements.txt")
```

**4. Containerize:**
```dockerfile
FROM python:3.9-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

CMD ["python", "train.py"]
```

**5. Use DVC for Data Versioning:**
```bash
# Track data
dvc add data/train.csv

# Version in git
git add data/train.csv.dvc
git commit -m "Update training data"

# Reproduce experiment
dvc repro
```

---

**Next**: [Advanced Topics →](../03-advanced/)
