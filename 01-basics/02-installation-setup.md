# Module 02: Installation & Setup

## 🎯 Learning Objectives
By the end of this module, you will:
- Install Terraform on your system
- Set up AWS CLI and credentials
- Configure VS Code for Terraform
- Verify your installation is working

---

## 📖 Understanding Installation & Setup (Intuition First)

Think about setting up a woodworking shop before you build anything. You need the main tool (the saw), the material supplier (the lumber yard you have an account with), and a good workbench where you'll actually work. Terraform's setup is the same three pieces: Terraform itself is the tool, your cloud provider account is the supplier, and your editor plus project folder is the workbench.

Terraform on its own is just a single small program — a decision-maker. It doesn't know how to talk to AWS or Azure until you give it credentials, the same way a builder needs an account at the lumber yard before they can order wood. That's why installing Terraform is only step one; configuring your cloud credentials (like the AWS CLI) is what actually lets Terraform *do* anything. Without credentials, Terraform can read your files but can't create a single resource.

The reason we're careful about credentials is that they're the keys to your cloud account, and your cloud account is where the money and the sensitive data live. Anyone holding those keys can spin up expensive resources or read private data, so they must never be typed directly into your code or committed to Git. Instead they live outside the project (in the AWS credentials file or environment variables) and get picked up automatically.

Setting up the editor and a `.gitignore` matters for a subtle reason: Terraform generates local files — provider plugins, lock files, and especially the state file — that either don't belong in version control or can leak secrets if committed. Getting the `.gitignore` right on day one saves you from accidentally publishing sensitive data later.

Finally, the verification step exists because a broken setup fails in confusing ways. Running `terraform version`, `aws sts get-caller-identity`, and a tiny test configuration confirms all three pieces — tool, credentials, and workspace — actually work together before you build anything real.

---

## 💻 Install Terraform

### Windows Installation

#### Option 1: Using Chocolatey (Recommended)
```powershell
# Install Chocolatey first (if not installed)
# Run PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Terraform
choco install terraform -y

# Verify installation
terraform version
```

#### Option 2: Manual Installation
1. Download from: https://www.terraform.io/downloads
2. Download `terraform_1.6.0_windows_amd64.zip`
3. Extract to `C:\terraform\`
4. Add to PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" variable
   - Add `C:\terraform\`
5. Open new PowerShell and run:
   ```powershell
   terraform version
   ```

### macOS Installation

```bash
# Using Homebrew (recommended)
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Verify
terraform version
```

### Linux Installation (Ubuntu/Debian)

```bash
# Add HashiCorp GPG key
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

# Add repository
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list

# Install
sudo apt update
sudo apt install terraform

# Verify
terraform version
```

---

## ☁️ Set Up AWS CLI

### Install AWS CLI

#### Windows:
```powershell
# Download and install from:
# https://awscli.amazonaws.com/AWSCLIV2.msi

# Verify
aws --version
```

#### macOS:
```bash
brew install awscli

# Verify
aws --version
```

#### Linux:
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify
aws --version
```

### Configure AWS Credentials

```bash
# Run configuration wizard
aws configure

# You'll be prompted for:
AWS Access Key ID: YOUR_ACCESS_KEY
AWS Secret Access Key: YOUR_SECRET_KEY
Default region name: eu-central-1
Default output format: json
```

### Where to Get AWS Credentials?

1. **Log into AWS Console**
2. **Go to IAM** → Users → Your User
3. **Security Credentials** tab
4. **Create Access Key**
5. **Copy** Access Key ID and Secret Access Key
6. ⚠️ **Never share or commit these to Git!**

### Verify AWS Access

```bash
# Test AWS connection
aws sts get-caller-identity

# Should output your AWS account info:
{
    "UserId": "AIDAXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-user"
}
```

---

## 🔧 Set Up VS Code

### Install VS Code
Download from: https://code.visualstudio.com/

### Install Terraform Extension

1. Open VS Code
2. Click Extensions (Ctrl+Shift+X)
3. Search "HashiCorp Terraform"
4. Click "Install"

### Install Helpful Extensions

```
1. HashiCorp Terraform (Official)
2. Terraform Autocomplete
3. AWS Toolkit
4. Git Graph
5. Better Comments
```

### Configure VS Code Settings

Create `.vscode/settings.json` in your workspace:

```json
{
  "terraform.languageServer": {
    "enabled": true,
    "args": []
  },
  "terraform.experimentalFeatures": {
    "validateOnSave": true
  },
  "[terraform]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "hashicorp.terraform"
  },
  "files.associations": {
    "*.tfvars": "terraform"
  }
}
```

---

## 📁 Create Your Workspace

### Set Up Directory Structure

```bash
# Create learning directory
mkdir terraform-practice
cd terraform-practice

# Create folder structure
mkdir 01-first-resource
mkdir 02-variables
mkdir 03-modules
mkdir 04-real-project

# Initialize Git
git init
```

### Create .gitignore

Create `.gitignore` file:

```bash
# Terraform files to ignore
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl
crash.log
override.tf
override.tf.json

# Sensitive data
*.tfvars
!example.tfvars
.env
*.pem
*.key

# OS files
.DS_Store
Thumbs.db

# Editor files
.vscode/
.idea/
*.swp
```

---

## ✅ Verification Checklist

Run these commands to verify everything is set up:

```bash
# 1. Terraform installed?
terraform version
# Expected: Terraform v1.6.x

# 2. AWS CLI installed?
aws --version
# Expected: aws-cli/2.x.x

# 3. AWS credentials configured?
aws sts get-caller-identity
# Expected: JSON with your account info

# 4. Can create files?
cd terraform-practice
touch test.tf
ls test.tf
# Expected: test.tf exists

# 5. VS Code installed?
code --version
# Expected: Version number
```

### Expected Output:

```
✅ Terraform v1.6.0
✅ aws-cli/2.13.0
✅ AWS Account: 123456789012
✅ File created successfully
✅ VS Code 1.82.0
```

---

## 🔍 Troubleshooting

### Issue: "terraform: command not found"

**Solution:**
```bash
# Check if Terraform is in PATH
echo $PATH  # Mac/Linux
echo $env:Path  # Windows PowerShell

# Add to PATH if missing (restart terminal after)
```

### Issue: "Unable to locate credentials"

**Solution:**
```bash
# Re-run AWS configure
aws configure

# Or manually create ~/.aws/credentials:
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
```

### Issue: "Access Denied" when running AWS commands

**Solution:**
- Check IAM user has required permissions
- Verify credentials are correct
- Try: `aws sts get-caller-identity` to test

### Issue: VS Code Terraform extension not working

**Solution:**
1. Reload VS Code window (Ctrl+Shift+P → "Reload Window")
2. Check extension is enabled
3. Verify `.tf` files have Terraform icon

---

## 🧪 Practice Exercise

### Test Your Setup

1. **Create a test file:**
   ```bash
   cd terraform-practice
   mkdir test-setup
   cd test-setup
   ```

2. **Create `main.tf`:**
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
   
   provider "aws" {
     region = "eu-central-1"
   }
   
   # This just checks if AWS connection works
   data "aws_caller_identity" "current" {}
   
   output "account_id" {
     value = data.aws_caller_identity.current.account_id
   }
   ```

3. **Initialize Terraform:**
   ```bash
   terraform init
   ```

   **Expected output:**
   ```
   Initializing the backend...
   Initializing provider plugins...
   - Installing hashicorp/aws v5.x.x...
   Terraform has been successfully initialized!
   ```

4. **Validate configuration:**
   ```bash
   terraform validate
   ```

   **Expected output:**
   ```
   Success! The configuration is valid.
   ```

5. **Plan (dry-run):**
   ```bash
   terraform plan
   ```

   **Expected output:**
   ```
   No changes. Your infrastructure matches the configuration.
   ```

6. **Apply:**
   ```bash
   terraform apply
   ```

   **You should see your AWS account ID!**

---

## 📚 Key Takeaways

```
✅ Terraform installed and verified
✅ AWS CLI configured with credentials
✅ VS Code set up with extensions
✅ Workspace created with proper .gitignore
✅ Test configuration runs successfully
```

---

## ⚠️ Security Best Practices

### DO:
- ✅ Use separate AWS IAM users for Terraform
- ✅ Enable MFA on AWS accounts
- ✅ Use `.gitignore` to exclude sensitive files
- ✅ Rotate access keys regularly
- ✅ Use least privilege IAM permissions

### DON'T:
- ❌ Commit `.tfstate` files to Git (contains sensitive data)
- ❌ Hardcode credentials in `.tf` files
- ❌ Share AWS access keys
- ❌ Use root account credentials
- ❌ Commit `.tfvars` with secrets

---

## 🎯 Challenge Exercise

**Set up a second AWS profile for testing:**

```bash
# Edit ~/.aws/credentials
[default]
aws_access_key_id = YOUR_PROD_KEY
aws_secret_access_key = YOUR_PROD_SECRET

[testing]
aws_access_key_id = YOUR_TEST_KEY
aws_secret_access_key = YOUR_TEST_SECRET

# Use the testing profile
export AWS_PROFILE=testing  # Mac/Linux
$env:AWS_PROFILE="testing"  # Windows PowerShell

# Verify
aws sts get-caller-identity
```

---

## 🎯 Interview Quick Points

- Terraform is a **single binary** — install via a package manager (Chocolatey, Homebrew, apt) or manually add to PATH
- Verify the install with **`terraform version`**
- Terraform needs **cloud credentials** to do anything — install and configure the provider CLI (e.g., `aws configure`)
- **Never hardcode credentials** in `.tf` files or commit them to Git
- Credentials live outside code — in `~/.aws/credentials`, environment variables, or a secrets manager
- Confirm cloud access with a command like **`aws sts get-caller-identity`**
- A proper **`.gitignore`** must exclude `.tfstate`, `.terraform/`, and `*.tfvars` with secrets
- **State files can contain sensitive data** — that's why they never go into version control
- Use **least-privilege IAM users** for Terraform, not root credentials, and enable MFA
- The HashiCorp Terraform VS Code extension adds syntax, validation, and format-on-save
- **Multiple named profiles** (e.g., `AWS_PROFILE`) let you target different accounts/environments
- Always verify the full toolchain (tool + credentials + workspace) before building real infrastructure

## ➡️ Next Module

Environment is ready! Let's create your first Terraform resource.

**[Module 03: Your First Resource →](./03-first-resource.md)**

---

**Progress:** ✅ Module 02 Complete | 📚 2/20 Modules
