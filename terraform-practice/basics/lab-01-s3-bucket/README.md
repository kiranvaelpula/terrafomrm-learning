# Lab 01: Create Your First S3 Bucket

**Difficulty**: Beginner  
**Time**: 15 minutes  
**Cost**: Free (S3 buckets are free, storage charges only apply for data)

## 🎯 Objectives

- Create an S3 bucket using Terraform
- Enable versioning on the bucket
- Add tags to resources
- Use outputs to display bucket information

## 📋 Prerequisites

- AWS credentials configured (`terraform_practice` profile)
- Terraform installed and working

## 🔨 Tasks

### Task 1: Create a Basic S3 Bucket

Create a file called `main.tf` and add:

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

# TODO: Create an S3 bucket resource
# Hint: resource "aws_s3_bucket" "my_bucket" { ... }
# Bucket name must be globally unique!
```

**Requirements**:
- Bucket name should include your name or unique identifier
- Example: `terraform-practice-yourname-2026`

### Task 2: Enable Versioning

Add versioning to your bucket:

```hcl
# TODO: Add versioning configuration
# Hint: Use aws_s3_bucket_versioning resource
```

### Task 3: Add Tags

Add these tags to your bucket:
- Name: "My First Terraform Bucket"
- Environment: "Learning"
- ManagedBy: "Terraform"

### Task 4: Create Outputs

Create `outputs.tf` and display:
- Bucket name
- Bucket ARN
- Bucket region

## ✅ Validation Steps

1. **Initialize Terraform**:
   ```bash
   terraform init
   ```

2. **Format your code**:
   ```bash
   terraform fmt
   ```

3. **Validate**:
   ```bash
   terraform validate
   ```

4. **Plan**:
   ```bash
   terraform plan
   ```
   - Should show 2 resources to create

5. **Apply**:
   ```bash
   terraform apply
   ```
   - Type `yes` to confirm

6. **Verify in AWS Console**:
   - Go to S3 service
   - Find your bucket
   - Check versioning is enabled
   - Verify tags are present

7. **Test outputs**:
   ```bash
   terraform output
   ```

## 🧹 Cleanup

**IMPORTANT**: Always destroy resources after practice!

```bash
terraform destroy
```

Type `yes` to confirm deletion.

## 📚 Key Concepts Learned

- Terraform providers and required_version
- Resource creation syntax
- Resource dependencies
- Tags and resource metadata
- Outputs for displaying information

## 🎓 Challenge

Try these additional tasks:
1. Add server-side encryption to the bucket
2. Create a second bucket for logs
3. Add a lifecycle rule to transition objects to Glacier after 30 days

## 💡 Tips

- Bucket names must be globally unique across ALL AWS accounts
- Use lowercase letters, numbers, and hyphens only
- Bucket names must be 3-63 characters long
- Add your initials or a random suffix to ensure uniqueness

## 📖 Reference

- [AWS S3 Bucket Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket)
- [S3 Bucket Versioning](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_versioning)

## ✨ Solution

Solution files are in the `solution/` directory. Try completing the lab yourself first!
