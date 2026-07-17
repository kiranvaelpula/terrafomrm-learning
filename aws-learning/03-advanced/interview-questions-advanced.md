# AWS Advanced - Interview Questions & Answers

## Overview

This document contains 25 advanced-level AWS interview questions covering advanced VPC, containers, security, cost optimization, multi-region, disaster recovery, and architecture design. These questions are for Solutions Architect, Senior DevOps Engineer, and Cloud Architect roles.

**Topics Covered:**
- Advanced networking (Transit Gateway, PrivateLink)
- Container orchestration (ECS, EKS)
- Event-driven architectures
- Security and compliance
- Cost optimization strategies
- Multi-region and DR
- Production architecture design

---

## Advanced Networking

### Q1: Explain AWS Transit Gateway and when you would use it over VPC Peering.

**Answer:**

**Transit Gateway** is a network hub that connects VPCs, VPNs, and Direct Connect gateways in a hub-and-spoke architecture.

**VPC Peering Limitations:**
- No transitive routing
- Requires N*(N-1)/2 connections for N VPCs
- Complex to manage at scale
- Cannot route through VPC to on-premises

**Transit Gateway Advantages:**
```
VPC Peering (5 VPCs): 10 connections
Transit Gateway (5 VPCs): 5 attachments

Benefit: Simplified topology, centralized routing
```

**Use Transit Gateway when:**
- More than 3-4 VPCs
- Need transitive routing
- Hybrid connectivity (VPN, Direct Connect)
- Multi-account architecture
- Complex routing requirements

**Use VPC Peering when:**
- Only 2-3 VPCs
- Simple connectivity needed
- Cost-sensitive (TGW is more expensive)
- Don't need transitive routing

**Example Architecture:**
```
          Transit Gateway
                 |
    +------------+------------+
    |            |            |
Prod VPC    Shared VPC    Dev VPC
    |            |            |
    +----VPN Gateway-------On-Prem
```

**Cost Comparison:**
```
VPC Peering: $0.01/GB
Transit Gateway: $0.05/hour/attachment + $0.02/GB
```


---

### Q2: How does AWS PrivateLink work and what are its benefits?

**Answer:**

**PrivateLink** provides private connectivity to services without exposing traffic to the internet.

**Architecture:**
```
Service Provider VPC          Service Consumer VPC
       |                              |
   NLB → VPC Endpoint Service    VPC Endpoint (ENI)
       |                              |
       +------Private AWS Network-----+
```

**How it works:**
1. Provider creates endpoint service backed by NLB
2. Consumer creates VPC endpoint to access service
3. Traffic stays on AWS network
4. No VPC peering required

**Benefits:**
- **Security**: No internet exposure
- **Scalability**: AWS handles scaling
- **Simplicity**: No VPC peering mess
- **Cross-account**: Easy service sharing
- **Cross-region**: Supported

**Use Cases:**
- SaaS applications
- Shared services (logging, monitoring)
- Partner integrations
- Internal service mesh

**vs VPC Peering:**

| Feature | PrivateLink | VPC Peering |
|---------|-------------|-------------|
| **Transitive** | No | No |
| **Scaling** | Automatic | Manual |
| **Service Scope** | Specific service | Entire VPC |
| **Setup** | Simple | Complex at scale |

**Example:**
```bash
# Provider creates endpoint service
aws ec2 create-vpc-endpoint-service-configuration \
  --network-load-balancer-arns arn:aws:elasticloadbalancing:... \
  --acceptance-required

# Consumer creates endpoint
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-consumer \
  --service-name com.amazonaws.vpce.us-east-1.vpce-svc-12345678 \
  --vpc-endpoint-type Interface
```

---

## Container Orchestration

### Q3: Compare ECS and EKS. When would you choose one over the other?

**Answer:**

| Aspect | ECS | EKS |
|--------|-----|-----|
| **Orchestration** | AWS proprietary | Kubernetes |
| **Learning Curve** | Low | High |
| **Control Plane** | Free | $0.10/hour (~$73/month) |
| **AWS Integration** | Native | Good (via controllers) |
| **Portability** | AWS only | Multi-cloud |
| **Ecosystem** | Limited | Extensive (Helm, operators) |
| **Complexity** | Simple | Complex |

