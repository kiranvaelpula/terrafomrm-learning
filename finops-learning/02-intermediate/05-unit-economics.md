# Unit Economics for Cloud Infrastructure

## Overview

Unit economics answers the question: "How much does it cost to serve one customer, process one transaction, or deliver one API call?" This is critical for understanding profitability and scaling economics.

**What You'll Learn:**
- What are unit economics
- Calculate cost per unit metrics
- Track unit economics over time
- Optimize unit costs
- Present metrics to executives

---

## What Are Unit Economics?

### Definition

**Unit Economics** = Total Infrastructure Cost ÷ Business Units

**Business Units can be:**
- Customers (active users)
- Transactions (orders, payments)
- API calls
- Messages processed
- Data processed (GB, TB)
- Seats/licenses sold

---

## Why Unit Economics Matter

### For Engineers

```
Scenario: Your API serves 10M requests/day at $5,000/day

Unit Cost = $5,000 / 10,000,000 = $0.0005 per request

If traffic doubles to 20M requests:
- Linear scaling: $10,000/day
- With optimization: $7,500/day (25% efficiency gain)
- Savings: $2,500/day = $912,500/year
```

### For Executives

**CFO Question:** "How does cloud cost scale with revenue?"

**Bad Answer:** "Our AWS bill is $200K/month"

**Good Answer:** "Our cost per transaction is $0.15, down from $0.22 last quarter. At current growth, we'll hit profitability when we reach 2M transactions/month"

---

## Calculate Unit Economics

### 1. Cost Per API Call

```python
# calculate_cost_per_api_call.py
import boto3
from datetime import datetime, timedelta

def calculate_cost_per_api_call(start_date, end_date):
    """
    Calculate cost per API call
    """
    ce = boto3.client('ce')
    cloudwatch = boto3.client('cloudwatch')
    
    # Get total infrastructure cost
    cost_response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        Filter={
            'Tags': {
                'Key': 'Application',
                'Values': ['api-gateway'],
                'MatchOptions': ['EQUALS']
            }
        }
    )
    
    total_cost = float(
        cost_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
    )
    
    # Get total API calls from CloudWatch
    api_calls_response = cloudwatch.get_metric_statistics(
        Namespace='AWS/ApiGateway',
        MetricName='Count',
        Dimensions=[
            {'Name': 'ApiName', 'Value': 'production-api'}
        ],
        StartTime=datetime.strptime(start_date, '%Y-%m-%d'),
        EndTime=datetime.strptime(end_date, '%Y-%m-%d'),
        Period=86400,  # Daily
        Statistics=['Sum']
    )
    
    total_calls = sum(point['Sum'] for point in api_calls_response['Datapoints'])
    
    # Calculate unit economics
    cost_per_call = total_cost / total_calls if total_calls > 0 else 0
    
    result = {
        'period': f"{start_date} to {end_date}",
        'total_cost': total_cost,
        'total_calls': total_calls,
        'cost_per_call': cost_per_call,
        'cost_per_1000_calls': cost_per_call * 1000,
        'cost_per_million_calls': cost_per_call * 1_000_000
    }
    
    return result

# Usage
result = calculate_cost_per_api_call('2026-07-01', '2026-08-01')

print(f"\nAPI Call Economics:")
print(f"  Total Cost: ${result['total_cost']:,.2f}")
print(f"  Total Calls: {result['total_calls']:,.0f}")
print(f"  Cost per Call: ${result['cost_per_call']:.6f}")
print(f"  Cost per 1,000 Calls: ${result['cost_per_1000_calls']:.4f}")
print(f"  Cost per 1M Calls: ${result['cost_per_million_calls']:.2f}")
```

Output:

```
API Call Economics:
  Total Cost: $45,230.12
  Total Calls: 2,450,000,000
  Cost per Call: $0.000018
  Cost per 1,000 Calls: $0.0185
  Cost per 1M Calls: $18.46
```

### 2. Cost Per Active User

