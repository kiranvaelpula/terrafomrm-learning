# Lab 09: A/B Testing for ML Models

## Overview
Implement A/B testing to compare model versions in production, measure impact, and make data-driven deployment decisions.

**Duration:** 1 hour  
**Difficulty:** Advanced  
**Prerequisites:** Labs 01-08, statistics basics

## Learning Objectives
- Design A/B tests for ML models
- Implement traffic splitting
- Collect and analyze metrics
- Calculate statistical significance
- Perform gradual rollouts

## Why A/B Testing?

```
Without A/B Testing:
- Deploy and hope for the best
- No quantitative comparison
- Risk of regression
❌ Uncertain impact

With A/B Testing:
- Measure actual performance
- Statistical validation
- Controlled rollout
✅ Data-driven decisions
```

## Setup

### 1. Install Dependencies

```bash
pip install fastapi uvicorn mlflow
pip install scipy pandas numpy
pip install redis  # For traffic routing
```

## Implementation

### Step 1: Traffic Splitter

Create `src/ab_router.py`:

```python
import hashlib
import redis
from typing import Dict, Tuple
import json

class ABRouter:
    def __init__(self, redis_host='localhost', redis_port=6379):
        """Initialize A/B testing router"""
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.experiments = {}
    
    def create_experiment(self, experiment_id: str, variants: Dict[str, float]):
        """
        Create A/B experiment
        
        Args:
            experiment_id: Unique experiment identifier
            variants: Dict of variant_name -> traffic_percentage
                     e.g., {'control': 0.5, 'treatment': 0.5}
        """
        # Validate traffic percentages sum to 1.0
        total = sum(variants.values())
        assert abs(total - 1.0) < 0.001, f"Traffic percentages must sum to 1.0 (got {total})"
        
        # Store experiment config
        self.redis_client.set(
            f"experiment:{experiment_id}",
            json.dumps(variants)
        )
        
        print(f"✅ Created experiment: {experiment_id}")
        for variant, traffic in variants.items():
            print(f"   {variant}: {traffic:.1%}")
    
    def assign_variant(self, experiment_id: str, user_id: str) -> str:
        """Assign user to a variant"""
        
        # Check if user already assigned
        assignment_key = f"assignment:{experiment_id}:{user_id}"
        existing = self.redis_client.get(assignment_key)
        
        if existing:
            return existing
        
        # Get experiment config
        config_raw = self.redis_client.get(f"experiment:{experiment_id}")
        if not config_raw:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        variants = json.loads(config_raw)
        
        # Deterministic assignment based on hash
        hash_value = int(hashlib.md5(f"{experiment_id}:{user_id}".encode()).hexdigest(), 16)
        bucket = (hash_value % 10000) / 10000.0  # Value between 0 and 1
        
        # Assign to variant based on traffic percentages
        cumulative = 0
        for variant, percentage in sorted(variants.items()):
            cumulative += percentage
            if bucket <= cumulative:
                # Store assignment
                self.redis_client.set(assignment_key, variant, ex=86400*30)  # 30 days TTL
                return variant
        
        # Fallback (shouldn't reach here)
        return list(variants.keys())[0]
    
    def get_variant_counts(self, experiment_id: str) -> Dict[str, int]:
        """Get assignment counts per variant"""
        pattern = f"assignment:{experiment_id}:*"
        
        counts = {}
        for key in self.redis_client.scan_iter(match=pattern, count=1000):
            variant = self.redis_client.get(key)
            counts[variant] = counts.get(variant, 0) + 1
        
        return counts

# Example usage
if __name__ == "__main__":
    router = ABRouter()
    
    # Create experiment
    router.create_experiment(
        experiment_id='model_v2_test',
        variants={
            'control': 0.5,    # 50% to existing model
            'treatment': 0.5   # 50% to new model
        }
    )
    
    # Assign users
    for i in range(100):
        user_id = f"user_{i}"
        variant = router.assign_variant('model_v2_test', user_id)
        print(f"{user_id} -> {variant}")
    
    # Check distribution
    counts = router.get_variant_counts('model_v2_test')
    print(f"\nDistribution: {counts}")
```

### Step 2: A/B Testing API

Create `src/ab_api.py`:

```python
from fastapi import FastAPI, Request
import mlflow
import pandas as pd
from ab_router import ABRouter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="A/B Testing API")

# Initialize router
router = ABRouter()

# Load models
models = {
    'control': mlflow.pyfunc.load_model('models:/churn-predictor/Production'),
    'treatment': mlflow.pyfunc.load_model('models:/churn-predictor-v2/Staging')
}

@app.post("/predict")
async def predict(request: Request, customer_data: dict):
    """Make prediction with A/B testing"""
    
    customer_id = customer_data.get('customer_id')
    
    # Assign to variant
    variant = router.assign_variant('model_v2_test', customer_id)
    
    # Get model for variant
    model = models[variant]
    
    # Prepare data
    df = pd.DataFrame([customer_data])
    X = df.drop('customer_id', axis=1, errors='ignore')
    
    # Predict
    prediction = model.predict(X)[0]
    
    # Log for analysis
    logger.info(f"customer={customer_id}, variant={variant}, prediction={prediction}")
    
    # Store prediction for later analysis
    router.redis_client.lpush(
        f"predictions:{variant}",
        f"{customer_id},{prediction}"
    )
    
    return {
        'customer_id': customer_id,
        'prediction': int(prediction),
        'variant': variant
    }

@app.get("/experiment/status")
async def experiment_status():
    """Get experiment status"""
    
    counts = router.get_variant_counts('model_v2_test')
    
    return {
        'experiment_id': 'model_v2_test',
        'assignments': counts,
        'total': sum(counts.values())
    }
```

