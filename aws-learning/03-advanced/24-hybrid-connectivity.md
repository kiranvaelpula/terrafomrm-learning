# Chapter 24: Hybrid Connectivity - Site-to-Site VPN & Direct Connect

## Overview

Hybrid connectivity links your on-premises data centers to AWS. This chapter covers the two primary options — Site-to-Site VPN (over the internet) and Direct Connect (dedicated physical connection) — plus resilient patterns that combine them.

**What You'll Learn**
- Site-to-Site VPN setup (Customer Gateway, Virtual Private Gateway, tunnels, BGP)
- AWS Direct Connect (dedicated vs hosted, Virtual Interfaces, DX Gateway)
- VPN over Direct Connect for encryption
- High-availability and resilient hybrid architectures
- Integration with Transit Gateway
- Cost, performance, and selection criteria

**Prerequisites**
- Strong VPC fundamentals
- Understanding of routing and BGP basics
- Familiarity with Transit Gateway (Chapter 14)

---

## Connectivity Options Comparison

| Feature | Site-to-Site VPN | Direct Connect |
|---------|-----------------|----------------|
| Medium | Public internet (encrypted) | Dedicated physical line |
| Bandwidth | Up to ~1.25 Gbps per tunnel | 50 Mbps – 100 Gbps |
| Latency | Variable (internet) | Consistent, low |
| Setup time | Minutes | Weeks–months (physical) |
| Cost | Low ($0.05/hr + data) | High (port + cross-connect + data) |
| Encryption | Built-in (IPsec) | Not by default (add VPN/MACsec) |
| Use case | Quick, backup, low-mid traffic | Production, high-throughput, consistent |

**Key point:** Many enterprises use **both** — Direct Connect as primary, VPN as backup.

---

## Part 1: Site-to-Site VPN

### What is Site-to-Site VPN?

An IPsec VPN connection between your on-premises network and your VPC, running over the public internet with encryption.

**Architecture:**
```
On-Premises                          AWS
┌──────────────┐                ┌──────────────────┐
│ Customer     │                │ Virtual Private   │
│ Gateway (CGW)│◀══ Tunnel 1 ══▶│ Gateway (VGW)     │
│ (your router)│◀══ Tunnel 2 ══▶│ or Transit Gateway│
└──────┬───────┘   (IPsec)      └────────┬──────────┘
       │                                  │
  On-prem network                    VPC (10.0.0.0/16)
  (192.168.0.0/16)
```

**Two tunnels** are always provisioned for redundancy (different AWS endpoints).

### Core Components

| Component | What it is |
|-----------|-----------|
| **Customer Gateway (CGW)** | Represents your on-prem router/firewall in AWS (its public IP + BGP ASN) |
| **Virtual Private Gateway (VGW)** | The AWS-side VPN endpoint, attached to a VPC |
| **Transit Gateway** | Alternative AWS-side endpoint (for multi-VPC hybrid) |
| **VPN Connection** | The IPsec connection with 2 tunnels |

### Setting Up Site-to-Site VPN

**Step 1: Create Customer Gateway**
```bash
# Represents your on-premises router
aws ec2 create-customer-gateway \
  --type ipsec.1 \
  --public-ip 203.0.113.10 \
  --bgp-asn 65000 \
  --tag-specifications 'ResourceType=customer-gateway,Tags=[{Key=Name,Value=OnPrem-Router}]'
```

**Step 2: Create Virtual Private Gateway and attach to VPC**
```bash
# Create VGW
aws ec2 create-vpn-gateway \
  --type ipsec.1 \
  --amazon-side-asn 64512 \
  --tag-specifications 'ResourceType=vpn-gateway,Tags=[{Key=Name,Value=Main-VGW}]'

# Attach to VPC
aws ec2 attach-vpn-gateway \
  --vpn-gateway-id vgw-12345678 \
  --vpc-id vpc-aaaaaaaa
```

