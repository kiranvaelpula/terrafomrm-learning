# Chapter 21: Multi-Region Architecture

## Overview

Multi-region architecture provides global reach, disaster recovery, and compliance with data residency requirements.

**Topics:**
- Multi-region strategies
- Global services (CloudFront, Route53)
- Cross-region replication
- Global databases (Aurora Global, DynamoDB Global Tables)
- Latency-based routing
- Disaster recovery patterns

---

## Why Multi-Region?

**Benefits:**
- Lower latency for global users
- Disaster recovery
- Data residency compliance
- High availability

**Challenges:**
- Data consistency
- Increased complexity
- Higher costs
- Cross-region data transfer fees

---

## Global Services

### CloudFront

```bash
# Create distribution
aws cloudfront create-distribution \
  --distribution-config file://distribution-config.json
```

**distribution-config.json:**
```json
{
  "CallerReference": "unique-ref-123",
  "Comment": "Global CDN",
  "Origins": {
    "Quantity": 2,
    "Items": [
      {
        "Id": "us-east-1-origin",
        "DomainName": "us-east-1-alb.elb.amazonaws.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "https-only"
        }
      },
      {
        "Id": "eu-west-1-origin",
        "DomainName": "eu-west-1-alb.elb.amazonaws.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "https-only"
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "us-east-1-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 7,
      "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    },
    "ForwardedValues": {
      "QueryString": true,
      "Cookies": {"Forward": "all"}
    }
  },
  "Enabled": true
}
```

### Route53 Latency-Based Routing

```bash
# Create hosted zone
aws route53 create-hosted-zone \
  --name example.com \
  --caller-reference 2026-01-15

# Create latency records
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://latency-records.json
```

**latency-records.json:**
```json
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "www.example.com",
        "Type": "A",
        "SetIdentifier": "US East",
        "Region": "us-east-1",
        "AliasTarget": {
          "HostedZoneId": "Z35SXDOTRQ7X7K",
          "DNSName": "us-east-1-alb.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    },
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "www.example.com",
        "Type": "A",
        "SetIdentifier": "EU West",
        "Region": "eu-west-1",
        "AliasTarget": {
          "HostedZoneId": "Z32O12XQLNTSW2",
          "DNSName": "eu-west-1-alb.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }
  ]
}
```

---

## S3 Cross-Region Replication

```bash
# Enable versioning (required)
aws s3api put-bucket-versioning \
  --bucket source-bucket \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-versioning \
  --bucket destination-bucket \
  --versioning-configuration Status=Enabled

# Set up replication
aws s3api put-bucket-replication \
  --bucket source-bucket \
  --replication-configuration file://replication.json
```

**replication.json:**
```json
{
  "Role": "arn:aws:iam::123456789012:role/s3-replication-role",
  "Rules": [{
    "Status": "Enabled",
    "Priority": 1,
    "Filter": {},
    "Destination": {
      "Bucket": "arn:aws:s3:::destination-bucket",
      "ReplicationTime": {
        "Status": "Enabled",
        "Time": {"Minutes": 15}
      },
      "Metrics": {
        "Status": "Enabled",
        "EventThreshold": {"Minutes": 15}
      }
    },
    "DeleteMarkerReplication": {"Status": "Enabled"}
  }]
}
```

---

## Aurora Global Database

```bash
# Create primary cluster
aws rds create-db-cluster \
  --db-cluster-identifier primary-cluster \
  --engine aurora-mysql \
  --engine-version 8.0.mysql_aurora.3.02.0 \
  --master-username admin \
  --master-user-password password \
  --database-name mydb \
  --region us-east-1

# Create global cluster
aws rds create-global-cluster \
  --global-cluster-identifier my-global-cluster \
  --source-db-cluster-identifier arn:aws:rds:us-east-1:123456789012:cluster:primary-cluster

# Add secondary region
aws rds create-db-cluster \
  --db-cluster-identifier secondary-cluster \
  --engine aurora-mysql \
  --global-cluster-identifier my-global-cluster \
  --region eu-west-1
```

**Features:**
- Replication lag < 1 second
- Read replicas in secondary regions
- Fast recovery (< 1 minute RTO)

---

## DynamoDB Global Tables

```bash
# Create table in primary region
aws dynamodb create-table \
  --table-name Users \
  --attribute-definitions AttributeName=UserId,AttributeType=S \
  --key-schema AttributeName=UserId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
  --region us-east-1

# Enable global table
aws dynamodb create-global-table \
  --global-table-name Users \
  --replication-group RegionName=us-east-1 RegionName=eu-west-1 \
  --region us-east-1
```

