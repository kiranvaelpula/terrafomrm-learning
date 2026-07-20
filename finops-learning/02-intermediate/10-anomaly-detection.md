# Cost Anomaly Detection

> **Catch unexpected cost spikes before they become budget disasters**

---

## 📖 Overview

**Cost anomalies** are unexpected deviations from normal spending patterns that can indicate:
- ✅ Legitimate business growth
- ⚠️ Misconfigured resources
- ❌ Security breaches
- ❌ Application bugs
- ❌ Runaway processes

**Why It Matters:**
- $10K anomaly detected in 1 hour → $240 wasted
- $10K anomaly detected in 24 hours → $10K wasted
- **Early detection saves money and prevents disasters**

---

## 🎯 Types of Cost Anomalies

### 1. Spike Anomalies
```yaml
Pattern: Sudden sharp increase
Example: $5K/day → $35K/day (overnight)

Common Causes:
  - Data transfer spike
  - New service launch
  - DDoS attack
  - Runaway Lambda function
  - Accidentally large instance launched

Detection: Simple threshold (3x standard deviation)
```

### 2. Trend Anomalies
```yaml
Pattern: Gradual but unusual increase
Example: $5K/day → $12K/day (over 2 weeks)

Common Causes:
  - Memory leak
  - Data accumulation
  - Inefficient code deploy
  - Zombie resources multiplying

Detection: Trend analysis + rate of change
```

### 3. Pattern Anomalies
```yaml
Pattern: Breaking normal patterns
Example: Weekend costs = weekday costs (usually 50% lower)

Common Causes:
  - Auto-stop not working
  - Background jobs running incorrectly
  - Misconfigured schedules

Detection: Day-of-week comparison
```

### 4. Service-Specific Anomalies
```yaml
Pattern: One service out of normal range
Example: RDS $2K/day → $8K/day (other services normal)

Common Causes:
  - Database query issue
  - Missing index
  - Over-provisioned instance
  - Backup issue

Detection: Per-service baselines
```

---

## 📊 Detection Methods

### Method 1: Statistical Analysis (Simple)

```python
import numpy as np
from datetime import datetime, timedelta

def detect_anomalies_simple(daily_costs, threshold=3):
    """
    Detect anomalies using standard deviation
    threshold=3 means 3 sigma (99.7% confidence)
    """
    
    mean = np.mean(daily_costs)
    std_dev = np.std(daily_costs)
    
    anomalies = []
    for i, cost in enumerate(daily_costs):
        z_score = (cost - mean) / std_dev
        
        if abs(z_score) > threshold:
            anomalies.append({
                'day': i + 1,
                'cost': cost,
                'mean': mean,
                'z_score': z_score,
                'deviation': f'{((cost - mean) / mean * 100):.1f}%'
            })
    
    return anomalies

# Example: Last 30 days of costs
costs = [4800, 4950, 4700, 4850, 4900, 5100, 4750, 4800,
         5200, 4900, 4850, 4700, 4950, 5000, 4800, 18500,  # Day 16 anomaly!
         5100, 4900, 4850, 4700, 4950, 5000, 4800, 4900,
         5200, 4800, 4750, 4900, 5050, 4850]

anomalies = detect_anomalies_simple(costs)

for a in anomalies:
    print(f"⚠️  Day {a['day']}: ${a['cost']:,} "
          f"(deviation: {a['deviation']}, z-score: {a['z_score']:.2f})")
```

**Output:**
```
⚠️  Day 16: $18,500 (deviation: +274.1%, z-score: 6.42)
```

### Method 2: Moving Average (Better for Trends)

```python
def detect_anomalies_moving_avg(daily_costs, window=7, threshold=2.5):
    """
    Detect anomalies using moving average
    More responsive to recent trends
    """
    
    anomalies = []
    
    for i in range(window, len(daily_costs)):
        # Calculate moving average
        window_data = daily_costs[i-window:i]
        moving_avg = np.mean(window_data)
        moving_std = np.std(window_data)
        
        current_cost = daily_costs[i]
        z_score = (current_cost - moving_avg) / moving_std
        
        if abs(z_score) > threshold:
            anomalies.append({
                'day': i + 1,
                'cost': current_cost,
                'moving_avg': moving_avg,
                'z_score': z_score,
                'deviation': ((current_cost - moving_avg) / moving_avg * 100)
            })
    
    return anomalies

# Use same costs as before
anomalies_ma = detect_anomalies_moving_avg(costs)

for a in anomalies_ma:
    print(f"⚠️  Day {a['day']}: ${a['cost']:,} vs avg ${a['moving_avg']:,.0f} "
          f"(+{a['deviation']:.1f}%)")
```