### Step 3: Metrics Collection

Create `src/ab_metrics.py`:

```python
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple
import redis

class ABMetricsAnalyzer:
    def __init__(self, redis_host='localhost'):
        self.redis_client = redis.Redis(host=redis_host, decode_responses=True)
    
    def collect_metrics(self, experiment_id: str, metric_name: str) -> Dict:
        """Collect metrics for each variant"""
        
        metrics = {}
        
        # Get variants from experiment config
        import json
        config = json.loads(self.redis_client.get(f"experiment:{experiment_id}"))
        
        for variant in config.keys():
            # Get metric values for this variant
            key = f"metrics:{experiment_id}:{variant}:{metric_name}"
            values = self.redis_client.lrange(key, 0, -1)
            values = [float(v) for v in values]
            
            if values:
                metrics[variant] = {
                    'values': values,
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'count': len(values),
                    'median': np.median(values)
                }
        
        return metrics
    
    def calculate_statistical_significance(self, 
                                          control_values: list,
                                          treatment_values: list,
                                          alpha: float = 0.05) -> Dict:
        """
        Calculate if difference is statistically significant
        
        Uses t-test for continuous metrics
        """
        # T-test
        t_statistic, p_value = stats.ttest_ind(treatment_values, control_values)
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt(
            (np.std(control_values)**2 + np.std(treatment_values)**2) / 2
        )
        cohens_d = (np.mean(treatment_values) - np.mean(control_values)) / pooled_std
        
        # Relative improvement
        control_mean = np.mean(control_values)
        treatment_mean = np.mean(treatment_values)
        relative_improvement = (treatment_mean - control_mean) / control_mean
        
        return {
            't_statistic': t_statistic,
            'p_value': p_value,
            'significant': p_value < alpha,
            'cohens_d': cohens_d,
            'effect_size': self._interpret_cohens_d(abs(cohens_d)),
            'control_mean': control_mean,
            'treatment_mean': treatment_mean,
            'absolute_improvement': treatment_mean - control_mean,
            'relative_improvement': relative_improvement
        }
    
    def _interpret_cohens_d(self, d: float) -> str:
        """Interpret effect size"""
        if d < 0.2:
            return 'negligible'
        elif d < 0.5:
            return 'small'
        elif d < 0.8:
            return 'medium'
        else:
            return 'large'
    
    def calculate_sample_size(self, 
                             baseline_rate: float,
                             mde: float,  # Minimum detectable effect
                             alpha: float = 0.05,
                             power: float = 0.8) -> int:
        """
        Calculate required sample size per variant
        
        Args:
            baseline_rate: Current conversion/success rate
            mde: Minimum detectable effect (e.g., 0.05 for 5% relative improvement)
            alpha: Significance level
            power: Statistical power
        """
        from scipy.stats import norm
        
        p1 = baseline_rate
        p2 = baseline_rate * (1 + mde)
        
        # Z-scores
        z_alpha = norm.ppf(1 - alpha/2)
        z_beta = norm.ppf(power)
        
        # Sample size calculation
        n = (
            (z_alpha * np.sqrt(2 * p1 * (1 - p1)) + 
             z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2)))**2 /
            (p2 - p1)**2
        )
        
        return int(np.ceil(n))
    
    def generate_report(self, experiment_id: str, metric_name: str = 'accuracy'):
        """Generate A/B test report"""
        
        metrics = self.collect_metrics(experiment_id, metric_name)
        
        if len(metrics) < 2:
            print("⚠️ Not enough data for comparison")
            return
        
        control = metrics.get('control', {})
        treatment = metrics.get('treatment', {})
        
        if not control or not treatment:
            print("⚠️ Missing control or treatment data")
            return
        
        # Statistical test
        sig_results = self.calculate_statistical_significance(
            control['values'],
            treatment['values']
        )
        
        print("\n" + "="*70)
        print(f"📊 A/B TEST REPORT: {experiment_id}")
        print("="*70)
        
        print(f"\n📈 Metric: {metric_name}")
        print(f"\n🔵 Control:")
        print(f"   Mean: {control['mean']:.4f} (±{control['std']:.4f})")
        print(f"   Samples: {control['count']}")
        
        print(f"\n🟢 Treatment:")
        print(f"   Mean: {treatment['mean']:.4f} (±{treatment['std']:.4f})")
        print(f"   Samples: {treatment['count']}")
        
        print(f"\n📊 Statistical Analysis:")
        print(f"   Absolute Improvement: {sig_results['absolute_improvement']:+.4f}")
        print(f"   Relative Improvement: {sig_results['relative_improvement']:+.2%}")
        print(f"   P-value: {sig_results['p_value']:.4f}")
        print(f"   Effect Size (Cohen's d): {sig_results['cohens_d']:.4f} ({sig_results['effect_size']})")
        
        if sig_results['significant']:
            if sig_results['relative_improvement'] > 0:
                print(f"\n✅ RESULT: Treatment is significantly BETTER (p < 0.05)")
                print(f"   RECOMMENDATION: Roll out treatment to 100%")
            else:
                print(f"\n❌ RESULT: Treatment is significantly WORSE (p < 0.05)")
                print(f"   RECOMMENDATION: Keep control, abandon treatment")
        else:
            print(f"\n⚠️ RESULT: No significant difference detected (p >= 0.05)")
            print(f"   RECOMMENDATION: Collect more data or abandon test")
        
        # Sample size check
        required_n = self.calculate_sample_size(
            baseline_rate=control['mean'],
            mde=0.05  # 5% MDE
        )
        print(f"\n📏 Sample Size:")
        print(f"   Current per variant: {control['count']}, {treatment['count']}")
        print(f"   Required for 5% MDE: {required_n} per variant")
        
        if min(control['count'], treatment['count']) < required_n:
            print(f"   ⚠️ Insufficient sample size - collect more data")
        
        print("="*70)

# Example usage
if __name__ == "__main__":
    analyzer = ABMetricsAnalyzer()
    
    # Simulate some metric data
    import redis
    r = redis.Redis(decode_responses=True)
    
    # Control model (baseline accuracy: 0.82)
    for _ in range(1000):
        r.lpush('metrics:model_v2_test:control:accuracy', np.random.normal(0.82, 0.05))
    
    # Treatment model (improved accuracy: 0.85)
    for _ in range(1000):
        r.lpush('metrics:model_v2_test:treatment:accuracy', np.random.normal(0.85, 0.05))
    
    # Generate report
    analyzer.generate_report('model_v2_test', 'accuracy')
```