**Features:**
- Multi-master (write to any region)
- Automatic replication
- Conflict resolution (last writer wins)

---

## Multi-Region Architecture Patterns

### 1. Active-Passive (DR)

```
Primary Region (us-east-1) - 100% traffic
    |
    +-- Application
    +-- Database (Aurora Global primary)
    +-- S3 (CRR to secondary)

Secondary Region (eu-west-1) - Standby
    |
    +-- Application (scaled to 0)
    +-- Database (Aurora Global secondary)
    +-- S3 (replica)
```

**Failover Process:**
1. Detect primary region failure
2. Promote secondary Aurora cluster
3. Update Route53 to point to secondary
4. Scale up secondary application
5. Monitor and verify

### 2. Active-Active

```
Region 1 (us-east-1) - 50% traffic
    |
    +-- Application
    +-- DynamoDB Global Table
    +-- Aurora Global (or separate DB)

Region 2 (eu-west-1) - 50% traffic
    |
    +-- Application
    +-- DynamoDB Global Table
    +-- Aurora Global (or separate DB)

Route53 Latency-Based Routing
```

### 3. Active-Active with Read Replicas

```
Region 1 - Writes + Reads
    +-- Primary RDS
    +-- Read Replicas

Region 2 - Reads only
    +-- Cross-Region Read Replicas
```

---

## Data Consistency

### Strategies:

**1. Eventual Consistency**
- S3 CRR, DynamoDB Global Tables
- Lower latency, higher availability
- Accept temporary inconsistencies

**2. Strong Consistency**
- Single-region writes
- Synchronous replication
- Higher latency, guaranteed consistency

**3. Application-Level**
- Version vectors
- Conflict-free replicated data types (CRDTs)
- Custom conflict resolution

---

## Cost Considerations

**Cross-Region Data Transfer:**
```
us-east-1 → eu-west-1: $0.02/GB
S3 CRR: $0.02/GB + storage in both regions
DynamoDB Global Tables: $0.02/GB + storage/requests in both regions
Aurora Global: $0.02/GB + instance costs in both regions
```

**Optimization:**
- Use CloudFront to reduce origin requests
- Compress data before replication
- Replicate only necessary data
- Use lifecycle policies

---

## AWS Global Accelerator

**What is Global Accelerator?**
- Static anycast IPs
- Routes traffic over AWS backbone
- Automatic failover
- Performance improvement (up to 60%)

**Creating Global Accelerator:**
```bash
# Create accelerator
aws globalaccelerator create-accelerator \
  --name my-accelerator \
  --ip-address-type IPV4 \
  --enabled

# Add listener
aws globalaccelerator create-listener \
  --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abc-123 \
  --port-ranges FromPort=80,ToPort=80 FromPort=443,ToPort=443 \
  --protocol TCP

# Create endpoint group (us-east-1)
aws globalaccelerator create-endpoint-group \
  --listener-arn arn:aws:globalaccelerator::123456789012:listener/xyz-456 \
  --endpoint-group-region us-east-1 \
  --endpoint-configurations \
    EndpointId=arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/abc,Weight=100

# Create endpoint group (eu-west-1)
aws globalaccelerator create-endpoint-group \
  --listener-arn arn:aws:globalaccelerator::123456789012:listener/xyz-456 \
  --endpoint-group-region eu-west-1 \
  --endpoint-configurations \
    EndpointId=arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/app/my-alb/def,Weight=100
```

**Global Accelerator vs CloudFront:**

| Feature | Global Accelerator | CloudFront |
|---------|-------------------|------------|
| **Use Case** | TCP/UDP applications | HTTP/HTTPS content |
| **Caching** | No | Yes |
| **Static IPs** | Yes (2 anycast IPs) | No |
| **Protocols** | TCP, UDP | HTTP, HTTPS, WebSocket |
| **Health Checks** | Yes | Yes |
| **Failover** | Automatic | Manual (origin groups) |
| **Best For** | Gaming, IoT, VoIP | Websites, APIs, streaming |

---

## Lambda@Edge and CloudFront Functions

### Lambda@Edge

**Use Cases:**
- A/B testing
- Authentication/authorization
- Bot detection
- Header manipulation
- Image transformation

