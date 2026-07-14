# Lab 08: Feature Store with Feast

## Overview
Implement a centralized feature store to manage, version, and serve features for training and inference. Learn online and offline feature serving.

**Duration:** 1 hour  
**Difficulty:** Advanced  
**Prerequisites:** Labs 01-07, feature engineering basics

## Learning Objectives
- Set up Feast feature store
- Define feature views
- Serve features online and offline
- Ensure training-serving consistency
- Version features

## Why Feature Store?

```
Without Feature Store:
- Feature code duplicated
- Training/serving skew
- No feature reuse
- Manual feature updates
❌ Inconsistent, inefficient

With Feature Store:
- Single source of truth
- Consistent features
- Easy reuse across models
- Automated updates
✅ Reliable, efficient
```

## Setup

### 1. Install Feast

```bash
pip install feast
pip install feast[redis]  # For online store
pip install feast[aws]    # For AWS data sources
```

## Implementation

### Step 1: Initialize Feast Project

```bash
# Create feature store
feast init customer_features
cd customer_features

# This creates:
# feature_store.yaml - Configuration
# example.py - Example feature definitions
```

### Step 2: Configure Feature Store

Edit `feature_store.yaml`:

```yaml
project: customer_churn
registry: data/registry.db
provider: local
online_store:
  type: redis
  connection_string: localhost:6379
offline_store:
  type: file
entity_key_serialization_version: 2
```

### Step 3: Define Entities and Features

Create `features.py`:

```python
from datetime import timedelta
from feast import Entity, Feature, FeatureView, FileSource, ValueType

# Define entity
customer = Entity(
    name="customer",
    value_type=ValueType.STRING,
    description="Customer identifier"
)

# Define data source (offline)
customer_data_source = FileSource(
    path="data/customer_features.parquet",
    event_timestamp_column="event_timestamp",
    created_timestamp_column="created_timestamp"
)

# Define feature view
customer_features = FeatureView(
    name="customer_features",
    entities=["customer"],
    ttl=timedelta(days=365),
    features=[
        Feature(name="age", dtype=ValueType.INT64),
        Feature(name="tenure_months", dtype=ValueType.INT64),
        Feature(name="monthly_charges", dtype=ValueType.DOUBLE),
        Feature(name="total_charges", dtype=ValueType.DOUBLE),
        Feature(name="num_support_calls", dtype=ValueType.INT64),
        Feature(name="satisfaction_score", dtype=ValueType.INT64),
        Feature(name="avg_monthly_usage_gb", dtype=ValueType.DOUBLE),
        Feature(name="late_payment_count", dtype=ValueType.INT64),
    ],
    online=True,
    batch_source=customer_data_source,
    tags={"team": "data-science"},
)

# Derived features
customer_derived_features = FeatureView(
    name="customer_derived_features",
    entities=["customer"],
    ttl=timedelta(days=365),
    features=[
        Feature(name="charges_per_month", dtype=ValueType.DOUBLE),
        Feature(name="is_high_value", dtype=ValueType.BOOL),
        Feature(name="churn_risk_score", dtype=ValueType.DOUBLE),
    ],
    online=True,
    batch_source=customer_data_source,
    tags={"team": "data-science", "type": "derived"},
)
```

### Step 4: Generate Feature Data

Create `scripts/generate_features.py`:

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_customer_features(n_customers=10000):
    """Generate customer feature data"""
    
    # Base features
    df = pd.DataFrame({
        'customer_id': [f'C{i:06d}' for i in range(n_customers)],
        'event_timestamp': [datetime.now() - timedelta(days=np.random.randint(0, 365)) 
                           for _ in range(n_customers)],
        'created_timestamp': [datetime.now() for _ in range(n_customers)],
        'age': np.random.randint(18, 80, n_customers),
        'tenure_months': np.random.randint(1, 72, n_customers),
        'monthly_charges': np.random.uniform(20, 120, n_customers),
        'total_charges': np.random.uniform(100, 8000, n_customers),
        'num_support_calls': np.random.poisson(2, n_customers),
        'satisfaction_score': np.random.randint(1, 6, n_customers),
        'avg_monthly_usage_gb': np.random.uniform(1, 100, n_customers),
        'late_payment_count': np.random.poisson(1, n_customers),
    })
    
    # Derived features
    df['charges_per_month'] = df['total_charges'] / (df['tenure_months'] + 1)
    df['is_high_value'] = df['monthly_charges'] > df['monthly_charges'].median()
    df['churn_risk_score'] = (
        0.2 * (df['num_support_calls'] / df['num_support_calls'].max()) +
        0.3 * (1 - df['satisfaction_score'] / 5) +
        0.2 * (df['late_payment_count'] / df['late_payment_count'].max()) +
        0.3 * (1 - df['tenure_months'] / 72)
    )
    
    return df

if __name__ == "__main__":
    df = generate_customer_features()
    
    # Save as parquet
    df.to_parquet('data/customer_features.parquet', index=False)
    
    print(f"✅ Generated {len(df)} customer features")
    print(df.head())
```

Run it:
```bash
python scripts/generate_features.py
```

### Step 5: Apply Features to Store

```bash
# Apply feature definitions
feast apply

# Materialize features to online store
feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")
```

### Step 6: Training with Feature Store

Create `src/train_with_feast.py`:

```python
from feast import FeatureStore
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

