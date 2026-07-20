# Cost Optimization Strategies

> **Systematic approaches to reduce cloud spend while maintaining performance**

## Overview

Cost optimization is not about cutting corners—it's about getting maximum value from every dollar spent. This guide covers proven strategies to reduce AWS costs by 30-50% without impacting performance or reliability.

---

## 🎯 The Cost Optimization Framework

```
┌────────────────────────────────────────┐
│      COST OPTIMIZATION PILLARS         │
├────────────────────────────────────────┤
│ 1. Right-Sizing (20-40% savings)      │
│ 2. Reserved Capacity (20-30%)          │
│ 3. Waste Elimination (10-20%)          │
│ 4. Architecture Optimization (10-30%)  │
└────────────────────────────────────────┘
```

---

## 1. Right-Sizing Strategy

### Compute Right-Sizing

**Problem:** Most EC2 instances are oversized by 40-60%

**Solution:** Monitor actual usage and adjust capacity accordingly.

**Right-Sizing Decision Matrix:**

| Avg CPU | Max CPU | Memory | Action |
|---------|---------|--------|--------|
| <10% | <20% | <30% | Downsize 2 levels |
| <20% | <40% | <50% | Downsize 1 level |
| 20-40% | <60% | <70% | Keep current |
| >50% | >70% | >80% | Upsize recommended |
| >70% | >90% | >90% | Urgent upsize |

### Database Right-Sizing

**RDS Right-Sizing Guidelines:**
- CPU <20% + Connections <50% of max → Downsize
- CPU consistently >70% → Upsize
- High IOPS wait → Consider storage optimization
- Memory pressure → Increase instance size

---

## 2. Reserved Capacity Strategy

### Reserved Instance (RI) Optimization

**RI vs Savings Plans Decision:**

| Workload Type | Recommendation | Savings |
|---------------|----------------|---------|
| Stable, predictable | 3-year RI | 60-65% |
| Growing, flexible | 1-year Compute SP | 40-50% |
| Variable compute | EC2 Instance SP | 30-40% |
| Mixed workloads | Combination | 35-55% |

### Savings Plans Strategy

```yaml
Savings Plan Allocation:
  Baseline (70% of usage):
    Type: Compute Savings Plan
    Term: 3-year
    Payment: Partial Upfront
    Savings: ~50%
  
  Growth (20% of usage):
    Type: EC2 Instance Savings Plan
    Term: 1-year
    Payment: No Upfront
    Savings: ~30%
  
  Burst (10% of usage):
    Type: On-Demand
    Note: Flexibility for spikes
```

---

## 3. Waste Elimination

### Common Waste Sources

1. **Unattached EBS Volumes**
   - Cost: $0.10/GB/month
   - Common cause: Instance terminated, volume retained
   - Action: Delete volumes older than 30 days

2. **Unused Elastic IPs**

   - Cost: $3.60/month per IP
   - Action: Release IPs not associated with instances

3. **Old Snapshots**
   - Cost: $0.05/GB/month
   - Action: Implement lifecycle policies, delete >1 year old

4. **Idle Load Balancers**
   - Cost: $16-27/month per LB
   - Action: Delete LBs with no active targets

5. **Unused NAT Gateways**
   - Cost: $32.40/month + data processing
   - Action: Consolidate or remove unused gateways

---

## 4. Architecture Optimization

### Serverless Migration

**When to Use Serverless:**
- Sporadic workloads (<20% time active)
- Event-driven processing
- Microservices with variable load
- Background jobs

**Cost Comparison Example:**
```
EC2 Approach (t3.small 24/7):
- Monthly cost: $15.33
- Average utilization: 10%
- Waste: 90%

Lambda Approach:
- 1M requests/month: $0.20
- Avg 512MB, 2s execution: $17.00
- Total: $17.20/month
- Utilization: 100%
- Better scaling, no waste
```

### Storage Optimization

**S3 Storage Classes:**

| Storage Class | Cost/GB/month | Retrieval | Use Case |
|---------------|---------------|-----------|----------|
| S3 Standard | $0.023 | Free | Active data |
| S3 IA | $0.0125 | $0.01/GB | <1x/month |
| S3 Glacier | $0.004 | $0.02/GB | Archival |
| S3 Deep Archive | $0.00099 | $0.02/GB | Long-term |

**S3 Lifecycle Policy Example:**
```json
{
  "Rules": [
    {
      "Id": "archive-old-data",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ]
    }
  ]
}
```

### Network Optimization

**Data Transfer Cost Reduction:**

1. **Use CloudFront** for static content (reduce egress costs)
2. **Consolidate resources** in same AZ (avoid inter-AZ transfer)
3. **Use VPC endpoints** for AWS services (avoid NAT gateway costs)
4. **Compress data** before transfer
5. **Use AWS Direct Connect** for large data transfers (>1TB/month)

