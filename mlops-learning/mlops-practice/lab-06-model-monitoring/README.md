# Lab 06: Model Monitoring & Drift Detection

## Overview
Implement comprehensive model monitoring to detect performance degradation, data drift, and concept drift. Learn to set up alerts and automated retraining triggers.

**Duration:** 1 hour  
**Difficulty:** Intermediate  
**Prerequisites:** Labs 01-05, statistics basics

## Learning Objectives
- Monitor model performance metrics
- Detect data drift
- Identify concept drift
- Set up automated alerts
- Trigger model retraining

## Why Model Monitoring?

```
Without Monitoring:
- Silent performance degradation
- Data changes go unnoticed
- Models become stale
❌ Production failures

With Monitoring:
- Real-time performance tracking
- Early drift detection
- Proactive retraining
✅ Reliable predictions
```

## Setup

### 1. Install Dependencies

```bash
pip install evidently pandas numpy scikit-learn
pip install prometheus-client grafana-api
pip install scipy matplotlib seaborn
```

## Implementation

### Step 1: Performance Monitoring

Create `src/performance_monitor.py`:

```python
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from datetime import datetime, timedelta
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self, metrics_file='monitoring/performance_metrics.jsonl'):
        self.metrics_file = metrics_file
        self.alert_thresholds = {
            'accuracy': 0.75,
            'f1_score': 0.70,
            'roc_auc': 0.75
        }
    
    def calculate_metrics(self, y_true, y_pred, y_proba=None):
        """Calculate all performance metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0),
            'sample_count': len(y_true),
            'positive_rate': y_pred.mean()
        }
        
        if y_proba is not None:
            metrics['roc_auc'] = roc_auc_score(y_true, y_proba)
        
        return metrics
    
    def log_metrics(self, metrics):
        """Log metrics to file"""
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
        
        logger.info(f"Metrics logged: accuracy={metrics['accuracy']:.4f}, f1={metrics['f1_score']:.4f}")
    
    def load_historical_metrics(self, days=7):
        """Load recent metrics"""
        try:
            with open(self.metrics_file, 'r') as f:
                lines = f.readlines()
            
            metrics = [json.loads(line) for line in lines]
            df = pd.DataFrame(metrics)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter recent
            cutoff = datetime.now() - timedelta(days=days)
            df = df[df['timestamp'] > cutoff]
            
            return df
        except FileNotFoundError:
            return pd.DataFrame()
    
    def check_performance_degradation(self, current_metrics):
        """Check if performance has degraded"""
        alerts = []
        
        for metric, threshold in self.alert_thresholds.items():
            if metric in current_metrics:
                value = current_metrics[metric]
                
                if value < threshold:
                    alerts.append({
                        'metric': metric,
                        'value': value,
                        'threshold': threshold,
                        'severity': 'HIGH' if value < threshold * 0.9 else 'MEDIUM'
                    })
        
        return alerts
    
    def generate_performance_report(self):
        """Generate performance report"""
        df = self.load_historical_metrics(days=30)
        
        if len(df) == 0:
            print("No historical metrics available")
            return
        
        print("\n" + "="*70)
        print("📊 MODEL PERFORMANCE REPORT (Last 30 Days)")
        print("="*70)
        
        # Overall statistics
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Predictions: {df['sample_count'].sum():,.0f}")
        print(f"   Average Accuracy: {df['accuracy'].mean():.4f}")
        print(f"   Average F1 Score: {df['f1_score'].mean():.4f}")
        
        # Recent performance
        recent = df.tail(7)
        print(f"\n📅 Last 7 Days:")
        print(f"   Average Accuracy: {recent['accuracy'].mean():.4f}")
        print(f"   Accuracy Std Dev: {recent['accuracy'].std():.4f}")
        
        # Trend
        if len(df) > 14:
            first_half = df.head(len(df)//2)['accuracy'].mean()
            second_half = df.tail(len(df)//2)['accuracy'].mean()
            trend = (second_half - first_half) / first_half * 100
            
            trend_icon = "📈" if trend > 0 else "📉"
            print(f"\n{trend_icon} Trend: {trend:+.2f}%")
        
        # Alerts
        current_metrics = df.iloc[-1].to_dict()
        alerts = self.check_performance_degradation(current_metrics)
        
        if alerts:
            print(f"\n⚠️  ALERTS ({len(alerts)}):")
            for alert in alerts:
                print(f"   {alert['severity']}: {alert['metric']} = {alert['value']:.4f} (threshold: {alert['threshold']})")
        else:
            print(f"\n✅ No performance alerts")
        
        print("="*70)

# Example usage
if __name__ == "__main__":
    monitor = PerformanceMonitor()
    
    # Simulate some predictions
    y_true = np.random.binomial(1, 0.3, 1000)
    y_pred = np.random.binomial(1, 0.3, 1000)
    y_proba = np.random.random(1000)
    
    # Calculate and log metrics
    metrics = monitor.calculate_metrics(y_true, y_pred, y_proba)
    monitor.log_metrics(metrics)
    
    # Generate report
    monitor.generate_performance_report()
```

