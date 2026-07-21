# Lab 13: Dynamic Blocks and For Expressions

**Difficulty**: Advanced  
**Time**: 35 minutes  
**Cost**: ~$0.02/hour

## 🎯 Objectives

- Master dynamic blocks for repetitive configuration
- Use for expressions to transform data
- Implement conditional resource creation
- Work with complex variable structures (lists, maps, objects)
- Create reusable, flexible configurations

## 📋 Prerequisites

- Completed intermediate labs
- Understanding of lists, maps, and objects
- Knowledge of conditionals in Terraform

## 🔨 Tasks

### Task 1: Dynamic Security Group Rules

**variables.tf**:

```hcl
variable "ingress_rules" {
  description = "List of ingress rules"
  type = list(object({
    description = string
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
  }))
  default = [
    {
      description = "HTTP"
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    },
    {
      description = "HTTPS"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    },
    {
      description = "SSH"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = ["10.0.0.0/8"]
    }
  ]
}

variable "egress_rules" {
  description = "List of egress rules"
  type = list(object({
    description = string
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
  }))
  default = [
    {
      description = "Allow all outbound"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }
  ]
}
```

**main.tf**:

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

# Get default VPC
data "aws_vpc" "default" {
  default = true
}

# Security group with dynamic rules
resource "aws_security_group" "dynamic" {
  name        = "dynamic-sg"
  description = "Security group with dynamic rules"
  vpc_id      = data.aws_vpc.default.id
  
  # Dynamic ingress rules
  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      description = ingress.value.description
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
  
  # Dynamic egress rules
  dynamic "egress" {
    for_each = var.egress_rules
    content {
      description = egress.value.description
      from_port   = egress.value.from_port
      to_port     = egress.value.to_port
      protocol    = egress.value.protocol
      cidr_blocks = egress.value.cidr_blocks
    }
  }
  
  tags = {
    Name = "Dynamic Security Group"
  }
}
```

### Task 2: For Expressions - Transform Data

**for-expressions.tf**:

```hcl
# Map of environments to instance types
variable "environments" {
  description = "Environment configurations"
  type = map(object({
    instance_type = string
    count         = number
  }))
  default = {
    dev = {
      instance_type = "t3.micro"
      count         = 1
    }
    staging = {
      instance_type = "t3.small"
      count         = 2
    }
    prod = {
      instance_type = "t3.medium"
      count         = 3
    }
  }
}

# For expression - Extract instance types
locals {
  # Create list of all instance types
  all_instance_types = [for env, config in var.environments : config.instance_type]
  
  # Create list of environment names
  environment_names = [for env, config in var.environments : env]
  
  # Create map of environment to total instances
  instance_counts = {
    for env, config in var.environments :
    env => config.count
  }
  
  # Conditional filtering - only prod-like environments
  prod_environments = {
    for env, config in var.environments :
    env => config
    if config.count > 1
  }
  
  # Complex transformation
  environment_tags = {
    for env, config in var.environments :
    env => {
      Environment  = env
      InstanceType = config.instance_type
      Count        = config.count
      IsProd       = config.count > 2 ? "true" : "false"
    }
  }
}

# Output the transformations
output "all_instance_types" {
  value = local.all_instance_types
}

output "prod_environments" {
  value = local.prod_environments
}

output "environment_tags" {
  value = local.environment_tags
}
```

### Task 3: Dynamic Subnet Creation

**dynamic-subnets.tf**:

```hcl
variable "subnet_config" {
  description = "Configuration for subnets"
  type = map(object({
    cidr_block        = string
    availability_zone = string
    public            = bool
  }))
  default = {
    public-1 = {
      cidr_block        = "10.0.1.0/24"
      availability_zone = "us-east-1a"
      public            = true
    }
    public-2 = {
      cidr_block        = "10.0.2.0/24"
      availability_zone = "us-east-1b"
      public            = true
    }
    private-1 = {
      cidr_block        = "10.0.11.0/24"
      availability_zone = "us-east-1a"
      public            = false
    }
    private-2 = {
      cidr_block        = "10.0.12.0/24"
      availability_zone = "us-east-1b"
      public            = false
    }
  }
}

