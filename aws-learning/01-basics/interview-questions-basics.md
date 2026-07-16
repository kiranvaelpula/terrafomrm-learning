# AWS Basics - Interview Questions

## Introduction

This chapter contains commonly asked interview questions covering AWS fundamentals, EC2, S3, and IAM. Each question includes detailed answers with examples and best practices.

## Table of Contents
- [General AWS Questions](#general-aws-questions)
- [IAM Questions](#iam-questions)
- [EC2 Questions](#ec2-questions)
- [S3 Questions](#s3-questions)
- [Scenario-Based Questions](#scenario-based-questions)

---

## General AWS Questions

### Q1: What is AWS and what are its main benefits?

**Answer:**
AWS (Amazon Web Services) is a comprehensive cloud computing platform providing:

```yaml
Benefits:
  Cost-Effective:
    - Pay-as-you-go pricing
    - No upfront costs
    - Scale based on demand
    
  Global Infrastructure:
    - 30+ regions worldwide
    - 99+ availability zones
    - Low latency globally
    
  Scalability:
    - Scale up/down automatically
    - Handle traffic spikes
    - Elastic resources
    
  Security:
    - Multiple compliance certifications
    - Data encryption
    - Identity and access management
    
  Reliability:
    - High availability
    - Disaster recovery
    - Fault tolerance
```

### Q2: Explain AWS Regions and Availability Zones

**Answer:**
```yaml
Region:
  - Geographic area
  - Contains multiple AZs
  - Completely isolated
  - Example: us-east-1 (N. Virginia)
  
Availability Zone (AZ):
  - One or more data centers
  - Within a region
  - Physically separated
  - Connected via low-latency links
  - Example: us-east-1a, us-east-1b
  
Edge Locations:
  - Content delivery network (CDN)
  - CloudFront caching
  - 400+ locations worldwide
```


**Best Practice:**
- Deploy applications across multiple AZs for high availability
- Use multiple regions for disaster recovery
- Choose regions close to users for low latency

### Q3: What is the AWS Free Tier?

**Answer:**
AWS Free Tier offers three types:

```yaml
12 Months Free (from account creation):
  EC2: 750 hours/month t2.micro/t3.micro
  S3: 5 GB storage, 20K GET, 2K PUT requests
  RDS: 750 hours/month db.t2.micro
  CloudFront: 50 GB data transfer
  Lambda: 1M requests/month
  
Always Free:
  DynamoDB: 25 GB storage
  Lambda: 1M requests/month
  SNS: 1M publishes/month
  CloudWatch: 10 metrics, 10 alarms
  
Trials:
  SageMaker: 2 months (250 hours)
  Lightsail: 1 month free
  Redshift: 2 months (750 hours)
```

### Q4: What is the Shared Responsibility Model?

**Answer:**
Security division between AWS and customer:

```
AWS Responsibilities (Security OF the Cloud):
├── Physical security of data centers
├── Hardware and infrastructure
├── Network infrastructure
├── Hypervisor and managed services
└── Global infrastructure

Customer Responsibilities (Security IN the Cloud):
├── Data encryption
├── IAM user management
├── Application security
├── Network configuration (Security Groups, NACLs)
├── OS patches and updates
└── Client-side and server-side encryption
```

**Example:**
```bash
# AWS manages:
# - Physical servers
# - Network hardware
# - Hypervisor

# You manage:
# - EC2 instance OS updates
sudo yum update -y

# - Security group rules
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345 \
  --protocol tcp --port 22 \
  --cidr 10.0.0.0/8

# - IAM user permissions
# - Application code security
```

---

## IAM Questions

### Q5: What is IAM and its key components?

**Answer:**
IAM (Identity and Access Management) controls access to AWS resources:

```yaml
Components:
  Users:
    - Individual people or applications
    - Permanent credentials
    - Console and/or programmatic access
    
  Groups:
    - Collection of users
    - Shared permissions
    - Example: Developers, Admins
    
  Roles:
    - Temporary credentials
    - For services or federated users
    - No permanent keys
    
  Policies:
    - JSON documents
    - Define permissions
    - Attached to users, groups, or roles
```

**Example Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

### Q6: Difference between IAM Role and IAM User?

**Answer:**
```yaml
IAM User:
  Credentials: Permanent (access key, password)
  Use Case: Individual person or service account
  Access Keys: Yes
  MFA: Can be enabled
  Example: Developer accessing AWS Console
  
IAM Role:
  Credentials: Temporary (STS tokens)
  Use Case: EC2, Lambda, cross-account access
  Access Keys: Auto-rotated temporary credentials
  MFA: Not applicable
  Example: EC2 instance accessing S3
```

**When to use each:**
```bash
# Use IAM User for:
# - Individual developers
# - CI/CD systems (with rotation)
# - Third-party applications

# Use IAM Role for:
# - EC2 instances
# - Lambda functions
# - Cross-account access
# - Federated users
```

### Q7: What is the principle of least privilege?

**Answer:**
Grant only the minimum permissions required:

```bash
# BAD: Too permissive
{
  "Effect": "Allow",
  "Action": "*",
  "Resource": "*"
}

# GOOD: Specific permissions
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject"
  ],
  "Resource": "arn:aws:s3:::my-app-bucket/uploads/*"
}

# BETTER: With conditions
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::my-app-bucket/uploads/*",
  "Condition": {
    "IpAddress": {
      "aws:SourceIp": "10.0.0.0/8"
    }
  }
}
```

### Q8: How do you secure the root account?

**Answer:**
```yaml
Root Account Security:
  1. Enable MFA:
     - Virtual MFA (Google Authenticator)
     - Hardware MFA device
     
  2. Strong Password:
     - Minimum 20 characters
     - Use password manager
     
  3. Don't Use for Daily Operations:
     - Create IAM admin users
     - Use IAM roles for services
     
  4. Delete Access Keys:
     - Root account shouldn't have access keys
     
  5. Monitor Usage:
     - Enable CloudTrail
     - Set up CloudWatch alarms
     
  6. Lock Away Credentials:
     - Store securely
     - Limited access
```

---

## EC2 Questions

### Q9: What is EC2 and what are instance types?

**Answer:**
EC2 (Elastic Compute Cloud) provides virtual servers:

```yaml
Instance Type Categories:
  General Purpose (T, M):
    - Balanced compute, memory, networking
    - Use: Web servers, small databases
    - Examples: t3.micro, m6i.large
    
  Compute Optimized (C):
    - High-performance processors
    - Use: Batch processing, gaming
    - Examples: c6i.large, c6a.xlarge
    
  Memory Optimized (R, X):
    - Fast performance for memory-intensive workloads
    - Use: In-memory databases, caching
    - Examples: r6i.large, x2gd.xlarge
    
  Storage Optimized (I, D):
    - High IOPS, throughput
    - Use: NoSQL databases, data warehousing
    - Examples: i3.large, d3.xlarge
    
  Accelerated Computing (P, G):
    - GPU instances
    - Use: ML training, graphics rendering
    - Examples: p4d.24xlarge, g5.xlarge
```

### Q10: Difference between Stop and Terminate?

**Answer:**
```yaml
Stop:
  Data Loss: EBS root volume retained
  Cost: No compute charges, EBS charges continue
  IP Address: Public IP released, private IP retained
  Recovery: Can restart instance
  Use Case: Temporary shutdown
  
Terminate:
  Data Loss: Instance and root volume deleted (unless configured)
  Cost: All charges stop
  IP Address: All IPs released
  Recovery: Cannot recover
  Use Case: Permanent removal
```

**Example:**
```bash
# Stop instance (can restart)
aws ec2 stop-instances --instance-ids i-12345678

# Terminate instance (permanent)
aws ec2 terminate-instances --instance-ids i-12345678

# Prevent accidental termination
aws ec2 modify-instance-attribute \
  --instance-id i-12345678 \
  --disable-api-termination
```

### Q11: What are Security Groups?

**Answer:**
Security Groups are virtual firewalls:

```yaml
Characteristics:
  - Stateful (return traffic auto-allowed)
  - Only ALLOW rules (no DENY)
  - Operate at instance level
  - Can reference other security groups
  - Default: All inbound denied, all outbound allowed
  
Common Rules:
  SSH (22): Remote administration
  HTTP (80): Web traffic
  HTTPS (443): Secure web traffic
  RDP (3389): Windows remote desktop
  Custom TCP/UDP: Application-specific
```

**Example:**
```bash
# Create security group
aws ec2 create-security-group \
  --group-name web-sg \
  --description "Web server security group"

# Allow SSH from specific IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345 \
  --protocol tcp --port 22 \
  --cidr 203.0.113.25/32

# Allow HTTP from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345 \
  --protocol tcp --port 80 \
  --cidr 0.0.0.0/0

# Allow all traffic from another security group
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345 \
  --protocol -1 \
  --source-group sg-67890
```

### Q12: What is an AMI?

**Answer:**
AMI (Amazon Machine Image) is a template for EC2 instances:

```yaml
Components:
  - Operating system
  - Application server
  - Applications
  - Configuration settings
  - Block device mappings
  
Types:
  Amazon-provided:
    - Amazon Linux 2023
    - Ubuntu
    - Red Hat
    - Windows Server
    
  AWS Marketplace:
    - Pre-configured software
    - Paid AMIs
    
  Custom AMIs:
    - Created from your instances
    - Organization-specific
    
  Community AMIs:
    - Shared by AWS community
```

**Create Custom AMI:**
```bash
# Create AMI from running instance
aws ec2 create-image \
  --instance-id i-12345678 \
  --name "my-web-server-v1.0" \
  --description "Web server with Apache configured"

# Copy AMI to another region
aws ec2 copy-image \
  --source-region us-east-1 \
  --source-image-id ami-12345678 \
  --region us-west-2 \
  --name "my-web-server-v1.0-west"
```

---

## S3 Questions

### Q13: What is Amazon S3 and its use cases?

**Answer:**
S3 (Simple Storage Service) is object storage:

```yaml
Characteristics:
  - Unlimited storage
  - 99.999999999% (11 9's) durability
  - Object size: 0 bytes to 5 TB
  - Bucket names: Globally unique
  
Use Cases:
  Backup and Archive:
    - Database backups
    - Log archival
    - Disaster recovery
    
  Content Distribution:
    - Static website hosting
    - Media files
    - With CloudFront CDN
    
  Data Lakes:
    - Big data analytics
    - With Athena, EMR
    
  Application Storage:
    - User uploads
    - Application assets
    - Configuration files
```

### Q14: Explain S3 Storage Classes

**Answer:**
```yaml
STANDARD:
  Availability: 99.99%
  Use: Frequently accessed data
  Retrieval: Instant
  Cost: Highest storage cost
  
INTELLIGENT-TIERING:
  Availability: 99.9%
  Use: Unknown or changing access patterns
  Retrieval: Instant
  Cost: Automatic optimization + monitoring fee
  
STANDARD-IA:
  Availability: 99.9%
  Use: Infrequently accessed
  Retrieval: Instant + retrieval fee
  Cost: Lower storage, retrieval charges
  
ONE_ZONE-IA:
  Availability: 99.5%
  Use: Recreatable infrequent data
  Retrieval: Instant + retrieval fee
  Cost: Lowest IA option
  
GLACIER Instant Retrieval:
  Availability: 99.9%
  Use: Archive with immediate access
  Retrieval: Milliseconds
  Minimum: 90 days
  
GLACIER Flexible Retrieval:
  Availability: 99.99%
  Use: Archive backups
  Retrieval: Minutes to hours
  Minimum: 90 days
  
GLACIER Deep Archive:
  Availability: 99.99%
  Use: Long-term compliance
  Retrieval: 12 hours
  Minimum: 180 days
```

### Q15: What is S3 Versioning?

**Answer:**
Versioning keeps multiple versions of objects:

```yaml
Benefits:
  - Protect against accidental deletion
  - Recover from unintended overwrites
  - Compliance and audit requirements
  
States:
  Unversioned (default): No version tracking
  Versioning-enabled: All versions kept
  Versioning-suspended: New versions not created
  
Notes:
  - Once enabled, cannot be disabled (only suspended)
  - Each version consumes storage
  - Delete markers for deleted objects
```

**Example:**
```bash
# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-bucket \
  --versioning-configuration Status=Enabled

# Upload file (creates version 1)
aws s3 cp file.txt s3://my-bucket/

# Upload again (creates version 2)
aws s3 cp file.txt s3://my-bucket/

# List all versions
aws s3api list-object-versions --bucket my-bucket

# Get specific version
aws s3api get-object \
  --bucket my-bucket \
  --key file.txt \
  --version-id abc123 \
  file-v1.txt

# Delete creates delete marker (can be removed)
aws s3 rm s3://my-bucket/file.txt

# Permanent delete requires version ID
aws s3api delete-object \
  --bucket my-bucket \
  --key file.txt \
  --version-id abc123
```

### Q16: How do you secure S3 buckets?

**Answer:**
Multiple layers of security:

```yaml
1. Block Public Access:
   - Enabled by default
   - Account and bucket level
   - Prevents accidental exposure
   
2. Bucket Policies:
   - Resource-based policies
   - Control access at bucket level
   - Can allow/deny based on conditions
   
3. IAM Policies:
   - User/role-based permissions
   - Control what users can do
   
4. Access Control Lists (ACLs):
   - Legacy (use policies instead)
   - Object-level permissions
   
5. Encryption:
   - SSE-S3: AWS-managed keys
   - SSE-KMS: KMS-managed keys
   - SSE-C: Customer-provided keys
   - Client-side encryption
   
6. Versioning:
   - Protect against deletion
   - Enable MFA delete
   
7. Logging:
   - Server access logging
   - CloudTrail for API calls
   - Object-level logging
```

**Example Secure Bucket Setup:**
```bash
# Block all public access
aws s3api put-public-access-block \
  --bucket my-bucket \
  --public-access-block-configuration \
    BlockPublicAcls=true,\
    IgnorePublicAcls=true,\
    BlockPublicPolicy=true,\
    RestrictPublicBuckets=true

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-bucket \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket my-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Enable logging
aws s3api put-bucket-logging \
  --bucket my-bucket \
  --bucket-logging-status '{
    "LoggingEnabled": {
      "TargetBucket": "my-logs-bucket",
      "TargetPrefix": "s3-access-logs/"
    }
  }'
```

---

## Scenario-Based Questions

### Q17: Design a highly available web application

**Answer:**
```yaml
Architecture:
  Region: us-east-1
  
  Compute:
    - Multi-AZ deployment (us-east-1a, us-east-1b, us-east-1c)
    - Auto Scaling Group (2-10 instances)
    - EC2 instances: t3.medium
    - Application Load Balancer
    
  Storage:
    - S3 for static assets (HTML, CSS, JS, images)
    - EBS volumes for application data
    - RDS Multi-AZ for database
    
  Network:
    - VPC with public and private subnets
    - Public subnets: Load balancer
    - Private subnets: EC2 instances, RDS
    - NAT Gateway for outbound internet
    
  Security:
    - Security Groups:
      - ALB: Allow 80/443 from 0.0.0.0/0
      - EC2: Allow 80 from ALB only
      - RDS: Allow 3306 from EC2 only
    - IAM roles for EC2 to access S3
    
  Monitoring:
    - CloudWatch metrics and alarms
    - CloudWatch Logs for application logs
    - SNS for alerting
```

### Q18: Troubleshoot unable to SSH to EC2 instance

**Answer:**
```yaml
Checklist:
  1. Security Group Rules:
     - Is port 22 allowed?
     - Is your IP whitelisted?
     
  2. Network ACLs:
     - Check subnet NACL rules
     - Both inbound and outbound
     
  3. Instance State:
     - Is instance running?
     - Check system/instance status checks
     
  4. Key Pair:
     - Using correct .pem file?
     - Correct permissions (chmod 400)?
     
  5. Public IP:
     - Does instance have public IP?
     - Using correct IP/DNS?
     
  6. Route Tables:
     - Subnet has route to IGW?
     
  7. Username:
     - Amazon Linux: ec2-user
     - Ubuntu: ubuntu
     - Red Hat: ec2-user
```

**Debugging Commands:**
```bash
# Check security group rules
aws ec2 describe-security-groups \
  --group-ids sg-12345678

# Check instance status
aws ec2 describe-instance-status \
  --instance-ids i-12345678

# Get instance details
aws ec2 describe-instances \
  --instance-ids i-12345678

# Test connectivity
telnet <public-ip> 22
nc -zv <public-ip> 22

# SSH with verbose output
ssh -v -i mykey.pem ec2-user@<public-ip>

# Use Session Manager (no SSH required)
aws ssm start-session --target i-12345678
```

### Q19: Design a cost-optimized solution

**Answer:**
```yaml
Cost Optimization Strategies:
  
  Compute:
    - Use appropriate instance types
    - Reserved Instances for steady workloads
    - Spot Instances for fault-tolerant workloads
    - Auto Scaling to match demand
    - Stop non-production instances off-hours
    
  Storage:
    - S3 Intelligent-Tiering
    - Lifecycle policies to Glacier
    - Delete old snapshots
    - Use gp3 instead of gp2 (EBS)
    
  Network:
    - CloudFront to reduce data transfer
    - VPC endpoints to avoid NAT charges
    - Consolidate regions
    
  Database:
    - RDS Reserved Instances
    - Aurora Serverless for variable workloads
    - DynamoDB on-demand for unpredictable access
    
  Monitoring:
    - Cost Explorer for analysis
    - Budget alerts
    - Trusted Advisor recommendations
    - Tag resources for cost allocation
```

**Example Auto-Stop Script:**
```python
import boto3
from datetime import datetime

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    # Get all instances with Environment=Dev tag
    instances = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Environment', 'Values': ['Dev']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    instance_ids = []
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])
    
    if instance_ids:
        # Stop instances after work hours
        current_hour = datetime.now().hour
        if current_hour >= 18 or current_hour < 8:  # 6 PM to 8 AM
            ec2.stop_instances(InstanceIds=instance_ids)
            print(f"Stopped instances: {instance_ids}")
    
    return {
        'statusCode': 200,
        'body': f'Processed {len(instance_ids)} instances'
    }
```

### Q20: Handle sensitive data in AWS

**Answer:**
```yaml
Data Protection Strategy:
  
  In Transit:
    - TLS/SSL for all connections
    - VPN or Direct Connect for hybrid
    - HTTPS for S3 access
    
  At Rest:
    - S3: SSE-KMS with CMK
    - EBS: Encryption enabled
    - RDS: Encryption at creation
    - DynamoDB: Encryption enabled
    
  Access Control:
    - IAM roles with least privilege
    - MFA for sensitive operations
    - Resource-based policies
    - VPC endpoints (no internet exposure)
    
  Secrets Management:
    - AWS Secrets Manager
    - Systems Manager Parameter Store
    - Never hard-code credentials
    - Rotate credentials regularly
    
  Monitoring:
    - CloudTrail for API audit
    - Config for compliance
    - GuardDuty for threats
    - Macie for data discovery
    
  Compliance:
    - Enable required compliance checks
    - Regular security assessments
    - Data classification and tagging
```

**Example Secrets Management:**
```bash
# Store secret in Secrets Manager
aws secretsmanager create-secret \
  --name prod/database/password \
  --secret-string '{"username":"admin","password":"MySecureP@ss123"}' \
  --kms-key-id alias/my-cmk

# Retrieve secret in application
aws secretsmanager get-secret-value \
  --secret-id prod/database/password \
  --query 'SecretString' \
  --output text

# Rotate secret automatically
aws secretsmanager rotate-secret \
  --secret-id prod/database/password \
  --rotation-lambda-arn arn:aws:lambda:region:account:function:rotator
```

---

## Quick Reference

### Common AWS CLI Commands

```bash
# IAM
aws iam list-users
aws iam create-user --user-name john
aws iam attach-user-policy --user-name john --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# EC2
aws ec2 describe-instances
aws ec2 run-instances --image-id ami-12345 --instance-type t3.micro
aws ec2 stop-instances --instance-ids i-12345
aws ec2 terminate-instances --instance-ids i-12345

# S3
aws s3 ls
aws s3 mb s3://my-bucket
aws s3 cp file.txt s3://my-bucket/
aws s3 sync ./folder s3://my-bucket/folder/
aws s3 rm s3://my-bucket/file.txt
```

### Best Practices Summary

```yaml
Security:
  - Enable MFA on root account
  - Use IAM roles instead of access keys
  - Follow principle of least privilege
  - Enable CloudTrail and Config
  - Encrypt data at rest and in transit

High Availability:
  - Multi-AZ deployments
  - Auto Scaling Groups
  - Load balancers
  - Route 53 health checks

Cost Optimization:
  - Right-size resources
  - Use Reserved/Spot instances
  - Implement auto-scaling
  - Set up billing alerts
  - Delete unused resources

Performance:
  - Use CloudFront for content delivery
  - Implement caching (ElastiCache)
  - Choose appropriate instance types
  - Optimize S3 request patterns

Reliability:
  - Automated backups
  - Disaster recovery plan
  - Infrastructure as Code
  - Monitoring and alerting
```

---

## Interview Tips

1. **Understand the fundamentals** - Know core services deeply
2. **Think about use cases** - Real-world application of services
3. **Security first** - Always consider security in your answers
4. **Cost awareness** - Demonstrate cost-optimization knowledge
5. **Hands-on experience** - Mention practical examples from your work
6. **Stay current** - Know about newer services and features
7. **Well-Architected Framework** - Understand the five pillars

---

## Additional Resources

- [AWS Certified Cloud Practitioner Exam Guide](https://aws.amazon.com/certification/certified-cloud-practitioner/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS Whitepapers](https://aws.amazon.com/whitepapers/)
- [AWS FAQs](https://aws.amazon.com/faqs/)
