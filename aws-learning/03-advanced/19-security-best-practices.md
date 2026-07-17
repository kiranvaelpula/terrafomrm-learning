# Chapter 19: AWS Security Best Practices

## Overview

Comprehensive AWS security covers identity, network, data, applications, and operations. This chapter explores AWS security services and best practices.

**What You'll Learn**
- AWS Security Hub
- Amazon GuardDuty
- AWS WAF (Web Application Firewall)
- AWS Shield
- AWS Config
- Secrets Manager
- KMS encryption
- Security best practices

---

## AWS Security Hub

Centralized security and compliance dashboard.

```bash
# Enable Security Hub
aws securityhub enable-security-hub

# Enable standards
aws securityhub batch-enable-standards \
  --standards-subscription-requests StandardsArn=arn:aws:securityhub:us-east-1::standards/aws-foundational-security-best-practices/v/1.0.0

# Get findings
aws securityhub get-findings \
  --filters '{"SeverityLabel": [{"Value": "CRITICAL", "Comparison": "EQUALS"}]}'
```

---

## Amazon GuardDuty

Intelligent threat detection.

```bash
# Enable GuardDuty
aws guardduty create-detector --enable

# Get findings
aws guardduty list-findings --detector-id abc123

# Create SNS notification for findings
aws guardduty create-publishing-destination \
  --detector-id abc123 \
  --destination-type S3 \
  --destination-properties DestinationArn=arn:aws:s3:::my-findings-bucket
```

**Findings Types:**
- Recon: Port scanning, unusual API activity
- Instance Compromise: Cryptocurrency mining, backdoor
- Account Compromise: Unusual behavior, credential leaks
- Bucket Compromise: Data exfiltration, suspicious access

---

## AWS WAF

**Create Web ACL:**
```bash
# Create IP set
aws wafv2 create-ip-set \
  --name BlockedIPs \
  --scope REGIONAL \
  --ip-address-version IPV4 \
  --addresses 192.0.2.0/24 203.0.113.0/24

# Create Web ACL
aws wafv2 create-web-acl \
  --name MyWebACL \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules file://waf-rules.json
```

**waf-rules.json:**
```json
[
  {
    "Name": "RateLimitRule",
    "Priority": 1,
    "Statement": {
      "RateBasedStatement": {
        "Limit": 2000,
        "AggregateKeyType": "IP"
      }
    },
    "Action": {"Block": {}},
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "RateLimit"
    }
  },
  {
    "Name": "SQLiRule",
    "Priority": 2,
    "Statement": {
      "ManagedRuleGroupStatement": {
        "VendorName": "AWS",
        "Name": "AWSManagedRulesSQLiRuleSet"
      }
    },
    "OverrideAction": {"None": {}},
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "SQLi"
    }
  }
]
```

**Associate with ALB:**
```bash
aws wafv2 associate-web-acl \
  --web-acl-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/abc-123 \
  --resource-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/xyz
```

---

## AWS Shield

**Standard (Free):**
- Automatic DDoS protection
- Layer 3/4 attacks
- Always-on detection

**Advanced ($3,000/month):**
- Enhanced protection
- 24/7 DDoS Response Team
- Cost protection
- Layer 7 DDoS protection

```bash
# Enable Shield Advanced
aws shield create-protection \
  --name MyAppProtection \
  --resource-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/xyz
```

---

## AWS Secrets Manager

```bash
# Create secret
aws secretsmanager create-secret \
  --name prod/db/password \
  --secret-string '{"username":"admin","password":"MySecurePassword123"}'

# Retrieve secret
aws secretsmanager get-secret-value \
  --secret-id prod/db/password

# Enable auto-rotation
aws secretsmanager rotate-secret \
  --secret-id prod/db/password \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRotation \
  --rotation-rules AutomaticallyAfterDays=30
```

**Python Usage:**
```python
import boto3
import json

client = boto3.client('secretsmanager')

def get_secret(secret_name):
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Use secret
db_creds = get_secret('prod/db/password')
username = db_creds['username']
password = db_creds['password']
```

---

## KMS Encryption

```bash
# Create KMS key
aws kms create-key \
  --description "Application encryption key"

# Create alias
aws kms create-alias \
  --alias-name alias/my-app-key \
  --target-key-id key-id

# Encrypt data
aws kms encrypt \
  --key-id alias/my-app-key \
  --plaintext fileb://data.txt \
  --output text \
  --query CiphertextBlob | base64 --decode > encrypted.bin

# Decrypt data
aws kms decrypt \
  --ciphertext-blob fileb://encrypted.bin \
  --output text \
  --query Plaintext | base64 --decode
```

