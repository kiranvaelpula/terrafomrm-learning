# Advanced Anomaly Detection

## Overview

Deep dive into anomaly detection techniques for IT operations, covering statistical methods, machine learning algorithms, and production implementation.

## Statistical Methods

### 1. Z-Score Method
```python
import numpy as np
from scipy import stats

def zscore_anomaly_detection(data, threshold=3):
    """Detect anomalies using Z-score"""
    z_scores = np.abs(stats.zscore(data))
    return z_scores > threshold

# Usage
cpu_data = [40, 42, 41, 43, 95, 44, 42]  # 95 is anomaly
anomalies = zscore_anomaly_detection(cpu_data)
print(f"Anomalies at indices: {np.where(anomalies)[0]}")
```

### 2. IQR (Interquartile Range)
```python
def iqr_anomaly_detection(data):
    """Detect anomalies using IQR method"""
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    return (data < lower_bound) | (data > upper_bound)
```

### 3. Moving Average with Confidence Bands
```python
def moving_average_anomaly(data, window=10, std_multiplier=3):
    """Detect anomalies using moving average"""
    rolling_mean = pd.Series(data).rolling(window=window).mean()
    rolling_std = pd.Series(data).rolling(window=window).std()
    
    upper_band = rolling_mean + (std_multiplier * rolling_std)
    lower_band = rolling_mean - (std_multiplier * rolling_std)
    
    anomalies = (data > upper_band) | (data < lower_band)
    return anomalies.fillna(False).values
```

## Machine Learning Methods

### 1. Isolation Forest
```python
from sklearn.ensemble import IsolationForest

class IsolationForestDetector:
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
    
    def fit(self, X):
        """Train on normal data"""
        self.model.fit(X)
        return self
    
    def predict(self, X):
        """Predict anomalies (-1 = anomaly, 1 = normal)"""
        predictions = self.model.predict(X)
        return predictions == -1
    
    def score(self, X):
        """Get anomaly scores (lower = more anomalous)"""
        return -self.model.score_samples(X)

# Multi-metric anomaly detection
detector = IsolationForestDetector(contamination=0.05)

# Features: CPU, Memory, Disk I/O, Network
X_train = historical_metrics[['cpu', 'memory', 'disk_io', 'network']]
detector.fit(X_train)

# Detect on new data
X_current = current_metrics[['cpu', 'memory', 'disk_io', 'network']]
anomalies = detector.predict(X_current)
scores = detector.score(X_current)

print(f"Anomalies detected: {anomalies.sum()}")
print(f"Top anomaly score: {scores.max():.3f}")
```

### 2. One-Class SVM
```python
from sklearn.svm import OneClassSVM

def oneclass_svm_detector(X_train, X_test, nu=0.1):
    """Anomaly detection with One-Class SVM"""
    model = OneClassSVM(nu=nu, kernel='rbf', gamma='auto')
    model.fit(X_train)
    
    predictions = model.predict(X_test)
    return predictions == -1  # True for anomalies
```

### 3. Autoencoder (Deep Learning)
```python
import tensorflow as tf
from tensorflow import keras

class AutoencoderDetector:
    def __init__(self, input_dim):
        # Build autoencoder
        self.model = keras.Sequential([
            keras.layers.Dense(32, activation='relu', input_shape=(input_dim,)),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(8, activation='relu'),
            # Bottleneck
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(input_dim, activation='sigmoid')
        ])
        
        self.model.compile(optimizer='adam', loss='mse')
        self.threshold = None
    
    def fit(self, X_train, epochs=50):
        """Train autoencoder on normal data"""
        self.model.fit(
            X_train, X_train,
            epochs=epochs,
            batch_size=32,
            validation_split=0.1,
            verbose=0
        )
        
        # Set threshold as 95th percentile of reconstruction error
        reconstructions = self.model.predict(X_train)
        mse = np.mean(np.square(X_train - reconstructions), axis=1)
        self.threshold = np.percentile(mse, 95)
        
        return self
    
    def predict(self, X):
        """Detect anomalies based on reconstruction error"""
        reconstructions = self.model.predict(X)
        mse = np.mean(np.square(X - reconstructions), axis=1)
        return mse > self.threshold

# Usage
detector = AutoencoderDetector(input_dim=4)
detector.fit(X_train)
anomalies = detector.predict(X_test)
```

