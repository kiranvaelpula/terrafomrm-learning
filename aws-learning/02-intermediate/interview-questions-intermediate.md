# AWS Intermediate - Interview Questions & Answers

## Overview

This document contains 20 intermediate-level AWS interview questions covering VPC networking, load balancing, auto-scaling, databases, serverless computing, DNS, monitoring, and CloudFormation. These questions are commonly asked for Cloud Engineer, DevOps Engineer, and Solutions Architect roles.

**Topics Covered:**
- VPC and networking concepts
- Load balancers (ALB/NLB)
- Auto Scaling strategies
- RDS and database management
- Lambda and serverless
- Route53 DNS
- CloudWatch monitoring
- CloudFormation IaC

---

## VPC and Networking

### Q1: Explain the difference between a public subnet and a private subnet in AWS VPC.

**Answer:**

**Public Subnet:**
- Has a route to an Internet Gateway (IGW)
- Resources can directly access the internet
- Resources get public IP addresses (if enabled)
- Used for: Web servers, load balancers, bastion hosts

**Private Subnet:**
- No direct route to Internet Gateway
- Uses NAT Gateway/Instance for outbound internet access
- Resources only have private IP addresses
- Used for: Application servers, databases, backend services

**Example Route Tables:**
```
Public Subnet Route Table:
Destination      Target
10.0.0.0/16     local
0.0.0.0/0       igw-xxxxx  ← Routes to Internet Gateway

Private Subnet Route Table:
Destination      Target
10.0.0.0/16     local
0.0.0.0/0       nat-xxxxx  ← Routes to NAT Gateway
```

**Key Point:** The route table determines whether a subnet is public or private, not the subnet itself.

---

### Q2: What is the difference between a NAT Gateway and a NAT Instance?

**Answer:**

| Feature | NAT Gateway | NAT Instance |
|---------|-------------|--------------|
| **Managed By** | AWS (fully managed) | You (self-managed EC2) |
| **Availability** | Highly available within AZ | Manual failover needed |
| **Bandwidth** | Up to 45 Gbps | Depends on instance type |
| **Maintenance** | No maintenance | You patch and maintain |
| **Security Groups** | Not supported | Supported |
| **Bastion Host** | No | Can be used as bastion |
| **Cost** | Hourly + data transfer | EC2 + data transfer |
| **Performance** | Better | Limited by instance |

**When to use NAT Gateway:**
- Production environments
- Need high availability
- Want hands-off management

**When to use NAT Instance:**
- Cost-sensitive dev/test environments
- Need security group control
- Want to use as bastion host


---

### Q3: Explain VPC Peering and its limitations.

**Answer:**

**VPC Peering** allows you to connect two VPCs privately using AWS's network, enabling resources to communicate as if they're in the same network.

**Setup:**
```
VPC A (10.0.0.0/16) ←--Peering Connection--→ VPC B (172.16.0.0/16)
```

**Limitations:**
1. **No Transitive Peering**
   - If A peers with B, and B peers with C, A cannot reach C
   - Must create direct A→C peering

2. **No Overlapping CIDR Blocks**
   - VPCs must have unique IP ranges
   - 10.0.0.0/16 cannot peer with 10.0.0.0/16

3. **Single Region (by default)**
   - Cross-region peering available but with limitations
   - Data transfer costs apply

4. **No Edge-to-Edge Routing**
   - Cannot route through VPC to reach on-premises network
   - Cannot route through VPC to reach internet

**Use Cases:**
- Connect production and development VPCs
- Multi-account architecture
- Shared services VPC
- Cross-region disaster recovery

**Alternative:** Transit Gateway for complex multi-VPC architectures

---

## Load Balancing

### Q4: What are the differences between Application Load Balancer (ALB) and Network Load Balancer (NLB)?

**Answer:**

| Feature | ALB | NLB |
|---------|-----|-----|
| **Layer** | Layer 7 (Application) | Layer 4 (Transport) |
| **Protocol** | HTTP, HTTPS, gRPC | TCP, UDP, TLS |
| **Routing** | Path, host, header-based | IP and port-based |
| **Performance** | Good (requests/sec) | Extreme (millions req/sec) |
| **Static IP** | No (uses DNS) | Yes (Elastic IP) |
| **WebSockets** | Yes | Yes |
| **SSL Termination** | Yes | Yes (TLS) |
| **Latency** | Higher (~ms) | Ultra-low (~100µs) |
| **Health Checks** | HTTP/HTTPS | TCP |
| **Pricing** | Per hour + LCU | Per hour + NLCU |

**When to use ALB:**
- HTTP/HTTPS applications
- Microservices with path-based routing
- Need content-based routing
- Container-based applications

**When to use NLB:**
- TCP/UDP applications
- Extreme performance requirements
- Need static IP addresses
- Gaming, IoT, financial services

**Example ALB Routing:**
```
www.example.com/api/*  → API Target Group
www.example.com/web/*  → Web Target Group
api.example.com/*      → API Target Group (host-based)
```


---

### Q5: Explain Target Groups and how they work with load balancers.

**Answer:**

**Target Groups** are logical groupings of targets (EC2 instances, IP addresses, Lambda functions, containers) that receive traffic from load balancers.

**Components:**
```
Load Balancer
    ↓
Listener (Port 80, 443)
    ↓
Rules (path-based, host-based)
    ↓
Target Group
    ↓
Targets (EC2, IP, Lambda, ECS)
```

**Target Types:**
1. **Instance** - EC2 instance IDs
2. **IP** - Private IP addresses (on-premises, containers)
3. **Lambda** - Serverless functions
4. **ALB** - Another ALB (chaining)

**Health Checks:**
```json
{
  "HealthCheckProtocol": "HTTP",
  "HealthCheckPath": "/health",
  "HealthCheckIntervalSeconds": 30,
  "HealthyThresholdCount": 2,
  "UnhealthyThresholdCount": 3,
  "Matcher": {"HttpCode": "200"}
}
```

**Advanced Features:**
- **Sticky Sessions**: Route user to same target
- **Deregistration Delay**: Connection draining period
- **Slow Start**: Gradual traffic increase to new targets
- **Cross-Zone Load Balancing**: Distribute across AZs

