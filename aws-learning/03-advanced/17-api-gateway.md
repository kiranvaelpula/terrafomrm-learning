# Chapter 17: API Gateway - API Management on AWS

## Overview

Amazon API Gateway is a fully managed service for creating, publishing, maintaining, monitoring, and securing APIs at any scale.

## 📖 Understanding API Gateway (Intuition First)

Picture the front desk of a large office building. Visitors don't wander in and roam freely to find the person they need. They stop at reception, show ID, get checked against a list, are told "you can go up but only to the 3rd floor," and are directed to the right department. The receptionist also turns away troublemakers and keeps a log of everyone who came through. API Gateway is that front desk for your backend services. Every request from the outside world hits the gateway first, and only well-behaved, authorized requests get passed through to your actual code.

Why put a front desk in front of your APIs? Because your backend services (Lambda functions, containers, other AWS services) shouldn't each have to worry about who's calling, whether they're allowed, whether they're flooding you with requests, or how to log it all. Making every service reinvent authentication, rate limiting, and monitoring is wasteful and inconsistent. API Gateway centralizes all of that "front-desk" work in one managed place, so your backend can focus purely on business logic while the gateway handles the cross-cutting concerns.

The gateway's core jobs map cleanly to receptionist duties. **Authentication and authorization** check who you are and what you're allowed to do (via API keys, IAM, Cognito, or Lambda authorizers). **Throttling and rate limiting** stop any one caller from overwhelming your system — like limiting how many visitors can enter per minute so the lobby doesn't stampede. **Request/response transformation** reshapes messages so the outside world and your backend can speak comfortably. And built-in **monitoring, logging, and caching** give you visibility and speed without extra plumbing.

AWS offers a few "front desk" models for different needs. **HTTP APIs** are the streamlined, cheaper option — great for simple proxying to Lambda or HTTP backends. **REST APIs** are the full-featured version with more controls like fine-grained request validation, API keys, and usage plans — worth the higher price when you need those capabilities. **WebSocket APIs** handle persistent, two-way real-time connections, for things like chat or live dashboards where the server needs to push messages back.

One more useful idea is **stages** — you can publish the same API to separate environments like `dev`, `test`, and `prod`, each with its own settings, so you can safely test changes before customers see them. Once you picture API Gateway as "a managed front desk that authenticates, rate-limits, transforms, logs, and routes every request before it reaches your backend," choosing between HTTP/REST/WebSocket and configuring auth or throttling becomes a matter of matching the desk's features to your needs.

**What You'll Learn**
- REST API vs HTTP API vs WebSocket API
- API Gateway integrations (Lambda, HTTP, AWS services)
- Authentication and authorization
- Request/response transformation
- Throttling and rate limiting
- API stages and deployment
- Monitoring and logging

---

## API Types

### REST API vs HTTP API

| Feature | REST API | HTTP API |
|---------|----------|----------|
| **Price** | $3.50/million | $1.00/million |
| **Features** | Full-featured | Streamlined |
| **Use Case** | Complex APIs | Simple APIs |
| **Auth** | All methods | JWT, OAuth 2.0, IAM |
| **Request Validation** | Yes | No |
| **API Keys** | Yes | No |

### WebSocket API

For real-time two-way communication (chat, gaming, live updates).

---

## Creating REST API

**Using AWS CLI:**
```bash
# Create API
aws apigateway create-rest-api \
  --name "My API" \
  --description "Sample API" \
  --endpoint-configuration types=REGIONAL

# Get root resource ID
aws apigateway get-resources \
  --rest-api-id abc123

# Create resource
aws apigateway create-resource \
  --rest-api-id abc123 \
  --parent-id xyz789 \
  --path-part users

# Create GET method
aws apigateway put-method \
  --rest-api-id abc123 \
  --resource-id resource-id \
  --http-method GET \
  --authorization-type NONE

# Create Lambda integration
aws apigateway put-integration \
  --rest-api-id abc123 \
  --resource-id resource-id \
  --http-method GET \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:my-function/invocations

# Deploy API
aws apigateway create-deployment \
  --rest-api-id abc123 \
  --stage-name prod
```

---

## Lambda Integration

**Python Lambda Function:**
```python
import json

def lambda_handler(event, context):
    # API Gateway proxy integration
    print(f"Event: {json.dumps(event)}")
    
    # Extract data
    method = event['httpMethod']
    path = event['path']
    body = json.loads(event.get('body', '{}'))
    query_params = event.get('queryStringParameters', {})
    headers = event.get('headers', {})
    
    # Process request
    response_body = {
        'message': 'Hello from Lambda',
        'method': method,
        'path': path
    }
    
    # Return response
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response_body)
    }
```

**Grant API Gateway Permission:**
```bash
aws lambda add-permission \
  --function-name my-function \
  --statement-id apigateway-access \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:123456789012:abc123/*"
```

---

## Authentication

### API Keys