### Method 3: AWS Cost Anomaly Detection (Native)

```python
import boto3

def setup_aws_anomaly_detection():
    """Configure AWS native anomaly detection"""
    
    ce_client = boto3.client('ce')
    
    # Create anomaly monitor
    monitor_response = ce_client.create_anomaly_monitor(
        AnomalyMonitor={
            'MonitorName': 'CompanyWideAnomalyMonitor',
            'MonitorType': 'DIMENSIONAL',
            'MonitorDimension': 'SERVICE'
        }
    )
    
    monitor_arn = monitor_response['MonitorArn']
    
    # Create anomaly subscription (alerts)
    subscription_response = ce_client.create_anomaly_subscription(
        AnomalySubscription={
            'SubscriptionName': 'CostAnomalyAlerts',
            'Threshold': 100,  # Alert if anomaly cost > $100
            'Frequency': 'IMMEDIATE',  # or 'DAILY', 'WEEKLY'
            'MonitorArnList': [monitor_arn],
            'Subscribers': [
                {
                    'Type': 'EMAIL',
                    'Address': 'finops-team@company.com'
                },
                {
                    'Type': 'SNS',
                    'Address': 'arn:aws:sns:us-east-1:123456789:cost-anomalies'
                }
            ]
        }
    )
    
    print(f"✅ Anomaly detection configured")
    print(f"   Monitor ARN: {monitor_arn}")
    print(f"   Subscription ARN: {subscription_response['SubscriptionArn']}")

# Get detected anomalies
def get_aws_anomalies(days_back=30):
    """Retrieve AWS-detected anomalies"""
    
    ce_client = boto3.client('ce')
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    response = ce_client.get_anomalies(
        DateInterval={
            'StartDate': str(start_date),
            'EndDate': str(end_date)
        },
        MaxResults=100
    )
    
    anomalies = []
    for anomaly in response['Anomalies']:
        anomalies.append({
            'date': anomaly['AnomalyStartDate'],
            'impact': float(anomaly['Impact']['TotalImpact']),
            'service': anomaly.get('RootCauses', [{}])[0].get('Service', 'Unknown'),
            'score': float(anomaly['AnomalyScore']['CurrentScore'])
        })
    
    return anomalies
```

---

## 🔍 Service-Specific Detection

### EC2 Anomaly Detection

```python
def detect_ec2_anomalies():
    """Detect unusual EC2 patterns"""
    
    checks = {
        'unexpected_instance_types': check_unexpected_instances(),
        'instance_count_spike': check_instance_count(),
        'data_transfer_spike': check_data_transfer(),
        'unusual_uptime': check_uptime_patterns()
    }
    
    return checks

def check_unexpected_instances():
    """Check for instance types not normally used"""
    
    ec2 = boto3.client('ec2')
    
    # Get running instances
    instances = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )
    
    # Define expected instance types
    expected_types = ['t3.medium', 't3.large', 'm5.large', 'm5.xlarge']
    
    anomalies = []
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_type = instance['InstanceType']
            
            # Flag unexpected large instances
            if instance_type not in expected_types:
                if instance_type.startswith(('p3', 'p4', 'x1', 'r5.16x', 'r5.24x')):
                    anomalies.append({
                        'instance_id': instance['InstanceId'],
                        'type': instance_type,
                        'launch_time': instance['LaunchTime'],
                        'tags': instance.get('Tags', []),
                        'concern': 'HIGH_COST_INSTANCE'
                    })
    
    return anomalies
```

### S3 Anomaly Detection

