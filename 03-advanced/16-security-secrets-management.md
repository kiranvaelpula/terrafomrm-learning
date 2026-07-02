# Module 16: Security & Secrets Management

## 📚 What You'll Learn
- Managing secrets in Terraform
- AWS Secrets Manager integration
- Using HashiCorp Vault
- Environment variables for secrets
- Sensitive data handling
- Security best practices

---

## 🔐 Why Secret Management Matters

### Problems with Hardcoded Secrets
- ❌ Visible in code and state files
- ❌ Stored in version control
- ❌ Shared across team insecurely
- ❌ Difficult to rotate
- ❌ Compliance violations

### Secure Approach
- ✅ Never commit secrets to Git
- ✅ Use external secret stores
- ✅ Encrypt state files
- ✅ Use IAM roles when possible
- ✅ Rotate secrets regularly

---

## 🎯 Methods for Managing Secrets

### 1. Environment Variables
### 2. AWS Secrets Manager
### 3. HashiCorp Vault
### 4. Terraform Cloud
### 5. SOPS (Secrets OPerationS)
### 6. AWS Parameter Store

---

## 1️⃣ Environment Variables

### Basic Usage

```hcl
# variables.tf
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true  # Marks as sensitive
}

# main.tf
resource "aws_db_instance" "main" {
  identifier     = "mydb"
  engine         = "postgres"
  instance_class = "db.t3.micro"
  username       = "admin"
  password       = var.db_password  # From environment
}
```

```bash
# Set environment variable
export TF_VAR_db_password="SuperSecretPassword123!"

# Or use .env file (don't commit!)
echo 'export TF_VAR_db_password="SuperSecretPassword123!"' > .env
source .env

# Run Terraform
terraform plan
terraform apply
```

### .gitignore for Secrets

```.gitignore
# Local .terraform directories
**/.terraform/*

# .tfstate files
*.tfstate
*.tfstate.*

# Crash log files
crash.log

# Exclude all .tfvars files
*.tfvars
*.tfvars.json

# Ignore override files
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# Ignore .env files
.env
.env.*

# Ignore secret files
secrets/
*.secret
*.pem
*.key
```

---

## 2️⃣ AWS Secrets Manager

### Store Secret in AWS Secrets Manager

```bash
# Create secret
aws secretsmanager create-secret \
    --name prod/db/password \
    --secret-string "SuperSecretPassword123!" \
    --region us-east-1

# Store JSON secret
aws secretsmanager create-secret \
    --name prod/app/config \
    --secret-string '{"username":"admin","password":"secret","api_key":"12345"}' \
    --region us-east-1
```

### Retrieve Secret in Terraform

```hcl
# data.tf
data "aws_secretsmanager_secret" "db_password" {
  name = "prod/db/password"
}

data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = data.aws_secretsmanager_secret.db_password.id
}

# main.tf
resource "aws_db_instance" "main" {
  identifier     = "prod-db"
  engine         = "postgres"
  instance_class = "db.t3.micro"
  username       = "admin"
  password       = data.aws_secretsmanager_secret_version.db_password.secret_string
}

# For JSON secrets
locals {
  app_config = jsondecode(data.aws_secretsmanager_secret_version.app_config.secret_string)
}

resource "aws_instance" "app" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  user_data = <<-EOF
              #!/bin/bash
              export API_KEY="${local.app_config.api_key}"
              export DB_USER="${local.app_config.username}"
              EOF
}
```

---

## 🎪 Lab 1: Complete Secrets Manager Setup

### Step 1: Create Secrets in AWS

```bash
# Database credentials
aws secretsmanager create-secret \
    --name myapp/prod/db \
    --secret-string '{
      "username": "admin",
      "password": "MyDBPassword123!",
      "host": "mydb.us-east-1.rds.amazonaws.com",
      "port": "5432",
      "dbname": "production"
    }'

# API keys
aws secretsmanager create-secret \
    --name myapp/prod/api-keys \
    --secret-string '{
      "stripe_key": "sk_live_xxxxxxxxxxxxx",
      "sendgrid_key": "SG.xxxxxxxxxxxxx",
      "aws_access_key": "AKIAxxxxxxxxxxxxx"
    }'
```

### Step 2: Create Terraform Configuration

