# Predictive Analytics for IT Operations

## Learning Objectives
- Understand predictive analytics in AIOps
- Predict system failures before they occur
- Forecast resource needs
- Implement predictive models

---

## What is Predictive Analytics in AIOps?

Predictive analytics uses historical data and ML models to forecast future events:
- **Failure Prediction**: Detect issues before they cause outages
- **Capacity Forecasting**: Plan infrastructure needs
- **Performance Degradation**: Identify slow degradation trends
- **Security Threats**: Predict potential attacks

---

## Failure Prediction

### 1. Disk Failure Prediction

Using SMART metrics to predict disk failures:

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

class DiskFailurePredictor:
    """Predict disk failures using SMART metrics"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.features = [
            'reallocated_sectors',
            'pending_sectors',
            'uncorrectable_errors',
            'temperature',
            'power_on_hours',
            'read_error_rate',
            'seek_error_rate'
        ]
    
    def prepare_data(self, smart_data):
        """Prepare SMART metrics for prediction"""
        
        df = pd.DataFrame(smart_data)
        
        # Add derived features
        df['error_rate_trend'] = df.groupby('disk_id')['read_error_rate'].diff()
        df['temp_trend'] = df.groupby('disk_id')['temperature'].diff()
        
        # Rolling statistics
        df['avg_temp_7d'] = df.groupby('disk_id')['temperature'].rolling(7).mean().reset_index(0, drop=True)
        
        return df
    
    def train(self, historical_data):
        """Train failure prediction model"""
        
        df = self.prepare_data(historical_data)
        
        X = df[self.features]
        y = df['failed_within_30_days']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        score = self.model.score(X_test, y_test)
        print(f"Model accuracy: {score:.2f}")
        
        # Feature importance
        importances = pd.DataFrame({
            'feature': self.features,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop predictors:")
        print(importances.head())
    
    def predict_failure(self, current_metrics):
        """Predict if disk will fail soon"""
        
        df = self.prepare_data([current_metrics])
        X = df[self.features]
        
        # Probability of failure
        failure_prob = self.model.predict_proba(X)[0][1]
        
        if failure_prob > 0.7:
            return {
                'alert': True,
                'probability': failure_prob,
                'message': f"High failure risk ({failure_prob:.1%})",
                'recommended_action': 'Replace disk immediately',
                'risk_level': 'critical'
            }
        elif failure_prob > 0.4:
            return {
                'alert': True,
                'probability': failure_prob,
                'message': f"Moderate failure risk ({failure_prob:.1%})",
                'recommended_action': 'Schedule disk replacement',
                'risk_level': 'warning'
            }
        else:
            return {
                'alert': False,
                'probability': failure_prob,
                'message': 'Disk health OK',
                'risk_level': 'normal'
            }

# Usage
predictor = DiskFailurePredictor()

# Train on historical data
historical_data = load_smart_history()
predictor.train(historical_data)

# Predict for current disk
current_smart = get_disk_smart_metrics('disk-001')
prediction = predictor.predict_failure(current_smart)

if prediction['alert']:
    send_alert(prediction)
```

---

## Service Outage Prediction

### Predict Service Failures

```python
from sklearn.ensemble import GradientBoostingClassifier
import numpy as np

class ServiceOutagePredictor:
    """Predict service outages based on multiple signals"""
    
    def __init__(self):
        self.model = GradientBoostingClassifier()
    
    def extract_features(self, time_window='1h'):
        """Extract features from various sources"""
        
        # Metrics features
        metrics = {
            'cpu_p95': get_percentile('cpu_usage', 95, time_window),
            'memory_p95': get_percentile('memory_usage', 95, time_window),
            'error_rate': get_error_rate(time_window),
            'latency_p99': get_percentile('latency', 99, time_window),
            'request_rate': get_request_rate(time_window)
        }
        
        # Log features
        logs = {
            'error_count': count_errors(time_window),
            'warning_count': count_warnings(time_window),
            'unique_error_types': count_unique_errors(time_window)
        }
        
        # Historical pattern
        historical = {
            'outages_last_7d': count_outages(days=7),
            'time_since_last_outage': time_since_last_outage(),
            'recent_deployments': count_deployments(time_window)
        }
        
        # Combine all features
        features = {**metrics, **logs, **historical}
        
        return features
    
    def predict_outage(self, look_ahead='30m'):
        """Predict if outage will occur in next period"""
        
        features = self.extract_features()
        X = np.array(list(features.values())).reshape(1, -1)
        
        # Predict probability
        outage_prob = self.model.predict_proba(X)[0][1]
        
        if outage_prob > 0.6:
            return {
                'will_fail': True,
                'probability': outage_prob,
                'time_window': look_ahead,
                'confidence': 'high' if outage_prob > 0.8 else 'medium',
                'contributing_factors': self.identify_factors(features),
                'recommended_actions': self.suggest_actions(features)
            }
        
        return {'will_fail': False, 'probability': outage_prob}
    
    def identify_factors(self, features):
        """Identify main contributing factors"""
        
        # Get feature importances
        feature_importance = dict(zip(
            features.keys(),
            self.model.feature_importances_
        ))
        
        # Sort by importance
        top_factors = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return [f[0] for f in top_factors]
    
    def suggest_actions(self, features):
        """Suggest preventive actions"""
        
        actions = []
        
        if features['cpu_p95'] > 80:
            actions.append("Scale up compute resources")
        
        if features['error_rate'] > 0.05:
            actions.append("Investigate error spike")
        
        if features['recent_deployments'] > 0:
            actions.append("Consider rolling back recent deployment")
        
        return actions

# Continuous monitoring
predictor = ServiceOutagePredictor()

while True:
    prediction = predictor.predict_outage(look_ahead='30m')
    
    if prediction['will_fail']:
        alert = f"""
        ⚠️ SERVICE OUTAGE PREDICTED
        
        Probability: {prediction['probability']:.1%}
        Time Window: {prediction['time_window']}
        Confidence: {prediction['confidence']}
        
        Contributing Factors:
        {', '.join(prediction['contributing_factors'])}
        
        Recommended Actions:
        {chr(10).join(f"- {a}" for a in prediction['recommended_actions'])}
        """
        
        send_alert(alert)
        trigger_preventive_actions(prediction['recommended_actions'])
    
    time.sleep(300)  # Check every 5 minutes
```

---


## Capacity Forecasting

### Resource Demand Prediction

```python
from prophet import Prophet
import pandas as pd

class CapacityForecaster:
    """Forecast resource capacity needs"""
    
    def __init__(self):
        self.models = {}
    
    def prepare_data(self, metric_name, historical_data):
        """Prepare data for Prophet"""
        
        df = pd.DataFrame({
            'ds': historical_data['timestamp'],
            'y': historical_data[metric_name]
        })
        
        return df
    
    def train_forecast_model(self, metric_name, historical_data):
        """Train forecasting model"""
        
        df = self.prepare_data(metric_name, historical_data)
        
        # Create and configure Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True,
            changepoint_prior_scale=0.05
        )
        
        # Add custom seasonality for business hours
        model.add_seasonality(
            name='business_hours',
            period=1,  # daily
            fourier_order=5,
            condition_name='is_business_hours'
        )
        
        # Fit model
        model.fit(df)
        
        self.models[metric_name] = model
        
        return model
    
    def forecast_capacity(self, metric_name, days_ahead=30):
        """Forecast capacity needs"""
        
        model = self.models.get(metric_name)
        if not model:
            raise ValueError(f"No model trained for {metric_name}")
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=days_ahead, freq='D')
        
        # Make prediction
        forecast = model.predict(future)
        
        # Extract predictions
        predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days_ahead)
        
        return predictions
    
    def check_capacity_threshold(self, forecast, threshold=80):
        """Check if capacity will exceed threshold"""
        
        violations = forecast[forecast['yhat'] > threshold]
        
        if not violations.empty:
            first_violation = violations.iloc[0]
            
            return {
                'alert': True,
                'date': first_violation['ds'],
                'predicted_value': first_violation['yhat'],
                'threshold': threshold,
                'days_until': (first_violation['ds'] - pd.Timestamp.now()).days,
                'recommendation': f"Scale up before {first_violation['ds'].date()}"
            }
        
        return {'alert': False}
    
    def generate_capacity_report(self, days_ahead=90):
        """Generate comprehensive capacity report"""
        
        report = {
            'generated_at': pd.Timestamp.now(),
            'forecast_period': f'{days_ahead} days',
            'metrics': {}
        }
        
        for metric_name in self.models.keys():
            forecast = self.forecast_capacity(metric_name, days_ahead)
            threshold_check = self.check_capacity_threshold(forecast)
            
            report['metrics'][metric_name] = {
                'current_value': get_current_value(metric_name),
                'predicted_max': forecast['yhat'].max(),
                'predicted_average': forecast['yhat'].mean(),
                'threshold_alert': threshold_check
            }
        
        return report

# Usage
forecaster = CapacityForecaster()

# Train models for different metrics
metrics = ['cpu_usage', 'memory_usage', 'disk_usage', 'network_throughput']

for metric in metrics:
    historical = get_historical_data(metric, days=90)
    forecaster.train_forecast_model(metric, historical)

# Generate 30-day forecast
forecast = forecaster.forecast_capacity('cpu_usage', days_ahead=30)

# Check for capacity issues
alert = forecaster.check_capacity_threshold(forecast, threshold=80)

if alert['alert']:
    print(f"⚠️ Capacity alert: {alert['recommendation']}")
    
# Generate full report
report = forecaster.generate_capacity_report(days_ahead=90)
```

---

## Performance Degradation Prediction

### Detect Gradual Performance Decline

```python
from scipy import stats
import numpy as np

class PerformanceDegradationDetector:
    """Detect gradual performance degradation"""
    
    def __init__(self, window_size=7):
        self.window_size = window_size
    
    def detect_trend(self, metric_values):
        """Detect if metric is trending up or down"""
        
        # Linear regression on recent data
        x = np.arange(len(metric_values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, metric_values)
        
        # Determine trend
        if p_value < 0.05:  # Statistically significant
            if slope > 0:
                trend = 'increasing'
                severity = 'high' if abs(slope) > 0.1 else 'medium'
            else:
                trend = 'decreasing'
                severity = 'high' if abs(slope) > 0.1 else 'medium'
        else:
            trend = 'stable'
            severity = 'low'
        
        return {
            'trend': trend,
            'slope': slope,
            'severity': severity,
            'r_squared': r_value ** 2,
            'confidence': 1 - p_value
        }
    
    def predict_threshold_breach(self, metric_values, threshold):
        """Predict when metric will breach threshold"""
        
        trend = self.detect_trend(metric_values)
        
        if trend['trend'] == 'increasing' and trend['confidence'] > 0.95:
            # Calculate days until breach
            current_value = metric_values[-1]
            slope = trend['slope']
            
            if slope > 0:
                days_to_breach = (threshold - current_value) / slope
                
                if days_to_breach > 0 and days_to_breach < 30:
                    return {
                        'will_breach': True,
                        'days_until_breach': int(days_to_breach),
                        'predicted_date': pd.Timestamp.now() + pd.Timedelta(days=days_to_breach),
                        'confidence': trend['confidence']
                    }
        
        return {'will_breach': False}
    
    def analyze_performance_degradation(self, service_metrics):
        """Comprehensive degradation analysis"""
        
        analysis = {
            'service': service_metrics['name'],
            'timestamp': pd.Timestamp.now(),
            'degrading': False,
            'factors': []
        }
        
        # Check latency trend
        latency_trend = self.detect_trend(service_metrics['latency_history'])
        if latency_trend['trend'] == 'increasing' and latency_trend['severity'] in ['high', 'medium']:
            analysis['degrading'] = True
            analysis['factors'].append({
                'metric': 'latency',
                'trend': latency_trend,
                'impact': 'User experience degrading'
            })
        
        # Check error rate trend
        error_trend = self.detect_trend(service_metrics['error_rate_history'])
        if error_trend['trend'] == 'increasing':
            analysis['degrading'] = True
            analysis['factors'].append({
                'metric': 'error_rate',
                'trend': error_trend,
                'impact': 'Service reliability decreasing'
            })
        
        # Check throughput trend
        throughput_trend = self.detect_trend(service_metrics['throughput_history'])
        if throughput_trend['trend'] == 'decreasing':
            analysis['degrading'] = True
            analysis['factors'].append({
                'metric': 'throughput',
                'trend': throughput_trend,
                'impact': 'Processing capacity declining'
            })
        
        return analysis

# Usage
detector = PerformanceDegradationDetector()

# Monitor service performance
service_metrics = {
    'name': 'payment-service',
    'latency_history': get_metric_history('latency', days=7),
    'error_rate_history': get_metric_history('error_rate', days=7),
    'throughput_history': get_metric_history('throughput', days=7)
}

analysis = detector.analyze_performance_degradation(service_metrics)

if analysis['degrading']:
    alert = f"""
    ⚠️ PERFORMANCE DEGRADATION DETECTED
    
    Service: {analysis['service']}
    
    Degrading Factors:
    """
    
    for factor in analysis['factors']:
        alert += f"\n- {factor['metric']}: {factor['trend']['trend']} ({factor['impact']})"
    
    send_alert(alert)
```

---

## Early Warning System

### Comprehensive Prediction System

```python
class EarlyWarningSystem:
    """Integrated early warning system"""
    
    def __init__(self):
        self.disk_predictor = DiskFailurePredictor()
        self.outage_predictor = ServiceOutagePredictor()
        self.capacity_forecaster = CapacityForecaster()
        self.degradation_detector = PerformanceDegradationDetector()
    
    def assess_system_health(self):
        """Comprehensive system health assessment"""
        
        warnings = []
        
        # Check disk health
        for disk in get_all_disks():
            smart = get_disk_smart_metrics(disk['id'])
            prediction = self.disk_predictor.predict_failure(smart)
            
            if prediction['alert']:
                warnings.append({
                    'type': 'disk_failure',
                    'severity': prediction['risk_level'],
                    'component': disk['id'],
                    'message': prediction['message'],
                    'action': prediction['recommended_action']
                })
        
        # Check service outage risk
        outage_pred = self.outage_predictor.predict_outage()
        if outage_pred['will_fail']:
            warnings.append({
                'type': 'service_outage',
                'severity': 'critical',
                'probability': outage_pred['probability'],
                'actions': outage_pred['recommended_actions']
            })
        
        # Check capacity
        capacity_report = self.capacity_forecaster.generate_capacity_report(30)
        for metric, data in capacity_report['metrics'].items():
            if data['threshold_alert']['alert']:
                warnings.append({
                    'type': 'capacity',
                    'severity': 'warning',
                    'metric': metric,
                    'details': data['threshold_alert']
                })
        
        # Check performance degradation
        for service in get_all_services():
            metrics = get_service_metrics(service)
            analysis = self.degradation_detector.analyze_performance_degradation(metrics)
            
            if analysis['degrading']:
                warnings.append({
                    'type': 'degradation',
                    'severity': 'medium',
                    'service': service,
                    'factors': analysis['factors']
                })
        
        return {
            'timestamp': pd.Timestamp.now(),
            'health_score': self.calculate_health_score(warnings),
            'warnings': warnings,
            'total_warnings': len(warnings)
        }
    
    def calculate_health_score(self, warnings):
        """Calculate overall health score (0-100)"""
        
        base_score = 100
        
        severity_weights = {
            'critical': 30,
            'high': 20,
            'medium': 10,
            'warning': 5,
            'low': 2
        }
        
        for warning in warnings:
            penalty = severity_weights.get(warning.get('severity', 'low'), 0)
            base_score -= penalty
        
        return max(0, base_score)
    
    def generate_daily_report(self):
        """Generate daily health report"""
        
        assessment = self.assess_system_health()
        
        report = f"""
        DAILY SYSTEM HEALTH REPORT
        {assessment['timestamp'].strftime('%Y-%m-%d')}
        
        Health Score: {assessment['health_score']}/100
        
        Warnings: {assessment['total_warnings']}
        """
        
        if assessment['warnings']:
            report += "\n\nACTION ITEMS:\n"
            
            for i, warning in enumerate(assessment['warnings'], 1):
                report += f"\n{i}. [{warning['severity'].upper()}] "
                report += f"{warning['type']}: {warning.get('message', 'See details')}"
        else:
            report += "\n\n✅ No warnings - System health is good!"
        
        return report

# Usage
ews = EarlyWarningSystem()

# Run daily assessment
assessment = ews.assess_system_health()

if assessment['health_score'] < 80:
    report = ews.generate_daily_report()
    send_to_ops_team(report)

# Schedule daily reports
schedule.every().day.at("09:00").do(lambda: send_to_ops_team(ews.generate_daily_report()))
```

---

## Best Practices

1. **Use Multiple Models**: Combine different prediction approaches
2. **Validate Predictions**: Track accuracy and adjust models
3. **Set Appropriate Thresholds**: Balance sensitivity and false positives
4. **Provide Context**: Explain why predictions are made
5. **Enable Actions**: Link predictions to remediation
6. **Update Regularly**: Retrain models with new data
7. **Monitor Model Drift**: Track prediction accuracy over time

---

## Summary

Predictive analytics in AIOps enables:
- Proactive failure prevention
- Capacity planning
- Performance optimization
- Reduced downtime and costs

---

**Next**: [Alert Correlation →](10-alert-correlation.md)
