# Module 04: Terraform Workflow

## The Terraform Workflow

Terraform has a simple 3-step workflow that you'll use for every change:

```
Write → Plan → Apply
```

Let's understand each step in detail.

---

## Step 1: Write

This is where you write your infrastructure code in `.tf` files.

```hcl
# main.tf
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-app-bucket-2024"
}
```

**What happens:**
- You define what infrastructure you want
- Terraform doesn't do anything yet - it's just code

---

## Step 2: Plan

Run `terraform plan` to preview what Terraform will do.

```bash
terraform plan
```

**What you'll see:**
```
Terraform will perform the following actions:

  # aws_s3_bucket.my_bucket will be created
  + resource "aws_s3_bucket" "my_bucket" {
      + bucket = "my-app-bucket-2024"
      + id     = (known after apply)
    }

Plan: 1 to add, 0 to change, 0 to destroy.
```

**Understanding the symbols:**
- `+` = Resource will be **created**
- `-` = Resource will be **destroyed**
- `~` = Resource will be **modified**
- `-/+` = Resource will be **replaced** (destroyed and recreated)

**Why plan is important:**
- See what will happen BEFORE it happens
- Catch mistakes before they affect real infrastructure
- Share plans with your team for review

---

## Step 3: Apply

Run `terraform apply` to create the actual infrastructure.

```bash
terraform apply
```

**What happens:**
1. Terraform shows you the plan again
2. Asks for confirmation: `Do you want to perform these actions?`
3. Type `yes` to proceed
4. Terraform creates the resources in AWS

**Output:**
```
aws_s3_bucket.my_bucket: Creating...
aws_s3_bucket.my_bucket: Creation complete after 2s

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

---

## The Complete Workflow in Action

Let's see a real example:

### Scenario: Add tags to your S3 bucket

**1. Write the change:**
```hcl
# main.tf
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-app-bucket-2024"
  
  tags = {
    Environment = "Development"
    Project     = "Learning Terraform"
  }
}
```

**2. Plan the change:**
```bash
terraform plan
```

Output shows:
```
  ~ resource "aws_s3_bucket" "my_bucket" {
        bucket = "my-app-bucket-2024"
        id     = "my-app-bucket-2024"
      + tags   = {
          + "Environment" = "Development"
          + "Project"     = "Learning Terraform"
        }
    }

Plan: 0 to add, 1 to change, 0 to destroy.
```

**3. Apply the change:**
```bash
terraform apply
```

Type `yes` when prompted, and Terraform updates the bucket with tags.

---

## terraform.tfstate - The State File

After you run `apply`, Terraform creates a file called `terraform.tfstate`.

**What is it?**
- A JSON file that stores the current state of your infrastructure
- Terraform's memory of what it created

**Why is it important?**
- Terraform compares your `.tf` files with `terraform.tfstate` to know what changed
- Without state, Terraform doesn't know what already exists

**Example state file:**
```json
{
  "version": 4,
  "terraform_version": "1.6.0",
  "resources": [
    {
      "type": "aws_s3_bucket",
      "name": "my_bucket",
      "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
      "instances": [
        {
          "attributes": {
            "bucket": "my-app-bucket-2024",
            "id": "my-app-bucket-2024",
            "tags": {
              "Environment": "Development"
            }
          }
        }
      ]
    }
  ]
}
```

**Important rules:**
- ⚠️ **Never edit terraform.tfstate manually**
- ⚠️ **Never delete terraform.tfstate** (you'll lose track of your infrastructure)
- ⚠️ **Don't commit terraform.tfstate to Git** (contains sensitive data)

---

## What If Things Go Wrong?

### Scenario 1: Made a mistake in your code

**Solution:** Just fix the code and run `terraform plan` again. Nothing is changed until you run `apply`.

### Scenario 2: Applied the wrong configuration

**Solution:** Fix the code and run `terraform apply` again. Terraform will correct the infrastructure.

### Scenario 3: Need to start over

**Solution:** Run `terraform destroy` to delete everything and start fresh.

```bash
terraform destroy
```

---

## Quick Command Reference

```bash
# Initialize Terraform (run once per project)
terraform init

# Format your code nicely
terraform fmt

# Check if your code is valid
terraform validate

# Preview changes
terraform plan

# Apply changes
terraform apply

# Apply without asking for confirmation (be careful!)
terraform apply -auto-approve

# Destroy all resources
terraform destroy
```

---

## Practical Exercise

**Task:** Modify your S3 bucket from Module 03

1. Add tags to your bucket:
   ```hcl
   tags = {
     Environment = "Dev"
     Owner       = "Your Name"
   }
   ```

2. Run `terraform plan` - what do you see?

3. Run `terraform apply` - what happened?

4. Change one tag value and repeat steps 2-3

5. Run `terraform destroy` to clean up

**Expected outcome:**
- Understand how Terraform detects changes
- See the difference between create, update, and destroy
- Learn to read Terraform's output

---

## Key Takeaways

✅ Terraform workflow is: **Write → Plan → Apply**

✅ Always run `terraform plan` before `apply`

✅ `terraform.tfstate` tracks your infrastructure

✅ Terraform is declarative - you tell it the end state, not the steps

✅ You can always fix mistakes and reapply

---

## Next Steps

In the next module, we'll dive deep into all Terraform commands and when to use them.

**Next:** [Module 05: Basic Commands](./05-basic-commands.md)
