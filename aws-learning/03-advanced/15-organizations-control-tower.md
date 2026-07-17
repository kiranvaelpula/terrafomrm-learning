# Chapter 15: AWS Organizations and Control Tower - Multi-Account Governance

## Overview

AWS Organizations enables you to centrally manage and govern multiple AWS accounts. Control Tower automates the setup of a secure, well-architected multi-account environment based on AWS best practices.

**What You'll Learn**
- AWS Organizations structure and hierarchy
- Service Control Policies (SCPs)
- AWS Control Tower setup and guardrails
- Account Factory for automated provisioning
- Consolidated billing and cost allocation
- Multi-account security best practices

**Prerequisites**
- AWS account with root access
- Understanding of IAM policies
- Basic AWS service knowledge
- Experience with AWS CLI

---

## AWS Organizations

### What is AWS Organizations?

AWS Organizations is a service for centrally managing multiple AWS accounts within your organization.

**Key Features:**
- Hierarchical account structure (OUs)
- Centralized billing
- Policy-based access control (SCPs)
- Automated account creation
- Service control across accounts

**Architecture:**
```
        Root (Management Account)
              |
    +---------+---------+
    |                   |
Production OU      Development OU
    |                   |
+---+---+           +---+---+
|       |           |       |
Prod-A Prod-B    Dev-A  Dev-B
```

### Creating an Organization

**Step 1: Enable Organizations**
```bash
# Create organization
aws organizations create-organization \
  --feature-set ALL

# Get organization details
aws organizations describe-organization
```


**Step 2: Create Organizational Units (OUs)**
```bash
# Get root ID
ROOT_ID=$(aws organizations list-roots --query 'Roots[0].Id' --output text)

# Create OUs
aws organizations create-organizational-unit \
  --parent-id $ROOT_ID \
  --name Production

aws organizations create-organizational-unit \
  --parent-id $ROOT_ID \
  --name Development

aws organizations create-organizational-unit \
  --parent-id $ROOT_ID \
  --name Shared-Services
```

**Step 3: Create Member Accounts**
```bash
# Create account
aws organizations create-account \
  --email prod-account@example.com \
  --account-name "Production Account"

# Move to OU
aws organizations move-account \
  --account-id 123456789012 \
  --source-parent-id $ROOT_ID \
  --destination-parent-id ou-prod-12345
```

---

## Service Control Policies (SCPs)

SCPs define maximum permissions for accounts in your organization.

### How SCPs Work

```
Root Account Permissions
    ↓
SCP (Deny S3 Delete)
    ↓
IAM Policy (Allow S3 *)
    ↓
Effective: Can read/write S3, but CANNOT delete
```

**Key Points:**
- SCPs don't grant permissions, they limit them
- Applied at OU or account level
- Root account unaffected by SCPs
- Explicit deny always wins

### Common SCP Examples

**1. Deny Region Outside Approved Regions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyAllOutsideAllowedRegions",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": [
            "us-east-1",
            "us-west-2",
            "eu-west-1"
          ]
        }
      }
    }
  ]
}
```

**2. Require MFA for Sensitive Actions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyDeleteWithoutMFA",
      "Effect": "Deny",
      "Action": [
        "ec2:TerminateInstances",
        "rds:DeleteDBInstance",
        "s3:DeleteBucket"
      ],
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

**3. Prevent IAM Changes in Production:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyIAMChanges",
      "Effect": "Deny",
      "Action": [
        "iam:CreateUser",
        "iam:DeleteUser",
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:AttachUserPolicy",
        "iam:DetachUserPolicy"
      ],
      "Resource": "*"
    }
  ]
}
```

**4. Deny Root User Actions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyRootAccount",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringLike": {
          "aws:PrincipalArn": "arn:aws:iam::*:root"
        }
      }
    }
  ]
}
```

**Attach SCP:**
```bash
# Create policy
aws organizations create-policy \
  --name RestrictRegions \
  --description "Limit operations to specific regions" \
  --type SERVICE_CONTROL_POLICY \
  --content file://scp-restrict-regions.json

# Attach to OU
aws organizations attach-policy \
  --policy-id p-12345678 \
  --target-id ou-prod-12345
