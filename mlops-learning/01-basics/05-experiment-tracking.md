# Experiment Tracking Basics

## Overview

Experiment tracking is the practice of logging, organizing, and comparing machine learning experiments. It's fundamental to MLOps because it enables reproducibility, collaboration, and continuous improvement.

## The Problem Without Experiment Tracking

Imagine training 50 models with different hyperparameters:

```
❌ Without tracking:
- "Which model was best?"
- "What parameters did I use?"
- "Can't remember what I tried yesterday"
- "Lost the model file"
- "Can't reproduce results"
```

```
✅ With tracking:
- All experiments logged automatically
- Easy comparison of results
- Full reproducibility
- Organized model artifacts
- Team collaboration enabled
```

## What to Track

### 1. Parameters (Inputs)
```python
params = {
    'n_estimators': 100,
    'max_depth': 10,
    'learning_rate': 0.01,
    'train_data': 'data/train_v2.csv'
}
```

### 2. Metrics (Outputs)
```python
metrics = {
    'accuracy': 0.92,
    'precision': 0.89,
    'recall': 0.95,
    'f1_score': 0.92,
    'training_time': 45.2
}
```

### 3. Artifacts (Files)
- Trained model files (.pkl, .h5)
- Plots and visualizations
- Confusion matrices
- Feature importance charts
- Training logs

### 4. Metadata
- Date and time
- Code version (git commit)
- Data version
- Environment (Python version, dependencies)
- Hardware used

## MLflow: Your First Tracking Tool

MLflow is the most popular open-source experiment tracking platform.

### Installation
```bash
pip install mlflow
```

### Basic Usage

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Start tracking
mlflow.set_experiment("my-first-experiment")

with mlflow.start_run():
    
    # Log parameters
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, max_depth=10)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Log metrics
    mlflow.log_metric("accuracy", accuracy)
    
    # Log model
    mlflow.sklearn.log_model(model, "random_forest_model")
    
    print(f"Model logged with accuracy: {accuracy:.4f}")
```

### Viewing Results

```bash
# Start MLflow UI
mlflow ui

# Open browser to http://localhost:5000
```

## Complete Tracking Example

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import pandas as pd
import matplotlib.pyplot as plt

def train_with_tracking(params):
    """Train model with complete experiment tracking"""
    
    # Set experiment
    mlflow.set_experiment("customer-churn-prediction")
    
    with mlflow.start_run(run_name=f"rf_{params['n_estimators']}"):
        
        # Log all parameters
        mlflow.log_params(params)
        
        # Log dataset info
        mlflow.log_param("data_path", "data/customers.csv")
        mlflow.log_param("data_size", len(df))
        
        # Load and split data
        X = df.drop('churn', axis=1)
        y = df['churn']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
        
        # Log all metrics
        mlflow.log_metrics(metrics)
        
        # Create and log confusion matrix plot
        from sklearn.metrics import confusion_matrix
        import seaborn as sns
        
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.savefig('confusion_matrix.png')
        mlflow.log_artifact('confusion_matrix.png')
        plt.close()
        
        # Log feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        feature_importance.to_csv('feature_importance.csv', index=False)
        mlflow.log_artifact('feature_importance.csv')
        
        # Log the model
        mlflow.sklearn.log_model(
            model, 
            "model",
            registered_model_name="churn-predictor"
        )
        
        # Log code version
        import subprocess
        try:
            git_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
            mlflow.log_param("git_commit", git_commit)
        except:
            pass
        
        print(f"✅ Experiment logged: accuracy={metrics['accuracy']:.4f}")
        
        return model, metrics

# Run multiple experiments
experiment_configs = [
    {'n_estimators': 50, 'max_depth': 10, 'random_state': 42},
    {'n_estimators': 100, 'max_depth': 10, 'random_state': 42},
    {'n_estimators': 100, 'max_depth': 20, 'random_state': 42},
    {'n_estimators': 200, 'max_depth': 20, 'random_state': 42},
]

for config in experiment_configs:
    train_with_tracking(config)
```

## Comparing Experiments

### In MLflow UI
1. Open http://localhost:5000
2. Select your experiment
3. Check multiple runs
4. Click "Compare"
5. View side-by-side comparison

### Programmatically
```python
import mlflow

# Search for all runs
client = mlflow.tracking.MlflowClient()
experiment = client.get_experiment_by_name("customer-churn-prediction")

runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["metrics.accuracy DESC"],
    max_results=10
)

# Display top runs
for run in runs:
    print(f"Run ID: {run.info.run_id}")
    print(f"  Accuracy: {run.data.metrics['accuracy']:.4f}")
    print(f"  Parameters: {run.data.params}")
    print()
```

## Organizing Experiments

### Use Meaningful Names
```python
# Bad
mlflow.set_experiment("exp1")

# Good
mlflow.set_experiment("customer-churn-rf-baseline")
```

