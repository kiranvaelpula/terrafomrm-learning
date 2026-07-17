# Chapter 20: AWS Cost Optimization

## Overview

Cost optimization is critical for cloud success. This chapter covers strategies, tools, and best practices for reducing AWS costs without sacrificing performance.

**What You'll Learn**
- AWS Cost Explorer and budgets
- Reserved Instances and Savings Plans
- Spot Instances
- Right-sizing resources
- S3 storage classes and lifecycle
- Cost allocation tags
- FinOps best practices

---

## AWS Cost Explorer

```bash
# Get cost and usage
aws ce get-cost-and-usage \
  --time-period Start=2026-01-01,End=2026-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost UsageQuantity \
  --group-by Type=DIMENSION,Key=SERVICE

# Get cost forecast
aws ce get-cost-forecast \
  --time-period Start=2026-02-01,End=2026-02-28 \
  --metric BLENDED_COST \
  --granularity MONTHLY
```

**Key Metrics:**
- BlendedCost: Average cost
- UnblendedCost: Actual cost
- AmortizedCost: RI/SP amortized

---

## Pricing Models

### 1. On-Demand
- Pay as you go
- No commitment
- Highest cost

### 2. Reserved Instances (RI)
- 1 or 3 year commitment
- Up to 72% savings
- Standard vs Convertible

```bash
# Purchase RI
aws ec2 purchase-reserved-instances-offering \
  --reserved-instances-offering-id abc-123 \
  --instance-count 2
```

**Types:**
- Standard RI: Best savings, least flexibility
- Convertible RI: Change instance type, moderate savings
- Scheduled RI: Recurring schedule

### 3. Savings Plans
- 1 or 3 year commitment
- More flexible than RI
- Up to 72% savings

```bash
# Create Savings Plan
aws savingsplans create-savings-plan \
  --savings-plan-type Compute \
  --commitment 10 \
  --upfront-payment-amount 0
```

**Types:**
- Compute Savings Plans: Most flexible
- EC2 Instance Savings Plans: Best savings

### 4. Spot Instances
- Up to 90% discount
- Can be interrupted
- Good for fault-tolerant workloads

```bash
# Request Spot instances
aws ec2 request-spot-instances \
  --spot-price "0.05" \
  --instance-count 5 \
  --type "one-time" \
  --launch-specification file://spec.json
```

---

## EC2 Cost Optimization

### Right-Sizing

**Analyze utilization:**
```bash
# Get CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
  --start-time 2026-01-01T00:00:00Z \
  --end-time 2026-01-31T23:59:59Z \
  --period 3600 \
  --statistics Average
```

**Recommendations:**
```
CPU < 10% consistently → Downsize
CPU < 40% most time → Consider smaller instance
CPU > 80% regularly → Upsize or add instances
```

### Stop Unused Instances

**Lambda to stop instances:**
```python
import boto3

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    # Stop dev instances at night
    instances = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Environment', 'Values': ['dev']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    instance_ids = []
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])
    
    if instance_ids:
        ec2.stop_instances(InstanceIds=instance_ids)
        print(f"Stopped instances: {instance_ids}")
```

**EventBridge Schedule:**
```bash
# Stop at 7 PM weekdays
aws events put-rule \
  --name stop-dev-instances \
  --schedule-expression "cron(0 19 ? * MON-FRI *)"

# Start at 8 AM weekdays
aws events put-rule \
  --name start-dev-instances \
  --schedule-expression "cron(0 8 ? * MON-FRI *)"
```

### Use Spot for Non-Critical Workloads

**Spot Fleet:**
```json
{
  "AllocationStrategy": "lowestPrice",
  "IamFleetRole": "arn:aws:iam::123456789012:role/aws-ec2-spot-fleet-role",
  "TargetCapacity": 20,
  "LaunchSpecifications": [
    {
      "ImageId": "ami-12345678",
      "InstanceType": "t3.medium",
      "KeyName": "my-key",
      "SpotPrice": "0.05"
    }
  ]
}
```

---

