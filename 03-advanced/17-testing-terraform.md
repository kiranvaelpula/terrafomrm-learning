# Module 17: Testing Terraform

## 📚 What You'll Learn
- Terraform validation and formatting
- Static analysis with tflint
- Policy as Code with Sentinel/OPA
- Integration testing with Terratest
- Unit testing strategies
- CI/CD testing pipelines

---

## 🎯 Types of Testing

### 1. **Syntax Validation** - Is the code valid?
### 2. **Formatting** - Is the code properly formatted?
### 3. **Static Analysis** - Does it follow best practices?
### 4. **Plan Testing** - What will change?
### 5. **Integration Testing** - Does it actually work?
### 6. **Policy Testing** - Does it comply with rules?

---

## 1️⃣ Built-in Terraform Validation

### terraform fmt

```bash
# Check formatting
terraform fmt -check

# Format all files
terraform fmt -recursive

# See what will be changed
terraform fmt -diff
```

### terraform validate

```bash
# Initialize first
terraform init

# Validate configuration
terraform validate

# Example output:
# Success! The configuration is valid.

# Or with errors:
# Error: Missing required argument
#   on main.tf line 5, in resource "aws_instance" "web":
#   5: resource "aws_instance" "web" {
# The argument "ami" is required, but no definition was found.
```

### Custom Validation Rules

```hcl
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  
  validation {
    condition     = contains(["t2.micro", "t2.small", "t2.medium"], var.instance_type)
    error_message = "Instance type must be t2.micro, t2.small, or t2.medium."
  }
}

variable "environment" {
  description = "Environment name"
  type        = string
  
  validation {
    condition     = can(regex("^(dev|staging|prod)$", var.environment))
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "cidr_block" {
  description = "VPC CIDR block"
  type        = string
  
  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "Must be a valid IPv4 CIDR block address."
  }
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  
  validation {
    condition     = contains(keys(var.tags), "Environment")
    error_message = "Tags must include 'Environment' key."
  }
}
```

---

## 2️⃣ Static Analysis with TFLint

### Install TFLint

```bash
# macOS
brew install tflint

# Windows (Chocolatey)
choco install tflint

# Linux
curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash
```

### Configure TFLint

```.tflint.hcl
plugin "aws" {
  enabled = true
  version = "0.27.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

rule "aws_instance_invalid_type" {
  enabled = true
}

rule "aws_instance_previous_type" {
  enabled = true
}

rule "terraform_deprecated_interpolation" {
  enabled = true
}

rule "terraform_documented_variables" {
  enabled = true
}

rule "terraform_naming_convention" {
  enabled = true
  format  = "snake_case"
}
```

### Run TFLint

```bash
# Initialize TFLint
tflint --init

# Run linting
tflint

# With custom config
tflint --config=.tflint.hcl

# Specific directory
tflint modules/vpc/

# Example output:
# 3 issue(s) found:
# 
# Warning: variable "instance_type" is not used (terraform_unused_declarations)
#   on variables.tf line 10
# 
# Error: "t1.micro" is an invalid value for instance_type (aws_instance_invalid_type)
#   on main.tf line 15
```

---

## 3️⃣ Pre-commit Hooks

### Install pre-commit

```bash
# Install pre-commit
pip install pre-commit

# Or using Homebrew
brew install pre-commit
```

### Configure .pre-commit-config.yaml

```.pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.83.5
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_docs
      - id: terraform_tflint
        args:
          - --args=--config=__GIT_WORKING_DIR__/.tflint.hcl
      - id: terraform_tfsec
      - id: terraform_checkov
        args:
          - --args=--quiet
          - --args=--skip-check CKV_AWS_*

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key
```

### Install and Use

```bash
# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Now hooks run automatically on git commit
git add .
git commit -m "Add new feature"
# Hooks run automatically
```

---

## 4️⃣ Security Scanning

### tfsec

