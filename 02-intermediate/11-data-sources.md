# Module 11: Data Sources

## 📚 What You'll Learn
- Understanding Data Sources
- Querying existing infrastructure
- Using data sources with resources
- Common data source patterns
- Best practices for data sources

---

## 🎯 What is a Data Source?

A **data source** allows Terraform to fetch or compute data from external sources. Unlike resources (which create/manage infrastructure), data sources only **read** existing information.

### Key Differences

| Resources | Data Sources |
|-----------|--------------|
| Create infrastructure | Read existing data |
| Modify infrastructure | Read-only |
| `resource` block | `data` block |
| Managed by Terraform | Managed elsewhere |

---

## 📖 Data Source Syntax

### Basic Syntax

```hcl
data "provider_type" "name" {
  # Filter criteria
}

# Reference the data
resource "some_resource" "example" {
  attribute = data.provider_type.name.attribute
}
```

### Example: Query Existing VPC

```hcl
# Data source to find existing VPC
data "aws_vpc" "existing" {
  default = true
}

# Use the VPC data in a resource
resource "aws_subnet" "my_subnet" {
  vpc_id     = data.aws_vpc.existing.id
  cidr_block = "10.0.1.0/24"
}

# Output VPC information
output "vpc_id" {
  value = data.aws_vpc.existing.id
}

output "vpc_cidr" {
  value = data.aws_vpc.existing.cidr_block
}
```

---

## 🔍 Common AWS Data Sources

### 1. AWS AMI (Amazon Machine Image)

```hcl
# Find latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Use the AMI in an EC2 instance
resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = "t2.micro"
  
  tags = {
    Name = "WebServer"
  }
}

output "ami_id" {
  value = data.aws_ami.amazon_linux_2.id
}

output "ami_name" {
  value = data.aws_ami.amazon_linux_2.name
}
```

### 2. AWS Availability Zones

```hcl
# Get all available AZs in the current region
data "aws_availability_zones" "available" {
  state = "available"
}

# Create subnets in each AZ
resource "aws_subnet" "public" {
  count             = length(data.aws_availability_zones.available.names)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "public-subnet-${count.index + 1}"
  }
}

output "availability_zones" {
  value = data.aws_availability_zones.available.names
}
```

### 3. AWS Account Information

```hcl
# Get current AWS account details
data "aws_caller_identity" "current" {}

# Get current AWS region
data "aws_region" "current" {}

# Use in resources
resource "aws_s3_bucket" "example" {
  bucket = "mybucket-${data.aws_caller_identity.current.account_id}"
}

output "account_info" {
  value = {
    account_id = data.aws_caller_identity.current.account_id
    caller_arn = data.aws_caller_identity.current.arn
    user_id    = data.aws_caller_identity.current.user_id
    region     = data.aws_region.current.name
  }
}
```

### 4. AWS VPC and Subnets

```hcl
# Find VPC by tag
data "aws_vpc" "selected" {
  tags = {
    Environment = "production"
  }
}

# Find subnets in the VPC
data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }
  
  tags = {
    Tier = "Private"
  }
}

# Get details of each subnet
data "aws_subnet" "private" {
  for_each = toset(data.aws_subnets.private.ids)
  id       = each.value
}

output "private_subnet_cidrs" {
  value = [for s in data.aws_subnet.private : s.cidr_block]
}
```

### 5. AWS Security Groups

```hcl
# Find security group by name
data "aws_security_group" "default" {
  name   = "default"
  vpc_id = data.aws_vpc.selected.id
}

# Use in EC2 instance
resource "aws_instance" "app" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = "t2.micro"
  vpc_security_group_ids = [data.aws_security_group.default.id]
}
```

### 6. AWS Route53 Zone

```hcl
# Find hosted zone
data "aws_route53_zone" "main" {
  name         = "example.com"
  private_zone = false
}

# Create DNS record
resource "aws_route53_record" "www" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "www.example.com"
  type    = "A"
  ttl     = 300
  records = [aws_instance.web.public_ip]
}
```

### 7. AWS IAM Policy Document

```hcl
# Define policy using data source
data "aws_iam_policy_document" "s3_read_only" {
  statement {
    sid    = "AllowS3ReadOnly"
    effect = "Allow"
    
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    
    resources = [
      "arn:aws:s3:::my-bucket",
      "arn:aws:s3:::my-bucket/*"
    ]
  }
}

# Create IAM policy from document
resource "aws_iam_policy" "s3_read_only" {
  name        = "S3ReadOnlyPolicy"
  description = "Allows read-only access to S3 bucket"
  policy      = data.aws_iam_policy_document.s3_read_only.json
}
```

---

## 🎪 Lab: Using Data Sources

### Objective
Create infrastructure using existing AWS resources via data sources.

