# Lab 03: Container Deployment with ECS

## Objective

Deploy containerized applications using Amazon ECS (Elastic Container Service) with Fargate.

**Duration:** 90 minutes

**Skills:**
- Docker containerization
- ECS clusters and services
- Task definitions
- Application Load Balancer integration
- CloudWatch logging

---

## Architecture

```
Internet → ALB → ECS Service (Fargate) → Container Tasks
                      ↓
                 CloudWatch Logs
```

**Components:**
- VPC with public/private subnets
- Application Load Balancer
- ECS Cluster with Fargate
- ECR (Elastic Container Registry)
- CloudWatch for logging

---

## Prerequisites

- AWS Account with Admin access
- AWS CLI configured
- Docker installed locally
- Basic Docker knowledge
- Completed Lab 01 (VPC basics)

---

## Step 1: Create Sample Application

**app.py:**
```python
from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Hello from ECS Container!',
        'hostname': socket.gethostname(),
        'container_id': os.getenv('HOSTNAME'),
        'version': 'v1.0'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
```

**requirements.txt:**
```
flask==2.3.2
gunicorn==21.2.0
```

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "app:app"]
```

---

## Step 2: Create ECR Repository

```bash
# Create ECR repository
aws ecr create-repository \
  --repository-name ecs-demo-app \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256

# Get repository URI
ECR_URI=$(aws ecr describe-repositories \
  --repository-names ecs-demo-app \
  --query 'repositories[0].repositoryUri' \
  --output text)

echo "ECR URI: $ECR_URI"

# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_URI
```

---

## Step 3: Build and Push Docker Image

```bash
# Build image
docker build -t ecs-demo-app:v1 .

# Tag image for ECR
docker tag ecs-demo-app:v1 $ECR_URI:v1
docker tag ecs-demo-app:v1 $ECR_URI:latest

# Push to ECR
docker push $ECR_URI:v1
docker push $ECR_URI:latest

# Verify image
aws ecr describe-images \
  --repository-name ecs-demo-app
```

---

## Step 4: Create VPC and Networking

```bash
# Create VPC
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=ECS-VPC}]'

VPC_ID=vpc-xxxxx

# Enable DNS
aws ec2 modify-vpc-attribute \
  --vpc-id $VPC_ID \
  --enable-dns-hostnames

# Create public subnets (2 AZs for ALB)
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Public-1a}]'

PUBLIC_SUBNET_1=subnet-xxxxx

aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Public-1b}]'

PUBLIC_SUBNET_2=subnet-yyyyy

# Create Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=ECS-IGW}]'

IGW_ID=igw-xxxxx

aws ec2 attach-internet-gateway \
  --vpc-id $VPC_ID \
  --internet-gateway-id $IGW_ID

# Create route table
aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=Public-RT}]'

RT_ID=rtb-xxxxx

# Add route to IGW
aws ec2 create-route \
  --route-table-id $RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID

# Associate subnets
aws ec2 associate-route-table \
  --route-table-id $RT_ID \
  --subnet-id $PUBLIC_SUBNET_1

aws ec2 associate-route-table \
  --route-table-id $RT_ID \
  --subnet-id $PUBLIC_SUBNET_2

# Auto-assign public IPs
aws ec2 modify-subnet-attribute \
  --subnet-id $PUBLIC_SUBNET_1 \
  --map-public-ip-on-launch

aws ec2 modify-subnet-attribute \
  --subnet-id $PUBLIC_SUBNET_2 \
  --map-public-ip-on-launch
```

---

## Step 5: Create Security Groups

```bash
# ALB Security Group
aws ec2 create-security-group \
  --group-name ALB-SG \
  --description "Security group for ALB" \
  --vpc-id $VPC_ID

ALB_SG=sg-xxxxx

aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# ECS Tasks Security Group
aws ec2 create-security-group \
  --group-name ECS-Tasks-SG \
  --description "Security group for ECS tasks" \
  --vpc-id $VPC_ID

ECS_SG=sg-yyyyy

# Allow traffic from ALB
aws ec2 authorize-security-group-ingress \
  --group-id $ECS_SG \
  --protocol tcp \
  --port 80 \
  --source-group $ALB_SG
```

---

## Step 6: Create Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name ecs-demo-alb \
  --subnets $PUBLIC_SUBNET_1 $PUBLIC_SUBNET_2 \
  --security-groups $ALB_SG \
  --scheme internet-facing \
  --type application

ALB_ARN=$(aws elbv2 describe-load-balancers \
  --names ecs-demo-alb \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

# Create Target Group
aws elbv2 create-target-group \
  --name ecs-demo-tg \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3

TG_ARN=$(aws elbv2 describe-target-groups \
  --names ecs-demo-tg \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Create Listener
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN
```

---

## Step 7: Create IAM Role for ECS Tasks