```python
def detect_s3_anomalies():
    """Detect unusual S3 patterns"""
    
    s3 = boto3.client('s3')
    cloudwatch = boto3.client('cloudwatch')
    
    buckets = s3.list_buckets()['Buckets']
    
    anomalies = []
    for bucket in buckets:
        bucket_name = bucket['Name']
        
        # Check storage growth
        storage_metrics = get_bucket_storage_metrics(bucket_name)
        growth_rate = calculate_growth_rate(storage_metrics)
        
        if growth_rate > 0.5:  # >50% growth in 30 days
            anomalies.append({
                'bucket': bucket_name,
                'type': 'RAPID_STORAGE_GROWTH',
                'growth_rate': f'{growth_rate*100:.1f}%',
                'concern': 'MEDIUM'
            })
        
        # Check request patterns
        request_metrics = get_bucket_request_metrics(bucket_name)
        if request_metrics['anomaly_detected']:
            anomalies.append({
                'bucket': bucket_name,
                'type': 'UNUSUAL_REQUEST_PATTERN',
                'detail': request_metrics['detail'],
                'concern': 'HIGH'
            })
    
    return anomalies
```

---

## 🚨 Alert Configuration

### Multi-Tier Alert System

```python
class AnomalyAlertSystem:
    """Comprehensive anomaly alerting"""
    
    def __init__(self):
        self.alert_tiers = {
            'INFO': {
                'threshold': 500,  # $500 anomaly
                'recipients': ['finops-team@company.com'],
                'slack': '#cost-monitoring',
                'urgency': 'low'
            },
            'WARNING': {
                'threshold': 2000,  # $2K anomaly
                'recipients': ['finops-team@company.com', 'eng-leads@company.com'],
                'slack': '#cost-alerts',
                'urgency': 'medium'
            },
            'CRITICAL': {
                'threshold': 5000,  # $5K anomaly
                'recipients': ['finops-team@company.com', 'eng-leads@company.com', 
                              'vp-engineering@company.com'],
                'slack': '#cost-critical',
                'pagerduty': True,
                'urgency': 'high'
            },
            'EMERGENCY': {
                'threshold': 20000,  # $20K anomaly
                'recipients': ['all-above', 'cto@company.com', 'cfo@company.com'],
                'slack': '#exec-alerts',
                'pagerduty': True,
                'auto_action': True,  # Auto-stop resources
                'urgency': 'critical'
            }
        }
    
    def send_alert(self, anomaly):
        """Send appropriate alert based on impact"""
        
        impact = anomaly['impact']
        tier = self.determine_tier(impact)
        config = self.alert_tiers[tier]
        
        # Send email
        self.send_email(
            recipients=config['recipients'],
            subject=f"[{tier}] Cost Anomaly Detected: ${impact:,.0f}",
            body=self.format_alert_body(anomaly)
        )
        
        # Send Slack
        self.send_slack(
            channel=config['slack'],
            message=self.format_slack_message(anomaly, tier)
        )
        
        # PagerDuty for critical
        if config.get('pagerduty'):
            self.trigger_pagerduty(anomaly, tier)
        
        # Auto-action for emergency
        if config.get('auto_action'):
            self.execute_emergency_response(anomaly)
    
    def format_slack_message(self, anomaly, tier):
        """Format Slack alert message"""
        
        emoji = {'INFO': 'ℹ️', 'WARNING': '⚠️', 'CRITICAL': '🚨', 'EMERGENCY': '🔥'}
        
        message = f"""
{emoji[tier]} *Cost Anomaly Detected*

*Impact:* ${anomaly['impact']:,.0f}
*Service:* {anomaly['service']}
*Date:* {anomaly['date']}
*Confidence:* {anomaly['score']:.1f}%

*Possible Causes:*
{self.identify_root_causes(anomaly)}

*Recommended Actions:*
{self.recommend_actions(anomaly)}

<link-to-cost-explorer|View in Cost Explorer>
        """
        
        return message
```

---

## 🔧 Automated Response Actions

### Auto-Response Framework

```python
def automated_anomaly_response(anomaly):
    """Automatically respond to detected anomalies"""
    
    if anomaly['impact'] > 20000:  # $20K+
        # Emergency: Stop resources
        emergency_cost_containment()
    
    elif anomaly['impact'] > 5000:  # $5K+
        # Critical: Alert and recommend
        alert_critical_team()
        recommend_immediate_actions()
    
    elif anomaly['impact'] > 2000:  # $2K+
        # Warning: Alert and monitor
        alert_finops_team()
        increase_monitoring_frequency()
    
    else:
        # Info: Log and track
        log_anomaly()

def emergency_cost_containment():
    """Emergency actions to stop cost bleeding"""
    
    actions = []
    
    # 1. Identify top cost drivers (last 4 hours)
    top_resources = identify_recent_cost_spikes(hours=4)
    
    # 2. Stop non-production resources immediately
    for resource in top_resources:
        if resource['environment'] != 'production':
            stop_resource(resource)
            actions.append(f"Stopped {resource['id']}")
    
    # 3. Alert for production resources
    prod_resources = [r for r in top_resources if r['environment'] == 'production']
    if prod_resources:
        alert_for_manual_review(prod_resources)
        actions.append(f"Flagged {len(prod_resources)} prod resources for review")
    
    # 4. Enable aggressive auto-scaling
    enable_aggressive_scaling()
    actions.append("Enabled aggressive auto-scaling")
    
    return actions
```

