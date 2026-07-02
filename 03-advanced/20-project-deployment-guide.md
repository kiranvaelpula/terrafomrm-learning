# Module 20: Project Deployment Guide

## 📚 Complete Deployment Walkthrough

This module provides step-by-step instructions to deploy the real-world project from Module 19.

---

## 🎯 Prerequisites

### Required Tools
```bash
# Terraform
terraform --version  # >= 1.5.0

# AWS CLI
aws --version  # >= 2.0

# Git
git --version

# Optional but recommended
tflint --version
pre-commit --version
```

### AWS Account Setup
- AWS Account with admin access
- AWS CLI configured
- S3 bucket for Terraform state
- DynamoDB table for state locking

---

## 📋 Step-by-Step Deployment

### Step 1: Clone and Setup

```bash
# Clone repository
git clone https://github.com/your-org/terraform-webapp.git
cd terraform-webapp

# Install pre-commit hooks
pre-commit install

# Verify structure
tree -L 2
```

### Step 2: Create Backend Infrastructure

```bash
# Run backend setup script
./scripts/setup-backend.sh

# Or manually:
cd bootstrap
terraform init
terraform apply

# Save outputs
export TF_STATE_BUCKET=$(terraform output -raw state_bucket_name)
export TF_LOCK_TABLE=$(terraform output -raw lock_table_name)
```

### Step 3: Configure Environment

```bash
# Choose environment
cd environments/dev  # or staging, prod

# Copy example tfvars
cp terraform.tfvars.example terraform.tfvars

# Edit variables
vim terraform.tfvars
```

### Step 4: Deploy Infrastructure

```bash
# Initialize
terraform init

# Validate
terraform validate

# Plan
terraform plan -out=tfplan

# Review plan carefully
terraform show tfplan

# Apply
terraform apply tfplan

# Save outputs
terraform output > outputs.txt
```

---

## 🎪 Complete Example: Dev Environment

### environments/dev/main.tf

```hcl
terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
  
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-locks"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      Owner       = var.owner
      CostCenter  = var.cost_center
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# Local variables
locals {
  azs = slice(data.aws_availability_zones.available.names, 0, 3)
  
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Networking Module
module "networking" {
  source = "../../modules/networking"
  
  environment            = var.environment
  vpc_cidr               = var.vpc_cidr
  availability_zones     = local.azs
  public_subnet_cidrs    = var.public_subnet_cidrs
  private_subnet_cidrs   = var.private_subnet_cidrs
  database_subnet_cidrs  = var.database_subnet_cidrs
  enable_nat_gateway     = var.enable_nat_gateway
  enable_flow_logs       = var.enable_flow_logs
  
  tags = local.common_tags
}

# Compute Module
module "compute" {
  source = "../../modules/compute"
  
  environment          = var.environment
  vpc_id               = module.networking.vpc_id
  public_subnet_ids    = module.networking.public_subnet_ids
  private_subnet_ids   = module.networking.private_subnet_ids
  ami_id               = data.aws_ami.amazon_linux_2.id
  instance_type        = var.instance_type
  asg_min_size         = var.asg_min_size
  asg_max_size         = var.asg_max_size
  asg_desired_capacity = var.asg_desired_capacity
  health_check_path    = var.health_check_path
  allowed_ssh_cidrs    = var.allowed_ssh_cidrs
  
  tags = local.common_tags
}

# Database Module
module "database" {
  source = "../../modules/database"
  
  environment              = var.environment
  vpc_id                   = module.networking.vpc_id
  db_subnet_group_name     = module.networking.db_subnet_group_name
  app_security_group_id    = module.compute.app_security_group_id
  db_instance_class        = var.db_instance_class
  db_allocated_storage     = var.db_allocated_storage
  db_name                  = var.db_name
  db_username              = var.db_username
  multi_az                 = var.db_multi_az
  backup_retention_period  = var.db_backup_retention_period
  
  tags = local.common_tags
}

# Storage Module
module "storage" {
  source = "../../modules/storage"
  
  environment    = var.environment
  bucket_prefix  = var.bucket_prefix
  enable_versioning = var.s3_enable_versioning
  
  tags = local.common_tags
}

# Monitoring Module
module "monitoring" {
  source = "../../modules/monitoring"
  
  environment         = var.environment
  alb_arn_suffix      = module.compute.alb_arn_suffix
  target_group_arn_suffix = module.compute.target_group_arn_suffix
  asg_name            = module.compute.asg_name
  db_instance_id      = module.database.db_instance_id
  alert_email         = var.alert_email
  
  tags = local.common_tags
}
```

### environments/dev/variables.tf

