# Chapter 18: EventBridge and SQS - Event-Driven Architecture

## Overview

EventBridge and SQS enable event-driven architectures, allowing loose coupling and scalable applications. EventBridge is a serverless event bus, while SQS is a managed message queue.

**What You'll Learn**
- EventBridge event buses and rules
- SQS standard vs FIFO queues
- SNS for pub/sub messaging
- Event-driven patterns
- DLQ (Dead Letter Queues)
- Message processing best practices

---

## Amazon EventBridge

### Architecture

```
Event Sources → Event Bus → Rules → Targets
    |              |          |        |
  AWS           Custom      Filter  Lambda
  SaaS          Apps       Transform  SQS
  Custom                             SNS
```

### Creating Event Bus

```bash
# Create custom event bus
aws events create-event-bus --name my-event-bus

# Put events
aws events put-events --entries file://events.json
```

**events.json:**
```json
[
  {
    "Source": "my.app",
    "DetailType": "user.signup",
    "Detail": "{\"userId\":\"123\",\"email\":\"user@example.com\"}",
    "EventBusName": "my-event-bus"
  }
]
```

### EventBridge Rules

```bash
# Create rule
aws events put-rule \
  --name UserSignupRule \
  --event-bus-name my-event-bus \
  --event-pattern '{
    "source": ["my.app"],
    "detail-type": ["user.signup"]
  }'

# Add target (Lambda)
aws events put-targets \
  --rule UserSignupRule \
  --event-bus-name my-event-bus \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:123456789012:function:process-signup"
```

### Event Patterns

**Exact Match:**
```json
{
  "source": ["my.app"],
  "detail-type": ["user.signup"]
}
```

**Prefix Match:**
```json
{
  "source": [{"prefix": "aws."}],
  "detail-type": [{"prefix": "EC2"}]
}
```

**Numeric Match:**
```json
{
  "detail": {
    "amount": [{"numeric": [">", 1000]}]
  }
}
```

---

## Amazon SQS

### Queue Types

**Standard Queue:**
- Unlimited throughput
- At-least-once delivery
- Best-effort ordering
- Use for: High throughput, order not critical

**FIFO Queue:**
- Up to 3,000 messages/sec (with batching)
- Exactly-once delivery
- Strict ordering
- Use for: Order matters, no duplicates

### Creating SQS Queue

**Standard Queue:**
```bash
aws sqs create-queue \
  --queue-name my-queue \
  --attributes '{
    "DelaySeconds": "0",
    "MessageRetentionPeriod": "345600",
    "VisibilityTimeout": "30",
    "ReceiveMessageWaitTimeSeconds": "20"
  }'
```

**FIFO Queue:**
```bash
aws sqs create-queue \
  --queue-name my-queue.fifo \
  --attributes '{
    "FifoQueue": "true",
    "ContentBasedDeduplication": "true",
    "DeduplicationScope": "messageGroup",
    "FifoThroughputLimit": "perMessageGroupId"
  }'
```

### Sending Messages

**Standard Queue:**
```python
import boto3
import json

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/my-queue'

# Send message
response = sqs.send_message(
    QueueUrl=queue_url,
    MessageBody=json.dumps({'orderId': '12345', 'amount': 99.99}),
    MessageAttributes={
        'Priority': {
            'StringValue': 'high',
            'DataType': 'String'
        }
    }
)

print(f"MessageId: {response['MessageId']}")
```

**FIFO Queue:**
```python
response = sqs.send_message(
    QueueUrl=fifo_queue_url,
    MessageBody=json.dumps({'orderId': '12345'}),
    MessageGroupId='order-processing',
    MessageDeduplicationId='unique-123'
)
```

**Batch Send:**
```python
response = sqs.send_message_batch(
    QueueUrl=queue_url,
    Entries=[
        {
            'Id': '1',
            'MessageBody': json.dumps({'order': 1})
        },
        {
            'Id': '2',
            'MessageBody': json.dumps({'order': 2})
        }
    ]
)
```

### Receiving Messages

**Long Polling (Recommended):**
```python
response = sqs.receive_message(
    QueueUrl=queue_url,
    MaxNumberOfMessages=10,
    WaitTimeSeconds=20,  # Long polling
    MessageAttributeNames=['All'],
    AttributeNames=['All']
)

for message in response.get('Messages', []):
    # Process message
    print(f"Body: {message['Body']}")
    
    # Delete message after processing
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=message['ReceiptHandle']
    )
```

### Dead Letter Queue