```

---

## AWS Control Tower

Automated setup and governance for multi-account environments.

### What is Control Tower?

**Control Tower provides:**
- Pre-configured multi-account structure
- Guardrails (preventive and detective controls)
- Account Factory for automated provisioning
- Centralized logging and monitoring
- Compliance dashboard

**Architecture:**
```
Management Account
    ↓
Control Tower Setup
    ↓
    +-- Log Archive Account (CloudTrail, Config)
    +-- Audit Account (Security, compliance)
    +-- Organizational Units
        ↓
        +-- Sandbox OU
        +-- Production OU
        +-- Custom OUs
```

### Setting Up Control Tower

**Prerequisites:**
- AWS Organizations enabled
- Root account access
- Decide home region
- Plan OU structure

**Setup Steps:**

**1. Enable Control Tower:**
```bash
# Via Console (easiest)
1. Navigate to AWS Control Tower
2. Click "Set up landing zone"
3. Select home region
4. Configure OUs:
   - Security OU (Log Archive, Audit)
   - Sandbox OU
   - Additional custom OUs
5. Review and confirm
```

**Wait time: 30-60 minutes**

**2. Landing Zone Components:**
```
Created automatically:
✓ Log Archive account
✓ Audit account
✓ Organizational Units
✓ Guardrails (SCPs + Config rules)
✓ CloudTrail (organization-wide)
✓ AWS Config (all accounts)
✓ IAM Identity Center (SSO)
```

### Guardrails

**Types:**

**1. Preventive (SCPs)**
- Block actions
- Cannot be bypassed
- Example: "Disallow internet access from VPC"

**2. Detective (Config Rules)**
- Monitor and alert
- Don't prevent actions
- Example: "Detect unencrypted S3 buckets"

**3. Proactive**
- Scan IaC templates
- Prevent non-compliant deployments

**Guardrail Levels:**

**Mandatory:**
- Cannot be disabled
- Applied automatically
- Example: "Disallow public write access to S3"

**Strongly Recommended:**
- Should enable
- Best practices
- Example: "Enable MFA for root user"

**Elective:**
- Optional
- Based on requirements
- Example: "Disallow specific instance types"

### Common Guardrails

**1. Disallow Public Read Access to S3:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": [
      "s3:GetObject",
      "s3:ListBucket"
    ],
    "Resource": "*",
    "Condition": {
      "StringEquals": {
        "s3:x-amz-acl": [
          "public-read",
          "public-read-write"
        ]
      }
    }
  }]
}
```

**2. Detect Unencrypted EBS Volumes:**
```
Config Rule: encrypted-volumes
Triggers when: EBS volume created without encryption
Action: Alert to security team
```

**3. Require VPC Flow Logs:**
```
Config Rule: vpc-flow-logs-enabled
Checks: All VPCs have flow logs enabled
Action: Non-compliant if disabled
```

### Account Factory

Automated account provisioning with guardrails.

**Creating Account via Account Factory:**

**1. Via Service Catalog:**
```bash
# Account Factory provisions through Service Catalog
1. Navigate to Service Catalog
2. Select "AWS Control Tower Account Factory"
3. Fill in details:
   - Account name
   - Email
   - OU
   - SSO user
4. Launch product
```

**2. Account Factory Terraform:**
```hcl
resource "aws_servicecatalog_provisioned_product" "account" {
  name                     = "production-app-account"
  product_name            = "AWS Control Tower Account Factory"
  provisioning_artifact_name = "AWS Control Tower Account Factory"
  
  provisioning_parameters {
    key   = "AccountName"
    value = "Production App Account"
  }
  
  provisioning_parameters {
    key   = "AccountEmail"
    value = "prod-app@example.com"
  }
  
  provisioning_parameters {
    key   = "ManagedOrganizationalUnit"
    value = "Production (ou-prod-12345)"
  }
  
  provisioning_parameters {
    key   = "SSOUserEmail"
    value = "admin@example.com"
  }
  
  provisioning_parameters {
    key   = "SSOUserFirstName"
    value = "Admin"
  }
  
  provisioning_parameters {
    key   = "SSOUserLastName"
    value = "User"
  }
}
```