```hcl
# provider.tf
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
  region = "us-east-1"
}

# secrets.tf
# Database secrets
data "aws_secretsmanager_secret" "db" {
  name = "myapp/prod/db"
}

data "aws_secretsmanager_secret_version" "db" {
  secret_id = data.aws_secretsmanager_secret.db.id
}

# API keys
data "aws_secretsmanager_secret" "api_keys" {
  name = "myapp/prod/api-keys"
}

data "aws_secretsmanager_secret_version" "api_keys" {
  secret_id = data.aws_secretsmanager_secret.api_keys.id
}

# Parse JSON secrets
locals {
  db_creds = jsondecode(data.aws_secretsmanager_secret_version.db.secret_string)
  api_keys = jsondecode(data.aws_secretsmanager_secret_version.api_keys.secret_string)
}

# main.tf
# RDS Database
resource "aws_db_instance" "app" {
  identifier             = "myapp-prod-db"
  engine                 = "postgres"
  engine_version         = "14.7"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  db_name                = local.db_creds.dbname
  username               = local.db_creds.username
  password               = local.db_creds.password
  skip_final_snapshot    = true
  publicly_accessible    = false
  
  tags = {
    Name        = "myapp-prod-db"
    Environment = "production"
  }
}

# Lambda function with secrets
resource "aws_lambda_function" "api" {
  filename      = "function.zip"
  function_name = "myapp-api"
  role          = aws_iam_role.lambda.arn
  handler       = "index.handler"
  runtime       = "nodejs18.x"
  
  environment {
    variables = {
      DB_HOST        = local.db_creds.host
      DB_USER        = local.db_creds.username
      DB_PASSWORD    = local.db_creds.password
      DB_NAME        = local.db_creds.dbname
      STRIPE_KEY     = local.api_keys.stripe_key
      SENDGRID_KEY   = local.api_keys.sendgrid_key
    }
  }
}

# IAM role for Lambda
resource "aws_iam_role" "lambda" {
  name = "lambda-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# outputs.tf
output "db_endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.app.endpoint
  sensitive   = true
}

output "db_username" {
  description = "Database username"
  value       = local.db_creds.username
  sensitive   = true
}
```

### Step 3: Deploy

```bash
terraform init
terraform plan
terraform apply

# Outputs are marked sensitive
terraform output db_endpoint
# Output: <sensitive>

# Force show sensitive output
terraform output -json | jq '.db_endpoint.value'
```

---

## 3️⃣ AWS Parameter Store

### Store Parameters

```bash
# Store individual parameters
aws ssm put-parameter \
    --name "/myapp/prod/db/host" \
    --value "mydb.us-east-1.rds.amazonaws.com" \
    --type String

aws ssm put-parameter \
    --name "/myapp/prod/db/password" \
    --value "MySecretPassword" \
    --type SecureString

# Store with KMS encryption
aws ssm put-parameter \
    --name "/myapp/prod/api/key" \
    --value "my-api-key-12345" \
    --type SecureString \
    --key-id alias/aws/ssm
```

### Retrieve in Terraform

```hcl
# data.tf
data "aws_ssm_parameter" "db_host" {
  name = "/myapp/prod/db/host"
}

data "aws_ssm_parameter" "db_password" {
  name            = "/myapp/prod/db/password"
  with_decryption = true
}

# main.tf
resource "aws_db_instance" "app" {
  identifier     = "myapp-db"
  engine         = "postgres"
  instance_class = "db.t3.micro"
  username       = "admin"
  password       = data.aws_ssm_parameter.db_password.value
  
  tags = {
    Name = "myapp-db"
  }
}
```

---

## 4️⃣ Sensitive Variable Handling

### Marking Variables as Sensitive

```hcl
# variables.tf
variable "database_password" {
  description = "Database admin password"
  type        = string
  sensitive   = true  # Won't be shown in logs
}

variable "api_keys" {
  description = "API keys"
  type = object({
    stripe   = string
    sendgrid = string
  })
  sensitive = true
}

# outputs.tf
output "db_connection_string" {
  description = "Database connection string"
  value       = "postgresql://${var.db_username}:${var.database_password}@${aws_db_instance.main.endpoint}/mydb"
  sensitive   = true  # Output won't be displayed
}
```

### Nonsensitive() Function

```hcl
# Sometimes you need to use sensitive values in non-sensitive contexts
resource "aws_instance" "app" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "app-server"
    # This would fail because var.database_password is sensitive
    # PasswordHash = md5(var.database_password)
    
    # Use nonsensitive() carefully
    PasswordHash = md5(nonsensitive(var.database_password))
  }
}
```

---

## 5️⃣ HashiCorp Vault Integration

### Setup Vault Provider

```hcl
# provider.tf
terraform {
  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = "~> 3.0"
    }
  }
}

provider "vault" {
  address = "https://vault.example.com:8200"
  token   = var.vault_token
}

# Read secrets from Vault
data "vault_generic_secret" "database" {
  path = "secret/myapp/database"
}

# Use secrets
resource "aws_db_instance" "app" {
  identifier     = "myapp-db"
  engine         = "postgres"
  instance_class = "db.t3.micro"
  username       = data.vault_generic_secret.database.data["username"]
  password       = data.vault_generic_secret.database.data["password"]
}
```

---

## 🔒 Sensitive Data in State Files

### Problem: State Files Contain Secrets

```json
// terraform.tfstate contains:
{
  "resources": [
    {
      "type": "aws_db_instance",
      "instances": [
        {
          "attributes": {
            "password": "MySecretPassword123!"  // ❌ Visible in state!
          }
        }
      ]
    }
  ]
}
```

