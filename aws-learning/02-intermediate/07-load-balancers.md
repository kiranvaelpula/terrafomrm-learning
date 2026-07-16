# Elastic Load Balancing

## Introduction

Elastic Load Balancing (ELB) automatically distributes incoming traffic across multiple targets (EC2 instances, containers, IP addresses, Lambda functions). Load balancers improve application availability, fault tolerance, and scalability. This chapter covers all three types of load balancers and their use cases.

## Table of Contents
- [Load Balancer Types](#load-balancer-types)
- [Application Load Balancer (ALB)](#application-load-balancer-alb)
- [Network Load Balancer (NLB)](#network-load-balancer-nlb)
- [Gateway Load Balancer (GWLB)](#gateway-load-balancer-gwlb)
- [Target Groups](#target-groups)
- [Health Checks](#health-checks)
- [SSL/TLS Termination](#ssltls-termination)
- [Advanced Features](#advanced-features)
- [Hands-on Exercises](#hands-on-exercises)

---

## Load Balancer Types

### Comparison Overview

```yaml
Application Load Balancer (ALB) - Layer 7:
  Protocol: HTTP, HTTPS, gRPC
  Use Case: Web applications, microservices
  Features: Content routing, host/path-based routing
  Target: EC2, IP, Lambda, containers
  Cost: $0.0225/hour + $0.008/LCU
  
Network Load Balancer (NLB) - Layer 4:
  Protocol: TCP, UDP, TLS
  Use Case: Extreme performance, static IP
  Features: Ultra-low latency, millions req/sec
  Target: EC2, IP, ALB
  Cost: $0.0225/hour + $0.006/NLCU
  
Gateway Load Balancer (GWLB) - Layer 3:
  Protocol: IP packets
  Use Case: Third-party virtual appliances
  Features: Traffic inspection, firewalls
  Target: Virtual appliances
  Cost: $0.0125/hour + $0.004/GLCU

Classic Load Balancer (CLB) - Legacy:
  Status: Previous generation
  Recommendation: Migrate to ALB/NLB
```

### Choosing the Right Load Balancer

```yaml
Use ALB When:
  - HTTP/HTTPS traffic
  - Microservices architecture
  - Container-based applications
  - Lambda functions as targets
  - Need path-based routing
  - WebSocket or HTTP/2 support
  
Use NLB When:
  - TCP/UDP traffic
  - Ultra-high performance needed
  - Static IP addresses required
  - PrivateLink support needed
  - Millions of requests per second
  - Lowest latency required
  
Use GWLB When:
  - Deploy virtual appliances
  - Third-party security tools
  - Traffic inspection needed
  - Transparent network gateway
```

---

## Application Load Balancer (ALB)

### ALB Architecture

```
Internet
    ↓
Application Load Balancer (ALB)
    ├── Listener: Port 80 (HTTP)
    │   └── Rules:
    │       ├── Path /api/* → API Target Group
    │       └── Path /web/* → Web Target Group
    │
    └── Listener: Port 443 (HTTPS)
        └── Rules:
            ├── Host api.example.com → API TG
            └── Host www.example.com → Web TG

Target Groups:
├── API Target Group
│   ├── EC2 Instance 1 (us-east-1a)
│   ├── EC2 Instance 2 (us-east-1b)
│   └── Health Check: GET /health
│
└── Web Target Group
    ├── EC2 Instance 3 (us-east-1a)
    ├── EC2 Instance 4 (us-east-1b)
    └── Health Check: GET /index.html
```

### Create Application Load Balancer

```bash
# Create security group for ALB
ALB_SG=$(aws ec2 create-security-group \
  --group-name alb-security-group \
  --description "Security group for ALB" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)

# Allow HTTP from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Allow HTTPS from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Create ALB
ALB_ARN=$(aws elbv2 create-load-balancer \
  --name my-application-lb \
  --subnets $PUBLIC_SUBNET_1 $PUBLIC_SUBNET_2 \
  --security-groups $ALB_SG \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4 \
  --tags Key=Name,Value=my-alb \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

# Get DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --load-balancer-arns $ALB_ARN \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

echo "ALB DNS: $ALB_DNS"
```


### ALB Target Groups and Listeners

```bash
# Create target group for EC2 instances
TG_ARN=$(aws elbv2 create-target-group \
  --name web-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --health-check-protocol HTTP \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --matcher HttpCode=200 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Register targets
aws elbv2 register-targets \
  --target-group-arn $TG_ARN \
  --targets Id=$INSTANCE_1 Id=$INSTANCE_2

# Create HTTP listener
HTTP_LISTENER=$(aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN \
  --query 'Listeners[0].ListenerArn' \
  --output text)

# Create HTTPS listener (requires certificate)
HTTPS_LISTENER=$(aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=$CERT_ARN \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN \
  --query 'Listeners[0].ListenerArn' \
  --output text)
```

### Path-Based Routing

```bash
# Create target groups for different paths
API_TG=$(aws elbv2 create-target-group \
  --name api-targets \
  --protocol HTTP \
  --port 8080 \
  --vpc-id $VPC_ID \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

IMAGES_TG=$(aws elbv2 create-target-group \
  --name images-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Create path-based rules
aws elbv2 create-rule \
  --listener-arn $HTTP_LISTENER \
  --priority 10 \
  --conditions Field=path-pattern,Values='/api/*' \
  --actions Type=forward,TargetGroupArn=$API_TG

aws elbv2 create-rule \
  --listener-arn $HTTP_LISTENER \
  --priority 20 \
  --conditions Field=path-pattern,Values='/images/*' \
  --actions Type=forward,TargetGroupArn=$IMAGES_TG
```

### Host-Based Routing

```bash
# Route based on host header
aws elbv2 create-rule \
  --listener-arn $HTTP_LISTENER \
  --priority 5 \
  --conditions Field=host-header,Values='api.example.com' \
  --actions Type=forward,TargetGroupArn=$API_TG

aws elbv2 create-rule \
  --listener-arn $HTTP_LISTENER \
  --priority 6 \
  --conditions Field=host-header,Values='www.example.com','example.com' \
  --actions Type=forward,TargetGroupArn=$WEB_TG
```

### ALB Advanced Features

```yaml
Sticky Sessions (Session Affinity):
  - Route requests from same client to same target
  - Cookie-based (application or load balancer)
  - Duration: 1 second to 7 days
  
Connection Draining (Deregistration Delay):
  - Complete in-flight requests before deregistering
  - Default: 300 seconds
  - Range: 0-3600 seconds
  
Cross-Zone Load Balancing:
  - Distribute traffic evenly across all AZs
  - Enabled by default for ALB
  - No additional charge
  
Access Logs:
  - Capture detailed request information
  - Store in S3
  - Contains: timestamp, client IP, latencies, paths
```

```bash
# Enable sticky sessions
aws elbv2 modify-target-group-attributes \
  --target-group-arn $TG_ARN \
  --attributes \
    Key=stickiness.enabled,Value=true \
    Key=stickiness.type,Value=lb_cookie \
    Key=stickiness.lb_cookie.duration_seconds,Value=86400

# Set deregistration delay
aws elbv2 modify-target-group-attributes \
  --target-group-arn $TG_ARN \
  --attributes Key=deregistration_delay.timeout_seconds,Value=30

# Enable access logs
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn $ALB_ARN \
  --attributes \
    Key=access_logs.s3.enabled,Value=true \
    Key=access_logs.s3.bucket,Value=my-alb-logs \
    Key=access_logs.s3.prefix,Value=alb-logs
```

---

## Network Load Balancer (NLB)

### NLB Characteristics

```yaml
Performance:
  - Millions of requests per second
  - Ultra-low latency (~100 microseconds)
  - Handles sudden traffic spikes
  - Preserves source IP
  
Static IP:
  - One static IP per AZ
  - Can assign Elastic IP
  - Use with firewall rules
  
Protocols:
  - TCP (Layer 4)
  - UDP
  - TLS termination
  
Target Types:
  - EC2 instances
  - IP addresses (on-premises)
  - Application Load Balancer
```

### Create Network Load Balancer

```bash
# Allocate Elastic IPs for NLB
EIP_1=$(aws ec2 allocate-address \
  --domain vpc \
  --query 'AllocationId' \
  --output text)

EIP_2=$(aws ec2 allocate-address \
  --domain vpc \
  --query 'AllocationId' \
  --output text)

# Create NLB with Elastic IPs
NLB_ARN=$(aws elbv2 create-load-balancer \
  --name my-network-lb \
  --type network \
  --scheme internet-facing \
  --subnet-mappings \
    SubnetId=$PUBLIC_SUBNET_1,AllocationId=$EIP_1 \
    SubnetId=$PUBLIC_SUBNET_2,AllocationId=$EIP_2 \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

# Create target group for TCP traffic
NLB_TG=$(aws elbv2 create-target-group \
  --name tcp-targets \
  --protocol TCP \
  --port 80 \
  --vpc-id $VPC_ID \
  --target-type instance \
  --health-check-protocol TCP \
  --health-check-interval-seconds 10 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 2 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Register targets
aws elbv2 register-targets \
  --target-group-arn $NLB_TG \
  --targets Id=$INSTANCE_1 Id=$INSTANCE_2

# Create TCP listener
aws elbv2 create-listener \
  --load-balancer-arn $NLB_ARN \
  --protocol TCP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$NLB_TG
```

### NLB with TLS Termination

```bash
# Create TLS listener
aws elbv2 create-listener \
  --load-balancer-arn $NLB_ARN \
  --protocol TLS \
  --port 443 \
  --certificates CertificateArn=$CERT_ARN \
  --default-actions Type=forward,TargetGroupArn=$NLB_TG \
  --alpn-policy HTTP2Preferred
```

### NLB for On-Premises Targets

```bash
# Create target group with IP targets
IP_TG=$(aws elbv2 create-target-group \
  --name onprem-targets \
  --protocol TCP \
  --port 443 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Register on-premises IPs (via VPN/Direct Connect)
aws elbv2 register-targets \
  --target-group-arn $IP_TG \
  --targets \
    Id=10.1.2.10,Port=443 \
    Id=10.1.2.11,Port=443
```

---

## Gateway Load Balancer (GWLB)

### GWLB Use Cases

```yaml
Purpose:
  - Deploy third-party virtual appliances
  - Transparent network gateway
  - Inline traffic inspection
  
Use Cases:
  - Firewalls
  - Intrusion detection/prevention (IDS/IPS)
  - Deep packet inspection
  - Payload manipulation
  
Architecture:
  Traffic → GWLB → Virtual Appliances → GWLB → Destination
```


---

## Target Groups

### Target Group Types

```yaml
Instance Target Type:
  - EC2 instances by instance ID
  - Auto Scaling Group integration
  - Health checks via instance

IP Target Type:
  - Any IP address in VPC CIDR
  - On-premises servers (via VPN/DX)
  - Other VPCs (via peering)
  - More flexible than instance type

Lambda Target Type (ALB only):
  - Invoke Lambda functions
  - HTTP request converted to JSON event
  - Response formatted as HTTP
  - Serverless backend
```

### Target Group Attributes

```bash
# View all attributes
aws elbv2 describe-target-group-attributes \
  --target-group-arn $TG_ARN

# Modify attributes
aws elbv2 modify-target-group-attributes \
  --target-group-arn $TG_ARN \
  --attributes \
    Key=deregistration_delay.timeout_seconds,Value=30 \
    Key=stickiness.enabled,Value=true \
    Key=stickiness.type,Value=lb_cookie \
    Key=load_balancing.algorithm.type,Value=least_outstanding_requests \
    Key=slow_start.duration_seconds,Value=30

# ALB-specific attributes
aws elbv2 modify-target-group-attributes \
  --target-group-arn $TG_ARN \
  --attributes \
    Key=lambda.multi_value_headers.enabled,Value=true \
    Key=load_balancing.algorithm.type,Value=round_robin
```

### Load Balancing Algorithms

```yaml
ALB Algorithms:
  Round Robin (default):
    - Distributes equally across targets
    - Simple and effective
    
  Least Outstanding Requests:
    - Routes to target with fewest requests
    - Better for long-running requests
    
NLB Algorithms:
  Flow Hash (default):
    - Based on: protocol, source/dest IP, port, TCP seq
    - Same client → same target
    - Connection-level stickiness
```

---

## Health Checks

### Health Check Configuration

```yaml
Health Check Parameters:
  Protocol: HTTP, HTTPS, TCP, gRPC
  Port: Traffic port or override
  Path: /health, /status (HTTP/HTTPS only)
  Interval: 5-300 seconds (default 30)
  Timeout: 2-120 seconds (default 5)
  Healthy Threshold: 2-10 (default 2)
  Unhealthy Threshold: 2-10 (default 2)
  Success Codes: 200, 200-299, 200,202

Health States:
  - Initial: Registering target
  - Healthy: Passing health checks
  - Unhealthy: Failing health checks
  - Draining: Deregistration in progress
  - Unused: No traffic
```

```bash
# Create target group with custom health check
TG_ARN=$(aws elbv2 create-target-group \
  --name custom-health-tg \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --health-check-enabled \
  --health-check-protocol HTTP \
  --health-check-port 8080 \
  --health-check-path /api/health \
  --health-check-interval-seconds 15 \
  --health-check-timeout-seconds 10 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --matcher HttpCode=200,202 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Check target health
aws elbv2 describe-target-health \
  --target-group-arn $TG_ARN

# Example output:
# {
#   "TargetHealthDescriptions": [
#     {
#       "Target": {"Id": "i-1234567890", "Port": 80},
#       "HealthCheckPort": "8080",
#       "TargetHealth": {
#         "State": "healthy"
#       }
#     }
#   ]
# }
```

### Application Health Check Endpoint

```python
# Flask health check endpoint example
from flask import Flask, jsonify
import psutil

app = Flask(__name__)

@app.route('/health')
def health_check():
    # Check application components
    checks = {
        'database': check_database(),
        'cache': check_cache(),
        'disk_space': psutil.disk_usage('/').percent < 90,
        'memory': psutil.virtual_memory().percent < 85
    }
    
    # Return 200 if all checks pass
    if all(checks.values()):
        return jsonify({
            'status': 'healthy',
            'checks': checks
        }), 200
    else:
        return jsonify({
            'status': 'unhealthy',
            'checks': checks
        }), 503

def check_database():
    try:
        # Database connection check
        conn = get_db_connection()
        conn.execute('SELECT 1')
        return True
    except:
        return False

def check_cache():
    try:
        # Redis/Memcached check
        cache = get_cache()
        cache.set('health_check', 'ok')
        return cache.get('health_check') == 'ok'
    except:
        return False
```

---

## SSL/TLS Termination

### Certificate Management

```yaml
Certificate Sources:
  - AWS Certificate Manager (ACM) - Free
  - Import third-party certificate
  - Self-signed (testing only)

SSL/TLS Termination:
  - Load balancer decrypts SSL/TLS
  - Backend communication can be HTTP or HTTPS
  - Offloads encryption from instances
  - Centralized certificate management
```

```bash
# Request ACM certificate
CERT_ARN=$(aws acm request-certificate \
  --domain-name example.com \
  --subject-alternative-names '*.example.com' \
  --validation-method DNS \
  --query 'CertificateArn' \
  --output text)

# Get DNS validation records
aws acm describe-certificate \
  --certificate-arn $CERT_ARN \
  --query 'Certificate.DomainValidationOptions'

# Add CNAME records to Route53 for validation
# Certificate will be issued once DNS validation completes

# Create HTTPS listener with certificate
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=$CERT_ARN \
  --ssl-policy ELBSecurityPolicy-TLS-1-2-2017-01 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN

# HTTP to HTTPS redirect
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=redirect,RedirectConfig='{
    "Protocol":"HTTPS",
    "Port":"443",
    "StatusCode":"HTTP_301"
  }'
```

### SSL/TLS Policies

```yaml
Recommended Policies:
  ELBSecurityPolicy-TLS-1-2-2017-01:
    - TLS 1.2 only
    - Strong cipher suites
    - Recommended for most use cases
  
  ELBSecurityPolicy-TLS-1-3-2021-06:
    - TLS 1.3 and 1.2
    - Latest security standards
    - Use for maximum security
  
  ELBSecurityPolicy-FS-1-2-2019-08:
    - Forward secrecy support
    - Strong ciphers only
```

---

## Advanced Features

### Fixed Response Actions

```bash
# Return custom HTTP response
aws elbv2 create-rule \
  --listener-arn $HTTP_LISTENER \
  --priority 100 \
  --conditions Field=path-pattern,Values='/maintenance' \
  --actions Type=fixed-response,FixedResponseConfig='{
    "StatusCode":"503",
    "ContentType":"text/plain",
    "MessageBody":"Service under maintenance"
  }'
```

### Weighted Target Groups

```bash
# Blue/Green deployment with traffic splitting
aws elbv2 create-rule \
  --listener-arn $HTTP_LISTENER \
  --priority 10 \
  --conditions Field=path-pattern,Values='/*' \
  --actions Type=forward,ForwardConfig='{
    "TargetGroups":[
      {"TargetGroupArn":"'$BLUE_TG'","Weight":90},
      {"TargetGroupArn":"'$GREEN_TG'","Weight":10}
    ],
    "TargetGroupStickinessConfig":{"Enabled":true}
  }'
```

### Authentication Actions

```bash
# Cognito authentication
aws elbv2 create-rule \
  --listener-arn $HTTPS_LISTENER \
  --priority 5 \
  --conditions Field=path-pattern,Values='/app/*' \
  --actions \
    Type=authenticate-cognito,AuthenticateCognitoConfig='{
      "UserPoolArn":"arn:aws:cognito-idp:region:account:userpool/id",
      "UserPoolClientId":"client-id",
      "UserPoolDomain":"domain"
    }' \
    Type=forward,TargetGroupArn=$TG_ARN
```

### Connection Idle Timeout

```bash
# Modify idle timeout (default: 60 seconds)
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn $ALB_ARN \
  --attributes \
    Key=idle_timeout.timeout_seconds,Value=120
```

---

## Hands-on Exercises

### Exercise 1: Complete ALB Setup

**Objective:** Deploy multi-tier application with ALB

```bash
#!/bin/bash
# Complete ALB deployment script

# Variables
VPC_ID="vpc-xxx"
SUBNET_1="subnet-xxx"
SUBNET_2="subnet-yyy"

# Create security groups
ALB_SG=$(aws ec2 create-security-group \
  --group-name alb-sg \
  --description "ALB security group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' --output text)

INSTANCE_SG=$(aws ec2 create-security-group \
  --group-name instance-sg \
  --description "Instance security group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' --output text)

# ALB: Allow HTTP/HTTPS from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG \
  --ip-permissions \
    IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges='[{CidrIp=0.0.0.0/0}]' \
    IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges='[{CidrIp=0.0.0.0/0}]'

# Instances: Allow traffic only from ALB
aws ec2 authorize-security-group-ingress \
  --group-id $INSTANCE_SG \
  --protocol tcp \
  --port 80 \
  --source-group $ALB_SG

# Launch instances
USER_DATA='#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
INSTANCE_ID=$(ec2-metadata --instance-id | cut -d " " -f 2)
echo "<h1>Instance: $INSTANCE_ID</h1>" > /var/www/html/index.html
echo "OK" > /var/www/html/health'

INSTANCE_1=$(aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.micro \
  --subnet-id $SUBNET_1 \
  --security-group-ids $INSTANCE_SG \
  --user-data "$USER_DATA" \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=web-1}]' \
  --query 'Instances[0].InstanceId' --output text)

INSTANCE_2=$(aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.micro \
  --subnet-id $SUBNET_2 \
  --security-group-ids $INSTANCE_SG \
  --user-data "$USER_DATA" \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=web-2}]' \
  --query 'Instances[0].InstanceId' --output text)

# Wait for instances
aws ec2 wait instance-running --instance-ids $INSTANCE_1 $INSTANCE_2

# Create ALB
ALB_ARN=$(aws elbv2 create-load-balancer \
  --name production-alb \
  --subnets $SUBNET_1 $SUBNET_2 \
  --security-groups $ALB_SG \
  --type application \
  --query 'LoadBalancers[0].LoadBalancerArn' --output text)

# Create target group
TG_ARN=$(aws elbv2 create-target-group \
  --name web-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --health-check-path /health \
  --query 'TargetGroups[0].TargetGroupArn' --output text)

# Register targets
aws elbv2 register-targets \
  --target-group-arn $TG_ARN \
  --targets Id=$INSTANCE_1 Id=$INSTANCE_2

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN

# Get ALB DNS
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --load-balancer-arns $ALB_ARN \
  --query 'LoadBalancers[0].DNSName' --output text)

echo "ALB deployed successfully!"
echo "URL: http://$ALB_DNS"
echo "Wait 2-3 minutes for targets to become healthy"
```

### Exercise 2: Path-Based Routing

**Objective:** Configure path-based routing for microservices

```bash
# Create target groups for different services
API_TG=$(aws elbv2 create-target-group \
  --name api-service \
  --protocol HTTP \
  --port 8080 \
  --vpc-id $VPC_ID \
  --query 'TargetGroups[0].TargetGroupArn' --output text)

WEB_TG=$(aws elbv2 create-target-group \
  --name web-service \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --query 'TargetGroups[0].TargetGroupArn' --output text)

# Create routing rules
aws elbv2 create-rule \
  --listener-arn $HTTP_LISTENER \
  --priority 10 \
  --conditions Field=path-pattern,Values='/api/*' \
  --actions Type=forward,TargetGroupArn=$API_TG

aws elbv2 create-rule \
  --listener-arn $HTTP_LISTENER \
  --priority 20 \
  --conditions Field=path-pattern,Values='/admin/*' \
  --actions Type=fixed-response,FixedResponseConfig='{
    "StatusCode":"403",
    "MessageBody":"Access Denied"
  }'

# Test routing
curl http://$ALB_DNS/api/health  # → API service
curl http://$ALB_DNS/            # → Web service (default)
curl http://$ALB_DNS/admin/      # → 403 Forbidden
```

### Exercise 3: Monitor Load Balancer

**Objective:** Enable monitoring and alarms

```bash
# Enable access logs
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn $ALB_ARN \
  --attributes \
    Key=access_logs.s3.enabled,Value=true \
    Key=access_logs.s3.bucket,Value=my-alb-logs

# Create CloudWatch alarm for unhealthy targets
aws cloudwatch put-metric-alarm \
  --alarm-name alb-unhealthy-targets \
  --alarm-description "Alert on unhealthy targets" \
  --metric-name UnHealthyHostCount \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=LoadBalancer,Value=$ALB_NAME \
  --alarm-actions $SNS_TOPIC_ARN

# Create alarm for high latency
aws cloudwatch put-metric-alarm \
  --alarm-name alb-high-latency \
  --metric-name TargetResponseTime \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=LoadBalancer,Value=$ALB_NAME
```

---

## Validation Checklist

- [ ] Load balancer created in multiple AZs
- [ ] Target groups configured with health checks
- [ ] Listeners created (HTTP/HTTPS)
- [ ] SSL/TLS certificate attached
- [ ] Security groups properly configured
- [ ] Targets registered and healthy
- [ ] Path/host-based routing tested
- [ ] Access logs enabled
- [ ] CloudWatch alarms configured
- [ ] Connection draining verified

---

## Troubleshooting

### Targets Unhealthy

```bash
# Check target health details
aws elbv2 describe-target-health \
  --target-group-arn $TG_ARN

# Common causes:
# 1. Security group doesn't allow traffic from ALB
# 2. Health check path returns non-200
# 3. Instance not running web server
# 4. Health check timeout too short
```

### 502 Bad Gateway

```yaml
Causes:
  - Target not responding
  - Connection timeout
  - Target returning invalid response
  - Keep-alive timeout too short

Solutions:
  - Check target health
  - Increase timeout values
  - Verify target application
  - Check security groups
```

---

## Best Practices

```yaml
High Availability:
  - Deploy ALB in multiple AZs (minimum 2)
  - Distribute targets across AZs
  - Use Route53 health checks

Security:
  - Use HTTPS with valid certificates
  - Enable access logs
  - Restrict security groups
  - Use AWS WAF for web protection

Performance:
  - Enable cross-zone load balancing
  - Use appropriate algorithm
  - Set proper health check intervals
  - Enable connection draining

Cost Optimization:
  - Right-size target instances
  - Use Auto Scaling
  - Delete unused load balancers
  - Monitor LCU/NLCU usage
```

---

## Next Steps

Now that you understand load balancers:
1. ✓ ALB, NLB, GWLB understood
2. ✓ Target groups and health checks configured
3. ✓ SSL/TLS termination implemented
4. → **Next:** Auto Scaling for dynamic capacity (Chapter 8)
5. → RDS databases integration (Chapter 9)

---

## Additional Resources

- [ELB User Guide](https://docs.aws.amazon.com/elasticloadbalancing/)
- [ALB Guide](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/)
- [NLB Guide](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/)
- [Best Practices](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/best-practices.html)