### Step 2: Data Drift Detection

Create `src/drift_detector.py`:

```python
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataDriftDetector:
    def __init__(self, reference_data: pd.DataFrame):
        """
        Initialize with reference dataset (training data)
        """
        self.reference_data = reference_data
        self.reference_stats = self._calculate_statistics(reference_data)
    
    def _calculate_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate statistical properties"""
        stats_dict = {}
        
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                stats_dict[col] = {
                    'mean': df[col].mean(),
                    'std': df[col].std(),
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'median': df[col].median(),
                    'q25': df[col].quantile(0.25),
                    'q75': df[col].quantile(0.75)
                }
            else:
                # Categorical
                stats_dict[col] = {
                    'value_counts': df[col].value_counts().to_dict(),
                    'unique_count': df[col].nunique()
                }
        
        return stats_dict
    
    def detect_drift_kolmogorov_smirnov(self, current_data: pd.DataFrame, 
                                        threshold: float = 0.05) -> Dict:
        """
        Detect drift using Kolmogorov-Smirnov test
        Null hypothesis: distributions are the same
        """
        drift_results = {}
        
        for col in current_data.columns:
            if col not in self.reference_data.columns:
                continue
            
            if current_data[col].dtype in ['int64', 'float64']:
                # KS test for numerical features
                statistic, p_value = stats.ks_2samp(
                    self.reference_data[col].dropna(),
                    current_data[col].dropna()
                )
                
                drift_results[col] = {
                    'test': 'kolmogorov_smirnov',
                    'statistic': statistic,
                    'p_value': p_value,
                    'drift_detected': p_value < threshold,
                    'severity': self._classify_drift_severity(p_value, threshold)
                }
        
        return drift_results
    
    def detect_drift_psi(self, current_data: pd.DataFrame, 
                        bins: int = 10, threshold: float = 0.1) -> Dict:
        """
        Population Stability Index (PSI)
        PSI < 0.1: No significant drift
        0.1 <= PSI < 0.2: Moderate drift
        PSI >= 0.2: Significant drift
        """
        drift_results = {}
        
        for col in current_data.columns:
            if col not in self.reference_data.columns:
                continue
            
            if current_data[col].dtype in ['int64', 'float64']:
                try:
                    # Bin data
                    ref_col = self.reference_data[col].dropna()
                    curr_col = current_data[col].dropna()
                    
                    # Create bins based on reference data
                    bins_edges = np.histogram_bin_edges(ref_col, bins=bins)
                    
                    # Calculate distributions
                    ref_dist, _ = np.histogram(ref_col, bins=bins_edges)
                    curr_dist, _ = np.histogram(curr_col, bins=bins_edges)
                    
                    # Normalize
                    ref_dist = ref_dist / len(ref_col)
                    curr_dist = curr_dist / len(curr_col)
                    
                    # Avoid division by zero
                    ref_dist = np.where(ref_dist == 0, 0.0001, ref_dist)
                    curr_dist = np.where(curr_dist == 0, 0.0001, curr_dist)
                    
                    # Calculate PSI
                    psi = np.sum((curr_dist - ref_dist) * np.log(curr_dist / ref_dist))
                    
                    drift_results[col] = {
                        'test': 'psi',
                        'psi_value': psi,
                        'drift_detected': psi >= threshold,
                        'severity': self._classify_psi_severity(psi)
                    }
                
                except Exception as e:
                    logger.warning(f"PSI calculation failed for {col}: {e}")
        
        return drift_results
    
    def detect_drift_chi_squared(self, current_data: pd.DataFrame,
                                threshold: float = 0.05) -> Dict:
        """
        Chi-squared test for categorical features
        """
        drift_results = {}
        
        for col in current_data.columns:
            if col not in self.reference_data.columns:
                continue
            
            if current_data[col].dtype == 'object' or current_data[col].dtype.name == 'category':
                try:
                    # Get value counts
                    ref_counts = self.reference_data[col].value_counts()
                    curr_counts = current_data[col].value_counts()
                    
                    # Align categories
                    all_categories = set(ref_counts.index) | set(curr_counts.index)
                    
                    ref_freq = [ref_counts.get(cat, 0) for cat in all_categories]
                    curr_freq = [curr_counts.get(cat, 0) for cat in all_categories]
                    
                    # Chi-squared test
                    statistic, p_value = stats.chisquare(curr_freq, ref_freq)
                    
                    drift_results[col] = {
                        'test': 'chi_squared',
                        'statistic': statistic,
                        'p_value': p_value,
                        'drift_detected': p_value < threshold,
                        'severity': self._classify_drift_severity(p_value, threshold)
                    }
                
                except Exception as e:
                    logger.warning(f"Chi-squared test failed for {col}: {e}")
        
        return drift_results
    
    def _classify_drift_severity(self, p_value: float, threshold: float) -> str:
        """Classify drift severity based on p-value"""
        if p_value >= threshold:
            return "NONE"
        elif p_value >= threshold / 2:
            return "LOW"
        elif p_value >= threshold / 10:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _classify_psi_severity(self, psi: float) -> str:
        """Classify drift severity based on PSI"""
        if psi < 0.1:
            return "NONE"
        elif psi < 0.2:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def comprehensive_drift_report(self, current_data: pd.DataFrame):
        """Generate comprehensive drift report"""
        print("\n" + "="*70)
        print("🔍 DATA DRIFT DETECTION REPORT")
        print("="*70)
        
        # Run all tests
        ks_results = self.detect_drift_kolmogorov_smirnov(current_data)
        psi_results = self.detect_drift_psi(current_data)
        chi_results = self.detect_drift_chi_squared(current_data)
        
        # Combine results
        all_features = set(ks_results.keys()) | set(psi_results.keys()) | set(chi_results.keys())
        
        drift_detected = False
        
        for feature in sorted(all_features):
            has_drift = False
            severity = "NONE"
            
            if feature in ks_results and ks_results[feature]['drift_detected']:
                has_drift = True
                severity = max(severity, ks_results[feature]['severity'], key=lambda x: ['NONE', 'LOW', 'MEDIUM', 'HIGH'].index(x))
            
            if feature in psi_results and psi_results[feature]['drift_detected']:
                has_drift = True
                severity = max(severity, psi_results[feature]['severity'], key=lambda x: ['NONE', 'LOW', 'MEDIUM', 'HIGH'].index(x))
            
            if feature in chi_results and chi_results[feature]['drift_detected']:
                has_drift = True
                severity = max(severity, chi_results[feature]['severity'], key=lambda x: ['NONE', 'LOW', 'MEDIUM', 'HIGH'].index(x))
            
            if has_drift:
                drift_detected = True
                icon = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🟢"
                print(f"\n{icon} {feature} - {severity} drift detected")
                
                if feature in ks_results:
                    print(f"   KS test: p-value = {ks_results[feature]['p_value']:.4f}")
                if feature in psi_results:
                    print(f"   PSI: {psi_results[feature]['psi_value']:.4f}")
        
        if not drift_detected:
            print("\n✅ No significant drift detected")
        
        print("\n" + "="*70)
        
        return {
            'drift_detected': drift_detected,
            'ks_results': ks_results,
            'psi_results': psi_results,
            'chi_results': chi_results
        }

# Example usage
if __name__ == "__main__":
    # Load reference data (training data)
    reference_df = pd.read_csv('data/raw/customers.csv').dropna()
    
    # Preprocess
    categorical_cols = reference_df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if col not in ['customer_id']:
            reference_df[col] = pd.Categorical(reference_df[col]).codes
    
    reference_df = reference_df.drop(['customer_id', 'churn'], axis=1, errors='ignore')
    
    # Create detector
    detector = DataDriftDetector(reference_df)
    
    # Simulate drifted data
    current_df = reference_df.copy()
    current_df['age'] = current_df['age'] + 5  # Age shift
    current_df['monthly_charges'] = current_df['monthly_charges'] * 1.2  # Price increase
    
    # Detect drift
    results = detector.comprehensive_drift_report(current_df)
```

