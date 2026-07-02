# Module 08: Introduction to Modules

## What are Terraform Modules?

A module is a **container for multiple resources** that are used together.

Think of modules as **reusable blueprints** for infrastructure.

---

## Why Use Modules?

### Without Modules (Repetitive)

```hcl
# dev/main.tf
resource "aws_vpc" "dev" {
  cidr_block = "10.0.0.0/16"
  tags = { Environment = "dev" }
}

resource "aws_subnet" "dev_public" {
  vpc_id     = aws_vpc.dev.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_subnet" "dev_private" {
  vpc_id     = aws_vpc.dev.id
  cidr_block = "10.0.2.0/24"
}

# 50 more lines...

# prod/main.tf  (duplicate everything, change values)
resource "aws_vpc" "prod" {
  cidr_block = "10.1.0.0/16"
  tags = { Environment = "prod" }
}
# Copy-paste 50 lines again...
```

### With Modules (Reusable)

```hcl
# dev/main.tf
module "vpc" {
  source = "../modules/vpc"
  
  environment = "dev"
  cidr_block  = "10.0.0.0/16"
}

# prod/main.tf
module "vpc" {
  source = "../modules/vpc"
  
  environment = "prod"
  cidr_block  = "10.1.0.0/16"
}
```

**Benefits:**
- ✅ Write once, use many times
- ✅ Easier to maintain
- ✅ Consistent across environments
- ✅ Less code duplication

---

## Types of Modules

### 1. Root Module
The directory where you run `terraform apply` - your main project.

### 2. Child Modules
Modules you create or download to use in your root module.

### 3. Published Modules
Modules from Terraform Registry (community-maintained).

---

## Creating Your First Module

### Project Structure
```
my-project/
├── main.tf              # Root module
├── modules/
│   └── s3-bucket/       # Child module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
```

### Step 1: Create the Module

**modules/s3-bucket/main.tf**
```hcl
resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  
  tags = merge(
    var.tags,
    {
      ManagedBy = "Terraform"
    }
  )
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}
```

**modules/s3-bucket/variables.tf**
```hcl
variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "enable_versioning" {
  description = "Enable bucket versioning"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to bucket"
  type        = map(string)
  default     = {}
}
```

**modules/s3-bucket/outputs.tf**
```hcl
output "bucket_id" {
  description = "ID of the bucket"
  value       = aws_s3_bucket.this.id
}

output "bucket_arn" {
  description = "ARN of the bucket"
  value       = aws_s3_bucket.this.arn
}
```

### Step 2: Use the Module

**main.tf (root module)**
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1"
}

module "app_bucket" {
  source = "./modules/s3-bucket"
  
  bucket_name       = "myapp-data-bucket"
  enable_versioning = true
  
  tags = {
    Environment = "dev"
    Project     = "MyApp"
  }
}

module "logs_bucket" {
  source = "./modules/s3-bucket"
  
  bucket_name       = "myapp-logs-bucket"
  enable_versioning = false
  
  tags = {
    Environment = "dev"
    Project     = "MyApp"
    Purpose     = "Logs"
  }
}
```

### Step 3: Use Module Outputs

```hcl
# Reference outputs from modules
output "app_bucket_arn" {
  value = module.app_bucket.bucket_arn
}

output "logs_bucket_arn" {
  value = module.logs_bucket.bucket_arn
}
```

### Step 4: Deploy

```bash
terraform init    # Downloads module
terraform plan
terraform apply
```

---

## Module Sources

### Local Modules
```hcl
module "vpc" {
  source = "./modules/vpc"
}

module "vpc_relative" {
  source = "../shared-modules/vpc"
}
```

### Terraform Registry
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
}
```

### GitHub
```hcl
module "vpc" {
  source = "github.com/myorg/terraform-modules//vpc?ref=v1.0.0"
}
```

### Git with SSH
```hcl
module "vpc" {
  source = "git@github.com:myorg/terraform-modules.git//vpc?ref=v1.0.0"
}
```

### S3 Bucket
```hcl
module "vpc" {
  source = "s3::https://s3-eu-west-1.amazonaws.com/mybucket/vpc-module.zip"
}
```

---

## Using Public Modules from Terraform Registry

### Example: AWS VPC Module

Visit: https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws

**Usage:**
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["eu-central-1a", "eu-central-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false

  tags = {
    Environment = "dev"
  }
}
```

**Always specify version:**
```hcl
version = "5.0.0"  # Good - pinned version
version = "~> 5.0"  # OK - allows 5.x updates
# No version         # Bad - uses latest (can break)
```

---

## Module Best Practices

### 1. Make Modules Generic and Reusable

❌ **Bad (too specific):**
```hcl
# modules/app-bucket/main.tf
resource "aws_s3_bucket" "this" {
  bucket = "myapp-prod-bucket"  # Hardcoded
}
```

✅ **Good (generic):**
```hcl
# modules/s3-bucket/main.tf
resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name  # Configurable
}
```

### 2. Use Meaningful Variable Names

❌ **Bad:**
```hcl
variable "x" { }
variable "flag" { }
```

✅ **Good:**
```hcl
variable "bucket_name" { }
variable "enable_versioning" { }
```

### 3. Always Provide Outputs

```hcl
# Always output resource IDs, ARNs, etc.
output "bucket_id" {
  value = aws_s3_bucket.this.id
}

