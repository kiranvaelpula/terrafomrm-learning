# Fix AWS Profile Configuration

Your `terraform_practice` profile is missing the access key and secret key. Here's how to fix it:

## Option 1: Manual Edit (Recommended)

Edit your credentials file:

```bash
notepad ~/.aws/credentials
```

Find the `[terraform_practice]` section and make it look like this:

```ini
[terraform_practice]
aws_access_key_id = YOUR_ACCESS_KEY_HERE
aws_secret_access_key = YOUR_SECRET_KEY_HERE
region = us-east-1
```

**Replace**:
- `YOUR_ACCESS_KEY_HERE` with your actual AWS Access Key (starts with AKIA...)
- `YOUR_SECRET_KEY_HERE` with your actual AWS Secret Access Key

## Option 2: Use AWS Configure

Run this command and follow prompts:

```bash
aws configure --profile terraform_practice
```

Enter:
1. AWS Access Key ID: [paste your key]
2. AWS Secret Access Key: [paste your secret]
3. Default region name: `us-east-1`
4. Default output format: `json`

## Option 3: Use Default Profile

If you want to use your default credentials instead:

1. Update `main.tf`:
```hcl
provider "aws" {
  region = "us-east-1"
  # Remove or comment out the profile line
}
```

2. Make sure your default profile works:
```bash
aws sts get-caller-identity
```

## After Fixing

Test your profile:

```bash
# Test the profile
aws sts get-caller-identity --profile terraform_practice

# If it works, you should see your account info
# Then try Terraform:
cd ~/Downloads/terraform-learning/terraform-practice/test-setup
terraform plan
```
