# Your First EC2 Instance

## Introduction

Amazon Elastic Compute Cloud (EC2) is one of the most fundamental AWS services. It provides resizable compute capacity in the cloud, allowing you to launch virtual servers (instances) within minutes. This chapter will guide you through launching, configuring, and managing your first EC2 instance.

## Table of Contents
- [What is EC2?](#what-is-ec2)
- [EC2 Instance Types](#ec2-instance-types)
- [Amazon Machine Images (AMIs)](#amazon-machine-images-amis)
- [Launching Your First Instance](#launching-your-first-instance)
- [Connecting to Your Instance](#connecting-to-your-instance)
- [Security Groups](#security-groups)
- [EC2 Storage Options](#ec2-storage-options)
- [Instance Management](#instance-management)
- [Hands-on Exercises](#hands-on-exercises)

---

## What is EC2?

### Overview

EC2 (Elastic Compute Cloud) provides:
- **Virtual servers** in the cloud
- **Scalable capacity** - scale up or down
- **Pay-as-you-go** pricing
- **Complete control** over computing resources
- **Integration** with other AWS services

### Key Concepts

```yaml
Instance: Virtual server running in AWS
AMI: Template for instance (operating system + software)
Instance Type: Hardware specification (CPU, memory, storage)
EBS: Elastic Block Store - persistent storage
Security Group: Virtual firewall for instances
Key Pair: SSH credentials for secure access
```

### EC2 Use Cases

```
Web Hosting: Deploy web applications
Development/Testing: Create dev environments
Data Processing: Batch jobs, data analysis
Gaming Servers: Multiplayer game hosting
Machine Learning: Training and inference
Microservices: Container and API hosting
```

---

## EC2 Instance Types

### Instance Type Categories

#### 1. General Purpose (T, M series)
```yaml
T3/T3a: Burstable performance
  - t3.micro: 2 vCPU, 1 GB RAM (Free Tier)
  - t3.small: 2 vCPU, 2 GB RAM
  - t3.medium: 2 vCPU, 4 GB RAM
  
M6i/M6a: Balanced compute, memory, networking
  - m6i.large: 2 vCPU, 8 GB RAM
  - m6i.xlarge: 4 vCPU, 16 GB RAM
```

#### 2. Compute Optimized (C series)
```yaml
C6i/C6a: High-performance processors
  - c6i.large: 2 vCPU, 4 GB RAM
  - c6i.xlarge: 4 vCPU, 8 GB RAM
  
Use Cases: Batch processing, web servers, gaming
```

#### 3. Memory Optimized (R, X series)
```yaml
R6i/R6a: Memory-intensive applications
  - r6i.large: 2 vCPU, 16 GB RAM
  - r6i.xlarge: 4 vCPU, 32 GB RAM
  
Use Cases: Databases, caching, real-time analytics
```

#### 4. Storage Optimized (I, D series)
```yaml
I3/I4i: High IOPS
  - i3.large: 2 vCPU, 15.25 GB RAM, NVMe SSD
  
Use Cases: NoSQL databases, data warehousing
```

#### 5. Accelerated Computing (P, G, Inf series)
```yaml
P4/P5: GPU instances for ML training
G5: Graphics-intensive applications
Inf2: ML inference
```

### Choosing Instance Type

```bash
# List available instance types in region
aws ec2 describe-instance-types \
  --region us-east-1 \
  --query 'InstanceTypes[?contains(InstanceType, `t3`)].InstanceType' \
  --output table

# Get detailed info about specific type
aws ec2 describe-instance-types \
  --instance-types t3.micro \
  --query 'InstanceTypes[0].[InstanceType, VCpuInfo.DefaultVCpus, MemoryInfo.SizeInMiB]' \
  --output table
```

**Instance Type Naming Convention:**
```
t3.micro
│└─── Instance size
└──── Instance generation
└───── Instance family

Families:
t = Burstable general purpose
m = General purpose
c = Compute optimized
r = Memory optimized
i = Storage optimized
p = GPU (parallel processing)
```

---

## Amazon Machine Images (AMIs)

### What is an AMI?

An AMI is a template containing:
- **Operating system**
- **Application server**
- **Applications**
- **Configuration**

### AMI Types

```yaml
Amazon Linux 2023: AWS-optimized Linux
Ubuntu: Popular Linux distribution
Red Hat Enterprise Linux: Enterprise Linux
Windows Server: Microsoft Windows
Custom AMIs: Your own images
```

### Finding AMIs

```bash
# List Amazon Linux 2023 AMIs
aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=al2023-ami-2023*" \
  --query 'Images[*].[ImageId,Name,CreationDate]' \
  --output table

# Find Ubuntu AMIs
aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].[ImageId,Name]' \
  --output table

# Get latest Amazon Linux 2023 AMI ID
aws ssm get-parameter \
  --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query 'Parameter.Value' \
  --output text
```

---

## Launching Your First Instance

### Method 1: AWS Console

**Step-by-Step Guide:**

```
1. Open EC2 Console
   └─ Navigate to: Services > EC2 > Launch Instance

2. Name and Tags
   └─ Name: my-first-instance
   └─ Tags: Environment=Learning, Project=AWSBasics

3. Choose AMI
   └─ Amazon Linux 2023 AMI (Free tier eligible)

4. Choose Instance Type
   └─ t3.micro or t2.micro (Free tier eligible)

5. Key Pair
   └─ Create new key pair: my-ec2-key
   └─ Type: RSA
   └─ Format: .pem (Linux/Mac) or .ppk (Windows/PuTTY)

6. Network Settings
   └─ VPC: Default
   └─ Subnet: Default (any AZ)
   └─ Auto-assign Public IP: Enable
   └─ Security Group: Create new
      ├─ Allow SSH from My IP
      └─ Allow HTTP from anywhere

7. Storage
   └─ 8 GB gp3 (Free tier: up to 30 GB)

8. Advanced Details (optional)
   └─ IAM instance profile: (none for now)
   └─ User data: (bootstrap scripts)

9. Review and Launch
```

### Method 2: AWS CLI

```bash
# Create key pair
aws ec2 create-key-pair \
  --key-name my-ec2-key \
  --query 'KeyMaterial' \
  --output text > my-ec2-key.pem

# Set permissions (Linux/Mac)
chmod 400 my-ec2-key.pem

# Get latest Amazon Linux 2023 AMI
AMI_ID=$(aws ssm get-parameter \
  --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query 'Parameter.Value' \
  --output text)

# Create security group
SG_ID=$(aws ec2 create-security-group \
  --group-name my-first-sg \
  --description "Security group for my first instance" \
  --query 'GroupId' \
  --output text)

# Allow SSH access
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# Allow HTTP access
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Launch instance
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.micro \
  --key-name my-ec2-key \
  --security-group-ids $SG_ID \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=my-first-instance}]' \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "Instance ID: $INSTANCE_ID"

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP address
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "Public IP: $PUBLIC_IP"
```

### Method 3: Using User Data (Bootstrap Script)

**user-data.sh:**
```bash
#!/bin/bash
# Update system
yum update -y

# Install Apache web server
yum install -y httpd

# Start and enable Apache
systemctl start httpd
systemctl enable httpd

# Create simple web page
cat > /var/www/html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>My First EC2 Instance</title>
</head>
<body>
    <h1>Hello from EC2!</h1>
    <p>Instance ID: <span id="instance-id"></span></p>
    <p>Availability Zone: <span id="az"></span></p>
    
    <script>
        // Fetch instance metadata
        fetch('http://169.254.169.254/latest/meta-data/instance-id')
            .then(response => response.text())
            .then(data => document.getElementById('instance-id').textContent = data);
        
        fetch('http://169.254.169.254/latest/meta-data/placement/availability-zone')
            .then(response => response.text())
            .then(data => document.getElementById('az').textContent = data);
    </script>
</body>
</html>
EOF
```

```bash
# Launch with user data
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.micro \
  --key-name my-ec2-key \
  --security-group-ids $SG_ID \
  --user-data file://user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=web-server}]'
```

---

## Connecting to Your Instance

### SSH Connection (Linux/Mac)

```bash
# Connect using SSH
ssh -i my-ec2-key.pem ec2-user@<PUBLIC_IP>

# Example
ssh -i my-ec2-key.pem ec2-user@54.123.45.67

# First connection may show fingerprint warning
# Type 'yes' to continue
```

**Troubleshooting SSH:**
```bash
# Verbose mode for debugging
ssh -v -i my-ec2-key.pem ec2-user@<PUBLIC_IP>

# Common issues:
# 1. Wrong permissions on key file
chmod 400 my-ec2-key.pem

# 2. Wrong username
# Amazon Linux: ec2-user
# Ubuntu: ubuntu
# Red Hat: ec2-user
# CentOS: centos
```

### PuTTY Connection (Windows)

```powershell
# Convert .pem to .ppk using PuTTYgen
# 1. Download PuTTYgen
# 2. Load .pem file
# 3. Save private key as .ppk

# Connect using PuTTY:
# 1. Host Name: ec2-user@<PUBLIC_IP>
# 2. Connection > SSH > Auth: Browse for .ppk file
# 3. Click Open
```

### EC2 Instance Connect (Browser-based)

```bash
# Enable Instance Connect (already enabled on Amazon Linux 2023)
# Console: EC2 > Instances > Select instance > Connect > EC2 Instance Connect

# CLI: Install Instance Connect client
pip install ec2instanceconnectcli

# Connect
mssh ec2-user@<INSTANCE_ID>
```

### Session Manager (No SSH required)

```bash
# Requires SSM agent (pre-installed on Amazon Linux 2023)
# Requires IAM role with AmazonSSMManagedInstanceCore policy

# Create IAM role
aws iam create-role \
  --role-name SSM-Role \
  --assume-role-policy-document file://ssm-trust-policy.json

aws iam attach-role-policy \
  --role-name SSM-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

# Connect via Session Manager
aws ssm start-session --target <INSTANCE_ID>
```

---

## Security Groups

### Understanding Security Groups

Security groups act as virtual firewalls:

```yaml
Stateful: Return traffic automatically allowed
Default: All outbound allowed, all inbound denied
Rules: Define allowed traffic
Multiple: Instance can have multiple security groups
```

### Creating Security Group Rules

```bash
# Create security group
aws ec2 create-security-group \
  --group-name web-server-sg \
  --description "Security group for web servers" \
  --vpc-id vpc-12345678

# Allow SSH from specific IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.0/24

# Allow HTTP from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Allow HTTPS from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Allow all traffic from another security group
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol -1 \
  --source-group sg-87654321
```

**Common Security Group Rules:**
```yaml
SSH (22): Administration
HTTP (80): Web traffic
HTTPS (443): Secure web traffic
RDP (3389): Windows remote desktop
MySQL (3306): Database
PostgreSQL (5432): Database
Redis (6379): Cache
Custom TCP: Application-specific
```

### Security Group Best Practices

```bash
# View security group rules
aws ec2 describe-security-groups \
  --group-ids sg-12345678

# Remove rule
aws ec2 revoke-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0
```

**Best Practices:**
```
1. Principle of Least Privilege
   - Only open required ports
   - Restrict source IPs when possible

2. Use Descriptive Names
   - web-server-sg
   - database-sg
   - application-sg

3. Regular Audits
   - Review unused security groups
   - Check for overly permissive rules

4. Layered Security
   - Combine security groups
   - Use NACLs for subnet-level control
   - Enable AWS WAF for web applications
```

---

## EC2 Storage Options

### EBS (Elastic Block Store)

```yaml
General Purpose SSD (gp3):
  - 3,000-16,000 IOPS
  - 125-1,000 MB/s throughput
  - Cost-effective

Provisioned IOPS SSD (io2):
  - Up to 64,000 IOPS
  - 1,000 MB/s throughput
  - High-performance databases

Throughput Optimized HDD (st1):
  - 500 MB/s throughput
  - Big data, data warehouses

Cold HDD (sc1):
  - 250 MB/s throughput
  - Infrequent access
```

```bash
# Create EBS volume
aws ec2 create-volume \
  --availability-zone us-east-1a \
  --size 10 \
  --volume-type gp3 \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=my-volume}]'

# Attach volume to instance
aws ec2 attach-volume \
  --volume-id vol-12345678 \
  --instance-id i-12345678 \
  --device /dev/sdf

# Format and mount (on instance)
sudo mkfs -t ext4 /dev/xvdf
sudo mkdir /mnt/data
sudo mount /dev/xvdf /mnt/data

# Make permanent (add to /etc/fstab)
echo "/dev/xvdf /mnt/data ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
```

### EBS Snapshots

```bash
# Create snapshot
aws ec2 create-snapshot \
  --volume-id vol-12345678 \
  --description "My first snapshot" \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Name,Value=daily-backup}]'

# List snapshots
aws ec2 describe-snapshots --owner-ids self

# Create volume from snapshot
aws ec2 create-volume \
  --snapshot-id snap-12345678 \
  --availability-zone us-east-1a \
  --volume-type gp3

# Copy snapshot to another region
aws ec2 copy-snapshot \
  --source-region us-east-1 \
  --source-snapshot-id snap-12345678 \
  --destination-region us-west-2
```

### Instance Store

```bash
# Instance store is ephemeral (data lost on stop/terminate)
# Automatically attached to certain instance types

# View instance store volumes
lsblk

# Example: i3.large has 475 GB NVMe SSD
# Mount instance store
sudo mkfs -t ext4 /dev/nvme1n1
sudo mkdir /mnt/instance-store
sudo mount /dev/nvme1n1 /mnt/instance-store
```

---

## Instance Management

### Start, Stop, Reboot, Terminate

```bash
# Stop instance
aws ec2 stop-instances --instance-ids i-12345678

# Start instance
aws ec2 start-instances --instance-ids i-12345678

# Reboot instance
aws ec2 reboot-instances --instance-ids i-12345678

# Terminate instance
aws ec2 terminate-instances --instance-ids i-12345678

# Check instance status
aws ec2 describe-instance-status --instance-ids i-12345678
```

### Modify Instance

```bash
# Change instance type (must be stopped first)
aws ec2 stop-instances --instance-ids i-12345678
aws ec2 wait instance-stopped --instance-ids i-12345678

aws ec2 modify-instance-attribute \
  --instance-id i-12345678 \
  --instance-type t3.small

aws ec2 start-instances --instance-ids i-12345678

# Enable termination protection
aws ec2 modify-instance-attribute \
  --instance-id i-12345678 \
  --disable-api-termination

# Disable termination protection
aws ec2 modify-instance-attribute \
  --instance-id i-12345678 \
  --no-disable-api-termination
```

### Instance Metadata

```bash
# Access from within instance
# Instance ID
curl http://169.254.169.254/latest/meta-data/instance-id

# Instance type
curl http://169.254.169.254/latest/meta-data/instance-type

# Public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4

# IAM role credentials
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# User data
curl http://169.254.169.254/latest/user-data
```

### Tags and Naming

```bash
# Create tags
aws ec2 create-tags \
  --resources i-12345678 \
  --tags Key=Environment,Value=Production Key=Owner,Value=DevTeam

# List instances with specific tag
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=Production" \
  --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value|[0]]' \
  --output table
```

---

## Hands-on Exercises

### Exercise 1: Launch and Connect

**Objective:** Launch an EC2 instance and connect via SSH

```bash
# Complete workflow script
#!/bin/bash

# Variables
KEY_NAME="my-first-key"
SG_NAME="my-first-sg"
INSTANCE_TYPE="t3.micro"

# Get latest Amazon Linux 2023 AMI
AMI_ID=$(aws ssm get-parameter \
  --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query 'Parameter.Value' --output text)

# Create key pair
aws ec2 create-key-pair \
  --key-name $KEY_NAME \
  --query 'KeyMaterial' \
  --output text > ${KEY_NAME}.pem
chmod 400 ${KEY_NAME}.pem

# Create security group
SG_ID=$(aws ec2 create-security-group \
  --group-name $SG_NAME \
  --description "My first security group" \
  --query 'GroupId' --output text)

# Allow SSH from your IP
MY_IP=$(curl -s https://checkip.amazonaws.com)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp --port 22 \
  --cidr ${MY_IP}/32

# Launch instance
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type $INSTANCE_TYPE \
  --key-name $KEY_NAME \
  --security-group-ids $SG_ID \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=my-first-instance}]' \
  --query 'Instances[0].InstanceId' --output text)

echo "Launched instance: $INSTANCE_ID"

# Wait for running state
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "Public IP: $PUBLIC_IP"
echo "Connect with: ssh -i ${KEY_NAME}.pem ec2-user@${PUBLIC_IP}"
```

### Exercise 2: Deploy Web Server

**Objective:** Launch an instance with Apache web server

```bash
# user-data script for web server
cat > web-server-userdata.sh << 'EOF'
#!/bin/bash
yum update -y
yum install -y httpd php php-mysql

systemctl start httpd
systemctl enable httpd

# Create PHP info page
cat > /var/www/html/index.php << 'HTML'
<?php
echo "<h1>EC2 Web Server</h1>";
echo "<p>Instance ID: " . file_get_contents('http://169.254.169.254/latest/meta-data/instance-id') . "</p>";
echo "<p>Instance Type: " . file_get_contents('http://169.254.169.254/latest/meta-data/instance-type') . "</p>";
echo "<p>Availability Zone: " . file_get_contents('http://169.254.169.254/latest/meta-data/placement/availability-zone') . "</p>";
phpinfo();
?>
HTML
EOF

# Launch instance with user data
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.micro \
  --key-name my-key \
  --security-group-ids $SG_ID \
  --user-data file://web-server-userdata.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=web-server}]'
```

### Exercise 3: Cleanup Resources

**Objective:** Properly clean up all created resources

```bash
#!/bin/bash

# Terminate instances
echo "Terminating instances..."
INSTANCE_IDS=$(aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running,stopped" \
  --query 'Reservations[*].Instances[*].InstanceId' \
  --output text)

if [ -n "$INSTANCE_IDS" ]; then
  aws ec2 terminate-instances --instance-ids $INSTANCE_IDS
  aws ec2 wait instance-terminated --instance-ids $INSTANCE_IDS
  echo "Instances terminated"
fi

# Delete security groups
echo "Deleting security groups..."
SG_IDS=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=my-*" \
  --query 'SecurityGroups[*].GroupId' \
  --output text)

for sg in $SG_IDS; do
  aws ec2 delete-security-group --group-id $sg && echo "Deleted $sg"
done

# Delete key pairs
echo "Deleting key pairs..."
aws ec2 delete-key-pair --key-name my-first-key
rm -f my-first-key.pem

echo "Cleanup complete!"
```

---

## Validation Checklist

- [ ] EC2 instance launched successfully
- [ ] SSH connection established
- [ ] Security group configured correctly
- [ ] Web server deployed and accessible
- [ ] Instance metadata accessed
- [ ] EBS volume attached and mounted
- [ ] Snapshot created
- [ ] Instance stopped and started
- [ ] Resources cleaned up properly

---

## Next Steps

Congratulations on launching your first EC2 instance! Next:
1. ✓ EC2 instance launched and managed
2. ✓ SSH connection established
3. ✓ Basic web server deployed
4. → **Next:** S3 Basics and object storage (Chapter 5)
5. → Explore VPC networking (Intermediate topics)

---

## Additional Resources

- [EC2 User Guide](https://docs.aws.amazon.com/ec2/)
- [EC2 Instance Types](https://aws.amazon.com/ec2/instance-types/)
- [EC2 Pricing](https://aws.amazon.com/ec2/pricing/)
- [Security Best Practices](https://docs.aws.amazon.com/ec2/latest/userguide/ec2-security.html)
