# Lab 01: Deploy Web Application on EC2 with ALB

## Objective

Deploy a scalable web application using EC2 instances behind an Application Load Balancer with Auto Scaling.

**Duration:** 60-90 minutes

**Skills:**
- EC2 instance management
- Application Load Balancer setup
- Auto Scaling Groups
- Security Groups
- User Data scripts

---

## Architecture

```
Internet
    ↓
Application Load Balancer (Public Subnets)
    ↓
Auto Scaling Group (Private Subnets)
    ↓
EC2 Instances (Web Servers)
```

---

## Prerequisites

- AWS Account with Admin access
- AWS CLI configured
- Key pair created
- Basic understanding of VPC, EC2, ALB

---

## Step 1: Create VPC

```bash
# Create VPC
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=WebApp-VPC}]'

# Note the VPC ID
VPC_ID=vpc-xxxxx

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
  --vpc-id $VPC_ID \
  --enable-dns-hostnames
```

---

## Step 2: Create Subnets

```bash
# Public Subnet 1
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Public-1a}]'

PUBLIC_SUBNET_1=subnet-xxxxx

# Public Subnet 2
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Public-1b}]'

PUBLIC_SUBNET_2=subnet-yyyyy

# Private Subnet 1
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.11.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Private-1a}]'

PRIVATE_SUBNET_1=subnet-zzzzz

# Private Subnet 2
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.12.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Private-1b}]'

PRIVATE_SUBNET_2=subnet-aaaaa
```

---

## Step 3: Configure Internet Access

```bash
# Create Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=WebApp-IGW}]'

IGW_ID=igw-xxxxx

# Attach to VPC
aws ec2 attach-internet-gateway \
  --vpc-id $VPC_ID \
  --internet-gateway-id $IGW_ID

# Create NAT Gateway (for private subnets)
# Allocate Elastic IP
aws ec2 allocate-address --domain vpc

EIP_ALLOC_ID=eipalloc-xxxxx

# Create NAT Gateway in public subnet
aws ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET_1 \
  --allocation-id $EIP_ALLOC_ID \
  --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=WebApp-NAT}]'

NAT_GW_ID=nat-xxxxx
```

---

## Step 4: Configure Route Tables

```bash
# Public Route Table
aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=Public-RT}]'

PUBLIC_RT_ID=rtb-xxxxx

# Add route to Internet Gateway
aws ec2 create-route \
  --route-table-id $PUBLIC_RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID

# Associate with public subnets
aws ec2 associate-route-table \
  --route-table-id $PUBLIC_RT_ID \
  --subnet-id $PUBLIC_SUBNET_1

aws ec2 associate-route-table \
  --route-table-id $PUBLIC_RT_ID \
  --subnet-id $PUBLIC_SUBNET_2

# Private Route Table
aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=Private-RT}]'

PRIVATE_RT_ID=rtb-yyyyy

# Add route to NAT Gateway
aws ec2 create-route \
  --route-table-id $PRIVATE_RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id $NAT_GW_ID

# Associate with private subnets
aws ec2 associate-route-table \
  --route-table-id $PRIVATE_RT_ID \
  --subnet-id $PRIVATE_SUBNET_1

aws ec2 associate-route-table \
  --route-table-id $PRIVATE_RT_ID \
  --subnet-id $PRIVATE_SUBNET_2
```

---

## Step 5: Create Security Groups

```bash
# ALB Security Group
aws ec2 create-security-group \
  --group-name ALB-SG \
  --description "Security group for ALB" \
  --vpc-id $VPC_ID

ALB_SG_ID=sg-xxxxx

# Allow HTTP from internet
aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Allow HTTPS from internet
aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG_ID \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# EC2 Security Group
aws ec2 create-security-group \
  --group-name Web-Server-SG \
  --description "Security group for web servers" \
  --vpc-id $VPC_ID

WEB_SG_ID=sg-yyyyy

# Allow HTTP from ALB only
aws ec2 authorize-security-group-ingress \
  --group-id $WEB_SG_ID \
  --protocol tcp \
  --port 80 \
  --source-group $ALB_SG_ID
```

---

## Step 6: Create Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name web-app-alb \
  --subnets $PUBLIC_SUBNET_1 $PUBLIC_SUBNET_2 \
  --security-groups $ALB_SG_ID \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4

ALB_ARN=arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/web-app-alb/xxxxx

# Create Target Group
aws elbv2 create-target-group \
  --name web-app-tg \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --health-check-path / \
  --health-check-interval-seconds 30 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3

TG_ARN=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/web-app-tg/xxxxx

# Create Listener
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN
```

---

## Step 7: Create Launch Template

**user-data.sh:**
```bash
#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd

# Create simple web page
cat <<EOF > /var/www/html/index.html
<!DOCTYPE html>
<html>
<head>
    <title>Web App Lab</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; }
        h1 { color: #FF9900; }
    </style>
</head>
<body>
    <h1>Welcome to AWS Web App Lab!</h1>
    <p>Instance ID: <strong>$(ec2-metadata --instance-id | cut -d" " -f2)</strong></p>
    <p>Availability Zone: <strong>$(ec2-metadata --availability-zone | cut -d" " -f2)</strong></p>
</body>
</html>
EOF
```

```bash
# Create Launch Template
aws ec2 create-launch-template \
  --launch-template-name web-app-template \
  --version-description "v1" \
  --launch-template-data '{
    "ImageId": "ami-0c55b159cbfafe1f0",
    "InstanceType": "t2.micro",
    "SecurityGroupIds": ["'$WEB_SG_ID'"],
    "UserData": "'$(base64 -w 0 user-data.sh)'",
    "TagSpecifications": [{
      "ResourceType": "instance",
      "Tags": [{"Key": "Name", "Value": "WebServer"}]
    }]
  }'
