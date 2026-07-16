# Amazon S3 Basics: Object Storage

## Introduction

Amazon Simple Storage Service (S3) is an object storage service that offers industry-leading scalability, data availability, security, and performance. This chapter covers everything you need to know to start using S3 for storing and retrieving any amount of data from anywhere.

## Table of Contents
- [What is Amazon S3?](#what-is-amazon-s3)
- [S3 Core Concepts](#s3-core-concepts)
- [Creating Your First Bucket](#creating-your-first-bucket)
- [Uploading and Managing Objects](#uploading-and-managing-objects)
- [S3 Storage Classes](#s3-storage-classes)
- [S3 Security and Access Control](#s3-security-and-access-control)
- [Versioning and Lifecycle](#versioning-and-lifecycle)
- [S3 CLI Operations](#s3-cli-operations)
- [Hands-on Exercises](#hands-on-exercises)

---

## What is Amazon S3?

### Overview

S3 provides:
- **Unlimited storage** - store any amount of data
- **99.999999999% (11 9's) durability**
- **99.99% availability** SLA
- **Cost-effective** - pay only for what you use
- **Global accessibility** - access from anywhere
- **Integration** with all AWS services

### Key Features

```yaml
Scalability: From 0 to exabytes
Durability: Data replicated across multiple facilities
Performance: Thousands of requests per second
Security: Encryption, access control, audit logging
Management: Lifecycle policies, versioning, replication
```

### Use Cases

```
Static Website Hosting: Host HTML, CSS, JS files
Backup and Archive: Disaster recovery
Data Lakes: Store structured/unstructured data
Content Distribution: With CloudFront CDN
Application Storage: User uploads, logs
Big Data Analytics: With Athena, EMR
Machine Learning: Training data storage
```

---

## S3 Core Concepts

### Objects and Buckets

```yaml
Bucket:
  - Container for objects
  - Globally unique name
  - Region-specific
  - Flat structure (no true folders)

Object:
  - Any file stored in S3
  - Consists of: Key, Value, Metadata
  - Size: 0 bytes to 5 TB
  - Key: Full path (my-folder/my-file.txt)
```

### Object Components

```json
{
  "Key": "documents/report-2024.pdf",
  "Value": "<binary data>",
  "VersionId": "abc123",
  "Metadata": {
    "Content-Type": "application/pdf",
    "x-amz-meta-author": "John Doe",
    "x-amz-meta-department": "Finance"
  },
  "StorageClass": "STANDARD",
  "Size": 1048576,
  "LastModified": "2024-01-15T10:30:00Z",
  "ETag": "\"d41d8cd98f00b204e9800998ecf8427e\""
}
```

### S3 URL Formats

```bash
# Path-style (legacy)
https://s3.amazonaws.com/bucket-name/object-key
https://s3.us-east-1.amazonaws.com/my-bucket/file.txt

# Virtual-hosted-style (preferred)
https://bucket-name.s3.amazonaws.com/object-key
https://my-bucket.s3.us-east-1.amazonaws.com/file.txt

# S3 URI (CLI)
s3://bucket-name/object-key
s3://my-bucket/documents/file.txt
```

---

## Creating Your First Bucket

### Bucket Naming Rules

```yaml
Requirements:
  - 3 to 63 characters
  - Lowercase letters, numbers, hyphens
  - Must start with letter or number
  - No uppercase or underscores
  - Not an IP address format
  - Globally unique across all AWS accounts

Valid: my-bucket-2024, company-data, website-assets
Invalid: MyBucket, bucket_name, 192.168.1.1, bu
```

### Create Bucket (Console)

```
1. S3 Console > Create bucket

2. Bucket name: my-first-bucket-yourname-2024

3. Region: us-east-1

4. Object Ownership: ACLs disabled (recommended)

5. Block Public Access: Keep all checked (default)

6. Versioning: Disabled (for now)

7. Encryption: Server-side encryption with Amazon S3 managed keys (SSE-S3)

8. Create bucket
```

### Create Bucket (CLI)

```bash
# Create bucket in default region
aws s3 mb s3://my-first-bucket-$(whoami)-2024

# Create bucket in specific region
aws s3 mb s3://my-bucket-us-west-2 --region us-west-2

# Create bucket with configurations
aws s3api create-bucket \
  --bucket my-configured-bucket \
  --region us-east-1 \
  --object-ownership BucketOwnerEnforced

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-configured-bucket \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket my-configured-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

### List Buckets

```bash
# List all buckets
aws s3 ls

# Using s3api for detailed info
aws s3api list-buckets

# Get bucket location
aws s3api get-bucket-location --bucket my-bucket

# Check if bucket exists
aws s3api head-bucket --bucket my-bucket && echo "Exists" || echo "Not found"
```

---

## Uploading and Managing Objects

### Upload Files

**Console Method:**
```
1. S3 Console > Select bucket
2. Click "Upload"
3. Add files or drag-and-drop
4. Set permissions (default: private)
5. Set storage class
6. Upload
```

**CLI Methods:**

```bash
# Upload single file (high-level)
aws s3 cp myfile.txt s3://my-bucket/

# Upload with custom metadata
aws s3 cp myfile.txt s3://my-bucket/ \
  --metadata author=john,department=engineering

# Upload folder recursively
aws s3 cp myfolder/ s3://my-bucket/myfolder/ --recursive

# Upload with different storage class
aws s3 cp largefile.zip s3://my-bucket/ \
  --storage-class INTELLIGENT_TIERING

# Upload using s3api (low-level)
aws s3api put-object \
  --bucket my-bucket \
  --key documents/report.pdf \
  --body report.pdf \
  --metadata '{"author":"John Doe","version":"1.0"}'
```

### Download Files

```bash
# Download single file
aws s3 cp s3://my-bucket/myfile.txt .

# Download folder recursively
aws s3 cp s3://my-bucket/myfolder/ ./local-folder/ --recursive

# Download with progress
aws s3 cp s3://my-bucket/largefile.zip . \
  --progress

# Download specific version
aws s3api get-object \
  --bucket my-bucket \
  --key myfile.txt \
  --version-id abc123 \
  myfile.txt
```

### List Objects

```bash
# List all objects in bucket
aws s3 ls s3://my-bucket/

# List objects with prefix
aws s3 ls s3://my-bucket/documents/

# List recursively
aws s3 ls s3://my-bucket/ --recursive

# List with details (size, date)
aws s3 ls s3://my-bucket/ --human-readable --summarize

# Using s3api for more control
aws s3api list-objects-v2 \
  --bucket my-bucket \
  --prefix documents/ \
  --query 'Contents[?Size > `1048576`].[Key,Size]' \
  --output table
```

### Copy, Move, Delete

```bash
# Copy within same bucket
aws s3 cp s3://my-bucket/file1.txt s3://my-bucket/backup/file1.txt

# Copy between buckets
aws s3 cp s3://source-bucket/file.txt s3://dest-bucket/file.txt

# Copy all objects matching pattern
aws s3 cp s3://my-bucket/ s3://backup-bucket/ \
  --recursive --exclude "*" --include "*.log"

# Move (copy + delete source)
aws s3 mv s3://my-bucket/old-location/file.txt s3://my-bucket/new-location/

# Sync directories
aws s3 sync ./local-folder s3://my-bucket/folder/
aws s3 sync s3://my-bucket/folder/ ./local-folder

# Delete single object
aws s3 rm s3://my-bucket/file.txt

# Delete folder
aws s3 rm s3://my-bucket/folder/ --recursive

# Delete all objects (dangerous!)
aws s3 rm s3://my-bucket/ --recursive
```

### Presigned URLs

Generate temporary URLs for private objects:

```bash
# Generate presigned URL (valid for 1 hour)
aws s3 presign s3://my-bucket/private-file.pdf \
  --expires-in 3600

# Custom expiration (7 days)
aws s3 presign s3://my-bucket/document.pdf \
  --expires-in 604800

# Use the URL
curl "<presigned-url>" -o downloaded-file.pdf
```

**Python Example:**
```python
import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')

try:
    # Generate presigned URL
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': 'my-bucket',
            'Key': 'documents/report.pdf'
        },
        ExpiresIn=3600  # 1 hour
    )
    print(f"Presigned URL: {url}")
except ClientError as e:
    print(f"Error: {e}")
```

---

## S3 Storage Classes

### Storage Class Comparison

```yaml
STANDARD:
  - Default storage class
  - 99.99% availability
  - Frequently accessed data
  - Cost: Highest storage, lowest retrieval

INTELLIGENT-TIERING:
  - Automatic cost optimization
  - Moves objects between access tiers
  - Cost: Small monitoring fee
  - Use: Unknown or changing access patterns

STANDARD-IA (Infrequent Access):
  - 99.9% availability
  - Lower storage cost
  - Retrieval fee applies
  - Use: Infrequently accessed data

ONE_ZONE-IA:
  - 99.5% availability
  - Single AZ storage
  - Lower cost than STANDARD-IA
  - Use: Recreatable infrequent data

GLACIER Instant Retrieval:
  - Archive storage
  - Millisecond retrieval
  - 90-day minimum storage
  - Use: Long-term archive with immediate access

GLACIER Flexible Retrieval:
  - Archive storage
  - Minutes to hours retrieval
  - 90-day minimum storage
  - Use: Long-term backups

GLACIER Deep Archive:
  - Lowest cost storage
  - 12-hour retrieval
  - 180-day minimum storage
  - Use: Compliance archives
```

### Setting Storage Classes

```bash
# Upload with specific storage class
aws s3 cp file.txt s3://my-bucket/ \
  --storage-class INTELLIGENT_TIERING

# Change storage class of existing object
aws s3 cp s3://my-bucket/file.txt s3://my-bucket/file.txt \
  --storage-class STANDARD_IA

# Batch change using S3 Batch Operations
aws s3api put-object \
  --bucket my-bucket \
  --key archive/old-data.zip \
  --storage-class GLACIER_IR
```

### Storage Class Transitions

```json
{
  "Rules": [
    {
      "Id": "ArchiveOldLogs",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "logs/"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER_IR"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ]
    }
  ]
}
```

---

## S3 Security and Access Control

### Bucket Policies

**Public Read Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

**Apply policy:**
```bash
aws s3api put-bucket-policy \
  --bucket my-bucket \
  --policy file://public-read-policy.json

# View policy
aws s3api get-bucket-policy --bucket my-bucket

# Delete policy
aws s3api delete-bucket-policy --bucket my-bucket
```

**Restrict to VPC:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ],
      "Condition": {
        "StringNotEquals": {
          "aws:SourceVpc": "vpc-12345678"
        }
      }
    }
  ]
}
```

**IP Restriction:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "IpAddress": {
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

### Block Public Access

```bash
# Enable all block public access settings
aws s3api put-public-access-block \
  --bucket my-bucket \
  --public-access-block-configuration \
    BlockPublicAcls=true,\
    IgnorePublicAcls=true,\
    BlockPublicPolicy=true,\
    RestrictPublicBuckets=true

# Get current settings
aws s3api get-public-access-block --bucket my-bucket
```

### Encryption

**Server-Side Encryption (SSE-S3):**
```bash
# Enable default encryption
aws s3api put-bucket-encryption \
  --bucket my-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Upload with encryption
aws s3 cp file.txt s3://my-bucket/ \
  --server-side-encryption AES256
```

**SSE-KMS (AWS Key Management Service):**
```bash
# Create KMS key
KEY_ID=$(aws kms create-key \
  --description "S3 encryption key" \
  --query 'KeyMetadata.KeyId' \
  --output text)

# Enable KMS encryption
aws s3api put-bucket-encryption \
  --bucket my-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "'$KEY_ID'"
      }
    }]
  }'
```

**Client-Side Encryption:**
```python
import boto3
from boto3.s3.transfer import TransferConfig

# Encrypt before upload
s3_client = boto3.client('s3')

# Upload encrypted file
with open('sensitive-data.txt', 'rb') as file:
    s3_client.put_object(
        Bucket='my-bucket',
        Key='encrypted-data.txt',
        Body=file,
        ServerSideEncryption='AES256'
    )
```

---

## Versioning and Lifecycle

### Enable Versioning

```bash
# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-bucket \
  --versioning-configuration Status=Enabled

# Check versioning status
aws s3api get-bucket-versioning --bucket my-bucket

# List all versions
aws s3api list-object-versions --bucket my-bucket

# Get specific version
aws s3api get-object \
  --bucket my-bucket \
  --key myfile.txt \
  --version-id abc123 \
  myfile-v1.txt

# Delete specific version
aws s3api delete-object \
  --bucket my-bucket \
  --key myfile.txt \
  --version-id abc123
```

### Lifecycle Policies

**lifecycle-policy.json:**
```json
{
  "Rules": [
    {
      "Id": "DeleteOldVersions",
      "Status": "Enabled",
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 30
      }
    },
    {
      "Id": "TransitionToIA",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "documents/"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER_IR"
        }
      ]
    },
    {
      "Id": "ExpireOldLogs",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "logs/"
      },
      "Expiration": {
        "Days": 365
      }
    }
  ]
}
```

```bash
# Apply lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-bucket \
  --lifecycle-configuration file://lifecycle-policy.json

# Get lifecycle configuration
aws s3api get-bucket-lifecycle-configuration --bucket my-bucket

# Delete lifecycle configuration
aws s3api delete-bucket-lifecycle --bucket my-bucket
```

---

## S3 CLI Operations

### Advanced S3 CLI

```bash
# Sync with delete (mirror)
aws s3 sync ./local-folder s3://my-bucket/ --delete

# Sync only newer files
aws s3 sync s3://my-bucket/ ./backup/ \
  --exclude "*" --include "2024-*"

# Copy with progress and multipart
aws s3 cp largefile.iso s3://my-bucket/ \
  --progress \
  --storage-class INTELLIGENT_TIERING

# Parallel transfers (default: 10)
aws configure set default.s3.max_concurrent_requests 20

# Multipart threshold (default: 8MB)
aws configure set default.s3.multipart_threshold 64MB

# Multipart chunk size (default: 8MB)
aws configure set default.s3.multipart_chunksize 16MB
```

### S3 Website Hosting

```bash
# Enable static website hosting
aws s3api put-bucket-website \
  --bucket my-website-bucket \
  --website-configuration '{
    "IndexDocument": {"Suffix": "index.html"},
    "ErrorDocument": {"Key": "error.html"}
  }'

# Upload website files
aws s3 sync ./website/ s3://my-website-bucket/

# Make bucket public for website
aws s3api put-bucket-policy \
  --bucket my-website-bucket \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-website-bucket/*"
    }]
  }'

# Website URL format
# http://my-website-bucket.s3-website-us-east-1.amazonaws.com
```

### S3 Event Notifications

```bash
# Configure SNS notification
aws s3api put-bucket-notification-configuration \
  --bucket my-bucket \
  --notification-configuration '{
    "TopicConfigurations": [{
      "TopicArn": "arn:aws:sns:us-east-1:123456789012:my-topic",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [{
            "Name": "prefix",
            "Value": "uploads/"
          }]
        }
      }
    }]
  }'

# Lambda function notification
aws s3api put-bucket-notification-configuration \
  --bucket my-bucket \
  --notification-configuration file://lambda-notification.json
```

---

## Hands-on Exercises

### Exercise 1: Create and Configure Bucket

**Objective:** Create a fully configured S3 bucket

```bash
#!/bin/bash

BUCKET_NAME="my-practice-bucket-$(date +%s)"

# Create bucket
aws s3 mb s3://$BUCKET_NAME

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket $BUCKET_NAME \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      },
      "BucketKeyEnabled": true
    }]
  }'

# Block public access
aws s3api put-public-access-block \
  --bucket $BUCKET_NAME \
  --public-access-block-configuration \
    BlockPublicAcls=true,\
    IgnorePublicAcls=true,\
    BlockPublicPolicy=true,\
    RestrictPublicBuckets=true

# Enable logging
aws s3api put-bucket-logging \
  --bucket $BUCKET_NAME \
  --bucket-logging-status '{
    "LoggingEnabled": {
      "TargetBucket": "'$BUCKET_NAME'",
      "TargetPrefix": "logs/"
    }
  }'

echo "Bucket created: $BUCKET_NAME"
```

### Exercise 2: Upload and Manage Files

**Objective:** Practice file operations

```bash
# Create test files
mkdir -p test-data/{documents,images,logs}
echo "Sample document" > test-data/documents/doc1.txt
echo "Another document" > test-data/documents/doc2.txt
echo "Application log" > test-data/logs/app.log

# Upload recursively
aws s3 sync test-data/ s3://my-bucket/test-data/

# List all objects
aws s3 ls s3://my-bucket/test-data/ --recursive

# Copy object
aws s3 cp s3://my-bucket/test-data/documents/doc1.txt \
  s3://my-bucket/backup/doc1-backup.txt

# Generate presigned URL
aws s3 presign s3://my-bucket/test-data/documents/doc1.txt \
  --expires-in 600

# Download object
aws s3 cp s3://my-bucket/test-data/documents/doc1.txt ./downloaded-doc1.txt

# Delete objects
aws s3 rm s3://my-bucket/test-data/ --recursive
```

### Exercise 3: Lifecycle and Storage Classes

**Objective:** Implement automated data management

```bash
# Create lifecycle policy file
cat > lifecycle.json << 'EOF'
{
  "Rules": [
    {
      "Id": "archive-old-data",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER_IR"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    }
  ]
}
EOF

# Apply lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-bucket \
  --lifecycle-configuration file://lifecycle.json

# Verify
aws s3api get-bucket-lifecycle-configuration \
  --bucket my-bucket
```

---

## Validation Checklist

- [ ] S3 bucket created with unique name
- [ ] Files uploaded successfully
- [ ] Objects downloaded
- [ ] Versioning enabled and tested
- [ ] Lifecycle policies configured
- [ ] Storage classes understood
- [ ] Bucket policy applied
- [ ] Encryption enabled
- [ ] Presigned URLs generated
- [ ] Static website hosted

---

## Next Steps

Now that you understand S3 basics:
1. ✓ Buckets created and configured
2. ✓ Objects uploaded and managed
3. ✓ Security and encryption implemented
4. → **Next:** Interview Questions (Chapter 6)
5. → Explore intermediate topics (VPC, RDS, Lambda)

---

## Additional Resources

- [S3 User Guide](https://docs.aws.amazon.com/s3/)
- [S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [S3 Pricing](https://aws.amazon.com/s3/pricing/)
- [S3 Performance Optimization](https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html)
