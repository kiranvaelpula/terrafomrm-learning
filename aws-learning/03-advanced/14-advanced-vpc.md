# Chapter 14: Advanced VPC - VPC Peering, PrivateLink, Transit Gateway

## Overview

Advanced VPC networking enables complex architectures with multiple VPCs, hybrid cloud connectivity, and sophisticated traffic routing. This chapter covers enterprise-grade networking patterns for large-scale AWS deployments.

**What You'll Learn**
- VPC Peering for VPC-to-VPC communication
- AWS PrivateLink for private service access
- AWS Transit Gateway for hub-and-spoke architecture
- VPC Endpoints for AWS service access
- Advanced routing strategies
- Multi-account networking

**Prerequisites**
- Strong understanding of VPC basics
- Familiarity with routing and subnets
- Experience with security groups and NACLs
- Understanding of CIDR notation

---

## VPC Peering

### What is VPC Peering?

VPC Peering connects two VPCs privately using AWS's network backbone, allowing resources to communicate using private IP addresses.

**Architecture:**
```
VPC A (10.0.0.0/16)     VPC B (172.16.0.0/16)
      |                       |
      +--Peering Connection---+
      |                       |
  EC2 (10.0.1.10) ←→ EC2 (172.16.1.20)
```

### Creating VPC Peering

**Step 1: Create Peering Connection**
```bash
# Requester side (VPC A)
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-11111111 \
  --peer-vpc-id vpc-22222222 \
  --peer-region us-west-2 \
  --tag-specifications 'ResourceType=vpc-peering-connection,Tags=[{Key=Name,Value=VPC-A-to-B}]'
```

**Step 2: Accept Peering Connection**
```bash
# Accepter side (VPC B)
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id pcx-12345678
```


**Step 3: Update Route Tables**
```bash
# VPC A route table - add route to VPC B
aws ec2 create-route \
  --route-table-id rtb-aaaaaaaa \
  --destination-cidr-block 172.16.0.0/16 \
  --vpc-peering-connection-id pcx-12345678

# VPC B route table - add route to VPC A
aws ec2 create-route \
  --route-table-id rtb-bbbbbbbb \
  --destination-cidr-block 10.0.0.0/16 \
  --vpc-peering-connection-id pcx-12345678
```

**Step 4: Update Security Groups**
```bash
# Allow traffic from peered VPC
aws ec2 authorize-security-group-ingress \
  --group-id sg-aaaaaaaa \
  --protocol tcp \
  --port 443 \
  --cidr 172.16.0.0/16
```

### VPC Peering Limitations

**1. No Transitive Peering**
```
VPC A ←→ VPC B ←→ VPC C
   ✗ A cannot reach C through B

Solution: Direct peering or Transit Gateway
VPC A ←→ VPC C (direct peering)
```

**2. No Overlapping CIDR Blocks**
```
❌ Cannot Peer:
VPC A: 10.0.0.0/16
VPC B: 10.0.0.0/16

✅ Can Peer:
VPC A: 10.0.0.0/16
VPC B: 172.16.0.0/16
```

**3. No Edge-to-Edge Routing**
```
❌ Cannot route through peered VPC to:
- Internet Gateway
- VPN Gateway
- Direct Connect Gateway
- NAT Gateway

Each VPC needs its own connectivity
```

### Cross-Region VPC Peering

```bash
# Peer VPCs in different regions
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-us-east-1 \
  --peer-vpc-id vpc-eu-west-1 \
  --peer-region eu-west-1 \
  --peer-owner-id 123456789012

# Data transfer costs apply for cross-region
```

### Cross-Account VPC Peering

```bash
# Account A creates request
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-aaaaaaaa \
  --peer-vpc-id vpc-bbbbbbbb \
  --peer-owner-id 987654321098 \
  --peer-region us-east-1

# Account B accepts
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id pcx-12345678
```


---

## AWS Transit Gateway

### What is Transit Gateway?

Transit Gateway acts as a network hub that connects VPCs, VPNs, and Direct Connect gateways in a hub-and-spoke architecture.

**Architecture:**
```
                Transit Gateway
                       |
        +--------------+--------------+
        |              |              |
    VPC A          VPC B          VPC C
        |              |              |
   10.0.0.0/16   172.16.0.0/16  192.168.0.0/16
        |
    VPN Gateway ← On-Premises
```

