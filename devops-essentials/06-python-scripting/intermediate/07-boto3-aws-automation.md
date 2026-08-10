# boto3 — AWS Automation with Python

> **boto3 is the AWS SDK for Python — manage EC2, S3, RDS, Lambda, and all AWS services programmatically. It's the most important Python library for AWS DevOps.**

---

## 📖 What is boto3?

boto3 lets you do everything the AWS Console or CLI does, but in Python — with loops, conditionals, error handling, and complex logic.

```python
# Instead of: aws ec2 describe-instances --filters ...
# You write:  ec2.describe_instances(Filters=[...])
```

---

## 🔧 Setup

```bash
pip install boto3

# Configure credentials (one of these methods):
# 1. AWS CLI: aws configure
# 2. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
# 3. IAM Role (on EC2/Lambda — PREFERRED for production)
# 4. ~/.aws/credentials file
```

---

## 🎯 Client vs Resource

```python
import boto3

# CLIENT — Low-level API (returns dicts, matches AWS API 1:1)
ec2_client = boto3.client('ec2', region_name='us-east-1')
response = ec2_client.describe_instances()    # Returns dict

# RESOURCE — High-level API (returns objects with methods)
ec2_resource = boto3.resource('ec2', region_name='us-east-1')
instances = ec2_resource.instances.all()      # Returns objects

# When to use which:
# Client: more control, all services supported, returns raw dicts
# Resource: cleaner code, object-oriented, fewer services supported
```

---

## 🖥️ EC2 Operations

```python
import boto3

ec2 = boto3.client('ec2')

# List all running instances
response = ec2.describe_instances(
    Filters=[
        {'Name': 'instance-state-name', 'Values': ['running']},
        {'Name': 'tag:Environment', 'Values': ['production']}
    ]
)

for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        # Get the Name tag
        name = next(
            (t['Value'] for t in instance.get('Tags', []) if t['Key'] == 'Name'),
            'No Name'
        )
        print(f"  {name}: {instance['InstanceId']} ({instance['InstanceType']})")


# Start/Stop instances
ec2.stop_instances(InstanceIds=['i-1234567890abcdef0'])
ec2.start_instances(InstanceIds=['i-1234567890abcdef0'])


# PRACTICAL: Stop all dev instances (cost savings)
def stop_dev_instances():
    """Stop all running instances tagged Environment=dev."""
    ec2_resource = boto3.resource('ec2')
    
    instances = ec2_resource.instances.filter(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': 'tag:Environment', 'Values': ['dev', 'development']}
        ]
    )
    
    ids = [i.id for i in instances]
    if ids:
        ec2_resource.instances.filter(InstanceIds=ids).stop()
        print(f"Stopped {len(ids)} instances: {ids}")
    else:
        print("No dev instances running")
    
    return ids
```

---

## 📦 S3 Operations

```python
import boto3

s3 = boto3.client('s3')

# List buckets
for bucket in s3.list_buckets()['Buckets']:
    print(f"  {bucket['Name']} (created: {bucket['CreationDate']})")

# Upload file
s3.upload_file(
    Filename='backup.tar.gz',           # Local path
    Bucket='my-backup-bucket',          # S3 bucket
    Key='backups/2026/08/backup.tar.gz' # S3 path (key)
)

# Download file
s3.download_file('my-bucket', 'config/app.yml', '/tmp/app.yml')

# List objects with prefix
response = s3.list_objects_v2(Bucket='my-bucket', Prefix='logs/2026/')
for obj in response.get('Contents', []):
    print(f"  {obj['Key']} ({obj['Size']} bytes)")

# Delete old objects
def cleanup_old_backups(bucket, prefix, days=30):
    """Delete S3 objects older than N days."""
    from datetime import datetime, timezone, timedelta
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    paginator = s3.get_paginator('list_objects_v2')
    deleted = 0
    
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            if obj['LastModified'] < cutoff:
                s3.delete_object(Bucket=bucket, Key=obj['Key'])
                deleted += 1
    
    print(f"Deleted {deleted} objects older than {days} days")
```

---

## 🛡️ Error Handling with boto3

```python
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def safe_s3_upload(local_path, bucket, key):
    """Upload to S3 with proper error handling."""
    s3 = boto3.client('s3')
    
    try:
        s3.upload_file(local_path, bucket, key)
        print(f"Uploaded: s3://{bucket}/{key}")
        
    except NoCredentialsError:
        print("ERROR: AWS credentials not configured")
        print("  Run 'aws configure' or set environment variables")
        sys.exit(1)
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print(f"ERROR: Bucket '{bucket}' does not exist")
        elif error_code == 'AccessDenied':
            print(f"ERROR: Access denied to bucket '{bucket}'")
        else:
            print(f"ERROR: AWS API error: {e}")
        sys.exit(1)
        
    except FileNotFoundError:
        print(f"ERROR: Local file not found: {local_path}")
        sys.exit(1)
```

---

## 🛠️ Complete Example: AWS Resource Report

```python
#!/usr/bin/env python3
"""Generate AWS resource inventory report."""

import boto3
import json
from datetime import datetime

def get_ec2_inventory():
    """Get all EC2 instances with details."""
    ec2 = boto3.client('ec2')
    instances = []
    
    paginator = ec2.get_paginator('describe_instances')
    for page in paginator.paginate():
        for res in page['Reservations']:
            for inst in res['Instances']:
                tags = {t['Key']: t['Value'] for t in inst.get('Tags', [])}
                instances.append({
                    'id': inst['InstanceId'],
                    'name': tags.get('Name', 'unnamed'),
                    'type': inst['InstanceType'],
                    'state': inst['State']['Name'],
                    'environment': tags.get('Environment', 'unknown'),
                    'az': inst['Placement']['AvailabilityZone'],
                })
    
    return instances

def main():
    print("AWS Resource Inventory")
    print("=" * 50)
    
    instances = get_ec2_inventory()
    
    # Summary by state
    from collections import Counter
    states = Counter(i['state'] for i in instances)
    print(f"\nEC2 Instances: {len(instances)} total")
    for state, count in states.items():
        print(f"  {state}: {count}")
    
    # Running instances by environment
    running = [i for i in instances if i['state'] == 'running']
    envs = Counter(i['environment'] for i in running)
    print(f"\nRunning by Environment:")
    for env, count in envs.most_common():
        print(f"  {env}: {count}")

if __name__ == "__main__":
    main()
```

---

## 🎯 Interview Quick Points

- `boto3.client()` = low-level (returns dicts, matches AWS API)
- `boto3.resource()` = high-level (returns objects, cleaner code)
- Credentials: env vars → ~/.aws/credentials → IAM roles
- Always use Filters to narrow API calls (cost + performance)
- Use `get_paginator()` for large result sets
- Catch `ClientError` for AWS-specific errors, check `response['Error']['Code']`
- Catch `NoCredentialsError` separately for clear user messaging
- Common: EC2 stop/start, S3 upload/download/cleanup, Lambda invoke
- Resource objects support `.filter()`, `.all()`, method chaining
- `region_name` parameter or `AWS_DEFAULT_REGION` env var for region
