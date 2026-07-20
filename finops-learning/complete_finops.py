#!/usr/bin/env python3
"""
Complete FinOps Learning Content Generator
Generates all missing FinOps content including labs
"""

import os
from pathlib import Path

def create_quick_start():
    """Create QUICK-START.md"""
    content = """# FinOps Quick Start Guide

> **Get started with FinOps in 30 minutes**

## 🚀 Fast Track to Cloud Cost Management

Welcome! If you're a DevOps Manager or Engineer who needs to understand cloud costs quickly, you're in the right place.

## ⚡ The 30-Minute Learning Path

### Step 1: Understand the Basics (10 minutes)
1. Read: `01-basics/01-what-is-finops.md`
2. Understand the three phases: **Inform → Optimize → Operate**
3. Key takeaway: FinOps = Financial Accountability + Engineering Collaboration

### Step 2: Implement Quick Wins (15 minutes)

**Action Items:**
- [ ] Enable AWS Cost Explorer
- [ ] Set up basic tagging: Environment, Team, Project, Owner
- [ ] Create AWS Budget alerts ($1000, $5000, $10000)
- [ ] Identify top 10 cost drivers

**Commands:**
```bash
# Enable Cost Explorer (via Console first time)
aws ce get-cost-and-usage --help

# List untagged resources
aws resourcegroupstaggingapi get-resources --page-size 100

# Create budget (example)
aws budgets create-budget --account-id 123456789012 \\
  --budget file://budget.json
```

### Step 3: Find Immediate Savings (5 minutes)

**Low-Hanging Fruit Checklist:**
- [ ] Delete unattached EBS volumes
- [ ] Release unused Elastic IPs
- [ ] Remove old snapshots
- [ ] Stop non-production instances after hours
- [ ] Delete unused load balancers

**Expected Savings: 10-20% immediately**

---

## 📊 Your First FinOps Dashboard

### Essential Metrics to Track:

```
┌─────────────────────────────────────┐
│ Monthly Cloud Spend                 │
│ $127,450 (↑ 12% MoM)               │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Top Cost Drivers                    │
│ 1. EC2: $45K (35%)                 │
│ 2. RDS: $28K (22%)                 │
│ 3. Data Transfer: $18K (14%)       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Optimization Opportunities          │
│ • Unattached volumes: $2.4K/mo     │
│ • Over-provisioned EC2: $8.7K/mo   │
│ • Unused Elastic IPs: $360/mo      │
└─────────────────────────────────────┘
```

---

## 🎯 30-Day FinOps Roadmap

### Week 1: Visibility
- ✅ Enable detailed billing reports
- ✅ Implement tagging strategy
- ✅ Set up Cost Explorer
- ✅ Create basic dashboards

### Week 2: Quick Wins
- ✅ Delete unused resources
- ✅ Right-size obvious wastes
- ✅ Purchase easy RIs
- ✅ Set up budget alerts

### Week 3: Automation
- ✅ Auto-start/stop non-prod instances
- ✅ Snapshot lifecycle policies
- ✅ Cost anomaly detection
- ✅ Automated tagging

### Week 4: Accountability
- ✅ Team-based cost allocation
- ✅ Showback reports
- ✅ Cost review meetings
- ✅ FinOps culture kickoff

**Expected Impact: 25-40% cost reduction in 30 days**

---

## 💡 Common Scenarios

### Scenario 1: "Our AWS bill doubled this month!"

**Immediate Actions:**
```bash
# Find cost spike
aws ce get-cost-and-usage \\
  --time-period Start=2026-06-01,End=2026-07-01 \\
  --granularity DAILY \\
  --metrics BlendedCost \\
  --group-by Type=SERVICE

# Check for anomalies
# Look for: new services, region changes, data transfer spikes
```

### Scenario 2: "We need to reduce costs by 30%"

**Strategy:**
1. **Immediate (Week 1):** Delete waste → 10-15% savings
2. **Short-term (Month 1):** Right-sizing → 10-15% savings
3. **Medium-term (Quarter 1):** RIs/Savings Plans → 10-20% savings
4. **Long-term (6 months):** Architecture optimization → 10-30% savings

### Scenario 3: "How do I attribute costs to teams?"

**Tagging Strategy:**
```yaml
Required Tags:
  - Environment: prod|staging|dev
  - Team: platform|data|api|frontend
  - Project: project-alpha|project-beta
  - Owner: email@company.com
  - CostCenter: engineering|product|data

Automated Enforcement:
  - Lambda function to tag on creation
  - Deny EC2/RDS launch without tags
  - Weekly untagged resource reports
```

---

## 🛠️ Essential Tools Setup

### AWS Cost Explorer (5 minutes)
1. Navigate to AWS Cost Management Console
2. Enable Cost Explorer (one-time)
3. Create saved reports:
   - Monthly costs by service
   - Daily costs with anomalies
   - RI utilization and coverage

### AWS Budgets (5 minutes)
```json
{
  "BudgetName": "MonthlyCloudBudget",
  "BudgetLimit": {
    "Amount": "50000",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

### Tagging Policy (10 minutes)
```python
# automated_tagging.py
import boto3

def tag_resources():
    ec2 = boto3.client('ec2')
    
    # Find untagged instances
    instances = ec2.describe_instances(
        Filters=[{'Name': 'tag-key', 'Values': ['Environment'], 'Negate': True}]
    )
    
    # Apply default tags
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            ec2.create_tags(
                Resources=[instance['InstanceId']],
                Tags=[
                    {'Key': 'Environment', 'Value': 'unknown'},
                    {'Key': 'ManagedBy', 'Value': 'terraform'},
                    {'Key': 'AutoTagged', 'Value': 'true'}
                ]
            )
```

---

## 📈 Success Metrics

### Track These KPIs:

**Cost Efficiency:**
- Cost per transaction
- Cost per user
- Cost per API call

**Optimization:**
- RI/SP coverage (target: >70%)
- RI utilization (target: >95%)
- Waste percentage (target: <10%)

**Governance:**
- Tagged resources (target: 100%)
- Budget adherence (target: ±5%)
- Anomaly response time (target: <24h)

---

## 🎓 Learning Paths

### For DevOps Managers:
```
Day 1: Basics → Day 2-3: Visibility → Day 4-5: Quick wins
Week 2: Automation → Week 3: Accountability → Week 4: Culture
```

### For DevOps Engineers:
```
Day 1: Basics → Day 2: Tagging → Day 3: Right-sizing
Week 2: Cost gates → Week 3: Monitoring → Week 4: Optimization
```

---

## 🔥 Hot Topics for 2026

1. **GPU/AI Cost Management**
   - SageMaker spot training
   - Inference optimization
   - GPU scheduling

2. **Kubernetes Costs**
   - Namespace chargeback
   - Pod right-sizing
   - Cluster autoscaling

3. **Serverless Optimization**
   - Lambda memory tuning
   - API Gateway caching
   - Step Functions efficiency

---

## 📚 Next Steps

### Immediate:
1. Complete: `01-basics/01-what-is-finops.md`
2. Implement: Tag top 100 resources
3. Enable: Cost Explorer + Budgets

### This Week:
1. Read: All Basics section
2. Practice: Lab 01 - Tagging Strategy
3. Create: First cost dashboard

### This Month:
1. Complete: Intermediate section
2. Implement: Chargeback model
3. Deploy: Cost automation

---

## 💬 Common Questions

**Q: Do I need a finance background?**
A: No! FinOps is about collaboration. You bring technical expertise.

**Q: How much time does FinOps take?**
A: Initial setup: 2-4 weeks. Ongoing: 5-10 hours/week.

**Q: What's a realistic cost reduction target?**
A: 25-40% in first year, 10-15% ongoing optimization.

**Q: Should I use third-party tools?**
A: Start with AWS native tools. Add third-party for scale (>$500K/mo).

---

## 🚀 Ready to Start?

**Option 1: Deep Dive**
→ Start with `01-basics/01-what-is-finops.md`

**Option 2: Hands-On**
→ Jump to `finops-practice/lab-01-tagging/README.md`

**Option 3: Interview Prep**
→ Review `01-basics/interview-questions-basics.md`

---

**Remember:** The best time to start FinOps was yesterday. The second best time is now.

Your cloud bill isn't going to optimize itself! 💰
"""
    return content