```bash
# Create DLQ
aws sqs create-queue --queue-name my-dlq

# Set redrive policy on main queue
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --attributes '{
    "RedrivePolicy": "{\"deadLetterTargetArn\":\"arn:aws:sqs:us-east-1:123456789012:my-dlq\",\"maxReceiveCount\":\"3\"}"
  }'
```

---

## Amazon SNS

### Topics and Subscriptions

```bash
# Create topic
aws sns create-topic --name my-topic

# Subscribe SQS queue
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:us-east-1:123456789012:my-queue

# Subscribe Lambda
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic \
  --protocol lambda \
  --notification-endpoint arn:aws:lambda:us-east-1:123456789012:function:my-function

# Subscribe Email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic \
  --protocol email \
  --notification-endpoint user@example.com
```

### Publishing Messages

```python
import boto3

sns = boto3.client('sns')

# Publish to topic
response = sns.publish(
    TopicArn='arn:aws:sns:us-east-1:123456789012:my-topic',
    Message='Hello from SNS',
    Subject='Notification',
    MessageAttributes={
        'eventType': {
            'DataType': 'String',
            'StringValue': 'user.signup'
        }
    }
)

print(f"MessageId: {response['MessageId']}")
```

### Message Filtering

```bash
# Set subscription filter policy
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:my-topic:abc-123 \
  --attribute-name FilterPolicy \
  --attribute-value '{
    "eventType": ["user.signup", "user.login"],
    "priority": [{"numeric": [">=", 5]}]
  }'
```

---

## Event-Driven Patterns

### 1. Fan-Out Pattern

```
Publisher → SNS Topic → SQS Queue 1 (Service A)
                     → SQS Queue 2 (Service B)
                     → Lambda (Service C)
```

**Implementation:**
```bash
# Create SNS topic
aws sns create-topic --name orders

# Create queues
aws sqs create-queue --queue-name inventory-queue
aws sqs create-queue --queue-name shipping-queue

# Subscribe queues to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:orders \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:us-east-1:123456789012:inventory-queue
```

### 2. Event Sourcing

```
Events → EventBridge → Lambda → DynamoDB Streams → Aggregator
```

### 3. CQRS Pattern

```
Write Path: API → Lambda → EventBridge → Write Service → DynamoDB
Read Path:  API → Lambda → Read Service → ElastiCache
```

### 4. Saga Pattern

```
Step 1 → Success → Step 2 → Success → Step 3
   |                  |                  |
  Fail → Compensate ← Fail → Compensate ← Fail
```

---

## Lambda Integration

**SQS Trigger:**
```python
def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        print(f"Processing: {body}")
        
        # Process message
        try:
            process_order(body)
        except Exception as e:
            print(f"Error: {e}")
            # Message will return to queue after visibility timeout
            raise
    
    # Successful processing deletes messages automatically
    return {'statusCode': 200}
```

**Configure Lambda trigger:**
```bash
aws lambda create-event-source-mapping \
  --function-name process-orders \
  --event-source-arn arn:aws:sqs:us-east-1:123456789012:my-queue \
  --batch-size 10 \
  --maximum-batching-window-in-seconds 5
```

**EventBridge Trigger:**
```python
def lambda_handler(event, context):
    print(f"Event: {json.dumps(event)}")
    
    source = event['source']
    detail_type = event['detail-type']
    detail = event['detail']
    
    if detail_type == 'user.signup':
        send_welcome_email(detail['email'])
    
    return {'statusCode': 200}
```

---

## Best Practices

**SQS:**
1. Use long polling (20 seconds) - Reduces empty responses and costs
2. Set appropriate visibility timeout - Should exceed processing time
3. Implement DLQ for failed messages - Capture and analyze failures
4. Use batch operations - Up to 10 messages per request
5. Delete messages after processing - Prevents reprocessing
6. Enable encryption at rest - Use KMS for sensitive data
7. Monitor queue metrics - ApproximateAgeOfOldestMessage is critical
8. Use FIFO for strict ordering - When sequence matters
9. Set message retention appropriately - Default 4 days, max 14 days
10. Implement idempotency - Handle duplicate messages gracefully

**EventBridge:**
1. Use descriptive event names - Follow naming convention (service.action)
2. Version your events - Include version in DetailType
3. Keep events small (<256 KB) - Use S3 for large payloads
4. Use event patterns for filtering - Reduce unnecessary invocations
5. Monitor failed invocations - Set up CloudWatch alarms
6. Use schema registry - Document event structures
7. Implement retry policies - Configure dead-letter queues
8. Test event patterns - Use EventBridge test event feature
9. Archive events for replay - Enable event archive
10. Use content-based filtering - Reduce costs and improve performance