### Step 1: Create `data.tf`

```hcl
# Get current AWS account and region
data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# Get available AZs
data "aws_availability_zones" "available" {
  state = "available"
}

# Find latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Find default VPC
data "aws_vpc" "default" {
  default = true
}

# Find default subnets
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}
```

### Step 2: Create `main.tf`

```hcl
# Create security group in default VPC
resource "aws_security_group" "web" {
  name        = "web-server-sg"
  description = "Security group for web server"
  vpc_id      = data.aws_vpc.default.id
  
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
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
    Name = "web-server-sg"
  }
}

# Create EC2 instance using data sources
resource "aws_instance" "web" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = "t2.micro"
  vpc_security_group_ids = [aws_security_group.web.id]
  subnet_id              = tolist(data.aws_subnets.default.ids)[0]
  
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y httpd
              systemctl start httpd
              systemctl enable httpd
              echo "<h1>Hello from Terraform!</h1>" > /var/www/html/index.html
              EOF
  
  tags = {
    Name        = "web-server"
    ManagedBy   = "Terraform"
    AccountID   = data.aws_caller_identity.current.account_id
    Region      = data.aws_region.current.name
  }
}
```

### Step 3: Create `outputs.tf`

```hcl
output "account_id" {
  description = "AWS Account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "region" {
  description = "AWS Region"
  value       = data.aws_region.current.name
}

output "availability_zones" {
  description = "Available AZs"
  value       = data.aws_availability_zones.available.names
}

output "ami_id" {
  description = "AMI ID used"
  value       = data.aws_ami.amazon_linux_2.id
}

output "ami_name" {
  description = "AMI name"
  value       = data.aws_ami.amazon_linux_2.name
}

output "default_vpc_id" {
  description = "Default VPC ID"
  value       = data.aws_vpc.default.id
}

output "default_vpc_cidr" {
  description = "Default VPC CIDR"
  value       = data.aws_vpc.default.cidr_block
}

output "instance_public_ip" {
  description = "Public IP of EC2 instance"
  value       = aws_instance.web.public_ip
}

output "instance_url" {
  description = "URL to access the web server"
  value       = "http://${aws_instance.web.public_ip}"
}
```

### Step 4: Run Terraform

```bash
# Initialize
terraform init

# View what data sources will query
terraform plan

# Apply
terraform apply

# View outputs
terraform output

# Test the web server
curl $(terraform output -raw instance_url)

# Cleanup
terraform destroy
```

---

## 🎨 Advanced Data Source Patterns

### 1. Conditional Data Sources

```hcl
variable "use_existing_vpc" {
  type    = bool
  default = true
}

variable "vpc_id" {
  type    = string
  default = ""
}

# Only query if using existing VPC
data "aws_vpc" "existing" {
  count = var.use_existing_vpc ? 1 : 0
  id    = var.vpc_id
}

# Use conditional logic
resource "aws_subnet" "example" {
  vpc_id     = var.use_existing_vpc ? data.aws_vpc.existing[0].id : aws_vpc.new[0].id
  cidr_block = "10.0.1.0/24"
}
```

### 2. Data Source with For_Each

```hcl
variable "subnet_ids" {
  type    = set(string)
  default = ["subnet-12345", "subnet-67890"]
}

data "aws_subnet" "selected" {
  for_each = var.subnet_ids
  id       = each.value
}

output "subnet_cidrs" {
  value = { for k, v in data.aws_subnet.selected : k => v.cidr_block }
}
```

### 3. Chaining Data Sources

```hcl
# Get VPC
data "aws_vpc" "main" {
  tags = {
    Name = "main-vpc"
  }
}

# Get subnets in that VPC
data "aws_subnets" "app" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
  
  tags = {
    Tier = "app"
  }
}

# Get details of each subnet
data "aws_subnet" "app_details" {
  for_each = toset(data.aws_subnets.app.ids)
  id       = each.value
}

# Use in load balancer
resource "aws_lb" "app" {
  name            = "app-lb"
  internal        = true
  subnets         = data.aws_subnets.app.ids
  security_groups = [aws_security_group.lb.id]
}
```

### 4. Remote State Data Source

```hcl
# Read from another Terraform state
data "terraform_remote_state" "network" {
  backend = "s3"
  
  config = {
    bucket = "my-terraform-state"
    key    = "network/terraform.tfstate"
    region = "us-east-1"
  }
}

# Use outputs from remote state
resource "aws_instance" "app" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = "t2.micro"
  subnet_id     = data.terraform_remote_state.network.outputs.private_subnet_id
}
```

### 5. Template File Data Source

```hcl
data "template_file" "user_data" {
  template = file("${path.module}/user_data.sh")
  
  vars = {
    server_port = var.server_port
    db_address  = aws_db_instance.example.address
    db_name     = var.db_name
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = "t2.micro"
  user_data     = data.template_file.user_data.rendered
}
```

