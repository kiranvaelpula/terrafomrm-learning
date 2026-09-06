# A/B Testing for Machine Learning

## Overview

A/B testing compares two model versions in production using statistical methods to determine which performs better.

## 📖 Understanding A/B Testing (Intuition First)

Suppose you've baked two versions of a cookie recipe and you're convinced the new one is better. How do you *know*? Not by tasting it yourself (you're biased) — you give version A to half your customers, version B to the other half, and measure who comes back for more. That controlled comparison, with real customers and real outcomes, is A/B testing. For ML, the "recipes" are two models, and the "customers coming back" are your business metrics.

The reason A/B testing exists is that **offline metrics lie about real-world impact**. A new model might have higher accuracy on your test set but actually *hurt* the business — maybe it's accurate but too aggressive, annoying users, or optimizing the wrong thing. The only way to truly know if model B beats model A is to let them both face real production traffic and measure what actually matters (revenue, conversions, engagement), not just accuracy in a lab.

The critical ingredient that makes A/B testing trustworthy is **statistical significance**. If model B gets a 2% higher conversion rate over 100 users, that could easily be random luck. A/B testing uses statistics (hypothesis testing, p-values, confidence intervals) to answer: "Is this difference real, or could it be chance?" You need enough traffic and enough time before declaring a winner — calling it too early is a classic, expensive mistake that leads teams to ship models that aren't actually better.

A/B testing overlaps with deployment strategies (canary is essentially a cautious A/B rollout), but its *purpose* is different: canary asks "is the new model safe?" while A/B testing asks "is the new model *better*, provably?" The rigor is higher — proper traffic splitting, controlling for confounders, and waiting for significance. It's how mature ML teams make deployment decisions based on evidence rather than hope or offline metrics alone.

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

## 🎯 Interview Quick Points

- A/B testing compares two models on real production traffic to prove which is better
- Analogy: give two cookie recipes to different customers, measure who comes back
- Exists because **offline metrics lie** — higher accuracy can still hurt the business
- Measure what matters: revenue, conversions, engagement — not just accuracy
- **Statistical significance** is essential — is the difference real or just luck?
- Uses hypothesis testing, p-values, confidence intervals
- Calling a winner too early (before significance) is a classic expensive mistake
- Different from canary: canary asks "is it safe?", A/B asks "is it provably better?"
- Requires proper traffic splitting and controlling for confounders
- How mature ML teams make evidence-based deployment decisions

**Next:** [Feature Stores](16-feature-stores.md)  
**Practice:** [Lab 09 - A/B Testing](../mlops-practice/lab-09-ab-testing/)
