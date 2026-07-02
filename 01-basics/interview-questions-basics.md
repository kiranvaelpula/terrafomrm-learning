# Terraform Interview Questions - Basics (Modules 01-05)

## Module 01: What is Terraform?

### Q1: What is Terraform?
**Answer:** Terraform is an open-source Infrastructure as Code (IaC) tool created by HashiCorp. It allows you to define, provision, and manage infrastructure using declarative configuration files written in HCL (HashiCorp Configuration Language).

### Q2: What is Infrastructure as Code (IaC)?
**Answer:** Infrastructure as Code is the practice of managing and provisioning infrastructure through code instead of manual processes. Benefits include version control, repeatability, consistency, and automation.

### Q3: What's the difference between declarative and imperative approaches?
**Answer:**
- **Declarative (Terraform):** You define the desired end state. Terraform figures out how to achieve it.
  ```hcl
  resource "aws_s3_bucket" "bucket" {
    bucket = "my-bucket"
  }
  ```
- **Imperative (Scripts):** You define step-by-step instructions on how to achieve the result.
  ```bash
  aws s3 mb s3://my-bucket
  aws s3api put-bucket-versioning --bucket my-bucket --versioning-configuration Status=Enabled
  ```

### Q4: Why use Terraform instead of manual infrastructure management?
**Answer:**
- **Automation:** No manual clicking in consoles
- **Version Control:** Track changes in Git
- **Consistency:** Same configuration every time
- **Scalability:** Easily replicate across environments
- **Documentation:** Code serves as documentation
- **Collaboration:** Team can review and approve changes

### Q5: What is HCL?
**Answer:** HCL (HashiCorp Configuration Language) is a declarative language designed for Terraform. It's human-readable and combines readability with expressiveness for defining infrastructure.

### Q6: Can Terraform manage multi-cloud infrastructure?
**Answer:** Yes! Terraform is cloud-agnostic and can manage resources across AWS, Azure, GCP, and 100+ other providers simultaneously using the same workflow.

---

## Module 02: Installation & Setup

### Q7: How do you verify Terraform installation?
**Answer:**
```bash
terraform version
# Output: Terraform v1.6.0
```

### Q8: What is the AWS CLI and why is it needed?
**Answer:** AWS CLI is a command-line tool for managing AWS services. Terraform uses AWS credentials configured via AWS CLI to authenticate and create resources in your AWS account.

### Q9: How do you configure AWS credentials for Terraform?
**Answer:** Multiple ways:
1. AWS CLI: `aws configure`
2. Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
3. Shared credentials file: `~/.aws/credentials`
4. IAM roles (for EC2 instances)

### Q10: What file extensions does Terraform use?
**Answer:**
- `.tf` - Terraform configuration files
- `.tfvars` - Variable value files
- `.tfstate` - State file (DO NOT edit manually)

---

## Module 03: Your First Resource

### Q11: What is a Terraform resource?
**Answer:** A resource is a component of your infrastructure (e.g., EC2 instance, S3 bucket, VPC). Each resource is declared using a resource block in Terraform.

### Q12: Explain this code:
```hcl
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-unique-bucket-name"
}
```
**Answer:**
- `resource` - Keyword to define a resource
- `"aws_s3_bucket"` - Resource type (AWS S3 bucket)
- `"my_bucket"` - Resource name (local identifier)
- `bucket = "..."` - Argument (bucket name)

### Q13: What is a Terraform provider?
**Answer:** A provider is a plugin that enables Terraform to interact with APIs of cloud providers (AWS, Azure, GCP) or other services. You must configure a provider before creating resources.

### Q14: What does `terraform init` do?
**Answer:**
1. Downloads required provider plugins
2. Initializes the backend (state storage)
3. Initializes modules
4. Creates `.terraform` directory

### Q15: What happens if you run `terraform apply` twice with the same configuration?
**Answer:** The second apply will show "No changes. Infrastructure is up-to-date." Terraform is idempotent - it only makes changes when needed.

---

## Module 04: Terraform Workflow

### Q16: What is the standard Terraform workflow?
**Answer:** **Write → Plan → Apply**
1. **Write:** Create/modify `.tf` files
2. **Plan:** `terraform plan` - Preview changes
3. **Apply:** `terraform apply` - Execute changes

### Q17: What does `terraform plan` do?
**Answer:** It shows what Terraform will do without actually making changes. It compares your configuration files with the current state and displays:
- `+` Resources to create
- `-` Resources to destroy
- `~` Resources to modify
- `-/+` Resources to replace

### Q18: What is terraform.tfstate?
**Answer:** The state file is Terraform's record of your infrastructure. It stores:
- Resource IDs and attributes
- Resource dependencies
- Current state of infrastructure
**Important:** Never edit manually, never delete, never commit to Git (contains secrets)

### Q19: Can you apply changes without running `terraform plan` first?
**Answer:** Yes, but it's not recommended. `terraform apply` shows a plan before asking for confirmation. However, best practice is to always run `terraform plan` separately to review changes carefully.

### Q20: What's the difference between `terraform destroy` and deleting the .tf file?
**Answer:**
- `terraform destroy` - Properly deletes all resources tracked in state
- Deleting .tf file then running `apply` - Also deletes resources but through drift detection
- Best practice: Use `terraform destroy` for explicit deletion

