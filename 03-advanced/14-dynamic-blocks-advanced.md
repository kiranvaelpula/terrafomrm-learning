# Module 14: Dynamic Blocks Advanced

## 📚 What You'll Learn
- Understanding dynamic blocks
- Complex dynamic block patterns
- Nested dynamic blocks
- Real-world use cases
- Best practices

---

## 🎯 What are Dynamic Blocks?

**Dynamic blocks** allow you to dynamically construct repeatable nested blocks within resource configurations. They're perfect for situations where you need to generate multiple similar configuration blocks.

### Without Dynamic Blocks (Repetitive)

```hcl
resource "aws_security_group" "example" {
  name = "example-sg"
  
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
  
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
}
```

### With Dynamic Blocks (Clean)

```hcl
locals {
  ingress_rules = [
    {
      port        = 80
      cidr_blocks = ["0.0.0.0/0"]
      description = "HTTP"
    },
    {
      port        = 443
      cidr_blocks = ["0.0.0.0/0"]
      description = "HTTPS"
    },
    {
      port        = 22
      cidr_blocks = ["10.0.0.0/8"]
      description = "SSH"
    },
    {
      port        = 3306
      cidr_blocks = ["10.0.0.0/8"]
      description = "MySQL"
    }
  ]
}

resource "aws_security_group" "example" {
  name = "example-sg"
  
  dynamic "ingress" {
    for_each = local.ingress_rules
    content {
      description = ingress.value.description
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

---

## 📖 Dynamic Block Syntax

### Basic Structure

```hcl
dynamic "BLOCK_NAME" {
  for_each = COLLECTION
  
  content {
    # Block configuration using:
    # BLOCK_NAME.value.attribute
    # BLOCK_NAME.key
  }
}
```

### Iterator Customization

```hcl
dynamic "ingress" {
  for_each = var.ingress_rules
  iterator = rule  # Custom iterator name
  
  content {
    from_port   = rule.value.port
    to_port     = rule.value.port
    protocol    = rule.value.protocol
    cidr_blocks = rule.value.cidr_blocks
  }
}
```

---

## 🎪 Lab 1: Security Group with Dynamic Blocks

### Step 1: Create `variables.tf`

```hcl
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "allowed_ports" {
  description = "List of allowed ports"
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
      description = "HTTP from anywhere"
    },
    {
      port        = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = "HTTPS from anywhere"
    },
    {
      port        = 22
      protocol    = "tcp"
      cidr_blocks = ["10.0.0.0/8"]
      description = "SSH from VPC"
    }
  ]
}
```

### Step 2: Create `main.tf`

```hcl
provider "aws" {
  region = "us-east-1"
}

