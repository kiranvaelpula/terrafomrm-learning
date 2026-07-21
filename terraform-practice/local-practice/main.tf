terraform {
  required_version = ">= 1.0"
}

# Local provider - no cloud credentials needed!
resource "local_file" "hello" {
  filename = "${path.module}/hello.txt"
  content  = "Hello from Terraform! Created at ${timestamp()}"
}

resource "local_file" "config" {
  filename = "${path.module}/config.json"
  content = jsonencode({
    environment = "learning"
    terraform   = true
    created_by  = "terraform-practice"
  })
}

output "hello_file_path" {
  value       = local_file.hello.filename
  description = "Path to the hello file"
}

output "config_content" {
  value       = jsondecode(local_file.config.content)
  description = "Configuration content"
}
