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
  profile = "default"
}

# Use module to create development bucket
module "dev_bucket" {
  source = "./modules/s3-bucket"
  
  bucket_name       = "my-dev-bucket-yourname-2026"
  enable_versioning = true
  
  tags = {
    Environment = "Development"
    Purpose     = "Learning Modules"
  }
}

# TODO: Create staging bucket using the same module
module "staging_bucket" {
  source = "./modules/s3-bucket"
  bucket_name       = "my-stage-bucket-yourname-2026"
  enable_versioning = true
  
  tags = {
    Environment = "Stage"
    Purpose     = "Learning Modules"
}
}

# TODO: Create production bucket
module "prod_bucket" {
  source = "./modules/s3-bucket"

  bucket_name       = "my-prod-bucket-yourname-2026"
  enable_versioning = true
  
  tags = {
    Environment = "Production"
    Purpose     = "Learning Modules"
  
  # Your configuration here
  # Enable versioning and encryption
}
}