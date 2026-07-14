# Lab 1: Anomaly Detection for IT Operations

## 🎯 Objectives

By the end of this lab, you will:
- Understand different types of anomalies in metrics
- Implement statistical anomaly detection methods
- Use machine learning for anomaly detection
- Handle seasonality and trends in time series
- Build a real-time anomaly detection system

## 📋 Prerequisites

- Python 3.8+
- pandas, numpy, scikit-learn
- Basic statistics knowledge

## 🛠️ Setup

```bash
# Install required packages
pip install pandas numpy scikit-learn matplotlib seaborn
pip install statsmodels prophet pyod

# Generate sample data
python generate_sample_data.py
```

## Lab Exercises

### Exercise 1: Statistical Anomaly Detection (20 mins)

**Task**: Detect anomalies using statistical methods

Create `statistical_detection.py`:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

class StatisticalAnomalyDetector:
    """Statistical anomaly detection using Z-score and IQR methods"""
    
    def __init__(self, threshold=3):
        self.threshold = threshold
        
    def detect_zscore(self, data):
        """Detect anomalies using Z-score method"""
        z_scores = np.abs(stats.zscore(data))
        return z_scores > self.threshold
    
    def detect_iqr(self, data):
        """Detect anomalies using IQR method"""
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return (data < lower_bound) | (data > upper_bound)
    
    def detect_moving_average(self, data, window=10, std_multiplier=3):
        """Detect anomalies using moving average and std deviation"""
        rolling_mean = pd.Series(data).rolling(window=window).mean()
        rolling_std = pd.Series(data).rolling(window=window).std()
        
        upper_bound = rolling_mean + (std_multiplier * rolling_std)
        lower_bound = rolling_mean - (std_multiplier * rolling_std)
        
        anomalies = (data > upper_bound) | (data < lower_bound)
        return anomalies.fillna(False).values