**SNS:**
1. Use message filtering - Reduce unnecessary deliveries
2. Set retry policies - Customize retry behavior per protocol
3. Enable encryption - Encrypt messages at rest and in transit
4. Use FIFO topics for ordering - When message order matters
5. Monitor delivery status - Track successful/failed deliveries
6. Implement message deduplication - Prevent duplicate processing
7. Use topic policies - Control who can publish/subscribe
8. Set appropriate TTL - Message time-to-live
9. Use multiple protocols - Email, SMS, HTTP, Lambda, SQS
10. Test subscription filters - Verify filtering logic

---

## Advanced Patterns

### Event Replay with EventBridge Archive

```bash
# Create archive
aws events create-archive \
  --archive-name user-events-archive \
  --event-source-arn arn:aws:events:us-east-1:123456789012:event-bus/my-event-bus \
  --retention-days 90 \
  --event-pattern '{
    "source": ["my.app"],
    "detail-type": ["user.signup", "user.login"]
  }'

# Replay events
aws events start-replay \
  --replay-name signup-replay-2026 \
  --event-source-arn arn:aws:events:us-east-1:123456789012:archive/user-events-archive \
  --event-start-time "2026-01-01T00:00:00Z" \
  --event-end-time "2026-01-31T23:59:59Z" \
  --destination '{
    "Arn": "arn:aws:events:us-east-1:123456789012:event-bus/my-event-bus",
    "FilterArns": ["arn:aws:events:us-east-1:123456789012:rule/UserSignupRule"]
  }'
```

### SQS FIFO with Message Groups

```python
import boto3
import json
from datetime import datetime

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/orders.fifo'

# Process orders per user (message group = userId)
# Orders from same user processed in order
# Orders from different users processed in parallel

def send_order(user_id, order_data):
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(order_data),
        MessageGroupId=f'user-{user_id}',  # Orders per user are ordered
        MessageDeduplicationId=order_data['order_id']  # Prevent duplicates
    )
    return response['MessageId']

# Send orders
send_order('user-123', {'order_id': 'order-1', 'item': 'laptop', 'amount': 999})
send_order('user-123', {'order_id': 'order-2', 'item': 'mouse', 'amount': 29})
send_order('user-456', {'order_id': 'order-3', 'item': 'keyboard', 'amount': 79})

# Processing guarantees:
# - order-1 processed before order-2 (same user)
# - order-3 can be processed in parallel (different user)
```

### EventBridge Schema Registry

```bash
# Create schema registry
aws schemas create-registry \
  --registry-name my-registry \
  --description "Company event schemas"

# Create schema
aws schemas create-schema \
  --registry-name my-registry \
  --schema-name my.app.UserSignup \
  --type OpenApi3 \
  --content file://user-signup-schema.json

# Generate code bindings
aws schemas get-code-binding-source \
  --registry-name my-registry \
  --schema-name my.app.UserSignup \
  --language Python3.6
```

**user-signup-schema.json:**
```json
{
  "openapi": "3.0.0",
  "info": {
    "version": "1.0.0",
    "title": "UserSignup"
  },
  "paths": {},
  "components": {
    "schemas": {
      "UserSignup": {
        "type": "object",
        "required": ["userId", "email", "timestamp"],
        "properties": {
          "userId": {
            "type": "string",
            "description": "Unique user identifier"
          },
          "email": {
            "type": "string",
            "format": "email"
          },
          "name": {
            "type": "string"
          },
          "timestamp": {
            "type": "string",
            "format": "date-time"
          },
          "source": {
            "type": "string",
            "enum": ["web", "mobile", "api"]
          }
        }
      }
    }
  }
}
```

### SNS FIFO with SQS FIFO (Ordered Fan-Out)

```bash
# Create SNS FIFO topic
aws sns create-topic \
  --name orders.fifo \
  --attributes FifoTopic=true,ContentBasedDeduplication=true

# Create SQS FIFO queues
aws sqs create-queue \
  --queue-name inventory.fifo \
  --attributes FifoQueue=true

aws sqs create-queue \
  --queue-name shipping.fifo \
  --attributes FifoQueue=true

# Subscribe queues to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:orders.fifo \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:us-east-1:123456789012:inventory.fifo

aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:orders.fifo \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:us-east-1:123456789012:shipping.fifo
```

