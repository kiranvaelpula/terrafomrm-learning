# Module 01: What is Terraform?

## 🎯 Learning Objectives
By the end of this module, you will:
- Understand what Terraform is and why it exists
- Know the difference between imperative and declarative approaches
- Understand Infrastructure as Code (IaC)
- Know when to use Terraform

---

## 📖 What is Terraform?

**Terraform is an Infrastructure as Code (IaC) tool** that lets you build, change, and version infrastructure safely and efficiently.

### Simple Analogy 🏗️

Think of Terraform like **architectural blueprints** for buildings:

- **Without blueprints** (Manual): You tell workers "put a wall here, add a door there" - prone to mistakes
- **With blueprints** (Terraform): You draw the complete plan once, and workers follow it exactly - consistent and repeatable

### Traditional vs. Terraform Approach

#### Traditional Way (Manual/Imperative):
```bash
# You manually click through AWS Console or run commands:
1. Log into AWS Console
2. Click "Create EC2 Instance"
3. Fill in instance type: t2.micro
4. Select VPC
5. Add security group
6. Click "Launch"
7. Wait... did I select the right subnet?
8. Six months later: "What settings did I use?"
```

#### Terraform Way (Declarative):
```hcl
# terraform.tf - Describe what you want
resource "aws_instance" "my_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "MyWebServer"
  }
}

# Run: terraform apply
# Terraform creates exactly what you described
# Six months later: Open the file and you know exactly what's running
```

---

## 🤔 Why Terraform?

### Problems with Manual Infrastructure

1. **Not Repeatable**
   - You click 20 buttons to create a server
   - Next time, you might miss step 15
   - Different people create resources differently

2. **Not Version Controlled**
   - "Who changed the security group?"
   - "What was the configuration before it broke?"
   - No history or rollback

3. **Not Documented**
   - Knowledge in people's heads
   - When they leave, knowledge is lost
   - New team members confused

4. **Time Consuming**
   - Creating 10 servers = same 20 clicks × 10 times
   - Updating 100 servers manually = hours of work

### Terraform Solves These Problems ✅

```
✅ Repeatable    : Same code = same infrastructure, every time
✅ Version Control: Git tracks all changes (who, what, when)
✅ Self-Documenting: Code is the documentation
✅ Fast          : Create 100 servers in minutes
✅ Multi-Cloud   : Works with AWS, Azure, GCP, etc.
✅ Safe          : Preview changes before applying
```

---

## 🏗️ What is Infrastructure as Code (IaC)?

**Infrastructure as Code = Treating infrastructure like software**

### Code Example:
```hcl
# This is code that creates infrastructure
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "production-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
  
  tags = {
    Name = "public-subnet"
  }
}
```

### Benefits of IaC:

| Benefit | Description | Example |
|---------|-------------|---------|
| **Automation** | No manual clicking | Create 100 servers with one command |
| **Consistency** | Same result every time | Dev looks exactly like prod |
| **Speed** | Rapid deployment | 5 minutes vs. 2 hours |
| **Safety** | Test before deploy | Preview changes first |
| **Collaboration** | Team can review | Pull requests for infrastructure |
| **Audit Trail** | Git history | See who changed what and when |

---

## 🆚 Declarative vs. Imperative

### Imperative (How to do it)
"Give me step-by-step instructions"

```bash
# Bash script - Imperative
aws ec2 create-vpc --cidr-block 10.0.0.0/16
VPC_ID=$(aws ec2 describe-vpcs --query 'Vpcs[0].VpcId')
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24
SUBNET_ID=$(aws ec2 describe-subnets --query 'Subnets[0].SubnetId')
# If any step fails, you're stuck!
```

### Declarative (What you want)
"This is my desired end state"

```hcl
# Terraform - Declarative
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.main.id  # Terraform figures out the ID
  cidr_block = "10.0.1.0/24"
}

# Terraform figures out HOW to create it
# Terraform handles dependencies automatically
```

---

## 🌍 Terraform Use Cases

### 1. Multi-Cloud Deployment
```hcl
# Same tool for AWS, Azure, GCP
provider "aws" {
  region = "us-east-1"
}

provider "azurerm" {
  features {}
}

# Create resources in both clouds with same workflow
```

