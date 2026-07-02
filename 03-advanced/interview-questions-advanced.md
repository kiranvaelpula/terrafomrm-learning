# Terraform Interview Questions - Advanced & Best Practices

## Best Practices & Production

### Q1: What's the recommended project structure for production?
**Answer:**
```
project/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── modules/
│   ├── vpc/
│   ├── ec2/
│   └── rds/
├── .gitignore
└── README.md
```
Separate environments, reusable modules, clear documentation.

### Q2: What should you include in .gitignore for Terraform?
**Answer:**
```
*.tfstate
*.tfstate.*
*.tfstate.backup
.terraform/
.terraform.lock.hcl  # Optional
*.tfvars  # If contains secrets
crash.log
override.tf
```

### Q3: How do you handle secrets in Terraform?
**Answer:**
**❌ Never do:**
```hcl
password = "MySecret123!"  # Hardcoded
```

**✅ Best practices:**
1. Use AWS Secrets Manager:
```hcl
data "aws_secretsmanager_secret_version" "db_pass" {
  secret_id = "prod/db/password"
}
```

2. Environment variables:
```bash
export TF_VAR_db_password="SecurePass123!"
```

3. Mark as sensitive:
```hcl
variable "password" {
  type      = string
  sensitive = true
}
```

### Q4: What's the difference between terraform.tfvars and *.auto.tfvars?
**Answer:**
- `terraform.tfvars` - Loaded automatically
- `*.auto.tfvars` - All files matching pattern loaded automatically
- `custom.tfvars` - Must specify: `terraform apply -var-file="custom.tfvars"`

### Q5: How do you organize tags across all resources?
**Answer:**
```hcl
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = var.team_name
    CostCenter  = var.cost_center
  }
}

resource "aws_instance" "server" {
  tags = merge(
    local.common_tags,
    {
      Name = "web-server"
      Role = "webserver"
    }
  )
}
```

### Q6: Should you use workspaces or separate state files for environments?
**Answer:**
**Separate state files (Recommended):**
```
environments/
├── dev/     → s3://bucket/dev/terraform.tfstate
├── staging/ → s3://bucket/staging/terraform.tfstate
└── prod/    → s3://bucket/prod/terraform.tfstate
```

**Workspaces (Use for temporary environments):**
```bash
terraform workspace new feature-test
```

**Why separate state?**
- Better isolation
- Prevents accidental changes to prod
- Clearer access control
- Independent state locking

### Q7: What are Terraform workspaces and when to use them?
**Answer:** Workspaces allow multiple state files within the same backend.
```bash
terraform workspace list
terraform workspace new dev
terraform workspace select prod
```

**Use cases:**
- ✅ Temporary test environments
- ✅ Feature branch testing
- ❌ Production environments (use separate directories instead)

### Q8: How do you prevent accidental deletion of critical resources?
**Answer:** Use lifecycle rules:
```hcl
resource "aws_db_instance" "production" {
  # ...
  
  lifecycle {
    prevent_destroy = true  # Can't destroy with terraform destroy
  }
}

resource "aws_instance" "server" {
  lifecycle {
    create_before_destroy = true  # Create new before deleting old
  }
}

resource "aws_security_group" "sg" {
  lifecycle {
    ignore_changes = [
      description,  # Ignore changes to description
    ]
  }
}
```

### Q9: What's the difference between create_before_destroy and prevent_destroy?
**Answer:**
- `prevent_destroy = true` - Blocks all destroy operations
- `create_before_destroy = true` - Creates replacement before destroying original (for zero-downtime)

### Q10: How do you handle provider version constraints?
**Answer:**
```hcl
terraform {
  required_version = ">= 1.6.0"  # Terraform CLI version
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  # Allow 5.x, but not 6.0
    }
  }
}
```

**Version constraint operators:**
- `= 1.0.0` - Exact version
- `>= 1.0` - Greater than or equal
- `~> 1.0` - Allow rightmost version bump (1.0 to 1.9, not 2.0)
- `>= 1.0, < 2.0` - Range

