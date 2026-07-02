# Module 07: Understanding Terraform State

## What is Terraform State?

Terraform state is a **JSON file** that stores information about your infrastructure.

Think of it as Terraform's memory - without it, Terraform has no idea what it created.

---

## Why State Matters

### Without State File
```bash
terraform apply  # Creates S3 bucket

# Delete terraform.tfstate
rm terraform.tfstate

terraform apply  # Error! Bucket already exists
# Terraform doesn't know it created the bucket
```

### With State File
```bash
terraform apply  # Creates S3 bucket (state saved)
terraform apply  # "No changes. Infrastructure is up-to-date."
# Terraform remembers what it created
```

---

## What's Inside terraform.tfstate?

**Example state file:**
```json
{
  "version": 4,
  "terraform_version": "1.6.0",
  "serial": 1,
  "lineage": "abc-123",
  "resources": [
    {
      "mode": "managed",
      "type": "aws_s3_bucket",
      "name": "my_bucket",
      "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
      "instances": [
        {
          "schema_version": 0,
          "attributes": {
            "id": "my-app-bucket",
            "arn": "arn:aws:s3:::my-app-bucket",
            "bucket": "my-app-bucket",
            "region": "eu-central-1",
            "tags": {
              "Environment": "dev"
            }
          }
        }
      ]
    }
  ]
}
```

**What Terraform stores:**
- Resource IDs (so it can update/delete them)
- Resource attributes (current configuration)
- Resource dependencies
- Output values
- Provider configuration

---

## How Terraform Uses State

### The Refresh-Plan-Apply Cycle

```
1. REFRESH: Read current state from terraform.tfstate
2. COMPARE: Compare with your .tf files
3. PLAN: Determine what changed
4. APPLY: Make necessary changes
5. UPDATE STATE: Save new state to terraform.tfstate
```

**Example:**

**Current state:**
```json
{
  "resources": [{
    "type": "aws_s3_bucket",
    "attributes": {
      "bucket": "my-bucket",
      "tags": {}
    }
  }]
}
```

**Your code (main.tf):**
```hcl
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-bucket"
  tags = {
    Environment = "dev"
  }
}
```

**Terraform's logic:**
```
State says: bucket exists, no tags
Code says: bucket should have tags
Action: Add tags to bucket
```

---

## Local vs Remote State

### Local State (Default)

**What:** State file stored on your computer

**File location:** `terraform.tfstate` in project directory

**Pros:**
- Simple, no setup needed
- Fast (no network calls)

**Cons:**
- ❌ Can't collaborate (state on your machine only)
- ❌ No locking (multiple people can run terraform simultaneously)
- ❌ Easy to lose (delete file = lose track of infrastructure)
- ❌ Secrets exposed (state contains passwords, keys)

**Good for:**
- Learning
- Personal projects
- Testing

### Remote State (Production)

**What:** State file stored in cloud (S3, Azure Storage, etc.)

**Pros:**
- ✅ Team collaboration (everyone uses same state)
- ✅ State locking (prevents conflicts)
- ✅ Encryption (secrets protected)
- ✅ Versioning (can recover old states)
- ✅ Backup (cloud provider handles it)

**Cons:**
- Requires initial setup
- Slightly slower (network calls)

**Good for:**
- Production environments
- Team projects
- CI/CD pipelines

---

## Setting Up Remote State (S3 Example)

### Step 1: Create S3 Bucket for State
```bash
# Manually create bucket once
aws s3 mb s3://my-terraform-state-bucket --region eu-central-1
aws s3api put-bucket-versioning \
  --bucket my-terraform-state-bucket \
  --versioning-configuration Status=Enabled
```

### Step 2: Configure Backend in Terraform

Create `backend.tf`:
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "dev/terraform.tfstate"  # Path in bucket
    region         = "eu-central-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"  # For state locking
  }
}
```

### Step 3: Create DynamoDB Table for Locking
```hcl
# Create this first, then use in backend config
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

### Step 4: Migrate Existing State
```bash
# If you already have local state
terraform init -migrate-state

# Terraform will ask: "Do you want to copy existing state to the new backend?"
# Type: yes
```

---

## State File Organization

### Single State (Simple Projects)
```
project/
├── main.tf
├── variables.tf
└── terraform.tfstate
```

### Multiple States (Recommended)
```
project/
├── dev/
│   ├── main.tf
│   ├── backend.tf       # Points to s3://bucket/dev/terraform.tfstate
│   └── dev.tfvars
├── staging/
│   ├── main.tf
│   ├── backend.tf       # Points to s3://bucket/staging/terraform.tfstate
│   └── staging.tfvars
└── prod/
    ├── main.tf
    ├── backend.tf       # Points to s3://bucket/prod/terraform.tfstate
    └── prod.tfvars
```

