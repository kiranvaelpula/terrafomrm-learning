# Module 10: Terraform Providers

## 📚 What You'll Learn
- Understanding Terraform Providers
- Provider configuration and versioning
- Multi-provider setup
- Provider aliases
- Best practices for provider management

---

## 🎯 What is a Provider?

A **provider** is a plugin that enables Terraform to interact with cloud platforms, SaaS providers, and other APIs. Think of providers as translators between Terraform and external services.

### Provider Responsibilities:
- 🔌 **API Communication**: Connect to service APIs
- 📦 **Resource Management**: Create, read, update, delete resources
- 🔄 **State Synchronization**: Track resource state
- 📝 **Schema Definition**: Define resource attributes

---

## 🏗️ Provider Types

### 1. Official Providers
Maintained by HashiCorp:
- `hashicorp/aws` - Amazon Web Services
- `hashicorp/azurerm` - Microsoft Azure
- `hashicorp/google` - Google Cloud Platform
- `hashicorp/kubernetes` - Kubernetes

### 2. Partner Providers
Maintained by technology partners:
- `datadog/datadog` - Datadog
- `mongodb/mongodbatlas` - MongoDB Atlas
- `pagerduty/pagerduty` - PagerDuty

### 3. Community Providers
Maintained by the community:
- Various open-source providers

---

## 📝 Provider Configuration

### Basic Provider Configuration

```hcl
# Configure the AWS Provider
provider "aws" {
  region = "us-east-1"
}

# Now you can create AWS resources
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-terraform-bucket-12345"
}
```

### Provider with Multiple Parameters

```hcl
provider "aws" {
  region     = "us-west-2"
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  
  default_tags {
    tags = {
      Environment = "Development"
      ManagedBy   = "Terraform"
      Project     = "MyApp"
    }
  }
}
```

---

## 🔒 Provider Version Constraints

### Why Version Constraints Matter
- Ensure compatibility
- Prevent breaking changes
- Reproducible infrastructure

### Version Constraint Syntax

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  # Allow 5.x versions
    }
    
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.0, < 4.0"  # Between 3.0 and 4.0
    }
    
    google = {
      source  = "hashicorp/google"
      version = "= 4.80.0"  # Exact version
    }
  }
}
```

### Version Constraint Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `=` | Exact version | `= 1.0.0` |
| `!=` | Not equal | `!= 1.0.0` |
| `>` | Greater than | `> 1.0.0` |
| `>=` | Greater or equal | `>= 1.0.0` |
| `<` | Less than | `< 2.0.0` |
| `<=` | Less or equal | `<= 2.0.0` |
| `~>` | Pessimistic constraint | `~> 1.2` (allows 1.3, 1.4, but not 2.0) |

---

## 🎭 Multiple Provider Configurations (Aliases)

### Why Use Provider Aliases?
- Manage resources in multiple regions
- Work with multiple AWS accounts
- Deploy to different environments

### Example: Multi-Region AWS Setup

```hcl
# Default provider (us-east-1)
provider "aws" {
  region = "us-east-1"
}

# West coast provider
provider "aws" {
  alias  = "west"
  region = "us-west-2"
}

# Europe provider
provider "aws" {
  alias  = "europe"
  region = "eu-west-1"
}

# Resources using different providers
resource "aws_s3_bucket" "east_bucket" {
  bucket = "my-east-bucket"
  # Uses default provider (us-east-1)
}

resource "aws_s3_bucket" "west_bucket" {
  provider = aws.west
  bucket   = "my-west-bucket"
}

resource "aws_s3_bucket" "europe_bucket" {
  provider = aws.europe
  bucket   = "my-europe-bucket"
}
```

### Example: Multi-Account AWS Setup

```hcl
provider "aws" {
  alias   = "production"
  region  = "us-east-1"
  profile = "prod-account"
}

provider "aws" {
  alias   = "development"
  region  = "us-east-1"
  profile = "dev-account"
}

resource "aws_s3_bucket" "prod_bucket" {
  provider = aws.production
  bucket   = "production-data-bucket"
}