**Example Use Case:**
```
ALB Listener Rule:
  IF path = /api/* 
    THEN forward to API-Target-Group
  ELSE IF path = /admin/*
    THEN forward to Admin-Target-Group
```

---

## Auto Scaling

### Q6: Explain the different Auto Scaling policies and when to use each.

**Answer:**

**1. Target Tracking Scaling**
Maintains a specific metric at a target value.

```json
{
  "TargetValue": 70.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ASGAverageCPUUtilization"
  }
}
```

**When to use:**
- Simple, common scaling needs
- CPU, network, or request count based
- Want AWS to manage scaling calculations

**2. Step Scaling**
Scales based on CloudWatch alarm thresholds with different step adjustments.

```
CPU > 80%: Add 2 instances
CPU > 90%: Add 4 instances
CPU < 40%: Remove 1 instance
```

**When to use:**
- Need different scaling increments
- Complex scaling logic
- Aggressive scaling for sudden spikes

**3. Simple Scaling**
Single adjustment based on alarm (legacy, not recommended).


**4. Scheduled Scaling**
Scale at specific times.

```bash
# Scale up at 9 AM weekdays
aws autoscaling put-scheduled-action \
  --auto-scaling-group-name my-asg \
  --scheduled-action-name scale-up-morning \
  --recurrence "0 9 * * MON-FRI" \
  --desired-capacity 10
```

**When to use:**
- Predictable traffic patterns
- Business hours scaling
- Batch processing windows

**5. Predictive Scaling**
Uses machine learning to forecast and scale ahead of demand.

**When to use:**
- Recurring traffic patterns
- Proactive scaling needed
- Want to optimize costs

**Best Practice:** Combine target tracking with scheduled scaling for optimal results.

---

### Q7: What is the difference between desired capacity, minimum capacity, and maximum capacity in Auto Scaling Groups?

**Answer:**

**Desired Capacity:**
- Target number of instances ASG maintains
- Auto Scaling adjusts this based on policies
- Can be manually changed

**Minimum Capacity:**
- Absolute minimum instances that must run
- ASG never scales below this number
- Protects against scaling to zero

**Maximum Capacity:**
- Upper limit on number of instances
- Prevents runaway scaling costs
- Acts as safety cap

**Example Configuration:**
```
Min: 2 instances (high availability)
Desired: 4 instances (current need)
Max: 10 instances (cost protection)

Traffic Pattern:
08:00 - Low traffic: 2 instances (at minimum)
12:00 - Medium traffic: 4 instances (desired)
18:00 - High traffic: 8 instances (scaled up)
22:00 - Peak traffic: 10 instances (at maximum, can't scale higher)
02:00 - Low traffic: 2 instances (back to minimum)
```

**Important Notes:**
- Desired capacity is always between min and max
- Setting desired = min = max disables auto scaling
- Changing min/max doesn't immediately affect running instances
- ASG gradually adjusts to new desired capacity

---

## Databases

### Q8: Explain the difference between RDS Multi-AZ and Read Replicas.

**Answer:**

**Multi-AZ Deployment:**

**Purpose:** High availability and disaster recovery

**How it works:**
```
Primary DB (us-east-1a)
    ↓ Synchronous replication
Standby DB (us-east-1b)
    ↓ Automatic failover
```

**Characteristics:**
- Synchronous replication
- Same region, different AZ
- Automatic failover (1-2 minutes)
- Same endpoint (no application changes)
- No read traffic to standby
- Higher cost (~2x)
- Backups from standby (no I/O impact)

**Read Replicas:**

**Purpose:** Scale read operations and improve performance

**How it works:**
```
Primary DB (us-east-1a)
    ↓ Asynchronous replication
Read Replica 1 (us-east-1b)
Read Replica 2 (us-west-2)
```


**Characteristics:**
- Asynchronous replication
- Can be in different regions
- Separate endpoints (app must route reads)
- Can be promoted to primary
- Up to 5 read replicas per database
- Useful for read-heavy workloads
- Can offload reporting queries

**Comparison Table:**

| Feature | Multi-AZ | Read Replica |
|---------|----------|--------------|
| **Purpose** | Availability | Scalability |
| **Replication** | Synchronous | Asynchronous |
| **Endpoint** | Same | Different |
| **Regions** | Same region only | Cross-region supported |
| **Failover** | Automatic | Manual promotion |
| **Reads** | Primary only | Yes, read traffic |
| **Writes** | Primary only | No writes |
| **Use Case** | DR | Read scaling |

**Can you have both?** Yes! Multi-AZ for availability + Read Replicas for scaling.

---

### Q9: What is Amazon Aurora and how does it differ from standard RDS?

**Answer:**

**Amazon Aurora** is AWS's proprietary relational database that's MySQL and PostgreSQL compatible but with significant architectural improvements.

**Key Differences:**

**1. Storage Architecture:**
- **RDS**: Traditional disk-based storage
- **Aurora**: Distributed, SSD-backed storage layer
- Aurora storage grows automatically (up to 128 TB)
- RDS requires manual scaling

**2. Performance:**
- Aurora: 5x faster than MySQL, 3x faster than PostgreSQL
- RDS: Standard database performance
- Aurora uses multiple replicas for reads

**3. Availability:**
- **Aurora**: 6 copies across 3 AZs (automatic)
- **RDS**: Multi-AZ requires manual enable
- Aurora handles up to 2 copy loss without affecting writes
- Aurora handles up to 3 copy loss without affecting reads

**4. Replicas:**
- **Aurora**: Up to 15 read replicas, <10ms replica lag
- **RDS**: Up to 5 read replicas, higher lag
- Aurora replicas can be failover targets

**5. Backup:**
- **Aurora**: Continuous backup to S3 (automated)
- **RDS**: Snapshot-based backups
- Aurora: Point-in-time restore to any second

**6. Endpoints:**
```
Aurora:
  - Cluster Endpoint (writes)
  - Reader Endpoint (reads, load balanced)
  - Custom Endpoints (specific instances)

RDS:
  - Single endpoint (or separate replica endpoints)
```

**7. Cost:**
- Aurora: Generally 20% more than RDS
- But better performance may reduce instance needs
- Aurora Serverless option for variable workloads

