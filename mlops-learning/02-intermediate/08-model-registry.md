# ML Model Registry

## Overview

A model registry is a centralized repository for managing, versioning, and governing ML models throughout their lifecycle. Think of it as "GitHub for ML models."

## Why Use a Model Registry?

**Without Registry:**
- Models scattered across different locations
- No clear production model
- Manual deployment process
- No audit trail
- Difficult collaboration

**With Registry:**
- Centralized model storage
- Clear staging (dev/staging/production)
- Automated deployment workflows
- Complete lineage tracking
- Team collaboration

## Model Lifecycle Stages

```
None → Staging → Production → Archived
```

### Stage Descriptions

**None**: Newly registered, not yet validated  
**Staging**: Validated, ready for pre-production testing  
**Production**: Deployed and serving predictions  
**Archived**: Deprecated, kept for historical reference

## MLflow Model Registry

### Registering a Model

```python
import mlflow
import mlflow.sklearn

# Register during training
with mlflow.start_run():
    model.fit(X_train, y_train)
    
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name="churn-predictor"
    )
```

### Managing Model Stages

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Transition to Staging
client.transition_model_version_stage(
    name="churn-predictor",
    version=3,
    stage="Staging"
)

# After validation, promote to Production
client.transition_model_version_stage(
    name="churn-predictor",
    version=3,
    stage="Production",
    archive_existing_versions=True  # Archive old production models
)
```

### Loading Models by Stage

```python
import mlflow.pyfunc

# Load production model
model = mlflow.pyfunc.load_model(
    model_uri="models:/churn-predictor/Production"
)

# Make predictions
predictions = model.predict(new_data)
```

## Model Governance

### Adding Descriptions

```python
client.update_registered_model(
    name="churn-predictor",
    description="Random Forest model for predicting customer churn. "
                "Trained on 2024-01 data with 92% accuracy."
)
```

### Adding Tags and Metadata

```python
client.set_model_version_tag(
    name="churn-predictor",
    version="3",
    key="validation_status",
    value="passed"
)

client.set_model_version_tag(
    name="churn-predictor",
    version="3",
    key="approved_by",
    value="data-science-team"
)
```

## Best Practices

✅ Use clear, descriptive model names  
✅ Always validate before promoting to production  
✅ Archive old versions, don't delete  
✅ Document model purpose and limitations  
✅ Tag models with metadata  
✅ Implement approval workflows

## Key Takeaways

✅ Model registry centralizes model management  
✅ Stages enable controlled deployment  
✅ Lineage tracking provides audit trail  
✅ Metadata enables governance  
✅ Integration with CI/CD automates workflows

---

**Next:** [Model Deployment Strategies](09-deployment-strategies.md)  
**Practice:** [Lab 04 - Model Registry](../mlops-practice/lab-04-model-registry/)
