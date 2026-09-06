# First ML Pipeline

## Overview

Building your first end-to-end ML pipeline is a crucial step in understanding MLOps. A pipeline automates the workflow from data ingestion to model deployment, making your ML process reproducible and scalable.

## What is an ML Pipeline?

An ML pipeline is an automated workflow that:
- Loads and preprocesses data
- Trains a model
- Evaluates performance
- Saves the trained model
- Can be executed repeatedly with consistent results

Think of it as a recipe that can be followed exactly the same way every time.

## 📖 Understanding ML Pipelines (Intuition First)

Think about the difference between a home cook improvising dinner and a fast-food chain serving millions of identical meals a day. The home cook tastes as they go, adds "a pinch of this," and every meal comes out a little different. The chain writes down an exact recipe: same ingredients, same order, same timing, same equipment — so any location, any employee, any day produces the same result. An ML pipeline turns your improvised, notebook-style modeling into that repeatable recipe.

In a Jupyter notebook, it's tempting to run cells out of order, tweak a preprocessing step by hand, and forget which version produced your best model. That works for exploration, but it's a nightmare for production. When you can't remember the exact sequence of steps that produced a result, you can't reproduce it, debug it, or trust it. A pipeline captures the *entire* sequence — load, validate, preprocess, engineer features, split, train, evaluate, save — as code that runs the same way every single time.

The reason pipelines matter so much in MLOps comes down to one word: **reproducibility**. If the steps are code, they can be version-controlled, tested, reviewed, and automated. You can rerun last month's exact process, hand the pipeline to a teammate, or trigger it automatically when new data arrives. The notebook becomes the place you *discover* things; the pipeline becomes the place you *productionize* them.

A subtle but critical point is that a pipeline must save **all the artifacts needed for inference**, not just the model. If you scaled your features during training with a specific scaler, you need that exact scaler at prediction time — otherwise the model sees numbers on a different scale and produces garbage. Forgetting to save preprocessing objects (scalers, encoders) is one of the most common ways pipelines silently break in production.

Finally, notice how the example pipeline is built from small, single-purpose steps with logging and error handling around them. This modularity is deliberate: when something fails, you want to know *exactly* which step broke and why. A good pipeline is not just automation — it's automation you can observe, test, and trust.

## Why ML Pipelines Matter

**Without a pipeline:**
```
❌ Manual data loading
❌ Inconsistent preprocessing
❌ Forgotten steps
❌ Hard to reproduce results
❌ Error-prone process
```

**With a pipeline:**
```
✅ Automated execution
✅ Consistent results
✅ Easy to reproduce
✅ Version controlled
✅ Scalable to production
```

## Components of an ML Pipeline

### 1. Data Ingestion
```python
def load_data(source):
    """Load data from source"""
    if source == 'csv':
        return pd.read_csv('data/train.csv')
    elif source == 'database':
        return load_from_database()
    # More sources...
```

### 2. Data Validation
```python
def validate_data(df):
    """Check data quality"""
    assert df.shape[0] > 0, "Empty dataset"
    assert df.isnull().sum().sum() < len(df) * 0.1, "Too many missing values"
    return df
```

### 3. Data Preprocessing
```python
def preprocess_data(df):
    """Clean and transform data"""
    # Handle missing values
    df = df.fillna(df.mean())
    
    # Encode categoricals
    df = pd.get_dummies(df, drop_first=True)
    
    # Scale features
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    
    return df, scaler
```

### 4. Feature Engineering
```python
def engineer_features(df):
    """Create new features"""
    df['feature_ratio'] = df['feature_a'] / (df['feature_b'] + 1)
    df['feature_interaction'] = df['feature_c'] * df['feature_d']
    return df
```

### 5. Train-Test Split
```python
def split_data(df, target_col='target', test_size=0.2):
    """Split into train and test sets"""
    from sklearn.model_selection import train_test_split
    
    X = df.drop(target_col, axis=1)
    y = df[target_col]
    
    return train_test_split(X, y, test_size=test_size, random_state=42)
```

### 6. Model Training
```python
def train_model(X_train, y_train, model_type='rf'):
    """Train ML model"""
    if model_type == 'rf':
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    elif model_type == 'lgbm':
        import lightgbm as lgb
        model = lgb.LGBMClassifier()
    
    model.fit(X_train, y_train)
    return model
```

### 7. Model Evaluation
```python
def evaluate_model(model, X_test, y_test):
    """Evaluate model performance"""
    from sklearn.metrics import accuracy_score, classification_report
    
    y_pred = model.predict(X_test)
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'report': classification_report(y_test, y_pred)
    }
    
    return metrics
```

