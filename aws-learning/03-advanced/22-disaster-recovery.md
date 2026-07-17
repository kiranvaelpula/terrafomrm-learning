# Chapter 22: Disaster Recovery Strategies

## Overview

Disaster Recovery (DR) ensures business continuity when failures occur. AWS provides multiple DR strategies with different RTO/RPO objectives.

**Topics:**
- DR strategies and trade-offs
- RTO and RPO concepts
- Backup and restore
- Pilot light
- Warm standby
- Multi-site active-active
- Testing DR plans

---

## DR Objectives

### RTO (Recovery Time Objective)
Maximum acceptable downtime after a disaster.

### RPO (Recovery Point Objective)  
Maximum acceptable data loss (measured in time).

```
Timeline:
Disaster → RPO → Detection → Recovery → RTO → Normal Operations
            ↑                              ↑
         Last Backup              Service Restored
```

---

## DR Strategies

| Strategy | RTO | RPO | Cost | Complexity |
|----------|-----|-----|------|------------|
| Backup & Restore | Hours-Days | Hours | Lowest | Low |
| Pilot Light | Hours | Minutes | Low | Medium |
| Warm Standby | Minutes | Seconds | Medium | Medium |
| Multi-Site Active-Active | Seconds | None | Highest | High |

---

## 1. Backup and Restore

**Lowest cost, highest RTO/RPO**

### Architecture
```
Production (us-east-1)
    |
    +-- EC2 Instances → AMIs → S3
    +-- EBS Volumes → Snapshots → S3
    +-- RDS Database → Snapshots → S3
    +-- S3 Buckets → Cross-Region Replication

DR Region (us-west-2)
    |
    +-- S3 (replicated data)
    +-- No running resources
```

### Implementation

**Automated Backups:**
```python
import boto3
from datetime import datetime

ec2 = boto3.client('ec2')
rds = boto3.client('rds')

def backup_ec2_instances():
    # Get production instances
    instances = ec2.describe_instances(
        Filters=[{'Name': 'tag:Environment', 'Values': ['production']}]
    )
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            # Create AMI
            ami = ec2.create_image(
                InstanceId=instance['InstanceId'],
                Name=f"backup-{instance['InstanceId']}-{datetime.now().strftime('%Y%m%d')}",
                NoReboot=True
            )
            
            # Copy to DR region
            ec2_dr = boto3.client('ec2', region_name='us-west-2')
            ec2_dr.copy_image(
                SourceImageId=ami['ImageId'],
                SourceRegion='us-east-1',
                Name=ami['ImageId']
            )

def backup_rds():
    # Create snapshot
    snapshot = rds.create_db_snapshot(
        DBSnapshotIdentifier=f"backup-{datetime.now().strftime('%Y%m%d')}",
        DBInstanceIdentifier='production-db'
    )
    
    # Copy to DR region
    rds_dr = boto3.client('rds', region_name='us-west-2')
    rds_dr.copy_db_snapshot(
        SourceDBSnapshotIdentifier=snapshot['DBSnapshot']['DBSnapshotArn'],
        TargetDBSnapshotIdentifier=snapshot['DBSnapshot']['DBSnapshotIdentifier'],
        SourceRegion='us-east-1'
    )
```

**Schedule with EventBridge:**
```bash
# Daily backups at 2 AM
aws events put-rule \
  --name daily-backups \
  --schedule-expression "cron(0 2 * * ? *)"

aws events put-targets \
  --rule daily-backups \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:123456789012:function:backup-function"
```

---

## 2. Pilot Light

**Core infrastructure running, scaled down**

### Architecture
```
Production (us-east-1)
    |
    +-- Full application stack
    +-- Auto Scaling: 10-50 instances
    +-- RDS Multi-AZ

DR Region (us-west-2)
    |
    +-- RDS Read Replica (continuously replicated)
    +-- AMIs ready
    +-- Launch Templates configured
    +-- Auto Scaling: 0 instances (ready to scale)
```

### Setup

**RDS Read Replica:**
```bash
# Create read replica in DR region
aws rds create-db-instance-read-replica \
  --db-instance-identifier dr-replica \
  --source-db-instance-identifier arn:aws:rds:us-east-1:123456789012:db:prod-db \
  --source-region us-east-1 \
  --db-instance-class db.t3.large \
  --region us-west-2
```