```hcl
# General
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "owner" {
  description = "Owner email"
  type        = string
}

variable "cost_center" {
  description = "Cost center"
  type        = string
}

# Networking
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDRs"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDRs"
  type        = list(string)
}

variable "database_subnet_cidrs" {
  description = "Database subnet CIDRs"
  type        = list(string)
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway"
  type        = bool
  default     = true
}

variable "enable_flow_logs" {
  description = "Enable VPC Flow Logs"
  type        = bool
  default     = true
}

# Compute
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "asg_min_size" {
  description = "ASG minimum size"
  type        = number
}

variable "asg_max_size" {
  description = "ASG maximum size"
  type        = number
}

variable "asg_desired_capacity" {
  description = "ASG desired capacity"
  type        = number
}

variable "health_check_path" {
  description = "Health check path"
  type        = string
  default     = "/health"
}

variable "allowed_ssh_cidrs" {
  description = "Allowed CIDR blocks for SSH"
  type        = list(string)
  default     = []
}

# Database
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
}

variable "db_allocated_storage" {
  description = "RDS allocated storage (GB)"
  type        = number
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "db_username" {
  description = "Database master username"
  type        = string
}

variable "db_multi_az" {
  description = "Enable Multi-AZ"
  type        = bool
}

variable "db_backup_retention_period" {
  description = "Backup retention period (days)"
  type        = number
}

# Storage
variable "bucket_prefix" {
  description = "S3 bucket prefix"
  type        = string
}

variable "s3_enable_versioning" {
  description = "Enable S3 versioning"
  type        = bool
  default     = true
}

# Monitoring
variable "alert_email" {
  description = "Email for alerts"
  type        = string
}
```

### environments/dev/terraform.tfvars

```hcl
# General
aws_region   = "us-east-1"
environment  = "dev"
project_name = "webapp"
owner        = "devops@example.com"
cost_center  = "engineering"

# Networking
vpc_cidr = "10.0.0.0/16"
public_subnet_cidrs = [
  "10.0.1.0/24",
  "10.0.2.0/24",
  "10.0.3.0/24"
]
private_subnet_cidrs = [
  "10.0.11.0/24",
  "10.0.12.0/24",
  "10.0.13.0/24"
]
database_subnet_cidrs = [
  "10.0.21.0/24",
  "10.0.22.0/24",
  "10.0.23.0/24"
]
enable_nat_gateway = true
enable_flow_logs   = false  # Disabled in dev to save costs

# Compute
instance_type        = "t3.micro"
asg_min_size         = 1
asg_max_size         = 3
asg_desired_capacity = 2
health_check_path    = "/health"
allowed_ssh_cidrs    = ["10.0.0.0/16"]  # VPC CIDR only

# Database
db_instance_class          = "db.t3.micro"
db_allocated_storage       = 20
db_name                    = "webapp"
db_username                = "admin"
db_multi_az                = false  # Single AZ in dev
db_backup_retention_period = 1

# Storage
bucket_prefix         = "webapp-dev"
s3_enable_versioning  = false  # Disabled in dev

# Monitoring
alert_email = "devops@example.com"
```

### environments/dev/outputs.tf

```hcl
# Networking Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

output "vpc_cidr" {
  description = "VPC CIDR"
  value       = module.networking.vpc_cidr
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.networking.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.networking.private_subnet_ids
}

# Compute Outputs
output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.compute.alb_dns_name
}

output "alb_url" {
  description = "ALB URL"
  value       = "http://${module.compute.alb_dns_name}"
}

output "asg_name" {
  description = "Auto Scaling Group name"
  value       = module.compute.asg_name
}

# Database Outputs
output "db_endpoint" {
  description = "RDS endpoint"
  value       = module.database.db_endpoint
  sensitive   = true
}

output "db_name" {
  description = "Database name"
  value       = module.database.db_name
}

# Storage Outputs
output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = module.storage.bucket_name
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = module.storage.bucket_arn
}

# Monitoring Outputs
output "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = module.monitoring.sns_topic_arn
}

# Summary Output
output "deployment_summary" {
  description = "Deployment summary"
  value = {
    environment     = var.environment
    vpc_id          = module.networking.vpc_id
    alb_url         = "http://${module.compute.alb_dns_name}"
    db_endpoint     = module.database.db_endpoint
    s3_bucket       = module.storage.bucket_name
    deployed_at     = timestamp()
  }
}
```

---

## 🚀 Deployment Scripts

### scripts/deploy.sh

