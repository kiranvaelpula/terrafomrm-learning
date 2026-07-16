# AWS Services Covered in This Guide

Complete list of AWS services and topics covered across all chapters.

**Last Updated**: July 16, 2026  
**Total Services**: 45+ AWS services

---

## 🎯 Core Services

### Compute (6 services)
- ✅ **EC2** - Elastic Compute Cloud (Virtual Machines)
- ✅ **Lambda** - Serverless Functions
- ✅ **ECS** - Elastic Container Service
- ✅ **EKS** - Elastic Kubernetes Service
- ✅ **Fargate** - Serverless Container Compute
- ✅ **Elastic Beanstalk** - Platform as a Service

### Storage (5 services)
- ✅ **S3** - Simple Storage Service (Object Storage)
- ✅ **EBS** - Elastic Block Store
- ✅ **EFS** - Elastic File System
- ✅ **Storage Gateway** - Hybrid Cloud Storage
- ✅ **FSx** - Managed File Systems

### Database (6 services)
- ✅ **RDS** - Relational Database Service
- ✅ **Aurora** - High-Performance Relational Database
- ✅ **DynamoDB** - NoSQL Database
- ✅ **ElastiCache** - In-Memory Cache (Redis/Memcached)
- ✅ **Redshift** - Data Warehouse
- ✅ **DocumentDB** - MongoDB-Compatible Database

---

## 🌐 Networking & Content Delivery

### Networking (8 services)
- ✅ **VPC** - Virtual Private Cloud
- ✅ **Route53** - DNS and Domain Management
  - Public Hosted Zones
  - Private Hosted Zones
  - Routing Policies
  - Health Checks
- ✅ **CloudFront** - Content Delivery Network (CDN)
- ✅ **API Gateway** - API Management
- ✅ **Direct Connect** - Dedicated Network Connection
- ✅ **Transit Gateway** - Network Hub
- ✅ **PrivateLink** - Private Connectivity
- ✅ **Global Accelerator** - Network Performance Optimizer

### Load Balancing (3 types)
- ✅ **Application Load Balancer (ALB)** - Layer 7
- ✅ **Network Load Balancer (NLB)** - Layer 4
- ✅ **Classic Load Balancer (CLB)** - Legacy

---

## 🔒 Security, Identity & Compliance

### Identity & Access (4 services)
- ✅ **IAM** - Identity and Access Management
  - Users, Groups, Roles
  - Policies and Permissions
  - MFA
  - Identity Federation
- ✅ **AWS Organizations** - Multi-Account Management
  - Service Control Policies (SCPs)
  - Organizational Units (OUs)
  - Consolidated Billing
- ✅ **AWS Control Tower** - Landing Zone & Governance ⭐ NEW
  - Account Factory
  - Guardrails
  - Dashboard
  - Compliance Management
- ✅ **AWS SSO** - Single Sign-On

### Security Services (7 services)
- ✅ **KMS** - Key Management Service
- ✅ **Secrets Manager** - Secret Storage
- ✅ **Certificate Manager** - SSL/TLS Certificates
- ✅ **WAF** - Web Application Firewall
- ✅ **Shield** - DDoS Protection
- ✅ **GuardDuty** - Threat Detection
- ✅ **Security Hub** - Security Posture Management

### Compliance (3 services)
- ✅ **CloudTrail** - API Audit Logs
- ✅ **Config** - Resource Configuration Tracking
- ✅ **Artifact** - Compliance Reports

---

## 📊 Management & Monitoring

### Monitoring (4 services)
- ✅ **CloudWatch** - Monitoring and Observability
  - Metrics
  - Logs
  - Alarms
  - Dashboards
  - Insights
- ✅ **X-Ray** - Distributed Tracing
- ✅ **Systems Manager** - Operations Management
- ✅ **Personal Health Dashboard** - AWS Status

### Automation (2 services)
- ✅ **CloudFormation** - Infrastructure as Code
- ✅ **AWS CDK** - Cloud Development Kit

---

