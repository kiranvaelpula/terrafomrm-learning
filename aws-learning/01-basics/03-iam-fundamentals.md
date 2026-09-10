# IAM Fundamentals: Identity and Access Management

## Introduction

AWS Identity and Access Management (IAM) is the foundation of AWS security. It controls who can access your AWS resources and what actions they can perform. Understanding IAM is critical for building secure, well-architected applications on AWS.

## 📖 Understanding IAM (Intuition First)

Picture a large office building with a security desk. IAM is that security system. It answers two questions for every single door: *who are you?* (authentication) and *are you allowed through this particular door?* (authorization). Nobody wanders freely — every person and every automated system gets a badge, and each badge only opens the doors its holder actually needs. That's the entire purpose of IAM: making sure the right identities can do exactly the right things, and nothing more.

Why does this matter? Because in the cloud, a single leaked credential with too much power can expose your whole company. If everyone in the building carried the master key, one lost key would be catastrophic. IAM exists so you can hand out narrow, specific badges instead — the intern gets into the supply closet, the finance team gets into the records room, and only a tiny few hold the master key. This is the famous **principle of least privilege**: give each identity the minimum access it needs to do its job.

The building has a few types of badge holders. **Users** are like permanent employees with their own long-term badge. **Groups** are departments — instead of programming each employee's badge one by one, you assign permissions to the "Developers" department and everyone in it inherits them. **Roles** are the clever part: they're like a temporary visitor badge you *assume* for a specific task, then hand back. An application, an EC2 server, or a person from another company can temporarily "wear" a role to get short-lived credentials — much safer than carrying a permanent key around.

**Policies** are the rulebooks that define what a badge can open. They're JSON documents that say things like "Allow reading from this specific storage bucket, but only if you used two-factor at the door, and only from the office IP address." The key mental model for how AWS decides access is simple but strict: *everything is denied by default, an explicit Allow opens the door, and an explicit Deny always wins* — even over an Allow. So a single Deny rule is an absolute veto.

Once you think of IAM as "a badge system where every identity gets the narrowest possible access, roles are temporary visitor passes, and an explicit Deny always beats an Allow," the users, groups, roles, policies, and permission boundaries in this chapter all click into place as pieces of one coherent security model.

