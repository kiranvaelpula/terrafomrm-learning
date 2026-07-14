# Lab 04: Model Registry & Versioning

## Overview
Build a centralized model registry to manage, version, and stage ML models from development to production. Learn model lifecycle management and governance.

**Duration:** 1 hour  
**Difficulty:** Intermediate  
**Prerequisites:** Labs 01-03, MLflow basics

## Learning Objectives
- Set up MLflow Model Registry
- Version and stage models (dev, staging, production)
- Manage model metadata and lineage
- Implement model transition workflows
- Compare model versions

## Why Model Registry?

```
Without Registry:
- Models scattered in directories
- No version history
- Unclear which model is in production
- Manual deployment process
❌ Chaos and risk

With Registry:
- Centralized model store
- Clear versioning
- Staging environments
- Automated transitions
✅ Governance and control
```

## Setup

### 1. Install Dependencies

```bash
pip install mlflow scikit-learn pandas boto3
```

### 2. Start MLflow Tracking Server with Registry

```bash
# Start MLflow with backend database
mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root ./mlruns \
    --host 0.0.0.0 \
    --port 5000

# Access UI: http://localhost:5000
```

## Implementation

### Step 1: Train and Register Models

Create `src/train_and_register.py`:

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import pandas as pd
import numpy as np

# Set tracking URI
mlflow.set_tracking_uri("http://localhost:5000")

class ModelTrainer:
    def __init__(self, experiment_name="model-registry-demo"):
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)
        
    def prepare_data(self, data_path):
        """Load and prepare data"""
        df = pd.read_csv(data_path)
        
        # Simple preprocessing
        df = df.dropna()
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col not in ['customer_id']:
                df[col] = pd.Categorical(df[col]).codes
        
        X = df.drop(['churn', 'customer_id'], axis=1, errors='ignore')
        y = df['churn']
        
        return train_test_split(X, y, test_size=0.2, random_state=42)
    
    def evaluate_model(self, model, X_test, y_test):
        """Calculate metrics"""
        y_pred = model.predict(X_test)
        
        return {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred)
        }
    
    def train_and_register(self, model_name, model_class, params, X_train, X_test, y_train, y_test):
        """Train model and register in MLflow"""
        
        with mlflow.start_run(run_name=f"{model_name}_training"):
            
            # Train model
            model = model_class(**params)
            model.fit(X_train, y_train)
            
            # Evaluate
            metrics = self.evaluate_model(model, X_test, y_test)
            
            # Log parameters
            mlflow.log_params(params)
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log model
            mlflow.sklearn.log_model(
                model,
                artifact_path="model",
                registered_model_name=model_name
            )
            
            print(f"✅ Registered {model_name}")
            print(f"   Accuracy: {metrics['accuracy']:.4f}")
            print(f"   F1 Score: {metrics['f1_score']:.4f}")
            
            return mlflow.active_run().info.run_id, metrics

# Train multiple models
if __name__ == "__main__":
    trainer = ModelTrainer()
    
    # Prepare data
    X_train, X_test, y_train, y_test = trainer.prepare_data('data/raw/customers.csv')
    
    print("🎯 Training and registering models...\n")
    
    # Model 1: Random Forest
    trainer.train_and_register(
        model_name="churn-predictor-rf",
        model_class=RandomForestClassifier,
        params={'n_estimators': 100, 'max_depth': 10, 'random_state': 42},
        X_train=X_train, X_test=X_test,
        y_train=y_train, y_test=y_test
    )
    
    # Model 2: Gradient Boosting
    trainer.train_and_register(
        model_name="churn-predictor-gb",
        model_class=GradientBoostingClassifier,
        params={'n_estimators': 100, 'learning_rate': 0.1, 'random_state': 42},
        X_train=X_train, X_test=X_test,
        y_train=y_train, y_test=y_test
    )
    
    # Model 3: Logistic Regression
    trainer.train_and_register(
        model_name="churn-predictor-lr",
        model_class=LogisticRegression,
        params={'max_iter': 1000, 'random_state': 42},
        X_train=X_train, X_test=X_test,
        y_train=y_train, y_test=y_test
    )
    
    print("\n✅ All models registered!")
    print("   View in MLflow UI: http://localhost:5000")