resource "aws_s3_bucket" "dev_bucket" {
  provider = aws.development
  bucket   = "development-data-bucket"
}
```

---

## 🌐 Multi-Cloud Provider Setup

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# AWS Provider
provider "aws" {
  region = "us-east-1"
}

# Azure Provider
provider "azurerm" {
  features {}
}

# GCP Provider
provider "google" {
  project = "my-gcp-project"
  region  = "us-central1"
}

# Create resources in AWS
resource "aws_s3_bucket" "aws_bucket" {
  bucket = "my-aws-bucket"
}

# Create resources in Azure
resource "azurerm_storage_account" "azure_storage" {
  name                     = "myazurestorage"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = "East US"
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# Create resources in GCP
resource "google_storage_bucket" "gcp_bucket" {
  name     = "my-gcp-bucket"
  location = "US"
}
```

---

## 🔐 Provider Authentication Methods

### AWS Authentication

#### Method 1: Environment Variables
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

#### Method 2: AWS Profile
```hcl
provider "aws" {
  region  = "us-east-1"
  profile = "my-aws-profile"  # From ~/.aws/credentials
}
```

#### Method 3: IAM Role (Recommended for EC2)
```hcl
provider "aws" {
  region = "us-east-1"
  # Automatically uses IAM role attached to EC2 instance
}
```

#### Method 4: Assume Role
```hcl
provider "aws" {
  region = "us-east-1"
  
  assume_role {
    role_arn     = "arn:aws:iam::123456789012:role/TerraformRole"
    session_name = "terraform-session"
  }
}
```

### Azure Authentication

```hcl
provider "azurerm" {
  features {}
  
  subscription_id = var.subscription_id
  client_id       = var.client_id
  client_secret   = var.client_secret
  tenant_id       = var.tenant_id
}
```

### GCP Authentication

```hcl
provider "google" {
  project     = "my-gcp-project"
  region      = "us-central1"
  credentials = file("path/to/service-account-key.json")
}
```

---

## 🎪 Lab: Multi-Region S3 Buckets

### Objective
Create S3 buckets in three different AWS regions using provider aliases.

### Step 1: Create `providers.tf`

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

# Default provider - US East
provider "aws" {
  region = "us-east-1"
  
  default_tags {
    tags = {
      ManagedBy = "Terraform"
      Project   = "MultiRegion"
    }
  }
}

# US West provider
provider "aws" {
  alias  = "west"
  region = "us-west-2"
  
  default_tags {
    tags = {
      ManagedBy = "Terraform"
      Project   = "MultiRegion"
    }
  }
}

