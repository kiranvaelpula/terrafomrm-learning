# AWS Cost Explorer and Analysis

## Overview

AWS Cost Explorer is the primary tool for analyzing cloud spending. This guide covers practical use of Cost Explorer for DevOps teams to understand, forecast, and optimize AWS costs.

**What You'll Learn:**
- Cost Explorer features and limitations
- Creating custom cost reports
- Cost forecasting
- Identifying cost anomalies
- Filtering and grouping strategies
- API automation

---

## Cost Explorer Basics

### Accessing Cost Explorer

```bash
# Enable Cost Explorer (one-time, takes 24 hours)
aws ce enable-cost-explorer

# Check if enabled
aws organizations describe-organization | grep FeatureSet
```

**Web Console:**
1. AWS Console → Billing & Cost Management
2. Cost Explorer → Launch Cost Explorer
3. Wait 24 hours for data processing

---

## Key Features

### 1. Daily/Monthly Cost Views

View costs at different granularities:

```python
# get_daily_costs.py
import boto3
from datetime import datetime, timedelta

ce = boto3.client('ce', region_name='us-east-1')

def get_daily_costs(days=30):
    """Get daily costs for last N days"""
    end = datetime.now().date()
    start = end - timedelta(days=days)
    
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start.strftime('%Y-%m-%d'),
            'End': end.strftime('%Y-%m-%d')
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost', 'UsageQuantity'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }
        ]
    )
    
    # Parse results
    daily_costs = {}
    for result in response['ResultsByTime']:
        date = result['TimePeriod']['Start']
        daily_costs[date] = {}
        
        for group in result['Groups']:
            service = group['Keys'][0]
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            daily_costs[date][service] = cost
    
    return daily_costs

# Usage
costs = get_daily_costs(7)
for date, services in costs.items():
    total = sum(services.values())
    print(f"\n{date}: ${total:.2f}")
    for service, cost in sorted(services.items(), key=lambda x: x[1], reverse=True)[:5]:
        if cost > 1:  # Only show services > $1
            print(f"  {service:30s}: ${cost:8.2f}")
```

Output:

```
2026-07-11: $2,345.67
  Amazon Elastic Compute Cloud  : $ 1,234.56
  Amazon Relational Database    : $   567.89
  Amazon Simple Storage Service : $   234.12
  AWS Lambda                    : $   123.45
  Amazon CloudFront             : $    89.23

2026-07-12: $2,456.78
  ...
```

### 2. Cost by Service

Identify top spending services:

```python
# cost_by_service.py
def get_monthly_service_costs():
    """Get current month costs grouped by service"""
    ce = boto3.client('ce')
    
    # First day of current month
    today = datetime.now()
    start = today.replace(day=1).strftime('%Y-%m-%d')
    end = today.strftime('%Y-%m-%d')
    
    response = ce.get_cost_and_usage(
        TimePeriod={'Start': start, 'End': end},
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )
    
    services = {}
    for group in response['ResultsByTime'][0]['Groups']:
        service = group['Keys'][0]
        cost = float(group['Metrics']['UnblendedCost']['Amount'])
        services[service] = cost
    
    # Calculate total
    total = sum(services.values())
    
    # Sort and display
    print(f"\nCurrent Month Cost: ${total:,.2f}\n")
    print(f"{'Service':<50s} {'Cost':>12s} {'%':>6s}")
    print("-" * 70)
    
    for service, cost in sorted(services.items(), key=lambda x: x[1], reverse=True):
        if cost > 10:  # Only show services > $10
            pct = (cost / total) * 100
            print(f"{service:<50s} ${cost:>10,.2f} {pct:>5.1f}%")

get_monthly_service_costs()
```

Output:

```
Current Month Cost: $125,450.23

Service                                            Cost        %
----------------------------------------------------------------------
Amazon Elastic Compute Cloud                   $ 45,230.12  36.0%
Amazon Relational Database Service             $ 28,450.45  22.7%
Amazon Simple Storage Service                  $ 15,320.78  12.2%
AWS Lambda                                     $  8,920.34   7.1%
Amazon CloudFront                              $  6,780.23   5.4%
Amazon Elastic Load Balancing                  $  4,560.89   3.6%
Amazon Route 53                                $  2,340.12   1.9%
AWS Data Transfer                              $  8,920.45   7.1%
Other                                          $  4,927.85   3.9%
```

