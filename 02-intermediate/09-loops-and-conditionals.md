# Module 09: Loops and Conditionals

## Why Loops and Conditionals?

Instead of copy-pasting resources, use loops to create multiple similar resources dynamically.

---

## Count - The Simple Loop

### Basic Example

**Without count (repetitive):**
```hcl
resource "aws_instance" "server1" {
  ami           = "ami-123456"
  instance_type = "t3.micro"
}

resource "aws_instance" "server2" {
  ami           = "ami-123456"
  instance_type = "t3.micro"
}

resource "aws_instance" "server3" {
  ami           = "ami-123456"
  instance_type = "t3.micro"
}
```

**With count:**
```hcl
resource "aws_instance" "server" {
  count = 3
  
  ami           = "ami-123456"
  instance_type = "t3.micro"
  
  tags = {
    Name = "server-${count.index}"
  }
}
```

**Result:** Creates 3 instances named `server-0`, `server-1`, `server-2`

### Count with List

```hcl
variable "availability_zones" {
  default = ["eu-central-1a", "eu-central-1b", "eu-central-1c"]
}

resource "aws_subnet" "public" {
  count = length(var.availability_zones)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index}.0/24"
  availability_zone = var.availability_zones[count.index]
  
  tags = {
    Name = "public-subnet-${count.index}"
  }
}
```

### Accessing Count Resources

```hcl
# Reference specific instance
output "first_instance_id" {
  value = aws_instance.server[0].id
}

# Reference all instances
output "all_instance_ids" {
  value = aws_instance.server[*].id
}
```

---

## For_Each - The Better Loop

### Why for_each is Better Than Count

**Problem with count:**
```hcl
variable "users" {
  default = ["alice", "bob", "charlie"]
}

resource "aws_iam_user" "users" {
  count = length(var.users)
  name  = var.users[count.index]
}

# If you remove "bob" from the middle:
variable "users" {
  default = ["alice", "charlie"]
}

# Terraform will:
# - Rename bob → charlie
# - Delete charlie
# ❌ Wrong! Should just delete bob
```

**Solution with for_each:**
```hcl
variable "users" {
  default = ["alice", "bob", "charlie"]
}

resource "aws_iam_user" "users" {
  for_each = toset(var.users)
  name     = each.value
}

# Remove "bob":
variable "users" {
  default = ["alice", "charlie"]
}

# Terraform will:
# - Delete only bob
# ✅ Correct!
```

### For_Each with Set

```hcl
variable "environments" {
  type    = set(string)
  default = ["dev", "staging", "prod"]
}

resource "aws_s3_bucket" "env_buckets" {
  for_each = var.environments
  
  bucket = "myapp-${each.value}-bucket"
  
  tags = {
    Environment = each.value
  }
}

# Access outputs
output "dev_bucket_id" {
  value = aws_s3_bucket.env_buckets["dev"].id
}
```

### For_Each with Map (Most Common)

```hcl
variable "instances" {
  type = map(object({
    instance_type = string
    ami           = string
  }))
  
  default = {
    web = {
      instance_type = "t3.micro"
      ami           = "ami-123456"
    }
    db = {
      instance_type = "t3.small"
      ami           = "ami-789012"
    }
    cache = {
      instance_type = "t3.micro"
      ami           = "ami-345678"
    }
  }
}

resource "aws_instance" "servers" {
  for_each = var.instances
  
  ami           = each.value.ami
  instance_type = each.value.instance_type
  
  tags = {
    Name = "${each.key}-server"
  }
}

# Outputs
output "web_server_ip" {
  value = aws_instance.servers["web"].public_ip
}

output "all_server_ips" {
  value = {
    for key, instance in aws_instance.servers :
    key => instance.public_ip
  }
}
```

---

## For Expressions - Transform Data

### List to List

```hcl
variable "names" {
  default = ["alice", "bob", "charlie"]
}

locals {
  uppercase_names = [for name in var.names : upper(name)]
  # Result: ["ALICE", "BOB", "CHARLIE"]
}
```

### List to Map

```hcl
variable "users" {
  default = ["alice", "bob", "charlie"]
}

locals {
  user_emails = {
    for name in var.users :
    name => "${name}@example.com"
  }
  # Result: {
  #   alice = "alice@example.com"
  #   bob = "bob@example.com"
  #   charlie = "charlie@example.com"
  # }
}
```

### Map to Map (Transform)

```hcl
variable "instances" {
  default = {
    web = "t3.micro"
    db  = "t3.small"
  }
}

locals {
  instance_details = {
    for name, type in var.instances :
    name => {
      instance_type = type
      monitoring    = name == "db" ? true : false
    }
  }
}
```

### Filter with If

```hcl
variable "numbers" {
  default = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}

locals {
  even_numbers = [for num in var.numbers : num if num % 2 == 0]
  # Result: [2, 4, 6, 8, 10]
}
```

---

## Conditional Expressions (Ternary Operator)

### Syntax: `condition ? true_value : false_value`

### Basic Example

```hcl
variable "environment" {
  default = "prod"
}

resource "aws_instance" "server" {
  ami           = "ami-123456"
  instance_type = var.environment == "prod" ? "t3.large" : "t3.micro"
  # If prod → t3.large, else → t3.micro
}
```

### Multiple Conditionals

```hcl
locals {
  instance_type = (
    var.environment == "prod" ? "t3.large" :
    var.environment == "staging" ? "t3.medium" :
    "t3.micro"
  )
}
```

### Conditional Resource Creation

```hcl
variable "create_backup" {
  type    = bool
  default = false
}

resource "aws_s3_bucket" "backup" {
  count = var.create_backup ? 1 : 0
  
  bucket = "myapp-backup-bucket"
}

# If create_backup = true → Creates 1 bucket
# If create_backup = false → Creates 0 buckets (nothing)
```

