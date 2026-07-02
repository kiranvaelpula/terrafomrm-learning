# Module 15: Import Existing Resources

## 📚 What You'll Learn
- Importing existing infrastructure into Terraform
- Using `terraform import` command
- Import blocks (Terraform 1.5+)
- Generating configuration from imports
- Best practices for imports

---

## 🎯 Why Import Resources?

### Common Scenarios:
- 🔄 Migrating from manual infrastructure to IaC
- 📦 Adopting Terraform for existing projects
- 🛠️ Resources created outside Terraform
- 🔧 Recovering from state file loss
- 📝 Bringing ClickOps resources under Terraform management

---

## 🔧 Import Methods

### 1. Classic Import (Pre-1.5)

```bash
terraform import RESOURCE_TYPE.NAME RESOURCE_ID
```

### 2. Import Blocks (Terraform 1.5+)

```hcl
import {
  to = aws_instance.example
  id = "i-1234567890abcdef0"
}
```

---

## 📖 Classic Import Method

### Step-by-Step Process

#### Step 1: Write the Resource Configuration

```hcl
# First, write the resource block (empty or minimal)
resource "aws_instance" "web" {
  # Leave empty for now
}
```

#### Step 2: Import the Resource

```bash
# Import existing EC2 instance
terraform import aws_instance.web i-1234567890abcdef0
```

#### Step 3: Get Resource State

```bash
# Show current state
terraform show

# Or show specific resource
terraform state show aws_instance.web
```

#### Step 4: Update Configuration

```hcl
# Copy attributes from terraform show output
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "Web Server"
  }
  
  # Add other attributes as needed
}
```

#### Step 5: Verify

```bash
# Plan should show no changes
terraform plan
```

---

## 🆕 Import Blocks (Terraform 1.5+)

### Basic Syntax

```hcl
import {
  to = RESOURCE_ADDRESS
  id = RESOURCE_ID
}

resource "RESOURCE_TYPE" "NAME" {
  # Configuration
}
```

### Example: Import EC2 Instance

```hcl
# import.tf
import {
  to = aws_instance.web
  id = "i-1234567890abcdef0"
}

# main.tf
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "Web Server"
  }
}
```

```bash
# Apply the import
terraform plan -generate-config-out=generated.tf
terraform apply
```

---

## 🎪 Lab 1: Import Existing S3 Bucket

### Scenario: Import an existing S3 bucket

#### Step 1: Create S3 Bucket (Simulating existing resource)

```bash
# Create bucket outside Terraform
aws s3api create-bucket \
  --bucket my-existing-bucket-12345 \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-existing-bucket-12345 \
  --versioning-configuration Status=Enabled

# Add tags
aws s3api put-bucket-tagging \
  --bucket my-existing-bucket-12345 \
  --tagging 'TagSet=[{Key=Environment,Value=Production},{Key=ManagedBy,Value=Terraform}]'
```

#### Step 2: Create Terraform Configuration

```hcl
# provider.tf
terraform {
  required_version = ">= 1.5"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}
```

#### Step 3: Import Using Import Block

```hcl
# import.tf
import {
  to = aws_s3_bucket.existing
  id = "my-existing-bucket-12345"
}

import {
  to = aws_s3_bucket_versioning.existing
  id = "my-existing-bucket-12345"
}

# main.tf
resource "aws_s3_bucket" "existing" {
  bucket = "my-existing-bucket-12345"
  
  tags = {
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_versioning" "existing" {
  bucket = aws_s3_bucket.existing.id
  
  versioning_configuration {
    status = "Enabled"
  }
}
```

#### Step 4: Plan and Apply

```bash
# Generate configuration (optional)
terraform plan -generate-config-out=generated.tf

# Review plan
terraform plan

# Apply import
terraform apply

# Verify
terraform state list
```

---

## 🎪 Lab 2: Import Multiple Resources

### Scenario: Import VPC, Subnets, and Security Groups

#### Step 1: Discover Existing Resources

