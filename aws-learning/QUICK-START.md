# AWS Quick Start Guide

Get started with AWS in 30 minutes.

## 🎯 What You'll Do

1. Create AWS account
2. Set up AWS CLI
3. Configure IAM user
4. Launch first EC2 instance
5. Deploy a simple web app

**Time Required**: 30-45 minutes  
**Cost**: Free (using AWS Free Tier)

---

## Step 1: Create AWS Account (10 minutes)

### Prerequisites
- Valid email address
- Phone number for verification
- Credit/debit card (no charges for free tier)

### Create Account

1. **Visit AWS Console**
   ```
   https://aws.amazon.com/
   ```

2. **Click "Create an AWS Account"**

3. **Enter Account Information**
   - Email address
   - Password
   - AWS account name

4. **Contact Information**
   - Choose "Personal" or "Professional"
   - Enter your details

5. **Payment Information**
   - Enter credit card details
   - AWS won't charge for free tier usage

6. **Identity Verification**
   - Enter phone number
   - Verify with code

7. **Select Support Plan**
   - Choose "Basic Support - Free"

8. **Complete Sign-Up**
   - Wait for account activation (2-24 hours)

### ✅ Checkpoint
- Received welcome email
- Can sign in to AWS Console
- Account shows "Active" status

---

## Step 2: Secure Root Account (5 minutes)

### Enable MFA (Multi-Factor Authentication)

1. **Sign in to AWS Console**
   ```
   https://console.aws.amazon.com/
   ```

2. **Go to IAM Dashboard**
   - Search for "IAM" in services

3. **Add MFA for Root User**
   - Click "Add MFA"
   - Choose "Virtual MFA device"
   - Scan QR code with Google Authenticator or Authy
   - Enter two consecutive MFA codes

### ✅ Checkpoint
- MFA enabled for root account
- Green checkmark in IAM dashboard

---

## Step 3: Create IAM User (10 minutes)

**Never use root account for daily tasks!**

### Create Admin User

1. **In IAM Dashboard, click "Users"**

2. **Click "Add User"**
   - Username: `admin-user`
   - Access type: Both (Console + Programmatic)

3. **Set Permissions**
   - Attach existing policies: `AdministratorAccess`

4. **Add Tags (Optional)**
   - Key: `Environment`, Value: `learning`

5. **Review and Create**
   - Download credentials CSV (save securely!)

6. **Enable MFA for IAM User**
   - Select user → Security credentials
   - Assign MFA device

### Save Access Keys
```bash
# Save these securely (from downloaded CSV)
Access Key ID: AKIAIOSFODNN7EXAMPLE
Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Console Password: YourPassword123!
Console URL: https://YOUR-ACCOUNT-ID.signin.aws.amazon.com/console
```

### ✅ Checkpoint
- IAM user created
- Admin permissions attached
- MFA enabled
- Credentials saved securely

---

## Step 4: Install AWS CLI (5 minutes)

### For Windows

```powershell
# Download and install
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Verify installation
aws --version
# Expected: aws-cli/2.x.x Python/3.x.x Windows/10 exe/AMD64
```

### For macOS

```bash
# Using Homebrew
brew install awscli

# Or download installer
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Verify
aws --version
```

### For Linux

```bash
# Download and install
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify
aws --version
```

### Configure AWS CLI

```bash
# Run configuration
aws configure

# Enter your credentials:
AWS Access Key ID: YOUR_ACCESS_KEY_ID
AWS Secret Access Key: YOUR_SECRET_ACCESS_KEY
Default region name: us-east-1
Default output format: json
```

### Test Configuration

```bash
# Get caller identity
aws sts get-caller-identity

# Expected output:
{
    "UserId": "AIDAIOSFODNN7EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/admin-user"
}
```

### ✅ Checkpoint
- AWS CLI installed
- Configuration successful
- Can run AWS commands

---

## Step 5: Launch First EC2 Instance (10 minutes)

### Using AWS Console

1. **Navigate to EC2**
   - Search "EC2" in AWS Console

2. **Launch Instance**
   - Click "Launch Instance"

3. **Choose AMI**
   - Select "Amazon Linux 2 AMI (Free tier eligible)"

4. **Choose Instance Type**
   - Select "t2.micro" (Free tier eligible)

5. **Configure Instance**
   - Keep defaults
   - Advanced: Add user data (optional)

6. **Add Storage**
   - 8 GB (Free tier: up to 30 GB)

7. **Add Tags**
   - Key: `Name`, Value: `my-first-instance`

8. **Configure Security Group**
   - Create new security group
   - Add rule: HTTP (port 80) from Anywhere
   - Add rule: SSH (port 22) from My IP

9. **Review and Launch**
   - Create new key pair
   - Name: `my-first-keypair`
   - Download .pem file (save securely!)
   - Click "Launch Instance"

### Using AWS CLI

