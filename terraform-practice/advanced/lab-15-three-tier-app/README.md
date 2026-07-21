# Lab 15: Complete 3-Tier Web Application

**Difficulty**: Advanced  
**Time**: 90 minutes  
**Cost**: ~$0.50/hour

## 🎯 Objectives

- Build a complete production-like 3-tier architecture
- Integrate all concepts from previous labs
- Use modules for reusability
- Implement remote state and state locking
- Apply security best practices
- Set up monitoring and logging

## 📋 Prerequisites

- Completed all previous labs
- Strong understanding of AWS services
- Understanding of application architecture
- Time and patience!

## 🏗️ Architecture

```
                        Internet
                           │
                           ▼
                   [Internet Gateway]
                           │
               ┌───────────┴───────────┐
               │  Application Load     │
               │  Balancer (Public)    │
               └───────────┬───────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │         Web Tier (Public)         │
         │  ┌──────────┐     ┌──────────┐   │
         │  │  EC2 ASG │     │  EC2 ASG │   │
         │  │ us-east-1a│    │us-east-1b│   │
         │  └────┬─────┘     └─────┬────┘   │
         └───────┼─────────────────┼─────────┘
                 │                 │
         ┌───────┴─────────────────┴─────────┐
         │    Application Tier (Private)     │
         │  ┌──────────┐     ┌──────────┐   │
         │  │  EC2 ASG │     │  EC2 ASG │   │
         │  │ us-east-1a│    │us-east-1b│   │
         │  └────┬─────┘     └─────┬────┘   │
         └───────┼─────────────────┼─────────┘
                 │                 │
         ┌───────┴─────────────────┴─────────┐
         │     Database Tier (Private)       │
         │  ┌──────────┐     ┌──────────┐   │
         │  │ RDS Multi-AZ  │ ElastiCache│   │
         │  │  MySQL        │  Redis     │   │
         │  └───────────┘     └──────────┘   │
         └───────────────────────────────────┘
```

## 🔨 Tasks

### Project Structure

```
terraform-practice/advanced/lab-15-three-tier-app/
├── backend.tf                 # S3 backend configuration
├── main.tf                    # Main configuration
├── variables.tf               # Input variables
├── outputs.tf                 # Outputs
├── terraform.tfvars           # Variable values
├── modules/
│   ├── networking/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── web-tier/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── app-tier/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── database-tier/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── scripts/
    ├── web-tier-userdata.sh
    └── app-tier-userdata.sh
```

### Task 1: Set Up Backend

**backend.tf**:

```hcl
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "terraform-state-yourname-2026"
    key            = "three-tier-app/terraform.tfstate"
    region         = "us-east-1"
    profile        = "terraform_practice"
    dynamodb_table = "terraform-state-locks"
    encrypt        = true
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
  
  default_tags {
    tags = {
      Project     = "ThreeTierApp"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
```

### Task 2: Define Variables

**variables.tf**:

```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile"
  type        = string
  default     = "terraform_practice"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "three-tier-app"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "web_instance_type" {
  description = "Web tier instance type"
  type        = string
  default     = "t3.micro"
}

variable "app_instance_type" {
  description = "App tier instance type"
  type        = string
  default     = "t3.small"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "appdb"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}
```

**terraform.tfvars**:

```hcl
aws_region         = "us-east-1"
aws_profile        = "terraform_practice"
environment        = "production"
project_name       = "three-tier-app"
vpc_cidr           = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]

web_instance_type = "t3.micro"
app_instance_type = "t3.small"
db_instance_class = "db.t3.micro"

db_name     = "appdb"
db_username = "admin"
db_password = "YourSecurePassword123!"  # Change this!
```

### Task 3: Create Networking Module

**modules/networking/main.tf**:

```hcl
# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Public Subnets (Web Tier)
resource "aws_subnet" "public" {
  count                   = length(var.availability_zones)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "${var.project_name}-public-${var.availability_zones[count.index]}"
    Tier = "Web"
  }
}

# Private Subnets - App Tier
resource "aws_subnet" "private_app" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = var.availability_zones[count.index]
  
  tags = {
    Name = "${var.project_name}-private-app-${var.availability_zones[count.index]}"
    Tier = "Application"
  }
}

# Private Subnets - Database Tier
resource "aws_subnet" "private_db" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 20)
  availability_zone = var.availability_zones[count.index]
  
  tags = {
    Name = "${var.project_name}-private-db-${var.availability_zones[count.index]}"
    Tier = "Database"
  }
}

# NAT Gateway
resource "aws_eip" "nat" {
  count  = length(var.availability_zones)
  domain = "vpc"
  
  tags = {
    Name = "${var.project_name}-nat-eip-${count.index + 1}"
  }
}

resource "aws_nat_gateway" "main" {
  count         = length(var.availability_zones)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = {
    Name = "${var.project_name}-nat-${count.index + 1}"
  }
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route_table" "private" {
  count  = length(var.availability_zones)
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }
  
  tags = {
    Name = "${var.project_name}-private-rt-${count.index + 1}"
  }
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count          = length(var.availability_zones)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_app" {
  count          = length(var.availability_zones)
  subnet_id      = aws_subnet.private_app[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

resource "aws_route_table_association" "private_db" {
  count          = length(var.availability_zones)
  subnet_id      = aws_subnet.private_db[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}
```

**modules/networking/variables.tf**:

```hcl
variable "project_name" {
  description = "Project name"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
}
```

**modules/networking/outputs.tf**:

```hcl
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  description = "Private application subnet IDs"
  value       = aws_subnet.private_app[*].id
}

output "private_db_subnet_ids" {
  description = "Private database subnet IDs"
  value       = aws_subnet.private_db[*].id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}
```

### Task 4: Create Web Tier Module

**modules/web-tier/main.tf**:

```hcl
# Security Group for ALB
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = var.vpc_id
  
  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "${var.project_name}-alb-sg"
  }
}

# Security Group for Web Tier EC2
resource "aws_security_group" "web" {
  name        = "${var.project_name}-web-sg"
  description = "Security group for web tier"
  vpc_id      = var.vpc_id
  
  ingress {
    description     = "HTTP from ALB"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "${var.project_name}-web-sg"
  }
}

# ALB
resource "aws_lb" "web" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.public_subnet_ids
  
  enable_deletion_protection = false
  
  tags = {
    Name = "${var.project_name}-alb"
  }
}

# Target Group
resource "aws_lb_target_group" "web" {
  name     = "${var.project_name}-web-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"
    matcher             = "200"
  }
  
  tags = {
    Name = "${var.project_name}-web-tg"
  }
}

# Listener
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.web.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}

# Get latest AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# Launch Template
resource "aws_launch_template" "web" {
  name_prefix   = "${var.project_name}-web-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  
  vpc_security_group_ids = [aws_security_group.web.id]
  
  user_data = base64encode(templatefile("${path.module}/../../scripts/web-tier-userdata.sh", {
    app_backend_url = var.app_backend_url
  }))
  
  monitoring {
    enabled = true
  }
  
  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.project_name}-web-instance"
      Tier = "Web"
    }
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "web" {
  name                = "${var.project_name}-web-asg"
  min_size            = 2
  max_size            = 4
  desired_capacity    = 2
  vpc_zone_identifier = var.public_subnet_ids
  target_group_arns   = [aws_lb_target_group.web.arn]
  health_check_type   = "ELB"
  health_check_grace_period = 300
  
  launch_template {
    id      = aws_launch_template.web.id
    version = "$Latest"
  }
  
  tag {
    key                 = "Name"
    value               = "${var.project_name}-web-asg-instance"
    propagate_at_launch = true
  }
}

# Scaling Policies
resource "aws_autoscaling_policy" "scale_up" {
  name                   = "${var.project_name}-web-scale-up"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.web.name
}

resource "aws_autoscaling_policy" "scale_down" {
  name                   = "${var.project_name}-web-scale-down"
  scaling_adjustment     = -1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.web.name
}
```

**Create similar modules for app-tier and database-tier...**

### Task 5: Create Main Configuration

**main.tf**:

```hcl
# Networking Module
module "networking" {
  source = "./modules/networking"
  
  project_name       = var.project_name
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}

# Database Tier Module (create first - no dependencies)
module "database" {
  source = "./modules/database-tier"
  
  project_name           = var.project_name
  vpc_id                 = module.networking.vpc_id
  private_subnet_ids     = module.networking.private_db_subnet_ids
  db_instance_class      = var.db_instance_class
  db_name                = var.db_name
  db_username            = var.db_username
  db_password            = var.db_password
  allowed_security_group = module.app_tier.security_group_id
}

# Application Tier Module
module "app_tier" {
  source = "./modules/app-tier"
  
  project_name       = var.project_name
  vpc_id             = module.networking.vpc_id
  private_subnet_ids = module.networking.private_app_subnet_ids
  instance_type      = var.app_instance_type
  db_endpoint        = module.database.db_endpoint
  db_name            = var.db_name
  web_security_group = module.web_tier.security_group_id
}

# Web Tier Module
module "web_tier" {
  source = "./modules/web-tier"
  
  project_name       = var.project_name
  vpc_id             = module.networking.vpc_id
  public_subnet_ids  = module.networking.public_subnet_ids
  instance_type      = var.web_instance_type
  app_backend_url    = module.app_tier.internal_lb_dns
}
```

### Task 6: Create User Data Scripts

**scripts/web-tier-userdata.sh**:

```bash
#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd

cat > /var/www/html/index.html <<EOF
<!DOCTYPE html>
<html>
<head>
    <title>Three-Tier Application</title>
    <style>
        body { font-family: Arial; text-align: center; margin-top: 50px; background: #f0f0f0; }
        h1 { color: #FF9900; }
        .info { background: white; padding: 30px; margin: 20px auto; width: 600px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <h1>🚀 Three-Tier Web Application</h1>
    <div class="info">
        <h2>Web Tier</h2>
        <p><strong>Instance ID:</strong> $(ec2-metadata --instance-id | cut -d " " -f 2)</p>
        <p><strong>AZ:</strong> $(ec2-metadata --availability-zone | cut -d " " -f 2)</p>
        <p><strong>Backend URL:</strong> ${app_backend_url}</p>
    </div>
</body>
</html>
EOF
```

### Task 7: Create Outputs

**outputs.tf**:

```hcl
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = module.web_tier.alb_dns_name
}

output "application_url" {
  description = "URL to access the application"
  value       = "http://${module.web_tier.alb_dns_name}"
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

output "db_endpoint" {
  description = "RDS endpoint"
  value       = module.database.db_endpoint
  sensitive   = true
}
```

## ✅ Validation Steps

1. **Initialize and apply**:
   ```bash
   terraform init
   terraform fmt -recursive
   terraform validate
   terraform plan
   terraform apply
   ```

2. **Access the application**:
   ```bash
   terraform output application_url
   # Open in browser
   ```

3. **Verify all tiers**:
   - Web tier: Check ALB and instances
   - App tier: Verify instances in private subnets
   - DB tier: Check RDS Multi-AZ

4. **Test auto scaling**:
   - Generate load on instances
   - Watch ASG scale up/down

5. **Test high availability**:
   - Terminate an instance
   - Verify new instance launches
   - No downtime

## 🧹 Cleanup

```bash
terraform destroy
# Confirm: yes
```

**Takes 10-15 minutes to destroy all resources.**

## 📚 What You Built

- ✅ Complete 3-tier architecture
- ✅ Multi-AZ deployment
- ✅ Auto scaling for web and app tiers
- ✅ RDS Multi-AZ database
- ✅ Private subnets for security
- ✅ NAT Gateways for private subnet internet access
- ✅ Application Load Balancer
- ✅ Security groups with least privilege
- ✅ Modular, reusable code
- ✅ Remote state management
- ✅ Production-ready infrastructure

## 🎓 Challenge

1. **Add HTTPS**: ACM certificate + HTTPS listener
2. **Add ElastiCache**: Redis cluster in DB tier
3. **Add Monitoring**: CloudWatch dashboards + alarms
4. **Add Bastion Host**: SSH access to private instances
5. **Add WAF**: Protect ALB from attacks
6. **Add Backup**: Automated RDS snapshots
7. **Add CI/CD**: GitHub Actions to deploy
8. **Multi-Region**: Deploy to second region

## 💰 Total Cost Estimate

- NAT Gateways: ~$0.09/hour
- ALB: ~$0.0225/hour
- EC2 instances (4): ~$0.04/hour
- RDS Multi-AZ: ~$0.034/hour
- **Total**: ~$0.50/hour (~$360/month)

**Always destroy after practice!**

## 🎉 Congratulations!

You've completed all 15 Terraform practice labs! You now have the skills to build production-grade infrastructure with Terraform.

## 📖 Reference

- All previous lab concepts combined
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)

## ✨ Solution

Solution files are in the `solution/` directory. Try completing the lab yourself first!