**Step 3: Create the VPN Connection**
```bash
# Dynamic routing (BGP) — recommended
aws ec2 create-vpn-connection \
  --type ipsec.1 \
  --customer-gateway-id cgw-12345678 \
  --vpn-gateway-id vgw-12345678 \
  --options '{"StaticRoutesOnly":false}' \
  --tag-specifications 'ResourceType=vpn-connection,Tags=[{Key=Name,Value=OnPrem-VPN}]'

# Static routing (if your router doesn't support BGP)
# --options '{"StaticRoutesOnly":true}'
```

**Step 4: Enable Route Propagation**
```bash
# Auto-propagate VPN routes into the VPC route table
aws ec2 enable-vgw-route-propagation \
  --route-table-id rtb-12345678 \
  --gateway-id vgw-12345678
```

**Step 5: Configure your on-premises router**
```bash
# AWS provides a downloadable config for your device
aws ec2 describe-vpn-connections \
  --vpn-connection-ids vpn-12345678 \
  --query 'VpnConnections[0].CustomerGatewayConfiguration' \
  --output text > vpn-config.txt

# Config includes: tunnel IPs, pre-shared keys, BGP settings
# Apply to Cisco, Juniper, Palo Alto, pfSense, etc.
```

### Static vs Dynamic (BGP) Routing

| Static Routing | Dynamic (BGP) Routing |
|----------------|----------------------|
| Manually define routes | Routes auto-exchanged via BGP |
| Simple, small networks | Scales, adapts to changes |
| No automatic failover of routes | Automatic failover between tunnels |
| Router doesn't need BGP | Requires BGP-capable router |

**Recommendation:** Use BGP (dynamic) for production — it enables automatic failover and route updates.

### VPN High Availability

```
For full redundancy, use TWO Customer Gateways
(two on-prem routers) + the two AWS tunnels each:

On-Prem Router 1 ──┬── Tunnel 1 ──┐
                   └── Tunnel 2 ──┤
                                  ├──▶ VGW / TGW
On-Prem Router 2 ──┬── Tunnel 1 ──┤
                   └── Tunnel 2 ──┘

4 tunnels total = survives router OR tunnel failure.
```

---

## Part 2: AWS Direct Connect (DX)

### What is Direct Connect?

A dedicated, private physical network connection between your data center and AWS — bypassing the public internet entirely.

**Architecture:**
```
Your Data Center          DX Location          AWS Region
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ Your Router  │──────│ DX Endpoint  │──────│ VPC / TGW    │
│              │ Cross│ (AWS cage)   │ AWS  │              │
│              │ Conn.│              │backbone              │
└──────────────┘      └──────────────┘      └──────────────┘
     (private, dedicated fiber — no internet)
```