## Time Series Anomaly Detection

### 1. LSTM Autoencoder
```python
class LSTMAnomalyDetector:
    def __init__(self, timesteps, features):
        self.timesteps = timesteps
        self.features = features
        self.model = self._build_model()
        self.threshold = None
    
    def _build_model(self):
        model = keras.Sequential([
            keras.layers.LSTM(64, activation='relu', 
                            input_shape=(self.timesteps, self.features),
                            return_sequences=True),
            keras.layers.LSTM(32, activation='relu', return_sequences=False),
            keras.layers.RepeatVector(self.timesteps),
            keras.layers.LSTM(32, activation='relu', return_sequences=True),
            keras.layers.LSTM(64, activation='relu', return_sequences=True),
            keras.layers.TimeDistributed(keras.layers.Dense(self.features))
        ])
        
        model.compile(optimizer='adam', loss='mse')
        return model
    
    def fit(self, X, epochs=50):
        """Train on normal time series data"""
        self.model.fit(X, X, epochs=epochs, batch_size=32, verbose=0)
        
        # Set threshold
        reconstructions = self.model.predict(X)
        mse = np.mean(np.square(X - reconstructions), axis=(1, 2))
        self.threshold = np.percentile(mse, 95)
        
        return self
    
    def predict(self, X):
        """Predict anomalies in time series"""
        reconstructions = self.model.predict(X)
        mse = np.mean(np.square(X - reconstructions), axis=(1, 2))
        return mse > self.threshold

# Prepare time series data
def create_sequences(data, timesteps=10):
    X = []
    for i in range(len(data) - timesteps):
        X.append(data[i:i+timesteps])
    return np.array(X)

# Usage
timesteps = 10
X_train = create_sequences(train_data, timesteps)
X_test = create_sequences(test_data, timesteps)

detector = LSTMAnomalyDetector(timesteps=timesteps, features=4)
detector.fit(X_train)
anomalies = detector.predict(X_test)
```

### 2. Prophet for Seasonal Data
```python
from prophet import Prophet

class ProphetAnomalyDetector:
    def __init__(self, interval_width=0.95):
        self.model = Prophet(
            interval_width=interval_width,
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=True
        )
    
    def fit_predict(self, df):
        """
        Fit Prophet and detect anomalies
        df must have 'ds' (datetime) and 'y' (value) columns
        """
        self.model.fit(df)
        forecast = self.model.predict(df)
        
        # Anomalies outside confidence interval
        anomalies = (
            (df['y'] < forecast['yhat_lower']) |
            (df['y'] > forecast['yhat_upper'])
        )
        
        return forecast, anomalies

# Usage for web traffic with daily patterns
df = pd.DataFrame({
    'ds': pd.date_range('2026-01-01', periods=180, freq='H'),
    'y': web_traffic_data
})

detector = ProphetAnomalyDetector(interval_width=0.95)
forecast, anomalies = detector.fit_predict(df)

print(f"Detected {anomalies.sum()} anomalies")
```

## Multi-Metric Anomaly Detection

### Correlation-Based Detection
```python
class MultiMetricAnomalyDetector:
    def __init__(self):
        self.correlation_threshold = 0.7
        self.detectors = {}
    
    def fit(self, metrics_df):
        """Train individual and correlation detectors"""
        # Train detector for each metric
        for column in metrics_df.columns:
            detector = IsolationForest(contamination=0.05)
            detector.fit(metrics_df[[column]])
            self.detectors[column] = detector
        
        # Compute correlation matrix
        self.correlation_matrix = metrics_df.corr()
    
    def detect(self, metrics_df):
        """Detect anomalies considering correlations"""
        anomalies = {}
        
        # Detect per metric
        for column in metrics_df.columns:
            predictions = self.detectors[column].predict(metrics_df[[column]])
            anomalies[column] = predictions == -1
        
        # Check correlated metrics
        correlated_anomalies = []
        for col1 in metrics_df.columns:
            if not anomalies[col1].any():
                continue
            
            # Find correlated metrics
            for col2 in metrics_df.columns:
                if col1 == col2:
                    continue
                
                if abs(self.correlation_matrix[col1][col2]) > self.correlation_threshold:
                    if anomalies[col2].any():
                        correlated_anomalies.append((col1, col2))
        
        return {
            'individual_anomalies': anomalies,
            'correlated_anomalies': correlated_anomalies
        }

# Usage
detector = MultiMetricAnomalyDetector()
detector.fit(historical_metrics)
results = detector.detect(current_metrics)

print("Correlated anomalies:")
for metric1, metric2 in results['correlated_anomalies']:
    print(f"  {metric1} ↔ {metric2}")
```