**Benefits:**
- ✅ Simplifies network topology
- ✅ Supports transitive routing
- ✅ Scales to thousands of VPCs
- ✅ Centralized routing policies
- ✅ Inter-region peering

### Creating Transit Gateway

**Step 1: Create Transit Gateway**
```bash
aws ec2 create-transit-gateway \
  --description "Main Transit Gateway" \
  --options \
    AmazonSideAsn=64512,\
    DefaultRouteTableAssociation=enable,\
    DefaultRouteTablePropagation=enable,\
    DnsSupport=enable,\
    VpnEcmpSupport=enable \
  --tag-specifications 'ResourceType=transit-gateway,Tags=[{Key=Name,Value=MainTGW}]'
```

**Step 2: Attach VPCs**
```bash
# Attach VPC A
aws ec2 create-transit-gateway-vpc-attachment \
  --transit-gateway-id tgw-12345678 \
  --vpc-id vpc-aaaaaaaa \
  --subnet-ids subnet-11111111 subnet-22222222 \
  --tag-specifications 'ResourceType=transit-gateway-attachment,Tags=[{Key=Name,Value=VPC-A-Attachment}]'

# Attach VPC B
aws ec2 create-transit-gateway-vpc-attachment \
  --transit-gateway-id tgw-12345678 \
  --vpc-id vpc-bbbbbbbb \
  --subnet-ids subnet-33333333 subnet-44444444
```

**Step 3: Update VPC Route Tables**
```bash
# VPC A - Route to other VPCs through TGW
aws ec2 create-route \
  --route-table-id rtb-aaaaaaaa \
  --destination-cidr-block 172.16.0.0/16 \
  --transit-gateway-id tgw-12345678

aws ec2 create-route \
  --route-table-id rtb-aaaaaaaa \
  --destination-cidr-block 192.168.0.0/16 \
  --transit-gateway-id tgw-12345678
```

### Transit Gateway Route Tables

**Create Isolated Routing Domains:**
```bash
# Production route table
aws ec2 create-transit-gateway-route-table \
  --transit-gateway-id tgw-12345678 \
  --tag-specifications 'ResourceType=transit-gateway-route-table,Tags=[{Key=Name,Value=Production}]'

# Development route table
aws ec2 create-transit-gateway-route-table \
  --transit-gateway-id tgw-12345678 \
  --tag-specifications 'ResourceType=transit-gateway-route-table,Tags=[{Key=Name,Value=Development}]'

# Associate VPCs with route tables
aws ec2 associate-transit-gateway-route-table \
  --transit-gateway-route-table-id tgw-rtb-prod \
  --transit-gateway-attachment-id tgw-attach-prod-vpc

# Propagate routes
aws ec2 enable-transit-gateway-route-table-propagation \
  --transit-gateway-route-table-id tgw-rtb-prod \
  --transit-gateway-attachment-id tgw-attach-shared-services
```


### Transit Gateway Peering

Connect Transit Gateways across regions:

```bash
# Region 1: Create peering attachment
aws ec2 create-transit-gateway-peering-attachment \
  --transit-gateway-id tgw-us-east-1 \
  --peer-transit-gateway-id tgw-eu-west-1 \
  --peer-account-id 123456789012 \
  --peer-region eu-west-1

# Region 2: Accept peering
aws ec2 accept-transit-gateway-peering-attachment \
  --transit-gateway-attachment-id tgw-attach-12345678 \
  --region eu-west-1
```

### Use Case: Centralized Egress

```
              Transit Gateway
                     |
    +----------------+----------------+
    |                |                |
VPC A            VPC B          Egress VPC
(No NAT)       (No NAT)        (NAT Gateway)
    |                |                |
    +----------------+                |
                     |                |
                     +--------→ Internet
```

**Configuration:**
```bash
# Route all internet traffic through Egress VPC
aws ec2 create-route \
  --route-table-id rtb-vpc-a \
  --destination-cidr-block 0.0.0.0/0 \
  --transit-gateway-id tgw-12345678

# Egress VPC handles NAT for all VPCs
# Cost savings: Single NAT Gateway vs multiple
```

