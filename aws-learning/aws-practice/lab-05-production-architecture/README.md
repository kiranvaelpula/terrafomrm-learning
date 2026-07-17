# Lab 05: Production-Ready Multi-Tier Architecture

## Objective

Build a complete production-ready multi-tier web application with high availability, security, monitoring, and disaster recovery.

**Duration:** 2-3 hours

**Skills:**
- Multi-tier architecture design
- High availability patterns
- Security best practices
- Monitoring and alerting
- Backup and disaster recovery
- Cost optimization

---

## Architecture

```
                    Internet
                       |
                  CloudFront (CDN)
                       |
                    Route53 (DNS)
                       |
              +-----------------+
              |   WAF + Shield  |
              +-----------------+
                       |
              Application Load Balancer
              /                    \
    Auto Scaling Group       Auto Scaling Group
         (AZ-1a)                  (AZ-1b)
            |                        |
       EC2 Instances             EC2 Instances
            |                        |
         NAT GW                   NAT GW
            |                        |
       RDS Primary ------>  RDS Standby (Multi-AZ)
            |
       ElastiCache Cluster
            |
         DynamoDB
```

**Components:**
- Multi-AZ VPC with public/private subnets
- Application Load Balancer with WAF
- Auto Scaling Groups across AZs
- RDS Multi-AZ with read replicas
- ElastiCache for session/cache
- CloudFront for content delivery
- S3 for static assets
- CloudWatch for monitoring
- SNS for alerts
- Backup and disaster recovery


---

## Prerequisites

- AWS Account with Admin access
- AWS CLI configured
- Completed previous labs
- Domain name (optional, for Route53)
- Basic understanding of production requirements

---

## Step 1: Create Multi-AZ VPC

```bash
# Create VPC
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=Prod-VPC}]'

VPC_ID=vpc-xxxxx

aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames

# Create Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=Prod-IGW}]'

IGW_ID=igw-xxxxx
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID

# Create Public Subnets (2 AZs)
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Public-1a}]'
PUBLIC_SUBNET_1A=subnet-xxxxx

aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Public-1b}]'
PUBLIC_SUBNET_1B=subnet-yyyyy

# Create Private Subnets for Application (2 AZs)
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.11.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=App-Private-1a}]'
APP_SUBNET_1A=subnet-zzzzz

aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.12.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=App-Private-1b}]'
APP_SUBNET_1B=subnet-aaaaa

# Create Private Subnets for Database (2 AZs)
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.21.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=DB-Private-1a}]'
DB_SUBNET_1A=subnet-bbbbb

aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.22.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=DB-Private-1b}]'
DB_SUBNET_1B=subnet-ccccc

# Create NAT Gateways (one per AZ for HA)
aws ec2 allocate-address --domain vpc
EIP_1A=eipalloc-xxxxx

aws ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET_1A \
  --allocation-id $EIP_1A \
  --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=NAT-1a}]'
NAT_1A=nat-xxxxx

aws ec2 allocate-address --domain vpc
EIP_1B=eipalloc-yyyyy

aws ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET_1B \
  --allocation-id $EIP_1B \
  --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=NAT-1b}]'
NAT_1B=nat-yyyyy

# Wait for NAT Gateways
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_1A $NAT_1B

# Create Route Tables
# Public Route Table
aws ec2 create-route-table --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=Public-RT}]'
PUBLIC_RT=rtb-xxxxx

aws ec2 create-route --route-table-id $PUBLIC_RT \
  --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID

aws ec2 associate-route-table --route-table-id $PUBLIC_RT --subnet-id $PUBLIC_SUBNET_1A
aws ec2 associate-route-table --route-table-id $PUBLIC_RT --subnet-id $PUBLIC_SUBNET_1B

# Private Route Tables (separate per AZ)
aws ec2 create-route-table --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=Private-RT-1a}]'
PRIVATE_RT_1A=rtb-yyyyy

aws ec2 create-route --route-table-id $PRIVATE_RT_1A \
  --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $NAT_1A

aws ec2 associate-route-table --route-table-id $PRIVATE_RT_1A --subnet-id $APP_SUBNET_1A
aws ec2 associate-route-table --route-table-id $PRIVATE_RT_1A --subnet-id $DB_SUBNET_1A

aws ec2 create-route-table --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=Private-RT-1b}]'
PRIVATE_RT_1B=rtb-zzzzz

aws ec2 create-route --route-table-id $PRIVATE_RT_1B \
  --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $NAT_1B

aws ec2 associate-route-table --route-table-id $PRIVATE_RT_1B --subnet-id $APP_SUBNET_1B
aws ec2 associate-route-table --route-table-id $PRIVATE_RT_1B --subnet-id $DB_SUBNET_1B
```


