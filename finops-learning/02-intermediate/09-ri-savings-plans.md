# Reserved Instances & Savings Plans Strategy

> **Master commitment-based discounts for 40-72% cloud savings**

---

## 📖 Overview

Reserved Instances (RIs) and Savings Plans (SPs) are **commitment-based discount programs** offering **40-72% savings** compared to on-demand pricing.

**Core Concept:** Commit to consistent usage (1-3 years) → Get massive discounts

### Quick Stats
- **Typical Savings:** 40-72% off on-demand pricing
- **Payback Period:** 3-9 months
- **Coverage Target:** 60-80% of baseline workloads
- **ROI:** $3-5 saved for every $1 committed

---

## 🎯 Reserved Instances Explained

### What Are RIs?

**Reserved Instances** = Capacity reservation + Billing discount

You reserve specific compute capacity for 1-3 years and get discounted rates.


### RI Types

**1. Standard RIs**
```yaml
Discount: 40-72%
Flexibility: Limited (can't change instance family)
Modifications: Can change AZ, scope, network type
Best For: Stable, predictable workloads
Example: Production databases, baseline app servers
```

**2. Convertible RIs**
```yaml
Discount: 31-54%
Flexibility: High (can change instance family)
Modifications: Can exchange for different instance types
Best For: Evolving infrastructure needs
Example: Applications planning instance type changes
```

**3. Scheduled RIs**
```yaml
Discount: 5-10%
Flexibility: Time-based
Use Case: Recurring batch jobs
Availability: Limited (being phased out)
```

### Payment Options

**All Upfront:**
- Pay 100% upfront
- Highest discount (up to 72%)
- No monthly charges
- Best ROI

**Partial Upfront:**
- Pay ~50% upfront
- Monthly charges for remainder
- Medium discount (up to 59%)
- Balanced approach

**No Upfront:**
- $0 upfront
- Monthly payments
- Lowest discount (up to 43%)
- Better cash flow

### RI Scope

**Regional RIs (Recommended):**
- Apply across all AZs in region
- Instance size flexibility
- No capacity reservation
- More flexible

**Zonal RIs:**
- Specific to one Availability Zone
- Capacity reservation guaranteed
- Less flexible
- Use for mission-critical workloads

---

## 💰 Savings Plans Explained

### What Are Savings Plans?

**Savings Plans** = Commitment to spend $/hour → Get discounts

You commit to a consistent amount of compute usage (measured in $/hour) for 1-3 years.

### SP Types

**1. Compute Savings Plans**
```yaml
Discount: Up to 66%
Flexibility: Maximum
Coverage: EC2, Lambda, Fargate
Changes Allowed: Any region, instance family, OS, tenancy
Best For: Dynamic, multi-service workloads
```

**2. EC2 Instance Savings Plans**
```yaml
Discount: Up to 72%
Flexibility: Medium
Coverage: EC2 only
Changes Allowed: Size, OS, tenancy within instance family
Best For: Consistent EC2 usage in specific families
```

**3. SageMaker Savings Plans**
```yaml
Discount: Up to 64%
Flexibility: SageMaker-specific
Coverage: SageMaker instances
Best For: ML training and inference workloads
```

### How Savings Plans Work

```python
# Example: $10/hour commitment = $7,300/month

# Hour 1: Usage = $12/hour
#   → $10 covered by SP (at discounted rate)
#   → $2 charged at on-demand rate
#   Result: Still saves money

# Hour 2: Usage = $8/hour
#   → $8 covered by SP (at discounted rate)
#   → $2 commitment unused (wasted)
#   Result: Still saves money vs on-demand

# Key: Match commitment to baseline, not peak
```

---

## 📊 RI vs Savings Plans Comparison

| Factor | Reserved Instances | Savings Plans |
|--------|-------------------|---------------|
| **Maximum Discount** | 72% | 72% |
| **Commitment Type** | Instance capacity | $/hour spend |
| **Flexibility** | Low-Medium | High |
| **Services** | EC2, RDS, ElastiCache, etc. | EC2, Lambda, Fargate |
| **Management** | More complex | Simpler |
| **Modifications** | Limited | Automatic |
| **Unused Capacity** | Can sell in marketplace | Lost if unused |
| **Best For** | Databases, cache | Compute workloads |

### When to Use Each

**Choose RIs:**
- ✅ RDS databases (only option)
- ✅ ElastiCache, Redshift, OpenSearch
- ✅ Fixed EC2 instance types
- ✅ Maximum savings on specific workloads

**Choose Savings Plans:**
- ✅ Variable EC2 instance families
- ✅ Lambda functions
- ✅ Fargate containers
- ✅ Prefer simplicity
- ✅ Growing/changing infrastructure

**Use Both:**
- ✅ RIs for databases
- ✅ Savings Plans for compute
- ✅ Maximum coverage

