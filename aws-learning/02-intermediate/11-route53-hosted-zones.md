# Amazon Route 53 and Hosted Zones

## Introduction

Amazon Route 53 is a highly available and scalable Domain Name System (DNS) web service. It connects user requests to infrastructure running on AWS and can route users to infrastructure outside of AWS. This chapter covers DNS fundamentals, hosted zones, routing policies, and health checks.

## Table of Contents
- [What is Route 53?](#what-is-route-53)
- [DNS Fundamentals](#dns-fundamentals)
- [Hosted Zones](#hosted-zones)
- [Record Types](#record-types)
- [Routing Policies](#routing-policies)
- [Health Checks](#health-checks)
- [Traffic Flow](#traffic-flow)
- [Integration with AWS Services](#integration-with-aws-services)
- [Hands-on Exercises](#hands-on-exercises)

---

## What is Route 53?

### Overview

```yaml
Route 53 is:
  - Fully managed DNS service
  - Domain registration
  - Health checking
  - Traffic management
  - 100% availability SLA
  
Key Features:
  - Global Anycast network
  - Low latency DNS queries
  - Multiple routing policies
  - DNSSEC support
  - Integration with AWS services
  - Domain registration and transfer
```

### Why "Route 53"?

```
Port 53 is the standard DNS port
Route → DNS routing
53 → DNS protocol port number
```

###Use Cases

```yaml
Domain Management:
  - Register new domains
  - Transfer existing domains
  - Auto-renew domains
  - Domain privacy protection
  
DNS Routing:
  - Simple routing to resources
  - Geographic load distribution
  - Failover for disaster recovery
  - Weighted traffic distribution
  
Traffic Management:
  - Blue/green deployments
  - A/B testing
  - Multi-region failover
  - Latency-based routing
  
Health Monitoring:
  - Endpoint health checks
  - CloudWatch alarms
  - Automatic failover
```

---

## DNS Fundamentals

### How DNS Works

```
User Request Flow:
┌──────────┐
│  User    │
│  Browser │
└────┬─────┘
     │ 1. Query: www.example.com
     ▼
┌────────────┐
│  DNS       │
│  Resolver  │  (ISP or 8.8.8.8)
└────┬───────┘
     │ 2. Recursive query
     ▼
┌────────────┐
│  Root      │  
│  Server    │  → .com TLD Server → example.com NS
└────┬───────┘
     │ 3. Authoritative answer
     ▼
┌────────────┐
│  Route 53  │
│  Name      │  Returns: 203.0.113.25
│  Server    │
└────┬───────┘
     │ 4. IP Address
     ▼
┌────────────┐
│  User      │  Connects to 203.0.113.25
│  Browser   │
└────────────┘
```

### DNS Record Components

```yaml
Record Structure:
  Name: www.example.com
  Type: A (Address record)
  Value: 203.0.113.25
  TTL: 300 (seconds)
  
TTL (Time To Live):
  - How long record is cached
  - Lower TTL = more queries, faster updates
  - Higher TTL = fewer queries, slower updates
  - Typical: 300-3600 seconds
```

---

## Hosted Zones

### What is a Hosted Zone?

```yaml
Hosted Zone:
  - Container for DNS records
  - Represents a domain or subdomain
  - Two types: Public and Private
  - Has 4 Route 53 name servers
  - Costs $0.50/month per zone
```

### Public Hosted Zone

```yaml
Public Hosted Zone:
  Purpose: Internet-facing domains
  Accessible: From anywhere on internet
  Use Cases:
    - Public websites
    - Public APIs
    - Email servers
    - CDN origins
```

**Create Public Hosted Zone:**
```bash
# Create hosted zone
aws route53 create-hosted-zone \
    --name example.com \
    --caller-reference $(date +%s) \
    --hosted-zone-config Comment="Primary domain for example.com"

# Get name servers
aws route53 get-hosted-zone \
    --id Z1234567890ABC \
    --query 'DelegationSet.NameServers'

# Output:
# [
#     "ns-123.awsdns-12.com",
#     "ns-456.awsdns-45.net",
#     "ns-789.awsdns-78.org",
#     "ns-012.awsdns-01.co.uk"
# ]

# Update domain registrar with these name servers
```

### Private Hosted Zone

```yaml
Private Hosted Zone:
  Purpose: Internal DNS resolution
  Accessible: Only from associated VPCs
  Use Cases:
    - Internal APIs
    - Database endpoints
    - Microservices communication
    - Private subdomains
```

**Create Private Hosted Zone:**
```bash
# Create private hosted zone
aws route53 create-hosted-zone \
    --name internal.example.com \
    --vpc VPCRegion=us-east-1,VPCId=vpc-0123456789abcdef0 \
    --caller-reference $(date +%s) \
    --hosted-zone-config Comment="Private zone for internal services",PrivateZone=true

# Associate additional VPC
aws route53 associate-vpc-with-hosted-zone \
    --hosted-zone-id Z0987654321XYZ \
    --vpc VPCRegion=us-west-2,VPCId=vpc-0fedcba9876543210

# List associations
aws route53 list-vpc-association-authorizations \
    --hosted-zone-id Z0987654321XYZ
```

###Split-View DNS

```yaml
Split-View (Split-Horizon) DNS:
  - Same domain name in public and private zones
  - Different records for internal vs external
  - Internal users get private IPs
  - External users get public IPs
  
Example:
  Public Zone (example.com):
    api.example.com → 203.0.113.25 (ALB public IP)
  
  Private Zone (example.com):
    api.example.com → 10.0.1.100 (Internal ALB)
```

---

## Record Types

### Common Record Types

**A Record (Address):**
```bash
# Map domain to IPv4 address
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "www.example.com",
                "Type": "A",
                "TTL": 300,
                "ResourceRecords": [{"Value": "203.0.113.25"}]
            }
        }]
    }'
```

**AAAA Record (IPv6):**
```bash
# Map domain to IPv6 address
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "www.example.com",
                "Type": "AAAA",
                "TTL": 300,
                "ResourceRecords": [{"Value": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"}]
            }
        }]
    }'
```

**CNAME Record (Canonical Name):**
```bash
# Alias for another domain
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "blog.example.com",
                "Type": "CNAME",
                "TTL": 300,
                "ResourceRecords": [{"Value": "example.wordpress.com"}]
            }
        }]
    }'

# Note: Cannot create CNAME for apex domain (example.com)
# Use Alias record instead
```

**MX Record (Mail Exchange):**
```bash
# Email server routing
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "example.com",
                "Type": "MX",
                "TTL": 300,
                "ResourceRecords": [
                    {"Value": "10 mail1.example.com"},
                    {"Value": "20 mail2.example.com"}
                ]
            }
        }]
    }'
```

**TXT Record:**
```bash
# Text records for verification, SPF, DKIM
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "example.com",
                "Type": "TXT",
                "TTL": 300,
                "ResourceRecords": [
                    {"Value": "\"v=spf1 include:_spf.google.com ~all\""},
                    {"Value": "\"google-site-verification=abc123xyz789\""}
                ]
            }
        }]
    }'
```

**NS Record (Name Server):**
```bash
# Delegate subdomain to different name servers
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "subdomain.example.com",
                "Type": "NS",
                "TTL": 172800,
                "ResourceRecords": [
                    {"Value": "ns1.subdomain-provider.com"},
                    {"Value": "ns2.subdomain-provider.com"}
                ]
            }
        }]
    }'
```

### Alias Records

```yaml
Alias vs CNAME:
  Alias:
    - Route 53 specific
    - Can use for apex domain
    - No charge for queries
    - Automatic health checks
    - Targets: ALB, CloudFront, S3, another record
  
  CNAME:
    - Standard DNS
    - Cannot use for apex domain
    - Charged for queries
    - No automatic health checks
    - Target: Any domain
```

**Create Alias Record:**
```bash
# Alias to Application Load Balancer
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "example.com",
                "Type": "A",
                "AliasTarget": {
                    "HostedZoneId": "Z35SXDOTRQ7X7K",
                    "DNSName": "my-alb-1234567890.us-east-1.elb.amazonaws.com",
                    "EvaluateTargetHealth": true
                }
            }
        }]
    }'

# Alias to CloudFront distribution
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "www.example.com",
                "Type": "A",
                "AliasTarget": {
                    "HostedZoneId": "Z2FDTNDATAQYW2",
                    "DNSName": "d123456789.cloudfront.net",
                    "EvaluateTargetHealth": false
                }
            }
        }]
    }'
```


---

## Routing Policies

### Simple Routing

```yaml
Simple Routing:
  - Single resource
  - Multiple IP addresses (random selection)
  - No health checks
  - Use case: Single web server or load balancer
```

```bash
# Simple routing with single IP
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "simple.example.com",
                "Type": "A",
                "TTL": 60,
                "ResourceRecords": [{"Value": "203.0.113.25"}]
            }
        }]
    }'

# Simple routing with multiple IPs (random selection)
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "multi.example.com",
                "Type": "A",
                "TTL": 60,
                "ResourceRecords": [
                    {"Value": "203.0.113.25"},
                    {"Value": "203.0.113.26"},
                    {"Value": "203.0.113.27"}
                ]
            }
        }]
    }'
```

### Weighted Routing

```yaml
Weighted Routing:
  - Distribute traffic by assigned weights
  - A/B testing
  - Gradual deployment
  - Can have health checks
  
Example:
  90% traffic to old version
  10% traffic to new version
```

```bash
# Create weighted records
# 90% to production
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "app.example.com",
                "Type": "A",
                "SetIdentifier": "Production",
                "Weight": 90,
                "TTL": 60,
                "ResourceRecords": [{"Value": "203.0.113.25"}]
            }
        }]
    }'

# 10% to canary
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "app.example.com",
                "Type": "A",
                "SetIdentifier": "Canary",
                "Weight": 10,
                "TTL": 60,
                "ResourceRecords": [{"Value": "203.0.113.26"}]
            }
        }]
    }'
```

### Latency-Based Routing

```yaml
Latency Routing:
  - Route to lowest latency region
  - Measure latency from user to AWS regions
  - Improves user experience
  - Automatically failover if unhealthy
```

```bash
# US East region
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "global.example.com",
                "Type": "A",
                "SetIdentifier": "US-East",
                "Region": "us-east-1",
                "TTL": 60,
                "ResourceRecords": [{"Value": "203.0.113.25"}],
                "HealthCheckId": "abc123-health-check"
            }
        }]
    }'

# EU West region
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "global.example.com",
                "Type": "A",
                "SetIdentifier": "EU-West",
                "Region": "eu-west-1",
                "TTL": 60,
                "ResourceRecords": [{"Value": "198.51.100.25"}],
                "HealthCheckId": "def456-health-check"
            }
        }]
    }'
```

### Failover Routing

```yaml
Failover Routing:
  - Active-passive failover
  - Primary and secondary resources
  - Health check on primary
  - Automatic failover to secondary
```

```bash
# Primary record
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "app.example.com",
                "Type": "A",
                "SetIdentifier": "Primary",
                "Failover": "PRIMARY",
                "TTL": 60,
                "ResourceRecords": [{"Value": "203.0.113.25"}],
                "HealthCheckId": "primary-health-check"
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
                "Name": "app.example.com",
                "Type": "A",
                "SetIdentifier": "Secondary",
                "Failover": "SECONDARY",
                "TTL": 60,
                "ResourceRecords": [{"Value": "198.51.100.25"}]
            }
        }]
    }'
```

### Geolocation Routing

```yaml
Geolocation Routing:
  - Route based on user's geographic location
  - Continent, country, or state level
  - Content localization
  - Compliance with data residency
  - Default location for no match
```

```bash
# North America traffic
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "www.example.com",
                "Type": "A",
                "SetIdentifier": "North-America",
                "GeoLocation": {"ContinentCode": "NA"},
                "TTL": 60,
                "ResourceRecords": [{"Value": "203.0.113.25"}]
            }
        }]
    }'

# Europe traffic
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "www.example.com",
                "Type": "A",
                "SetIdentifier": "Europe",
                "GeoLocation": {"ContinentCode": "EU"},
                "TTL": 60,
                "ResourceRecords": [{"Value": "198.51.100.25"}]
            }
        }]
    }'

# Default for rest of world
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "www.example.com",
                "Type": "A",
                "SetIdentifier": "Default",
                "GeoLocation": {"ContinentCode": "*"},
                "TTL": 60,
                "ResourceRecords": [{"Value": "192.0.2.25"}]
            }
        }]
    }'
```

### Geoproximity Routing

```yaml
Geoproximity Routing:
  - Route based on geographic location + bias
  - Bias: -99 to +99 (shift traffic toward/away)
  - More precise than geolocation
  - Requires Traffic Flow
```

### Multi-Value Answer Routing

```yaml
Multi-Value Answer:
  - Return multiple values (up to 8)
  - Each with health check
  - Simple load distribution
  - Like simple routing but with health checks
```

```bash
# Multi-value records
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "multivalue.example.com",
                "Type": "A",
                "SetIdentifier": "Server-1",
                "MultiValueAnswer": true,
                "TTL": 60,
                "ResourceRecords": [{"Value": "203.0.113.25"}],
                "HealthCheckId": "health-check-1"
            }
        }]
    }'

aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "multivalue.example.com",
                "Type": "A",
                "SetIdentifier": "Server-2",
                "MultiValueAnswer": true,
                "TTL": 60,
                "ResourceRecords": [{"Value": "203.0.113.26"}],
                "HealthCheckId": "health-check-2"
            }
        }]
    }'
```

---

## Health Checks

### Health Check Types

```yaml
Endpoint Health Checks:
  - Monitor an endpoint (IP or domain)
  - Protocol: HTTP, HTTPS, TCP
  - Port: Any port
  - Path: For HTTP/HTTPS
  - Frequency: 30s or 10s (Fast)
  
Calculated Health Checks:
  - Monitor status of other health checks
  - Logical AND, OR, NOT
  - Child health checks
  
CloudWatch Alarm Health Checks:
  - Based on CloudWatch alarm state
  - Monitor any CloudWatch metric
```

### Creating Health Checks

**HTTP Health Check:**
```bash
# Create HTTP health check
aws route53 create-health-check \
    --caller-reference $(date +%s) \
    --health-check-config '{
        "Type": "HTTP",
        "ResourcePath": "/health",
        "FullyQualifiedDomainName": "api.example.com",
        "Port": 80,
        "RequestInterval": 30,
        "FailureThreshold": 3
    }' \
    --health-check-tags Key=Name,Value="API Health Check"

# With string matching
aws route53 create-health-check \
    --caller-reference $(date +%s) \
    --health-check-config '{
        "Type": "HTTP",
        "ResourcePath": "/health",
        "FullyQualifiedDomainName": "api.example.com",
        "Port": 80,
        "RequestInterval": 30,
        "FailureThreshold": 3,
        "MeasureLatency": true,
        "EnableSNI": false,
        "SearchString": "\"status\":\"healthy\""
    }'
```

**HTTPS Health Check:**
```bash
# HTTPS health check
aws route53 create-health-check \
    --caller-reference $(date +%s) \
    --health-check-config '{
        "Type": "HTTPS",
        "ResourcePath": "/api/health",
        "FullyQualifiedDomainName": "secure.example.com",
        "Port": 443,
        "RequestInterval": 30,
        "FailureThreshold": 3,
        "EnableSNI": true
    }'
```

**TCP Health Check:**
```bash
# TCP health check (for non-HTTP services)
aws route53 create-health-check \
    --caller-reference $(date +%s) \
    --health-check-config '{
        "Type": "TCP",
        "IPAddress": "203.0.113.25",
        "Port": 3306,
        "RequestInterval": 30,
        "FailureThreshold": 3
    }'
```

**Calculated Health Check:**
```bash
# Calculated health check (monitors multiple child checks)
aws route53 create-health-check \
    --caller-reference $(date +%s) \
    --health-check-config '{
        "Type": "CALCULATED",
        "ChildHealthChecks": [
            "abc123-health-check-1",
            "def456-health-check-2",
            "ghi789-health-check-3"
        ],
        "HealthThreshold": 2
    }'
# Healthy if at least 2 out of 3 child checks are healthy
```

**CloudWatch Alarm Health Check:**
```bash
# Create CloudWatch alarm first
aws cloudwatch put-metric-alarm \
    --alarm-name high-cpu-alarm \
    --alarm-description "Alert when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2

# Create health check based on alarm
aws route53 create-health-check \
    --caller-reference $(date +%s) \
    --health-check-config '{
        "Type": "CLOUDWATCH_METRIC",
        "AlarmIdentifier": {
            "Region": "us-east-1",
            "Name": "high-cpu-alarm"
        },
        "InsufficientDataHealthStatus": "Healthy"
    }'
```

### Health Check Monitoring

```bash
# Get health check status
aws route53 get-health-check-status \
    --health-check-id abc123-health-check

# List all health checks
aws route53 list-health-checks

# Get health check details
aws route53 get-health-check \
    --health-check-id abc123-health-check
```

---

## Traffic Flow

### Traffic Flow Overview

```yaml
Traffic Flow:
  - Visual policy editor
  - Complex routing logic
  - Version control
  - Reusable templates
  - Geoproximity support
```

### Traffic Policy Example

```json
{
    "AWSPolicyFormatVersion": "2015-10-01",
    "RecordType": "A",
    "StartRule": "geolocation_rule",
    "Endpoints": {
        "us_east_endpoint": {
            "Type": "value",
            "Value": "203.0.113.25"
        },
        "eu_west_endpoint": {
            "Type": "value",
            "Value": "198.51.100.25"
        },
        "default_endpoint": {
            "Type": "value",
            "Value": "192.0.2.25"
        }
    },
    "Rules": {
        "geolocation_rule": {
            "RuleType": "geo",
            "GeoproximityLocation": [
                {
                    "EndpointReference": "us_east_endpoint",
                    "Region": "us-east-1",
                    "Bias": 0,
                    "EvaluateTargetHealth": true,
                    "HealthCheck": "health-check-us"
                },
                {
                    "EndpointReference": "eu_west_endpoint",
                    "Region": "eu-west-1",
                    "Bias": 0,
                    "EvaluateTargetHealth": true,
                    "HealthCheck": "health-check-eu"
                }
            ],
            "GeoproximityLocationDefault": {
                "EndpointReference": "default_endpoint",
                "EvaluateTargetHealth": false
            }
        }
    }
}
```

---

## Integration with AWS Services

### CloudFront Integration

```bash
# Create Alias record for CloudFront
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "cdn.example.com",
                "Type": "A",
                "AliasTarget": {
                    "HostedZoneId": "Z2FDTNDATAQYW2",
                    "DNSName": "d123456789.cloudfront.net",
                    "EvaluateTargetHealth": false
                }
            }
        }]
    }'
```

### Application Load Balancer Integration

```bash
# Get ALB hosted zone ID (varies by region)
# us-east-1: Z35SXDOTRQ7X7K
# us-west-2: Z1H1FL5HABSF5

# Create Alias record for ALB
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "app.example.com",
                "Type": "A",
                "AliasTarget": {
                    "HostedZoneId": "Z35SXDOTRQ7X7K",
                    "DNSName": "my-alb-123456.us-east-1.elb.amazonaws.com",
                    "EvaluateTargetHealth": true
                }
            }
        }]
    }'
```

### S3 Website Integration

```bash
# S3 website endpoint must match bucket name
# Bucket: www.example.com
# Endpoint: www.example.com.s3-website-us-east-1.amazonaws.com

# Create Alias record for S3 website
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "www.example.com",
                "Type": "A",
                "AliasTarget": {
                    "HostedZoneId": "Z3AQBSTGFYJSTF",
                    "DNSName": "s3-website-us-east-1.amazonaws.com",
                    "EvaluateTargetHealth": false
                }
            }
        }]
    }'
```

---

## Hands-on Exercises

### Exercise 1: Multi-Region Failover Setup

**Objective:** Configure active-passive failover between two regions

**Architecture:**
```
Primary (us-east-1) ──┐
                       ├─→ Route 53 Failover ─→ User
Secondary (us-west-2) ─┘
```

**Solution:**
```bash
# 1. Create health check for primary
PRIMARY_HC=$(aws route53 create-health-check \
    --caller-reference $(date +%s) \
    --health-check-config '{
        "Type": "HTTPS",
        "ResourcePath": "/health",
        "FullyQualifiedDomainName": "primary-alb.us-east-1.elb.amazonaws.com",
        "Port": 443,
        "RequestInterval": 30,
        "FailureThreshold": 3
    }' \
    --query 'HealthCheck.Id' \
    --output text)

# 2. Create primary failover record
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "app.example.com",
                "Type": "A",
                "SetIdentifier": "Primary-US-East",
                "Failover": "PRIMARY",
                "AliasTarget": {
                    "HostedZoneId": "Z35SXDOTRQ7X7K",
                    "DNSName": "primary-alb.us-east-1.elb.amazonaws.com",
                    "EvaluateTargetHealth": true
                },
                "HealthCheckId": "'$PRIMARY_HC'"
            }
        }]
    }'

# 3. Create secondary failover record
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "app.example.com",
                "Type": "A",
                "SetIdentifier": "Secondary-US-West",
                "Failover": "SECONDARY",
                "AliasTarget": {
                    "HostedZoneId": "Z1H1FL5HABSF5",
                    "DNSName": "secondary-alb.us-west-2.elb.amazonaws.com",
                    "EvaluateTargetHealth": false
                }
            }
        }]
    }'

# 4. Test failover
# Stop primary ALB or make health check fail
# Verify DNS resolves to secondary

# 5. Monitor health check
watch -n 5 'aws route53 get-health-check-status \
    --health-check-id '$PRIMARY_HC
```

### Exercise 2: Weighted Routing for Blue/Green Deployment

**Objective:** Gradually shift traffic from blue to green deployment

**Solution:**
```bash
# Initial: 100% blue, 0% green
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "api.example.com",
                    "Type": "A",
                    "SetIdentifier": "Blue",
                    "Weight": 100,
                    "TTL": 60,
                    "ResourceRecords": [{"Value": "203.0.113.25"}]
                }
            },
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "api.example.com",
                    "Type": "A",
                    "SetIdentifier": "Green",
                    "Weight": 0,
                    "TTL": 60,
                    "ResourceRecords": [{"Value": "203.0.113.26"}]
                }
            }
        ]
    }'

# Step 1: 90% blue, 10% green (canary)
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
        "Changes": [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": "api.example.com",
                    "Type": "A",
                    "SetIdentifier": "Blue",
                    "Weight": 90,
                    "TTL": 60,
                    "ResourceRecords": [{"Value": "203.0.113.25"}]
                }
            },
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": "api.example.com",
                    "Type": "A",
                    "SetIdentifier": "Green",
                    "Weight": 10,
                    "TTL": 60,
                    "ResourceRecords": [{"Value": "203.0.113.26"}]
                }
            }
        ]
    }'

# Step 2: 50% blue, 50% green
# Step 3: 0% blue, 100% green (complete migration)
```

---

## Best Practices

```yaml
Domain Management:
  - Enable auto-renewal
  - Enable transfer lock
  - Use domain privacy protection
  - Set up billing alerts

DNS Configuration:
  - Use short TTLs during migrations (60s)
  - Use longer TTLs for stable records (3600s)
  - Always have default/catch-all geolocation
  - Test DNS changes before production

Health Checks:
  - Monitor critical endpoints
  - Use calculated health checks for redundancy
  - Set appropriate failure thresholds
  - Configure CloudWatch alarms

High Availability:
  - Use multi-region deployments
  - Configure automatic failover
  - Test failover procedures regularly
  - Monitor Route 53 query metrics

Security:
  - Enable DNSSEC for domain security
  - Use Route 53 Resolver DNS Firewall
  - Implement least privilege IAM policies
  - Enable CloudTrail logging

Cost Optimization:
  - Delete unused hosted zones
  - Consolidate health checks
  - Use alias records (free queries)
  - Monitor query counts
```

---

## Summary

```yaml
Key Takeaways:
  - Route 53 provides managed DNS service
  - Hosted zones contain DNS records
  - Multiple routing policies for different use cases
  - Health checks enable automatic failover
  - Alias records for AWS resource integration
  - Traffic Flow for complex routing logic
  - Private hosted zones for internal DNS
  
Next Steps:
  - Register or transfer domain
  - Create hosted zones (public/private)
  - Configure routing policies
  - Set up health checks
  - Integrate with other AWS services
  - Test failover scenarios
```

**Related Topics:**
- Chapter 07: Load Balancers (ALB integration)
- Chapter 12: CloudWatch Monitoring
- Chapter 19: CloudFront CDN

---

**Resources:**
- [Route 53 Documentation](https://docs.aws.amazon.com/route53/)
- [Routing Policy Reference](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)
- [Health Checks](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover.html)
- [Route 53 Pricing](https://aws.amazon.com/route53/pricing/)
