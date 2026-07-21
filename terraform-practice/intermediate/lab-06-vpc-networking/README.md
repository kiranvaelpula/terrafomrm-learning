# Lab 06: VPC with Public and Private Subnets

**Difficulty**: Intermediate  
**Time**: 45 minutes  
**Cost**: ~$0.10/hour (NAT Gateway ~$0.045/hour)

## 🎯 Objectives

- Create a custom VPC from scratch
- Configure public and private subnets across multiple AZs
- Set up Internet Gateway and NAT Gateway
- Configure route tables properly
- Understand VPC networking concepts

## 📋 Prerequisites

- Completed basics labs
- Understanding of CIDR notation
- Knowledge of public vs private subnets

## 🏗️ Architecture

You'll build:
```
VPC (10.0.0.0/16)
├── Public Subnet 1 (10.0.1.0/24) - us-east-1a
├── Public Subnet 2 (10.0.2.0/24) - us-east-1b
├── Private Subnet 1 (10.0.11.0/24) - us-east-1a
└── Private Subnet 2 (10.0.12.0/24) - us-east-1b

Internet Gateway → Public Subnets
NAT Gateway (in Public Subnet) → Private Subnets
```

## 🔨 Tasks

### Task 1: Create VPC

Create `main.tf`:

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

# TODO: Create VPC with CIDR 10.0.0.0/16
# Enable DNS hostnames and DNS support
resource "aws_vpc" "main" {
  # Your code here
}
```

### Task 2: Create Internet Gateway

```hcl
# TODO: Create Internet Gateway
# Attach to the VPC created above
```

### Task 3: Create Subnets

Create 4 subnets (2 public, 2 private):

```hcl
# Public Subnet 1
resource "aws_subnet" "public_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true  # Important for public subnets!
  
  tags = {
    Name = "Public Subnet 1"
    Type = "Public"
  }
}

# TODO: Create public_2, private_1, private_2
# Private subnets should have map_public_ip_on_launch = false
```

### Task 4: Create NAT Gateway

```hcl
# First, allocate Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  domain = "vpc"
  
  tags = {
    Name = "NAT Gateway EIP"
  }
}

# TODO: Create NAT Gateway
# Place it in public_subnet_1
# Associate the EIP created above
```

### Task 5: Create Route Tables

```hcl
# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = {
    Name = "Public Route Table"
  }
}

# TODO: Create Private Route Table
# Route 0.0.0.0/0 to NAT Gateway (not IGW!)
```

### Task 6: Associate Route Tables

```hcl
# TODO: Associate public route table with both public subnets
# Use aws_route_table_association resource

# TODO: Associate private route table with both private subnets
```

### Task 7: Create Variables

Create `variables.tf`:

```hcl
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
  default     = "terraform-practice"
}

# TODO: Add variables for subnet CIDRs
# TODO: Add variable for availability zones
```

### Task 8: Create Outputs

Create `outputs.tf`:

```hcl
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = [
    aws_subnet.public_1.id,
    aws_subnet.public_2.id
  ]
}

# TODO: Add outputs for:
# - Private subnet IDs
# - NAT Gateway ID
# - Internet Gateway ID
# - VPC CIDR block
```

## ✅ Validation Steps

1. **Initialize and plan**:
   ```bash
   terraform init
   terraform fmt
   terraform validate
   terraform plan
   ```
   - Should show ~13-15 resources to create

2. **Apply**:
   ```bash
   terraform apply
   ```

3. **Verify in AWS Console**:
   - Go to VPC Dashboard
   - Check VPC is created with correct CIDR
   - Verify 4 subnets (2 public, 2 private)
   - Check Internet Gateway is attached
   - Verify NAT Gateway is running
   - Check route tables and associations

4. **Test connectivity** (Optional):
   ```bash
   # Launch EC2 in public subnet - should have internet
   # Launch EC2 in private subnet - should have internet via NAT
   ```

## 🧹 Cleanup

**IMPORTANT**: NAT Gateway costs money even when idle!

```bash
terraform destroy
```

Verify NAT Gateway is deleted in console.

## 📚 Key Concepts Learned

- VPC CIDR planning
- Public vs private subnets
- Internet Gateway for public access
- NAT Gateway for private subnet internet access
- Route tables and associations
- Multi-AZ architecture
- VPC resource dependencies

## 🎓 Challenge

1. **Add VPC Flow Logs**:
   ```hcl
   resource "aws_flow_log" "main" {
     vpc_id          = aws_vpc.main.id
     traffic_type    = "ALL"
     iam_role_arn    = # Create IAM role
     log_destination = # Create CloudWatch log group
   }
   ```

2. **Add Network ACLs**:
   - Create custom NACLs for public and private subnets
   - Add appropriate ingress/egress rules

3. **Add VPC Endpoints**:
   - Create S3 VPC endpoint (Gateway type)
   - No internet charges for S3 traffic!

4. **Make it Multi-Region**:
   - Use variables for region
   - Use data sources for AZ discovery

## 💡 Tips

- NAT Gateway is expensive (~$32/month). Always destroy after practice!
- Use NAT Instance (EC2) for cheaper alternative in practice
- Public subnets MUST have route to Internet Gateway
- Private subnets route through NAT Gateway for outbound internet
- Each subnet exists in exactly one availability zone
- Use /24 CIDR for subnets (256 IPs, ~251 usable)

## 💰 Cost Breakdown

- VPC: Free
- Subnets: Free
- Internet Gateway: Free
- NAT Gateway: ~$0.045/hour + $0.045/GB processed
- **Total for lab**: ~$0.10 for 1-2 hours

## 📖 Reference

- [AWS VPC Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc)
- [AWS Subnet Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet)
- [AWS NAT Gateway](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/nat_gateway)
- [VPC Best Practices](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-design.html)

## ✨ Solution

Solution files are in the `solution/` directory. Try completing the lab yourself first!