---

## State Management Advanced

### Q11: How do you share state between Terraform configurations?
**Answer:** Use remote state data source:
```hcl
# Configuration A creates VPC
output "vpc_id" {
  value = aws_vpc.main.id
}

# Configuration B reads VPC ID
data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "terraform-state"
    key    = "network/terraform.tfstate"
    region = "eu-central-1"
  }
}

resource "aws_instance" "app" {
  vpc_id = data.terraform_remote_state.network.outputs.vpc_id
}
```

### Q12: What is state locking and how do you implement it in AWS?
**Answer:** State locking prevents concurrent modifications.

**Implementation:**
```hcl
# Create DynamoDB table
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
}

# Use in backend
terraform {
  backend "s3" {
    bucket         = "terraform-state"
    key            = "terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "terraform-locks"  # Enables locking
  }
}
```

### Q13: What happens if state lock fails to release?
**Answer:** Manual unlock required:
```bash
# Get lock ID from error message
terraform force-unlock <lock-id>
```
**Causes:**
- Process crashed
- Network interruption
- Ctrl+C during apply

### Q14: How do you migrate state from one backend to another?
**Answer:**
```bash
# 1. Update backend configuration
# 2. Run init with migration flag
terraform init -migrate-state

# 3. Confirm when prompted
# 4. Verify
terraform plan
```

### Q15: What's the difference between terraform refresh and terraform apply -refresh-only?
**Answer:**
- `terraform refresh` - Updates state (older command)
- `terraform apply -refresh-only` - Safer, shows plan before updating state (recommended)

---

## Modules Advanced

### Q16: How do you version control modules stored in Git?
**Answer:**
```bash
# Tag releases
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0

# Use in Terraform
module "vpc" {
  source = "git::https://github.com/myorg/modules.git//vpc?ref=v1.0.0"
}
```

### Q17: How do you test modules before using in production?
**Answer:**
1. **Local testing:**
```
test/
├── main.tf        # Test configuration
└── terraform.tfvars
```

2. **Automated testing with Terratest (Go):**
```go
func TestVPCModule(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "../modules/vpc",
    }
    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)
    
    vpcId := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcId)
}
```

3. **Terraform validate in CI/CD**

### Q18: What's the difference between a module and a resource?
**Answer:**
- **Resource:** Single infrastructure component (1 S3 bucket)
- **Module:** Collection of resources working together (VPC with subnets, route tables, gateways)

### Q19: How do you handle optional module inputs?
**Answer:**
```hcl
# Module variables.tf
variable "enable_vpn" {
  type    = bool
  default = false
}

variable "vpn_config" {
  type = object({
    cidr_block = string
  })
  default = null  # Optional
}

# Module main.tf
resource "aws_vpn_gateway" "vpn" {
  count  = var.enable_vpn ? 1 : 0
  vpc_id = aws_vpc.main.id
}
```

### Q20: How do you document modules?
**Answer:**
```markdown
# VPC Module

## Description
Creates a VPC with public and private subnets across multiple AZs.

## Usage
```hcl
module "vpc" {
  source = "./modules/vpc"
  
  vpc_cidr = "10.0.0.0/16"
  azs      = ["eu-central-1a", "eu-central-1b"]
}
```

## Requirements
| Name | Version |
|------|---------|
| terraform | >= 1.6 |
| aws | ~> 5.0 |

## Inputs
| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| vpc_cidr | VPC CIDR block | string | - | yes |
| azs | Availability zones | list(string) | - | yes |

## Outputs
| Name | Description |
|------|-------------|
| vpc_id | VPC ID |
| subnet_ids | List of subnet IDs |
```

---

## CI/CD Integration

### Q21: What's a typical Terraform CI/CD workflow?
**Answer:**
```yaml
# Pull Request
- terraform fmt -check
- terraform validate
- terraform plan
- Post plan as PR comment

# Merge to main
- terraform apply -auto-approve

# With approval
- Manual approval step
- terraform apply
```