## S3 Cost Optimization

### Storage Classes

| Class | Use Case | Cost | Retrieval |
|-------|----------|------|-----------|
| Standard | Frequent access | Highest | Free |
| Intelligent-Tiering | Unknown patterns | Auto-optimized | Free |
| Standard-IA | Infrequent access | Lower | Fee |
| One Zone-IA | Infrequent, non-critical | Lowest IA | Fee |
| Glacier Instant | Archive, instant | Very low | Fee |
| Glacier Flexible | Archive, minutes-hours | Very low | Fee |
| Glacier Deep Archive | Long-term archive | Lowest | Highest fee |

### Lifecycle Policies

```json
{
  "Rules": [
    {
      "Id": "Move to IA after 30 days",
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
    },
    {
      "Id": "Delete incomplete multipart uploads",
      "Status": "Enabled",
      "AbortIncompleteMultipartUpload": {
        "DaysAfterInitiation": 7
      }
    }
  ]
}
```

```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-bucket \
  --lifecycle-configuration file://lifecycle.json
```

### S3 Intelligent-Tiering

```bash
# Enable Intelligent-Tiering
aws s3api put-bucket-intelligent-tiering-configuration \
  --bucket my-bucket \
  --id EntirePrefix \
  --intelligent-tiering-configuration '{
    "Id": "EntirePrefix",
    "Status": "Enabled",
    "Tierings": [
      {
        "Days": 90,
        "AccessTier": "ARCHIVE_ACCESS"
      },
      {
        "Days": 180,
        "AccessTier": "DEEP_ARCHIVE_ACCESS"
      }
    ]
  }'
```

---

## RDS Cost Optimization

### Right-Size Databases

```bash
# Get CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=mydb \
  --start-time 2026-01-01T00:00:00Z \
  --end-time 2026-01-31T23:59:59Z \
  --period 3600 \
  --statistics Average,Maximum
```

### Aurora Serverless

**For variable workloads:**
```bash
aws rds create-db-cluster \
  --db-cluster-identifier aurora-serverless \
  --engine aurora-mysql \
  --engine-mode serverless \
  --scaling-configuration \
    MinCapacity=2,\
    MaxCapacity=16,\
    AutoPause=true,\
    SecondsUntilAutoPause=300
```

### Stop Dev/Test Databases

```python
# Lambda to stop RDS instances
def lambda_handler(event, context):
    rds = boto3.client('rds')
    
    # Get dev databases
    response = rds.describe_db_instances()
    
    for db in response['DBInstances']:
        tags = rds.list_tags_for_resource(
            ResourceName=db['DBInstanceArn']
        )['TagList']
        
        env = next((tag['Value'] for tag in tags if tag['Key'] == 'Environment'), None)
        
        if env == 'dev' and db['DBInstanceStatus'] == 'available':
            rds.stop_db_instance(DBInstanceIdentifier=db['DBInstanceIdentifier'])
            print(f"Stopped: {db['DBInstanceIdentifier']}")
```

---

## Lambda Cost Optimization

### Memory vs Duration Trade-off

```
Cost = (Duration × Memory) × Request count
```

**Test different memory sizes:**
```python
# Higher memory = more CPU = faster execution
Memory: 128 MB, Duration: 1000ms, Cost: X
Memory: 512 MB, Duration: 250ms, Cost: 0.9X ← Cheaper!
Memory: 3008 MB, Duration: 100ms, Cost: 1.2X
```

### Reduce Package Size

```bash
# Use Lambda Layers
# Before: 50 MB function
# After: 5 MB function + 45 MB layer

# Create layer
zip -r layer.zip python/
aws lambda publish-layer-version \
  --layer-name my-dependencies \
  --zip-file fileb://layer.zip
```

### Use ARM (Graviton2)

```bash
# 20% cost savings with arm64
aws lambda create-function \
  --function-name my-function \
  --runtime python3.9 \
  --architectures arm64 \
  --handler index.handler \
  --role arn:aws:iam::123456789012:role/lambda-role \
  --zip-file fileb://function.zip
```