---

## AWS PrivateLink

### What is PrivateLink?

PrivateLink provides private connectivity between VPCs and AWS services or your own services without exposing traffic to the internet.

**Architecture:**
```
Service Provider VPC          Service Consumer VPC
       |                              |
   NLB → VPC Endpoint Service    VPC Endpoint
       |                              |
       +--------Private Link----------+
```

**Benefits:**
- ✅ Traffic stays on AWS network
- ✅ No VPC peering needed
- ✅ Scales automatically
- ✅ Simplified security (no security groups needed)
- ✅ Works across accounts/regions

### Creating PrivateLink Service

**Provider Side:**

**Step 1: Create Network Load Balancer**
```bash
aws elbv2 create-load-balancer \
  --name my-service-nlb \
  --type network \
  --subnets subnet-11111111 subnet-22222222 \
  --scheme internal
```

**Step 2: Create VPC Endpoint Service**
```bash
aws ec2 create-vpc-endpoint-service-configuration \
  --network-load-balancer-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/my-service-nlb/xyz \
  --acceptance-required \
  --tag-specifications 'ResourceType=vpc-endpoint-service,Tags=[{Key=Name,Value=MyService}]'

# Note the service name: com.amazonaws.vpce.us-east-1.vpce-svc-12345678
```

**Step 3: Allow Consumer Accounts**
```bash
aws ec2 modify-vpc-endpoint-service-permissions \
  --service-id vpce-svc-12345678 \
  --add-allowed-principals arn:aws:iam::987654321098:root
```

**Consumer Side:**

**Step 4: Create VPC Endpoint**
```bash
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-consumer \
  --vpc-endpoint-type Interface \
  --service-name com.amazonaws.vpce.us-east-1.vpce-svc-12345678 \
  --subnet-ids subnet-aaaaaaaa subnet-bbbbbbbb \
  --security-group-ids sg-consumer
```


**Step 5: Accept Connection Request**
```bash
# Provider accepts consumer's connection
aws ec2 accept-vpc-endpoint-connections \
  --service-id vpce-svc-12345678 \
  --vpc-endpoint-ids vpce-87654321
```

### VPC Endpoints for AWS Services

**Interface Endpoints (PrivateLink)**

Access AWS services privately without internet gateway:

```bash
# Create endpoint for S3
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-12345678 \
  --vpc-endpoint-type Interface \
  --service-name com.amazonaws.us-east-1.s3 \
  --subnet-ids subnet-11111111 subnet-22222222 \
  --security-group-ids sg-12345678

# Supported services:
# - S3, DynamoDB, SQS, SNS, Lambda, ECS, ECR
# - KMS, Secrets Manager, Systems Manager
# - CloudWatch, CloudFormation, API Gateway
# - And many more...
```

**Gateway Endpoints (Free)**

For S3 and DynamoDB only:

```bash
# Create gateway endpoint for S3
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-12345678 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-aaaaaaaa rtb-bbbbbbbb \
  --vpc-endpoint-type Gateway

# No additional charges
# Automatically updates route tables
```

**Endpoint Policies:**

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

---

## Advanced Routing Patterns

### Routing Priority

**Route table evaluation order:**
```
1. Most specific route wins
2. Local routes always preferred
3. Propagated routes (TGW, VGW)
4. Static routes

Example:
10.0.0.0/8 → TGW
10.0.1.0/24 → NAT Gateway  ← This wins for 10.0.1.x traffic
```

### Blackhole Routes

Explicitly drop traffic:

```bash
aws ec2 create-route \
  --route-table-id rtb-12345678 \
  --destination-cidr-block 192.168.100.0/24 \
  --blackhole

# Use cases:
# - Block specific networks
# - Prevent accidental routing
# - Security isolation
```

### Prefix Lists

Manage CIDR blocks as groups:

```bash
# Create managed prefix list
aws ec2 create-managed-prefix-list \
  --prefix-list-name prod-networks \
  --entries Cidr=10.0.0.0/16,Description=VPC-A \
            Cidr=172.16.0.0/16,Description=VPC-B \
  --max-entries 10 \
  --address-family IPv4

# Use in route table
aws ec2 create-route \
  --route-table-id rtb-12345678 \
  --destination-prefix-list-id pl-12345678 \
  --transit-gateway-id tgw-12345678

# Use in security group
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --ip-permissions IpProtocol=tcp,FromPort=443,ToPort=443,PrefixListIds=[{PrefixListId=pl-12345678}]
```


