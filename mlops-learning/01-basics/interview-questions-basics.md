# MLOps Interview Questions - Basics

## Conceptual Questions

### Q1: What is MLOps and why is it important?

**Answer**: MLOps (Machine Learning Operations) is a set of practices that combines ML, DevOps, and Data Engineering to deploy and maintain ML systems in production reliably and efficiently.

**Why Important**:
- **Reproducibility**: Track experiments, data, and models
- **Collaboration**: Data scientists and engineers work together
- **Automation**: Automated training, testing, deployment
- **Monitoring**: Track model performance in production
- **Faster Time-to-Value**: Days instead of months

**Key Differences from Traditional Software**:
```
Traditional DevOps          MLOps
├── Code versioning    →   ├── Code + Data + Model versioning
├── Unit tests         →   ├── Unit + Data + Model tests
├── Deploy binary      →   ├── Deploy model + pipeline
└── Monitor logs       →   └── Monitor performance + drift
```

---

### Q2: Explain the ML lifecycle and where MLOps fits in.

**Answer**: The ML lifecycle has 7 stages, and MLOps provides tools/practices for each:

```
1. Problem Definition
   MLOps: Document requirements, define success metrics

2. Data Collection & Exploration
   MLOps: Data versioning (DVC), data validation

3. Data Preparation & Feature Engineering
   MLOps: Feature stores, reproducible pipelines

4. Model Training
   MLOps: Experiment tracking (MLflow), hyperparameter tuning

5. Model Evaluation
   MLOps: Model registry, validation framework

6. Model Deployment
   MLOps: Model serving, CI/CD pipelines

7. Monitoring & Maintenance
   MLOps: Performance monitoring, drift detection, auto-retraining
```

---

### Q3: What is experiment tracking and why is it crucial?

**Answer**: Experiment tracking records all ML experiments including:
- **Parameters**: Hyperparameters used (learning_rate, batch_size)
- **Metrics**: Performance metrics (accuracy, F1, RMSE)
- **Artifacts**: Models, plots, reports
- **Code**: Version of code used
- **Environment**: Dependencies and versions

**Why Crucial**:
```python
# Without tracking:
# "Which model had 92% accuracy? What parameters did I use?"
# "Can't reproduce yesterday's results!"

# With MLflow tracking:
with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_metric("accuracy", 0.92)
    mlflow.sklearn.log_model(model, "model")

# Result: Every experiment is reproducible and comparable
```

**Benefits**:
- Reproducibility
- Comparison of experiments
- Audit trail
- Team collaboration

---

### Q4: What is the difference between model versioning and data versioning?

**Answer**:

**Model Versioning**: Track different versions of trained models
```python
# MLflow Model Registry
mlflow.register_model(
    model_uri="runs:/abc123/model",
    name="churn-predictor"
)
# Results in: churn-predictor v1, v2, v3...

# Each version has:
- Model binary
- Training code
- Parameters
- Metrics
- Stage (Staging/Production)
```

**Data Versioning**: Track different versions of datasets
```bash
# DVC (Data Version Control)
dvc add data/training_data.csv
git add data/training_data.csv.dvc
git commit -m "Dataset v1"

# Later, update data
dvc add data/training_data.csv
git commit -m "Dataset v2 - added 10K samples"

# Switch between versions
git checkout <commit>
dvc checkout
```

**Why Both Are Needed**:
```
Model v1 trained on Data v1 = Accuracy 85%
Model v2 trained on Data v1 = Accuracy 87%
Model v2 trained on Data v2 = Accuracy 90%

Without versioning: Can't reproduce or debug!
```

---

### Q5: What is a model registry and what problem does it solve?

**Answer**: A model registry is a centralized repository for managing ML models and their lifecycle.

**Key Features**:
```python
# 1. Register model
result = mlflow.register_model(
    model_uri="runs:/abc123/model",
    name="fraud-detector"
)

# 2. Version automatically (v1, v2, v3...)

# 3. Lifecycle stages
client.transition_model_version_stage(
    name="fraud-detector",
    version=2,
    stage="Production"
)

# 4. Load model by stage
model = mlflow.sklearn.load_model(
    "models:/fraud-detector/Production"
)
```

**Problems It Solves**:
- ❌ "Which model is in production?"
- ❌ "How do we rollback to previous version?"
- ❌ "Who deployed this model?"
- ❌ "What were the training metrics?"

