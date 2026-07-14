# Model Versioning

## Overview

Model versioning is the practice of tracking different versions of trained ML models, similar to how Git versions code. It's essential for reproducibility, collaboration, and production deployment.

## Why Version Models?

**The Problem:**
```
❌ "model_final.pkl"
❌ "model_final_v2.pkl"
❌ "model_final_v2_actually_final.pkl"
❌ "model_FINAL_FOR_REAL.pkl"
```

**The Solution:**
```
✅ model v1.0.0 - Baseline RandomForest
✅ model v1.1.0 - Added new features
✅ model v2.0.0 - Switched to GradientBoosting
✅ model v2.1.0 - Hyperparameter tuning
```

## What to Version

### 1. Model Artifacts
- Trained model file (`.pkl`, `.h5`, `.pt`)
- Model architecture/configuration
- Training checkpoints

### 2. Model Metadata
- Training parameters
- Performance metrics
- Training data version
- Code version (git commit)
- Training date and duration
- Environment (Python version, libraries)

### 3. Preprocessing Artifacts
- Scalers, encoders, transformers
- Feature engineering pipelines
- Vocabulary files (for NLP)

## Semantic Versioning for ML

Use semantic versioning: `MAJOR.MINOR.PATCH`

### MAJOR (1.0.0 → 2.0.0)
- Complete model rewrite
- Different algorithm
- Breaking changes in API
- New problem formulation

### MINOR (1.0.0 → 1.1.0)
- New features added
- Non-breaking improvements
- New data sources
- Enhanced preprocessing

### PATCH (1.0.0 → 1.0.1)
- Bug fixes
- Hyperparameter tuning
- Small improvements
- Retraining with same setup

## Versioning with MLflow

```python
import mlflow
import mlflow.sklearn

# Log model with version
with mlflow.start_run() as run:
    # Train model
    model.fit(X_train, y_train)
    
    # Log metrics
    mlflow.log_metric("accuracy", 0.92)
    
    # Log model to registry with version
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name="customer-churn-predictor"
    )
    
    print(f"Model version created: {run.info.run_id}")
```

## Version Comparison

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Get all versions
versions = client.search_model_versions("name='customer-churn-predictor'")

print("Version | Stage | Accuracy | Date")
print("-" * 50)

for version in versions:
    run = client.get_run(version.run_id)
    accuracy = run.data.metrics.get('accuracy', 'N/A')
    
    print(f"v{version.version} | {version.current_stage} | "
          f"{accuracy} | {version.creation_timestamp}")
```

## Best Practices

### 1. Naming Convention
```python
# Use descriptive names
model_name = "churn-predictor-rf-v2"

# Include metadata in tags
mlflow.set_tags({
    "algorithm": "random_forest",
    "data_version": "2024-01",
    "experiment_type": "baseline"
})
```

### 2. Git Integration
```python
import subprocess

def get_git_info():
    """Get current git commit"""
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
    branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()
    
    return {'commit': commit, 'branch': branch}

# Log with model
with mlflow.start_run():
    git_info = get_git_info()
    mlflow.log_params(git_info)
```

### 3. Reproducibility Checklist
```python
def log_reproducibility_info(model, data):
    """Log everything needed to reproduce"""
    
    mlflow.log_params({
        'python_version': sys.version,
        'sklearn_version': sklearn.__version__,
        'data_hash': hashlib.md5(data.tobytes()).hexdigest(),
        'random_seed': 42,
        'training_date': datetime.now().isoformat()
    })
    
    # Save environment
    with open('requirements.txt', 'w') as f:
        subprocess.call(['pip', 'freeze'], stdout=f)
    mlflow.log_artifact('requirements.txt')
```

## Key Takeaways

✅ Use semantic versioning (MAJOR.MINOR.PATCH)  
✅ Version models with metadata  
✅ Track preprocessing artifacts  
✅ Integrate with Git  
✅ Enable reproducibility

## Interview Questions

**Q: Why version models separately from code?**
A: Models are artifacts trained on data at specific points in time, unlike code which is deterministic. Same code + different data = different model.

**Q: What makes a model reproducible?**
A: Versioned code, versioned data, logged parameters, saved random seeds, and documented environment.

---

**Next:** [ML Model Registry](08-model-registry.md)  
**Practice:** [Lab 04 - Model Registry](../mlops-practice/lab-04-model-registry/)
