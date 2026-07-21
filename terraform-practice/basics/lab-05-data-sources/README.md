# Lab 05: Data Sources and Dependencies

**Difficulty**: Beginner  
**Time**: 20 minutes  
**Cost**: Free (No resources created, only queried)

## 🎯 Objectives

- Understand and use Terraform data sources
- Query existing AWS resources
- Create resource dependencies
- Use data source outputs in resource configuration

## 📋 Prerequisites

- Completed Labs 01-04
- AWS credentials configured
- Understanding of AWS AMIs and availability zones

## 🔨 Tasks

### Task 1: Query AWS AMI

Create `main.tf` and query the latest Amazon Linux 2023 AMI:

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

# TODO: Create data source to find latest Amazon Linux 2023 AMI
# Hint: data "aws_ami" "amazon_linux" { ... }
# Filter by: name = "al2023-ami-*-x86_64"
# owners = ["amazon"]
```

### Task 2: Query Availability Zones

Query available AZs in the region:

```hcl
# TODO: Get list of available availability zones
# Hint: data "aws_availability_zones" "available" { ... }
# Filter: state = "available"
```

### Task 3: Query VPC Information

Get default VPC details:

```hcl
# TODO: Get default VPC information
# Hint: data "aws_vpc" "default" { ... }
```

### Task 4: Create EC2 Using Data Sources

Create an EC2 instance using the queried AMI:

```hcl
# TODO: Create EC2 instance
# Use: ami = data.aws_ami.amazon_linux.id
# Add tags including the AMI name
```

### Task 5: Output Data Source Information

Create `outputs.tf`:

```hcl
# Output AMI details
output "ami_id" {
  description = "ID of the Amazon Linux 2023 AMI"
  value       = # TODO
}

output "ami_name" {
  description = "Name of the AMI"
  value       = # TODO
}

# Output AZ information
output "availability_zones" {
  description = "List of available AZs"
  value       = # TODO
}

# Output VPC information
output "default_vpc_id" {
  description = "Default VPC ID"
  value       = # TODO
}
```

## ✅ Validation Steps

1. **Initialize and validate**:
   ```bash
   terraform init
   terraform fmt
   terraform validate
   ```

2. **Plan** (notice data sources are read during plan):
   ```bash
   terraform plan
   ```

3. **Apply**:
   ```bash
   terraform apply
   ```

4. **Check outputs**:
   ```bash
   terraform output
   ```

5. **Verify in Console**:
   - Note the AMI ID from output
   - Go to EC2 → AMIs and search for it
   - Verify it's the latest Amazon Linux 2023

## 🧹 Cleanup

```bash
terraform destroy
```

## 📚 Key Concepts Learned

- Data sources vs. resources
- Querying existing AWS infrastructure
- Using data source outputs in resources
- Implicit dependencies through references
- Dynamic AMI selection

## 🎓 Challenge

Try these additional tasks:
1. Query the latest Ubuntu AMI instead
2. Find all subnets in the default VPC
3. Get current AWS region and account ID using data sources
4. Create a security group and reference the default VPC

**Hints**:
```hcl
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}
```

## 💡 Tips

- Data sources are read-only
- Data sources are refreshed during `terraform plan` and `terraform apply`
- Use data sources to reference existing infrastructure
- Data sources don't create resources, so they're free
- Most AWS resources have corresponding data sources

## 🔍 Common Data Sources

| Data Source | Purpose |
|------------|---------|
| `aws_ami` | Find AMI IDs |
| `aws_availability_zones` | List AZs |
| `aws_vpc` | Get VPC details |
| `aws_subnet` | Get subnet info |
| `aws_security_group` | Reference SGs |
| `aws_caller_identity` | Get AWS account details |
| `aws_region` | Get current region |

## 📖 Reference

- [Terraform Data Sources](https://developer.hashicorp.com/terraform/language/data-sources)
- [AWS AMI Data Source](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ami)
- [AWS Availability Zones](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/availability_zones)

## ✨ Solution

Solution files are in the `solution/` directory. Try completing the lab yourself first!