**Choose ECS when:**
- AWS-only infrastructure
- Team new to containers
- Want simplicity
- Tight AWS service integration
- Cost-sensitive for control plane

**Choose EKS when:**
- Need Kubernetes features
- Multi-cloud strategy
- Team knows Kubernetes
- Want extensive ecosystem
- Need portability

**Real-World Scenarios:**

**ECS Example:**
```
Startup with:
- AWS-only
- Small team
- Need quick deployment
→ ECS is perfect
```

**EKS Example:**
```
Enterprise with:
- Multi-cloud strategy
- Experienced K8s team
- Complex deployments
- Need Helm, Operators
→ EKS is better
```

**Hybrid Approach:**
- Use both: ECS for simple services, EKS for complex ones
- Migrate gradually: Start ECS, move to EKS as team grows

---

### Q4: Explain ECS Fargate vs EC2 launch types. When do you use each?

**Answer:**

**EC2 Launch Type:**
- You manage EC2 instances
- More control
- Lower cost per task
- Good for consistent workloads

**Fargate Launch Type:**
- Serverless containers
- AWS manages infrastructure
- Pay per task
- Good for variable workloads

**Cost Comparison:**

**Example: 1 vCPU, 2 GB RAM, 24/7**
```
EC2 (t3.small): ~$15/month
Fargate: ~$30/month

But:
EC2 overhead: patching, monitoring, scaling
Fargate: Zero operational overhead
```

**Use EC2 when:**
- Consistent, predictable workload
- Need instance-level control
- Cost optimization critical
- Large-scale deployment
- Special instance types needed

**Use Fargate when:**
- Variable workload
- Want zero ops
- Quick starts needed
- Pay-per-use model fits
- Don't want to manage infrastructure

**Best Practice: Mix Both**
```yaml
Service Configuration:
  capacityProviders:
    - FARGATE          # Base capacity
    - FARGATE_SPOT     # Burst capacity  
    - EC2              # Reserved capacity for steady-state
  
  Strategy:
    - FARGATE: weight=1, base=2
    - FARGATE_SPOT: weight=3
    - EC2: weight=1
```

---

## Event-Driven Architecture

### Q5: Design an event-driven order processing system using AWS services.

**Answer:**

**Architecture:**
```
API Gateway
    ↓
Lambda (Order API)
    ↓
EventBridge
    ↓
    +-------+-------+-------+
    |       |       |       |
  SQS     SNS    Lambda  Step Functions
    ↓       ↓       ↓       ↓
Payment Notify Inventory Workflow
Service Email   Update   Orchestration
```

**Implementation:**

**1. Order Submission:**
```javascript
// Lambda: Order API
const { EventBridge } = require('@aws-sdk/client-eventbridge');
const eventbridge = new EventBridge();

exports.handler = async (event) => {
  const order = JSON.parse(event.body);
  
  // Publish order event
  await eventbridge.putEvents({
    Entries: [{
      Source: 'ecommerce.orders',
      DetailType: 'OrderPlaced',
      Detail: JSON.dumps({
        orderId: order.id,
        userId: order.userId,
        items: order.items,
        total: order.total
      })
    }]
  });
  
  return { statusCode: 202, body: 'Order accepted' };
};
```

**2. Event Rules:**
```bash
# Payment Processing
aws events put-rule \
  --name ProcessPayment \
  --event-pattern '{
    "source": ["ecommerce.orders"],
    "detail-type": ["OrderPlaced"]
  }'

aws events put-targets \
  --rule ProcessPayment \
  --targets "Id"="1","Arn"="arn:aws:sqs:us-east-1:123456789012:payment-queue"
```

**3. SQS Processing:**
```javascript
// Lambda: Payment Processor
exports.handler = async (event) => {
  for (const record of event.Records) {
    const order = JSON.parse(JSON.parse(record.body).detail);
    
    try {
      // Process payment
      await processPayment(order);
      
      // Publish success event
      await eventbridge.putEvents({
        Entries: [{
          Source: 'ecommerce.payments',
          DetailType: 'PaymentSuccess',
          Detail: JSON.dumps({ orderId: order.orderId })
        }]
      });
    } catch (error) {
      // Publish failure event
      await eventbridge.putEvents({
        Entries: [{
          Source: 'ecommerce.payments',
          DetailType: 'PaymentFailed',
          Detail: JSON.dumps({ orderId: order.orderId, error: error.message })
        }]
      });
    }
  }
};
```

