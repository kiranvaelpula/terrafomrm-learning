# Module 06: Variables and Outputs

## Why Variables Matter

Imagine you have the same S3 bucket code for dev, staging, and prod. Without variables:

```hcl
# dev - main.tf
resource "aws_s3_bucket" "app_bucket" {
  bucket = "myapp-dev-bucket"
  tags = {
    Environment = "dev"
  }
}

# staging - main.tf (copy paste, change values)
resource "aws_s3_bucket" "app_bucket" {
  bucket = "myapp-staging-bucket"
  tags = {
    Environment = "staging"
  }
}
```

This is repetitive and error-prone. **Variables solve this!**

---

## Input Variables - Making Code Reusable

### Basic Variable Declaration

Create a file called `variables.tf`:

```hcl
# variables.tf
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}
```

Now use these variables in `main.tf`:

```hcl
# main.tf
resource "aws_s3_bucket" "app_bucket" {
  bucket = var.bucket_name
  
  tags = {
    Environment = var.environment
  }
}
```

**How to reference a variable:** `var.variable_name`

---

## Variable Types

### 1. String
```hcl
variable "bucket_name" {
  type = string
}
```

### 2. Number
```hcl
variable "instance_count" {
  type = number
}
```

### 3. Bool
```hcl
variable "enable_versioning" {
  type = bool
}
```

### 4. List
```hcl
variable "availability_zones" {
  type = list(string)
}

# Usage in code
resource "aws_subnet" "example" {
  count             = length(var.availability_zones)
  availability_zone = var.availability_zones[count.index]
}
```

### 5. Map
```hcl
variable "tags" {
  type = map(string)
}

# Usage
resource "aws_s3_bucket" "example" {
  tags = var.tags
}
```

### 6. Object (Complex)
```hcl
variable "instance_config" {
  type = object({
    instance_type = string
    ami           = string
    disk_size     = number
  })
}

# Usage
resource "aws_instance" "example" {
  instance_type = var.instance_config.instance_type
  ami           = var.instance_config.ami
}
```

---

## Providing Variable Values

### Method 1: Command Line
```bash
terraform apply -var="environment=dev" -var="bucket_name=myapp-dev"
```

### Method 2: Variable Files (Recommended)

Create `dev.tfvars`:
```hcl
environment = "dev"
bucket_name = "myapp-dev-bucket"
```

Apply with:
```bash
terraform apply -var-file="dev.tfvars"
```

**Multiple environments:**
```bash
# dev.tfvars
environment = "dev"
bucket_name = "myapp-dev-bucket"

# staging.tfvars
environment = "staging"
bucket_name = "myapp-staging-bucket"

# prod.tfvars
environment = "prod"
bucket_name = "myapp-prod-bucket"
```

### Method 3: terraform.tfvars (Auto-loaded)

If you name your file `terraform.tfvars`, Terraform loads it automatically:

```hcl
# terraform.tfvars
environment = "dev"
bucket_name = "myapp-dev-bucket"
```

```bash
terraform apply  # Automatically uses terraform.tfvars
```

### Method 4: Environment Variables
```bash
export TF_VAR_environment="dev"
export TF_VAR_bucket_name="myapp-dev-bucket"
terraform apply
```

### Method 5: Default Values
```hcl
variable "environment" {
  type    = string
  default = "dev"
}
```

---

## Variable Validation

Add rules to validate input:

```hcl
variable "environment" {
  type        = string
  description = "Environment name"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
```

**Try it:**
```bash
terraform apply -var="environment=test"
# Error: Environment must be dev, staging, or prod.
```

---

## Sensitive Variables

Mark variables containing secrets as sensitive:

```hcl
variable "database_password" {
  type      = string
  sensitive = true
}
```

**Effect:**
- Terraform won't show the value in logs
- Won't show in `terraform plan` output
- Will show `(sensitive value)` instead

---

## Output Values - Getting Information Out

Outputs let you display useful information after `terraform apply`.

### Basic Output

Create `outputs.tf`:

```hcl
# outputs.tf
output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.app_bucket.bucket
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.app_bucket.arn
}
```

**After apply:**
```bash
terraform apply

Outputs:

bucket_name = "myapp-dev-bucket"
bucket_arn = "arn:aws:s3:::myapp-dev-bucket"
```

### View Outputs Anytime
```bash
terraform output

# Specific output
terraform output bucket_name

# JSON format
terraform output -json
```

---

## Sensitive Outputs

```hcl
output "database_password" {
  value     = aws_db_instance.example.password
  sensitive = true
}
```

**Effect:**
- Hidden in console output
- Still accessible via `terraform output database_password`

---

## Practical Example: Multi-Environment Setup

