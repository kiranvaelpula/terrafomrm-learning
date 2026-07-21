# Lab 09: RDS Database with Multi-AZ

**Difficulty**: Intermediate  
**Time**: 35 minutes  
**Cost**: ~$0.05/hour (db.t3.micro in Multi-AZ ~$0.034/hour)

## 🎯 Objectives

- Create RDS MySQL database instance
- Configure Multi-AZ for high availability
- Set up DB subnet group
- Configure security groups for database access
- Use sensitive variables for passwords
- Implement backup and maintenance windows

## 📋 Prerequisites

- Completed Lab 06 (VPC) or have existing VPC
- Understanding of databases and security
- Knowledge of sensitive data handling

## 🏗️ Architecture

```
VPC
├── Private Subnet 1 (AZ-a) ─┐
├── Private Subnet 2 (AZ-b) ─┼─ DB Subnet Group
│                             │
│   RDS Instance (Multi-AZ)  │
│   Primary in AZ-a          │
│   Standby in AZ-b          │
│                             │
└── Security Group ───────────┘
    (Port 3306 from specific SG)
```

## 🔨 Tasks

### Task 1: Create Variables

**variables.tf**:

```hcl
variable "db_name" {
  description = "Name of the database"
  type        = string
  default     = "practicedb"
}

variable "db_username" {
  description = "Master username for the database"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "Master password for the database"
  type        = string
  sensitive   = true
  
  validation {
    condition     = length(var.db_password) >= 8
    error_message = "Password must be at least 8 characters long."
  }
}

variable "db_instance_class" {
  description = "Instance class for RDS"
  type        = string
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

# TODO: Add variables for:
# - multi_az (bool)
# - backup_retention_period
# - vpc_id
# - private_subnet_ids
```

### Task 2: Create terraform.tfvars

**terraform.tfvars**:

```hcl
db_name     = "practicedb"
db_username = "admin"
db_password = "YourSecurePassword123!"  # Change this!

# TODO: Add other variable values
# IMPORTANT: Add terraform.tfvars to .gitignore!
```

**Create .gitignore**:

```
# .gitignore
*.tfstate
*.tfstate.*
.terraform/
terraform.tfvars
*.tfvars
```

### Task 3: Create Security Group

**main.tf**:

```hcl
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = "us-east-1"
  profile = "terraform_practice"
}

# Get VPC information (or use Lab 06 VPC)
data "aws_vpc" "selected" {
  default = true  # Or use specific VPC ID
}

# Get private subnets
data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }
  
  # Filter for private subnets if using custom VPC
  # tags = {
  #   Type = "Private"
  # }
}

# Security group for RDS
resource "aws_security_group" "rds" {
  name        = "rds-practice-sg"
  description = "Security group for RDS instance"
  vpc_id      = data.aws_vpc.selected.id
  
  # Allow MySQL from within VPC
  ingress {
    description = "MySQL from VPC"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.selected.cidr_block]
  }
  
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "RDS Practice SG"
  }
}

# TODO: Create security group for EC2 that can access RDS
# Use this as source in RDS security group instead of CIDR
```

### Task 4: Create DB Subnet Group

```hcl
resource "aws_db_subnet_group" "main" {
  name       = "practice-db-subnet-group"
  subnet_ids = data.aws_subnets.private.ids  # At least 2 subnets required!
  
  tags = {
    Name = "Practice DB Subnet Group"
  }
}
```

### Task 5: Create DB Parameter Group

```hcl
resource "aws_db_parameter_group" "main" {
  name   = "practice-mysql-params"
  family = "mysql8.0"
  
  parameter {
    name  = "character_set_server"
    value = "utf8mb4"
  }
  
  parameter {
    name  = "collation_server"
    value = "utf8mb4_unicode_ci"
  }
  
  # TODO: Add more parameters:
  # - max_connections
  # - slow_query_log
  # - long_query_time
  
  tags = {
    Name = "Practice DB Parameters"
  }
}
```

### Task 6: Create RDS Instance

```hcl
resource "aws_db_instance" "main" {
  identifier        = "practice-mysql-db"
  engine            = "mysql"
  engine_version    = "8.0"
  instance_class    = var.db_instance_class
  allocated_storage = var.allocated_storage
  storage_type      = "gp3"
  storage_encrypted = true
  
  # Database configuration
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  
  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false  # IMPORTANT: Keep databases private!
  
  # High availability
  multi_az = true  # Creates standby in different AZ
  
  # Backup configuration
  backup_retention_period = 7  # Days
  backup_window          = "03:00-04:00"  # UTC
  maintenance_window     = "sun:04:00-sun:05:00"
  
  # Additional configuration
  parameter_group_name = aws_db_parameter_group.main.name
  skip_final_snapshot  = true  # For practice only! Set to false in production
  
  # Deletion protection
  deletion_protection = false  # For practice only!
  
  # Monitoring
  enabled_cloudwatch_logs_exports = ["error", "general", "slowquery"]
  
  tags = {
    Name        = "Practice MySQL Database"
    Environment = "Learning"
  }
}
```

### Task 7: Create Outputs

