# Chapter 23: Real-World Production Architecture

## Project Overview

Build a complete, production-ready e-commerce platform on AWS with high availability, scalability, security, and disaster recovery.

**Architecture Components:**
- Multi-tier application (web, app, database)
- Multi-region deployment (us-east-1, eu-west-1)
- CI/CD pipeline
- Monitoring and logging
- Security best practices
- Cost optimization

**Tech Stack:**
- Frontend: React (S3 + CloudFront)
- Backend API: Node.js (ECS Fargate)
- Database: Aurora Global Database
- Cache: ElastiCache Redis
- Search: Elasticsearch
- Message Queue: SQS
- CI/CD: CodePipeline, CodeBuild

---

## Architecture Diagram

```
Users
  |
CloudFront (CDN)
  |
  +-- S3 (Static Frontend)
  |
  +-- Route53 (Latency Routing)
      |
      +----------+----------+
      |                     |
  Region 1              Region 2
  (us-east-1)           (eu-west-1)
      |                     |
   WAF + ALB              WAF + ALB
      |                     |
  ECS Fargate           ECS Fargate
  (API Servers)         (API Servers)
      |                     |
  ElastiCache           ElastiCache
      |                     |
  Aurora Global         Aurora Global
  (Primary)             (Secondary)
      |
  S3 (Images, CRR)
      |
  SQS (Order Processing)
      |
  Lambda (Background Jobs)
```

---

## Phase 1: Networking Foundation

### VPC Setup (Both Regions)

**Create VPCs:**
```bash
# US East Region
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=prod-vpc-us}]' \
  --region us-east-1

# EU West Region
aws ec2 create-vpc \
  --cidr-block 10.1.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=prod-vpc-eu}]' \
  --region eu-west-1
```

**Create Subnets:**
```bash
# Public subnets (ALB)
aws ec2 create-subnet --vpc-id vpc-us --cidr-block 10.0.1.0/24 --availability-zone us-east-1a
aws ec2 create-subnet --vpc-id vpc-us --cidr-block 10.0.2.0/24 --availability-zone us-east-1b

# Private subnets (ECS)
aws ec2 create-subnet --vpc-id vpc-us --cidr-block 10.0.11.0/24 --availability-zone us-east-1a
aws ec2 create-subnet --vpc-id vpc-us --cidr-block 10.0.12.0/24 --availability-zone us-east-1b

# Database subnets
aws ec2 create-subnet --vpc-id vpc-us --cidr-block 10.0.21.0/24 --availability-zone us-east-1a
aws ec2 create-subnet --vpc-id vpc-us --cidr-block 10.0.22.0/24 --availability-zone us-east-1b
```

---

## Phase 2: Database Layer

### Aurora Global Database

```bash
# Create primary cluster (us-east-1)
aws rds create-db-cluster \
  --db-cluster-identifier ecommerce-primary \
  --engine aurora-mysql \
  --engine-version 8.0.mysql_aurora.3.02.0 \
  --master-username admin \
  --master-user-password $(aws secretsmanager get-random-password --output text) \
  --database-name ecommerce \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00" \
  --db-subnet-group-name db-subnet-group \
  --vpc-security-group-ids sg-database \
  --region us-east-1

# Create global cluster
aws rds create-global-cluster \
  --global-cluster-identifier ecommerce-global \
  --source-db-cluster-identifier arn:aws:rds:us-east-1:123456789012:cluster:ecommerce-primary

# Add secondary region
aws rds create-db-cluster \
  --db-cluster-identifier ecommerce-secondary \
  --engine aurora-mysql \
  --global-cluster-identifier ecommerce-global \
  --db-subnet-group-name db-subnet-group-eu \
  --vpc-security-group-ids sg-database-eu \
  --region eu-west-1
```

### ElastiCache Redis

