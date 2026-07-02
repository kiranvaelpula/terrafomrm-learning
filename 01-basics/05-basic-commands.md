# Module 05: Basic Terraform Commands

## Essential Commands You'll Use Every Day

Let's learn all the core Terraform commands with practical examples.

---

## 1. terraform init

**What it does:** Initializes a Terraform project

**When to use:**
- First time working with a Terraform project
- After adding a new provider
- After adding/changing modules
- When you clone a project from Git

**Example:**
```bash
terraform init
```

**What happens:**
1. Downloads provider plugins (like AWS, Azure)
2. Sets up the backend (where state is stored)
3. Initializes modules
4. Creates `.terraform` directory

**Output:**
```
Initializing the backend...
Initializing provider plugins...
- Installing hashicorp/aws v5.31.0...
- Installed hashicorp/aws v5.31.0

Terraform has been successfully initialized!
```

**Common issue:**
```bash
# If you get errors, try:
terraform init -upgrade  # Upgrades providers to latest versions
```

---

## 2. terraform plan

**What it does:** Shows what Terraform will do WITHOUT making changes

**When to use:**
- Before every `terraform apply`
- To review changes
- To catch errors

**Example:**
```bash
terraform plan
```

**Save a plan to a file:**
```bash
terraform plan -out=myplan.tfplan
terraform apply myplan.tfplan  # Apply the saved plan
```

**Target specific resources:**
```bash
# Only plan changes for one resource
terraform plan -target=aws_s3_bucket.my_bucket
```

**Useful flags:**
```bash
terraform plan -var="environment=prod"     # Pass variables
terraform plan -var-file="prod.tfvars"     # Use variable file
terraform plan -refresh=false              # Skip state refresh
terraform plan -destroy                    # Preview destroy
```

---

## 3. terraform apply

**What it does:** Creates, updates, or deletes infrastructure

**When to use:**
- After reviewing `terraform plan`
- To make your infrastructure match your code

**Example:**
```bash
terraform apply
```

**Skip the confirmation prompt:**
```bash
terraform apply -auto-approve
```

⚠️ **Warning:** Only use `-auto-approve` in automation/CI pipelines, not manually!

**Apply a saved plan:**
```bash
terraform plan -out=myplan.tfplan
terraform apply myplan.tfplan
```

**Target specific resources:**
```bash
# Only apply changes to one resource
terraform apply -target=aws_s3_bucket.my_bucket
```

---

## 4. terraform destroy

**What it does:** Deletes all infrastructure managed by Terraform

**When to use:**
- Cleaning up test environments
- Decommissioning infrastructure
- Starting fresh

**Example:**
```bash
terraform destroy
```

**Destroy specific resources:**
```bash
terraform destroy -target=aws_s3_bucket.my_bucket
```

**Skip confirmation:**
```bash
terraform destroy -auto-approve
```

⚠️ **Warning:** This permanently deletes resources! Be very careful!

---

## 5. terraform fmt

**What it does:** Formats your Terraform code to standard style

**When to use:**
- Before committing code to Git
- To keep code consistent across your team

**Example:**
```bash
# Format all .tf files in current directory
terraform fmt

# Format recursively (including subdirectories)
terraform fmt -recursive

# Check if files need formatting (don't change them)
terraform fmt -check
```

**Before:**
```hcl
resource "aws_s3_bucket" "my_bucket" {
bucket="my-bucket"
tags={
Environment="dev"
}
}
```

**After:**
```hcl
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-bucket"
  
  tags = {
    Environment = "dev"
  }
}
```

---

## 6. terraform validate

**What it does:** Checks if your Terraform code is syntactically correct

**When to use:**
- After writing new code
- Before running `plan` or `apply`
- In CI/CD pipelines

**Example:**
```bash
terraform validate
```

**Success:**
```
Success! The configuration is valid.
```

**Error example:**
```
Error: Missing required argument

  on main.tf line 5:
   5: resource "aws_s3_bucket" "my_bucket" {

The argument "bucket" is required, but no definition was found.
```

**Difference between validate and plan:**
- `validate`: Checks syntax only (fast, no AWS connection needed)
- `plan`: Checks if resources can actually be created (slower, needs AWS credentials)

---

## 7. terraform show

**What it does:** Shows current state or saved plan in readable format

**When to use:**
- To see what infrastructure currently exists
- To inspect a saved plan file

**Example:**
```bash
# Show current state
terraform show

# Show a saved plan
terraform show myplan.tfplan
```

**JSON output:**
```bash
terraform show -json
```

---

## 8. terraform output

**What it does:** Displays output values from your state

**When to use:**
- To get information about created resources
- In scripts that need resource details

**First, define outputs in your code:**
```hcl
# outputs.tf
output "bucket_name" {
  value = aws_s3_bucket.my_bucket.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.my_bucket.arn
}
```

**Then use the command:**
```bash
# Show all outputs
terraform output

# Show specific output
terraform output bucket_name

# JSON format
terraform output -json
```

