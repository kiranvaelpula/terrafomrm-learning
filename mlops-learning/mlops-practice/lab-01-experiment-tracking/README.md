# Lab 1: Experiment Tracking & Versioning

## 🎯 Objectives

By the end of this lab, you will:
- Set up MLflow for experiment tracking
- Log parameters, metrics, and artifacts
- Compare multiple experiments
- Register and version models
- Retrieve models for deployment

## 📋 Prerequisites

- Python 3.8+
- Basic machine learning knowledge
- scikit-learn installed

## 🛠️ Setup

```bash
# Install required packages
pip install mlflow scikit-learn pandas numpy matplotlib

# Start MLflow UI
mlflow ui --port 5000

# Open browser to http://localhost:5000
```

## Lab Exercises

### Exercise 1: Basic Experiment Tracking (15 mins)

**Task**: Train a simple model and track it with MLflow

Create `train_basic.py`:

```python
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

# Load data
data = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

# Set experiment name
mlflow.set_experiment("iris-classification")

# Start MLflow run
with mlflow.start_run(run_name="baseline-model"):
    
    # Log parameters
    n_estimators = 100
    max_depth = 5
    
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    mlflow.log_param("model_type", "RandomForest")
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Make predictions
    predictions = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, predictions)
    f1 = f1_score(y_test, predictions, average='weighted')
    
    # Log metrics
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1_score", f1)
    
    # Log model
    mlflow.sklearn.log_model(model, "model")
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1 Score: {f1:.4f}")
```

**Run it**:
```bash
python train_basic.py
```

**Questions**:
1. What's the accuracy of your model?
2. Can you find the run in MLflow UI?
3. Where are the model artifacts stored?

---

### Exercise 2: Hyperparameter Tuning with Tracking (20 mins)

**Task**: Track multiple experiments with different hyperparameters

Create `hyperparameter_tuning.py`:

```python
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
import numpy as np

# Load data
data = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

mlflow.set_experiment("iris-hyperparameter-tuning")

# Hyperparameter grid
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 7, 10],
    'min_samples_split': [2, 5, 10]
}

best_accuracy = 0
best_params = {}

# Try different combinations
for n_est in param_grid['n_estimators']:
    for depth in param_grid['max_depth']:
        for min_split in param_grid['min_samples_split']:
            
            with mlflow.start_run(run_name=f"rf-n{n_est}-d{depth}-s{min_split}"):
                
                # Log parameters
                mlflow.log_param("n_estimators", n_est)
                mlflow.log_param("max_depth", depth)
                mlflow.log_param("min_samples_split", min_split)
                
                # Train model
                model = RandomForestClassifier(
                    n_estimators=n_est,
                    max_depth=depth,
                    min_samples_split=min_split,
                    random_state=42
                )
                model.fit(X_train, y_train)
                
                # Predictions
                predictions = model.predict(X_test)
                
                # Metrics
                accuracy = accuracy_score(y_test, predictions)
                precision = precision_score(y_test, predictions, average='weighted')
                recall = recall_score(y_test, predictions, average='weighted')
                
                mlflow.log_metric("accuracy", accuracy)
                mlflow.log_metric("precision", precision)
                mlflow.log_metric("recall", recall)
                
                # Track best model
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_params = {
                        'n_estimators': n_est,
                        'max_depth': depth,
                        'min_samples_split': min_split
                    }
                    
                    # Log as best model
                    mlflow.set_tag("best_model", "True")
                    mlflow.sklearn.log_model(model, "model")

print(f"Best Accuracy: {best_accuracy:.4f}")
print(f"Best Parameters: {best_params}")
```

**Your Task**:
1. Run the hyperparameter tuning script
2. Use MLflow UI to find the best model
3. Compare runs using the "Compare" feature
4. What hyperparameters gave the best results?

---

### Exercise 3: Logging Artifacts (15 mins)

**Task**: Log visualizations and additional artifacts

Create `train_with_artifacts.py`:

```python
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json

# Load data
data = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

mlflow.set_experiment("iris-with-artifacts")

with mlflow.start_run(run_name="model-with-visualizations"):
    
    # Parameters
    params = {
        'n_estimators': 100,
        'max_depth': 7,
        'random_state': 42
    }
    mlflow.log_params(params)
    
    # Train
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    # Metrics
    from sklearn.metrics import accuracy_score
    accuracy = accuracy_score(y_test, predictions)
    mlflow.log_metric("accuracy", accuracy)
    
    # 1. Log confusion matrix plot
    cm = confusion_matrix(y_test, predictions)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig('confusion_matrix.png')
    mlflow.log_artifact('confusion_matrix.png')
    plt.close()
    
    # 2. Log feature importance
    feature_importance = pd.DataFrame({
        'feature': data.feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    plt.figure(figsize=(10, 6))
    plt.barh(feature_importance['feature'], feature_importance['importance'])
    plt.xlabel('Importance')
    plt.title('Feature Importance')
    plt.tight_layout()
    plt.savefig('feature_importance.png')
    mlflow.log_artifact('feature_importance.png')
    plt.close()
    
    # 3. Log classification report as JSON
    report = classification_report(y_test, predictions, output_dict=True)
    with open('classification_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    mlflow.log_artifact('classification_report.json')
    
    # 4. Log feature importance as CSV
    feature_importance.to_csv('feature_importance.csv', index=False)
    mlflow.log_artifact('feature_importance.csv')
    
    # 5. Log model
    mlflow.sklearn.log_model(model, "model")
    
    print(f"✅ Model trained and artifacts logged!")
    print(f"   Accuracy: {accuracy:.4f}")
```