```

### Step 2: Model Stage Management

Create `src/model_stage_manager.py`:

```python
import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("http://localhost:5000")

class ModelStageManager:
    def __init__(self):
        self.client = MlflowClient()
    
    def list_registered_models(self):
        """List all registered models"""
        models = self.client.search_registered_models()
        
        print("\n📋 Registered Models")
        print("=" * 70)
        
        for model in models:
            print(f"\n🔹 {model.name}")
            print(f"   Description: {model.description or 'N/A'}")
            print(f"   Latest Versions:")
            
            for version in model.latest_versions:
                print(f"      v{version.version} - Stage: {version.current_stage}")
        
        return models
    
    def get_model_versions(self, model_name):
        """Get all versions of a model"""
        versions = self.client.search_model_versions(f"name='{model_name}'")
        
        print(f"\n📦 Versions for {model_name}")
        print("=" * 70)
        
        for version in versions:
            print(f"\nVersion {version.version}")
            print(f"   Stage: {version.current_stage}")
            print(f"   Run ID: {version.run_id}")
            print(f"   Created: {version.creation_timestamp}")
            
        return versions
    
    def transition_model_stage(self, model_name, version, stage, archive_existing=True):
        """
        Transition model to a new stage
        
        Stages: None, Staging, Production, Archived
        """
        print(f"\n🔄 Transitioning {model_name} v{version} to {stage}")
        
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage,
            archive_existing_versions=archive_existing
        )
        
        print(f"   ✅ Transitioned to {stage}")
    
    def compare_model_versions(self, model_name, version1, version2):
        """Compare metrics between two versions"""
        
        def get_metrics(version):
            model_version = self.client.get_model_version(model_name, version)
            run = self.client.get_run(model_version.run_id)
            return run.data.metrics
        
        metrics1 = get_metrics(version1)
        metrics2 = get_metrics(version2)
        
        print(f"\n📊 Comparing {model_name}")
        print("=" * 70)
        print(f"{'Metric':<15} {'v' + str(version1):<15} {'v' + str(version2):<15} {'Winner'}")
        print("-" * 70)
        
        for metric in metrics1:
            val1 = metrics1.get(metric, 0)
            val2 = metrics2.get(metric, 0)
            winner = "v" + str(version1) if val1 > val2 else "v" + str(version2)
            
            print(f"{metric:<15} {val1:<15.4f} {val2:<15.4f} {winner}")
    
    def add_model_description(self, model_name, description):
        """Add description to model"""
        self.client.update_registered_model(
            name=model_name,
            description=description
        )
        print(f"✅ Updated description for {model_name}")
    
    def add_version_tag(self, model_name, version, key, value):
        """Add tag to model version"""
        self.client.set_model_version_tag(model_name, version, key, value)
        print(f"✅ Added tag {key}={value} to {model_name} v{version}")
    
    def get_production_model(self, model_name):
        """Get the current production model"""
        versions = self.client.get_latest_versions(model_name, stages=["Production"])
        
        if versions:
            version = versions[0]
            print(f"\n🚀 Production Model: {model_name}")
            print(f"   Version: {version.version}")
            print(f"   Run ID: {version.run_id}")
            return version
        else:
            print(f"❌ No production version found for {model_name}")
            return None

# Example usage
if __name__ == "__main__":
    manager = ModelStageManager()
    
    # List all models
    manager.list_registered_models()
    
    # Get versions for specific model
    manager.get_model_versions("churn-predictor-rf")
    
    # Transition to staging
    manager.transition_model_stage(
        model_name="churn-predictor-rf",
        version=1,
        stage="Staging"
    )
    
    # Add description
    manager.add_model_description(
        model_name="churn-predictor-rf",
        description="Random Forest model for customer churn prediction"
    )
    
    # Add tags
    manager.add_version_tag(
        model_name="churn-predictor-rf",
        version=1,
        key="validated_by",
        value="data-science-team"
    )
    
    # Compare versions (if multiple exist)
    # manager.compare_model_versions("churn-predictor-rf", 1, 2)
    
    # Promote to production
    manager.transition_model_stage(
        model_name="churn-predictor-rf",
        version=1,
        stage="Production",
        archive_existing=True
    )
    
    # Get production model
    manager.get_production_model("churn-predictor-rf")