### Step 3: Concept Drift Detection

Create `src/concept_drift_detector.py`:

```python
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConceptDriftDetector:
    """
    Detect concept drift (relationship between features and target changes)
    """
    
    def __init__(self, window_size=1000, warning_threshold=0.05, drift_threshold=0.1):
        self.window_size = window_size
        self.warning_threshold = warning_threshold
        self.drift_threshold = drift_threshold
        
        self.reference_accuracy = None
        self.recent_accuracies = []
    
    def set_baseline(self, accuracy: float):
        """Set baseline accuracy from training/validation"""
        self.reference_accuracy = accuracy
        logger.info(f"Baseline accuracy set: {accuracy:.4f}")
    
    def check_drift(self, y_true: np.array, y_pred: np.array) -> Dict:
        """
        Check for concept drift using ADWIN-style approach
        """
        current_accuracy = accuracy_score(y_true, y_pred)
        self.recent_accuracies.append(current_accuracy)
        
        # Keep only recent window
        if len(self.recent_accuracies) > self.window_size:
            self.recent_accuracies.pop(0)
        
        if self.reference_accuracy is None:
            self.reference_accuracy = current_accuracy
            return {'drift_detected': False, 'status': 'baseline_set'}
        
        # Calculate performance drop
        avg_recent = np.mean(self.recent_accuracies)
        performance_drop = self.reference_accuracy - avg_recent
        
        # Determine drift level
        if performance_drop >= self.drift_threshold:
            status = 'DRIFT'
            severity = 'HIGH'
            action = 'retrain_immediately'
        elif performance_drop >= self.warning_threshold:
            status = 'WARNING'
            severity = 'MEDIUM'
            action = 'increase_monitoring'
        else:
            status = 'STABLE'
            severity = 'NONE'
            action = 'none'
        
        return {
            'drift_detected': status != 'STABLE',
            'status': status,
            'severity': severity,
            'current_accuracy': current_accuracy,
            'baseline_accuracy': self.reference_accuracy,
            'recent_average': avg_recent,
            'performance_drop': performance_drop,
            'recommended_action': action
        }
    
    def generate_report(self):
        """Generate drift detection report"""
        if len(self.recent_accuracies) == 0:
            print("No data available")
            return
        
        avg_recent = np.mean(self.recent_accuracies)
        std_recent = np.std(self.recent_accuracies)
        
        print("\n" + "="*70)
        print("📊 CONCEPT DRIFT REPORT")
        print("="*70)
        print(f"\nBaseline Accuracy: {self.reference_accuracy:.4f}")
        print(f"Recent Average: {avg_recent:.4f} (±{std_recent:.4f})")
        print(f"Performance Drop: {(self.reference_accuracy - avg_recent):.4f}")
        print(f"Sample Size: {len(self.recent_accuracies)}")
        print("="*70)

# Example usage
if __name__ == "__main__":
    detector = ConceptDriftDetector(window_size=100)
    
    # Set baseline
    detector.set_baseline(accuracy=0.85)
    
    # Simulate predictions with degrading performance
    for i in range(200):
        # Gradual performance degradation
        true_accuracy = 0.85 - (i / 200) * 0.15
        
        y_true = np.random.binomial(1, 0.3, 50)
        y_pred = (np.random.random(50) < true_accuracy).astype(int)
        
        result = detector.check_drift(y_true, y_pred)
        
        if result['drift_detected']:
            logger.warning(f"Step {i}: {result['status']} - Action: {result['recommended_action']}")
    
    detector.generate_report()
```