```bash
# Find VPC
aws ec2 describe-vpcs --query 'Vpcs[0].VpcId' --output text
# Output: vpc-1234567890abcdef0

# Find Subnets
aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-1234567890abcdef0" \
  --query 'Subnets[*].[SubnetId,CidrBlock]' --output table

# Find Security Groups
aws ec2 describe-security-groups --filters "Name=vpc-id,Values=vpc-1234567890abcdef0" \
  --query 'SecurityGroups[*].[GroupId,GroupName]' --output table
```

#### Step 2: Create Import Configuration

```hcl
# import.tf
import {
  to = aws_vpc.main
  id = "vpc-1234567890abcdef0"
}

import {
  to = aws_subnet.public_1
  id = "subnet-1234567890abcdef0"
}

import {
  to = aws_subnet.public_2
  id = "subnet-0987654321fedcba0"
}

import {
  to = aws_security_group.web
  id = "sg-1234567890abcdef0"
}
```

#### Step 3: Write Resource Configuration

```hcl
# main.tf
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name      = "main-vpc"
    ManagedBy = "Terraform"
  }
}

resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "public-subnet-1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "public-subnet-2"
  }
}

resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main.id
  
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
  
  tags = {
    Name = "web-sg"
  }
}
```

#### Step 4: Apply

```bash
terraform init
terraform plan
terraform apply

# Verify all resources
terraform state list
```

---

## 🔍 Finding Resource IDs

### AWS Resource ID Patterns

| Resource Type | ID Format | How to Find |
|--------------|-----------|-------------|
| EC2 Instance | `i-*` | `aws ec2 describe-instances` |
| VPC | `vpc-*` | `aws ec2 describe-vpcs` |
| Subnet | `subnet-*` | `aws ec2 describe-subnets` |
| Security Group | `sg-*` | `aws ec2 describe-security-groups` |
| S3 Bucket | `bucket-name` | `aws s3 ls` |
| IAM Role | `role-name` | `aws iam list-roles` |
| RDS Instance | `db-identifier` | `aws rds describe-db-instances` |
| Lambda Function | `function-name` | `aws lambda list-functions` |

### Quick Reference Commands

```bash
# EC2 Instances
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value|[0]]' --output table

# S3 Buckets
aws s3api list-buckets --query 'Buckets[*].Name' --output table

# RDS Instances
aws rds describe-db-instances --query 'DBInstances[*].[DBInstanceIdentifier,Engine]' --output table

# Lambda Functions
aws lambda list-functions --query 'Functions[*].FunctionName' --output table

# Security Groups
aws ec2 describe-security-groups --query 'SecurityGroups[*].[GroupId,GroupName,VpcId]' --output table

# IAM Roles
aws iam list-roles --query 'Roles[*].[RoleName,Arn]' --output table
```

---

## 🔄 Bulk Import Strategy

### 1. Create Import Script

```bash
#!/bin/bash
# import-script.sh

# Array of resources to import
declare -A resources=(
  ["aws_instance.web1"]="i-1234567890abcdef0"
  ["aws_instance.web2"]="i-0987654321fedcba0"
  ["aws_security_group.web"]="sg-1234567890abcdef0"
  ["aws_s3_bucket.data"]="my-data-bucket"
)

# Loop and import
for resource in "${!resources[@]}"; do
  echo "Importing $resource (${resources[$resource]})"
  terraform import "$resource" "${resources[$resource]}"
done
```

### 2. Using Import Blocks (Recommended)

```hcl
# imports.tf
locals {
  instances = {
    web1 = "i-1234567890abcdef0"
    web2 = "i-0987654321fedcba0"
    web3 = "i-abcdef0123456789"
  }
}

# Generate imports dynamically
import {
  for_each = local.instances
  to       = aws_instance.web[each.key]
  id       = each.value
}

# main.tf
resource "aws_instance" "web" {
  for_each = local.instances
  
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "web-${each.key}"
  }
}
```

---

## 🎪 Lab 3: Generate Configuration from Imports

### Using Terraform 1.5+ Config Generation

```hcl
# import.tf
import {
  to = aws_instance.existing
  id = "i-1234567890abcdef0"
}
```

