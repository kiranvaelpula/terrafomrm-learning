# MLOps and AIOps Integration

Learn how to integrate MLOps practices with AIOps to build, deploy, and maintain machine learning models for IT operations at scale.

---

## Why MLOps for AIOps?

AIOps relies heavily on ML models that need to be:
- **Versioned**: Track model iterations
- **Deployed**: Push models to production
- **Monitored**: Detect model drift
- **Retrained**: Update models regularly
- **Reproducible**: Recreate models exactly

**Without MLOps**: Manual deployment, no versioning, model drift undetected
**With MLOps**: Automated pipeline, version control, continuous monitoring

---

## MLOps Lifecycle for AIOps Models

### 1. Experiment Tracking

Track AIOps model experiments to understand what works:

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import IsolationForest

# Start MLflow experiment
mlflow.set_experiment("aiops-anomaly-detection")

with mlflow.start_run():
    # Log parameters
    contamination = 0.1
    mlflow.log_param("contamination", contamination)
    mlflow.log_param("model_type", "IsolationForest")
    
    # Train model
    model = IsolationForest(contamination=contamination)
    model.fit(training_data)
    
    # Evaluate
    predictions = model.predict(test_data)
    precision, recall, f1 = evaluate_model(predictions, test_labels)
    
    # Log metrics
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)
    
    # Log model
    mlflow.sklearn.log_model(model, "anomaly_detector")
    
    print(f"Model logged with F1: {f1:.3f}")
```

**Benefits**:
- Compare different algorithms easily
- Track hyperparameter tuning
- Reproduce best models

---

### 2. Model Registry

Centralize model storage and versioning:

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Register model
model_uri = f"runs:/{run_id}/anomaly_detector"
model_details = mlflow.register_model(model_uri, "AnomalyDetector")

# Transition to staging
client.transition_model_version_stage(
    name="AnomalyDetector",
    version=model_details.version,
    stage="Staging"
)

# After validation, promote to production
client.transition_model_version_stage(
    name="AnomalyDetector",
    version=model_details.version,
    stage="Production"
)

print(f"Model version {model_details.version} in Production")
```

**Model Stages**:
- **None**: Just registered
- **Staging**: Testing in pre-prod
- **Production**: Serving live traffic
- **Archived**: Old versions

---

### 3. Model Deployment Pipeline

Automate model deployment:

```python
# deploy_aiops_model.py

import mlflow.pyfunc
from fastapi import FastAPI
import uvicorn

# Load production model
model_name = "AnomalyDetector"
model_version = "Production"
model = mlflow.pyfunc.load_model(f"models:/{model_name}/{model_version}")

# Create API
app = FastAPI()

@app.post("/predict")
def predict_anomaly(data: dict):
    """Detect anomalies in metrics"""
    features = extract_features(data['metrics'])
    prediction = model.predict(features)
    
    return {
        'is_anomaly': bool(prediction[0] == -1),
        'confidence': calculate_confidence(features),
        'model_version': get_model_version(),
        'timestamp': datetime.now().isoformat()
    }

@app.get("/health")
def health_check():
    """Check model service health"""
    return {
        'status': 'healthy',
        'model': model_name,
        'version': get_model_version()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Deployment with Docker**:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY deploy_aiops_model.py .

# Set MLflow tracking URI
ENV MLFLOW_TRACKING_URI=http://mlflow-server:5000

# Run service
CMD ["python", "deploy_aiops_model.py"]
```

---

### 4. Continuous Training Pipeline

Automate model retraining:

```python
# continuous_training.py

import schedule
import time
from datetime import datetime, timedelta

class ContinuousTrainer:
    def __init__(self):
        self.model_name = "AnomalyDetector"
        self.retraining_interval_days = 7
        
    def should_retrain(self):
        """Check if model needs retraining"""
        # Get current production model
        client = MlflowClient()
        model_versions = client.search_model_versions(
            f"name='{self.model_name}' and stage='Production'"
        )
        
        if not model_versions:
            return True
            
        # Check model age
        last_updated = model_versions[0].last_updated_timestamp
        age_days = (datetime.now().timestamp() - last_updated) / 86400
        
        if age_days > self.retraining_interval_days:
            return True
        
        # Check model performance
        current_f1 = self.evaluate_current_model()
        if current_f1 < 0.80:  # Performance threshold
            return True
            
        return False
    
    def retrain_model(self):
        """Retrain and deploy new model"""
        print("Starting model retraining...")
        
        # Fetch recent data
        training_data = fetch_training_data(days=30)
        test_data = fetch_test_data(days=7)
        
        # Train new model
        with mlflow.start_run():
            model = IsolationForest(contamination=0.1)
            model.fit(training_data)
            
            # Evaluate
            metrics = evaluate_model(model, test_data)
            
            # Log results
            for metric_name, value in metrics.items():
                mlflow.log_metric(metric_name, value)
            
            # Log model
            mlflow.sklearn.log_model(model, "anomaly_detector")
            
            # Get current production performance
            prod_f1 = self.evaluate_current_model()
            new_f1 = metrics['f1_score']
            
            # Deploy if better
            if new_f1 > prod_f1:
                print(f"New model better: {new_f1:.3f} > {prod_f1:.3f}")
                self.deploy_model(mlflow.active_run().info.run_id)
            else:
                print(f"Keeping current model: {prod_f1:.3f} >= {new_f1:.3f}")
    
    def deploy_model(self, run_id):
        """Deploy new model to production"""
        # Register model
        model_uri = f"runs:/{run_id}/anomaly_detector"
        model_details = mlflow.register_model(model_uri, self.model_name)
        
        # Transition to production
        client = MlflowClient()
        client.transition_model_version_stage(
            name=self.model_name,
            version=model_details.version,
            stage="Production"
        )
        
        print(f"Deployed model version {model_details.version}")
    
    def run(self):
        """Run continuous training loop"""
        schedule.every().day.at("02:00").do(
            lambda: self.retrain_model() if self.should_retrain() else None
        )
        
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour

# Run
trainer = ContinuousTrainer()
trainer.run()
```

---

## Model Monitoring for AIOps

### 1. Performance Monitoring

Track model accuracy in production:

```python
from prometheus_client import Counter, Histogram, Gauge
import numpy as np

# Prometheus metrics
prediction_counter = Counter(
    'aiops_predictions_total',
    'Total predictions made',
    ['model', 'prediction']
)

prediction_latency = Histogram(
    'aiops_prediction_latency_seconds',
    'Prediction latency'
)

model_accuracy = Gauge(
    'aiops_model_accuracy',
    'Current model accuracy'
)

class MonitoredModel:
    def __init__(self, model):
        self.model = model
        self.predictions = []
        self.actuals = []
        
    @prediction_latency.time()
    def predict(self, features):
        """Make prediction with monitoring"""
        prediction = self.model.predict(features)
        
        # Count prediction
        label = 'anomaly' if prediction[0] == -1 else 'normal'
        prediction_counter.labels(
            model='AnomalyDetector',
            prediction=label
        ).inc()
        
        # Store for accuracy calculation
        self.predictions.append(prediction[0])
        
        return prediction
    
    def record_actual(self, actual):
        """Record actual outcome (from human feedback)"""
        self.actuals.append(actual)
        
        # Update accuracy metric
        if len(self.actuals) >= 100:
            accuracy = np.mean(
                np.array(self.predictions[-100:]) == 
                np.array(self.actuals[-100:])
            )
            model_accuracy.set(accuracy)
```

---

### 2. Data Drift Detection

Detect when input data changes:

```python
from scipy import stats
import numpy as np

class DriftDetector:
    def __init__(self, reference_data):
        self.reference_data = reference_data
        self.reference_stats = self.compute_stats(reference_data)
        
    def compute_stats(self, data):
        """Compute statistical properties"""
        return {
            'mean': np.mean(data, axis=0),
            'std': np.std(data, axis=0),
            'min': np.min(data, axis=0),
            'max': np.max(data, axis=0)
        }
    
    def detect_drift(self, current_data):
        """Detect if current data has drifted"""
        current_stats = self.compute_stats(current_data)
        
        drift_detected = False
        drift_features = []
        
        for i in range(len(self.reference_stats['mean'])):
            # Kolmogorov-Smirnov test
            statistic, pvalue = stats.ks_2samp(
                self.reference_data[:, i],
                current_data[:, i]
            )
            
            if pvalue < 0.05:  # Significant difference
                drift_detected = True
                drift_features.append(i)
        
        if drift_detected:
            alert_drift(drift_features)
            trigger_retraining()
        
        return drift_detected, drift_features

# Usage
detector = DriftDetector(training_data)

# Check weekly
current_week_data = fetch_recent_data(days=7)
drifted, features = detector.detect_drift(current_week_data)

if drifted:
    print(f"Drift detected in features: {features}")
```

