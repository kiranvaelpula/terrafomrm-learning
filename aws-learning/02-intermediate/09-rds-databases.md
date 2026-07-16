# Amazon RDS (Relational Database Service)

## Introduction

Amazon RDS is a managed relational database service that makes it easy to set up, operate, and scale databases in the cloud. RDS handles routine database tasks like provisioning, patching, backup, recovery, and scaling, allowing you to focus on your applications.

## Table of Contents
- [What is RDS?](#what-is-rds)
- [RDS Database Engines](#rds-database-engines)
- [RDS vs EC2 Database](#rds-vs-ec2-database)
- [Multi-AZ Deployments](#multi-az-deployments)
- [Read Replicas](#read-replicas)
- [Backups and Recovery](#backups-and-recovery)
- [Parameter Groups](#parameter-groups)
- [Security](#security)
- [Performance Insights](#performance-insights)
- [Hands-on Exercises](#hands-on-exercises)

---

## What is RDS?

### RDS Overview

RDS is a fully managed database service that supports multiple database engines:

```yaml
Key Features:
  - Automated backups
  - Software patching
  - High availability with Multi-AZ
  - Read replicas for scalability
  - Point-in-time recovery
  - Monitoring and metrics
  - Encryption at rest and in transit
  - Automated failover

Benefits:
  - Reduced operational overhead
  - Cost-effective
  - Scalable (vertical and horizontal)
  - Secure
  - Highly available
```

### RDS Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Application                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │           RDS Endpoint            │
        └───────────────┬───────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
   ┌────▼─────┐                  ┌─────▼────┐
   │ Primary  │◄────Sync────────►│ Standby  │
   │ Database │   Replication    │ Database │
   │  (AZ-1)  │                  │  (AZ-2)  │
   └──────────┘                  └──────────┘
   Multi-AZ Deployment
        
        │
   ┌────▼──────┐
   │ Read      │  Async Replication
   │ Replica   │◄──────────┐
   │  (AZ-3)   │           │
   └───────────┘      From Primary
```

---

## RDS Database Engines

### Supported Engines

RDS supports six database engines:

```yaml
1. MySQL:
   - Version: 5.7, 8.0
   - Use Cases: Web applications, e-commerce
   - Max Storage: 64 TiB
   - Max IOPS: 256,000
   
2. PostgreSQL:
   - Version: 11, 12, 13, 14, 15
   - Use Cases: Complex queries, JSON data
   - Max Storage: 64 TiB
   - Max IOPS: 256,000
   
3. MariaDB:
   - Version: 10.4, 10.5, 10.6
   - Use Cases: MySQL replacement
   - Max Storage: 64 TiB
   
4. Oracle:
   - Edition: SE, EE, SE1, SE2
   - License: BYOL or License Included
   - Use Cases: Enterprise applications
   - Max Storage: 64 TiB
   
5. Microsoft SQL Server:
   - Edition: Express, Web, Standard, Enterprise
   - Version: 2016, 2017, 2019, 2022
   - Use Cases: .NET applications
   - Max Storage: 16 TiB
   
6. Amazon Aurora:
   - MySQL-compatible and PostgreSQL-compatible
   - Cloud-native, up to 5x performance
   - Max Storage: 128 TiB (auto-scaling)
   - Serverless option available
```

### Engine Selection Guide

```yaml
Choose MySQL/MariaDB when:
  - Open-source requirement
  - Web applications
  - Community support needed
  - Cost-effective solution

Choose PostgreSQL when:
  - Complex queries and analytics
  - JSON/JSONB support needed
  - Advanced indexing required
  - ACID compliance critical

Choose Oracle when:
  - Legacy Oracle applications
  - Advanced Oracle features needed
  - Enterprise support required

Choose SQL Server when:
  - .NET applications
  - Integration with Microsoft stack
  - T-SQL features required

Choose Amazon Aurora when:
  - High performance needed
  - Automatic scaling required
  - Global database needed
  - Best AWS integration
```

---

## RDS vs EC2 Database

### Comparison

```yaml
RDS (Managed):
  Pros:
    - Automated backups
    - Automated patching
    - Multi-AZ high availability
    - Easy scaling
    - Read replicas
    - Monitoring included
  Cons:
    - Limited database access
    - No OS-level access
    - Fewer customization options
    - Higher cost per instance

EC2 Self-Managed:
  Pros:
    - Full control
    - Custom configurations
    - Any database version
    - OS-level access
  Cons:
    - Manual backups
    - Manual patching
    - Self-managed HA
    - More operational overhead
    - You handle all maintenance
```

### Cost Comparison

```bash
# RDS db.t3.medium (2 vCPU, 4GB RAM)
# On-Demand: ~$0.068/hour = ~$50/month
# Reserved 1yr: ~$0.045/hour = ~$33/month

# EC2 t3.medium + EBS + Backups + Labor
# Instance: ~$30/month
# Storage: ~$10/month
# Snapshots: ~$5/month
# Management: Your time
```

---

## Multi-AZ Deployments

###

 Multi-AZ Overview

Multi-AZ provides high availability and failover support:

```yaml
Architecture:
  Primary: Active database in AZ-1
  Standby: Synchronized replica in AZ-2
  Replication: Synchronous (no data loss)
  Failover: Automatic (1-2 minutes)
  Endpoint: Single DNS endpoint
  
Benefits:
  - Increased availability
  - Data redundancy
  - Automatic failover
  - No manual intervention
  - Backups from standby (no performance impact)
  
When to Use:
  - Production workloads
  - Mission-critical applications
  - Compliance requirements
  - High availability needed
```

### Creating Multi-AZ RDS Instance

**AWS Console:**
1. Navigate to RDS → Create database
2. Choose engine (e.g., MySQL)
3. Templates → Production
4. Availability & durability → **Multi-AZ DB instance**
5. Configure instance size and storage
6. Set master username/password
7. Create database

**AWS CLI:**
```bash
# Create Multi-AZ MySQL database
aws rds create-db-instance \
    --db-instance-identifier myapp-prod-db \
    --db-instance-class db.t3.medium \
    --engine mysql \
    --engine-version 8.0.35 \
    --master-username admin \
    --master-user-password MySecurePass123! \
    --allocated-storage 100 \
    --storage-type gp3 \
    --storage-encrypted \
    --multi-az \
    --vpc-security-group-ids sg-0123456789abcdef0 \
    --db-subnet-group-name my-db-subnet-group \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --preferred-maintenance-window "mon:04:00-mon:05:00" \
    --enable-cloudwatch-logs-exports '["error","general","slowquery"]' \
    --tags Key=Environment,Value=Production Key=Application,Value=MyApp

# Check status
aws rds describe-db-instances \
    --db-instance-identifier myapp-prod-db \
    --query 'DBInstances[0].[DBInstanceStatus,MultiAZ,AvailabilityZone]'
```

### Failover Testing

```bash
# Force failover for testing (simulates AZ failure)
aws rds reboot-db-instance \
    --db-instance-identifier myapp-prod-db \
    --force-failover

# Monitor failover progress
aws rds describe-events \
    --source-identifier myapp-prod-db \
    --source-type db-instance \
    --duration 60
```

---

## Read Replicas

### Read Replica Overview

```yaml
Purpose:
  - Scale read workload
  - Offload reporting queries
  - Disaster recovery
  - Near real-time analytics
  
Characteristics:
  - Asynchronous replication
  - Eventually consistent
  - Can be in different region
  - Can be promoted to standalone
  - Up to 5 read replicas per source
  
Use Cases:
  - Read-heavy workloads
  - Business intelligence
  - Analytics queries
  - Geographic distribution
```

### Creating Read Replicas

**AWS CLI:**
```bash
# Create read replica in same region
aws rds create-db-instance-read-replica \
    --db-instance-identifier myapp-read-replica-1 \
    --source-db-instance-identifier myapp-prod-db \
    --db-instance-class db.t3.medium \
    --publicly-accessible false \
    --tags Key=Environment,Value=Production Key=Type,Value=ReadReplica

# Create cross-region read replica
aws rds create-db-instance-read-replica \
    --db-instance-identifier myapp-read-replica-dr \
    --source-db-instance-identifier arn:aws:rds:us-east-1:123456789012:db:myapp-prod-db \
    --db-instance-class db.t3.medium \
    --region us-west-2 \
    --storage-encrypted \
    --kms-key-id arn:aws:kms:us-west-2:123456789012:key/abcd1234

# Promote read replica to standalone
aws rds promote-read-replica \
    --db-instance-identifier myapp-read-replica-dr
```

### Multi-AZ vs Read Replicas

```yaml
Multi-AZ:
  Purpose: High availability
  Replication: Synchronous
  Standby: Not accessible
  Failover: Automatic
  Cost: ~2x single-AZ
  Performance: No read scaling

Read Replicas:
  Purpose: Read scaling
  Replication: Asynchronous
  Replicas: Read-accessible
  Failover: Manual promotion
  Cost: Per replica
  Performance: Scales reads
```

---

## Backups and Recovery

### Automated Backups

```yaml
Automated Backups:
  - Daily full backup
  - Transaction logs every 5 minutes
  - Retention: 1-35 days (default 7)
  - Stored in S3
  - Free backup storage = database size
  - Point-in-time recovery
  
Backup Window:
  - Specify preferred time
  - Takes from standby (Multi-AZ)
  - I/O suspension (Single-AZ)
```

### Manual Snapshots

**AWS CLI:**
```bash
# Create manual snapshot
aws rds create-db-snapshot \
    --db-instance-identifier myapp-prod-db \
    --db-snapshot-identifier myapp-prod-db-snapshot-$(date +%Y%m%d)

# List snapshots
aws rds describe-db-snapshots \
    --db-instance-identifier myapp-prod-db

# Copy snapshot to another region
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier arn:aws:rds:us-east-1:123456789012:snapshot:myapp-prod-db-snapshot-20260716 \
    --target-db-snapshot-identifier myapp-prod-db-snapshot-20260716-dr \
    --region us-west-2 \
    --kms-key-id arn:aws:kms:us-west-2:123456789012:key/abcd1234

# Share snapshot with another account
aws rds modify-db-snapshot-attribute \
    --db-snapshot-identifier myapp-prod-db-snapshot-20260716 \
    --attribute-name restore \
    --values-to-add 987654321098
```


### Point-in-Time Recovery

```bash
# Restore to specific time
aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier myapp-prod-db \
    --target-db-instance-identifier myapp-prod-db-restored \
    --restore-time 2026-07-16T10:30:00Z \
    --db-instance-class db.t3.medium

# Restore to latest restorable time
aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier myapp-prod-db \
    --target-db-instance-identifier myapp-prod-db-latest \
    --use-latest-restorable-time \
    --db-instance-class db.t3.medium
```

### Restore from Snapshot

```bash
# Restore database from snapshot
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier myapp-prod-db-restored \
    --db-snapshot-identifier myapp-prod-db-snapshot-20260716 \
    --db-instance-class db.t3.medium \
    --vpc-security-group-ids sg-0123456789abcdef0 \
    --db-subnet-group-name my-db-subnet-group \
    --multi-az

# Delete snapshot after restore
aws rds delete-db-snapshot \
    --db-snapshot-identifier myapp-prod-db-snapshot-20260715
```

---

## Parameter Groups

### Parameter Group Overview

```yaml
DB Parameter Group:
  - Database engine configuration
  - Controls engine behavior
  - Applied to DB instances
  - Static and dynamic parameters
  
DB Cluster Parameter Group:
  - For Aurora clusters
  - Applies to all cluster instances
```

### Working with Parameter Groups

**AWS CLI:**
```bash
# Create custom parameter group
aws rds create-db-parameter-group \
    --db-parameter-group-name myapp-mysql8-params \
    --db-parameter-group-family mysql8.0 \
    --description "Custom MySQL 8.0 parameters for MyApp"

# Modify parameters
aws rds modify-db-parameter-group \
    --db-parameter-group-name myapp-mysql8-params \
    --parameters \
        "ParameterName=max_connections,ParameterValue=200,ApplyMethod=immediate" \
        "ParameterName=slow_query_log,ParameterValue=1,ApplyMethod=immediate" \
        "ParameterName=long_query_time,ParameterValue=2,ApplyMethod=immediate" \
        "ParameterName=innodb_buffer_pool_size,ParameterValue={DBInstanceClassMemory*3/4},ApplyMethod=pending-reboot"

# Describe parameters
aws rds describe-db-parameters \
    --db-parameter-group-name myapp-mysql8-params \
    --query 'Parameters[?ParameterName==`max_connections`]'

# Apply parameter group to instance
aws rds modify-db-instance \
    --db-instance-identifier myapp-prod-db \
    --db-parameter-group-name myapp-mysql8-params \
    --apply-immediately
```

### Common MySQL Parameters

```yaml
Performance:
  max_connections: 200
  innodb_buffer_pool_size: "{DBInstanceClassMemory*3/4}"
  innodb_log_file_size: 256M
  query_cache_size: 0  # Disabled in MySQL 8.0
  
Logging:
  slow_query_log: 1
  long_query_time: 2
  general_log: 0  # Only enable for debugging
  log_output: FILE
  
Character Set:
  character_set_server: utf8mb4
  collation_server: utf8mb4_unicode_ci
```

---

## Security

### Network Security

```yaml
Security Layers:
  1. VPC: Network isolation
  2. Security Groups: Instance-level firewall
  3. DB Subnet Groups: Subnet placement
  4. Public Access: Enabled/disabled
  5. IAM Database Authentication: AWS IAM integration
```

**AWS CLI:**
```bash
# Create DB subnet group
aws rds create-db-subnet-group \
    --db-subnet-group-name my-db-subnet-group \
    --db-subnet-group-description "Private subnets for RDS" \
    --subnet-ids subnet-0123456789abcdef0 subnet-0987654321fedcba0 \
    --tags Key=Environment,Value=Production

# Modify security groups
aws rds modify-db-instance \
    --db-instance-identifier myapp-prod-db \
    --vpc-security-group-ids sg-0123456789abcdef0 sg-0fedcba9876543210 \
    --apply-immediately
```

### Encryption

```bash
# Create encrypted database
aws rds create-db-instance \
    --db-instance-identifier myapp-encrypted-db \
    --db-instance-class db.t3.medium \
    --engine mysql \
    --master-username admin \
    --master-user-password MySecurePass123! \
    --allocated-storage 100 \
    --storage-encrypted \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/abcd1234-ef56-7890-abcd-ef1234567890

# Enable encryption in-transit (SSL/TLS)
# In parameter group:
aws rds modify-db-parameter-group \
    --db-parameter-group-name myapp-mysql8-params \
    --parameters "ParameterName=require_secure_transport,ParameterValue=1,ApplyMethod=immediate"
```

### IAM Database Authentication

```bash
# Enable IAM authentication
aws rds modify-db-instance \
    --db-instance-identifier myapp-prod-db \
    --enable-iam-database-authentication \
    --apply-immediately

# Create DB user for IAM authentication (in MySQL)
# mysql> CREATE USER 'iamuser' IDENTIFIED WITH AWSAuthenticationPlugin AS 'RDS';
# mysql> GRANT SELECT, INSERT, UPDATE ON myapp.* TO 'iamuser'@'%';

# Generate authentication token
TOKEN=$(aws rds generate-db-auth-token \
    --hostname myapp-prod-db.abcdefgh.us-east-1.rds.amazonaws.com \
    --port 3306 \
    --username iamuser \
    --region us-east-1)

# Connect using token
mysql -h myapp-prod-db.abcdefgh.us-east-1.rds.amazonaws.com \
    -u iamuser \
    --password="$TOKEN" \
    --ssl-ca=/path/to/rds-ca-bundle.pem
```

---

## Performance Insights

### Enabling Performance Insights

```bash
# Enable on existing instance
aws rds modify-db-instance \
    --db-instance-identifier myapp-prod-db \
    --enable-performance-insights \
    --performance-insights-retention-period 7 \
    --apply-immediately

# Create instance with Performance Insights
aws rds create-db-instance \
    --db-instance-identifier myapp-prod-db \
    --db-instance-class db.t3.medium \
    --engine mysql \
    --master-username admin \
    --master-user-password MySecurePass123! \
    --allocated-storage 100 \
    --enable-performance-insights \
    --performance-insights-retention-period 7
```

### Monitoring Queries

**Key Metrics:**
```yaml
Database Load:
  - Average Active Sessions (AAS)
  - Wait events
  - Top SQL queries
  
Performance:
  - CPU utilization
  - Database connections
  - Read/write IOPS
  - Latency
  
Resources:
  - Memory usage
  - Storage usage
  - Network throughput
```

### CloudWatch Metrics

```bash
# Get CPU utilization
aws cloudwatch get-metric-statistics \
    --namespace AWS/RDS \
    --metric-name CPUUtilization \
    --dimensions Name=DBInstanceIdentifier,Value=myapp-prod-db \
    --start-time 2026-07-16T00:00:00Z \
    --end-time 2026-07-16T23:59:59Z \
    --period 3600 \
    --statistics Average

# Get database connections
aws cloudwatch get-metric-statistics \
    --namespace AWS/RDS \
    --metric-name DatabaseConnections \
    --dimensions Name=DBInstanceIdentifier,Value=myapp-prod-db \
    --start-time 2026-07-16T00:00:00Z \
    --end-time 2026-07-16T23:59:59Z \
    --period 300 \
    --statistics Maximum
```

---

## Hands-on Exercises

### Exercise 1: Create Multi-AZ MySQL Database

**Objective:** Set up a production-ready MySQL database with Multi-AZ

**Steps:**
1. Create DB subnet group in private subnets
2. Create security group allowing MySQL port 3306
3. Launch Multi-AZ MySQL 8.0 instance
4. Configure automated backups
5. Enable Performance Insights
6. Test connection

**Solution:**
```bash
# 1. Create DB subnet group
aws rds create-db-subnet-group \
    --db-subnet-group-name myapp-db-subnets \
    --db-subnet-group-description "Private subnets for RDS" \
    --subnet-ids subnet-private1 subnet-private2

# 2. Create security group
SG_ID=$(aws ec2 create-security-group \
    --group-name myapp-rds-sg \
    --description "Security group for RDS MySQL" \
    --vpc-id vpc-0123456789 \
    --output text --query 'GroupId')

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 3306 \
    --source-group sg-app-servers

# 3. Create Multi-AZ RDS instance
aws rds create-db-instance \
    --db-instance-identifier myapp-mysql-prod \
    --db-instance-class db.t3.medium \
    --engine mysql \
    --engine-version 8.0.35 \
    --master-username admin \
    --master-user-password $(openssl rand -base64 32) \
    --allocated-storage 100 \
    --storage-type gp3 \
    --storage-encrypted \
    --multi-az \
    --vpc-security-group-ids $SG_ID \
    --db-subnet-group-name myapp-db-subnets \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --enable-performance-insights \
    --performance-insights-retention-period 7 \
    --enable-cloudwatch-logs-exports '["error","slowquery"]' \
    --tags Key=Environment,Value=Production

# 4. Wait for availability
aws rds wait db-instance-available \
    --db-instance-identifier myapp-mysql-prod

# 5. Get endpoint
aws rds describe-db-instances \
    --db-instance-identifier myapp-mysql-prod \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text
```


### Exercise 2: Configure Read Replicas

**Objective:** Scale read capacity with read replicas

**Steps:**
1. Create read replica from primary database
2. Configure application to use read replica for queries
3. Monitor replication lag
4. Test failover by promoting replica

**Solution:**
```bash
# 1. Create read replica
aws rds create-db-instance-read-replica \
    --db-instance-identifier myapp-mysql-read-1 \
    --source-db-instance-identifier myapp-mysql-prod \
    --db-instance-class db.t3.medium \
    --publicly-accessible false

# 2. Create another read replica in different AZ
aws rds create-db-instance-read-replica \
    --db-instance-identifier myapp-mysql-read-2 \
    --source-db-instance-identifier myapp-mysql-prod \
    --db-instance-class db.t3.medium \
    --availability-zone us-east-1c

# 3. Monitor replication lag
aws cloudwatch get-metric-statistics \
    --namespace AWS/RDS \
    --metric-name ReplicaLag \
    --dimensions Name=DBInstanceIdentifier,Value=myapp-mysql-read-1 \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Average

# 4. Test promoting replica (DR scenario)
aws rds promote-read-replica \
    --db-instance-identifier myapp-mysql-read-2 \
    --backup-retention-period 7
```

### Exercise 3: Implement Backup Strategy

**Objective:** Set up comprehensive backup and recovery plan

**Steps:**
1. Configure automated backups
2. Create manual snapshot
3. Test point-in-time recovery
4. Copy snapshot to another region for DR

**Solution:**
```bash
# 1. Modify backup settings
aws rds modify-db-instance \
    --db-instance-identifier myapp-mysql-prod \
    --backup-retention-period 14 \
    --preferred-backup-window "03:00-04:00" \
    --apply-immediately

# 2. Create manual snapshot
SNAPSHOT_ID="myapp-mysql-prod-manual-$(date +%Y%m%d-%H%M)"
aws rds create-db-snapshot \
    --db-instance-identifier myapp-mysql-prod \
    --db-snapshot-identifier $SNAPSHOT_ID \
    --tags Key=Type,Value=Manual Key=Date,Value=$(date +%Y-%m-%d)

# 3. Test point-in-time recovery (to 1 hour ago)
aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier myapp-mysql-prod \
    --target-db-instance-identifier myapp-mysql-pitr-test \
    --restore-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --db-instance-class db.t3.small \
    --no-multi-az

# 4. Copy snapshot to DR region
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier arn:aws:rds:us-east-1:123456789012:snapshot:$SNAPSHOT_ID \
    --target-db-snapshot-identifier $SNAPSHOT_ID-dr \
    --region us-west-2 \
    --kms-key-id arn:aws:kms:us-west-2:123456789012:key/your-kms-key

# 5. Verify snapshot in DR region
aws rds describe-db-snapshots \
    --db-snapshot-identifier $SNAPSHOT_ID-dr \
    --region us-west-2
```

---

## Amazon Aurora

### Aurora Overview

Aurora is AWS's cloud-native database with MySQL and PostgreSQL compatibility:

```yaml
Key Features:
  - Up to 5x faster than MySQL
  - Up to 3x faster than PostgreSQL
  - 6 copies across 3 AZs
  - Automatic scaling (10GB to 128TB)
  - Up to 15 read replicas
  - Sub-10ms replica lag
  - Backtrack (time travel)
  - Global database (cross-region)
  - Serverless option

Architecture:
  - Storage layer: Shared, distributed
  - Compute layer: Independent instances
  - Automatic replication
  - Continuous backup to S3
```

### Creating Aurora Cluster

```bash
# Create Aurora MySQL cluster
aws rds create-db-cluster \
    --db-cluster-identifier myapp-aurora-cluster \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.04.0 \
    --master-username admin \
    --master-user-password MySecurePass123! \
    --database-name myappdb \
    --vpc-security-group-ids sg-0123456789abcdef0 \
    --db-subnet-group-name myapp-db-subnets \
    --backup-retention-period 7 \
    --storage-encrypted \
    --enable-cloudwatch-logs-exports '["audit","error","slowquery"]'

# Create primary instance
aws rds create-db-instance \
    --db-instance-identifier myapp-aurora-instance-1 \
    --db-instance-class db.r6g.large \
    --engine aurora-mysql \
    --db-cluster-identifier myapp-aurora-cluster \
    --publicly-accessible false

# Create read replica instance
aws rds create-db-instance \
    --db-instance-identifier myapp-aurora-instance-2 \
    --db-instance-class db.r6g.large \
    --engine aurora-mysql \
    --db-cluster-identifier myapp-aurora-cluster \
    --publicly-accessible false
```

### Aurora Serverless

```bash
# Create Aurora Serverless v2 cluster
aws rds create-db-cluster \
    --db-cluster-identifier myapp-aurora-serverless \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.04.0 \
    --master-username admin \
    --master-user-password MySecurePass123! \
    --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=16 \
    --vpc-security-group-ids sg-0123456789abcdef0 \
    --db-subnet-group-name myapp-db-subnets \
    --enable-http-endpoint  # For Data API

# Create serverless instance
aws rds create-db-instance \
    --db-instance-identifier myapp-aurora-serverless-1 \
    --db-instance-class db.serverless \
    --engine aurora-mysql \
    --db-cluster-identifier myapp-aurora-serverless
```

---

## Best Practices

### Performance

```yaml
Instance Sizing:
  - Start with T3 for dev/test
  - Use R6g/R6i for production
  - Monitor CPU, memory, IOPS
  - Scale vertically first
  - Add read replicas for reads

Storage:
  - Use gp3 for general workloads
  - Use io1/io2 for high IOPS
  - Monitor storage metrics
  - Enable auto-scaling

Connection Pooling:
  - Use RDS Proxy
  - Reduces connection overhead
  - Improves failover time
  - Better resource utilization
```

### High Availability

```yaml
Multi-AZ:
  - Always use for production
  - Test failover regularly
  - Monitor replication lag
  - Plan maintenance windows

Backups:
  - Retention: 7-35 days
  - Test restore procedures
  - Cross-region snapshots
  - Document recovery RTO/RPO
```

### Security

```yaml
Network:
  - Use private subnets
  - Restrict security groups
  - Disable public access
  - Use VPC endpoints

Encryption:
  - Enable at-rest encryption
  - Use SSL/TLS in-transit
  - Rotate credentials
  - Use IAM authentication

Access Control:
  - Principle of least privilege
  - Use IAM policies
  - Audit access logs
  - Enable database audit logs
```

### Cost Optimization

```yaml
Instance Selection:
  - Right-size instances
  - Use Reserved Instances (40-60% savings)
  - Consider Aurora Serverless for variable workloads
  - Use graviton instances (R6g) for 20% savings

Storage:
  - Delete unused snapshots
  - Use snapshot lifecycle policies
  - Monitor storage growth
  - Use gp3 instead of io1 when possible

Monitoring:
  - Set up billing alarms
  - Track cost allocation tags
  - Review Cost Explorer reports
  - Identify idle databases
```

---

## Troubleshooting

### Common Issues

**Issue 1: Connection Timeout**
```yaml
Causes:
  - Security group misconfigured
  - DB subnet group incorrect
  - NACLs blocking traffic
  - Instance not available

Solutions:
  - Check security group rules
  - Verify route tables
  - Check NACL rules
  - Verify instance status
```

```bash
# Check instance status
aws rds describe-db-instances \
    --db-instance-identifier myapp-prod-db \
    --query 'DBInstances[0].DBInstanceStatus'

# Verify security group
aws rds describe-db-instances \
    --db-instance-identifier myapp-prod-db \
    --query 'DBInstances[0].VpcSecurityGroups'
```

**Issue 2: High CPU Utilization**
```yaml
Causes:
  - Inefficient queries
  - Missing indexes
  - Insufficient instance size
  - Lock contention

Solutions:
  - Use Performance Insights
  - Optimize queries
  - Add indexes
  - Scale instance
```

```bash
# Check Performance Insights
aws pi get-resource-metrics \
    --service-type RDS \
    --identifier db-ABCDEFGHIJKLMNOP \
    --metric-queries file://pi-query.json \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S)
```

**Issue 3: Storage Full**
```yaml
Causes:
  - Data growth
  - Large transaction logs
  - Snapshot overhead

Solutions:
  - Enable storage auto-scaling
  - Purge old data
  - Optimize tables
  - Increase storage
```

```bash
# Enable storage auto-scaling
aws rds modify-db-instance \
    --db-instance-identifier myapp-prod-db \
    --max-allocated-storage 1000 \
    --apply-immediately

# Check storage metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/RDS \
    --metric-name FreeStorageSpace \
    --dimensions Name=DBInstanceIdentifier,Value=myapp-prod-db \
    --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 3600 \
    --statistics Average
```

---

## Summary

Amazon RDS simplifies database management by automating routine tasks:

```yaml
Key Takeaways:
  - Choose the right engine for your workload
  - Use Multi-AZ for production high availability
  - Implement read replicas for read scaling
  - Configure automated backups and test restores
  - Enable encryption at rest and in transit
  - Use Performance Insights for optimization
  - Consider Aurora for cloud-native performance
  - Implement proper security controls
  - Monitor costs and optimize regularly

Next Steps:
  - Practice creating and configuring RDS instances
  - Test failover scenarios
  - Implement backup and recovery procedures
  - Explore Aurora for high-performance workloads
  - Learn about RDS Proxy for connection pooling
```

**Related Topics:**
- Chapter 06: VPC Networking (for DB subnet groups)
- Chapter 12: CloudWatch Monitoring (for RDS metrics)
- Chapter 13: CloudFormation (for IaC deployment)
- Chapter 16: Security & Secrets Management (for credential management)

---

**Resources:**
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)
- [RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- [Aurora Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/)
- [RDS Pricing](https://aws.amazon.com/rds/pricing/)