```bash
# Create Redis cluster
aws elasticache create-replication-group \
  --replication-group-id ecommerce-cache \
  --replication-group-description "E-commerce cache" \
  --engine redis \
  --cache-node-type cache.r6g.large \
  --num-cache-clusters 2 \
  --automatic-failover-enabled \
  --multi-az-enabled \
  --cache-subnet-group-name cache-subnet-group \
  --security-group-ids sg-cache \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled
```

---

## Phase 3: Application Layer

### ECS Cluster Setup

**Create Cluster:**
```bash
aws ecs create-cluster \
  --cluster-name ecommerce-cluster \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=2 \
    capacityProvider=FARGATE_SPOT,weight=3
```

**Task Definition:**
```json
{
  "family": "api-service",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [{
    "name": "api",
    "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/ecommerce-api:latest",
    "portMappings": [{
      "containerPort": 3000,
      "protocol": "tcp"
    }],
    "environment": [
      {"name": "NODE_ENV", "value": "production"},
      {"name": "REDIS_HOST", "value": "ecommerce-cache.xxx.cache.amazonaws.com"}
    ],
    "secrets": [{
      "name": "DB_PASSWORD",
      "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:db-password"
    }],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/api-service",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "api"
      }
    },
    "healthCheck": {
      "command": ["CMD-SHELL", "curl -f http://localhost:3000/health || exit 1"],
      "interval": 30,
      "timeout": 5,
      "retries": 3
    }
  }]
}
```

**Create Service:**
```bash
aws ecs create-service \
  --cluster ecommerce-cluster \
  --service-name api-service \
  --task-definition api-service:1 \
  --desired-count 4 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-private-1,subnet-private-2],
    securityGroups=[sg-ecs],
    assignPublicIp=DISABLED
  }" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,
    containerName=api,
    containerPort=3000" \
  --health-check-grace-period-seconds 60
```

### Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name ecommerce-alb \
  --subnets subnet-public-1 subnet-public-2 \
  --security-groups sg-alb \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4

# Create target group
aws elbv2 create-target-group \
  --name api-targets \
  --protocol HTTP \
  --port 3000 \
  --vpc-id vpc-12345678 \
  --target-type ip \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:... \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

---

## Phase 4: Frontend

### S3 + CloudFront

**Create S3 Bucket:**
```bash
aws s3 mb s3://ecommerce-frontend-prod
aws s3 website s3://ecommerce-frontend-prod \
  --index-document index.html \
  --error-document error.html
```

**CloudFront Distribution:**
```json
{
  "Origins": {
    "Quantity": 2,
    "Items": [
      {
        "Id": "S3-Origin",
        "DomainName": "ecommerce-frontend-prod.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": "origin-access-identity/cloudfront/ABCDEF"
        }
      },
      {
        "Id": "API-Origin",
        "DomainName": "api.example.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "https-only"
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-Origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
    "Compress": true,
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000
  },
  "CacheBehaviors": {
    "Quantity": 1,
    "Items": [{
      "PathPattern": "/api/*",
      "TargetOriginId": "API-Origin",
      "ViewerProtocolPolicy": "https-only",
      "AllowedMethods": {
        "Quantity": 7,
        "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
      },
      "MinTTL": 0,
      "DefaultTTL": 0,
      "MaxTTL": 0
    }]
  }
}
```

---

## Phase 5: Background Processing

### SQS + Lambda

**Create Queue:**
```bash
aws sqs create-queue \
  --queue-name order-processing \
  --attributes '{
    "VisibilityTimeout": "300",
    "MessageRetentionPeriod": "1209600",
    "ReceiveMessageWaitTimeSeconds": "20"
  }'

# Create DLQ
aws sqs create-queue --queue-name order-processing-dlq

# Set redrive policy
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/order-processing \
  --attributes '{
    "RedrivePolicy": "{\"deadLetterTargetArn\":\"arn:aws:sqs:us-east-1:123456789012:order-processing-dlq\",\"maxReceiveCount\":\"3\"}"
  }'
```

