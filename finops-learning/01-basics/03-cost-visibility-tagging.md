# Cost Visibility and Tagging Strategy

## Overview

Cost visibility is the foundation of FinOps. Without knowing where money goes, you can't optimize it. This guide covers AWS tagging strategies, cost allocation, and visibility tools for DevOps teams.

**Key Concepts:**
- Tag-based cost allocation
- Cost allocation reports
- Resource grouping
- Showback vs Chargeback
- Cost attribution strategies

---

## Why Cost Visibility Matters

### The Problem

```
Monthly AWS Bill: $850,000

Question: "Which team spent the most?"
Answer: "We don't know"

Question: "What's our cost per customer?"
Answer: "We don't know"

Question: "Which environment costs more - dev or prod?"
Answer: "We don't know"
```

**Without visibility, you can't:**
- Hold teams accountable
- Optimize effectively
- Plan budgets accurately
- Justify cloud spending to executives

---

## AWS Tagging Strategy

### Required Tags (Minimum)

Every AWS resource should have these tags:

```yaml
Required Tags:
  - Environment: dev | staging | prod
  - Owner: team-name or email
  - Application: app-name
  - CostCenter: cost-center-id
  - Project: project-name
```

### Recommended Tags

```yaml
Recommended Tags:
  - ManagedBy: terraform | cdk | manual
  - Compliance: pci | hipaa | sox | none
  - BackupPolicy: daily | weekly | none
  - DataClassification: public | internal | confidential | restricted
  - ExpirationDate: YYYY-MM-DD (for temporary resources)
```

### Example: EC2 Instance

```bash
# Tag an EC2 instance with required tags
aws ec2 create-tags \
  --resources i-1234567890abcdef0 \
  --tags \
    Key=Environment,Value=production \
    Key=Owner,Value=platform-team \
    Key=Application,Value=api-gateway \
    Key=CostCenter,Value=engineering-1001 \
    Key=Project,Value=customer-portal
```

---

## Implementing Tagging Policies

### 1. AWS Organizations Tag Policies

Define organization-wide tagging standards:

```json
{
  "tags": {
    "Environment": {
      "tag_key": {
        "@@assign": "Environment"
      },
      "tag_value": {
        "@@assign": [
          "dev",
          "staging",
          "prod"
        ]
      },
      "enforced_for": {
        "@@assign": [
          "ec2:instance",
          "rds:db",
          "s3:bucket",
          "lambda:function"
        ]
      }
    },
    "Owner": {
      "tag_key": {
        "@@assign": "Owner"
      },
      "enforced_for": {
        "@@assign": [
          "ec2:*",
          "rds:*",
          "s3:*"
        ]
      }
    },
    "CostCenter": {
      "tag_key": {
        "@@assign": "CostCenter"
      },
      "tag_value": {
        "@@assign": [
          "engineering-1001",
          "marketing-2001",
          "sales-3001"
        ]
      }
    }
  }
}
```

Apply tag policy to organization:

```bash
# Create tag policy
aws organizations create-policy \
  --content file://tag-policy.json \
  --description "Mandatory tagging policy" \
  --name "OrgTaggingPolicy" \
  --type TAG_POLICY

# Attach to root
aws organizations attach-policy \
  --policy-id p-12345678 \
  --target-id r-abcd
```

### 2. Terraform Enforce Tagging

```hcl
# variables.tf
variable "required_tags" {
  type = map(string)
  default = {
    Environment = ""
    Owner       = ""
    Application = ""
    CostCenter  = ""
    Project     = ""
  }
}

# Validate tags at apply time
resource "null_resource" "validate_tags" {
  triggers = {
    tags = jsonencode(var.required_tags)
  }

  provisioner "local-exec" {
    command = <<-EOT
      if [ -z "${var.required_tags["Environment"]}" ]; then
        echo "Error: Environment tag is required"
        exit 1
      fi
    EOT
  }
}

# Apply tags to all resources
locals {
  common_tags = merge(
    var.required_tags,
    {
      ManagedBy = "terraform"
      CreatedAt = timestamp()
    }
  )
}

resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t3.medium"
  
  tags = local.common_tags
}
```

### 3. Lambda Tag Enforcement

Automatically tag resources that are missing tags:

```python
# auto_tag_resources.py
import boto3
from datetime import datetime

def lambda_handler(event, context):
    """
    Automatically tag untagged resources
    Triggered by CloudWatch Events on resource creation
    """
    
    ec2 = boto3.client('ec2')
    
    # Get resource from CloudWatch Event
    resource_id = event['detail']['instance-id']
    
    # Check existing tags
    response = ec2.describe_tags(
        Filters=[
            {'Name': 'resource-id', 'Values': [resource_id]},
        ]
    )
    
    existing_tags = {tag['Key']: tag['Value'] for tag in response['Tags']}
    
    # Define required tags
    required_tags = ['Environment', 'Owner', 'CostCenter']
    missing_tags = [tag for tag in required_tags if tag not in existing_tags]
    
    if missing_tags:
        # Get user who created the resource
        user_arn = event['detail']['userIdentity']['arn']
        user_name = user_arn.split('/')[-1]
        
        # Apply default tags
        default_tags = {
            'Owner': user_name,
            'Environment': 'untagged',
            'CostCenter': 'unknown',
            'AutoTagged': 'true',
            'TaggedDate': datetime.now().isoformat()
        }
        
        tags_to_apply = [
            {'Key': k, 'Value': v} 
            for k, v in default_tags.items() 
            if k in missing_tags or k in ['AutoTagged', 'TaggedDate']
        ]
        
        ec2.create_tags(
            Resources=[resource_id],
            Tags=tags_to_apply
        )
        
        # Send notification
        sns = boto3.client('sns')
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:123456789012:untagged-resources',
            Subject=f'Resource {resource_id} auto-tagged',
            Message=f'Resource created by {user_name} was missing required tags. Default tags applied.'
        )
        
        return {
            'statusCode': 200,
            'body': f'Tagged {resource_id} with default values'
        }
    
    return {
        'statusCode': 200,
        'body': 'Resource already properly tagged'
    }
```

---

## Cost Allocation Reports

### 1. Enable Cost Allocation Tags

```bash
# Activate cost allocation tags
aws ce update-cost-allocation-tags-status \
  --cost-allocation-tags-status \
    TagKey=Environment,Status=Active \
    TagKey=Owner,Status=Active \
    TagKey=Application,Status=Active \
    TagKey=CostCenter,Status=Active \
    TagKey=Project,Status=Active
```

### 2. Generate Cost Reports by Tag

Python script to get costs by team:

```python
# cost_by_team.py
import boto3
from datetime import datetime, timedelta

def get_cost_by_tag(tag_key, start_date, end_date):
    """
    Get cost breakdown by tag
    """
    ce = boto3.client('ce')
    
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
    
    results = {}
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            tag_value = group['Keys'][0].split('$')[1]
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            results[tag_value] = results.get(tag_value, 0) + cost
    
    return results

# Usage
start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
end = datetime.now().strftime('%Y-%m-%d')

# Cost by team
team_costs = get_cost_by_tag('Owner', start, end)
print("\nCost by Team (Last 30 Days):")
for team, cost in sorted(team_costs.items(), key=lambda x: x[1], reverse=True):
    print(f"  {team:20s}: ${cost:,.2f}")

# Cost by environment
env_costs = get_cost_by_tag('Environment', start, end)
print("\nCost by Environment:")
for env, cost in sorted(env_costs.items(), key=lambda x: x[1], reverse=True):
    print(f"  {env:20s}: ${cost:,.2f}")
```

Output:

```
Cost by Team (Last 30 Days):
  platform-team       : $125,450.23
  data-team          : $98,320.15
  mobile-team        : $45,200.67
  web-team           : $38,920.45
  untagged           : $12,450.00  ⚠️

Cost by Environment:
  prod               : $245,680.50
  staging            : $45,320.00
  dev                : $29,341.00
```

---

## AWS Cost Categories

Create custom cost categories for better reporting:

```python
# create_cost_categories.py
import boto3

ce = boto3.client('ce')

# Create "Business Unit" category
response = ce.create_cost_category_definition(
    Name='BusinessUnit',
    RuleVersion='CostCategoryExpression.v1',
    Rules=[
        {
            'Value': 'Engineering',
            'Rule': {
                'Or': [
                    {
                        'Tags': {
                            'Key': 'Owner',
                            'Values': ['platform-team', 'api-team', 'data-team'],
                            'MatchOptions': ['EQUALS']
                        }
                    }
                ]
            }
        },
        {
            'Value': 'Product',
            'Rule': {
                'Tags': {
                    'Key': 'Owner',
                    'Values': ['product-team', 'design-team'],
                    'MatchOptions': ['EQUALS']
                }
            }
        },
        {
            'Value': 'Marketing',
            'Rule': {
                'Tags': {
                    'Key': 'CostCenter',
                    'Values': ['marketing-2001'],
                    'MatchOptions': ['STARTS_WITH']
                }
            }
        }
    ],
    DefaultValue='Unallocated'
)

print(f"Created Cost Category: {response['CostCategoryArn']}")
```