**Event Types:**
1. **Viewer Request**: CloudFront receives request
2. **Origin Request**: CloudFront forwards to origin
3. **Origin Response**: CloudFront receives response
4. **Viewer Response**: CloudFront returns to user

**Example: A/B Testing**
```python
import json

def lambda_handler(event, context):
    request = event['Records'][0]['cf']['request']
    headers = request['headers']
    
    # Check for existing cookie
    cookie_header = headers.get('cookie', [])
    cookies = {}
    
    if cookie_header:
        for cookie in cookie_header[0]['value'].split(';'):
            if '=' in cookie:
                key, value = cookie.strip().split('=', 1)
                cookies[key] = value
    
    # Assign experiment group
    experiment_group = cookies.get('experiment', None)
    
    if not experiment_group:
        import random
        experiment_group = 'A' if random.random() < 0.5 else 'B'
        
        # Add cookie to response
        response = {
            'status': '302',
            'statusDescription': 'Found',
            'headers': {
                'location': [{
                    'key': 'Location',
                    'value': request['uri']
                }],
                'set-cookie': [{
                    'key': 'Set-Cookie',
                    'value': f'experiment={experiment_group}; Path=/; Max-Age=2592000'
                }]
            }
        }
        return response
    
    # Route based on experiment
    if experiment_group == 'B':
        request['uri'] = f'/variant-b{request["uri"]}'
    
    return request
```

**Deploy Lambda@Edge:**
```bash
# Create Lambda function
aws lambda create-function \
  --region us-east-1 \
  --function-name ab-testing \
  --runtime python3.9 \
  --role arn:aws:iam::123456789012:role/lambda-edge-role \
  --handler index.lambda_handler \
  --zip-file fileb://function.zip

# Publish version
VERSION=$(aws lambda publish-version \
  --function-name ab-testing \
  --query 'Version' --output text)

# Associate with CloudFront
aws cloudfront update-distribution \
  --id E123EXAMPLE \
  --distribution-config file://distribution-with-lambda.json
```

### CloudFront Functions

**Lighter, faster, cheaper than Lambda@Edge**

**Example: Add Security Headers**
```javascript
function handler(event) {
    var response = event.response;
    var headers = response.headers;
    
    // Add security headers
    headers['strict-transport-security'] = { value: 'max-age=31536000; includeSubdomains; preload'};
    headers['content-security-policy'] = { value: "default-src 'self'"};
    headers['x-content-type-options'] = { value: 'nosniff'};
    headers['x-frame-options'] = { value: 'DENY'};
    headers['x-xss-protection'] = { value: '1; mode=block'};
    headers['referrer-policy'] = { value: 'same-origin'};
    
    return response;
}
```

**Deploy CloudFront Function:**
```bash
# Create function
aws cloudfront create-function \
  --name security-headers \
  --function-config Comment="Add security headers",Runtime=cloudfront-js-1.0 \
  --function-code fileb://function.js

# Publish function
aws cloudfront publish-function \
  --name security-headers \
  --if-match ETVABCEXAMPLE

# Associate with distribution
aws cloudfront update-distribution \
  --id E123EXAMPLE \
  --distribution-config file://distribution-with-function.json
```

---

## Cross-Region VPC Connectivity

### VPC Peering

**Limitations:**
- No transitive routing
- CIDR blocks cannot overlap
- Not scalable for many VPCs

**Setup:**
```bash
# Create peering connection
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-11111111 \
  --peer-vpc-id vpc-22222222 \
  --peer-region eu-west-1

# Accept connection (in peer region)
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id pcx-123456 \
  --region eu-west-1

# Add routes (both VPCs)
aws ec2 create-route \
  --route-table-id rtb-11111111 \
  --destination-cidr-block 10.1.0.0/16 \
  --vpc-peering-connection-id pcx-123456
```

### Transit Gateway

**Benefits:**
- Hub-and-spoke topology
- Transitive routing
- Scales to thousands of VPCs
- Cross-region support

**Architecture:**
```
        Transit Gateway (us-east-1)
                |
    +-----------+------------+
    |           |            |
  VPC-A       VPC-B        VPC-C
    |
    Peering Connection
    |
        Transit Gateway (eu-west-1)
                |
    +-----------+------------+
    |           |            |
  VPC-D       VPC-E        VPC-F
```