## 🚀 Developer Tools & CI/CD

### Source Control & Build (4 services)
- ✅ **CodeCommit** - Git Repositories
- ✅ **CodeBuild** - Build Service
- ✅ **CodeDeploy** - Deployment Service
- ✅ **CodePipeline** - CI/CD Pipeline

### Additional Tools (2 services)
- ✅ **CodeArtifact** - Artifact Repository
- ✅ **Cloud9** - Cloud IDE

---

## 🔄 Integration & Messaging

### Application Integration (5 services)
- ✅ **SQS** - Simple Queue Service
- ✅ **SNS** - Simple Notification Service
- ✅ **EventBridge** - Event Bus
- ✅ **Step Functions** - Workflow Orchestration
- ✅ **AppSync** - Managed GraphQL

---

## 💰 Cost Management

### Cost Tools (3 services)
- ✅ **Cost Explorer** - Cost Analysis
- ✅ **Budgets** - Cost Alerts
- ✅ **Cost and Usage Reports** - Detailed Billing

### Cost Optimization
- ✅ **Reserved Instances** - Compute Savings
- ✅ **Savings Plans** - Flexible Savings
- ✅ **Spot Instances** - Low-Cost Compute

---

## 📍 Coverage by Chapter

### Basics (6 chapters)
**Services Covered**: 5 services
- IAM fundamentals
- EC2 basics
- S3 basics
- Basic networking concepts
- AWS account management

### Intermediate (9 chapters)
**Services Covered**: 15 services
- VPC and networking
- Load balancers (ALB, NLB, CLB)
- Auto Scaling Groups
- RDS and Aurora
- Lambda and serverless
- **Route53 and Hosted Zones** ⭐ NEW
  - Public hosted zones
  - Private hosted zones
  - Routing policies (Simple, Weighted, Latency, Failover, Geolocation, Geoproximity)
  - Health checks
  - Traffic flow
- CloudWatch monitoring
- CloudFormation IaC

### Advanced (11 chapters)
**Services Covered**: 25+ services
- Advanced VPC (Peering, PrivateLink, Transit Gateway)
- **AWS Organizations & Control Tower** ⭐ NEW
  - Multi-account strategy
  - Landing Zone setup
  - Service Control Policies
  - Guardrails and compliance
- Container orchestration (ECS, EKS)
- API Gateway
- Event-driven architecture (EventBridge, SQS, SNS)
- Security best practices (GuardDuty, Security Hub, WAF)
- Cost optimization strategies
- Multi-region architecture
- Disaster recovery patterns

---

## 🎯 Special Focus Topics

### Multi-Account Governance ⭐ NEW
**Chapter**: 15-organizations-control-tower.md

**AWS Organizations**:
- Account structure design
- Organizational Units (OUs)
- Service Control Policies (SCPs)
- Consolidated billing
- Cross-account access

**AWS Control Tower**:
- Landing Zone setup
- Account Factory
- Guardrails (preventive & detective)
- Dashboard and compliance
- Integration with Organizations
- Best practices for governance

**Real-World Scenarios**:
- Enterprise multi-account setup
- Development/staging/production isolation
- Compliance enforcement
- Centralized logging and security

---

### DNS & Hosted Zones ⭐ NEW
**Chapter**: 11-route53-hosted-zones.md

**Route53 Hosted Zones**:
- Public hosted zones (internet-facing domains)
- Private hosted zones (VPC-internal DNS)
- Creating and managing zones
- Record types (A, AAAA, CNAME, MX, TXT, etc.)

**Routing Policies**:
- Simple routing
- Weighted routing (A/B testing, gradual rollout)
- Latency-based routing (global performance)
- Failover routing (active-passive DR)
- Geolocation routing (compliance, localization)
- Geoproximity routing (traffic flow)
- Multi-value answer routing

**Advanced Features**:
- Health checks and monitoring
- Traffic flow visualization
- DNSSEC
- Domain registration
- Integration with CloudFront, ALB, S3