## Production Implementation

### Real-Time Anomaly Detection System
```python
from collections import deque
import threading
import time

class RealtimeAnomalyDetector:
    def __init__(self, window_size=100, retrain_interval=1000):
        self.window_size = window_size
        self.retrain_interval = retrain_interval
        
        self.data_buffer = deque(maxlen=window_size)
        self.model = IsolationForest(contamination=0.05)
        self.is_trained = False
        self.samples_processed = 0
        
        self.anomaly_callback = None
        self.lock = threading.Lock()
    
    def on_anomaly(self, callback):
        """Register callback for anomaly events"""
        self.anomaly_callback = callback
    
    def process(self, datapoint):
        """Process new datapoint"""
        with self.lock:
            self.data_buffer.append(datapoint)
            self.samples_processed += 1
            
            # Train if buffer is full and not trained
            if len(self.data_buffer) == self.window_size and not self.is_trained:
                self._train()
            
            # Retrain periodically
            if self.samples_processed % self.retrain_interval == 0:
                self._train()
            
            # Predict if trained
            if self.is_trained:
                is_anomaly = self._predict(datapoint)
                
                if is_anomaly and self.anomaly_callback:
                    self.anomaly_callback(datapoint)
                
                return is_anomaly
        
        return False
    
    def _train(self):
        """Retrain model"""
        X = np.array(list(self.data_buffer)).reshape(-1, 1)
        self.model.fit(X)
        self.is_trained = True
    
    def _predict(self, datapoint):
        """Predict if datapoint is anomaly"""
        X = np.array([[datapoint]])
        prediction = self.model.predict(X)
        return prediction[0] == -1

# Usage
detector = RealtimeAnomalyDetector(window_size=100)

def handle_anomaly(datapoint):
    print(f"🚨 Anomaly detected: {datapoint}")
    send_alert(f"CPU anomaly: {datapoint}%")
    investigate()

detector.on_anomaly(handle_anomaly)

# Stream data
for cpu_value in cpu_stream():
    detector.process(cpu_value)
    time.sleep(1)  # 1 second intervals
```

## Tuning and Optimization

### Reducing False Positives
```python
class TunedAnomalyDetector:
    def __init__(self):
        self.models = {
            'isolation_forest': IsolationForest(contamination=0.05),
            'one_class_svm': OneClassSVM(nu=0.05),
            'lof': LocalOutlierFactor(contamination=0.05, novelty=True)
        }
        self.voting_threshold = 2  # Require 2 out of 3 models to agree
    
    def fit(self, X):
        """Train all models"""
        for model in self.models.values():
            model.fit(X)
        return self
    
    def predict(self, X):
        """Ensemble prediction with voting"""
        votes = []
        
        for model in self.models.values():
            predictions = model.predict(X)
            votes.append(predictions == -1)
        
        # Count votes for each sample
        vote_counts = np.sum(votes, axis=0)
        
        # Anomaly if threshold exceeded
        return vote_counts >= self.voting_threshold

# Usage: Reduces false positives by requiring consensus
detector = TunedAnomalyDetector()
detector.fit(X_train)
anomalies = detector.predict(X_test)
```

## Next Steps

Continue to [Log Analysis & Pattern Recognition](07-log-analysis.md)

---

**Key Takeaways**:
- Use multiple methods for robust detection
- Tune contamination parameter based on your data
- Consider seasonality in time series
- Implement ensemble methods to reduce false positives
- Monitor and retrain models periodically