```bash
# Install tfsec
brew install tfsec

# Scan current directory
tfsec .

# With specific format
tfsec --format json

# Ignore specific checks
tfsec --exclude-check aws-s3-enable-bucket-encryption

# Example output:
# Result 1
# 
#   [aws-s3-enable-bucket-encryption]
#   CRITICAL: S3 Bucket does not have encryption enabled
#   
#   main.tf:10-15
#   
#      10 | resource "aws_s3_bucket" "data" {
#      11 |   bucket = "my-data-bucket"
#      12 |   # Missing encryption configuration
#      13 | }
```

### Checkov

```bash
# Install checkov
pip install checkov

# Scan directory
checkov --directory .

# Specific framework
checkov --framework terraform

# Skip specific checks
checkov -d . --skip-check CKV_AWS_19

# Example output:
# Check: CKV_AWS_19: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
# 	FAILED for resource: aws_s3_bucket.data
# 	File: main.tf:10-15
```

---

## 5️⃣ Integration Testing with Terratest

### Install Terratest

```go
// go.mod
module github.com/myorg/terraform-tests

go 1.21

require (
    github.com/gruntwork-io/terratest v0.45.0
    github.com/stretchr/testify v1.8.4
)
```

### Basic Test Example

```go
// test/terraform_basic_test.go
package test

import (
    "testing"
    
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestTerraformBasicExample(t *testing.T) {
    t.Parallel()
    
    // Configure Terraform options
    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        // Path to Terraform code
        TerraformDir: "../examples/basic",
        
        // Variables to pass
        Vars: map[string]interface{}{
            "instance_type": "t2.micro",
            "environment":   "test",
        },
    })
    
    // Clean up resources at the end of the test
    defer terraform.Destroy(t, terraformOptions)
    
    // Run terraform init and apply
    terraform.InitAndApply(t, terraformOptions)
    
    // Get output values
    instanceID := terraform.Output(t, terraformOptions, "instance_id")
    
    // Assertions
    assert.NotEmpty(t, instanceID)
}
```

### Advanced Test with AWS SDK

```go
// test/terraform_aws_test.go
package test

import (
    "testing"
    
    "github.com/aws/aws-sdk-go/aws"
    "github.com/aws/aws-sdk-go/aws/session"
    "github.com/aws/aws-sdk-go/service/ec2"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestEC2Instance(t *testing.T) {
    t.Parallel()
    
    terraformOptions := &terraform.Options{
        TerraformDir: "../examples/ec2",
        Vars: map[string]interface{}{
            "instance_type": "t2.micro",
            "ami_id":        "ami-0c55b159cbfafe1f0",
        },
    }
    
    defer terraform.Destroy(t, terraformOptions)
    
    terraform.InitAndApply(t, terraformOptions)
    
    // Get outputs
    instanceID := terraform.Output(t, terraformOptions, "instance_id")
    region := terraform.Output(t, terraformOptions, "region")
    
    // Verify with AWS SDK
    sess := session.Must(session.NewSession(&aws.Config{
        Region: aws.String(region),
    }))
    
    ec2Client := ec2.New(sess)
    
    input := &ec2.DescribeInstancesInput{
        InstanceIds: []*string{aws.String(instanceID)},
    }
    
    result, err := ec2Client.DescribeInstances(input)
    assert.NoError(t, err)
    assert.Equal(t, 1, len(result.Reservations))
    
    instance := result.Reservations[0].Instances[0]
    assert.Equal(t, "t2.micro", *instance.InstanceType)
    assert.Equal(t, "running", *instance.State.Name)
}
```

### Run Tests

```bash
# Run all tests
go test -v ./test/

# Run specific test
go test -v ./test/ -run TestTerraformBasicExample

# With timeout
go test -v -timeout 30m ./test/

# Parallel execution
go test -v -parallel 10 ./test/
```

---

## 🎪 Lab: Complete Testing Pipeline

### Project Structure

