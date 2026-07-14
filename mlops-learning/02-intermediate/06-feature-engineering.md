# Feature Engineering Pipeline

## Learning Objectives
- Build reproducible feature engineering pipelines
- Implement feature transformations at scale
- Version and track features
- Create reusable feature pipelines

---

## What is Feature Engineering?

Feature engineering transforms raw data into features that better represent patterns for ML models.

### Why Pipeline Feature Engineering?

**Without Pipeline:**
```python
# BAD: Non-reproducible feature engineering
df['age_squared'] = df['age'] ** 2
df['income_log'] = np.log(df['income'] + 1)
df['is_weekend'] = df['date'].dt.dayofweek >= 5

# Train model
model.fit(df[features], df['target'])

# Problem: How do you apply the same transformations in production?
```

**With Pipeline:**
```python
# GOOD: Reproducible pipeline
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer

pipeline = Pipeline([
    ('feature_engineer', FeatureEngineer()),
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier())
])

pipeline.fit(X_train, y_train)
# Same transformations applied consistently
predictions = pipeline.predict(X_prod)
```

---

## Basic Feature Engineering Pipeline

### Simple sklearn Pipeline
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier

# Define feature types
numeric_features = ['age', 'income', 'credit_score']
categorical_features = ['gender', 'occupation', 'city']

# Numeric pipeline
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

# Categorical pipeline
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Combine transformers
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Full pipeline
ml_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100))
])

# Train
ml_pipeline.fit(X_train, y_train)

# Predict (transformations applied automatically)
predictions = ml_pipeline.predict(X_test)
```

---

## Custom Feature Transformers

### Creating Custom Transformers
```python
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np

class DateFeatureExtractor(BaseEstimator, TransformerMixin):
    """Extract features from datetime columns"""
    
    def __init__(self, date_column='date'):
        self.date_column = date_column
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X = X.copy()
        
        # Convert to datetime
        X[self.date_column] = pd.to_datetime(X[self.date_column])
        
        # Extract features
        X['year'] = X[self.date_column].dt.year
        X['month'] = X[self.date_column].dt.month
        X['day'] = X[self.date_column].dt.day
        X['day_of_week'] = X[self.date_column].dt.dayofweek
        X['is_weekend'] = (X['day_of_week'] >= 5).astype(int)
        X['quarter'] = X[self.date_column].dt.quarter
        
        # Drop original column
        X = X.drop(columns=[self.date_column])
        
        return X

class AggregateFeatures(BaseEstimator, TransformerMixin):
    """Create aggregate features"""
    
    def __init__(self, group_columns, agg_column, agg_funcs=['mean', 'std']):
        self.group_columns = group_columns
        self.agg_column = agg_column
        self.agg_funcs = agg_funcs
        self.agg_values_ = None
    
    def fit(self, X, y=None):
        # Calculate aggregations from training data
        self.agg_values_ = (
            X.groupby(self.group_columns)[self.agg_column]
            .agg(self.agg_funcs)
            .reset_index()
        )
        return self
    
    def transform(self, X):
        X = X.copy()
        
        # Merge aggregated features
        X = X.merge(
            self.agg_values_,
            on=self.group_columns,
            how='left',
            suffixes=('', f'_{self.agg_column}_agg')
        )
        
        # Fill missing values with global mean
        for func in self.agg_funcs:
            col_name = f'{self.agg_column}_{func}'
            if col_name in X.columns:
                X[col_name].fillna(X[col_name].mean(), inplace=True)
        
        return X

# Usage
pipeline = Pipeline([
    ('date_features', DateFeatureExtractor(date_column='transaction_date')),
    ('agg_features', AggregateFeatures(
        group_columns=['user_id'],
        agg_column='transaction_amount',
        agg_funcs=['mean', 'std', 'count']
    )),
    ('preprocessor', preprocessor),
    ('model', RandomForestClassifier())
])
```

---

## Advanced Feature Engineering

### Text Features
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

class TextFeatureExtractor(BaseEstimator, TransformerMixin):
    """Extract features from text data"""
    
    def __init__(self, text_column, max_features=100, n_components=20):
        self.text_column = text_column
        self.max_features = max_features
        self.n_components = n_components
        self.vectorizer = None
        self.svd = None
    
    def fit(self, X, y=None):
        # TF-IDF vectorization
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            stop_words='english'
        )
        tfidf_matrix = self.vectorizer.fit_transform(X[self.text_column])
        
        # Dimensionality reduction
        self.svd = TruncatedSVD(n_components=self.n_components)
        self.svd.fit(tfidf_matrix)
        
        return self
    
    def transform(self, X):
        X = X.copy()
        
        # Transform text
        tfidf_matrix = self.vectorizer.transform(X[self.text_column])
        text_features = self.svd.transform(tfidf_matrix)
        
        # Create feature names
        feature_names = [f'text_component_{i}' for i in range(self.n_components)]
        
        # Add to dataframe
        text_df = pd.DataFrame(text_features, columns=feature_names, index=X.index)
        X = pd.concat([X, text_df], axis=1)
        
        # Drop original column
        X = X.drop(columns=[self.text_column])
        
        return X
```