---

## Step 2: Create Security Groups

```bash
# ALB Security Group
aws ec2 create-security-group \
  --group-name ALB-SG \
  --description "Security group for Application Load Balancer" \
  --vpc-id $VPC_ID
ALB_SG=sg-xxxxx

aws ec2 authorize-security-group-ingress --group-id $ALB_SG \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress --group-id $ALB_SG \
  --protocol tcp --port 443 --cidr 0.0.0.0/0

# Application Security Group
aws ec2 create-security-group \
  --group-name App-SG \
  --description "Security group for application servers" \
  --vpc-id $VPC_ID
APP_SG=sg-yyyyy

aws ec2 authorize-security-group-ingress --group-id $APP_SG \
  --protocol tcp --port 80 --source-group $ALB_SG

# Database Security Group
aws ec2 create-security-group \
  --group-name DB-SG \
  --description "Security group for database" \
  --vpc-id $VPC_ID
DB_SG=sg-zzzzz

aws ec2 authorize-security-group-ingress --group-id $DB_SG \
  --protocol tcp --port 3306 --source-group $APP_SG

# ElastiCache Security Group
aws ec2 create-security-group \
  --group-name Cache-SG \
  --description "Security group for ElastiCache" \
  --vpc-id $VPC_ID
CACHE_SG=sg-aaaaa

aws ec2 authorize-security-group-ingress --group-id $CACHE_SG \
  --protocol tcp --port 6379 --source-group $APP_SG
```

---

## Step 3: Create S3 Bucket for Static Assets

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="prod-static-assets-$ACCOUNT_ID"

# Create bucket
aws s3 mb s3://$BUCKET_NAME

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled

# Enable server-side encryption
aws s3api put-bucket-encryption \
  --bucket $BUCKET_NAME \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      },
      "BucketKeyEnabled": true
    }]
  }'

# Enable logging
aws s3api put-bucket-logging \
  --bucket $BUCKET_NAME \
  --bucket-logging-status '{
    "LoggingEnabled": {
      "TargetBucket": "'$BUCKET_NAME'",
      "TargetPrefix": "logs/"
    }
  }'

# Bucket policy for CloudFront
cat > bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AllowCloudFrontAccess",
    "Effect": "Allow",
    "Principal": {
      "Service": "cloudfront.amazonaws.com"
    },
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
  }]
}
EOF

aws s3api put-bucket-policy \
  --bucket $BUCKET_NAME \
  --policy file://bucket-policy.json
```

---

## Step 4: Create RDS Multi-AZ Database

```bash
# Create DB subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name prod-db-subnet-group \
  --db-subnet-group-description "Subnet group for production database" \
  --subnet-ids $DB_SUBNET_1A $DB_SUBNET_1B

# Create RDS instance (Multi-AZ)
aws rds create-db-instance \
  --db-instance-identifier prod-database \
  --db-instance-class db.t3.small \
  --engine mysql \
  --engine-version 8.0.35 \
  --master-username admin \
  --master-user-password YourSecurePassword123! \
  --allocated-storage 100 \
  --storage-type gp3 \
  --storage-encrypted \
  --vpc-security-group-ids $DB_SG \
  --db-subnet-group-name prod-db-subnet-group \
  --multi-az \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00" \
  --preferred-maintenance-window "mon:04:00-mon:05:00" \
  --enable-cloudwatch-logs-exports '["error","general","slowquery"]' \
  --deletion-protection \
  --copy-tags-to-snapshot \
  --tags Key=Name,Value=Production-Database Key=Environment,Value=Production

# Wait for RDS instance
aws rds wait db-instance-available --db-instance-identifier prod-database

# Create read replica for scaling
aws rds create-db-instance-read-replica \
  --db-instance-identifier prod-database-replica \
  --source-db-instance-identifier prod-database \
  --db-instance-class db.t3.small