# Create VPC
resource "aws_vpc" "dynamic" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "Dynamic VPC"
  }
}

# Dynamically create subnets
resource "aws_subnet" "dynamic" {
  for_each = var.subnet_config
  
  vpc_id                  = aws_vpc.dynamic.id
  cidr_block              = each.value.cidr_block
  availability_zone       = each.value.availability_zone
  map_public_ip_on_launch = each.value.public
  
  tags = {
    Name = each.key
    Type = each.value.public ? "Public" : "Private"
  }
}

# Use for expression to filter public subnets
locals {
  public_subnet_ids = [
    for name, subnet in aws_subnet.dynamic :
    subnet.id
    if var.subnet_config[name].public
  ]
  
  private_subnet_ids = [
    for name, subnet in aws_subnet.dynamic :
    subnet.id
    if !var.subnet_config[name].public
  ]
}

output "public_subnets" {
  value = local.public_subnet_ids
}

output "private_subnets" {
  value = local.private_subnet_ids
}
```

### Task 4: Conditional Resource Creation

**conditional-resources.tf**:

```hcl
variable "create_nat_gateway" {
  description = "Whether to create NAT Gateway"
  type        = bool
  default     = false
}

variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring"
  type        = bool
  default     = false
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

# Create NAT Gateway only if enabled
resource "aws_eip" "nat" {
  count  = var.create_nat_gateway ? 1 : 0
  domain = "vpc"
  
  tags = {
    Name = "NAT Gateway EIP"
  }
}

resource "aws_nat_gateway" "main" {
  count = var.create_nat_gateway ? 1 : 0
  
  allocation_id = aws_eip.nat[0].id
  subnet_id     = local.public_subnet_ids[0]
  
  tags = {
    Name = "Main NAT Gateway"
  }
}

# Create monitoring resources only in production
resource "aws_cloudwatch_log_group" "app" {
  count = var.environment == "prod" ? 1 : 0
  
  name              = "/aws/app/logs"
  retention_in_days = 30
  
  tags = {
    Environment = var.environment
  }
}

# Create SNS topic for alerts (prod only)
resource "aws_sns_topic" "alerts" {
  count = var.environment == "prod" ? 1 : 0
  
  name = "app-alerts"
  
  tags = {
    Environment = var.environment
  }
}
```

### Task 5: Dynamic Nested Blocks

**nested-blocks.tf**:

```hcl
variable "alarms" {
  description = "CloudWatch alarms configuration"
  type = list(object({
    name                = string
    metric_name         = string
    threshold           = number
    comparison_operator = string
    dimensions          = map(string)
  }))
  default = [
    {
      name                = "high-cpu"
      metric_name         = "CPUUtilization"
      threshold           = 80
      comparison_operator = "GreaterThanThreshold"
      dimensions = {
        InstanceId = "i-1234567890abcdef0"
      }
    },
    {
      name                = "low-memory"
      metric_name         = "MemoryUtilization"
      threshold           = 20
      comparison_operator = "LessThanThreshold"
      dimensions = {
        InstanceId = "i-1234567890abcdef0"
      }
    }
  ]
}

# Dynamic CloudWatch alarms
resource "aws_cloudwatch_metric_alarm" "dynamic" {
  for_each = {
    for alarm in var.alarms :
    alarm.name => alarm
  }
  
  alarm_name          = each.value.name
  comparison_operator = each.value.comparison_operator
  evaluation_periods  = 2
  metric_name         = each.value.metric_name
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = each.value.threshold
  
  # Dynamic dimensions block
  dimensions = each.value.dimensions
}
```

### Task 6: Advanced For Expressions

**advanced-for.tf**:

```hcl
variable "instances" {
  description = "Instance configurations"
  type = list(object({
    name          = string
    instance_type = string
    environment   = string
    backup        = bool
  }))
  default = [
    { name = "web-1", instance_type = "t3.micro", environment = "dev", backup = false },
    { name = "web-2", instance_type = "t3.small", environment = "staging", backup = true },
    { name = "app-1", instance_type = "t3.medium", environment = "prod", backup = true },
    { name = "db-1", instance_type = "t3.large", environment = "prod", backup = true },
  ]
}