**Aurora Serverless:**
```
Database auto-scales based on demand
Pause during inactivity (pay only for storage)
Good for: Dev/test, infrequent workloads
```

**When to choose Aurora:**
- Need extreme availability (99.99%)
- High-performance requirements
- Large-scale applications
- Want automated scaling
- MySQL/PostgreSQL compatibility needed

**When to choose RDS:**
- Cost-sensitive workloads
- Standard performance sufficient
- Need other engines (SQL Server, Oracle, MariaDB)
- Simpler architecture preferred

---

## Serverless Computing

### Q10: Explain AWS Lambda cold starts and how to mitigate them.

**Answer:**

**Cold Start** occurs when Lambda initializes a new execution environment for your function.

**Cold Start Process:**
```
1. Download code package
2. Start execution environment
3. Load runtime
4. Run initialization code
5. Execute function handler
   ↓
Total delay: 100ms - several seconds
```


**Warm Start:**
```
Reuse existing execution environment
   ↓
Execute function handler immediately
   ↓
Latency: Single-digit milliseconds
```

**Factors Affecting Cold Start:**
1. **Runtime**: Python/Node.js fastest, Java slowest
2. **Memory**: Higher memory = faster startup
3. **VPC**: VPC functions have longer cold starts
4. **Package Size**: Smaller packages start faster
5. **Dependencies**: Fewer dependencies = faster

**Mitigation Strategies:**

**1. Provisioned Concurrency**
```bash
# Pre-warm function instances
aws lambda put-provisioned-concurrency-config \
  --function-name my-function \
  --provisioned-concurrent-executions 5
```
- Keeps instances warm
- Eliminates cold starts
- Costs more (pay for warm instances)

**2. Keep Functions Warm**
```python
# Scheduled ping to keep warm
CloudWatch Event (every 5 minutes)
  → Lambda function
```

**3. Optimize Package Size**
```python
# ❌ BAD - 50 MB package
import pandas
import numpy
import tensorflow

# ✅ GOOD - 5 MB package
import json
import boto3
```

**4. Increase Memory**
```bash
# More memory = more CPU = faster startup
aws lambda update-function-configuration \
  --function-name my-function \
  --memory-size 1024  # Up from 128
```

**5. Minimize VPC Usage**
```
If possible, avoid VPC for Lambda
Use VPC only when accessing private resources
Consider NAT Gateway alternatives
```

**6. Global Variables for Reuse**
```python
# Initialize outside handler (reused across invocations)
import boto3
s3_client = boto3.client('s3')  # Reused

def lambda_handler(event, context):
    # This runs every invocation
    s3_client.list_buckets()
```

**7. Use Layers**
```bash
# Share dependencies across functions
aws lambda publish-layer-version \
  --layer-name my-dependencies \
  --zip-file fileb://layer.zip
```

**Typical Cold Start Times:**
- Python: 100-200ms
- Node.js: 150-250ms
- Go: 150-300ms
- Java: 500ms-2s
- .NET: 400ms-1.5s

**Real-World Impact:**
```
API Gateway → Lambda (cold start)
First request: 2 seconds
Subsequent requests: 10ms

With Provisioned Concurrency:
All requests: 10-20ms
```

---

### Q11: What are Lambda execution limits and how do you work within them?

**Answer:**

**Lambda Limits:**

**Hard Limits (Cannot Change):**
```
Max execution time: 15 minutes
Max deployment package: 50 MB (zipped), 250 MB (unzipped)
Max layers: 5 per function
Max /tmp storage: 10 GB
Max file descriptors: 1,024
Max processes/threads: 1,024
```

**Soft Limits (Can Request Increase):**
```
Concurrent executions: 1,000 (per region)
Function and layer storage: 75 GB
```

**Memory and CPU:**
```
Memory: 128 MB to 10,240 MB (increments of 1 MB)
CPU: Proportional to memory (1,792 MB = 1 vCPU)
```


**Workarounds for Limits:**

**1. Execution Time Limit (15 min)**
```python
# Problem: Long-running job
# Solution: Chain functions or use Step Functions

# Step Functions workflow:
Start → Lambda 1 (process batch 1)
      → Lambda 2 (process batch 2)
      → Lambda 3 (process batch 3)
      → Complete
```

**2. Memory Limit**
```python
# Problem: Large dataset processing
# Solution: Stream data or use S3 Select

# ❌ Load entire file
data = s3.get_object(Bucket='bucket', Key='large.csv')['Body'].read()

# ✅ Stream data
response = s3.get_object(Bucket='bucket', Key='large.csv')
for line in response['Body'].iter_lines():
    process(line)
```

**3. Deployment Package Size**
```bash
# Problem: Large dependencies
# Solution: Use Lambda Layers

# Layer for common dependencies:
layers/
  python/
    lib/
      python3.9/
        site-packages/
          pandas/
          numpy/

# Function package now only contains your code
```

**4. /tmp Storage Limit (10 GB)**
```python
# Problem: Need to write large temp files
# Solution: Stream to S3 instead

# ❌ Write to /tmp
with open('/tmp/output.csv', 'w') as f:
    f.write(large_data)

# ✅ Stream to S3
s3.upload_fileobj(data_stream, 'bucket', 'output.csv')
```

**5. Concurrent Execution Limit**
```bash
# Reserve concurrency for critical functions
aws lambda put-function-concurrency \
  --function-name critical-function \
  --reserved-concurrent-executions 100

# Other functions share remaining capacity
```

**Best Practices:**
- Design for short executions (<1 minute ideal)
- Use external storage (S3, DynamoDB) for large data
- Implement checkpointing for long processes
- Monitor CloudWatch metrics for throttling
- Request limit increases proactively

---

## DNS and Route53

### Q12: Explain the different Route53 routing policies and their use cases.

**Answer:**

**1. Simple Routing**
```
Route to a single resource
Example: www.example.com → 192.0.2.1
```
**Use Case:** Single resource, no health checks needed

**2. Weighted Routing**
```
Route 70% traffic to Server A
Route 30% traffic to Server B

Record: www.example.com, Weight: 70 → 192.0.2.1
Record: www.example.com, Weight: 30 → 192.0.2.2
```
**Use Cases:**
- A/B testing
- Blue-green deployments
- Gradual migration
- Load distribution

