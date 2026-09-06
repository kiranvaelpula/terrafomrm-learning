# Model Deployment Strategies

## Overview

Deployment strategies determine how new models are released to production. Choosing the right strategy minimizes risk and ensures smooth transitions.

## 📖 Understanding Deployment Strategies (Intuition First)

Imagine a restaurant wants to change its signature dish. The reckless approach: yank the old dish off the menu at 6pm and serve the new one to every customer that night — if it's bad, everyone's dinner is ruined and you find out only after the damage is done. A smarter chef first serves the new dish to a few tables (canary), watches their reactions, and only rolls it out to everyone once it's clearly a hit. If it flops, only a few plates were affected and you switch back instantly. Model deployment strategies are exactly this: different ways to introduce a new model while controlling how many users are exposed to risk.

The reason we need *strategies* at all — rather than just "replace the old model" — is that a new model can look great in testing and still fail on real production traffic. Real users behave differently than test data, and the cost of a bad model (wrong fraud decisions, bad recommendations, broken predictions) can be huge. Deployment strategies exist to limit the "blast radius" of a bad release and to make rollback fast and painless.

The main strategies trade off **risk, cost, and speed**. *Recreate* (replace) is simplest but has downtime and full exposure. *Blue-green* runs two full environments and flips traffic instantly (fast rollback, but double the infrastructure). *Canary* sends a small slice of traffic to the new model first, then gradually increases — safest for catching problems early, but slower to fully roll out. *Shadow* runs the new model alongside the old on real traffic without serving its results, purely to observe — zero user risk, ideal for validation before any real cutover.

For ML specifically, there's a twist: you're not just deploying code, you're deploying a *model whose quality you must verify on live data*. That's why canary and shadow deployments are especially popular in ML — they let you compare the new model's predictions against the current one on real traffic before trusting it. The deployment strategy is your safety net between "the model passed offline tests" and "the model is trusted with all production decisions."

## Deployment Strategies

### 1. Recreate (Replace) Deployment
**How it works:** Stop old version, deploy new version

```
Old Model (v1) → Downtime → New Model (v2)
```

**Pros:**
- Simple to implement
- Clean cutover

**Cons:**
- Downtime required
- High risk if new model fails

**Use when:** Development/testing environments

### 2. Blue-Green Deployment
**How it works:** Run both versions, switch traffic

```
Blue (v1) ← 100% traffic
Green (v2) ← 0% traffic

After validation:
Blue (v1) ← 0% traffic
Green (v2) ← 100% traffic
```

**Pros:**
- Zero downtime
- Instant rollback
- Full testing before switch

**Cons:**
- Requires 2x resources
- More complex infrastructure

**Use when:** Production deployments with risk management

**Implementation:**
```python
# Kubernetes with Services
apiVersion: v1
kind: Service
metadata:
  name: model-api
spec:
  selector:
    version: green  # Switch to 'blue' for rollback
  ports:
  - port: 80
    targetPort: 8000
```

### 3. Canary Deployment
**How it works:** Gradually shift traffic to new version

```
Stage 1: Old (95%) + New (5%)
Stage 2: Old (75%) + New (25%)
Stage 3: Old (50%) + New (50%)
Stage 4: Old (0%) + New (100%)
```

**Pros:**
- Gradual risk reduction
- Real-world validation
- Easy rollback

**Cons:**
- Longer deployment time
- Complex monitoring

**Use when:** High-risk changes, large user base

### 4. Shadow Deployment
**How it works:** Run new model alongside old, don't use predictions

```
User Request → Old Model (v1) → Response to User
            ↓
            New Model (v2) → Logged (not sent to user)
```

**Pros:**
- Zero risk to users
- Real production data testing
- Performance comparison

**Cons:**
- Double infrastructure cost
- Doesn't test user impact

**Use when:** Validating significant model changes

### 5. A/B Testing
**How it works:** Split users into groups, compare results

```
50% users → Model A
50% users → Model B

Measure: Accuracy, Latency, Business Metrics
```

**Pros:**
- Statistical validation
- Business metric impact
- Data-driven decisions

**Cons:**
- Requires more time
- Complex analysis

**Use when:** Comparing model performance impact

## Rollback Strategies

### Instant Rollback
```python
# Switch back to previous version
kubectl set image deployment/model-api \
  model=model-api:v1
```

### Percentage-based Rollback
```python
# Gradually reduce traffic to new version
# 100% → 75% → 50% → 0%
```

## Choosing a Strategy

| Requirement | Strategy |
|-------------|----------|
| Zero downtime | Blue-Green, Canary |
| Gradual rollout | Canary |
| Risk-free testing | Shadow |
| Business impact measurement | A/B Testing |
| Simple setup | Recreate |

## Best Practices

✅ Always have a rollback plan  
✅ Monitor metrics during deployment  
✅ Set automatic rollback triggers  
✅ Test in staging first  
✅ Document deployment process  
✅ Use canary for high-risk changes

## Key Takeaways

✅ Different strategies for different risk levels  
✅ Gradual rollouts reduce risk  
✅ Always enable quick rollback  
✅ Monitor during deployment  
✅ Choose based on requirements

---

## 🎯 Interview Quick Points

- Deployment strategies control how many users are exposed to a new model's risk
- Analogy: a chef testing a new dish on a few tables before the whole restaurant
- **Recreate/Replace**: stop old, start new — simple but has downtime + full exposure
- **Blue-Green**: two full environments, instant traffic flip — fast rollback, double cost
- **Canary**: small % of traffic first, gradually increase — safest, catches issues early
- **Shadow**: new model runs on real traffic but results not served — zero user risk, pure validation
- Trade-offs are **risk vs. cost vs. speed**
- ML twist: you must verify model quality on *live* data — canary and shadow are especially useful
- **Always have a rollback plan** and automated rollback triggers (error rate, latency thresholds)
- The strategy is your safety net between "passed offline tests" and "trusted in production"

**Next:** [Model Serving](10-model-serving.md)  
**Practice:** [Lab 05 - Model Deployment](../mlops-practice/lab-05-model-deployment/)