```bash
#!/bin/bash
set -e

# Configuration
ENVIRONMENT=${1:-dev}
ACTION=${2:-plan}

echo "🚀 Deploying to: $ENVIRONMENT"
echo "📋 Action: $ACTION"

# Navigate to environment directory
cd "environments/$ENVIRONMENT"

# Initialize if needed
if [ ! -d ".terraform" ]; then
    echo "📦 Initializing Terraform..."
    terraform init
fi

# Validate
echo "✅ Validating configuration..."
terraform validate

# Format check
echo "🎨 Checking format..."
terraform fmt -check -recursive || terraform fmt -recursive

# Plan
echo "📊 Planning changes..."
terraform plan -out=tfplan

if [ "$ACTION" = "apply" ]; then
    echo "⚠️  About to apply changes to $ENVIRONMENT"
    read -p "Continue? (yes/no): " -r
    if [ "$REPLY" = "yes" ]; then
        echo "🔨 Applying changes..."
        terraform apply tfplan
        
        echo "✅ Deployment complete!"
        echo "📝 Outputs:"
        terraform output
    else
        echo "❌ Deployment cancelled"
        exit 1
    fi
else
    echo "📋 Plan saved to tfplan"
    echo "Run './scripts/deploy.sh $ENVIRONMENT apply' to apply"
fi
```

### scripts/destroy.sh

```bash
#!/bin/bash
set -e

ENVIRONMENT=${1:-dev}

echo "⚠️  WARNING: About to destroy $ENVIRONMENT environment!"
read -p "Type '$ENVIRONMENT' to confirm: " -r

if [ "$REPLY" != "$ENVIRONMENT" ]; then
    echo "❌ Confirmation failed. Exiting."
    exit 1
fi

cd "environments/$ENVIRONMENT"

echo "🗑️  Destroying infrastructure..."
terraform destroy -auto-approve

echo "✅ Infrastructure destroyed"
```

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] Enable MFA on AWS root account
- [ ] Use IAM roles instead of access keys
- [ ] Enable encryption for S3, RDS, EBS
- [ ] Configure VPC Flow Logs
- [ ] Set up AWS CloudTrail
- [ ] Enable GuardDuty
- [ ] Configure Security Hub
- [ ] Set up AWS Config
- [ ] Enable automated backups
- [ ] Configure WAF rules
- [ ] Set up DDoS protection with Shield
- [ ] Review all security groups
- [ ] Enable RDS encryption
- [ ] Use Secrets Manager for credentials
- [ ] Configure least privilege IAM policies
- [ ] Enable versioning on state bucket
- [ ] Configure MFA delete on state bucket
- [ ] Set up monitoring and alerting
- [ ] Configure log retention policies
- [ ] Enable AWS Config rules
- [ ] Set up incident response procedures

---

## 📊 Monitoring and Maintenance

### Daily Tasks
```bash
# Check application health
curl http://$(terraform output -raw alb_dns_name)/health

# Check CloudWatch dashboards
aws cloudwatch get-dashboard --dashboard-name $ENVIRONMENT-dashboard

# Review recent logs
aws logs tail /aws/ec2/$ENVIRONMENT --follow
```

### Weekly Tasks
```bash
# Review cost
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-08 \
    --granularity DAILY --metrics BlendedCost

# Check for security findings
aws securityhub get-findings --max-items 10

# Review CloudWatch alarms
aws cloudwatch describe-alarms --state-value ALARM
```

### Monthly Tasks
- Review and rotate credentials
- Check for Terraform updates
- Review and update AMIs
- Analyze cost optimization opportunities
- Review security group rules
- Update documentation
- Test disaster recovery procedures
- Review backup retention policies

---

## 🐛 Troubleshooting

### Issue: Terraform State Locked

```bash
# Check lock
aws dynamodb get-item \
    --table-name terraform-state-locks \
    --key '{"LockID": {"S": "myapp-dev/terraform.tfstate"}}'

# Force unlock (use carefully!)
terraform force-unlock <LOCK_ID>
```

### Issue: ASG Instances Failing Health Checks

```bash
# Check target group health
aws elbv2 describe-target-health \
    --target-group-arn $(terraform output -raw target_group_arn)

# SSH to instance (if bastion configured)
aws ssm start-session --target <INSTANCE_ID>

# Check application logs
sudo journalctl -u myapp -f
```

### Issue: RDS Connection Timeout

```bash
# Check security groups
aws ec2 describe-security-groups \
    --group-ids $(terraform output -raw db_security_group_id)

# Test from EC2 instance
telnet $(terraform output -raw db_endpoint | cut -d: -f1) 5432
```

---

## 📚 Additional Resources

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)

---

## 🎓 Final Challenge

Deploy the complete infrastructure to all three environments:
1. Deploy to dev
2. Test thoroughly
3. Promote to staging
4. Run integration tests
5. Deploy to prod with approval
6. Set up monitoring
7. Document everything
8. Create runbook for operations

---

**🎉 Congratulations!** You've completed the Terraform learning path! You're now ready to build production-ready infrastructure as code!

---

## ⏭️ What's Next?

- Get HashiCorp Terraform Associate Certification
- Contribute to open-source Terraform projects
- Build your own modules
- Share your knowledge with others
- Keep learning and stay updated

**Thank you for completing this journey! 🚀**