```

---

## Step 8: Create Auto Scaling Group

```bash
# Create Auto Scaling Group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name web-app-asg \
  --launch-template LaunchTemplateName=web-app-template,Version='$Latest' \
  --min-size 2 \
  --max-size 6 \
  --desired-capacity 2 \
  --health-check-type ELB \
  --health-check-grace-period 300 \
  --vpc-zone-identifier "$PRIVATE_SUBNET_1,$PRIVATE_SUBNET_2" \
  --target-group-arns $TG_ARN

# Create Scaling Policies
# Scale up policy
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name web-app-asg \
  --policy-name scale-up \
  --scaling-adjustment 2 \
  --adjustment-type ChangeInCapacity \
  --cooldown 300

# Scale down policy
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name web-app-asg \
  --policy-name scale-down \
  --scaling-adjustment -1 \
  --adjustment-type ChangeInCapacity \
  --cooldown 300
```

---

## Step 9: Configure Auto Scaling Based on CPU

```bash
# Create CloudWatch alarm for scale up
aws cloudwatch put-metric-alarm \
  --alarm-name cpu-high \
  --alarm-description "Scale up when CPU > 70%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 70 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=AutoScalingGroupName,Value=web-app-asg \
  --alarm-actions $(aws autoscaling describe-policies --auto-scaling-group-name web-app-asg --policy-names scale-up --query 'ScalingPolicies[0].PolicyARN' --output text)

# Create CloudWatch alarm for scale down
aws cloudwatch put-metric-alarm \
  --alarm-name cpu-low \
  --alarm-description "Scale down when CPU < 30%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 30 \
  --comparison-operator LessThanThreshold \
  --dimensions Name=AutoScalingGroupName,Value=web-app-asg \
  --alarm-actions $(aws autoscaling describe-policies --auto-scaling-group-name web-app-asg --policy-names scale-down --query 'ScalingPolicies[0].PolicyARN' --output text)
```

---

## Step 10: Test the Application

```bash
# Get ALB DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --names web-app-alb \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

echo "Application URL: http://$ALB_DNS"

# Test the application
curl http://$ALB_DNS

# Test multiple times to see load balancing
for i in {1..10}; do
  curl http://$ALB_DNS | grep "Instance ID"
  sleep 1
done
```

---

## Verification Checklist

- [ ] VPC created with 4 subnets
- [ ] Internet Gateway and NAT Gateway working
- [ ] Security groups configured correctly
- [ ] ALB accessible from internet
- [ ] 2 EC2 instances running in private subnets
- [ ] Web page displays instance ID
- [ ] Load balancing working (different instance IDs)
- [ ] Auto Scaling triggers on CPU threshold

---

## Cleanup

```bash
# Delete Auto Scaling Group
aws autoscaling delete-auto-scaling-group \
  --auto-scaling-group-name web-app-asg \
  --force-delete

# Delete Launch Template
aws ec2 delete-launch-template \
  --launch-template-name web-app-template

# Delete ALB
aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN
aws elbv2 delete-target-group --target-group-arn $TG_ARN

# Delete NAT Gateway and EIP (wait for deletion)
aws ec2 delete-nat-gateway --nat-gateway-id $NAT_GW_ID
sleep 60
aws ec2 release-address --allocation-id $EIP_ALLOC_ID

# Delete Internet Gateway
aws ec2 detach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID
aws ec2 delete-internet-gateway --internet-gateway-id $IGW_ID

# Delete Security Groups
aws ec2 delete-security-group --group-id $ALB_SG_ID
aws ec2 delete-security-group --group-id $WEB_SG_ID

# Delete Subnets
aws ec2 delete-subnet --subnet-id $PUBLIC_SUBNET_1
aws ec2 delete-subnet --subnet-id $PUBLIC_SUBNET_2
aws ec2 delete-subnet --subnet-id $PRIVATE_SUBNET_1
aws ec2 delete-subnet --subnet-id $PRIVATE_SUBNET_2

# Delete VPC
aws ec2 delete-vpc --vpc-id $VPC_ID
```

---

## Troubleshooting

**Issue: Instances not healthy in target group**
- Check security group allows traffic from ALB
- Verify web server is running: `systemctl status httpd`
- Check health check path returns 200 OK

**Issue: Cannot access ALB**
- Verify ALB security group allows port 80/443
- Check ALB is in public subnets
- Verify route table has IGW route

**Issue: Auto Scaling not working**
- Check CloudWatch alarms are configured
- Verify IAM role has permissions
- Check CPU metrics are being reported

---

## Bonus Challenges

1. **Add HTTPS**: Configure SSL certificate and HTTPS listener
2. **Multiple Environments**: Create dev, staging, prod with different scaling policies
3. **CloudFront**: Add CloudFront for global distribution
4. **Custom Metrics**: Scale based on custom application metrics
5. **Blue-Green**: Implement blue-green deployment strategy

---

## Cost Estimate

- **EC2 (t2.micro)**: $0.0116/hour × 2 = $17/month
- **ALB**: $0.0225/hour + $0.008/LCU = $22/month
- **NAT Gateway**: $0.045/hour = $33/month
- **Data Transfer**: ~$9/GB out
- **Total**: ~$72/month (delete after lab!)

---

## Learning Outcomes

✅ Created scalable VPC architecture
✅ Configured Application Load Balancer
✅ Implemented Auto Scaling
✅ Set up CloudWatch monitoring
✅ Deployed web application on EC2

**Next Lab:** [lab-02-serverless-api](../lab-02-serverless-api/) - Build serverless API with Lambda

