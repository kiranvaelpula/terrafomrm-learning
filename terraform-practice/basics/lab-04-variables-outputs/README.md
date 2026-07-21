# Lab 04: Variables and Outputs

**Difficulty**: Beginner  
**Time**: 25 minutes  
**Cost**: Free

## 🎯 Objectives

- Use input variables for configuration
- Understand variable types and validation
- Create meaningful outputs
- Use variable files (.tfvars)
- Implement locals for computed values

## 📋 Prerequisites

- Completed Labs 01-03
- Understanding of basic Terraform syntax

## 🔨 Tasks

### Task 1: Create Variables File

Create `variables.tf`:

```hcl
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "instance_count" {
  description = "Number of EC2 instances to create"
  type        = number
  default     = 1
  validation {
    condition     = var.instance_count > 0 && var.instance_count <= 5
    error_message = "Instance count must be between 1 and 5."
  }
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "enable_monitoring" {
  description = "Enable detailed monitoring"
  type        = bool
  default     = false
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "allowed_ssh_ips" {
  description = "List of IPs allowed to SSH"
  type        = list(string)
  default     = []
}
```

### Task 2: Create terraform.tfvars

Create `terraform.tfvars`:

```hcl
aws_region      = "us-east-1"
environment     = "dev"
project_name    = "terraform-lab"
instance_count  = 2
instance_type   = "t2.micro"
enable_monitoring = true

common_tags = {
  Project     = "Terraform Learning"
  ManagedBy   = "Terraform"
  Owner       = "YourName"
}

allowed_ssh_ips = [
  "YOUR_IP/32"  # Replace with your IP
]
```

### Task 3: Use Locals for Computed Values

In `main.tf`:

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
  region  = var.aws_region
  profile = "terraform_practice"
}

locals {
  # Computed naming convention
  name_prefix = "${var.project_name}-${var.environment}"
  
  # Merge common tags with resource-specific tags
  common_tags = merge(
    var.common_tags,
    {
      Environment = var.environment
      Terraform   = "true"
    }
  )
  
  # Conditional values
  monitoring_enabled = var.environment == "prod" ? true : var.enable_monitoring
}

# Find latest Amazon Linux AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# Security Group
resource "aws_security_group" "main" {
  name        = "${local.name_prefix}-sg"
  description = "Security group for ${var.project_name}"

  dynamic "ingress" {
    for_each = var.allowed_ssh_ips
    content {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
      description = "SSH from ${ingress.value}"
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-sg"
    }
  )
}

# EC2 Instances
resource "aws_instance" "app" {
  count = var.instance_count

  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  
  vpc_security_group_ids = [aws_security_group.main.id]
  monitoring             = local.monitoring_enabled

  tags = merge(
    local.common_tags,
    {
      Name  = "${local.name_prefix}-instance-${count.index + 1}"
      Index = count.index
    }
  )
}
```

### Task 4: Create Comprehensive Outputs

Create `outputs.tf`:

```hcl
output "environment" {
  description = "Current environment"
  value       = var.environment
}

output "instance_ids" {
  description = "IDs of created instances"
  value       = aws_instance.app[*].id
}

output "instance_public_ips" {
  description = "Public IPs of instances"
  value       = aws_instance.app[*].public_ip
}

output "instance_private_ips" {
  description = "Private IPs of instances"
  value       = aws_instance.app[*].private_ip
}

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.main.id
}

output "instance_details" {
  description = "Detailed instance information"
  value = {
    for idx, instance in aws_instance.app : idx => {
      id         = instance.id
      public_ip  = instance.public_ip
      private_ip = instance.private_ip
      az         = instance.availability_zone
    }
  }
}

# Sensitive output example
output "ssh_command" {
  description = "SSH commands to connect to instances"
  value = [
    for instance in aws_instance.app :
    "ssh -i YOUR_KEY.pem ec2-user@${instance.public_ip}"
  ]
}
```

## ✅ Validation Steps

1. **Validate Variables**:
   ```bash
   terraform init
   terraform validate
   ```

2. **Check Plan with Variables**:
   ```bash
   terraform plan
   ```

3. **Try Different Environments**:
   ```bash
   terraform plan -var="environment=prod"
   terraform plan -var="instance_count=3"
   ```

4. **Apply**:
   ```bash
   terraform apply
   ```

5. **View Outputs**:
   ```bash
   terraform output
   terraform output instance_public_ips
   terraform output -json instance_details | jq
   ```

6. **Test Variable Validation**:
   ```bash
   terraform plan -var="environment=test"  # Should fail
   terraform plan -var="instance_count=10" # Should fail
   ```

## 🧹 Cleanup

```bash
terraform destroy
```

## 📚 Key Concepts Learned

- Input variables and types
- Variable validation
- Default values
- Locals for computed values
- Dynamic blocks
- Output values
- Variable files (.tfvars)
- Count and splat expressions
- Complex output structures

## 🎓 Challenge

1. **Add more variable types**:
   - object() for complex structures
   - list(object()) for multiple configurations

2. **Create environment-specific configs**:
   - `dev.tfvars`
   - `prod.tfvars`
   - Apply with: `terraform apply -var-file="prod.tfvars"`

3. **Add conditional resources**:
   - Only create monitoring if environment is prod
   - Different instance types per environment

4. **Add sensitive variables**:
   ```hcl
   variable "db_password" {
     description = "Database password"
     type        = string
     sensitive   = true
   }
   ```

## 💡 Tips

- Use descriptive variable names
- Always add descriptions
- Use validation for important variables
- Keep sensitive values out of .tfvars files
- Use locals for complex computations
- Document variable types clearly

## 📖 Reference

- [Input Variables](https://developer.hashicorp.com/terraform/language/values/variables)
- [Output Values](https://developer.hashicorp.com/terraform/language/values/outputs)
- [Local Values](https://developer.hashicorp.com/terraform/language/values/locals)
- [Variable Validation](https://developer.hashicorp.com/terraform/language/values/variables#custom-validation-rules)