**Benefits:**
- Decoupled services
- Easy to add new consumers
- Automatic retries (SQS)
- Event history (EventBridge)
- Scalable

**vs Traditional:**
```
Traditional: API → Monolith → Database
Event-Driven: API → EventBus → Multiple Services

Benefits:
- Services can be deployed independently
- Easy to add new features
- Resilient to failures
```


---

## Security

### Q6: How do you implement defense in depth for an AWS application?

**Answer:**

Defense in depth implements multiple layers of security controls.

**Layers:**

**1. Network Layer:**
```
- VPC with public/private subnets
- Security Groups (stateful)
- NACLs (stateless)
- WAF on ALB/CloudFront
- Shield for DDoS protection
```

**2. Identity Layer:**
```
- IAM roles (no access keys)
- MFA for privileged access
- Least privilege policies
- SCPs for organizations
```

**3. Data Layer:**
```
- Encryption at rest (KMS)
- Encryption in transit (TLS)
- S3 bucket policies
- RDS encryption
```

**4. Application Layer:**
```
- Input validation
- Authentication (Cognito)
- Authorization
- API rate limiting
```

**5. Monitoring Layer:**
```
- CloudTrail (all API calls)
- GuardDuty (threat detection)
- Security Hub (centralized)
- Config (compliance)
- VPC Flow Logs
```

**Example Implementation:**
```
Internet
  ↓
CloudFront + WAF (Layer 7 protection)
  ↓
ALB in Public Subnet
  ↓
Security Group (Allow from ALB only)
  ↓
ECS in Private Subnet
  ↓
Security Group (Allow from ECS only)
  ↓
RDS in Isolated Subnet
  ↓
Encryption at Rest (KMS)
```

**Auto-Remediation:**
```python
# Lambda for automated response
def lambda_handler(event, context):
    finding = event['detail']['findings'][0]
    
    if finding['Title'] == 'S3 Bucket Public':
        bucket = extract_bucket_name(finding)
        
        # Auto-fix
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
        
        # Notify
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:123456789012:security-alerts',
            Message=f'Auto-fixed public S3 bucket: {bucket}'
        )
```

---

### Q7: Explain AWS Security Hub and how it integrates with other security services.

**Answer:**

**Security Hub** provides centralized security and compliance monitoring.

**Architecture:**
```
         Security Hub
              ↓
    +---------+---------+
    |         |         |
GuardDuty  Config  Inspector
    |         |         |
Findings  Rules   Vulnerabilities
    ↓         ↓         ↓
  Aggregated & Prioritized
    ↓
EventBridge → Lambda → Auto-remediation
    ↓
  SNS → Alerts
```

**Integrations:**

**1. GuardDuty (Threat Detection):**
- Analyzes VPC Flow Logs, CloudTrail, DNS logs
- Detects malicious activity
- Findings sent to Security Hub

**2. AWS Config (Compliance):**
- Monitors resource configurations
- Checks compliance rules
- Non-compliant findings to Security Hub

**3. Inspector (Vulnerability Scanning):**
- Scans EC2, containers, Lambda
- Identifies software vulnerabilities
- Results in Security Hub

**4. IAM Access Analyzer:**
- Identifies unintended access
- External access findings to Security Hub

**Setup:**
```bash
# Enable Security Hub
aws securityhub enable-security-hub

# Enable standards
aws securityhub batch-enable-standards \
  --standards-subscription-requests \
    StandardsArn=arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0 \
    StandardsArn=arn:aws:securityhub:us-east-1::standards/aws-foundational-security-best-practices/v/1.0.0

# Get findings
aws securityhub get-findings \
  --filters '{"SeverityLabel": [{"Value": "CRITICAL", "Comparison": "EQUALS"}]}'
```