**outputs.tf**:

```hcl
output "db_instance_endpoint" {
  description = "Connection endpoint for the database"
  value       = aws_db_instance.main.endpoint
}

output "db_instance_address" {
  description = "Address of the RDS instance"
  value       = aws_db_instance.main.address
}

output "db_instance_port" {
  description = "Port the database is listening on"
  value       = aws_db_instance.main.port
}

output "db_instance_name" {
  description = "Name of the database"
  value       = aws_db_instance.main.db_name
}

# Don't output password!
# output "db_password" {
#   value     = var.db_password
#   sensitive = true
# }

output "connection_string" {
  description = "MySQL connection string"
  value       = "mysql -h ${aws_db_instance.main.address} -P ${aws_db_instance.main.port} -u ${var.db_username} -p ${var.db_name}"
  sensitive   = true
}
```

## ✅ Validation Steps

1. **Initialize and apply**:
   ```bash
   terraform init
   terraform fmt
   terraform validate
   terraform plan
   terraform apply
   ```
   
   **Note**: RDS creation takes 5-10 minutes!

2. **Check outputs**:
   ```bash
   terraform output
   terraform output -raw connection_string
   ```

3. **Verify in AWS Console**:
   - RDS → Databases → Your instance
   - Check Multi-AZ is enabled
   - Verify it's in private subnets
   - Check security group rules
   - View monitoring and logs

4. **Test connectivity** (Optional):
   
   Launch EC2 in same VPC:
   
   ```bash
   # Install MySQL client on EC2
   sudo yum install mysql -y
   
   # Connect to RDS
   mysql -h <endpoint> -P 3306 -u admin -p
   # Enter password from terraform.tfvars
   
   # Test commands
   SHOW DATABASES;
   USE practicedb;
   CREATE TABLE test (id INT, name VARCHAR(50));
   INSERT INTO test VALUES (1, 'Terraform');
   SELECT * FROM test;
   ```

## 🧹 Cleanup

**IMPORTANT**: RDS costs money!

```bash
terraform destroy
```

Takes 5-10 minutes to delete.

## 📚 Key Concepts Learned

- RDS instance configuration
- Multi-AZ for high availability
- DB subnet groups (minimum 2 AZs)
- Database security groups
- Sensitive variable handling
- Parameter groups for DB configuration
- Backup and maintenance windows
- Storage encryption
- Connection endpoints

## 🎓 Challenge

1. **Add Read Replica**:
   ```hcl
   resource "aws_db_instance" "replica" {
     identifier             = "practice-mysql-replica"
     replicate_source_db    = aws_db_instance.main.identifier
     instance_class         = var.db_instance_class
     skip_final_snapshot    = true
     publicly_accessible    = false
   }
   ```

2. **Use Secrets Manager for Password**:
   ```hcl
   resource "aws_secretsmanager_secret" "db_password" {
     name = "practice-db-password"
   }
   
   resource "aws_secretsmanager_secret_version" "db_password" {
     secret_id     = aws_secretsmanager_secret.db_password.id
     secret_string = var.db_password
   }
   ```

3. **Add CloudWatch Alarms**:
   - CPU utilization > 80%
   - Free storage < 20%
   - Connection count > 100

4. **Implement Automated Backups to S3**:
   - Enable snapshot export to S3
   - Lifecycle rules for old snapshots

5. **Add Enhanced Monitoring**:
   ```hcl
   resource "aws_db_instance" "main" {
     # ... other config ...
     
     monitoring_interval = 60  # seconds
     monitoring_role_arn = aws_iam_role.rds_monitoring.arn
   }
   ```

## 💡 Tips

- **NEVER** commit passwords to Git (use .gitignore)
- Use AWS Secrets Manager or Parameter Store in production
- Multi-AZ costs ~2x but provides HA
- Set `deletion_protection = true` in production
- Set `skip_final_snapshot = false` in production
- Use encrypted snapshots for backups
- Keep databases in private subnets
- Use specific security groups (not 0.0.0.0/0)
- Enable automated backups (7-35 days retention)
- Monitor database metrics with CloudWatch

## 💰 Cost Breakdown

- db.t3.micro Multi-AZ: ~$0.034/hour (~$25/month)
- Storage (20GB gp3): ~$2.30/month
- Backup storage: First 20GB free
- **Total**: ~$27/month (~$0.037/hour)

**Destroy after practice to avoid charges!**

## 🔒 Security Best Practices

1. **Network Security**:
   - Private subnets only
   - Restrictive security groups
   - No public access

2. **Data Security**:
   - Enable storage encryption
   - Encrypt backups
   - Use SSL for connections

3. **Access Security**:
   - Strong passwords (or Secrets Manager)
   - IAM database authentication
   - Audit logs enabled

4. **Monitoring**:
   - CloudWatch metrics
   - Performance Insights
   - Enhanced monitoring

## 📖 Reference

- [AWS RDS Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_instance)
- [DB Subnet Group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_subnet_group)
- [DB Parameter Group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_parameter_group)
- [RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)

## ✨ Solution

Solution files are in the `solution/` directory. Try completing the lab yourself first!

