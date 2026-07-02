# Module 13: Terraform Workspaces

## 📚 What You'll Learn
- Understanding Terraform workspaces
- Creating and managing workspaces
- Workspace use cases and patterns
- Workspace vs separate state files
- Best practices

---

## 🎯 What are Workspaces?

**Workspaces** allow you to manage multiple instances of the same infrastructure with a single configuration. Each workspace has its own state file.

### Think of it Like This:
- One codebase
- Multiple environments (dev, staging, prod)
- Separate state for each

```
my-infrastructure/
├── main.tf (same code)
└── terraform.tfstate.d/
    ├── dev/terraform.tfstate
    ├── staging/terraform.tfstate
    └── prod/terraform.tfstate
```

---

## 🔧 Workspace Commands

### Basic Commands

```bash
# List workspaces
terraform workspace list

# Show current workspace
terraform workspace show

# Create new workspace
terraform workspace new dev

# Switch to workspace
terraform workspace select dev

# Delete workspace
terraform workspace delete dev
```

### Workspace Workflow

```bash
# Start with default workspace
terraform workspace show
# Output: default

# Create dev workspace
terraform workspace new dev
# Switched to workspace "dev"

# Create resources
terraform apply

# Create staging workspace
terraform workspace new staging
terraform apply

# Switch back to dev
terraform workspace select dev

# List all
terraform workspace list
#   default
# * dev
#   staging
```

---

## 📝 Using Workspaces in Configuration

### 1. Access Current Workspace

```hcl
# Reference current workspace name
resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = "t2.micro"
  
  tags = {
    Name        = "web-${terraform.workspace}"
    Environment = terraform.workspace
  }
}

# Creates:
# - "web-dev" in dev workspace
# - "web-staging" in staging workspace
# - "web-prod" in prod workspace
```

### 2. Environment-Specific Configuration

```hcl
# variables.tf
variable "instance_type" {
  type = map(string)
  default = {
    dev     = "t2.micro"
    staging = "t2.small"
    prod    = "t2.large"
  }
}

variable "instance_count" {
  type = map(number)
  default = {
    dev     = 1
    staging = 2
    prod    = 5
  }
}

# main.tf
resource "aws_instance" "app" {
  count         = var.instance_count[terraform.workspace]
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = var.instance_type[terraform.workspace]
  
  tags = {
    Name        = "app-${terraform.workspace}-${count.index + 1}"
    Environment = terraform.workspace
  }
}
```

### 3. Conditional Resources

```hcl
# Only create in production
resource "aws_db_instance" "prod_db" {
  count = terraform.workspace == "prod" ? 1 : 0
  
  identifier        = "prod-database"
  engine            = "postgres"
  instance_class    = "db.t3.large"
  allocated_storage = 100
}

# Use RDS in prod, SQLite in dev
locals {
  db_endpoint = terraform.workspace == "prod" ? aws_db_instance.prod_db[0].endpoint : "sqlite:///dev.db"
}
```

---

## 🎪 Lab: Multi-Environment Setup

### Objective
Create infrastructure for dev, staging, and prod using workspaces.

### Step 1: Create `variables.tf`

```hcl
variable "environment_config" {
  type = map(object({
    instance_type  = string
    instance_count = number
    db_allocated_storage = number
    enable_monitoring = bool
  }))
  
  default = {
    dev = {
      instance_type        = "t2.micro"
      instance_count       = 1
      db_allocated_storage = 20
      enable_monitoring    = false
    }
    staging = {
      instance_type        = "t2.small"
      instance_count       = 2
      db_allocated_storage = 50
      enable_monitoring    = true
    }
    prod = {
      instance_type        = "t2.large"
      instance_count       = 5
      db_allocated_storage = 100
      enable_monitoring    = true
    }
  }
}

locals {
  config = var.environment_config[terraform.workspace]
}
```

### Step 2: Create `main.tf`

