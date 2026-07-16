# AWS Lambda and Serverless Computing

## Introduction

AWS Lambda is a serverless compute service that lets you run code without provisioning or managing servers. You pay only for the compute time you consume, making it ideal for event-driven architectures, microservices, and applications with variable workloads.

## Table of Contents
- [What is Lambda?](#what-is-lambda)
- [Lambda Fundamentals](#lambda-fundamentals)
- [Creating Lambda Functions](#creating-lambda-functions)
- [Event Sources and Triggers](#event-sources-and-triggers)
- [IAM Roles and Permissions](#iam-roles-and-permissions)
- [Environment Variables and Configuration](#environment-variables-and-configuration)
- [Lambda Layers](#lambda-layers)
- [VPC Integration](#vpc-integration)
- [API Gateway Integration](#api-gateway-integration)
- [Error Handling and Retries](#error-handling-and-retries)
- [Performance and Optimization](#performance-and-optimization)
- [Hands-on Exercises](#hands-on-exercises)

---

## What is Lambda?

### Lambda Overview

```yaml
Serverless Compute:
  - No server management
  - Automatic scaling
  - Pay per request
  - Millisecond billing
  - Built-in high availability
  
Key Features:
  - Supports multiple languages
  - Event-driven execution
  - Stateless functions
  - 15-minute max execution
  - Concurrent execution control
  - Built-in monitoring
```

### Lambda Architecture

```
Event Sources              Lambda Function           Destinations
┌────────────┐            ┌─────────────┐          ┌──────────────┐
│  S3        │────────────│   Lambda    │──────────│  S3          │
│  Bucket    │   Event    │   Function  │  Result  │  Bucket      │
└────────────┘            │             │          └──────────────┘
┌────────────┐            │  - Runtime  │          ┌──────────────┐
│  API       │────────────│  - Handler  │──────────│  DynamoDB    │
│  Gateway   │   Request  │  - IAM Role │  Write   │  Table       │
└────────────┘            │  - Env Vars │          └──────────────┘
┌────────────┐            │  - Layers   │          ┌──────────────┐
│  EventBridge│───────────│  - VPC      │──────────│  SNS Topic   │
│  Rule      │   Schedule │             │  Notify  │              │
└────────────┘            └─────────────┘          └──────────────┘
```

### Use Cases

```yaml
Data Processing:
  - Real-time file processing
  - Stream processing
  - ETL operations
  - Image/video processing
  
Backends:
  - REST APIs
  - GraphQL APIs
  - Webhooks
  - Mobile backends
  
Automation:
  - Scheduled tasks
  - Infrastructure automation
  - Security automation
  - Backup automation
  
IoT:
  - Device data processing
  - Real-time analytics
  - Alert notifications
```

---

## Lambda Fundamentals

### Supported Runtimes

```yaml
Languages:
  - Node.js: 18.x, 20.x
  - Python: 3.9, 3.10, 3.11, 3.12
  - Java: 11, 17, 21
  - .NET: 6, 8
  - Go: 1.x
  - Ruby: 3.2, 3.3
  - Custom Runtime: Any language via runtime API
```

### Resource Limits

```yaml
Execution:
  Timeout: 1 sec - 15 minutes
  Memory: 128 MB - 10,240 MB
  Ephemeral Storage: 512 MB - 10,240 MB (/tmp)
  Environment Variables: 4 KB total
  
Deployment:
  Package Size: 50 MB (zipped), 250 MB (unzipped)
  Layers: Up to 5 layers
  Layer Size: 50 MB (zipped), 250 MB (unzipped)
  
Concurrency:
  Default: 1,000 concurrent executions per region
  Reserved: Can reserve specific capacity
  Provisioned: Pre-warmed instances
```

---

## Creating Lambda Functions

### Simple Python Function

**AWS Console:**
1. Navigate to Lambda → Create function
2. Choose "Author from scratch"
3. Function name: `hello-world-function`
4. Runtime: Python 3.12
5. Create function
6. Add code in inline editor

**Function Code:**
```python
import json

def lambda_handler(event, context):
    """
    Simple Lambda function that returns a greeting
    """
    name = event.get('name', 'World')
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': f'Hello, {name}!',
            'requestId': context.request_id
        })
    }
```

**AWS CLI:**
```bash
# Create function code
cat > lambda_function.py << 'EOF'
import json

def lambda_handler(event, context):
    name = event.get('name', 'World')
    return {
        'statusCode': 200,
        'body': json.dumps({'message': f'Hello, {name}!'})
    }
EOF

# Create deployment package
zip function.zip lambda_function.py

# Create IAM role for Lambda
aws iam create-role \
    --role-name lambda-execution-role \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }'

# Attach basic execution policy
aws iam attach-role-policy \
    --role-name lambda-execution-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create Lambda function
aws lambda create-function \
    --function-name hello-world-function \
    --runtime python3.12 \
    --role arn:aws:iam::123456789012:role/lambda-execution-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --description "Simple Hello World Lambda function" \
    --timeout 30 \
    --memory-size 128 \
    --tags Environment=Development,Application=Demo

# Invoke function
aws lambda invoke \
    --function-name hello-world-function \
    --payload '{"name": "AWS"}' \
    response.json

cat response.json
```

### Node.js Function

```javascript
//

 index.js
exports.handler = async (event) => {
    console.log('Event:', JSON.stringify(event, null, 2));
    
    const name = event.name || 'World';
    const response = {
        statusCode: 200,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: `Hello, ${name}!`,
            timestamp: new Date().toISOString()
        })
    };
    
    return response;
};
```

```bash
# Create and deploy Node.js function
cat > index.js << 'EOF'
exports.handler = async (event) => {
    const name = event.name || 'World';
    return {
        statusCode: 200,
        body: JSON.stringify({message: `Hello, ${name}!`})
    };
};
EOF

zip function.zip index.js

aws lambda create-function \
    --function-name hello-nodejs-function \
    --runtime nodejs20.x \
    --role arn:aws:iam::123456789012:role/lambda-execution-role \
    --handler index.handler \
    --zip-file fileb://function.zip
```


---

## Event Sources and Triggers

### S3 Event Trigger

**Python Function (process-image.py):**
```python
import json
import boto3
from urllib.parse import unquote_plus

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Process images uploaded to S3
    """
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        
        print(f'Processing: s3://{bucket}/{key}')
        
        # Get object metadata
        response = s3.head_object(Bucket=bucket, Key=key)
        size = response['ContentLength']
        content_type = response['ContentType']
        
        print(f'Size: {size} bytes, Type: {content_type}')
        
        # Process image (example: copy to processed folder)
        if content_type.startswith('image/'):
            new_key = f'processed/{key}'
            s3.copy_object(
                Bucket=bucket,
                CopySource={'Bucket': bucket, 'Key': key},
                Key=new_key
            )
            print(f'Copied to: {new_key}')
    
    return {'statusCode': 200, 'body': json.dumps('Processing complete')}
```

**Configure S3 Trigger:**
```bash
# Create Lambda function
zip function.zip process-image.py

aws lambda create-function \
    --function-name process-s3-images \
    --runtime python3.12 \
    --role arn:aws:iam::123456789012:role/lambda-s3-role \
    --handler process-image.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 60

# Add S3 permission to Lambda
aws lambda add-permission \
    --function-name process-s3-images \
    --statement-id s3-trigger-permission \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::my-upload-bucket

# Configure S3 event notification
aws s3api put-bucket-notification-configuration \
    --bucket my-upload-bucket \
    --notification-configuration '{
        "LambdaFunctionConfigurations": [{
            "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:process-s3-images",
            "Events": ["s3:ObjectCreated:*"],
            "Filter": {
                "Key": {
                    "FilterRules": [
                        {"Name": "prefix", "Value": "uploads/"},
                        {"Name": "suffix", "Value": ".jpg"}
                    ]
                }
            }
        }]
    }'
```

### DynamoDB Stream Trigger

```python
# process-dynamodb-stream.py
import json

def lambda_handler(event, context):
    """
    Process DynamoDB stream events
    """
    for record in event['Records']:
        event_name = record['eventName']  # INSERT, MODIFY, REMOVE
        
        if event_name == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            print(f'New item: {json.dumps(new_image)}')
        
        elif event_name == 'MODIFY':
            old_image = record['dynamodb']['OldImage']
            new_image = record['dynamodb']['NewImage']
            print(f'Modified from {old_image} to {new_image}')
        
        elif event_name == 'REMOVE':
            old_image = record['dynamodb']['OldImage']
            print(f'Deleted item: {json.dumps(old_image)}')
    
    return {'statusCode': 200}
```

```bash
# Create event source mapping
aws lambda create-event-source-mapping \
    --function-name process-dynamodb-stream \
    --event-source-arn arn:aws:dynamodb:us-east-1:123456789012:table/MyTable/stream/2026-07-16T00:00:00.000 \
    --starting-position LATEST \
    --batch-size 100
```

### SQS Trigger

```python
# process-sqs-messages.py
import json

def lambda_handler(event, context):
    """
    Process messages from SQS queue
    """
    for record in event['Records']:
        message_id = record['messageId']
        body = json.loads(record['body'])
        
        print(f'Processing message {message_id}: {body}')
        
        # Process the message
        # If processing fails, raise exception to retry
        
    return {'statusCode': 200}
```

```bash
# Create event source mapping for SQS
aws lambda create-event-source-mapping \
    --function-name process-sqs-messages \
    --event-source-arn arn:aws:sqs:us-east-1:123456789012:my-queue \
    --batch-size 10 \
    --maximum-batching-window-in-seconds 5
```

### EventBridge (CloudWatch Events) Scheduled Trigger

```python
# scheduled-backup.py
import boto3
import json
from datetime import datetime

def lambda_handler(event, context):
    """
    Run scheduled backup every day at 2 AM
    """
    print(f'Backup started at {datetime.now().isoformat()}')
    
    # Perform backup operations
    # Example: Create RDS snapshot
    rds = boto3.client('rds')
    
    snapshot_id = f"scheduled-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    response = rds.create-db-snapshot(
        DBSnapshotIdentifier=snapshot_id,
        DBInstanceIdentifier='myapp-prod-db',
        Tags=[
            {'Key': 'Type', 'Value': 'Automated'},
            {'Key': 'Date', 'Value': datetime.now().strftime('%Y-%m-%d')}
        ]
    )
    
    print(f'Snapshot created: {snapshot_id}')
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Backup completed: {snapshot_id}')
    }
```

```bash
# Create EventBridge rule for daily execution
aws events put-rule \
    --name daily-backup-rule \
    --schedule-expression "cron(0 2 * * ? *)" \
    --description "Trigger daily backup at 2 AM UTC"

# Add Lambda permission
aws lambda add-permission \
    --function-name scheduled-backup \
    --statement-id eventbridge-permission \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:us-east-1:123456789012:rule/daily-backup-rule

# Add Lambda as target
aws events put-targets \
    --rule daily-backup-rule \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:123456789012:function:scheduled-backup"
```

---

## IAM Roles and Permissions

### Basic Execution Role

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

### S3 Access Role

```bash
# Create IAM policy for S3 access
cat > lambda-s3-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket/*",
                "arn:aws:s3:::my-bucket"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
EOF

# Create policy
aws iam create-policy \
    --policy-name LambdaS3AccessPolicy \
    --policy-document file://lambda-s3-policy.json

# Attach to role
aws iam attach-role-policy \
    --role-name lambda-execution-role \
    --policy-arn arn:aws:iam::123456789012:policy/LambdaS3AccessPolicy
```

### DynamoDB Access Role

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/MyTable"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetRecords",
                "dynamodb:GetShardIterator",
                "dynamodb:DescribeStream",
                "dynamodb:ListStreams"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/MyTable/stream/*"
        }
    ]
}
```

---

## Environment Variables and Configuration

### Setting Environment Variables

```bash
# Update function with environment variables
aws lambda update-function-configuration \
    --function-name my-function \
    --environment Variables="{
        DB_HOST=mydb.cluster-abc.us-east-1.rds.amazonaws.com,
        DB_NAME=myappdb,
        DB_USER=appuser,
        API_KEY=your-api-key,
        DEBUG=false,
        REGION=us-east-1
    }"
```

### Using Environment Variables in Code

```python
# Using environment variables
import os
import boto3
import pymysql

def lambda_handler(event, context):
    # Get environment variables
    db_host = os.environ['DB_HOST']
    db_name = os.environ['DB_NAME']
    db_user = os.environ['DB_USER']
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    if debug:
        print(f'Connecting to {db_host}/{db_name}')
    
    # Get password from Secrets Manager
    secrets = boto3.client('secretsmanager')
    secret = secrets.get_secret_value(SecretId='myapp/db/password')
    db_password = secret['SecretString']
    
    # Connect to database
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    
    # Execute query
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM users")
        result = cursor.fetchone()
    
    connection.close()
    
    return {'statusCode': 200, 'body': f'User count: {result[0]}'}
```

---

## Lambda Layers

### Creating a Layer

```bash
# Create layer with external dependencies
mkdir -p python/lib/python3.12/site-packages
pip install requests -t python/lib/python3.12/site-packages/
zip -r my-layer.zip python

# Publish layer
aws lambda publish-layer-version \
    --layer-name my-dependencies-layer \
    --description "Common dependencies: requests, boto3" \
    --zip-file fileb://my-layer.zip \
    --compatible-runtimes python3.12 python3.11

# Attach layer to function
aws lambda update-function-configuration \
    --function-name my-function \
    --layers arn:aws:lambda:us-east-1:123456789012:layer:my-dependencies-layer:1
```

### Using Layers in Functions

```python
# Function using layer
import requests  # From layer
import json

def lambda_handler(event, context):
    # Use requests library from layer
    response = requests.get('https://api.example.com/data')
    
    return {
        'statusCode': 200,
        'body': json.dumps(response.json())
    }
```

---

## VPC Integration

### Lambda in VPC

```yaml
When to Use VPC:
  - Access RDS databases in private subnets
  - Access ElastiCache clusters
  - Access internal APIs
  - Access on-premises resources via VPN/Direct Connect

Considerations:
  - Cold start latency increases
  - NAT Gateway needed for internet access
  - ENI creation time
  - Concurrent execution limits
```

### Configure VPC Access

```bash
# Update function with VPC configuration
aws lambda update-function-configuration \
    --function-name my-vpc-function \
    --vpc-config SubnetIds=subnet-0123456789abcdef0,subnet-0987654321fedcba0,SecurityGroupIds=sg-0123456789abcdef0

# IAM role needs VPC permissions
aws iam attach-role-policy \
    --role-name lambda-execution-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole
```

### VPC Lambda Function Example

```python
# vpc-rds-function.py
import pymysql
import os

# Create connection outside handler for reuse
connection = None

def get_connection():
    global connection
    if connection is None or not connection.open:
        connection = pymysql.connect(
            host=os.environ['DB_HOST'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            database=os.environ['DB_NAME'],
            connect_timeout=5
        )
    return connection

def lambda_handler(event, context):
    conn = get_connection()
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s", (event['userId'],))
        result = cursor.fetchone()
    
    return {
        'statusCode': 200,
        'body': str(result)
    }
```

---

## API Gateway Integration

### Creating REST API with Lambda

```bash
# Create REST API
API_ID=$(aws apigateway create-rest-api \
    --name my-api \
    --description "My Lambda API" \
    --endpoint-configuration types=REGIONAL \
    --output text --query 'id')

# Get root resource
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --query 'items[0].id' \
    --output text)

# Create /users resource
RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part users \
    --output text --query 'id')

# Create GET method
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method GET \
    --authorization-type NONE

# Integrate with Lambda
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:my-function/invocations

# Add Lambda permission
aws lambda add-permission \
    --function-name my-function \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:123456789012:$API_ID/*/*"

# Deploy API
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod

# Get API endpoint
echo "https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/users"
```

### Lambda Function for API Gateway

```python
# api-handler.py
import json

def lambda_handler(event, context):
    """
    Handle API Gateway requests
    """
    # Parse request
    http_method = event['httpMethod']
    path = event['path']
    query_params = event.get('queryStringParameters', {})
    headers = event.get('headers', {})
    body = json.loads(event.get('body', '{}'))
    
    print(f'{http_method} {path}')
    
    # Route based on method
    if http_method == 'GET':
        return get_users(query_params)
    elif http_method == 'POST':
        return create_user(body)
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

def get_users(params):
    # Get users from database
    users = [
        {'id': 1, 'name': 'John Doe'},
        {'id': 2, 'name': 'Jane Smith'}
    ]
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(users)
    }

def create_user(data):
    # Validate and create user
    if 'name' not in data:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Name is required'})
        }
    
    # Save to database
    user = {'id': 3, 'name': data['name']}
    
    return {
        'statusCode': 201,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(user)
    }
```


---

## Error Handling and Retries

### Error Types

```yaml
Function Errors:
  - Runtime errors (exceptions)
  - Timeout errors
  - Out of memory errors
  - Permission errors
  
Invocation Errors:
  - Throttling (429)
  - Service errors (500)
  - Request too large (413)
```

### Retry Behavior

```yaml
Synchronous Invocation:
  - No automatic retry
  - Client receives error
  - Examples: API Gateway, ALB
  
Asynchronous Invocation:
  - Automatic retry (2 times)
  - Event queued for up to 6 hours
  - Examples: S3, SNS, EventBridge
  - Can configure Dead Letter Queue
  
Stream-based:
  - Retries until data expires
  - Examples: DynamoDB Streams, Kinesis
  - Can configure max retry attempts
```

### Error Handling Example

```python
# robust-handler.py
import json
import boto3
from botocore.exceptions import ClientError

sqs = boto3.client('sqs')
DLQ_URL = 'https://sqs.us-east-1.amazonaws.com/123456789012/my-dlq'

def lambda_handler(event, context):
    """
    Handle errors gracefully with retries and DLQ
    """
    try:
        # Process event
        result = process_event(event)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    
    except ValueError as e:
        # Validation error - don't retry
        print(f'Validation error: {str(e)}')
        send_to_dlq(event, str(e))
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
    
    except ClientError as e:
        # AWS service error - might be transient
        error_code = e.response['Error']['Code']
        print(f'AWS error {error_code}: {str(e)}')
        
        if error_code in ['Throttling', 'ServiceUnavailable']:
            # Transient error - raise to retry
            raise
        else:
            # Permanent error - send to DLQ
            send_to_dlq(event, str(e))
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Service error'})
            }
    
    except Exception as e:
        # Unknown error
        print(f'Unexpected error: {str(e)}')
        send_to_dlq(event, str(e))
        raise  # Raise to trigger retry

def process_event(event):
    # Simulate processing
    if 'data' not in event:
        raise ValueError('Missing required field: data')
    
    return {'processed': True}

def send_to_dlq(event, error):
    """Send failed event to Dead Letter Queue"""
    try:
        sqs.send_message(
            QueueUrl=DLQ_URL,
            MessageBody=json.dumps({
                'originalEvent': event,
                'error': error,
                'timestamp': context.get_remaining_time_in_millis()
            })
        )
    except Exception as e:
        print(f'Failed to send to DLQ: {str(e)}')
```

### Configuring Dead Letter Queue

```bash
# Create DLQ
DLQ_URL=$(aws sqs create-queue \
    --queue-name lambda-dlq \
    --output text --query 'QueueUrl')

DLQ_ARN=$(aws sqs get-queue-attributes \
    --queue-url $DLQ_URL \
    --attribute-names QueueArn \
    --output text --query 'Attributes.QueueArn')

# Configure Lambda DLQ
aws lambda update-function-configuration \
    --function-name my-function \
    --dead-letter-config TargetArn=$DLQ_ARN

# Configure retry attempts for async invocation
aws lambda put-function-event-invoke-config \
    --function-name my-function \
    --maximum-retry-attempts 1 \
    --maximum-event-age-in-seconds 3600
```

---

## Performance and Optimization

### Memory and CPU

```yaml
Memory Allocation:
  - Sets CPU proportionally
  - 128 MB = ~0.08 vCPU
  - 1,792 MB = 1 vCPU
  - 10,240 MB = ~6 vCPU
  
Optimization:
  - Test different memory settings
  - Monitor duration vs cost
  - Use Power Tuning tool
  - Higher memory = faster but more expensive
```

### Cold Start Optimization

```python
# Optimize cold starts
import boto3
import json

# Initialize outside handler (reused across invocations)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')

# Load configuration once
CONFIG = json.loads(os.environ.get('CONFIG', '{}'))

def lambda_handler(event, context):
    """
    Handler with optimized cold start
    """
    # Use pre-initialized clients
    response = table.get_item(Key={'id': event['userId']})
    
    return {
        'statusCode': 200,
        'body': json.dumps(response.get('Item'))
    }
```

### Provisioned Concurrency

```bash
# Configure provisioned concurrency (eliminates cold starts)
aws lambda put-provisioned-concurrency-config \
    --function-name my-critical-function \
    --provisioned-concurrent-executions 10 \
    --qualifier prod

# Auto-scaling for provisioned concurrency
aws application-autoscaling register-scalable-target \
    --service-namespace lambda \
    --resource-id function:my-critical-function:prod \
    --scalable-dimension lambda:function:ProvisionedConcurrentExecutions \
    --min-capacity 5 \
    --max-capacity 50

aws application-autoscaling put-scaling-policy \
    --service-namespace lambda \
    --resource-id function:my-critical-function:prod \
    --scalable-dimension lambda:function:ProvisionedConcurrentExecutions \
    --policy-name target-tracking-policy \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
        "TargetValue": 0.70,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "LambdaProvisionedConcurrencyUtilization"
        }
    }'
```

### Connection Pooling with RDS

```python
# Use RDS Proxy for connection pooling
import pymysql
import os

def lambda_handler(event, context):
    # Connect via RDS Proxy (handles connection pooling)
    connection = pymysql.connect(
        host=os.environ['RDS_PROXY_ENDPOINT'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME']
    )
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s", (event['userId'],))
        result = cursor.fetchone()
    
    connection.close()
    
    return {'statusCode': 200, 'body': str(result)}
```

---

## Hands-on Exercises

### Exercise 1: Create S3 Image Processing Pipeline

**Objective:** Build a serverless image processing pipeline

**Architecture:**
```
S3 Upload → Lambda → Resize → S3 Processed
                   ↓
                   DynamoDB (metadata)
```

**Steps:**
1. Create S3 buckets for uploads and processed images
2. Create Lambda function to resize images
3. Configure S3 trigger
4. Store metadata in DynamoDB

**Solution:**
```bash
# 1. Create S3 buckets
aws s3 mb s3://my-image-uploads
aws s3 mb s3://my-image-processed

# 2. Create DynamoDB table
aws dynamodb create-table \
    --table-name image-metadata \
    --attribute-definitions AttributeName=imageId,AttributeType=S \
    --key-schema AttributeName=imageId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

# 3. Create function (with PIL/Pillow layer)
cat > resize_image.py << 'EOF'
import boto3
import json
from PIL import Image
from io import BytesIO
from urllib.parse import unquote_plus
from datetime import datetime
import uuid

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('image-metadata')

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        
        # Download image
        response = s3.get_object(Bucket=bucket, Key=key)
        img = Image.open(BytesIO(response['Body'].read()))
        
        # Resize to thumbnail
        img.thumbnail((200, 200))
        
        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format=img.format)
        buffer.seek(0)
        
        # Upload to processed bucket
        processed_key = f"thumbnails/{key}"
        s3.put_object(
            Bucket='my-image-processed',
            Key=processed_key,
            Body=buffer,
            ContentType=response['ContentType']
        )
        
        # Save metadata
        image_id = str(uuid.uuid4())
        table.put_item(Item={
            'imageId': image_id,
            'originalKey': key,
            'processedKey': processed_key,
            'size': str(img.size),
            'format': img.format,
            'processedAt': datetime.now().isoformat()
        })
        
        print(f'Processed: {key} -> {processed_key}')
    
    return {'statusCode': 200}
EOF

# Deploy function
pip install Pillow -t .
zip -r function.zip .
aws lambda create-function \
    --function-name process-images \
    --runtime python3.12 \
    --role arn:aws:iam::123456789012:role/lambda-s3-dynamodb-role \
    --handler resize_image.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 60 \
    --memory-size 512

# 4. Configure S3 trigger (as shown earlier)
```

### Exercise 2: Build REST API with CRUD Operations

**Objective:** Create a serverless REST API for user management

**Solution:**
```python
# users-api.py
import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    
    try:
        if http_method == 'GET' and path == '/users':
            return list_users()
        
        elif http_method == 'GET' and path.startswith('/users/'):
            user_id = path.split('/')[-1]
            return get_user(user_id)
        
        elif http_method == 'POST' and path == '/users':
            body = json.loads(event['body'])
            return create_user(body)
        
        elif http_method == 'PUT' and path.startswith('/users/'):
            user_id = path.split('/')[-1]
            body = json.loads(event['body'])
            return update_user(user_id, body)
        
        elif http_method == 'DELETE' and path.startswith('/users/'):
            user_id = path.split('/')[-1]
            return delete_user(user_id)
        
        else:
            return response(404, {'error': 'Not found'})
    
    except Exception as e:
        return response(500, {'error': str(e)})

def list_users():
    result = table.scan()
    return response(200, result['Items'])

def get_user(user_id):
    result = table.get_item(Key={'userId': user_id})
    if 'Item' in result:
        return response(200, result['Item'])
    return response(404, {'error': 'User not found'})

def create_user(data):
    import uuid
    user_id = str(uuid.uuid4())
    item = {
        'userId': user_id,
        'name': data['name'],
        'email': data['email']
    }
    table.put_item(Item=item)
    return response(201, item)

def update_user(user_id, data):
    table.update_item(
        Key={'userId': user_id},
        UpdateExpression='SET #n = :name, email = :email',
        ExpressionAttributeNames={'#n': 'name'},
        ExpressionAttributeValues={
            ':name': data['name'],
            ':email': data['email']
        }
    )
    return response(200, {'userId': user_id, **data})

def delete_user(user_id):
    table.delete_item(Key={'userId': user_id})
    return response(204, {})

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body, default=str)
    }
```

### Exercise 3: Implement Event-Driven Architecture

**Objective:** Build event-driven order processing system

**Architecture:**
```
API Gateway → Lambda (Create Order) → SQS → Lambda (Process) → SNS
                                                                  ↓
                                                               Email
```

**Solution:**
```bash
# 1. Create SQS queue
QUEUE_URL=$(aws sqs create-queue \
    --queue-name order-processing-queue \
    --output text --query 'QueueUrl')

# 2. Create SNS topic
TOPIC_ARN=$(aws sns create-topic \
    --name order-notifications \
    --output text --query 'TopicArn')

# 3. Subscribe email
aws sns subscribe \
    --topic-arn $TOPIC_ARN \
    --protocol email \
    --notification-endpoint admin@example.com

# 4. Create order function
cat > create_order.py << 'EOF'
import json
import boto3
import uuid

sqs = boto3.client('sqs')
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123456789012/order-processing-queue'

def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    order = {
        'orderId': str(uuid.uuid4()),
        'items': body['items'],
        'totalAmount': body['totalAmount'],
        'customerEmail': body['customerEmail']
    }
    
    # Send to SQS for processing
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(order)
    )
    
    return {
        'statusCode': 202,
        'body': json.dumps({'orderId': order['orderId'], 'status': 'processing'})
    }
EOF

# 5. Create processing function
cat > process_order.py << 'EOF'
import json
import boto3

sns = boto3.client('sns')
TOPIC_ARN = 'arn:aws:sns:us-east-1:123456789012:order-notifications'

def lambda_handler(event, context):
    for record in event['Records']:
        order = json.loads(record['body'])
        
        # Process order (payment, inventory, etc.)
        print(f"Processing order: {order['orderId']}")
        
        # Send notification
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject=f"Order {order['orderId']} Confirmed",
            Message=f"Your order has been confirmed!\n\nOrder ID: {order['orderId']}\nTotal: ${order['totalAmount']}"
        )
    
    return {'statusCode': 200}
EOF
```

---

## Best Practices

```yaml
Development:
  - One function per task
  - Keep functions small and focused
  - Use environment variables
  - Implement proper logging
  - Use layers for dependencies
  
Performance:
  - Initialize SDK clients outside handler
  - Use provisioned concurrency for latency-sensitive apps
  - Optimize memory allocation
  - Minimize package size
  - Use connection pooling (RDS Proxy)
  
Security:
  - Principle of least privilege for IAM
  - Use Secrets Manager for credentials
  - Enable VPC when accessing private resources
  - Validate all inputs
  - Enable AWS X-Ray tracing
  
Cost Optimization:
  - Right-size memory allocation
  - Use reserved concurrency sparingly
  - Set appropriate timeouts
  - Clean up unused functions
  - Monitor and optimize cold starts
  
Monitoring:
  - Use CloudWatch Logs and Metrics
  - Enable X-Ray for distributed tracing
  - Set up alarms for errors and throttles
  - Use Lambda Insights for detailed metrics
```

---

## Summary

```yaml
Key Takeaways:
  - Lambda enables serverless compute
  - Pay only for execution time
  - Automatic scaling and HA
  - Multiple trigger sources
  - Integrate with API Gateway for REST APIs
  - Use layers for code reuse
  - VPC integration for private resources
  - Proper error handling and retries
  - Optimize for performance and cost
  
Next Steps:
  - Build serverless APIs
  - Process S3 events
  - Implement scheduled tasks
  - Create event-driven architectures
  - Explore Step Functions for workflows
```

**Related Topics:**
- Chapter 09: RDS Databases (for Lambda + RDS)
- Chapter 12: CloudWatch Monitoring
- Chapter 13: CloudFormation (for IaC)
- Chapter 17: API Gateway Advanced

---

**Resources:**
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Serverless Application Model (SAM)](https://aws.amazon.com/serverless/sam/)
- [Lambda Pricing](https://aws.amazon.com/lambda/pricing/)