**What Gets Created:**
- New AWS account
- Baseline guardrails applied
- CloudTrail enabled
- Config enabled
- SSO user provisioned
- VPC (optional)

---

## Consolidated Billing

### Cost Management

**Benefits:**
- Single payer account
- Volume discounts
- Reserved Instance sharing
- Savings Plans sharing
- Consolidated reporting

**Cost Allocation:**
```bash
# Activate cost allocation tags
aws ce create-cost-category-definition \
  --name Department \
  --rules '[{
    "Value": "Engineering",
    "Rule": {
      "Tags": {
        "Key": "Department",
        "Values": ["Engineering"]
      }
    }
  }]'

# View costs by account
aws ce get-cost-and-usage \
  --time-period Start=2026-01-01,End=2026-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=LINKED_ACCOUNT
```

### Reserved Instance Sharing

```
Management Account buys 10 RIs
    ↓
Automatically shared across organization
    ↓
Account A uses 3 RIs
Account B uses 5 RIs
Account C uses 2 RIs
    ↓
All benefit from discounted rate
```

---

## Multi-Account Strategy

### Best Practices

**1. Account Structure:**
```
Root (Management Account)
├── Security OU
│   ├── Log Archive
│   └── Audit
├── Infrastructure OU
│   ├── Networking
│   └── Shared Services
├── Production OU
│   ├── Production-App1
│   └── Production-App2
├── Non-Production OU
│   ├── Development
│   ├── Staging
│   └── Testing
└── Sandbox OU
    └── Developer Sandboxes
```

**2. Cross-Account Access:**
```bash
# Assume role in another account
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/CrossAccountRole \
  --role-session-name my-session

# Use temporary credentials
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...
```

**3. Resource Sharing (RAM):**
```bash
# Share Transit Gateway
aws ram create-resource-share \
  --name shared-tgw \
  --resource-arns arn:aws:ec2:us-east-1:111111111111:transit-gateway/tgw-12345 \
  --principals arn:aws:organizations::111111111111:ou/o-abc/ou-prod-xyz
```

---

## Security and Compliance

### CloudTrail Organization Trail

```bash
# Create organization trail
aws cloudtrail create-trail \
  --name organization-trail \
  --s3-bucket-name organization-cloudtrail-bucket \
  --is-organization-trail \
  --is-multi-region-trail

# Start logging
aws cloudtrail start-logging --name organization-trail
```

### AWS Config Aggregator

```bash
# Create aggregator
aws configservice put-configuration-aggregator \
  --configuration-aggregator-name organization-aggregator \
  --organization-aggregation-source '{
    "RoleArn": "arn:aws:iam::123456789012:role/ConfigRole",
    "AllAwsRegions": true
  }'

# View compliance across accounts
aws configservice describe-aggregate-compliance-by-config-rules \
  --configuration-aggregator-name organization-aggregator
```

---

## Hands-On Exercise

### Task: Set Up Multi-Account Environment

**Scenario:** Create a production-ready multi-account structure.

**Step 1: Enable Organizations**
```bash
aws organizations create-organization --feature-set ALL
```

**Step 2: Create OU Structure**
```bash
ROOT_ID=$(aws organizations list-roots --query 'Roots[0].Id' --output text)

# Create OUs
aws organizations create-organizational-unit \
  --parent-id $ROOT_ID \
  --name Security

aws organizations create-organizational-unit \
  --parent-id $ROOT_ID \
  --name Production

aws organizations create-organizational-unit \
  --parent-id $ROOT_ID \
  --name Development
```

**Step 3: Create SCPs**
```bash
# Restrict regions
aws organizations create-policy \
  --name RestrictRegions \
  --type SERVICE_CONTROL_POLICY \
  --content file://scp-regions.json

# Attach to Production OU
aws organizations attach-policy \
  --policy-id p-12345 \
  --target-id ou-prod-12345
```

**Step 4: Create Member Accounts**
```bash
aws organizations create-account \
  --email prod-app@example.com \
  --account-name "Production Application"
```

**Step 5: Enable AWS Config**
```bash
# In each account
aws configservice put-configuration-recorder \
  --configuration-recorder name=default,roleARN=arn:aws:iam::123456789012:role/ConfigRole

aws configservice start-configuration-recorder \
  --configuration-recorder-name default
```

