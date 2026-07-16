# What is AWS (Amazon Web Services)?

## Learning Objectives

By the end of this chapter, you will:
- Understand what AWS is and why it matters
- Learn the history and evolution of AWS
- Understand cloud computing fundamentals
- Know the key benefits of using AWS
- Understand AWS global infrastructure
- Learn about AWS service categories
- Understand AWS pricing models

---

## 🎯 What is AWS?

**Amazon Web Services (AWS)** is the world's most comprehensive and broadly adopted cloud platform, offering over 200 fully featured services from data centers globally.

### Simple Definition

AWS is a cloud computing platform that provides:
- **Compute power** (virtual servers)
- **Storage** (files, databases)
- **Networking** (connect resources)
- **Security** (protect data)
- **Many specialized services** (AI, analytics, IoT, etc.)

All available on-demand, pay-as-you-go, without owning physical hardware.

---

## 📖 History of AWS

### The Origin Story

**2002**: Amazon.com needed to scale its e-commerce infrastructure
- Built internal tools for reliability and scalability
- Realized these tools could help other companies

**2006**: AWS officially launched
- **March 2006**: S3 (Simple Storage Service)
- **August 2006**: EC2 (Elastic Compute Cloud)
- **Initial vision**: Provide infrastructure as a service

**2010s**: Rapid expansion
- Added 100+ services
- Became the market leader
- Netflix, Airbnb, and thousands adopted AWS

**Today (2026)**: 
- 200+ services
- 32+ geographic regions
- Millions of customers
- $80+ billion annual revenue

---

## ☁️ Cloud Computing Fundamentals

### What is Cloud Computing?

**Cloud computing** is the on-demand delivery of IT resources over the Internet with pay-as-you-go pricing.

### Traditional Infrastructure vs Cloud

**Traditional (On-Premises)**:
```
Buy servers → Install in data center → Configure → Maintain
├─ High upfront costs
├─ Long procurement time (weeks/months)
├─ Fixed capacity
├─ You manage everything
└─ Hardware becomes obsolete
```

**Cloud (AWS)**:
```
Click button → Server ready in minutes → Use → Pay only for usage
├─ No upfront costs
├─ Instant provisioning
├─ Scale up/down as needed
├─ AWS manages infrastructure
└─ Always latest technology
```

### Example: Launching a Web Server

**Traditional**:
1. Order server hardware (2-4 weeks)
2. Setup data center space
3. Install and configure (1-2 weeks)
4. Total: 4-6 weeks + $10,000+ upfront

**AWS**:
1. Click "Launch Instance"
2. Server ready in 60 seconds
3. Total: 1 minute + $0.01/hour

---

## 🌍 AWS Global Infrastructure

### Regions and Availability Zones

**AWS Region**: A geographic area with multiple data centers
- **32+ Regions worldwide** (2026)
- Examples: us-east-1 (N. Virginia), eu-west-1 (Ireland), ap-southeast-1 (Singapore)

**Availability Zone (AZ)**: One or more data centers within a Region
- Each Region has 3-6 AZs
- Isolated from each other for fault tolerance
- Connected with low-latency networking

```
AWS Global Infrastructure
│
├── Region: us-east-1 (N. Virginia)
│   ├── AZ: us-east-1a (Data center 1)
│   ├── AZ: us-east-1b (Data center 2)
│   ├── AZ: us-east-1c (Data center 3)
│   └── AZ: us-east-1d (Data center 4)
│
├── Region: eu-west-1 (Ireland)
│   ├── AZ: eu-west-1a
│   ├── AZ: eu-west-1b
│   └── AZ: eu-west-1c
│
└── Region: ap-southeast-1 (Singapore)
    ├── AZ: ap-southeast-1a
    ├── AZ: ap-southeast-1b
    └── AZ: ap-southeast-1c
```

**Edge Locations**: 400+ locations for content delivery (CloudFront CDN)

### Choosing a Region

Consider these factors:

**1. Compliance**: Data sovereignty requirements
```
Example: EU data must stay in EU regions
```

