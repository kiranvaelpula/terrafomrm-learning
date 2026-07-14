# MLOps Quick Start Guide

Get started with MLOps in 30 minutes!

## 🎯 Goal
Set up a basic ML pipeline with experiment tracking and model deployment.

## Prerequisites
- Python 3.8+ installed
- pip or conda package manager
- Basic ML knowledge

## Step 1: Install MLOps Tools (5 mins)

```bash
# Create virtual environment
python -m venv mlops-env
source mlops-env/bin/activate  # On Windows: mlops-env\Scripts\activate

# Install core MLOps tools
pip install mlflow scikit-learn pandas numpy
pip install dvc[s3]  # For data versioning
pip install evidently  # For monitoring
```

## Step 2: Track Your First Experiment (5 mins)

Create `train.py`:

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load data
data = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2
)

# Start MLflow run
with mlflow.start_run():
    # Parameters
    n_estimators = 100
    max_depth = 5
    
    # Log parameters
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    
    # Train model
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    # Log metrics
    mlflow.log_metric("accuracy", accuracy)
    
    # Log model
    mlflow.sklearn.log_model(model, "model")
    
    print(f"Accuracy: {accuracy}")

print("✅ Experiment tracked successfully!")
```

Run it:
```bash
python train.py
mlflow ui  # View at http://localhost:5000
```

## Step 3: Version Your Data (5 mins)

```bash
# Initialize DVC
dvc init

# Add data to DVC tracking
dvc add data/training_data.csv

# Commit to git
git add data/training_data.csv.dvc .dvc/
git commit -m "Track training data"

# Configure remote storage (example: S3)
dvc remote add -d myremote s3://my-bucket/dvc-storage
dvc push
```

## Step 4: Create ML Pipeline (5 mins)

Create `pipeline.py`:

```python
import mlflow
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# Define pipeline
def create_pipeline():
    return Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(n_estimators=100))
    ])

# Train with pipeline
with mlflow.start_run(run_name="pipeline_experiment"):
    pipeline = create_pipeline()
    pipeline.fit(X_train, y_train)
    
    # Log pipeline
    mlflow.sklearn.log_model(pipeline, "pipeline_model")
    
    # Save artifacts
    mlflow.log_artifact("config.yaml")

print("✅ Pipeline created and tracked!")
```

## Step 5: Deploy Model Locally (5 mins)

```bash
# Serve model with MLflow
mlflow models serve -m runs:/<RUN_ID>/model -p 5001

# Test the endpoint
curl -X POST http://localhost:5001/invocations \
  -H 'Content-Type: application/json' \
  -d '{"inputs": [[5.1, 3.5, 1.4, 0.2]]}'
```

Or use Python:

```python
import mlflow
import pandas as pd

# Load model
model_uri = "runs:/<RUN_ID>/model"
model = mlflow.sklearn.load_model(model_uri)

# Make prediction
data = pd.DataFrame([[5.1, 3.5, 1.4, 0.2]])
prediction = model.predict(data)
print(f"Prediction: {prediction}")
```

## Step 6: Monitor Model Performance (5 mins)

Create `monitor.py`:

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
import pandas as pd

# Load reference and current data
reference_data = pd.read_csv('data/reference.csv')
current_data = pd.read_csv('data/current.csv')

# Create drift report
report = Report(metrics=[
    DataDriftPreset(),
    DataQualityPreset()
])

report.run(reference_data=reference_data, current_data=current_data)
report.save_html('drift_report.html')

print("✅ Monitoring report generated!")
```

## Complete Example: End-to-End Pipeline

Create `e2e_pipeline.py`:

```python
import mlflow
import mlflow.sklearn
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.datasets import load_iris
import pandas as pd

def run_mlops_pipeline():
    # 1. Data Loading
    data = load_iris()
    X = pd.DataFrame(data.data, columns=data.feature_names)
    y = pd.Series(data.target)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    # 2. MLflow Experiment
    mlflow.set_experiment("iris_classification")
    
    with mlflow.start_run(run_name="production_model"):
        # 3. Create Pipeline
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('rf', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        
        # 4. Log parameters
        mlflow.log_param("model_type", "RandomForest")
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("scaler", "StandardScaler")
        
        # 5. Cross-validation
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5)
        mlflow.log_metric("cv_mean_accuracy", cv_scores.mean())
        mlflow.log_metric("cv_std_accuracy", cv_scores.std())
        
        # 6. Train
        pipeline.fit(X_train, y_train)
        
        # 7. Evaluate
        train_score = pipeline.score(X_train, y_train)
        test_score = pipeline.score(X_test, y_test)
        
        mlflow.log_metric("train_accuracy", train_score)
        mlflow.log_metric("test_accuracy", test_score)
        
        # 8. Log model
        mlflow.sklearn.log_model(
            pipeline,
            "model",
            registered_model_name="iris_classifier"
        )
        
        # 9. Log artifacts
        feature_importance = pd.DataFrame({
            'feature': data.feature_names,
            'importance': pipeline.named_steps['rf'].feature_importances_
        }).sort_values('importance', ascending=False)
        
        feature_importance.to_csv('feature_importance.csv', index=False)
        mlflow.log_artifact('feature_importance.csv')
        
        print(f"✅ Pipeline complete!")
        print(f"   Train Accuracy: {train_score:.4f}")
        print(f"   Test Accuracy: {test_score:.4f}")
        print(f"   CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

if __name__ == "__main__":
    run_mlops_pipeline()
```

## 🎓 What You've Learned

✅ Experiment tracking with MLflow
✅ Data versioning with DVC
✅ ML pipeline creation
✅ Model deployment
✅ Performance monitoring
✅ End-to-end MLOps workflow

## Next Steps

1. **Explore Basics**: Read [What is MLOps](01-basics/01-what-is-mlops.md)
2. **Deep Dive**: Learn about [Model Versioning](02-intermediate/07-model-versioning.md)
3. **Practice**: Work through exercises in `mlops-practice/`
4. **Build**: Create production ML pipeline

## Common Issues & Solutions

### Issue: MLflow UI not starting
```bash
# Check if port is already in use
lsof -i :5000
# Use different port
mlflow ui --port 5001
```

### Issue: Model serialization fails
```bash
# Ensure all dependencies are logged
pip freeze > requirements.txt
mlflow.log_artifact('requirements.txt')
```

### Issue: DVC remote storage errors
```bash
# Configure credentials
dvc remote modify myremote access_key_id 'YOUR_KEY'
dvc remote modify myremote secret_access_key 'YOUR_SECRET'
```

## Useful Commands

```bash
# MLflow
mlflow ui                              # Start UI
mlflow models serve -m <model_uri>    # Serve model
mlflow experiments list                # List experiments

# DVC
dvc add <file>                        # Track data
dvc push                              # Push to remote
dvc pull                              # Pull from remote
dvc repro                             # Reproduce pipeline

# Model Registry
mlflow models --help                  # Model commands
```

## Resources

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [DVC Documentation](https://dvc.org/doc)
- [Evidently Documentation](https://docs.evidentlyai.com/)

---
Ready to dive deeper? Start with [01-basics](01-basics/)!