### Step 4: Gradual Rollout

Create `src/gradual_rollout.py`:

```python
import time
from ab_router import ABRouter

class GradualRollout:
    def __init__(self):
        self.router = ABRouter()
    
    def execute_rollout(self, 
                       experiment_id: str,
                       stages: list,
                       stage_duration_hours: int = 24):
        """
        Execute gradual rollout
        
        Args:
            experiment_id: Experiment ID
            stages: List of dicts with traffic percentages
                   e.g., [{'control': 0.9, 'treatment': 0.1},
                         {'control': 0.5, 'treatment': 0.5},
                         {'control': 0, 'treatment': 1.0}]
            stage_duration_hours: Hours to wait between stages
        """
        
        for i, stage in enumerate(stages):
            print(f"\n🚀 Stage {i+1}/{len(stages)}")
            print(f"   Traffic: {stage}")
            
            # Update experiment config
            self.router.create_experiment(experiment_id, stage)
            
            if i < len(stages) - 1:
                print(f"   Waiting {stage_duration_hours} hours...")
                time.sleep(stage_duration_hours * 3600)
        
        print(f"\n✅ Rollout complete!")

# Example
if __name__ == "__main__":
    rollout = GradualRollout()
    
    # Define rollout stages
    stages = [
        {'control': 0.95, 'treatment': 0.05},   # 5% treatment
        {'control': 0.90, 'treatment': 0.10},   # 10% treatment
        {'control': 0.75, 'treatment': 0.25},   # 25% treatment
        {'control': 0.50, 'treatment': 0.50},   # 50% treatment
        {'control': 0.25, 'treatment': 0.75},   # 75% treatment
        {'control': 0.00, 'treatment': 1.00},   # 100% treatment
    ]
    
    # Execute (with short duration for testing)
    # rollout.execute_rollout('model_v2_test', stages, stage_duration_hours=1)
    print("Rollout plan prepared")
```

## Best Practices

✅ **Define success metrics upfront** - Know what you're measuring  
✅ **Calculate required sample size** - Don't stop too early  
✅ **Use randomization** - Avoid selection bias  
✅ **Monitor continuously** - Detect issues quickly  
✅ **Gradual rollout** - Minimize risk  
✅ **Document decisions** - Keep audit trail

## Key Takeaways

✅ A/B testing validates model improvements objectively  
✅ Statistical significance ensures reliable decisions  
✅ Gradual rollouts minimize production risk  
✅ Traffic splitting enables safe experimentation  
✅ Metrics collection enables data-driven decisions

## Next Steps

- **Lab 10**: Complete end-to-end MLOps project
- Add multi-armed bandit optimization
- Implement champion/challenger framework
- Add automated rollback on degradation

## Resources

- [A/B Testing Guide](https://www.optimizely.com/optimization-glossary/ab-testing/)
- [Statistical Significance](https://en.wikipedia.org/wiki/Statistical_significance)
- [Evan Miller's Sample Size Calculator](https://www.evanmiller.org/ab-testing/sample-size.html)