## Table of Contents
- [What is IAM?](#what-is-iam)
- [IAM Core Components](#iam-core-components)
- [Users and User Groups](#users-and-user-groups)
- [IAM Policies](#iam-policies)
- [Roles and Temporary Credentials](#roles-and-temporary-credentials)
- [Permission Boundaries](#permission-boundaries)
- [MFA and Password Policies](#mfa-and-password-policies)
- [IAM Best Practices](#iam-best-practices)
- [Hands-on Exercises](#hands-on-exercises)

---

## What is IAM?

### Overview

IAM enables you to:
- **Control access** to AWS services and resources
- **Create and manage** users, groups, and roles
- **Define permissions** using policies
- **Enable temporary access** for applications
- **Implement security** best practices

### Key Features

```yaml
Global Service: IAM is region-independent
Free: No additional charge for IAM
Integrated: Works with all AWS services
Granular: Fine-grained access control
Identity Federation: Integrate with existing identity systems
```

### IAM vs Root Account

```
Root Account:
├── Complete unrestricted access
├── Cannot be limited by IAM policies
├── Should have MFA enabled
└── Use only for account management tasks

IAM Users:
├── Limited by assigned IAM policies
├── Can have specific permissions
├── Recommended for daily operations
└── Can be audited and monitored
```

---

## IAM Core Components

### 1. Users

Individual people or services that interact with AWS:

```bash
# Create IAM user
aws iam create-user --user-name john.doe

# Create user with tags
aws iam create-user \
  --user-name john.doe \
  --tags Key=Department,Value=Engineering Key=Role,Value=Developer
```

### 2. Groups

Collections of users with shared permissions:

```bash
# Create group
aws iam create-group --group-name Developers

# Add user to group
aws iam add-user-to-group \
  --group-name Developers \
  --user-name john.doe
```

### 3. Roles

Temporary identities for services or federated users:

```bash
# Create role for EC2
aws iam create-role \
  --role-name EC2-S3-Access-Role \
  --assume-role-policy-document file://trust-policy.json
```

### 4. Policies

JSON documents that define permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::my-bucket"
    }
  ]
}
```

---

## Users and User Groups

### Creating IAM Users

**Console Method:**
```
1. IAM Console > Users > Add users
2. Enter username
3. Select access type:
   - Programmatic access (CLI/API/SDK)
   - AWS Management Console access
4. Set permissions
5. Review and create
```

**CLI Method:**

```bash
# Create user
aws iam create-user --user-name developer1

# Create console access
aws iam create-login-profile \
  --user-name developer1 \
  --password 'TempPassword123!' \
  --password-reset-required

# Create access keys for CLI
aws iam create-access-key --user-name developer1
```

**Output Example:**
```json
{
  "AccessKey": {
    "UserName": "developer1",
    "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
    "Status": "Active",
    "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "CreateDate": "2024-01-15T10:30:00Z"
  }
}
```

### Managing User Groups

```bash
# Create groups
aws iam create-group --group-name Developers
aws iam create-group --group-name Admins
aws iam create-group --group-name ReadOnly

# List groups
aws iam list-groups

# Add users to groups
aws iam add-user-to-group --group-name Developers --user-name developer1
aws iam add-user-to-group --group-name Developers --user-name developer2

# List users in group
aws iam get-group --group-name Developers

# Remove user from group
aws iam remove-user-from-group --group-name Developers --user-name developer1
```

### Group Hierarchy Example

```
Organization
│
├── Admins Group
│   ├── Policy: AdministratorAccess
│   ├── Users: admin1, admin2
│   └── MFA Required: Yes
│
├── Developers Group
│   ├── Policy: DeveloperAccess (custom)
│   ├── Users: dev1, dev2, dev3
│   └── MFA Required: Yes
│
├── QA Group
│   ├── Policy: QAAccess (custom)
│   ├── Users: qa1, qa2
│   └── MFA Required: No
│
└── ReadOnly Group
    ├── Policy: ReadOnlyAccess
    ├── Users: auditor1, manager1
    └── MFA Required: No
```

---

## IAM Policies

### Policy Types

#### 1. AWS Managed Policies

Pre-built policies maintained by AWS:

```bash
# List managed policies
aws iam list-policies --scope AWS --max-items 10

# Common managed policies
AdministratorAccess
PowerUserAccess
ReadOnlyAccess
SecurityAudit
```

**Attach Managed Policy:**
```bash
# To user
aws iam attach-user-policy \
  --user-name developer1 \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# To group
aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess

# To role
aws iam attach-role-policy \
  --role-name MyRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

#### 2. Customer Managed Policies

Custom policies you create:

**s3-developer-policy.json:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListAllBuckets",
      "Effect": "Allow",
      "Action": "s3:ListAllMyBuckets",
      "Resource": "*"
    },
    {
      "Sid": "ReadWriteDevBucket",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::dev-bucket/*"
    },
    {
      "Sid": "ListDevBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::dev-bucket"
    }
  ]
}
```

```bash
# Create customer managed policy
aws iam create-policy \
  --policy-name S3DeveloperAccess \
  --policy-document file://s3-developer-policy.json

# Attach to group
aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::123456789012:policy/S3DeveloperAccess
```

#### 3. Inline Policies

Policies directly attached to a single user, group, or role:

```bash
# Create inline policy for user
aws iam put-user-policy \
  --user-name developer1 \
  --policy-name DynamoDBAccess \
  --policy-document file://dynamodb-policy.json

# List inline policies
aws iam list-user-policies --user-name developer1

# Delete inline policy
aws iam delete-user-policy \
  --user-name developer1 \
  --policy-name DynamoDBAccess
```

### Policy Structure

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Statement identifier (optional)",
      "Effect": "Allow or Deny",
      "Principal": "Who (for resource policies)",
      "Action": "What actions",
      "Resource": "Which resources",
      "Condition": "When (optional)"
    }
  ]
}
```

### Policy Examples

**EC2 Full Access in Specific Region:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ec2:*",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    }
  ]
}
```

**S3 Access with MFA Required:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::sensitive-bucket/*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    }
  ]
}
```

**Time-based Access:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*",
      "Condition": {
        "DateGreaterThan": {
          "aws:CurrentTime": "2024-01-01T00:00:00Z"
        },
        "DateLessThan": {
          "aws:CurrentTime": "2024-12-31T23:59:59Z"
        }
      }
    }
  ]
}
```

**IP-based Restrictions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "NotIpAddress": {
          "aws:SourceIp": [
            "192.168.1.0/24",
            "203.0.113.0/24"
          ]
        }
      }
    }
  ]
}
```

### Policy Evaluation Logic

```
1. By default, all requests are DENIED
2. Explicit ALLOW overrides default DENY
3. Explicit DENY overrides any ALLOW
4. Evaluation order:
   ├── Organization SCPs (if applicable)
   ├── Resource-based policies
   ├── IAM permissions boundaries
   ├── Session policies (temporary credentials)
   └── Identity-based policies
```

---

## Roles and Temporary Credentials

### What are IAM Roles?

Roles provide temporary security credentials:

```yaml
Use Cases:
  - EC2 instances accessing AWS services
  - Lambda functions
  - Cross-account access
  - Federation with external identity providers
  - AWS service-to-service calls
```

### Creating IAM Roles

**trust-policy.json (EC2):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

```bash
# Create role
aws iam create-role \
  --role-name EC2-S3-Access-Role \
  --assume-role-policy-document file://trust-policy.json

# Attach policy to role
aws iam attach-role-policy \
  --role-name EC2-S3-Access-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name EC2-S3-Profile

# Add role to instance profile
aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-S3-Profile \
  --role-name EC2-S3-Access-Role
```

### Cross-Account Access

**trust-policy-cross-account.json:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111111111111:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "unique-external-id"
        }
      }
    }
  ]
}
```

```bash
# Create cross-account role
aws iam create-role \
  --role-name CrossAccountRole \
  --assume-role-policy-document file://trust-policy-cross-account.json

# Assume role from another account
aws sts assume-role \
  --role-arn arn:aws:iam::222222222222:role/CrossAccountRole \
  --role-session-name session1 \
  --external-id unique-external-id
```

### Service-Linked Roles

```bash
# List service-linked roles
aws iam list-roles --query 'Roles[?contains(RoleName, `AWSServiceRole`)]'

# Create service-linked role (if required)
aws iam create-service-linked-role \
  --aws-service-name elasticbeanstalk.amazonaws.com
```

---

## Permission Boundaries

Permission boundaries set the maximum permissions an IAM entity can have:

**permission-boundary.json:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "ec2:*",
        "rds:*"
      ],
      "Resource": "*"
    }
  ]
}
```

```bash
# Create boundary policy
aws iam create-policy \
  --policy-name DeveloperBoundary \
  --policy-document file://permission-boundary.json

# Apply to user
aws iam put-user-permissions-boundary \
  --user-name developer1 \
  --permissions-boundary arn:aws:iam::123456789012:policy/DeveloperBoundary

# Verify
aws iam get-user --user-name developer1
```

**Permission Boundary Logic:**
```
Effective Permissions = Identity-based Policy ∩ Permission Boundary

Example:
- Identity Policy allows: s3:*, ec2:*, lambda:*
- Permission Boundary allows: s3:*, ec2:*
- Effective permissions: s3:*, ec2:* (lambda:* blocked)
```

---

## MFA and Password Policies

### Enable MFA for Users

```bash
# Create virtual MFA device
aws iam create-virtual-mfa-device \
  --virtual-mfa-device-name developer1-mfa \
  --outfile qr-code.png \
  --bootstrap-method QRCodePNG

# Enable MFA device
aws iam enable-mfa-device \
  --user-name developer1 \
  --serial-number arn:aws:iam::123456789012:mfa/developer1-mfa \
  --authentication-code-1 123456 \
  --authentication-code-2 789012

# List MFA devices
aws iam list-mfa-devices --user-name developer1
```

### Password Policy

```bash
# Set account password policy
aws iam update-account-password-policy \
  --minimum-password-length 14 \
  --require-symbols \
  --require-numbers \
  --require-uppercase-characters \
  --require-lowercase-characters \
  --allow-users-to-change-password \
  --max-password-age 90 \
  --password-reuse-prevention 5 \
  --hard-expiry

# Get password policy
aws iam get-account-password-policy
```

**Password Policy Example Output:**
```json
{
  "PasswordPolicy": {
    "MinimumPasswordLength": 14,
    "RequireSymbols": true,
    "RequireNumbers": true,
    "RequireUppercaseCharacters": true,
    "RequireLowercaseCharacters": true,
    "AllowUsersToChangePassword": true,
    "MaxPasswordAge": 90,
    "PasswordReusePrevention": 5,
    "HardExpiry": true
  }
}
```

---

## IAM Best Practices

### 1. Principle of Least Privilege

```bash
# BAD: Too permissive
{
  "Effect": "Allow",
  "Action": "*",
  "Resource": "*"
}

# GOOD: Specific permissions
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject"
  ],
  "Resource": "arn:aws:s3:::my-app-bucket/*"
}
```

### 2. Use Groups Instead of User Policies

```bash
# Create groups with policies
aws iam create-group --group-name Developers
aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess

# Add users to groups
aws iam add-user-to-group --group-name Developers --user-name developer1
```

### 3. Enable MFA for Privileged Users

```bash
# Policy requiring MFA for sensitive operations
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

### 4. Rotate Credentials Regularly

```bash
# List access keys
aws iam list-access-keys --user-name developer1

# Get access key last used
aws iam get-access-key-last-used --access-key-id AKIAIOSFODNN7EXAMPLE

# Rotate access key
aws iam create-access-key --user-name developer1
# Update applications with new key
aws iam delete-access-key --user-name developer1 --access-key-id OLD_KEY_ID
```

### 5. Use Roles for Applications

```bash
# Don't: Hard-code credentials in application
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."

# Do: Use IAM role for EC2
# Attach role to instance - credentials automatically provided
aws ec2 run-instances \
  --image-id ami-12345678 \
  --iam-instance-profile Name=EC2-S3-Profile
```

### 6. Monitor and Audit

```bash
# Generate credential report
aws iam generate-credential-report
aws iam get-credential-report > credential-report.csv

# List unused credentials
aws iam list-users --query 'Users[?PasswordLastUsed<`2023-01-01`]'

# Enable CloudTrail for IAM events
aws cloudtrail create-trail \
  --name iam-audit-trail \
  --s3-bucket-name iam-audit-logs
```

---

## Hands-on Exercises

### Exercise 1: User and Group Management

**Objective:** Create a complete IAM structure for a development team

**Tasks:**

```bash
# 1. Create groups
aws iam create-group --group-name Developers
aws iam create-group --group-name Admins
aws iam create-group --group-name ReadOnly

# 2. Attach policies to groups
aws iam attach-group-policy \
  --group-name Admins \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

aws iam attach-group-policy \
  --group-name ReadOnly \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# 3. Create custom policy for developers
cat > developer-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "s3:*",
        "rds:Describe*",
        "rds:List*"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name DeveloperPolicy \
  --policy-document file://developer-policy.json

aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/DeveloperPolicy

# 4. Create users
for user in alice bob charlie; do
  aws iam create-user --user-name $user
  aws iam create-login-profile \
    --user-name $user \
    --password "TempPass123!" \
    --password-reset-required
done

# 5. Assign users to groups
aws iam add-user-to-group --group-name Developers --user-name alice
aws iam add-user-to-group --group-name Developers --user-name bob
aws iam add-user-to-group --group-name Admins --user-name charlie

# 6. Verify
aws iam get-group --group-name Developers
```

### Exercise 2: Create IAM Role for EC2

**Objective:** Create a role that allows EC2 instances to access S3

**Tasks:**

```bash
# 1. Create trust policy
cat > ec2-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# 2. Create role
aws iam create-role \
  --role-name EC2-S3-FullAccess \
  --assume-role-policy-document file://ec2-trust-policy.json

# 3. Attach S3 policy
aws iam attach-role-policy \
  --role-name EC2-S3-FullAccess \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# 4. Create instance profile
aws iam create-instance-profile \
  --instance-profile-name EC2-S3-Profile

# 5. Add role to instance profile
aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-S3-Profile \
  --role-name EC2-S3-FullAccess

# 6. Verify
aws iam get-role --role-name EC2-S3-FullAccess
aws iam get-instance-profile --instance-profile-name EC2-S3-Profile
```

### Exercise 3: Policy Simulator

**Objective:** Test IAM policies before applying them

**Tasks:**

```bash
# Test if user can perform action
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/alice \
  --action-names s3:GetObject s3:PutObject ec2:RunInstances \
  --resource-arns arn:aws:s3:::my-bucket/*

# Test custom policy
aws iam simulate-custom-policy \
  --policy-input-list file://test-policy.json \
  --action-names s3:GetObject s3:PutObject \
  --resource-arns arn:aws:s3:::test-bucket/*
```

---

## Validation Checklist

- [ ] IAM users created
- [ ] User groups configured with appropriate policies
- [ ] IAM roles created for EC2 and Lambda
- [ ] Custom policies created and tested
- [ ] MFA enabled for privileged users
- [ ] Password policy configured
- [ ] Permission boundaries understood
- [ ] Cross-account roles tested
- [ ] Credential rotation process understood
- [ ] IAM best practices implemented

---

## Troubleshooting

### Access Denied Errors

```bash
# Check effective permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/developer1 \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-bucket/file.txt

# Review CloudTrail logs
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=developer1 \
  --max-results 10
```

### MFA Issues

```bash
# List MFA devices
aws iam list-mfa-devices --user-name developer1

# Deactivate MFA (if needed)
aws iam deactivate-mfa-device \
  --user-name developer1 \
  --serial-number arn:aws:iam::123456789012:mfa/developer1-mfa
```

---

## 🎯 Interview Quick Points

- IAM handles **authentication** (who you are) and **authorization** (what you can do) — it's a global, free service
- Four core building blocks: **Users, Groups, Roles, and Policies**
- **Roles provide temporary credentials** via STS — ideal for EC2, Lambda, cross-account, and federation (no hard-coded keys)
- **Policy evaluation:** deny by default → explicit Allow grants → **explicit Deny always wins**
- Always follow the **principle of least privilege** — grant only the permissions actually needed
- Prefer **attaching policies to groups**, not individual users, for easier management
- **Permission boundaries** cap the maximum permissions an identity can ever have (effective perms = policy ∩ boundary)
- Policy types: **AWS-managed, customer-managed, and inline** policies
- Use **conditions** (MFA present, source IP, time, region) to tighten access
- Use **IAM roles for applications** instead of long-lived access keys, and rotate any keys regularly
- **Never use the root account** for day-to-day work; enforce MFA on privileged users
- Audit with **credential reports, access-key-last-used, the Policy Simulator, and CloudTrail**

---

## Next Steps

Now that you understand IAM fundamentals:
1. ✓ IAM concepts mastered
2. ✓ Users, groups, and roles configured
3. ✓ Policies created and tested
4. → **Next:** Launch your first EC2 instance (Chapter 4)
5. → Work with S3 buckets using IAM roles (Chapter 5)

---

## Additional Resources

- [IAM User Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/)
- [IAM Policy Reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Policy Simulator](https://policysim.aws.amazon.com/)
