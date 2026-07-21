# AWS Credentials Setup Guide

## Step 1: Get AWS Access Keys

1. **Log in to AWS Console**: https://console.aws.amazon.com/
2. **Go to IAM**:
   - Click your username (top right)
   - Select "Security credentials"
3. **Create Access Key**:
   - Scroll to "Access keys" section
   - Click "Create access key"
   - Choose "Command Line Interface (CLI)"
   - Check the confirmation box
   - Click "Next" → "Create access key"
4. **Download or Copy**:
   - Access Key ID (starts with AKIA...)
   - Secret Access Key (show and copy)
   - **Important**: Save these! You can't view the secret again.

## Step 2: Configure AWS CLI

```bash
# Run this command
aws configure

# Enter when prompted:
AWS Access Key ID: <paste your access key>
AWS Secret Access Key: <paste your secret key>
Default region name: us-east-1
Default output format: json
```

## Step 3: Verify Credentials

```bash
# Test your credentials
aws sts get-caller-identity

# Should show:
# {
#     "UserId": "AIDAXXXXXXXXXX",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/your-username"
# }
```

## Step 4: Test Terraform

```bash
cd ~/Downloads/terraform-learning/terraform-practice/test-setup

# Initialize
terraform init

# Should work now!
terraform plan
```

---

## Alternative: Use AWS SSO (If Your Company Uses SSO)

```bash
# Configure SSO
aws configure sso

# Follow prompts to:
# 1. Enter SSO start URL
# 2. Choose your region
# 3. Select account/role
# 4. Set profile name (e.g., "default" or "terraform_practice")

# Login
aws sso login --profile default

# Test
aws sts get-caller-identity --profile default
```

---

## Troubleshooting

### Error: "InvalidClientTokenId"
- Your credentials are wrong or expired
- Run `aws configure` again with correct keys

### Error: "ExpiredToken"
- If using SSO: Run `aws sso login`
- If using access keys: Keys might be deactivated in AWS Console

### Error: "Access Denied"
- Your IAM user needs permissions
- Minimum needed: `AmazonEC2ReadOnlyAccess` (for learning)
- Better: `PowerUserAccess` (for full practice)

---

## Security Best Practices

1. **Never commit credentials** to Git
2. **Use IAM users** with specific permissions (not root)
3. **Enable MFA** on your AWS account
4. **Rotate keys regularly**
5. **Use least privilege** - only grant needed permissions

---

## What Permissions Do You Need?

For Terraform practice, you'll need:
- **EC2**: Launch instances, security groups, key pairs
- **VPC**: Create networks, subnets, route tables
- **S3**: Create buckets, objects (for state storage)
- **IAM**: Create roles and policies (for advanced practice)

**Recommended Managed Policy**: `PowerUserAccess`
