# Lab 02: Serverless API with Lambda and API Gateway

## Objective

Build a complete serverless REST API using Lambda, API Gateway, and DynamoDB.

**Duration:** 60 minutes

**Skills:**
- Lambda functions
- API Gateway
- DynamoDB
- IAM roles
- Serverless architecture

---

## Architecture

```
Client → API Gateway → Lambda → DynamoDB
```

---

## Step 1: Create DynamoDB Table

```bash
# Create table
aws dynamodb create-table \
  --table-name Users \
  --attribute-definitions \
    AttributeName=userId,AttributeType=S \
  --key-schema \
    AttributeName=userId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --tags Key=Project,Value=ServerlessAPI

# Verify
aws dynamodb describe-table --table-name Users
```

---

## Step 2: Create IAM Role for Lambda

```bash
# Trust policy
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

# Create role
aws iam create-role \
  --role-name LambdaAPIRole \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name LambdaAPIRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# DynamoDB policy
cat > dynamodb-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:Scan",
      "dynamodb:DeleteItem"
    ],
    "Resource": "arn:aws:dynamodb:us-east-1:*:table/Users"
  }]
}
EOF

aws iam put-role-policy \
  --role-name LambdaAPIRole \
  --policy-name DynamoDBAccess \
  --policy-document file://dynamodb-policy.json
```

---

## Step 3: Create Lambda Functions

**handler.py:**
```python
import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    
    try:
        if http_method == 'GET' and path == '/users':
            return get_all_users()
        elif http_method == 'GET' and path.startswith('/users/'):
            user_id = path.split('/')[-1]
            return get_user(user_id)
        elif http_method == 'POST' and path == '/users':
            return create_user(event['body'])
        elif http_method == 'DELETE' and path.startswith('/users/'):
            user_id = path.split('/')[-1]
            return delete_user(user_id)
        else:
            return response(404, {'message': 'Not found'})
    
    except Exception as e:
        return response(500, {'error': str(e)})

def get_all_users():
    result = table.scan()
    return response(200, result['Items'])

def get_user(user_id):
    result = table.get_item(Key={'userId': user_id})
    if 'Item' in result:
        return response(200, result['Item'])
    return response(404, {'message': 'User not found'})

def create_user(body):
    data = json.loads(body)
    table.put_item(Item={
        'userId': data['userId'],
        'name': data['name'],
        'email': data['email']
    })
    return response(201, {'message': 'User created'})

def delete_user(user_id):
    table.delete_item(Key={'userId': user_id})
    return response(200, {'message': 'User deleted'})

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

```bash
# Package Lambda
zip function.zip handler.py

# Create Lambda function
aws lambda create-function \
  --function-name UserAPI \
  --runtime python3.9 \
  --role arn:aws:iam::123456789012:role/LambdaAPIRole \
  --handler handler.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 256
```

---

## Step 4: Create API Gateway

```bash
# Create REST API
aws apigateway create-rest-api \
  --name "User API" \
  --description "Serverless User API"

API_ID=xxxxx

# Get root resource
ROOT_ID=$(aws apigateway get-resources \
  --rest-api-id $API_ID \
  --query 'items[0].id' \
  --output text)

# Create /users resource
aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part users

USERS_RESOURCE_ID=xxxxx

# Create /users/{userId} resource
aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $USERS_RESOURCE_ID \
  --path-part '{userId}'

USER_RESOURCE_ID=yyyyy

# Create GET method for /users
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $USERS_RESOURCE_ID \
  --http-method GET \
  --authorization-type NONE

# Integrate with Lambda
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $USERS_RESOURCE_ID \
  --http-method GET \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:UserAPI/invocations

# Add permission for API Gateway to invoke Lambda
aws lambda add-permission \
  --function-name UserAPI \
  --statement-id apigateway-access \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:123456789012:$API_ID/*/*"

# Deploy API
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod
```

---

## Step 5: Test the API

```bash
# Get API endpoint
API_ENDPOINT="https://$API_ID.execute-api.us-east-1.amazonaws.com/prod"

# Create user
curl -X POST $API_ENDPOINT/users \
  -H "Content-Type: application/json" \
  -d '{"userId":"1","name":"John Doe","email":"john@example.com"}'

# Get all users
curl $API_ENDPOINT/users

# Get specific user
curl $API_ENDPOINT/users/1

# Delete user
curl -X DELETE $API_ENDPOINT/users/1
```

---

## Bonus: Add Authentication with Cognito

```bash
# Create Cognito User Pool
aws cognito-idp create-user-pool \
  --pool-name UserAPIPool \
  --auto-verified-attributes email

# Create authorizer in API Gateway
aws apigateway create-authorizer \
  --rest-api-id $API_ID \
  --name CognitoAuth \
  --type COGNITO_USER_POOLS \
  --provider-arns arn:aws:cognito-idp:us-east-1:123456789012:userpool/us-east-1_ABC123 \
  --identity-source method.request.header.Authorization
```

---

## Cleanup

```bash
# Delete API
aws apigateway delete-rest-api --rest-api-id $API_ID

# Delete Lambda
aws lambda delete-function --function-name UserAPI

# Delete DynamoDB table
aws dynamodb delete-table --table-name Users

# Delete IAM role
aws iam detach-role-policy \
  --role-name LambdaAPIRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam delete-role-policy \
  --role-name LambdaAPIRole \
  --policy-name DynamoDBAccess

aws iam delete-role --role-name LambdaAPIRole
```

---

## Cost Estimate

- **Lambda**: First 1M requests free, then $0.20/million
- **API Gateway**: $3.50/million requests
- **DynamoDB**: Pay per request (first 25 GB free)
- **Total**: ~$1-5/month for low traffic

---

**Next Lab:** [lab-03-container-deployment](../lab-03-container-deployment/)

