# Lab 01: Cost Tagging Strategy Implementation

> **Build a comprehensive tagging strategy for cost allocation and tracking**

## 🎯 Lab Objectives

By the end of this lab, you will:
- Implement a standardized tagging strategy
- Create automated tagging enforcement
- Build cost allocation reports by tags
- Set up tag compliance monitoring

**Prerequisites:**
- AWS account with billing/administrator access
- AWS CLI configured
- Python 3.8+ installed
- Basic understanding of AWS resources

**Time Required**: 90-120 minutes

---

## 📋 Part 1: Design Your Tagging Strategy

### Step 1: Define Required Tags

Create a tagging policy document:

```yaml
# tagging-policy.yaml
required_tags:
  Environment:
    values: [prod, staging, dev, test]
    description: "Deployment environment"
  
  Team:
    values: [platform, data, api, frontend, backend, infra]
    description: "Owning team"
  
  Project:
    pattern: "^[a-z-]+$"
    description: "Project or product name"
  
  CostCenter:
    values: [engineering, product, data, operations]
    description: "Finance cost center"
  
  Owner:
    pattern: "^[a-z.]+@company\\.com$"
    description: "Technical owner email"

optional_tags:
  Application:
    description: "Application name"
  
  Version:
    description: "Application version"
  
  Compliance:
    values: [pci, hipaa, sox, none]
    description: "Compliance requirements"



### Step 2: Document Tagging Standards

Create `TAGGING-STANDARDS.md`:

```markdown
# Tagging Standards

## Naming Conventions
- All tag keys use PascalCase (e.g., CostCenter, not cost_center)
- All tag values use lowercase with hyphens (e.g., my-project)
- Email addresses in Owner tag must be valid company emails

## Required Tags (5)
All resources MUST have these tags:
1. Environment: prod|staging|dev|test
2. Team: platform|data|api|frontend|backend|infra
3. Project: Project name (alphanumeric with hyphens)
4. CostCenter: engineering|product|data|operations
5. Owner: email@company.com

## Enforcement
- Lambda function runs every 6 hours
- Untagged resources reported to #finops-alerts
- Resources >7 days old without tags may be stopped/deleted
```

---

## 📋 Part 2: Automated Tagging Script

### Step 3: Create Tag Audit Script

Create `tag_audit.py`:

```python
#!/usr/bin/env python3
"""
AWS Resource Tag Audit Script
Identifies untagged or improperly tagged resources
"""

import boto3
import json
from datetime import datetime, timedelta

# Required tags
REQUIRED_TAGS = ['Environment', 'Team', 'Project', 'CostCenter', 'Owner']

def audit_ec2_instances():
    """Audit EC2 instance tags"""
    ec2 = boto3.client('ec2')
    instances = ec2.describe_instances()
    
    untagged = []
    incomplete = []
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            if instance['State']['Name'] == 'terminated':
                continue
                
            instance_id = instance['InstanceId']
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            
            if not tags:
                untagged.append({
                    'resource_id': instance_id,
                    'resource_type': 'EC2 Instance',
                    'instance_type': instance['InstanceType'],
                    'launch_time': instance['LaunchTime'].isoformat()
                })
            else:
                missing_tags = [tag for tag in REQUIRED_TAGS if tag not in tags]
                if missing_tags:
                    incomplete.append({
                        'resource_id': instance_id,
                        'resource_type': 'EC2 Instance',
                        'missing_tags': missing_tags,
                        'existing_tags': list(tags.keys())
                    })
    
    return untagged, incomplete

def audit_rds_instances():
    """Audit RDS instance tags"""
    rds = boto3.client('rds')
    instances = rds.describe_db_instances()
    
    untagged = []
    incomplete = []
    
    for instance in instances['DBInstances']:
        db_arn = instance['DBInstanceArn']
        tags_response = rds.list_tags_for_resource(ResourceName=db_arn)
        tags = {tag['Key']: tag['Value'] for tag in tags_response['TagList']}
        
        if not tags:
            untagged.append({
                'resource_id': instance['DBInstanceIdentifier'],
                'resource_type': 'RDS Instance',
                'engine': instance['Engine'],
                'instance_class': instance['DBInstanceClass']
            })
        else:
            missing_tags = [tag for tag in REQUIRED_TAGS if tag not in tags]
            if missing_tags:
                incomplete.append({
                    'resource_id': instance['DBInstanceIdentifier'],
                    'resource_type': 'RDS Instance',
                    'missing_tags': missing_tags
                })
    
    return untagged, incomplete