```bash
# Create API key
aws apigateway create-api-key \
  --name MyAPIKey \
  --enabled \
  --value "secretkey12345"

# Create usage plan
aws apigateway create-usage-plan \
  --name "Basic Plan" \
  --throttle burstLimit=100,rateLimit=50 \
  --quota limit=10000,period=MONTH

# Associate API key with usage plan
aws apigateway create-usage-plan-key \
  --usage-plan-id plan-id \
  --key-id key-id \
  --key-type API_KEY
```

### IAM Authorization

```python
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

# Sign request with IAM credentials
session = boto3.Session()
credentials = session.get_credentials()

request = AWSRequest(method='GET', url='https://abc123.execute-api.us-east-1.amazonaws.com/prod/users')
SigV4Auth(credentials, 'execute-api', 'us-east-1').add_auth(request)
```

### Cognito Authorizer

```bash
# Create authorizer
aws apigateway create-authorizer \
  --rest-api-id abc123 \
  --name CognitoAuth \
  --type COGNITO_USER_POOLS \
  --provider-arns arn:aws:cognito-idp:us-east-1:123456789012:userpool/us-east-1_ABC123 \
  --identity-source method.request.header.Authorization
```

### Lambda Authorizer

```python
def lambda_handler(event, context):
    token = event['authorizationToken']
    
    # Validate token
    if token == 'valid-token':
        return generate_policy('user', 'Allow', event['methodArn'])
    else:
        return generate_policy('user', 'Deny', event['methodArn'])

def generate_policy(principal_id, effect, resource):
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
    }
```

---

## Request/Response Transformation

**Mapping Template:**
```json
#set($inputRoot = $input.path('$'))
{
  "userId": "$inputRoot.id",
  "userName": "$inputRoot.name",
  "timestamp": "$context.requestTime"
}
```

**Request Validation:**
```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "name": { "type": "string", "minLength": 1 },
    "email": { "type": "string", "format": "email" },
    "age": { "type": "integer", "minimum": 0 }
  },
  "required": ["name", "email"]
}
```

---

## Throttling and Rate Limiting

```bash
# Set throttle settings on method
aws apigateway update-method \
  --rest-api-id abc123 \
  --resource-id xyz789 \
  --http-method GET \
  --patch-operations \
    op=replace,path=/throttle/burstLimit,value=100 \
    op=replace,path=/throttle/rateLimit,value=50
```

**Usage Plan with Quotas:**
```bash
aws apigateway create-usage-plan \
  --name "Premium Plan" \
  --api-stages apiId=abc123,stage=prod \
  --throttle burstLimit=500,rateLimit=200 \
  --quota limit=100000,period=MONTH
```

---

## CORS Configuration

```bash
# Enable CORS
aws apigateway update-integration-response \
  --rest-api-id abc123 \
  --resource-id xyz789 \
  --http-method GET \
  --status-code 200 \
  --patch-operations \
    op=add,path=/responseParameters/method.response.header.Access-Control-Allow-Origin,value="'*'"
```

---

## Monitoring

**Enable CloudWatch Logs:**
```bash
aws apigateway update-stage \
  --rest-api-id abc123 \
  --stage-name prod \
  --patch-operations \
    op=replace,path=/methodSettings/*/logging/loglevel,value=INFO \
    op=replace,path=/methodSettings/*/logging/dataTrace,value=true
```

**Key Metrics:**
- Count: Number of API calls
- Latency: Request processing time
- IntegrationLatency: Backend response time
- 4XXError: Client errors
- 5XXError: Server errors

---

## Best Practices

1. **Use HTTP API for simple use cases** (cheaper)
2. **Enable caching** to reduce backend load
3. **Implement proper authentication**
4. **Set up throttling** to protect backends
5. **Use stages** for dev/staging/prod
6. **Enable CloudWatch logging**
7. **Implement request validation**
8. **Use custom domain names**

---

## 🎯 Interview Quick Points

- **API Gateway is a managed "front desk"** — a single entry point that secures, routes, and manages API traffic
- Offloads cross-cutting concerns from backends: **auth, throttling, caching, transformation, logging**
- **HTTP API** = simpler and cheaper (~$1/M); **REST API** = full-featured (~$3.50/M); **WebSocket API** = real-time two-way
- Common integrations: **Lambda, HTTP endpoints, and direct AWS service** calls
- Auth options: **IAM, Cognito user pools, API keys/usage plans, and Lambda authorizers**
- **Throttling and rate limits** protect backends from overload and enable tiered access
- **Stages** (dev/test/prod) let you deploy and version APIs independently
- **Caching** reduces backend load and latency for repeated requests
- **Request/response mapping** transforms payloads between clients and backends
- Pairs naturally with **Lambda** to build fully serverless APIs
- Integrates with **CloudWatch and X-Ray** for monitoring and tracing
- Use **custom domains + ACM certs** and WAF for production-grade, secure APIs

## Summary

API Gateway provides fully managed API hosting with authentication, throttling, caching, and monitoring. Choose REST API for complex requirements, HTTP API for simple/cost-effective solutions, and WebSocket API for real-time communication.

**Next Chapter:** [18-eventbridge-sqs.md](./18-eventbridge-sqs.md) - Event-driven Architecture