### Q22: How do you implement Terraform in GitHub Actions?
**Answer:**
```yaml
name: Terraform

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.6.0
      
      - name: Terraform Format
        run: terraform fmt -check -recursive
      
      - name: Terraform Init
        run: terraform init
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      
      - name: Terraform Validate
        run: terraform validate
      
      - name: Terraform Plan
        run: terraform plan -no-color
        continue-on-error: true
      
      - name: Terraform Apply
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: terraform apply -auto-approve
```

### Q23: How do you store AWS credentials securely in CI/CD?
**Answer:**
- ✅ GitHub Secrets
- ✅ AWS IAM Roles for GitHub Actions (OIDC)
- ✅ HashiCorp Vault
- ❌ Never commit to code
- ❌ Never in logs

**Best approach (OIDC):**
```yaml
- name: Configure AWS Credentials
  uses: aws-actions/configure-aws-credentials@v2
  with:
    role-to-assume: arn:aws:iam::123456789:role/GitHubActionsRole
    aws-region: eu-central-1
```

### Q24: What is Terraform Cloud and when should you use it?
**Answer:** Terraform Cloud is HashiCorp's managed service providing:
- Remote state storage
- Remote execution
- State locking
- Policy as code (Sentinel)
- Cost estimation
- Private module registry

**Use when:**
- Team collaboration needed
- Need policy enforcement
- Want managed state without setting up S3/DynamoDB
- Need audit logs

### Q25: What is the difference between terraform plan and terraform apply?
**Answer:**
- `plan` - Read-only, shows what will change
- `apply` - Executes changes, updates state

**apply includes plan:**
```bash
terraform apply
# Shows plan
# Asks: "Do you want to perform these actions?"
```

---

## Performance & Optimization

### Q26: How do you speed up Terraform operations?
**Answer:**
1. **Increase parallelism:**
```bash
terraform apply -parallelism=20  # Default is 10
```

2. **Target specific resources:**
```bash
terraform plan -target=aws_instance.web
```

3. **Split large configurations:**
- Separate networking, compute, database
- Use modules

4. **Use -refresh=false:**
```bash
terraform plan -refresh=false  # Skip state refresh
```

### Q27: What is the -target flag and when should you use it?
**Answer:**
```bash
terraform apply -target=aws_s3_bucket.logs
```

**Use cases:**
- ✅ Troubleshooting specific resource
- ✅ Emergency fixes
- ❌ Don't use regularly (breaks dependency management)

### Q28: How do you handle large infrastructure deployments?
**Answer:**
1. **Split into layers:**
```
├── 1-network/
├── 2-security/
├── 3-compute/
└── 4-database/
```

2. **Use workspaces or separate states**

3. **Increase timeouts:**
```hcl
resource "aws_db_instance" "db" {
  timeouts {
    create = "60m"
    update = "60m"
    delete = "60m"
  }
}
```

### Q29: What causes "Error acquiring state lock"?
**Answer:**
**Causes:**
- Another terraform process running
- Previous process crashed without releasing lock
- Network issues

**Solution:**
```bash
terraform force-unlock <lock-id>
```

### Q30: How do you handle Terraform timeouts?
**Answer:**
```hcl
resource "aws_db_instance" "db" {
  # ...
  
  timeouts {
    create = "60m"
    update = "60m"
    delete = "2h"
  }
}
```

---

## Security & Compliance

### Q31: What are Terraform Sentinel policies?
**Answer:** Sentinel is HashiCorp's policy-as-code framework (Terraform Cloud/Enterprise only):
```hcl
# Ensure all S3 buckets are encrypted
import "tfplan"

main = rule {
  all tfplan.resources.aws_s3_bucket as _, instances {
    all instances as _, r {
      r.applied.server_side_encryption_configuration is not null
    }
  }
}
```

### Q32: How do you scan Terraform code for security issues?
**Answer:**
**Tools:**
1. **tfsec** - Static analysis
```bash
tfsec .
```

2. **Checkov** - Policy as code
```bash
checkov -d .
```