**Automated Response:**
```python
# EventBridge rule triggers Lambda
def handle_security_finding(event, context):
    finding = event['detail']['findings'][0]
    severity = finding['Severity']['Label']
    title = finding['Title']
    
    if severity == 'CRITICAL':
        # Immediate action
        if 'S3' in title:
            remediate_s3(finding)
        elif 'EC2' in title:
            isolate_instance(finding)
        
        # Alert on-call
        pagerduty.trigger_incident(finding)
    
    elif severity == 'HIGH':
        # Create ticket
        jira.create_issue(finding)
```

**Benefits:**
- Single pane of glass
- Automated compliance checks
- Prioritized findings
- Auto-remediation capabilities
- Cross-account aggregation

---

## Cost Optimization

### Q8: You have a 24/7 application with variable load. How do you optimize costs?

**Answer:**

**Analysis Approach:**

**1. Understand Usage Patterns:**
```
CloudWatch Metrics Analysis:
- Peak hours: 9 AM - 6 PM (High load)
- Off-peak: 6 PM - 9 AM (Medium load)
- Weekends: Low load
```

**2. Right-Size Resources:**
```bash
# Analyze CPU utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
  --start-time 2026-01-01T00:00:00Z \
  --end-time 2026-01-31T23:59:59Z \
  --period 3600 \
  --statistics Average,Maximum

# Result: Average 25%, Maximum 45%
# Action: Downsize from t3.large → t3.medium
# Savings: 50%
```

**3. Mixed Pricing Strategy:**
```
Baseline capacity (24/7):
  - Reserved Instances (3 years)
  - Savings: 72%
  - Example: 10 instances

Variable capacity:
  - On-Demand or Spot
  - Example: 0-20 instances

Cost Comparison:
On-Demand only: $10,000/month
RI + On-Demand: $4,500/month
RI + Spot: $3,800/month
```

**4. Auto Scaling Configuration:**
```yaml
Auto Scaling Group:
  MinSize: 10  # Covered by RI
  MaxSize: 30
  
  Policies:
    - TargetTracking:
        CPU: 70%
    - Scheduled:
        - Scale to 25 at 8 AM weekdays
        - Scale to 15 at 7 PM weekdays
        - Scale to 10 on weekends

  Mixed Instances:
    OnDemandBaseCapacity: 10  # RI covers this
    OnDemandPercentageAboveBaseCapacity: 0  # Rest is Spot
    SpotAllocationStrategy: capacity-optimized
```

**5. Additional Optimizations:**

**Storage:**
```bash
# S3 Intelligent-Tiering
aws s3api put-bucket-intelligent-tiering-configuration \
  --bucket my-bucket \
  --id EntirePrefix \
  --intelligent-tiering-configuration '{
    "Status": "Enabled",
    "Tierings": [
      {"Days": 90, "AccessTier": "ARCHIVE_ACCESS"},
      {"Days": 180, "AccessTier": "DEEP_ARCHIVE_ACCESS"}
    ]
  }'
```

**Database:**
```
RDS:
  - Use Read Replicas for read-heavy workloads
  - Aurora Serverless for variable workloads
  - Stop dev/test databases off-hours

Example:
Standard RDS: $500/month 24/7
Aurora Serverless: $200/month (auto-pauses)
```

**Monitoring:**
```bash
# Set budget alerts
aws budgets create-budget \
  --account-id 123456789012 \
  --budget '{
    "BudgetName": "Monthly",
    "BudgetLimit": {"Amount": "5000", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }' \
  --notifications-with-subscribers '[{
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80
    },
    "Subscribers": [{
      "SubscriptionType": "EMAIL",
      "Address": "admin@example.com"
    }]
  }]'
```

**Result:**
```
Before: $10,000/month
After:
  - Right-sizing: Save 30% = $7,000
  - Reserved Instances: Save 40% more = $4,200
  - Spot Instances: Save 20% more = $3,360
  - Storage optimization: Save 10% = $3,024

Total savings: 70% (~$7,000/month)
```

---

## Multi-Region & DR

### Q9: Design a multi-region active-active architecture with data consistency.

**Answer:**