```bash
# Task execution role (for ECS to pull images and write logs)
cat > task-execution-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document file://task-execution-trust-policy.json

aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

EXECUTION_ROLE_ARN=$(aws iam get-role \
  --role-name ecsTaskExecutionRole \
  --query 'Role.Arn' \
  --output text)

# Task role (for application to access AWS services)
aws iam create-role \
  --role-name ecsTaskRole \
  --assume-role-policy-document file://task-execution-trust-policy.json

TASK_ROLE_ARN=$(aws iam get-role \
  --role-name ecsTaskRole \
  --query 'Role.Arn' \
  --output text)
```

---

## Step 8: Create ECS Cluster

```bash
# Create ECS cluster
aws ecs create-cluster \
  --cluster-name demo-cluster \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=1 \
    capacityProvider=FARGATE_SPOT,weight=2

# Verify cluster
aws ecs describe-clusters --clusters demo-cluster
```

---

## Step 9: Create Task Definition

```bash
# Create task definition JSON
cat > task-definition.json <<EOF
{
  "family": "ecs-demo-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "$EXECUTION_ROLE_ARN",
  "taskRoleArn": "$TASK_ROLE_ARN",
  "containerDefinitions": [
    {
      "name": "demo-app",
      "image": "$ECR_URI:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/demo-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ]
    }
  ]
}
EOF

# Create CloudWatch Log Group
aws logs create-log-group --log-group-name /ecs/demo-app

# Register task definition
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json

# Get task definition ARN
TASK_DEF_ARN=$(aws ecs describe-task-definition \
  --task-definition ecs-demo-task \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text)
```

---

## Step 10: Create ECS Service

```bash
# Create ECS service
aws ecs create-service \
  --cluster demo-cluster \
  --service-name demo-service \
  --task-definition ecs-demo-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[$PUBLIC_SUBNET_1,$PUBLIC_SUBNET_2],
    securityGroups=[$ECS_SG],
    assignPublicIp=ENABLED
  }" \
  --load-balancers "targetGroupArn=$TG_ARN,containerName=demo-app,containerPort=80" \
  --health-check-grace-period-seconds 60

# Wait for service to be stable
aws ecs wait services-stable \
  --cluster demo-cluster \
  --services demo-service
```

---

## Step 11: Test the Application

```bash
# Get ALB DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --names ecs-demo-alb \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

echo "Application URL: http://$ALB_DNS"

# Test the application
curl http://$ALB_DNS

# Test health check
curl http://$ALB_DNS/health

# Test multiple times to see different containers
for i in {1..10}; do
  echo "Request $i:"
  curl -s http://$ALB_DNS | jq '.hostname'
  sleep 1
done
```

---

## Step 12: Configure Auto Scaling

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/demo-cluster/demo-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy (CPU-based)
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/demo-cluster/demo-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'

# Create scaling policy (Request count based)
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/demo-cluster/demo-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name request-count-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 1000.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ALBRequestCountPerTarget",
      "ResourceLabel": "'$(echo $ALB_ARN | cut -d: -f6)/$TG_ARN'"
    }
  }'
```

---

## Step 13: Update Service (Rolling Deployment)

```bash
# Build new version
docker build -t ecs-demo-app:v2 .
docker tag ecs-demo-app:v2 $ECR_URI:v2
docker push $ECR_URI:v2

# Update task definition with new image
sed 's/:latest/:v2/' task-definition.json > task-definition-v2.json

aws ecs register-task-definition \
  --cli-input-json file://task-definition-v2.json

# Update service
aws ecs update-service \
  --cluster demo-cluster \
  --service demo-service \
  --task-definition ecs-demo-task \
  --force-new-deployment

# Watch deployment progress
watch -n 5 'aws ecs describe-services \
  --cluster demo-cluster \
  --services demo-service \
  --query "services[0].deployments" \
  --output table'
```

---

## Step 14: Monitor with CloudWatch

```bash
# View logs
aws logs tail /ecs/demo-app --follow

# Create dashboard
cat > dashboard.json <<EOF
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ECS", "CPUUtilization", {"stat": "Average"}],
          [".", "MemoryUtilization", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "ECS Metrics"
      }
    }
  ]
}
EOF

aws cloudwatch put-dashboard \
  --dashboard-name ECS-Demo \
  --dashboard-body file://dashboard.json
```

---

## Verification Checklist

- [ ] ECR repository created with image
- [ ] VPC with public subnets configured
- [ ] ALB accessible from internet
- [ ] ECS cluster created
- [ ] 2 tasks running successfully
- [ ] Application responds on ALB endpoint
- [ ] Different container IDs on each request
- [ ] CloudWatch logs visible
- [ ] Auto scaling policies configured
- [ ] Rolling deployment working

---

## Cleanup

```bash
# Delete ECS service
aws ecs update-service \
  --cluster demo-cluster \
  --service demo-service \
  --desired-count 0