**2. Latency**: Proximity to users
```
Users in Asia → Choose ap-southeast-1
Users in Europe → Choose eu-west-1
```

**3. Service Availability**: Not all services in all regions
```
Check: aws.amazon.com/about-aws/global-infrastructure/regional-product-services/
```

**4. Cost**: Pricing varies by region
```
us-east-1 is often cheapest
eu regions typically 10-15% more expensive
```

---

## 💰 AWS Pricing Models

### Pay-As-You-Go

Pay only for what you use, no upfront commitment.

**Example: EC2 t2.micro**:
```
Cost: $0.0116 per hour
Running 24/7 for a month: $0.0116 × 24 × 30 = $8.35/month
Running 8 hours/day: $0.0116 × 8 × 30 = $2.78/month
```

### Save When You Reserve

**Reserved Instances**: Commit 1-3 years, save up to 75%
```
On-Demand: $8.35/month
1-year Reserved: $5.00/month (40% savings)
3-year Reserved: $3.00/month (64% savings)
```

### Pay Less by Using More

Volume discounts for services like S3:
```
First 50 TB: $0.023 per GB
Next 450 TB: $0.022 per GB  
Over 500 TB: $0.021 per GB
```

### AWS Free Tier

**Always Free**: Services with perpetual free tier
- Lambda: 1 million requests/month
- DynamoDB: 25 GB storage
- CloudWatch: 10 custom metrics

**12 Months Free**: After signing up
- EC2: 750 hours/month of t2.micro
- S3: 5 GB standard storage
- RDS: 750 hours/month of db.t2.micro

**Trials**: Short-term free trials
- SageMaker: 2 months
- Inspector: 90 days

---

## 🎨 AWS Service Categories

AWS offers 200+ services across 25+ categories. Here are the most important:

### 1. Compute

**EC2 (Elastic Compute Cloud)**: Virtual servers
```bash
# Launch a virtual server
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name my-key-pair
```

**Lambda**: Serverless compute (run code without servers)
```python
# Lambda function example
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
```

**ECS/EKS**: Container orchestration
**Elastic Beanstalk**: Platform as a Service (PaaS)

### 2. Storage

**S3 (Simple Storage Service)**: Object storage
```bash
# Upload file to S3
aws s3 cp myfile.txt s3://my-bucket/

# List objects
aws s3 ls s3://my-bucket/
```

**EBS (Elastic Block Store)**: Block storage for EC2
**EFS (Elastic File System)**: Shared file storage
**Glacier**: Long-term archival storage

### 3. Database

**RDS (Relational Database Service)**: Managed SQL databases
- MySQL, PostgreSQL, Oracle, SQL Server, MariaDB

**DynamoDB**: NoSQL database (key-value, document)
**Aurora**: High-performance MySQL/PostgreSQL compatible
**ElastiCache**: In-memory cache (Redis, Memcached)

### 4. Networking

**VPC (Virtual Private Cloud)**: Isolated network
**Route53**: DNS service
**CloudFront**: Content Delivery Network (CDN)
**API Gateway**: Create and manage APIs

### 5. Security & Identity

**IAM (Identity and Access Management)**: Users, roles, permissions
**KMS (Key Management Service)**: Encryption keys
**WAF (Web Application Firewall)**: Protect web apps
**Shield**: DDoS protection

### 6. Management & Monitoring

**CloudWatch**: Monitoring and logging
**CloudTrail**: API audit logs
**CloudFormation**: Infrastructure as Code
**Systems Manager**: Operations management

---

## ✅ Benefits of AWS

### 1. Agility

**Speed**: Launch resources in minutes
```
Traditional: Weeks to get a server
AWS: 60 seconds to launch EC2 instance
```

**Experimentation**: Try new ideas cheaply
```
Test new features with minimal cost
Fail fast without large investments
```

### 2. Cost Savings

**No Upfront Investment**:
```
Traditional data center: $100,000+ upfront
AWS: $0 upfront, pay $10/month if that's what you use
```

**Variable Expense**:
```
Pay only for what you consume
Scale costs with usage
No wasted capacity
```

