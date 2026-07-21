# Lab 12: Remote State with Team Collaboration

**Difficulty**: Advanced  
**Time**: 40 minutes  
**Cost**: ~$0.01/hour

## 🎯 Objectives

- Set up S3 + DynamoDB backend for team collaboration
- Implement state locking to prevent concurrent modifications
- Use remote state data sources to share outputs between projects
- Configure encryption and access control
- Learn team collaboration best practices

## 📋 Prerequisites

- Completed Lab 08 (State Management basics)
- Understanding of state files
- Multiple Terraform projects or team scenarios

## 🏗️ Architecture

```
Project A (Network)                Project B (Application)
├── VPC                            ├── EC2 Instances
├── Subnets                        ├── Uses VPC from Project A
└── Outputs                        └── Reads remote state from A
        │
        └──────────> S3 Bucket (State Storage)
                            │
                     DynamoDB (State Locks)
```

## 🔨 Tasks

### Task 1: Set Up Backend Infrastructure

**(Complete this once for all projects)**

**00-backend/main.tf**:

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

# S3 bucket for state storage
resource "aws_s3_bucket" "terraform_state" {
  bucket = "team-terraform-state-yourname-2026"
  
  lifecycle {
    prevent_destroy = false  # Set true in production!
  }
  
  tags = {
    Name        = "Terraform Team State Bucket"
    Environment = "Shared"
    Purpose     = "State Storage"
  }
}

# Enable versioning (critical for state recovery!)
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Optional: Lifecycle policy to manage old versions
resource "aws_s3_bucket_lifecycle_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  rule {
    id     = "expire-old-versions"
    status = "Enabled"
    
    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
  
  rule {
    id     = "delete-incomplete-uploads"
    status = "Enabled"
    
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# DynamoDB table for state locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-team-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
  
  tags = {
    Name        = "Terraform Team State Locks"
    Environment = "Shared"
  }
}

# Outputs for other projects
output "state_bucket_name" {
  description = "S3 bucket name for state storage"
  value       = aws_s3_bucket.terraform_state.id
}

output "dynamodb_table_name" {
  description = "DynamoDB table name for state locking"
  value       = aws_dynamodb_table.terraform_locks.name
}

output "backend_config" {
  description = "Backend configuration to use in other projects"
  value = <<-EOF
    terraform {
      backend "s3" {
        bucket         = "${aws_s3_bucket.terraform_state.id}"
        region         = "us-east-1"
        profile        = "terraform_practice"
        dynamodb_table = "${aws_dynamodb_table.terraform_locks.name}"
        encrypt        = true
      }
    }
  EOF
}
```

**Apply backend infrastructure**:

```bash
cd 00-backend
terraform init
terraform apply
terraform output backend_config
```

### Task 2: Create Network Project (Project A)

**01-network/backend.tf**:

```hcl
terraform {
  required_version = ">= 1.0"
  
  backend "s3" {
    bucket         = "team-terraform-state-yourname-2026"
    key            = "network/terraform.tfstate"
    region         = "us-east-1"
    profile        = "terraform_practice"
    dynamodb_table = "terraform-team-locks"
    encrypt        = true
  }
}
```

**01-network/main.tf**:

```hcl
provider "aws" {
  region  = "us-east-1"
  profile = "terraform_practice"
}

# Create VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name    = "Shared VPC"
    Project = "Network"
  }
}

# Create public subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "Public Subnet"
  }
}

# Create Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "Main IGW"
  }
}

# Create route table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = {
    Name = "Public Route Table"
  }
}

# Associate route table
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Security group for web servers
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main.id
  
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
    Name = "Web Security Group"
  }
}
```

**01-network/outputs.tf**:

```hcl
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_id" {
  description = "ID of the public subnet"
  value       = aws_subnet.public.id
}

output "web_security_group_id" {
  description = "ID of the web security group"
  value       = aws_security_group.web.id
}
```

**Apply network project**:

```bash
cd 01-network
terraform init
terraform apply
```

### Task 3: Create Application Project (Project B)

**02-application/backend.tf**:

```hcl
terraform {
  required_version = ">= 1.0"
  
  backend "s3" {
    bucket         = "team-terraform-state-yourname-2026"
    key            = "application/terraform.tfstate"
    region         = "us-east-1"
    profile        = "terraform_practice"
    dynamodb_table = "terraform-team-locks"
    encrypt        = true
  }
}
```

**02-application/main.tf**:

```hcl
provider "aws" {
  region  = "us-east-1"
  profile = "terraform_practice"
}

# Read remote state from network project
data "terraform_remote_state" "network" {
  backend = "s3"
  
  config = {
    bucket  = "team-terraform-state-yourname-2026"
    key     = "network/terraform.tfstate"
    region  = "us-east-1"
    profile = "terraform_practice"
  }
}

# Get latest Amazon Linux AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# Create EC2 instance using outputs from network project
resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  
  # Use VPC and subnet from network project
  subnet_id              = data.terraform_remote_state.network.outputs.public_subnet_id
  vpc_security_group_ids = [data.terraform_remote_state.network.outputs.web_security_group_id]
  
  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y httpd
    systemctl start httpd
    systemctl enable httpd
    echo "<h1>Hello from Application Project!</h1>" > /var/www/html/index.html
    echo "<p>VPC ID: ${data.terraform_remote_state.network.outputs.vpc_id}</p>" >> /var/www/html/index.html
  EOF
  
  tags = {
    Name    = "Web Server"
    Project = "Application"
  }
}
```

**02-application/outputs.tf**:

```hcl
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.web.id
}