def train_model_with_feast():
    """Train model using features from Feast"""
    
    # Initialize feature store
    store = FeatureStore(repo_path=".")
    
    # Get training data
    print("📥 Fetching features from feature store...")
    
    # Entity dataframe (customers to get features for)
    entity_df = pd.DataFrame({
        'customer_id': [f'C{i:06d}' for i in range(10000)],
        'event_timestamp': pd.Timestamp.now()
    })
    
    # Get historical features for training
    training_df = store.get_historical_features(
        entity_df=entity_df,
        features=[
            'customer_features:age',
            'customer_features:tenure_months',
            'customer_features:monthly_charges',
            'customer_features:total_charges',
            'customer_features:num_support_calls',
            'customer_features:satisfaction_score',
            'customer_derived_features:charges_per_month',
            'customer_derived_features:is_high_value',
            'customer_derived_features:churn_risk_score',
        ],
    ).to_df()
    
    print(f"   Retrieved {len(training_df)} training samples")
    
    # Load labels (target)
    labels_df = pd.read_csv('data/customer_labels.csv')
    training_df = training_df.merge(labels_df, on='customer_id')
    
    # Prepare data
    feature_cols = [col for col in training_df.columns 
                   if col not in ['customer_id', 'event_timestamp', 'churn']]
    
    X = training_df[feature_cols]
    y = training_df['churn']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train
    print("🎯 Training model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"✅ Model trained: accuracy = {accuracy:.4f}")
    
    # Save model with feature metadata
    joblib.dump({
        'model': model,
        'features': feature_cols,
        'feature_store_project': 'customer_churn'
    }, 'models/model_feast.pkl')
    
    return model, accuracy

if __name__ == "__main__":
    train_model_with_feast()
```

### Step 7: Online Serving

Create `src/serve_with_feast.py`:

```python
from feast import FeatureStore
import pandas as pd
import joblib
import numpy as np

class ModelWithFeast:
    def __init__(self, model_path='models/model_feast.pkl', feast_repo_path="."):
        """Initialize model with Feast feature store"""
        
        # Load model
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.features = model_data['features']
        
        # Initialize feature store
        self.store = FeatureStore(repo_path=feast_repo_path)
        
        print("✅ Model and feature store initialized")
    
    def predict(self, customer_ids):
        """Make predictions using online features"""
        
        # Get online features
        print(f"📥 Fetching online features for {len(customer_ids)} customers...")
        
        entity_rows = [{'customer': customer_id} for customer_id in customer_ids]
        
        feature_vector = self.store.get_online_features(
            features=[
                'customer_features:age',
                'customer_features:tenure_months',
                'customer_features:monthly_charges',
                'customer_features:total_charges',
                'customer_features:num_support_calls',
                'customer_features:satisfaction_score',
                'customer_derived_features:charges_per_month',
                'customer_derived_features:is_high_value',
                'customer_derived_features:churn_risk_score',
            ],
            entity_rows=entity_rows,
        ).to_dict()
        
        # Convert to DataFrame
        features_df = pd.DataFrame(feature_vector)
        
        # Predict
        predictions = self.model.predict(features_df[self.features])
        probabilities = self.model.predict_proba(features_df[self.features])[:, 1]
        
        return predictions, probabilities

# Example usage
if __name__ == "__main__":
    # Initialize model
    predictor = ModelWithFeast()
    
    # Make predictions
    customer_ids = ['C000001', 'C000002', 'C000003']
    predictions, probabilities = predictor.predict(customer_ids)
    
    # Display results
    print("\n🔮 Predictions:")
    for cid, pred, prob in zip(customer_ids, predictions, probabilities):
        print(f"   {cid}: Churn = {pred}, Probability = {prob:.4f}")
```

### Step 8: Feature Monitoring

Create `src/monitor_features.py`:

```python
from feast import FeatureStore
import pandas as pd
import numpy as np
from scipy import stats

class FeatureMonitor:
    def __init__(self, feast_repo_path="."):
        self.store = FeatureStore(repo_path=feast_repo_path)
    
    def check_feature_freshness(self):
        """Check if features are up to date"""
        # Implementation depends on your data pipeline
        pass
    
    def detect_feature_drift(self, reference_df, current_entity_df):
        """Detect drift in features"""
        
        # Get current features
        current_df = self.store.get_historical_features(
            entity_df=current_entity_df,
            features=[
                'customer_features:age',
                'customer_features:monthly_charges',
                'customer_features:satisfaction_score',
            ],
        ).to_df()
        
        drift_results = {}
        
        for feature in ['age', 'monthly_charges', 'satisfaction_score']:
            # KS test
            statistic, p_value = stats.ks_2samp(
                reference_df[feature],
                current_df[feature]
            )
            
            drift_results[feature] = {
                'p_value': p_value,
                'drift_detected': p_value < 0.05
            }
        
        return drift_results

if __name__ == "__main__":
    monitor = FeatureMonitor()
    print("✅ Feature monitoring initialized")
```

## Key Commands

```bash
# Apply feature definitions
feast apply

# Materialize features to online store
feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")

# Get feature store info
feast feature-views list
feast entities list

# Tear down
feast teardown
```

## Best Practices

✅ **Centralize feature logic** - Single source of truth  
✅ **Version features** - Track changes over time  
✅ **Monitor feature quality** - Detect data issues early  
✅ **Document features** - Make them discoverable  
✅ **Test feature transformations** - Ensure correctness  
✅ **Use consistent naming** - Follow conventions

## Key Takeaways

✅ Feature stores eliminate training-serving skew  
✅ Online/offline serving ensures consistency  
✅ Feature reuse accelerates model development  
✅ Centralized management simplifies governance  
✅ Versioning enables reproducibility

## Next Steps

- **Lab 09**: A/B Testing for model comparison
- **Lab 10**: End-to-end MLOps project
- Add feature monitoring
- Implement feature lineage tracking

## Resources

- [Feast Documentation](https://docs.feast.dev/)
- [Feature Store for ML](https://www.featurestore.org/)
- [Feast Tutorial](https://docs.feast.dev/getting-started/quickstart)
