variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
  
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]*[a-z0-9]$", var.bucket_name))
    error_message = "Bucket name must start and end with lowercase letter or number."
  }
}

variable "enable_versioning" {
  description = "Enable versioning for the bucket"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to the bucket"
  type        = map(string)
  default     = {}
}

# TODO: Add more variables:
# - enable_encryption
# - lifecycle_rules
# - cors_configuration