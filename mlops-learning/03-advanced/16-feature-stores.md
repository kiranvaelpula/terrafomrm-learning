# Feature Stores

## Overview

A feature store is a centralized repository for storing, managing, and serving ML features. It solves training-serving skew and enables feature reuse.

## 📖 Understanding Feature Stores (Intuition First)

Imagine a big restaurant where five chefs each independently chop onions their own way, in their own station, with no coordination. Wasteful, inconsistent, and when a dish tastes off nobody knows whose onions were the problem. Now imagine a shared prep kitchen that chops onions once, consistently, and every chef pulls from it. That shared prep kitchen is a feature store: features are computed once, centrally, and reused everywhere — consistently.

The killer problem feature stores solve is **training/serving skew**. During training, a data scientist computes "average purchase over last 30 days" in a pandas notebook. Later, an engineer re-implements that same feature in production serving code — and subtly gets it wrong (different time window, different handling of nulls). Now the model sees features in production that differ from what it trained on, and predictions silently degrade. A feature store guarantees the *exact same* feature computation is used for both training and serving, eliminating this entire class of bug.

The second big win is **reuse**. In a large organization, "customer lifetime value" or "days since last login" gets recomputed by every team building every model — duplicated code, duplicated compute, inconsistent definitions. A feature store lets one team define a feature once, and everyone else discovers and reuses it. It becomes a shared, governed catalog of features, like a library of well-tested functions instead of everyone copy-pasting their own version.

Architecturally, feature stores usually have two halves: an **offline store** (large historical feature values, for training — throughput matters) and an **online store** (low-latency lookups of current feature values, for real-time serving — speed matters). The store keeps them in sync so the feature a model trained on offline is identical to what it fetches online at inference. Tools like **Feast** and **Tecton** provide this. Feature stores are an advanced MLOps component — worth it when you have multiple models, multiple teams, and real training/serving-skew pain.

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

## 🎯 Interview Quick Points

- A feature store centralizes computing, storing, and serving ML features
- Analogy: a shared prep kitchen that chops onions once for all chefs
- Solves **training/serving skew** — same feature computed identically in training and serving
- Enables **feature reuse** — define once, discover and reuse across teams/models
- Two halves: **offline store** (historical, for training) + **online store** (low-latency, for serving)
- The store keeps offline and online in sync
- Eliminates duplicated feature code and inconsistent definitions
- Acts as a governed catalog of features (like a shared, tested function library)
- Tools: **Feast** (open source), **Tecton** (commercial), SageMaker Feature Store
- Advanced component — worth it with multiple models/teams and real skew pain

**Next:** [ML on Kubernetes](17-ml-kubernetes.md)  
**Practice:** [Lab 08 - Feature Store](../mlops-practice/lab-08-feature-store/)
