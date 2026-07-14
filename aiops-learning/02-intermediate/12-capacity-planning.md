# Capacity Planning with AIOps

## Learning Objectives
- Forecast infrastructure capacity needs
- Optimize resource allocation
- Plan for growth
- Prevent capacity-related outages

---

## What is Capacity Planning?

Capacity planning ensures you have sufficient resources to meet demand:
- **Right-sizing**: Not too much, not too little
- **Growth planning**: Anticipate future needs
- **Cost optimization**: Avoid over-provisioning
- **Performance**: Maintain SLAs

**Traditional Approach:** Manual analysis, spreadsheets, guesswork  
**AIOps Approach:** ML-powered forecasting, automated recommendations

---

## Resource Forecasting

### CPU/Memory Forecasting with Prophet

```python
from prophet import Prophet
import pandas as pd
import numpy as np

class ResourceForecaster:
    """Forecast resource usage"""
    
    def __init__(self):
        self.models = {}
    
    def prepare_data(self, metric_data):
        """Prepare data for Prophet"""
        
        df = pd.DataFrame({
            'ds': pd.to_datetime(metric_data['timestamp']),
            'y': metric_data['value']
        })
        
        # Add regressors
        df['is_business_hours'] = df['ds'].dt.hour.between(9, 17).astype(int)
        df['is_weekend'] = (df['ds'].dt.dayofweek >= 5).astype(int)
        
        return df
    
    def train(self, resource_type, historical_data):
        """Train forecasting model"""
        
        df = self.prepare_data(historical_data)
        
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05
        )
        
        # Add custom regressors
        model.add_regressor('is_business_hours')
        model.add_regressor('is_weekend')
        
        model.fit(df)
        
        self.models[resource_type] = model
        
        return model
    
    def forecast(self, resource_type, days_ahead=30):
        """Generate forecast"""
        
        model = self.models[resource_type]
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=days_ahead, freq='D')
        
        # Add regressor values
        future['is_business_hours'] = future['ds'].dt.hour.between(9, 17).astype(int)
        future['is_weekend'] = (future['ds'].dt.dayofweek >= 5).astype(int)
        
        # Forecast
        forecast = model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days_ahead)
    
    def identify_capacity_needs(self, forecast, current_capacity, threshold=80):
        """Identify when additional capacity is needed"""
        
        # Calculate when usage exceeds threshold
        forecast['usage_pct'] = (forecast['yhat'] / current_capacity) * 100
        
        needs_scaling = forecast[forecast['usage_pct'] > threshold]
        
        if not needs_scaling.empty:
            first_breach = needs_scaling.iloc[0]
            
            # Calculate required capacity
            peak_usage = forecast['yhat'].max()
            required_capacity = peak_usage / (threshold / 100)
            additional_capacity = required_capacity - current_capacity
            
            return {
                'needs_scaling': True,
                'first_breach_date': first_breach['ds'],
                'days_until_breach': (first_breach['ds'] - pd.Timestamp.now()).days,
                'current_capacity': current_capacity,
                'required_capacity': required_capacity,
                'additional_capacity': additional_capacity,
                'recommendation': f"Add {additional_capacity:.0f} units before {first_breach['ds'].date()}"
            }
        
        return {'needs_scaling': False}

# Usage
forecaster = ResourceForecaster()

# Train on historical CPU data
cpu_history = get_cpu_history(days=90)
forecaster.train('cpu', cpu_history)

# Forecast next 30 days
forecast = forecaster.forecast('cpu', days_ahead=30)

# Check capacity needs
current_cpu_cores = 16
capacity_check = forecaster.identify_capacity_needs(forecast, current_cpu_cores, threshold=80)

if capacity_check['needs_scaling']:
    print(f"⚠️ {capacity_check['recommendation']}")
```

---

## Growth Rate Analysis