locals {
  # Group instances by environment
  instances_by_env = {
    for env in distinct([for i in var.instances : i.environment]) :
    env => [
      for i in var.instances :
      i if i.environment == env
    ]
  }
  
  # Get instances that need backup
  backup_instances = [
    for i in var.instances :
    i if i.backup
  ]
  
  # Create tags for all instances
  instance_tags = {
    for i in var.instances :
    i.name => {
      Name        = i.name
      Environment = i.environment
      Backup      = i.backup ? "enabled" : "disabled"
      InstanceType = i.instance_type
    }
  }
  
  # Count instances per environment
  instance_counts_per_env = {
    for env in distinct([for i in var.instances : i.environment]) :
    env => length([for i in var.instances : i if i.environment == env])
  }
}

output "instances_by_environment" {
  value = local.instances_by_env
}

output "backup_instances" {
  value = local.backup_instances
}

output "instance_counts" {
  value = local.instance_counts_per_env
}
```

## ✅ Validation Steps

1. **Apply configuration**:
   ```bash
   terraform init
   terraform fmt
   terraform validate
   terraform plan
   terraform apply
   ```

2. **Check dynamic security group**:
   ```bash
   aws ec2 describe-security-groups \
     --group-names dynamic-sg \
     --query 'SecurityGroups[0].IpPermissions' \
     --profile terraform_practice
   ```

3. **Verify outputs**:
   ```bash
   terraform output all_instance_types
   terraform output prod_environments
   terraform output public_subnets
   terraform output instances_by_environment
   ```

4. **Test conditional creation**:
   ```bash
   # Without NAT Gateway
   terraform apply -var="create_nat_gateway=false"
   
   # With NAT Gateway
   terraform apply -var="create_nat_gateway=true"
   
   # Production environment
   terraform apply -var="environment=prod"
   ```

## 🧹 Cleanup

```bash
terraform destroy
```

## 📚 Key Concepts Learned

- Dynamic blocks for repetitive nested blocks
- For expressions to transform data structures
- Conditional resource creation with count/for_each
- Complex variable structures (lists, maps, objects)
- Filtering and grouping with for expressions
- When to use dynamic vs multiple resources

## 🎓 Challenge

1. **Create Dynamic RDS Parameter Group**:
   ```hcl
   variable "db_parameters" {
     type = list(object({
       name  = string
       value = string
     }))
   }
   
   resource "aws_db_parameter_group" "dynamic" {
     dynamic "parameter" {
       for_each = var.db_parameters
       content {
         name  = parameter.value.name
         value = parameter.value.value
       }
     }
   }
   ```

2. **Dynamic IAM Policy**:
   - Multiple statements
   - Dynamic actions and resources
   - Conditional policies based on environment

3. **Dynamic Tags**:
   ```hcl
   locals {
     common_tags = merge(
       var.tags,
       {
         for k, v in var.additional_tags :
         k => v
         if v != ""
       }
     )
   }
   ```

4. **Complex Filtering**:
   - Filter instances by multiple criteria
   - Group by multiple attributes
   - Nested transformations

## 💡 Tips

- Use dynamic blocks for nested configuration blocks only
- Prefer for_each over count for resources
- Use for expressions in locals for complex transformations
- Keep dynamic blocks simple - complex logic goes in locals
- Use meaningful variable names in for expressions
- Comment complex transformations
- Test with different input combinations

## 🆚 When to Use What

| Feature | Use For | Don't Use For |
|---------|---------|---------------|
| dynamic blocks | Nested blocks (rules, tags) | Top-level resources |
| for_each | Multiple similar resources | Simple lists |
| count | Simple resource repetition | Complex scenarios |
| for expressions | Data transformation | Creating resources |
| conditionals | Optional resources | Complex logic |

## 📖 Reference

- [Dynamic Blocks](https://developer.hashicorp.com/terraform/language/expressions/dynamic-blocks)
- [For Expressions](https://developer.hashicorp.com/terraform/language/expressions/for)
- [Conditional Expressions](https://developer.hashicorp.com/terraform/language/expressions/conditionals)
- [Complex Types](https://developer.hashicorp.com/terraform/language/expressions/types)

## ✨ Solution

Solution files are in the `solution/` directory. Try completing the lab yourself first!