**3. Latency-Based Routing**
```
User in US-East → Route to us-east-1 resource
User in EU → Route to eu-west-1 resource

Automatically routes to lowest latency endpoint
```
**Use Cases:**
- Global applications
- Improve user experience
- Multi-region deployments

**4. Failover Routing**
```
Primary: 192.0.2.1 (Health check: Healthy)
Secondary: 192.0.2.2 (Used if primary fails)

If primary unhealthy → Route to secondary
```
**Use Cases:**
- Active-passive DR
- High availability
- Backup resources


**5. Geolocation Routing**
```
Users from US → US server
Users from EU → EU server
Users from Asia → Asia server
Default → US server (for unmatched locations)
```
**Use Cases:**
- Content localization
- Compliance (data sovereignty)
- Region-specific content
- Language-based routing

**6. Geoproximity Routing**
```
Route based on resource location and user location
Bias: -99 to +99 (shrinks or expands region)

Resource A (us-east-1), Bias: +50
Resource B (us-west-2), Bias: -50
→ More traffic goes to Resource A
```
**Use Cases:**
- Complex geographic distribution
- Fine-tuned traffic control
- Multi-region load distribution

**7. Multivalue Answer Routing**
```
Returns multiple healthy records (up to 8)
www.example.com:
  192.0.2.1 (healthy)
  192.0.2.2 (healthy)
  192.0.2.3 (unhealthy - excluded)
```
**Use Cases:**
- Client-side load balancing
- Simple redundancy
- Multiple healthy endpoints

**Decision Tree:**
```
Need health checks? → No → Simple Routing
                    → Yes ↓

Single resource? → Yes → Failover
                → No ↓

Testing new version? → Yes → Weighted
                     → No ↓

Global users? → Yes → Latency or Geolocation
              → No → Simple or Multivalue
```

---

## Monitoring

### Q13: Explain CloudWatch Metrics, Logs, and Alarms. How do they work together?

**Answer:**

**CloudWatch Architecture:**
```
AWS Services → CloudWatch Metrics
Applications → CloudWatch Logs
Metrics + Logs → CloudWatch Alarms → SNS → Actions
```

**1. CloudWatch Metrics**

Numeric measurements over time.

**Built-in Metrics (Free):**
```
EC2: CPU, Network, Disk (5-minute intervals)
RDS: Connections, IOPS, CPU
ELB: Request count, latency
Lambda: Invocations, errors, duration
```

**Custom Metrics:**
```bash
# Publish custom metric
aws cloudwatch put-metric-data \
  --namespace MyApp \
  --metric-name MemoryUsage \
  --value 75.5 \
  --unit Percent
```

**2. CloudWatch Logs**

Store and analyze log data.

**Structure:**
```
Log Group: /aws/lambda/my-function
  ↓
Log Stream: 2026/01/15/[$LATEST]abc123
  ↓
Log Events: Individual log entries with timestamps
```

**Common Sources:**
- Lambda functions (automatic)
- EC2 (requires CloudWatch agent)
- ECS containers
- VPC Flow Logs
- CloudTrail logs
- Application logs

**Log Insights Query:**
```sql
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)
```


**3. CloudWatch Alarms**

Monitor metrics and trigger actions.

**Alarm States:**
```
OK: Metric within threshold
ALARM: Metric breached threshold
INSUFFICIENT_DATA: Not enough data
```

**Example Alarm:**
```json
{
  "AlarmName": "HighCPU",
  "MetricName": "CPUUtilization",
  "Namespace": "AWS/EC2",
  "Statistic": "Average",
  "Period": 300,
  "EvaluationPeriods": 2,
  "Threshold": 80,
  "ComparisonOperator": "GreaterThanThreshold",
  "ActionsEnabled": true,
  "AlarmActions": ["arn:aws:sns:us-east-1:123456789012:alerts"]
}
```

**Alarm Actions:**
- Send SNS notification
- Execute Auto Scaling policy
- Trigger Lambda function
- Create Systems Manager OpsItem

**How They Work Together:**

**Example: Application Monitoring**
```
1. Application logs → CloudWatch Logs
   |
   v
2. Metric Filter: Count ERROR entries
   |
   v
3. CloudWatch Metric: ErrorCount
   |
   v
4. CloudWatch Alarm: If ErrorCount > 10 in 5 min
   |
   v
5. SNS Topic → Email/SMS/Lambda
   |
   v
6. Auto-remediation: Restart service, scale out, etc.
```

**Practical Example:**
```python
# 1. Application logs errors
logger.error("Database connection failed")

# 2. CloudWatch Logs receives log

# 3. Metric Filter (defined in AWS):
[ERROR] - Pattern match

# 4. Increment ErrorCount metric

# 5. Alarm triggers if threshold exceeded

# 6. SNS sends notification to ops team
```

**Best Practices:**
- Use composite alarms for complex conditions
- Set appropriate evaluation periods
- Avoid alarm fatigue (meaningful alerts only)
- Use anomaly detection for dynamic thresholds
- Implement alarming at multiple levels

---

## CloudFormation

### Q14: What is the difference between CloudFormation parameters and mappings?

**Answer:**

**Parameters:**
Input values provided at stack creation/update time.

```yaml
Parameters:
  InstanceType:
    Type: String
    Default: t2.micro
    AllowedValues:
      - t2.micro
      - t2.small
      - t2.medium
    Description: EC2 instance type
  
  Environment:
    Type: String
    AllowedValues:
      - dev
      - staging
      - prod

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
```

**Characteristics:**
- User provides values when deploying
- Validated against constraints
- Can have defaults
- Dynamic inputs

**Mappings:**
Predefined lookup tables within template.

```yaml
Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-0c55b159cbfafe1f0
      InstanceType: t3.micro
    us-west-2:
      AMI: ami-0d1cd67c26f5fca19
      InstanceType: t3.small
  
  EnvironmentMap:
    dev:
      InstanceCount: 1
      DBSize: db.t3.micro
    prod:
      InstanceCount: 5
      DBSize: db.r5.large

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionMap, !Ref 'AWS::Region', AMI]
      InstanceType: !FindInMap [EnvironmentMap, !Ref Environment, InstanceCount]
```


