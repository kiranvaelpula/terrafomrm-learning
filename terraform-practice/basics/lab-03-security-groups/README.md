# Lab 03: Security Groups Deep Dive

**Difficulty**: Beginner  
**Time**: 20 minutes  
**Cost**: Free (Security groups have no cost)

## 🎯 Objectives

- Create security groups with multiple rules
- Use dynamic blocks for repetitive configuration
- Understand ingress and egress rules
- Reference security groups from other resources

## 📋 Prerequisites

- Completed Labs 01-02
- Understanding of networking basics (ports, protocols, CIDR)

## 🔨 Tasks

### Task 1: Create Basic Security Group

Create `main.tf`:

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

# Security Group for Web Server
resource "aws_security_group" "web" {
  name        = "terraform-lab-web-sg"
  description = "Security group for web servers"

  # HTTP from anywhere
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP from anywhere"
  }

  # HTTPS from anywhere
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS from anywhere"
  }

  # SSH from specific IP (replace with your IP)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["YOUR_IP/32"]  # TODO: Replace with your IP
    description = "SSH from my IP"
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "Terraform Lab Web SG"
    Environment = "Learning"
  }
}
```

### Task 2: Create Database Security Group

```hcl
# Security Group for Database
resource "aws_security_group" "database" {
  name        = "terraform-lab-db-sg"
  description = "Security group for database servers"

  # MySQL from web security group only
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "MySQL from web servers"
  }

  # PostgreSQL from web security group
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "PostgreSQL from web servers"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "Terraform Lab DB SG"
    Environment = "Learning"
  }
}
```

### Task 3: Use Dynamic Blocks for Multiple Ports

Create `variables.tf`:

```hcl
variable "ingress_ports" {
  description = "List of ingress ports to allow"
  type = list(object({
    port        = number
    protocol    = string
    cidr_blocks = list(string)
    description = string
  }))
  
  default = [
    {
      port        = 80
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = "HTTP"
    },
    {
      port        = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = "HTTPS"
    },
    {
      port        = 8080
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = "Alternative HTTP"
    }
  ]
}
```

Add dynamic security group:

```hcl
# Security Group with Dynamic Blocks
resource "aws_security_group" "dynamic" {
  name        = "terraform-lab-dynamic-sg"
  description = "Security group using dynamic blocks"

  dynamic "ingress" {
    for_each = var.ingress_ports
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
      description = ingress.value.description
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "Terraform Lab Dynamic SG"
  }
}
```

### Task 4: Create Security Group Rules as Separate Resources

```hcl
# Alternative: Separate SG and rules
resource "aws_security_group" "app" {
  name        = "terraform-lab-app-sg"
  description = "Security group for application servers"

  tags = {
    Name = "Terraform Lab App SG"
  }
}

# Ingress rule for HTTP
resource "aws_security_group_rule" "app_http" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.app.id
  description       = "HTTP access"
}

# Ingress rule for app from web SG
resource "aws_security_group_rule" "app_from_web" {
  type                     = "ingress"
  from_port                = 8080
  to_port                  = 8080
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.web.id
  security_group_id        = aws_security_group.app.id
  description              = "App port from web servers"
}

# Egress rule
resource "aws_security_group_rule" "app_egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.app.id
  description       = "All outbound"
}
```

### Task 5: Create Outputs

Create `outputs.tf`:

```hcl
output "web_sg_id" {
  description = "ID of web security group"
  value       = aws_security_group.web.id
}

output "database_sg_id" {
  description = "ID of database security group"
  value       = aws_security_group.database.id
}

output "dynamic_sg_id" {
  description = "ID of dynamic security group"
  value       = aws_security_group.dynamic.id
}

output "app_sg_id" {
  description = "ID of app security group"
  value       = aws_security_group.app.id
}

output "all_security_groups" {
  description = "All security group IDs"
  value = {
    web      = aws_security_group.web.id
    database = aws_security_group.database.id
    dynamic  = aws_security_group.dynamic.id
    app      = aws_security_group.app.id
  }
}
```

## ✅ Validation Steps

1. **Find Your IP**:
   ```bash
   curl ifconfig.me
   ```
   Update the SSH ingress rule with your IP

2. **Initialize and Plan**:
   ```bash
   terraform init
   terraform plan
   ```
   - Should show 4 security groups and 3 rules

3. **Apply**:
   ```bash
   terraform apply
   ```

4. **Verify in AWS Console**:
   - EC2 → Security Groups
   - Find your security groups
   - Check ingress/egress rules

5. **View Outputs**:
   ```bash
   terraform output
   terraform output -json all_security_groups | jq
   ```

## 🧹 Cleanup

```bash
terraform destroy
```

## 📚 Key Concepts Learned

- Security group creation and configuration
- Ingress and egress rules
- CIDR blocks and IP filtering
- Security group references
- Dynamic blocks for repetitive configuration
- Separate security group rules
- Security group dependencies

## 🎓 Challenge

1. **Add More Rules**:
   - Allow ICMP (ping) from your IP
   - Allow RDP (3389) for Windows servers
   - Create rules for specific CIDR ranges

2. **Create a Bastion Security Group**:
   - Only allow SSH from your IP
   - Reference it from other security groups

3. **Add IPv6 Support**:
   ```hcl
   ipv6_cidr_blocks = ["::/0"]
   ```

4. **Add Prefix Lists**:
   ```hcl
   prefix_list_ids = ["pl-xxxxxx"]
   ```

## 💡 Tips

- Always use specific CIDR blocks in production (never 0.0.0.0/0 for SSH)
- Use security group references instead of CIDR blocks when possible
- Document each rule with descriptions
- Group related ports together
- Use dynamic blocks when you have many similar rules
- Separate security group rules provide more flexibility

## ⚠️ Security Best Practices

- **Never open SSH (22) to 0.0.0.0/0**
- Use bastion hosts for SSH access
- Follow principle of least privilege
- Regular audit of security group rules
- Use descriptive names and descriptions
- Tag security groups properly

## 📖 Reference

- [AWS Security Group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group)
- [Security Group Rule](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule)
- [Dynamic Blocks](https://developer.hashicorp.com/terraform/language/expressions/dynamic-blocks)
