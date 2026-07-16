# Auto Scaling Groups

## Introduction

Auto Scaling helps maintain application availability and allows you to scale EC2 capacity up or down automatically according to defined conditions. This chapter covers Auto Scaling Groups (ASG), launch templates, scaling policies, and integration with load balancers.

## Table of Contents
- [What is Auto Scaling?](#what-is-auto-scaling)
- [Launch Templates and Configurations](#launch-templates-and-configurations)
- [Auto Scaling Groups](#auto-scaling-groups)
- [Scaling Policies](#scaling-policies)
- [Instance Lifecycle](#instance-lifecycle)
- [Integration with Load Balancers](#integration-with-load-balancers)
- [Monitoring and Metrics](#monitoring-and-metrics)
- [Hands-on Exercises](#hands-on-exercises)

---

## What is Auto Scaling?

### Benefits

```yaml
High Availability:
  - Replace unhealthy instances automatically
  - Distribute across multiple AZs
  - Maintain desired capacity
  
Cost Optimization:
  - Scale down during low demand
  - Pay only for needed capacity
  - Right-size your fleet
  
Performance:
  - Scale up during high demand
  - Maintain response times
  - Handle traffic spikes
```

### Auto Scaling Components

```
Launch Template
  ↓
Auto Scaling Group (ASG)
  ├── Desired Capacity: 4
  ├── Min Capacity: 2
  ├── Max Capacity: 10
  ├── Availability Zones: us-east-1a, us-east-1b
  └── Scaling Policies
      ├── Scale Out: +2 instances (CPU > 75%)
      └── Scale In: -1 instance (CPU < 25%)
```

---

## Launch Templates and Configurations

### Launch Template vs Launch Configuration

```yaml
Launch Template (Recommended):
  - Versioning support
  - Multiple instance types
  - Spot/On-Demand mix
  - T2/T3 Unlimited
  - Modification support
  
Launch Configuration (Legacy):
  - No versioning
  - Single instance type
  - Immutable
  - Being phased out
```

### Create Launch Template

```bash
# Create security group
ASG_SG=$(aws ec2 create-security-group \
  --group-name asg-security-group \
  --description "Security group for ASG instances" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)

# Allow HTTP from ALB
aws ec2 authorize-security-group-ingress \
  --group-id $ASG_SG \
  --protocol tcp \
  --port 80 \
  --source-group $ALB_SG

# User data script
cat > user-data.sh << 'EOF'
#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd

# Get instance metadata
INSTANCE_ID=$(ec2-metadata --instance-id | cut -d " " -f 2)
AZ=$(ec2-metadata --availability-zone | cut -d " " -f 2)

# Create simple web page
cat > /var/www/html/index.html << HTML
<html>
<head><title>Auto Scaled Instance</title></head>
<body>
<h1>Hello from Auto Scaling!</h1>
<p>Instance ID: $INSTANCE_ID</p>
<p>Availability Zone: $AZ</p>
</body>
</html>
HTML

# Health check endpoint
echo "OK" > /var/www/html/health
EOF

# Create launch template
LT_ID=$(aws ec2 create-launch-template \
  --launch-template-name web-launch-template \
  --version-description "v1" \
  --launch-template-data '{
    "ImageId": "ami-0c55b159cbfafe1f0",
    "InstanceType": "t3.micro",
    "SecurityGroupIds": ["'$ASG_SG'"],
    "UserData": "'$(base64 -w 0 user-data.sh)'",
    "TagSpecifications": [{
      "ResourceType": "instance",
      "Tags": [{"Key":"Name","Value":"ASG-Instance"}]
    }],
    "IamInstanceProfile": {
      "Name": "EC2-CloudWatch-Role"
    },
    "Monitoring": {"Enabled": true}
  }' \
  --query 'LaunchTemplate.LaunchTemplateId' \
  --output text)

echo "Launch Template ID: $LT_ID"
```

### Launch Template with Mixed Instances

```json
{
  "LaunchTemplate": {
    "LaunchTemplateId": "lt-xxx",
    "Version": "$Latest"
  },
  "Overrides": [
    {
      "InstanceType": "t3.micro",
      "WeightedCapacity": 1
    },
    {
      "InstanceType": "t3.small",
      "WeightedCapacity": 2
    },
    {
      "InstanceType": "t3a.micro",
      "WeightedCapacity": 1
    }
  ]
}
```


---

## Auto Scaling Groups

### Create Auto Scaling Group

```bash
# Create Auto Scaling Group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name web-asg \
  --launch-template LaunchTemplateId=$LT_ID,Version='$Latest' \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 4 \
  --default-cooldown 300 \
  --health-check-type ELB \
  --health-check-grace-period 300 \
  --vpc-zone-identifier "$PRIVATE_SUBNET_1,$PRIVATE_SUBNET_2" \
  --target-group-arns $TG_ARN \
  --tags \
    Key=Name,Value=ASG-Instance,PropagateAtLaunch=true \
    Key=Environment,Value=Production,PropagateAtLaunch=true

# Describe ASG
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names web-asg

# List instances in ASG
aws autoscaling describe-auto-scaling-instances \
  --query 'AutoScalingInstances[?AutoScalingGroupName==`web-asg`]'
```

### ASG Configuration Parameters

```yaml
Capacity:
  MinSize: Minimum instances (never go below)
  MaxSize: Maximum instances (never exceed)
  DesiredCapacity: Target number of instances
  
Health Checks:
  Type: EC2 or ELB
  GracePeriod: Time before health checks start (seconds)
  
Cooldown:
  DefaultCooldown: Wait time after scaling activity
  Purpose: Prevent rapid scaling
  Default: 300 seconds
  
Termination Policy:
  - OldestInstance
  - NewestInstance
  - OldestLaunchConfiguration
  - ClosestToNextInstanceHour (cost optimization)
  - Default
```

### Update Auto Scaling Group

```bash
# Update capacity
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name web-asg \
  --min-size 3 \
  --max-size 15 \
  --desired-capacity 6

# Update launch template version
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name web-asg \
  --launch-template LaunchTemplateId=$LT_ID,Version='$Latest'

# Add more subnets
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name web-asg \
  --vpc-zone-identifier "$SUBNET_1,$SUBNET_2,$SUBNET_3"
```

---

## Scaling Policies

### Types of Scaling Policies

```yaml
Target Tracking:
  - Maintain specific metric value
  - Example: Keep CPU at 50%
  - Simplest to configure
  - Recommended for most use cases
  
Step Scaling:
  - Scale by steps based on alarm severity
  - Example: +2 instances if CPU > 80%, +4 if CPU > 90%
  - More granular control
  
Simple Scaling:
  - Single scaling adjustment
  - Legacy approach
  - Use step scaling instead
  
Scheduled Scaling:
  - Scale at specific times
  - Example: Scale up at 9 AM, down at 6 PM
  - Predictable patterns
```

### Target Tracking Scaling

```bash
# CPU-based target tracking
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name web-asg \
  --policy-name target-tracking-cpu \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    },
    "TargetValue": 50.0
  }'

# ALB request count per target
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name web-asg \
  --policy-name target-tracking-requests \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ALBRequestCountPerTarget",
      "ResourceLabel": "'$ALB_NAME'/'$TG_NAME'"
    },
    "TargetValue": 1000.0
  }'

# Custom metric
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name web-asg \
  --policy-name target-tracking-custom \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "CustomizedMetricSpecification": {
      "MetricName": "QueueDepth",
      "Namespace": "MyApp",
      "Statistic": "Average"
    },
    "TargetValue": 100.0
  }'
```

### Step Scaling Policy

```bash
# Create CloudWatch alarms
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu-alarm \
  --alarm-description "Scale up when CPU > 75%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 75 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=AutoScalingGroupName,Value=web-asg

aws cloudwatch put-metric-alarm \
  --alarm-name low-cpu-alarm \
  --alarm-description "Scale down when CPU < 25%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 25 \
  --comparison-operator LessThanThreshold \
  --dimensions Name=AutoScalingGroupName,Value=web-asg

# Create step scaling policy
SCALE_OUT_POLICY=$(aws autoscaling put-scaling-policy \
  --auto-scaling-group-name web-asg \
  --policy-name scale-out-policy \
  --policy-type StepScaling \
  --adjustment-type PercentChangeInCapacity \
  --metric-aggregation-type Average \
  --step-adjustments \
    MetricIntervalLowerBound=0,MetricIntervalUpperBound=10,ScalingAdjustment=10 \
    MetricIntervalLowerBound=10,ScalingAdjustment=20 \
  --query 'PolicyARN' --output text)

SCALE_IN_POLICY=$(aws autoscaling put-scaling-policy \
  --auto-scaling-group-name web-asg \
  --policy-name scale-in-policy \
  --policy-type StepScaling \
  --adjustment-type PercentChangeInCapacity \
  --metric-aggregation-type Average \
  --step-adjustments \
    MetricIntervalUpperBound=0,ScalingAdjustment=-10 \
  --query 'PolicyARN' --output text)

# Link alarms to policies
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu-alarm \
  --alarm-actions $SCALE_OUT_POLICY

aws cloudwatch put-metric-alarm \
  --alarm-name low-cpu-alarm \
  --alarm-actions $SCALE_IN_POLICY
```

### Scheduled Scaling

```bash
# Scale up weekday mornings
aws autoscaling put-scheduled-update-group-action \
  --auto-scaling-group-name web-asg \
  --scheduled-action-name scale-up-morning \
  --recurrence "0 9 * * MON-FRI" \
  --min-size 5 \
  --max-size 15 \
  --desired-capacity 10

# Scale down weekday evenings
aws autoscaling put-scheduled-update-group-action \
  --auto-scaling-group-name web-asg \
  --scheduled-action-name scale-down-evening \
  --recurrence "0 18 * * MON-FRI" \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 4

# Scale down weekends
aws autoscaling put-scheduled-update-group-action \
  --auto-scaling-group-name web-asg \
  --scheduled-action-name scale-down-weekend \
  --recurrence "0 0 * * SAT" \
  --min-size 2 \
  --max-size 5 \
  --desired-capacity 2
```

---

## Instance Lifecycle

### Lifecycle States

```
Pending → InService → Terminating → Terminated
              ↓
          Detaching → Detached
              ↓
         Standby (maintenance)
              ↓
          EnteringStandby → InService
```

### Lifecycle Hooks

```yaml
Purpose:
  - Perform actions before instance launch/terminate
  - Examples: Install software, backup data, deregister from services
  
Hook Types:
  - Launch Hook: Before instance enters InService
  - Terminate Hook: Before instance terminates
  
States During Hook:
  - Pending:Wait (launch hook)
  - Terminating:Wait (terminate hook)
  - Pending:Proceed or Terminating:Proceed (complete)
```

```bash
# Create launch lifecycle hook
aws autoscaling put-lifecycle-hook \
  --lifecycle-hook-name launch-hook \
  --auto-scaling-group-name web-asg \
  --lifecycle-transition autoscaling:EC2_INSTANCE_LAUNCHING \
  --default-result CONTINUE \
  --heartbeat-timeout 300 \
  --notification-target-arn $SNS_TOPIC_ARN \
  --role-arn $IAM_ROLE_ARN

# Create terminate lifecycle hook
aws autoscaling put-lifecycle-hook \
  --lifecycle-hook-name terminate-hook \
  --auto-scaling-group-name web-asg \
  --lifecycle-transition autoscaling:EC2_INSTANCE_TERMINATING \
  --default-result CONTINUE \
  --heartbeat-timeout 300

# Complete lifecycle action (from Lambda or script)
aws autoscaling complete-lifecycle-action \
  --lifecycle-hook-name launch-hook \
  --auto-scaling-group-name web-asg \
  --lifecycle-action-result CONTINUE \
  --instance-id i-1234567890
```

### Lambda Function for Lifecycle Hook

```python
import boto3
import json

asg = boto3.client('autoscaling')
ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    # Parse SNS message
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    instance_id = message['EC2InstanceId']
    hook_name = message['LifecycleHookName']
    asg_name = message['AutoScalingGroupName']
    transition = message['LifecycleTransition']
    
    try:
        if transition == 'autoscaling:EC2_INSTANCE_LAUNCHING':
            # Perform launch actions
            print(f"Configuring instance {instance_id}")
            # Example: Wait for instance to be ready, install software
            configure_instance(instance_id)
            
        elif transition == 'autoscaling:EC2_INSTANCE_TERMINATING':
            # Perform termination actions
            print(f"Cleaning up instance {instance_id}")
            # Example: Backup data, deregister from services
            cleanup_instance(instance_id)
        
        # Complete lifecycle action
        asg.complete_lifecycle_action(
            LifecycleHookName=hook_name,
            AutoScalingGroupName=asg_name,
            LifecycleActionResult='CONTINUE',
            InstanceId=instance_id
        )
        
        return {'statusCode': 200, 'body': 'Success'}
        
    except Exception as e:
        print(f"Error: {e}")
        # Abandon lifecycle action on error
        asg.complete_lifecycle_action(
            LifecycleHookName=hook_name,
            AutoScalingGroupName=asg_name,
            LifecycleActionResult='ABANDON',
            InstanceId=instance_id
        )
        return {'statusCode': 500, 'body': str(e)}

def configure_instance(instance_id):
    # Custom configuration logic
    pass

def cleanup_instance(instance_id):
    # Custom cleanup logic
    pass
```

---

## Integration with Load Balancers

### ALB Integration

```bash
# Create ASG with ALB target group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name web-asg \
  --launch-template LaunchTemplateId=$LT_ID \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 4 \
  --target-group-arns $ALB_TG_ARN \
  --health-check-type ELB \
  --health-check-grace-period 300 \
  --vpc-zone-identifier "$SUBNET_1,$SUBNET_2"

# Attach additional target group
aws autoscaling attach-load-balancer-target-groups \
  --auto-scaling-group-name web-asg \
  --target-group-arns $ADDITIONAL_TG_ARN

# Detach target group
aws autoscaling detach-load-balancer-target-groups \
  --auto-scaling-group-name web-asg \
  --target-group-arns $TG_ARN
```

### Health Check Integration

```yaml
EC2 Health Check:
  - Checks: EC2 instance status
  - Unhealthy: Instance status checks fail
  - Fast failure detection
  
ELB Health Check:
  - Checks: Load balancer target health
  - Unhealthy: Fails ELB health checks
  - Application-aware
  - Recommended with load balancers
  
Combined:
  - Use ELB health check type
  - ASG replaces instances failing ELB checks
  - More comprehensive monitoring
```

---

## Monitoring and Metrics

### ASG CloudWatch Metrics

```yaml
Group Metrics:
  GroupMinSize: Minimum group size
  GroupMaxSize: Maximum group size
  GroupDesiredCapacity: Desired capacity
  GroupInServiceInstances: Running instances
  GroupPendingInstances: Launching instances
  GroupTerminatingInstances: Terminating instances
  GroupTotalInstances: Total instances
  
Enable detailed monitoring:
  aws autoscaling enable-metrics-collection \
    --auto-scaling-group-name web-asg \
    --granularity "1Minute" \
    --metrics GroupDesiredCapacity GroupInServiceInstances
```

### Scaling Activities

```bash
# View scaling activities
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name web-asg \
  --max-records 20

# Example output shows:
# - Timestamp
# - Activity ID
# - Description
# - Cause (policy trigger, manual, scheduled)
# - Status (Successful, Failed, Cancelled)
```

### CloudWatch Dashboard

```bash
# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name ASG-Dashboard \
  --dashboard-body file://dashboard.json
```

**dashboard.json:**
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/AutoScaling", "GroupDesiredCapacity", {"stat": "Average"}],
          [".", "GroupInServiceInstances", {"stat": "Average"}]
        ],
        "period": 60,
        "stat": "Average",
        "region": "us-east-1",
        "title": "ASG Capacity"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/EC2", "CPUUtilization", {"stat": "Average"}]
        ],
        "period": 60,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Average CPU Utilization"
      }
    }
  ]
}
```

---

## Hands-on Exercises

### Exercise 1: Complete ASG with ALB

**Objective:** Deploy fully functional Auto Scaling setup

```bash
#!/bin/bash
# Complete ASG deployment

# Variables
VPC_ID="vpc-xxx"
SUBNET_1="subnet-xxx"
SUBNET_2="subnet-yyy"
ALB_TG_ARN="arn:aws:elasticloadbalancing:..."

# Create launch template
LT_ID=$(aws ec2 create-launch-template \
  --launch-template-name asg-lt \
  --version-description "v1" \
  --launch-template-data '{
    "ImageId": "ami-0c55b159cbfafe1f0",
    "InstanceType": "t3.micro",
    "SecurityGroupIds": ["sg-xxx"],
    "UserData": "'$(cat user-data.sh | base64 -w 0)'",
    "TagSpecifications": [{
      "ResourceType": "instance",
      "Tags": [{"Key":"Name","Value":"ASG-Web"}]
    }],
    "Monitoring": {"Enabled": true}
  }' \
  --query 'LaunchTemplate.LaunchTemplateId' --output text)

# Create Auto Scaling Group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name production-asg \
  --launch-template LaunchTemplateId=$LT_ID,Version='$Latest' \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 4 \
  --default-cooldown 300 \
  --health-check-type ELB \
  --health-check-grace-period 300 \
  --vpc-zone-identifier "$SUBNET_1,$SUBNET_2" \
  --target-group-arns $ALB_TG_ARN \
  --tags Key=Environment,Value=Production,PropagateAtLaunch=true

# Create target tracking policy
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name production-asg \
  --policy-name cpu-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    },
    "TargetValue": 50.0
  }'

