# Module 10: Terraform Best Practices

## Project Structure

### Recommended Structure

```
my-project/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── backend.tf
│   │   └── dev.tfvars
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── backend.tf
│   │   └── staging.tfvars
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       ├── backend.tf
│       └── prod.tfvars
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── ec2/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   └── rds/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── README.md
├── .gitignore
└── README.md
```

---

## File Organization

### 1. Separate Concerns

**Good structure:**
```
main.tf           # Main resources
variables.tf      # Variable declarations
outputs.tf        # Output declarations
provider.tf       # Provider configuration
backend.tf        # Backend configuration
versions.tf       # Version constraints
```

**Bad structure:**
```
everything.tf     # All code in one file ❌
```

### 2. Logical File Names

```
vpc.tf            # VPC resources
ec2.tf            # EC2 instances
rds.tf            # RDS databases
security-groups.tf # Security groups
iam.tf            # IAM roles and policies
```

---

## Naming Conventions

### Resource Names

✅ **Good:**
```hcl
resource "aws_s3_bucket" "app_logs" {
  bucket = "myapp-logs-${var.environment}"
}

resource "aws_instance" "web_server" {
  # ...
}
```

❌ **Bad:**
```hcl
resource "aws_s3_bucket" "bucket1" {  # Too generic
  # ...
}

resource "aws_instance" "MyWebServer" {  # PascalCase (avoid)
  # ...
}
```

### Variable Names

✅ **Good:**
```hcl
variable "instance_type" { }
variable "vpc_cidr_block" { }
variable "enable_monitoring" { }
```

❌ **Bad:**
```hcl
variable "x" { }              # Not descriptive
variable "InstanceType" { }   # Wrong case
variable "flag" { }           # Ambiguous
```

### Naming Convention Summary

- Use `snake_case` for everything
- Be descriptive and specific
- Use prefixes for grouping: `vpc_`, `db_`, `app_`
- Boolean variables: `enable_`, `has_`, `is_`

---

## Code Quality

### 1. Always Use `terraform fmt`

```bash
# Format all files
terraform fmt -recursive

# Check formatting in CI/CD
terraform fmt -check -recursive
```

### 2. Always Use `terraform validate`

```bash
# Validate configuration
terraform validate

# In CI/CD pipeline
terraform init -backend=false
terraform validate
```

### 3. Use Clear Descriptions

✅ **Good:**
```hcl
variable "instance_type" {
  description = "EC2 instance type for web servers (e.g., t3.micro, t3.small)"
  type        = string
}
```

❌ **Bad:**
```hcl
variable "instance_type" {
  type = string
}
```

### 4. Add Comments for Complex Logic

```hcl
# Calculate subnet CIDR blocks dynamically
# First 3 subnets are public (10.0.0.0/24, 10.0.1.0/24, 10.0.2.0/24)
# Next 3 subnets are private (10.0.10.0/24, 10.0.11.0/24, 10.0.12.0/24)
locals {
  public_subnet_cidrs = [
    for i in range(3) :
    cidrsubnet(var.vpc_cidr, 8, i)
  ]
  
  private_subnet_cidrs = [
    for i in range(3) :
    cidrsubnet(var.vpc_cidr, 8, i + 10)
  ]
}
```

---

## Variable Best Practices

### 1. Use Type Constraints

✅ **Good:**
```hcl
variable "instance_count" {
  description = "Number of instances to create"
  type        = number
  
  validation {
    condition     = var.instance_count > 0 && var.instance_count <= 10
    error_message = "Instance count must be between 1 and 10."
  }
}
```

### 2. Provide Sensible Defaults

```hcl
variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "tags" {
  description = "Common resource tags"
  type        = map(string)
  default     = {}
}
```

### 3. Use Validation Rules

```hcl
variable "environment" {
  description = "Environment name"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
```

### 4. Group Related Variables

```hcl
variable "database_config" {
  description = "Database configuration"
  type = object({
    instance_class    = string
    allocated_storage = number
    engine_version    = string
    multi_az          = bool
  })
}
```

---

## State Management

### 1. Always Use Remote State for Production

```hcl
terraform {
  backend "s3" {
    bucket         = "myapp-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "eu-central-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

### 2. Separate State Per Environment

```
environments/
├── dev/
│   └── backend.tf     # → s3://bucket/dev/terraform.tfstate
├── staging/
│   └── backend.tf     # → s3://bucket/staging/terraform.tfstate
└── prod/
    └── backend.tf     # → s3://bucket/prod/terraform.tfstate