**Why separate states:**
- Isolates environments (dev can't break prod)
- Different teams can work independently
- Reduces risk (smaller blast radius)

---

## State Locking

### What is State Locking?

Prevents multiple people from running `terraform apply` at the same time.

**Without locking:**
```
Person A: terraform apply  (starts)
Person B: terraform apply  (starts simultaneously)
Result: Both modify infrastructure → CONFLICT!
```

**With locking:**
```
Person A: terraform apply  (locks state)
Person B: terraform apply  (waits for lock)
Result: Changes applied safely, one at a time
```

### How to Enable Locking

**S3 Backend (with DynamoDB):**
```hcl
terraform {
  backend "s3" {
    bucket         = "my-state-bucket"
    key            = "terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "terraform-locks"  # This enables locking
  }
}
```

**Force unlock (if process crashed):**
```bash
terraform force-unlock <lock-id>
```

---

## State Commands

### List Resources in State
```bash
terraform state list
```
Output:
```
aws_s3_bucket.my_bucket
aws_iam_role.app_role
```

### Show Resource Details
```bash
terraform state show aws_s3_bucket.my_bucket
```

### Remove Resource from State
```bash
# Removes from state, doesn't delete actual resource
terraform state rm aws_s3_bucket.my_bucket
```

**Use case:** Resource was deleted manually, remove it from state.

### Move/Rename Resource
```bash
# Renamed resource in code, update state to match
terraform state mv aws_s3_bucket.old_name aws_s3_bucket.new_name
```

### Pull State (View Raw)
```bash
terraform state pull > state.json
```

### Push State (Dangerous!)
```bash
terraform state push state.json
```
⚠️ **Warning:** Can corrupt state, use with caution!

---

## Import Existing Resources

### Scenario: You Created S3 Bucket Manually

**Step 1: Write the resource definition**
```hcl
# main.tf
resource "aws_s3_bucket" "existing" {
  # Leave empty for now
}
```

**Step 2: Import it**
```bash
terraform import aws_s3_bucket.existing my-existing-bucket-name
```

**Step 3: Check what's different**
```bash
terraform plan
```

**Step 4: Update code to match reality**
```hcl
resource "aws_s3_bucket" "existing" {
  bucket = "my-existing-bucket-name"
  # Add other attributes shown in plan
}
```

**Step 5: Verify**
```bash
terraform plan  # Should show "No changes"
```

---

## State File Security

### What Sensitive Data is in State?

```json
{
  "resources": [{
    "type": "aws_db_instance",
    "attributes": {
      "password": "MySecretPassword123!",  // 😱 In plain text!
      "username": "admin",
      "endpoint": "db.example.com:5432"
    }
  }]
}
```

### Security Best Practices

✅ **Do:**
- Use remote state with encryption
- Enable S3 bucket versioning
- Use IAM to restrict state access
- Enable state locking
- Use `.gitignore` for local state

```
# .gitignore
terraform.tfstate
terraform.tfstate.backup
.terraform/
*.tfvars  # If contains secrets
```

❌ **Don't:**
- Commit state files to Git
- Share state files via email
- Store state in public S3 buckets
- Edit state files manually

### Encrypted Remote State Example
```hcl
terraform {
  backend "s3" {
    bucket         = "my-state-bucket"
    key            = "terraform.tfstate"
    region         = "eu-central-1"
    encrypt        = true              # Server-side encryption
    kms_key_id     = "alias/terraform"  # Use KMS for encryption
    dynamodb_table = "terraform-locks"
  }
}
```

---

## State Disasters and Recovery

### Disaster 1: Deleted State File

**Problem:** Lost `terraform.tfstate`

**Solution:**
1. If using remote state, just run `terraform init` again
2. If local state with versioning in S3, recover from backup
3. Worst case: Recreate state by importing resources

### Disaster 2: Corrupted State

**Problem:** State file is corrupted

**Solution:**
```bash
# If remote state with versioning enabled
aws s3api list-object-versions \
  --bucket my-state-bucket \
  --prefix terraform.tfstate

# Download previous version
aws s3api get-object \
  --bucket my-state-bucket \
  --key terraform.tfstate \
  --version-id <version-id> \
  terraform.tfstate.backup

# Use the backup
mv terraform.tfstate.backup terraform.tfstate
```

### Disaster 3: State Locked Forever

**Problem:** Process crashed, lock not released

**Solution:**
```bash
terraform force-unlock <lock-id>
```

Get lock ID from error message:
```
Error: Error acquiring the state lock

Lock Info:
  ID:        a1b2c3d4-...
  Path:      my-state-bucket/terraform.tfstate
  Operation: OperationTypeApply
```

---

## Practical Exercise

**Task 1: Local State Management**
```bash
# 1. Create S3 bucket
# 2. Check state
terraform state list
terraform state show aws_s3_bucket.my_bucket

# 3. Add tags in code
# 4. See what changed
terraform plan

# 5. Apply and check state again
terraform apply
terraform state show aws_s3_bucket.my_bucket
```

**Task 2: Simulate State Loss**
```bash
# 1. Create infrastructure
terraform apply

# 2. Backup state
cp terraform.tfstate terraform.tfstate.backup

# 3. Delete state
rm terraform.tfstate

# 4. Try to apply (see error)
terraform apply

# 5. Restore state
cp terraform.tfstate.backup terraform.tfstate

# 6. Verify everything works
terraform plan
```

**Task 3: Import Existing Resource**
```bash
# 1. Create S3 bucket manually in AWS console
# 2. Write resource definition in Terraform
# 3. Import it
terraform import aws_s3_bucket.imported <bucket-name>
# 4. Update code to match
# 5. Verify with terraform plan
```

---

## Key Takeaways

✅ State is Terraform's memory of infrastructure

✅ **Never** edit state files manually

✅ **Never** commit state to Git

✅ Use remote state for production

✅ Enable state locking to prevent conflicts

✅ Use encryption for sensitive data

✅ Keep state backups (versioning in S3)

✅ Use separate states for different environments

---

## Next Steps

Now let's learn about Terraform modules - the key to reusable infrastructure code!

**Next:** [Module 08: Introduction to Modules](./08-intro-to-modules.md)