---

## Resource Groups

Group resources for easy cost tracking:

```bash
# Create resource group for production API
aws resource-groups create-group \
  --name production-api \
  --resource-query '{
    "Type": "TAG_FILTERS_1_0",
    "Query": "{\"ResourceTypeFilters\":[\"AWS::AllSupported\"],\"TagFilters\":[{\"Key\":\"Environment\",\"Values\":[\"prod\"]},{\"Key\":\"Application\",\"Values\":[\"api\"]}]}"
  }'

# Get resources in group
aws resource-groups list-group-resources \
  --group-name production-api
```

---

## Showback vs Chargeback

### Showback (Informational)

Teams see their costs but aren't financially charged:

```python
# showback_report.py
def generate_showback_report(team_name, month):
    """
    Generate showback report for team
    """
    costs = get_team_costs(team_name, month)
    
    report = f"""
    ╔═══════════════════════════════════════╗
    ║   Showback Report - {team_name}       
    ║   Month: {month}                      
    ╚═══════════════════════════════════════╝
    
    Total Cost: ${costs['total']:,.2f}
    
    Breakdown by Service:
      EC2:        ${costs['ec2']:,.2f}
      RDS:        ${costs['rds']:,.2f}
      S3:         ${costs['s3']:,.2f}
      Lambda:     ${costs['lambda']:,.2f}
      Other:      ${costs['other']:,.2f}
    
    Breakdown by Environment:
      Production: ${costs['prod']:,.2f}
      Staging:    ${costs['staging']:,.2f}
      Dev:        ${costs['dev']:,.2f}
    
    Cost Trend:
      Last Month: ${costs['last_month']:,.2f}
      Change:     {costs['change_pct']:+.1f}%
    
    Top 5 Most Expensive Resources:
      {format_top_resources(costs['top_resources'])}
    
    Recommendations:
      - Consider rightsizing instances (save $2,340/mo)
      - Enable S3 Intelligent Tiering (save $890/mo)
      - Use Spot instances for dev (save $1,560/mo)
    """
    
    return report
```

### Chargeback (Financial Transfer)

Teams are actually charged for their usage:

```python
# chargeback_system.py
def process_chargeback(month):
    """
    Process actual financial chargeback
    """
    teams = get_all_teams()
    
    for team in teams:
        # Get team's actual costs
        costs = get_team_costs(team['name'], month)
        
        # Apply markup (if infrastructure team provides services)
        markup = 1.15  # 15% overhead for platform team
        chargeback_amount = costs['total'] * markup
        
        # Create chargeback entry
        create_accounting_entry(
            team=team['name'],
            cost_center=team['cost_center'],
            amount=chargeback_amount,
            month=month,
            description=f'AWS Cloud Services - {month}'
        )
        
        # Send invoice
        send_invoice(
            to=team['manager_email'],
            amount=chargeback_amount,
            breakdown=costs,
            month=month
        )
        
        print(f"Chargeback processed: {team['name']} = ${chargeback_amount:,.2f}")
```

---

## Untagged Resources Detection

Find and report untagged resources:

```python
# find_untagged_resources.py
import boto3

def find_untagged_resources():
    """
    Find all resources without required tags
    """
    ec2 = boto3.client('ec2')
    rds = boto3.client('rds')
    s3 = boto3.client('s3')
    
    required_tags = ['Environment', 'Owner', 'CostCenter']
    untagged = []
    
    # Check EC2 instances
    instances = ec2.describe_instances()
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            missing = [t for t in required_tags if t not in tags]
            
            if missing:
                untagged.append({
                    'Type': 'EC2',
                    'Id': instance['InstanceId'],
                    'MissingTags': missing
                })
    
    # Check RDS databases
    databases = rds.describe_db_instances()
    for db in databases['DBInstances']:
        tags = rds.list_tags_for_resource(
            ResourceName=db['DBInstanceArn']
        )['TagList']
        tag_dict = {tag['Key']: tag['Value'] for tag in tags}
        missing = [t for t in required_tags if t not in tag_dict]
        
        if missing:
            untagged.append({
                'Type': 'RDS',
                'Id': db['DBInstanceIdentifier'],
                'MissingTags': missing
            })
    
    # Check S3 buckets
    buckets = s3.list_buckets()
    for bucket in buckets['Buckets']:
        try:
            tags = s3.get_bucket_tagging(Bucket=bucket['Name'])['TagSet']
            tag_dict = {tag['Key']: tag['Value'] for tag in tags}
        except:
            tag_dict = {}
        
        missing = [t for t in required_tags if t not in tag_dict]
        
        if missing:
            untagged.append({
                'Type': 'S3',
                'Id': bucket['Name'],
                'MissingTags': missing
            })
    
    return untagged

# Usage
untagged = find_untagged_resources()
print(f"\nFound {len(untagged)} untagged resources:\n")
for resource in untagged[:10]:  # Show first 10
    print(f"  {resource['Type']:5s} {resource['Id']:30s} Missing: {', '.join(resource['MissingTags'])}")
```