✅ **Registry provides**:
- Centralized model storage
- Version control
- Lifecycle management
- Metadata and lineage
- Access control

---

## Practical Questions

### Q6: How would you set up experiment tracking for a new ML project?

**Answer**:

**Step 1: Install MLflow**
```bash
pip install mlflow
```

**Step 2: Create tracking script**
```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier

# Set experiment
mlflow.set_experiment("customer-churn")

# Track experiment
with mlflow.start_run(run_name="baseline"):
    # Log parameters
    params = {"n_estimators": 100, "max_depth": 5}
    mlflow.log_params(params)
    
    # Train
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    
    # Log metrics
    accuracy = model.score(X_test, y_test)
    mlflow.log_metric("accuracy", accuracy)
    
    # Log model
    mlflow.sklearn.log_model(model, "model")
    
    # Log artifacts
    mlflow.log_artifact("plots/confusion_matrix.png")
```

**Step 3: Start UI**
```bash
mlflow ui
# Access at http://localhost:5000
```

**Step 4: Compare experiments in UI**
- View all runs
- Compare metrics
- Download models
- View artifacts

---

### Q7: Explain how to version datasets using DVC.

**Answer**:

**Setup**:
```bash
# Initialize DVC
dvc init

# Configure remote storage (S3)
dvc remote add -d myremote s3://my-bucket/dvc-storage
```

**Version a dataset**:
```bash
# Add data file to DVC
dvc add data/training_data.csv

# Commit the .dvc file to git
git add data/training_data.csv.dvc .gitignore
git commit -m "Add training data v1"

# Push data to remote
dvc push
```

**Update dataset**:
```bash
# Modify data
python update_data.py

# Re-add to DVC
dvc add data/training_data.csv

# Commit new version
git add data/training_data.csv.dvc
git commit -m "Training data v2 - added features"
dvc push
```

**Retrieve specific version**:
```bash
# Checkout old version
git checkout <commit-hash>
dvc checkout

# Data file now matches that commit
```

---

### Q8: How do you deploy an ML model as a REST API?

**Answer**:

**Method 1: Flask**
```python
from flask import Flask, request, jsonify
import mlflow.sklearn

app = Flask(__name__)

# Load model
model = mlflow.sklearn.load_model("models:/fraud-detector/production")

@app.route('/predict', methods=['POST'])
def predict():
    # Get features from request
    data = request.json
    features = pd.DataFrame([data])
    
    # Make prediction
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]
    
    return jsonify({
        'prediction': int(prediction),
        'probability': float(probability)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Method 2: MLflow Serve**
```bash
# Serve model directly
mlflow models serve -m models:/fraud-detector/production -p 5000

# Test
curl -X POST http://localhost:5000/invocations \
  -H 'Content-Type: application/json' \
  -d '{"inputs": [[1.0, 2.0, 3.0]]}'
```

**Method 3: Containerize**
```dockerfile
FROM python:3.9-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY model/ /model/
COPY app.py .

EXPOSE 5000
CMD ["python", "app.py"]
```

---

### Q9: What metrics would you track for a deployed ML model?

**Answer**:

**Model Performance Metrics**:
```python
from prometheus_client import Counter, Histogram, Gauge

# Prediction metrics
predictions_total = Counter('predictions_total', 'Total predictions')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction time')

# Model performance
model_accuracy = Gauge('model_accuracy', 'Current accuracy')
model_precision = Gauge('model_precision', 'Current precision')
model_recall = Gauge('model_recall', 'Current recall')

# Business metrics
fraud_detected = Counter('fraud_detected_total', 'Frauds caught')
false_positives = Counter('false_positives_total', 'False alarms')
```

**Data Quality Metrics**:
```python
# Feature drift
feature_drift = Gauge('feature_drift_score', 'Data drift score', ['feature'])

# Missing values
missing_values_rate = Gauge('missing_values_rate', 'Missing data rate')