**Architecture:**
```
            Route53 (Latency-Based)
                     |
        +------------+------------+
        |                         |
   Region 1 (US)             Region 2 (EU)
        |                         |
   CloudFront                CloudFront
        |                         |
      ALB                       ALB
        |                         |
   ECS Fargate               ECS Fargate
        |                         |
   DynamoDB Global         DynamoDB Global
   (Multi-master)          (Multi-master)
        |                         |
   Aurora Global           Aurora Global
   (Primary)               (Secondary Read)
```

**Data Strategy:**

**1. DynamoDB Global Tables (Multi-Master):**
```bash
# Supports writes in both regions
aws dynamodb create-table \
  --table-name Users \
  --attribute-definitions AttributeName=UserId,AttributeType=S \
  --key-schema AttributeName=UserId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES

aws dynamodb create-global-table \
  --global-table-name Users \
  --replication-group RegionName=us-east-1 RegionName=eu-west-1
```

**Conflict Resolution:**
- Last Writer Wins (automatic)
- Replication lag: <1 second

**2. Aurora Global (Single-Master for Strong Consistency):**
```bash
# Primary in us-east-1
# Read replicas in eu-west-1
# Write lag: <1 second
# Failover: <1 minute
```

**Strategy:**
- Writes go to primary region
- Reads from local region
- If primary fails, promote secondary

**3. S3 Cross-Region Replication:**
```json
{
  "Role": "arn:aws:iam::123456789012:role/s3-replication-role",
  "Rules": [{
    "Status": "Enabled",
    "Priority": 1,
    "Filter": {},
    "Destination": {
      "Bucket": "arn:aws:s3:::bucket-eu",
      "ReplicationTime": {
        "Status": "Enabled",
        "Time": {"Minutes": 15}
      }
    }
  }]
}
```

**Routing Strategy:**
```bash
# Route53 latency-based routing
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "api.example.com",
          "Type": "A",
          "SetIdentifier": "US",
          "Region": "us-east-1",
          "AliasTarget": {
            "HostedZoneId": "Z35SXDOTRQ7X7K",
            "DNSName": "us-alb.elb.amazonaws.com"
          }
        }
      },
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "api.example.com",
          "Type": "A",
          "SetIdentifier": "EU",
          "Region": "eu-west-1",
          "AliasTarget": {
            "HostedZoneId": "Z32O12XQLNTSW2",
            "DNSName": "eu-alb.elb.amazonaws.com"
          }
        }
      }
    ]
  }'
```

**Consistency Trade-offs:**

**Eventual Consistency (DynamoDB Global Tables):**
```
US User updates profile → Replicated to EU in <1s
EU User might see old data briefly
Acceptable for: User profiles, preferences
```

**Strong Consistency (Aurora Global):**
```
Financial transactions → Always to primary region
EU users have higher latency for writes
Acceptable for: Payments, inventory
```

**Application Logic:**
```javascript
// Hybrid approach
async function updateUser(userId, data) {
  // Non-critical data → DynamoDB (eventually consistent)
  await dynamodb.updateItem({
    TableName: 'Users',
    Key: { UserId: userId },
    UpdateExpression: 'SET #name = :name, #email = :email',
    ExpressionAttributeNames: { '#name': 'name', '#email': 'email' },
    ExpressionAttributeValues: { ':name': data.name, ':email': data.email }
  }).promise();
  
  // Critical data → Aurora (strongly consistent)
  await aurora.query(
    'UPDATE accounts SET balance = ? WHERE user_id = ?',
    [data.balance, userId]
  );
}
```

**RTO/RPO:**
```
RTO: Seconds (automatic Route53 failover)
RPO: <1 second (DynamoDB), <1 second (Aurora)
```

---

## Real-World Scenarios

### Q10: You're experiencing intermittent 5XX errors from your API. How do you troubleshoot?

**Answer:**

**Systematic Approach:**

**1. Check CloudWatch Metrics:**
```bash
# ALB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name HTTPCode_Target_5XX_Count \
  --dimensions Name=LoadBalancer,Value=app/my-alb/xyz \
  --start-time 2026-01-15T00:00:00Z \
  --end-time 2026-01-15T23:59:59Z \
  --period 300 \
  --statistics Sum

# Check target response time
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --period 300 \
  --statistics Average,Maximum
```