```

### Step 3: Load and Use Registered Models

Create `src/use_registered_model.py`:

```python
import mlflow
import mlflow.pyfunc
import pandas as pd
import numpy as np

mlflow.set_tracking_uri("http://localhost:5000")

class ModelLoader:
    def __init__(self):
        self.model = None
        self.model_info = {}
    
    def load_model_by_stage(self, model_name, stage="Production"):
        """Load model from specific stage"""
        model_uri = f"models:/{model_name}/{stage}"
        
        print(f"📥 Loading {model_name} from {stage} stage...")
        self.model = mlflow.pyfunc.load_model(model_uri)
        
        print(f"   ✅ Model loaded successfully")
        return self.model
    
    def load_model_by_version(self, model_name, version):
        """Load specific model version"""
        model_uri = f"models:/{model_name}/{version}"
        
        print(f"📥 Loading {model_name} version {version}...")
        self.model = mlflow.pyfunc.load_model(model_uri)
        
        print(f"   ✅ Model loaded successfully")
        return self.model
    
    def predict(self, data):
        """Make predictions"""
        if self.model is None:
            raise ValueError("No model loaded. Load a model first.")
        
        predictions = self.model.predict(data)
        return predictions
    
    def predict_proba(self, data):
        """Get prediction probabilities"""
        if self.model is None:
            raise ValueError("No model loaded. Load a model first.")
        
        # Try to get probabilities
        try:
            probas = self.model._model_impl.python_model.predict_proba(data)
            return probas
        except:
            print("⚠️ Model does not support predict_proba")
            return None

# Example usage
if __name__ == "__main__":
    loader = ModelLoader()
    
    # Load production model
    model = loader.load_model_by_stage("churn-predictor-rf", stage="Production")
    
    # Prepare sample data
    df = pd.read_csv('data/raw/customers.csv').head(10)
    
    # Preprocess
    df = df.dropna()
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if col not in ['customer_id']:
            df[col] = pd.Categorical(df[col]).codes
    
    X = df.drop(['churn', 'customer_id'], axis=1, errors='ignore')
    
    # Make predictions
    print("\n🔮 Making predictions...")
    predictions = loader.predict(X)
    
    print(f"\nPredictions for {len(predictions)} samples:")
    print(predictions)
    
    # Calculate churn risk
    churn_risk = predictions.mean()
    print(f"\n📊 Overall churn risk: {churn_risk:.1%}")
```

### Step 4: Model Promotion Workflow

Create `src/model_promotion_workflow.py`:

```python
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

mlflow.set_tracking_uri("http://localhost:5000")