### 3. Cost by Account (Organizations)

```python
# cost_by_account.py
def get_cost_by_account():
    """Get costs grouped by AWS account"""
    ce = boto3.client('ce')
    
    # Last 30 days
    end = datetime.now().date()
    start = end - timedelta(days=30)
    
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start.strftime('%Y-%m-%d'),
            'End': end.strftime('%Y-%m-%d')
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'LINKED_ACCOUNT'
            }
        ]
    )
    
    accounts = {}
    for group in response['ResultsByTime'][0]['Groups']:
        account_id = group['Keys'][0]
        cost = float(group['Metrics']['UnblendedCost']['Amount'])
        accounts[account_id] = cost
    
    # Get account names (from Organizations)
    org = boto3.client('organizations')
    account_names = {}
    
    for account_id in accounts.keys():
        try:
            account = org.describe_account(AccountId=account_id)
            account_names[account_id] = account['Account']['Name']
        except:
            account_names[account_id] = 'Unknown'
    
    # Display
    print(f"\n{'Account Name':<30s} {'Account ID':<15s} {'Cost':>12s}")
    print("-" * 60)
    
    for account_id, cost in sorted(accounts.items(), key=lambda x: x[1], reverse=True):
        name = account_names.get(account_id, 'Unknown')
        print(f"{name:<30s} {account_id:<15s} ${cost:>10,.2f}")
```

Output:

```
Account Name                   Account ID      Cost
------------------------------------------------------------
production                     123456789012   $ 85,450.23
staging                        234567890123   $ 25,320.45
development                    345678901234   $ 10,230.78
security-tools                 456789012345   $  3,450.00
shared-services                567890123456   $    999.77
```

---

## Advanced Filtering

### 1. Filter by Tag

```python
# cost_by_team.py
def get_cost_by_team_tag():
    """Get costs grouped by Owner tag"""
    ce = boto3.client('ce')
    
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': '2026-07-01',
            'End': '2026-07-18'
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {
                'Type': 'TAG',
                'Key': 'Owner'
            }
        ],
        Filter={
            'Tags': {
                'Key': 'Owner',
                'Values': [],  # All values
                'MatchOptions': ['EQUALS']
            }
        }
    )
    
    teams = {}
    for group in response['ResultsByTime'][0]['Groups']:
        team = group['Keys'][0].split('$')[1]  # Remove 'Owner$' prefix
        cost = float(group['Metrics']['UnblendedCost']['Amount'])
        teams[team] = cost
    
    return teams
```

### 2. Filter by Region

```python
# cost_by_region.py
def get_cost_by_region():
    """Get costs grouped by AWS region"""
    ce = boto3.client('ce')
    
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': '2026-07-01',
            'End': '2026-07-18'
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'REGION'
            }
        ]
    )
    
    regions = {}
    for group in response['ResultsByTime'][0]['Groups']:
        region = group['Keys'][0]
        cost = float(group['Metrics']['UnblendedCost']['Amount'])
        regions[region] = cost
    
    print(f"\n{'Region':<20s} {'Cost':>12s}")
    print("-" * 35)
    
    for region, cost in sorted(regions.items(), key=lambda x: x[1], reverse=True):
        if cost > 100:  # Only show regions > $100
            print(f"{region:<20s} ${cost:>10,.2f}")
```

### 3. Complex Filters

```python
# complex_filter.py
def get_prod_ec2_linux_costs():
    """
    Get costs for:
    - Production environment
    - EC2 service only
    - Linux instances only
    """
    ce = boto3.client('ce')
    
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': '2026-07-01',
            'End': '2026-07-18'
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost', 'UsageQuantity'],
        Filter={
            'And': [
                {
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': ['Amazon Elastic Compute Cloud - Compute'],
                        'MatchOptions': ['EQUALS']
                    }
                },
                {
                    'Tags': {
                        'Key': 'Environment',
                        'Values': ['prod', 'production'],
                        'MatchOptions': ['EQUALS']
                    }
                },
                {
                    'Dimensions': {
                        'Key': 'PLATFORM',
                        'Values': ['Linux'],
                        'MatchOptions': ['STARTS_WITH']
                    }
                }
            ]
        }
    )
    
    total = 0
    for result in response['ResultsByTime']:
        cost = float(result['Total']['UnblendedCost']['Amount'])
        total += cost
    
    return total
```

