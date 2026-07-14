# A/B Testing for Machine Learning

## Overview

A/B testing compares two model versions in production using statistical methods to determine which performs better.

## Why A/B Test Models?

- Validate improvements objectively
- Measure real-world impact
- Make data-driven decisions
- Reduce deployment risk

## A/B Test Design

```
Users → Random Assignment → Model A (Control) or Model B (Treatment)
                          ↓                    ↓
                    Track Metrics        Track Metrics
                          ↓                    ↓
                    Statistical Comparison
```

## Implementation

```python
import hashlib

def assign_variant(user_id):
    """Deterministic user assignment"""
    hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
    return 'A' if hash_value % 2 == 0 else 'B'

@app.post("/predict")
def predict(user_id: str, features):
    variant = assign_variant(user_id)
    
    if variant == 'A':
        prediction = model_a.predict(features)
    else:
        prediction = model_b.predict(features)
    
    # Log for analysis
    log_experiment(user_id, variant, prediction)
    
    return {"prediction": prediction, "variant": variant}
```

## Statistical Analysis

```python
from scipy.stats import ttest_ind

# Collect metrics
accuracy_a = [...]  # Model A accuracies
accuracy_b = [...]  # Model B accuracies

# T-test
t_stat, p_value = ttest_ind(accuracy_a, accuracy_b)

if p_value < 0.05:
    if mean(accuracy_b) > mean(accuracy_a):
        print("✅ Model B is significantly better")
    else:
        print("❌ Model B is significantly worse")
else:
    print("⚠️ No significant difference")
```

## Sample Size Calculation

```python
from statsmodels.stats.power import zt_ind_solve_power

required_n = zt_ind_solve_power(
    effect_size=0.2,  # Minimum detectable effect
    alpha=0.05,       # Significance level
    power=0.8,        # Statistical power
    alternative='two-sided'
)

print(f"Required sample size per variant: {int(required_n)}")
```

## Best Practices

✅ Define success metrics upfront  
✅ Calculate required sample size  
✅ Run long enough for significance  
✅ Monitor during experiment  
✅ Use gradual rollout  
✅ Have rollback plan

---

**Next:** [Feature Stores](16-feature-stores.md)  
**Practice:** [Lab 09 - A/B Testing](../mlops-practice/lab-09-ab-testing/)
