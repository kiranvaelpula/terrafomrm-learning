# Lab 02: Launch an EC2 Instance

**Difficulty**: Beginner  
**Time**: 20 minutes  
**Cost**: ~$0.01/hour (t2.micro free tier eligible)

## 🎯 Objectives

- Launch an EC2 instance using Terraform
- Create and attach a security group
- Use data sources to find AMI
- Connect to the instance

## 📋 Prerequisites

- Completed Lab 01
- AWS key pair created (or create one in this lab)

## 🔨 Tasks

### Task 1: Setup Provider

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
```

### Task 2: Find Latest Amazon Linux AMI

Use a data source to find the latest Amazon Linux 2023 AMI:

```hcl
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}
```

### Task 3: Create Security Group

Create a security group that allows:
- SSH (port 22) from your IP
- HTTP (port 80) from anywhere

```hcl
resource "aws_security_group" "web_sg" {
  name        = "terraform-lab-web-sg"
  description = "Security group for web server"

  # TODO: Add ingress rules for SSH and HTTP
  # TODO: Add egress rule for all outbound traffic
  
  tags = {
    Name = "Terraform Lab Web SG"
  }
}
```

### Task 4: Create EC2 Instance

```hcl
resource "aws_instance" "web_server" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t2.micro"
  
  # TODO: Attach the security group
  # TODO: Add user_data to install Apache
  # TODO: Add tags

  tags = {
    Name = "Terraform Lab Web Server"
  }
}
```

### Task 5: Add User Data

Add this user data script to install Apache:

```bash
#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello from Terraform!</h1>" > /var/www/html/index.html
```

### Task 6: Create Outputs

In `outputs.tf`:

```hcl
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.web_server.id
}

output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.web_server.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.web_server.public_dns
}
```

## ✅ Validation Steps

1. **Initialize and Plan**:
   ```bash
   terraform init
   terraform plan
   ```
   - Should show 2 resources to create

2. **Apply**:
   ```bash
   terraform apply
   ```

3. **Get the Public IP**:
   ```bash
   terraform output instance_public_ip
   ```

4. **Test the Web Server**:
   ```bash
   # Wait 2-3 minutes for instance to fully start
   curl http://$(terraform output -raw instance_public_ip)
   ```
   
   Or open in browser: `http://YOUR_INSTANCE_IP`

5. **Verify in AWS Console**:
   - EC2 → Instances → Find your instance
   - Check it's running
   - Verify security group is attached

## 🧹 Cleanup

```bash
terraform destroy
```

## 📚 Key Concepts Learned

- Data sources for dynamic values
- Security groups and rules
- EC2 instance configuration
- User data scripts
- Instance metadata

## 🎓 Challenge

1. **Add SSH key pair**:
   - Create a key pair resource
   - Attach it to the instance
   - SSH into the instance

2. **Add EBS volume**:
   - Create a separate EBS volume
   - Attach it to the instance

3. **Add Elastic IP**:
   - Create an Elastic IP
   - Associate it with the instance

## 💡 Tips

- Wait 2-3 minutes after apply for user data to complete
- Use `terraform show` to see all resource attributes
- Check `/var/log/cloud-init-output.log` on the instance if user data fails
- T2.micro is free tier eligible (750 hours/month)

## ⚠️ Security Notes

- Don't open SSH to 0.0.0.0/0 in production
- Use your specific IP: `YOUR_IP/32`
- Find your IP: `curl ifconfig.me`

## 📖 Reference

- [AWS EC2 Instance](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance)
- [AWS Security Group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group)
- [AWS AMI Data Source](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ami)