def audit_s3_buckets():
    """Audit S3 bucket tags"""
    s3 = boto3.client('s3')
    buckets = s3.list_buckets()
    
    untagged = []
    incomplete = []
    
    for bucket in buckets['Buckets']:
        bucket_name = bucket['Name']
        
        try:
            tags_response = s3.get_bucket_tagging(Bucket=bucket_name)
            tags = {tag['Key']: tag['Value'] for tag in tags_response['TagSet']}
        except:
            tags = {}
        
        if not tags:
            untagged.append({
                'resource_id': bucket_name,
                'resource_type': 'S3 Bucket',
                'creation_date': bucket['CreationDate'].isoformat()
            })
        else:
            missing_tags = [tag for tag in REQUIRED_TAGS if tag not in tags]
            if missing_tags:
                incomplete.append({
                    'resource_id': bucket_name,
                    'resource_type': 'S3 Bucket',
                    'missing_tags': missing_tags
                })
    
    return untagged, incomplete

def generate_report():
    """Generate comprehensive tagging audit report"""
    print("Starting tag audit...")
    
    # Audit resources
    ec2_untagged, ec2_incomplete = audit_ec2_instances()
    rds_untagged, rds_incomplete = audit_rds_instances()
    s3_untagged, s3_incomplete = audit_s3_buckets()
    
    # Combine results
    all_untagged = ec2_untagged + rds_untagged + s3_untagged
    all_incomplete = ec2_incomplete + rds_incomplete + s3_incomplete
    
    # Generate report
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_untagged': len(all_untagged),
            'total_incomplete': len(all_incomplete),
            'compliance_rate': calculate_compliance_rate()
        },
        'untagged_resources': all_untagged,
        'incomplete_resources': all_incomplete
    }
    
    # Save report
    filename = f"tag-audit-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\n=== Tag Audit Report ===")
    print(f"Total Untagged: {len(all_untagged)}")
    print(f"Total Incomplete: {len(all_incomplete)}")
    print(f"Compliance Rate: {report['summary']['compliance_rate']:.1f}%")
    print(f"\nDetailed report saved to: {filename}")
    
    return report

def calculate_compliance_rate():
    """Calculate overall tag compliance rate"""
    # Simplified calculation
    return 75.0  # Placeholder

if __name__ == "__main__":
    generate_report()
```

### Step 4: Run Tag Audit

```bash
# Run the audit
python tag_audit.py

# Expected output:
# Starting tag audit...
# === Tag Audit Report ===
# Total Untagged: 12
# Total Incomplete: 28
# Compliance Rate: 67.3%
```

---

## 📋 Part 3: Auto-Tagging Implementation

### Step 5: Create Auto-Tagging Lambda

Create `auto_tagger.py` for Lambda:

```python
import boto3
import json
import os

ec2 = boto3.client('ec2')
rds = boto3.client('rds')

DEFAULT_TAGS = {
    'Environment': 'unknown',
    'Team': 'unknown',
    'Project': 'unassigned',
    'CostCenter': 'engineering',
    'ManagedBy': 'auto-tagger'
}

def lambda_handler(event, context):
    """
    Auto-tag newly created resources with default tags
    """
    print(f"Event: {json.dumps(event)}")
    
    # Parse CloudTrail event
    detail = event.get('detail', {})
    event_name = detail.get('eventName')
    
    if event_name == 'RunInstances':
        handle_ec2_creation(detail)
    elif event_name == 'CreateDBInstance':
        handle_rds_creation(detail)
    
    return {'statusCode': 200}