```

### 3. Enable State Locking

```hcl
# Create DynamoDB table for locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
}
```

### 4. Never Commit State Files

```
# .gitignore
*.tfstate
*.tfstate.*
*.tfstate.backup
.terraform/
.terraform.lock.hcl  # Optional - team preference
```

---

## Security Best Practices

### 1. Never Hardcode Secrets

❌ **Bad:**
```hcl
resource "aws_db_instance" "db" {
  username = "admin"
  password = "MyPassword123!"  # ❌ Hardcoded secret
}
```

✅ **Good:**
```hcl
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

resource "aws_db_instance" "db" {
  username = "admin"
  password = var.db_password  # ✅ From environment or secrets manager
}
```

### 2. Use Secrets Manager or SSM Parameter Store

```hcl
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/db/password"
}

resource "aws_db_instance" "db" {
  username = "admin"
  password = data.aws_secretsmanager_secret_version.db_password.secret_string
}
```

### 3. Mark Sensitive Variables

```hcl
variable "db_password" {
  type      = string
  sensitive = true
}

output "db_endpoint" {
  value     = aws_db_instance.db.endpoint
  sensitive = false
}

output "db_password" {
  value     = var.db_password
  sensitive = true  # Won't show in logs
}
```

### 4. Don't Commit tfvars with Secrets

```
# .gitignore
secrets.tfvars
*.secret.tfvars
*-secrets.tfvars
```

Use environment variables instead:
```bash
export TF_VAR_db_password="SecurePassword123!"
terraform apply
```

---

## Module Best Practices

### 1. Keep Modules Focused

✅ **Good (single purpose):**
```
modules/
├── vpc/          # Just VPC
├── ec2/          # Just EC2
└── rds/          # Just RDS
```

❌ **Bad (too much):**
```
modules/
└── everything/   # VPC + EC2 + RDS + everything
```

### 2. Version Your Modules

```hcl
module "vpc" {
  source  = "git::https://github.com/myorg/modules.git//vpc?ref=v1.2.0"
  # or
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
}
```

### 3. Document Modules

**modules/vpc/README.md:**
```markdown
# VPC Module

Creates a VPC with public and private subnets.

## Usage

```hcl
module "vpc" {
  source = "./modules/vpc"
  
  vpc_cidr = "10.0.0.0/16"
  availability_zones = ["eu-central-1a", "eu-central-1b"]
}
```

## Inputs

| Name | Description | Type | Default |
|------|-------------|------|---------|
| vpc_cidr | VPC CIDR block | string | - |
| availability_zones | List of AZs | list(string) | - |

## Outputs

| Name | Description |
|------|-------------|
| vpc_id | VPC ID |
| public_subnet_ids | Public subnet IDs |
```

### 4. Use Outputs Generously

```hcl
# modules/vpc/outputs.tf
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.this.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.this.cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}
```

---

## Tagging Strategy

### 1. Consistent Tagging

```hcl
variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "MyApp"
    ManagedBy   = "Terraform"
    Environment = "prod"
    Owner       = "DevOps Team"
    CostCenter  = "Engineering"
  }
}

resource "aws_instance" "server" {
  ami           = "ami-123456"
  instance_type = "t3.micro"
  
  tags = merge(
    var.common_tags,
    {
      Name = "web-server"
      Role = "webserver"
    }
  )
}
```

### 2. Use Locals for Tag Management

```hcl
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = var.owner
  }
}

resource "aws_s3_bucket" "bucket" {
  bucket = "my-bucket"
  tags   = local.common_tags
}

resource "aws_instance" "server" {
  ami  = "ami-123456"
  tags = merge(
    local.common_tags,
    {
      Name = "web-server"
    }
  )
}
```

---

## Version Constraints

### 1. Pin Provider Versions

```hcl
terraform {
  required_version = ">= 1.6.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  # Allow 5.x updates, but not 6.0
    }
  }
}
```

### 2. Use Semantic Versioning

```
"1.2.3"      # Exact version (too restrictive)
">= 1.2.3"   # Greater than or equal (risky)
"~> 1.2.0"   # Allow 1.2.x updates (recommended)
"~> 1.2"     # Allow 1.x updates
```

---

## Testing and Validation

### 1. Pre-commit Checks

Create `.pre-commit.sh`:
```bash
#!/bin/bash