# Get RDS endpoint
RDS_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier prod-database \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)
```

---

## Step 5: Create ElastiCache Redis Cluster

```bash
# Create cache subnet group
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name prod-cache-subnet-group \
  --cache-subnet-group-description "Subnet group for ElastiCache" \
  --subnet-ids $APP_SUBNET_1A $APP_SUBNET_1B

# Create Redis replication group
aws elasticache create-replication-group \
  --replication-group-id prod-redis \
  --replication-group-description "Production Redis cluster" \
  --engine redis \
  --cache-node-type cache.t3.small \
  --num-cache-clusters 2 \
  --automatic-failover-enabled \
  --multi-az-enabled \
  --cache-subnet-group-name prod-cache-subnet-group \
  --security-group-ids $CACHE_SG \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled \
  --snapshot-retention-limit 5 \
  --snapshot-window "03:00-05:00"

# Wait for cluster
sleep 300

# Get Redis endpoint
REDIS_ENDPOINT=$(aws elasticache describe-replication-groups \
  --replication-group-id prod-redis \
  --query 'ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint.Address' \
  --output text)
```

---

## Step 6: Create Application Load Balancer with WAF

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name prod-alb \
  --subnets $PUBLIC_SUBNET_1A $PUBLIC_SUBNET_1B \
  --security-groups $ALB_SG \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4 \
  --tags Key=Name,Value=Production-ALB

ALB_ARN=$(aws elbv2 describe-load-balancers \
  --names prod-alb \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

# Create target group
aws elbv2 create-target-group \
  --name prod-tg \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --deregistration-delay 30 \
  --target-type instance

TG_ARN=$(aws elbv2 describe-target-groups \
  --names prod-tg \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Create listener (HTTP - redirect to HTTPS)
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=redirect,RedirectConfig='{
    Protocol=HTTPS,Port=443,StatusCode=HTTP_301
  }'

# Create WAF Web ACL
aws wafv2 create-web-acl \
  --name prod-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules '[
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
        "MetricName": "RateLimitRule"
      }
    }
  ]' \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=prod-waf

WAF_ARN=$(aws wafv2 list-web-acls --scope REGIONAL \
  --query "WebACLs[?Name=='prod-waf'].ARN" --output text)

# Associate WAF with ALB
aws wafv2 associate-web-acl \
  --web-acl-arn $WAF_ARN \
  --resource-arn $ALB_ARN
```


---

## Step 7: Create Launch Template and Auto Scaling