**Analysis:**
```
If TargetResponseTime spikes → Backend slow
If UnhealthyHostCount increases → Instances failing
If RequestCount spikes → Traffic surge
```

**2. Check Application Logs:**
```bash
# CloudWatch Logs Insights
aws logs start-query \
  --log-group-name /aws/ecs/api-service \
  --start-time 1642204800 \
  --end-time 1642291200 \
  --query-string '
    fields @timestamp, @message
    | filter @message like /ERROR/ or @message like /500/
    | stats count() by bin(5m)
    | sort @timestamp desc
  '
```

**3. Check Infrastructure:**
```bash
# ECS task health
aws ecs describe-tasks \
  --cluster my-cluster \
  --tasks $(aws ecs list-tasks --cluster my-cluster --service-name api-service --output text)

# Database connections
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=prod-db

# CPU/Memory
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=api-service
```

**Common Causes & Solutions:**

**A. Database Connection Pool Exhausted:**
```javascript
// Problem: Creating new connections each request
const mysql = require('mysql');
app.get('/api/users', async (req, res) => {
  const connection = mysql.createConnection({...}); // ❌ Bad
  // ...
});

// Solution: Use connection pool
const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  connectionLimit: 20,
  queueLimit: 0
});

app.get('/api/users', async (req, res) => {
  pool.query('SELECT * FROM users', (err, results) => {
    // ...
  });
});
```

**B. Memory Leak:**
```bash
# Check memory usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization

# If consistently increasing → Memory leak
# Solution: Restart tasks, fix application code
```

**C. Slow Queries:**
```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- Find slow queries
SELECT * FROM mysql.slow_log 
ORDER BY query_time DESC 
LIMIT 10;

-- Solution: Add indexes
CREATE INDEX idx_user_email ON users(email);
```

**D. Insufficient Resources:**
```bash
# Scale up
aws ecs update-service \
  --cluster my-cluster \
  --service api-service \
  --desired-count 10  # Increase from 4

# Or increase task resources
# Update task definition with more CPU/memory
```

**4. Enable X-Ray for Detailed Tracing:**
```javascript
const AWSXRay = require('aws-xray-sdk');
const AWS = AWSXRay.captureAWS(require('aws-sdk'));

app.use(AWSXRay.express.openSegment('api-service'));

app.get('/api/users', async (req, res) => {
  const segment = AWSXRay.getSegment();
  
  const subsegment = segment.addNewSubsegment('database-query');
  const results = await queryDatabase();
  subsegment.close();
  
  res.json(results);
});

app.use(AWSXRay.express.closeSegment());
```

**X-Ray shows:**
```
Request breakdown:
- ALB: 5ms
- Lambda/ECS: 200ms
  - Auth: 20ms
  - Database query: 150ms  ← PROBLEM!
  - Response formatting: 30ms
```

**5. Implement Monitoring Alerts:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name high-5xx-errors \
  --alarm-description "Alert when 5XX errors > 10 in 5 minutes" \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:ops-alerts
```

**Prevention:**
- Health checks
- Circuit breakers
- Rate limiting
- Connection pooling
- Caching (ElastiCache)
- Proper error handling

---

### Q11: Design a cost-effective solution for processing 10TB of data uploaded daily to S3.

**Answer:**

**Requirements Analysis:**
- 10 TB/day = ~120 MB/second average
- Processing: Transform, analyze, store results
- Budget-conscious

**Architecture:**
```
S3 Upload → S3 Event → SQS → Lambda/Batch → Results S3
    ↓
Lifecycle → Glacier (after 30 days)
```

**Solution Components:**

**1. S3 Event Notification + SQS:**
```bash
# Create SQS queue
aws sqs create-queue --queue-name data-processing

# Configure S3 event notification
aws s3api put-bucket-notification-configuration \
  --bucket incoming-data \
  --notification-configuration '{
    "QueueConfigurations": [{
      "QueueArn": "arn:aws:sqs:us-east-1:123456789012:data-processing",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [{
            "Name": "prefix",
            "Value": "uploads/"
          }]
        }
      }
    }]
  }'
```

**2. Processing Options:**

**Option A: Lambda (for small files <5 GB):**
```python
import boto3
import json

