# Model Monitoring & Observability

## Overview

Model monitoring tracks ML model performance in production, detecting issues before they impact users. It's essential for maintaining model reliability.

## What to Monitor

### 1. Performance Metrics
- Accuracy, Precision, Recall
- Business metrics (revenue, conversions)
- Prediction latency
- Error rates

### 2. Data Quality
- Missing values
- Out-of-range values
- Distribution changes
- Feature correlations

### 3. System Health
- API response time
- Request rate
- Resource usage (CPU, memory)
- Error logs

## Implementation Example

```python
from prometheus_client import Counter, Histogram, Gauge
import logging

# Metrics
predictions_total = Counter('predictions_total', 'Total predictions')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')
model_accuracy = Gauge('model_accuracy', 'Current model accuracy')

@app.post("/predict")
@prediction_latency.time()
def predict(data):
    try:
        prediction = model.predict(data)
        predictions_total.inc()
        
        # Log prediction for later analysis
        log_prediction(data, prediction)
        
        return {"prediction": prediction}
    except Exception as e:
        logging.error(f"Prediction failed: {e}")
        raise
```

## Monitoring Dashboard

Use Grafana + Prometheus:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'model-api'
    static_configs:
      - targets: ['localhost:8000']
```

## Alerts

```yaml
# Alert if accuracy drops
groups:
  - name: model_alerts
    rules:
      - alert: ModelAccuracyDrop
        expr: model_accuracy < 0.75
        for: 10m
        annotations:
          summary: "Model accuracy below threshold"
```

## Best Practices

✅ Monitor predictions continuously  
✅ Set up automated alerts  
✅ Track both ML and system metrics  
✅ Log predictions for analysis  
✅ Create monitoring dashboards  
✅ Define SLAs and track them

## Key Takeaways

✅ Monitoring prevents silent failures  
✅ Track performance, data, and system health  
✅ Automate alerts for issues  
✅ Dashboards provide visibility  
✅ Essential for production ML

---

**Next:** [Drift Detection](14-drift-detection.md)  
**Practice:** [Lab 06 - Model Monitoring](../mlops-practice/lab-06-model-monitoring/)