```hcl
provider "aws" {
  region = "us-east-1"
  
  default_tags {
    tags = {
      Environment = terraform.workspace
      ManagedBy   = "Terraform"
      Workspace   = terraform.workspace
    }
  }
}

# Data sources
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security Group
resource "aws_security_group" "app" {
  name_prefix = "${terraform.workspace}-app-"
  description = "Security group for ${terraform.workspace} environment"
  vpc_id      = data.aws_vpc.default.id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

# EC2 Instances
resource "aws_instance" "app" {
  count                  = local.config.instance_count
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = local.config.instance_type
  vpc_security_group_ids = [aws_security_group.app.id]
  subnet_id              = tolist(data.aws_subnets.default.ids)[count.index % length(data.aws_subnets.default.ids)]
  
  monitoring = local.config.enable_monitoring
  
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y httpd
              systemctl start httpd
              systemctl enable httpd
              echo "<h1>Hello from ${terraform.workspace} - Server ${count.index + 1}</h1>" > /var/www/html/index.html
              EOF
  
  tags = {
    Name = "${terraform.workspace}-app-${count.index + 1}"
  }
}

# S3 Bucket
resource "aws_s3_bucket" "data" {
  bucket = "${terraform.workspace}-myapp-data-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  
  versioning_configuration {
    status = terraform.workspace == "prod" ? "Enabled" : "Suspended"
  }
}

# CloudWatch Alarms (only in staging and prod)
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  count               = local.config.enable_monitoring ? local.config.instance_count : 0
  alarm_name          = "${terraform.workspace}-high-cpu-${count.index + 1}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ec2 cpu utilization"
  
  dimensions = {
    InstanceId = aws_instance.app[count.index].id
  }
}

# Data source for account ID
data "aws_caller_identity" "current" {}
```

### Step 3: Create `outputs.tf`

```hcl
output "workspace" {
  value       = terraform.workspace
  description = "Current workspace"
}

output "environment_config" {
  value = {
    instance_type        = local.config.instance_type
    instance_count       = local.config.instance_count
    db_storage           = local.config.db_allocated_storage
    monitoring_enabled   = local.config.enable_monitoring
  }
  description = "Configuration for current environment"
}

output "instance_ids" {
  value       = aws_instance.app[*].id
  description = "IDs of EC2 instances"
}

output "instance_public_ips" {
  value       = aws_instance.app[*].public_ip
  description = "Public IPs of EC2 instances"
}

output "instance_urls" {
  value       = [for ip in aws_instance.app[*].public_ip : "http://${ip}"]
  description = "URLs to access instances"
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.data.id
  description = "S3 bucket name"
}

output "alarms_created" {
  value       = length(aws_cloudwatch_metric_alarm.high_cpu)
  description = "Number of CloudWatch alarms created"
}
```

### Step 4: Deploy to Multiple Workspaces

```bash
# Initialize
terraform init

# Create and deploy to dev
terraform workspace new dev
terraform plan
terraform apply

# Check outputs
terraform output

# Create and deploy to staging
terraform workspace new staging
terraform plan
terraform apply

# Create and deploy to prod
terraform workspace new prod
terraform plan
terraform apply

# List workspaces
terraform workspace list
#   default
#   dev
# * prod
#   staging

# Compare resources
terraform workspace select dev
terraform state list

terraform workspace select prod
terraform state list

# Cleanup specific workspace
terraform workspace select dev
terraform destroy

terraform workspace select staging
terraform destroy

terraform workspace select prod
terraform destroy

# Delete workspaces
terraform workspace select default
terraform workspace delete dev
terraform workspace delete staging
terraform workspace delete prod
```

---

## 🎯 Workspaces with Remote State

### S3 Backend with Workspaces

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "app/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    
    # Workspace state files stored at:
    # env:/dev/app/terraform.tfstate
    # env:/staging/app/terraform.tfstate
    # env:/prod/app/terraform.tfstate
    workspace_key_prefix = "env"
  }
}
```

### Custom Workspace Key Prefix

```hcl
terraform {
  backend "s3" {
    bucket               = "my-terraform-state"
    key                  = "terraform.tfstate"
    workspace_key_prefix = "environments"
  }
}

# Creates:
# environments/dev/terraform.tfstate
# environments/staging/terraform.tfstate
# environments/prod/terraform.tfstate
```

---

## ⚖️ Workspaces vs Separate Directories

### Using Workspaces

```
project/
├── main.tf
├── variables.tf
├── outputs.tf
└── terraform.tfstate.d/
    ├── dev/
    ├── staging/
    └── prod/
```

**Pros:**
- ✅ Single codebase
- ✅ DRY (Don't Repeat Yourself)
- ✅ Easy to switch
- ✅ Less code duplication

**Cons:**
- ❌ Must use conditionals for differences
- ❌ Easy to accidentally affect wrong environment
- ❌ Harder to have completely different configs

### Using Separate Directories

```
project/
├── dev/
│   ├── main.tf
│   ├── variables.tf
│   └── terraform.tfstate
├── staging/
│   ├── main.tf
│   ├── variables.tf
│   └── terraform.tfstate
└── prod/
    ├── main.tf
    ├── variables.tf
    └── terraform.tfstate