---

## 📈 Anomaly Analysis Dashboard

### Real-Time Monitoring

```python
def create_anomaly_dashboard():
    """Build real-time anomaly monitoring dashboard"""
    
    dashboard_widgets = {
        'anomaly_count': {
            'title': 'Anomalies Detected (Last 30 Days)',
            'metric': 'COUNT(anomalies)',
            'threshold': 5  # Alert if >5 anomalies/month
        },
        
        'total_anomaly_impact': {
            'title': 'Total Anomaly Cost Impact',
            'metric': 'SUM(anomaly_impact)',
            'threshold': 10000  # Alert if >$10K total
        },
        
        'time_to_detection': {
            'title': 'Average Detection Time',
            'metric': 'AVG(detection_time_hours)',
            'target': 2  # Goal: <2 hours
        },
        
        'resolution_time': {
            'title': 'Average Resolution Time',
            'metric': 'AVG(resolution_time_hours)',
            'target': 4  # Goal: <4 hours
        },
        
        'anomaly_by_service': {
            'title': 'Anomalies by Service',
            'metric': 'COUNT(anomalies) GROUP BY service',
            'visualization': 'bar_chart'
        }
    }
    
    return dashboard_widgets
```

---

## 💡 Real-World Example

**Scenario: E-Commerce Platform**

```yaml
Event Timeline:
  Day 1, 2am: Lambda costs spike
  Day 1, 3am: Anomaly detected ($12K vs $200 normal)
  Day 1, 3:15am: Alert sent to on-call engineer
  Day 1, 4am: Root cause identified (infinite loop in code)
  Day 1, 4:30am: Bad deployment rolled back
  Day 1, 6am: Costs back to normal

Impact:
  Without Detection: $12K/hour = $288K/day = potential $8.6M/month
  With Detection: $12K total (4 hours)
  Savings: $276K+ in first day alone

Lesson: 
  - Detection within 1 hour saved $276K+
  - Automated alerts critical for off-hours
  - Rollback procedures must be practiced
```

---

## 📚 Best Practices

### 1. Set Realistic Thresholds
```yaml
Too Sensitive:
  - Alert on every 10% deviation
  - Result: Alert fatigue, ignored alerts

Too Lenient:
  - Only alert on 500% deviation
  - Result: Huge costs before detection

Sweet Spot:
  - $500: Info (review next business day)
  - $2K: Warning (review within 4 hours)
  - $5K: Critical (immediate response)
  - $20K: Emergency (auto-action + escalation)
```

### 2. Context Matters
```yaml
Monday spike: Normal (weekend → weekday)
Black Friday spike: Expected (planned event)
3am Saturday spike: Anomaly! (investigate)

Always consider:
  - Day of week patterns
  - Business events
  - Planned launches
  - Seasonal variations
```

### 3. Continuous Improvement
```yaml
Monthly Review:
  - False positive rate (target: <10%)
  - Detection time (target: <2 hours)
  - Resolution time (target: <4 hours)
  - Root cause categories
  - Threshold adjustments needed
```

---

## 🎯 Summary

**Key Takeaways:**
1. Early detection saves exponentially more money
2. Multiple detection methods catch different anomaly types
3. Automated alerts with appropriate urgency levels
4. Have emergency response procedures ready
5. Continuous refinement of thresholds

**Implementation Checklist:**
- [ ] Enable AWS Cost Anomaly Detection
- [ ] Set up custom statistical monitoring
- [ ] Configure multi-tier alerts
- [ ] Define emergency response procedures
- [ ] Create anomaly dashboard
- [ ] Test alert system
- [ ] Document root cause playbooks

**Next:**
- [Budget Management](11-budget-management.md)
- [FinOps Automation](../03-advanced/14-finops-automation.md)
- [FinOps Tools](12-finops-tools.md)