**Setup:**
```bash
# Create Transit Gateway (us-east-1)
TGW_US=$(aws ec2 create-transit-gateway \
  --description "US Transit Gateway" \
  --options AmazonSideAsn=64512 \
  --region us-east-1 \
  --query 'TransitGateway.TransitGatewayId' --output text)

# Create Transit Gateway (eu-west-1)
TGW_EU=$(aws ec2 create-transit-gateway \
  --description "EU Transit Gateway" \
  --options AmazonSideAsn=64513 \
  --region eu-west-1 \
  --query 'TransitGateway.TransitGatewayId' --output text)

# Create cross-region peering
aws ec2 create-transit-gateway-peering-attachment \
  --transit-gateway-id $TGW_US \
  --peer-transit-gateway-id $TGW_EU \
  --peer-region eu-west-1 \
  --region us-east-1

# Attach VPC to Transit Gateway
aws ec2 create-transit-gateway-vpc-attachment \
  --transit-gateway-id $TGW_US \
  --vpc-id vpc-11111111 \
  --subnet-ids subnet-111 subnet-222
```

### AWS PrivateLink

**Use Case:** Access services across VPCs/regions privately

```bash
# Create VPC endpoint service (provider)
aws ec2 create-vpc-endpoint-service-configuration \
  --network-load-balancer-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/my-nlb/abc \
  --acceptance-required

# Create VPC endpoint (consumer)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-22222222 \
  --service-name com.amazonaws.vpce.us-east-1.vpce-svc-123456 \
  --vpc-endpoint-type Interface \
  --subnet-ids subnet-333 subnet-444
```

---

## RDS Cross-Region Read Replicas

**Use Cases:**
- Disaster recovery
- Low-latency reads in other regions
- Migration to new region

**Create Read Replica:**
```bash
# Create cross-region read replica
aws rds create-db-instance-read-replica \
  --db-instance-identifier mydb-replica-eu \
  --source-db-instance-identifier arn:aws:rds:us-east-1:123456789012:db:mydb \
  --db-instance-class db.r5.large \
  --region eu-west-1

# Promote to standalone (for DR)
aws rds promote-read-replica \
  --db-instance-identifier mydb-replica-eu \
  --region eu-west-1
```

**Aurora Global Database (Better Option):**
```bash
# Create global cluster
aws rds create-global-cluster \
  --global-cluster-identifier my-global-cluster \
  --engine aurora-mysql \
  --engine-version 5.7.mysql_aurora.2.10.1

# Create primary cluster
aws rds create-db-cluster \
  --db-cluster-identifier primary-cluster \
  --engine aurora-mysql \
  --global-cluster-identifier my-global-cluster \
  --master-username admin \
  --master-user-password MyPassword123 \
  --region us-east-1

# Add secondary region
aws rds create-db-cluster \
  --db-cluster-identifier secondary-cluster \
  --engine aurora-mysql \
  --global-cluster-identifier my-global-cluster \
  --region eu-west-1

# Failover to secondary
aws rds failover-global-cluster \
  --global-cluster-identifier my-global-cluster \
  --target-db-cluster-identifier secondary-cluster
```

**Performance:**
- Replication lag: < 1 second
- RTO (Recovery Time): < 1 minute
- RPO (Recovery Point): < 1 second

---

## ElastiCache Global Datastore

**For Redis caching across regions**

```bash
# Create primary replication group
aws elasticache create-replication-group \
  --replication-group-id cache-primary \
  --replication-group-description "Primary cache" \
  --engine redis \
  --cache-node-type cache.r5.large \
  --num-cache-clusters 2 \
  --region us-east-1

# Create global datastore
aws elasticache create-global-replication-group \
  --global-replication-group-id-suffix global-cache \
  --primary-replication-group-id cache-primary \
  --region us-east-1

# Add secondary region
aws elasticache create-replication-group \
  --replication-group-id cache-secondary \
  --replication-group-description "Secondary cache" \
  --global-replication-group-id cache-primary-global-cache \
  --region eu-west-1
```

**Features:**
- Sub-second replication
- Local read latency
- Failover capability

---

## Monitoring Multi-Region