**Benefits:**
- Consistent, low latency (not subject to internet congestion)
- High bandwidth (up to 100 Gbps)
- Reduced data transfer costs at scale
- More secure (private, doesn't traverse internet)

### Dedicated vs Hosted Connections

| Type | Description | Bandwidth |
|------|-------------|-----------|
| **Dedicated** | Physical port allocated to you at a DX location | 1, 10, 100 Gbps |
| **Hosted** | Provisioned through an AWS Partner (they own the port) | 50 Mbps – 10 Gbps |

Use **Hosted** if you don't need a full dedicated port or want faster provisioning via a partner.

### Virtual Interfaces (VIFs)

A DX connection carries traffic through Virtual Interfaces:

| VIF Type | Purpose | Connects to |
|----------|---------|-------------|
| **Private VIF** | Access VPC resources privately | VGW or DX Gateway |
| **Public VIF** | Access AWS public services (S3, DynamoDB) over DX | AWS public endpoints |
| **Transit VIF** | Connect to Transit Gateway (multi-VPC) | DX Gateway → Transit Gateway |

```bash
# Create a Private VIF
aws directconnect create-private-virtual-interface \
  --connection-id dxcon-12345678 \
  --new-private-virtual-interface '{
    "virtualInterfaceName": "prod-private-vif",
    "vlan": 100,
    "asn": 65000,
    "authKey": "bgp-auth-key",
    "amazonAddress": "169.254.1.1/30",
    "customerAddress": "169.254.1.2/30",
    "virtualGatewayId": "vgw-12345678"
  }'
```

### Direct Connect Gateway (DX Gateway)

A DX Gateway lets a single DX connection reach **multiple VPCs across regions**.

```
                    ┌─────────────────┐
On-Prem ── DX ──────│  DX Gateway     │
                    └────────┬────────┘
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         VPC (us-east-1) VPC (eu-west-1) Transit Gateway
```

```bash
# Create DX Gateway
aws directconnect create-direct-connect-gateway \
  --direct-connect-gateway-name "global-dx-gw" \
  --amazon-side-asn 64512

# Associate with a Transit Gateway (for multi-VPC, multi-region)
aws directconnect create-direct-connect-gateway-association \
  --direct-connect-gateway-id <dx-gw-id> \
  --gateway-id tgw-12345678
```

### DX Resiliency Models (AWS recommended)

| Model | Setup | SLA |
|-------|-------|-----|
| **Development** | Single connection, single location | No HA |
| **High Resiliency** | 2 connections at 2 different DX locations | Survives location failure |
| **Maximum Resiliency** | 2 connections each at 2 locations (4 total) | Highest — survives device + location failure |

---

## Part 3: Resilient Hybrid Architectures

### Pattern 1: Direct Connect + VPN Backup (most common)

```
                    ┌── Direct Connect (primary) ──┐
On-Premises ────────┤                              ├──▶ AWS (TGW/VGW)
                    └── Site-to-Site VPN (backup) ─┘

BGP prefers DX. If DX fails, traffic auto-fails over to VPN.
```

**Why:** DX gives performance; VPN gives a cheap, always-available fallback. BGP handles the failover automatically by preferring the DX route.

### Pattern 2: VPN over Direct Connect (encryption on DX)

```
DX by default is NOT encrypted (it's private but not encrypted).
For compliance requiring encryption in transit:

On-Prem ── IPsec VPN tunnel running OVER Direct Connect ──▶ AWS

Combines DX performance/privacy WITH VPN encryption.
```

### Pattern 3: Transit Gateway + DX + VPN (enterprise hub)

```
                     Transit Gateway (hub)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   VPC (Prod)          VPC (Dev)          Transit VIF
                                               │
                                          DX Gateway
                                               │
                                   ┌───────────┴──────────┐
                                   │                      │
                             Direct Connect          VPN (backup)
                                   │                      │
                              On-Premises ────────────────┘
```

This is the standard large-enterprise pattern: TGW as the hub connects all VPCs, and a Transit VIF via DX Gateway (with VPN backup) connects on-premises.

---

## Cost Comparison

**Site-to-Site VPN:**
```
Connection:    $0.05/hour (~$36/month) per connection
Data transfer: Standard AWS data-out rates
```

**Direct Connect:**
```
Port hours:    $0.30/hr (1Gbps) to $22.50/hr (100Gbps) — varies by location
Cross-connect: Charged by the DX location/colo provider
Data transfer: LOWER than internet rates (e.g., ~$0.02/GB out vs ~$0.09/GB)
  → At high volume, DX data savings offset the port cost
```

**Rule of thumb:** VPN for low traffic/quick setup. DX when you have consistent high traffic (data transfer savings + performance justify the cost).

---

## Selection Decision Tree

```
Need hybrid connectivity?
│
├── Need it FAST / low traffic / backup? ──────▶ Site-to-Site VPN
│
├── Need consistent low latency + high bandwidth? ──▶ Direct Connect
│
├── Need DX but also encryption? ──────────────▶ VPN over Direct Connect
│
├── Multiple VPCs / regions on-prem access? ───▶ DX Gateway + Transit Gateway
│
└── Production critical? ──────────────────────▶ DX (primary) + VPN (backup)
```

---

## Troubleshooting Hybrid Connectivity

```bash
# Check VPN tunnel status (should be UP)
aws ec2 describe-vpn-connections \
  --vpn-connection-ids vpn-12345678 \
  --query 'VpnConnections[0].VgwTelemetry[*].[OutsideIpAddress,Status]' \
  --output table

# Check DX connection state
aws directconnect describe-connections \
  --connection-id dxcon-12345678 \
  --query 'connections[0].connectionState'

# Check BGP status on VIF
aws directconnect describe-virtual-interfaces \
  --query 'virtualInterfaces[*].[virtualInterfaceName,bgpPeers[0].bgpStatus]' \
  --output table

# Common issues:
# - Tunnel DOWN: check pre-shared key, IKE/IPsec settings, firewall
# - BGP not established: check ASN, peer IPs, BGP auth key
# - No traffic despite UP: check route propagation + security groups + NACLs
# - Asymmetric routing: verify BGP route advertisements both directions
```

---

## Best Practices

**1. Always design for redundancy**
- VPN: use 2 tunnels (default) + optionally 2 Customer Gateways
- DX: use High or Maximum Resiliency model (2+ connections)
- Combine DX + VPN backup for critical workloads

**2. Use BGP (dynamic routing)** for automatic failover between paths.

**3. Encrypt sensitive traffic** — DX alone is private but not encrypted; add VPN-over-DX or MACsec for compliance.

**4. Use Transit Gateway** as the hub when connecting on-prem to many VPCs — avoid attaching VPN/DX to each VPC separately.

**5. Monitor tunnel/BGP health** with CloudWatch alarms on VPN tunnel state and DX connection state.

**6. Plan CIDRs carefully** — on-prem and VPC ranges must not overlap.

---

## Interview Q&A

**Q: When would you use VPN vs Direct Connect?**
> VPN for quick setup, low-to-medium traffic, or as a backup — it runs over the internet with IPsec encryption and is cheap. Direct Connect for production workloads needing consistent low latency and high bandwidth — it's a dedicated physical line. In practice I use both: DX as primary for performance, VPN as automatic backup via BGP.

**Q: Is Direct Connect encrypted?**
> Not by default. DX is private (doesn't traverse the internet) but not encrypted. For compliance requiring encryption in transit, I run an IPsec VPN over the Direct Connect connection, or use MACsec on supported ports.

**Q: How do you connect on-premises to multiple VPCs across regions?**
> A Direct Connect Gateway associated with a Transit Gateway. The DX connection uses a Transit VIF to the DX Gateway, which connects to the Transit Gateway hub, which in turn connects to all VPCs across regions. One physical connection reaches everything.

**Q: How do you make hybrid connectivity highly available?**
> Multiple layers: two VPN tunnels (default) plus optionally two customer gateways; for DX, the Maximum Resiliency model with connections at two DX locations; and combining DX primary with VPN backup using BGP for automatic failover. Plus CloudWatch monitoring on tunnel and connection health.

---

## Summary

**Key Takeaways:**
- **Site-to-Site VPN** — IPsec over internet, quick, cheap, always 2 tunnels for redundancy
- **Direct Connect** — dedicated physical line, consistent performance, high bandwidth
- **VIFs** — Private (VPC), Public (AWS services), Transit (to TGW)
- **DX Gateway** — one DX reaches multiple VPCs/regions
- **DX + VPN backup** — the standard resilient production pattern
- **VPN over DX** — adds encryption to Direct Connect
- **Transit Gateway** — the hub that ties hybrid connectivity to many VPCs

**Related Chapters:**
- [14-advanced-vpc.md](./14-advanced-vpc.md) — Transit Gateway, VPC Peering, PrivateLink
- [15-organizations-control-tower.md](./15-organizations-control-tower.md) — Multi-account networking
- [21-multi-region.md](./21-multi-region.md) — Cross-region connectivity