---

## 🌐 Multi-Cloud Data Sources

### Azure Data Sources

```hcl
# Get existing resource group
data "azurerm_resource_group" "existing" {
  name = "my-resource-group"
}

# Get existing virtual network
data "azurerm_virtual_network" "existing" {
  name                = "my-vnet"
  resource_group_name = data.azurerm_resource_group.existing.name
}

# Use in new resource
resource "azurerm_subnet" "new" {
  name                 = "new-subnet"
  resource_group_name  = data.azurerm_resource_group.existing.name
  virtual_network_name = data.azurerm_virtual_network.existing.name
  address_prefixes     = ["10.0.2.0/24"]
}
```

### GCP Data Sources

```hcl
# Get existing GCP project
data "google_project" "current" {}

# Get existing VPC
data "google_compute_network" "existing" {
  name = "my-network"
}

# Get compute zones
data "google_compute_zones" "available" {
  region = "us-central1"
  status = "UP"
}

# Use in instance
resource "google_compute_instance" "app" {
  name         = "app-server"
  machine_type = "n1-standard-1"
  zone         = data.google_compute_zones.available.names[0]
  
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }
  
  network_interface {
    network = data.google_compute_network.existing.id
  }
}
```

---

## 💡 Best Practices

### 1. Use Data Sources for Existing Infrastructure

```hcl
# ✅ Good - Query existing resources
data "aws_vpc" "existing" {
  id = var.vpc_id
}

# ❌ Bad - Hardcoding values
resource "aws_subnet" "example" {
  vpc_id = "vpc-12345678"  # Don't hardcode
}
```

### 2. Add Filters to Data Sources

```hcl
# ✅ Good - Specific filters
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical
  
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}

# ❌ Bad - Too broad
data "aws_ami" "ubuntu" {
  most_recent = true
}
```

### 3. Handle Data Source Errors

```hcl
# Use lifecycle to handle missing data
data "aws_vpc" "selected" {
  id = var.vpc_id
  
  lifecycle {
    postcondition {
      condition     = self.state == "available"
      error_message = "VPC must be in available state"
    }
  }
}
```

### 4. Document Data Source Dependencies

```hcl
# data.tf
# Data sources for querying existing infrastructure
# Dependencies:
# - Requires default VPC to exist
# - Requires appropriate AWS credentials with read permissions

data "aws_vpc" "default" {
  default = true
}
```

---

## 🐛 Common Issues and Solutions

### Issue 1: Data Source Returns Multiple Results

```
Error: multiple results found
```

**Solution:**
```hcl
# Add more specific filters
data "aws_vpc" "selected" {
  tags = {
    Name        = "production-vpc"
    Environment = "prod"
  }
}
```

### Issue 2: Data Source Returns No Results

```
Error: no matching resource found
```

**Solution:**
```hcl
# Verify the resource exists first
# Add appropriate filters
# Check permissions
```

### Issue 3: Circular Dependency

```
Error: Cycle: data.aws_subnet.example, aws_subnet.example
```

**Solution:**
```hcl
# Don't reference a resource in a data source that references that data source
# Break the circular dependency by using explicit dependencies
```

---

## 📝 Quiz

1. What is the difference between a resource and a data source?
2. How do you reference a data source attribute?
3. Can data sources modify infrastructure?
4. What's the syntax for a data source block?
5. How do you handle data sources that might not exist?

### Answers
1. Resources create/manage infrastructure; data sources read existing information
2. `data.provider_type.name.attribute`
3. No, data sources are read-only
4. `data "provider_type" "name" { ... }`
5. Use count/for_each with conditionals or lifecycle postconditions

---

## 🎓 Challenge Exercise

### Challenge: Dynamic Infrastructure Discovery

Create a Terraform configuration that:
1. Discovers all VPCs in your account tagged with `Environment = "production"`
2. For each VPC, find all subnets
3. Create a Security Group in each VPC allowing HTTPS
4. Output a summary of all discovered infrastructure
5. Bonus: Find the latest Ubuntu AMI and create an instance in one subnet

---

## 📚 Additional Resources

- [Data Sources Documentation](https://www.terraform.io/docs/language/data-sources/index.html)
- [AWS Provider Data Sources](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources)
- [Remote State Data Source](https://www.terraform.io/docs/language/state/remote-state-data.html)

---

## ⏭️ Next Steps

Ready to learn about **Remote State Best Practices**? Continue to [Module 12: Remote State Best Practices](./12-remote-state-best-practices.md)

---

**🎉 Congratulations!** You now understand how to use data sources to query existing infrastructure and make your Terraform code more dynamic!
