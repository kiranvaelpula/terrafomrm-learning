# What is MLOps?

## Overview

**MLOps** (Machine Learning Operations) is a set of practices that combines Machine Learning, DevOps, and Data Engineering to deploy and maintain ML systems in production reliably and efficiently.

## The Challenge

Traditional ML development faces these problems:

```
Data Scientist's Laptop ✅ → Production ❌
- Works on my machine
- Can't reproduce results
- Model degrades over time
- Slow deployment (weeks/months)
- No monitoring
```

## MLOps Solution

```
Automated ML Pipeline:
Data → Feature Engineering → Training → Validation → Deployment → Monitoring
  ↓           ↓                 ↓           ↓            ↓            ↓
Version   Version           Version     Register     Serve      Track Drift
Control   Control           Control     Model        Model      Auto-retrain
```

## Core Components

### 1. Experiment Tracking
Track every experiment to ensure reproducibility:

```python
import mlflow

with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_param("epochs", 100)
    mlflow.log_metric("accuracy", 0.95)
    mlflow.sklearn.log_model(model, "model")
```

### 2. Model Versioning
Every model version is tracked and retrievable:

```
models/
├── model_v1.pkl  # Baseline: 85% accuracy
├── model_v2.pkl  # With feature X: 90% accuracy  
└── model_v3.pkl  # Current production: 92% accuracy
```

### 3. Data Versioning
Track data changes like code:

```bash
# Track dataset
dvc add data/training_data.csv

# Commit to git
git add data/training_data.csv.dvc
git commit -m "Update training data"

# Push data to remote storage
dvc push
```

### 4. Continuous Training (CT)
Automatically retrain when:
- New data arrives
- Model performance drops
- Schedule-based (weekly/monthly)

### 5. Continuous Deployment (CD)
Deploy models automatically after validation:

```yaml
# CI/CD Pipeline
stages:
  - train
  - validate
  - deploy

deploy_model:
  script:
    - if [ accuracy > 0.90 ]; then
        deploy_to_production
      fi
```

### 6. Model Monitoring
Track model performance in production:

```python
# Monitor predictions
metrics = {
    'prediction_latency': 50ms,
    'accuracy': 0.89,  # Down from 0.92!
    'data_drift_detected': True
}

if metrics['accuracy'] < threshold:
    trigger_retraining()
```

## MLOps vs DevOps

| Aspect | DevOps | MLOps |
|--------|---------|-------|
| **Artifacts** | Code | Code + Data + Models |
| **Testing** | Unit/Integration | Statistical/Data validation |
| **Deployment** | Binary/Container | Model + Feature pipeline |
| **Monitoring** | Logs/Metrics | Model performance + Data drift |
| **Rollback** | Previous version | Previous model version |

## MLOps Lifecycle

### 1. Data Pipeline
```python
# Data collection and validation
def prepare_data():
    data = load_data('s3://bucket/data')
    validate_schema(data)
    clean_data = preprocess(data)
    save_version(clean_data, version='v1.2')
    return clean_data
```

### 2. Feature Engineering
```python
# Create and store features
from feast import FeatureStore

store = FeatureStore(repo_path=".")
features = store.get_online_features(
    features=['user_age', 'purchase_history'],
    entity_rows=[{'user_id': 123}]
)
```

### 3. Model Training
```python
# Training with tracking
def train_model(data, params):
    mlflow.start_run()
    mlflow.log_params(params)
    
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    mlflow.log_metric("accuracy", accuracy)
    mlflow.sklearn.log_model(model, "model")
    
    return model
```

### 4. Model Validation
```python
# Validate before deployment
def validate_model(model, test_data):
    predictions = model.predict(test_data)
    
    # Performance checks
    assert accuracy_score(y_test, predictions) > 0.85
    
    # Fairness checks
    assert demographic_parity(predictions) < 0.1
    
    # Robustness checks
    assert adversarial_accuracy(model) > 0.80
    
    return True
```

### 5. Model Deployment
```python
# Deploy to production
from seldon_core.seldon_client import SeldonClient

client = SeldonClient(deployment_name="my-model")
client.predict(data={"instances": [[1.0, 2.0, 3.0]]})
```

