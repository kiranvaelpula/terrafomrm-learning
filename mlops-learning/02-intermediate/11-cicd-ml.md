# CI/CD for Machine Learning

## Overview

Continuous Integration and Continuous Deployment (CI/CD) for ML automates testing, validation, and deployment of ML models. It's DevOps principles applied to machine learning.

## 📖 Understanding CI/CD for ML (Intuition First)

In traditional software, CI/CD is an assembly line: you push code, and it's automatically built, tested, and shipped — no human manually copying files to servers. CI/CD for ML is the same assembly line idea, but with an extra worker on the line whose only job is *training and validating a model*. The pipeline doesn't just test code; it retrains the model, checks that the new model is actually good enough, and only then ships it.

The reason ML needs its own flavor of CI/CD is that ML has three things that can trigger a release, not one. In normal software, you deploy when *code* changes. In ML, you might deploy because the code changed, OR because new *data* arrived, OR because the live model's performance *decayed*. That third trigger — "the model got worse, retrain and redeploy automatically" — is unique to ML and is why the pipeline includes a training and validation stage that plain DevOps pipelines don't have.

The most important ML-specific gate is **model validation**. In software CI, tests check "does the code work?" In ML CI, you also need "is this model good enough to ship?" — checking accuracy against a threshold, comparing against the currently deployed model (don't ship a worse one!), and running fairness and robustness checks. A model can pass all code tests and still be a terrible model, so this statistical gate is essential before anything reaches production.

Put together, an ML CI/CD pipeline typically flows: code push → build → test code → train model → validate model (the ML gate) → deploy (often canary) → monitor. And critically, the monitoring stage can *loop back* and trigger the whole pipeline again when it detects the model has decayed. That closed loop — where production monitoring automatically kicks off retraining and redeployment — is the hallmark of mature MLOps and what people mean by "Continuous Training (CT)."

## CI/CD Pipeline Stages

```
Code Push → Build → Test → Train → Validate → Deploy → Monitor
```

### 1. Continuous Integration (CI)
- Automated code testing
- Data validation
- Model testing
- Integration tests

### 2. Continuous Training (CT)
- Automated model retraining
- Triggered by new data or schedule
- Hyperparameter optimization

### 3. Continuous Deployment (CD)
- Automated model deployment
- Staged rollouts
- Production monitoring

## GitHub Actions Example

```yaml
name: ML Pipeline

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/

  train:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Train model
        run: python train.py
      
      - name: Validate model
        run: python validate.py --min-accuracy 0.75

  deploy:
    needs: train
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: kubectl apply -f k8s/deployment.yaml
```

## Testing in ML

### 1. Data Tests
```python
def test_data_schema():
    df = load_data()
    assert 'target' in df.columns
    assert df['age'].between(18, 100).all()

def test_data_distribution():
    df = load_data()
    assert 0.2 < df['target'].mean() < 0.4  # Expected churn rate
```

### 2. Model Tests
```python
def test_model_accuracy():
    model = load_model()
    X_test, y_test = load_test_data()
    
    accuracy = model.score(X_test, y_test)
    assert accuracy > 0.75, f"Accuracy {accuracy} below threshold"

def test_model_inference():
    model = load_model()
    sample = create_sample_input()
    
    prediction = model.predict([sample])
    assert prediction.shape == (1,)
    assert 0 <= prediction[0] <= 1
```

### 3. API Tests
```python
def test_prediction_endpoint():
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 200
    assert 'prediction' in response.json()
```

## Automated Model Validation

```python
def validate_model(model, X_test, y_test, baseline_metrics):
    """Validate new model against baseline"""
    
    # Calculate metrics
    metrics = calculate_metrics(model, X_test, y_test)
    
    # Compare with baseline
    checks = {
        'accuracy': metrics['accuracy'] >= baseline_metrics['accuracy'] * 0.95,
        'precision': metrics['precision'] >= baseline_metrics['precision'] * 0.90,
        'recall': metrics['recall'] >= baseline_metrics['recall'] * 0.90
    }
    
    if not all(checks.values()):
        raise ValueError(f"Model validation failed: {checks}")
    
    return True
```

## Deployment Gates

```python
# Only deploy if validation passes
if validate_model(new_model, test_data, baseline):
    deploy_to_production(new_model)
else:
    send_alert("Model validation failed")
    keep_current_model()
```

## Best Practices

✅ Automate everything  
✅ Test rigorously (data, model, API)  
✅ Use deployment gates  
✅ Enable quick rollback  
✅ Monitor after deployment  
✅ Version control everything

## Key Takeaways

✅ CI/CD automates ML lifecycle  
✅ Testing prevents bad models in production  
✅ Continuous training keeps models fresh  
✅ Deployment gates ensure quality  
✅ Monitoring validates deployments

---

## 🎯 Interview Quick Points

- CI/CD for ML = DevOps automation (build, test, deploy) plus a train-and-validate stage
- Three release triggers in ML: **code change, new data, OR model decay** (only code in normal software)
- **Continuous Training (CT)** is the ML-specific addition — auto-retrain on new data/decay/schedule
- The key ML gate is **model validation**: is the new model good enough AND better than the current one?
- Validation checks: accuracy threshold, comparison vs production model, fairness, robustness
- A model can pass all code tests and still be a bad model — hence the statistical gate
- Typical flow: push → build → test → train → validate → deploy (canary) → monitor
- Monitoring **loops back** to trigger retraining — the closed loop of mature MLOps
- Tools: GitHub Actions/GitLab CI/Jenkins + MLflow + model validation steps
- Deploy models with canary/shadow strategies, not big-bang replacement

**Next:** [Data Versioning](12-data-versioning.md)  
**Practice:** [Lab 07 - CI/CD for ML](../mlops-practice/lab-07-cicd-ml/)