### Tag Your Runs
```python
with mlflow.start_run():
    mlflow.set_tag("model_type", "random_forest")
    mlflow.set_tag("data_version", "v2.1")
    mlflow.set_tag("experiment_goal", "baseline")
    mlflow.set_tag("team", "data-science")
```

### Use Nested Runs
```python
with mlflow.start_run(run_name="hyperparameter_tuning"):
    
    for params in param_grid:
        with mlflow.start_run(run_name=f"trial_{i}", nested=True):
            # Train and log
            train_model(params)
```

## Best Practices

### 1. Track Everything
```python
# Parameters
mlflow.log_params({
    'model_type': 'random_forest',
    'train_size': len(X_train),
    'features': X_train.columns.tolist()
})

# Metrics
mlflow.log_metrics({
    'train_accuracy': train_acc,
    'test_accuracy': test_acc,
    'training_time_seconds': training_time
})

# Artifacts
mlflow.log_artifact('model.pkl')
mlflow.log_artifact('scaler.pkl')
mlflow.log_artifact('config.yaml')
```

### 2. Use Consistent Naming
```python
# Standardize metric names
METRIC_NAMES = {
    'accuracy': 'test_accuracy',
    'precision': 'test_precision',
    'recall': 'test_recall'
}
```

### 3. Add Context
```python
# Log environment info
mlflow.log_param("python_version", sys.version)
mlflow.log_param("sklearn_version", sklearn.__version__)
mlflow.log_param("platform", platform.platform())
```

### 4. Clean Up
```python
# Delete failed runs
if training_failed:
    mlflow.end_run(status='FAILED')
```

## Tracking During Development

### Jupyter Notebook
```python
# At the start of notebook
import mlflow
mlflow.set_experiment("notebook-experiments")

# In each cell where you train
with mlflow.start_run(run_name="cell_5_rf_model"):
    # Your training code
    mlflow.log_param("cell_number", 5)
```

### Python Script
```python
# script.py
if __name__ == "__main__":
    mlflow.set_experiment("script-experiments")
    
    with mlflow.start_run():
        main()
```

## Common Pitfalls

❌ **Don't:**
- Forget to log parameters
- Only log final metrics
- Use generic experiment names
- Skip artifact logging
- Ignore run organization

✅ **Do:**
- Log comprehensive information
- Track intermediate metrics
- Use descriptive names
- Save all important artifacts
- Organize with tags and nested runs

## Alternative Tools

While MLflow is most popular, other options include:

### Weights & Biases (W&B)
```python
import wandb

wandb.init(project="my-project")
wandb.config.update(params)
wandb.log({"accuracy": 0.92})
```

### Neptune
```python
import neptune

run = neptune.init_run(project="workspace/project")
run["parameters"] = params
run["metrics/accuracy"] = 0.92
```

### TensorBoard
```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter('runs/experiment_1')
writer.add_scalar('accuracy', 0.92, epoch)
```

## Integration with Your Pipeline

```python
class MLPipelineWithTracking:
    def __init__(self, config, experiment_name):
        self.config = config
        mlflow.set_experiment(experiment_name)
    
    def run(self):
        with mlflow.start_run():
            # Log config
            mlflow.log_params(self.config)
            
            # Execute pipeline steps
            data = self.load_data()
            mlflow.log_param("data_size", len(data))
            
            X_train, X_test, y_train, y_test = self.split_data(data)
            mlflow.log_param("train_size", len(X_train))
            
            model = self.train_model(X_train, y_train)
            
            metrics = self.evaluate(model, X_test, y_test)
            mlflow.log_metrics(metrics)
            
            mlflow.sklearn.log_model(model, "model")
            
            return model, metrics
```

## Key Takeaways

✅ Track parameters, metrics, and artifacts for every experiment  
✅ Use meaningful experiment and run names  
✅ Compare experiments to find best models  
✅ Make experiments reproducible  
✅ Collaborate effectively with teams  
✅ MLflow is the industry standard tool

## Interview Questions

**Q: Why is experiment tracking important?**
A: It enables reproducibility, helps compare different approaches, facilitates collaboration, and maintains a history of what was tried.

**Q: What's the difference between parameters and metrics?**
A: Parameters are inputs/settings (what you control), metrics are outputs/results (what you measure).

**Q: How do you reproduce an experiment?**
A: Log all parameters, data versions, code versions, and artifacts. Use the same inputs to get the same outputs.

**Q: What should you track for every experiment?**
A: Parameters, metrics, model artifacts, data version, code version, environment, and execution time.

## Practice Exercise

Track 5 different models:
1. Set up MLflow
2. Create an experiment
3. Train 5 models with different parameters
4. Log all parameters and metrics
5. View results in MLflow UI
6. Find the best model
7. Load and use the best model

## Resources

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [Experiment Tracking Best Practices](https://neptune.ai/blog/ml-experiment-tracking)

---

**Next:** [Feature Engineering Pipeline](../02-intermediate/06-feature-engineering.md)  
**Practice:** [Lab 01 - Experiment Tracking](../mlops-practice/lab-01-experiment-tracking/)