**Characteristics:**
- Hardcoded in template
- Static values
- Lookup using FindInMap
- Cannot be changed without updating template

**When to Use:**

**Parameters:**
- Values that change per deployment
- User-specific inputs
- Secrets (with NoEcho)
- Environment-specific settings

```yaml
# Good parameter use
Parameters:
  DBPassword:
    Type: String
    NoEcho: true
  ProjectName:
    Type: String
```

**Mappings:**
- Region-specific values (AMIs)
- Fixed environment configurations
- Lookup tables
- Multi-dimensional data

```yaml
# Good mapping use
Mappings:
  RegionAMI:
    us-east-1:
      HVM64: ami-0c55b159cbfafe1f0
    eu-west-1:
      HVM64: ami-0bbc25e23a7640b9b
```

**Combined Example:**
```yaml
Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]

Mappings:
  EnvironmentConfig:
    dev:
      InstanceType: t2.micro
      MinSize: 1
      MaxSize: 2
    prod:
      InstanceType: t3.large
      MinSize: 3
      MaxSize: 10

Resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      MinSize: !FindInMap [EnvironmentConfig, !Ref Environment, MinSize]
      MaxSize: !FindInMap [EnvironmentConfig, !Ref Environment, MaxSize]
```

---

### Q15: How do you handle secrets and sensitive data in CloudFormation?

**Answer:**

**Never Do This:**
```yaml
# ❌ NEVER hardcode secrets
Resources:
  Database:
    Properties:
      MasterUserPassword: "MyPassword123"
```

**Best Practices:**

**1. NoEcho Parameters**
```yaml
Parameters:
  DBPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    Description: Database password (will not be shown)

Resources:
  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      MasterUserPassword: !Ref DBPassword
```

**2. AWS Secrets Manager (Recommended)**
```yaml
Resources:
  DBSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Description: RDS database credentials
      GenerateSecretString:
        SecretStringTemplate: '{"username": "admin"}'
        GenerateStringKey: password
        PasswordLength: 32
        ExcludeCharacters: '"@/\'
  
  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      MasterUsername: !Sub '{{resolve:secretsmanager:${DBSecret}:SecretString:username}}'
      MasterUserPassword: !Sub '{{resolve:secretsmanager:${DBSecret}:SecretString:password}}'
```


**3. AWS Systems Manager Parameter Store**
```yaml
# Store parameter first:
aws ssm put-parameter \
  --name /myapp/db/password \
  --value "MySecurePassword" \
  --type SecureString

# Reference in template:
Resources:
  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      MasterUserPassword: !Sub '{{resolve:ssm-secure:/myapp/db/password}}'
```

**4. Dynamic References**
```yaml
# Secrets Manager
!Sub '{{resolve:secretsmanager:secret-id:SecretString:key}}'

# SSM Parameter Store (plain)
!Sub '{{resolve:ssm:parameter-name}}'

# SSM Parameter Store (secure)
!Sub '{{resolve:ssm-secure:parameter-name}}'
```

**5. Pre-created Secrets**
```bash
# Create secret before deploying stack
aws secretsmanager create-secret \
  --name prod-db-password \
  --secret-string "VerySecurePassword123"

# Reference in template
MasterUserPassword: !Sub '{{resolve:secretsmanager:prod-db-password}}'
```

**Complete Example:**
```yaml
Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]

Resources:
  # Create secret
  AppSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub '${Environment}-app-secret'
      GenerateSecretString:
        SecretStringTemplate: '{"username": "appuser"}'
        GenerateStringKey: password
        PasswordLength: 32
  
  # Rotate secret automatically
  SecretRotation:
    Type: AWS::SecretsManager::RotationSchedule
    Properties:
      SecretId: !Ref AppSecret
      RotationLambdaARN: !GetAtt RotationLambda.Arn
      RotationRules:
        AutomaticallyAfterDays: 30
  
  # Use secret in application
  AppConfig:
    Type: AWS::AppConfig::ConfigurationProfile
    Properties:
      ApplicationId: !Ref Application
      LocationUri: !Sub 
        - 'secretsmanager://${SecretArn}'
        - SecretArn: !Ref AppSecret
```

**Key Points:**
- NoEcho prevents console display
- Secrets Manager rotates credentials
- Parameter Store cheaper for simple use cases
- Dynamic references fetch at runtime
- Never commit secrets to version control
- Use least privilege IAM policies

---

## Real-World Scenarios

### Q16: How would you design a highly available web application on AWS?

**Answer:**

**Architecture Components:**

```
         Internet
            |
    [Route53 DNS]
            |
    [CloudFront CDN]
            |
   [Application Load Balancer]
      /              \
[Target Group]  [Target Group]
    |                |
[us-east-1a]    [us-east-1b]
    |                |
[Auto Scaling Group (2-10 instances)]
    |                |
[EC2 Instances]  [EC2 Instances]
    |                |
    +-------+--------+
            |
    [RDS Multi-AZ]
   Primary / Standby
            |
    [ElastiCache]
       (Redis)
```


**Design Decisions:**

**1. Multi-AZ Deployment**
```
Minimum 2 Availability Zones
EC2 instances in both AZs
RDS Multi-AZ for automatic failover
```

**2. Auto Scaling**
```yaml
MinSize: 2 (one per AZ)
DesiredCapacity: 4
MaxSize: 10

Scaling Policies:
  - Target Tracking: CPU 70%
  - Scheduled: Scale up at 9 AM
```

**3. Load Balancing**
```
Application Load Balancer
  - Health checks every 30s
  - Cross-zone enabled
  - Sticky sessions for user state
```

**4. Database Layer**
```
RDS Multi-AZ:
  - Automatic failover
  - Read replicas for read scaling
  - Automated backups (7-day retention)
  
ElastiCache:
  - Cache frequent queries
  - Session storage
  - Reduce DB load
```

**5. Static Content**
```
S3 for static assets
  - Versioning enabled
  - Lifecycle policies
  
CloudFront CDN
  - Global edge locations
  - HTTPS only
  - Origin failover
```

**6. Monitoring**
```
CloudWatch:
  - CPU, memory, disk metrics
  - Custom application metrics
  - Log aggregation
  
Alarms:
  - High CPU → Scale out
  - High error rate → Notify ops
  - Health check failures → Alert
```