# Prediction distribution
prediction_distribution = Histogram('prediction_distribution', 'Pred dist')
```

**System Metrics**:
```python
# Infrastructure
memory_usage = Gauge('memory_usage_bytes', 'Memory used')
cpu_usage = Gauge('cpu_usage_percent', 'CPU used')
request_rate = Counter('request_rate', 'Requests per second')
```

**Example Dashboard**:
```
┌─────────────────────────────────────────┐
│ Model Performance                       │
│ Accuracy: 92% ▲ (+2%)                  │
│ Latency: 45ms ▼ (-5ms)                 │
│ Predictions/day: 1.2M                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Data Drift Alert!                       │
│ Feature 'income' distribution changed   │
│ KS statistic: 0.15 (threshold: 0.10)   │
│ → Recommend retraining                  │
└─────────────────────────────────────────┘
```

---

### Q10: How do you handle model rollback if a new model performs poorly?

**Answer**:

**Strategy 1: Blue-Green Deployment**
```python
# Deploy new model (green) alongside old (blue)
deploy_model(model_v2, environment='green')

# Route 10% traffic to green
route_traffic(blue=0.9, green=0.1)

# Monitor metrics
if green_performance > blue_performance:
    route_traffic(blue=0, green=1)  # Full switch
    retire_model(model_v1)
else:
    route_traffic(blue=1, green=0)  # Rollback
    retire_model(model_v2)
```

**Strategy 2: Model Registry Stages**
```python
# New model in Staging
client.transition_model_version_stage(
    name="fraud-detector",
    version=3,
    stage="Staging"
)

# Test in staging environment
if validate_staging_performance():
    # Promote to Production
    client.transition_model_version_stage(
        name="fraud-detector",
        version=3,
        stage="Production"
    )
    # Old model automatically archived
else:
    # Keep current production model
    print("New model failed validation")
```

**Strategy 3: Kubernetes Rollback**
```bash
# Deploy new model
kubectl set image deployment/model-api model=model:v2

# Monitor
kubectl rollout status deployment/model-api

# If issues detected, rollback
kubectl rollout undo deployment/model-api

# Back to v1
```

**Monitoring for Rollback Decision**:
```python
def should_rollback(new_model_metrics, old_model_metrics):
    """Decide if rollback needed"""
    
    # Performance degradation
    if new_model_metrics['accuracy'] < old_model_metrics['accuracy'] - 0.05:
        return True, "Accuracy dropped by 5%"
    
    # Latency issues
    if new_model_metrics['p95_latency'] > 500:  # ms
        return True, "Latency too high"
    
    # Error rate spike
    if new_model_metrics['error_rate'] > 0.05:
        return True, "Error rate > 5%"
    
    return False, "Model performing well"
```

---

## Scenario-Based Questions

### Q11: Your ML model's accuracy dropped from 90% to 75% in production. How do you debug?

**Answer**:

**Step 1: Check Data Drift**
```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

# Compare training vs production data
report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=training_data, 
           current_data=production_data)

if report.as_dict()['metrics'][0]['result']['dataset_drift']:
    print("❌ Data drift detected!")
    print("Features changed:", get_drifted_features())
```

**Step 2: Check Label Drift**
```python
# Compare prediction distribution
training_pred_dist = training_labels.value_counts(normalize=True)
production_pred_dist = production_preds.value_counts(normalize=True)

if (training_pred_dist - production_pred_dist).abs().max() > 0.1:
    print("❌ Label distribution changed!")
```

**Step 3: Investigate Feature Changes**
```python
for feature in features:
    training_stats = training_data[feature].describe()
    production_stats = production_data[feature].describe()
    
    if abs(training_stats['mean'] - production_stats['mean']) > threshold:
        print(f"⚠️ {feature} mean changed significantly")
```

**Step 4: Check for Missing Values**
```python
missing_rate = production_data.isnull().mean()
if missing_rate.any() > 0.1:
    print("❌ High missing value rate:", missing_rate)
```

**Step 5: Validate Model Inputs**
```python
# Check if features are in expected range
for feature in numeric_features:
    out_of_range = (
        (production_data[feature] < training_min[feature]) |
        (production_data[feature] > training_max[feature])
    ).sum()
    
    if out_of_range > 0:
        print(f"⚠️ {out_of_range} {feature} values out of training range")
```

**Solution**: Based on findings, either:
1. Retrain with recent data (data drift)
2. Fix data pipeline (data quality issues)
3. Update feature engineering (distribution changes)

---

### Q12: How would you implement continuous training for an ML model?

**Answer**:

**Architecture**:
```
New Data → Trigger → Training Pipeline → Validation → Deploy
    ↓         ↓            ↓                 ↓          ↓
  Daily    Schedule    Auto-train        A/B test   Automatic
  Batch    or Event                      vs current  or Manual
