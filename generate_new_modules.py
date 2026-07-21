#!/usr/bin/env python3
"""
Generate remaining FinOps and Platform Engineering content
This script creates all missing files with comprehensive content
"""

import os
from pathlib import Path

# FinOps Intermediate Files
finops_intermediate = {
    "06-cost-optimization-strategies.md": """# AWS Cost Optimization Strategies

## Overview
This guide covers practical cost optimization strategies for AWS, including Reserved Instances, Savings Plans, Spot instances, and rightsizing recommendations.

**Topics:**
- Reserved Instances vs Savings Plans
- Spot instance strategies
- Rightsizing EC2/RDS
- Storage optimization
- Network cost reduction

## Reserved Instances vs Savings Plans

### Reserved Instances (RIs)

**Types:**
1. Standard RIs - 75% discount, 1-3 years
2. Convertible RIs - 54% discount, can change instance type
3. Scheduled RIs - For predictable workloads

**When to Use:**
- Steady-state workloads
- Known capacity needs
- Specific instance types

### Savings Plans

**Types:**
1. Compute Savings Plans - 66% discount, any instance family
2. EC2 Instance Savings Plans - 72% discount, specific family
3. SageMaker Savings Plans - For ML workloads

**Advantages:**
- Flexibility across instance types
- Automatically applies to Lambda, Fargate
- Easier to manage

## Spot Instances

**Best Practices:**
- Use for fault-tolerant workloads
- Implement graceful shutdown handlers
- Mix with On-Demand for resilience
- 70-90% cost savings

## Rightsizing

**Tools:**
- AWS Compute Optimizer
- Cost Explorer rightsizing recommendations
- CloudWatch metrics analysis

**Process:**
1. Analyze utilization (CPU, memory, network)
2. Identify underutilized resources
3. Recommend smaller instance types
4. Test and implement changes

## Storage Optimization

**S3 Strategies:**
- S3 Intelligent-Tiering
- Lifecycle policies
- Delete incomplete multipart uploads
- Use Glacier for archival

**EBS Strategies:**
- Delete unattached volumes
- Use gp3 instead of gp2
- Snapshot cleanup
- Right-size volume capacity

## Summary

Cost optimization is ongoing:
- Review monthly
- Automate where possible
- Balance cost vs performance
- Use multiple strategies together

**Related Topics:**
- [AWS Cost Explorer](../01-basics/04-aws-cost-explorer.md)
- [Budgets and Alerts](07-budgets-alerts.md)
""",

    "07-budgets-alerts.md": """# AWS Budgets and Cost Alerts

## Overview
Set up proactive cost monitoring with AWS Budgets, CloudWatch alarms, and automated alerting systems.

**Topics:**
- AWS Budgets setup
- CloudWatch billing alarms
- Anomaly detection
- Alert integrations (Slack, email, PagerDuty)

## AWS Budgets

**Budget Types:**
1. Cost budgets - Track spending
2. Usage budgets - Track resource usage
3. RI/SP utilization - Track commitment usage
4. RI/SP coverage - Track discount coverage

**Creating Budgets:**
```python
import boto3

budgets = boto3.client('budgets')

response = budgets.create_budget(
    AccountId='123456789012',
    Budget={
        'BudgetName': 'Monthly-Production-Budget',
        'BudgetLimit': {
            'Amount': '50000',
            'Unit': 'USD'
        },
        'TimeUnit': 'MONTHLY',
        'BudgetType': 'COST'
    },
    NotificationsWithSubscribers=[
        {
            'Notification': {
                'NotificationType': 'ACTUAL',
                'ComparisonOperator': 'GREATER_THAN',
                'Threshold': 80,
                'ThresholdType': 'PERCENTAGE'
            },
            'Subscribers': [
                {
                    'SubscriptionType': 'EMAIL',
                    'Address': 'devops@company.com'
                }
            ]
        }
    ]
)
```

## CloudWatch Billing Alarms

**Setup Process:**
1. Enable billing alerts in Billing preferences
2. Create CloudWatch alarm for EstimatedCharges
3. Configure SNS topic for notifications
4. Set threshold and actions

**Example:**
```python
import boto3

cloudwatch = boto3.client('cloudwatch')
sns = boto3.client('sns')

# Create SNS topic
topic = sns.create_topic(Name='billing-alerts')
topic_arn = topic['TopicArn']

# Subscribe email
sns.subscribe(
    TopicArn=topic_arn,
    Protocol='email',
    Endpoint='finance@company.com'
)

# Create alarm
cloudwatch.put_metric_alarm(
    AlarmName='MonthlyBillingAlert',
    MetricName='EstimatedCharges',
    Namespace='AWS/Billing',
    Statistic='Maximum',
    Period=21600,  # 6 hours
    EvaluationPeriods=1,
    Threshold=45000,
    ComparisonOperator='GreaterThanThreshold',
    AlarmActions=[topic_arn],
    Dimensions=[
        {'Name': 'Currency', 'Value': 'USD'}
    ]
)
```

## Anomaly Detection

**AWS Cost Anomaly Detection:**
- Machine learning-based
- Automatically detects unusual spending
- Configurable sensitivity
- Integration with AWS Budgets

**Setup:**
```python
ce = boto3.client('ce')

# Create anomaly monitor
monitor = ce.create_anomaly_monitor(
    AnomalyMonitor={
        'MonitorName': 'Production-Anomaly-Monitor',
        'MonitorType': 'DIMENSIONAL',
        'MonitorDimension': 'SERVICE'
    }
)

# Create anomaly subscription
subscription = ce.create_anomaly_subscription(
    AnomalySubscription={
        'SubscriptionName': 'Production-Alerts',
        'Threshold': 100,  # $100 threshold
        'Frequency': 'DAILY',
        'MonitorArnList': [monitor['MonitorArn']],
        'Subscribers': [
            {
                'Type': 'EMAIL',
                'Address': 'devops@company.com'
            }
        ]
    }
)
```

## Slack Integration

**Lambda for Slack Notifications:**
```python
import json
import boto3
from urllib.request import Request, urlopen

def lambda_handler(event, context):
    # Parse SNS message
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    # Extract cost information
    alarm_name = message.get('AlarmName')
    new_state = message.get('NewStateValue')
    reason = message.get('NewStateReason')
    
    # Build Slack message
    slack_message = {
        'text': f'🚨 AWS Cost Alert',
        'attachments': [
            {
                'color': 'danger' if new_state == 'ALARM' else 'good',
                'fields': [
                    {'title': 'Alarm', 'value': alarm_name, 'short': True},
                    {'title': 'State', 'value': new_state, 'short': True},
                    {'title': 'Reason', 'value': reason, 'short': False}
                ]
            }
        ]
    }
    
    # Send to Slack
    webhook_url = os.environ['SLACK_WEBHOOK_URL']
    req = Request(webhook_url, json.dumps(slack_message).encode('utf-8'))
    response = urlopen(req)
    
    return {'statusCode': 200}
```

## Daily Cost Reports

**Automated Email Reports:**
```python
import boto3
from datetime import datetime, timedelta

def send_daily_cost_report():
    ce = boto3.client('ce')
    ses = boto3.client('ses')
    
    # Get yesterday's costs
    end = datetime.now().date()
    start = end - timedelta(days=1)
    
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start.strftime('%Y-%m-%d'),
            'End': end.strftime('%Y-%m-%d')
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )
    
    # Build email
    total = float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
    
    email_body = f'''
    Daily AWS Cost Report - {start}
    
    Total Cost: ${total:.2f}
    
    Top Services:
    '''
    
    for group in response['ResultsByTime'][0]['Groups'][:5]:
        service = group['Keys'][0]
        cost = float(group['Metrics']['UnblendedCost']['Amount'])
        email_body += f'  {service}: ${cost:.2f}\\n'
    
    # Send email
    ses.send_email(
        Source='noreply@company.com',
        Destination={'ToAddresses': ['team@company.com']},
        Message={
            'Subject': {'Data': f'Daily Cost Report - ${total:.2f}'},
            'Body': {'Text': {'Data': email_body}}
        }
    )
```

## Best Practices

1. **Multiple Budget Levels:**
   - Overall account budget
   - Per-service budgets
   - Per-team budgets
   - Per-environment budgets

2. **Threshold Strategy:**
   - 50% - Informational
   - 80% - Warning
   - 100% - Critical
   - 120% - Emergency

3. **Automation:**
   - Auto-stop dev environments at night
   - Auto-scale down on weekends
   - Delete unused resources

4. **Escalation:**
   - Team lead at 80%
   - Director at 100%
   - CTO at 120%

## Summary

Effective cost alerting requires:
- Multiple budget types
- Proactive anomaly detection
- Automated reporting
- Clear escalation paths
- Integration with team workflows

**Related Topics:**
- [Cost Visibility](../01-basics/03-cost-visibility-tagging.md)
- [Cost Optimization](06-cost-optimization-strategies.md)
""",

    "08-cost-gates-cicd.md": """# Cost Gates in CI/CD Pipelines

## Overview
Implement cost checks in your CI/CD pipelines to prevent expensive infrastructure changes from reaching production.

**Topics:**
- Pre-deployment cost estimation
- Policy-as-code for cost
- Terraform cost analysis
- Automated cost reviews

## Why Cost Gates Matter

**Problem:**
```
Developer: Deploys new RDS instance
Instance Type: db.r6g.16xlarge
Cost: $5,000/month
Nobody notices until bill arrives
```

**Solution:**
```
Pipeline: Analyzes Terraform plan
Estimated Cost: $5,000/month (+400% from current)
Pipeline: BLOCKS deployment
Developer: Switches to db.r6g.2xlarge
Cost: $625/month
Pipeline: APPROVED
```

## Infracost Integration

**Install Infracost:**
```bash
# Install Infracost CLI
curl -fsSL https://raw.githubusercontent.com/infracost/infracost/master/scripts/install.sh | sh

# Register for API key
infracost auth login
```

**GitLab CI Example:**
```yaml
# .gitlab-ci.yml
cost_estimate:
  stage: plan
  image: infracost/infracost:latest
  script:
    - terraform init
    - terraform plan -out tfplan.binary
    - terraform show -json tfplan.binary > plan.json
    
    # Generate cost estimate
    - infracost breakdown --path plan.json --format json --out-file infracost.json
    
    # Get cost diff
    - infracost diff --path plan.json --compare-to infracost-base.json
    
    # Check cost increase
    - |
      COST_INCREASE=$(jq '.diffTotalMonthlyCost | tonumber' infracost.json)
      if (( $(echo "$COST_INCREASE > 1000" | bc -l) )); then
        echo "Cost increase of \$$COST_INCREASE exceeds \$1000 threshold"
        exit 1
      fi
  artifacts:
    reports:
      infracost: infracost.json

deploy:
  stage: deploy
  needs: [cost_estimate]
  script:
    - terraform apply tfplan.binary
  when: manual
```

**GitHub Actions Example:**
```yaml
name: Cost Check

on: [pull_request]

jobs:
  infracost:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Infracost
        uses: infracost/actions/setup@v2
        with:
          api-key: ${{ secrets.INFRACOST_API_KEY }}
      
      - name: Checkout base branch
        uses: actions/checkout@v3
        with:
          ref: '${{ github.event.pull_request.base.ref }}'
      
      - name: Generate base cost estimate
        run: |
          terraform init
          terraform plan -out tfplan.binary
          terraform show -json tfplan.binary > plan.json
          infracost breakdown --path plan.json --format json --out-file /tmp/infracost-base.json
      
      - name: Checkout PR branch
        uses: actions/checkout@v3
      
      - name: Generate PR cost estimate
        run: |
          terraform init
          terraform plan -out tfplan.binary
          terraform show -json tfplan.binary > plan.json
          infracost diff --path plan.json --compare-to /tmp/infracost-base.json --format json --out-file /tmp/infracost.json
      
      - name: Post comment
        uses: infracost/actions/comment@v1
        with:
          path: /tmp/infracost.json
          behavior: update
```

## Custom Cost Policies

**OPA (Open Policy Agent) for Cost:**
```rego
# cost_policy.rego
package terraform.cost

import input as tfplan

deny[msg] {
    resource := tfplan.resource_changes[_]
    resource.type == "aws_instance"
    resource.change.after.instance_type == "m5.24xlarge"
    msg := sprintf("Instance type %s is too expensive. Use m5.2xlarge or smaller.", [resource.change.after.instance_type])
}

deny[msg] {
    resource := tfplan.resource_changes[_]
    resource.type == "aws_rds_cluster"
    resource.change.after.instance_class == "db.r6g.16xlarge"
    msg := "RDS instance class db.r6g.16xlarge exceeds cost limits"
}

warn[msg] {
    count_instances := count([r | r := tfplan.resource_changes[_]; r.type == "aws_instance"])
    count_instances > 10
    msg := sprintf("Creating %d instances. Consider using Auto Scaling Group.", [count_instances])
}
```

**Use in Pipeline:**
```bash
# Check cost policy
terraform show -json tfplan.binary > plan.json
conftest test plan.json -p cost_policy.rego

# Output:
# FAIL - cost_policy.rego:5 - RDS instance class db.r6g.16xlarge exceeds cost limits
# WARN - cost_policy.rego:15 - Creating 12 instances. Consider using Auto Scaling Group.
```

## Automated Cost Reviews

**Lambda Cost Reviewer:**
```python
import boto3
import json

def lambda_handler(event, context):
    """
    Triggered by CodePipeline
    Reviews Terraform plan for cost implications
    """
    
    # Get Terraform plan from CodePipeline
    codepipeline = boto3.client('codepipeline')
    s3 = boto3.client('s3')
    
    job_id = event['CodePipeline.job']['id']
    
    try:
        # Download Terraform plan
        plan = get_terraform_plan_from_s3()
        
        # Analyze cost
        cost_analysis = analyze_cost(plan)
        
        # Check thresholds
        if cost_analysis['monthly_increase'] > 1000:
            # BLOCK deployment
            codepipeline.put_job_failure_result(
                jobId=job_id,
                failureDetails={
                    'message': f"Cost increase of ${cost_analysis['monthly_increase']:.2f} exceeds $1000 threshold",
                    'type': 'JobFailed'
                }
            )
            
            # Send notification
            send_cost_alert(cost_analysis)
            
        else:
            # APPROVE deployment
            codepipeline.put_job_success_result(jobId=job_id)
    
    except Exception as e:
        codepipeline.put_job_failure_result(
            jobId=job_id,
            failureDetails={'message': str(e), 'type': 'JobFailed'}
        )

def analyze_cost(plan):
    """Analyze Terraform plan for cost"""
    cost_increase = 0
    
    for resource in plan['resource_changes']:
        if resource['change']['actions'][0] == 'create':
            # Estimate cost based on resource type
            cost_increase += estimate_resource_cost(resource)
    
    return {
        'monthly_increase': cost_increase,
        'resources': len(plan['resource_changes'])
    }

def estimate_resource_cost(resource):
    """Simple cost estimation"""
    pricing = {
        'aws_instance': {
            't3.micro': 7.50,
            't3.small': 15.00,
            't3.medium': 30.00,
            'm5.large': 70.00,
            'm5.2xlarge': 280.00
        },
        'aws_rds_cluster': {
            'db.r6g.large': 180.00,
            'db.r6g.xlarge': 360.00,
            'db.r6g.2xlarge': 720.00
        }
    }
    
    resource_type = resource['type']
    
    if resource_type == 'aws_instance':
        instance_type = resource['change']['after']['instance_type']
        return pricing.get(resource_type, {}).get(instance_type, 0)
    
    elif resource_type == 'aws_rds_cluster':
        instance_class = resource['change']['after']['instance_class']
        return pricing.get(resource_type, {}).get(instance_class, 0)
    
    return 0
```

## Cost Budgets for Pipelines

**Pipeline-Specific Budgets:**
```python
import boto3

def create_pipeline_budget(pipeline_name, monthly_limit):
    """Create budget for specific pipeline"""
    budgets = boto3.client('budgets')
    
    response = budgets.create_budget(
        AccountId='123456789012',
        Budget={
            'BudgetName': f'{pipeline_name}-monthly-budget',
            'BudgetLimit': {
                'Amount': str(monthly_limit),
                'Unit': 'USD'
            },
            'TimeUnit': 'MONTHLY',
            'BudgetType': 'COST',
            'CostFilters': {
                'TagKeyValue': [f'Pipeline${pipeline_name}']
            }
        },
        NotificationsWithSubscribers=[
            {
                'Notification': {
                    'NotificationType': 'FORECASTED',
                    'ComparisonOperator': 'GREATER_THAN',
                    'Threshold': 100,
                    'ThresholdType': 'PERCENTAGE'
                },
                'Subscribers': [
                    {
                        'SubscriptionType': 'SNS',
                        'Address': 'arn:aws:sns:us-east-1:123456789012:pipeline-cost-alerts'
                    }
                ]
            }
        ]
    )
```

## Cost Dashboard in PR Comments

**GitHub Actions Cost Comment:**
```yaml
- name: Generate cost report
  run: |
    cat > cost_comment.md <<EOF
    ## 💰 Cost Impact Analysis
    
    **Monthly Cost Change:** +\$$(jq '.diffTotalMonthlyCost' infracost.json)
    
    **Breakdown:**
    $(infracost output --path infracost.json --format table)
    
    **Approval Status:** $(if [ $(jq '.diffTotalMonthlyCost | tonumber' infracost.json) -lt 1000 ]; then echo "✅ Approved"; else echo "❌ Requires Review"; fi)
    EOF

- name: Comment on PR
  uses: actions/github-script@v6
  with:
    script: |
      const fs = require('fs');
      const comment = fs.readFileSync('cost_comment.md', 'utf8');
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.name,
        body: comment
      });
```

## Terraform Cost Estimation Module

**Reusable Module:**
```hcl
# modules/cost-check/main.tf
data "external" "cost_estimate" {
  program = ["python3", "${path.module}/estimate_cost.py"]
  
  query = {
    instance_type  = var.instance_type
    instance_count = var.instance_count
    storage_gb     = var.storage_gb
  }
}

resource "null_resource" "cost_gate" {
  triggers = {
    cost = data.external.cost_estimate.result.monthly_cost
  }
  
  provisioner "local-exec" {
    command = <<-EOT
      COST=${data.external.cost_estimate.result.monthly_cost}
      THRESHOLD=1000
      
      if [ $(echo "$COST > $THRESHOLD" | bc -l) -eq 1 ]; then
        echo "❌ Cost of \$$COST exceeds threshold of \$$THRESHOLD"
        exit 1
      else
        echo "✅ Cost of \$$COST is within budget"
      fi
    EOT
  }
}
```

## Best Practices

1. **Set Reasonable Thresholds:**
   - < $100: Auto-approve
   - $100-$1000: Team lead review
   - > $1000: Manager approval required

2. **Cost Context:**
   - Show cost per resource
   - Compare to baseline
   - Show trend over time

3. **Education:**
   - Explain why deployment was blocked
   - Suggest cheaper alternatives
   - Link to cost optimization docs

4. **Exceptions Process:**
   - Allow manual override with justification
   - Require manager approval
   - Log all exceptions

5. **Continuous Improvement:**
   - Track cost trends
   - Update policies based on learnings
   - Automate common optimizations

## Summary

Cost gates in CI/CD:
- Prevent expensive mistakes
- Educate developers on costs
- Enforce cost policies
- Enable informed decisions

**Key Tools:**
- Infracost (cost estimation)
- OPA (policy enforcement)
- Custom Lambda functions
- Pipeline integration

**Related Topics:**
- [Unit Economics](05-unit-economics.md)
- [Budgets and Alerts](07-budgets-alerts.md)
"""
}

def create_file(path, content):
    """Create file with content"""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write in chunks to avoid line limit
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created: {path}")

def main():
    print("🚀 Generating remaining FinOps content...")
    
    for filename, content in finops_intermediate.items():
        filepath = f"finops-learning/02-intermediate/{filename}"
        create_file(filepath, content)
    
    print("\n✅ FinOps Intermediate files created successfully!")

if __name__ == "__main__":
    main()