### 2. Environment Management
```
Development Environment  → dev.tfvars
Staging Environment      → staging.tfvars
Production Environment   → production.tfvars

Same code, different configurations
```

### 3. Disaster Recovery
```bash
# Primary region fails? Deploy to backup region:
terraform apply -var="region=eu-west-1"

# Infrastructure recreated in minutes
```

### 4. Compliance & Governance
```hcl
# Enforce policies in code
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-data"
  
  # Force encryption
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  
  # Block public access (compliance requirement)
  public_access_block {
    block_public_acls   = true
    block_public_policy = true
  }
}
```

---

## 🎭 Terraform vs. Other Tools

| Tool | Type | Best For |
|------|------|----------|
| **Terraform** | Infrastructure | Creating cloud resources |
| **Ansible** | Configuration | Installing software, configuring servers |
| **CloudFormation** | Infrastructure (AWS only) | AWS-specific infrastructure |
| **Kubernetes** | Container Orchestration | Running containerized apps |
| **Docker** | Containerization | Packaging applications |

### When to Use Terraform:
- ✅ Creating cloud infrastructure (VPCs, servers, databases)
- ✅ Multi-cloud deployments
- ✅ Infrastructure that changes frequently
- ✅ Team collaboration on infrastructure

### When NOT to Use Terraform:
- ❌ Installing software on servers (use Ansible)
- ❌ Application deployment (use CI/CD pipelines)
- ❌ Container orchestration (use Kubernetes)
- ❌ One-time manual tasks

---

## 🧪 Real-World Example

### Scenario: Deploy a Web Application

**Without Terraform (Manual - 2 hours):**
1. Log into AWS Console
2. Create VPC
3. Create 2 subnets
4. Create Internet Gateway
5. Create Route Tables
6. Create Security Groups
7. Launch 3 EC2 instances
8. Create Load Balancer
9. Create RDS database
10. Configure everything manually

**With Terraform (5 minutes):**
```hcl
# main.tf (simplified)
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  cidr   = "10.0.0.0/16"
}

module "ec2_instances" {
  source        = "./modules/ec2"
  instance_count = 3
}

module "alb" {
  source = "terraform-aws-modules/alb/aws"
}

module "rds" {
  source = "terraform-aws-modules/rds/aws"
}
```

```bash
terraform init
terraform apply
# Everything created in 5 minutes, exactly as specified
```

---

## ✅ Knowledge Check

### Quiz:

1. **What is Infrastructure as Code?**
   <details>
   <summary>Click to reveal answer</summary>
   Managing and provisioning infrastructure through code instead of manual processes.
   </details>

2. **What is the difference between imperative and declarative?**
   <details>
   <summary>Click to reveal answer</summary>
   Imperative: Tell HOW to do it (step-by-step)
   Declarative: Tell WHAT you want (desired state)
   </details>

3. **Name 3 benefits of using Terraform**
   <details>
   <summary>Click to reveal answer</summary>
   1. Automation and speed
   2. Version control and collaboration
   3. Consistency and repeatability
   </details>

4. **Can Terraform work with multiple cloud providers?**
   <details>
   <summary>Click to reveal answer</summary>
   Yes! Terraform supports AWS, Azure, GCP, and 1,700+ other providers.
   </details>

---

## 🎯 Challenge Exercise

**Think about your current work:**

1. What infrastructure do you manage manually today?
2. How long does it take to create a new environment?
3. How do you document your infrastructure?
4. What happens when someone makes a manual change?

Write down your answers. We'll revisit this in Module 20 to see how Terraform solves these problems.

---

## 📚 Key Takeaways

```
✅ Terraform = Infrastructure as Code tool
✅ Declarative = Describe WHAT you want, not HOW
✅ Benefits = Automation, Repeatability, Version Control
✅ Multi-cloud = Same tool for AWS, Azure, GCP
✅ Self-documenting = Code IS the documentation
```

---

## ➡️ Next Module

Ready to install Terraform and set up your environment?

**[Module 02: Installation & Setup →](./02-installation-setup.md)**

---

**Progress:** ✅ Module 01 Complete | 📚 1/20 Modules