### 8. Model Saving
```python
def save_model(model, scaler, path='models/'):
    """Save trained model and artifacts"""
    import joblib
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    joblib.dump(model, f'{path}model_{timestamp}.pkl')
    joblib.dump(scaler, f'{path}scaler_{timestamp}.pkl')
    
    print(f"Model saved: model_{timestamp}.pkl")
```

## Complete Pipeline Example

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLPipeline:
    """Complete ML pipeline"""
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.scaler = None
        self.metrics = {}
    
    def load_data(self):
        """Step 1: Load data"""
        logger.info("Loading data...")
        df = pd.read_csv(self.config['data_path'])
        logger.info(f"Loaded {len(df)} samples")
        return df
    
    def validate_data(self, df):
        """Step 2: Validate data"""
        logger.info("Validating data...")
        
        # Check for empty data
        assert len(df) > 0, "Empty dataset"
        
        # Check for target column
        assert self.config['target_col'] in df.columns, "Target column missing"
        
        # Check for excessive missing values
        missing_pct = df.isnull().sum() / len(df)
        assert (missing_pct < 0.2).all(), "Too many missing values"
        
        logger.info("Data validation passed")
        return df
    
    def preprocess_data(self, df):
        """Step 3: Preprocess data"""
        logger.info("Preprocessing data...")
        
        # Handle missing values
        df = df.fillna(df.median())
        
        # Encode categorical variables
        categorical_cols = df.select_dtypes(include=['object']).columns
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
        
        logger.info(f"Preprocessed to {df.shape[1]} features")
        return df
    
    def engineer_features(self, df):
        """Step 4: Feature engineering"""
        logger.info("Engineering features...")
        
        # Add your feature engineering logic here
        # Example: df['new_feature'] = df['feature_a'] / df['feature_b']
        
        return df
    
    def split_data(self, df):
        """Step 5: Split data"""
        logger.info("Splitting data...")
        
        X = df.drop(self.config['target_col'], axis=1)
        y = df[self.config['target_col']]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=self.config['test_size'],
            random_state=42
        )
        
        logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")
        return X_train, X_test, y_train, y_test
    
    def scale_features(self, X_train, X_test):
        """Step 6: Scale features"""
        logger.info("Scaling features...")
        
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled
    
    def train_model(self, X_train, y_train):
        """Step 7: Train model"""
        logger.info("Training model...")
        
        self.model = RandomForestClassifier(
            n_estimators=self.config['n_estimators'],
            max_depth=self.config['max_depth'],
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        logger.info("Model training complete")
    
    def evaluate_model(self, X_test, y_test):
        """Step 8: Evaluate model"""
        logger.info("Evaluating model...")
        
        y_pred = self.model.predict(X_test)
        
        self.metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'report': classification_report(y_test, y_pred, output_dict=True)
        }
        
        logger.info(f"Accuracy: {self.metrics['accuracy']:.4f}")
        return self.metrics
    
    def save_artifacts(self):
        """Step 9: Save model and scaler"""
        logger.info("Saving artifacts...")
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        joblib.dump(self.model, f'models/model_{timestamp}.pkl')
        joblib.dump(self.scaler, f'models/scaler_{timestamp}.pkl')
        
        # Save metrics
        import json
        with open(f'models/metrics_{timestamp}.json', 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        logger.info(f"Artifacts saved with timestamp: {timestamp}")
    
    def run(self):
        """Execute complete pipeline"""
        logger.info("=" * 60)
        logger.info("Starting ML Pipeline")
        logger.info("=" * 60)
        
        try:
            # Execute pipeline steps
            df = self.load_data()
            df = self.validate_data(df)
            df = self.preprocess_data(df)
            df = self.engineer_features(df)
            
            X_train, X_test, y_train, y_test = self.split_data(df)
            X_train, X_test = self.scale_features(X_train, X_test)
            
            self.train_model(X_train, y_train)
            self.evaluate_model(X_test, y_test)
            self.save_artifacts()
            
            logger.info("=" * 60)
            logger.info("Pipeline completed successfully!")
            logger.info("=" * 60)
            
            return self.metrics
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

# Example usage
if __name__ == "__main__":
    config = {
        'data_path': 'data/train.csv',
        'target_col': 'target',
        'test_size': 0.2,
        'n_estimators': 100,
        'max_depth': 10
    }
    
    pipeline = MLPipeline(config)
    metrics = pipeline.run()
    
    print("\nFinal Metrics:")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
```

## Running Your Pipeline

### Command Line
```bash
python pipeline.py
```

### As a Module
```python
from pipeline import MLPipeline

config = {...}
pipeline = MLPipeline(config)
results = pipeline.run()
```

### With Different Configurations
```python
# Development
dev_config = {'data_path': 'data/dev.csv', ...}
MLPipeline(dev_config).run()

# Production
prod_config = {'data_path': 'data/prod.csv', ...}
MLPipeline(prod_config).run()
```

## Pipeline Best Practices

### 1. Use Configuration Files
```python
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

pipeline = MLPipeline(config)
```

### 2. Add Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
```

### 3. Implement Error Handling
```python
try:
    pipeline.run()
except ValidationError as e:
    logger.error(f"Data validation failed: {e}")
    notify_team(e)
except ModelError as e:
    logger.error(f"Model training failed: {e}")
    rollback()
```

### 4. Version Your Code
```bash
git add pipeline.py
git commit -m "Add ML pipeline v1.0"
git tag v1.0
```

### 5. Test Your Pipeline
```python
def test_pipeline():
    config = {'data_path': 'data/test_sample.csv', ...}
    pipeline = MLPipeline(config)
    
    metrics = pipeline.run()
    
    assert metrics['accuracy'] > 0.5, "Model accuracy too low"
    assert pipeline.model is not None, "Model not trained"
```

## Common Pitfalls

❌ **Don't:**
- Hard-code file paths
- Skip data validation
- Forget to save preprocessing artifacts (scalers, encoders)
- Ignore error handling
- Mix training and inference code

✅ **Do:**
- Use configuration files
- Validate data at every step
- Save all artifacts needed for inference
- Log everything
- Separate training and inference pipelines

## Next Steps

After building your first pipeline:

1. **Add Experiment Tracking** (Chapter 05)
   - Track parameters and metrics
   - Compare different runs

2. **Automate with DVC** (Lab 02)
   - Version data and models
   - Create reproducible pipelines

3. **Deploy with CI/CD** (Lab 07)
   - Automate training
   - Deploy automatically

## 🎯 Interview Quick Points

- An ML pipeline is an **automated, repeatable workflow** from data ingestion to model saving — a "recipe" that runs identically every time
- Pipelines exist to solve **reproducibility**: notebooks explore, pipelines productionize
- Typical stages: **load → validate → preprocess → feature engineering → split → train → evaluate → save**
- **Save all inference artifacts**, not just the model — scalers, encoders, and config must travel with it or predictions break
- **Fit preprocessing on training data only**, then apply (transform) to test/production to avoid data leakage
- Use **fixed random seeds** and **versioned data/code** to make runs reproducible
- Drive pipelines with **config files** (YAML) instead of hard-coded paths so they're flexible across environments
- Add **logging and error handling** around each step so failures are observable and pinpointed
- **Separate training and inference** code paths — they have different requirements
- Pipelines are **testable** (assert accuracy thresholds, assert model exists) and **versionable** (git tags)
- Being modular (small single-purpose steps) makes debugging and reuse far easier
- Frameworks that scale this idea: **scikit-learn Pipeline, MLflow Projects, Kedro, Kubeflow Pipelines**

## Key Takeaways

✅ Pipelines automate the ML workflow  
✅ Reproducibility is crucial for MLOps  
✅ Configuration makes pipelines flexible  
✅ Logging helps debug issues  
✅ Testing ensures reliability  
✅ Saving artifacts enables inference

## Interview Questions

**Q: What is an ML pipeline?**
A: An automated workflow that handles data loading, preprocessing, model training, and evaluation in a reproducible way.

**Q: Why use pipelines instead of notebooks?**
A: Pipelines are reproducible, testable, versionable, and can be automated for production use.

**Q: What artifacts should be saved?**
A: Model file, preprocessing objects (scalers, encoders), training metrics, and configuration used.

**Q: How do you make pipelines reproducible?**
A: Use fixed random seeds, version data and code, save configurations, and document dependencies.

## Resources

- [Scikit-learn Pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html)
- [MLflow Projects](https://mlflow.org/docs/latest/projects.html)
- [Kedro Framework](https://kedro.org/)
- [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/)

## Practice Exercise

Build a pipeline for your own dataset:
1. Start with data loading
2. Add validation
3. Implement preprocessing
4. Train a simple model
5. Evaluate and save
6. Run it end-to-end
7. Verify you can load and use the saved model

---

**Next:** [Experiment Tracking Basics](05-experiment-tracking.md)
