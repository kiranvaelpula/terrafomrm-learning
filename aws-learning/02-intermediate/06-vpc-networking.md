# VPC Networking Fundamentals

## Introduction

Amazon Virtual Private Cloud (VPC) is a foundational AWS service that lets you launch resources in a logically isolated virtual network. Understanding VPC networking is critical for building secure, scalable applications on AWS. This chapter covers VPC concepts, subnet design, routing, internet connectivity, and security.

## Table of Contents
- [What is a VPC?](#what-is-a-vpc)
- [VPC Components](#vpc-components)
- [CIDR Blocks and IP Addressing](#cidr-blocks-and-ip-addressing)
- [Subnets: Public vs Private](#subnets-public-vs-private)
- [Internet Gateway and NAT](#internet-gateway-and-nat)
- [Route Tables](#route-tables)
- [Network ACLs](#network-acls)
- [VPC Peering](#vpc-peering)
- [VPC Endpoints](#vpc-endpoints)
- [Hands-on Exercises](#hands-on-exercises)

---

## What is a VPC?

### Overview

A VPC is your own private network within AWS:

```yaml
Characteristics:
  - Logically isolated from other VPCs
  - Complete control over network configuration
  - Can span multiple Availability Zones
  - Cannot span multiple regions
  - Default VPC provided per region
  - Can create up to 5 VPCs per region (soft limit)
```

### VPC Benefits

```yaml
Security:
  - Network isolation
  - Security groups and NACLs
  - Private subnets
  - VPN and Direct Connect

Control:
  - Define IP address range
  - Create subnets
  - Configure route tables
  - Network gateway control

Scalability:
  - Supports thousands of instances
  - Elastic IP addresses
  - Multiple availability zones
```

### Default vs Custom VPC

```yaml
Default VPC:
  CIDR: 172.31.0.0/16
  Subnets: One per AZ (all public)
  Internet Gateway: Attached
  Route Table: Routes to internet
  DNS: Enabled
  DHCP: AWS default options
  
Custom VPC:
  CIDR: You choose (10.0.0.0/16, 192.168.0.0/16, etc.)
  Subnets: You create and configure
  Internet Gateway: You attach if needed
  Route Tables: You configure
  DNS: Optional
  DHCP: Custom options available
```

---

## VPC Components

### Core Components Diagram

```
VPC (10.0.0.0/16)
│
├── Internet Gateway (IGW)
│   └── Enables internet connectivity
│
├── Subnets
│   ├── Public Subnet (10.0.1.0/24) - AZ-1
│   │   ├── Route to IGW
│   │   └── Auto-assign public IP
│   │
│   ├── Private Subnet (10.0.2.0/24) - AZ-1
│   │   ├── No direct internet route
│   │   └── Uses NAT Gateway
│   │
│   ├── Public Subnet (10.0.3.0/24) - AZ-2
│   └── Private Subnet (10.0.4.0/24) - AZ-2
│
├── Route Tables
│   ├── Main Route Table
│   ├── Public Route Table (to IGW)
│   └── Private Route Table (to NAT)
│
├── NAT Gateway
│   └── Allows outbound internet from private subnets
│
├── Network ACLs
│   └── Subnet-level firewall
│
└── Security Groups
    └── Instance-level firewall
```


---

## CIDR Blocks and IP Addressing

### Understanding CIDR Notation

```yaml
CIDR Format: IP_Address/Prefix_Length
Example: 10.0.0.0/16

Common CIDR Blocks:
  /16: 65,536 IP addresses (10.0.0.0 - 10.0.255.255)
  /24: 256 IP addresses (10.0.0.0 - 10.0.0.255)
  /28: 16 IP addresses (10.0.0.0 - 10.0.0.15)
  /32: 1 IP address (specific host)

AWS Reserved IPs (per subnet):
  .0: Network address
  .1: VPC router
  .2: DNS server
  .3: Future use
  .255: Broadcast (not supported, but reserved)
  Example in 10.0.1.0/24: 5 reserved, 251 usable
```

### VPC CIDR Best Practices

```yaml
Recommended CIDR Blocks:
  - 10.0.0.0/8 (10.0.0.0 - 10.255.255.255)
  - 172.16.0.0/12 (172.16.0.0 - 172.31.255.255)
  - 192.168.0.0/16 (192.168.0.0 - 192.168.255.255)

VPC Size Recommendations:
  Small: /24 (256 IPs) - Dev/test
  Medium: /20 (4,096 IPs) - Small production
  Large: /16 (65,536 IPs) - Production
  
Avoid:
  - Overlapping with on-premises networks
  - Overlapping with other VPCs (if peering)
  - Too small (hard to expand)
  - Too large (waste of space)
```

### Create VPC with CIDR

```bash
# Create VPC
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=my-vpc}]' \
  --query 'Vpc.VpcId' \
  --output text)

echo "VPC ID: $VPC_ID"

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
  --vpc-id $VPC_ID \
  --enable-dns-hostnames

# Enable DNS support
aws ec2 modify-vpc-attribute \
  --vpc-id $VPC_ID \
  --enable-dns-support

# Add secondary CIDR (optional)
aws ec2 associate-vpc-cidr-block \
  --vpc-id $VPC_ID \
  --cidr-block 10.1.0.0/16
```


---

## Subnets: Public vs Private

### Subnet Fundamentals

```yaml
Subnet:
  - Subdivision of VPC
  - Exists in single AZ
  - Has own CIDR (subset of VPC CIDR)
  - Can be public or private
  - Minimum size: /28 (16 IPs, 11 usable)
  - Maximum size: Same as VPC CIDR

Public Subnet:
  - Has route to Internet Gateway
  - Instances get public IP
  - Accessible from internet
  - Use: Web servers, load balancers

Private Subnet:
  - No direct internet route
  - Uses NAT for outbound
  - Not directly accessible
  - Use: Databases, application servers
```

### Multi-AZ Subnet Design

```yaml
Best Practice Architecture:
VPC: 10.0.0.0/16

Availability Zone 1:
  Public:  10.0.1.0/24
  Private: 10.0.2.0/24
  Data:    10.0.3.0/24

Availability Zone 2:
  Public:  10.0.11.0/24
  Private: 10.0.12.0/24
  Data:    10.0.13.0/24

Availability Zone 3:
  Public:  10.0.21.0/24
  Private: 10.0.22.0/24
  Data:    10.0.23.0/24
```

### Create Subnets

```bash
# Get available AZs
aws ec2 describe-availability-zones \
  --region us-east-1 \
  --query 'AvailabilityZones[*].ZoneName' \
  --output table

# Create public subnet - AZ1
PUBLIC_SUBNET_1=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet-1a}]' \
  --query 'Subnet.SubnetId' \
  --output text)

# Enable auto-assign public IP
aws ec2 modify-subnet-attribute \
  --subnet-id $PUBLIC_SUBNET_1 \
  --map-public-ip-on-launch

# Create private subnet - AZ1
PRIVATE_SUBNET_1=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-subnet-1a}]' \
  --query 'Subnet.SubnetId' \
  --output text)

# Create public subnet - AZ2
PUBLIC_SUBNET_2=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.11.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet-1b}]' \
  --query 'Subnet.SubnetId' \
  --output text)

aws ec2 modify-subnet-attribute \
  --subnet-id $PUBLIC_SUBNET_2 \
  --map-public-ip-on-launch

# Create private subnet - AZ2
PRIVATE_SUBNET_2=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.12.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-subnet-1b}]' \
  --query 'Subnet.SubnetId' \
  --output text)
```


---

## Internet Gateway and NAT

### Internet Gateway (IGW)

```yaml
Purpose:
  - Enables internet connectivity
  - Attached to VPC
  - Horizontally scaled, redundant, HA
  - No bandwidth constraints
  - One IGW per VPC

Requirements for Internet Access:
  1. IGW attached to VPC
  2. Route table entry to IGW
  3. Public IP or Elastic IP
  4. Security group allows traffic
  5. Network ACL allows traffic
```

```bash
# Create Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=my-igw}]' \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)

# Attach to VPC
aws ec2 attach-internet-gateway \
  --internet-gateway-id $IGW_ID \
  --vpc-id $VPC_ID

# Verify attachment
aws ec2 describe-internet-gateways \
  --internet-gateway-ids $IGW_ID
```

### NAT Gateway

```yaml
Purpose:
  - Allows private subnet outbound internet
  - Prevents inbound from internet
  - Managed by AWS
  - Highly available within AZ

NAT Gateway vs NAT Instance:
  NAT Gateway (Recommended):
    - Managed service
    - Automatic scaling
    - Up to 45 Gbps
    - Requires Elastic IP
    - $0.045/hour + data transfer
    
  NAT Instance (Legacy):
    - EC2 instance
    - Manual scaling
    - Depends on instance type
    - Can be cheaper for low traffic
    - Requires management
```

```bash
# Allocate Elastic IP for NAT
EIP_ALLOC=$(aws ec2 allocate-address \
  --domain vpc \
  --query 'AllocationId' \
  --output text)

# Create NAT Gateway in public subnet
NAT_GW_ID=$(aws ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET_1 \
  --allocation-id $EIP_ALLOC \
  --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=my-nat-gw}]' \
  --query 'NatGateway.NatGatewayId' \
  --output text)

# Wait for available state
aws ec2 wait nat-gateway-available \
  --nat-gateway-ids $NAT_GW_ID

# Check status
aws ec2 describe-nat-gateways \
  --nat-gateway-ids $NAT_GW_ID
```

### High Availability NAT

```yaml
Best Practice: One NAT Gateway per AZ

Single AZ (Not HA):
  AZ-1 Public: NAT Gateway
  AZ-1 Private: → NAT Gateway
  AZ-2 Private: → NAT Gateway (cross-AZ traffic)

Multi-AZ (HA):
  AZ-1 Public: NAT Gateway 1
  AZ-1 Private: → NAT Gateway 1
  AZ-2 Public: NAT Gateway 2
  AZ-2 Private: → NAT Gateway 2
```


---

## Route Tables

### Route Table Basics

```yaml
Route Table:
  - Contains routing rules
  - Each subnet associated with one route table
  - Main route table (default for subnets)
  - Custom route tables for specific needs

Route Components:
  Destination: Target CIDR (0.0.0.0/0 = all traffic)
  Target: Where to send traffic (IGW, NAT, VPC peering)
  
Route Priority:
  - Most specific route wins
  - Local VPC route always first
```

### Create Route Tables

```bash
# Create public route table
PUBLIC_RT=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=public-rt}]' \
  --query 'RouteTable.RouteTableId' \
  --output text)

# Add route to Internet Gateway
aws ec2 create-route \
  --route-table-id $PUBLIC_RT \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID

# Associate with public subnets
aws ec2 associate-route-table \
  --route-table-id $PUBLIC_RT \
  --subnet-id $PUBLIC_SUBNET_1

aws ec2 associate-route-table \
  --route-table-id $PUBLIC_RT \
  --subnet-id $PUBLIC_SUBNET_2

# Create private route table
PRIVATE_RT=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=private-rt}]' \
  --query 'RouteTable.RouteTableId' \
  --output text)

# Add route to NAT Gateway
aws ec2 create-route \
  --route-table-id $PRIVATE_RT \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id $NAT_GW_ID

# Associate with private subnets
aws ec2 associate-route-table \
  --route-table-id $PRIVATE_RT \
  --subnet-id $PRIVATE_SUBNET_1

aws ec2 associate-route-table \
  --route-table-id $PRIVATE_RT \
  --subnet-id $PRIVATE_SUBNET_2
```

### Route Table Examples

```bash
# View route table
aws ec2 describe-route-tables \
  --route-table-ids $PUBLIC_RT

# Example output interpretation:
# Destination        Target              Status
# 10.0.0.0/16       local               active  (VPC internal)
# 0.0.0.0/0         igw-xxx             active  (Internet)

# Add specific route
aws ec2 create-route \
  --route-table-id $PRIVATE_RT \
  --destination-cidr-block 192.168.0.0/16 \
  --vpc-peering-connection-id pcx-xxx

# Delete route
aws ec2 delete-route \
  --route-table-id $PRIVATE_RT \
  --destination-cidr-block 0.0.0.0/0
```

---

## Network ACLs

### NACL vs Security Groups

```yaml
Network ACL (Subnet Level):
  - Stateless (return traffic must be explicitly allowed)
  - Applies to all instances in subnet
  - Numbered rules (processed in order)
  - Supports ALLOW and DENY rules
  - Default: Allow all inbound/outbound

Security Group (Instance Level):
  - Stateful (return traffic automatically allowed)
  - Applies to specific instances
  - All rules evaluated
  - Only ALLOW rules
  - Default: Deny all inbound, allow all outbound
```

### Default NACL Rules

```yaml
Default NACL (allows everything):
  Inbound:
    Rule 100: Allow ALL traffic from 0.0.0.0/0
    Rule *: Deny ALL traffic
  
  Outbound:
    Rule 100: Allow ALL traffic to 0.0.0.0/0
    Rule *: Deny ALL traffic

Custom NACL (denies everything by default):
  Inbound: Rule *: Deny ALL
  Outbound: Rule *: Deny ALL
```

### Create Custom NACL

```bash
# Create NACL
NACL_ID=$(aws ec2 create-network-acl \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=network-acl,Tags=[{Key=Name,Value=custom-nacl}]' \
  --query 'NetworkAcl.NetworkAclId' \
  --output text)

# Allow HTTP inbound
aws ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID \
  --rule-number 100 \
  --protocol tcp \
  --port-range From=80,To=80 \
  --cidr-block 0.0.0.0/0 \
  --egress false \
  --rule-action allow

# Allow HTTPS inbound
aws ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID \
  --rule-number 110 \
  --protocol tcp \
  --port-range From=443,To=443 \
  --cidr-block 0.0.0.0/0 \
  --egress false \
  --rule-action allow

# Allow ephemeral ports inbound (for return traffic)
aws ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID \
  --rule-number 120 \
  --protocol tcp \
  --port-range From=1024,To=65535 \
  --cidr-block 0.0.0.0/0 \
  --egress false \
  --rule-action allow

# Allow all outbound
aws ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID \
  --rule-number 100 \
  --protocol -1 \
  --cidr-block 0.0.0.0/0 \
  --egress true \
  --rule-action allow

# Associate with subnet
aws ec2 replace-network-acl-association \
  --association-id $(aws ec2 describe-network-acls \
    --filters "Name=association.subnet-id,Values=$PUBLIC_SUBNET_1" \
    --query 'NetworkAcls[0].Associations[0].NetworkAclAssociationId' \
    --output text) \
  --network-acl-id $NACL_ID
```


---

## VPC Peering

### What is VPC Peering?

```yaml
VPC Peering:
  - Network connection between two VPCs
  - Private connectivity using AWS network
  - Can be in same or different regions
  - Can be in same or different accounts
  - Not transitive (A→B, B→C doesn't mean A→C)
  
Use Cases:
  - Connect production and development VPCs
  - Share resources across VPCs
  - Multi-region applications
  - Cross-account access
```

### VPC Peering Setup

```bash
# Create peering connection (from VPC A to VPC B)
PEER_ID=$(aws ec2 create-vpc-peering-connection \
  --vpc-id $VPC_A_ID \
  --peer-vpc-id $VPC_B_ID \
  --peer-region us-west-2 \
  --tag-specifications 'ResourceType=vpc-peering-connection,Tags=[{Key=Name,Value=vpc-a-to-vpc-b}]' \
  --query 'VpcPeeringConnection.VpcPeeringConnectionId' \
  --output text)

# Accept peering (in peer VPC account/region)
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id $PEER_ID \
  --region us-west-2

# Add routes in VPC A
aws ec2 create-route \
  --route-table-id $VPC_A_RT \
  --destination-cidr-block 10.1.0.0/16 \
  --vpc-peering-connection-id $PEER_ID

# Add routes in VPC B
aws ec2 create-route \
  --route-table-id $VPC_B_RT \
  --destination-cidr-block 10.0.0.0/16 \
  --vpc-peering-connection-id $PEER_ID \
  --region us-west-2

# Update security groups to allow traffic
aws ec2 authorize-security-group-ingress \
  --group-id $SG_A \
  --protocol -1 \
  --source-group $SG_B
```

---

## VPC Endpoints

### Types of VPC Endpoints

```yaml
Interface Endpoint (PrivateLink):
  - ENI with private IP
  - Supports many AWS services
  - Costs: $0.01/hour + data transfer
  - Use: API Gateway, CloudWatch, SNS, etc.

Gateway Endpoint:
  - Route table target
  - Free (only data transfer costs)
  - Supports: S3, DynamoDB
  - Preferred for S3/DynamoDB access

Gateway Load Balancer Endpoint:
  - For third-party appliances
  - Inspection, firewalls
```

### Create S3 Gateway Endpoint

```bash
# Create S3 gateway endpoint
ENDPOINT_ID=$(aws ec2 create-vpc-endpoint \
  --vpc-id $VPC_ID \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids $PRIVATE_RT \
  --query 'VpcEndpoint.VpcEndpointId' \
  --output text)

# Verify
aws ec2 describe-vpc-endpoints \
  --vpc-endpoint-ids $ENDPOINT_ID

# Check route table (new S3 route added automatically)
aws ec2 describe-route-tables \
  --route-table-ids $PRIVATE_RT
```

### Create Interface Endpoint

```bash
# Create interface endpoint for EC2
INTERFACE_EP=$(aws ec2 create-vpc-endpoint \
  --vpc-id $VPC_ID \
  --vpc-endpoint-type Interface \
  --service-name com.amazonaws.us-east-1.ec2 \
  --subnet-ids $PRIVATE_SUBNET_1 $PRIVATE_SUBNET_2 \
  --security-group-ids $EP_SG \
  --query 'VpcEndpoint.VpcEndpointId' \
  --output text)

# Enable private DNS
aws ec2 modify-vpc-endpoint \
  --vpc-endpoint-id $INTERFACE_EP \
  --private-dns-enabled
```

---

## Hands-on Exercises

### Exercise 1: Complete VPC Setup

**Objective:** Create production-ready VPC with public/private subnets

```bash
#!/bin/bash
# Complete VPC setup script

set -e

# Variables
VPC_CIDR="10.0.0.0/16"
AWS_REGION="us-east-1"

echo "Creating VPC..."
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block $VPC_CIDR \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=production-vpc}]' \
  --query 'Vpc.VpcId' \
  --output text)

# Enable DNS
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support

echo "Creating subnets..."
# Public subnets
PUBLIC_SUBNET_1=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone ${AWS_REGION}a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-1a},{Key=Type,Value=Public}]' \
  --query 'Subnet.SubnetId' --output text)

PUBLIC_SUBNET_2=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone ${AWS_REGION}b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-1b},{Key=Type,Value=Public}]' \
  --query 'Subnet.SubnetId' --output text)

# Enable auto-assign public IP
aws ec2 modify-subnet-attribute --subnet-id $PUBLIC_SUBNET_1 --map-public-ip-on-launch
aws ec2 modify-subnet-attribute --subnet-id $PUBLIC_SUBNET_2 --map-public-ip-on-launch

# Private subnets
PRIVATE_SUBNET_1=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.11.0/24 \
  --availability-zone ${AWS_REGION}a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-1a},{Key=Type,Value=Private}]' \
  --query 'Subnet.SubnetId' --output text)

PRIVATE_SUBNET_2=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.12.0/24 \
  --availability-zone ${AWS_REGION}b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-1b},{Key=Type,Value=Private}]' \
  --query 'Subnet.SubnetId' --output text)

echo "Creating Internet Gateway..."
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=production-igw}]' \
  --query 'InternetGateway.InternetGatewayId' --output text)

aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID

echo "Creating NAT Gateway..."
EIP_ALLOC=$(aws ec2 allocate-address --domain vpc --query 'AllocationId' --output text)

NAT_GW_ID=$(aws ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET_1 \
  --allocation-id $EIP_ALLOC \
  --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=production-nat}]' \
  --query 'NatGateway.NatGatewayId' --output text)

echo "Waiting for NAT Gateway..."
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_GW_ID

echo "Creating route tables..."
# Public route table
PUBLIC_RT=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=public-rt}]' \
  --query 'RouteTable.RouteTableId' --output text)

aws ec2 create-route --route-table-id $PUBLIC_RT --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID

aws ec2 associate-route-table --route-table-id $PUBLIC_RT --subnet-id $PUBLIC_SUBNET_1
aws ec2 associate-route-table --route-table-id $PUBLIC_RT --subnet-id $PUBLIC_SUBNET_2

# Private route table
PRIVATE_RT=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=private-rt}]' \
  --query 'RouteTable.RouteTableId' --output text)

aws ec2 create-route --route-table-id $PRIVATE_RT --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $NAT_GW_ID

aws ec2 associate-route-table --route-table-id $PRIVATE_RT --subnet-id $PRIVATE_SUBNET_1
aws ec2 associate-route-table --route-table-id $PRIVATE_RT --subnet-id $PRIVATE_SUBNET_2

echo "VPC Setup Complete!"
echo "VPC ID: $VPC_ID"
echo "Public Subnets: $PUBLIC_SUBNET_1, $PUBLIC_SUBNET_2"
echo "Private Subnets: $PRIVATE_SUBNET_1, $PRIVATE_SUBNET_2"
```

### Exercise 2: Test Connectivity

**Objective:** Verify public and private subnet connectivity

```bash
# Launch instance in public subnet
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.micro \
  --subnet-id $PUBLIC_SUBNET_1 \
  --security-group-ids $SG_ID \
  --key-name my-key \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=public-test}]'

# Launch instance in private subnet
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.micro \
  --subnet-id $PRIVATE_SUBNET_1 \
  --security-group-ids $SG_ID \
  --key-name my-key \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=private-test}]'

# Test from public instance
ssh -i my-key.pem ec2-user@<public-ip>
ping -c 4 8.8.8.8  # Should work (internet via IGW)

# Test from private instance (via bastion/SSM)
# SSH from public to private or use Session Manager
ping -c 4 8.8.8.8  # Should work (internet via NAT)
curl https://www.amazon.com  # Should work
```

### Exercise 3: VPC Flow Logs

**Objective:** Enable VPC Flow Logs for monitoring

```bash
# Create CloudWatch log group
aws logs create-log-group \
  --log-group-name /aws/vpc/flowlogs

# Create IAM role for Flow Logs
cat > flow-logs-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "vpc-flow-logs.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

ROLE_ARN=$(aws iam create-role \
  --role-name VPCFlowLogsRole \
  --assume-role-policy-document file://flow-logs-trust-policy.json \
  --query 'Role.Arn' --output text)

# Attach policy
aws iam put-role-policy \
  --role-name VPCFlowLogsRole \
  --policy-name VPCFlowLogsPolicy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ],
      "Resource": "*"
    }]
  }'

# Enable Flow Logs
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids $VPC_ID \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/flowlogs \
  --deliver-logs-permission-arn $ROLE_ARN

# Query Flow Logs
aws logs tail /aws/vpc/flowlogs --follow
```

---

## Validation Checklist

- [ ] VPC created with appropriate CIDR
- [ ] Public and private subnets in multiple AZs
- [ ] Internet Gateway attached
- [ ] NAT Gateway created in public subnet
- [ ] Route tables configured correctly
- [ ] Security groups configured
- [ ] Network ACLs understood
- [ ] VPC peering tested (if applicable)
- [ ] VPC endpoints created for S3
- [ ] Connectivity verified from both subnet types

---

## Troubleshooting

### Cannot Access Internet from Public Subnet

```bash
# Check: IGW attached?
aws ec2 describe-internet-gateways \
  --filters "Name=attachment.vpc-id,Values=$VPC_ID"

# Check: Route to IGW exists?
aws ec2 describe-route-tables \
  --filters "Name=association.subnet-id,Values=$PUBLIC_SUBNET_1"

# Check: Public IP assigned?
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress'

# Check: Security group allows traffic?
aws ec2 describe-security-groups --group-ids $SG_ID
```

### Cannot Access Internet from Private Subnet

```bash
# Check: NAT Gateway exists and available?
aws ec2 describe-nat-gateways \
  --filter "Name=vpc-id,Values=$VPC_ID"

# Check: Route to NAT Gateway?
aws ec2 describe-route-tables \
  --filters "Name=association.subnet-id,Values=$PRIVATE_SUBNET_1"

# Check: NAT in public subnet with IGW route?
# NAT needs internet access itself
```

---

## Best Practices

```yaml
CIDR Planning:
  - Plan for growth
  - Avoid overlaps with on-prem
  - Use /16 for production VPCs
  - Reserve space for future subnets

High Availability:
  - Multi-AZ subnets
  - NAT Gateway per AZ
  - Distribute resources across AZs

Security:
  - Private subnets for databases/apps
  - Public subnets only for load balancers
  - Security groups over NACLs
  - VPC Flow Logs enabled
  - VPC endpoints for AWS services

Cost Optimization:
  - Use VPC endpoints (avoid NAT costs)
  - Right-size NAT Gateways
  - Delete unused resources
  - Consider NAT instances for dev/test
```

---

## Next Steps

Now that you understand VPC networking:
1. ✓ VPC fundamentals mastered
2. ✓ Public and private subnets configured
3. ✓ Routing and connectivity understood
4. → **Next:** Load Balancers and traffic distribution (Chapter 7)
5. → Auto Scaling for dynamic capacity (Chapter 8)

---

## Additional Resources

- [VPC User Guide](https://docs.aws.amazon.com/vpc/)
- [VPC Peering Guide](https://docs.aws.amazon.com/vpc/latest/peering/)
- [VPC Endpoints Guide](https://docs.aws.amazon.com/vpc/latest/privatelink/)
- [VPC Best Practices](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html)
