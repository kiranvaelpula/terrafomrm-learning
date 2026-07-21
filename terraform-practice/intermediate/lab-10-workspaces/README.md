# Lab 10: Terraform Workspaces

**Difficulty**: Intermediate  
**Time**: 30 minutes  
**Cost**: ~$0.03/hour

## 🎯 Objectives

- Understand Terraform workspaces
- Create and switch between workspaces
- Use workspace-aware resource naming
- Implement environment-specific configurations
- Learn when to use workspaces vs separate states

## 📋 Prerequisites

- Completed basics labs
- Understanding of environments (dev, staging, prod)
- Knowledge of variables and conditionals

## 🏗️ Concept

Workspaces allow you to manage multiple instances of the same infrastructure using a single configuration. Each workspace has its own state file.

```
terraform.tfstate.d/
├── dev/
│   └── terraform.tfstate
├── staging/
│   └── terraform.tfstate
└── prod/
    └── terraform.tfstate
```

## 🔨 Tasks

### Task 1: Create Workspace-Aware Configuration

**variables.tf**:

```hcl
variable "instance_type" {
  description = "EC2 instance type per environment"
  type        = map(string)
  default = {
    dev     = "t3.micro"
    staging = "t3.small"
    prod    = "t3.medium"
  }
}

variable "instance_count" {
  description = "Number of instances per environment"
  type        = map(number)
  default = {
    dev     = 1
    staging = 2
    prod    = 3
  }
}

variable "enable_monitoring" {
  description = "Enable detailed monitoring per environment"
  type        = map(bool)
  default = {
    dev     = false
    staging = true
    prod    = true
  }
}

# TODO: Add more environment-specific variables:
# - backup_retention_days
# - multi_az
# - deletion_protection
```

### Task 2: Create Main Configuration

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

# Get current workspace
locals {
  environment = terraform.workspace
  
  # Common tags for all resources
  common_tags = {
    Environment = local.environment
    Workspace   = terraform.workspace
    ManagedBy   = "Terraform"
    Project     = "WorkspacePractice"
  }
}

# Get latest Amazon Linux AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# Create S3 bucket (workspace-aware naming)
resource "aws_s3_bucket" "app" {
  bucket = "workspace-practice-${local.environment}-yourname-2026"
  
  tags = merge(
    local.common_tags,
    {
      Name = "App Bucket - ${local.environment}"
    }
  )
}

# Create EC2 instances (workspace-aware count)
resource "aws_instance" "app" {
  count = var.instance_count[local.environment]
  
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type[local.environment]
  
  monitoring = var.enable_monitoring[local.environment]
  
  tags = merge(
    local.common_tags,
    {
      Name = "App Server ${count.index + 1} - ${local.environment}"
    }
  )
}

# TODO: Add RDS instance with workspace-aware configuration
# - Multi-AZ only in staging and prod
# - Backup retention: dev=1, staging=7, prod=30
```

### Task 3: Create Outputs

**outputs.tf**:

```hcl
output "workspace" {
  description = "Current workspace"
  value       = terraform.workspace
}

output "environment" {
  description = "Current environment"
  value       = local.environment
}

output "bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.app.id
}

output "instance_ids" {
  description = "EC2 instance IDs"
  value       = aws_instance.app[*].id
}

output "instance_count" {
  description = "Number of instances created"
  value       = length(aws_instance.app)
}

output "instance_types" {
  description = "Instance types by environment"
  value       = var.instance_type[local.environment]
}
```

### Task 4: Work with Workspaces

**Initialize**:

```bash
terraform init
```

**List workspaces** (default exists):

```bash
terraform workspace list
```

**Create dev workspace**:

```bash
terraform workspace new dev
```

**Apply in dev**:

```bash
terraform apply
# Check outputs - 1 t3.micro instance
terraform output
```

**Create staging workspace**:

```bash
terraform workspace new staging
```

**Apply in staging**:

```bash
terraform apply
# Check outputs - 2 t3.small instances
terraform output
```

**Create prod workspace**:

```bash
terraform workspace new prod
terraform apply
# Check outputs - 3 t3.medium instances
terraform output
```

**Switch between workspaces**:

```bash
# List all workspaces
terraform workspace list

# Switch to dev
terraform workspace select dev
terraform output

# Switch to staging
terraform workspace select staging
terraform output

# Switch to prod
terraform workspace select prod
terraform output
```

**Show resources per workspace**:

```bash
terraform workspace select dev
terraform state list

terraform workspace select staging
terraform state list

terraform workspace select prod
terraform state list
```

### Task 5: Conditional Resources Based on Workspace

Add to **main.tf**:

```hcl
# Load balancer only in staging and prod
resource "aws_lb" "app" {
  count = contains(["staging", "prod"], local.environment) ? 1 : 0
  
  name               = "app-lb-${local.environment}"
  internal           = false
  load_balancer_type = "application"
  
  # ... other configuration ...
  
  tags = merge(
    local.common_tags,
    {
      Name = "App LB - ${local.environment}"
    }
  )
}