### 6. Monitoring & Retraining
```python
# Monitor and trigger retraining
def monitor_model():
    metrics = get_production_metrics()
    
    if metrics['accuracy'] < 0.85:
        trigger_retraining_pipeline()
    
    if detect_data_drift(metrics):
        alert_team()
        trigger_retraining_pipeline()
```

## Benefits

### For Data Scientists
✅ **Focus on modeling**: Less time on deployment
✅ **Reproducibility**: Every experiment tracked
✅ **Collaboration**: Shared experiments and models
✅ **Faster iteration**: Automated pipelines

### For ML Engineers
✅ **Automation**: Reduce manual work
✅ **Reliability**: Consistent deployments
✅ **Scalability**: Deploy many models
✅ **Monitoring**: Track model health

### For Organizations
✅ **Faster time-to-value**: Days instead of months
✅ **Better models**: Continuous improvement
✅ **Lower costs**: Automated operations
✅ **Compliance**: Audit trail for models

## Real-World Example

### Without MLOps
```
Week 1-2: Data scientist trains model on laptop
Week 3: Share model.pkl via email
Week 4: Engineer tries to deploy
Week 5: "Works on my machine" debugging
Week 6: Manual deployment to prod
Week 7: Model fails, no monitoring
Week 8: Start over...
```
**Time to Production**: 8+ weeks

### With MLOps
```
Day 1: Data scientist uses shared platform
Day 2: Automated pipeline trains & validates
Day 3: Auto-deployment to staging
Day 4: A/B test in production
Day 5: Full rollout with monitoring
```
**Time to Production**: 5 days

## MLOps Maturity Levels

### Level 0: Manual Process
- Jupyter notebooks
- Manual deployment
- No tracking
- Rare releases

### Level 1: ML Pipeline Automation
- Automated training
- Experiment tracking
- Some versioning
- Occasional releases

### Level 2: CI/CD Pipeline Automation
- Automated deployment
- Comprehensive testing
- Full versioning
- Frequent releases

### Level 3: Full MLOps Automation
- Auto-retraining
- Production monitoring
- Auto-remediation
- Continuous deployment

## Getting Started Checklist

Week 1: Setup
- [ ] Choose experiment tracking tool (MLflow)
- [ ] Set up model registry
- [ ] Configure data versioning (DVC)

Week 2: Automation
- [ ] Create training pipeline
- [ ] Add model validation
- [ ] Set up CI/CD

Week 3: Production
- [ ] Deploy first model
- [ ] Configure monitoring
- [ ] Set up alerting

Week 4: Optimization
- [ ] Implement A/B testing
- [ ] Add drift detection
- [ ] Enable auto-retraining

## Common Pitfalls

❌ **Treating ML like software**: ML needs data and statistical testing
❌ **No data versioning**: Can't reproduce results
❌ **Ignoring monitoring**: Models degrade over time
❌ **Manual processes**: Doesn't scale
❌ **No validation**: Bad models in production

## Tools Landscape

```
Experiment Tracking: MLflow, Weights & Biases
Data Versioning: DVC, Pachyderm
Model Registry: MLflow, ModelDB
Deployment: Seldon, KServe, SageMaker
Monitoring: Evidently, WhyLabs, Arize
Feature Stores: Feast, Tecton
Orchestration: Kubeflow, Apache Airflow
```

## Success Metrics

Track these to measure MLOps success:

```yaml
Development Velocity:
  - experiments_per_week: 20
  - model_training_time: < 2 hours
  - time_to_production: < 1 week

Model Quality:
  - production_accuracy: > 90%
  - model_uptime: 99.9%
  - prediction_latency: < 100ms

Operational Efficiency:
  - deployment_frequency: Daily
  - mean_time_to_detection: < 1 hour
  - mean_time_to_recovery: < 4 hours
```

## Next Steps

Continue to [ML Lifecycle Overview](02-ml-lifecycle.md) to understand the complete machine learning workflow.

---

**Remember**: MLOps is not just tools—it's a culture of collaboration between data scientists, engineers, and operations teams to deliver reliable ML systems.