---

## Best Practices

**1. Management Account:**
- Use only for organizational management
- No application workloads
- Enable MFA for root user
- Restrict access

**2. Security:**
- Enable CloudTrail in all accounts
- Use AWS Config for compliance
- Implement SCPs for governance
- Regular security audits

**3. Cost Management:**
- Tag all resources
- Use cost allocation tags
- Set up budgets per account
- Regular cost reviews

**4. Operations:**
- Centralized logging (Log Archive account)
- Centralized security (Audit account)
- Automated account provisioning
- Infrastructure as Code

**5. Access:**
- Use IAM Identity Center (SSO)
- Implement least privilege
- Regular access reviews
- Role-based access control

---

## Summary

AWS Organizations provides centralized management of multiple AWS accounts with SCPs for governance and consolidated billing. Control Tower automates multi-account setup with pre-configured guardrails, Account Factory for provisioning, and compliance monitoring.

**Key Takeaways:**
- Organizations for multi-account management
- SCPs limit maximum permissions (deny-list approach)
- Control Tower for automated governance and landing zone
- Guardrails enforce compliance (preventive and detective)
- Account Factory for standardized provisioning via Service Catalog
- Consolidated billing with volume discounts and RI/SP sharing
- Multi-account strategy isolates workloads and improves security
- CloudTrail organization trails for centralized logging
- AWS Config aggregator for compliance across accounts
- IAM Identity Center (AWS SSO) for centralized access
- Use OUs to group accounts by function or environment
- Tag policies ensure consistent resource tagging
- Resource Access Manager (RAM) for cross-account sharing
- Implement least privilege with SCPs and IAM policies

**Real-World Multi-Account Structure:**
```
Root
├── Security OU
│   ├── Log Archive (CloudTrail, Config, VPC Flow Logs)
│   └── Security Tooling (GuardDuty, Security Hub, Inspector)
├── Infrastructure OU
│   ├── Network (Transit Gateway, Direct Connect, VPN)
│   └── Shared Services (Active Directory, DNS, Monitoring)
├── Workloads OU
│   ├── Production OU
│   │   ├── App1-Prod
│   │   ├── App2-Prod
│   │   └── Data-Prod
│   ├── Staging OU
│   │   ├── App1-Staging
│   │   └── App2-Staging
│   └── Development OU
│       ├── App1-Dev
│       └── App2-Dev
└── Sandbox OU
    ├── Developer-Sandbox-1
    └── Developer-Sandbox-2
```

**Cost Example (100 accounts):**
```
AWS Organizations: Free
Control Tower: Free
CloudTrail org trail: $2 + data ingestion
Config: $2/account/region = $200/month (100 accounts × 1 region)
Data storage: Varies by usage

Total overhead: ~$250-300/month for governance
Savings from consolidated billing: Typically 5-15% = $500-1500/month

Net benefit: $200-1200/month savings
```

**Next Chapter:** [16-ecs-eks.md](./16-ecs-eks.md) - Container Orchestration



---

## Advanced SCP Patterns

### Time-Based Restrictions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyOutsideBusinessHours",
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances",
        "rds:CreateDBInstance"
      ],
      "Resource": "*",
      "Condition": {
        "DateGreaterThan": {"aws:CurrentTime": "2026-01-01T17:00:00Z"},
        "DateLessThan": {"aws:CurrentTime": "2026-01-02T09:00:00Z"}
      }
    }
  ]
}
```

### Tag-Based Access Control

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RequireProjectTag",
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances",
        "rds:CreateDBInstance",
        "s3:CreateBucket"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotLike": {
          "aws:RequestTag/Project": "*"
        }
      }
    }
  ]
}
```

### Prevent Public Access

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyPublicS3",
      "Effect": "Deny",
      "Action": [
        "s3:PutBucketPublicAccessBlock",
        "s3:PutAccountPublicAccessBlock"
      ],
      "Resource": "*",
      "Condition": {
        "Bool": {
          "s3:BlockPublicAcls": "false"
        }
      }
    },
    {
      "Sid": "DenyPublicRDS",
      "Effect": "Deny",
      "Action": "rds:ModifyDBInstance",
      "Resource": "*",
      "Condition": {
        "Bool": {
          "rds:PubliclyAccessible": "true"
        }
      }
    }
  ]
}
```

---

## Control Tower Customizations

### Custom Guardrails

**Create Custom Guardrail (Config Rule):**
```python
import boto3