# CloudWatch alarms only in prod
resource "aws_cloudwatch_metric_alarm" "cpu" {
  count = local.environment == "prod" ? length(aws_instance.app) : 0
  
  alarm_name          = "cpu-high-${count.index}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  
  dimensions = {
    InstanceId = aws_instance.app[count.index].id
  }
  
  tags = local.common_tags
}
```

## ✅ Validation Steps

1. **Verify workspace isolation**:
   ```bash
   # In dev
   terraform workspace select dev
   terraform state list
   # Should see 1 instance + 1 bucket
   
   # In staging
   terraform workspace select staging
   terraform state list
   # Should see 2 instances + 1 bucket
   
   # In prod
   terraform workspace select prod
   terraform state list
   # Should see 3 instances + 1 bucket + alarms
   ```

2. **Verify in AWS Console**:
   - EC2: Should see 6 instances total (1+2+3)
   - S3: Should see 3 buckets (one per environment)
   - Each resource should have correct tags

3. **Test workspace switching**:
   ```bash
   terraform workspace select dev
   terraform output instance_count
   # Should show: 1
   
   terraform workspace select staging
   terraform output instance_count
   # Should show: 2
   
   terraform workspace select prod
   terraform output instance_count
   # Should show: 3
   ```

## 🧹 Cleanup

**Must destroy each workspace separately**:

```bash
terraform workspace select dev
terraform destroy

terraform workspace select staging
terraform destroy

terraform workspace select prod
terraform destroy

# Can't delete current workspace, switch first
terraform workspace select default

# Delete workspaces
terraform workspace delete dev
terraform workspace delete staging
terraform workspace delete prod
```

## 📚 Key Concepts Learned

- Creating and managing workspaces
- Workspace-aware resource naming
- Environment-specific configurations
- Using `terraform.workspace` in code
- Conditional resource creation based on workspace
- Workspace state isolation

## 🎓 Challenge

1. **Add More Environment Logic**:
   ```hcl
   locals {
     is_production = terraform.workspace == "prod"
     is_dev        = terraform.workspace == "dev"
     
     deletion_protection = local.is_production
     backup_enabled      = !local.is_dev
   }
   ```

2. **Use Remote Backend with Workspaces**:
   ```hcl
   terraform {
     backend "s3" {
       bucket         = "terraform-state-yourname-2026"
       key            = "workspaces/terraform.tfstate"
       region         = "us-east-1"
       profile        = "terraform_practice"
       dynamodb_table = "terraform-state-locks"
       
       # workspace_key_prefix changes the S3 path per workspace
       workspace_key_prefix = "env"
     }
   }
   
   # Creates paths like:
   # env/dev/terraform.tfstate
   # env/staging/terraform.tfstate
   # env/prod/terraform.tfstate
   ```

3. **Add Auto Scaling**:
   - Dev: No auto scaling
   - Staging: 2-4 instances
   - Prod: 3-10 instances

4. **Environment-Specific CIDR Blocks**:
   ```hcl
   locals {
     vpc_cidr = {
       dev     = "10.0.0.0/16"
       staging = "10.1.0.0/16"
       prod    = "10.2.0.0/16"
     }
   }
   ```

## 💡 When to Use Workspaces

### ✅ Good Use Cases:
- Development and testing environments
- Short-lived feature environments
- Same infrastructure, different data
- Single team, simple needs

### ❌ When NOT to Use:
- Different AWS accounts per environment
- Different networking (VPC, CIDR)
- Different regions
- Team collaboration (use separate states)
- Production isolation requirements

### Alternative: Separate Directories
```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   └── backend.tf
│   ├── staging/
│   │   ├── main.tf
│   │   └── backend.tf
│   └── prod/
│       ├── main.tf
│       └── backend.tf
└── modules/
    └── app/
```

## 💡 Tips

- Workspace names should be lowercase
- Default workspace can't be deleted
- Each workspace has its own state file
- Use `terraform.workspace` to get current workspace
- Workspaces are NOT suitable for different AWS accounts
- Consider using separate directories for production
- Always tag resources with workspace name
- Use workspace-aware naming to avoid conflicts

## 🆚 Workspaces vs Separate States

| Feature | Workspaces | Separate States |
|---------|-----------|----------------|
| Same config | ✅ Yes | ❌ No (separate dirs) |
| Different AWS accounts | ❌ No | ✅ Yes |
| Team collaboration | ⚠️ Tricky | ✅ Easy |
| Production isolation | ⚠️ Weak | ✅ Strong |
| Complexity | 🟢 Simple | 🟡 Moderate |

## 📖 Reference

- [Terraform Workspaces](https://developer.hashicorp.com/terraform/language/state/workspaces)
- [When to Use Workspaces](https://developer.hashicorp.com/terraform/cli/workspaces)
- [Workspace Commands](https://developer.hashicorp.com/terraform/cli/commands/workspace)

## ✨ Solution

Solution files are in the `solution/` directory. Try completing the lab yourself first!

