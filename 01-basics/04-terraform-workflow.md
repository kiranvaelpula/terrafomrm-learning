# Module 04: Terraform Workflow

## 📖 Understanding the Terraform Workflow (Intuition First)

The Terraform workflow is a lot like renovating a house with a good contractor. First you *write* down what you want changed. Then the contractor walks the house and hands you an estimate: "I'll knock down this wall, add that window, and leave the kitchen alone." Only after you approve the estimate do they pick up the tools and actually do the work. Write, plan, apply — describe, estimate, execute.

The reason this three-step rhythm exists is trust. Infrastructure changes can be expensive or destructive, so you never want a tool to silently do things you didn't expect. The `plan` step is the estimate you review before committing. It tells you in plain terms what will be *added*, *changed*, *destroyed*, or *replaced*, using simple symbols (`+`, `~`, `-`, `-/+`). Reading that estimate is where you catch mistakes — before they hit real systems, not after.

The magic that makes this possible is the *state file*. Terraform keeps a written record of everything it has built, like the contractor keeping the current floor plan of your house. When you change your code, Terraform compares three things: what your code says you want, what the state file says already exists, and what's actually out there. The difference between those is exactly the plan it shows you. Without this memory, Terraform couldn't tell "create something new" apart from "modify something that's already there."

Because Terraform is declarative, mistakes are cheap. Nothing happens until you run `apply`, so a wrong edit is just a wrong draft — fix the code and re-plan. And because Terraform always works toward your described end state, if reality drifts (someone changed a setting by hand), the next apply nudges everything back to match your code.

That's the whole mental model: you keep editing a description of the destination, Terraform keeps a memory of what's real, and every change is previewed as an estimate before it's executed. This is why the workflow feels safe even when managing large, critical systems.

---

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

## 🎯 Interview Quick Points

- The core workflow is **Write → Plan → Apply**
- **Always run `terraform plan` before `apply`** to preview changes
- Plan symbols: **`+` create, `-` destroy, `~` modify, `-/+` replace** (destroy then recreate)
- **Nothing changes until you run `apply`** — plans are safe, read-only previews
- Terraform is **declarative** — you define the desired end state, not the steps
- **`terraform.tfstate`** stores the current known state of your infrastructure
- Terraform computes changes by **diffing code vs. state vs. real infrastructure**
- **Never manually edit or delete `terraform.tfstate`** — it tracks what Terraform manages
- **Don't commit state to Git** — it can contain sensitive values
- Mistakes are cheap: **fix the code and re-run plan/apply**; use `destroy` to start fresh
- `apply -auto-approve` skips confirmation — reserve it for **CI/CD automation**, not manual runs
- Terraform automatically **refreshes state** during plan/apply to detect drift

## Next Steps

In the next module, we'll dive deep into all Terraform commands and when to use them.

**Next:** [Module 05: Basic Commands](./05-basic-commands.md)
