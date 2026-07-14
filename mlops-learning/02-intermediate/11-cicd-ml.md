# CI/CD for Machine Learning

## Overview

Continuous Integration and Continuous Deployment (CI/CD) for ML automates testing, validation, and deployment of ML models. It's DevOps principles applied to machine learning.

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

**Next:** [Data Versioning](12-data-versioning.md)  
**Practice:** [Lab 07 - CI/CD for ML](../mlops-practice/lab-07-cicd-ml/)