**Failover Process:**
```python
def failover_to_dr():
    # 1. Promote read replica
    rds_dr = boto3.client('rds', region_name='us-west-2')
    rds_dr.promote_read-replica(DBInstanceIdentifier='dr-replica')
    
    # 2. Scale up application
    asg_dr = boto3.client('autoscaling', region_name='us-west-2')
    asg_dr.set_desired_capacity(
        AutoScalingGroupName='dr-asg',
        DesiredCapacity=10
    )
    
    # 3. Update Route53
    route53 = boto3.client('route53')
    route53.change_resource_record_sets(
        HostedZoneId='Z1234567890ABC',
        ChangeBatch={
            'Changes': [{
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': 'www.example.com',
                    'Type': 'A',
                    'SetIdentifier': 'DR',
                    'Failover': 'PRIMARY',
                    'AliasTarget': {
                        'HostedZoneId': 'Z32O12XQLNTSW2',
                        'DNSName': 'dr-alb.us-west-2.elb.amazonaws.com'
                    }
                }
            }]
        }
    )
```

---

## 3. Warm Standby

**Scaled-down but fully functional**

### Architecture
```
Production (us-east-1)
    |
    +-- Auto Scaling: 10-50 instances
    +-- RDS Multi-AZ (db.r5.2xlarge)
    +-- 100% traffic

DR Region (us-west-2)
    |
    +-- Auto Scaling: 2-10 instances (running)
    +-- RDS Read Replica (db.r5.large)
    +-- 0% traffic (ready to receive)
```

### Implementation

**Keep DR running:**
```bash
# DR Auto Scaling Group (scaled down)
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name dr-asg \
  --launch-template LaunchTemplateName=app-template \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 2 \
  --vpc-zone-identifier subnet-dr-1,subnet-dr-2 \
  --region us-west-2

# Scale up during failover
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name dr-asg \
  --desired-capacity 10 \
  --region us-west-2
```

**Health Checks:**
```python
import boto3

def check_dr_health():
    cloudwatch = boto3.client('cloudwatch', region_name='us-west-2')
    
    # Check DR application health
    response = cloudwatch.get-metric-statistics(
        Namespace='AWS/ApplicationELB',
        MetricName='HealthyHostCount',
        Dimensions=[{'Name': 'LoadBalancer', 'Value': 'app/dr-alb/xyz'}],
        StartTime=datetime.utcnow() - timedelta(minutes=5),
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=['Average']
    )
    
    healthy_hosts = response['Datapoints'][0]['Average'] if response['Datapoints'] else 0
    
    if healthy_hosts < 1:
        send_alert("DR environment unhealthy!")
```

---

## 4. Multi-Site Active-Active

**Full production in multiple regions**

### Architecture
```
Region 1 (us-east-1) - 50% traffic
    |
    +-- Auto Scaling: 10-50 instances
    +-- DynamoDB Global Table
    +-- Aurora Global Database

Region 2 (eu-west-1) - 50% traffic
    |
    +-- Auto Scaling: 10-50 instances
    +-- DynamoDB Global Table
    +-- Aurora Global Database

Route53 Latency-Based Routing
CloudFront (Global CDN)
```

### Setup

**DynamoDB Global Table:**
```bash
# Create table
aws dynamodb create-table \
  --table-name Users \
  --attribute-definitions AttributeName=UserId,AttributeType=S \
  --key-schema AttributeName=UserId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
  --region us-east-1

# Create global table
aws dynamodb create-global-table \
  --global-table-name Users \
  --replication-group RegionName=us-east-1 RegionName=eu-west-1
```

**Aurora Global Database:**
```bash
# Create global cluster
aws rds create-global-cluster \
  --global-cluster-identifier my-global-db \
  --engine aurora-mysql

# Add primary region
aws rds create-db-cluster \
  --db-cluster-identifier primary-cluster \
  --engine aurora-mysql \
  --global-cluster-identifier my-global-db \
  --region us-east-1

# Add secondary region
aws rds create-db-cluster \
  --db-cluster-identifier secondary-cluster \
  --engine aurora-mysql \
  --global-cluster-identifier my-global-db \
  --region eu-west-1
```