3. **Terraform validate**
```bash
terraform validate
```

4. **Custom validation rules:**
```hcl
variable "environment" {
  validation {
    condition     = can(regex("^(dev|staging|prod)$", var.environment))
    error_message = "Invalid environment."
  }
}
```

### Q33: How do you implement least privilege access for Terraform?
**Answer:**
```hcl
# IAM policy for Terraform
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "s3:*",
        "rds:*"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "eu-central-1"
        }
      }
    }
  ]
}
```

**Best practices:**
- Separate IAM roles per environment
- Use resource-specific permissions
- Enable MFA for production
- Audit with CloudTrail

### Q34: How do you handle compliance requirements (GDPR, HIPAA)?
**Answer:**
1. **Encryption at rest:**
```hcl
resource "aws_s3_bucket_server_side_encryption_configuration" "bucket" {
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
```

2. **Encryption in transit:**
```hcl
resource "aws_lb_listener" "https" {
  protocol = "HTTPS"
  ssl_policy = "ELBSecurityPolicy-TLS-1-2-2017-01"
}
```

3. **Logging and auditing:**
```hcl
resource "aws_s3_bucket_logging" "logs" {
  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = "access-logs/"
}
```

4. **Tagging for compliance:**
```hcl
tags = {
  Compliance = "HIPAA"
  DataClass  = "PHI"
}
```

### Q35: How do you rotate secrets managed by Terraform?
**Answer:**
**Don't manage secrets directly in Terraform!**

**Better approach:**
1. **Use AWS Secrets Manager:**
```hcl
resource "aws_secretsmanager_secret" "db_password" {
  name = "prod/db/password"
}

resource "aws_secretsmanager_secret_rotation" "db_password" {
  secret_id           = aws_secretsmanager_secret.db_password.id
  rotation_lambda_arn = aws_lambda_function.rotate.arn
  
  rotation_rules {
    automatically_after_days = 30
  }
}
```

2. **Reference in code:**
```hcl
data "aws_secretsmanager_secret_version" "db_pass" {
  secret_id = aws_secretsmanager_secret.db_password.id
}
```

---

## Troubleshooting & Debugging

### Q36: How do you debug Terraform issues?
**Answer:**
1. **Enable debug logging:**
```bash
export TF_LOG=DEBUG
export TF_LOG_PATH=terraform.log
terraform apply
```

2. **Check provider logs:**
```bash
export TF_LOG=TRACE
```

3. **Validate configuration:**
```bash
terraform validate
terraform fmt -check
```

4. **Use terraform console:**
```bash
terraform console
> var.environment
> local.instance_type
```

### Q37: What does "cycle" error mean?
**Answer:** Circular dependency detected:
```hcl
# Bad - creates cycle
resource "aws_instance" "a" {
  subnet_id = aws_subnet.b.id
}

resource "aws_subnet" "b" {
  vpc_id = aws_instance.a.vpc_id  # Circular!
}
```

**Fix:** Remove circular reference or use `depends_on`

### Q38: How do you handle "resource already exists" errors?
**Answer:**
1. **Import existing resource:**
```bash
terraform import aws_s3_bucket.bucket my-existing-bucket
```

2. **Remove from state if duplicate:**
```bash
terraform state rm aws_s3_bucket.bucket
```

3. **Use unique names:**
```hcl
resource "aws_s3_bucket" "bucket" {
  bucket = "myapp-${var.environment}-${random_id.bucket.hex}"
}
```

### Q39: What causes "Error loading state" errors?
**Answer:**
**Causes:**
- Corrupted state file
- Network issues accessing remote state
- Wrong backend configuration
- State locked by another process

**Solutions:**
```bash
# Check backend config
terraform init

# Force unlock if stuck
terraform force-unlock <lock-id>

# Restore from backup
cp terraform.tfstate.backup terraform.tfstate
```

### Q40: How do you recover from a failed apply?
**Answer:**
1. **Check what was created:**
```bash
terraform show
terraform state list
```

