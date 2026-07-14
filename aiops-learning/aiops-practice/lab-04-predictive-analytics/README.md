# Lab 04: Predictive Analytics for Capacity Planning

## Overview
Build predictive models to forecast resource utilization, detect capacity constraints before they occur, and optimize infrastructure scaling decisions.

**Duration:** 3-4 hours  
**Difficulty:** Advanced  
**Prerequisites:** Labs 01-03, Time series analysis, ML fundamentals

## Learning Objectives
- Forecast CPU, memory, and disk usage
- Detect capacity saturation trends
- Predict scaling requirements
- Optimize cost vs performance
- Build automated scaling recommendations

## Lab Architecture

```
Metrics Collection → Time Series DB → Forecasting Models → Capacity Planner → Scaling Actions
         ↓               ↓                  ↓                    ↓
    Prometheus      InfluxDB/          ARIMA/LSTM         Recommendation
                    TimescaleDB        Prophet            Engine
```

## Setup

### 1. Install Dependencies

```bash
pip install pandas numpy scikit-learn \
    prophet statsmodels tensorflow \
    matplotlib seaborn plotly \
    influxdb-client prometheus-client
```

### 2. Generate Sample Data

Create `scripts/generate_metrics.py`:

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_resource_metrics(days=30, interval_minutes=5):
    """Generate synthetic resource utilization data"""
    
    timestamps = pd.date_range(
        end=datetime.now(),
        periods=days * 24 * (60 // interval_minutes),
        freq=f'{interval_minutes}min'
    )
    
    data = []
    base_cpu = 45
    base_memory = 60
    base_disk = 70
    
    for i, ts in enumerate(timestamps):
        hour = ts.hour
        day_of_week = ts.dayofweek
        
        # Daily patterns
        daily_pattern = 20 * np.sin(2 * np.pi * hour / 24)
        
        # Weekly patterns (higher on weekdays)
        weekly_pattern = -10 if day_of_week >= 5 else 0
        
        # Trend (gradual increase)
        trend = 0.1 * (i / len(timestamps)) * 100
        
        # Noise
        noise = np.random.normal(0, 5)
        
        # Calculate metrics
        cpu = max(0, min(100, base_cpu + daily_pattern + weekly_pattern + trend + noise))
        memory = max(0, min(100, base_memory + daily_pattern * 0.8 + trend + noise))
        disk = max(0, min(100, base_disk + trend * 1.5 + noise * 0.5))
        
        # Network throughput (GB)
        network = max(0, 10 + daily_pattern / 2 + np.random.normal(0, 2))
        
        # Request rate
        requests = max(0, int(1000 + daily_pattern * 50 + np.random.normal(0, 100)))
        
        data.append({
            'timestamp': ts,
            'cpu_percent': round(cpu, 2),
            'memory_percent': round(memory, 2),
            'disk_percent': round(disk, 2),
            'network_gb': round(network, 2),
            'requests_per_minute': requests
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_resource_metrics(days=90)
    df.to_csv('../data/resource_metrics.csv', index=False)
    print(f"✅ Generated {len(df)} metric records")
    print(df.head())
```

Run the script:
```bash
python scripts/generate_metrics.py
```

## Implementation

### Step 1: Time Series Forecasting with Prophet

Create `src/capacity_forecaster.py`:

```python
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from typing import Dict, List

class CapacityForecaster:
    def __init__(self):
        self.models = {}
        self.forecasts = {}
        
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Load metrics data"""
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    def prepare_prophet_data(self, df: pd.DataFrame, metric: str) -> pd.DataFrame:
        """Prepare data for Prophet format"""
        prophet_df = df[['timestamp', metric]].copy()
        prophet_df.columns = ['ds', 'y']
        return prophet_df
    
    def train_forecast_model(self, df: pd.DataFrame, metric: str, 
                            forecast_days: int = 30):
        """Train Prophet model and generate forecast"""
        print(f"📊 Training model for {metric}...")
        
        # Prepare data
        prophet_df = self.prepare_prophet_data(df, metric)
        
        # Initialize and train model
        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=True,
            changepoint_prior_scale=0.05
        )
        
        model.fit(prophet_df)
        
        # Generate forecast
        future = model.make_future_dataframe(periods=forecast_days, freq='5min')
        forecast = model.predict(future)
        
        # Store model and forecast
        self.models[metric] = model
        self.forecasts[metric] = forecast
        
        return forecast
    
    def detect_capacity_constraints(self, forecast: pd.DataFrame, 
                                    threshold: float = 80) -> Dict:
        """Detect when capacity will exceed threshold"""
        # Filter future predictions
        future_forecast = forecast[forecast['ds'] > pd.Timestamp.now()]
        
        # Find when threshold is exceeded
        constraint_points = future_forecast[future_forecast['yhat'] > threshold]
        
        if len(constraint_points) > 0:
            first_constraint = constraint_points.iloc[0]
            days_until = (first_constraint['ds'] - pd.Timestamp.now()).days
            
            return {
                'will_exceed': True,
                'threshold': threshold,
                'first_exceed_date': first_constraint['ds'],
                'days_until_exceed': days_until,
                'predicted_value': first_constraint['yhat'],
                'confidence_interval': (first_constraint['yhat_lower'], 
                                       first_constraint['yhat_upper'])
            }
        else:
            return {
                'will_exceed': False,
                'threshold': threshold
            }
    
    def calculate_growth_rate(self, df: pd.DataFrame, metric: str, 
                             window_days: int = 7) -> float:
        """Calculate metric growth rate"""
        recent = df.tail(window_days * 24 * 12)  # Last N days (5min intervals)
        
        if len(recent) < 2:
            return 0.0
        
        first_val = recent[metric].iloc[:100].mean()
        last_val = recent[metric].iloc[-100:].mean()
        
        growth_rate = ((last_val - first_val) / first_val) * 100
        return round(growth_rate, 2)
    
    def plot_forecast(self, metric: str, save_path: str = None):
        """Visualize forecast"""
        model = self.models[metric]
        forecast = self.forecasts[metric]
        
        fig = model.plot(forecast)
        plt.title(f'{metric.replace("_", " ").title()} Forecast')
        plt.xlabel('Date')
        plt.ylabel('Utilization (%)')
        
        # Add threshold line
        plt.axhline(y=80, color='r', linestyle='--', label='Capacity Threshold')
        plt.legend()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig
    
    def generate_capacity_report(self, df: pd.DataFrame, 
                                metrics: List[str], forecast_days: int = 30):
        """Generate comprehensive capacity report"""
        print("\n" + "="*70)
        print("📊 CAPACITY PLANNING REPORT")
        print("="*70)
        
        for metric in metrics:
            print(f"\n🔍 {metric.replace('_', ' ').title()}")
            print("-" * 70)
            
            # Train model
            forecast = self.train_forecast_model(df, metric, forecast_days)
            
            # Current status
            current_value = df[metric].iloc[-1]
            print(f"   Current: {current_value:.2f}%")
            
            # Growth rate
            growth = self.calculate_growth_rate(df, metric)
            print(f"   7-day Growth Rate: {growth:+.2f}%")
            
            # Forecast
            future_avg = forecast.tail(24*12)['yhat'].mean()  # Next day average
            print(f"   Predicted (24h): {future_avg:.2f}%")
            
            # Capacity constraints
            constraints = self.detect_capacity_constraints(forecast)
            
            if constraints['will_exceed']:
                print(f"   ⚠️  WARNING: Will exceed {constraints['threshold']}% threshold")
                print(f"   📅 Date: {constraints['first_exceed_date'].date()}")
                print(f"   ⏰ Days Until: {constraints['days_until_exceed']}")
                print(f"   📈 Predicted Value: {constraints['predicted_value']:.2f}%")
            else:
                print(f"   ✅ OK: Below {constraints['threshold']}% threshold")
            
            # Save plot
            self.plot_forecast(metric, f'../data/forecast_{metric}.png')
        
        print("\n" + "="*70)

# Run forecasting
if __name__ == "__main__":
    forecaster = CapacityForecaster()
    
    # Load data
    df = forecaster.load_data('../data/resource_metrics.csv')
    
    # Generate report
    metrics = ['cpu_percent', 'memory_percent', 'disk_percent']
    forecaster.generate_capacity_report(df, metrics, forecast_days=30)
    
    print("\n✅ Forecast visualizations saved")
```

### Step 2: LSTM-based Forecasting

Create `src/lstm_forecaster.py`:

```python
import numpy as np
import pandas as pd
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

class LSTMForecaster:
    def __init__(self, sequence_length=24*12):  # 24 hours of 5min data
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = MinMaxScaler()
        
    def prepare_sequences(self, data: np.array):
        """Prepare sequences for LSTM"""
        X, y = [], []
        
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:i + self.sequence_length])
            y.append(data[i + self.sequence_length])
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        """Build LSTM model"""
        model = keras.Sequential([
            layers.LSTM(64, activation='relu', return_sequences=True, 
                       input_shape=input_shape),
            layers.Dropout(0.2),
            layers.LSTM(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
    
    def train(self, df: pd.DataFrame, metric: str, epochs=50):
        """Train LSTM model"""
        print(f"🧠 Training LSTM for {metric}...")
        
        # Prepare data
        data = df[metric].values.reshape(-1, 1)
        scaled_data = self.scaler.fit_transform(data)
        
        X, y = self.prepare_sequences(scaled_data)
        
        # Split train/test
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        # Build and train model
        self.model = self.build_model((X_train.shape[1], 1))
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=32,
            verbose=0
        )
        
        # Evaluate
        test_loss = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"   Test MAE: {test_loss[1]:.4f}")
        
        return history
    
    def forecast(self, df: pd.DataFrame, metric: str, steps=24*12):
        """Generate forecast"""
        # Prepare last sequence
        data = df[metric].values.reshape(-1, 1)
        scaled_data = self.scaler.transform(data)
        
        last_sequence = scaled_data[-self.sequence_length:]
        predictions = []
        
        # Iterative prediction
        current_sequence = last_sequence.copy()
        
        for _ in range(steps):
            # Predict next value
            pred = self.model.predict(current_sequence.reshape(1, -1, 1), verbose=0)
            predictions.append(pred[0, 0])
            
            # Update sequence
            current_sequence = np.append(current_sequence[1:], pred)
        
        # Inverse transform
        predictions = self.scaler.inverse_transform(
            np.array(predictions).reshape(-1, 1)
        )
        
        return predictions.flatten()

# Example usage
if __name__ == "__main__":
    forecaster = LSTMForecaster()
    
    # Load data
    df = pd.read_csv('../data/resource_metrics.csv')
    
    # Train model
    history = forecaster.train(df, 'cpu_percent', epochs=30)
    
    # Generate forecast
    predictions = forecaster.forecast(df, 'cpu_percent', steps=24*12)
    
    print(f"\n📈 Forecast for next 24 hours:")
    print(f"   Min: {predictions.min():.2f}%")
    print(f"   Max: {predictions.max():.2f}%")
    print(f"   Mean: {predictions.mean():.2f}%")
```

### Step 3: Scaling Recommendation Engine

Create `src/scaling_recommender.py`:

```python
import pandas as pd
from typing import Dict, List
from capacity_forecaster import CapacityForecaster

class ScalingRecommender:
    def __init__(self, cost_per_unit: float = 0.10):
        self.forecaster = CapacityForecaster()
        self.cost_per_unit = cost_per_unit  # $ per hour per unit
        
    def analyze_scaling_need(self, df: pd.DataFrame, metric: str,
                            current_capacity: int) -> Dict:
        """Determine if scaling is needed"""
        # Train forecast model
        forecast = self.forecaster.train_forecast_model(df, metric, forecast_days=7)
        
        # Check capacity constraints
        constraints = self.forecaster.detect_capacity_constraints(forecast, threshold=80)
        
        if constraints['will_exceed']:
            # Calculate required additional capacity
            predicted_max = forecast.tail(24*12*7)['yhat'].max()
            current_usage_percent = predicted_max
            required_capacity = int(np.ceil(
                (current_usage_percent / 80) * current_capacity
            ))
            additional_units = required_capacity - current_capacity
            
            return {
                'action': 'scale_up',
                'current_capacity': current_capacity,
                'recommended_capacity': required_capacity,
                'additional_units': additional_units,
                'predicted_max_usage': predicted_max,
                'days_until_needed': constraints['days_until_exceed'],
                'estimated_cost_increase': additional_units * self.cost_per_unit * 24 * 30
            }
        else:
            # Check if we can scale down
            predicted_max = forecast.tail(24*12*7)['yhat'].max()
            
            if predicted_max < 60:  # Under-utilized
                safe_capacity = int(np.ceil((predicted_max / 60) * current_capacity))
                units_to_remove = current_capacity - safe_capacity
                
                if units_to_remove > 0:
                    return {
                        'action': 'scale_down',
                        'current_capacity': current_capacity,
                        'recommended_capacity': safe_capacity,
                        'units_to_remove': units_to_remove,
                        'predicted_max_usage': predicted_max,
                        'estimated_cost_savings': units_to_remove * self.cost_per_unit * 24 * 30
                    }
            
            return {
                'action': 'no_change',
                'current_capacity': current_capacity,
                'predicted_max_usage': predicted_max
            }
    
    def generate_scaling_plan(self, df: pd.DataFrame, 
                             resources: Dict[str, int]) -> Dict:
        """Generate comprehensive scaling plan"""
        plan = {}
        total_cost_impact = 0
        
        for resource, current_capacity in resources.items():
            metric = f"{resource}_percent"
            
            if metric in df.columns:
                recommendation = self.analyze_scaling_need(df, metric, current_capacity)
                plan[resource] = recommendation
                
                if 'estimated_cost_increase' in recommendation:
                    total_cost_impact += recommendation['estimated_cost_increase']
                elif 'estimated_cost_savings' in recommendation:
                    total_cost_impact -= recommendation['estimated_cost_savings']
        
        plan['total_monthly_cost_impact'] = total_cost_impact
        
        return plan
    
    def print_scaling_plan(self, plan: Dict):
        """Print scaling recommendations"""
        print("\n" + "="*70)
        print("📋 SCALING RECOMMENDATIONS")
        print("="*70)
        
        for resource, rec in plan.items():
            if resource == 'total_monthly_cost_impact':
                continue
                
            print(f"\n🔧 {resource.upper()}")
            print("-" * 70)
            
            action = rec['action']
            
            if action == 'scale_up':
                print(f"   ⚠️  Action: SCALE UP")
                print(f"   Current Capacity: {rec['current_capacity']} units")
                print(f"   Recommended: {rec['recommended_capacity']} units")
                print(f"   Add: +{rec['additional_units']} units")
                print(f"   Timeline: Within {rec['days_until_needed']} days")
                print(f"   Cost Impact: +${rec['estimated_cost_increase']:.2f}/month")
            
            elif action == 'scale_down':
                print(f"   💰 Action: SCALE DOWN")
                print(f"   Current Capacity: {rec['current_capacity']} units")
                print(f"   Recommended: {rec['recommended_capacity']} units")
                print(f"   Remove: -{rec['units_to_remove']} units")
                print(f"   Cost Savings: -${rec['estimated_cost_savings']:.2f}/month")
            
            else:
                print(f"   ✅ Action: NO CHANGE NEEDED")
                print(f"   Current Capacity: {rec['current_capacity']} units")
            
            print(f"   Predicted Peak: {rec['predicted_max_usage']:.2f}%")
        
        cost_impact = plan['total_monthly_cost_impact']
        print(f"\n💵 Total Monthly Cost Impact: {'+' if cost_impact > 0 else ''}${cost_impact:.2f}")
        print("="*70)

# Generate scaling recommendations
if __name__ == "__main__":
    import numpy as np
    
    recommender = ScalingRecommender(cost_per_unit=0.10)
    
    # Load data
    df = pd.read_csv('../data/resource_metrics.csv')
    
    # Current resources
    resources = {
        'cpu': 10,      # 10 CPU units
        'memory': 8,    # 8 GB units
        'disk': 5       # 5 storage units
    }
    
    # Generate scaling plan
    plan = recommender.generate_scaling_plan(df, resources)
    
    # Print recommendations
    recommender.print_scaling_plan(plan)
```

## Exercises

### Exercise 1: Multi-variate Forecasting
Implement forecasting that considers correlations between metrics:
```python
# CPU, memory, and network often correlate
# Use VAR (Vector Autoregression) model
```

### Exercise 2: Anomaly-aware Forecasting
Filter anomalies before forecasting to improve accuracy

### Exercise 3: Cost Optimization
Build optimizer that balances performance SLAs with cost

## Validation

Run complete capacity planning:

```bash
# Generate data
python scripts/generate_metrics.py

# Run forecasting
python src/capacity_forecaster.py

# Get scaling recommendations
python src/scaling_recommender.py
```

## Key Takeaways

✅ Time series forecasting predicts future resource needs  
✅ Prophet handles seasonality and trends automatically  
✅ LSTM captures complex patterns in metrics  
✅ Capacity planning prevents outages and optimizes costs  
✅ Automated recommendations reduce manual planning effort

## Next Steps

- **Lab 05**: Alert correlation and noise reduction
- Integrate with auto-scaling systems
- Build cost optimization dashboard
- Implement multi-cloud capacity planning

## Resources

- [Prophet Documentation](https://facebook.github.io/prophet/)
- [Time Series Forecasting](https://otexts.com/fpp3/)
- [Capacity Planning Guide](https://landing.google.com/sre/sre-book/chapters/addressing-cascading-failures/)