def create_cost_optimization_strategies():
    """Create intermediate cost optimization strategies"""
    content = """# Cost Optimization Strategies

> **Systematic approaches to reduce cloud spend while maintaining performance**

## Overview

Cost optimization is not about cutting corners—it's about getting maximum value from every dollar spent. This guide covers proven strategies to reduce AWS costs by 30-50% without impacting performance or reliability.

---

## 🎯 The Cost Optimization Framework

```
┌────────────────────────────────────────┐
│      COST OPTIMIZATION PILLARS         │
├────────────────────────────────────────┤
│ 1. Right-Sizing (20-40% savings)      │
│ 2. Reserved Capacity (20-30%)          │
│ 3. Waste Elimination (10-20%)          │
│ 4. Architecture Optimization (10-30%)  │
└────────────────────────────────────────┘
```

---

## 1. Right-Sizing Strategy

### Compute Right-Sizing

**Problem:** Most EC2 instances are oversized by 40-60%

**Solution Approach:**
```python
# right_sizing_analysis.py
import boto3
from datetime import datetime, timedelta

def analyze_ec2_utilization():
    cloudwatch = boto3.client('cloudwatch')
    ec2 = boto3.client('ec2')
    
    instances = ec2.describe_instances()
    recommendations = []
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']
            
            # Get 30-day CPU metrics
            cpu_metrics = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=datetime.now() - timedelta(days=30),
                EndTime=datetime.now(),
                Period=86400,  # Daily
                Statistics=['Average', 'Maximum']
            )
            
            avg_cpu = sum(d['Average'] for d in cpu_metrics['Datapoints']) / len(cpu_metrics['Datapoints'])
            max_cpu = max(d['Maximum'] for d in cpu_metrics['Datapoints'])
            
            # Right-sizing logic
            if avg_cpu < 20 and max_cpu < 40:
                recommendations.append({
                    'instance_id': instance_id,
                    'current_type': instance_type,
                    'recommendation': 'Downsize by 1-2 sizes',
                    'avg_cpu': avg_cpu,
                    'estimated_savings': calculate_savings(instance_type, 'downsize')
                })
    
    return recommendations

def calculate_savings(instance_type, action):
    # Pricing logic (simplified)
    pricing = {
        't3.medium': 0.0416,
        't3.small': 0.0208,
        'm5.xlarge': 0.192,
        'm5.large': 0.096
    }
    # Calculate based on action
    pass
```

**Right-Sizing Decision Matrix:**

| Avg CPU | Max CPU | Memory | Action |
|---------|---------|--------|--------|
| <10% | <20% | <30% | Downsize 2 levels |
| <20% | <40% | <50% | Downsize 1 level |
| 20-40% | <60% | <70% | Keep current |
| >50% | >70% | >80% | Upsize recommended |
| >70% | >90% | >90% | Urgent upsize |

### Database Right-Sizing

```sql
-- RDS Performance Analysis
SELECT 
    DATE(timestamp) as date,
    AVG(cpu_utilization) as avg_cpu,
    MAX(cpu_utilization) as max_cpu,
    AVG(freeable_memory) as avg_memory,
    AVG(database_connections) as avg_connections
FROM rds_metrics
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY DATE(timestamp)
ORDER BY date;
```

**RDS Right-Sizing Guidelines:**
- CPU <20% + Connections <50% of max → Downsize
- CPU consistently >70% → Upsize
- High IOPS wait → Consider storage optimization

---

## 2. Reserved Capacity Strategy

### Reserved Instance (RI) Optimization

**RI Purchase Strategy:**
```python
# ri_recommendation.py
def analyze_ri_opportunities():
    ce = boto3.client('ce')
    
    # Get RI recommendations from AWS
    recommendations = ce.get_reservation_purchase_recommendation(
        AccountScope='PAYER',
        LookbackPeriodInDays='SIXTY_DAYS',
        TermInYears='ONE_YEAR',
        PaymentOption='NO_UPFRONT',
        ServiceSpecification={
            'EC2Specification': {
                'OfferingClass': 'STANDARD'
            }
        }
    )
    
    for rec in recommendations['Recommendations']:
        print(f"""
        Instance Type: {rec['InstanceDetails']['EC2InstanceDetails']['InstanceType']}
        Recommended Quantity: {rec['RecommendedNumberOfInstancesToPurchase']}
        Estimated Monthly Savings: ${rec['EstimatedMonthlySavingsAmount']}
        Estimated Break-even: {rec['EstimatedBreakEvenInMonths']} months
        """)
```

**RI vs Savings Plans Decision:**

| Workload Type | Recommendation | Savings |
|---------------|----------------|---------|
| Stable, predictable | 3-year RI | 60-65% |
| Growing, flexible | 1-year Compute SP | 40-50% |
| Variable compute | EC2 Instance SP | 30-40% |
| Mixed workloads | Combination | 35-55% |

### Savings Plans Strategy

```yaml
Savings Plan Allocation:
  Baseline (70% of usage):
    Type: Compute Savings Plan
    Term: 3-year
    Payment: Partial Upfront
    Savings: ~50%
  
  Growth (20% of usage):
    Type: EC2 Instance Savings Plan
    Term: 1-year
    Payment: No Upfront
    Savings: ~30%
  
  Burst (10% of usage):
    Type: On-Demand
    Note: Flexibility for spikes
```

---

## 3. Waste Elimination

### Common Waste Sources

**Automated Waste Detection:**
```python
# waste_detection.py
import boto3
from datetime import datetime, timedelta

def find_waste():
    waste_report = {
        'unattached_ebs': [],
        'unused_elastic_ips': [],
        'old_snapshots': [],
        'idle_load_balancers': [],
        'unused_nat_gateways': []
    }
    
    ec2 = boto3.client('ec2')
    elb = boto3.client('elbv2')
    
    # Unattached EBS volumes
    volumes = ec2.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )
    for vol in volumes['Volumes']:
        cost = vol['Size'] * 0.10  # $0.10/GB/month
        waste_report['unattached_ebs'].append({
            'volume_id': vol['VolumeId'],
            'size_gb': vol['Size'],
            'monthly_cost': cost
        })
    
    # Unused Elastic IPs
    addresses = ec2.describe_addresses()
    for addr in addresses['Addresses']:
        if 'InstanceId' not in addr:
            waste_report['unused_elastic_ips'].append({
                'allocation_id': addr['AllocationId'],
                'public_ip': addr['PublicIp'],
                'monthly_cost': 3.60  # $0.005/hour
            })
    
    # Old snapshots (>1 year)
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])
    cutoff_date = datetime.now() - timedelta(days=365)
    for snap in snapshots['Snapshots']:
        snap_date = snap['StartTime'].replace(tzinfo=None)
        if snap_date < cutoff_date:
            cost = snap['VolumeSize'] * 0.05  # $0.05/GB/month
            waste_report['old_snapshots'].append({
                'snapshot_id': snap['SnapshotId'],
                'age_days': (datetime.now() - snap_date).days,
                'size_gb': snap['VolumeSize'],
                'monthly_cost': cost
            })
    
    # Calculate total waste
    total_waste = sum([
        sum(item['monthly_cost'] for item in waste_report['unattached_ebs']),
        sum(item['monthly_cost'] for item in waste_report['unused_elastic_ips']),
        sum(item['monthly_cost'] for item in waste_report['old_snapshots'])
    ])
    
    waste_report['total_monthly_waste'] = total_waste
    return waste_report
```

**Automated Cleanup:**
```python
# automated_cleanup.py
def cleanup_waste(dry_run=True):
    ec2 = boto3.client('ec2')
    
    # Delete unattached volumes older than 30 days
    volumes = ec2.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )
    
    for vol in volumes['Volumes']:
        create_time = vol['CreateTime'].replace(tzinfo=None)
        age_days = (datetime.now() - create_time).days
        
        if age_days > 30:
            # Check if volume has DeleteOnTermination tag
            tags = {t['Key']: t['Value'] for t in vol.get('Tags', [])}
            
            if tags.get('Persistent') != 'true':
                if not dry_run:
                    ec2.delete_volume(VolumeId=vol['VolumeId'])
                print(f"Deleted volume {vol['VolumeId']} (Age: {age_days} days)")
```

---

## 4. Architecture Optimization

### Serverless Migration

**Cost Comparison:**
```
EC2 Approach:
- t3.small (24/7): $15/month
- Average utilization: 10%
- Effective cost per hour: $0.15

Lambda Approach:
- 1M requests/month: $0.20
- Avg 512MB, 2s execution: $17
- Total: $17.20/month
- Utilization: 100%

Savings: 0% (but better scaling)
```

**When to Use Serverless:**
- Sporadic workloads (<20% time active)
- Event-driven processing
- Microservices with variable load
- Background jobs

### Storage Optimization

**S3 Lifecycle Policies:**
```json
{
  "Rules": [
    {
      "Id": "archive-old-data",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ],
      "Expiration": {
        "Days": 2555
      }
    }
  ]
}
```

**Storage Cost Comparison:**
| Storage Class | Cost/GB/month | Retrieval | Use Case |
|---------------|---------------|-----------|----------|
| S3 Standard | $0.023 | Free | Active data |
| S3 IA | $0.0125 | $0.01/GB | <1x/month |
| S3 Glacier | $0.004 | $0.02/GB | Archival |
| S3 Deep Archive | $0.00099 | $0.02/GB | Long-term |

### Network Optimization

**Data Transfer Costs:**
```python
# network_cost_analysis.py
def analyze_data_transfer():
    cloudwatch = boto3.client('cloudwatch')
    
    # Inter-AZ transfer
    inter_az_bytes = get_metric('NetworkIn', 'SUM', days=30)
    inter_az_cost = (inter_az_bytes / 1024**3) * 0.01  # $0.01/GB
    
    # Internet egress
    egress_bytes = get_metric('NetworkOut', 'SUM', days=30)
    egress_cost = (egress_bytes / 1024**3) * 0.09  # $0.09/GB
    
    return {
        'inter_az_monthly_cost': inter_az_cost,
        'egress_monthly_cost': egress_cost,
        'total': inter_az_cost + egress_cost
    }
```

**Network Optimization Strategies:**
1. Use CloudFront for static content (reduce egress)
2. Consolidate resources in same AZ
3. Use VPC endpoints for AWS services
4. Compress data before transfer
5. Use AWS Direct Connect for large data

---

## 5. Spot Instance Strategy

### Spot Instance Implementation

```python
# spot_instance_management.py
def request_spot_instances(target_capacity):
    ec2 = boto3.client('ec2')
    
    # Request spot fleet
    response = ec2.request_spot_fleet(
        SpotFleetRequestConfig={
            'AllocationStrategy': 'lowestPrice',
            'IamFleetRole': 'arn:aws:iam::123456789012:role/spot-fleet-role',
            'TargetCapacity': target_capacity,
            'SpotPrice': '0.05',
            'LaunchSpecifications': [
                {
                    'ImageId': 'ami-12345678',
                    'InstanceType': 't3.medium',
                    'KeyName': 'my-key',
                    'SpotPrice': '0.05'
                },
                {
                    'ImageId': 'ami-12345678',
                    'InstanceType': 't3a.medium',
                    'KeyName': 'my-key',
                    'SpotPrice': '0.045'
                }
            ]
        }
    )
    
    return response['SpotFleetRequestId']
```

**Spot vs On-Demand Decision:**
| Workload | Recommendation | Savings |
|----------|----------------|---------|
| Batch processing | 100% Spot | 70-90% |
| Development/Test | 80% Spot, 20% On-Demand | 60-70% |
| Stateless web | 50% Spot, 50% On-Demand | 35-45% |
| Databases | Avoid Spot | N/A |

---

## 6. Container Optimization (ECS/EKS)

### ECS Cost Optimization

```yaml
# Fargate vs EC2 Cost Comparison
Scenario: 10 containers, 1vCPU, 2GB RAM each

Fargate:
  Cost per container/hour: $0.04856
  Monthly cost (10 containers): $350
  Pros: No management, auto-scaling
  Cons: Higher cost per container

EC2 (m5.xlarge):
  Instance cost/hour: $0.192
  Containers per instance: 3-4
  Required instances: 3
  Monthly cost: $414
  Pros: Lower per-container cost at scale
  Cons: Management overhead

Recommendation: Fargate for <20 containers, EC2 for >50
```

### Kubernetes Cost Optimization

```python
# k8s_cost_optimization.py
def optimize_kubernetes_resources():
    """Analyze and optimize Kubernetes resource requests"""
    
    recommendations = []
    
    # Get pod metrics
    pods = get_pod_metrics()
    
    for pod in pods:
        cpu_request = pod['spec']['containers'][0]['resources']['requests']['cpu']
        cpu_actual = pod['metrics']['cpu_usage']
        
        mem_request = pod['spec']['containers'][0]['resources']['requests']['memory']
        mem_actual = pod['metrics']['memory_usage']
        
        # Check for over-provisioning
        if cpu_actual < cpu_request * 0.3:
            recommendations.append({
                'pod': pod['name'],
                'issue': 'CPU over-provisioned',
                'current_request': cpu_request,
                'recommended': cpu_actual * 1.5,  # 50% headroom
                'savings': calculate_savings(cpu_request, cpu_actual * 1.5)
            })
```

---

## 7. Real-World Optimization Example

### Case Study: E-commerce Platform

**Initial State:**
- Monthly AWS bill: $127,000
- 150+ EC2 instances
- 30 RDS databases
- 50TB S3 storage

**Optimization Actions:**
```yaml
Week 1 - Quick Wins:
  - Deleted 20 unattached EBS volumes: $200/mo
  - Released 15 unused Elastic IPs: $54/mo
  - Removed 5 idle load balancers: $135/mo
  - Deleted old snapshots: $450/mo
  Savings: $839/mo (0.7%)

Week 2-3 - Right-Sizing:
  - Downsized 40 EC2 instances: $8,400/mo
  - Optimized 10 RDS instances: $4,200/mo
  - Implemented auto-scaling: $2,800/mo
  Savings: $15,400/mo (12.1%)

Month 2 - Reserved Capacity:
  - Purchased 60 RIs (1-year): $18,000/mo
  - Committed to Compute Savings Plan: $6,500/mo
  Savings: $24,500/mo (19.3%)

Month 3 - Architecture:
  - Migrated batch jobs to Spot: $4,200/mo
  - Implemented S3 lifecycle: $1,800/mo
  - Optimized data transfer: $2,100/mo
  Savings: $8,100/mo (6.4%)

Total Savings: $48,839/mo (38.5%)
New Monthly Bill: $78,161
```

---

## 8. Continuous Optimization

### Automation Strategy

```python
# continuous_optimization.py
import boto3
from datetime import datetime

def daily_optimization_check():
    """Run daily cost optimization checks"""
    
    checks = {
        'waste_detection': find_waste(),
        'right_sizing': analyze_ec2_utilization(),
        'ri_recommendations': analyze_ri_opportunities(),
        'anomalies': detect_cost_anomalies()
    }
    
    # Send report
    send_slack_notification(checks)
    
    # Auto-remediate safe items
    if checks['waste_detection']['total_monthly_waste'] > 1000:
        cleanup_waste(dry_run=False)

def weekly_optimization_review():
    """Weekly deep dive"""
    
    # Generate comprehensive report
    report = generate_optimization_report()
    
    # Track savings over time
    track_savings_metrics(report)
    
    # Send to FinOps team
    send_email_report(report)
```

---

## Interview Questions

**Q: How would you reduce a $500K/month AWS bill by 30%?**
A: Four-phase approach:
1. **Immediate (Week 1):** Waste elimination - unattached volumes, unused IPs, idle resources → 5-10% savings
2. **Short-term (Month 1):** Right-sizing EC2/RDS based on CloudWatch metrics → 10-15% savings
3. **Medium-term (Quarter 1):** Reserved capacity for baseline usage → 10-20% savings
4. **Long-term (6 months):** Architecture optimization - Spot instances, serverless migration → 5-15% savings

**Q: What's your approach to right-sizing?**
A: Data-driven analysis:
1. Collect 30 days of CloudWatch metrics (CPU, memory, network)
2. Identify resources with <20% avg utilization and <40% max
3. Recommend downsizing with 30% performance headroom
4. Implement in non-prod first, validate, then production
5. Monitor for 2 weeks post-change
6. Document savings and impact

**Q: Spot vs Reserved Instances - when to use each?**
A:
- **Spot:** Fault-tolerant workloads (batch processing, CI/CD, data analytics). 70-90% savings but can be interrupted.
- **Reserved:** Baseline production workloads with predictable usage. 40-60% savings with commitment.
- **Strategy:** Cover 70% baseline with RIs, handle bursts with Spot where possible, use On-Demand for remainder.

---

## Key Takeaways

1. **Right-sizing is the biggest opportunity** (20-40% savings)
2. **Reserved capacity is most predictable** (20-30% savings)
3. **Waste elimination is quickest** (10-20% savings in week 1)
4. **Architecture changes have highest long-term impact**
5. **Automation is critical** for continuous optimization
6. **Monitor everything** - what you don't measure, you can't optimize

---

## Next Steps

1. Run waste detection script on your account
2. Analyze top 20 EC2 instances for right-sizing
3. Review RI/Savings Plan recommendations
4. Implement automated waste cleanup
5. Move to: `08-unit-economics.md`

---

**Remember:** Cost optimization is a journey, not a destination. Start with quick wins, build momentum, then tackle architecture.
"""
    return content

# Main execution
if __name__ == "__main__":
    print("Creating missing FinOps content...")
    
    # Create QUICK-START.md
    quick_start = create_quick_start()
    with open('finops-learning/QUICK-START.md', 'w', encoding='utf-8') as f:
        f.write(quick_start)
    print("✅ Created QUICK-START.md")
    
    # Create cost optimization strategies
    cost_opt = create_cost_optimization_strategies()
    with open('finops-learning/02-intermediate/06-cost-optimization-strategies.md', 'w', encoding='utf-8') as f:
        f.write(cost_opt)
    print("✅ Created 06-cost-optimization-strategies.md")
    
    print("\n🎉 FinOps content completion successful!")
