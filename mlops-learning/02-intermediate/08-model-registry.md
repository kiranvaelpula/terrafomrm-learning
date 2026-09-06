# ML Model Registry

## Overview

A model registry is a centralized repository for managing, versioning, and governing ML models throughout their lifecycle. Think of it as "GitHub for ML models."

## 📖 Understanding the Model Registry (Intuition First)

If model versioning is like keeping every batch of medicine labeled, the model registry is the **central pharmacy shelf system** that decides which batch is currently dispensed to patients, which is in trials, and which is retired. Versioning answers "what are all the models we've made?"; the registry answers "which one is *live* right now, which is being tested, and how do we promote or roll back between them?"

The core idea is **stages**. A model in the registry isn't just a version — it lives in a stage like `Staging`, `Production`, or `Archived`. This gives you a single source of truth: instead of someone asking "which model file is actually running in prod?" and getting three different answers, everyone queries the registry and gets one authoritative answer. When you want to release a new model, you *promote* it from Staging to Production; if it misbehaves, you *transition* the old one back — no fumbling with file paths.

Why is a central registry so valuable? Because in a real organization, models are scattered — on laptops, in S3 buckets, in someone's notebook. Without a registry, deployment is manual and error-prone, there's no audit trail, and collaboration is painful. The registry centralizes storage, standardizes the promotion workflow, tracks lineage (which data and code produced this model), and often integrates directly with deployment pipelines so promoting to Production can *automatically* trigger a deploy.

Think of it as the governance layer of MLOps: it's where model *management* meets model *operations*. It answers the questions auditors and on-call engineers actually ask — who approved this model, when did it go live, what did it replace, and how do I revert.

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

## 🎯 Interview Quick Points

- A model registry is "GitHub for ML models" — centralized storage, versioning, governance
- The core concept is **stages**: Staging → Production → Archived
- Provides a **single source of truth** for "which model is live right now?"
- **Promotion** moves a model from Staging to Production; rollback transitions back
- Solves scattered models, manual deployment, and missing audit trails
- Tracks **lineage** — which data and code produced each model
- Often integrates with CI/CD so promoting to Production auto-triggers a deploy
- It's the **governance layer** of MLOps — approvals, audit, who deployed what and when
- Versioning = "all models we made"; registry = "which is live/staging/retired"
- **MLflow Model Registry**, SageMaker Model Registry are common implementations

**Next:** [Model Deployment Strategies](09-deployment-strategies.md)  
**Practice:** [Lab 04 - Model Registry](../mlops-practice/lab-04-model-registry/)
