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
  region  = "us-east-1"  # Change to your preferred region
  profile = "terraform_practice"  # Use your SSO profile
}

# This just checks if AWS connection works
data "aws_caller_identity" "current" {}

output "account_id" {
  value       = data.aws_caller_identity.current.account_id
  description = "Your AWS Account ID"
}

output "caller_arn" {
  value       = data.aws_caller_identity.current.arn
  description = "Your AWS IAM User ARN"
}

output "user_id" {
  value       = data.aws_caller_identity.current.user_id
  description = "Your AWS User ID"
}