```

**Pros:**
- ✅ Complete isolation
- ✅ Different configurations possible
- ✅ Harder to accidentally affect wrong environment
- ✅ Can have different providers/versions

**Cons:**
- ❌ Code duplication
- ❌ Changes must be replicated
- ❌ More maintenance

---

## 🎨 Advanced Patterns

### 1. Dynamic Backend Configuration

```hcl
# backend.tf
terraform {
  backend "s3" {}
}
```

```bash
# backend-dev.tfvars
bucket = "my-terraform-state"
key    = "dev/terraform.tfstate"
region = "us-east-1"

# backend-prod.tfvars  
bucket = "my-terraform-state"
key    = "prod/terraform.tfstate"
region = "us-east-1"

# Initialize with specific backend
terraform init -backend-config=backend-dev.tfvars
```

### 2. Workspace-Specific Variables

```hcl
# terraform.tfvars (default)
region = "us-east-1"

# dev.tfvars
region         = "us-east-1"
instance_type  = "t2.micro"
instance_count = 1

# prod.tfvars
region         = "us-west-2"
instance_type  = "t2.large"
instance_count = 10

# Usage
terraform workspace select dev
terraform apply -var-file="dev.tfvars"

terraform workspace select prod
terraform apply -var-file="prod.tfvars"
```

### 3. Workspace Validation

```hcl
# Ensure only valid workspaces
locals {
  valid_workspaces = ["dev", "staging", "prod"]
  
  # Validate workspace
  validate_workspace = contains(local.valid_workspaces, terraform.workspace)
}

# Use in lifecycle
resource "null_resource" "workspace_validation" {
  lifecycle {
    precondition {
      condition     = local.validate_workspace
      error_message = "Invalid workspace. Must be one of: ${join(", ", local.valid_workspaces)}"
    }
  }
}
```

---

## 💡 Best Practices

### 1. Name Workspaces Clearly

```bash
# ✅ Good
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# ❌ Bad
terraform workspace new test1
terraform workspace new xyz
terraform workspace new temp
```

### 2. Don't Use Default Workspace for Production

```bash
# ❌ Bad - Using default for prod
terraform workspace select default
terraform apply  # affects production!

# ✅ Good - Named workspace
terraform workspace select prod
terraform apply
```

### 3. Document Workspace Usage

```hcl
# README.md

## Workspaces

This project uses Terraform workspaces for environment management.

### Available Workspaces:
- `dev`: Development environment
- `staging`: Staging environment
- `prod`: Production environment

### Usage:
```bash
# Switch to dev
terraform workspace select dev
terraform apply -var-file="dev.tfvars"

# Switch to prod
terraform workspace select prod
terraform apply -var-file="prod.tfvars"
```
```

### 4. Include Workspace in Resource Names

```hcl
# ✅ Good - Clear naming
resource "aws_instance" "web" {
  tags = {
    Name = "${terraform.workspace}-web-server"
  }
}

# ❌ Bad - Ambiguous
resource "aws_instance" "web" {
  tags = {
    Name = "web-server"
  }
}
```

### 5. Protect Production Workspace

```bash
# Add to .gitignore
.terraform/
terraform.tfstate
terraform.tfstate.backup
terraform.tfstate.d/

# CI/CD protection
if [[ "$WORKSPACE" == "prod" && "$BRANCH" != "main" ]]; then
  echo "Production can only be deployed from main branch"
  exit 1
fi
```

---

## 🐛 Common Issues

### Issue 1: Workspace Not Found

```bash
# Error: Workspace "dev" doesn't exist

# Solution: Create it
terraform workspace new dev
```

### Issue 2: Wrong Workspace Active

```bash
# Always check before applying
terraform workspace show

# Switch if needed
terraform workspace select correct-workspace
```

### Issue 3: Can't Delete Active Workspace

```bash
# Error: can't delete active workspace

# Solution: Switch first
terraform workspace select default
terraform workspace delete old-workspace
```

---

## 📝 Quiz

1. What is a Terraform workspace?
2. How do you create a new workspace?
3. How do you reference the current workspace in code?
4. What's the difference between workspaces and separate directories?
5. When should you NOT use workspaces?

---

## 🎓 Challenge Exercise

Create a multi-workspace setup with:
1. Three workspaces: dev, staging, prod
2. Different instance counts per environment
3. Different instance types per environment
4. Conditional monitoring (only staging and prod)
5. Environment-specific S3 buckets
6. Proper tagging with workspace name

---

## ⏭️ Next Steps

Continue to [Module 14: Dynamic Blocks Advanced](./14-dynamic-blocks-advanced.md)

---

**🎉 Congratulations!** You now understand Terraform workspaces and can manage multiple environments with a single configuration!