**Publish to FIFO topic:**
```python
import boto3

sns = boto3.client('sns')

response = sns.publish(
    TopicArn='arn:aws:sns:us-east-1:123456789012:orders.fifo',
    Message='Order placed',
    MessageGroupId='order-group-1',
    MessageDeduplicationId='unique-order-123'
)
```

### Complete Event-Driven Microservices Example

**Architecture:**
```
API Gateway → Lambda (Order Service)
                ↓
            EventBridge
                ↓
    +-----------+------------+
    ↓           ↓            ↓
Lambda      Lambda       Lambda
(Inventory) (Payment)  (Notification)
    ↓           ↓            ↓
DynamoDB    Stripe API   SES/SNS
```

**Order Service Lambda:**
```python
import boto3
import json
from datetime import datetime

events = boto3.client('events')

def lambda_handler(event, context):
    # Parse order from API Gateway
    order = json.loads(event['body'])
    
    order_id = generate_order_id()
    
    # Publish event to EventBridge
    response = events.put_events(
        Entries=[
            {
                'Source': 'order.service',
                'DetailType': 'OrderPlaced',
                'Detail': json.dumps({
                    'orderId': order_id,
                    'userId': order['userId'],
                    'items': order['items'],
                    'total': calculate_total(order['items']),
                    'timestamp': datetime.utcnow().isoformat()
                }),
                'EventBusName': 'orders-bus'
            }
        ]
    )
    
    return {
        'statusCode': 202,
        'body': json.dumps({'orderId': order_id, 'status': 'processing'})
    }
```

**Inventory Service Lambda:**
```python
import boto3
import json

dynamodb = boto3.resource('dynamodb')
events = boto3.client('events')
table = dynamodb.Table('inventory')

def lambda_handler(event, context):
    detail = event['detail']
    order_id = detail['orderId']
    items = detail['items']
    
    # Check inventory
    try:
        for item in items:
            response = table.update_item(
                Key={'sku': item['sku']},
                UpdateExpression='SET quantity = quantity - :qty',
                ConditionExpression='quantity >= :qty',
                ExpressionAttributeValues={':qty': item['quantity']},
                ReturnValues='UPDATED_NEW'
            )
        
        # Inventory reserved successfully
        events.put_events(
            Entries=[{
                'Source': 'inventory.service',
                'DetailType': 'InventoryReserved',
                'Detail': json.dumps({
                    'orderId': order_id,
                    'items': items
                }),
                'EventBusName': 'orders-bus'
            }]
        )
        
    except Exception as e:
        # Inventory insufficient
        events.put_events(
            Entries=[{
                'Source': 'inventory.service',
                'DetailType': 'InventoryFailed',
                'Detail': json.dumps({
                    'orderId': order_id,
                    'reason': str(e)
                }),
                'EventBusName': 'orders-bus'
            }]
        )
```

**EventBridge Rules:**
```bash
# Route to Inventory service
aws events put-rule \
  --name route-to-inventory \
  --event-bus-name orders-bus \
  --event-pattern '{
    "source": ["order.service"],
    "detail-type": ["OrderPlaced"]
  }'

aws events put-targets \
  --rule route-to-inventory \
  --event-bus-name orders-bus \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:123456789012:function:inventory-service"

# Route to Payment service
aws events put-rule \
  --name route-to-payment \
  --event-bus-name orders-bus \
  --event-pattern '{
    "source": ["inventory.service"],
    "detail-type": ["InventoryReserved"]
  }'

aws events put-targets \
  --rule route-to-payment \
  --event-bus-name orders-bus \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:123456789012:function:payment-service"
```

---

## Error Handling and Retries

### SQS Retry Strategy

**Exponential Backoff:**
```python
import boto3
import time
import json
from botocore.exceptions import ClientError

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1:123456789012/my-queue'

def process_with_retry(message, max_retries=3):
    receipt_handle = message['ReceiptHandle']
    body = json.loads(message['Body'])
    
    for attempt in range(max_retries):
        try:
            # Process message
            result = process_message(body)
            
            # Delete on success
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            return result
            
        except Exception as e:
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = 2 ** attempt
                print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                # Max retries exceeded, message goes to DLQ
                print(f"Max retries exceeded: {e}")
                raise

def poll_and_process():
    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20,
            AttributeNames=['ApproximateReceiveCount']
        )
        
        for message in response.get('Messages', []):
            receive_count = int(message['Attributes']['ApproximateReceiveCount'])
            
            if receive_count > 3:
                # Message has been received too many times, let it go to DLQ
                continue
            
            try:
                process_with_retry(message)
            except Exception as e:
                print(f"Failed to process message: {e}")
```

