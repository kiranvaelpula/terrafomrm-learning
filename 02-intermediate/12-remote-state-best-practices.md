# Module 12: Remote State Best Practices

## 📚 What You'll Learn
- Remote state backends
- State locking mechanisms
- Best practices for state management
- Migrating to remote state
- Securing state files
- Team collaboration with remote state

---

## 🎯 Why Remote State?

### Problems with Local State
- ❌ Not shared across team
- ❌ No locking mechanism
- ❌ Risk of loss/corruption
- ❌ No version control for state
- ❌ Secrets stored in plain text

### Benefits of Remote State
- ✅ Shared across team
- ✅ State locking prevents conflicts
- ✅ Automatic backups
- ✅ Version history
- ✅ Encryption at rest
- ✅ Access control

---

## 🏗️ Remote State Backends

### 1. AWS S3 + DynamoDB (Recommended for AWS)

**Why S3 + DynamoDB?**
- S3: Stores state file
- DynamoDB: Provides state locking
- Both: Highly available and durable

#### Configuration

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

#### Setup Script

```bash
# Create S3 bucket
aws s3api create-bucket \
    --bucket my-terraform-state-bucket \
    --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket my-terraform-state-bucket \
    --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
    --bucket my-terraform-state-bucket \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'

# Block public access
aws s3api put-public-access-block \
    --bucket my-terraform-state-bucket \
    --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# Create DynamoDB table for locking
aws dynamodb create-table \
    --table-name terraform-state-lock \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

### 2. Terraform Cloud

```hcl
terraform {
  cloud {
    organization = "my-org"
    
    workspaces {
      name = "my-workspace"
    }
  }
}
```

### 3. Azure Storage

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "terraformstatestg"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}
```

### 4. GCS (Google Cloud Storage)

```hcl
terraform {
  backend "gcs" {
    bucket = "my-terraform-state-bucket"
    prefix = "prod"
  }
}
```

---

## 🔐 Security Best Practices

### 1. Encryption

```hcl
# S3 with encryption
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true  # Enable encryption
    kms_key_id     = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
  }
}
```

### 2. Access Control - IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::my-terraform-state-bucket"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::my-terraform-state-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/terraform-state-lock"
    }
  ]
}
```

### 3. Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::my-terraform-state-bucket",
        "arn:aws:s3:::my-terraform-state-bucket/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

---

## 🔄 Migrating to Remote State

### Step 1: Current Local State

```hcl
# Currently using local state (default)
# terraform.tfstate exists locally
```

### Step 2: Add Backend Configuration

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

### Step 3: Initialize Migration

```bash
# Terraform will detect backend change
terraform init

# Output:
# Initializing the backend...
# Do you want to copy existing state to the new backend?
#   Pre-existing state was found while migrating...
# 
# Would you like to copy this state to the new backend?
# Enter "yes" to copy and "no" to start with an empty state.

# Type: yes
```

### Step 4: Verify Migration

```bash
# Verify remote state
terraform state list

# Check S3
aws s3 ls s3://my-terraform-state-bucket/prod/

# Check local state is replaced with backend config
ls -la terraform.tfstate*
# Should show terraform.tfstate.backup only
```

---

## 🎪 Lab: Setting Up Remote State

### Objective
Set up S3 backend with state locking for a production-ready configuration.

### Step 1: Create Backend Infrastructure

```hcl
# bootstrap/main.tf
# This creates the S3 bucket and DynamoDB table
# Run this ONCE with local state, then never touch it again

provider "aws" {
  region = "us-east-1"
}

# S3 bucket for state
resource "aws_s3_bucket" "terraform_state" {
  bucket = "mycompany-terraform-state-${data.aws_caller_identity.current.account_id}"
  
  lifecycle {
    prevent_destroy = true
  }
  
  tags = {
    Name        = "Terraform State Bucket"
    Environment = "All"
    ManagedBy   = "Terraform"
  }
}

# Enable versioning
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

# DynamoDB table for locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-state-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
  
  lifecycle {
    prevent_destroy = true
  }
  
  tags = {
    Name        = "Terraform State Locks"
    Environment = "All"
    ManagedBy   = "Terraform"
  }
}

# Get current account ID
data "aws_caller_identity" "current" {}

# Outputs
output "s3_bucket_name" {
  value       = aws_s3_bucket.terraform_state.id
  description = "S3 bucket for Terraform state"
}

output "dynamodb_table_name" {
  value       = aws_dynamodb_table.terraform_locks.name
  description = "DynamoDB table for state locking"
}
```

### Step 2: Deploy Bootstrap

```bash
cd bootstrap
terraform init
terraform plan
terraform apply

# Save outputs
export TF_STATE_BUCKET=$(terraform output -raw s3_bucket_name)
export TF_LOCK_TABLE=$(terraform output -raw dynamodb_table_name)
```

### Step 3: Configure Remote Backend

```hcl
# production/backend.tf
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "mycompany-terraform-state-123456789012"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-locks"
    
    # Optional: Use AWS profile
    # profile = "production"
  }
}
```

### Step 4: Use Remote State

```bash
cd production
terraform init

# Create some resources
terraform apply

# Verify state is in S3
aws s3 ls s3://$TF_STATE_BUCKET/production/

# Verify lock works (open two terminals)
# Terminal 1:
terraform plan

# Terminal 2 (while Terminal 1 is running):
terraform plan
# Should see: Error locking state: resource temporarily unavailable
```

---

## 🔄 State Locking

### How State Locking Works

```
User 1: terraform apply
  ↓
  Acquire lock in DynamoDB
  ↓
  Modify infrastructure
  ↓
  Update state in S3
  ↓
  Release lock