---

## Cost Forecasting

Predict future costs based on historical trends:

```python
# cost_forecast.py
def forecast_monthly_cost():
    """Forecast next month's cost"""
    ce = boto3.client('ce')
    
    # Forecast for next 30 days
    start = datetime.now().date()
    end = start + timedelta(days=30)
    
    response = ce.get_cost_forecast(
        TimePeriod={
            'Start': start.strftime('%Y-%m-%d'),
            'End': end.strftime('%Y-%m-%d')
        },
        Metric='UNBLENDED_COST',
        Granularity='MONTHLY'
    )
    
    forecast = float(response['Total']['Amount'])
    
    # Get last month's actual
    last_month_end = start
    last_month_start = (last_month_end - timedelta(days=30))
    
    actual_response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': last_month_start.strftime('%Y-%m-%d'),
            'End': last_month_end.strftime('%Y-%m-%d')
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost']
    )
    
    actual = float(actual_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
    
    change = ((forecast - actual) / actual) * 100
    
    print(f"\nCost Forecast:")
    print(f"  Last 30 days (actual): ${actual:,.2f}")
    print(f"  Next 30 days (forecast): ${forecast:,.2f}")
    print(f"  Change: {change:+.1f}%")
    
    if change > 10:
        print(f"\n⚠️  WARNING: Forecasted increase of {change:.1f}%!")
        print("  Action required to prevent budget overrun")

forecast_monthly_cost()
```

Output:

```
Cost Forecast:
  Last 30 days (actual): $125,450.23
  Next 30 days (forecast): $142,320.45
  Change: +13.4%

⚠️  WARNING: Forecasted increase of 13.4%!
  Action required to prevent budget overrun
```

---

## Cost Anomaly Detection

Detect unusual spending patterns:

```python
# anomaly_detection.py
def detect_cost_anomalies():
    """
    Detect daily costs that are significantly higher than average
    """
    ce = boto3.client('ce')
    
    # Get last 30 days
    end = datetime.now().date()
    start = end - timedelta(days=30)
    
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start.strftime('%Y-%m-%d'),
            'End': end.strftime('%Y-%m-%d')
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost']
    )
    
    daily_costs = []
    for result in response['ResultsByTime']:
        date = result['TimePeriod']['Start']
        cost = float(result['Total']['UnblendedCost']['Amount'])
        daily_costs.append({'date': date, 'cost': cost})
    
    # Calculate average and standard deviation
    costs = [d['cost'] for d in daily_costs]
    avg = sum(costs) / len(costs)
    variance = sum((c - avg) ** 2 for c in costs) / len(costs)
    std_dev = variance ** 0.5
    
    # Find anomalies (>2 std deviations from mean)
    threshold = avg + (2 * std_dev)
    anomalies = [d for d in daily_costs if d['cost'] > threshold]
    
    print(f"\nCost Anomaly Detection (Last 30 Days)")
    print(f"  Average daily cost: ${avg:.2f}")
    print(f"  Standard deviation: ${std_dev:.2f}")
    print(f"  Anomaly threshold: ${threshold:.2f}")
    print(f"\nAnomalies detected: {len(anomalies)}")
    
    for anomaly in anomalies:
        pct_over = ((anomaly['cost'] - avg) / avg) * 100
        print(f"  {anomaly['date']}: ${anomaly['cost']:.2f} (+{pct_over:.1f}%)")
    
    return anomalies
```

Output:

```
Cost Anomaly Detection (Last 30 Days)
  Average daily cost: $4,181.67
  Standard deviation: $523.45
  Anomaly threshold: $5,228.57

Anomalies detected: 3
  2026-07-05: $5,890.23 (+40.8%)
  2026-07-12: $6,234.56 (+49.1%)
  2026-07-14: $5,456.78 (+30.5%)
```

### Investigating Anomalies