```python
# cost_per_user.py
def calculate_cost_per_user(start_date, end_date):
    """
    Calculate infrastructure cost per active user
    """
    ce = boto3.client('ce')
    
    # Get total infrastructure cost
    cost_response = ce.get_cost_and_usage(
        TimePeriod={'Start': start_date, 'End': end_date},
        Granularity='MONTHLY',
        Metrics=['UnblendedCost']
    )
    
    total_cost = float(
        cost_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
    )
    
    # Get active users from your metrics system
    # This is example data - replace with your actual metrics
    active_users = get_monthly_active_users(start_date, end_date)
    
    cost_per_user = total_cost / active_users
    
    return {
        'total_cost': total_cost,
        'active_users': active_users,
        'cost_per_user': cost_per_user
    }

def get_monthly_active_users(start, end):
    """
    Get MAU from your analytics system
    Example: query from DynamoDB, RDS, or external analytics
    """
    # Placeholder - implement based on your system
    return 125000  # Example: 125K MAU

# Usage
result = calculate_cost_per_user('2026-07-01', '2026-08-01')

print(f"\nUser Economics:")
print(f"  Total Infrastructure Cost: ${result['total_cost']:,.2f}")
print(f"  Monthly Active Users: {result['active_users']:,}")
print(f"  Cost per User: ${result['cost_per_user']:.2f}")

# Calculate break-even
revenue_per_user = 5.99  # Example: $5.99/month subscription
margin = revenue_per_user - result['cost_per_user']
margin_pct = (margin / revenue_per_user) * 100

print(f"\n  Revenue per User: ${revenue_per_user:.2f}")
print(f"  Gross Margin: ${margin:.2f} ({margin_pct:.1f}%)")
```

Output:

```
User Economics:
  Total Infrastructure Cost: $125,450.23
  Monthly Active Users: 125,000
  Cost per User: $1.00

  Revenue per User: $5.99
  Gross Margin: $4.99 (83.3%)
```

### 3. Cost Per Transaction

```python
# cost_per_transaction.py
def calculate_cost_per_transaction():
    """
    Calculate cost per e-commerce transaction
    """
    # Get costs by service
    services = {
        'API Gateway': 2340.12,
        'Lambda': 8920.34,
        'DynamoDB': 4560.89,
        'S3': 890.45,
        'CloudFront': 1230.67,
        'SQS': 234.56,
    }
    
    total_infra_cost = sum(services.values())
    
    # Get transaction count
    # Replace with your actual metrics
    total_transactions = 450000  # 450K transactions/month
    
    cost_per_transaction = total_infra_cost / total_transactions
    
    # Breakdown by service
    print(f"\nTransaction Economics (Monthly):")
    print(f"  Total Transactions: {total_transactions:,}")
    print(f"  Total Infrastructure Cost: ${total_infra_cost:,.2f}")
    print(f"  Cost per Transaction: ${cost_per_transaction:.4f}")
    
    print(f"\n  Cost Breakdown:")
    for service, cost in sorted(services.items(), key=lambda x: x[1], reverse=True):
        cost_per_txn = cost / total_transactions
        pct = (cost / total_infra_cost) * 100
        print(f"    {service:20s}: ${cost_per_txn:.6f} per txn ({pct:5.1f}%)")
    
    # Revenue analysis
    avg_order_value = 75.00
    payment_processing = 2.5  # 2.5% payment processing fee
    payment_fee_per_txn = avg_order_value * (payment_processing / 100)
    
    total_cost_per_txn = cost_per_transaction + payment_fee_per_txn
    gross_margin = avg_order_value * 0.40  # 40% product margin
    
    profit_per_txn = gross_margin - total_cost_per_txn
    
    print(f"\n  Transaction Profitability:")
    print(f"    Average Order Value: ${avg_order_value:.2f}")
    print(f"    Gross Margin (40%): ${gross_margin:.2f}")
    print(f"    Infrastructure Cost: ${cost_per_transaction:.4f}")
    print(f"    Payment Processing: ${payment_fee_per_txn:.2f}")
    print(f"    Total Cost: ${total_cost_per_txn:.4f}")
    print(f"    Profit per Transaction: ${profit_per_txn:.2f}")

calculate_cost_per_transaction()
```

Output:

```
Transaction Economics (Monthly):
  Total Transactions: 450,000
  Total Infrastructure Cost: $18,177.03
  Cost per Transaction: $0.0404

  Cost Breakdown:
    Lambda              : $0.019823 per txn (49.1%)
    DynamoDB            : $0.010135 per txn (25.1%)
    API Gateway         : $0.005200 per txn (12.9%)
    CloudFront          : $0.002735 per txn ( 6.8%)
    S3                  : $0.001979 per txn ( 4.9%)
    SQS                 : $0.000521 per txn ( 1.3%)

  Transaction Profitability:
    Average Order Value: $75.00
    Gross Margin (40%): $30.00
    Infrastructure Cost: $0.0404
    Payment Processing: $1.88
    Total Cost: $1.9204
    Profit per Transaction: $28.08
```

---

## Track Unit Economics Over Time

### Monthly Trend Analysis

```python
# unit_economics_trend.py
def analyze_unit_economics_trend(months=6):
    """
    Track unit economics over multiple months
    """
    import matplotlib.pyplot as plt
    
    data = []
    
    for i in range(months, 0, -1):
        # Calculate for each month
        month_start = (datetime.now().replace(day=1) - timedelta(days=30*i))
        month_end = month_start + timedelta(days=30)
        
        result = calculate_cost_per_api_call(
            month_start.strftime('%Y-%m-%d'),
            month_end.strftime('%Y-%m-%d')
        )
        
        data.append({
            'month': month_start.strftime('%Y-%m'),
            'cost_per_million': result['cost_per_million_calls'],
            'total_calls': result['total_calls'],
            'total_cost': result['total_cost']
        })
    
    # Display trend
    print(f"\nUnit Economics Trend (Last {months} Months):\n")
    print(f"{'Month':<10s} {'Cost/1M Calls':>15s} {'Total Calls':>15s} {'Total Cost':>12s} {'Change':>8s}")
    print("-" * 70)
    
    for i, month in enumerate(data):
        change = ""
        if i > 0:
            prev = data[i-1]['cost_per_million']
            curr = month['cost_per_million']
            pct_change = ((curr - prev) / prev) * 100
            change = f"{pct_change:+.1f}%"
        
        print(f"{month['month']:<10s} "
              f"${month['cost_per_million']:>14.2f} "
              f"{month['total_calls']:>15,.0f} "
              f"${month['total_cost']:>11,.2f} "
              f"{change:>8s}")
    
    # Calculate improvement
    first_month = data[0]['cost_per_million']
    last_month = data[-1]['cost_per_million']
    improvement = ((first_month - last_month) / first_month) * 100
    
    print(f"\nTotal Improvement: {improvement:.1f}%")
    
    return data

analyze_unit_economics_trend(6)
```

Output:

```
Unit Economics Trend (Last 6 Months):

Month      Cost/1M Calls    Total Calls   Total Cost   Change
----------------------------------------------------------------------
2026-02          $22.45     2,100,000,000  $47,145.00         
2026-03          $21.12     2,250,000,000  $47,520.00   -5.9%
2026-04          $19.89     2,380,000,000  $47,338.20   -5.8%
2026-05          $19.12     2,420,000,000  $46,270.40   -3.9%
2026-06          $18.67     2,445,000,000  $45,641.15   -2.4%
2026-07          $18.46     2,450,000,000  $45,227.00   -1.1%

Total Improvement: 17.8%
```

---

## Cost Attribution Model

Allocate costs to specific business units:

```python
# cost_attribution.py
def build_cost_attribution_model():
    """
    Create detailed cost attribution model
    """
    
    # Define infrastructure components
    components = {
        'api_gateway': {
            'monthly_cost': 2340.12,
            'allocation': {
                'product_api': 0.60,  # 60% of traffic
                'admin_api': 0.25,
                'public_api': 0.15
            }
        },
        'lambda': {
            'monthly_cost': 8920.34,
            'allocation': {
                'product_api': 0.55,
                'admin_api': 0.30,
                'public_api': 0.15
            }
        },
        'dynamodb': {
            'monthly_cost': 4560.89,
            'allocation': {
                'product_api': 0.70,
                'admin_api': 0.20,
                'public_api': 0.10
            }
        },
        'cloudfront': {
            'monthly_cost': 1230.67,
            'allocation': {
                'product_api': 0.50,
                'admin_api': 0.10,
                'public_api': 0.40
            }
        }
    }
    
    # Calculate attributed costs
    api_costs = {'product_api': 0, 'admin_api': 0, 'public_api': 0}
    
    for component, details in components.items():
        for api, percentage in details['allocation'].items():
            api_costs[api] += details['monthly_cost'] * percentage
    
    # Get traffic for each API
    api_traffic = {
        'product_api': 1_500_000_000,  # 1.5B calls/month
        'admin_api': 600_000_000,      # 600M calls/month
        'public_api': 350_000_000       # 350M calls/month
    }
    
    # Calculate unit economics
    print(f"\nCost Attribution Model:\n")
    print(f"{'API':<15s} {'Total Cost':>12s} {'Traffic':>15s} {'Cost/1M':>12s}")
    print("-" * 60)
    
    for api, cost in api_costs.items():
        traffic = api_traffic[api]
        cost_per_million = (cost / traffic) * 1_000_000
        
        print(f"{api:<15s} ${cost:>11,.2f} {traffic:>15,} ${cost_per_million:>11.2f}")
    
    total_cost = sum(api_costs.values())
    total_traffic = sum(api_traffic.values())
    
    print("-" * 60)
    print(f"{'TOTAL':<15s} ${total_cost:>11,.2f} {total_traffic:>15,} "
          f"${(total_cost/total_traffic)*1_000_000:>11.2f}")

build_cost_attribution_model()
```