class ModelPromoter:
    def __init__(self):
        self.client = MlflowClient()
    
    def validate_model(self, model_name, version, validation_data_path):
        """Validate model on holdout dataset"""
        print(f"\n🔍 Validating {model_name} v{version}...")
        
        # Load model
        model_uri = f"models:/{model_name}/{version}"
        model = mlflow.pyfunc.load_model(model_uri)
        
        # Load validation data
        df = pd.read_csv(validation_data_path)
        df = df.dropna()
        
        # Preprocess
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col not in ['customer_id']:
                df[col] = pd.Categorical(df[col]).codes
        
        X = df.drop(['churn', 'customer_id'], axis=1, errors='ignore')
        y = df['churn']
        
        # Predict
        y_pred = model.predict(X)
        
        # Calculate metrics
        accuracy = accuracy_score(y, y_pred)
        f1 = f1_score(y, y_pred)
        
        print(f"   Accuracy: {accuracy:.4f}")
        print(f"   F1 Score: {f1:.4f}")
        
        return {'accuracy': accuracy, 'f1_score': f1}
    
    def promote_to_staging(self, model_name, version, min_accuracy=0.75):
        """Promote model to staging if it passes validation"""
        print(f"\n🎯 Attempting to promote {model_name} v{version} to Staging")
        
        # Validate
        metrics = self.validate_model(model_name, version, 'data/raw/customers.csv')
        
        # Check threshold
        if metrics['accuracy'] >= min_accuracy:
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage="Staging"
            )
            print(f"   ✅ Promoted to Staging")
            return True
        else:
            print(f"   ❌ Failed validation (accuracy {metrics['accuracy']:.4f} < {min_accuracy})")
            return False
    
    def promote_to_production(self, model_name, version):
        """Promote staging model to production"""
        print(f"\n🚀 Promoting {model_name} v{version} to Production")
        
        # Check if currently in staging
        model_version = self.client.get_model_version(model_name, version)
        
        if model_version.current_stage != "Staging":
            print(f"   ❌ Model must be in Staging first (currently: {model_version.current_stage})")
            return False
        
        # Get current production model
        prod_versions = self.client.get_latest_versions(model_name, stages=["Production"])
        
        if prod_versions:
            print(f"   ⚠️ Archiving current production version {prod_versions[0].version}")
        
        # Promote
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage="Production",
            archive_existing_versions=True
        )
        
        print(f"   ✅ Promoted to Production")
        
        # Add deployment timestamp tag
        from datetime import datetime
        self.client.set_model_version_tag(
            model_name, 
            version, 
            "deployed_at", 
            datetime.now().isoformat()
        )
        
        return True
    
    def rollback_production(self, model_name, to_version):
        """Rollback production to previous version"""
        print(f"\n⏮️ Rolling back {model_name} to version {to_version}")
        
        self.client.transition_model_version_stage(
            name=model_name,
            version=to_version,
            stage="Production",
            archive_existing_versions=True
        )
        
        print(f"   ✅ Rolled back to v{to_version}")

# Example workflow
if __name__ == "__main__":
    promoter = ModelPromoter()
    
    model_name = "churn-predictor-rf"
    
    # Workflow: None -> Staging -> Production
    
    # Step 1: Promote to staging
    success = promoter.promote_to_staging(model_name, version=1, min_accuracy=0.75)
    
    if success:
        # Step 2: Promote to production (after manual approval)
        input("\nPress Enter to promote to production...")
        promoter.promote_to_production(model_name, version=1)
    
    # Rollback example (if needed)
    # promoter.rollback_production(model_name, to_version=1)
```

## Exercises

### Exercise 1: Automated Model Selection
Build a system that automatically selects the best model:

```python
def select_best_model(models, metric='f1_score'):
    best_model = None
    best_score = 0
    
    for model in models:
        # Get metrics and compare
        pass
    
    return best_model
```

### Exercise 2: Model Approval Workflow
Implement approval system with notifications:

```python
def request_approval(model_name, version, reviewers):
    # Send notification
    # Wait for approval
    # Transition if approved
    pass
```

### Exercise 3: A/B Testing Setup
Prepare models for A/B testing:

```python
def setup_ab_test(model_a, model_b, traffic_split=0.5):
    # Tag models for A/B testing
    # Configure traffic routing
    pass
```

## Best Practices

✅ **Always validate before promotion** - Run tests on holdout data  
✅ **Use descriptive names** - Include algorithm and purpose  
✅ **Tag extensively** - Add metadata for governance  
✅ **Document transitions** - Log reasons for stage changes  
✅ **Keep staging environment** - Test before production  
✅ **Enable rollback** - Keep previous versions accessible

## Model Registry CLI Commands

```bash
# List all models
mlflow models list

# Get model info
mlflow models describe --name churn-predictor-rf

# Transition stage
mlflow models transition \
    --name churn-predictor-rf \
    --version 1 \
    --stage Production

# Serve model
mlflow models serve \
    --model-uri models:/churn-predictor-rf/Production \
    --port 5001
```

## Key Takeaways

✅ Model registry provides centralized model management  
✅ Staging enables safe testing before production  
✅ Versioning tracks model evolution  
✅ Metadata and tags support governance  
✅ Workflows ensure consistent deployment process

## Next Steps

- **Lab 05**: Model Deployment with REST APIs
- **Lab 06**: Model Monitoring and drift detection
- Implement approval workflows
- Add automated testing gates

## Resources

- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
- [Model Versioning Best Practices](https://ml-ops.org/content/model-registry)
- [Model Governance](https://www.datarobot.com/wiki/model-governance/)