---

## Backup Strategies

### AWS Backup

**Centralized backup management:**
```bash
# Create backup plan
aws backup create-backup-plan \
  --backup-plan file://backup-plan.json
```

**backup-plan.json:**
```json
{
  "BackupPlanName": "DailyBackupPlan",
  "Rules": [{
    "RuleName": "DailyBackup",
    "TargetBackupVaultName": "Default",
    "ScheduleExpression": "cron(0 2 * * ? *)",
    "StartWindowMinutes": 60,
    "CompletionWindowMinutes": 120,
    "Lifecycle": {
      "DeleteAfterDays": 35,
      "MoveToColdStorageAfterDays": 7
    },
    "CopyActions": [{
      "DestinationBackupVaultArn": "arn:aws:backup:us-west-2:123456789012:backup-vault:DR-Vault",
      "Lifecycle": {
        "DeleteAfterDays": 35
      }
    }]
  }]
}
```

**Assign resources:**
```bash
aws backup create-backup-selection \
  --backup-plan-id plan-id \
  --backup-selection file://selection.json
```

**selection.json:**
```json
{
  "SelectionName": "ProductionResources",
  "IamRoleArn": "arn:aws:iam::123456789012:role/AWSBackupRole",
  "Resources": [
    "arn:aws:rds:*:*:db:prod-*",
    "arn:aws:ec2:*:*:volume/*"
  ],
  "ListOfTags": [{
    "ConditionType": "STRINGEQUALS",
    "ConditionKey": "Environment",
    "ConditionValue": "Production"
  }]
}
```

---

## DR Testing

**Regular testing is critical**

### Test Plan

**1. Documentation Test (Quarterly)**
- Review runbooks
- Update contacts
- Verify access

**2. Tabletop Exercise (Quarterly)**
- Walk through scenarios
- Identify gaps
- Update procedures

**3. Simulation Test (Semi-annually)**
- Restore from backups
- Launch DR environment
- Don't switch traffic

**4. Failover Test (Annually)**
- Full failover to DR
- Run production traffic
- Measure RTO/RPO
- Fail back to primary

### Automated DR Testing

```python
def test_dr_recovery():
    """Automated DR test"""
    
    # 1. Create test snapshot
    snapshot = create_test_snapshot()
    
    # 2. Restore in DR region
    restored_db = restore_snapshot_in_dr(snapshot)
    
    # 3. Launch test instances
    instances = launch_test_instances()
    
    # 4. Run validation tests
    tests_passed = run_validation_tests(instances, restored_db)
    
    # 5. Clean up
    cleanup_test_resources(instances, restored_db)
    
    # 6. Report results
    send_report({
        'tests_passed': tests_passed,
        'rto_achieved': calculate_rto(),
        'rpo_achieved': calculate_rpo()
    })
```

---

## Best Practices

**1. Automate Everything**
- Automated backups
- Automated failover
- Automated testing

**2. Monitor Continuously**
- Backup success/failure
- Replication lag
- DR environment health

**3. Document Thoroughly**
- Runbooks
- Contact lists
- Recovery procedures

**4. Test Regularly**
- Scheduled DR drills
- Measure actual RTO/RPO
- Update based on results

**5. Use Multiple Strategies**
- Critical data: Pilot Light or better
- Less critical: Backup and Restore
- Different RPO/RTO for different systems

---

## Cost Comparison

**Example: 100 EC2 instances, 5 TB RDS**

| Strategy | Monthly Cost | RTO | RPO |
|----------|--------------|-----|-----|
| Backup & Restore | $500 | 24 hours | 24 hours |
| Pilot Light | $2,000 | 1 hour | 15 minutes |
| Warm Standby | $15,000 | 10 minutes | 1 minute |
| Multi-Site | $30,000 | Seconds | Seconds |

---

## Summary

Choose DR strategy based on RTO/RPO requirements and budget. Backup and Restore for non-critical, Pilot Light for moderate requirements, Warm Standby for low RTO, Multi-Site for mission-critical applications. Test regularly and automate failover.

**Next Chapter:** [23-real-world-project.md](./23-real-world-project.md)