### 3. Scalability

**Elastic**: Grow or shrink as needed
```bash
# Scale from 1 to 100 servers automatically
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name my-asg \
  --min-size 1 \
  --max-size 100
```

**Global in Minutes**: Deploy worldwide
```
Launch in multiple regions with a few clicks
Reach users globally with low latency
```

### 4. Reliability

**99.99% Availability**: Built for high availability
```
Multiple Availability Zones
Automatic failover
Redundant infrastructure
```

**Backup and Disaster Recovery**: Built-in
```bash
# Create automated backups
aws rds modify-db-instance \
  --db-instance-identifier mydb \
  --backup-retention-period 7
```

### 5. Security

**Security is Job Zero**: AWS's top priority
```
- Data encryption at rest and in transit
- Compliance certifications (SOC, PCI-DSS, HIPAA)
- DDoS protection
- Identity and access management
```

**Shared Responsibility Model**:
```
AWS Responsible For:
├─ Physical security
├─ Infrastructure
├─ Hardware
└─ Network

Customer Responsible For:
├─ Data encryption
├─ Application security
├─ Access management
└─ Configuration
```

---

## 🎯 Real-World Use Cases

### 1. Startup: Airbnb

**Challenge**: Rapid growth, unpredictable traffic
**Solution**: AWS auto-scaling and global infrastructure
**Result**: 
- Handle millions of bookings
- Scale for peak seasons
- Global presence in 200+ countries

### 2. Enterprise: Netflix

**Challenge**: Stream to 200+ million subscribers globally
**Solution**: AWS for compute, storage, and CDN
**Result**:
- 100% cloud-native
- Delivers 35% of internet traffic
- Streams to entire world

### 3. Government: CIA

**Challenge**: Secure, compliant cloud infrastructure
**Solution**: AWS GovCloud
**Result**:
- Top-secret workloads in cloud
- Compliance with strict regulations
- Modern infrastructure

### 4. Small Business: Local E-commerce

**Challenge**: Build online store with limited budget
**Solution**: AWS Free Tier + pay-as-you-go
**Result**:
- Launch for <$50/month
- Scale during holiday season
- Professional infrastructure

---

## 📊 AWS vs Competitors

### Market Share (2026)

| Provider | Market Share | Key Strength |
|----------|-------------|--------------|
| **AWS** | 32% | Most services, mature |
| Azure | 23% | Microsoft integration |
| Google Cloud | 11% | Data analytics, AI |
| Others | 34% | Specialized solutions |

### Why Choose AWS?

**Maturity**: 20 years of experience (since 2006)
**Breadth**: 200+ services vs 100-150 for competitors
**Global**: 32 regions vs 20-25 for others
**Community**: Largest cloud community
**Certifications**: Most recognized certifications

---

## 🎓 AWS Certifications

### Foundation

**AWS Certified Cloud Practitioner**:
- Entry-level certification
- Covers AWS basics
- No technical prerequisites
- Great starting point

### Associate Level

**Solutions Architect - Associate**:
- Design distributed systems
- Most popular cert
- Good for architects/developers

**Developer - Associate**:
- For application developers
- Focus on SDK and APIs

**SysOps Administrator - Associate**:
- For system administrators
- Focus on operations

### Professional Level

**Solutions Architect - Professional**:
- Advanced architecture
- Complex migrations

**DevOps Engineer - Professional**:
- CI/CD and automation
- Advanced operations

### Specialty

- Security
- Machine Learning
- Database
- Data Analytics
- Advanced Networking

---

## 🔧 Getting Started with AWS

### Step 1: Create Account

```
1. Visit aws.amazon.com
2. Click "Create an AWS Account"
3. Provide email and payment information
4. Choose support plan (Basic is free)
```

### Step 2: Secure Account

```bash
# Enable MFA for root account
1. Go to IAM Console
2. Click "Add MFA"
3. Use Google Authenticator or Authy
4. Scan QR code and verify
```

### Step 3: Create IAM User