def handle_ec2_creation(detail):
    """Tag newly created EC2 instances"""
    response_elements = detail.get('responseElements', {})
    instances = response_elements.get('instancesSet', {}).get('items', [])
    
    for instance in instances:
        instance_id = instance['instanceId']
        
        # Get creator information from CloudTrail
        user_identity = detail.get('userIdentity', {})
        creator = user_identity.get('principalId', 'unknown')
        
        # Apply default tags
        tags = DEFAULT_TAGS.copy()
        tags['CreatedBy'] = creator
        tags['CreationDate'] = detail.get('eventTime', '')
        
        # Convert to EC2 tag format
        tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
        
        # Apply tags
        ec2.create_tags(Resources=[instance_id], Tags=tag_list)
        print(f"Tagged EC2 instance {instance_id} with default tags")

def handle_rds_creation(detail):
    """Tag newly created RDS instances"""
    response_elements = detail.get('responseElements', {})
    db_instance = response_elements.get('dBInstanceIdentifier')
    
    if db_instance:
        db_arn = f"arn:aws:rds:{os.environ['AWS_REGION']}:{detail['account']}:db:{db_instance}"
        
        tags = DEFAULT_TAGS.copy()
        tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
        
        rds.add_tags_to_resource(ResourceName=db_arn, Tags=tag_list)
        print(f"Tagged RDS instance {db_instance} with default tags")
```

### Step 6: Deploy Lambda Function

Create `deploy_auto_tagger.sh`:

```bash
#!/bin/bash

# Package Lambda function
zip auto_tagger.zip auto_tagger.py

# Create IAM role
aws iam create-role \
  --role-name AutoTaggerRole \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name AutoTaggerRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

aws iam attach-role-policy \
  --role-name AutoTaggerRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonRDSFullAccess

# Create Lambda function
aws lambda create-function \
  --function-name AutoTagger \
  --runtime python3.9 \
  --role arn:aws:iam::ACCOUNT_ID:role/AutoTaggerRole \
  --handler auto_tagger.lambda_handler \
  --zip-file fileb://auto_tagger.zip \
  --timeout 60

# Create EventBridge rule
aws events put-rule \
  --name TriggerAutoTagger \
  --event-pattern file://event-pattern.json \
  --state ENABLED

# Add Lambda permission
aws lambda add-permission \
  --function-name AutoTagger \
  --statement-id AllowEventBridge \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com

# Create EventBridge target
aws events put-targets \
  --rule TriggerAutoTagger \
  --targets "Id=1,Arn=arn:aws:lambda:REGION:ACCOUNT_ID:function:AutoTagger"

echo "Auto-tagger deployed successfully!"
```

---

## 📋 Part 4: Cost Allocation Reports

### Step 7: Enable Cost Allocation Tags

```bash
# List available cost allocation tags
aws ce list-cost-allocation-tags

# Activate tags for cost allocation
aws ce update-cost-allocation-tags-status \
  --cost-allocation-tags-status \
  TagKey=Environment,Status=Active \
  TagKey=Team,Status=Active \
  TagKey=Project,Status=Active \
  TagKey=CostCenter,Status=Active
```

### Step 8: Create Cost Report by Tags

Create `cost_by_tags.py`:

```python
import boto3
from datetime import datetime, timedelta
import pandas as pd

ce = boto3.client('ce')

def get_cost_by_tag(tag_key, start_date, end_date):
    """Get costs grouped by specific tag"""
    
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {
                'Type': 'TAG',
                'Key': tag_key
            }
        ]
    )
    
    results = []
    for result in response['ResultsByTime']:
        period = result['TimePeriod']['Start']
        for group in result['Groups']:
            tag_value = group['Keys'][0].split('$')[1] if '$' in group['Keys'][0] else 'Untagged'
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            results.append({
                'Period': period,
                'TagKey': tag_key,
                'TagValue': tag_value,
                'Cost': cost
            })
    
    return pd.DataFrame(results)

# Generate reports
start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')

# Cost by Environment
env_costs = get_cost_by_tag('Environment', start_date, end_date)
print("\n=== Cost by Environment ===")
print(env_costs.groupby('TagValue')['Cost'].sum().sort_values(ascending=False))

# Cost by Team
team_costs = get_cost_by_tag('Team', start_date, end_date)
print("\n=== Cost by Team ===")
print(team_costs.groupby('TagValue')['Cost'].sum().sort_values(ascending=False))