```bash
# Generate configuration automatically
terraform plan -generate-config-out=generated_resources.tf

# Review generated file
cat generated_resources.tf

# The generated file will contain:
# resource "aws_instance" "existing" {
#   ami           = "ami-0c55b159cbfafe1f0"
#   instance_type = "t2.micro"
#   # ... all other attributes
# }

# Apply
terraform apply
```

---

## 🛡️ Import Best Practices

### 1. Start with State List

```bash
# Before importing, check current state
terraform state list

# After import
terraform state list

# Should show new resource
```

### 2. Incremental Import

```hcl
# ✅ Good - Import one resource at a time
import {
  to = aws_instance.web1
  id = "i-1234567890abcdef0"
}

# Test
terraform apply

# Then add next resource
import {
  to = aws_instance.web2
  id = "i-0987654321fedcba0"
}
```

### 3. Use Modules for Organization

```
project/
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   └── imports.tf
│   └── compute/
│       ├── main.tf
│       └── imports.tf
└── main.tf
```

### 4. Document Imported Resources

```hcl
# imported_resources.md

## Imported Resources

### VPC Infrastructure
- VPC: vpc-1234567890abcdef0 (imported: 2024-01-15)
- Subnet 1: subnet-1234567890abcdef0 (imported: 2024-01-15)
- Subnet 2: subnet-0987654321fedcba0 (imported: 2024-01-15)

### Compute
- EC2 web1: i-1234567890abcdef0 (imported: 2024-01-16)
- EC2 web2: i-0987654321fedcba0 (imported: 2024-01-16)
```

### 5. Verify After Import

```bash
# Plan should show no changes
terraform plan

# If changes shown, update configuration
# Then plan again until clean
```

---

## 🔧 Advanced Import Patterns

### 1. Import with Data Sources

```hcl
# Find existing resources
data "aws_instances" "existing" {
  filter {
    name   = "tag:Environment"
    values = ["Production"]
  }
}

# Import them
import {
  for_each = toset(data.aws_instances.existing.ids)
  to       = aws_instance.prod[each.key]
  id       = each.value
}
```

### 2. Conditional Import

```hcl
variable "import_existing" {
  type    = bool
  default = false
}

import {
  count = var.import_existing ? 1 : 0
  to    = aws_instance.web
  id    = "i-1234567890abcdef0"
}
```

### 3. Import with Remote State

```hcl
# Read from remote state
data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "terraform-state"
    key    = "network/terraform.tfstate"
    region = "us-east-1"
  }
}

# Import resources from other state
import {
  to = aws_vpc.imported
  id = data.terraform_remote_state.network.outputs.vpc_id
}
```

---

## 🐛 Common Import Issues

### Issue 1: Resource Already Exists

```
Error: resource already exists in state
```

**Solution:**
```bash
# Remove from state first
terraform state rm aws_instance.web

# Then reimport
terraform import aws_instance.web i-1234567890abcdef0
```

### Issue 2: Wrong Resource Type

```
Error: resource type mismatch
```

**Solution:**
```bash
# Use correct resource type
# Check AWS docs for correct type
terraform import aws_instance.web i-1234567890abcdef0  # Correct
terraform import aws_ec2_instance.web i-1234567890abcdef0  # Wrong
```

### Issue 3: Missing Required Fields

```
Error: configuration requires X but not set
```

**Solution:**
```hcl
# Add required fields to configuration
resource "aws_instance" "web" {
  ami           = "ami-xxx"  # Required
  instance_type = "t2.micro"  # Required
  
  # Import will fill other fields
}
```

---

## 📝 Quiz

1. What are the two methods to import resources?
2. When should you use import blocks vs classic import?
3. How do you find resource IDs?
4. What happens if terraform plan shows changes after import?
5. Can you import resources across providers?

---

## 🎓 Challenge Exercise

Import a complete AWS environment:
1. Import a VPC with 2 subnets
2. Import a security group
3. Import 2 EC2 instances
4. Import an S3 bucket
5. Import an RDS database
6. Ensure `terraform plan` shows no changes

---

## ⏭️ Next Steps

Continue to [Module 16: Security & Secrets Management](./16-security-secrets-management.md)

---

**🎉 Congratulations!** You can now import existing infrastructure into Terraform!