aws ecs delete-service \
  --cluster demo-cluster \
  --service demo-service \
  --force

# Delete cluster
aws ecs delete-cluster --cluster demo-cluster

# Delete ALB and target group
aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN
sleep 30
aws elbv2 delete-target-group --target-group-arn $TG_ARN

# Delete ECR repository
aws ecr delete-repository \
  --repository-name ecs-demo-app \
  --force

# Delete security groups
aws ec2 delete-security-group --group-id $ECS_SG
aws ec2 delete-security-group --group-id $ALB_SG

# Delete Internet Gateway
aws ec2 detach-internet-gateway \
  --vpc-id $VPC_ID \
  --internet-gateway-id $IGW_ID
aws ec2 delete-internet-gateway --internet-gateway-id $IGW_ID

# Delete subnets
aws ec2 delete-subnet --subnet-id $PUBLIC_SUBNET_1
aws ec2 delete-subnet --subnet-id $PUBLIC_SUBNET_2

# Delete VPC
aws ec2 delete-vpc --vpc-id $VPC_ID

# Delete IAM roles
aws iam detach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
aws iam delete-role --role-name ecsTaskExecutionRole
aws iam delete-role --role-name ecsTaskRole

# Delete CloudWatch logs
aws logs delete-log-group --log-group-name /ecs/demo-app
```

---

## Troubleshooting

**Issue: Tasks failing to start**
- Check CloudWatch logs for error messages
- Verify ECR image exists and is accessible
- Ensure IAM execution role has correct permissions
- Check security group allows traffic

**Issue: Health checks failing**
- Verify `/health` endpoint works locally
- Check security group allows traffic from ALB
- Increase health check grace period
- Review task logs

**Issue: Cannot pull image from ECR**
- Verify Docker login to ECR succeeded
- Check IAM execution role has `ecr:GetAuthorizationToken`
- Ensure image exists in ECR repository

**Commands for debugging:**
```bash
# Describe service events
aws ecs describe-services \
  --cluster demo-cluster \
  --services demo-service

# View task details
aws ecs describe-tasks \
  --cluster demo-cluster \
  --tasks $(aws ecs list-tasks --cluster demo-cluster --query 'taskArns[0]' --output text)

# Check stopped tasks
aws ecs describe-tasks \
  --cluster demo-cluster \
  --tasks $(aws ecs list-tasks --cluster demo-cluster --desired-status STOPPED --query 'taskArns[0]' --output text)
```

---

## Bonus Challenges

1. **Blue-Green Deployment**: Implement blue-green deployment with CodeDeploy
2. **Private Subnets**: Move tasks to private subnets with NAT Gateway
3. **Service Discovery**: Add AWS Cloud Map for service discovery
4. **Secrets Management**: Use Secrets Manager for sensitive data
5. **Multi-Container**: Add sidecar container (nginx proxy)
6. **CI/CD Pipeline**: Automate with CodePipeline
7. **Cost Optimization**: Use Fargate Spot for non-critical tasks

---

## Advanced: Blue-Green Deployment

```bash
# Create additional target group (green)
aws elbv2 create-target-group \
  --name ecs-demo-tg-green \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --target-type ip

TG_GREEN_ARN=...

# Update listener with weighted target groups
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions \
    Type=forward,ForwardConfig='{
      TargetGroups=[
        {TargetGroupArn='$TG_ARN',Weight=90},
        {TargetGroupArn='$TG_GREEN_ARN',Weight=10}
      ]
    }'

# Gradually shift traffic
# 90/10 → 50/50 → 10/90 → 0/100
```

---

## Cost Estimate

**Per Month (2 tasks running 24/7):**
- **Fargate (0.25 vCPU, 0.5 GB)**: ~$15
  - vCPU: $0.04048/hour × 0.25 × 730 hours = $7.40
  - Memory: $0.004445/GB/hour × 0.5 × 730 hours = $1.62
  - Total Fargate: ~$9/task × 2 = $18
- **ALB**: $16.20 + $0.008/LCU = ~$22
- **ECR Storage**: $0.10/GB = ~$1
- **Data Transfer**: $0.09/GB out = varies
- **CloudWatch Logs**: $0.50/GB ingested = ~$5

**Total**: ~$46/month

**Cost Savings:**
- Use Fargate Spot (70% cheaper)
- Delete resources when not in use
- Use CloudWatch log retention policies
- Implement ECR lifecycle policies

---

## Learning Outcomes

✅ Deployed containerized application to ECS  
✅ Configured Fargate serverless containers  
✅ Set up Application Load Balancer  
✅ Implemented auto scaling policies  
✅ Configured CloudWatch logging  
✅ Performed rolling deployments  
✅ Monitored container health

**Next Lab:** [lab-04-cicd-pipeline](../lab-04-cicd-pipeline/) - Build complete CI/CD pipeline