---

## 9. terraform refresh

**What it does:** Updates state file with real-world infrastructure

**When to use:**
- When resources were changed outside Terraform
- To sync state with reality

**Example:**
```bash
terraform refresh
```

⚠️ **Note:** This is usually not needed - `plan` and `apply` automatically refresh.

---

## 10. terraform state

**What it does:** Advanced state management commands

**Common state commands:**

```bash
# List all resources in state
terraform state list

# Show details of a specific resource
terraform state show aws_s3_bucket.my_bucket

# Remove a resource from state (doesn't delete the actual resource)
terraform state rm aws_s3_bucket.my_bucket

# Move/rename a resource in state
terraform state mv aws_s3_bucket.old aws_s3_bucket.new

# Pull current state and display it
terraform state pull
```

**When to use:**
- Debugging state issues
- Importing existing resources
- Refactoring code structure

---

## 11. terraform import

**What it does:** Imports existing infrastructure into Terraform state

**When to use:**
- You created resources manually and want Terraform to manage them
- Migrating to Terraform from manual management

**Example:**
```bash
# 1. First, write the resource in your code
resource "aws_s3_bucket" "existing_bucket" {
  # Leave empty initially
}

# 2. Import the existing bucket
terraform import aws_s3_bucket.existing_bucket my-existing-bucket-name

# 3. Run terraform plan to see what's different
terraform plan

# 4. Update your code to match the real resource
```

---

## 12. terraform workspace

**What it does:** Manages multiple environments (dev, staging, prod) with the same code

**Commands:**
```bash
# List workspaces
terraform workspace list

# Create new workspace
terraform workspace new dev

# Switch workspace
terraform workspace select prod

# Show current workspace
terraform workspace show

# Delete workspace
terraform workspace delete dev
```

**Use case:**
```bash
terraform workspace new dev
terraform apply  # Creates dev infrastructure

terraform workspace new prod
terraform apply  # Creates prod infrastructure (separate state)
```

---

## Common Command Patterns

### Daily Development Workflow
```bash
# 1. Make changes to .tf files
# 2. Format code
terraform fmt

# 3. Validate syntax
terraform validate

# 4. Preview changes
terraform plan

# 5. Apply changes
terraform apply
```

### First Time Setup
```bash
terraform init
terraform plan
terraform apply
```

### Making Changes
```bash
terraform plan
terraform apply
```

### Cleaning Up
```bash
terraform destroy
```

### CI/CD Pipeline
```bash
terraform init -input=false
terraform validate
terraform plan -out=tfplan
terraform apply -auto-approve tfplan
```

---

## Debugging and Logging

**Enable detailed logs:**
```bash
# Set log level (TRACE, DEBUG, INFO, WARN, ERROR)
export TF_LOG=DEBUG
terraform apply

# Save logs to file
export TF_LOG=DEBUG
export TF_LOG_PATH=terraform.log
terraform apply
```

**Turn off logging:**
```bash
unset TF_LOG
unset TF_LOG_PATH
```

---

## Command Flags You Should Know

### Global Flags (work with any command)
```bash
-chdir=DIR          # Run command in different directory
-var="key=value"    # Set a variable
-var-file=FILE      # Load variables from file
```

### Apply/Plan Flags
```bash
-target=RESOURCE    # Target specific resource
-auto-approve       # Skip confirmation
-out=FILE           # Save plan to file
-refresh=false      # Don't refresh state
-lock=false         # Don't lock state
```

---

## Practical Exercise

**Task:** Practice all commands with a real S3 bucket

```bash
# 1. Create a file: main.tf
# 2. Add AWS S3 bucket resource
# 3. Run these commands in order:

terraform init
terraform validate
terraform fmt
terraform plan
terraform apply
terraform show
terraform state list
terraform output (if you defined outputs)
terraform destroy
```

**Experiment:**
- Try `terraform plan -target=aws_s3_bucket.my_bucket`
- Try `terraform apply -auto-approve` (carefully!)
- Try `terraform fmt` on badly formatted code

---

## Command Cheat Sheet

```bash
# Essential
terraform init       # Initialize project
terraform plan       # Preview changes
terraform apply      # Apply changes
terraform destroy    # Delete everything

# Code Quality
terraform fmt        # Format code
terraform validate   # Check syntax

# Information
terraform show       # Show state/plan
terraform output     # Show outputs
terraform state list # List resources

# Advanced
terraform import     # Import existing resource
terraform workspace  # Manage workspaces
terraform state      # Manage state
```

---

## Key Takeaways

✅ `init` first, always

✅ `plan` before `apply`, always

✅ `fmt` and `validate` keep code clean

✅ `destroy` is powerful and dangerous

✅ Use `-target` to work with specific resources

✅ Enable logging when debugging

---

## Next Steps

Now that you know the commands, let's learn how to use variables to make your code reusable!

**Next:** [Module 06: Variables and Outputs](../02-intermediate/06-variables-and-outputs.md)