# Example: Detect CPU anomalies
def detect_cpu_anomalies():
    # Load sample CPU metrics
    df = pd.read_csv('../data/metrics/cpu_usage.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    detector = StatisticalAnomalyDetector(threshold=3)
    
    # Apply different methods
    df['anomaly_zscore'] = detector.detect_zscore(df['cpu_percent'])
    df['anomaly_iqr'] = detector.detect_iqr(df['cpu_percent'])
    df['anomaly_ma'] = detector.detect_moving_average(df['cpu_percent'])
    
    # Visualize results
    plt.figure(figsize=(15, 8))
    
    plt.subplot(3, 1, 1)
    plt.plot(df['timestamp'], df['cpu_percent'], label='CPU Usage', alpha=0.7)
    plt.scatter(df[df['anomaly_zscore']]['timestamp'], 
                df[df['anomaly_zscore']]['cpu_percent'], 
                color='red', label='Anomalies (Z-score)', s=100)
    plt.title('Z-Score Method')
    plt.legend()
    
    plt.subplot(3, 1, 2)
    plt.plot(df['timestamp'], df['cpu_percent'], label='CPU Usage', alpha=0.7)
    plt.scatter(df[df['anomaly_iqr']]['timestamp'], 
                df[df['anomaly_iqr']]['cpu_percent'], 
                color='orange', label='Anomalies (IQR)', s=100)
    plt.title('IQR Method')
    plt.legend()
    
    plt.subplot(3, 1, 3)
    plt.plot(df['timestamp'], df['cpu_percent'], label='CPU Usage', alpha=0.7)
    plt.scatter(df[df['anomaly_ma']]['timestamp'], 
                df[df['anomaly_ma']]['cpu_percent'], 
                color='green', label='Anomalies (Moving Avg)', s=100)
    plt.title('Moving Average Method')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('cpu_anomalies_statistical.png')
    print(f"✅ Found {df['anomaly_zscore'].sum()} anomalies using Z-score")
    print(f"✅ Found {df['anomaly_iqr'].sum()} anomalies using IQR")
    print(f"✅ Found {df['anomaly_ma'].sum()} anomalies using Moving Average")
    
    return df

if __name__ == "__main__":
    detect_cpu_anomalies()
```

**Your Task**:
1. Run the detection on CPU metrics
2. Compare the three methods - which finds more anomalies?
3. Adjust thresholds to reduce false positives
4. Try on memory and disk metrics

---

### Exercise 2: ML-Based Anomaly Detection (25 mins)

**Task**: Use machine learning algorithms for anomaly detection

Create `ml_detection.py`:

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

class MLAnomalyDetector:
    """ML-based anomaly detection"""
    
    def __init__(self, method='isolation_forest', contamination=0.1):
        self.method = method
        self.contamination = contamination
        self.scaler = StandardScaler()
        
        if method == 'isolation_forest':
            self.model = IsolationForest(
                contamination=contamination,
                random_state=42
            )
        elif method == 'one_class_svm':
            self.model = OneClassSVM(nu=contamination)
    
    def fit(self, X):
        """Train on normal data"""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        return self
    
    def predict(self, X):
        """Predict anomalies (True = anomaly)"""
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        # Convert to boolean (-1 = anomaly, 1 = normal)
        return predictions == -1
    
    def score(self, X):
        """Get anomaly scores"""
        X_scaled = self.scaler.transform(X)
        if hasattr(self.model, 'score_samples'):
            return -self.model.score_samples(X_scaled)  # Higher = more anomalous
        else:
            return -self.model.decision_function(X_scaled)

# Example: Multi-metric anomaly detection
def detect_system_anomalies():
    # Load metrics
    df = pd.read_csv('../data/metrics/system_metrics.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Select features
    features = ['cpu_percent', 'memory_percent', 'disk_io', 'network_bytes']
    X = df[features].values
    
    # Train on first 80% (assumed normal)
    split_idx = int(len(X) * 0.8)
    X_train = X[:split_idx]
    X_test = X[split_idx:]
    
    # Isolation Forest
    detector_if = MLAnomalyDetector(method='isolation_forest', contamination=0.05)
    detector_if.fit(X_train)
    anomalies_if = detector_if.predict(X_test)
    scores_if = detector_if.score(X_test)
    
    # One-Class SVM
    detector_svm = MLAnomalyDetector(method='one_class_svm', contamination=0.05)
    detector_svm.fit(X_train)
    anomalies_svm = detector_svm.predict(X_test)
    scores_svm = detector_svm.score(X_test)
    
    # Create results dataframe
    results = df[split_idx:].copy()
    results['anomaly_if'] = anomalies_if
    results['score_if'] = scores_if
    results['anomaly_svm'] = anomalies_svm
    results['score_svm'] = scores_svm
    
    # Visualize
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    for idx, feature in enumerate(features):
        row = idx // 2
        col = idx % 2
        
        axes[row, col].plot(results['timestamp'], results[feature], 
                           label=feature, alpha=0.7)
        axes[row, col].scatter(
            results[results['anomaly_if']]['timestamp'],
            results[results['anomaly_if']][feature],
            color='red', label='Isolation Forest', s=100, marker='x'
        )
        axes[row, col].scatter(
            results[results['anomaly_svm']]['timestamp'],
            results[results['anomaly_svm']][feature],
            color='orange', label='One-Class SVM', s=50, marker='o'
        )
        axes[row, col].set_title(feature)
        axes[row, col].legend()
        axes[row, col].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('system_anomalies_ml.png')
    
    print(f"✅ Isolation Forest found {anomalies_if.sum()} anomalies")
    print(f"✅ One-Class SVM found {anomalies_svm.sum()} anomalies")
    print(f"✅ Both methods agreed on {(anomalies_if & anomalies_svm).sum()} anomalies")
    
    # Show top 5 most anomalous points
    top_anomalies = results.nlargest(5, 'score_if')[['timestamp'] + features + ['score_if']]
    print("\n📊 Top 5 Most Anomalous Points:")
    print(top_anomalies)
    
    return results

if __name__ == "__main__":
    detect_system_anomalies()
```

**Your Task**:
1. Run ML detection on system metrics
2. Compare Isolation Forest vs One-Class SVM
3. Adjust contamination parameter
4. Add LSTM-based detection for time series

---

### Exercise 3: Handling Seasonality (20 mins)

**Task**: Detect anomalies in data with daily/weekly patterns

Create `seasonal_detection.py`:

```python
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt

class SeasonalAnomalyDetector:
    """Anomaly detection for seasonal time series using Prophet"""
    
    def __init__(self, interval_width=0.99):
        self.model = Prophet(
            interval_width=interval_width,
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=True
        )
    
    def fit_predict(self, df):
        """
        Fit Prophet model and detect anomalies
        df must have 'ds' (datetime) and 'y' (value) columns
        """
        # Fit model
        self.model.fit(df)
        
        # Make predictions
        forecast = self.model.predict(df)
        
        # Detect anomalies (outside confidence interval)
        anomalies = (
            (df['y'] < forecast['yhat_lower']) | 
            (df['y'] > forecast['yhat_upper'])
        )
        
        return forecast, anomalies

# Example: Detect web traffic anomalies with daily/weekly patterns
def detect_traffic_anomalies():
    # Load web traffic data (with daily patterns)
    df = pd.read_csv('../data/metrics/web_traffic.csv')
    df['ds'] = pd.to_datetime(df['timestamp'])
    df['y'] = df['requests_per_minute']
    
    # Initialize detector
    detector = SeasonalAnomalyDetector(interval_width=0.95)
    
    # Fit and detect
    forecast, anomalies = detector.fit_predict(df[['ds', 'y']])
    
    # Visualize
    fig, axes = plt.subplots(2, 1, figsize=(15, 10))
    
    # Plot 1: Full time series with forecast
    axes[0].plot(df['ds'], df['y'], label='Actual', alpha=0.7)
    axes[0].plot(forecast['ds'], forecast['yhat'], 
                label='Predicted', color='orange', linewidth=2)
    axes[0].fill_between(forecast['ds'], 
                         forecast['yhat_lower'], 
                         forecast['yhat_upper'],
                         alpha=0.3, color='orange', label='Confidence Interval')
    axes[0].scatter(df[anomalies]['ds'], df[anomalies]['y'], 
                   color='red', s=100, label='Anomalies', zorder=5)
    axes[0].set_title('Web Traffic with Seasonality')
    axes[0].legend()
    
    # Plot 2: Components (trend, weekly, daily)
    from prophet.plot import plot_components
    fig2 = detector.model.plot_components(forecast)
    
    plt.tight_layout()
    plt.savefig('traffic_anomalies_seasonal.png')
    
    print(f"✅ Detected {anomalies.sum()} anomalies in seasonal data")
    print(f"\n📊 Anomaly timestamps:")
    print(df[anomalies][['ds', 'y']])
    
    # Analyze anomaly patterns
    df['hour'] = df['ds'].dt.hour
    df['day_of_week'] = df['ds'].dt.day_name()
    df['anomaly'] = anomalies
    
    anomaly_summary = df[df['anomaly']].groupby(['day_of_week', 'hour']).size()
    print(f"\n📈 Anomaly patterns:")
    print(anomaly_summary)
    
    return df, forecast, anomalies

if __name__ == "__main__":
    detect_traffic_anomalies()
```

**Your Task**:
1. Run seasonal detection on web traffic
2. Identify which days/hours have most anomalies
3. Adjust confidence interval (interval_width)
4. Try on database query metrics

---

### Exercise 4: Real-Time Anomaly Detection (20 mins)

**Task**: Build a streaming anomaly detector

Create `realtime_detection.py`:

```python
import pandas as pd
import numpy as np
from collections import deque
from sklearn.ensemble import IsolationForest

class RealtimeAnomalyDetector:
    """Real-time anomaly detection with sliding window"""
    
    def __init__(self, window_size=100, contamination=0.1, retrain_interval=50):
        self.window_size = window_size
        self.contamination = contamination
        self.retrain_interval = retrain_interval
        
        self.data_window = deque(maxlen=window_size)
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.samples_since_retrain = 0
        self.is_trained = False
    
    def update(self, value):
        """Process new data point and return anomaly status"""
        # Add to window
        self.data_window.append(value)
        
        # Train if we have enough data
        if len(self.data_window) >= self.window_size and not self.is_trained:
            self._train()
        
        # Retrain periodically
        if self.samples_since_retrain >= self.retrain_interval:
            self._train()
        
        # Predict
        if self.is_trained:
            prediction = self.model.predict([[value]])
            self.samples_since_retrain += 1
            return prediction[0] == -1  # True if anomaly
        
        return False
    
    def _train(self):
        """Retrain model on current window"""
        X = np.array(self.data_window).reshape(-1, 1)
        self.model.fit(X)
        self.is_trained = True
        self.samples_since_retrain = 0

# Simulate real-time monitoring
def simulate_realtime_monitoring():
    # Load data
    df = pd.read_csv('../data/metrics/cpu_usage.csv')
    
    detector = RealtimeAnomalyDetector(window_size=100, contamination=0.05)
    
    results = []
    anomaly_count = 0
    
    print("🔴 Starting real-time anomaly detection...")
    print("=" * 60)
    
    for idx, row in df.iterrows():
        value = row['cpu_percent']
        timestamp = row['timestamp']
        
        is_anomaly = detector.update(value)
        
        results.append({
            'timestamp': timestamp,
            'value': value,
            'anomaly': is_anomaly
        })
        
        if is_anomaly:
            anomaly_count += 1
            print(f"⚠️ ANOMALY at {timestamp}: CPU = {value:.2f}%")
        
        # Simulate delay (in production, this would be real-time)
        if idx % 100 == 0:
            print(f"📊 Processed {idx} samples, detected {anomaly_count} anomalies")
    
    print("=" * 60)
    print(f"✅ Monitoring complete: {anomaly_count} anomalies detected")
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv('realtime_results.csv', index=False)
    
    return results_df

if __name__ == "__main__":
    simulate_realtime_monitoring()
```

**Your Task**:
1. Run real-time detector simulation
2. Adjust window size and contamination
3. Add alerting for detected anomalies
4. Implement confidence scores

---

## 🧪 Verification

Run the verification script:

```bash
python verify.py
```

**Expected Results**:
```
✅ Statistical detection working
✅ ML detection working
✅ Seasonal detection working
✅ Real-time detection working
✅ Anomalies detected correctly
✅ Visualizations generated
```

## 📊 Success Criteria

- [ ] Implemented statistical anomaly detection
- [ ] Used ML algorithms for detection
- [ ] Handled seasonal patterns
- [ ] Built real-time detector
- [ ] Generated visualizations
- [ ] Compared different methods

## 🎓 Key Takeaways

1. **No Single Best Method**: Combine statistical and ML approaches
2. **Context Matters**: Understand your metrics' patterns
3. **Tune for Environment**: Adjust thresholds to reduce false positives
4. **Handle Seasonality**: Use appropriate methods for periodic data
5. **Monitor Performance**: Track detection accuracy and latency

## 🏆 Challenge

**Advanced Exercise**: Build a multi-metric anomaly detector that:
1. Monitors 10+ system metrics simultaneously
2. Detects correlated anomalies across metrics
3. Provides root cause hints
4. Sends alerts to Slack/PagerDuty

See `challenges/multi-metric-detector.md`

## 📚 Resources

- [PyOD Documentation](https://pyod.readthedocs.io/)
- [Prophet Guide](https://facebook.github.io/prophet/)
- [Isolation Forest Paper](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)

---

**Next Lab**: [Lab 2: Log Analysis & Pattern Recognition](../lab-02-log-analysis/)