output "instance_public_ip" {
  description = "Public IP of the instance"
  value       = aws_instance.web.public_ip
}

output "web_url" {
  description = "URL of the web server"
  value       = "http://${aws_instance.web.public_ip}"
}

# Show network info from remote state
output "using_vpc_id" {
  description = "VPC ID from network project"
  value       = data.terraform_remote_state.network.outputs.vpc_id
}
```

**Apply application project**:

```bash
cd 02-application
terraform init
terraform apply
terraform output web_url
```

### Task 4: Test State Locking

**Terminal 1**:

```bash
cd 01-network
terraform apply
# Don't confirm yet - leave it waiting
```

**Terminal 2** (quickly):

```bash
cd 01-network
terraform apply
# Should see: "Error acquiring the state lock"
```

This proves state locking is working!

### Task 5: View State in S3

```bash
# List state files
aws s3 ls s3://team-terraform-state-yourname-2026/ --profile terraform_practice --recursive

# Download network state (read-only!)
aws s3 cp s3://team-terraform-state-yourname-2026/network/terraform.tfstate ./network-state.json --profile terraform_practice

# View state (don't edit!)
cat network-state.json | jq '.outputs'
```

## ✅ Validation Steps

1. **Verify backend setup**:
   ```bash
   aws s3 ls s3://team-terraform-state-yourname-2026/ --profile terraform_practice
   # Should show network/ and application/ folders
   ```

2. **Check state locking**:
   ```bash
   aws dynamodb scan --table-name terraform-team-locks --profile terraform_practice
   # Should be empty when no operations running
   ```

3. **Verify remote state data source**:
   ```bash
   cd 02-application
   terraform output using_vpc_id
   # Should match VPC ID from network project
   ```

4. **Test the web server**:
   ```bash
   curl $(terraform output -raw web_url)
   # Should show VPC ID from network project
   ```

5. **Verify versioning**:
   ```bash
   aws s3api list-object-versions \
     --bucket team-terraform-state-yourname-2026 \
     --prefix network/ \
     --profile terraform_practice
   ```

## 🧹 Cleanup

**Important order**:

```bash
# 1. Destroy application first (depends on network)
cd 02-application
terraform destroy

# 2. Destroy network
cd ../01-network
terraform destroy

# 3. Finally destroy backend infrastructure
cd ../00-backend
terraform destroy
```

## 📚 Key Concepts Learned

- S3 + DynamoDB backend for teams
- State locking to prevent concurrent modifications
- Remote state data sources
- State encryption and versioning
- Cross-project dependencies
- Terraform project organization

## 🎓 Challenge

1. **Add IAM Policies for Team Members**:
   ```hcl
   # Restrict who can access state
   resource "aws_s3_bucket_policy" "terraform_state" {
     bucket = aws_s3_bucket.terraform_state.id
     
     policy = jsonencode({
       Version = "2012-10-17"
       Statement = [
         {
           Sid    = "EnforcedTLS"
           Effect = "Deny"
           Principal = "*"
           Action = "s3:*"
           Resource = [
             aws_s3_bucket.terraform_state.arn,
             "${aws_s3_bucket.terraform_state.arn}/*"
           ]
           Condition = {
             Bool = {
               "aws:SecureTransport" = "false"
             }
           }
         }
       ]
     })
   }
   ```

2. **Add KMS Encryption**:
   - Create KMS key
   - Use for S3 encryption
   - Grant team access

3. **Create Database Project**:
   - Project C: Database (RDS)
   - Uses VPC from Project A
   - Outputs connection string to Project B

4. **Implement Workspace Strategy**:
   - Use workspaces for environments
   - Different state paths per workspace
   - Environment-specific configurations

5. **Add State File Backup**:
   - Lambda to backup state to separate bucket
   - Cross-region replication
   - Automated testing of backup restoration

## 💡 Tips

- **NEVER** edit state files manually
- **ALWAYS** enable versioning on state bucket
- **ALWAYS** enable state locking for teams
- Use descriptive state file keys (`network/`, `app/`, `db/`)
- Implement least privilege for state bucket access
- Use separate state files per environment
- Document remote state data source dependencies
- Test state locking before team deployment
- Keep backend configuration in separate file
- Use consistent backend configuration across team

## 🔒 Security Best Practices

1. **Encryption**:
   ```hcl
   # Use KMS for enhanced security
   sse_algorithm     = "aws:kms"
   kms_master_key_id = "arn:aws:kms:..."
   ```

2. **Access Control**:
   - IAM policies for state bucket
   - MFA delete on bucket
   - Bucket policy requiring SSL
   - CloudTrail for audit logs

3. **State File Protection**:
   - Versioning enabled
   - Lifecycle policies for old versions
   - Cross-region replication
   - Regular backups

## 🆚 Collaboration Strategies

| Strategy | Use Case | Pros | Cons |
|----------|----------|------|------|
| Single State | Small teams | Simple | Conflicts |
| Split States | Large teams | Isolated | Complex dependencies |
| Workspaces | Same infra | Easy | Single file |
| Separate Accounts | Enterprises | Secure | Management overhead |

## 📖 Reference

- [S3 Backend](https://developer.hashicorp.com/terraform/language/settings/backends/s3)
- [Remote State Data Source](https://developer.hashicorp.com/terraform/language/state/remote-state-data)
- [State Locking](https://developer.hashicorp.com/terraform/language/state/locking)
- [Team Collaboration](https://developer.hashicorp.com/terraform/tutorials/automation/automate-terraform)

## ✨ Solution

Solution files are in the `solution/` directory. Try completing the lab yourself first!