```
terraform-project/
├── .github/
│   └── workflows/
│       └── terraform-test.yml
├── .pre-commit-config.yaml
├── .tflint.hcl
├── examples/
│   └── basic/
│       ├── main.tf
│       └── variables.tf
├── modules/
│   └── vpc/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── test/
│   ├── go.mod
│   └── terraform_test.go
├── main.tf
├── variables.tf
└── outputs.tf
```

### GitHub Actions Workflow

```.github/workflows/terraform-test.yml
name: Terraform Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  validate:
    name: Validate
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.6.0
      
      - name: Terraform Format
        run: terraform fmt -check -recursive
      
      - name: Terraform Init
        run: terraform init
      
      - name: Terraform Validate
        run: terraform validate
  
  lint:
    name: Lint
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Setup TFLint
        uses: terraform-linters/setup-tflint@v3
        with:
          tflint_version: v0.48.0
      
      - name: Init TFLint
        run: tflint --init
      
      - name: Run TFLint
        run: tflint -f compact
  
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Run tfsec
        uses: aquasecurity/tfsec-action@v1.0.0
        with:
          soft_fail: false
      
      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: terraform
          soft_fail: false
  
  test:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: [validate, lint, security]
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Setup Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Run Terratest
        run: |
          cd test
          go test -v -timeout 30m
```

---

## 6️⃣ Policy as Code

### Open Policy Agent (OPA)

```rego
# policy/deny_public_s3.rego
package terraform.analysis

import input as tfplan

deny[msg] {
    r := tfplan.resource_changes[_]
    r.type == "aws_s3_bucket"
    r.change.after.acl == "public-read"
    msg := sprintf("S3 bucket '%s' has public-read ACL", [r.name])
}

deny[msg] {
    r := tfplan.resource_changes[_]
    r.type == "aws_instance"
    not r.change.after.instance_type in ["t2.micro", "t2.small", "t3.micro"]
    msg := sprintf("Instance '%s' uses invalid instance type: %s", [r.name, r.change.after.instance_type])
}
```

### Run OPA

```bash
# Install OPA
brew install opa

# Run policy check
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > tfplan.json
opa eval -d policy/ -i tfplan.json "data.terraform.analysis.deny"
```

---

## 💡 Testing Best Practices

### 1. Test Pyramid

```
           /\
          /  \  Manual Tests
         /____\
        /      \  Integration Tests (Terratest)
       /________\
      /          \  Unit Tests (validation, lint)
     /____________\
```

### 2. Environment Isolation

```hcl
# Use unique names for test resources
resource "aws_s3_bucket" "test" {
  bucket = "test-bucket-${random_id.test.hex}"
}

resource "random_id" "test" {
  byte_length = 8
}
```

### 3. Cleanup After Tests

```go
defer terraform.Destroy(t, terraformOptions)
```

### 4. Test Different Scenarios

```go
func TestInstanceTypes(t *testing.T) {
    testCases := []struct {
        name         string
        instanceType string
        shouldPass   bool
    }{
        {"valid_t2_micro", "t2.micro", true},
        {"valid_t2_small", "t2.small", true},
        {"invalid_t1_micro", "t1.micro", false},
    }
    
    for _, tc := range testCases {
        t.Run(tc.name, func(t *testing.T) {
            // Test logic
        })
    }
}
```

---

## 📝 Quiz

1. What's the difference between `terraform fmt` and `terraform validate`?
2. What tool is used for static analysis?
3. What is Terratest used for?
4. How do you prevent test resources from being left behind?
5. What is Policy as Code?

---

## 🎓 Challenge Exercise

Set up a complete testing pipeline with:
1. Pre-commit hooks for formatting and validation
2. TFLint for static analysis
3. tfsec for security scanning
4. Terratest for integration testing
5. GitHub Actions workflow
6. Policy enforcement with OPA

---

## ⏭️ Next Steps

Continue to [Module 18: CI/CD Integration](./18-cicd-integration.md)

---

**🎉 Congratulations!** You now know how to properly test Terraform code!
