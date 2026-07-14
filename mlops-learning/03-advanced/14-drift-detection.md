# Drift Detection

## Overview

Drift occurs when production data differs from training data, degrading model performance. Two types exist: data drift and concept drift.

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

**Next:** [A/B Testing for ML](15-ab-testing.md)  
**Practice:** [Lab 06 - Model Monitoring](../mlops-practice/lab-06-model-monitoring/)