```bash
# Create key pair
aws ec2 create-key-pair \
  --key-name my-first-keypair \
  --query 'KeyMaterial' \
  --output text > my-first-keypair.pem

# Set permissions (Linux/macOS)
chmod 400 my-first-keypair.pem

# Launch instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name my-first-keypair \
  --security-group-ids sg-0123456789abcdef0 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=my-first-instance}]'
```

### Connect to Instance

```bash
# Get instance public IP
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=my-first-instance" \
  --query 'Reservations[*].Instances[*].PublicIpAddress' \
  --output text

# SSH into instance
ssh -i my-first-keypair.pem ec2-user@YOUR_INSTANCE_IP
```

### ✅ Checkpoint
- EC2 instance running
- Can SSH into instance
- Instance shows in EC2 dashboard

---

## Step 6: Deploy Simple Web App (5 minutes)

### Install Web Server

```bash
# SSH into your EC2 instance first
ssh -i my-first-keypair.pem ec2-user@YOUR_INSTANCE_IP

# Update packages
sudo yum update -y

# Install Apache
sudo yum install httpd -y

# Start Apache
sudo systemctl start httpd
sudo systemctl enable httpd

# Create simple web page
echo "<h1>Hello from AWS!</h1><p>My first EC2 deployment</p>" | \
  sudo tee /var/www/html/index.html
```

### Test Web App

```bash
# In browser, visit:
http://YOUR_INSTANCE_IP

# Or using curl
curl http://YOUR_INSTANCE_IP
```

### ✅ Checkpoint
- Web server running
- Can access web page from browser
- Shows "Hello from AWS!"

---

## Step 7: Clean Up (Important!)

**Always clean up to avoid charges!**

### Stop Instance (Preserves for later)

```bash
# Using AWS CLI
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# Using Console
EC2 Dashboard → Select instance → Instance State → Stop
```

### Terminate Instance (Permanently deletes)

```bash
# Using AWS CLI
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0

# Using Console
EC2 Dashboard → Select instance → Instance State → Terminate
```

### Delete Key Pair (Optional)

```bash
# Using AWS CLI
aws ec2 delete-key-pair --key-name my-first-keypair

# Delete local file
rm my-first-keypair.pem
```

---

## 🎉 Congratulations!

You've successfully:
- ✅ Created AWS account
- ✅ Secured with MFA
- ✅ Set up IAM user
- ✅ Installed AWS CLI
- ✅ Launched EC2 instance
- ✅ Deployed web application

---

## Next Steps

### Continue Learning
1. [What is AWS?](01-basics/01-what-is-aws.md) - Understand AWS fundamentals
2. [IAM Fundamentals](01-basics/03-iam-fundamentals.md) - Deep dive into security
3. [S3 Basics](01-basics/05-s3-basics.md) - Learn object storage
4. [Complete Lab 1](aws-practice/lab-01-web-app-ec2/README.md) - Build full web app

### Explore More Services
- **S3** - Store files and static websites
- **RDS** - Managed databases
- **Lambda** - Serverless functions
- **CloudWatch** - Monitoring and logs

### Get Certified
- Start with AWS Certified Cloud Practitioner
- Progress to Solutions Architect Associate

---

## 💰 Cost Management Tips

### Stay Within Free Tier
- ✅ Use t2.micro instances (750 hours/month free)
- ✅ Stay under 30 GB EBS storage
- ✅ Use S3 standard tier (5 GB free)
- ✅ Set up billing alerts

### Set Up Billing Alarm

```bash
# Create SNS topic for alerts
aws sns create-topic --name billing-alerts

# Subscribe to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:billing-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# Create billing alarm (via CloudWatch)
aws cloudwatch put-metric-alarm \
  --alarm-name billing-alarm \
  --alarm-description "Alert when charges exceed $10" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

---

## 🆘 Troubleshooting

### Can't SSH to Instance
```bash
# Check security group allows SSH from your IP
aws ec2 describe-security-groups \
  --group-ids YOUR_SECURITY_GROUP_ID

# Verify instance is running
aws ec2 describe-instance-status \
  --instance-ids YOUR_INSTANCE_ID
```

### AWS CLI Not Working
```bash
# Reconfigure
aws configure

# Check credentials
cat ~/.aws/credentials

# Test with simple command
aws sts get-caller-identity
```

### Billing Concerns
- Check AWS Cost Explorer
- Review Free Tier usage
- Set up billing alerts
- Terminate unused resources

---

## 📚 Additional Resources

- [AWS Free Tier Details](https://aws.amazon.com/free/)
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [AWS Getting Started Tutorials](https://aws.amazon.com/getting-started/)
- [AWS Training and Certification](https://aws.amazon.com/training/)

---

**Questions?** → See [FAQ](FAQ.md) or [Troubleshooting Guide](TROUBLESHOOTING.md)
