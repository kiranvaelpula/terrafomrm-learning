# Lab 07: Creating and Using Terraform Modules

**Difficulty**: Intermediate  
**Time**: 40 minutes  
**Cost**: ~$0.02/hour

## 🎯 Objectives

- Create reusable Terraform modules
- Understand module structure and best practices
- Pass inputs and outputs between modules
- Use local and remote modules
- Version and publish modules

## 📋 Prerequisites

- Completed basics and Lab 06
- Understanding of variables and outputs
- Knowledge of DRY principles

## 🏗️ What You'll Build

Create a reusable S3 bucket module and use it to create multiple buckets with consistent configuration.

## 🔨 Tasks

### Task 1: Create Module Directory Structure

```bash
mkdir -p modules/s3-bucket
cd modules/s3-bucket
```

Create the module structure:
```
modules/
└── s3-bucket/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    └── README.md
```

### Task 2: Create the Module

**modules/s3-bucket/main.tf**:

```hcl
# TODO: Create S3 bucket resource with:
# - Configurable bucket name
# - Configurable versioning
# - Configurable tags
# - Server-side encryption enabled by default

resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  
  tags = merge(
    var.tags,
    {
      ManagedBy = "Terraform"
      Module    = "s3-bucket"
    }
  )
}

# TODO: Add versioning configuration
# Use var.enable_versioning

# TODO: Add server-side encryption
# Use aws_s3_bucket_server_side_encryption_configuration
```

**modules/s3-bucket/variables.tf**:

```hcl
variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
  
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]*[a-z0-9]$", var.bucket_name))
    error_message = "Bucket name must start and end with lowercase letter or number."
  }
}

variable "enable_versioning" {
  description = "Enable versioning for the bucket"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to the bucket"
  type        = map(string)
  default     = {}
}

# TODO: Add more variables:
# - enable_encryption
# - lifecycle_rules
# - cors_configuration
```

**modules/s3-bucket/outputs.tf**:

```hcl
output "bucket_id" {
  description = "ID of the S3 bucket"
  value       = aws_s3_bucket.this.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.this.arn
}

# TODO: Add more outputs:
# - bucket_domain_name
# - bucket_regional_domain_name
```

### Task 3: Use the Module

**main.tf** (in root directory):

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

# Use module to create development bucket
module "dev_bucket" {
  source = "./modules/s3-bucket"
  
  bucket_name       = "my-dev-bucket-yourname-2026"
  enable_versioning = true
  
  tags = {
    Environment = "Development"
    Purpose     = "Learning Modules"
  }
}

# TODO: Create staging bucket using the same module
module "staging_bucket" {
  source = "./modules/s3-bucket"
  
  # Your configuration here
}

# TODO: Create production bucket
module "prod_bucket" {
  source = "./modules/s3-bucket"
  
  # Your configuration here
  # Enable versioning and encryption
}
```

### Task 4: Create Outputs for Module Outputs

**outputs.tf**:

```hcl
output "dev_bucket_id" {
  description = "Development bucket ID"
  value       = module.dev_bucket.bucket_id
}

output "dev_bucket_arn" {
  description = "Development bucket ARN"
  value       = module.dev_bucket.bucket_arn
}

# TODO: Add outputs for staging and prod buckets
output "all_bucket_ids" {
  description = "All bucket IDs"
  value = {
    dev     = module.dev_bucket.bucket_id
    staging = module.staging_bucket.bucket_id
    prod    = module.prod_bucket.bucket_id
  }
}
```

### Task 5: Advanced - Create VPC Module

Create a VPC module based on Lab 06:

```bash
mkdir -p modules/vpc
```

**modules/vpc/main.tf**:

```hcl
# TODO: Convert Lab 06 VPC code into a reusable module
# - VPC with configurable CIDR
# - Public and private subnets (configurable count)
# - Internet Gateway
# - Optional NAT Gateway
# - Route tables
```

**modules/vpc/variables.tf**:

```hcl
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}

variable "azs" {
  description = "Availability zones"
  type        = list(string)
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
}

# TODO: Add variables for private subnets, NAT, etc.
```

## ✅ Validation Steps

1. **Initialize** (downloads module):
   ```bash
   terraform init
   ```

2. **Validate module**:
   ```bash
   terraform validate
   ```

3. **Plan**:
   ```bash
   terraform plan
   ```
   - Should show 6-9 resources (3 buckets × 2-3 resources each)

4. **Apply**:
   ```bash
   terraform apply
   ```

5. **Check outputs**:
   ```bash
   terraform output
   ```

6. **Verify buckets in console**

7. **Test module reusability**:
   - All three buckets should be created
   - Each should have different tags
   - Configuration should be consistent

## 🧹 Cleanup

```bash
terraform destroy
```

## 📚 Key Concepts Learned

- Module structure (main.tf, variables.tf, outputs.tf)
- Module inputs and outputs
- Module reusability
- Local vs remote modules
- Module composition
- DRY principle in infrastructure code

## 🎓 Challenge

1. **Publish Module to Registry**:
   - Create GitHub repo: `terraform-aws-s3-bucket`
   - Add versioning tags (v1.0.0)
   - Publish to Terraform Registry

2. **Use Published Module**:
   ```hcl
   module "bucket" {
     source  = "your-org/s3-bucket/aws"
     version = "1.0.0"
     
     bucket_name = "example"
   }
   ```

3. **Create EC2 Module**:
   - Instance with security group
   - Configurable instance type
   - User data support
   - Tags

4. **Module Composition**:
   - Create "web-app" module that uses:
     - VPC module
     - EC2 module
     - S3 module

5. **Add Lifecycle Rules**:
   - Transition to IA after 30 days
   - Transition to Glacier after 90 days
   - Expire after 365 days

## 💡 Tips

- Keep modules focused and single-purpose
- Use semantic versioning for modules
- Document modules with README
- Include examples in `examples/` directory
- Use `terraform-docs` to generate documentation
- Pin module versions in production
- Test modules before publishing

## 🗂️ Module Best Practices

### Directory Structure
```
modules/
└── my-module/
    ├── main.tf           # Resources
    ├── variables.tf      # Input variables
    ├── outputs.tf        # Output values
    ├── versions.tf       # Provider requirements
    ├── README.md         # Documentation
    └── examples/         # Usage examples
        └── complete/
            ├── main.tf
            └── outputs.tf
```

### Naming Conventions
- Module names: `terraform-<PROVIDER>-<NAME>`
- Variables: Use clear, descriptive names
- Outputs: Export all useful attributes
- Resources: Use `this` for single resources

### Module Inputs
- Required variables: No default
- Optional variables: Sensible defaults
- Add descriptions to all variables
- Use validation blocks
- Group related variables

### Module Outputs
- Output all useful resource attributes
- Use descriptions
- Consider sensitive outputs

## 📖 Reference

- [Terraform Modules](https://developer.hashicorp.com/terraform/language/modules)
- [Module Structure](https://developer.hashicorp.com/terraform/language/modules/develop/structure)
- [Publishing Modules](https://developer.hashicorp.com/terraform/registry/modules/publish)
- [Module Best Practices](https://www.terraform-best-practices.com/code-structure)

## ✨ Solution

Solution files are in the `solution/` directory. Try completing the lab yourself first!