```bash
# Never use root account for daily tasks!
1. Create IAM user with admin permissions
2. Enable MFA for IAM user
3. Use this for daily activities
```

### Step 4: Set Billing Alert

```bash
# Prevent unexpected charges
aws cloudwatch put-metric-alarm \
  --alarm-name billing-alert \
  --alarm-description "Alert when charges exceed $10" \
  --metric-name EstimatedCharges \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

### Step 5: Launch First Resource

```bash
# Launch first EC2 instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=MyFirstInstance}]'
```

---

## 🤔 Common Misconceptions

### Misconception 1: "AWS is too expensive"

**Reality**: AWS can be very cost-effective
- Free Tier for learning
- Pay only for what you use
- Often cheaper than on-premises
- Example: t2.micro runs for $8.35/month (vs $1000+ for physical server)

### Misconception 2: "AWS is only for big companies"

**Reality**: AWS serves all sizes
- Startups use it to launch quickly
- Small businesses benefit from not managing hardware
- Individuals use it for side projects
- Free Tier is perfect for learning

### Misconception 3: "AWS is not secure"

**Reality**: AWS is extremely secure
- More secure than most private data centers
- Compliance with major standards
- Shared Responsibility Model
- You control your security configuration

### Misconception 4: "I'll be locked into AWS"

**Reality**: Avoid vendor lock-in
- Use standard tools (Docker, Kubernetes)
- Infrastructure as Code (Terraform works multi-cloud)
- Data portability
- Many services have open-source alternatives

---

## 📚 Learning Resources

### Official AWS Resources

**Free Training**:
- AWS Skill Builder: https://skillbuilder.aws/
- AWS Training: https://aws.amazon.com/training/
- AWS Documentation: https://docs.aws.amazon.com/

**Hands-On**:
- AWS Free Tier: https://aws.amazon.com/free/
- AWS Workshops: https://workshops.aws/
- AWS Tutorials: https://aws.amazon.com/getting-started/

### Community Resources

**Forums & Communities**:
- AWS subreddit: r/aws
- AWS re:Post (Q&A forum)
- AWS User Groups (local meetups)

**Blogs & News**:
- AWS Blog: https://aws.amazon.com/blogs/
- AWS What's New: https://aws.amazon.com/new/
- Werner Vogels' blog (AWS CTO)

---

## 🎯 Key Takeaways

✅ **AWS is the leading cloud platform** with 200+ services and 32+ regions

✅ **Pay-as-you-go pricing** means no upfront costs, pay only for usage

✅ **Global infrastructure** enables worldwide deployment in minutes

✅ **Free Tier** provides hands-on learning at no cost

✅ **Shared Responsibility** - AWS secures infrastructure, you secure your data

✅ **Scalability** - grow from 1 user to millions without changing architecture

✅ **Certifications** validate your AWS knowledge and boost career

---

## ✏️ Practice Questions

**Q1**: What is the difference between a Region and an Availability Zone?
<details>
<summary>Answer</summary>
A Region is a geographic area (like US East) containing multiple Availability Zones. An Availability Zone is one or more data centers within a Region, isolated for fault tolerance but connected with low-latency networking.
</details>

**Q2**: What's included in AWS Free Tier for EC2?
<details>
<summary>Answer</summary>
750 hours per month of t2.micro instances for 12 months after signup. This allows you to run one t2.micro instance 24/7 for a year, or multiple instances within the 750-hour limit.
</details>

**Q3**: Who is responsible for patching the guest OS on an EC2 instance?
<details>
<summary>Answer</summary>
You (the customer) are responsible. Under the Shared Responsibility Model, AWS manages the hypervisor and physical infrastructure, but you manage the guest OS, applications, and data.
</details>

---

## 🚀 Next Steps

Continue your AWS journey:
- **Next Chapter**: [AWS Account Setup →](02-account-setup.md)
- **Hands-On**: [Quick Start Guide](../QUICK-START.md)
- **Practice**: Create your AWS account and explore the console

---

**Remember**: The best way to learn AWS is by doing. Start with the Free Tier and experiment!