---

## Cost Visibility Dashboard

Create CloudWatch dashboard for cost visibility:

```python
# create_cost_dashboard.py
import boto3

cloudwatch = boto3.client('cloudwatch')

dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/Billing", "EstimatedCharges", {"stat": "Maximum"}]
                ],
                "period": 86400,
                "stat": "Maximum",
                "region": "us-east-1",
                "title": "Total Estimated Charges",
                "yAxis": {
                    "left": {
                        "label": "USD"
                    }
                }
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/Billing", "EstimatedCharges", {"dimensions": {"ServiceName": "EC2"}}],
                    ["...", {"dimensions": {"ServiceName": "RDS"}}],
                    ["...", {"dimensions": {"ServiceName": "S3"}}],
                    ["...", {"dimensions": {"ServiceName": "Lambda"}}]
                ],
                "period": 86400,
                "stat": "Maximum",
                "region": "us-east-1",
                "title": "Cost by Service"
            }
        }
    ]
}

response = cloudwatch.put_dashboard(
    DashboardName='CostVisibility',
    DashboardBody=json.dumps(dashboard_body)
)
```

---

## Best Practices

### 1. Tag Everything

- **Tag at creation** - Use Terraform/CDK defaults
- **Automate tagging** - Lambda functions for enforcement
- **Validate tags** - Pre-deployment checks in CI/CD

### 2. Consistent Naming

```yaml
# Good
Environment: prod
Owner: platform-team
Application: api-gateway

# Bad
Env: production
Team: Platform Team (capital letters, spaces)
App: API-GW (inconsistent abbreviation)
```

### 3. Use Tag Policies

- Enforce at organization level
- Define allowed values
- Prevent typos and inconsistencies

### 4. Regular Audits

```bash
# Weekly audit
0 9 * * 1 /scripts/find_untagged_resources.py | mail -s "Untagged Resources Report" platform@company.com
```

### 5. Cost Allocation Reports

- Enable in AWS Billing Console
- Export to S3 for analysis
- Create automated reports

---

## Common Mistakes

### ❌ Mistake 1: Inconsistent Tag Values

```yaml
# Multiple teams using different values for same environment
Environment: prod
Environment: production
Environment: PROD
Environment: prd
```

**Solution:** Use tag policies to enforce allowed values

### ❌ Mistake 2: Too Many Tags

```yaml
# 20+ tags that nobody uses
Region: us-east-1  # Already in resource ARN
CreatedBy: john@example.com
CreatedDate: 2026-01-15
ModifiedBy: jane@example.com
ModifiedDate: 2026-02-10
# ... 15 more tags
```

**Solution:** Start with 5-7 essential tags

### ❌ Mistake 3: Tags Only on Some Resources

```yaml
# EC2: fully tagged
# S3: partially tagged
# Lambda: not tagged
# RDS: not tagged
```

**Solution:** Enforce tagging in Terraform/CDK

---

## Tools

### AWS Native

- **Cost Explorer** - Visual cost analysis
- **Cost and Usage Reports** - Detailed CSV exports
- **Cost Allocation Tags** - Tag-based reporting
- **Cost Categories** - Custom grouping
- **Budgets** - Alerts on overspending

### Third-Party

- **CloudHealth** - Multi-cloud cost management
- **Cloudability** - FinOps platform
- **Vantage** - Real-time cost visibility
- **nOps** - AWS cost optimization
- **Kubecost** - Kubernetes cost visibility

---

## Summary

Cost visibility through tagging:

✅ **Implement consistent tagging strategy**
✅ **Enforce tags with policies**
✅ **Automate tagging for new resources**
✅ **Generate showback/chargeback reports**
✅ **Regular audits for untagged resources**
✅ **Use AWS Cost Categories for grouping**
✅ **Create cost dashboards**

**Next Steps:**
- Define your tagging standards
- Implement tag enforcement
- Enable cost allocation tags
- Create automated reports
- Establish showback/chargeback process

---

**Related Topics:**
- [Cost Optimization Strategies](../02-intermediate/06-cost-optimization-strategies.md)
- [Cloud Budgets and Alerts](../02-intermediate/07-budgets-alerts.md)
- [Unit Economics](../02-intermediate/08-unit-economics.md)