---

## Multi-Account Networking

### Hub-and-Spoke with Transit Gateway

**Architecture:**
```
                    Network Account
                   (Transit Gateway)
                          |
        +-----------------+-----------------+
        |                 |                 |
  Production          Staging           Development
   Account            Account             Account
   (VPC A)            (VPC B)             (VPC C)
```

**Setup:**

**1. Share Transit Gateway (Network Account)**
```bash
# Create Resource Share
aws ram create-resource-share \
  --name transit-gateway-share \
  --resource-arns arn:aws:ec2:us-east-1:111111111111:transit-gateway/tgw-12345678 \
  --principals \
    arn:aws:organizations::111111111111:ou/o-abc123/ou-prod-xyz \
    arn:aws:organizations::111111111111:ou/o-abc123/ou-dev-xyz
```

**2. Accept Share (Member Accounts)**
```bash
aws ram accept-resource-share-invitation \
  --resource-share-invitation-arn arn:aws:ram:us-east-1:111111111111:resource-share-invitation/xyz
```

**3. Attach VPCs (Member Accounts)**
```bash
aws ec2 create-transit-gateway-vpc-attachment \
  --transit-gateway-id tgw-12345678 \
  --vpc-id vpc-member-account \
  --subnet-ids subnet-11111111 subnet-22222222
```

### Shared Services VPC

Common pattern for centralized services:

```
          Transit Gateway
                 |
    +------------+------------+
    |            |            |
App VPC    Shared Svcs    Data VPC
    |            |            |
    |     +------+------+     |
    |     |             |     |
    | DNS Server  Active Dir  |
    | Monitoring    Logging   |
    +-------------------------+
```

**Configuration:**
```bash
# Shared Services VPC can reach all VPCs
# App VPCs can only reach Shared Services
# Data VPCs isolated from App VPCs

# Transit Gateway route table for App VPC
aws ec2 create-transit-gateway-route \
  --transit-gateway-route-table-id tgw-rtb-apps \
  --destination-cidr-block 10.100.0.0/16 \
  --transit-gateway-attachment-id tgw-attach-shared-services
```

---

## VPC Flow Logs Analysis

### Enable Enhanced Flow Logs

```bash
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-12345678 \
  --traffic-type ALL \
  --log-destination-type s3 \
  --log-destination arn:aws:s3:::my-flow-logs-bucket \
  --log-format '${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${packets} ${bytes} ${start} ${end} ${action} ${log-status} ${vpc-id} ${subnet-id} ${instance-id} ${tcp-flags} ${type} ${pkt-srcaddr} ${pkt-dstaddr}'
```

### Analyze Traffic Patterns

**CloudWatch Insights Query:**
```sql
fields @timestamp, srcAddr, dstAddr, srcPort, dstPort, action
| filter action = "REJECT"
| stats count() by srcAddr
| sort count desc
| limit 20
```

**Athena Query for S3 Logs:**
```sql
SELECT 
  srcaddr,
  dstaddr,
  SUM(bytes) as total_bytes
FROM vpc_flow_logs
WHERE action = 'ACCEPT'
  AND date = '2026-01-15'
GROUP BY srcaddr, dstaddr
ORDER BY total_bytes DESC
LIMIT 100;
```

---

## Network Troubleshooting

### VPC Reachability Analyzer

Test connectivity between source and destination:

```bash
# Create analysis path
aws ec2 create-network-insights-path \
  --source i-source-instance \
  --destination i-destination-instance \
  --protocol tcp \
  --destination-port 443

# Run analysis
aws ec2 start-network-insights-analysis \
  --network-insights-path-id nip-12345678

# Get results
aws ec2 describe-network-insights-analyses \
  --network-insights-analysis-ids nia-12345678
```

**Results show:**
- Security group rules blocking traffic
- NACL rules denying packets  
- Route table misconfiguration
- Missing IGW/NAT Gateway
- Blackhole routes


### VPC Traffic Mirroring

Capture and inspect network traffic:

```bash
# Create mirror target (NLB or ENI)
aws ec2 create-traffic-mirror-target \
  --network-load-balancer-arn arn:aws:elasticloadbalancing:... \
  --description "Security analysis target"

# Create mirror filter
aws ec2 create-traffic-mirror-filter \
  --description "Capture all traffic"

# Add filter rules
aws ec2 create-traffic-mirror-filter-rule \
  --traffic-mirror-filter-id tmf-12345678 \
  --traffic-direction ingress \
  --rule-number 100 \
  --rule-action accept \
  --destination-cidr-block 0.0.0.0/0 \
  --source-cidr-block 0.0.0.0/0

# Create mirror session
aws ec2 create-traffic-mirror-session \
  --network-interface-id eni-source \
  --traffic-mirror-target-id tmt-12345678 \
  --traffic-mirror-filter-id tmf-12345678 \
  --session-number 1
```

**Use Cases:**
- Security monitoring
- Intrusion detection
- Network forensics
- Compliance auditing

---

## Cost Optimization

### Data Transfer Costs

**VPC Peering:**
```
Same AZ: $0.01/GB
Different AZ: $0.01/GB each direction
Different Region: $0.02/GB
```

**Transit Gateway:**
```
Attachment: $0.05/hour per attachment
Data Processing: $0.02/GB
Inter-region: Additional $0.02/GB
```

**PrivateLink:**
```
VPC Endpoint: $0.01/hour
Data Processed: $0.01/GB
```

**Gateway Endpoints (S3/DynamoDB):**
```
FREE - No charges
```

### Optimization Strategies

**1. Use Gateway Endpoints when possible**
```bash
# FREE for S3 and DynamoDB
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-12345678 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-12345678 \
  --vpc-endpoint-type Gateway
```

**2. Consolidate VPCs with Transit Gateway**
```
Instead of: N*(N-1)/2 peering connections
Use: N Transit Gateway attachments

Example: 10 VPCs
Peering: 45 connections
TGW: 10 attachments
```

**3. Use Same-AZ Communication**
```
Deploy related resources in same AZ
Reduces data transfer costs
```

---

## Best Practices

### Network Architecture

**1. Plan CIDR Ranges Carefully**
```yaml
Production:
  VPC A: 10.0.0.0/16
  VPC B: 10.1.0.0/16
  VPC C: 10.2.0.0/16

Staging:
  VPC A: 172.16.0.0/16
  VPC B: 172.17.0.0/16

Development:
  VPC A: 192.168.0.0/16
```

**2. Use Transit Gateway for Scalability**
- More than 3-4 VPCs → Use Transit Gateway
- Complex routing → Use TGW route tables
- Hybrid connectivity → Single VPN/DX to TGW

**3. Implement Defense in Depth**
```
Layer 1: Security Groups (stateful)
Layer 2: NACLs (stateless)
Layer 3: AWS WAF (application layer)
Layer 4: VPC Flow Logs (monitoring)
Layer 5: Traffic Mirroring (deep inspection)
```

**4. Use PrivateLink for Service Access**
```
Benefits:
- No VPC peering needed
- Scales automatically
- Simplified security
- Cross-account/region support
```

### Security Best Practices

**1. Enable VPC Flow Logs**
```bash
# Enable on all VPCs
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-12345678 \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/flowlogs
```

**2. Use Private Subnets by Default**
```
Public: Only ALBs, bastion hosts
Private: Applications, databases
Isolated: Databases (no internet access)
```

**3. Implement Network Segmentation**
```
Separate VPCs for:
- Production
- Staging
- Development
- Management/Shared Services
```


---

## Hands-On Exercise

### Task: Build Multi-VPC Architecture with Transit Gateway

**Scenario:** Create three VPCs (Production, Shared Services, Development) connected via Transit Gateway with isolated routing.

**Step 1: Create VPCs**
```bash
# Production VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=Production}]'

# Shared Services VPC
aws ec2 create-vpc --cidr-block 10.100.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=SharedServices}]'

# Development VPC  
aws ec2 create-vpc --cidr-block 10.200.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=Development}]'
```