User 2: terraform apply (while User 1 is working)
  ↓
  Try to acquire lock → FAILS
  ↓
  Error: state is locked by User 1
```

### Force Unlock (Use Carefully!)

```bash
# Only use if process crashed and lock wasn't released
terraform force-unlock LOCK_ID

# Example:
terraform force-unlock a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## 📁 State File Organization

### Pattern 1: Environment-Based

```
s3://my-tf-state/
├── dev/
│   ├── network/terraform.tfstate
│   ├── compute/terraform.tfstate
│   └── database/terraform.tfstate
├── staging/
│   ├── network/terraform.tfstate
│   ├── compute/terraform.tfstate
│   └── database/terraform.tfstate
└── prod/
    ├── network/terraform.tfstate
    ├── compute/terraform.tfstate
    └── database/terraform.tfstate
```

### Pattern 2: Project-Based

```
s3://my-tf-state/
├── project-a/
│   ├── dev.tfstate
│   ├── staging.tfstate
│   └── prod.tfstate
├── project-b/
│   ├── dev.tfstate
│   └── prod.tfstate
└── shared/
    └── network.tfstate
```

### Pattern 3: Workspace-Based

```hcl
# Use Terraform workspaces with remote state
terraform {
  backend "s3" {
    bucket         = "my-tf-state"
    key            = "project/terraform.tfstate"
    region         = "us-east-1"
    workspace_key_prefix = "env"
  }
}

# Creates:
# s3://my-tf-state/env:dev/project/terraform.tfstate
# s3://my-tf-state/env:staging/project/terraform.tfstate
# s3://my-tf-state/env:prod/project/terraform.tfstate
```

---

## 🤝 Team Collaboration

### 1. Backend Configuration Variables

```hcl
# backend.tf
terraform {
  backend "s3" {
    # Use backend config file
  }
}
```

```hcl
# backend-config-dev.hcl
bucket         = "mycompany-terraform-state"
key            = "dev/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "terraform-locks"
encrypt        = true
profile        = "dev"
```

```bash
# Initialize with backend config
terraform init -backend-config=backend-config-dev.hcl
```

### 2. Shared Workspace Setup

```bash
# Developer 1
git clone repo
cd project
terraform init
terraform workspace select dev
terraform plan

# Developer 2 (different computer)
git clone repo
cd project
terraform init  # Uses same remote state
terraform workspace select dev
terraform plan  # Sees same state as Developer 1
```

### 3. CI/CD Integration

```yaml
# .github/workflows/terraform.yml
name: Terraform

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  terraform:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.5.0
      
      - name: Terraform Init
        run: terraform init
      
      - name: Terraform Plan
        run: terraform plan
      
      - name: Terraform Apply
        if: github.ref == 'refs/heads/main'
        run: terraform apply -auto-approve
```

---

## 🛡️ State Security Checklist

- [ ] Enable encryption at rest
- [ ] Enable versioning on S3 bucket
- [ ] Use IAM policies to restrict access
- [ ] Enable MFA delete on S3 bucket
- [ ] Use VPC endpoints for S3/DynamoDB access
- [ ] Enable AWS CloudTrail logging
- [ ] Use separate state files for different environments
- [ ] Never commit state files to Git
- [ ] Regularly backup state files
- [ ] Implement least privilege access

---

## 💡 Best Practices

### 1. One State File Per Environment

```hcl
# ❌ Bad - Shared state across environments
terraform {
  backend "s3" {
    bucket = "my-state"
    key    = "terraform.tfstate"
  }
}

# ✅ Good - Separate state per environment
terraform {
  backend "s3" {
    bucket = "my-state"
    key    = "${var.environment}/terraform.tfstate"
  }
}
```

### 2. Use Consistent Naming

```
# Good naming pattern
<company>-terraform-state-<account-id>
terraform-locks-<region>
<environment>/<component>/terraform.tfstate
```

### 3. Enable Logging

```hcl
# S3 bucket logging
resource "aws_s3_bucket_logging" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = "terraform-state-logs/"
}
```

### 4. Lifecycle Policies

```hcl
resource "aws_s3_bucket_lifecycle_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  rule {
    id     = "archive-old-versions"
    status = "Enabled"
    
    noncurrent_version_transition {
      noncurrent_days = 90
      storage_class   = "GLACIER"
    }
    
    noncurrent_version_expiration {
      noncurrent_days = 365
    }
  }
}
```

---

## 🐛 Common Issues

### Issue 1: State Locked

```bash
# Check DynamoDB for locks
aws dynamodb scan --table-name terraform-state-locks

# Force unlock (careful!)
terraform force-unlock <LOCK_ID>
```

### Issue 2: Permission Denied

```bash
# Verify IAM permissions
aws s3 ls s3://my-terraform-state-bucket
aws dynamodb describe-table --table-name terraform-state-locks
```

### Issue 3: State Divergence

```bash
# Refresh state from real infrastructure
terraform refresh

# Or use targeted refresh
terraform apply -refresh-only
```

---

## 📝 Quiz

1. Why use remote state instead of local state?
2. What is state locking and why is it important?
3. Which AWS services are used for remote state?
4. How do you migrate from local to remote state?
5. What security measures should be applied to state files?

---

## 🎓 Challenge Exercise

Set up a complete remote state infrastructure with:
1. S3 bucket with versioning and encryption
2. DynamoDB table for locking
3. Proper IAM policies
4. Separate state files for dev and prod
5. CloudTrail logging enabled

---

## ⏭️ Next Steps

Continue to [Module 13: Workspaces](../03-advanced/13-workspaces.md)

---

**🎉 Congratulations!** You now understand remote state management and can implement production-ready state storage!