**7. Security**
```
VPC:
  - Public subnets: ALB
  - Private subnets: EC2, RDS
  
Security Groups:
  - ALB: Allow 80/443 from internet
  - EC2: Allow traffic only from ALB
  - RDS: Allow traffic only from EC2
  
WAF: Protect against common attacks
```

**Failure Scenarios:**

| Failure | Impact | Mitigation |
|---------|--------|------------|
| EC2 instance fails | Auto Scaling launches replacement | < 5 min recovery |
| AZ outage | Traffic routes to healthy AZ | Automatic |
| RDS primary fails | Multi-AZ fails over to standby | 1-2 min downtime |
| Region outage | Route53 fails over to DR region | Manual or automated |

**Cost Optimization:**
- Reserved Instances for baseline capacity
- Spot Instances for batch processing
- S3 lifecycle policies (S3 → Glacier)
- CloudFront caching reduces origin load
- Auto Scaling handles variable load

---

### Q17: How do you implement blue-green deployment using AWS services?

**Answer:**

**Blue-Green Deployment** maintains two identical production environments, switching traffic between them for zero-downtime deployments.

**Approach 1: Using Route53 Weighted Routing**

**Setup:**
```
Blue Environment (Current Production)
  - ALB: blue-alb.internal
  - Target Group: blue-tg
  - EC2 Instances: Running v1.0

Green Environment (New Version)
  - ALB: green-alb.internal
  - Target Group: green-tg
  - EC2 Instances: Running v2.0
```

**Deployment Steps:**
```
1. Route53 weighted routing:
   www.example.com:
     - blue-alb.internal (Weight: 100)
     - green-alb.internal (Weight: 0)

2. Deploy green environment with new version

3. Test green environment thoroughly

4. Gradually shift traffic:
   - blue-alb (Weight: 90), green-alb (Weight: 10)
   - blue-alb (Weight: 50), green-alb (Weight: 50)
   - blue-alb (Weight: 0), green-alb (Weight: 100)

5. Monitor for issues

6. Rollback if needed:
   - Revert weights to blue: 100

7. Decommission blue environment
```


**Approach 2: Using Target Groups**

```bash
# Current state
ALB → blue-target-group (v1.0)

# Deploy green target group
aws elbv2 create-target-group \
  --name green-target-group \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-12345

# Register green instances
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --targets Id=i-green1 Id=i-green2

# Switch ALB listener to green
aws elbv2 modify-listener \
  --listener-arn arn:aws:elasticloadbalancing:... \
  --default-actions Type=forward,TargetGroupArn=arn:.../green-target-group

# Instant cutover to new version
```

**Approach 3: Using Auto Scaling Groups**

```yaml
BlueAutoScalingGroup:
  MinSize: 2
  DesiredCapacity: 2
  MaxSize: 4
  LaunchTemplate: v1.0

GreenAutoScalingGroup:
  MinSize: 2
  DesiredCapacity: 2  
  MaxSize: 4
  LaunchTemplate: v2.0

# ALB switches between ASGs via target groups
```

**Approach 4: Using CloudFormation**

```yaml
# Create two complete stacks
aws cloudformation create-stack \
  --stack-name app-blue \
  --template-body file://app-template.yaml \
  --parameters ParameterKey=Version,ParameterValue=v1.0

aws cloudformation create-stack \
  --stack-name app-green \
  --template-body file://app-template.yaml \
  --parameters ParameterKey=Version,ParameterValue=v2.0

# Route53 record points to active stack's ALB
```

**Database Considerations:**

```
Option 1: Shared Database
  - Blue and green share same DB
  - Requires backward-compatible schema changes
  - Simpler but riskier

Option 2: Database per Environment
  - Separate DB for blue and green
  - Sync data before cutover
  - More complex but safer
  
Option 3: Read Replicas
  - Green uses read replica promoted to primary
  - Zero data sync time
```

**Monitoring During Deployment:**

```python
# CloudWatch metrics to watch
metrics = [
    'TargetResponseTime',
    'TargetResponseCode',
    'UnHealthyHostCount',
    'RequestCount',
    'ActiveConnectionCount'
]

# Auto-rollback criteria
if green_error_rate > blue_error_rate * 1.5:
    rollback_to_blue()

if green_latency > blue_latency * 2:
    rollback_to_blue()
```

**Pros:**
- Zero downtime
- Easy rollback
- Full testing before cutover
- Reduced risk

**Cons:**
- Double resources during deployment
- Database migration complexity
- Increased cost temporarily
- Stateful application challenges

---

### Q18: Explain how you would troubleshoot high latency in an application running on AWS.

**Answer:**

**Systematic Troubleshooting Approach:**

**1. Identify the Layer**
```
Client → CloudFront → ALB → EC2 → RDS
   │         │         │      │      │
Check each layer for latency
```

**Step 1: CloudWatch Metrics**
```bash
# Check ALB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --dimensions Name=LoadBalancer,Value=app/my-alb/... \
  --start-time 2026-01-15T00:00:00Z \
  --end-time 2026-01-15T23:59:59Z \
  --period 300 \
  --statistics Average
```


**Step 2: Check Each Component**

**CloudFront:**
```
Metrics to check:
  - OriginLatency
  - CacheHitRate (low rate = more origin requests)
  
Issues:
  - Cache not configured properly
  - TTL too low
  - Origin slow to respond
```

**Application Load Balancer:**
```
Metrics to check:
  - TargetResponseTime
  - RequestCount
  - UnhealthyHostCount
  
Issues:
  - Insufficient targets
  - Health check failures
  - SSL negotiation overhead
```

**EC2 Instances:**
```
Metrics to check:
  - CPUUtilization (>80% = problem)
  - NetworkIn/Out
  - DiskReadOps/WriteOps
  - StatusCheckFailed
  
Issues:
  - Undersized instances
  - CPU throttling
  - Memory pressure
  - Disk I/O bottleneck
```

**RDS Database:**
```
Metrics to check:
  - DatabaseConnections
  - ReadLatency / WriteLatency
  - CPUUtilization
  - FreeableMemory
  
Issues:
  - Slow queries
  - Missing indexes
  - Connection pool exhausted
  - Instance too small
```

