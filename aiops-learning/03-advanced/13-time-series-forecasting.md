# Time Series Forecasting for IT Operations

## Overview

Time series forecasting predicts future system behavior based on historical patterns, enabling proactive capacity planning and issue prevention.

## Forecasting Methods

### 1. ARIMA (AutoRegressive Integrated Moving Average)

```python
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

class ARIMAForecaster:
    def __init__(self, order=(1, 1, 1)):
        self.order = order
        self.model = None
    
    def fit(self, data):
        """Fit ARIMA model"""
        self.model = ARIMA(data, order=self.order)
        self.fitted_model = self.model.fit()
        return self
    
    def forecast(self, steps=24):
        """Forecast future values"""
        forecast = self.fitted_model.forecast(steps=steps)
        confidence_int = self.fitted_model.get_forecast(steps=steps).conf_int()
        
        return {
            'forecast': forecast,
            'lower_bound': confidence_int.iloc[:, 0],
            'upper_bound': confidence_int.iloc[:, 1]
        }

# Usage: CPU utilization forecast
cpu_history = pd.Series(historical_cpu_data, index=pd.date_range('2026-06-13', periods=len(historical_cpu_data), freq='H'))

forecaster = ARIMAForecaster(order=(2, 1, 2))
forecaster.fit(cpu_history)

# Forecast next 24 hours
forecast = forecaster.forecast(steps=24)

print(f"24-hour forecast:")
print(forecast['forecast'])

# Alert if predicted to exceed threshold
if forecast['upper_bound'].max() > 90:
    alert("CPU expected to exceed 90% in next 24 hours")
```

### 2. Prophet (Facebook's Forecasting Tool)

```python
from prophet import Prophet

class ProphetForecaster:
    def __init__(self):
        self.model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=True,
            changepoint_prior_scale=0.05
        )
    
    def fit(self, df):
        """
        Fit Prophet model
        df must have 'ds' (timestamp) and 'y' (value) columns
        """
        self.model.fit(df)
        return self
    
    def forecast(self, periods, freq='H'):
        """Forecast future periods"""
        future = self.model.make_future_dataframe(periods=periods, freq=freq)
        forecast = self.model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    
    def detect_capacity_issues(self, forecast, threshold):
        """Check if forecast exceeds capacity"""
        issues = forecast[forecast['yhat'] > threshold]
        
        if not issues.empty:
            first_issue = issues.iloc[0]
            return {
                'will_exceed': True,
                'first_exceeds_at': first_issue['ds'],
                'predicted_value': first_issue['yhat']
            }
        
        return {'will_exceed': False}

# Usage: Database connection forecast
df = pd.DataFrame({
    'ds': pd.date_range('2026-01-01', periods=180, freq='D'),
    'y': db_connection_usage
})

forecaster = ProphetForecaster()
forecaster.fit(df)

# Forecast next 30 days
forecast = forecaster.forecast(periods=30, freq='D')

# Check capacity
max_connections = 1000
result = forecaster.detect_capacity_issues(forecast, threshold=max_connections * 0.9)

if result['will_exceed']:
    print(f"⚠️ Connections will exceed 90% capacity on {result['first_exceeds_at']}")
    print(f"   Predicted: {result['predicted_value']:.0f} connections")
    
    # Auto-scale
    schedule_capacity_increase(result['first_exceeds_at'])
```

### 3. LSTM (Long Short-Term Memory Networks)

```python
import tensorflow as tf
from tensorflow import keras
import numpy as np

class LSTMForecaster:
    def __init__(self, lookback=24, forecast_horizon=24):
        self.lookback = lookback
        self.forecast_horizon = forecast_horizon
        self.model = self._build_model()
        self.scaler = None
    
    def _build_model(self):
        """Build LSTM model"""
        model = keras.Sequential([
            keras.layers.LSTM(64, activation='relu', 
                            input_shape=(self.lookback, 1),
                            return_sequences=True),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(32, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(self.forecast_horizon)
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
    
    def prepare_data(self, data):
        """Prepare sequences for LSTM"""
        # Normalize
        from sklearn.preprocessing import MinMaxScaler
        self.scaler = MinMaxScaler()
        data_scaled = self.scaler.fit_transform(data.reshape(-1, 1))
        
        X, y = [], []
        for i in range(len(data_scaled) - self.lookback - self.forecast_horizon):
            X.append(data_scaled[i:i+self.lookback])
            y.append(data_scaled[i+self.lookback:i+self.lookback+self.forecast_horizon])
        
        return np.array(X), np.array(y)
    
    def fit(self, data, epochs=50, batch_size=32):
        """Train LSTM model"""
        X, y = self.prepare_data(data)
        
        self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=0
        )
        
        return self
    
    def forecast(self, last_sequence):
        """Forecast next values"""
        # Prepare input
        last_scaled = self.scaler.transform(last_sequence.reshape(-1, 1))
        X_input = last_scaled[-self.lookback:].reshape(1, self.lookback, 1)
        
        # Predict
        prediction_scaled = self.model.predict(X_input, verbose=0)
        
        # Inverse transform
        prediction = self.scaler.inverse_transform(
            prediction_scaled.reshape(-1, 1)
        ).flatten()
        
        return prediction

# Usage: Memory usage forecast
memory_history = np.array(memory_usage_data)

forecaster = LSTMForecaster(lookback=24, forecast_horizon=24)
forecaster.fit(memory_history, epochs=100)

# Forecast next 24 hours
last_24_hours = memory_history[-24:]
forecast = forecaster.forecast(last_24_hours)

print("24-hour memory forecast:")
print(forecast)

# Alert if memory expected to exceed 90%
if forecast.max() > 90:
    hours_until_critical = np.argmax(forecast > 90) + 1
    print(f"⚠️ Memory will exceed 90% in {hours_until_critical} hours")
```

