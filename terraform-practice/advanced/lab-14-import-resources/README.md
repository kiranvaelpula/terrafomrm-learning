# Lab 14: Import Existing AWS Resources

**Difficulty**: Advanced  
**Time**: 30 minutes  
**Cost**: Free (using existing resources)

## 🎯 Objectives

- Import existing AWS resources into Terraform state
- Generate configuration from imported resources
- Handle import conflicts and dependencies
- Migrate resources between states
- Understand import limitations

## 📋 Prerequisites

- Completed basics and intermediate labs
- Existing AWS resources (we'll create some first)
- Understanding of Terraform state

## 🔨 Tasks

### Task 1: Create Resources Manually (Outside Terraform)

First, create some resources using AWS CLI to simulate existing infrastructure:

```bash
# Create VPC
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=ExistingVPC}]' \
  --profile terraform_practice \
  --query 'Vpc.VpcId' \
  --output text)

echo "VPC ID: $VPC_ID"

# Create subnet
SUBNET_ID=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=ExistingSubnet}]' \
  --profile terraform_practice \
  --query 'Subnet.SubnetId' \
  --output text)

echo "Subnet ID: $SUBNET_ID"

# Create security group
SG_ID=$(aws ec2 create-security-group \
  --group-name existing-sg \
  --description "Existing security group" \
  --vpc-id $VPC_ID \
  --profile terraform_practice \
  --query 'GroupId' \
  --output text)

echo "Security Group ID: $SG_ID"

# Add rule to security group
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --profile terraform_practice

# Create S3 bucket
BUCKET_NAME="existing-bucket-yourname-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --profile terraform_practice

echo "Bucket Name: $BUCKET_NAME"

# Save IDs for import
echo "VPC_ID=$VPC_ID" > resource_ids.txt
echo "SUBNET_ID=$SUBNET_ID" >> resource_ids.txt
echo "SG_ID=$SG_ID" >> resource_ids.txt
echo "BUCKET_NAME=$BUCKET_NAME" >> resource_ids.txt

cat resource_ids.txt
```

**IMPORTANT**: Save these IDs! You'll need them for import.

### Task 2: Create Terraform Configuration

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

# Empty resource blocks - we'll import into these
resource "aws_vpc" "imported" {
  # Configuration will be added after import
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "ExistingVPC"
  }
}

resource "aws_subnet" "imported" {
  vpc_id            = aws_vpc.imported.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  
  tags = {
    Name = "ExistingSubnet"
  }
}

resource "aws_security_group" "imported" {
  name        = "existing-sg"
  description = "Existing security group"
  vpc_id      = aws_vpc.imported.id
  
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "ExistingSG"
  }
}

resource "aws_s3_bucket" "imported" {
  bucket = "existing-bucket-yourname-TIMESTAMP"  # Replace with actual name!
  
  tags = {
    Name = "ExistingBucket"
  }
}
```

### Task 3: Import Resources (Method 1 - Classic Import)

```bash
# Initialize Terraform
terraform init

# Import VPC
terraform import aws_vpc.imported vpc-XXXXXXXXX

# Import Subnet
terraform import aws_subnet.imported subnet-XXXXXXXXX

# Import Security Group
terraform import aws_security_group.imported sg-XXXXXXXXX

# Import S3 Bucket
terraform import aws_s3_bucket.imported existing-bucket-yourname-TIMESTAMP
```

**After import, verify**:

```bash
terraform state list
terraform state show aws_vpc.imported
```

### Task 4: Generate Configuration from State

After importing, your configuration might not match exactly. Let's generate correct config:

```bash
# Show what Terraform sees
terraform show

# Generate configuration (manually or using tools)
terraform plan
```

If plan shows changes, update your configuration to match:

**Updated main.tf** (example):

```hcl
resource "aws_vpc" "imported" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = false
  enable_dns_support   = true
  
  tags = {
    Name = "ExistingVPC"
  }
}

resource "aws_subnet" "imported" {
  vpc_id                  = aws_vpc.imported.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = false
  
  tags = {
    Name = "ExistingSubnet"
  }
}

# Continue updating other resources...
```

### Task 5: Import with Configuration (Terraform 1.5+)

**New method using import blocks**:

**imports.tf**:

```hcl
import {
  to = aws_vpc.imported
  id = "vpc-XXXXXXXXX"  # Replace with actual VPC ID
}

import {
  to = aws_subnet.imported
  id = "subnet-XXXXXXXXX"  # Replace with actual Subnet ID
}

import {
  to = aws_security_group.imported
  id = "sg-XXXXXXXXX"  # Replace with actual SG ID
}