**Step 3: Application-Level Analysis**

**Enable X-Ray:**
```python
from aws_xray_sdk.core import xray_recorder

@xray_recorder.capture('process_request')
def process_request(event):
    # X-Ray traces this function
    result = call_database()
    return result
```

**Analyze traces:**
```
Request breakdown:
  - ALB: 50ms
  - Application: 200ms
    - Auth check: 20ms
    - Database query: 150ms  ← Problem here!
    - Response formatting: 30ms
```

**Step 4: Common Issues and Solutions**

**Issue: Database Slow Queries**
```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- Find slow queries
SELECT * FROM mysql.slow_log 
WHERE query_time > 2 
ORDER BY query_time DESC;

-- Solution: Add indexes
CREATE INDEX idx_user_email ON users(email);
```

**Issue: High CPU on EC2**
```bash
# Check what's using CPU
top -b -n 1

# Look for memory leaks
free -m

# Check application logs
tail -f /var/log/application.log

# Solution: Scale up or optimize code
```

**Issue: Connection Pool Exhausted**
```python
# ❌ Bad - creates new connection each time
def query_db():
    conn = psycopg2.connect(...)
    result = conn.execute("SELECT ...")
    return result

# ✅ Good - reuse connection pool
import psycopg2.pool
pool = psycopg2.pool.SimpleConnectionPool(5, 20, ...)

def query_db():
    conn = pool.getconn()
    result = conn.execute("SELECT ...")
    pool.putconn(conn)
    return result
```

**Issue: Cold Starts (Lambda)**
```
Solutions:
  - Provisioned concurrency
  - Increase memory
  - Reduce package size
  - Remove VPC if not needed
```


**Step 5: Implement Caching**

```
Application Layer:
  - ElastiCache (Redis/Memcached)
  - Cache frequently accessed data
  - Reduce database load

Content Layer:
  - CloudFront for static assets
  - S3 for media files
  - API Gateway caching

Database Layer:
  - RDS Read Replicas
  - Query result caching
  - DAX for DynamoDB
```

**Troubleshooting Checklist:**
```
□ Check CloudWatch metrics for all components
□ Review application logs for errors
□ Analyze X-Ray traces for bottlenecks
□ Verify Auto Scaling is working
□ Check database query performance
□ Review network connectivity
□ Verify security groups and NACLs
□ Check for throttling (API Gateway, Lambda)
□ Monitor costs (unexpected scaling?)
```

---

### Q19: How would you migrate an on-premises application to AWS with minimal downtime?

**Answer:**

**Migration Strategy:**

**Phase 1: Assessment**
```
1. Application Discovery:
   - Dependencies mapping
   - Database schema analysis
   - Network requirements
   - Performance baselines

2. Tools:
   - AWS Application Discovery Service
   - AWS Migration Evaluator
   - CloudEndure Discovery
```

**Phase 2: Pilot Migration (Dev/Test)**

**Week 1-2: Setup AWS Foundation**
```
1. Create VPC with proper subnets
2. Set up VPN/Direct Connect to on-premises
3. Configure security groups and NACLs
4. Set up IAM roles and policies
5. Create S3 buckets for data
```

**Week 3-4: Database Migration**

**Option A: Database Migration Service (DMS)**
```
1. Create replication instance
2. Set up source endpoint (on-prem DB)
3. Set up target endpoint (RDS)
4. Create migration task
5. Start continuous replication

Source DB (on-prem)
    ↓ Continuous replication
Target DB (RDS)
```

**Commands:**
```bash
# Create replication instance
aws dms create-replication-instance \
  --replication-instance-identifier migration-instance \
  --replication-instance-class dms.t3.medium

# Create endpoints
aws dms create-endpoint \
  --endpoint-identifier source-db \
  --endpoint-type source \
  --engine-name mysql \
  --server-name on-prem-server.local \
  --port 3306

# Start replication
aws dms start-replication-task \
  --replication-task-arn arn:aws:dms:... \
  --start-replication-task-type start-replication
```

**Option B: Native Database Tools**
```bash
# MySQL example
# 1. Initial dump
mysqldump --all-databases > initial_dump.sql

# 2. Upload to S3
aws s3 cp initial_dump.sql s3://migration-bucket/

# 3. Restore to RDS
mysql -h rds-endpoint < initial_dump.sql

# 4. Set up binary log replication
```

**Week 5-6: Application Migration**

**Option A: Lift-and-Shift (EC2)**
```
1. Create AMIs from on-prem servers
2. Launch EC2 instances from AMIs
3. Configure ALB and Auto Scaling
4. Test application thoroughly
```

**Option B: Refactor to Containers (ECS)**
```
1. Containerize application
2. Push images to ECR
3. Deploy to ECS Fargate
4. Configure ALB
```


**Phase 3: Cutover Strategy**

**Approach 1: DNS Cutover (Recommended)**
```
1. On-Premises:
   www.example.com → On-prem LB (TTL: 300)
   
2. Sync data to AWS (DMS running)

3. Verify AWS environment ready
   - All health checks passing
   - Data in sync
   - Load testing complete

4. Lower DNS TTL
   www.example.com → On-prem LB (TTL: 60)
   Wait 5 minutes

5. Switch DNS to AWS
   www.example.com → AWS ALB (TTL: 60)

6. Monitor closely (1-2 hours)

7. Keep on-prem running as fallback (1 week)

Downtime: < 5 minutes (DNS propagation)
```

**Approach 2: Gradual Migration (Blue-Green)**
```
Week 1: 10% traffic to AWS (Route53 weighted routing)
Week 2: 25% traffic to AWS
Week 3: 50% traffic to AWS
Week 4: 100% traffic to AWS

Downtime: 0 minutes
```

**Migration Timeline:**

```
Day 1-7: Infrastructure setup
Day 8-14: Database initial sync
Day 15-21: Application deployment and testing
Day 22-28: Parallel run (both environments)
Day 29: Cutover window
Day 30-37: Post-cutover monitoring
Day 38-45: Decommission on-premises
```

**Rollback Plan:**

```
If issues detected within first 24 hours:

1. Immediate: DNS switch back to on-premises
2. Database: Stop DMS replication
3. Investigation: Review CloudWatch logs/metrics
4. Fix: Address issues in AWS environment
5. Retry: Attempt cutover again

Recovery Time: 10-15 minutes
```

