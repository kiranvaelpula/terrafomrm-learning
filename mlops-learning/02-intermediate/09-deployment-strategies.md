# Model Deployment Strategies

## Overview

Deployment strategies determine how new models are released to production. Choosing the right strategy minimizes risk and ensures smooth transitions.

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

**Next:** [Model Serving](10-model-serving.md)  
**Practice:** [Lab 05 - Model Deployment](../mlops-practice/lab-05-model-deployment/)