### Step 4: Monitoring Dashboard

Create `src/monitoring_dashboard.py`:

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from performance_monitor import PerformanceMonitor
from drift_detector import DataDriftDetector

class MonitoringDashboard:
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
    
    def generate_dashboard(self, output_path='monitoring/dashboard.png'):
        """Generate monitoring dashboard"""
        
        # Load metrics
        df = self.performance_monitor.load_historical_metrics(days=30)
        
        if len(df) == 0:
            print("No data available")
            return
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Model Monitoring Dashboard', fontsize=16, fontweight='bold')
        
        # Plot 1: Accuracy over time
        axes[0, 0].plot(df['timestamp'], df['accuracy'], marker='o', linewidth=2)
        axes[0, 0].axhline(y=0.75, color='r', linestyle='--', label='Threshold')
        axes[0, 0].set_title('Accuracy Over Time')
        axes[0, 0].set_xlabel('Date')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: F1 Score over time
        axes[0, 1].plot(df['timestamp'], df['f1_score'], marker='o', color='orange', linewidth=2)
        axes[0, 1].axhline(y=0.70, color='r', linestyle='--', label='Threshold')
        axes[0, 1].set_title('F1 Score Over Time')
        axes[0, 1].set_xlabel('Date')
        axes[0, 1].set_ylabel('F1 Score')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Prediction volume
        axes[1, 0].bar(df['timestamp'], df['sample_count'], color='green', alpha=0.6)
        axes[1, 0].set_title('Daily Prediction Volume')
        axes[1, 0].set_xlabel('Date')
        axes[1, 0].set_ylabel('Count')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Positive rate
        axes[1, 1].plot(df['timestamp'], df['positive_rate'], marker='o', color='purple', linewidth=2)
        axes[1, 1].set_title('Positive Prediction Rate')
        axes[1, 1].set_xlabel('Date')
        axes[1, 1].set_ylabel('Rate')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ Dashboard saved to {output_path}")
        
        return fig

