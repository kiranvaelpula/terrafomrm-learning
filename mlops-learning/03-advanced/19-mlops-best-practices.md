# MLOps Best Practices

## Overview

Production ML requires following established best practices to ensure reliability, scalability, and maintainability.

## 📖 Understanding MLOps Best Practices (Intuition First)

Best practices are the accumulated scar tissue of teams who learned the hard way. Every rule here exists because someone, somewhere, skipped it and got burned — a model that couldn't be reproduced, a data leak that inflated accuracy, a silent decay that cost millions, a deployment nobody could roll back. Think of best practices as the building code for ML: not bureaucracy, but the minimum standards that keep the structure from collapsing.

The unifying theme across all MLOps best practices is **treating ML as an engineering discipline, not a science experiment**. A research notebook can be messy, one-off, and irreproducible — that's fine for exploration. But the moment a model touches production and real users depend on it, it needs the same rigor as any critical software system: version control, testing, monitoring, documentation, and automation. The most common failure in ML organizations is trying to run production ML with a research mindset.

If you internalize just a few principles, make them these: **reproducibility** (you can recreate any result from versioned code + data + config), **automation** (humans don't manually copy models to servers — pipelines do), **monitoring** (you assume models will decay and watch for it), and **validation gates** (nothing reaches production without passing quality checks). Almost every specific best practice — project structure, config management, testing, CI/CD — is a concrete expression of one of these principles.

The other quiet truth is that MLOps is as much about **culture and collaboration** as tooling. ML sits at the intersection of data scientists, ML engineers, and operations, who historically speak different languages. Best practices like standardized project structure, shared feature stores, and clear model documentation exist partly to make these groups work together smoothly. The best tooling in the world fails if the team treats handoffs as someone else's problem.

## Code Organization

### Project Structure
```
ml-project/
├── data/                   # Data files
├── notebooks/              # Exploratory notebooks
├── src/
│   ├── data/              # Data processing
│   ├── features/          # Feature engineering
│   ├── models/            # Model code
│   ├── serving/           # API code
│   └── utils/             # Utilities
├── tests/                 # Unit & integration tests
├── configs/               # Configuration files
├── models/                # Saved models
├── docs/                  # Documentation
├── .dvc/                  # DVC files
├── .github/workflows/     # CI/CD
├── requirements.txt       # Dependencies
├── setup.py              # Package setup
└── README.md             # Project docs
```

### Modular Code
```python
# Bad: Everything in one file
def train_model():
    # 500 lines of code...

# Good: Separated concerns
from src.data import load_data, preprocess
from src.models import train_model
from src.evaluation import evaluate_model

def main():
    data = load_data()
    data = preprocess(data)
    model = train_model(data)
    metrics = evaluate_model(model)
```

## Configuration Management

### Use Config Files
```yaml
# config.yaml
data:
  train_path: "data/train.csv"
  test_size: 0.2

model:
  type: "random_forest"
  n_estimators: 100
  max_depth: 10

training:
  epochs: 50
  batch_size: 32
  learning_rate: 0.001
```

```python
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

model = train_model(config['model'])
```

## Testing

### Test Everything
```python
# test_data.py
def test_data_loading():
    df = load_data('data/test.csv')
    assert len(df) > 0
    assert 'target' in df.columns

# test_model.py
def test_model_prediction():
    model = load_model()
    sample = create_sample()
    prediction = model.predict([sample])
    assert 0 <= prediction[0] <= 1

# test_api.py
def test_prediction_endpoint():
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 200
```

## Documentation

### Document Models
```python
"""
Customer Churn Prediction Model

Purpose: Predict customer churn probability
Algorithm: Random Forest Classifier
Training Data: customers_2024_01.csv (10,000 samples)
Features: 15 customer attributes
Performance: 92% accuracy, 89% F1-score
Last Updated: 2024-01-15
Owner: Data Science Team
"""
```

### API Documentation
```python
@app.post("/predict", 
          summary="Predict customer churn",
          description="Returns churn probability for a customer")
def predict(customer: CustomerData):
    """
    Predict customer churn probability.
    
    Parameters:
    - customer: Customer features
    
    Returns:
    - prediction: Churn probability (0-1)
    - risk_level: HIGH/MEDIUM/LOW
    """
    pass
```

## Security

### Protect Secrets
```python
# Bad
API_KEY = "sk-1234567890abcdef"

# Good
import os
API_KEY = os.getenv('API_KEY')
```

### Validate Input
```python
from pydantic import BaseModel, validator

class CustomerData(BaseModel):
    age: int
    income: float
    
    @validator('age')
    def age_must_be_valid(cls, v):
        if not 18 <= v <= 100:
            raise ValueError('Invalid age')
        return v
```

## Monitoring

### Log Everything
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def predict(data):
    logger.info(f"Prediction request: {data.id}")
    
    try:
        prediction = model.predict(data)
        logger.info(f"Prediction: {prediction}")
        return prediction
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise
```

### Track Metrics
```python
from prometheus_client import Counter, Histogram

predictions_total = Counter('predictions_total', 'Total predictions')
prediction_latency = Histogram('prediction_latency_seconds', 'Latency')

@prediction_latency.time()
def predict(data):
    result = model.predict(data)
    predictions_total.inc()
    return result
```

## Reproducibility

### Pin Dependencies
```txt
# requirements.txt
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
```

### Set Random Seeds
```python
import random
import numpy as np
import torch

def set_seeds(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
```

## Data Management

### Version Data
```bash
# Track with DVC
dvc add data/train.csv
git add data/train.csv.dvc
git commit -m "Add training data v1"
```

### Validate Data
```python
def validate_data(df):
    assert len(df) > 1000, "Too few samples"
    assert df['age'].between(18, 100).all(), "Invalid ages"
    assert df.isnull().sum().sum() < len(df) * 0.1, "Too many nulls"
```

## Collaboration

### Code Reviews
- Review all ML code
- Check for data leakage
- Verify reproducibility
- Test before merge

### Documentation
- Document decisions
- Explain model choices
- Share experiment results
- Maintain changelog

## Performance

### Optimize Inference
```python
# Cache predictions
from functools import lru_cache

@lru_cache(maxsize=1000)
def predict_cached(customer_id):
    return model.predict(get_features(customer_id))

# Batch predictions
def predict_batch(customers):
    features = [get_features(c) for c in customers]
    return model.predict(features)  # Single call
```

### Monitor Resources
```python
import psutil
import time

def train_with_monitoring():
    start = time.time()
    
    model.fit(X_train, y_train)
    
    duration = time.time() - start
    memory = psutil.Process().memory_info().rss / 1024 / 1024
    
    print(f"Training time: {duration:.2f}s")
    print(f"Memory used: {memory:.2f}MB")
```

## Deployment

### Health Checks
```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "version": "1.0.0"
    }
```

### Gradual Rollout
```python
# Start with 5% traffic
# Increase to 25%, 50%, 100% gradually
# Monitor metrics at each stage
```

## Common Anti-Patterns to Avoid

❌ Training and serving code duplication  
❌ No version control  
❌ Hard-coded configuration  
❌ No tests  
❌ No monitoring  
❌ Ignoring data drift  
❌ No documentation  
❌ Manual deployment

## Key Takeaways

✅ Organize code properly  
✅ Use configuration files  
✅ Test everything  
✅ Document thoroughly  
✅ Version data and models  
✅ Monitor production  
✅ Automate workflows  
✅ Follow security best practices

---

## 🎯 Interview Quick Points

- Best practices are accumulated lessons from teams who got burned skipping them
- Core theme: **treat ML as an engineering discipline, not a science experiment**
- The most common org failure: running production ML with a research mindset
- Four pillars: **reproducibility, automation, monitoring, validation gates**
- Reproducibility = recreate any result from versioned code + data + config
- Automation = pipelines deploy models, not humans copying files
- Monitoring = assume models decay, watch for it continuously
- Validation gates = nothing reaches prod without passing quality checks
- MLOps is as much **culture/collaboration** (DS + ML eng + ops) as tooling
- Standardized structure, feature stores, and documentation smooth team handoffs

**Next:** [Real-World Project](20-real-world-project.md)  
**Practice:** [Lab 10 - End-to-End Project](../mlops-practice/lab-10-e2e-project/)