config = boto3.client('config')

# Custom rule: Require specific tags
response = config.put_config_rule(
    ConfigRule={
        'ConfigRuleName': 'required-tags',
        'Description': 'Ensures all EC2 instances have required tags',
        'Source': {
            'Owner': 'AWS',
            'SourceIdentifier': 'REQUIRED_TAGS'
        },
        'InputParameters': json.dumps({
            'tag1Key': 'Environment',
            'tag2Key': 'CostCenter',
            'tag3Key': 'Owner'
        }),
        'Scope': {
            'ComplianceResourceTypes': [
                'AWS::EC2::Instance'
            ]
        }
    }
)
```

### Customizations for Control Tower (CfCT)

**Use CloudFormation StackSets to deploy custom resources:**

```yaml
# manifest.yaml
---
resources:
  - name: VPCFlowLogsRole
    resource_file: templates/vpc-flow-logs-role.yaml
    deploy_method: stack_set
    deployment_targets:
      accounts:
        - ALL
    regions:
      - us-east-1
      - eu-west-1

  - name: RequiredTags
    resource_file: templates/required-tags-config-rule.yaml
    deploy_method: stack_set
    deployment_targets:
      organizational_units:
        - Production
        - Development
```

**templates/vpc-flow-logs-role.yaml:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: VPC Flow Logs IAM Role

Resources:
  FlowLogsRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: vpc-flow-logs.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: CloudWatchLogPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                  - logs:DescribeLogGroups
                  - logs:DescribeLogStreams
                Resource: '*'

Outputs:
  FlowLogsRoleArn:
    Value: !GetAtt FlowLogsRole.Arn
    Export:
      Name: VPCFlowLogsRoleArn
```

---

## Account Vending Machine (Automated Provisioning)

**Lambda-based Account Creation:**
```python
import boto3
import json

organizations = boto3.client('organizations')
servicecatalog = boto3.client('servicecatalog')

def lambda_handler(event, context):
    """
    Automated account creation via API/EventBridge
    """
    
    account_name = event['accountName']
    account_email = event['accountEmail']
    ou_id = event['organizationalUnitId']
    account_type = event.get('accountType', 'production')
    
    # Create account
    response = organizations.create_account(
        Email=account_email,
        AccountName=account_name,
        RoleName='OrganizationAccountAccessRole'
    )
    
    create_account_request_id = response['CreateAccountStatus']['Id']
    
    # Wait for account creation
    while True:
        status = organizations.describe_create_account_status(
            CreateAccountRequestId=create_account_request_id
        )
        
        state = status['CreateAccountStatus']['State']
        
        if state == 'SUCCEEDED':
            account_id = status['CreateAccountStatus']['AccountId']
            break
        elif state == 'FAILED':
            raise Exception(f"Account creation failed: {status['CreateAccountStatus']['FailureReason']}")
        
        time.sleep(5)
    
    # Move to correct OU
    organizations.move_account(
        AccountId=account_id,
        SourceParentId=get_root_id(),
        DestinationParentId=ou_id
    )
    
    # Tag account
    organizations.tag_resource(
        ResourceId=account_id,
        Tags=[
            {'Key': 'Type', 'Value': account_type},
            {'Key': 'CreatedBy', 'Value': 'AccountVendingMachine'},
            {'Key': 'CreatedAt', 'Value': datetime.utcnow().isoformat()}
        ]
    )
    
    # Apply baseline (optional)
    apply_account_baseline(account_id, account_type)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'accountId': account_id,
            'accountName': account_name,
            'message': 'Account created successfully'
        })
    }

def apply_account_baseline(account_id, account_type):
    """Apply security and compliance baseline"""
    
    # Assume role in new account
    sts = boto3.client('sts')
    assumed_role = sts.assume_role(
        RoleArn=f'arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole',
        RoleSessionName='BaselineSetup'
    )
    
    credentials = assumed_role['Credentials']
    
    # Create session for new account
    session = boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )
    
    # Enable CloudTrail
    cloudtrail = session.client('cloudtrail')
    cloudtrail.create_trail(
        Name='organization-trail',
        S3BucketName='organization-cloudtrail-bucket',
        IsOrganizationTrail=False,
        IsMultiRegionTrail=True
    )
    cloudtrail.start_logging(Name='organization-trail')
    
    # Enable Config
    config = session.client('config')
    config.put_configuration_recorder(
        ConfigurationRecorder={
            'name': 'default',
            'roleARN': f'arn:aws:iam::{account_id}:role/ConfigRole',
            'recordingGroup': {
                'allSupported': True,
                'includeGlobalResourceTypes': True
            }
        }
    )
    config.start_configuration_recorder(ConfigurationRecorderName='default')
    
    # Enable GuardDuty
    guardduty = session.client('guardduty')
    detector = guardduty.create_detector(Enable=True)
    
    print(f"Baseline applied to account {account_id}")
```