### EventBridge Retry Configuration

```python
# Lambda with retry configuration
import boto3

events = boto3.client('events')

# Put rule with retry policy
response = events.put_rule(
    Name='ProcessOrders',
    EventPattern=json.dumps({
        'source': ['order.service'],
        'detail-type': ['OrderPlaced']
    }),
    State='ENABLED'
)

# Add target with retry configuration
events.put_targets(
    Rule='ProcessOrders',
    Targets=[
        {
            'Id': '1',
            'Arn': 'arn:aws:lambda:us-east-1:123456789012:function:process-order',
            'RetryPolicy': {
                'MaximumRetryAttempts': 2,
                'MaximumEventAge': 3600  # 1 hour
            },
            'DeadLetterConfig': {
                'Arn': 'arn:aws:sqs:us-east-1:123456789012:event-dlq'
            }
        }
    ]
)
```

---

## Performance Optimization

### SQS Batch Processing

**Receive and Delete in Batches:**
```python
import boto3
import json

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/my-queue'

def batch_process():
    while True:
        # Receive up to 10 messages
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20,
            MessageAttributeNames=['All']
        )
        
        messages = response.get('Messages', [])
        if not messages:
            continue
        
        # Process all messages
        processed = []
        for message in messages:
            try:
                body = json.loads(message['Body'])
                result = process_message(body)
                processed.append({
                    'Id': message['MessageId'],
                    'ReceiptHandle': message['ReceiptHandle']
                })
            except Exception as e:
                print(f"Error processing {message['MessageId']}: {e}")
        
        # Batch delete successful messages
        if processed:
            sqs.delete_message_batch(
                QueueUrl=queue_url,
                Entries=processed
            )
```

### EventBridge Input Transformation

**Reduce Lambda payload size:**
```bash
# Only send relevant fields to Lambda
aws events put-targets \
  --rule ProcessOrders \
  --targets '{
    "Id": "1",
    "Arn": "arn:aws:lambda:us-east-1:123456789012:function:process-order",
    "InputTransformer": {
      "InputPathsMap": {
        "orderId": "$.detail.orderId",
        "userId": "$.detail.userId",
        "total": "$.detail.total"
      },
      "InputTemplate": "{\"orderId\": <orderId>, \"userId\": <userId>, \"total\": <total>}"
    }
  }'
```

---

## Cost Optimization

### SQS Cost Analysis

**Pricing (us-east-1):**
```
Standard Queue:
- First 1M requests/month: Free
- $0.40 per million requests after
- $0.09 per GB data transfer out

FIFO Queue:
- First 1M requests/month: Free
- $0.50 per million requests after
- $0.09 per GB data transfer out

Example:
10M messages/month, 1KB each:
- Standard: $3.60/month
- FIFO: $4.50/month
```

**Optimization:**
1. Use batch operations (10x cost reduction)
2. Long polling (reduce empty receives)
3. Right-size message retention
4. Delete messages promptly

### EventBridge Cost Analysis

**Pricing:**
```
- $1.00 per million events published
- Free for AWS service events
- Archive: $0.10 per GB/month
- Replay: $0.10 per GB

Example:
100M events/month:
- Publishing: $100/month
- Archive (10GB): $1/month
- Total: $101/month
```

### SNS Cost Analysis

**Pricing:**
```
Email/SMS: $0.50 per million notifications
HTTP/S: $0.60 per million notifications
SQS/Lambda: $0.00 (free)

Example:
10M notifications/month to SQS: Free
10M notifications/month to HTTP: $6/month
```

---

## Monitoring

**CloudWatch Metrics:**
```python
# SQS metrics
- ApproximateNumberOfMessagesVisible
- ApproximateAgeOfOldestMessage
- NumberOfMessagesReceived
- NumberOfMessagesDeleted

# EventBridge metrics
- Invocations
- FailedInvocations
- TriggeredRules

# SNS metrics
- NumberOfMessagesPublished
- NumberOfNotificationsDelivered
- NumberOfNotificationsFailed
```

---

## Summary

EventBridge provides event routing and filtering, SQS offers reliable message queuing, and SNS enables pub/sub messaging. Together they enable scalable, decoupled, event-driven architectures.

**Next Chapter:** [19-security-best-practices.md](./19-security-best-practices.md) - AWS Security