s3 = boto3.client('s3')

def lambda_handler(event, context):
    for record in event['Records']:
        message = json.loads(record['body'])
        bucket = message['Records'][0]['s3']['bucket']['name']
        key = message['Records'][0]['s3']['object']['key']
        
        # Download
        obj = s3.get_object(Bucket=bucket, Key=key)
        data = obj['Body'].read()
        
        # Process
        results = process_data(data)
        
        # Upload results
        s3.put_object(
            Bucket='processed-data',
            Key=f'results/{key}',
            Body=json.dumps(results)
        )
```

**Cost:** Free tier covers 1M requests, then $0.20/million

**Option B: AWS Batch (for large files):**
```yaml
# Batch compute environment
ComputeEnvironment:
  Type: EC2
  InstanceTypes:
    - c5.xlarge  # Compute optimized
    - c5.2xlarge
  MinvCpus: 0
  MaxvCpus: 256
  DesiredvCpus: 0
  SpotIamFleetRole: arn:aws:iam::123456789012:role/SpotFleetRole
  AllocationStrategy: SPOT_CAPACITY_OPTIMIZED  # Cheapest

JobDefinition:
  Type: container
  Image: my-processing-image
  Vcpus: 4
  Memory: 8192
  Command:
    - python
    - process.py
    - --input
    - Ref::input_path
```

**Cost:** Spot instances 70% cheaper
- c5.xlarge Spot: ~$0.05/hour
- 10 TB @ 1 GB/min per instance = ~167 hours
- Cost: ~$8/day

**3. Storage Optimization:**
```json
{
  "Rules": [{
    "Id": "ArchiveOldData",
    "Status": "Enabled",
    "Transitions": [
      {
        "Days": 30,
        "StorageClass": "INTELLIGENT_TIERING"
      },
      {
        "Days": 90,
        "StorageClass": "GLACIER"
      },
      {
        "Days": 365,
        "StorageClass": "DEEP_ARCHIVE"
      }
    ],
    "Expiration": {
      "Days": 2555  # 7 years
    }
  }]
}
```

**Storage Costs:**
```
Standard: $0.023/GB/month × 10 TB × 30 days = $7,000/month
Glacier: $0.004/GB/month × 10 TB = $40/month (after 90 days)
Deep Archive: $0.00099/GB/month × 10 TB = $10/month (after 365 days)
```

**4. Monitoring:**
```bash
# Track costs
aws ce get-cost-and-usage \
  --time-period Start=2026-01-01,End=2026-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# Set budget alert
aws budgets create-budget \
  --account-id 123456789012 \
  --budget '{
    "BudgetName": "DataProcessing",
    "BudgetLimit": {"Amount": "500", "Unit": "USD"},
    "TimeUnit": "MONTHLY"
  }'
```

**Total Cost Estimate:**
```
S3 Storage (Standard): $230/month (10 TB)
Processing (Batch Spot): $240/month (8 hours/day)
Data Transfer: $0 (same region)
SQS: $1/month
Total: ~$471/month

With lifecycle:
Month 1-3: $471/month
Month 4+: $280/month (Glacier transition)
Month 12+: $250/month (Deep Archive)
```

**Alternative (Serverless):**
```
S3 → Lambda → Athena (query in place)
Cost: $5/TB scanned
10 TB/day × $5 = $50/day = $1,500/month

Only use if queries are infrequent
```

**Recommendation: AWS Batch with Spot Instances**
- Most cost-effective
- Handles large files
- Scalable
- Reliable

---

## Summary

These advanced questions cover real-world AWS scenarios including networking, containers, security, cost optimization, multi-region, and disaster recovery. Master these concepts for senior cloud roles.

**Key Topics Covered:**
- Advanced networking (Transit Gateway, PrivateLink)
- Container orchestration (ECS vs EKS)
- Event-driven architectures
- Security in depth
- Cost optimization strategies
- Multi-region active-active
- Disaster recovery patterns
- Production troubleshooting
- Large-scale data processing

**Preparation Tips:**
- Build hands-on projects
- Practice architecture design
- Understand trade-offs
- Learn cost implications
- Study real-world case studies