---

## Compliance and Auditing

### Compliance Dashboard

**Query Config Aggregator:**
```python
import boto3

config = boto3.client('config')

def get_compliance_summary():
    """Get compliance summary across all accounts"""
    
    response = config.describe_aggregate_compliance_by_config_rules(
        ConfigurationAggregatorName='organization-aggregator',
        Filters={
            'ComplianceType': 'NON_COMPLIANT'
        }
    )
    
    non_compliant = {}
    
    for rule in response['AggregateComplianceByConfigRules']:
        rule_name = rule['ConfigRuleName']
        account_id = rule['AccountId']
        region = rule['AwsRegion']
        
        if account_id not in non_compliant:
            non_compliant[account_id] = []
        
        non_compliant[account_id].append({
            'rule': rule_name,
            'region': region,
            'compliance': rule['Compliance']['ComplianceType']
        })
    
    return non_compliant

# Generate compliance report
compliance_data = get_compliance_summary()

for account_id, violations in compliance_data.items():
    print(f"\nAccount: {account_id}")
    print(f"Non-compliant rules: {len(violations)}")
    for violation in violations:
        print(f"  - {violation['rule']} ({violation['region']})")
```

### Automated Remediation

**Auto-remediate non-compliant resources:**
```python
import boto3

def lambda_handler(event, context):
    """
    Triggered by Config rule compliance change
    Automatically remediates common issues
    """
    
    rule_name = event['configRuleName']
    resource_id = event['configRuleInvokingEvent']['configurationItem']['resourceId']
    resource_type = event['configRuleInvokingEvent']['configurationItem']['resourceType']
    
    if rule_name == 'S3_BUCKET_PUBLIC_READ_PROHIBITED':
        remediate_public_s3_bucket(resource_id)
    
    elif rule_name == 'ENCRYPTED_VOLUMES':
        remediate_unencrypted_volume(resource_id)
    
    elif rule_name == 'EC2_INSTANCE_NO_PUBLIC_IP':
        remediate_public_ec2(resource_id)

def remediate_public_s3_bucket(bucket_name):
    """Block public access on S3 bucket"""
    s3 = boto3.client('s3')
    
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )
    
    print(f"Blocked public access on bucket: {bucket_name}")

def remediate_unencrypted_volume(volume_id):
    """Create encrypted snapshot and new volume"""
    ec2 = boto3.client('ec2')
    
    # Create snapshot
    snapshot = ec2.create_snapshot(
        VolumeId=volume_id,
        Description='Snapshot for encryption'
    )
    
    # Wait for snapshot
    waiter = ec2.get_waiter('snapshot_completed')
    waiter.wait(SnapshotIds=[snapshot['SnapshotId']])
    
    # Copy snapshot with encryption
    encrypted_snapshot = ec2.copy_snapshot(
        SourceSnapshotId=snapshot['SnapshotId'],
        Encrypted=True,
        KmsKeyId='alias/aws/ebs'
    )
    
    print(f"Created encrypted snapshot: {encrypted_snapshot['SnapshotId']}")
```

---

## Cost Allocation and Chargeback