echo "Running Terraform validation..."

terraform fmt -check -recursive
if [ $? -ne 0 ]; then
  echo "❌ Code not formatted. Run: terraform fmt -recursive"
  exit 1
fi

terraform validate
if [ $? -ne 0 ]; then
  echo "❌ Validation failed"
  exit 1
fi

echo "✅ All checks passed"
```

### 2. Always Plan Before Apply

```bash
# Bad workflow
terraform apply -auto-approve

# Good workflow
terraform plan -out=tfplan
# Review the plan
terraform apply tfplan
```

### 3. Use Terraform Plan in CI/CD

```yaml
# GitHub Actions example
- name: Terraform Plan
  run: |
    terraform init
    terraform plan -out=tfplan
    
- name: Save Plan
  uses: actions/upload-artifact@v3
  with:
    name: tfplan
    path: tfplan
```

---

## Performance Tips

### 1. Use `-target` for Specific Resources

```bash
# Only apply changes to specific resource
terraform plan -target=aws_s3_bucket.logs
terraform apply -target=aws_s3_bucket.logs
```

### 2. Use `-parallelism` for Large Deployments

```bash
# Default is 10, increase for faster deployments
terraform apply -parallelism=20
```

### 3. Split Large State Files

Instead of one huge root module:
```
environments/prod/
├── networking/        # VPC, subnets
├── compute/          # EC2, ASG
├── database/         # RDS, ElastiCache
└── storage/          # S3, EFS
```

---

## CI/CD Best Practices

### Typical Workflow

```yaml
name: Terraform

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        
      - name: Terraform Format
        run: terraform fmt -check -recursive
        
      - name: Terraform Init
        run: terraform init
        
      - name: Terraform Validate
        run: terraform validate
        
      - name: Terraform Plan
        run: terraform plan -out=tfplan
        
      - name: Terraform Apply
        if: github.ref == 'refs/heads/main'
        run: terraform apply -auto-approve tfplan
```

---

## Documentation

### 1. Project README

```markdown
# MyApp Infrastructure

Infrastructure as Code for MyApp using Terraform.

## Prerequisites

- Terraform >= 1.6.0
- AWS CLI configured
- Access to AWS account

## Usage

```bash
cd environments/dev
terraform init
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
```

## Structure

- `modules/` - Reusable Terraform modules
- `environments/` - Environment-specific configurations

## Environments

- **dev**: Development environment
- **staging**: Staging environment
- **prod**: Production environment
```

### 2. Module README

Each module should have:
- Purpose
- Usage example
- Input variables table
- Output values table
- Requirements/dependencies

---

## Common Mistakes to Avoid

### ❌ Don't Do This:

1. **Hardcode values**
```hcl
resource "aws_s3_bucket" "bucket" {
  bucket = "my-prod-bucket"  # ❌ Use variables
}
```

2. **Commit secrets**
```bash
git add secrets.tfvars  # ❌ Never commit secrets
```

3. **Edit state manually**
```bash
vim terraform.tfstate  # ❌ Use terraform state commands
```

4. **Skip `terraform plan`**
```bash
terraform apply -auto-approve  # ❌ Always review plans
```

5. **Use default workspace for everything**
```bash
# ❌ Bad
terraform workspace select default
terraform apply  # All environments in one state

# ✅ Good
cd environments/dev
terraform apply
```

---

## Checklist

Before committing code:
- [ ] Run `terraform fmt`
- [ ] Run `terraform validate`
- [ ] Test with `terraform plan`
- [ ] Add/update documentation
- [ ] No secrets in code
- [ ] Add `.tfvars` to `.gitignore` if needed
- [ ] Module has README
- [ ] Variables have descriptions
- [ ] Outputs are documented

---

## Key Takeaways

✅ Use consistent project structure

✅ Separate environments with different state files

✅ Never commit secrets or state files

✅ Always use `terraform plan` before `apply`

✅ Version your modules

✅ Use remote state with locking for teams

✅ Tag all resources consistently

✅ Document everything

✅ Validate and format code automatically

---

## Next Steps

Practice these best practices in real projects and explore advanced topics like CI/CD integration!

**Next:** Continue building real-world projects to solidify these practices.