**CloudWatch Cross-Region Dashboard:**
```python
import boto3
import json

cloudwatch = boto3.client('cloudwatch')

# Create dashboard
dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/ApplicationELB", "RequestCount", {"region": "us-east-1", "label": "US East"}],
                    ["...", {"region": "eu-west-1", "label": "EU West"}],
                    ["...", {"region": "ap-southeast-1", "label": "Asia Pacific"}]
                ],
                "period": 300,
                "stat": "Sum",
                "region": "us-east-1",
                "title": "Global Request Count",
                "yAxis": {"left": {"label": "Requests"}}
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/ApplicationELB", "TargetResponseTime", {"region": "us-east-1", "stat": "Average"}],
                    ["...", {"region": "eu-west-1"}],
                    ["...", {"region": "ap-southeast-1"}]
                ],
                "period": 300,
                "stat": "Average",
                "region": "us-east-1",
                "title": "Response Time by Region",
                "yAxis": {"left": {"label": "Seconds"}}
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/RDS", "AuroraGlobalDBReplicationLag", {"DBClusterIdentifier": "secondary-cluster"}]
                ],
                "period": 60,
                "stat": "Average",
                "region": "us-east-1",
                "title": "Aurora Replication Lag"
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='GlobalApp',
    DashboardBody=json.dumps(dashboard_body)
)

print("Dashboard created successfully")
```

**CloudWatch Alarms for Multi-Region:**
```python
# Alarm for high replication lag
cloudwatch.put_metric_alarm(
    AlarmName='aurora-replication-lag-high',
    ComparisonOperator='GreaterThanThreshold',
    EvaluationPeriods=2,
    MetricName='AuroraGlobalDBReplicationLag',
    Namespace='AWS/RDS',
    Period=60,
    Statistic='Average',
    Threshold=5000.0,  # 5 seconds
    ActionsEnabled=True,
    AlarmActions=['arn:aws:sns:us-east-1:123456789012:ops-team'],
    AlarmDescription='Aurora replication lag exceeded 5 seconds',
    Dimensions=[
        {
            'Name': 'DBClusterIdentifier',
            'Value': 'secondary-cluster'
        }
    ]
)

# Alarm for regional failover
cloudwatch.put_metric_alarm(
    AlarmName='us-east-1-unhealthy',
    ComparisonOperator='LessThanThreshold',
    EvaluationPeriods=2,
    MetricName='HealthyHostCount',
    Namespace='AWS/ApplicationELB',
    Period=60,
    Statistic='Average',
    Threshold=1.0,
    ActionsEnabled=True,
    AlarmActions=['arn:aws:sns:us-east-1:123456789012:failover-lambda'],
    AlarmDescription='No healthy hosts in us-east-1'
)
```

---

## Regional Failover Automation

**Automated Failover Lambda:**
```python
import boto3
import json

route53 = boto3.client('route53')
rds = boto3.client('rds')

def lambda_handler(event, context):
    """
    Automated failover to secondary region
    Triggered by CloudWatch alarm or manual invocation
    """
    
    # Configuration
    hosted_zone_id = 'Z1234567890ABC'
    primary_region = 'us-east-1'
    secondary_region = 'eu-west-1'
    record_name = 'app.example.com'
    
    # Step 1: Promote Aurora secondary to primary
    try:
        print("Promoting Aurora secondary cluster...")
        rds_eu = boto3.client('rds', region_name=secondary_region)
        
        response = rds_eu.failover_global_cluster(
            GlobalClusterIdentifier='my-global-cluster',
            TargetDbClusterIdentifier='secondary-cluster'
        )
        print(f"Aurora failover initiated: {response}")
        
    except Exception as e:
        print(f"Error promoting Aurora: {e}")
        return {'statusCode': 500, 'body': json.dumps(f'Aurora failover failed: {e}')}
    
    # Step 2: Update Route53 to point to secondary region ALB
    try:
        print("Updating Route53 records...")
        
        # Get current record
        response = route53.list_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            StartRecordName=record_name,
            StartRecordType='A',
            MaxItems='1'
        )
        
        current_record = response['ResourceRecordSets'][0]
        
        # Update to secondary region
        change_batch = {
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': record_name,
                        'Type': 'A',
                        'SetIdentifier': 'EU West (Failover)',
                        'Region': secondary_region,
                        'AliasTarget': {
                            'HostedZoneId': 'Z32O12XQLNTSW2',  # EU-West-1 ALB zone
                            'DNSName': 'eu-west-1-alb.elb.amazonaws.com',
                            'EvaluateTargetHealth': True
                        }
                    }
                }
            ]
        }
        
        response = route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch=change_batch
        )
        
        print(f"Route53 updated: {response['ChangeInfo']['Id']}")
        
    except Exception as e:
        print(f"Error updating Route53: {e}")
        return {'statusCode': 500, 'body': json.dumps(f'Route53 update failed: {e}')}
    
    # Step 3: Scale up secondary region capacity
    try:
        print("Scaling secondary region...")
        
        autoscaling_eu = boto3.client('autoscaling', region_name=secondary_region)
        
        autoscaling_eu.set_desired_capacity(
            AutoScalingGroupName='secondary-asg',
            DesiredCapacity=10,  # Match primary capacity
            HonorCooldown=False
        )
        
        print("Secondary region scaled up")
        
    except Exception as e:
        print(f"Error scaling: {e}")
    
    # Step 4: Send notification
    try:
        sns = boto3.client('sns')
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:123456789012:ops-team',
            Subject='CRITICAL: Failover to EU-West-1 Completed',
            Message=f'''
            Automated failover to secondary region completed.
            
            Actions taken:
            1. Aurora cluster promoted in eu-west-1
            2. Route53 updated to point to eu-west-1
            3. Auto Scaling group scaled to 10 instances
            
            Please verify application functionality.
            '''
        )
    except Exception as e:
        print(f"Error sending notification: {e}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Failover completed successfully')
    }
```