```python
class GrowthAnalyzer:
    """Analyze resource growth patterns"""
    
    def calculate_growth_rate(self, historical_data, period='monthly'):
        """Calculate resource growth rate"""
        
        df = pd.DataFrame(historical_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Resample by period
        if period == 'daily':
            resampled = df.resample('D').mean()
        elif period == 'weekly':
            resampled = df.resample('W').mean()
        else:  # monthly
            resampled = df.resample('M').mean()
        
        # Calculate growth rate
        resampled['growth_rate'] = resampled['value'].pct_change() * 100
        
        # Average growth rate
        avg_growth = resampled['growth_rate'].mean()
        
        return {
            'average_growth_rate': avg_growth,
            'growth_trend': resampled,
            'projection': self.project_future_usage(resampled, avg_growth)
        }
    
    def project_future_usage(self, current_data, growth_rate, months=12):
        """Project future usage based on growth rate"""
        
        current_usage = current_data['value'].iloc[-1]
        
        projections = []
        for month in range(1, months + 1):
            projected_usage = current_usage * ((1 + growth_rate/100) ** month)
            projections.append({
                'month': month,
                'projected_usage': projected_usage
            })
        
        return pd.DataFrame(projections)
    
    def identify_inflection_points(self, growth_trend):
        """Identify when growth accelerates or decelerates"""
        
        # Calculate second derivative (acceleration)
        growth_trend['acceleration'] = growth_trend['growth_rate'].diff()
        
        # Find significant changes
        threshold = growth_trend['acceleration'].std() * 2
        inflection_points = growth_trend[abs(growth_trend['acceleration']) > threshold]
        
        return inflection_points

# Usage
analyzer = GrowthAnalyzer()

growth = analyzer.calculate_growth_rate(historical_data, period='monthly')
print(f"Average monthly growth: {growth['average_growth_rate']:.2f}%")

# Project 12 months ahead
projections = growth['projection']
print("\nProjected usage:")
print(projections)
```

---

## Cost-Optimized Capacity Planning

```python
class CostOptimizer:
    """Optimize capacity for cost"""
    
    def __init__(self):
        self.pricing = {
            'compute': {'on_demand': 0.10, 'reserved': 0.06},  # per hour
            'storage': {'standard': 0.023, 'infrequent': 0.0125},  # per GB/month
            'network': 0.09  # per GB
        }
    
    def calculate_current_cost(self, resources):
        """Calculate current monthly cost"""
        
        monthly_hours = 730  # average hours per month
        
        costs = {
            'compute': resources['compute_hours'] * self.pricing['compute']['on_demand'],
            'storage': resources['storage_gb'] * self.pricing['storage']['standard'],
            'network': resources['network_gb'] * self.pricing['network']
        }
        
        total = sum(costs.values())
        
        return {'total': total, 'breakdown': costs}
    
    def recommend_optimization(self, usage_pattern, forecast):
        """Recommend cost optimizations"""
        
        recommendations = []
        
        # Check for reserved instance savings
        steady_usage = usage_pattern['steady_state_hours']
        if steady_usage > 500:  # hours per month
            savings = steady_usage * (self.pricing['compute']['on_demand'] - 
                                     self.pricing['compute']['reserved'])
            recommendations.append({
                'action': 'purchase_reserved_instances',
                'hours': steady_usage,
                'monthly_savings': savings,
                'annual_savings': savings * 12
            })
        
        # Check for storage tiering
        if usage_pattern['infrequent_access_data'] > 100:  # GB
            gb = usage_pattern['infrequent_access_data']
            savings = gb * (self.pricing['storage']['standard'] - 
                           self.pricing['storage']['infrequent'])
            recommendations.append({
                'action': 'move_to_infrequent_storage',
                'size_gb': gb,
                'monthly_savings': savings
            })
        
        # Check for auto-scaling opportunities
        peak_to_avg_ratio = usage_pattern['peak_usage'] / usage_pattern['average_usage']
        if peak_to_avg_ratio > 2:
            recommendations.append({
                'action': 'implement_autoscaling',
                'current_ratio': peak_to_avg_ratio,
                'potential_savings': 'up to 40%'
            })
        
        return recommendations
    
    def project_future_costs(self, current_resources, growth_rate, months=12):
        """Project costs with growth"""
        
        projections = []
        
        for month in range(1, months + 1):
            scaled_resources = {
                key: value * ((1 + growth_rate/100) ** month)
                for key, value in current_resources.items()
            }
            
            cost = self.calculate_current_cost(scaled_resources)
            
            projections.append({
                'month': month,
                'total_cost': cost['total'],
                'compute_cost': cost['breakdown']['compute'],
                'storage_cost': cost['breakdown']['storage'],
                'network_cost': cost['breakdown']['network']
            })
        
        return pd.DataFrame(projections)

# Usage
optimizer = CostOptimizer()

current_resources = {
    'compute_hours': 1000,
    'storage_gb': 500,
    'network_gb': 200
}

cost = optimizer.calculate_current_cost(current_resources)
print(f"Current monthly cost: ${cost['total']:.2f}")

# Get optimization recommendations
usage_pattern = {
    'steady_state_hours': 600,
    'infrequent_access_data': 200,
    'peak_usage': 100,
    'average_usage': 40
}

recommendations = optimizer.recommend_optimization(usage_pattern, None)
print("\nCost optimization recommendations:")
for rec in recommendations:
    print(f"- {rec['action']}: Save ${rec.get('monthly_savings', 0):.2f}/month")
```