if __name__ == "__main__":
    dashboard = MonitoringDashboard()
    dashboard.generate_dashboard()
```

## Exercises

### Exercise 1: Automated Retraining
Trigger retraining when drift is detected:

```python
def auto_retrain_pipeline(drift_result):
    if drift_result['severity'] == 'HIGH':
        # Trigger retraining pipeline
        logger.info("Triggering automated retraining...")
        # Call training pipeline
```

### Exercise 2: Alerting Integration
Send alerts via Slack/email:

```python
def send_alert(alert_type, message):
    # Send to Slack
    # Send email
    pass
```

### Exercise 3: Feature Importance Drift
Monitor feature importance changes over time

## Key Takeaways

✅ Performance monitoring tracks model health  
✅ Data drift detection prevents silent failures  
✅ Concept drift indicates retraining needs  
✅ Automated alerts enable proactive response  
✅ Regular monitoring ensures production reliability

## Next Steps

- **Lab 07**: CI/CD for ML with automated testing
- **Lab 08**: Feature Store implementation
- Integrate with Prometheus/Grafana
- Add custom drift metrics

## Resources

- [Evidently AI](https://www.evidentlyai.com/)
- [Monitoring ML Models](https://christophergs.com/machine%20learning/2020/03/14/how-to-monitor-machine-learning-models/)
- [Data Drift Guide](https://towardsdatascience.com/understanding-data-drift-model-drift-and-concept-drift-6da5c>