**Deploy Failover Automation:**
```bash
# Create IAM role for Lambda
aws iam create-role \
  --role-name failover-lambda-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach policies
aws iam attach-role-policy \
  --role-name failover-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonRDSFullAccess

aws iam attach-role-policy \
  --role-name failover-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonRoute53FullAccess

# Create Lambda function
aws lambda create-function \
  --function-name regional-failover \
  --runtime python3.9 \
  --role arn:aws:iam::123456789012:role/failover-lambda-role \
  --handler index.lambda_handler \
  --zip-file fileb://failover.zip \
  --timeout 300

# Create SNS topic for alarms
aws sns create-topic --name regional-failover

# Subscribe Lambda to SNS
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:regional-failover \
  --protocol lambda \
  --notification-endpoint arn:aws:lambda:us-east-1:123456789012:function:regional-failover
```

---

## Route53 Advanced Routing

### Health Checks

```bash
# Create health check
aws route53 create-health-check \
  --caller-reference 2026-01-15-us-east-1 \
  --health-check-config '{
    "Type": "HTTPS",
    "ResourcePath": "/health",
    "FullyQualifiedDomainName": "us-east-1-alb.elb.amazonaws.com",
    "Port": 443,
    "RequestInterval": 30,
    "FailureThreshold": 3
  }'

# Configure alarm on health check
aws route53 put-alarm \
  --health-check-id abc-123 \
  --alarm-name "US-East-1 Unhealthy" \
  --comparison-operator LessThanThreshold \
  --evaluation-periods 2 \
  --metric-name HealthCheckStatus \
  --namespace AWS/Route53 \
  --period 60 \
  --statistic Minimum \
  --threshold 1.0
```

### Geolocation Routing

```bash
# Create geolocation records
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "www.example.com",
          "Type": "A",
          "SetIdentifier": "North America",
          "GeoLocation": {"ContinentCode": "NA"},
          "AliasTarget": {
            "HostedZoneId": "Z35SXDOTRQ7X7K",
            "DNSName": "us-east-1-alb.elb.amazonaws.com",
            "EvaluateTargetHealth": true
          }
        }
      },
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "www.example.com",
          "Type": "A",
          "SetIdentifier": "Europe",
          "GeoLocation": {"ContinentCode": "EU"},
          "AliasTarget": {
            "HostedZoneId": "Z32O12XQLNTSW2",
            "DNSName": "eu-west-1-alb.elb.amazonaws.com",
            "EvaluateTargetHealth": true
          }
        }
      },
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "www.example.com",
          "Type": "A",
          "SetIdentifier": "Default",
          "GeoLocation": {"ContinentCode": "*"},
          "AliasTarget": {
            "HostedZoneId": "Z35SXDOTRQ7X7K",
            "DNSName": "us-east-1-alb.elb.amazonaws.com",
            "EvaluateTargetHealth": true
          }
        }
      }
    ]
  }'
```

### Weighted Routing (Traffic Shifting)