data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "dynamic_example" {
  name        = "${var.environment}-dynamic-sg"
  description = "Security group with dynamic blocks"
  vpc_id      = data.aws_vpc.default.id
  
  # Dynamic ingress rules
  dynamic "ingress" {
    for_each = var.allowed_ports
    
    content {
      description = ingress.value.description
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
  
  # Single egress rule (no dynamic needed)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }
  
  tags = {
    Name        = "${var.environment}-dynamic-sg"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
```

### Step 3: Create `outputs.tf`

```hcl
output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.dynamic_example.id
}

output "ingress_rules" {
  description = "Ingress rules created"
  value       = var.allowed_ports
}
```

### Step 4: Test

```bash
terraform init
terraform plan
terraform apply

# View the created rules
aws ec2 describe-security-groups \
  --group-ids $(terraform output -raw security_group_id) \
  --query 'SecurityGroups[0].IpPermissions'

terraform destroy
```

---

## 🎨 Advanced Patterns

### 1. Conditional Dynamic Blocks

```hcl
variable "enable_ssh" {
  type    = bool
  default = false
}

locals {
  ssh_rule = var.enable_ssh ? [{
    port        = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
    description = "SSH"
  }] : []
  
  base_rules = [
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
    }
  ]
  
  all_rules = concat(local.base_rules, local.ssh_rule)
}

resource "aws_security_group" "conditional" {
  name = "conditional-sg"
  
  dynamic "ingress" {
    for_each = local.all_rules
    
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

### 2. Nested Dynamic Blocks

```hcl
variable "aws_accounts" {
  type = map(object({
    regions = list(string)
    vpcs = list(object({
      cidr = string
      subnets = list(object({
        cidr = string
        az   = string
      }))
    }))
  }))
}

# Example using nested dynamics
resource "aws_vpc_peering_connection" "example" {
  for_each = var.aws_accounts
  
  vpc_id      = aws_vpc.main.id
  peer_vpc_id = each.value.peer_vpc_id
  
  dynamic "accepter" {
    for_each = each.value.regions
    
    content {
      allow_remote_vpc_dns_resolution = true
    }
  }
}
```

### 3. Dynamic Blocks with Maps

```hcl
locals {
  tags = {
    Environment = "production"
    Project     = "myapp"
    ManagedBy   = "Terraform"
    Owner       = "DevOps"
  }
}

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  # Convert map to list for dynamic block
  dynamic "tag" {
    for_each = local.tags
    
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }
}
```

### 4. Environment-Specific Dynamic Configuration

```hcl
variable "environment" {
  type = string
}

locals {
  environment_configs = {
    dev = {
      instance_types = ["t2.micro"]
      storage = [
        { size = 20, type = "gp2" }
      ]
    }
    staging = {
      instance_types = ["t2.small", "t2.medium"]
      storage = [
        { size = 50, type = "gp3" },
        { size = 100, type = "gp3" }
      ]
    }
    prod = {
      instance_types = ["t2.large", "t2.xlarge"]
      storage = [
        { size = 100, type = "gp3" },
        { size = 500, type = "io2" },
        { size = 1000, type = "io2" }
      ]
    }
  }
  
  config = local.environment_configs[var.environment]
}

resource "aws_instance" "app" {
  count         = length(local.config.instance_types)
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = local.config.instance_types[count.index]
  
  dynamic "ebs_block_device" {
    for_each = local.config.storage
    
    content {
      device_name = "/dev/sd${substr("fghijk", ebs_block_device.key, 1)}"
      volume_size = ebs_block_device.value.size
      volume_type = ebs_block_device.value.type
    }
  }
}
```

---

## 🎪 Lab 2: IAM Policy with Dynamic Statements

### Complete Example

```hcl
# variables.tf
variable "s3_buckets" {
  description = "S3 buckets to grant access to"
  type        = list(string)
  default     = ["bucket-1", "bucket-2", "bucket-3"]
}

variable "enable_dynamodb_access" {
  description = "Enable DynamoDB access"
  type        = bool
  default     = true
}

variable "dynamodb_tables" {
  description = "DynamoDB tables to grant access to"
  type        = list(string)
  default     = ["users", "sessions", "products"]
}

# main.tf
data "aws_iam_policy_document" "app" {
  # S3 bucket access - always included
  dynamic "statement" {
    for_each = var.s3_buckets
    
    content {
      sid    = "S3Access${statement.key}"
      effect = "Allow"
      
      actions = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ]
      
      resources = [
        "arn:aws:s3:::${statement.value}/*"
      ]
    }
  }
  
  # S3 list buckets
  statement {
    sid    = "S3ListBuckets"
    effect = "Allow"
    
    actions = [
      "s3:ListBucket"
    ]
    
    resources = [
      for bucket in var.s3_buckets :
      "arn:aws:s3:::${bucket}"
    ]
  }
  
  # DynamoDB access - conditional
  dynamic "statement" {
    for_each = var.enable_dynamodb_access ? var.dynamodb_tables : []
    
    content {
      sid    = "DynamoDBAccess${statement.key}"
      effect = "Allow"
      
      actions = [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ]
      
      resources = [
        "arn:aws:dynamodb:*:*:table/${statement.value}"
      ]
    }
  }
}

resource "aws_iam_policy" "app" {
  name        = "app-policy"
  description = "Policy for application"
  policy      = data.aws_iam_policy_document.app.json
}

# outputs.tf
output "policy_json" {
  description = "Generated IAM policy JSON"
  value       = data.aws_iam_policy_document.app.json
}

output "policy_arn" {
  description = "IAM policy ARN"
  value       = aws_iam_policy.app.arn
}
```

---

## 🎪 Lab 3: Load Balancer with Dynamic Listeners

```hcl
variable "listeners" {
  description = "Load balancer listeners"
  type = list(object({
    port              = number
    protocol          = string
    certificate_arn   = string
    ssl_policy        = string
  }))
  
  default = [
    {
      port            = 80
      protocol        = "HTTP"
      certificate_arn = ""
      ssl_policy      = ""
    },
    {
      port            = 443
      protocol        = "HTTPS"
      certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012"
      ssl_policy      = "ELBSecurityPolicy-TLS-1-2-2017-01"
    }
  ]
}

resource "aws_lb" "app" {
  name               = "app-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb.id]
  subnets            = data.aws_subnets.public.ids
}

resource "aws_lb_target_group" "app" {
  name     = "app-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.main.id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "app" {
  count             = length(var.listeners)
  load_balancer_arn = aws_lb.app.arn
  port              = var.listeners[count.index].port
  protocol          = var.listeners[count.index].protocol
  certificate_arn   = var.listeners[count.index].certificate_arn != "" ? var.listeners[count.index].certificate_arn : null
  ssl_policy        = var.listeners[count.index].ssl_policy != "" ? var.listeners[count.index].ssl_policy : null
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}
```

---

## 🔧 Real-World Use Cases

### 1. Multi-Region VPC Setup

```hcl
variable "regions" {
  type = map(object({
    cidr = string
    azs  = list(string)
    private_subnets = list(string)
    public_subnets  = list(string)
  }))
  
  default = {
    us-east-1 = {
      cidr            = "10.0.0.0/16"
      azs             = ["us-east-1a", "us-east-1b"]
      private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
      public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
    }
    us-west-2 = {
      cidr            = "10.1.0.0/16"
      azs             = ["us-west-2a", "us-west-2b"]
      private_subnets = ["10.1.1.0/24", "10.1.2.0/24"]
      public_subnets  = ["10.1.101.0/24", "10.1.102.0/24"]
    }
  }
}

resource "aws_vpc" "main" {
  for_each = var.regions
  
  cidr_block = each.value.cidr
  
  tags = {
    Name = "vpc-${each.key}"
  }
}

resource "aws_subnet" "private" {
  for_each = merge([
    for region_key, region in var.regions : {
      for idx, subnet in region.private_subnets :
      "${region_key}-private-${idx}" => {
        vpc_id     = aws_vpc.main[region_key].id
        cidr_block = subnet
        az         = region.azs[idx]
        region     = region_key
      }
    }
  ]...)
  
  vpc_id            = each.value.vpc_id
  cidr_block        = each.value.cidr_block
  availability_zone = each.value.az
  
  tags = {
    Name = "private-${each.key}"
  }
}
```

### 2. Dynamic CloudWatch Alarms

```hcl
variable "alarm_configs" {
  type = map(object({
    metric_name         = string
    comparison_operator = string
    threshold           = number
    evaluation_periods  = number
    period              = number
    statistic           = string
    actions_enabled     = bool
  }))
  
  default = {
    high_cpu = {
      metric_name         = "CPUUtilization"
      comparison_operator = "GreaterThanThreshold"
      threshold           = 80
      evaluation_periods  = 2
      period              = 300
      statistic           = "Average"
      actions_enabled     = true
    }
    low_memory = {
      metric_name         = "MemoryUtilization"
      comparison_operator = "LessThanThreshold"
      threshold           = 20
      evaluation_periods  = 2
      period              = 300
      statistic           = "Average"
      actions_enabled     = true
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "instance" {
  for_each = var.alarm_configs
  
  alarm_name          = "${var.instance_name}-${each.key}"
  comparison_operator = each.value.comparison_operator
  evaluation_periods  = each.value.evaluation_periods
  metric_name         = each.value.metric_name
  namespace           = "AWS/EC2"
  period              = each.value.period
  statistic           = each.value.statistic
  threshold           = each.value.threshold
  actions_enabled     = each.value.actions_enabled
  
  dimensions = {
    InstanceId = aws_instance.app.id
  }
  
  alarm_actions = each.value.actions_enabled ? [aws_sns_topic.alerts.arn] : []
}
```

---

## 💡 Best Practices

### 1. Use Dynamic Blocks for Repetitive Patterns

```hcl
# ✅ Good - Dynamic block for multiple similar rules
dynamic "ingress" {
  for_each = var.ingress_rules
  content {
    ...
  }
}

# ❌ Bad - Repeating the same block
ingress { ... }
ingress { ... }
ingress { ... }
```

### 2. Keep Data Structures Clean

```hcl
# ✅ Good - Structured data
variable "rules" {
  type = list(object({
    port        = number
    protocol    = string
    cidr_blocks = list(string)
  }))
}

# ❌ Bad - Unstructured
variable "ports" { type = list(number) }
variable "protocols" { type = list(string) }
```

### 3. Use Custom Iterators for Clarity

```hcl
# ✅ Good - Clear iterator name
dynamic "ingress" {
  for_each = var.security_rules
  iterator = rule
  
  content {
    from_port = rule.value.port
  }
}

# ❌ Less clear - default iterator
dynamic "ingress" {
  for_each = var.security_rules
  
  content {
    from_port = ingress.value.port
  }
}
```

### 4. Don't Overuse Dynamic Blocks

```hcl
# ❌ Bad - Dynamic block for single item
dynamic "ingress" {
  for_each = [{ port = 80 }]
  content {
    from_port = ingress.value.port
  }
}

# ✅ Good - Simple block
ingress {
  from_port = 80
}
```

---

## 📝 Quiz

1. What problem do dynamic blocks solve?
2. What is the syntax for a dynamic block?
3. How do you access values within a dynamic block?
4. Can you have nested dynamic blocks?
5. When should you NOT use dynamic blocks?

---

## 🎓 Challenge Exercise

Create a complete application infrastructure with:
1. Security group with dynamic ingress/egress rules
2. IAM policy with dynamic statements for multiple services
3. Load balancer with dynamic listeners
4. CloudWatch alarms with dynamic metrics
5. All driven by variables

---

## ⏭️ Next Steps

Continue to [Module 15: Import Existing Resources](./15-import-existing-resources.md)

---

**🎉 Congratulations!** You now master dynamic blocks and can create flexible, DRY Terraform configurations!
