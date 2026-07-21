#!/usr/bin/env python3
"""
Complete all pending FinOps content files
Generates comprehensive content for all placeholder files
"""

import os

# File templates for completion
files_to_complete = {
    "finops-learning/02-intermediate/09-ri-savings-plans.md": """# Reserved Instances & Savings Plans Strategy

> **Master the art of commitment-based discounts for maximum cloud savings**

---

## 📖 Overview

Reserved Instances (RIs) and Savings Plans (SPs) are **commitment-based discount programs** that can reduce AWS compute costs by **40-72%** compared to on-demand pricing.

**Key Concept:** You commit to using a certain amount of compute capacity (RIs) or spending (SPs) for 1 or 3 years in exchange for significant discounts.

### Quick Comparison

| Feature | Reserved Instances | Savings Plans |
|---------|-------------------|---------------|
| **Discount** | Up to 72% | Up to 72% |
| **Flexibility** | Limited | High |
| **Commitment** | Specific instance | $/hour spend |
| **Coverage** | EC2, RDS, ElastiCache, etc. | EC2, Lambda, Fargate |
| **Management** | More complex | Simpler |

---

## 🎯 Reserved Instances (RIs) Deep Dive

### What Are Reserved Instances?

Reserved Instances provide **capacity reservation** combined with billing discounts.

**Types of RIs:**

1. **Standard RIs**
   - 40-72% discount
   - No instance changes allowed
   - Can modify AZ, scope, network
   - Best for predictable workloads

2. **Convertible RIs**
   - 31-54% discount
   - Can change instance family
   - More flexibility
   - Better for evolving needs

3. **Scheduled RIs**
   - For recurring schedules
   - Specific time windows
   - Less common

### Payment Options

```yaml
All Upfront:
  - Highest discount (up to 72%)
  - Pay entire amount upfront
  - No monthly charges
  - Best ROI
  
Partial Upfront:
  - Medium discount (up to 59%)
  - Pay ~50% upfront
  - Monthly charges for remainder
  - Balanced approach
  
No Upfront:
  - Lowest discount (up to 43%)
  - No upfront payment
  - Monthly charges
  - Cash flow friendly
```

### RI Scope Types

**Regional RIs:**
- Apply across all AZs in region
- Instance size flexibility
- More flexible
- Recommended for most cases

**Zonal RIs:**
- Specific to one AZ
- Capacity reservation
- Less flexible
- Use for critical workloads

---

## 💰 Savings Plans Deep Dive

### What Are Savings Plans?

Savings Plans offer flexible pricing in exchange for **consistent usage commitment** measured in $/hour.

**Types of Savings Plans:**

1. **Compute Savings Plans**
   - Most flexible option
   - Apply to EC2, Lambda, Fargate
   - Any region, instance family, OS, tenancy
   - Up to 66% savings
   
2. **EC2 Instance Savings Plans**
   - Less flexible
   - Specific instance family in region
   - Can change size, OS, tenancy
   - Up to 72% savings
   
3. **SageMaker Savings Plans**
   - For ML workloads
   - Up to 64% savings

### How Savings Plans Work

```python
# Example: $10/hour commitment
Commitment: $10/hour = $7,300/month

Hour 1: Actual usage = $12/hour
  - $10 covered by SP (discounted)
  - $2 charged at on-demand rates
  
Hour 2: Actual usage = $8/hour
  - $8 covered by SP (discounted)
  - $2 commitment unused (wasted)
  
Goal: Match commitment to baseline usage
```

---

## 📊 RI vs Savings Plans: Which to Choose?

### Decision Matrix

```yaml
Choose RIs When:
  - Predictable instance types
  - Fixed infrastructure
  - Maximum savings needed
  - RDS, ElastiCache, etc.
  
Choose Savings Plans When:
  - Dynamic workloads
  - Multiple instance families
  - Lambda/Fargate usage
  - Prefer simplicity
  
Use Both:
  - RIs for specific databases/cache
  - SPs for compute flexibility
  - Maximum coverage
```

### Real-World Strategy

**Scenario: SaaS Company**
```yaml
Monthly Spend: $100,000

Breakdown:
  - EC2: $60,000 (variable instance types)
  - RDS: $25,000 (2 production databases)
  - Lambda: $10,000
  - Other: $5,000

Optimal Strategy:
  - Compute SP: $30/hour ($21,900/month) for baseline EC2
  - Standard RIs: $18,000/month for RDS databases
  - On-demand: Remaining variable workload
  
Result:
  - Coverage: ~40% of spend
  - Savings: $15,000/month (15%)
  - Flexibility: Maintained for growth
```

---

## 🎯 RI/SP Purchase Strategy

### Step 1: Analyze Historical Usage

```python
# Python script to analyze usage patterns
import boto3
import pandas as pd
from datetime import datetime, timedelta

def analyze_compute_usage(days=90):
    """Analyze 90 days of usage for RI/SP recommendations"""
    
    ce_client = boto3.client('ce')
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': str(start_date),
            'End': str(end_date)
        },
        Granularity='DAILY',
        Metrics=['UsageQuantity', 'BlendedCost'],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'INSTANCE_TYPE'},
            {'Type': 'DIMENSION', 'Key': 'REGION'}
        ],
        Filter={
            'Dimensions': {
                'Key': 'SERVICE',
                'Values': ['Amazon Elastic Compute Cloud - Compute']
            }
        }
    )
    
    # Process data
    usage_data = []
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            usage_data.append({
                'date': result['TimePeriod']['Start'],
                'instance_type': group['Keys'][0],
                'region': group['Keys'][1],
                'hours': float(group['Metrics']['UsageQuantity']['Amount']),
                'cost': float(group['Metrics']['BlendedCost']['Amount'])
            })
    
    df = pd.DataFrame(usage_data)
    
    # Calculate baseline (minimum daily usage)
    baseline = df.groupby(['instance_type', 'region'])['hours'].min()
    
    print("\nBaseline Usage for RI Consideration:")
    print("=" * 70)
    for (instance, region), hours in baseline.items():
        if hours >= 20:  # At least 20 hours/day = good RI candidate
            monthly_hours = hours * 30
            print(f"{instance} in {region}: {hours:.0f} hours/day "
                  f"({monthly_hours:.0f} hours/month)")
    
    return df, baseline