**Network Cost Breakdown:**
```
Data Transfer Costs:
- Inbound: Free
- Outbound to Internet: $0.09/GB (first 10TB)
- Inter-AZ: $0.01/GB each direction
- Same AZ: Free
```

---

## 5. Spot Instance Strategy

### When to Use Spot Instances

**Spot vs On-Demand Decision:**

| Workload | Recommendation | Savings |
|----------|----------------|---------|
| Batch processing | 100% Spot | 70-90% |
| Development/Test | 80% Spot, 20% On-Demand | 60-70% |
| Stateless web | 50% Spot, 50% On-Demand | 35-45% |
| Databases | Avoid Spot | N/A |

**Best Practices:**
- Use multiple instance types for diversification
- Implement graceful shutdown handling
- Use Spot Fleet for automatic failover
- Monitor interruption notices (2-minute warning)
- Combine with Auto Scaling Groups

---

## 6. Container Optimization (ECS/EKS)

### Fargate vs EC2 for ECS

**Cost Comparison:**
```
Scenario: 10 containers, 1vCPU, 2GB RAM each

Fargate:
  Cost per container/hour: $0.04856
  Monthly cost (10 containers): $350
  Pros: No management, auto-scaling
  Cons: Higher cost per container

EC2 (m5.xlarge):
  Instance cost/hour: $0.192
  Containers per instance: 3-4
  Required instances: 3
  Monthly cost: $414
  Pros: Lower per-container cost at scale
  Cons: Management overhead

Recommendation: 
  - Fargate for <20 containers
  - EC2 for >50 containers
  - Hybrid for in-between
```

### Kubernetes Cost Optimization

**Key Strategies:**
1. **Right-size pod requests/limits** based on actual usage
2. **Use cluster autoscaler** for dynamic scaling
3. **Implement Horizontal Pod Autoscaler** (HPA)
4. **Use namespace resource quotas** for cost control
5. **Schedule non-critical workloads on Spot nodes**

**Resource Request Optimization:**
```yaml
# Before (Over-provisioned)
resources:
  requests:
    cpu: "1000m"
    memory: "2Gi"
  limits:
    cpu: "2000m"
    memory: "4Gi"

# After (Right-sized)
resources:
  requests:
    cpu: "200m"      # Based on actual 150m avg usage
    memory: "512Mi"   # Based on actual 400Mi avg usage
  limits:
    cpu: "500m"
    memory: "1Gi"
```

---

## 7. Real-World Optimization Example

### Case Study: E-commerce Platform

**Initial State:**
- Monthly AWS bill: $127,000
- 150+ EC2 instances
- 30 RDS databases
- 50TB S3 storage

**Optimization Journey:**

**Week 1 - Quick Wins ($839/mo, 0.7%):**
- Deleted 20 unattached EBS volumes: $200/mo
- Released 15 unused Elastic IPs: $54/mo
- Removed 5 idle load balancers: $135/mo
- Deleted old snapshots: $450/mo

**Week 2-3 - Right-Sizing ($15,400/mo, 12.1%):**
- Downsized 40 EC2 instances: $8,400/mo
- Optimized 10 RDS instances: $4,200/mo
- Implemented auto-scaling: $2,800/mo

**Month 2 - Reserved Capacity ($24,500/mo, 19.3%):**
- Purchased 60 RIs (1-year): $18,000/mo
- Committed to Compute Savings Plan: $6,500/mo

**Month 3 - Architecture ($8,100/mo, 6.4%):**
- Migrated batch jobs to Spot: $4,200/mo
- Implemented S3 lifecycle: $1,800/mo
- Optimized data transfer: $2,100/mo

**Total Results:**
- Total Savings: $48,839/mo (38.5%)
- New Monthly Bill: $78,161
- ROI: Savings paid for FinOps engineer salary in 3 months

---

## 8. Continuous Optimization

### Monthly Optimization Checklist

**Week 1: Review & Report**
- [ ] Generate monthly cost report
- [ ] Review top cost drivers
- [ ] Identify anomalies
- [ ] Compare to budget

**Week 2: Quick Wins**
- [ ] Delete unused resources
- [ ] Review recent waste
- [ ] Check for new optimization opportunities

**Week 3: Strategic Review**
- [ ] Review RI/SP utilization
- [ ] Assess right-sizing opportunities
- [ ] Evaluate new service costs

**Week 4: Planning**
- [ ] Update cost forecasts
- [ ] Plan next month's optimizations
- [ ] Review team chargeback
- [ ] Prepare executive report

---

## 9. Cost Optimization Tools

### AWS Native Tools

1. **AWS Cost Explorer**
   - Visualize spending patterns
   - Forecast future costs
   - Analyze by service, tag, account

2. **AWS Compute Optimizer**
   - Right-sizing recommendations
   - Based on actual usage metrics
   - Covers EC2, EBS, Lambda, Auto Scaling

3. **AWS Trusted Advisor**
   - Cost optimization checks
   - Identifies idle resources
   - RI/SP recommendations

