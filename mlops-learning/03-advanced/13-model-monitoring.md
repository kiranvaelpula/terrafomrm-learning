# Model Monitoring & Observability

## Overview

Model monitoring tracks ML model performance in production, detecting issues before they impact users. It's essential for maintaining model reliability.

## 📖 Understanding Model Monitoring (Intuition First)

A newly deployed model is like a new employee who was brilliant on their first day — but you can't just walk away and assume they'll stay brilliant forever. The world changes around them, and without check-ins you won't notice they've quietly started making mistakes until a customer complains. Model monitoring is the ongoing performance review that catches the slide *before* it becomes a disaster.

The crucial insight is that **models fail silently**. Traditional software fails loudly — it throws an error, crashes, returns a 500. A decaying model does none of that. It keeps returning confident predictions with the exact same latency and zero errors; they're just increasingly *wrong*. Your API dashboard looks perfectly healthy while the model quietly costs you money. This is why you can't monitor ML systems the same way you monitor regular services — "is it up and fast?" completely misses "is it still correct?"

So model monitoring watches multiple layers at once. There's **operational health** (latency, throughput, errors) — same as any service. But then there's **ML-specific health**: prediction accuracy (when you eventually get ground truth), the distribution of inputs (data drift), the distribution of outputs (are predictions suddenly skewing?), and business metrics (is the model actually driving revenue/conversions?). A drop in any of these is an early warning even before accuracy officially tanks.

The hardest part of ML monitoring is that **ground truth is often delayed or missing**. If you predict whether a customer will churn in 30 days, you won't *know* if you were right for 30 days. So monitoring leans heavily on *proxy* signals — especially input drift — that you can measure immediately, as leading indicators of trouble. When monitoring catches a problem, it triggers the loop back to retraining. Monitoring is the sense organ of MLOps: without it, the whole "detect decay → retrain" cycle is blind.

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

## 🎯 Interview Quick Points

- Model monitoring tracks production performance to catch degradation before users do
- **Models fail silently** — no errors, same latency, just increasingly wrong predictions
- "Is it up and fast?" misses "is it still correct?" — ML needs deeper monitoring
- Monitor layers: operational (latency/errors), accuracy, input drift, output drift, business metrics
- **Ground truth is often delayed/missing** — you may not know if predictions were right for weeks
- So monitoring relies on **proxy signals** (especially input drift) as leading indicators
- Monitoring is the trigger for the retrain loop — it's the "sense organ" of MLOps
- Tools: Evidently, WhyLabs, Arize, Prometheus/Grafana for operational metrics
- Set alerting thresholds so degradation triggers investigation/retraining automatically
- Business metrics matter most — a model can be "accurate" yet hurt revenue

**Next:** [Drift Detection](14-drift-detection.md)  
**Practice:** [Lab 06 - Model Monitoring](../mlops-practice/lab-06-model-monitoring/)