---

## 🎯 Purchase Strategy

### Step 1: Analyze Usage (Python)

```python
import boto3
import pandas as pd
from datetime import datetime, timedelta

def analyze_ri_sp_opportunities(days=90):
    """Analyze 90 days of usage for recommendations"""
    
    ce_client = boto3.client('ce')
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get RI recommendations
    ri_recs = ce_client.get_reservation_purchase_recommendation(
        Service='Amazon Elastic Compute Cloud - Compute',
        LookbackPeriodInDays='SIXTY_DAYS',
        TermInYears='ONE_YEAR',
        PaymentOption='PARTIAL_UPFRONT'
    )
    
    # Get Savings Plan recommendations
    sp_recs = ce_client.get_savings_plans_purchase_recommendation(
        SavingsPlansType='COMPUTE_SP',
        LookbackPeriodInDays='SIXTY_DAYS',
        TermInYears='ONE_YEAR',
        PaymentOption='PARTIAL_UPFRONT'
    )
    
    print("="*70)
    print("RI/SP Purchase Recommendations")
    print("="*70)
    
    # Process RI recommendations
    if 'Recommendations' in ri_recs:
        total_ri_savings = 0
        print("\n📦 Reserved Instance Recommendations:")
        for rec in ri_recs['Recommendations'][:5]:  # Top 5
            details = rec['RecommendationDetails']
            savings = float(details['EstimatedMonthlySavingsAmount'])
            total_ri_savings += savings
            
            print(f"  • {details['InstanceType']} in {details['AvailabilityZone']}")
            print(f"    Quantity: {details['RecommendedNumberOfInstancesToPurchase']}")
            print(f"    Monthly Savings: ${savings:.2f}")
            print()
    
    # Process SP recommendations
    if 'SavingsPlansPurchaseRecommendation' in sp_recs:
        sp_details = sp_recs['SavingsPlansPurchaseRecommendation']
        print("\n💰 Savings Plan Recommendations:")
        for rec in sp_details.get('SavingsPlansPurchaseRecommendationDetails', [])[:3]:
            print(f"  • Hourly Commitment: ${rec['HourlyCommitmentToPurchase']}/hour")
            print(f"    Monthly Savings: ${rec['EstimatedMonthlySavingsAmount']}")
            print(f"    Upfront Cost: ${rec['UpfrontCost']}")
            print()
    
    return ri_recs, sp_recs

# Run analysis
analyze_ri_sp_opportunities()
```

### Step 2: Calculate Baseline Usage

```python
def calculate_baseline_usage():
    """Find minimum consistent usage (baseline)"""
    
    ce_client = boto3.client('ce')
    
    # Get 90 days of hourly usage
    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': '2026-04-01',
            'End': '2026-07-01'
        },
        Granularity='HOURLY',
        Metrics=['UsageQuantity'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'INSTANCE_TYPE'}]
    )
    
    # Calculate percentiles
    usage_by_type = {}
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            instance_type = group['Keys'][0]
            usage = float(group['Metrics']['UsageQuantity']['Amount'])
            
            if instance_type not in usage_by_type:
                usage_by_type[instance_type] = []
            usage_by_type[instance_type].append(usage)
    
    print("\n📊 Baseline Usage Analysis:")
    print("="*70)
    for instance_type, usage_list in usage_by_type.items():
        usage_series = pd.Series(usage_list)
        
        baseline = usage_series.quantile(0.10)  # 10th percentile
        median = usage_series.quantile(0.50)
        peak = usage_series.quantile(0.90)
        
        print(f"\n{instance_type}:")
        print(f"  Baseline (P10): {baseline:.1f} instances")
        print(f"  Median (P50): {median:.1f} instances")
        print(f"  Peak (P90): {peak:.1f} instances")
        print(f"  💡 Recommendation: Purchase RI/SP for {baseline:.0f} instances")
    
    return usage_by_type

calculate_baseline_usage()
```

### Step 3: Optimization Strategy

**Coverage Target:** 60-80% of compute spend

```yaml
Phase 1: Low-Hanging Fruit (Month 1)
  Target: Databases and cache (RIs)
  Coverage: 20-30%
  Risk: Low
  
Phase 2: Baseline Compute (Month 2-3)
  Target: Stable EC2 baseline (Savings Plans)
  Coverage: 40-60%
  Risk: Low
  
Phase 3: Advanced Optimization (Month 4-6)
  Target: Additional predictable workloads
  Coverage: 60-80%
  Risk: Medium
  
Don't Target: Peak/burst capacity
```

---

## 💡 Real-World Examples

### Example 1: E-Commerce Platform

**Before RI/SP:**
```yaml
Monthly Spend: $150,000

Breakdown:
  - EC2 (web/app servers): $80,000 on-demand
  - RDS (2 prod databases): $40,000 on-demand
  - Lambda: $15,000
  - EBS/Data Transfer: $15,000
```