### File Structure
```
my-project/
├── main.tf           # Resources
├── variables.tf      # Variable declarations
├── outputs.tf        # Output declarations
├── dev.tfvars        # Dev values
├── staging.tfvars    # Staging values
└── prod.tfvars       # Prod values
```

### variables.tf
```hcl
variable "environment" {
  description = "Environment name"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Must be dev, staging, or prod."
  }
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "bucket_prefix" {
  description = "Prefix for bucket names"
  type        = string
}

variable "enable_versioning" {
  description = "Enable S3 versioning"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}
```

### main.tf
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
  region = var.region
}

resource "aws_s3_bucket" "app_bucket" {
  bucket = "${var.bucket_prefix}-${var.environment}"
  
  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}

resource "aws_s3_bucket_versioning" "app_bucket" {
  bucket = aws_s3_bucket.app_bucket.id
  
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}
```

### outputs.tf
```hcl
output "bucket_name" {
  description = "Name of the created bucket"
  value       = aws_s3_bucket.app_bucket.bucket
}

output "bucket_arn" {
  description = "ARN of the bucket"
  value       = aws_s3_bucket.app_bucket.arn
}

output "environment" {
  description = "Current environment"
  value       = var.environment
}
```

### dev.tfvars
```hcl
environment        = "dev"
region            = "eu-central-1"
bucket_prefix     = "myapp"
enable_versioning = false

tags = {
  Project     = "MyApp"
  ManagedBy   = "Terraform"
  CostCenter  = "Engineering"
}
```

### prod.tfvars
```hcl
environment        = "prod"
region            = "eu-central-1"
bucket_prefix     = "myapp"
enable_versioning = true

tags = {
  Project     = "MyApp"
  ManagedBy   = "Terraform"
  CostCenter  = "Engineering"
  Compliance  = "Required"
}
```

### Usage
```bash
# Deploy dev
terraform apply -var-file="dev.tfvars"

# Deploy prod
terraform apply -var-file="prod.tfvars"
```

---

## Variable Precedence (Order of Priority)

Terraform loads variables in this order (later overrides earlier):

1. Environment variables (`TF_VAR_name`)
2. `terraform.tfvars` file
3. `*.auto.tfvars` files (alphabetical order)
4. `-var` and `-var-file` command line flags

**Example:**
```hcl
# variables.tf
variable "environment" {
  default = "dev"  # Priority 1 (lowest)
}

# terraform.tfvars
environment = "staging"  # Priority 2

# Command line
terraform apply -var="environment=prod"  # Priority 3 (highest)

# Result: environment = "prod"
```

---

## Local Values (Intermediate Variables)

Sometimes you need to compute values. Use `locals`:

```hcl
locals {
  bucket_name = "${var.project}-${var.environment}-bucket"
  common_tags = {
    Environment = var.environment
    Project     = var.project
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket" "app" {
  bucket = local.bucket_name
  tags   = local.common_tags
}
```

**Difference between variables and locals:**
- Variables: Input from users
- Locals: Computed internally

---

## Best Practices

### ✅ Do This

```hcl
# Clear descriptions
variable "instance_type" {
  description = "EC2 instance type (e.g., t3.micro, t3.small)"
  type        = string
}

# Use validation
variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Invalid environment."
  }
}

# Provide sensible defaults
variable "region" {
  type    = string
  default = "eu-central-1"
}

# Group related variables
variable "database_config" {
  type = object({
    instance_class = string
    allocated_storage = number
    engine_version = string
  })
}
```

### ❌ Avoid This

```hcl
# No description
variable "x" {
  type = string
}

# Hardcoded values
resource "aws_s3_bucket" "bucket" {
  bucket = "my-hardcoded-bucket-name"  # Use variable instead
}

# Secrets in .tfvars files (in Git)
# Store secrets in environment variables or secret managers
```

---

## Practical Exercise

**Task:** Create a flexible EC2 instance configuration

1. Create `variables.tf` with:
   - `region` (string, default: eu-central-1)
   - `instance_type` (string)
   - `environment` (string with validation)
   - `tags` (map)

2. Create `dev.tfvars` and `prod.tfvars`

3. Create `main.tf` with EC2 instance using variables

4. Create `outputs.tf` with instance ID and public IP

5. Deploy both environments:
   ```bash
   terraform apply -var-file="dev.tfvars"
   terraform apply -var-file="prod.tfvars"
   ```

---

## Key Takeaways

✅ Variables make code reusable across environments

✅ Use `.tfvars` files for different environments

✅ Always add descriptions to variables

✅ Use validation to catch errors early

✅ Mark sensitive data as `sensitive = true`

✅ Outputs show important information after apply

✅ Use `locals` for computed values

---

## Next Steps

Now let's learn about Terraform state management - the heart of how Terraform tracks your infrastructure.

**Next:** [Module 07: Understanding State](./07-understanding-state.md)
