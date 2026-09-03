# TODO: Create S3 bucket resource with:
# - Configurable bucket name
# - Configurable versioning
# - Configurable tags
# - Server-side encryption enabled by default

resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  
  tags = merge(
    var.tags,
    {
      ManagedBy = "Terraform"
      Module    = "s3-bucket"
    }
  )
}

# TODO: Add versioning configuration
# Use var.enable_versioning

# TODO: Add server-side encryption
# Use aws_s3_bucket_server_side_encryption_configuration