---

## Automated Capacity Management

```python
class AutoCapacityManager:
    """Automated capacity management"""
    
    def __init__(self):
        self.forecaster = ResourceForecaster()
        self.optimizer = CostOptimizer()
        self.alert_thresholds = {
            'warning': 70,  # % capacity
            'critical': 85
        }
    
    def assess_capacity_status(self, resource_type):
        """Assess current capacity status"""
        
        current_usage = get_current_usage(resource_type)
        current_capacity = get_current_capacity(resource_type)
        
        usage_pct = (current_usage / current_capacity) * 100
        
        # Forecast future usage
        forecast = self.forecaster.forecast(resource_type, days_ahead=30)
        capacity_check = self.forecaster.identify_capacity_needs(
            forecast, current_capacity, threshold=self.alert_thresholds['warning']
        )
        
        status = {
            'resource': resource_type,
            'current_usage': current_usage,
            'current_capacity': current_capacity,
            'usage_percentage': usage_pct,
            'status': self.determine_status(usage_pct),
            'forecast': capacity_check
        }
        
        return status
    
    def determine_status(self, usage_pct):
        """Determine capacity status"""
        
        if usage_pct >= self.alert_thresholds['critical']:
            return 'critical'
        elif usage_pct >= self.alert_thresholds['warning']:
            return 'warning'
        else:
            return 'healthy'
    
    def generate_capacity_report(self):
        """Generate comprehensive capacity report"""
        
        resources = ['cpu', 'memory', 'storage', 'network']
        
        report = {
            'timestamp': pd.Timestamp.now(),
            'resources': {},
            'overall_health': 'healthy'
        }
        
        for resource in resources:
            status = self.assess_capacity_status(resource)
            report['resources'][resource] = status
            
            if status['status'] in ['critical', 'warning']:
                report['overall_health'] = status['status']
        
        return report
    
    def auto_scale_if_needed(self, resource_type, status):
        """Automatically scale if needed"""
        
        if status['status'] == 'critical':
            # Immediate scaling
            scale_amount = status['current_capacity'] * 0.2  # 20% increase
            
            self.execute_scaling(resource_type, scale_amount)
            
            return {
                'scaled': True,
                'amount': scale_amount,
                'reason': 'Critical capacity threshold reached'
            }
        
        elif status['forecast']['needs_scaling']:
            # Proactive scaling
            additional = status['forecast']['additional_capacity']
            
            # Schedule scaling
            self.schedule_scaling(
                resource_type,
                additional,
                status['forecast']['first_breach_date']
            )
            
            return {
                'scaled': False,
                'scheduled': True,
                'amount': additional,
                'date': status['forecast']['first_breach_date']
            }
        
        return {'scaled': False}
    
    def execute_scaling(self, resource_type, amount):
        """Execute scaling action"""
        print(f"Scaling {resource_type} by {amount} units")
        # Implementation depends on infrastructure
    
    def schedule_scaling(self, resource_type, amount, date):
        """Schedule future scaling"""
        print(f"Scheduled {resource_type} scaling of {amount} units for {date}")
        # Add to scheduling system

# Usage
manager = AutoCapacityManager()

# Generate daily capacity report
report = manager.generate_capacity_report()

print(f"Overall Health: {report['overall_health']}")

for resource, status in report['resources'].items():
    print(f"\n{resource.upper()}:")
    print(f"  Usage: {status['usage_percentage']:.1f}%")
    print(f"  Status: {status['status']}")
    
    if status['forecast']['needs_scaling']:
        print(f"  Action needed: {status['forecast']['recommendation']}")
        
        # Auto-scale if enabled
        scaling_result = manager.auto_scale_if_needed(resource, status)
        if scaling_result['scaled']:
            print(f"  ✅ Auto-scaled by {scaling_result['amount']}")
```

---

## Summary

AIOps-powered capacity planning enables:
- Accurate resource forecasting
- Proactive capacity management
- Cost optimization
- Automated scaling decisions

---

**Next**: [Interview Questions - Intermediate →](interview-questions-intermediate.md)