```bash
# Create IAM role for EC2 instances
cat > ec2-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ec2.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name ProdEC2Role \
  --assume-role-policy-document file://ec2-trust-policy.json

aws iam attach-role-policy \
  --role-name ProdEC2Role \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy

aws iam attach-role-policy \
  --role-name ProdEC2Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

# Create custom policy for S3 and Secrets
cat > ec2-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    },
    {
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name ProdEC2Role \
  --policy-name CustomAccess \
  --policy-document file://ec2-policy.json

aws iam create-instance-profile --instance-profile-name ProdEC2Profile
aws iam add-role-to-instance-profile \
  --instance-profile-name ProdEC2Profile \
  --role-name ProdEC2Role

# User data script
cat > user-data.sh <<'EOF'
#!/bin/bash
# Update system
yum update -y

# Install dependencies
yum install -y python3 python3-pip mysql-client redis-tools

# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm

# Install application
cd /home/ec2-user
pip3 install flask gunicorn pymysql redis boto3

# Create application
cat > app.py <<'PYTHON'
from flask import Flask, jsonify
import pymysql
import redis
import os

app = Flask(__name__)

# Database connection
db_config = {
    'host': os.environ.get('DB_HOST'),
    'user': 'admin',
    'password': os.environ.get('DB_PASS'),
    'database': 'production'
}

# Redis connection
cache = redis.Redis(
    host=os.environ.get('REDIS_HOST'),
    port=6379,
    ssl=True
)

@app.route('/')
def home():
    return jsonify({
        'message': 'Production Application',
        'status': 'healthy',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/db-check')
def db_check():
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        return jsonify({'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'database': 'error', 'message': str(e)}), 500

@app.route('/cache-check')
def cache_check():
    try:
        cache.ping()
        return jsonify({'cache': 'connected'}), 200
    except Exception as e:
        return jsonify({'cache': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
PYTHON

# Set environment variables
export DB_HOST=$RDS_ENDPOINT
export REDIS_HOST=$REDIS_ENDPOINT
export DB_PASS="YourSecurePassword123!"

# Start application
nohup gunicorn --bind 0.0.0.0:80 --workers 4 app:app > /var/log/app.log 2>&1 &
EOF

# Create Launch Template
aws ec2 create-launch-template \
  --launch-template-name prod-app-template \
  --version-description "Production application v1" \
  --launch-template-data '{
    "ImageId": "ami-0c55b159cbfafe1f0",
    "InstanceType": "t3.small",
    "IamInstanceProfile": {"Name": "ProdEC2Profile"},
    "SecurityGroupIds": ["'$APP_SG'"],
    "UserData": "'$(base64 -w 0 user-data.sh)'",
    "Monitoring": {"Enabled": true},
    "TagSpecifications": [{
      "ResourceType": "instance",
      "Tags": [
        {"Key": "Name", "Value": "ProdApp"},
        {"Key": "Environment", "Value": "Production"}
      ]
    }]
  }'

# Create Auto Scaling Group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name prod-asg \
  --launch-template LaunchTemplateName=prod-app-template,Version='$Latest' \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 4 \
  --health-check-type ELB \
  --health-check-grace-period 300 \
  --vpc-zone-identifier "$APP_SUBNET_1A,$APP_SUBNET_1B" \
  --target-group-arns $TG_ARN \
  --enabled-metrics GroupDesiredCapacity,GroupInServiceInstances,GroupMinSize,GroupMaxSize,GroupTotalInstances

# Create Target Tracking Scaling Policies
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name prod-asg \
  --policy-name cpu-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    },
    "TargetValue": 70.0
  }'

aws autoscaling put-scaling-policy \
  --auto-scaling-group-name prod-asg \
  --policy-name alb-request-count-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ALBRequestCountPerTarget",
      "ResourceLabel": "'$(echo $ALB_ARN | cut -d: -f6)/$(echo $TG_ARN | cut -d: -f6)'"
    },
    "TargetValue": 1000.0
  }'
```

---

## Step 8: Create CloudFront Distribution

```bash
# Create Origin Access Identity
OAI_ID=$(aws cloudfront create-cloud-front-origin-access-identity \
  --cloud-front-origin-access-identity-config \
    CallerReference=$(date +%s),Comment="OAI for production" \
  --query 'CloudFrontOriginAccessIdentity.Id' \
  --output text)

# Get ALB DNS
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --names prod-alb \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

# Create CloudFront distribution
cat > cloudfront-config.json <<EOF
{
  "CallerReference": "$(date +%s)",
  "Comment": "Production CloudFront distribution",
  "Enabled": true,
  "Origins": {
    "Quantity": 2,
    "Items": [
      {
        "Id": "ALB",
        "DomainName": "$ALB_DNS",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "https-only",
          "OriginSslProtocols": {
            "Quantity": 1,
            "Items": ["TLSv1.2"]
          }
        }
      },
      {
        "Id": "S3",
        "DomainName": "$BUCKET_NAME.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": "origin-access-identity/cloudfront/$OAI_ID"
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "ALB",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 7,
      "Items": ["GET","HEAD","OPTIONS","PUT","POST","PATCH","DELETE"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET","HEAD"]
      }
    },
    "ForwardedValues": {
      "QueryString": true,
      "Cookies": {"Forward": "all"}
    },
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000,
    "Compress": true
  },
  "CacheBehaviors": {
    "Quantity": 1,
    "Items": [{
      "PathPattern": "/static/*",
      "TargetOriginId": "S3",
      "ViewerProtocolPolicy": "redirect-to-https",
      "AllowedMethods": {
        "Quantity": 2,
        "Items": ["GET","HEAD"]
      },
      "ForwardedValues": {
        "QueryString": false,
        "Cookies": {"Forward": "none"}
      },
      "MinTTL": 0,
      "DefaultTTL": 86400,
      "MaxTTL": 31536000,
      "Compress": true
    }]
  },
  "PriceClass": "PriceClass_100",
  "ViewerCertificate": {
    "CloudFrontDefaultCertificate": true
  }
}
EOF

aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json

# Get CloudFront domain
CLOUDFRONT_DOMAIN=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[0].DomainName" \
  --output text)
```

