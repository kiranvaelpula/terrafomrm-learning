# Module 03: Your First Terraform Resource

## 🎯 Learning Objectives
By the end of this module, you will:
- Create your first AWS resource with Terraform
- Understand Terraform configuration files
- Learn the basic Terraform workflow
- Successfully deploy and destroy infrastructure

---

## 🎬 Your First Resource: S3 Bucket

We'll start simple - creating an AWS S3 bucket (cloud storage).

### Why S3 Bucket?
- ✅ Free tier eligible
- ✅ Quick to create (seconds)
- ✅ Easy to understand
- ✅ Safe to practice with
- ✅ Easy to delete

---

## 📝 Create Your First Configuration

### Step 1: Create Project Directory

```bash
cd terraform-practice
mkdir my-first-resource
cd my-first-resource
```

### Step 2: Create `main.tf`

```hcl
# main.tf - Your first Terraform configuration

# Configure Terraform itself
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = "eu-central-1"  # Frankfurt region
}

# Create an S3 bucket
resource "aws_s3_bucket" "my_first_bucket" {
  bucket = "my-terraform-learning-bucket-12345"  # Must be globally unique!
  
  tags = {
    Name        = "My First Bucket"
    Environment = "Learning"
    ManagedBy   = "Terraform"
  }
}

# Output the bucket name
output "bucket_name" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.my_first_bucket.id
}

output "bucket_arn" {
  description = "The ARN of the S3 bucket"
  value       = aws_s3_bucket.my_first_bucket.arn
}
```

### 📖 Understanding the Code

Let's break down each section:

#### 1. Terraform Block
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
```
- `required_version`: Minimum Terraform version needed
- `required_providers`: Which cloud provider plugins to use
- `~> 5.0`: Use version 5.x (any minor version)

#### 2. Provider Block
```hcl
provider "aws" {
  region = "eu-central-1"
}
```
- `provider`: Which cloud to use (AWS, Azure, GCP, etc.)
- `region`: Which AWS region to create resources in

#### 3. Resource Block
```hcl
resource "aws_s3_bucket" "my_first_bucket" {
  bucket = "my-terraform-learning-bucket-12345"
  
  tags = {
    Name = "My First Bucket"
  }
}
```
- `resource`: Declares a resource to create
- `"aws_s3_bucket"`: Resource type (S3 bucket)
- `"my_first_bucket"`: Local name (how you reference it in Terraform)
- `bucket = "..."`: The actual bucket name in AWS
- `tags`: Labels for organization

#### 4. Output Block
```hcl
output "bucket_name" {
  value = aws_s3_bucket.my_first_bucket.id
}
```
- `output`: Shows values after resource is created
- Useful for getting information about created resources

---

## 🚀 The Terraform Workflow

### The Four Essential Commands

```
terraform init    → Download provider plugins
terraform plan    → Preview changes (dry-run)
terraform apply   → Create resources
terraform destroy → Delete resources
```

---

## 🏃 Let's Run It!

### Step 1: Initialize

```bash
terraform init
```

**What happens:**
- Downloads AWS provider plugin
- Creates `.terraform` directory
- Creates `.terraform.lock.hcl` file

**Expected output:**
```
Initializing the backend...

Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 5.0"...
- Installing hashicorp/aws v5.20.0...
- Installed hashicorp/aws v5.20.0

Terraform has been successfully initialized!
```

### Step 2: Validate (Optional but Recommended)

```bash
terraform validate
```

**Expected output:**
```
Success! The configuration is valid.
```

### Step 3: Format (Optional - Makes code pretty)

```bash
terraform fmt
```

This auto-formats your code to follow Terraform style conventions.

### Step 4: Plan (Preview Changes)

```bash
terraform plan
```

**What happens:**
- Shows what Terraform will create
- **GREEN + sign** = will be created
- **RED - sign** = will be deleted
- **YELLOW ~ sign** = will be modified

**Expected output:**
```
Terraform will perform the following actions:

  # aws_s3_bucket.my_first_bucket will be created
  + resource "aws_s3_bucket" "my_first_bucket" {
      + bucket                      = "my-terraform-learning-bucket-12345"
      + id                          = (known after apply)
      + arn                         = (known after apply)
      + tags                        = {
          + "Environment" = "Learning"
          + "ManagedBy"   = "Terraform"
          + "Name"        = "My First Bucket"
        }
    }

Plan: 1 to add, 0 to change, 0 to destroy.
```

### Step 5: Apply (Create the Resource!)

```bash
terraform apply
```

**What happens:**
- Shows the plan again
- Asks for confirmation: `yes`
- Creates the S3 bucket in AWS

**Type `yes` and press Enter**

**Expected output:**
```
aws_s3_bucket.my_first_bucket: Creating...
aws_s3_bucket.my_first_bucket: Creation complete after 2s

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

Outputs:

bucket_arn = "arn:aws:s3:::my-terraform-learning-bucket-12345"
bucket_name = "my-terraform-learning-bucket-12345"
```

🎉 **Congratulations! You just created your first AWS resource with Terraform!**

---

## 🔍 Verify in AWS Console

1. Log into AWS Console
2. Go to **S3 service**
3. You should see your bucket: `my-terraform-learning-bucket-12345`
4. Check the tags - you'll see what you defined in Terraform!

---

## 📊 Understanding Terraform State

After running `terraform apply`, you'll see a new file: `terraform.tfstate`

```bash
ls -la
# You'll see:
# main.tf
# terraform.tfstate  ← This is new!
# .terraform/
# .terraform.lock.hcl
```

### What is terraform.tfstate?

```json
{
  "version": 4,
  "terraform_version": "1.6.0",
  "serial": 1,
  "resources": [
    {
      "mode": "managed",
      "type": "aws_s3_bucket",
      "name": "my_first_bucket",
      "instances": [
        {
          "attributes": {
            "arn": "arn:aws:s3:::my-terraform-learning-bucket-12345",
            "bucket": "my-terraform-learning-bucket-12345",
            "id": "my-terraform-learning-bucket-12345"
          }
        }
      ]
    }
  ]
}
```

**What it does:**
- Tracks what resources Terraform manages
- Maps Terraform configuration to real AWS resources
- **⚠️ Contains sensitive data - never commit to Git!**

---

## 🗑️ Clean Up (Destroy Resources)

**Important:** Always destroy practice resources to avoid charges!

```bash
terraform destroy
```

**What happens:**
- Shows what will be deleted
- Asks for confirmation: `yes`
- Deletes the S3 bucket

**Expected output:**
```
aws_s3_bucket.my_first_bucket: Refreshing state...

Terraform will perform the following actions:

  # aws_s3_bucket.my_first_bucket will be destroyed
  - resource "aws_s3_bucket" "my_first_bucket" {
      - bucket = "my-terraform-learning-bucket-12345" -> null
      - id     = "my-terraform-learning-bucket-12345" -> null
    }

Plan: 0 to add, 0 to change, 1 to destroy.

Do you really want to destroy all resources?
  Enter a value: yes

aws_s3_bucket.my_first_bucket: Destroying...
aws_s3_bucket.my_first_bucket: Destruction complete after 1s

Destroy complete! Resources: 1 destroyed.
```

🎉 **Resource cleaned up successfully!**

---

## 🧪 Practice Exercise

Now it's your turn! Create a second S3 bucket with different settings:

```hcl
resource "aws_s3_bucket" "my_second_bucket" {
  bucket = "my-second-terraform-bucket-67890"  # Change the number!
  
  tags = {
    Name        = "My Second Bucket"
    Environment = "Practice"
    CreatedBy   = "YourName"
    Purpose     = "Learning Terraform"
  }
}

output "second_bucket_arn" {
  value = aws_s3_bucket.my_second_bucket.arn
}
```

**Tasks:**
1. Add this resource to your `main.tf`
2. Run `terraform plan` - what will it do?
3. Run `terraform apply` - create it!
4. Verify in AWS Console - do you see both buckets?
5. Run `terraform destroy` - clean up!

---

## ❌ Common Errors & Solutions

### Error: "Bucket name already exists"

```
Error: Error creating S3 bucket: BucketAlreadyExists
```

**Solution:** S3 bucket names are globally unique. Change the bucket name:
```hcl
bucket = "my-terraform-learning-bucket-YOUR-INITIALS-12345"
```

### Error: "Invalid bucket name"

```
Error: Error validating S3 bucket name
```

**Solution:** Bucket names must:
- Be lowercase
- Be 3-63 characters
- Start and end with letter or number
- No underscores or spaces

**Good:** `my-bucket-123`
**Bad:** `My_Bucket 123`

### Error: "NoCredentialProviders"

```
Error: No valid credential sources found
```

**Solution:**
```bash
# Re-configure AWS credentials
aws configure

# Verify
aws sts get-caller-identity
```

---

## 🎯 Challenge Exercise

**Create a more complex S3 bucket with versioning and encryption:**

```hcl
resource "aws_s3_bucket" "advanced_bucket" {
  bucket = "my-advanced-bucket-12345"
  
  tags = {
    Name = "Advanced Practice Bucket"
  }
}

resource "aws_s3_bucket_versioning" "advanced_bucket_versioning" {
  bucket = aws_s3_bucket.advanced_bucket.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "advanced_bucket_encryption" {
  bucket = aws_s3_bucket.advanced_bucket.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
```

**Try it:**
1. Add this to `main.tf`
2. Run `terraform plan`
3. How many resources will be created?
4. Run `terraform apply`
5. Check in AWS Console - is versioning enabled? Is encryption enabled?
6. Destroy when done!

---

## 📚 Key Takeaways

```
✅ Created first AWS resource with Terraform
✅ Learned terraform init/plan/apply/destroy workflow
✅ Understood Terraform configuration structure
✅ Saw terraform.tfstate file (infrastructure state)
✅ Practiced with real AWS resources
✅ Learned to clean up resources
```

---

## 🎓 What You Learned

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `terraform init` | Download providers | First time, or when changing providers |
| `terraform validate` | Check syntax | Before plan/apply |
| `terraform fmt` | Format code | Before committing to Git |
| `terraform plan` | Preview changes | Before every apply |
| `terraform apply` | Create/update resources | To deploy infrastructure |
| `terraform destroy` | Delete resources | To clean up |

---

## ➡️ Next Module

You've created resources! Next, let's learn the complete Terraform workflow in depth.

**[Module 04: Terraform Workflow →](./04-terraform-workflow.md)**

---

**Progress:** ✅ Module 03 Complete | 📚 3/20 Modules

🎉 **Congrats on creating your first infrastructure with code!**