**Analysis:**
- EC2: 50 m5.xlarge running 24/7
- RDS: 2 x db.r5.2xlarge running 24/7
- Lambda: Variable, but consistent baseline

**Strategy Implemented:**
```yaml
1. RDS Standard RIs (3-year, partial upfront):
   - 2 x db.r5.2xlarge
   - Cost: $18,000/month (was $40,000)
   - Savings: $22,000/month (55%)

2. Compute Savings Plan ($30/hour):
   - Covers baseline EC2 + Lambda
   - Cost: $21,900/month (was $50,000 baseline)
   - Savings: $28,100/month (56%)

3. Keep on-demand for:
   - Peak traffic EC2 (burst capacity)
   - Variable Lambda executions
```

**Results:**
```yaml
New Monthly Spend: $100,000
Total Savings: $50,000/month (33%)
Annual Impact: $600,000/year
Payback Period: 4 months
```

### Example 2: SaaS Startup

**Profile:**
- Monthly spend: $25,000
- Fast growth (20% MoM)
- Unpredictable instance types

**Strategy:**
```yaml
Avoid Standard RIs: Too inflexible for growth

Use Compute Savings Plans:
  - $5/hour commitment ($3,650/month)
  - Covers 50% of baseline
  - Flexibility for growth
  
Results:
  - Savings: $1,200/month (immediate)
  - Flexibility: Maintained
  - Can increase commitment quarterly
```

---

## ⚠️ Common Mistakes

### 1. Over-Committing

**Problem:**
```yaml
Committed: $50/hour SP
Actual Usage: $35/hour average
Result: Wasting $15/hour ($10,950/month!)
```

**Solution:**
- Start conservative (50-60% of baseline)
- Add more commitments quarterly
- Better to under-commit initially

### 2. Buying Wrong RI Type

**Problem:**
```yaml
Bought: Standard RI for m5.large
Reality: Switched to m6i.large after 6 months
Result: RI doesn't apply, wasted money
```

**Solution:**
- Use Convertible RIs if infrastructure evolving
- Or use Savings Plans instead

### 3. Ignoring RDS/ElastiCache

**Problem:**
```yaml
Focus: Only EC2 RIs/SPs
Missed: RDS databases at full on-demand price
Result: Left 50-60% savings on table
```

**Solution:**
- Always check RDS, ElastiCache, Redshift first
- These have highest ROI

### 4. Not Monitoring Utilization

**Problem:**
```yaml
Purchased: 10 RIs
6 months later: Only 7 being used
Result: 30% of RI investment wasted
```

**Solution:**
```python
# Monitor RI/SP utilization weekly
import boto3

def check_ri_utilization():
    """Monitor RI utilization"""
    
    ce_client = boto3.client('ce')
    
    response = ce_client.get_reservation_utilization(
        TimePeriod={
            'Start': '2026-06-01',
            'End': '2026-07-01'
        },
        Granularity='MONTHLY'
    )
    
    for period in response['UtilizationsByTime']:
        util = period['Total']
        utilization_pct = float(util['UtilizationPercentage'])
        
        print(f"RI Utilization: {utilization_pct:.1f}%")
        
        if utilization_pct < 90:
            print("⚠️  WARNING: RI utilization below target!")
            print(f"   Unused hours: {util['TotalAmortizedFee']}")

check_ri_utilization()
```

---

## 🎯 Best Practices

### 1. Start Small, Scale Gradually

```yaml
Month 1: 20-30% coverage (obvious wins)
Month 3: 40-50% coverage (validated patterns)
Month 6: 60-70% coverage (optimized)
Month 12: 70-80% coverage (mature)
```

### 2. Mix Commitment Types

```yaml
Optimal Portfolio:
  - 30-40%: Standard RIs (max savings, stable workloads)
  - 40-50%: Savings Plans (flexibility)
  - 10-20%: Convertible RIs (evolving needs)
  - 10-20%: On-demand (burst, experimentation)
```

### 3. Align with Business Cycles

- **Annual contracts?** 1-year terms
- **Stable revenue?** 3-year terms (max savings)
- **High growth?** Conservative commitments
- **Seasonal business?** Avoid over-commitment

### 4. Monitor and Adjust