```bash
# Gradual traffic shift: 10% to new region
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [
      {
        "Action": "UPSERT",
        "ResourceRecordSet": {
          "Name": "api.example.com",
          "Type": "A",
          "SetIdentifier": "US-East-1",
          "Weight": 90,
          "AliasTarget": {
            "HostedZoneId": "Z35SXDOTRQ7X7K",
            "DNSName": "us-east-1-alb.elb.amazonaws.com",
            "EvaluateTargetHealth": true
          }
        }
      },
      {
        "Action": "UPSERT",
        "ResourceRecordSet": {
          "Name": "api.example.com",
          "Type": "A",
          "SetIdentifier": "EU-West-1",
          "Weight": 10,
          "AliasTarget": {
            "HostedZoneId": "Z32O12XQLNTSW2",
            "DNSName": "eu-west-1-alb.elb.amazonaws.com",
            "EvaluateTargetHealth": true
          }
        }
      }
    ]
  }'
```

---

## Complete Multi-Region Deployment Example

**Terraform Configuration:**
```hcl
# variables.tf
variable "regions" {
  type = map(object({
    cidr_block = string
    azs        = list(string)
  }))
  default = {
    "us-east-1" = {
      cidr_block = "10.0.0.0/16"
      azs        = ["us-east-1a", "us-east-1b"]
    }
    "eu-west-1" = {
      cidr_block = "10.1.0.0/16"
      azs        = ["eu-west-1a", "eu-west-1b"]
    }
  }
}

# main.tf
module "regional_infrastructure" {
  source   = "./modules/regional"
  for_each = var.regions
  
  region     = each.key
  cidr_block = each.value.cidr_block
  azs        = each.value.azs
}

# modules/regional/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
  alias  = "regional"
}

# VPC
resource "aws_vpc" "main" {
  provider             = aws.regional
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name   = "vpc-${var.region}"
    Region = var.region
  }
}

# Subnets
resource "aws_subnet" "public" {
  provider                = aws.regional
  count                   = length(var.azs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.cidr_block, 8, count.index)
  availability_zone       = var.azs[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "public-${var.azs[count.index]}"
  }
}

resource "aws_subnet" "private" {
  provider          = aws.regional
  count             = length(var.azs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.cidr_block, 8, count.index + 100)
  availability_zone = var.azs[count.index]
  
  tags = {
    Name = "private-${var.azs[count.index]}"
  }
}

# ALB
resource "aws_lb" "main" {
  provider           = aws.regional
  name               = "alb-${var.region}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
  
  tags = {
    Name   = "alb-${var.region}"
    Region = var.region
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "app" {
  provider            = aws.regional
  name                = "asg-${var.region}"
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns   = [aws_lb_target_group.app.arn]
  min_size            = 2
  max_size            = 10
  desired_capacity    = 2
  
  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }
  
  tag {
    key                 = "Name"
    value               = "app-${var.region}"
    propagate_at_launch = true
  }
}

# Aurora Global Database
resource "aws_rds_global_cluster" "main" {
  count                     = var.region == "us-east-1" ? 1 : 0
  global_cluster_identifier = "global-cluster"
  engine                    = "aurora-mysql"
  engine_version            = "5.7.mysql_aurora.2.10.1"
  database_name             = "mydb"
}

resource "aws_rds_cluster" "main" {
  provider                = aws.regional
  cluster_identifier      = "cluster-${var.region}"
  engine                  = "aurora-mysql"
  global_cluster_identifier = var.region == "us-east-1" ? aws_rds_global_cluster.main[0].id : "global-cluster"
  master_username         = var.region == "us-east-1" ? "admin" : null
  master_password         = var.region == "us-east-1" ? random_password.db.result : null
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.db.id]
  skip_final_snapshot     = true
}
```

---

## Cost Analysis

### Multi-Region Cost Breakdown

**Sample Application:**
- 2 regions (us-east-1, eu-west-1)
- 10 EC2 instances per region (t3.medium)
- 2 ALBs
- Aurora Global Database
- S3 with CRR
- CloudFront
- Route53

**Monthly Costs:**
```
EC2 (20 × t3.medium):           20 × $30 = $600
ALB (2 regions):                 2 × $16 = $32
Aurora (2 regions):              2 × $87 = $174
  - db.r5.large × 2 per region
S3 Storage (1 TB × 2):           2 × $23 = $46
S3 CRR (500 GB/month):           500 × $0.02 = $10
CloudFront (1 TB transfer):      $85
Route53 (2 hosted zones):        2 × $0.50 = $1
Data Transfer (cross-region):    200 GB × $0.02 = $4
Global Accelerator:              $18 (per accelerator)
----------------------------------------
Total Monthly Cost:              ~$970

Single Region Equivalent:        ~$550
Multi-Region Premium:            ~$420 (76% increase)
```