**S3 Encryption:**
```bash
# Enable default encryption
aws s3api put-bucket-encryption \
  --bucket my-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:us-east-1:123456789012:key/abc-123"
      },
      "BucketKeyEnabled": true
    }]
  }'
```

---

## AWS Config

Monitor configuration compliance.

```bash
# Enable Config
aws configservice put-configuration-recorder \
  --configuration-recorder name=default,roleARN=arn:aws:iam::123456789012:role/ConfigRole

# Create rule
aws configservice put-config-rule \
  --config-rule file://s3-bucket-public-read-prohibited.json
```

**s3-bucket-public-read-prohibited.json:**
```json
{
  "ConfigRuleName": "s3-bucket-public-read-prohibited",
  "Description": "Checks S3 buckets are not publicly readable",
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "S3_BUCKET_PUBLIC_READ_PROHIBITED"
  }
}
```

---

## IAM Best Practices

**1. Use MFA:**
```bash
# Enable MFA for root user
aws iam enable-mfa-device \
  --user-name root \
  --serial-number arn:aws:iam::123456789012:mfa/root \
  --authentication-code-1 123456 \
  --authentication-code-2 789012
```

**2. Least Privilege:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    }
  ]
}
```

**3. Use IAM Roles:**
```bash
# Create role for EC2
aws iam create-role \
  --role-name EC2-S3-Access \
  --assume-role-policy-document file://trust-policy.json

# Attach policy
aws iam attach-role-policy \
  --role-name EC2-S3-Access \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

**4. Rotate Credentials:**
```bash
# List access keys
aws iam list-access-keys --user-name myuser

# Create new key
aws iam create-access-key --user-name myuser

# Delete old key (after updating applications)
aws iam delete-access-key \
  --user-name myuser \
  --access-key-id AKIAIOSFODNN7EXAMPLE
```

---

## Network Security

**1. Security Groups (Stateful):**
```bash
# Allow HTTPS from specific CIDR
aws ec2 authorize-security-group-ingress \
  --group-id sg-123456 \
  --protocol tcp \
  --port 443 \
  --cidr 10.0.0.0/8

# Allow all from another SG
aws ec2 authorize-security-group-ingress \
  --group-id sg-backend \
  --protocol tcp \
  --port 8080 \
  --source-group sg-frontend
```

**2. NACLs (Stateless):**
```bash
# Create NACL rule
aws ec2 create-network-acl-entry \
  --network-acl-id acl-123456 \
  --rule-number 100 \
  --protocol tcp \
  --port-range From=443,To=443 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow
```

**3. VPC Flow Logs:**
```bash
# Enable flow logs
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-123456 \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/flowlogs
```

---

## Data Protection

**1. S3 Bucket Policies:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "Bool": {"aws:SecureTransport": "false"}
      }
    }
  ]
}
```

**2. Block Public Access:**
```bash
aws s3api put-public-access-block \
  --bucket my-bucket \
  --public-access-block-configuration \
    BlockPublicAcls=true,\
    IgnorePublicAcls=true,\
    BlockPublicPolicy=true,\
    RestrictPublicBuckets=true
```

**3. Versioning and MFA Delete:**
```bash
# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-bucket \
  --versioning-configuration Status=Enabled,MFADelete=Enabled \
  --mfa "arn:aws:iam::123456789012:mfa/root 123456"
```

---

## Compliance and Auditing

**AWS CloudTrail:**
```bash
# Create trail
aws cloudtrail create-trail \
  --name my-trail \
  --s3-bucket-name my-cloudtrail-bucket \
  --is-multi-region-trail

# Start logging
aws cloudtrail start-logging --name my-trail

# Query with CloudTrail Insights
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=RunInstances
```

---

## Incident Response

**1. Automate Response:**
```python
# Lambda function for auto-remediation
def lambda_handler(event, context):
    # Security Hub finding
    finding = event['detail']['findings'][0]
    
    if finding['Title'] == 'S3 Bucket Public Read':
        bucket = finding['Resources'][0]['Id'].split(':')[-1]
        
        # Block public access
        s3 = boto3.client('s3')
        s3.put_public_access_block(
            Bucket=bucket,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
```

**2. Forensics:**
- Take EBS snapshots
- Isolate instances (change security groups)
- Capture memory dumps
- Preserve logs

---

## Summary

AWS provides comprehensive security tools: Security Hub for centralized monitoring, GuardDuty for threat detection, WAF for application protection, Shield for DDoS, Secrets Manager for credentials, KMS for encryption, and Config for compliance.

**Next Chapter:** [20-cost-optimization.md](./20-cost-optimization.md)

