# Terraform Interview Questions - Intermediate (Modules 06-09)

## Module 06: Variables and Outputs

### Q1: What are input variables in Terraform?
**Answer:** Input variables allow you to parameterize your Terraform configuration, making it reusable across different environments without changing the code.
```hcl
variable "environment" {
  type    = string
  default = "dev"
}
```

### Q2: What are the different ways to provide variable values?
**Answer:**
1. **Command line:** `terraform apply -var="env=prod"`
2. **Variable files:** `terraform apply -var-file="prod.tfvars"`
3. **terraform.tfvars:** Auto-loaded file
4. **Environment variables:** `export TF_VAR_environment="prod"`
5. **Default values:** In variable declaration

### Q3: What is variable precedence order in Terraform?
**Answer:** (highest to lowest priority)
1. Command line flags (`-var`)
2. `*.auto.tfvars` files (alphabetical)
3. `terraform.tfvars` file
4. Environment variables (`TF_VAR_*`)
5. Default values in variable blocks

### Q4: What variable types does Terraform support?
**Answer:**
- **Primitives:** string, number, bool
- **Collections:** list, set, map
- **Structural:** object, tuple
```hcl
variable "instance_count" { type = number }
variable "regions" { type = list(string) }
variable "tags" { type = map(string) }
variable "config" { type = object({ name = string, size = number }) }
```

### Q5: How do you add validation to variables?
**Answer:**
```hcl
variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Must be dev, staging, or prod."
  }
}
```

### Q6: What is a sensitive variable and how do you mark it?
**Answer:** Sensitive variables hide values in logs and output:
```hcl
variable "db_password" {
  type      = string
  sensitive = true
}
```
Values show as `(sensitive value)` in plan/apply output.

### Q7: What are output values and why use them?
**Answer:** Outputs display information after `terraform apply` and can be used by other Terraform configurations:
```hcl
output "instance_ip" {
  value = aws_instance.server.public_ip
}
```
Access with: `terraform output instance_ip`

### Q8: How do you reference a variable in code?
**Answer:** Use `var.` prefix:
```hcl
resource "aws_instance" "server" {
  instance_type = var.instance_type
}
```

### Q9: What are local values?
**Answer:** Locals are computed values used internally, not inputs from users:
```hcl
locals {
  full_name = "${var.prefix}-${var.environment}-bucket"
}

resource "aws_s3_bucket" "bucket" {
  bucket = local.full_name
}
```

### Q10: Difference between variables and locals?
**Answer:**
- **Variables:** Input parameters (from users/files)
- **Locals:** Computed/derived values (internal calculations)

---

## Module 07: Understanding State

### Q11: What is Terraform state and why is it important?
**Answer:** State is a JSON file that maps real-world resources to your configuration. It's essential because:
- Tracks resource IDs
- Stores metadata
- Improves performance (caching)
- Enables collaboration

### Q12: What are the dangers of editing state manually?
**Answer:**
- ❌ Corrupts state file
- ❌ Breaks resource tracking
- ❌ Causes drift between real infrastructure and state
- ❌ Can lead to duplicate resources or orphaned resources
**Always use `terraform state` commands instead**

### Q13: What is state locking and why is it needed?
**Answer:** State locking prevents multiple users from running Terraform simultaneously on the same state, which would cause conflicts and corruption. Implemented using DynamoDB in AWS.

### Q14: Compare local vs remote state
**Answer:**

| Feature | Local State | Remote State |
|---------|-------------|--------------|
| Location | Local disk | Cloud (S3, etc) |
| Collaboration | ❌ No | ✅ Yes |
| Locking | ❌ No | ✅ Yes |
| Encryption | ❌ No | ✅ Yes |
| Backup | Manual | Automatic |
| Use case | Learning, personal | Production, teams |

### Q15: How do you configure S3 backend for remote state?
**Answer:**
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "eu-central-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

### Q16: What is state drift?
**Answer:** State drift occurs when real-world infrastructure differs from Terraform state due to:
- Manual changes in AWS console
- Changes by other tools
- Resource deletion outside Terraform

Detect with: `terraform plan` or `terraform refresh`

### Q17: How do you import existing resources into Terraform?
**Answer:**
```bash
# 1. Write resource definition
resource "aws_s3_bucket" "existing" {}

# 2. Import
terraform import aws_s3_bucket.existing my-bucket-name

# 3. Update code to match
terraform plan  # See differences
```

### Q18: What does `terraform state mv` do?
**Answer:** Renames or moves a resource in state:
```bash
terraform state mv aws_instance.old aws_instance.new
```
Useful when refactoring code structure.

### Q19: What does `terraform state rm` do?
**Answer:** Removes resource from state WITHOUT deleting the actual resource:
```bash
terraform state rm aws_s3_bucket.bucket
```
The bucket still exists in AWS, but Terraform stops managing it.