# EU provider
provider "aws" {
  alias  = "eu"
  region = "eu-west-1"
  
  default_tags {
    tags = {
      ManagedBy = "Terraform"
      Project   = "MultiRegion"
    }
  }
}
```

### Step 2: Create `main.tf`

```hcl
# East coast bucket
resource "aws_s3_bucket" "east" {
  bucket = "myapp-data-east-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket_versioning" "east" {
  bucket = aws_s3_bucket.east.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# West coast bucket
resource "aws_s3_bucket" "west" {
  provider = aws.west
  bucket   = "myapp-data-west-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket_versioning" "west" {
  provider = aws.west
  bucket   = aws_s3_bucket.west.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Europe bucket
resource "aws_s3_bucket" "eu" {
  provider = aws.eu
  bucket   = "myapp-data-eu-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket_versioning" "eu" {
  provider = aws.eu
  bucket   = aws_s3_bucket.eu.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Random suffix for unique bucket names
resource "random_id" "bucket_suffix" {
  byte_length = 4
}
```

### Step 3: Create `outputs.tf`

```hcl
output "east_bucket_name" {
  value       = aws_s3_bucket.east.bucket
  description = "US East bucket name"
}

output "west_bucket_name" {
  value       = aws_s3_bucket.west.bucket
  description = "US West bucket name"
}

output "eu_bucket_name" {
  value       = aws_s3_bucket.eu.bucket
  description = "EU bucket name"
}

output "bucket_summary" {
  value = {
    east = {
      name   = aws_s3_bucket.east.bucket
      region = "us-east-1"
      arn    = aws_s3_bucket.east.arn
    }
    west = {
      name   = aws_s3_bucket.west.bucket
      region = "us-west-2"
      arn    = aws_s3_bucket.west.arn
    }
    eu = {
      name   = aws_s3_bucket.eu.bucket
      region = "eu-west-1"
      arn    = aws_s3_bucket.eu.arn
    }
  }
  description = "Summary of all buckets"
}
```

### Step 4: Run Terraform

```bash
# Initialize
terraform init

# Plan
terraform plan

# Apply
terraform apply

# Verify
aws s3 ls --region us-east-1 | grep myapp-data-east
aws s3 ls --region us-west-2 | grep myapp-data-west
aws s3 ls --region eu-west-1 | grep myapp-data-eu

# Cleanup
terraform destroy
```

---

## 🎯 Best Practices

### 1. Always Specify Provider Versions
```hcl
# ❌ Bad - No version constraint
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

# ✅ Good - Version constrained
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

### 2. Use Default Tags
```hcl
provider "aws" {
  region = "us-east-1"
  
  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
      CostCenter  = var.cost_center
      Owner       = var.owner
    }
  }
}
```

### 3. Don't Hardcode Credentials
```hcl
# ❌ Bad - Hardcoded credentials
provider "aws" {
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}

# ✅ Good - Use environment variables or IAM roles
provider "aws" {
  region = "us-east-1"
  # Credentials from environment or IAM role
}
```

### 4. Use Separate Provider Configuration Files
```
project/
├── providers.tf       # All provider configurations
├── main.tf           # Main resources
├── variables.tf      # Variable definitions
└── outputs.tf        # Outputs
```

### 5. Provider Configuration in Modules
```hcl
# Root module
provider "aws" {
  region = "us-east-1"
}

module "vpc" {
  source = "./modules/vpc"
  # Providers are inherited by default
}

# For specific provider
module "west_vpc" {
  source = "./modules/vpc"
  
  providers = {
    aws = aws.west
  }
}
```

---

## 🔍 Provider Configuration Reference

### Common Provider Settings

#### AWS
```hcl
provider "aws" {
  region                   = "us-east-1"
  profile                  = "default"
  shared_credentials_files = ["~/.aws/credentials"]
  shared_config_files      = ["~/.aws/config"]
  
  default_tags {
    tags = {
      Environment = "Production"
    }
  }
  
  ignore_tags {
    keys = ["CreatedBy"]
  }
}
```

#### Azure
```hcl
provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = true
    }
    
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
  
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
}
```

#### GCP
```hcl
provider "google" {
  project     = var.project_id
  region      = "us-central1"
  zone        = "us-central1-a"
  credentials = file(var.credentials_file)
  
  user_project_override = true
  billing_project       = var.billing_project
}
```

---

## 💡 Common Provider Commands

```bash
# View providers used
terraform providers

# View provider schema
terraform providers schema -json

# Lock provider versions
terraform providers lock

# Mirror providers locally
terraform providers mirror ./providers

# Upgrade providers
terraform init -upgrade
```

---

## 🐛 Common Issues and Solutions

### Issue 1: Provider Version Conflicts
```
Error: Failed to query available provider packages
```

**Solution:**
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

### Issue 2: Provider Not Found
```
Error: Could not load plugin
```

**Solution:**
```bash
# Reinitialize
terraform init

# Or upgrade providers
terraform init -upgrade
```

### Issue 3: Authentication Errors
```
Error: error configuring Terraform AWS Provider
```

**Solution:**
```bash
# Verify credentials
aws sts get-caller-identity

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

---

## 📝 Quiz

1. What is a Terraform provider?
2. How do you specify a provider version?
3. What are provider aliases used for?
4. What's the difference between `=` and `~>` in version constraints?
5. How do providers get authenticated?

### Answers
1. A plugin that enables Terraform to interact with APIs
2. Using `required_providers` block with `version` parameter
3. To use multiple configurations of the same provider (e.g., different regions)
4. `=` requires exact version, `~>` allows patch/minor updates
5. Via environment variables, config files, IAM roles, or explicit credentials

---

## 🎓 Challenge Exercise

### Challenge: Multi-Cloud Storage Setup

Create a Terraform configuration that:
1. Creates an S3 bucket in AWS (us-east-1)
2. Creates an Azure Storage Account
3. Creates a GCS bucket in GCP
4. All with proper versioning and lifecycle policies
5. Output all bucket/storage URLs

**Requirements:**
- Use proper version constraints
- Implement default tags where applicable
- Use variables for configuration
- Include proper outputs

---

## 📚 Additional Resources

- [Terraform Provider Documentation](https://www.terraform.io/docs/language/providers/index.html)
- [Provider Registry](https://registry.terraform.io/browse/providers)
- [AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Azure Provider Docs](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [GCP Provider Docs](https://registry.terraform.io/providers/hashicorp/google/latest/docs)

---

## ⏭️ Next Steps

Ready to learn about **Data Sources**? Continue to [Module 11: Data Sources](./11-data-sources.md)

---

**🎉 Congratulations!** You now understand how to work with Terraform providers, configure multiple providers, and manage provider versions effectively!