```python
# investigate_anomaly.py
def investigate_anomaly_date(date):
    """
    Dig into a specific day to find what caused high costs
    """
    ce = boto3.client('ce')
    
    next_day = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Get cost breakdown by service for that day
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': date,
            'End': next_day
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }
        ]
    )
    
    print(f"\nCost breakdown for {date}:")
    
    services = []
    for group in response['ResultsByTime'][0]['Groups']:
        service = group['Keys'][0]
        cost = float(group['Metrics']['UnblendedCost']['Amount'])
        services.append({'service': service, 'cost': cost})
    
    # Sort by cost
    services.sort(key=lambda x: x['cost'], reverse=True)
    
    total = sum(s['cost'] for s in services)
    print(f"Total: ${total:.2f}\n")
    
    for s in services[:10]:  # Top 10 services
        if s['cost'] > 10:
            pct = (s['cost'] / total) * 100
            print(f"  {s['service']:<50s} ${s['cost']:>8.2f} ({pct:>5.1f}%)")

# Usage
investigate_anomaly_date('2026-07-12')
```

---

## Cost and Usage Reports (CUR)

For detailed analysis, enable Cost and Usage Reports:

```python
# enable_cur.py
import boto3

cur = boto3.client('cur', region_name='us-east-1')

# Create S3 bucket for reports
s3 = boto3.client('s3')
bucket_name = 'my-company-aws-cur'

s3.create_bucket(Bucket=bucket_name)

# Enable CUR
response = cur.put_report_definition(
    ReportDefinition={
        'ReportName': 'daily-cost-usage-report',
        'TimeUnit': 'DAILY',
        'Format': 'textORcsv',
        'Compression': 'GZIP',
        'AdditionalSchemaElements': [
            'RESOURCES'
        ],
        'S3Bucket': bucket_name,
        'S3Prefix': 'cur/',
        'S3Region': 'us-east-1',
        'AdditionalArtifacts': [
            'ATHENA'
        ],
        'RefreshClosedReports': True,
        'ReportVersioning': 'OVERWRITE_REPORT'
    }
)

print("Cost and Usage Report enabled")
print(f"Reports will be delivered to s3://{bucket_name}/cur/")
```

### Analyze CUR with Athena

```sql
-- Query CUR data with Athena
-- Find most expensive resources

SELECT 
    line_item_resource_id,
    product_servicename,
    SUM(line_item_unblended_cost) as cost
FROM 
    cost_and_usage_report
WHERE 
    year = '2026'
    AND month = '7'
GROUP BY 
    line_item_resource_id,
    product_servicename
ORDER BY 
    cost DESC
LIMIT 20;
```

---

## Savings Plans and RIs Analysis

Track Reserved Instance and Savings Plans utilization:

```python
# ri_utilization.py
def get_ri_utilization():
    """Get Reserved Instance utilization"""
    ce = boto3.client('ce')
    
    end = datetime.now().date()
    start = end - timedelta(days=30)
    
    response = ce.get_reservation_utilization(
        TimePeriod={
            'Start': start.strftime('%Y-%m-%d'),
            'End': end.strftime('%Y-%m-%d')
        },
        Granularity='MONTHLY'
    )
    
    util = response['UtilizationsByTime'][0]['Total']
    
    utilization_pct = float(util['UtilizationPercentage'])
    purchased_hours = float(util['PurchasedHours'])
    used_hours = float(util['TotalActualHours'])
    unused_hours = purchased_hours - used_hours
    
    print(f"\nReserved Instance Utilization (Last 30 Days)")
    print(f"  Utilization: {utilization_pct:.1f}%")
    print(f"  Purchased hours: {purchased_hours:,.0f}")
    print(f"  Used hours: {used_hours:,.0f}")
    print(f"  Unused hours: {unused_hours:,.0f}")
    
    if utilization_pct < 80:
        print(f"\n⚠️  WARNING: Low RI utilization ({utilization_pct:.1f}%)")
        print("  Consider modifying or exchanging RIs")
```

---

## Cost Optimization Recommendations

Get AWS Cost Optimization Hub recommendations:

```python
# cost_recommendations.py
def get_cost_recommendations():
    """Get AWS cost optimization recommendations"""
    ce = boto3.client('ce')
    
    # Get rightsizing recommendations
    response = ce.get_rightsizing_recommendation(
        Service='AmazonEC2'
    )
    
    print("\nRightsizing Recommendations:")
    
    for rec in response['RightsizingRecommendations'][:10]:
        current = rec['CurrentInstance']
        recommended = rec.get('ModifyRecommendationDetail', {})
        
        if recommended:
            print(f"\n Instance: {current['ResourceId']}")
            print(f"  Current: {current['InstanceType']}")
            print(f"  Recommended: {recommended['TargetInstances'][0]['InstanceType']}")
            print(f"  Monthly savings: ${recommended['EstimatedMonthlySavings']:.2f}")
```

---

## Dashboard Creation

Create automated Cost Explorer dashboards:

```python
# create_cost_dashboard.py
def create_weekly_cost_report():
    """
    Generate weekly cost report
    """
    ce = boto3.client('ce')
    
    # Last 7 days
    end = datetime.now().date()
    start = end - timedelta(days=7)
    
    # Get costs by service
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start.strftime('%Y-%m-%d'),
            'End': end.strftime('%Y-%m-%d')
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )
    
    # Process data
    daily_data = {}
    for result in response['ResultsByTime']:
        date = result['TimePeriod']['Start']
        daily_data[date] = {}
        
        for group in result['Groups']:
            service = group['Keys'][0]
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            daily_data[date][service] = cost
    
    # Create HTML report
    html = f"""
    <html>
    <head><title>Weekly Cost Report</title></head>
    <body>
        <h1>AWS Cost Report</h1>
        <h2>Week of {start} to {end}</h2>
        
        <table border="1">
            <tr>
                <th>Date</th>
                <th>Total Cost</th>
                <th>Top Services</th>
            </tr>
    """
    
    for date, services in daily_data.items():
        total = sum(services.values())
        top_services = sorted(services.items(), key=lambda x: x[1], reverse=True)[:3]
        top_str = "<br>".join([f"{s}: ${c:.2f}" for s, c in top_services])
        
        html += f"""
            <tr>
                <td>{date}</td>
                <td>${total:.2f}</td>
                <td>{top_str}</td>
            </tr>
        """
    
    html += """
        </table>
    </body>
    </html>
    """
    
    # Email report
    send_email(
        to='finance@company.com',
        subject=f'Weekly AWS Cost Report - {start}',
        html_body=html
    )
```

---

## Best Practices

### 1. Enable Cost Explorer Early

- Takes 24 hours to activate
- Costs $0.01 per request (after 50 free per month)
- Enable in management account

### 2. Use Consistent Time Periods

```python
# Good - consistent monthly reporting
start = datetime(2026, 7, 1)
end = datetime(2026, 8, 1)

# Bad - arbitrary date ranges
start = datetime(2026, 6, 15)
end = datetime(2026, 7, 22)
```

### 3. Cache API Results

```python
# Cost Explorer API has rate limits
# Cache results for frequently accessed data

import json
from functools import lru_cache

@lru_cache(maxsize=128)
def get_monthly_costs_cached(month):
    """Cached version of monthly costs"""
    return get_monthly_costs(month)
```

### 4. Automate Reporting

```bash
# Cron job for daily cost report
0 8 * * * /scripts/daily_cost_report.py | mail -s "Daily AWS Cost Report" team@company.com
```

### 5. Set Up Alerts

Use AWS Budgets with Cost Explorer data:
- Daily spending threshold
- Month-to-date vs forecast
- Service-specific alerts

---

## Summary

Cost Explorer capabilities:

✅ **Daily/monthly cost views**
✅ **Filter by service, account, region, tags**
✅ **Cost forecasting**
✅ **Anomaly detection**
✅ **RI and Savings Plans utilization**
✅ **Rightsizing recommendations**
✅ **API automation**

**Key Takeaways:**
- Cost Explorer is essential for cost visibility
- Use API for automation and custom reporting
- Combine with tags for team/project allocation
- Enable CUR for detailed analysis
- Set up automated alerts and reports

---

**Related Topics:**
- [Cost Tagging Strategy](03-cost-visibility-tagging.md)
- [AWS Budgets and Alerts](../02-intermediate/07-budgets-alerts.md)
- [Cost Optimization Tools](../02-intermediate/09-finops-tools.md)
