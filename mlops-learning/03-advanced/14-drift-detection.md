# Drift Detection

## Overview

Drift occurs when production data differs from training data, degrading model performance. Two types exist: data drift and concept drift.

## 📖 Understanding Drift (Intuition First)

Imagine you learned to drive in a quiet small town, then moved to a chaotic megacity. Your driving skills didn't change — but the *world* did, and suddenly your once-safe habits get you into trouble. That mismatch between what you learned and the reality you now face is exactly what "drift" means for a model. The model is frozen at the moment it was trained; the world keeps moving; and the growing gap between them quietly erodes performance.

There are two flavors, and the distinction matters. **Data drift (covariate shift)** is when the *inputs* change — your users are now younger, transactions are larger, traffic comes from new regions. The relationship you learned might still be valid, but you're seeing inputs you weren't trained on. **Concept drift** is deeper and nastier: the *relationship itself* changes — what predicted fraud last year no longer predicts it because fraudsters adapted. Same inputs, different correct answer. Data drift means "the questions changed"; concept drift means "the answers changed."

Why detect drift at all instead of just watching accuracy? Because, as monitoring taught us, accuracy is often unknowable in real time — you don't get ground truth for days or weeks. Drift detection is the **early-warning system** you *can* measure instantly. You compare the statistical distribution of today's production data against your training/reference data. If they've diverged significantly, that's a red flag that your model is heading for trouble, long before the accuracy numbers confirm it.

The detection itself is statistical: tests like Kolmogorov-Smirnov (for numeric distributions), Population Stability Index (PSI), or chi-square (for categories) quantify "how different is now from before?" Tools like Evidently automate this. When drift crosses a threshold, it triggers investigation and often automatic retraining. The mental model: drift detection watches the *inputs and relationships* so you can act before the *outcomes* go bad.

## Types of Drift

### 1. Data Drift (Covariate Shift)
**Definition:** Input features (X) distribution changes  
**Example:** User demographics change over time

```python
# Training: Age 25-45
# Production: Age 18-65 (distribution shifted)
```

### 2. Concept Drift
**Definition:** Relationship between X and y changes  
**Example:** User behavior patterns change

```python
# Training: High price → Low sales
# Production: High price → High sales (luxury trend)
```

## Detection Methods

### Statistical Tests

```python
from scipy.stats import ks_2samp

# Kolmogorov-Smirnov test
statistic, p_value = ks_2samp(training_data['age'], production_data['age'])

if p_value < 0.05:
    print("⚠️ Data drift detected!")
```

### PSI (Population Stability Index)

```python
import numpy as np

def calculate_psi(expected, actual, bins=10):
    """Calculate PSI for drift detection"""
    expected_percents = np.histogram(expected, bins)[0] / len(expected)
    actual_percents = np.histogram(actual, bins)[0] / len(actual)
    
    psi = np.sum((actual_percents - expected_percents) * 
                 np.log(actual_percents / expected_percents))
    
    return psi

# PSI < 0.1: No drift
# 0.1 <= PSI < 0.2: Moderate drift
# PSI >= 0.2: Significant drift
```

## Monitoring for Drift

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=train_df, current_data=production_df)
report.show()
```

## Response Strategies

1. **Monitor:** Track drift over time
2. **Alert:** Notify team when drift detected
3. **Retrain:** Automatically trigger retraining
4. **Rollback:** Revert to previous model if needed

## Best Practices

✅ Monitor continuously  
✅ Set drift thresholds  
✅ Automate detection  
✅ Have retraining pipeline ready  
✅ Test detection before production

---

## 🎯 Interview Quick Points

- Drift = production data/relationships diverging from training, degrading the model
- Analogy: learning to drive in a small town, then moving to a chaotic megacity
- **Data drift (covariate shift)**: the inputs change ("the questions changed")
- **Concept drift**: the input→output relationship changes ("the answers changed") — nastier
- Drift detection is an **early-warning system** you can measure instantly (unlike delayed accuracy)
- Compare today's data distribution against a training/reference distribution
- Statistical tests: **Kolmogorov-Smirnov** (numeric), **PSI** (Population Stability Index), **chi-square** (categorical)
- When drift crosses a threshold → investigate → often trigger automatic retraining
- Tools: Evidently automates drift detection and reporting
- Drift watches inputs/relationships so you act before outcomes go bad

**Next:** [A/B Testing for ML](15-ab-testing.md)  
**Practice:** [Lab 06 - Model Monitoring](../mlops-practice/lab-06-model-monitoring/)
