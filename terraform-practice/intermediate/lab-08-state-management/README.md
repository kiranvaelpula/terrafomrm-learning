# Lab 08: State Management and Remote Backend

**Difficulty**: Intermediate  
**Time**: 35 minutes  
**Cost**: ~$0.01/hour (S3 and DynamoDB)

## 🎯 Objectives

- Understand Terraform state files
- Configure S3 remote backend
- Enable state locking with DynamoDB
- Learn state operations (list, show, mv, rm)
- Understand state file security

## 📋 Prerequisites

- Completed basics labs
- Understanding of state purpose
- AWS S3 and DynamoDB basics

## 🏗️ What You'll Build

- S3 bucket for state storage
- DynamoDB table for state locking
- Remote backend configuration
- State operation examples

## 🔨 Tasks

### Task 1: Create Backend Infrastructure

**backend-setup/main.tf**:

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

# S3 bucket for state storage
resource "aws_s3_bucket" "terraform_state" {
  bucket = "terraform-state-yourname-2026"  # MUST be globally unique!
  
  tags = {
    Name        = "Terraform State Bucket"
    Environment = "Practice"
  }
}

# Enable versioning (IMPORTANT for state recovery!)
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB table for state locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-state-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
  
  tags = {
    Name        = "Terraform State Locks"
    Environment = "Practice"
  }
}

# Outputs for backend configuration
output "s3_bucket_name" {
  description = "Name of the S3 bucket for state"
  value       = aws_s3_bucket.terraform_state.id
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for locks"
  value       = aws_dynamodb_table.terraform_locks.name
}
```

**Apply the backend infrastructure**:

```bash
cd backend-setup
terraform init
terraform apply
```

**Note the outputs!** You'll need them for the next step.

### Task 2: Configure Remote Backend

Create a new project directory:

```bash
cd ..
mkdir remote-state-test
cd remote-state-test
```

**backend.tf**:

```hcl
terraform {
  backend "s3" {
    bucket         = "terraform-state-yourname-2026"  # From Task 1 output
    key            = "practice/remote-state-test/terraform.tfstate"
    region         = "us-east-1"
    profile        = "terraform_practice"
    
    # Enable state locking
    dynamodb_table = "terraform-state-locks"  # From Task 1 output
    
    # Enable encryption
    encrypt = true
  }
}
```

**main.tf**:

```hcl
provider "aws" {
  region  = "us-east-1"
  profile = "terraform_practice"
}

# Create a test resource
resource "aws_s3_bucket" "test" {
  bucket = "remote-state-test-yourname-2026"
  
  tags = {
    Name = "Remote State Test"
  }
}

output "bucket_name" {
  value = aws_s3_bucket.test.id
}
```

### Task 3: Initialize with Remote Backend

```bash
terraform init
```

You should see:
```
Initializing the backend...
Successfully configured the backend "s3"!
```

**Verify**:
- Check S3 bucket for state file
- Apply changes and watch DynamoDB for lock

```bash
terraform apply
```

During apply, check DynamoDB console for the lock entry!

### Task 4: State Operations

**List resources in state**:

```bash
terraform state list
```

**Show specific resource**:

```bash
terraform state show aws_s3_bucket.test
```

**Add another resource**:

```hcl
# Add to main.tf
resource "aws_s3_bucket" "test2" {
  bucket = "remote-state-test2-yourname-2026"
  
  tags = {
    Name = "Remote State Test 2"
  }
}
```

```bash
terraform apply
terraform state list
```

**Move resource in state** (rename):

```bash
terraform state mv aws_s3_bucket.test2 aws_s3_bucket.renamed
```

**Remove resource from state** (without destroying):

```bash
terraform state rm aws_s3_bucket.renamed
```

Now the resource exists in AWS but not in Terraform state!

**Pull state to local file**:

```bash
terraform state pull > state.json
cat state.json  # Inspect the state file
```

### Task 5: Migrate from Local to Remote

Create another test project with local state:

```bash
cd ..
mkdir local-state-test
cd local-state-test
```

**main.tf**:

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
  region  = "us-east-1"
  profile = "terraform_practice"
}

resource "aws_s3_bucket" "local" {
  bucket = "local-state-test-yourname-2026"
  
  tags = {
    Name = "Local State Test"
  }
}
```