**Cost Optimization Strategies:**
1. Use Savings Plans for EC2 (save 40-60%)
2. Aurora Serverless for variable workloads
3. S3 Intelligent-Tiering for storage
4. Reserved Capacity for predictable load
5. Spot Instances for non-critical workloads

**Optimized Costs:**
```
EC2 (Savings Plan 60% off):      $240
ALB:                             $32
Aurora (Reserved 40% off):       $104
S3 (Intelligent-Tiering):        $40
Data Transfer:                   $14
CloudFront:                      $85
Route53:                         $1
----------------------------------------
Optimized Total:                 ~$516 (47% savings)
```

---

## Testing Multi-Region Setup

**Health Check Script:**
```python
import requests
import time
from datetime import datetime

regions = {
    'us-east-1': 'https://us-east-1-alb-123.us-east-1.elb.amazonaws.com',
    'eu-west-1': 'https://eu-west-1-alb-456.eu-west-1.elb.amazonaws.com',
    'cloudfront': 'https://d123abc.cloudfront.net'
}

def check_endpoint(name, url):
    try:
        start = time.time()
        response = requests.get(f'{url}/health', timeout=5)
        latency = (time.time() - start) * 1000
        
        status = '✅' if response.status_code == 200 else '❌'
        print(f"{datetime.now().strftime('%H:%M:%S')} | {name:15} | {status} | {latency:.0f}ms | HTTP {response.status_code}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"{datetime.now().strftime('%H:%M:%S')} | {name:15} | ❌ | Error: {e}")
        return False

def main():
    print("Multi-Region Health Check")
    print("=" * 70)
    
    while True:
        print()
        for name, url in regions.items():
            check_endpoint(name, url)
        
        time.sleep(30)

if __name__ == '__main__':
    main()
```

**Output:**
```
Multi-Region Health Check
======================================================================

14:30:15 | us-east-1       | ✅ | 45ms | HTTP 200
14:30:15 | eu-west-1       | ✅ | 152ms | HTTP 200
14:30:15 | cloudfront      | ✅ | 23ms | HTTP 200

14:30:45 | us-east-1       | ✅ | 43ms | HTTP 200
14:30:45 | eu-west-1       | ✅ | 149ms | HTTP 200
14:30:45 | cloudfront      | ✅ | 21ms | HTTP 200
```

---

## Best Practices

**1. Data Strategy:**
- Use Aurora Global Database for relational data
- DynamoDB Global Tables for NoSQL
- S3 CRR for objects
- Consider data residency requirements

**2. Routing Strategy:**
- Latency-based routing for best performance
- Geolocation routing for compliance
- Failover routing for DR
- Health checks on all endpoints

**3. Failover Planning:**
- Document RTO/RPO requirements
- Automate failover procedures
- Regular DR testing
- Clear runbooks

**4. Cost Management:**
- Monitor cross-region data transfer
- Use CloudFront to reduce data transfer
- Reserved capacity for baseline
- Right-size resources per region

**5. Security:**
- Encrypt data in transit (TLS)
- Encrypt at rest (KMS)
- Consistent security policies across regions
- Centralized logging and monitoring

**6. Testing:**
- Chaos engineering (simulate failures)
- Load testing from multiple regions
- Failover drills
- Performance benchmarking

---

## Summary

Multi-region architecture provides global reach, disaster recovery, and compliance with data residency requirements. Use Aurora Global Database and DynamoDB Global Tables for global data, CloudFront for content delivery, Route53 for intelligent routing, and automate failover procedures. Balance performance, availability, and cost based on your specific requirements.

**Key Takeaways:**
- Active-Active for global applications
- Active-Passive for disaster recovery
- Aurora Global DB for relational data (< 1 second lag)
- DynamoDB Global Tables for multi-master NoSQL
- CloudFront + Global Accelerator for performance
- Lambda@Edge for edge computing
- Route53 for intelligent routing
- Transit Gateway for VPC connectivity
- Automate failover procedures
- Monitor replication lag and health
- Test regularly

**Next Chapter:** [22-disaster-recovery.md](./22-disaster-recovery.md)

Multi-region architecture requires careful planning for data replication, consistency, routing, and cost. Use Aurora Global Database and DynamoDB Global Tables for global data, CloudFront for content delivery, and Route53 for intelligent routing.

**Next Chapter:** [22-disaster-recovery.md](./22-disaster-recovery.md)

