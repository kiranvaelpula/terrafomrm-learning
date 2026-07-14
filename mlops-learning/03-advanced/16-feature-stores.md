# Feature Stores

## Overview

A feature store is a centralized repository for storing, managing, and serving ML features. It solves training-serving skew and enables feature reuse.

## Why Feature Stores?

**Without Feature Store:**
- Feature code duplicated (training vs serving)
- Training-serving skew
- No feature reuse across teams
- Inconsistent feature definitions

**With Feature Store:**
- Single source of truth
- Consistent features everywhere
- Easy feature sharing
- Online + offline serving

## Feast Framework

### Setup

```bash
pip install feast
feast init my_feature_repo
cd my_feature_repo
```

### Define Features

```python
from feast import Entity, Feature, FeatureView, FileSource, ValueType
from datetime import timedelta

# Define entity
customer = Entity(
    name="customer",
    value_type=ValueType.STRING,
    description="Customer ID"
)

# Define data source
customer_source = FileSource(
    path="data/customer_features.parquet",
    event_timestamp_column="event_timestamp"
)

# Define feature view
customer_features = FeatureView(
    name="customer_features",
    entities=["customer"],
    ttl=timedelta(days=1),
    features=[
        Feature(name="age", dtype=ValueType.INT64),
        Feature(name="income", dtype=ValueType.DOUBLE),
        Feature(name="tenure_months", dtype=ValueType.INT64)
    ],
    online=True,
    batch_source=customer_source
)
```

### Apply to Store

```bash
feast apply
```

### Training (Offline Features)

```python
from feast import FeatureStore
import pandas as pd

store = FeatureStore(repo_path=".")

# Entity dataframe
entity_df = pd.DataFrame({
    "customer_id": ["C001", "C002", "C003"],
    "event_timestamp": pd.Timestamp.now()
})

# Get historical features
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "customer_features:age",
        "customer_features:income",
        "customer_features:tenure_months"
    ]
).to_df()

# Train model with training_df
```

### Inference (Online Features)

```python
# Get online features for real-time prediction
online_features = store.get_online_features(
    features=[
        "customer_features:age",
        "customer_features:income",
        "customer_features:tenure_months"
    ],
    entity_rows=[{"customer": "C001"}]
).to_dict()

# Make prediction
prediction = model.predict(online_features)
```

## Key Benefits

✅ **Training-Serving Consistency:** Same features everywhere  
✅ **Feature Reuse:** Share across models and teams  
✅ **Fast Online Serving:** Millisecond latency  
✅ **Time Travel:** Point-in-time correct features  
✅ **Governance:** Track feature lineage

## Best Practices

✅ Define features once, use everywhere  
✅ Version features like code  
✅ Monitor feature quality  
✅ Document features  
✅ Use online serving for real-time  
✅ Use offline serving for training

---

**Next:** [ML on Kubernetes](17-ml-kubernetes.md)  
**Practice:** [Lab 08 - Feature Store](../mlops-practice/lab-08-feature-store/)