4. **AWS Cost Anomaly Detection**
   - ML-based anomaly detection
   - Automated alerts
   - Root cause analysis

### Third-Party Tools

**When to Consider:**
- Monthly spend >$100K
- Multi-cloud environment
- Need advanced analytics
- Require automation capabilities

**Popular Options:**
- CloudHealth by VMware
- Cloudability by Apptio
- nOps
- Vantage
- Kubecost (for Kubernetes)

---

## 10. Optimization Metrics & KPIs

### Key Performance Indicators

**Cost Efficiency:**
- Cost per transaction
- Cost per user/customer
- Cost per API call
- Cost per deployment

**Optimization Rate:**
- Month-over-month cost trend
- Waste percentage (<10% target)
- RI/SP coverage (>70% target)
- RI/SP utilization (>95% target)

**Governance:**
- Tagged resources percentage (100% target)
- Budget adherence (±5% target)
- Cost anomaly detection time (<24h target)
- Optimization implementation rate

---

## Interview Questions

**Q: How would you reduce a $500K/month AWS bill by 30%?**

**A:** Four-phase approach:

1. **Immediate (Week 1):** Waste elimination
   - Delete unattached volumes, unused IPs, idle LBs
   - Expected: 5-10% savings ($25K-50K/mo)

2. **Short-term (Month 1):** Right-sizing
   - Analyze CloudWatch metrics for EC2/RDS
   - Downsize over-provisioned resources
   - Expected: 10-15% savings ($50K-75K/mo)

3. **Medium-term (Quarter 1):** Reserved capacity
   - Purchase RIs/Savings Plans for baseline
   - Cover 70% of predictable usage
   - Expected: 10-20% savings ($50K-100K/mo)

4. **Long-term (6 months):** Architecture optimization
   - Migrate to Spot instances, serverless
   - Optimize data transfer, storage
   - Expected: 5-15% savings ($25K-75K/mo)

**Total:** 30-60% savings possible ($150K-300K/mo)

**Q: What's your approach to right-sizing EC2 instances?**

**A:** Data-driven 6-step process:

1. **Collect Metrics:** 30 days CloudWatch data (CPU, memory, network, disk)
2. **Analyze Utilization:** Identify <20% avg, <40% max utilization
3. **Recommend Changes:** Downsize with 30% performance headroom
4. **Test in Non-Prod:** Validate changes in staging environment
5. **Deploy to Production:** Implement during maintenance window
6. **Monitor Results:** Track for 2 weeks, document savings

**Q: Spot instances vs Reserved Instances - when to use each?**

**A:**

**Spot Instances (70-90% savings):**
- Use for: Batch processing, CI/CD, data analytics, dev/test
- Requirements: Fault-tolerant, stateless, flexible timing
- Risk: 2-minute interruption notice

**Reserved Instances (40-60% savings):**
- Use for: Production databases, baseline web servers
- Requirements: Predictable, 24/7 usage
- Commitment: 1-3 year term

**Strategy:** 
- Cover 70% baseline with RIs
- Handle bursts with Spot (where possible)
- Use On-Demand for remainder (flexibility)

**Q: How do you measure success of cost optimization efforts?**

**A:** Track three categories of metrics:

1. **Financial Impact:**
   - Month-over-month cost reduction percentage
   - Total savings achieved vs target
   - Cost avoidance (preventing waste before it happens)

2. **Operational Efficiency:**
   - RI/SP coverage and utilization rates
   - Waste percentage (unused resources)
   - Time to detect and remediate anomalies

3. **Business Value:**
   - Cost per unit economics (transaction, user, API call)
   - Cloud ROI (revenue/cloud spend)
   - Engineering velocity (not slowed by cost gates)

**Example Dashboard:**
```
Month-over-Month: -12% ($580K → $511K)
Total YTD Savings: $847K
Waste Percentage: 7% (target: <10%)
RI Coverage: 74% (target: >70%)
Tagged Resources: 98% (target: 100%)
```

---

## Key Takeaways

1. **Right-sizing is the biggest opportunity** - 20-40% savings potential
2. **Quick wins build momentum** - Start with waste elimination
3. **Reserved capacity is predictable** - 20-30% guaranteed savings
4. **Automation is critical** - Manual optimization doesn't scale
5. **Monitor continuously** - What you don't measure, you can't optimize
6. **Balance cost vs velocity** - Don't slow down engineering teams

---

## Next Steps

1. **Audit your environment** - Run waste detection
2. **Analyze top 20 resources** - Right-sizing opportunities
3. **Review RI/SP recommendations** - AWS Cost Explorer
4. **Implement automation** - Start with waste cleanup
5. **Continue learning** → Move to `08-unit-economics.md`

---

**Remember:** Cost optimization is a continuous journey. Start with quick wins, build momentum, then tackle architectural changes. Every dollar saved is a dollar that can be invested in innovation.