---

### 3. Model Drift Detection

Detect when model performance degrades:

```python
class ModelDriftDetector:
    def __init__(self, baseline_accuracy=0.95):
        self.baseline_accuracy = baseline_accuracy
        self.accuracy_history = []
        
    def check_drift(self, predictions, actuals):
        """Check if model accuracy has drifted"""
        accuracy = np.mean(predictions == actuals)
        self.accuracy_history.append(accuracy)
        
        # Check recent accuracy
        if len(self.accuracy_history) >= 100:
            recent_accuracy = np.mean(self.accuracy_history[-100:])
            
            # Alert if dropped significantly
            if recent_accuracy < self.baseline_accuracy * 0.9:
                return {
                    'drifted': True,
                    'current_accuracy': recent_accuracy,
                    'baseline_accuracy': self.baseline_accuracy,
                    'drop_percentage': (
                        (self.baseline_accuracy - recent_accuracy) / 
                        self.baseline_accuracy * 100
                    )
                }
        
        return {'drifted': False}

# Usage
drift_detector = ModelDriftDetector()

# After each prediction with feedback
result = drift_detector.check_drift(predictions, actuals)
if result['drifted']:
    alert(f"Model drift detected: {result['drop_percentage']:.1f}% drop")
    trigger_retraining()
```

---

## Feature Store for AIOps

Centralize feature engineering:

```python
# feature_store.py

import pandas as pd
from typing import List, Dict
import redis

class AIOpsFeatureStore:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379)
        
    def create_features(self, metrics_df: pd.DataFrame) -> pd.DataFrame:
        """Create features from raw metrics"""
        features = pd.DataFrame()
        
        # Time-based features
        features['hour'] = metrics_df['timestamp'].dt.hour
        features['day_of_week'] = metrics_df['timestamp'].dt.dayofweek
        features['is_weekend'] = features['day_of_week'].isin([5, 6])
        
        # Statistical features
        features['rolling_mean_10'] = metrics_df['value'].rolling(10).mean()
        features['rolling_std_10'] = metrics_df['value'].rolling(10).std()
        features['rolling_mean_60'] = metrics_df['value'].rolling(60).mean()
        
        # Rate of change
        features['rate_of_change'] = metrics_df['value'].diff()
        features['acceleration'] = features['rate_of_change'].diff()
        
        # Z-score
        features['z_score'] = (
            (metrics_df['value'] - metrics_df['value'].mean()) / 
            metrics_df['value'].std()
        )
        
        return features
    
    def store_features(self, entity_id: str, features: Dict):
        """Store features in Redis for fast access"""
        key = f"features:{entity_id}"
        self.redis_client.hmset(key, features)
        self.redis_client.expire(key, 86400)  # 24 hours
    
    def get_features(self, entity_id: str) -> Dict:
        """Retrieve features from store"""
        key = f"features:{entity_id}"
        return self.redis_client.hgetall(key)
    
    def get_training_dataset(
        self,
        start_time: str,
        end_time: str
    ) -> pd.DataFrame:
        """Get historical features for training"""
        # Fetch from data warehouse
        metrics = fetch_metrics(start_time, end_time)
        features = self.create_features(metrics)
        return features

# Usage
feature_store = AIOpsFeatureStore()

# For training
training_features = feature_store.get_training_dataset(
    start_time='2024-01-01',
    end_time='2024-01-31'
)

# For inference
features = feature_store.get_features('server-01')
```

---

## A/B Testing AIOps Models

Test new models safely:

```python
import random
from enum import Enum

class ModelVariant(Enum):
    CONTROL = "control"  # Current production model
    TREATMENT = "treatment"  # New model being tested

class ABTest:
    def __init__(self, treatment_percentage=10):
        self.treatment_percentage = treatment_percentage
        self.control_model = load_model("production")
        self.treatment_model = load_model("staging")
        
        # Metrics storage
        self.metrics = {
            ModelVariant.CONTROL: [],
            ModelVariant.TREATMENT: []
        }
    
    def get_variant(self, entity_id: str) -> ModelVariant:
        """Determine which model variant to use"""
        # Consistent assignment based on entity_id
        hash_value = hash(entity_id) % 100
        
        if hash_value < self.treatment_percentage:
            return ModelVariant.TREATMENT
        return ModelVariant.CONTROL
    
    def predict(self, entity_id: str, features):
        """Make prediction with A/B testing"""
        variant = self.get_variant(entity_id)
        
        # Use assigned model
        if variant == ModelVariant.TREATMENT:
            prediction = self.treatment_model.predict(features)
        else:
            prediction = self.control_model.predict(features)
        
        # Record for analysis
        return prediction, variant
    
    def record_outcome(self, variant: ModelVariant, outcome: dict):
        """Record outcome for analysis"""
        self.metrics[variant].append(outcome)
    
    def analyze_results(self):
        """Analyze A/B test results"""
        control_accuracy = np.mean([
            m['correct'] for m in self.metrics[ModelVariant.CONTROL]
        ])
        
        treatment_accuracy = np.mean([
            m['correct'] for m in self.metrics[ModelVariant.TREATMENT]
        ])
        
        # Statistical significance test
        from scipy.stats import ttest_ind
        
        control_scores = [m['correct'] for m in self.metrics[ModelVariant.CONTROL]]
        treatment_scores = [m['correct'] for m in self.metrics[ModelVariant.TREATMENT]]
        
        t_stat, p_value = ttest_ind(control_scores, treatment_scores)
        
        return {
            'control_accuracy': control_accuracy,
            'treatment_accuracy': treatment_accuracy,
            'improvement': treatment_accuracy - control_accuracy,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'recommendation': (
                'Deploy treatment' if p_value < 0.05 and treatment_accuracy > control_accuracy
                else 'Keep control'
            )
        }

# Usage
ab_test = ABTest(treatment_percentage=10)

# Make predictions
prediction, variant = ab_test.predict('server-01', features)

# Record outcome (after getting feedback)
ab_test.record_outcome(variant, {
    'correct': prediction_was_correct,
    'latency': prediction_latency
})

# Analyze after sufficient data
if len(ab_test.metrics[ModelVariant.CONTROL]) > 1000:
    results = ab_test.analyze_results()
    print(results)
```

---

## MLOps Tools for AIOps

### 1. MLflow Setup

```python
# mlflow_setup.py

import mlflow
from mlflow.tracking import MlflowClient

# Configure MLflow
mlflow.set_tracking_uri("http://mlflow-server:5000")

# Create experiments
mlflow.set_experiment("anomaly-detection")
mlflow.set_experiment("root-cause-analysis")
mlflow.set_experiment("capacity-forecasting")

# Create registered models
client = MlflowClient()
client.create_registered_model(
    "AnomalyDetector",
    tags={"task": "anomaly_detection"},
    description="Detects anomalies in system metrics"
)
```

### 2. Kubernetes Deployment

```yaml
# aiops-model-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: anomaly-detector
spec:
  replicas: 3
  selector:
    matchLabels:
      app: anomaly-detector
  template:
    metadata:
      labels:
        app: anomaly-detector
    spec:
      containers:
      - name: model-server
        image: aiops/anomaly-detector:v1.0
        ports:
        - containerPort: 8000
        env:
        - name: MLFLOW_TRACKING_URI
          value: "http://mlflow:5000"
        - name: MODEL_NAME
          value: "AnomalyDetector"
        - name: MODEL_STAGE
          value: "Production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: anomaly-detector-service
spec:
  selector:
    app: anomaly-detector
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## Best Practices

1. **Version Everything**: Models, features, code, data
2. **Automate Pipeline**: From training to deployment
3. **Monitor Constantly**: Performance and drift
4. **Test Safely**: Use A/B testing and canary deployments
5. **Document Models**: What they do, limitations, retraining schedule
6. **Implement Rollback**: Quick rollback if new model fails
7. **Track Lineage**: Know which data trained which model
8. **Use Feature Store**: Consistent features for training and inference

---

## Summary

MLOps practices enable AIOps at scale:
- Track experiments to find best models
- Deploy models reliably with CI/CD
- Monitor for data and model drift
- Retrain automatically when needed
- Test new models safely with A/B testing
- Use feature stores for consistency

**Next**: [AIOps Security and Privacy →](18-aiops-security-privacy.md)