---

## Step 9: Configure Monitoring and Alerts

```bash
# Create SNS topic
aws sns create-topic --name production-alerts

SNS_TOPIC_ARN=$(aws sns list-topics \
  --query "Topics[?contains(TopicArn, 'production-alerts')].TopicArn" \
  --output text)

# Subscribe email
aws sns subscribe \
  --topic-arn $SNS_TOPIC_ARN \
  --protocol email \
  --notification-endpoint your-email@example.com

# CloudWatch alarms for ALB
aws cloudwatch put-metric-alarm \
  --alarm-name prod-alb-unhealthy-hosts \
  --alarm-description "Alert when unhealthy hosts detected" \
  --metric-name UnHealthyHostCount \
  --namespace AWS/ApplicationELB \
  --statistic Maximum \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=LoadBalancer,Value=$(echo $ALB_ARN | cut -d: -f6) \
  --alarm-actions $SNS_TOPIC_ARN

aws cloudwatch put-metric-alarm \
  --alarm-name prod-alb-high-response-time \
  --alarm-description "Alert on high response time" \
  --metric-name TargetResponseTime \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=LoadBalancer,Value=$(echo $ALB_ARN | cut -d: -f6) \
  --alarm-actions $SNS_TOPIC_ARN

# CloudWatch alarm for RDS
aws cloudwatch put-metric-alarm \
  --alarm-name prod-rds-cpu-high \
  --alarm-description "Alert on high RDS CPU" \
  --metric-name CPUUtilization \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=DBInstanceIdentifier,Value=prod-database \
  --alarm-actions $SNS_TOPIC_ARN

# Create CloudWatch dashboard
cat > dashboard.json <<EOF
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ApplicationELB", "RequestCount", {"stat": "Sum"}],
          [".", "TargetResponseTime", {"stat": "Average"}],
          [".", "HTTPCode_Target_5XX_Count", {"stat": "Sum"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "ALB Metrics",
        "yAxis": {"left": {"min": 0}}
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/RDS", "CPUUtilization", {"stat": "Average"}],
          [".", "DatabaseConnections", {"stat": "Sum"}],
          [".", "ReadLatency", {"stat": "Average"}],
          [".", "WriteLatency", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "RDS Metrics"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/EC2", "CPUUtilization", {"stat": "Average"}],
          ["AWS/AutoScaling", "GroupDesiredCapacity", {"stat": "Average"}],
          [".", "GroupInServiceInstances", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Auto Scaling Metrics"
      }
    }
  ]
}
EOF

aws cloudwatch put-dashboard \
  --dashboard-name Production-Dashboard \
  --dashboard-body file://dashboard.json
```


---

## Step 10: Configure Backup and Disaster Recovery

```bash
# Enable AWS Backup
aws backup create-backup-plan \
  --backup-plan '{
    "BackupPlanName": "ProductionBackupPlan",
    "Rules": [
      {
        "RuleName": "DailyBackups",
        "TargetBackupVaultName": "Default",
        "ScheduleExpression": "cron(0 5 ? * * *)",
        "StartWindowMinutes": 60,
        "CompletionWindowMinutes": 120,
        "Lifecycle": {
          "DeleteAfterDays": 30,
          "MoveToColdStorageAfterDays": 7
        }
      },
      {
        "RuleName": "WeeklyBackups",
        "TargetBackupVaultName": "Default",
        "ScheduleExpression": "cron(0 5 ? * SUN *)",
        "StartWindowMinutes": 60,
        "CompletionWindowMinutes": 180,
        "Lifecycle": {
          "DeleteAfterDays": 90
        }
      }
    ]
  }'

BACKUP_PLAN_ID=$(aws backup list-backup-plans \
  --query "BackupPlansList[?BackupPlanName=='ProductionBackupPlan'].BackupPlanId" \
  --output text)

# Create backup selection
cat > backup-selection.json <<EOF
{
  "SelectionName": "ProductionResources",
  "IamRoleArn": "arn:aws:iam::$ACCOUNT_ID:role/service-role/AWSBackupDefaultServiceRole",
  "Resources": [
    "arn:aws:rds:us-east-1:$ACCOUNT_ID:db:prod-database",
    "arn:aws:elasticache:us-east-1:$ACCOUNT_ID:cluster:prod-redis"
  ],
  "ListOfTags": [{
    "ConditionType": "STRINGEQUALS",
    "ConditionKey": "Environment",
    "ConditionValue": "Production"
  }]
}
EOF

aws backup create-backup-selection \
  --backup-plan-id $BACKUP_PLAN_ID \
  --backup-selection file://backup-selection.json

# Enable automated RDS snapshots (already enabled with retention)
aws rds modify-db-instance \
  --db-instance-identifier prod-database \
  --backup-retention-period 7 \
  --apply-immediately

# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier prod-database \
  --db-snapshot-identifier prod-database-manual-$(date +%Y%m%d)
```