**Your Task**:
1. Run the script and check artifacts in MLflow UI
2. Download the confusion matrix image
3. View the classification report
4. Add a ROC curve visualization

---

### Exercise 4: Model Registry (10 mins)

**Task**: Register and version models in MLflow Model Registry

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Get the best run from experiment
experiment = client.get_experiment_by_name("iris-hyperparameter-tuning")
runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["metrics.accuracy DESC"],
    max_results=1
)

best_run = runs[0]
run_id = best_run.info.run_id

print(f"Best Run ID: {run_id}")
print(f"Best Accuracy: {best_run.data.metrics['accuracy']:.4f}")

# Register model
model_uri = f"runs:/{run_id}/model"
model_name = "iris-classifier"

# Create registered model
result = mlflow.register_model(model_uri, model_name)

print(f"✅ Model registered: {model_name}")
print(f"   Version: {result.version}")

# Transition model to staging
client.transition_model_version_stage(
    name=model_name,
    version=result.version,
    stage="Staging"
)

print(f"✅ Model transitioned to Staging")

# Later, promote to production
# client.transition_model_version_stage(
#     name=model_name,
#     version=result.version,
#     stage="Production"
# )
```

**Your Task**:
1. Register your best model
2. Transition it through stages: None → Staging → Production
3. View the model in the "Models" tab of MLflow UI
4. Add a description and tags to your registered model

---

### Exercise 5: Load and Use Registered Model (10 mins)

**Task**: Load a model from the registry and make predictions

Create `inference.py`:

```python
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.datasets import load_iris

# Load data
data = load_iris()
X_test = pd.DataFrame(data.data[:5], columns=data.feature_names)

print("Test Data:")
print(X_test)

# Load model from registry
model_name = "iris-classifier"
stage = "Staging"  # or "Production"

model = mlflow.sklearn.load_model(f"models:/{model_name}/{stage}")

# Make predictions
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)

print(f"\nPredictions: {predictions}")
print(f"Class names: {data.target_names}")
print(f"\nPredicted classes:")
for i, pred in enumerate(predictions):
    print(f"  Sample {i+1}: {data.target_names[pred]} (confidence: {probabilities[i][pred]:.2%})")

# Log inference
with mlflow.start_run(run_name="inference-test"):
    mlflow.log_param("model_stage", stage)
    mlflow.log_param("num_samples", len(X_test))
    mlflow.log_metric("avg_confidence", probabilities.max(axis=1).mean())
```

**Your Task**:
1. Load your registered model
2. Make predictions on new data
3. Compare predictions from "Staging" vs "Production" models
4. Create a simple REST API using Flask to serve predictions

---

## 🧪 Verification

Run the verification script:

```bash
python verify.py
```

**Expected Results**:
```
✅ MLflow UI accessible at http://localhost:5000
✅ Experiments created successfully
✅ At least 10 runs logged
✅ Model registered in Model Registry
✅ Artifacts (plots, reports) logged
✅ Model loaded and predictions made
```

## 📊 Success Criteria

- [ ] Successfully tracked multiple experiments
- [ ] Logged parameters, metrics, and artifacts
- [ ] Used MLflow UI to compare runs
- [ ] Registered model in Model Registry
- [ ] Transitioned model through stages
- [ ] Loaded and used registered model

## 🎓 Key Takeaways

1. **Reproducibility**: Track everything (data, code, params, metrics)
2. **Comparison**: Easily compare experiments to find best model
3. **Versioning**: Model registry provides versioning and lifecycle management
4. **Artifacts**: Log visualizations and reports for better understanding
5. **Collaboration**: Team can access and use same experiments

## 🏆 Challenge

**Advanced Exercise**: Create an automated hyperparameter optimization using Optuna or Hyperopt, logging all trials to MLflow, and automatically registering the best model.

See `challenges/auto-hyperparam-tuning.md` for details.

## 📚 Additional Resources

- [MLflow Tracking Documentation](https://mlflow.org/docs/latest/tracking.html)
- [MLflow Model Registry Guide](https://mlflow.org/docs/latest/model-registry.html)
- [MLflow Examples](https://github.com/mlflow/mlflow/tree/master/examples)

---

**Next Lab**: [Lab 2: Data Versioning with DVC](../lab-02-data-versioning/)