## Capacity Planning

### Automated Capacity Planning System

```python
class CapacityPlanner:
    def __init__(self):
        self.forecasters = {
            'cpu': ProphetForecaster(),
            'memory': ProphetForecaster(),
            'disk': ProphetForecaster(),
            'network': ProphetForecaster()
        }
        
        self.thresholds = {
            'cpu': 80,
            'memory': 85,
            'disk': 90,
            'network': 75
        }
    
    def train(self, historical_data):
        """Train forecasters on historical data"""
        for metric, forecaster in self.forecasters.items():
            df = pd.DataFrame({
                'ds': historical_data['timestamp'],
                'y': historical_data[metric]
            })
            forecaster.fit(df)
        
        return self
    
    def plan_capacity(self, days_ahead=30):
        """Generate capacity plan"""
        plan = {}
        
        for metric, forecaster in self.forecasters.items():
            # Forecast
            forecast = forecaster.forecast(periods=days_ahead, freq='D')
            
            # Check threshold
            threshold = self.thresholds[metric]
            issues = forecast[forecast['yhat'] > threshold]
            
            if not issues.empty:
                first_issue = issues.iloc[0]
                days_until_issue = (first_issue['ds'] - pd.Timestamp.now()).days
                
                plan[metric] = {
                    'action_needed': True,
                    'days_until_threshold': days_until_issue,
                    'predicted_value': first_issue['yhat'],
                    'threshold': threshold,
                    'recommendation': self._generate_recommendation(
                        metric,
                        first_issue['yhat'],
                        threshold
                    )
                }
            else:
                plan[metric] = {
                    'action_needed': False,
                    'status': 'OK for next 30 days'
                }
        
        return plan
    
    def _generate_recommendation(self, metric, predicted, threshold):
        """Generate action recommendation"""
        overage = predicted - threshold
        
        recommendations = {
            'cpu': f"Scale horizontally by {int(overage/10)} instances",
            'memory': f"Upgrade instance type or add {int(overage)}GB memory",
            'disk': f"Provision additional {int(overage)}GB storage",
            'network': f"Upgrade network bandwidth by {int(overage)}%"
        }
        
        return recommendations[metric]

# Usage
planner = CapacityPlanner()

# Train on 90 days of historical data
historical = pd.read_csv('metrics_history.csv')
planner.train(historical)

# Generate 30-day capacity plan
plan = planner.plan_capacity(days_ahead=30)

print("Capacity Plan:")
for metric, details in plan.items():
    if details['action_needed']:
        print(f"\n⚠️ {metric.upper()}:")
        print(f"   Action needed in {details['days_until_threshold']} days")
        print(f"   Will reach {details['predicted_value']:.1f}% "
              f"(threshold: {details['threshold']}%)")
        print(f"   Recommendation: {details['recommendation']}")
    else:
        print(f"\n✅ {metric.upper()}: {details['status']}")
```

## Workload Forecasting

### Predict Peak Traffic