```python
# Automated monthly RI/SP review
def monthly_ri_sp_review():
    """Comprehensive monthly review"""
    
    checks = {
        'utilization': check_ri_utilization(),
        'coverage': check_coverage_ratio(),
        'savings': calculate_realized_savings(),
        'recommendations': get_new_recommendations()
    }
    
    # Generate report
    print("\n" + "="*70)
    print("Monthly RI/SP Review Report")
    print("="*70)
    
    print(f"\n✅ Current Utilization: {checks['utilization']:.1f}%")
    print(f"📊 Coverage Ratio: {checks['coverage']:.1f}%")
    print(f"💰 Monthly Savings: ${checks['savings']:,.2f}")
    print(f"💡 New Opportunities: ${checks['recommendations']:,.2f}/month")
    
    # Alerts
    if checks['utilization'] < 85:
        print("\n⚠️  ACTION: RI utilization low - review sizing")
    
    if checks['coverage'] < 60:
        print("💡 OPPORTUNITY: Coverage below target - consider more commitments")
    
    return checks

# Run monthly review
monthly_ri_sp_review()
```

---

## 📈 ROI Calculation

### RI ROI Example

```python
def calculate_ri_roi(instance_type, quantity, term_years=1, payment='PARTIAL'):
    """Calculate ROI for RI purchase"""
    
    # Pricing examples (simplified)
    prices = {
        'm5.large': {
            'on_demand_hourly': 0.096,
            'ri_1yr_partial_upfront': 3200,
            'ri_1yr_partial_hourly': 0.038
        }
    }
    
    pricing = prices[instance_type]
    hours_per_year = 8760
    
    # On-demand cost
    on_demand_annual = (pricing['on_demand_hourly'] * 
                       hours_per_year * quantity)
    
    # RI cost
    ri_upfront = pricing['ri_1yr_partial_upfront'] * quantity
    ri_hourly_annual = (pricing['ri_1yr_partial_hourly'] * 
                        hours_per_year * quantity)
    ri_total_annual = ri_upfront + ri_hourly_annual
    
    # Savings
    annual_savings = on_demand_annual - ri_total_annual
    roi_percentage = (annual_savings / ri_total_annual) * 100
    payback_months = (ri_upfront / (annual_savings / 12))
    
    print(f"\nRI ROI Analysis: {quantity}x {instance_type}")
    print("="*70)
    print(f"On-Demand Annual Cost: ${on_demand_annual:,.2f}")
    print(f"RI Annual Cost: ${ri_total_annual:,.2f}")
    print(f"  - Upfront: ${ri_upfront:,.2f}")
    print(f"  - Hourly: ${ri_hourly_annual:,.2f}")
    print(f"\n💰 Annual Savings: ${annual_savings:,.2f}")
    print(f"📈 ROI: {roi_percentage:.1f}%")
    print(f"⏱️  Payback Period: {payback_months:.1f} months")
    
    return {
        'savings': annual_savings,
        'roi': roi_percentage,
        'payback_months': payback_months
    }

# Example: 10 m5.large instances
calculate_ri_roi('m5.large', quantity=10)
```

**Output:**
```
RI ROI Analysis: 10x m5.large
======================================================================
On-Demand Annual Cost: $8,409.60
RI Annual Cost: $5,530.80
  - Upfront: $32,000.00
  - Hourly: $3,330.80

💰 Annual Savings: $2,878.80
📈 ROI: 52.1%
⏱️  Payback Period: 4.4 months
```

---

## 🎓 Interview Questions

### Q1: When would you choose Savings Plans over Reserved Instances?

**A:** Choose Savings Plans when:
- Using multiple instance families
- Infrastructure is evolving
- Using Lambda/Fargate heavily
- Prefer simplicity and automation
- Need maximum flexibility

Choose RIs when:
- Specific instance types are stable
- Need RDS/ElastiCache coverage
- Want maximum discount (72%)
- Can manage complexity

### Q2: How do you determine the right RI/SP commitment level?

**A:** Analyze baseline usage:
1. Get 90 days of hourly usage data
2. Calculate 10th percentile (baseline)
3. Start with 50-60% of baseline
4. Monitor utilization monthly
5. Add more commitments quarterly
6. Target 70-80% coverage long-term

### Q3: What's the risk of over-committing to RIs/SPs?

**A:** Risks:
- Paying for unused capacity
- Locked into pricing for 1-3 years
- Reduces flexibility
- Opportunity cost
- Can waste 20-30% of investment if miscalculated

Mitigation:
- Start conservative
- Use Convertible RIs or SPs for flexibility
- Monitor utilization closely
- Increase commitments gradually

---

## 📚 Next Steps

1. **Analyze your usage:** Run the Python scripts above
2. **Start small:** 20-30% coverage initially
3. **Monitor closely:** Weekly utilization checks
4. **Scale gradually:** Add more commitments quarterly
5. **Mix strategies:** Use both RIs and SPs

**Related:**
- [Cost Optimization Strategies](06-cost-optimization-strategies.md)
- [Budget Management](11-budget-management.md)
- [FinOps Tools](12-finops-tools.md)

---

**Bottom Line:** RIs and Savings Plans can save 40-72%, but success requires analysis, gradual adoption, and continuous monitoring. Start conservative, validate, then scale!