### Interaction Features
```python
from sklearn.preprocessing import PolynomialFeatures

class InteractionFeatureCreator(BaseEstimator, TransformerMixin):
    """Create interaction features between numeric columns"""
    
    def __init__(self, numeric_columns, degree=2, include_bias=False):
        self.numeric_columns = numeric_columns
        self.degree = degree
        self.include_bias = include_bias
        self.poly = None
        self.feature_names = None
    
    def fit(self, X, y=None):
        self.poly = PolynomialFeatures(
            degree=self.degree,
            include_bias=self.include_bias,
            interaction_only=False
        )
        self.poly.fit(X[self.numeric_columns])
        
        # Get feature names
        self.feature_names = self.poly.get_feature_names_out(self.numeric_columns)
        
        return self
    
    def transform(self, X):
        X = X.copy()
        
        # Create polynomial features
        poly_features = self.poly.transform(X[self.numeric_columns])
        
        # Create DataFrame
        poly_df = pd.DataFrame(
            poly_features,
            columns=self.feature_names,
            index=X.index
        )
        
        # Drop original numeric columns (already in poly features)
        X = X.drop(columns=self.numeric_columns)
        
        # Concatenate
        X = pd.concat([X, poly_df], axis=1)
        
        return X
```

---

## Feature Engineering with MLflow

### Logging Pipeline with MLflow
```python
import mlflow
import mlflow.sklearn
from sklearn.pipeline import Pipeline

def train_with_feature_engineering(X_train, y_train, X_test, y_test):
    """Train model with full feature pipeline and log to MLflow"""
    
    with mlflow.start_run(run_name="feature_pipeline_experiment"):
        
        # Define pipeline
        pipeline = Pipeline([
            ('date_features', DateFeatureExtractor('date')),
            ('text_features', TextFeatureExtractor('description')),
            ('agg_features', AggregateFeatures(['user_id'], 'amount')),
            ('interactions', InteractionFeatureCreator(['age', 'income'])),
            ('preprocessor', preprocessor),
            ('model', RandomForestClassifier(n_estimators=100))
        ])
        
        # Train
        pipeline.fit(X_train, y_train)
        
        # Evaluate
        train_score = pipeline.score(X_train, y_train)
        test_score = pipeline.score(X_test, y_test)
        
        # Log parameters
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("has_date_features", True)
        mlflow.log_param("has_text_features", True)
        mlflow.log_param("interaction_degree", 2)
        
        # Log metrics
        mlflow.log_metric("train_accuracy", train_score)
        mlflow.log_metric("test_accuracy", test_score)
        
        # Log pipeline
        mlflow.sklearn.log_model(pipeline, "model")
        
        # Log feature names
        feature_names = pipeline.named_steps['preprocessor'].get_feature_names_out()
        with open("features.txt", "w") as f:
            f.write("\n".join(feature_names))
        mlflow.log_artifact("features.txt")
        
        print(f"Train accuracy: {train_score:.4f}")
        print(f"Test accuracy: {test_score:.4f}")
        
        return pipeline
```

---

## Feature Store Pattern

### Simple Feature Store Implementation
```python
import pandas as pd
from datetime import datetime
import hashlib

class SimpleFeatureStore:
    """Simple feature store for managing features"""
    
    def __init__(self, storage_path="./feature_store"):
        self.storage_path = storage_path
        self.metadata = {}
    
    def register_feature(self, name, transformer, description=""):
        """Register a feature transformation"""
        feature_id = hashlib.md5(name.encode()).hexdigest()[:8]
        
        self.metadata[name] = {
            'feature_id': feature_id,
            'transformer': transformer,
            'description': description,
            'created_at': datetime.now().isoformat()
        }
        
        return feature_id
    
    def compute_features(self, name, data):
        """Compute features using registered transformer"""
        if name not in self.metadata:
            raise ValueError(f"Feature {name} not registered")
        
        transformer = self.metadata[name]['transformer']
        features = transformer.fit_transform(data)
        
        return features
    
    def save_features(self, name, features, entity_id_column):
        """Save computed features"""
        feature_id = self.metadata[name]['feature_id']
        
        # Add metadata
        features['_feature_id'] = feature_id
        features['_computed_at'] = datetime.now()
        
        # Save to parquet
        filepath = f"{self.storage_path}/{name}_{feature_id}.parquet"
        features.to_parquet(filepath)
        
        print(f"Saved features to {filepath}")
        
        return filepath
    
    def load_features(self, name, entity_ids=None):
        """Load features for given entities"""
        feature_id = self.metadata[name]['feature_id']
        filepath = f"{self.storage_path}/{name}_{feature_id}.parquet"
        
        features = pd.read_parquet(filepath)
        
        if entity_ids is not None:
            features = features[features.index.isin(entity_ids)]
        
        return features

# Usage
feature_store = SimpleFeatureStore()

# Register features
feature_store.register_feature(
    name="user_aggregates",
    transformer=AggregateFeatures(['user_id'], 'amount'),
    description="User-level transaction aggregates"
)

# Compute and save
features = feature_store.compute_features("user_aggregates", df)
feature_store.save_features("user_aggregates", features, entity_id_column='user_id')

# Load for training
training_features = feature_store.load_features("user_aggregates", entity_ids=train_user_ids)
```