### Q20: How do you recover from a deleted state file?
**Answer:**
1. **Remote state:** Reinitialize with `terraform init`
2. **S3 versioning:** Restore previous version from S3
3. **Backup file:** Use `terraform.tfstate.backup`
4. **No backup:** Manually import all resources (painful!)

---

## Module 08: Introduction to Modules

### Q21: What is a Terraform module?
**Answer:** A module is a container for multiple resources that are used together. It's a way to organize and reuse Terraform code.

### Q22: What's the difference between root module and child module?
**Answer:**
- **Root module:** The directory where you run `terraform apply`
- **Child module:** A module called by another module

### Q23: How do you use a module?
**Answer:**
```hcl
module "vpc" {
  source = "./modules/vpc"
  
  cidr_block = "10.0.0.0/16"
  environment = "prod"
}
```

### Q24: What module sources does Terraform support?
**Answer:**
- Local paths: `./modules/vpc`
- Terraform Registry: `terraform-aws-modules/vpc/aws`
- GitHub: `github.com/org/repo//module`
- Git: `git::https://example.com/repo.git//module`
- S3: `s3::https://s3.amazonaws.com/bucket/module.zip`

### Q25: How do you access module outputs?
**Answer:**
```hcl
module "vpc" {
  source = "./modules/vpc"
}

resource "aws_instance" "server" {
  subnet_id = module.vpc.subnet_id  # Access module output
}
```

### Q26: Why should you version your modules?
**Answer:**
- Prevents breaking changes
- Enables rollback
- Ensures consistency across environments
- Allows testing before updating
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"  # Pin to specific version
}
```

### Q27: What should every module have?
**Answer:**
- `main.tf` - Resources
- `variables.tf` - Input variables
- `outputs.tf` - Output values
- `README.md` - Documentation
- `versions.tf` - Version constraints (optional)

### Q28: How do you pass data between modules?
**Answer:** Using outputs and inputs:
```hcl
# Module A outputs
output "vpc_id" {
  value = aws_vpc.main.id
}

# Module B uses it
module "ec2" {
  source = "./modules/ec2"
  vpc_id = module.vpc.vpc_id  # Pass output from module A
}
```

### Q29: Can you use count with modules?
**Answer:** Yes!
```hcl
module "bucket" {
  source = "./modules/s3"
  count  = 3
  
  bucket_name = "bucket-${count.index}"
}
```

### Q30: What's better for modules: count or for_each?
**Answer:** **for_each** is better because:
- Resources have meaningful keys (not just 0, 1, 2)
- Removing items from the middle doesn't recreate everything
```hcl
module "vpc" {
  source   = "./modules/vpc"
  for_each = var.environments
  
  name = each.key
}
```

---

## Module 09: Loops and Conditionals

### Q31: What's the difference between count and for_each?
**Answer:**

| Feature | count | for_each |
|---------|-------|----------|
| Type | Integer | Set or Map |
| Access | Index (0, 1, 2) | Key (name) |
| Removal | Recreates resources | Only removes specific one |
| Best for | Fixed numbers | Dynamic lists/maps |

### Q32: How does count work?
**Answer:**
```hcl
resource "aws_instance" "server" {
  count = 3
  
  ami           = "ami-123"
  instance_type = "t3.micro"
  
  tags = {
    Name = "server-${count.index}"  # server-0, server-1, server-2
  }
}
```

### Q33: How does for_each work?
**Answer:**
```hcl
variable "environments" {
  default = ["dev", "staging", "prod"]
}

resource "aws_s3_bucket" "env" {
  for_each = toset(var.environments)
  
  bucket = "myapp-${each.value}"
}
```

### Q34: What is a for expression?
**Answer:** Transforms lists and maps:
```hcl
# List to list
locals {
  upper_names = [for name in var.names : upper(name)]
}

# List to map
locals {
  name_email = {
    for name in var.users : name => "${name}@example.com"
  }
}

# Filter with if
locals {
  prod_instances = [for i in var.instances : i if i.env == "prod"]
}
```

### Q35: What is the ternary operator in Terraform?
**Answer:** `condition ? true_value : false_value`
```hcl
resource "aws_instance" "server" {
  instance_type = var.env == "prod" ? "t3.large" : "t3.micro"
}
```

### Q36: How do you conditionally create resources?
**Answer:** Use count with ternary:
```hcl
variable "create_bucket" {
  type = bool
  default = false
}

resource "aws_s3_bucket" "backup" {
  count = var.create_bucket ? 1 : 0  # Creates 1 or 0 buckets
  bucket = "backup-bucket"
}
```

### Q37: What are dynamic blocks?
**Answer:** Dynamic blocks allow you to create repeated nested blocks:
```hcl
variable "ingress_rules" {
  default = [
    { port = 80 },
    { port = 443 },
    { port = 22 }
  ]
}

resource "aws_security_group" "web" {
  name = "web-sg"
  
  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}