```bash
terraform init
terraform apply
```

State is stored locally in `terraform.tfstate`.

**Now migrate to remote backend**:

Add **backend.tf**:

```hcl
terraform {
  backend "s3" {
    bucket         = "terraform-state-yourname-2026"
    key            = "practice/local-state-test/terraform.tfstate"
    region         = "us-east-1"
    profile        = "terraform_practice"
    dynamodb_table = "terraform-state-locks"
    encrypt        = true
  }
}
```

```bash
terraform init -migrate-state
```

Answer `yes` to migrate. Your local state is now in S3!

## ✅ Validation Steps

1. **Verify remote state**:
   ```bash
   aws s3 ls s3://terraform-state-yourname-2026/practice/ --profile terraform_practice
   ```

2. **Check state locking**:
   - Run `terraform apply`
   - Quickly check DynamoDB table for lock entry
   - Lock should disappear after apply completes

3. **Test concurrent access**:
   - Open two terminal windows
   - Run `terraform apply` in both
   - Second one should wait for lock

4. **Verify versioning**:
   ```bash
   aws s3api list-object-versions \
     --bucket terraform-state-yourname-2026 \
     --prefix practice/ \
     --profile terraform_practice
   ```

## 🧹 Cleanup

**Important order**:

1. Destroy test resources:
   ```bash
   cd remote-state-test
   terraform destroy
   
   cd ../local-state-test
   terraform destroy
   ```

2. Destroy backend infrastructure:
   ```bash
   cd ../backend-setup
   terraform destroy
   ```

## 📚 Key Concepts Learned

- Remote state benefits
- S3 backend configuration
- State locking with DynamoDB
- State operations (list, show, mv, rm, pull)
- State migration
- State file security (encryption, versioning)

## 🎓 Challenge

1. **Add Lifecycle Policy**:
   - Keep only 30 days of state versions
   - Transition old versions to Glacier

2. **Add S3 Bucket Policy**:
   - Restrict access to specific IAM users
   - Require SSL for all operations

3. **Workspace with Remote State**:
   - Create workspaces (dev, staging, prod)
   - Each workspace has separate state file
   
   ```bash
   terraform workspace new dev
   terraform workspace new staging
   terraform workspace list
   ```

4. **Implement State File Backup**:
   - Lambda to copy state to backup bucket
   - Triggered on state file update

5. **Remote State Data Source**:
   - Create second project
   - Read outputs from first project's state
   
   ```hcl
   data "terraform_remote_state" "other" {
     backend = "s3"
     config = {
       bucket = "terraform-state-yourname-2026"
       key    = "practice/remote-state-test/terraform.tfstate"
       region = "us-east-1"
     }
   }
   
   output "other_bucket" {
     value = data.terraform_remote_state.other.outputs.bucket_name
   }
   ```

## 💡 Tips

- **ALWAYS** enable versioning on state bucket
- **ALWAYS** enable encryption
- **ALWAYS** use state locking for team work
- Use different state files per environment (dev, staging, prod)
- Never edit state files manually
- Use `terraform state mv` for refactoring
- Back up state files regularly
- Restrict S3 bucket access
- Use separate AWS accounts for different environments

## 🔒 Security Best Practices

```hcl
# backend.tf with all security features
terraform {
  backend "s3" {
    bucket         = "terraform-state-yourname-2026"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    profile        = "terraform_practice"
    
    # State locking
    dynamodb_table = "terraform-state-locks"
    
    # Encryption
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-east-1:ACCOUNT:key/KEY-ID"  # Optional: Use KMS
    
    # Access control
    acl            = "private"
  }
}
```

## 📖 Reference

- [Terraform State](https://developer.hashicorp.com/terraform/language/state)
- [S3 Backend](https://developer.hashicorp.com/terraform/language/settings/backends/s3)
- [State Locking](https://developer.hashicorp.com/terraform/language/state/locking)
- [State Commands](https://developer.hashicorp.com/terraform/cli/commands/state)

## ✨ Solution

Solution files are in the `solution/` directory. Try completing the lab yourself first!