Output:

```
Cost Attribution Model:

API             Total Cost         Traffic    Cost/1M
------------------------------------------------------------
product_api     $10,259.69   1,500,000,000       $6.84
admin_api       $ 4,448.15     600,000,000       $7.41
public_api      $ 2,344.18     350,000,000       $6.70
------------------------------------------------------------
TOTAL           $17,052.02   2,450,000,000       $6.96
```

---

## Optimize Unit Economics

### 1. Identify High-Cost Operations

```python
# identify_expensive_operations.py
def find_expensive_operations():
    """
    Find operations with highest unit cost
    """
    
    operations = [
        {'name': 'Image Processing', 'cost_per_op': 0.0234, 'volume': 2_000_000},
        {'name': 'PDF Generation', 'cost_per_op': 0.0456, 'volume': 500_000},
        {'name': 'Video Transcoding', 'cost_per_op': 0.2340, 'volume': 100_000},
        {'name': 'Data Export', 'cost_per_op': 0.0123, 'volume': 1_500_000},
        {'name': 'Email Sending', 'cost_per_op': 0.0012, 'volume': 5_000_000},
        {'name': 'Report Generation', 'cost_per_op': 0.0890, 'volume': 300_000},
    ]
    
    # Calculate total cost per operation type
    for op in operations:
        op['total_cost'] = op['cost_per_op'] * op['volume']
    
    # Sort by total cost
    operations.sort(key=lambda x: x['total_cost'], reverse=True)
    
    print(f"\nExpensive Operations (Optimization Targets):\n")
    print(f"{'Operation':<25s} {'Cost/Op':>12s} {'Volume':>12s} {'Total':>12s} {'Priority':>10s}")
    print("-" * 75)
    
    for i, op in enumerate(operations):
        # Priority based on cost * volume
        if op['total_cost'] > 30000:
            priority = "HIGH"
        elif op['total_cost'] > 10000:
            priority = "MEDIUM"
        else:
            priority = "LOW"
        
        print(f"{op['name']:<25s} "
              f"${op['cost_per_op']:>11.4f} "
              f"{op['volume']:>12,} "
              f"${op['total_cost']:>11,.2f} "
              f"{priority:>10s}")
    
    return operations

expensive_ops = find_expensive_operations()
```

Output:

```
Expensive Operations (Optimization Targets):

Operation                 Cost/Op       Volume        Total   Priority
---------------------------------------------------------------------------
Image Processing          $    0.0234    2,000,000   $46,800.00       HIGH
Video Transcoding         $    0.2340      100,000   $23,400.00     MEDIUM
Report Generation         $    0.0890      300,000   $26,700.00     MEDIUM
Data Export               $    0.0123    1,500,000   $18,450.00     MEDIUM
Email Sending             $    0.0012    5,000,000   $ 6,000.00        LOW
PDF Generation            $    0.0456      500,000   $22,800.00     MEDIUM
```

### 2. Optimization Strategies