**Lambda Processor:**
```javascript
// order-processor/index.js
const AWS = require('aws-sdk');
const mysql = require('mysql2/promise');

exports.handler = async (event) => {
  const connection = await mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: 'ecommerce'
  });
  
  for (const record of event.Records) {
    const order = JSON.parse(record.body);
    
    try {
      // Process order
      await connection.execute(
        'INSERT INTO orders (user_id, total, status) VALUES (?, ?, ?)',
        [order.userId, order.total, 'processing']
      );
      
      // Send notification
      const sns = new AWS.SNS();
      await sns.publish({
        TopicArn: process.env.SNS_TOPIC_ARN,
        Message: `Order ${order.id} received`
      }).promise();
      
    } catch (error) {
      console.error('Error processing order:', error);
      throw error; // Message will go to DLQ
    }
  }
  
  await connection.end();
};
```

---

## Phase 6: CI/CD Pipeline

### CodePipeline

**pipeline.yaml:**
```yaml
version: 0.2
phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
  
  build:
    commands:
      - echo Build started on `date`
      - docker build -t $IMAGE_REPO_NAME:$IMAGE_TAG .
      - docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
  
  post_build:
    commands:
      - echo Build completed on `date`
      - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
      - printf '[{"name":"api","imageUri":"%s"}]' $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG > imagedefinitions.json
artifacts:
  files: imagedefinitions.json
```

---

## Phase 7: Monitoring

### CloudWatch Dashboards

**Create Dashboard:**
```python
import boto3
import json

cloudwatch = boto3.client('cloudwatch')

dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/ApplicationELB", "TargetResponseTime", {"stat": "Average"}],
                    [".", "RequestCount", {"stat": "Sum"}],
                    [".", "HTTPCode_Target_5XX_Count", {"stat": "Sum"}]
                ],
                "period": 300,
                "stat": "Average",
                "region": "us-east-1",
                "title": "ALB Metrics"
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/RDS", "CPUUtilization", {"stat": "Average"}],
                    [".", "DatabaseConnections", {"stat": "Average"}]
                ],
                "period": 300,
                "region": "us-east-1",
                "title": "Database Metrics"
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='EcommerceProduction',
    DashboardBody=json.dumps(dashboard_body)
)
```

### Alarms

```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name high-error-rate \
  --alarm-description "Alert when error rate > 5%" \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 100 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts
```

---

## Phase 8: Security

### WAF Rules

```bash
# Create Web ACL
aws wafv2 create-web-acl \
  --name ecommerce-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules file://waf-rules.json

# Associate with ALB
aws wafv2 associate-web-acl \
  --web-acl-arn arn:aws:wafv2:... \
  --resource-arn arn:aws:elasticloadbalancing:...
```

### Enable Security Services

```bash
# Enable GuardDuty
aws guardduty create-detector --enable

# Enable Security Hub
aws securityhub enable-security-hub

# Enable Config
aws configservice put-configuration-recorder \
  --configuration-recorder name=default,roleARN=arn:aws:iam::123456789012:role/ConfigRole
```

---

## Cost Analysis

**Monthly Estimated Costs:**
```
CloudFront: $500
ALB: $400
ECS Fargate: $2,000 (8 tasks @ $0.04/hr)
Aurora Global: $1,800
ElastiCache: $600
S3: $200
Data Transfer: $800
Other Services: $700
---
Total: ~$7,000/month
```

**Optimization Opportunities:**
- Use Savings Plans: Save 30-40%
- Fargate Spot: Save 70% for non-critical tasks
- S3 Intelligent-Tiering: Save 20-30%
- Reserved Cache Nodes: Save 30-40%

---

## Summary

This production architecture provides high availability, scalability, security, and disaster recovery. It uses multi-region deployment, managed services, and AWS best practices for a production-ready e-commerce platform.

**Next:** [interview-questions-advanced.md](./interview-questions-advanced.md)