**Real-World Use Cases**:
- Blue-green deployments
- Global load balancing
- Disaster recovery DNS switching
- Internal service discovery

---

## 📚 Integration Topics

### Cross-Service Integration
- **VPC + Route53**: Private hosted zones for internal service discovery
- **CloudFront + Route53**: Global CDN with DNS routing
- **ALB + Route53**: Health-check based failover
- **Control Tower + CloudTrail**: Centralized audit logging
- **Control Tower + Config**: Compliance monitoring across accounts
- **Organizations + SSO**: Centralized identity management

---

## 🎓 Certification Alignment

### AWS Certified Cloud Practitioner
**Covered Services**: IAM, EC2, S3, VPC, CloudWatch, basic concepts

### AWS Certified Solutions Architect - Associate
**Covered Services**: All intermediate + VPC deep dive, Route53, RDS, Lambda

### AWS Certified Solutions Architect - Professional
**Covered Services**: All services + Organizations, Control Tower, advanced networking, DR

### AWS Certified DevOps Engineer
**Covered Services**: CI/CD tools, CloudFormation, monitoring, automation

---

## 🔍 Service Selection Guide

### When to Use What

**Compute**:
- EC2 → Full control, specific requirements
- Lambda → Event-driven, serverless
- Fargate → Containers without server management
- ECS/EKS → Container orchestration

**Storage**:
- S3 → Object storage, static assets, backups
- EBS → EC2 attached storage
- EFS → Shared file system across EC2s
- FSx → High-performance file systems

**Database**:
- RDS/Aurora → Relational data, transactions
- DynamoDB → NoSQL, high-scale key-value
- ElastiCache → Caching, session storage
- Redshift → Data warehousing, analytics

**Networking**:
- ALB → HTTP/HTTPS, modern apps
- NLB → TCP/UDP, high performance
- Route53 → DNS, domain management, routing
- CloudFront → Global content delivery

**Multi-Account**:
- Organizations → Account management
- Control Tower → Governance automation
- SSO → Centralized authentication

---

## 📈 Services by Learning Priority

### Priority 1 (Must Know)
1. IAM
2. EC2
3. S3
4. VPC
5. Route53

### Priority 2 (Core Skills)
6. RDS
7. Lambda
8. CloudWatch
9. Load Balancers
10. Auto Scaling

### Priority 3 (Advanced)
11. Organizations
12. Control Tower
13. ECS/EKS
14. EventBridge
15. Security Hub

---

## 🎯 Real-World Application

### Enterprise Multi-Account Setup
```
AWS Organization
├── Management Account (Control Tower)
│   ├── Organizations
│   ├── Control Tower
│   └── Consolidated Billing
├── Security OU
│   ├── Log Archive Account
│   └── Security Tooling Account
├── Production OU
│   ├── Prod Account 1
│   └── Prod Account 2
├── Development OU
│   └── Dev/Test Accounts
└── Shared Services OU
    ├── Route53 (Hosted Zones)
    └── Networking Account
```

### Global Application Architecture
```
Route53 (Global DNS + Hosted Zones)
├── Latency-based routing
├── Health checks
└── Traffic policies
    ├── us-east-1
    │   ├── CloudFront
    │   ├── ALB
    │   ├── EC2 Auto Scaling
    │   └── RDS Multi-AZ
    ├── eu-west-1
    │   └── (Same stack)
    └── ap-southeast-1
        └── (Same stack)
```

---

## 📖 Additional Resources

- **AWS Documentation**: https://docs.aws.amazon.com/
- **AWS Well-Architected**: https://aws.amazon.com/architecture/well-architected/
- **AWS Control Tower Guide**: https://docs.aws.amazon.com/controltower/
- **Route53 Developer Guide**: https://docs.aws.amazon.com/route53/

---

**Summary**: This guide covers **45+ AWS services** with special emphasis on **AWS Control Tower** for multi-account governance and **Route53 Hosted Zones** for DNS management, providing comprehensive enterprise-ready cloud knowledge.
