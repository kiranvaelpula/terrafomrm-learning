output "dev_bucket_id" {
  description = "Development bucket ID"
  value       = module.dev_bucket.bucket_id
}

output "dev_bucket_arn" {
  description = "Development bucket ARN"
  value       = module.dev_bucket.bucket_arn
}

# TODO: Add outputs for staging and prod buckets
output "all_bucket_ids" {
  description = "All bucket IDs"
  value = {
    dev     = module.dev_bucket.bucket_id
    staging = module.staging_bucket.bucket_id
    prod    = module.prod_bucket.bucket_id
  }
}