```python
class WorkloadForecaster:
    def __init__(self):
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True
        )
        
        # Add holidays/special events
        self.model.add_country_holidays(country_name='US')
    
    def fit(self, df):
        """Train on historical traffic data"""
        self.model.fit(df)
        return self
    
    def forecast_peak_events(self, days_ahead=90):
        """Forecast and identify peak traffic events"""
        # Generate forecast
        future = self.model.make_future_dataframe(periods=days_ahead, freq='D')
        forecast = self.model.predict(future)
        
        # Identify peaks (> 95th percentile)
        threshold = forecast['yhat'].quantile(0.95)
        peaks = forecast[forecast['yhat'] > threshold].copy()
        
        # Enrich with details
        peaks['peak_severity'] = (peaks['yhat'] / threshold - 1) * 100
        peaks['recommended_capacity'] = peaks['yhat'] * 1.2  # 20% buffer
        
        return peaks[['ds', 'yhat', 'peak_severity', 'recommended_capacity']]
    
    def prepare_for_peak(self, peak_date, current_capacity):
        """Generate preparation plan for peak event"""
        # Forecast for peak date
        future = pd.DataFrame({'ds': [peak_date]})
        forecast = self.model.predict(future)
        
        predicted_load = forecast['yhat'].iloc[0]
        required_capacity = predicted_load * 1.2  # 20% buffer
        
        scale_factor = required_capacity / current_capacity
        
        return {
            'peak_date': peak_date,
            'predicted_load': predicted_load,
            'required_capacity': required_capacity,
            'current_capacity': current_capacity,
            'scale_factor': scale_factor,
            'scale_up_date': peak_date - pd.Timedelta(days=2),  # Scale 2 days before
            'scale_down_date': peak_date + pd.Timedelta(days=1)  # Scale down 1 day after
        }

# Usage: E-commerce Black Friday preparation
df = pd.DataFrame({
    'ds': pd.date_range('2025-01-01', '2026-07-13', freq='D'),
    'y': daily_traffic  # Requests per second
})

forecaster = WorkloadForecaster()
forecaster.fit(df)

# Forecast next 90 days and find peaks
peaks = forecaster.forecast_peak_events(days_ahead=90)

print("Predicted Peak Traffic Events:")
print(peaks)

# Prepare for Black Friday 2026
black_friday = pd.Timestamp('2026-11-27')
current_capacity = 10000  # req/sec

plan = forecaster.prepare_for_peak(black_friday, current_capacity)

print(f"\nBlack Friday Preparation Plan:")
print(f"  Predicted load: {plan['predicted_load']:.0f} req/sec")
print(f"  Required capacity: {plan['required_capacity']:.0f} req/sec")
print(f"  Scale factor: {plan['scale_factor']:.1f}x")
print(f"  Scale up on: {plan['scale_up_date'].date()}")
print(f"  Scale down on: {plan['scale_down_date'].date()}")

# Auto-schedule scaling
schedule_scaling_event(
    date=plan['scale_up_date'],
    action='scale_up',
    target_capacity=plan['required_capacity']
)
```

## Failure Prediction

### Predict System Failures

```python
from sklearn.ensemble import GradientBoostingClassifier

class FailurePredictor:
    def __init__(self):
        self.model = GradientBoostingClassifier(n_estimators=100)
        self.feature_names = None
    
    def train(self, historical_incidents):
        """
        Train on historical incidents
        historical_incidents: DataFrame with features and 'failed' column
        """
        X = historical_incidents.drop('failed', axis=1)
        y = historical_incidents['failed']
        
        self.feature_names = X.columns.tolist()
        self.model.fit(X, y)
        
        return self
    
    def predict_failure(self, current_metrics):
        """Predict probability of failure"""
        X = current_metrics[self.feature_names]
        
        failure_prob = self.model.predict_proba([X])[0][1]
        will_fail = failure_prob > 0.7
        
        return {
            'will_fail': will_fail,
            'failure_probability': failure_prob,
            'risk_level': self._get_risk_level(failure_prob)
        }
    
    def _get_risk_level(self, probability):
        """Categorize risk level"""
        if probability > 0.9:
            return 'CRITICAL'
        elif probability > 0.7:
            return 'HIGH'
        elif probability > 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def get_failure_indicators(self):
        """Get most important failure indicators"""
        importances = self.model.feature_importances_
        
        indicators = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        return indicators

# Usage
# Train on historical data
historical = pd.read_csv('historical_metrics_with_failures.csv')

predictor = FailurePredictor()
predictor.train(historical)

# Current system state
current_state = {
    'cpu_trend': 0.15,  # 15% increase per hour
    'memory_trend': 0.20,  # 20% increase per hour
    'error_rate': 0.05,
    'latency_p95': 500,
    'disk_io_wait': 15,
    'connection_pool_utilization': 0.85
}

# Predict failure
prediction = predictor.predict_failure(pd.Series(current_state))

if prediction['will_fail']:
    print(f"⚠️ FAILURE PREDICTION")
    print(f"   Probability: {prediction['failure_probability']:.1%}")
    print(f"   Risk Level: {prediction['risk_level']}")
    
    # Take preventive action
    if prediction['risk_level'] == 'CRITICAL':
        emergency_scale_up()
    elif prediction['risk_level'] == 'HIGH':
        schedule_maintenance()
    
    notify_team(f"System failure predicted with {prediction['failure_probability']:.0%} confidence")

# Show key indicators
print("\nTop Failure Indicators:")
print(predictor.get_failure_indicators().head(5))
```

## Best Practices

1. **Multiple Models**: Use ensemble of forecasting methods
2. **Seasonality**: Account for daily, weekly, yearly patterns
3. **Retraining**: Retrain models regularly with new data
4. **Confidence Intervals**: Always include uncertainty bounds
5. **Validation**: Backtest forecasts on historical data
6. **Lead Time**: Forecast far enough ahead for action
7. **Automation**: Auto-scale based on forecasts

## Next Steps

Continue to [NLP for IT Operations](14-nlp-it-operations.md)

---

**Key Takeaway**: Accurate forecasting enables proactive operations, preventing issues before they impact users.