---

## Data Transfer Costs

### Minimize Cross-Region Transfer

```
Same Region: Free
Different Region: $0.02/GB
Internet Out: $0.09/GB (first 10 TB)
```

**Strategies:**
- Keep resources in same region
- Use CloudFront for static content
- Use VPC endpoints (no internet charges)

### Use VPC Endpoints

```bash
# S3 Gateway Endpoint (FREE)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-123456 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-123456
```

### CloudFront for Static Content

```bash
# Reduce S3 data transfer costs
# S3 → Internet: $0.09/GB
# S3 → CloudFront: $0.00/GB
# CloudFront → Internet: $0.085/GB (cheaper + global)
```

---

## Monitoring and Alerting

### Budgets

```bash
# Create budget
aws budgets create-budget \
  --account-id 123456789012 \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

**budget.json:**
```json
{
  "BudgetName": "Monthly Budget",
  "BudgetLimit": {
    "Amount": "1000",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

**notifications.json:**
```json
[
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "admin@example.com"
      }
    ]
  }
]
```

### Cost Anomaly Detection

```bash
# Create anomaly monitor
aws ce create-anomaly-monitor \
  --anomaly-monitor '{
    "MonitorName": "ServiceMonitor",
    "MonitorType": "DIMENSIONAL",
    "MonitorDimension": "SERVICE"
  }'

# Create subscription
aws ce create-anomaly-subscription \
  --anomaly-subscription '{
    "SubscriptionName": "EmailAlerts",
    "MonitorArnList": ["arn:aws:ce::123456789012:anomalymonitor/abc-123"],
    "Subscribers": [{
      "Type": "EMAIL",
      "Address": "admin@example.com"
    }],
    "Threshold": 100,
    "Frequency": "DAILY"
  }'
```

---

## Cost Allocation Tags

```bash
# Activate cost allocation tags
aws ce create-cost-category-definition \
  --name "Environment" \
  --rules '[{
    "Value": "Production",
    "Rule": {
      "Tags": {
        "Key": "Environment",
        "Values": ["prod", "production"]
      }
    }
  }]'

# Tag resources
aws ec2 create-tags \
  --resources i-1234567890abcdef0 \
  --tags Key=Environment,Value=Production \
         Key=CostCenter,Value=Engineering \
         Key=Project,Value=WebApp
```

---

## FinOps Best Practices

**1. Visibility**
- Enable Cost Explorer
- Use cost allocation tags
- Set up budgets and alerts
- Review Cost and Usage Reports

**2. Accountability**
- Tag all resources
- Assign cost centers
- Create departmental budgets
- Regular cost reviews

**3. Optimization**
- Right-size continuously
- Use Reserved Instances/Savings Plans
- Leverage Spot Instances
- Delete unused resources
- Optimize storage tiers

**4. Automation**
- Auto-stop dev/test resources
- Automated right-sizing recommendations
- Scheduled scaling
- Lifecycle policies

---

## Cost Optimization Checklist

```
□ Enable Cost Explorer
□ Set up budgets and alerts
□ Tag all resources
□ Review unused resources monthly
□ Analyze RI/Savings Plan recommendations
□ Right-size EC2 instances
□ Use Spot for appropriate workloads
□ Implement S3 lifecycle policies
□ Stop dev/test resources off-hours
□ Use VPC endpoints
□ Optimize data transfer
□ Review CloudWatch log retention
□ Delete old snapshots/AMIs
□ Use CloudFront for static content
□ Monitor cost anomalies
```

---

## Summary

Cost optimization requires continuous monitoring and adjustment. Use Reserved Instances and Savings Plans for committed workloads, Spot for flexible workloads, right-size resources, optimize storage tiers, and automate cost management.

**Key Takeaways:**
- Cost Explorer for analysis and forecasting
- Reserved Instances: 1-3 year commitment, up to 72% savings, less flexible
- Savings Plans: 1-3 year commitment, up to 72% savings, more flexible
- Spot Instances: Up to 90% savings, can be interrupted
- Right-size resources based on actual utilization
- Stop/schedule non-production resources
- S3 lifecycle policies for automatic tier transitions
- Use CloudFront and VPC endpoints to reduce data transfer
- Enable Cost Anomaly Detection for unusual spend
- Tag all resources for cost allocation
- Set budgets and alerts
- Implement FinOps culture: visibility, accountability, optimization
- Use AWS Compute Optimizer for right-sizing recommendations
- Lambda memory optimization can reduce costs
- EBS gp3 is cheaper than gp2 with better performance
- Use S3 Intelligent-Tiering for unknown access patterns
- Delete unused snapshots, AMIs, and EBS volumes
- Review and act on Trusted Advisor recommendations monthly

**Cost Optimization Framework:**
```
1. Visibility
   - Enable Cost Explorer
   - Tag all resources
   - Set up cost allocation

2. Accountability  
   - Assign cost centers
   - Create budgets per team/project
   - Regular cost reviews

3. Optimization
   - Right-size continuously
   - Use commitment discounts
   - Automate resource scheduling
   - Optimize storage tiers

4. Automation
   - Auto-stop dev/test
   - Automated snapshots and cleanups
   - Cost anomaly alerts
   - Scheduled scaling
```

**Real-World Cost Savings Example:**
```
Before optimization:
- 50 × t3.large on-demand: $3,000/month
- 5 TB S3 Standard: $115/month
- 10 × db.r5.large RDS: $1,740/month
- Data transfer: $500/month
Total: $5,355/month

After optimization:
- 20 × t3.large Reserved (baseline): $880/month
- 30 × t3.large Spot (variable): $270/month
- 5 TB S3 Intelligent-Tiering: $90/month
- 10 × db.r5.large Reserved: $1,044/month
- VPC endpoints + CloudFront: $200/month
Total: $2,484/month

Savings: $2,871/month (54% reduction!)
Annual savings: $34,452
```

**Next Chapter:** [21-multi-region.md](./21-multi-region.md)



---

## AWS Compute Optimizer

**Enable Compute Optimizer:**
```bash
# Enable for organization
aws compute-optimizer update-enrollment-status \
  --status Active \
  --include-member-accounts

# Get EC2 recommendations
aws compute-optimizer get-ec2-instance-recommendations \
  --instance-arns arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0

# Get Auto Scaling group recommendations
aws compute-optimizer get-auto-scaling-group-recommendations \
  --auto-scaling-group-arns arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:abc:autoScalingGroupName/my-asg

# Get Lambda recommendations
aws compute-optimizer get-lambda-function-recommendations \
  --function-arns arn:aws:lambda:us-east-1:123456789012:function:my-function
```

**Python Script to Apply Recommendations:**
```python
import boto3
import json

compute_optimizer = boto3.client('compute-optimizer')
ec2 = boto3.client('ec2')

def get_and_apply_recommendations():
    """Get Compute Optimizer recommendations and apply them"""
    
    # Get EC2 recommendations
    response = compute_optimizer.get_ec2_instance-recommendations(
        maxResults=100
    )
    
    savings = 0
    actions = []
    
    for recommendation in response['instanceRecommendations']:
        instance_arn = recommendation['instanceArn']
        instance_id = instance_arn.split('/')[-1]
        current_type = recommendation['currentInstanceType']
        finding = recommendation['finding']
        
        if finding == 'Overprovisioned':
            # Get recommended instance type
            options = recommendation['recommendationOptions']
            best_option = options[0]  # First option is usually best
            
            recommended_type = best_option['instanceType']
            estimated_savings = best_option['estimatedMonthlySavings']['value']
            
            if estimated_savings > 10:  # Only if savings > $10/month
                savings += estimated_savings
                actions.append({
                    'instance_id': instance_id,
                    'current': current_type,
                    'recommended': recommended_type,
                    'savings': estimated_savings
                })
        
        elif finding == 'Underprovisioned':
            print(f"Instance {instance_id} is underprovisioned - manual review needed")
    
    # Print recommendations
    print(f"\nTotal potential savings: ${savings:.2f}/month")
    print(f"Number of instances to optimize: {len(actions)}\n")
    
    for action in actions:
        print(f"Instance: {action['instance_id']}")
        print(f"  Current: {action['current']}")
        print(f"  Recommended: {action['recommended']}")
        print(f"  Monthly savings: ${action['savings']:.2f}")
        print()
    
    # Optional: Auto-apply (use with caution!)
    # for action in actions:
    #     modify_instance_type(action['instance_id'], action['recommended'])
    
    return actions

def modify_instance_type(instance_id, new_type):
    """Modify instance type (requires stop/start)"""
    
    # Stop instance
    ec2.stop_instances(InstanceIds=[instance_id])
    waiter = ec2.get_waiter('instance_stopped')
    waiter.wait(InstanceIds=[instance_id])
    
    # Modify instance type
    ec2.modify_instance_attribute(
        InstanceId=instance_id,
        InstanceType={'Value': new_type}
    )
    
    # Start instance
    ec2.start_instances(InstanceIds=[instance_id])
    
    print(f"Modified {instance_id} to {new_type}")

if __name__ == '__main__':
    get_and_apply_recommendations()
```

---

## Trusted Advisor

**Programmatic Access:**
```python
import boto3

support = boto3.client('support', region_name='us-east-1')

def get_trusted_advisor_recommendations():
    """Get Trusted Advisor cost optimization checks"""
    
    # Get all checks
    response = support.describe_trusted_advisor_checks(language='en')
    
    cost_checks = [
        check for check in response['checks']
        if check['category'] == 'cost_optimizing'
    ]
    
    results = {}
    
    for check in cost_checks:
        check_id = check['id']
        check_name = check['name']
        
        # Get check result
        result = support.describe_trusted_advisor_check_result(
            checkId=check_id,
            language='en'
        )
        
        status = result['result']['status']
        flagged_resources = len(result['result'].get('flaggedResources', []))
        
        if flagged_resources > 0:
            results[check_name] = {
                'status': status,
                'flagged_resources': flagged_resources,
                'description': check['description']
            }
    
    return results

# Get recommendations
recommendations = get_trusted_advisor_recommendations()

for check_name, data in recommendations.items():
    print(f"\n{check_name}")
    print(f"Status: {data['status']}")
    print(f"Flagged resources: {data['flagged_resources']}")
    print(f"Description: {data['description']}")
```

**Common Trusted Advisor Checks:**
1. Low Utilization Amazon EC2 Instances
2. Underutilized Amazon EBS Volumes
3. Unassociated Elastic IP Addresses
4. Idle Load Balancers
5. Amazon RDS Idle DB Instances
6. Amazon Route 53 Latency Resource Record Sets

---

## Advanced Cost Allocation

**Cost Categories:**
```python
import boto3

ce = boto3.client('ce')

# Create cost category
response = ce.create_cost_category_definition(
    Name='BusinessUnit',
    RuleVersion='CostCategoryExpression.v1',
    Rules=[
        {
            'Value': 'Engineering',
            'Rule': {
                'Tags': {
                    'Key': 'Department',
                    'Values': ['Engineering', 'Dev', 'DevOps']
                }
            }
        },
        {
            'Value': 'Sales',
            'Rule': {
                'Tags': {
                    'Key': 'Department',
                    'Values': ['Sales', 'Marketing']
                }
            }
        },
        {
            'Value': 'Operations',
            'Rule': {
                'Tags': {
                    'Key': 'Department',
                    'Values': ['Ops', 'IT', 'Support']
                }
            }
        }
    ],
    DefaultValue='Other'
)

# Query costs by category
response = ce.get_cost_and_usage(
    TimePeriod={
        'Start': '2026-01-01',
        'End': '2026-01-31'
    },
    Granularity='MONTHLY',
    Metrics=['BlendedCost'],
    GroupBy=[
        {
            'Type': 'COST_CATEGORY',
            'Key': 'BusinessUnit'
        }
    ]
)

for group in response['ResultsByTime'][0]['Groups']:
    category = group['Keys'][0]
    cost = group['Metrics']['BlendedCost']['Amount']
    print(f"{category}: ${float(cost):.2f}")
```

**Split Costs by Team:**
```python
def generate_team_chargeback_report(month):
    """Generate monthly chargeback report per team"""
    
    ce = boto3.client('ce')
    
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': f'{month}-01',
            'End': f'{month}-31'
        },
        Granularity='MONTHLY',
        Metrics=['BlendedCost', 'UnblendedCost', 'UsageQuantity'],
        GroupBy=[
            {'Type': 'TAG', 'Key': 'Team'},
            {'Type': 'SERVICE'}
        ]
    )
    
    team_costs = {}
    
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            team = group['Keys'][0].split('$')[1]  # Extract team name
            service = group['Keys'][1]
            cost = float(group['Metrics']['BlendedCost']['Amount'])
            
            if team not in team_costs:
                team_costs[team] = {}
            
            if service not in team_costs[team]:
                team_costs[team][service] = 0
            
            team_costs[team][service] += cost
    
    # Generate report
    print(f"\nCost Chargeback Report - {month}")
    print("=" * 60)
    
    for team, services in sorted(team_costs.items()):
        total = sum(services.values())
        print(f"\n{team}: ${total:.2f}")
        
        for service, cost in sorted(services.items(), key=lambda x: x[1], reverse=True):
            if cost > 1:  # Only show services > $1
                print(f"  {service:40} ${cost:>10.2f}")
    
    return team_costs
```

---

## Automated Cost Optimization

**Lambda Function for Unused Resource Cleanup:**
```python
import boto3
from datetime import datetime, timedelta

ec2 = boto3.client('ec2')
rds = boto3.client('rds')
elb = boto3.client('elbv2')

def lambda_handler(event, context):
    """
    Automated cleanup of unused resources
    Runs daily via EventBridge
    """
    
    savings = 0
    
    # 1. Delete unattached EBS volumes
    savings += cleanup_unattached_volumes()
    
    # 2. Delete old snapshots
    savings += cleanup_old_snapshots()
    
    # 3. Release unassociated Elastic IPs
    savings += cleanup_elastic_ips()
    
    # 4. Delete unused load balancers
    savings += cleanup_idle_load_balancers()
    
    # 5. Stop idle RDS instances (dev/test only)
    savings += stop_idle_rds_instances()
    
    # Send summary
    send_cleanup_summary(savings)
    
    return {
        'statusCode': 200,
        'body': f'Cleanup complete. Estimated monthly savings: ${savings:.2f}'
    }

def cleanup_unattached_volumes():
    """Delete EBS volumes not attached for 7+ days"""
    
    savings = 0
    cutoff_date = datetime.now() - timedelta(days=7)
    
    volumes = ec2.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )['Volumes']
    
    for volume in volumes:
        create_time = volume['CreateTime'].replace(tzinfo=None)
        
        if create_time < cutoff_date:
            volume_id = volume['VolumeId']
            size = volume['Size']
            
            # Calculate savings ($0.10/GB/month for gp3)
            monthly_cost = size * 0.08
            
            try:
                ec2.delete_volume(VolumeId=volume_id)
                savings += monthly_cost
                print(f"Deleted volume {volume_id} (${monthly_cost:.2f}/month)")
            except Exception as e:
                print(f"Error deleting {volume_id}: {e}")
    
    return savings

def cleanup_old_snapshots():
    """Delete snapshots older than 90 days (except tagged for retention)"""
    
    savings = 0
    cutoff_date = datetime.now() - timedelta(days=90)
    
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']
    
    for snapshot in snapshots:
        start_time = snapshot['StartTime'].replace(tzinfo=None)
        
        if start_time < cutoff_date:
            # Check for retention tag
            tags = {tag['Key']: tag['Value'] for tag in snapshot.get('Tags', [])}
            
            if tags.get('Retention') != 'Keep':
                snapshot_id = snapshot['SnapshotId']
                size = snapshot['VolumeSize']
                
                # Snapshot storage: $0.05/GB/month
                monthly_cost = size * 0.05
                
                try:
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    savings += monthly_cost
                    print(f"Deleted snapshot {snapshot_id} (${monthly_cost:.2f}/month)")
                except Exception as e:
                    print(f"Error deleting {snapshot_id}: {e}")
    
    return savings

def cleanup_elastic_ips():
    """Release Elastic IPs not associated with instances"""
    
    savings = 0
    
    addresses = ec2.describe_addresses()['Addresses']
    
    for address in addresses:
        if 'InstanceId' not in address:
            allocation_id = address['AllocationId']
            
            # $0.005/hour = $3.60/month per unassociated EIP
            monthly_cost = 3.60
            
            try:
                ec2.release_address(AllocationId=allocation_id)
                savings += monthly_cost
                print(f"Released EIP {address['PublicIp']} (${monthly_cost:.2f}/month)")
            except Exception as e:
                print(f"Error releasing {allocation_id}: {e}")
    
    return savings

def cleanup_idle_load_balancers():
    """Delete ALBs with no active target"""
    
    savings = 0
    
    load_balancers = elb.describe_load_balancers()['LoadBalancers']
    
    for lb in load_balancers:
        lb_arn = lb['LoadBalancerArn']
        lb_name = lb['LoadBalancerName']
        
        # Get target groups
        target_groups = elb.describe_target_groups(
            LoadBalancerArn=lb_arn
        )['TargetGroups']
        
        has_healthy_targets = False
        
        for tg in target_groups:
            health = elb.describe_target_health(
                TargetGroupArn=tg['TargetGroupArn']
            )['TargetHealthDescriptions']
            
            if any(t['TargetHealth']['State'] == 'healthy' for t in health):
                has_healthy_targets = True
                break
        
        if not has_healthy_targets:
            # ALB: $16/month
            monthly_cost = 16
            
            print(f"Would delete idle ALB: {lb_name} (${monthly_cost:.2f}/month)")
            # Uncomment to actually delete:
            # elb.delete_load_balancer(LoadBalancerArn=lb_arn)
            # savings += monthly_cost
    
    return savings

def stop_idle_rds_instances():
    """Stop dev/test RDS instances during off-hours"""
    
    savings = 0
    
    instances = rds.describe_db_instances()['DBInstances']
    
    for instance in instances:
        db_id = instance['DBInstanceIdentifier']
        tags = rds.list_tags_for_resource(
            ResourceName=instance['DBInstanceArn']
        )['TagList']
        
        env = next((tag['Value'] for tag in tags if tag['Key'] == 'Environment'), None)
        
        # Only stop dev/test, not production
        if env in ['dev', 'test', 'development'] and instance['DBInstanceStatus'] == 'available':
            instance_class = instance['DBInstanceClass']
            
            # Rough cost estimate (varies by type)
            monthly_cost = get_rds_monthly_cost(instance_class)
            
            # Stopped instances save ~70% (still pay for storage)
            potential_savings = monthly_cost * 0.7
            
            print(f"Would stop RDS: {db_id} (potential ${potential_savings:.2f}/month savings)")
            # Uncomment to actually stop:
            # rds.stop_db_instance(DBInstanceIdentifier=db_id)
            # savings += potential_savings
    
    return savings

def get_rds_monthly_cost(instance_class):
    """Estimate monthly RDS cost"""
    costs = {
        'db.t3.micro': 15,
        'db.t3.small': 30,
        'db.t3.medium': 60,
        'db.t3.large': 120,
        'db.r5.large': 180,
        'db.r5.xlarge': 360
    }
    return costs.get(instance_class, 100)
```

---

## Reserved Instance Management

**RI Purchase Recommendations:**
```python
import boto3

ce = boto3.client('ce')

def get_ri_recommendations():
    """Get RI purchase recommendations"""
    
    response = ce.get_reservation_purchase_recommendation(
        Service='Amazon Elastic Compute Cloud - Compute',
        LookbackPeriodInDays='SIXTY_DAYS',
        TermInYears='ONE_YEAR',
        PaymentOption='NO_UPFRONT'
    )
    
    recommendations = response['Recommendations']
    
    print("Reserved Instance Purchase Recommendations\n")
    print("=" * 70)
    
    total_savings = 0
    
    for rec in recommendations:
        details = rec['RecommendationDetails'][0]
        
        instance_type = details['InstanceDetails']['EC2InstanceDetails']['InstanceType']
        recommended_instances = details['RecommendedNumberOfInstancesToPurchase']
        estimated_savings = float(rec['RecommendationSummary']['TotalEstimatedMonthlySavingsAmount'])
        upfront_cost = float(details['UpfrontCost'])
        monthly_cost = float(details['RecurringStandardMonthlyCost'])
        
        total_savings += estimated_savings
        
        print(f"\nInstance Type: {instance_type}")
        print(f"Recommended quantity: {recommended_instances}")
        print(f"Monthly cost: ${monthly_cost:.2f}")
        print(f"Estimated monthly savings: ${estimated_savings:.2f}")
        print(f"ROI: {(estimated_savings/monthly_cost)*100:.1f}%")
    
    print(f"\nTotal estimated monthly savings: ${total_savings:.2f}")
    print(f"Total estimated annual savings: ${total_savings*12:.2f}")
    
    return recommendations
```

**RI Utilization Monitoring:**
```python
def monitor_ri_utilization():
    """Monitor RI utilization and coverage"""
    
    ce = boto3.client('ce')
    
    # Get RI utilization
    response = ce.get_reservation_utilization(
        TimePeriod={
            'Start': '2026-01-01',
            'End': '2026-01-31'
        },
        Granularity='MONTHLY'
    )
    
    for period in response['UtilizationsByTime']:
        utilization = period['Total']['UtilizationPercentage']
        purchased_hours = period['Total']['PurchasedHours']
        used_hours = period['Total']['UsedHours']
        unused_hours = period['Total']['UnusedHours']
        
        print(f"\nReserved Instance Utilization")
        print(f"Utilization: {utilization}%")
        print(f"Purchased hours: {purchased_hours}")
        print(f"Used hours: {used_hours}")
        print(f"Wasted hours: {unused_hours}")
        
        if float(utilization) < 80:
            print("⚠️  Warning: RI utilization below 80%")
            print("Consider: Modifying instance types or selling unused RIs")
    
    # Get RI coverage
    coverage_response = ce.get_reservation_coverage(
        TimePeriod={
            'Start': '2026-01-01',
            'End': '2026-01-31'
        },
        Granularity='MONTHLY'
    )
    
    for period in coverage_response['CoveragesByTime']:
        coverage = period['Total']['CoverageHours']['CoverageHoursPercentage']
        on_demand_hours = period['Total']['CoverageHours']['OnDemandHours']
        
        print(f"\nReserved Instance Coverage")
        print(f"Coverage: {coverage}%")
        print(f"On-Demand hours: {on_demand_hours}")
        
        if float(coverage) < 70:
            print("💡 Opportunity: Increase RI coverage to save more")
```

---

## Savings Plans vs Reserved Instances

**Comparison:**
```
Savings Plans (Recommended for most)
✓ More flexible (change instance family, size, OS, region)
✓ Applies to Fargate and Lambda
✓ Similar savings (up to 72%)
✓ Easier to manage
✗ Slightly less savings than Standard RIs

Reserved Instances
✓ Maximum savings (up to 75% for Standard)
✓ Can sell on RI Marketplace
✗ Less flexible (Convertible has less savings)
✗ More complex to manage
✗ EC2 only
```

**When to use each:**
- **Savings Plans**: Most scenarios, flexible workloads
- **Standard RIs**: Very stable, predictable workloads where you know exact instance type
- **Convertible RIs**: When you need flexibility but want RI benefits
- **Spot**: Flexible, fault-tolerant workloads