---

## Step 11: Cost Optimization

```bash
# Create budget
aws budgets create-budget \
  --account-id $ACCOUNT_ID \
  --budget '{
    "BudgetName": "ProductionMonthlyBudget",
    "BudgetLimit": {
      "Amount": "500",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }' \
  --notifications-with-subscribers '[{
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [{
      "SubscriptionType": "EMAIL",
      "Address": "your-email@example.com"
    }]
  }]'

# Enable Cost Explorer
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-12-31 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Tag resources for cost tracking
aws ec2 create-tags \
  --resources $(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=ProdApp" \
    --query 'Reservations[*].Instances[*].InstanceId' \
    --output text) \
  --tags Key=CostCenter,Value=Engineering Key=Project,Value=ProductionApp
```

---

## Verification Checklist

- [ ] Multi-AZ VPC with 6 subnets created
- [ ] NAT Gateways in each AZ for HA
- [ ] Security groups configured with least privilege
- [ ] S3 bucket with versioning and encryption
- [ ] RDS Multi-AZ database running
- [ ] RDS read replica created
- [ ] ElastiCache Redis cluster running
- [ ] Application Load Balancer accessible
- [ ] WAF associated with ALB
- [ ] Auto Scaling Group with 4 instances running
- [ ] CloudFront distribution created
- [ ] CloudWatch alarms configured
- [ ] SNS notifications working
- [ ] Backup plan active
- [ ] Application accessible via CloudFront
- [ ] All health checks passing

---

## Testing the Application

```bash
# Test ALB directly
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --names prod-alb \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

curl http://$ALB_DNS
curl http://$ALB_DNS/health

# Test CloudFront
CLOUDFRONT_DOMAIN=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[0].DomainName" \
  --output text)

curl https://$CLOUDFRONT_DOMAIN
curl https://$CLOUDFRONT_DOMAIN/health

# Load test (requires Apache Bench)
ab -n 10000 -c 100 https://$CLOUDFRONT_DOMAIN/

# Watch Auto Scaling
watch -n 10 'aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names prod-asg \
  --query "AutoScalingGroups[0].[DesiredCapacity,MinSize,MaxSize]" \
  --output table'

# Check RDS connections
aws rds describe-db-instances \
  --db-instance-identifier prod-database \
  --query 'DBInstances[0].DBInstanceStatus'

# Check ElastiCache
aws elasticache describe-replication-groups \
  --replication-group-id prod-redis \
  --query 'ReplicationGroups[0].Status'
```

---

## Disaster Recovery Testing

```bash
# Simulate AZ failure - terminate instances in one AZ
AZ1_INSTANCES=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=ProdApp" \
    "Name=availability-zone,Values=us-east-1a" \
    "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].InstanceId' \
  --output text)

aws ec2 terminate-instances --instance-ids $AZ1_INSTANCES

# Watch Auto Scaling recover
watch -n 5 'aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names prod-asg'

# Test RDS failover
aws rds reboot-db-instance \
  --db-instance-identifier prod-database \
  --force-failover

# Monitor RDS failover
watch -n 5 'aws rds describe-db-instances \
  --db-instance-identifier prod-database \
  --query "DBInstances[0].[DBInstanceStatus,AvailabilityZone]"'

# Test backup restore
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier prod-database-restored \
  --db-snapshot-identifier prod-database-manual-$(date +%Y%m%d)
```

---

## Cleanup

**WARNING:** This will delete all production resources!