### Solution 1: Encrypt State with S3

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true  # Encrypt at rest
    kms_key_id     = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
    dynamodb_table = "terraform-locks"
  }
}
```

### Solution 2: Use Terraform Cloud

```hcl
terraform {
  cloud {
    organization = "my-org"
    
    workspaces {
      name = "prod"
    }
  }
}

# State is encrypted and managed by Terraform Cloud
```

---

## 🛡️ Security Best Practices

### 1. Never Hardcode Secrets

```hcl
# ❌ BAD - Hardcoded
resource "aws_db_instance" "app" {
  password = "MyPassword123!"
}

# ✅ GOOD - From external source
resource "aws_db_instance" "app" {
  password = data.aws_secretsmanager_secret_version.db_password.secret_string
}
```

### 2. Use IAM Roles Instead of Keys

```hcl
# ❌ BAD - Access keys
provider "aws" {
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}

# ✅ GOOD - IAM role or environment
provider "aws" {
  region = "us-east-1"
  # Uses IAM role or environment variables
}
```

### 3. Limit Secret Access

```hcl
# IAM policy for Secrets Manager access
resource "aws_iam_policy" "secrets_read" {
  name = "secrets-read-policy"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:us-east-1:123456789012:secret:myapp/prod/*"
        ]
        Condition = {
          StringEquals = {
            "aws:RequestedRegion": "us-east-1"
          }
        }
      }
    ]
  })
}
```

### 4. Rotate Secrets Regularly

```hcl
# Enable automatic rotation
resource "aws_secretsmanager_secret_rotation" "db_password" {
  secret_id           = aws_secretsmanager_secret.db_password.id
  rotation_lambda_arn = aws_lambda_function.rotate_secret.arn
  
  rotation_rules {
    automatically_after_days = 30
  }
}
```

### 5. Use Separate Secrets Per Environment

```
secrets/
├── dev/
│   ├── db/password
│   └── api/keys
├── staging/
│   ├── db/password
│   └── api/keys
└── prod/
    ├── db/password
    └── api/keys
```

---

## 🎪 Lab 2: Complete Security Setup

### Objective: Secure application with proper secret management

```hcl
# secrets.tf
# Create secrets in AWS Secrets Manager using Terraform
resource "aws_secretsmanager_secret" "db_master_password" {
  name                    = "prod/db/master-password"
  recovery_window_in_days = 7
  
  tags = {
    Environment = "production"
    ManagedBy   = "Terraform"
  }
}

resource "random_password" "db_master" {
  length  = 32
  special = true
}

resource "aws_secretsmanager_secret_version" "db_master_password" {
  secret_id     = aws_secretsmanager_secret.db_master_password.id
  secret_string = random_password.db_master.result
}

# KMS key for encryption
resource "aws_kms_key" "secrets" {
  description             = "KMS key for secrets encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  
  tags = {
    Name = "secrets-encryption-key"
  }
}

resource "aws_kms_alias" "secrets" {
  name          = "alias/secrets-encryption"
  target_key_id = aws_kms_key.secrets.key_id
}

# RDS with secure password
resource "aws_db_instance" "secure" {
  identifier     = "secure-db"
  engine         = "postgres"
  engine_version = "14.7"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.secrets.arn
  
  db_name  = "myapp"
  username = "admin"
  password = aws_secretsmanager_secret_version.db_master_password.secret_string
  
  backup_retention_period = 7
  skip_final_snapshot     = false
  final_snapshot_identifier = "secure-db-final-snapshot"
  
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  tags = {
    Name        = "secure-database"
    Environment = "production"
  }
}

# Store connection info back in Secrets Manager
resource "aws_secretsmanager_secret" "db_connection" {
  name = "prod/db/connection-info"
}

resource "aws_secretsmanager_secret_version" "db_connection" {
  secret_id = aws_secretsmanager_secret.db_connection.id
  
  secret_string = jsonencode({
    username = aws_db_instance.secure.username
    password = aws_secretsmanager_secret_version.db_master_password.secret_string
    endpoint = aws_db_instance.secure.endpoint
    port     = aws_db_instance.secure.port
    dbname   = aws_db_instance.secure.db_name
  })
}
```

---

## 📝 Quiz

1. Why should secrets never be hardcoded?
2. What are three methods to manage secrets in Terraform?
3. How do you mark a variable as sensitive?
4. Where are secrets visible even when marked sensitive?
5. What's the best practice for AWS authentication?

---

## 🎓 Challenge Exercise

Create a secure infrastructure with:
1. RDS database with password from AWS Secrets Manager
2. Lambda function accessing the database
3. IAM roles with least privilege
4. KMS encryption for all secrets
5. Automatic secret rotation
6. No hardcoded credentials anywhere

---

## ⏭️ Next Steps

Continue to [Module 17: Testing Terraform](./17-testing-terraform.md)

---

**🎉 Congratulations!** You now understand how to manage secrets securely in Terraform!