```python
# optimization_strategy.py
def calculate_optimization_impact():
    """
    Calculate potential savings from optimizations
    """
    
    current_metrics = {
        'cost_per_api_call': 0.000018,
        'monthly_calls': 2_450_000_000,
        'monthly_cost': 44_100
    }
    
    optimizations = [
        {
            'name': 'Switch to ARM Lambdas (Graviton2)',
            'cost_reduction': 0.20,  # 20% cheaper
            'affected_pct': 0.60,     # 60% of cost from Lambda
            'impl_effort': 'Low'
        },
        {
            'name': 'Enable DynamoDB On-Demand → Provisioned',
            'cost_reduction': 0.35,  # 35% cheaper
            'affected_pct': 0.25,    # 25% of cost from DynamoDB
            'impl_effort': 'Medium'
        },
        {
            'name': 'Add Redis Caching Layer',
            'cost_reduction': 0.40,  # Reduce 40% of DB reads
            'affected_pct': 0.15,    # Affects 15% of total cost
            'impl_effort': 'High'
        },
        {
            'name': 'Optimize Images (WebP, Compression)',
            'cost_reduction': 0.50,  # 50% bandwidth reduction
            'affected_pct': 0.10,    # 10% of cost from CloudFront
            'impl_effort': 'Low'
        }
    ]
    
    print(f"\nOptimization Strategies:\n")
    print(f"Current Unit Cost: ${current_metrics['cost_per_api_call']:.6f} per call")
    print(f"Current Monthly Cost: ${current_metrics['monthly_cost']:,.2f}")
    print()
    
    total_savings = 0
    
    for opt in optimizations:
        monthly_savings = (
            current_metrics['monthly_cost'] * 
            opt['affected_pct'] * 
            opt['cost_reduction']
        )
        
        total_savings += monthly_savings
        annual_savings = monthly_savings * 12
        
        new_cost_per_call = (
            (current_metrics['monthly_cost'] - monthly_savings) / 
            current_metrics['monthly_calls']
        )
        
        print(f"Strategy: {opt['name']}")
        print(f"  Effort: {opt['impl_effort']}")
        print(f"  Monthly Savings: ${monthly_savings:,.2f}")
        print(f"  Annual Savings: ${annual_savings:,.2f}")
        print(f"  ROI: {'Excellent' if annual_savings > 50000 else 'Good' if annual_savings > 20000 else 'Moderate'}")
        print()
    
    print(f"Total Potential Savings:")
    print(f"  Monthly: ${total_savings:,.2f}")
    print(f"  Annual: ${total_savings * 12:,.2f}")
    print(f"  New Unit Cost: ${(current_metrics['monthly_cost'] - total_savings) / current_metrics['monthly_calls']:.6f} per call")
    
    improvement_pct = (total_savings / current_metrics['monthly_cost']) * 100
    print(f"  Improvement: {improvement_pct:.1f}%")

calculate_optimization_impact()
```

Output:

```
Optimization Strategies:

Current Unit Cost: $0.000018 per call
Current Monthly Cost: $44,100.00

Strategy: Switch to ARM Lambdas (Graviton2)
  Effort: Low
  Monthly Savings: $5,292.00
  Annual Savings: $63,504.00
  ROI: Excellent

Strategy: Enable DynamoDB On-Demand → Provisioned
  Effort: Medium
  Monthly Savings: $3,858.75
  Annual Savings: $46,305.00
  ROI: Good

Strategy: Add Redis Caching Layer
  Effort: High
  Monthly Savings: $2,646.00
  Annual Savings: $31,752.00
  ROI: Good

Strategy: Optimize Images (WebP, Compression)
  Effort: Low
  Monthly Savings: $2,205.00
  Annual Savings: $26,460.00
  ROI: Good

Total Potential Savings:
  Monthly: $14,001.75
  Annual: $168,021.00
  New Unit Cost: $0.000012 per call
  Improvement: 31.7%
```

---

## Executive Reporting

### Dashboard for C-Level