```bash
# Delete Auto Scaling Group
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name prod-asg \
  --min-size 0 --max-size 0 --desired-capacity 0
sleep 60
aws autoscaling delete-auto-scaling-group \
  --auto-scaling-group-name prod-asg \
  --force-delete

# Delete Launch Template
aws ec2 delete-launch-template --launch-template-name prod-app-template

# Delete CloudFront (takes time)
DIST_ID=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[0].Id" --output text)
aws cloudfront get-distribution-config --id $DIST_ID > dist-config.json
# Edit config to set Enabled: false, then update and delete

# Delete ALB
aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN
sleep 30
aws elbv2 delete-target-group --target-group-arn $TG_ARN

# Delete WAF
aws wafv2 disassociate-web-acl --resource-arn $ALB_ARN
# Delete WAF web ACL (requires lock token)

# Delete RDS (skip final snapshot for cleanup)
aws rds delete-db-instance \
  --db-instance-identifier prod-database-replica \
  --skip-final-snapshot
aws rds modify-db-instance \
  --db-instance-identifier prod-database \
  --no-deletion-protection \
  --apply-immediately
aws rds delete-db-instance \
  --db-instance-identifier prod-database \
  --skip-final-snapshot

# Delete ElastiCache
aws elasticache delete-replication-group \
  --replication-group-id prod-redis \
  --no-retain-primary-cluster

# Wait for deletions
sleep 300

# Delete subnets groups
aws rds delete-db-subnet-group --db-subnet-group-name prod-db-subnet-group
aws elasticache delete-cache-subnet-group --cache-subnet-group-name prod-cache-subnet-group

# Delete NAT Gateways
aws ec2 delete-nat-gateway --nat-gateway-id $NAT_1A
aws ec2 delete-nat-gateway --nat-gateway-id $NAT_1B
sleep 120

# Release Elastic IPs
aws ec2 release-address --allocation-id $EIP_1A
aws ec2 release-address --allocation-id $EIP_1B

# Delete Internet Gateway
aws ec2 detach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID
aws ec2 delete-internet-gateway --internet-gateway-id $IGW_ID

# Delete Security Groups
aws ec2 delete-security-group --group-id $CACHE_SG
aws ec2 delete-security-group --group-id $DB_SG
aws ec2 delete-security-group --group-id $APP_SG
aws ec2 delete-security-group --group-id $ALB_SG

# Delete Subnets
for SUBNET in $PUBLIC_SUBNET_1A $PUBLIC_SUBNET_1B $APP_SUBNET_1A $APP_SUBNET_1B $DB_SUBNET_1A $DB_SUBNET_1B; do
  aws ec2 delete-subnet --subnet-id $SUBNET
done

# Delete VPC
aws ec2 delete-vpc --vpc-id $VPC_ID

# Empty and delete S3 bucket
aws s3 rm s3://$BUCKET_NAME --recursive
aws s3 rb s3://$BUCKET_NAME

# Delete IAM roles
aws iam remove-role-from-instance-profile \
  --instance-profile-name ProdEC2Profile \
  --role-name ProdEC2Role
aws iam delete-instance-profile --instance-profile-name ProdEC2Profile

for ROLE in ProdEC2Role; do
  aws iam list-attached-role-policies --role-name $ROLE \
    --query 'AttachedPolicies[*].PolicyArn' --output text | \
    xargs -n 1 aws iam detach-role-policy --role-name $ROLE --policy-arn
  aws iam list-role-policies --role-name $ROLE \
    --query 'PolicyNames[*]' --output text | \
    xargs -n 1 aws iam delete-role-policy --role-name $ROLE --policy-name
  aws iam delete-role --role-name $ROLE
done

# Delete SNS topic
aws sns delete-topic --topic-arn $SNS_TOPIC_ARN

# Delete CloudWatch alarms
aws cloudwatch delete-alarms \
  --alarm-names prod-alb-unhealthy-hosts prod-alb-high-response-time prod-rds-cpu-high

# Delete backup plan
aws backup delete-backup-plan --backup-plan-id $BACKUP_PLAN_ID
```

---

## Cost Estimate