---

## Module 05: Basic Commands

### Q21: What does `terraform fmt` do?
**Answer:** Automatically formats Terraform configuration files to a canonical style (proper indentation, spacing, alignment). Run before committing code.

### Q22: What's the difference between `terraform validate` and `terraform plan`?
**Answer:**
- `terraform validate` - Checks syntax and configuration validity (fast, no cloud connection needed)
- `terraform plan` - Checks if resources can actually be created (slower, requires credentials)

### Q23: How do you target a specific resource for apply?
**Answer:**
```bash
terraform apply -target=aws_s3_bucket.my_bucket
```
Useful for applying changes to specific resources without affecting others.

### Q24: What does `terraform show` do?
**Answer:** Displays the current state or a saved plan in human-readable format. Useful for inspecting what Terraform knows about your infrastructure.

### Q25: What is the purpose of `terraform refresh`?
**Answer:** Updates the state file with the real-world infrastructure status. Useful when resources were modified outside Terraform. Note: `plan` and `apply` automatically refresh by default.

### Q26: How do you save a Terraform plan?
**Answer:**
```bash
terraform plan -out=myplan.tfplan
terraform apply myplan.tfplan
```

### Q27: What does the `-auto-approve` flag do?
**Answer:** Skips the interactive approval prompt for `apply` or `destroy`. Use only in automation/CI-CD pipelines, never manually.

### Q28: How do you enable debug logging in Terraform?
**Answer:**
```bash
export TF_LOG=DEBUG
export TF_LOG_PATH=terraform.log
terraform apply
```
Levels: TRACE, DEBUG, INFO, WARN, ERROR

### Q29: What does `terraform state list` do?
**Answer:** Lists all resources currently tracked in the Terraform state file.

### Q30: How would you remove a resource from Terraform state without deleting it?
**Answer:**
```bash
terraform state rm aws_s3_bucket.my_bucket
```
The actual AWS resource remains, but Terraform stops tracking it.

---

## Scenario-Based Questions

### Q31: You ran `terraform apply` but got an error. What should you do?
**Answer:**
1. Read the error message carefully
2. Fix the issue in your code
3. Run `terraform plan` to verify the fix
4. Run `terraform apply` again
Terraform is safe to retry - it won't duplicate resources.

### Q32: You accidentally deleted `terraform.tfstate`. How do you recover?
**Answer:**
1. If using remote state: Run `terraform init` to re-download
2. If local state with backup: Restore from `terraform.tfstate.backup`
3. If no backup: Must import resources manually using `terraform import`

### Q33: Two team members run `terraform apply` at the same time. What happens?
**Answer:** 
- **Without state locking:** Conflict! Both might modify infrastructure simultaneously.
- **With state locking (recommended):** Second person waits for the first to finish.

### Q34: How do you migrate from local state to remote state?
**Answer:**
1. Add backend configuration to code
2. Run `terraform init -migrate-state`
3. Confirm migration when prompted
4. Verify with `terraform plan`

### Q35: Your AWS credentials expired. What error will you see?
**Answer:** Authentication error from AWS provider, typically "UnauthorizedOperation" or "InvalidClientTokenId". Fix by running `aws configure` or refreshing credentials.

---

## Quick Fire Questions

### Q36: What language does Terraform use?
**Answer:** HCL (HashiCorp Configuration Language)

### Q37: Is Terraform free?
**Answer:** Yes, open-source and free. Terraform Cloud/Enterprise have paid tiers.

### Q38: Can Terraform manage on-premise infrastructure?
**Answer:** Yes, with appropriate providers (VMware, OpenStack, etc.)

### Q39: What's the file extension for Terraform files?
**Answer:** `.tf`

### Q40: What command initializes a Terraform project?
**Answer:** `terraform init`

### Q41: What command formats Terraform code?
**Answer:** `terraform fmt`

### Q42: What command validates Terraform syntax?
**Answer:** `terraform validate`

### Q43: What command shows planned changes?
**Answer:** `terraform plan`

### Q44: What command applies changes?
**Answer:** `terraform apply`

### Q45: What command destroys all resources?
**Answer:** `terraform destroy`

### Q46: Where are provider plugins stored?
**Answer:** `.terraform/providers/` directory

### Q47: Should you commit `.terraform/` to Git?
**Answer:** No, add to `.gitignore`

### Q48: Should you commit `terraform.tfstate` to Git?
**Answer:** No! It contains secrets. Use remote state instead.

### Q49: What's the default AWS region if not specified?
**Answer:** `us-east-1` (but always specify explicitly)

### Q50: Can you have multiple providers in one configuration?
**Answer:** Yes, you can use multiple providers and multiple regions simultaneously.

---

## Key Takeaways for Interviews

✅ Understand declarative vs imperative
✅ Know the Write → Plan → Apply workflow
✅ Explain what state files are and why they matter
✅ Know basic commands and when to use them
✅ Understand provider concept
✅ Know security basics (don't commit state/secrets)

---

**Next:** [Intermediate Interview Questions](../02-intermediate/interview-questions-intermediate.md)