2. **Fix the error in code**

3. **Rerun apply:**
```bash
terraform apply
```

Terraform is idempotent - safe to retry!

---

## Real-World Scenarios

### Q41: Your team member manually created resources in AWS. How do you bring them under Terraform management?
**Answer:**
```bash
# 1. Write resource definition
resource "aws_instance" "existing" {
  # Add basic structure
}

# 2. Import
terraform import aws_instance.existing i-1234567890abcdef0

# 3. Run plan to see differences
terraform plan

# 4. Update code to match reality
# 5. Verify
terraform plan  # Should show no changes
```

### Q42: How do you implement blue-green deployment with Terraform?
**Answer:**
```hcl
variable "active_version" {
  default = "blue"
}

resource "aws_instance" "blue" {
  count = var.active_version == "blue" ? 3 : 0
  # ...
}

resource "aws_instance" "green" {
  count = var.active_version == "green" ? 3 : 0
  # ...
}

resource "aws_lb_target_group_attachment" "active" {
  target_group_arn = aws_lb_target_group.main.arn
  target_id        = var.active_version == "blue" ? 
                     aws_instance.blue[0].id : 
                     aws_instance.green[0].id
}
```

### Q43: How do you implement disaster recovery?
**Answer:**
1. **State backup:**
```hcl
# S3 versioning
resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

2. **Cross-region replication:**
```hcl
resource "aws_s3_bucket_replication_configuration" "replication" {
  role   = aws_iam_role.replication.arn
  bucket = aws_s3_bucket.terraform_state.id
  
  rule {
    status = "Enabled"
    destination {
      bucket = aws_s3_bucket.terraform_state_dr.arn
      storage_class = "STANDARD_IA"
    }
  }
}
```

3. **Infrastructure replication:**
```
# Deploy same infrastructure in DR region
├── us-east-1/
└── eu-west-1/  # DR region
```

### Q44: How do you handle database password rotation without downtime?
**Answer:**
```hcl
# Use AWS Secrets Manager rotation
resource "aws_secretsmanager_secret_rotation" "db" {
  secret_id           = aws_secretsmanager_secret.db_password.id
  rotation_lambda_arn = aws_lambda_function.rotate_secret.arn
  
  rotation_rules {
    automatically_after_days = 30
  }
}

# Application reads from Secrets Manager
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
}

resource "aws_db_instance" "db" {
  password = data.aws_secretsmanager_secret_version.db_password.secret_string
  
  lifecycle {
    ignore_changes = [password]  # Let Secrets Manager handle rotation
  }
}
```

### Q45: How do you manage Terraform for a 100+ person team?
**Answer:**
1. **Separate repositories by service:**
```
├── network-infra/
├── compute-infra/
├── database-infra/
└── monitoring-infra/
```

2. **Use Terraform Cloud workspaces**

3. **Implement approval workflows:**
```yaml
- terraform plan
- Manual approval required
- terraform apply
```

4. **Policy enforcement (Sentinel)**

5. **Module registry for reusable components**

6. **Clear CODEOWNERS:**
```
# CODEOWNERS
/network-infra/ @network-team
/database-infra/ @dba-team
```

---

## Key Takeaways

✅ Use remote state with locking for teams
✅ Never commit secrets or state files
✅ Version control modules
✅ Implement CI/CD for Terraform
✅ Use security scanning tools (tfsec, Checkov)
✅ Separate environments with different state files
✅ Document everything
✅ Test before production deployment

---

## HashiCorp Certified: Terraform Associate Exam Tips

**Exam focuses on:**
- IaC concepts
- Terraform workflow (init, plan, apply)
- State management
- Modules
- Variables and outputs
- Terraform Cloud basics

**Study tips:**
- Practice hands-on labs
- Understand state management deeply
- Know when to use count vs for_each
- Memorize common commands
- Understand module sources

**Resources:**
- HashiCorp Learn: https://learn.hashicorp.com/terraform
- Practice exams
- Official study guide

Good luck! 🚀