---

## Production Feature Pipeline

### Serving Features in Production
```python
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# Load trained pipeline
pipeline = joblib.load("model_pipeline.pkl")

class PredictionRequest(BaseModel):
    """Request schema"""
    user_id: int
    transaction_date: str
    transaction_amount: float
    description: str
    # ... other fields

class PredictionResponse(BaseModel):
    """Response schema"""
    prediction: int
    probability: float
    features_used: int

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make prediction with feature engineering"""
    
    try:
        # Convert to DataFrame
        data = pd.DataFrame([request.dict()])
        
        # Pipeline handles all feature engineering
        prediction = pipeline.predict(data)[0]
        probability = pipeline.predict_proba(data)[0].max()
        
        # Get feature count
        n_features = pipeline.named_steps['preprocessor'].transform(data).shape[1]
        
        return PredictionResponse(
            prediction=int(prediction),
            probability=float(probability),
            features_used=n_features
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pipeline/info")
async def pipeline_info():
    """Get pipeline information"""
    
    steps = [step[0] for step in pipeline.steps]
    
    return {
        "pipeline_steps": steps,
        "model_type": type(pipeline.named_steps['model']).__name__
    }
```

---

## Feature Engineering Best Practices

### 1. Version Your Features
```python
from dataclasses import dataclass
from typing import List, Dict
import json

@dataclass
class FeatureVersion:
    """Track feature versions"""
    version: str
    features: List[str]
    transformations: Dict[str, str]
    created_at: str
    
    def save(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.__dict__, f, indent=2)
    
    @classmethod
    def load(cls, filepath):
        with open(filepath) as f:
            data = json.load(f)
        return cls(**data)

# Track feature version
feature_version = FeatureVersion(
    version="v1.0.0",
    features=["age_squared", "income_log", "is_weekend"],
    transformations={
        "age_squared": "age ** 2",
        "income_log": "log(income + 1)",
        "is_weekend": "day_of_week >= 5"
    },
    created_at=datetime.now().isoformat()
)

feature_version.save("features_v1.0.0.json")
```

### 2. Test Your Transformations
```python
import pytest
import pandas as pd
import numpy as np

def test_date_feature_extractor():
    """Test date feature extraction"""
    
    # Create test data
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-06-15', '2024-12-31'],
        'value': [1, 2, 3]
    })
    
    # Apply transformer
    transformer = DateFeatureExtractor('date')
    result = transformer.fit_transform(df)
    
    # Assertions
    assert 'year' in result.columns
    assert 'month' in result.columns
    assert 'is_weekend' in result.columns
    assert result['year'].iloc[0] == 2024
    assert result['month'].iloc[1] == 6
    assert 'date' not in result.columns  # Original column removed

def test_pipeline_consistency():
    """Test pipeline produces consistent results"""
    
    # Same input data
    df1 = pd.DataFrame({'age': [25, 30], 'income': [50000, 60000]})
    df2 = pd.DataFrame({'age': [25, 30], 'income': [50000, 60000]})
    
    # Apply pipeline
    result1 = pipeline.transform(df1)
    result2 = pipeline.transform(df2)
    
    # Should be identical
    np.testing.assert_array_equal(result1, result2)
```

### 3. Monitor Feature Quality
```python
def monitor_feature_quality(features_df, reference_stats):
    """Monitor feature quality in production"""
    
    issues = []
    
    for col in features_df.columns:
        # Check for missing values
        missing_pct = features_df[col].isna().sum() / len(features_df)
        if missing_pct > 0.1:  # More than 10%
            issues.append(f"{col}: {missing_pct:.1%} missing values")
        
        # Check for distribution shift
        if col in reference_stats:
            current_mean = features_df[col].mean()
            reference_mean = reference_stats[col]['mean']
            reference_std = reference_stats[col]['std']
            
            # Check if mean is more than 3 std deviations away
            z_score = abs(current_mean - reference_mean) / reference_std
            if z_score > 3:
                issues.append(f"{col}: Distribution shift detected (z={z_score:.2f})")
    
    return issues

# Usage
reference_stats = {
    'age': {'mean': 35.0, 'std': 10.0},
    'income': {'mean': 55000, 'std': 15000}
}

issues = monitor_feature_quality(production_features, reference_stats)
if issues:
    print("⚠️ Feature quality issues:")
    for issue in issues:
        print(f"  - {issue}")
```

---

## Summary

Key takeaways:
- Use sklearn pipelines for reproducible feature engineering
- Create custom transformers for domain-specific features
- Version and track your features
- Test transformations thoroughly
- Monitor feature quality in production
- Use feature stores for complex systems

---

**Next**: [Model Versioning →](07-model-versioning.md)