# Enable detailed monitoring
aws autoscaling enable-metrics-collection \
  --auto-scaling-group-name production-asg \
  --granularity "1Minute"

echo "ASG deployed successfully!"
```

### Exercise 2: Test Scaling

**Objective:** Trigger scaling activities

```bash
# Generate load to trigger scale-out
# SSH to one instance
ssh -i my-key.pem ec2-user@<instance-ip>

# Install stress tool
sudo yum install -y stress

# Generate CPU load
stress --cpu 4 --timeout 300s

# Watch scaling activity
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name production-asg \
  --max-records 5

# Monitor CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=AutoScalingGroupName,Value=production-asg \
  --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average
```

---

## Validation Checklist

- [ ] Launch template created
- [ ] Auto Scaling Group configured
- [ ] Min, Max, Desired capacity set appropriately
- [ ] Integrated with load balancer
- [ ] ELB health checks enabled
- [ ] Scaling policies configured
- [ ] CloudWatch alarms created
- [ ] Lifecycle hooks tested (if used)
- [ ] Monitoring enabled
- [ ] Scaling activities verified

---

## Best Practices

```yaml
Configuration:
  - Use launch templates (not launch configurations)
  - Enable detailed monitoring
  - Set appropriate health check grace period
  - Use multiple AZs for high availability
  
Scaling:
  - Start with target tracking policies
  - Set realistic target values
  - Use multiple metrics when needed
  - Configure proper cooldown periods
  
Cost Optimization:
  - Use Spot Instances for fault-tolerant workloads
  - Mix instance types
  - Schedule scaling for predictable patterns
  - Right-size instances
  
Security:
  - Use IAM roles (not access keys)
  - Minimal security group rules
  - Regular AMI updates
  - Enable encryption
```

---

## Next Steps

1. ✓ Auto Scaling Groups mastered
2. ✓ Scaling policies configured
3. ✓ Load balancer integration complete
4. → **Next:** RDS Databases (Chapter 9)
5. → Lambda Serverless (Chapter 10)

---

## Additional Resources

- [Auto Scaling User Guide](https://docs.aws.amazon.com/autoscaling/)
- [Scaling Policies](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scale-based-on-demand.html)
- [Best Practices](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-best-practices.html)