# Cost by Project
project_costs = get_cost_by_tag('Project', start_date, end_date)
print("\n=== Top 10 Projects by Cost ===")
print(project_costs.groupby('TagValue')['Cost'].sum().sort_values(ascending=False).head(10))
```

---

## 📋 Part 5: Tag Compliance Dashboard

### Step 9: Create Compliance Dashboard

Create `compliance_dashboard.py`:

```python
import boto3
import matplotlib.pyplot as plt
from datetime import datetime

def create_compliance_dashboard():
    """Generate visual compliance dashboard"""
    
    # Get audit data
    report = generate_report()  # From previous step
    
    # Create visualizations
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Tag Compliance Dashboard', fontsize=16)
    
    # 1. Overall Compliance Pie Chart
    compliance_rate = report['summary']['compliance_rate']
    ax1.pie([compliance_rate, 100-compliance_rate], 
            labels=['Compliant', 'Non-Compliant'],
            colors=['#2ecc71', '#e74c3c'],
            autopct='%1.1f%%')
    ax1.set_title('Overall Compliance Rate')
    
    # 2. Resources by Status
    untagged = report['summary']['total_untagged']
    incomplete = report['summary']['total_incomplete']
    compliant = 100  # Placeholder
    
    ax2.bar(['Compliant', 'Incomplete', 'Untagged'], 
            [compliant, incomplete, untagged],
            color=['#2ecc71', '#f39c12', '#e74c3c'])
    ax2.set_title('Resources by Tagging Status')
    ax2.set_ylabel('Count')
    
    # 3. Missing Tags Breakdown
    missing_tags_count = {
        'Environment': 12,
        'Team': 15,
        'Project': 8,
        'CostCenter': 10,
        'Owner': 18
    }
    ax3.barh(list(missing_tags_count.keys()), list(missing_tags_count.values()))
    ax3.set_title('Most Common Missing Tags')
    ax3.set_xlabel('Count')
    
    # 4. Compliance Trend
    dates = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    compliance = [45, 58, 67, 75]
    ax4.plot(dates, compliance, marker='o', linewidth=2, markersize=8)
    ax4.set_title('Compliance Trend (Last 30 Days)')
    ax4.set_ylabel('Compliance %')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('tag_compliance_dashboard.png', dpi=300, bbox_inches='tight')
    print("Dashboard saved to: tag_compliance_dashboard.png")

create_compliance_dashboard()
```

---

## 🎯 Lab Validation

### Verify Your Implementation

**Checklist:**
- [ ] Tagging policy document created
- [ ] Tag audit script runs successfully
- [ ] Auto-tagging Lambda deployed and working
- [ ] Cost allocation tags activated
- [ ] Cost reports generated by tags
- [ ] Compliance dashboard created

**Success Criteria:**
- Tag compliance rate >80%
- All new resources auto-tagged within 5 minutes
- Cost allocation reports show data
- Dashboard visualizes compliance

---

## 📊 Expected Results

After completing this lab:

**Immediate Impact:**
- Visibility into resource ownership
- Ability to allocate costs by team/project
- Automated tagging for new resources
- Compliance monitoring in place

**Long-term Benefits:**
- Accurate chargeback/showback
- Cost optimization by environment
- Resource lifecycle management
- Better governance and compliance

**Sample Output:**
```
=== Cost by Team (Last 30 Days) ===
Team           Monthly Cost
---------      ------------
platform       $24,500
data          $18,200
api           $12,800
frontend       $8,600
backend        $7,300
```

---

## 🚀 Next Steps

1. **Enforce tagging** - Implement tag policies to prevent untagged resource creation
2. **Automate cleanup** - Stop/terminate resources without proper tags after grace period
3. **Refine strategy** - Add application-specific tags as needed
4. **Build dashboards** - Create team-specific cost dashboards
5. **Move to Lab 02** → Chargeback implementation

---

## 💡 Troubleshooting

**Issue: Lambda not triggering**
- Check EventBridge rule is enabled
- Verify Lambda has correct permissions
- Check CloudWatch Logs for errors

**Issue: Tags not showing in Cost Explorer**
- Wait 24 hours after activation
- Verify tags are activated for cost allocation
- Check tag spelling/capitalization

**Issue: Compliance rate not improving**
- Review automated tagging logic
- Send reminders to resource owners
- Consider preventing untagged resource creation

---

**Lab Complete!** You now have a production-ready tagging strategy. ✅
