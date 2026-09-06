# Model Serving

## Overview

Model serving is the process of making trained ML models accessible for predictions, typically via APIs. It's the bridge between model training and real-world use.

## 📖 Understanding Model Serving (Intuition First)

A trained model sitting in a file is like a brilliant expert locked in a room with no phone — all that knowledge, completely unreachable. Model serving is opening a phone line to that expert so applications can *ask questions and get answers*. Until you serve it, a model delivers exactly zero business value, no matter how accurate it is.

The central design question in serving is *when* predictions are needed. Sometimes you need answers instantly, one at a time, while a user waits — a fraud check as someone clicks "pay," or a recommendation as a page loads. That's **online/real-time serving**, and it lives or dies by latency (often needing sub-100ms responses). Other times you need to score millions of records overnight with no user waiting — like generating churn scores for every customer before the morning report. That's **batch serving**, where throughput matters far more than latency.

This distinction drives everything downstream. Real-time serving needs an always-on API, autoscaling for traffic spikes, low-latency infrastructure, and careful attention to the model's response time. Batch serving needs a scheduler, efficient bulk processing, and somewhere to store results — but doesn't care if a single prediction takes a second. Choosing the wrong pattern is a classic mistake: forcing batch-style heavy models into a real-time path causes timeouts, while running real-time infrastructure for a nightly job wastes money.

Serving is also where MLOps concerns get very real: you need to handle versioning (which model answers?), scaling (traffic isn't constant), monitoring (is it still accurate and fast?), and the dreaded **training/serving skew** — where features are computed slightly differently in serving than in training, silently corrupting predictions. This is why feature stores and shared transformation pipelines matter so much: the model must see production data in *exactly* the same shape it saw during training.

## Serving Patterns

### 1. Batch Prediction
Process large datasets at once, results stored for later use.

```python
# Daily batch scoring
predictions = model.predict(all_customers)
save_to_database(predictions)
```

**Use cases:** Nightly scoring, periodic reports, non-time-critical predictions

### 2. Real-time (Online) Serving
Immediate predictions via API endpoints.

```python
@app.post("/predict")
def predict(data: CustomerData):
    prediction = model.predict([data])
    return {"churn_probability": prediction[0]}
```

**Use cases:** Web applications, mobile apps, real-time decisions

### 3. Streaming
Continuous prediction on data streams.

```python
# Kafka consumer
for message in kafka_consumer:
    data = parse(message)
    prediction = model.predict(data)
    kafka_producer.send('predictions', prediction)
```

**Use cases:** IoT, fraud detection, real-time monitoring

## REST API Serving with FastAPI

```python
from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()
model = joblib.load('model.pkl')

@app.post("/predict")
def predict(features: List[float]):
    prediction = model.predict([features])
    return {"prediction": int(prediction[0])}
```

## Serving Frameworks

### TensorFlow Serving
```bash
# Serve SavedModel
tensorflow_model_server \
  --rest_api_port=8501 \
  --model_name=my_model \
  --model_base_path=/models/my_model
```

### Torch Serve
```bash
# Archive and serve PyTorch model
torch-model-archiver --model-name resnet \
  --version 1.0 \
  --model-file model.py \
  --serialized-file model.pth

torchserve --start --model-store model_store
```

### MLflow Models
```bash
# Serve MLflow model
mlflow models serve \
  -m models:/my-model/Production \
  -p 5000
```

## Performance Optimization

### 1. Model Optimization
```python
# Quantization
quantized_model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)
```

### 2. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def predict_with_cache(customer_id):
    return model.predict(get_features(customer_id))
```

### 3. Batch Processing
```python
# Batch requests together
@app.post("/predict/batch")
def predict_batch(requests: List[PredictionRequest]):
    features = [r.features for r in requests]
    predictions = model.predict(features)  # Single batch call
    return predictions
```

## Monitoring Serving

```python
from prometheus_client import Counter, Histogram

# Track predictions
prediction_counter = Counter('predictions_total', 'Total predictions made')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')

@app.post("/predict")
@prediction_latency.time()
def predict(data):
    prediction = model.predict(data)
    prediction_counter.inc()
    return prediction
```

## Best Practices

✅ Separate serving from training code  
✅ Version your serving API  
✅ Implement health checks  
✅ Add request validation  
✅ Monitor latency and throughput  
✅ Handle errors gracefully  
✅ Log predictions for monitoring

## Key Takeaways

✅ Choose serving pattern based on use case  
✅ REST APIs are most common for real-time  
✅ Optimize for latency in production  
✅ Monitor serving performance  
✅ Use frameworks for production serving

---

## 🎯 Interview Quick Points

- Model serving makes a trained model accessible for predictions (usually via API)
- Without serving, a model delivers zero value no matter how accurate
- **Online/real-time serving**: one prediction at a time, user waiting, latency-critical (<100ms)
- **Batch serving**: score millions of records offline, throughput matters, latency doesn't
- Choosing the wrong pattern is a classic mistake (batch model in real-time path = timeouts)
- Real-time needs: always-on API, autoscaling, low-latency infra
- Batch needs: scheduler, bulk processing, result storage
- **Training/serving skew** is a major risk — features must be computed identically in both
- Feature stores and shared pipelines prevent training/serving skew
- Serving frameworks: FastAPI/Flask, Seldon, KServe, SageMaker endpoints, TorchServe

**Next:** [CI/CD for ML](11-cicd-ml.md)  
**Practice:** [Lab 05 - Model Deployment](../mlops-practice/lab-05-model-deployment/)
