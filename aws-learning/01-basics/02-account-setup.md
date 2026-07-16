# AWS Account Setup & Best Practices

## Introduction

Setting up your AWS account correctly from the start is crucial for security, cost management, and operational efficiency. This chapter covers everything from creating your first AWS account to implementing production-ready best practices.

## Table of Contents
- [Creating Your AWS Account](#creating-your-aws-account)
- [Root Account Security](#root-account-security)
- [AWS Free Tier](#aws-free-tier)
- [Setting Up Billing Alerts](#setting-up-billing-alerts)
- [Account Organization](#account-organization)
- [Initial Configuration](#initial-configuration)
- [AWS CLI Setup](#aws-cli-setup)
- [Cost Management](#cost-management)
- [Security Best Practices](#security-best-practices)
- [Hands-on Exercise](#hands-on-exercise)

---

## Creating Your AWS Account

### Step-by-Step Account Creation

**Prerequisites:**
- Valid email address
- Credit/debit card
- Phone number for verification

**Steps:**

1. **Visit AWS Signup Page**
   ```
   URL: https://aws.amazon.com/free/
   ```

2. **Provide Account Information**
   ```
   - Root user email address
   - AWS account name (company/project name)
   - Password (minimum 8 characters)
   ```

3. **Contact Information**
   ```
   - Account type: Personal or Professional
   - Full name
   - Phone number
   - Address
   ```

4. **Payment Information**
   - Credit/debit card details
   - AWS charges $1 for verification (refunded)

5. **Identity Verification**
   - Automated phone call or SMS
   - Enter verification code

6. **Select Support Plan**
   - Basic (Free) - Recommended for learning
   - Developer ($29/month)
   - Business ($100/month)
   - Enterprise (Custom pricing)

### Account ID and Alias

After account creation:

```bash
# Your account ID is a 12-digit number
# Example: 123456789012

# Set a memorable account alias
aws iam create-account-alias --account-alias my-company-aws
```

**Signin URLs:**
```
# With account ID
https://123456789012.signin.aws.amazon.com/console

# With alias
https://my-company-aws.signin.aws.amazon.com/console
```

---

## Root Account Security

### What is the Root User?

The root user has **complete access** to all AWS services and resources. This account must be protected with the highest security measures.

### Securing Your Root Account

#### 1. Enable MFA (Multi-Factor Authentication)

**Using Virtual MFA (Recommended):**

```bash
# AWS Console Steps:
1. Sign in as root user
2. Navigate to: My Security Credentials
3. Click: Activate MFA
4. Choose: Virtual MFA device
5. Use authenticator app:
   - Google Authenticator
   - Authy
   - Microsoft Authenticator
6. Scan QR code
7. Enter two consecutive MFA codes
```

**CLI Verification:**
```bash
# Check MFA status
aws iam get-account-summary | grep AccountMFAEnabled
```

#### 2. Create Strong Password

```bash
# Password Requirements:
- Minimum 14 characters (recommended 20+)
- Mix of uppercase, lowercase, numbers, symbols
- No dictionary words
- Use password manager

# Example password generator (Linux/macOS):
openssl rand -base64 32
```

#### 3. Don't Use Root for Daily Operations

**Best Practice:**
- Use root only for account and service management tasks
- Create IAM users for daily operations
- Create IAM admin users for administrative tasks

#### 4. Monitor Root Account Activity

```bash
# Enable CloudTrail
aws cloudtrail create-trail \
  --name root-account-trail \
  --s3-bucket-name my-cloudtrail-bucket

# Create CloudWatch alarm for root usage
aws cloudwatch put-metric-alarm \
  --alarm-name root-account-usage \
  --alarm-description "Alert on root account usage" \
  --metric-name RootAccountUsage \
  --namespace AWS/CloudTrail \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold
```

---

## AWS Free Tier

### Understanding Free Tier

AWS offers three types of free tier offerings:

#### 1. Always Free
Services with permanent free tier limits:
```yaml
DynamoDB: 25 GB storage, 25 read/write capacity units
Lambda: 1 million requests/month
SNS: 1 million publishes/month
CloudWatch: 10 metrics, 10 alarms
API Gateway: 1 million API calls/month
```

#### 2. 12 Months Free
Available for 12 months starting from account creation:
```yaml
EC2: 750 hours/month of t2.micro or t3.micro instances
S3: 5 GB standard storage, 20,000 GET, 2,000 PUT requests
RDS: 750 hours/month of db.t2.micro, db.t3.micro, or db.t4g.micro
CloudFront: 50 GB data transfer out, 2 million HTTP/HTTPS requests
EBS: 30 GB of SSD or Magnetic storage
```

#### 3. Trials
Short-term free trials for specific services:
```yaml
SageMaker: 2 months free (250 hours/month)
Lightsail: 1 month free
Redshift: 2 months free (750 hours DC2.Large)
```

### Staying Within Free Tier

**Track Usage:**

```bash
# Check Free Tier usage via CLI
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://free-tier-filter.json
```

**free-tier-filter.json:**
```json
{
  "Tags": {
    "Key": "aws:createdBy",
    "Values": ["FreeTier"]
  }
}
```

**Free Tier Usage Alerts:**

```bash
# Create SNS topic for alerts
aws sns create-topic --name free-tier-alerts

# Subscribe your email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:free-tier-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com
```

---

## Setting Up Billing Alerts

### Enable Billing Alerts

**Step 1: Enable Billing Alerts in Console**
```
1. Sign in as root user
2. Navigate to: Billing Dashboard
3. Click: Billing Preferences
4. Check: Receive Billing Alerts
5. Save preferences
```

**Step 2: Create Budget Alert**

```bash
# Create a monthly budget
aws budgets create-budget \
  --account-id 123456789012 \
  --budget file://monthly-budget.json \
  --notifications-with-subscribers file://budget-notifications.json
```

**monthly-budget.json:**
```json
{
  "BudgetName": "Monthly-Budget",
  "BudgetLimit": {
    "Amount": "50",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {},
  "CostTypes": {
    "IncludeTax": true,
    "IncludeSubscription": true,
    "UseBlended": false
  }
}
```

**budget-notifications.json:**
```json
[
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "your-email@example.com"
      }
    ]
  },
  {
    "Notification": {
      "NotificationType": "FORECASTED",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 100,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "your-email@example.com"
      }
    ]
  }
]
```

### Cost Anomaly Detection

```bash
# Create cost anomaly monitor
aws ce create-anomaly-monitor \
  --anomaly-monitor file://anomaly-monitor.json
```

**anomaly-monitor.json:**
```json
{
  "MonitorName": "DailyCostMonitor",
  "MonitorType": "DIMENSIONAL",
  "MonitorDimension": "SERVICE"
}
```

---

## Account Organization

### Multi-Account Strategy

Even for learning, understanding account organization is important:

```
Root Account (Management Account)
│
├── Development Account
│   ├── Dev Environment
│   └── Test Environment
│
├── Production Account
│   ├── Staging Environment
│   └── Production Environment
│
└── Security/Audit Account
    ├── CloudTrail Logs
    └── Security Tools
```

### AWS Organizations Setup

```bash
# Create organization
aws organizations create-organization \
  --feature-set ALL

# Create organizational unit
aws organizations create-organizational-unit \
  --parent-id r-abc123 \
  --name Development

# Create account in organization
aws organizations create-account \
  --email dev-account@example.com \
  --account-name "Development Account"
```

### Service Control Policies (SCPs)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "ec2:InstanceType": [
            "t2.micro",
            "t3.micro"
          ]
        }
      }
    }
  ]
}
```

---

## Initial Configuration

### Region Selection

```bash
# List available regions
aws ec2 describe-regions --output table

# Set default region
aws configure set default.region us-east-1

# View current configuration
aws configure list
```

### Enable AWS Services

**Essential Services to Enable:**

```bash
# Enable CloudTrail
aws cloudtrail create-trail \
  --name my-trail \
  --s3-bucket-name my-cloudtrail-bucket \
  --is-multi-region-trail

aws cloudtrail start-logging --name my-trail

# Enable Config
aws configservice put-configuration-recorder \
  --configuration-recorder file://config-recorder.json

aws configservice put-delivery-channel \
  --delivery-channel file://delivery-channel.json

# Enable GuardDuty
aws guardduty create-detector --enable
```

### VPC Configuration

```bash
# Get default VPC
aws ec2 describe-vpcs --filters "Name=isDefault,Values=true"

# Create new VPC
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=MyVPC}]'
```

---

## AWS CLI Setup

### Installation

**Linux:**
```bash
# Download installer
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Unzip and install
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version
```

**macOS:**
```bash
# Using Homebrew
brew install awscli

# Verify
aws --version
```

**Windows (PowerShell):**
```powershell
# Using MSI installer
# Download from: https://awscli.amazonaws.com/AWSCLIV2.msi
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Verify
aws --version
```

### Configuration

```bash
# Configure AWS CLI
aws configure

# Prompts:
# AWS Access Key ID: [Your access key]
# AWS Secret Access Key: [Your secret key]
# Default region name: us-east-1
# Default output format: json

# Alternative: Use environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Named Profiles

```bash
# Create named profiles
aws configure --profile development
aws configure --profile production

# Use specific profile
aws s3 ls --profile development

# Set default profile
export AWS_PROFILE=development
```

**~/.aws/credentials:**
```ini
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[development]
aws_access_key_id = AKIAI44QH8DHBEXAMPLE
aws_secret_access_key = je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY

[production]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

### AWS CloudShell

AWS CloudShell is a browser-based shell:

```bash
# Access CloudShell from AWS Console
# Top navigation bar > CloudShell icon

# Pre-installed tools:
- AWS CLI v2
- Python 3
- Node.js
- Git
- Docker (in some regions)

# Persistent storage: 1 GB per region
```

---

## Cost Management

### Cost Explorer

```bash
# Enable Cost Explorer via Console
# Billing > Cost Explorer > Enable Cost Explorer

# Get cost and usage
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics "BlendedCost" "UnblendedCost" "UsageQuantity" \
  --group-by Type=DIMENSION,Key=SERVICE
```

### Cost Allocation Tags

```bash
# Activate cost allocation tags
aws ce update-cost-allocation-tags-status \
  --cost-allocation-tags-status file://tags.json
```

**tags.json:**
```json
[
  {
    "TagKey": "Environment",
    "Status": "Active"
  },
  {
    "TagKey": "Project",
    "Status": "Active"
  },
  {
    "TagKey": "Owner",
    "Status": "Active"
  }
]
```

### Savings Plans

```bash
# Describe Savings Plans offerings
aws savingsplans describe-savingsplans-offerings \
  --service-codes AmazonEC2,AWSLambda \
  --product-types EC2Instance,Lambda

# Purchase Savings Plan (example)
aws savingsplans create-savingsplan \
  --savings-plan-offering-id sp-off-123456 \
  --commitment 100 \
  --upfront-payment-amount 1000
```

### Cost Optimization Checklist

```yaml
Daily:
  - Review billing dashboard
  - Check running resources
  
Weekly:
  - Analyze Cost Explorer reports
  - Review unused resources
  
Monthly:
  - Analyze monthly bill
  - Review and adjust budgets
  - Check Trusted Advisor recommendations
  
Quarterly:
  - Review architecture for optimization
  - Evaluate Reserved Instances/Savings Plans
```

---

## Security Best Practices

### Account Security Checklist

```bash
# 1. Root account MFA ✓
aws iam get-account-summary | grep AccountMFAEnabled

# 2. Password policy
aws iam update-account-password-policy \
  --minimum-password-length 14 \
  --require-symbols \
  --require-numbers \
  --require-uppercase-characters \
  --require-lowercase-characters \
  --max-password-age 90 \
  --password-reuse-prevention 5

# 3. Enable CloudTrail
aws cloudtrail describe-trails

# 4. Enable GuardDuty
aws guardduty list-detectors

# 5. Enable Security Hub
aws securityhub enable-security-hub
```

### IAM Best Practices

```bash
# Create IAM admin group
aws iam create-group --group-name Administrators

# Attach admin policy
aws iam attach-group-policy \
  --group-name Administrators \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Create IAM user
aws iam create-user --user-name john.doe

# Add user to group
aws iam add-user-to-group \
  --group-name Administrators \
  --user-name john.doe

# Create access key
aws iam create-access-key --user-name john.doe
```

### Enable AWS Security Services

```bash
# Enable Config
aws configservice put-configuration-recorder \
  --configuration-recorder name=default,roleARN=arn:aws:iam::123456789012:role/config-role

# Enable GuardDuty
aws guardduty create-detector --enable

# Enable Security Hub
aws securityhub enable-security-hub \
  --enable-default-standards

# Enable Macie (data security)
aws macie2 enable-macie
```

---

## Hands-on Exercise

### Exercise 1: Secure Account Setup

**Objective:** Set up a secure AWS account following best practices

**Tasks:**

1. **Enable Root MFA**
   ```bash
   # Console: IAM > My Security Credentials > MFA
   # Use virtual MFA device
   ```

2. **Create Billing Alert**
   ```bash
   # Create budget
   aws budgets create-budget \
     --account-id $(aws sts get-caller-identity --query Account --output text) \
     --budget file://budget.json \
     --notifications-with-subscribers file://notifications.json
   ```

3. **Set Password Policy**
   ```bash
   aws iam update-account-password-policy \
     --minimum-password-length 14 \
     --require-symbols \
     --require-numbers \
     --require-uppercase-characters \
     --require-lowercase-characters
   ```

4. **Enable CloudTrail**
   ```bash
   # Create S3 bucket for logs
   aws s3 mb s3://my-cloudtrail-logs-$(date +%s)
   
   # Create trail
   aws cloudtrail create-trail \
     --name my-trail \
     --s3-bucket-name my-cloudtrail-logs-$(date +%s)
   
   # Start logging
   aws cloudtrail start-logging --name my-trail
   ```

### Exercise 2: Cost Management Setup

**Objective:** Set up comprehensive cost monitoring

**Tasks:**

1. **Enable Cost Explorer**
   - Console: Billing > Cost Explorer > Enable

2. **Create Cost Budget**
   ```bash
   # Monthly budget with alerts at 50%, 80%, 100%
   cat > monthly-budget.json << EOF
   {
     "BudgetName": "MonthlyBudget",
     "BudgetLimit": {
       "Amount": "100",
       "Unit": "USD"
     },
     "TimeUnit": "MONTHLY",
     "BudgetType": "COST"
   }
   EOF
   
   aws budgets create-budget \
     --account-id $(aws sts get-caller-identity --query Account --output text) \
     --budget file://monthly-budget.json
   ```

3. **Set Up Cost Anomaly Detection**
   ```bash
   aws ce create-anomaly-monitor \
     --anomaly-monitor '{
       "MonitorName": "ServiceCostMonitor",
       "MonitorType": "DIMENSIONAL",
       "MonitorDimension": "SERVICE"
     }'
   ```

### Exercise 3: Multi-Profile CLI Setup

**Objective:** Configure AWS CLI with multiple profiles

**Tasks:**

1. **Create Profiles**
   ```bash
   # Development profile
   aws configure --profile dev
   # Enter: access key, secret key, region=us-east-1, output=json
   
   # Production profile
   aws configure --profile prod
   # Enter: access key, secret key, region=us-west-2, output=json
   ```

2. **Test Profiles**
   ```bash
   # Test dev profile
   aws s3 ls --profile dev
   
   # Test prod profile
   aws s3 ls --profile prod
   
   # Set default profile
   export AWS_PROFILE=dev
   aws s3 ls
   ```

3. **Create Helper Script**
   ```bash
   cat > ~/.aws/switch-profile.sh << 'EOF'
   #!/bin/bash
   export AWS_PROFILE=$1
   echo "Switched to profile: $AWS_PROFILE"
   aws sts get-caller-identity
   EOF
   
   chmod +x ~/.aws/switch-profile.sh
   
   # Usage
   source ~/.aws/switch-profile.sh dev
   ```

---

## Validation Checklist

- [ ] AWS account created and accessible
- [ ] Root account has MFA enabled
- [ ] Strong root account password set
- [ ] Billing alerts configured
- [ ] Free Tier tracking enabled
- [ ] AWS CLI installed and configured
- [ ] Multiple CLI profiles set up
- [ ] CloudTrail enabled for logging
- [ ] Cost Explorer enabled
- [ ] Budget alerts created
- [ ] Password policy configured
- [ ] IAM admin user created
- [ ] Security services explored

---

## Troubleshooting

### Issue: Can't Access Account

```bash
# Check if using correct account ID
aws sts get-caller-identity

# Verify region
aws configure get region

# Test credentials
aws iam get-user
```

### Issue: Billing Alerts Not Working

```bash
# Verify billing alerts enabled
# Console: Billing > Billing Preferences

# Check SNS topic subscription
aws sns list-subscriptions

# Confirm email subscription
# Check email for confirmation link
```

### Issue: CLI Authentication Fails

```bash
# Verify credentials
cat ~/.aws/credentials

# Test with verbose output
aws s3 ls --debug

# Recreate access key
aws iam create-access-key --user-name your-username
```

---

## Best Practices Summary

1. **Security First**
   - Enable MFA on root account immediately
   - Don't use root for daily operations
   - Create IAM users with least privilege

2. **Cost Awareness**
   - Set up billing alerts before using services
   - Monitor Free Tier usage
   - Tag all resources consistently

3. **Organization**
   - Use multiple accounts for different environments
   - Implement clear naming conventions
   - Use AWS Organizations for multi-account management

4. **Monitoring**
   - Enable CloudTrail from day one
   - Set up Cost Explorer
   - Configure anomaly detection

5. **Documentation**
   - Keep track of account IDs and aliases
   - Document your organizational structure
   - Maintain inventory of IAM users and roles

---

## Next Steps

Now that your AWS account is set up securely:
1. ✓ Account created and secured
2. ✓ Billing alerts configured
3. ✓ AWS CLI installed
4. → **Next:** IAM Fundamentals (Chapter 3)
5. → Create your first EC2 instance (Chapter 4)

---

## Additional Resources

- [AWS Account Best Practices](https://aws.amazon.com/premiumsupport/knowledge-center/best-practices-root-user/)
- [AWS Free Tier Details](https://aws.amazon.com/free/)
- [AWS CLI User Guide](https://docs.aws.amazon.com/cli/latest/userguide/)
- [AWS Organizations Guide](https://docs.aws.amazon.com/organizations/)
- [Cost Management Best Practices](https://aws.amazon.com/aws-cost-management/resources/)