---

## Dynamic Blocks - Nested Loops

### Problem: Repeated Nested Blocks

```hcl
resource "aws_security_group" "example" {
  name = "example"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
}
```

### Solution: Dynamic Block

```hcl
variable "ingress_rules" {
  default = [
    { port = 80, cidr = ["0.0.0.0/0"] },
    { port = 443, cidr = ["0.0.0.0/0"] },
    { port = 22, cidr = ["10.0.0.0/8"] }
  ]
}

resource "aws_security_group" "example" {
  name = "example"
  
  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = ingress.value.cidr
    }
  }
}
```

### Complex Dynamic Block

```hcl
variable "security_rules" {
  type = map(object({
    port        = number
    protocol    = string
    cidr_blocks = list(string)
    description = string
  }))
  
  default = {
    http = {
      port        = 80
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = "HTTP access"
    }
    https = {
      port        = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = "HTTPS access"
    }
    ssh = {
      port        = 22
      protocol    = "tcp"
      cidr_blocks = ["10.0.0.0/8"]
      description = "SSH access from internal"
    }
  }
}

resource "aws_security_group" "example" {
  name = "example-sg"
  
  dynamic "ingress" {
    for_each = var.security_rules
    content {
      description = ingress.value.description
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

---

## Practical Examples

### Example 1: Multi-Region Deployment

```hcl
variable "regions" {
  default = {
    eu = {
      region = "eu-central-1"
      cidr   = "10.0.0.0/16"
    }
    us = {
      region = "us-east-1"
      cidr   = "10.1.0.0/16"
    }
  }
}

provider "aws" {
  alias  = "multi"
  region = "eu-central-1"
}

module "vpc" {
  source   = "./modules/vpc"
  for_each = var.regions
  
  providers = {
    aws = aws.multi
  }
  
  region     = each.value.region
  cidr_block = each.value.cidr
  name       = "${each.key}-vpc"
}
```

### Example 2: Environment-Specific Configuration

```hcl
variable "environment" {
  default = "dev"
}

locals {
  env_config = {
    dev = {
      instance_type = "t3.micro"
      instance_count = 1
      enable_monitoring = false
    }
    staging = {
      instance_type = "t3.small"
      instance_count = 2
      enable_monitoring = true
    }
    prod = {
      instance_type = "t3.large"
      instance_count = 3
      enable_monitoring = true
    }
  }
  
  config = local.env_config[var.environment]
}

resource "aws_instance" "app" {
  count = local.config.instance_count
  
  ami           = "ami-123456"
  instance_type = local.config.instance_type
  monitoring    = local.config.enable_monitoring
  
  tags = {
    Name = "app-${var.environment}-${count.index}"
  }
}
```

### Example 3: Conditional Resources

```hcl
variable "environment" {
  default = "dev"
}

variable "enable_backup" {
  type    = bool
  default = false
}

# Create backup bucket only in prod
resource "aws_s3_bucket" "backup" {
  count = var.environment == "prod" ? 1 : 0
  
  bucket = "myapp-backup-${var.environment}"
}

# Create monitoring only if enabled
resource "aws_cloudwatch_metric_alarm" "cpu" {
  count = var.enable_backup ? 1 : 0
  
  alarm_name = "high-cpu"
  # ... other configuration
}
```

---

## Common Patterns

### Pattern 1: Create Resources from List

```hcl
variable "bucket_names" {
  default = ["logs", "data", "backups"]
}

resource "aws_s3_bucket" "buckets" {
  for_each = toset(var.bucket_names)
  bucket   = "myapp-${each.value}"
}
```

### Pattern 2: Create Subnets Across AZs

```hcl
variable "availability_zones" {
  default = ["eu-central-1a", "eu-central-1b", "eu-central-1c"]
}

resource "aws_subnet" "public" {
  for_each = toset(var.availability_zones)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, index(var.availability_zones, each.value))
  availability_zone = each.value
  
  tags = {
    Name = "public-${each.value}"
  }
}
```

### Pattern 3: Merge Maps

```hcl
variable "common_tags" {
  default = {
    Project   = "MyApp"
    ManagedBy = "Terraform"
  }
}

variable "environment" {
  default = "dev"
}

resource "aws_instance" "server" {
  ami           = "ami-123456"
  instance_type = "t3.micro"
  
  tags = merge(
    var.common_tags,
    {
      Environment = var.environment
      Name        = "web-server"
    }
  )
}
```

---

## Practical Exercise

**Task: Create dynamic security group**

```hcl
# 1. Define variable
variable "allowed_ports" {
  default = [
    { port = 80, description = "HTTP" },
    { port = 443, description = "HTTPS" },
    { port = 22, description = "SSH" }
  ]
}

# 2. Create security group with dynamic rules
resource "aws_security_group" "web" {
  name = "web-sg"
  
  dynamic "ingress" {
    for_each = var.allowed_ports
    content {
      description = ingress.value.description
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}

# 3. Test with different ports
# 4. Try adding/removing ports
```

---

## Key Takeaways

✅ Use `count` for simple loops (0-N)

✅ Use `for_each` for loops with identifiable items (better than count)

✅ Use `for` expressions to transform lists and maps

✅ Use ternary operator `? :` for conditionals

✅ Use `dynamic` blocks for repeated nested blocks

✅ `for_each` prevents unwanted resource recreation

✅ Combine conditionals with count for optional resources

---

## Next Steps

Learn about best practices and how to organize your Terraform projects!

**Next:** [Module 10: Best Practices](../03-advanced/10-best-practices.md)