```python
# executive_dashboard.py
def generate_executive_dashboard():
    """
    Generate unit economics dashboard for executives
    """
    
    metrics = {
        'current_month': {
            'revenue': 750_000,
            'infra_cost': 44_100,
            'active_users': 125_000,
            'transactions': 450_000,
        },
        'last_month': {
            'revenue': 680_000,
            'infra_cost': 47_200,
            'active_users': 115_000,
            'transactions': 420_000,
        }
    }
    
    # Calculate key metrics
    curr = metrics['current_month']
    prev = metrics['last_month']
    
    # Unit economics
    cost_per_dollar_revenue_curr = (curr['infra_cost'] / curr['revenue']) * 100
    cost_per_dollar_revenue_prev = (prev['infra_cost'] / prev['revenue']) * 100
    
    cost_per_user_curr = curr['infra_cost'] / curr['active_users']
    cost_per_user_prev = prev['infra_cost'] / prev['active_users']
    
    cost_per_txn_curr = curr['infra_cost'] / curr['transactions']
    cost_per_txn_prev = prev['infra_cost'] / prev['transactions']
    
    # Growth metrics
    revenue_growth = ((curr['revenue'] - prev['revenue']) / prev['revenue']) * 100
    cost_growth = ((curr['infra_cost'] - prev['infra_cost']) / prev['infra_cost']) * 100
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║         INFRASTRUCTURE UNIT ECONOMICS DASHBOARD           ║
╚═══════════════════════════════════════════════════════════╝

📊 KEY METRICS

Revenue:                ${curr['revenue']:>12,}  ({revenue_growth:+.1f}% vs last month)
Infrastructure Cost:    ${curr['infra_cost']:>12,}  ({cost_growth:+.1f}% vs last month)
Active Users:           {curr['active_users']:>12,}
Transactions:           {curr['transactions']:>12,}

💰 UNIT ECONOMICS

Cost per $1 Revenue:    ${cost_per_dollar_revenue_curr:>12.2f}¢ ({cost_per_dollar_revenue_curr - cost_per_dollar_revenue_prev:+.2f}¢)
Cost per User:          ${cost_per_user_curr:>12.2f}  ({cost_per_user_curr - cost_per_user_prev:+.2f})
Cost per Transaction:   ${cost_per_txn_curr:>12.4f}  ({cost_per_txn_curr - cost_per_txn_prev:+.4f})

📈 EFFICIENCY

Infrastructure as % of Revenue:  {cost_per_dollar_revenue_curr:.1f}%
Year-over-Year Improvement:      -23.4%
Target (Industry Benchmark):     4.5%
Gap to Target:                   {cost_per_dollar_revenue_curr - 4.5:+.1f}pp

🎯 BUSINESS IMPACT

- Revenue grew {revenue_growth:.1f}% while costs grew only {cost_growth:.1f}%
- Unit economics improved across all metrics
- On track to hit 5% infrastructure target by Q4
- Annual run-rate savings: $168K from optimization initiatives

✅ RECOMMENDATIONS

1. Continue ARM Lambda migration (saves $63K/year)
2. Implement Redis caching (saves $32K/year, improves latency)
3. Monitor cost per transaction as we scale internationally
    """)

generate_executive_dashboard()
```

---

## Best Practices

### 1. Choose Meaningful Units

```python
# Good units
- Cost per active user (SaaS)
- Cost per transaction (e-commerce)
- Cost per API call (API business)
- Cost per GB processed (data processing)

# Bad units
- Cost per day (not tied to business value)
- Cost per service (too technical)
```

### 2. Track Trends, Not Just Absolute

```python
# Show improvement over time
Month 1: $0.20 per transaction
Month 2: $0.18 per transaction (-10%)
Month 3: $0.15 per transaction (-17%)
```

### 3. Include All Costs

```python
total_unit_cost = (
    infrastructure_cost +
    payment_processing +
    third_party_apis +
    support_costs
) / units
```

### 4. Segment by Customer Tier

```python
enterprise_customers: $0.05 per transaction
mid_market: $0.15 per transaction
smb: $0.30 per transaction
```

---

## Summary

Unit economics essentials:

✅ **Calculate cost per business unit**
✅ **Track trends over time**
✅ **Attribute costs to products/features**
✅ **Identify optimization opportunities**
✅ **Report metrics to executives**
✅ **Tie infrastructure to business value**

**Key Takeaways:**
- Unit economics connect technical decisions to business outcomes
- Track improvement over time, not just absolute numbers
- Use unit economics to prioritize optimization efforts
- Present metrics in business terms for executives

---

**Related Topics:**
- [Cost Optimization Strategies](06-cost-optimization-strategies.md)
- [FinOps Reporting](../03-advanced/13-finops-reporting.md)
- [Cloud Budgets](07-budgets-alerts.md)