```

### Q38: When should you use dynamic blocks?
**Answer:**
- ✅ When you have variable number of nested blocks
- ✅ When nested blocks depend on input variables
- ❌ Avoid overusing - can make code hard to read
- ❌ Don't use for top-level resources (use for_each instead)

### Q39: How do you reference resources created with count?
**Answer:**
```hcl
resource "aws_instance" "server" {
  count = 3
  # ...
}

# Access specific instance
output "first_ip" {
  value = aws_instance.server[0].public_ip
}

# Access all instances
output "all_ips" {
  value = aws_instance.server[*].public_ip
}
```

### Q40: How do you reference resources created with for_each?
**Answer:**
```hcl
resource "aws_instance" "server" {
  for_each = toset(["web", "db", "cache"])
  # ...
}

# Access specific instance
output "web_ip" {
  value = aws_instance.server["web"].public_ip
}

# Access all instances
output "all_ips" {
  value = {
    for key, instance in aws_instance.server :
    key => instance.public_ip
  }
}
```

---

## Scenario-Based Questions

### Q41: You need to create 5 identical S3 buckets. Which approach is better?
**Answer:**
```hcl
# Better: Use count or for_each
variable "bucket_names" {
  default = ["logs", "data", "backups", "archives", "temp"]
}

resource "aws_s3_bucket" "buckets" {
  for_each = toset(var.bucket_names)
  bucket   = "myapp-${each.value}"
}
```
**Why:** Avoids code duplication, easier to maintain

### Q42: How do you create different instance types for dev vs prod?
**Answer:**
```hcl
variable "environment" {
  default = "dev"
}

locals {
  instance_type = var.environment == "prod" ? "t3.large" : "t3.micro"
}

resource "aws_instance" "server" {
  instance_type = local.instance_type
}
```

### Q43: You need to create a VPC module that works for any AWS region. How?
**Answer:**
```hcl
# modules/vpc/variables.tf
variable "region" {
  type = string
}

variable "cidr_block" {
  type = string
}

# modules/vpc/main.tf
data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_subnet" "public" {
  for_each = toset(data.aws_availability_zones.available.names)
  
  vpc_id            = aws_vpc.main.id
  availability_zone = each.value
  # ...
}
```

### Q44: How would you manage 3 environments (dev/staging/prod) with one codebase?
**Answer:**
```
project/
├── modules/
│   └── infrastructure/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   └── dev.tfvars
│   ├── staging/
│   │   ├── main.tf
│   │   └── staging.tfvars
│   └── prod/
│       ├── main.tf
│       └── prod.tfvars
```

Each environment uses the same modules with different variables.

### Q45: Your team wants to use a module from Terraform Registry. What should you check?
**Answer:**
- ✅ Version stability and maintenance
- ✅ Documentation quality
- ✅ Number of downloads and stars
- ✅ Recent updates
- ✅ Source code quality
- ✅ License
**Always pin to specific version!**

---

## Advanced Concepts

### Q46: What is the `depends_on` argument?
**Answer:** Explicitly defines dependencies between resources:
```hcl
resource "aws_instance" "server" {
  # ...
  depends_on = [aws_s3_bucket.logs]
}
```
**Use sparingly** - Terraform usually handles dependencies automatically.

### Q47: What functions does Terraform provide?
**Answer:** Many! Examples:
- **String:** `upper()`, `lower()`, `replace()`, `format()`
- **Collection:** `length()`, `merge()`, `concat()`
- **Numeric:** `min()`, `max()`, `abs()`
- **Date:** `timestamp()`, `formatdate()`
- **IP:** `cidrsubnet()`, `cidrhost()`

### Q48: How do you use the merge function?
**Answer:**
```hcl
locals {
  common_tags = {
    Project   = "MyApp"
    ManagedBy = "Terraform"
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

### Q49: What is the splat operator?
**Answer:** The `[*]` operator extracts attributes from lists:
```hcl
# Instead of this:
output "ip_addresses" {
  value = [
    aws_instance.server[0].public_ip,
    aws_instance.server[1].public_ip,
    aws_instance.server[2].public_ip
  ]
}

# Use this:
output "ip_addresses" {
  value = aws_instance.server[*].public_ip
}
```

### Q50: How do you handle complex conditionals?
**Answer:** Use locals for readability:
```hcl
locals {
  instance_type = (
    var.environment == "prod" ? "t3.large" :
    var.environment == "staging" ? "t3.medium" :
    "t3.micro"
  )
  
  enable_monitoring = var.environment == "prod" ? true : false
  backup_retention  = var.environment == "prod" ? 30 : 7
}
```

---

## Key Takeaways for Interviews

✅ Understand variable types and precedence
✅ Know when to use count vs for_each (for_each is usually better)
✅ Explain state management and locking
✅ Understand modules and when to use them
✅ Know how to handle conditionals and loops
✅ Understand the importance of remote state for teams

---

**Next:** [Advanced Interview Questions](../03-advanced/interview-questions-advanced.md)