```

**Implementation**:
```python
# training_pipeline.py
def continuous_training_pipeline():
    """Automated retraining pipeline"""
    
    # 1. Check if retraining needed
    if not should_retrain():
        print("Model still performing well")
        return
    
    # 2. Collect new data
    new_data = fetch_data_since_last_training()
    print(f"Collected {len(new_data)} new samples")
    
    # 3. Combine with historical data
    all_data = combine_datasets(historical_data, new_data)
    
    # 4. Prepare features
    X, y = prepare_features(all_data)
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    
    # 5. Train new model
    with mlflow.start_run():
        model = train_model(X_train, y_train)
        
        # Log everything
        mlflow.log_params(model.get_params())
        mlflow.log_metric("train_accuracy", model.score(X_train, y_train))
        mlflow.log_metric("test_accuracy", model.score(X_test, y_test))
        mlflow.sklearn.log_model(model, "model")
    
    # 6. Validate new model
    if validate_model(model, X_test, y_test):
        # 7. Deploy to staging
        deploy_to_staging(model)
        
        # 8. Run A/B test
        if ab_test_passes(model):
            # 9. Promote to production
            promote_to_production(model)
            notify_team("✅ New model deployed")
        else:
            notify_team("⚠️ A/B test failed, keeping current model")
    else:
        notify_team("❌ New model failed validation")

def should_retrain():
    """Decide if retraining is needed"""
    # Performance drop
    if get_recent_accuracy() < baseline_accuracy - 0.05:
        return True
    
    # Data drift
    if detect_data_drift():
        return True
    
    # Scheduled (weekly)
    if days_since_last_training() > 7:
        return True
    
    return False
```

**Scheduling** (Airflow DAG):
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

dag = DAG(
    'ml_retraining',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1)
)

check_drift = PythonOperator(
    task_id='check_drift',
    python_callable=detect_data_drift,
    dag=dag
)

retrain = PythonOperator(
    task_id='retrain_model',
    python_callable=continuous_training_pipeline,
    dag=dag
)

check_drift >> retrain
```

---

## Quick Answer Questions

### Q13: What is MLflow?

**Answer**: Open-source platform for the complete ML lifecycle:
- **Tracking**: Log experiments, parameters, metrics
- **Projects**: Package code in reusable format
- **Models**: Standard format for deploying models
- **Registry**: Centralized model store with versioning

### Q14: What is DVC (Data Version Control)?

**Answer**: Version control system for ML data and models:
- Git-like commands for data (`dvc add`, `dvc push`)
- Stores data in remote storage (S3, GCS, Azure)
- Tracks data changes with lightweight `.dvc` files
- Creates reproducible ML pipelines

### Q15: What is model drift?

**Answer**: Degradation of model performance over time due to:
- **Data drift**: Input feature distributions change
- **Concept drift**: Relationship between features and target changes
- **Label drift**: Target distribution changes

Example: Fraud model trained in 2020 sees new fraud patterns in 2026.

### Q16: What is A/B testing in ML?

**Answer**: Comparing two model versions by serving both to users:
- Route 90% traffic to Model A (current)
- Route 10% traffic to Model B (new)
- Compare performance metrics
- Gradually shift if Model B better

### Q17: What is feature store?

**Answer**: Centralized repository for ML features:
- Stores computed features
- Serves features for training and inference
- Ensures consistency between training/serving
- Examples: Feast, Tecton

### Q18: What is model serving?

**Answer**: Deploying models to make predictions:
- **Batch**: Predict on large datasets offline
- **Online**: Real-time API predictions
- **Streaming**: Predictions on event streams

### Q19: What is model monitoring?

**Answer**: Tracking deployed model health:
- Performance metrics (accuracy, latency)
- Data quality (missing values, ranges)
- Drift detection
- Business metrics

### Q20: What is CI/CD for ML?

**Answer**: Automated pipelines for ML:
- **CI**: Automated testing (code, data, model validation)
- **CD**: Automated deployment to production
- Includes: data validation, model testing, canary deployments

---

## Tips for MLOps Interviews

1. **Emphasize End-to-End**: Show you understand the full lifecycle
2. **Practical Experience**: Have examples from real projects
3. **Tools Knowledge**: Know MLflow, DVC, or similar tools
4. **Production Focus**: Talk about deployment, monitoring, not just training
5. **Business Impact**: Connect technical decisions to business outcomes

---

**Next Level**: Ready for intermediate? Check out [Intermediate Interview Questions](../02-intermediate/interview-questions-intermediate.md)