import {
  to = aws_s3_bucket.imported
  id = "existing-bucket-yourname-TIMESTAMP"  # Replace with actual bucket name
}
```

Then run:

```bash
terraform plan -generate-config-out=generated.tf
```

This generates configuration automatically!

### Task 6: Handle Complex Imports

**Import resources with dependencies**:

```bash
# Create EC2 instance manually
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.micro \
  --subnet-id $SUBNET_ID \
  --security-group-ids $SG_ID \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ExistingInstance}]' \
  --profile terraform_practice \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "Instance ID: $INSTANCE_ID"

# Import EC2 instance
terraform import aws_instance.imported $INSTANCE_ID
```

**main.tf** (add):

```hcl
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "imported" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.imported.id
  vpc_security_group_ids = [aws_security_group.imported.id]
  
  tags = {
    Name = "ExistingInstance"
  }
  
  lifecycle {
    ignore_changes = [ami]  # Prevent replacement if AMI differs
  }
}
```

### Task 7: State Operations After Import

**Move resources in state**:

```bash
# Rename resource in state
terraform state mv aws_vpc.imported aws_vpc.main

# Move to module
terraform state mv aws_subnet.imported module.network.aws_subnet.public
```

**Remove resource from state** (without destroying):

```bash
terraform state rm aws_s3_bucket.imported
```

**Replace provider**:

```bash
terraform state replace-provider \
  registry.terraform.io/-/aws \
  registry.terraform.io/hashicorp/aws
```

## ✅ Validation Steps

1. **Verify import**:
   ```bash
   terraform state list
   # Should show all imported resources
   ```

2. **Check plan shows no changes**:
   ```bash
   terraform plan
   # Should show: "No changes. Your infrastructure matches the configuration."
   ```

3. **Verify state matches AWS**:
   ```bash
   # Check VPC
   terraform state show aws_vpc.imported
   aws ec2 describe-vpcs --vpc-ids $VPC_ID --profile terraform_practice
   
   # Compare values match
   ```

4. **Test Terraform management**:
   ```bash
   # Make a change in Terraform
   # For example, add a tag
   
   terraform apply
   # Should update the resource
   ```

## 🧹 Cleanup

```bash
# Destroy using Terraform (now that resources are imported)
terraform destroy

# Or if you removed from state, delete manually
aws ec2 delete-vpc --vpc-id $VPC_ID --profile terraform_practice
aws s3 rb s3://$BUCKET_NAME --force --profile terraform_practice
```

## 📚 Key Concepts Learned

- Importing existing resources into Terraform
- Generating configuration from state
- Handling import conflicts
- State operations (mv, rm)
- Import limitations and gotchas
- Lifecycle rules to prevent unwanted changes

## 🎓 Challenge

1. **Import Entire Environment**:
   - Import all resources from a dev environment
   - Generate complete configuration
   - Ensure plan shows no changes

2. **Import with Modules**:
   ```bash
   terraform import module.vpc.aws_vpc.main vpc-XXXXXXXXX
   ```

3. **Batch Import Script**:
   ```bash
   #!/bin/bash
   # Read resource IDs from file
   while IFS='=' read -r key value; do
     case $key in
       VPC_ID)
         terraform import aws_vpc.imported $value
         ;;
       SUBNET_ID)
         terraform import aws_subnet.imported $value
         ;;
     esac
   done < resource_ids.txt
   ```

4. **Import RDS with Snapshots**:
   - Import RDS instance
   - Import parameter groups
   - Import subnet groups

5. **Generate Complete Module**:
   - Import multiple related resources
   - Generate module structure
   - Document dependencies

## 💡 Tips

- **ALWAYS** backup state before import operations
- Import into empty resource blocks first
- Run `terraform plan` after import to see differences
- Use `terraform show` to see imported attributes
- Start with simple resources (VPC, S3)
- Handle dependencies in correct order
- Use `-generate-config-out` (Terraform 1.5+) to auto-generate config
- Test imports in non-production first
- Document what was imported and why

## 🚫 Import Limitations

- Can't import resources that don't exist in provider
- Some resources have complex import IDs
- Sensitive data not imported (passwords, keys)
- Resource ordering matters for dependencies
- Not all attributes are imported
- Can't bulk import (one at a time)

## 🔍 Common Import ID Formats

| Resource | Import ID Format |
|----------|------------------|
| VPC | `vpc-xxxxxxxxx` |
| Subnet | `subnet-xxxxxxxxx` |
| EC2 Instance | `i-xxxxxxxxx` |
| Security Group | `sg-xxxxxxxxx` |
| S3 Bucket | `bucket-name` |
| RDS Instance | `database-name` |
| IAM Role | `role-name` |
| Route53 Zone | `zone-id` |

## 📖 Reference

- [Import Command](https://developer.hashicorp.com/terraform/cli/commands/import)
- [Import Blocks (1.5+)](https://developer.hashicorp.com/terraform/language/import)
- [State Commands](https://developer.hashicorp.com/terraform/cli/commands/state)
- [Resource Import](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) (See each resource docs for import format)

## ✨ Solution

Solution files are in the `solution/` directory. Try completing the lab yourself first!