**Step 2: Create Transit Gateway**
```bash
aws ec2 create-transit-gateway \
  --description "Central Hub TGW" \
  --options \
    DefaultRouteTableAssociation=disable,\
    DefaultRouteTablePropagation=disable \
  --tag-specifications 'ResourceType=transit-gateway,Tags=[{Key=Name,Value=CentralTGW}]'
```

**Step 3: Create TGW Route Tables**
```bash
# Production route table (can only reach Shared Services)
aws ec2 create-transit-gateway-route-table \
  --transit-gateway-id tgw-xxx \
  --tag-specifications 'ResourceType=transit-gateway-route-table,Tags=[{Key=Name,Value=Production-RT}]'

# Development route table (can reach Shared Services and Production)
aws ec2 create-transit-gateway-route-table \
  --transit-gateway-id tgw-xxx \
  --tag-specifications 'ResourceType=transit-gateway-route-table,Tags=[{Key=Name,Value=Development-RT}]'

# Shared Services route table (can reach all)
aws ec2 create-transit-gateway-route-table \
  --transit-gateway-id tgw-xxx \
  --tag-specifications 'ResourceType=transit-gateway-route-table,Tags=[{Key=Name,Value=SharedServices-RT}]'
```

**Step 4: Attach VPCs to Transit Gateway**
```bash
# Attach each VPC
aws ec2 create-transit-gateway-vpc-attachment \
  --transit-gateway-id tgw-xxx \
  --vpc-id vpc-production \
  --subnet-ids subnet-prod-1 subnet-prod-2

# Repeat for other VPCs
```

**Step 5: Configure Routing**
```bash
# Production can only reach Shared Services
aws ec2 create-transit-gateway-route \
  --transit-gateway-route-table-id tgw-rtb-prod \
  --destination-cidr-block 10.100.0.0/16 \
  --transit-gateway-attachment-id tgw-attach-shared

# Development can reach both
aws ec2 create-transit-gateway-route \
  --transit-gateway-route-table-id tgw-rtb-dev \
  --destination-cidr-block 10.0.0.0/16 \
  --transit-gateway-attachment-id tgw-attach-prod

aws ec2 create-transit-gateway-route \
  --transit-gateway-route-table-id tgw-rtb-dev \
  --destination-cidr-block 10.100.0.0/16 \
  --transit-gateway-attachment-id tgw-attach-shared
```

**Step 6: Test Connectivity**
```bash
# From Production EC2: Can reach Shared Services
ping 10.100.1.10  # ✅ Success

# From Production EC2: Cannot reach Development
ping 10.200.1.10  # ❌ Timeout (no route)

# From Development EC2: Can reach Production
ping 10.0.1.10    # ✅ Success
```

---

## Summary

**Key Takeaways:**
- VPC Peering for simple VPC-to-VPC connectivity
- Transit Gateway for hub-and-spoke at scale
- PrivateLink for private service access
- VPC Endpoints reduce internet gateway dependency
- Advanced routing enables complex topologies
- Network segmentation improves security
- Cost optimization through proper architecture

**When to Use:**

| Solution | Use Case |
|----------|----------|
| **VPC Peering** | 2-3 VPCs, simple connectivity |
| **Transit Gateway** | 4+ VPCs, hybrid cloud, complex routing |
| **PrivateLink** | Service exposure, cross-account access |
| **Gateway Endpoints** | S3/DynamoDB access (FREE) |
| **Interface Endpoints** | Private AWS service access |

**Next Steps:**
- Implement Transit Gateway for your organization
- Set up PrivateLink for internal services
- Enable VPC Flow Logs for all VPCs
- Practice with Reachability Analyzer
- Design multi-account network architecture

---

## Additional Resources

**Official Documentation:**
- [VPC Peering Guide](https://docs.aws.amazon.com/vpc/latest/peering/)
- [Transit Gateway Guide](https://docs.aws.amazon.com/vpc/latest/tgw/)
- [PrivateLink Guide](https://docs.aws.amazon.com/vpc/latest/privatelink/)
- [VPC Endpoints](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-endpoints.html)

**Tools:**
- VPC Reachability Analyzer
- Transit Gateway Network Manager
- CloudWatch VPC Flow Logs
- AWS Network Firewall

**Next Chapter:** [15-organizations-control-tower.md](./15-organizations-control-tower.md) - Multi-account governance