**Monthly costs for production workload:**

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| **Compute** |
| EC2 (t3.small × 4) | 730 hours | ~$60 |
| NAT Gateways (2) | Data processing | ~$66 |
| **Database** |
| RDS (db.t3.small Multi-AZ) | Primary + standby | ~$88 |
| RDS Read Replica | db.t3.small | ~$44 |
| ElastiCache (cache.t3.small × 2) | Redis cluster | ~$50 |
| **Network** |
| ALB | Hours + LCUs | ~$25 |
| CloudFront | Data transfer | ~$20 |
| Data Transfer OUT | 100 GB | ~$9 |
| **Storage** |
| EBS (gp3, 100GB × 4) | Instance storage | ~$32 |
| RDS Storage (100GB) | gp3 | ~$11 |
| S3 Standard (50GB) | Static assets | ~$1.15 |
| RDS Backups (100GB) | Automated backups | ~$9.50 |
| **Security & Monitoring** |
| WAF | Web ACL + rules | ~$15 |
| CloudWatch | Logs + metrics | ~$10 |
| AWS Backup | Backup storage | ~$5 |
| **TOTAL** | | **~$445/month** |

**Cost Savings Strategies:**
- Use Reserved Instances (40% savings on EC2/RDS)
- Implement Auto Scaling to match demand
- Use S3 Intelligent-Tiering for static assets
- Enable CloudWatch log retention policies
- Use Fargate Spot for non-critical workloads
- Implement S3 lifecycle policies
- Use Aurora Serverless for variable workloads

**Estimated with Reserved Instances:** ~$320/month (28% savings)

---

## Troubleshooting

**High latency:**
- Check CloudWatch metrics for bottlenecks
- Review RDS slow query logs
- Check ElastiCache hit rate
- Verify ALB target health

**Database connection issues:**
- Verify security group rules
- Check RDS max connections setting
- Review application connection pooling
- Check RDS parameter group settings

**Auto Scaling not working:**
- Review CloudWatch alarms
- Check scaling policies
- Verify target tracking metrics
- Review ASG health check settings

**High costs:**
- Review Cost Explorer reports
- Check for idle resources
- Implement right-sizing recommendations
- Review data transfer costs
- Enable AWS Trusted Advisor

---

## Production Checklist

### Security
- [ ] All data encrypted at rest and in transit
- [ ] WAF rules configured
- [ ] Security groups follow least privilege
- [ ] IAM roles use minimal permissions
- [ ] MFA enabled on root account
- [ ] CloudTrail logging enabled
- [ ] VPC Flow Logs enabled
- [ ] Secrets in AWS Secrets Manager
- [ ] Regular security assessments

### High Availability
- [ ] Multi-AZ deployment
- [ ] Auto Scaling configured
- [ ] Health checks working
- [ ] Load balancing active
- [ ] Database replicas in place
- [ ] Automated failover tested

### Monitoring
- [ ] CloudWatch dashboards created
- [ ] Alarms configured
- [ ] SNS notifications working
- [ ] Log aggregation enabled
- [ ] Application monitoring
- [ ] Custom metrics published

### Backup & DR
- [ ] Automated backups configured
- [ ] Backup retention policies set
- [ ] DR plan documented
- [ ] Failover procedures tested
- [ ] RTO/RPO defined
- [ ] Cross-region replication (if needed)

### Performance
- [ ] CDN (CloudFront) configured
- [ ] Caching strategy implemented
- [ ] Database indexes optimized
- [ ] Application code profiled
- [ ] Load testing completed

### Cost Optimization
- [ ] Reserved Instances purchased
- [ ] Right-sizing implemented
- [ ] Unused resources removed
- [ ] Budget alerts configured
- [ ] Cost allocation tags applied

---

## Learning Outcomes

✅ Designed multi-tier production architecture  
✅ Implemented high availability across AZs  
✅ Configured security layers (WAF, SGs, encryption)  
✅ Set up comprehensive monitoring and alerting  
✅ Implemented backup and disaster recovery  
✅ Optimized for cost and performance  
✅ Practiced production operations  
✅ Understood AWS Well-Architected principles

---

## Next Steps

1. **Implement CI/CD**: Automate deployments with CodePipeline
2. **Add Container Orchestration**: Migrate to ECS or EKS
3. **Multi-Region**: Expand to multiple regions
4. **Advanced Security**: Add GuardDuty, Security Hub
5. **Compliance**: Implement compliance controls (HIPAA, PCI DSS)
6. **Observability**: Add X-Ray tracing, advanced logging
7. **Cost Management**: Implement FinOps practices

**Congratulations!** You've built a production-ready AWS architecture! 🎉