**Post-Migration:**

```
□ Verify all functionality
□ Performance testing
□ Security audit
□ Cost optimization
□ Documentation update
□ Team training
□ Decommission on-premises (after 30 days)
```

---

### Q20: How do you implement disaster recovery for a mission-critical application on AWS?

**Answer:**

**DR Strategy Levels:**

**1. Backup and Restore (RPO: hours, RTO: hours-days)**
```
Cost: Lowest
Complexity: Lowest

Implementation:
  - Automated S3 snapshots
  - RDS automated backups
  - EBS snapshots
  - AMI backups

Recovery Process:
  1. Launch instances from AMIs
  2. Restore RDS from snapshot
  3. Attach EBS volumes
  4. Update DNS

Example:
aws ec2 create-snapshot \
  --volume-id vol-1234567890abcdef0 \
  --description "Daily backup"
```

**2. Pilot Light (RPO: minutes, RTO: hours)**
```
Cost: Low-Medium
Complexity: Medium

Active:
  - Database replication running
  - Core infrastructure provisioned but minimal
  - AMIs and configs ready

Standby:
  - Scaled-down resources
  - Minimal compute instances
  - Data continuously replicated

Recovery Process:
  1. Scale up compute resources
  2. Update DNS to DR region
  3. Test and verify
  
Time: 1-4 hours
```


**3. Warm Standby (RPO: seconds, RTO: minutes)**
```
Cost: Medium-High
Complexity: High

Primary Region (us-east-1):
  - Full production environment
  - All services running
  - 100% traffic

DR Region (us-west-2):
  - Scaled-down but running
  - Database replication active
  - Ready to scale up instantly

Implementation:
  - RDS Cross-Region Read Replicas
  - S3 Cross-Region Replication
  - Route53 Health Checks
  - Auto Scaling policies ready

Recovery:
  1. Promote read replica to primary
  2. Scale up DR instances
  3. Route53 failover
  
Time: 10-30 minutes
```

**4. Multi-Region Active-Active (RPO: 0, RTO: seconds)**
```
Cost: Highest (2x infrastructure)
Complexity: Very High

Both Regions Active:
  - us-east-1: 50% traffic
  - us-west-2: 50% traffic
  - Real-time data sync
  - Global Accelerator

Benefits:
  - Zero downtime
  - No data loss
  - Instant failover
  - Performance benefits

Challenges:
  - Data consistency
  - Conflict resolution
  - Cost (double resources)
```

**Complete DR Implementation:**

**Architecture:**
```yaml
Primary Region (us-east-1):
  VPC: 10.0.0.0/16
  Resources:
    - ALB
    - Auto Scaling Group (4-10 instances)
    - RDS Multi-AZ
    - ElastiCache
    - S3 (versioning enabled)
    
DR Region (us-west-2):
  VPC: 10.1.0.0/16
  Resources:
    - ALB (standby)
    - Auto Scaling Group (2-4 instances)
    - RDS Read Replica
    - ElastiCache (optional)
    - S3 (replica)

Global:
  Route53:
    - Primary: us-east-1
    - Failover: us-west-2
    - Health checks every 30s
```

**Database DR:**
```bash
# RDS Cross-Region Read Replica
aws rds create-db-instance-read-replica \
  --db-instance-identifier dr-replica \
  --source-db-instance-identifier prod-db \
  --source-region us-east-1 \
  --region us-west-2

# Promote replica during DR
aws rds promote-read-replica \
  --db-instance-identifier dr-replica \
  --region us-west-2
```

**S3 Replication:**
```json
{
  "Role": "arn:aws:iam::123456789012:role/s3-replication-role",
  "Rules": [{
    "Status": "Enabled",
    "Priority": 1,
    "Filter": {},
    "Destination": {
      "Bucket": "arn:aws:s3:::dr-bucket-us-west-2",
      "ReplicationTime": {
        "Status": "Enabled",
        "Time": {
          "Minutes": 15
        }
      }
    }
  }]
}
```

**Route53 Failover:**
```bash
# Primary record
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "www.example.com",
        "Type": "A",
        "SetIdentifier": "Primary",
        "Failover": "PRIMARY",
        "AliasTarget": {
          "HostedZoneId": "Z1234567890ABC",
          "DNSName": "us-east-1-alb.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'

# Secondary (DR) record
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "www.example.com",
        "Type": "A",
        "SetIdentifier": "Secondary",
        "Failover": "SECONDARY",
        "AliasTarget": {
          "HostedZoneId": "Z0987654321XYZ",
          "DNSName": "us-west-2-alb.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'
```

**DR Testing:**
```
Monthly Tests:
  □ Backup restoration
  □ Failover simulation
  □ Data integrity verification
  □ RPO/RTO measurement
  
Quarterly Tests:
  □ Full DR drill
  □ Team runbook practice
  □ Documentation update
  
Annual Tests:
  □ Complete failover with live traffic
  □ Extended DR operation (24-48 hours)
```

**DR Metrics:**
```
RPO (Recovery Point Objective):
  - Maximum acceptable data loss
  - Backup and Restore: 24 hours
  - Pilot Light: 1 hour
  - Warm Standby: 1 minute
  - Active-Active: 0 seconds

RTO (Recovery Time Objective):
  - Maximum acceptable downtime
  - Backup and Restore: 24 hours
  - Pilot Light: 4 hours
  - Warm Standby: 30 minutes
  - Active-Active: 0 seconds
```

---

## Summary

These 20 intermediate questions cover:
- VPC networking and connectivity
- Load balancing strategies
- Auto Scaling configurations
- Database management and replication
- Serverless architecture
- DNS and routing
- Monitoring and troubleshooting
- Infrastructure as Code
- Real-world scenarios and DR

**Next Steps:**
- Review advanced AWS topics
- Practice hands-on labs
- Build real-world projects
- Study AWS Well-Architected Framework

**Related Files:**
- [13-cloudformation-basics.md](./13-cloudformation-basics.md) - CloudFormation deep dive
- [../03-advanced/interview-questions-advanced.md](../03-advanced/interview-questions-advanced.md) - Advanced questions