output "bucket_arn" {
  value = aws_s3_bucket.this.arn
}
```

### 4. Use Sensible Defaults

```hcl
variable "enable_versioning" {
  type    = bool
  default = false  # Safe default
}

variable "tags" {
  type    = map(string)
  default = {}  # Empty map as default
}
```

### 5. Add Clear Documentation

```hcl
variable "instance_type" {
  description = "EC2 instance type (e.g., t3.micro, t3.small)"
  type        = string
}
```

Create `README.md` in module directory:
```markdown
# S3 Bucket Module

Creates an S3 bucket with optional versioning.

## Usage

```hcl
module "bucket" {
  source = "./modules/s3-bucket"
  
  bucket_name       = "my-bucket"
  enable_versioning = true
}
```

## Inputs

| Name | Description | Type | Default |
|------|-------------|------|---------|
| bucket_name | Name of S3 bucket | string | - |
| enable_versioning | Enable versioning | bool | false |

## Outputs

| Name | Description |
|------|-------------|
| bucket_id | Bucket ID |
| bucket_arn | Bucket ARN |
```

---

## Passing Data Between Modules

### Example: VPC and EC2 Modules

```hcl
module "vpc" {
  source = "./modules/vpc"
  
  cidr_block = "10.0.0.0/16"
}

module "ec2" {
  source = "./modules/ec2"
  
  # Use output from VPC module
  subnet_id = module.vpc.public_subnet_ids[0]
  vpc_id    = module.vpc.vpc_id
}
```

---

## Module Versioning

### For Local Modules
Use Git tags:
```bash
git tag v1.0.0
git push --tags
```

```hcl
module "vpc" {
  source = "git::https://github.com/myorg/modules.git//vpc?ref=v1.0.0"
}
```

### For Registry Modules
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"  # Semantic versioning
}
```

---

## Module Count and For_Each

### Create Multiple Instances of a Module

**Using count:**
```hcl
module "buckets" {
  source = "./modules/s3-bucket"
  count  = 3
  
  bucket_name = "my-bucket-${count.index}"
}

# Access outputs
output "first_bucket_arn" {
  value = module.buckets[0].bucket_arn
}
```

**Using for_each (better):**
```hcl
variable "environments" {
  type = map(object({
    cidr_block = string
  }))
  
  default = {
    dev = {
      cidr_block = "10.0.0.0/16"
    }
    staging = {
      cidr_block = "10.1.0.0/16"
    }
    prod = {
      cidr_block = "10.2.0.0/16"
    }
  }
}

module "vpc" {
  source   = "./modules/vpc"
  for_each = var.environments
  
  name       = each.key
  cidr_block = each.value.cidr_block
}

# Access outputs
output "dev_vpc_id" {
  value = module.vpc["dev"].vpc_id
}
```

---

## Practical Exercise

**Task: Create a reusable EC2 module**

### 1. Create Module Structure
```
my-project/
├── modules/
│   └── ec2-instance/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── main.tf
```

### 2. Create the Module

**modules/ec2-instance/main.tf**
```hcl
resource "aws_instance" "this" {
  ami           = var.ami_id
  instance_type = var.instance_type
  
  tags = merge(
    var.tags,
    {
      Name = var.instance_name
    }
  )
}
```

**modules/ec2-instance/variables.tf**
```hcl
variable "ami_id" {
  description = "AMI ID for instance"
  type        = string
}

variable "instance_type" {
  description = "Instance type"
  type        = string
  default     = "t3.micro"
}

variable "instance_name" {
  description = "Name tag for instance"
  type        = string
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
```

**modules/ec2-instance/outputs.tf**
```hcl
output "instance_id" {
  value = aws_instance.this.id
}

output "public_ip" {
  value = aws_instance.this.public_ip
}
```

### 3. Use the Module

**main.tf**
```hcl
module "web_server" {
  source = "./modules/ec2-instance"
  
  ami_id        = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
  instance_name = "web-server"
  
  tags = {
    Environment = "dev"
    Role        = "webserver"
  }
}

module "db_server" {
  source = "./modules/ec2-instance"
  
  ami_id        = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.small"
  instance_name = "db-server"
  
  tags = {
    Environment = "dev"
    Role        = "database"
  }
}

output "web_server_ip" {
  value = module.web_server.public_ip
}
```

### 4. Deploy
```bash
terraform init
terraform plan
terraform apply
```

---

## Key Takeaways

✅ Modules are reusable infrastructure blueprints

✅ Create modules for commonly used patterns

✅ Use public modules from Terraform Registry

✅ Always version your modules

✅ Pass data between modules using outputs

✅ Make modules generic and configurable

✅ Document module inputs and outputs

---

## Next Steps

Learn about loops and conditionals to make your Terraform code even more powerful!

**Next:** [Module 09: Loops and Conditionals](./09-loops-and-conditionals.md)
