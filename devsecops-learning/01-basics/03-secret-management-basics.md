# Secret Management Basics

## Learning Objectives

By the end of this chapter, you will:
- Understand what secrets are and why they need protection
- Learn different types of secrets
- Know the dangers of hardcoded secrets
- Implement basic secret management
- Use environment variables and secret stores
- Understand secret rotation concepts

---

## What Are Secrets?

**Secrets** are sensitive pieces of information that should be kept confidential:

### Types of Secrets

**1. Credentials:**
- Database passwords
- API keys
- Service account passwords
- SSH keys
- TLS certificates

**2. Tokens:**
- OAuth tokens
- JWT signing keys
- Session tokens
- Personal access tokens

**3. Configuration:**
- Encryption keys
- Signing keys
- Connection strings
- Private keys

**4. Third-Party:**
- AWS access keys
- GitHub tokens
- Stripe API keys
- SendGrid credentials

---

## Why Secret Management Matters

### The Cost of Exposed Secrets

**Real-World Incidents:**

```yaml
# 2021: Codecov breach
Impact: 
  - 29,000 customers affected
  - CI/CD credentials exposed
  - Cost: Millions in remediation

# 2019: Capital One breach
Impact:
  - 100M+ customer records
  - Misconfigured IAM role
  - Cost: $80M+ in fines

# 2018: GitHub token exposure
Impact:
  - 1.5M repositories scanned
  - AWS keys found in 10% of repos
  - Automated crypto mining
```

### Consequences

1. **Financial**: Data breaches, regulatory fines
2. **Reputational**: Customer trust loss
3. **Operational**: System compromise, downtime
4. **Legal**: Compliance violations, lawsuits

---

## Common Anti-Patterns (What NOT to Do)

### ❌ Anti-Pattern 1: Hardcoded Secrets

```python
# BAD: Hardcoded in source code
import psycopg2

conn = psycopg2.connect(
    host="db.example.com",
    database="myapp",
    user="admin",
    password="SuperSecret123!"  # NEVER DO THIS!
)
```

**Why It's Bad:**
- Visible in version control history
- Accessible to anyone with code access
- Impossible to rotate without redeployment
- Violates separation of code and config

### ❌ Anti-Pattern 2: Secrets in Configuration Files

```yaml
# config.yaml - BAD
database:
  host: db.example.com
  username: admin
  password: SuperSecret123!  # Committed to git

api_keys:
  stripe: sk_live_abc123def456  # Exposed!
```

### ❌ Anti-Pattern 3: Secrets in Docker Images

```dockerfile
# Dockerfile - BAD
FROM python:3.9

# These get baked into the image!
ENV DATABASE_PASSWORD="SuperSecret123!"
ENV API_KEY="sk_live_abc123def456"

COPY app.py .
CMD ["python", "app.py"]
```

**Why It's Bad:**
- Secrets stored in image layers
- Visible with `docker history`
- Shared with image repositories
- Can't be changed without rebuild

### ❌ Anti-Pattern 4: Secrets in Logs

```python
# BAD: Logging secrets
import logging

logger = logging.getLogger(__name__)

def authenticate(username, password):
    logger.info(f"Login attempt: {username} with password {password}")  # EXPOSED!
    # ...
```

---

## Proper Secret Management

### ✅ Pattern 1: Environment Variables

**Basic approach for development:**

```python
# Good: Use environment variables
import os
import psycopg2

# Load from environment
DB_PASSWORD = os.environ.get('DATABASE_PASSWORD')

if not DB_PASSWORD:
    raise ValueError("DATABASE_PASSWORD environment variable not set")

conn = psycopg2.connect(
    host=os.environ.get('DATABASE_HOST'),
    database=os.environ.get('DATABASE_NAME'),
    user=os.environ.get('DATABASE_USER'),
    password=DB_PASSWORD
)
```

**Setting Environment Variables:**

```bash
# Linux/Mac
export DATABASE_PASSWORD="secret123"
export API_KEY="key123"

# Windows PowerShell
$env:DATABASE_PASSWORD="secret123"
$env:API_KEY="key123"

# Docker
docker run -e DATABASE_PASSWORD="secret123" myapp

# Kubernetes Secret
kubectl create secret generic db-credentials \
  --from-literal=password=secret123
```

### ✅ Pattern 2: .env Files (Development Only)

**Use for local development, NEVER commit to git:**

```bash
# .env file
DATABASE_PASSWORD=secret123
API_KEY=key123
STRIPE_KEY=sk_test_abc123
```

```python
# Load with python-dotenv
from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env file

password = os.getenv('DATABASE_PASSWORD')
```

**Important: Add to .gitignore**

```bash
# .gitignore
.env
.env.local
.env.*.local
*.secret
secrets/
```

### ✅ Pattern 3: Secret Management Services

**Production-grade secret management:**

**AWS Secrets Manager:**

```python
import boto3
import json

def get_secret(secret_name):
    """Retrieve secret from AWS Secrets Manager"""
    client = boto3.client('secretsmanager', region_name='us-east-1')
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise

# Usage
db_credentials = get_secret('prod/database/credentials')
password = db_credentials['password']
```

**HashiCorp Vault:**

```python
import hvac

# Initialize Vault client
client = hvac.Client(url='https://vault.example.com')

# Authenticate (multiple methods available)
client.auth.approle.login(
    role_id='my-role-id',
    secret_id='my-secret-id'
)

# Read secret
secret = client.secrets.kv.v2.read_secret_version(
    path='database/creds'
)

password = secret['data']['data']['password']
```

**Azure Key Vault:**

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# Authenticate
credential = DefaultAzureCredential()
vault_url = "https://myvault.vault.azure.net"
client = SecretClient(vault_url=vault_url, credential=credential)

# Retrieve secret
secret = client.get_secret("database-password")
password = secret.value
```

### ✅ Pattern 4: Kubernetes Secrets

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  # Base64 encoded values
  password: c3VwZXJzZWNyZXQxMjM=
  username: YWRtaW4=
```

```yaml
# deployment.yaml - Using secrets
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: app
        image: myapp:latest
        env:
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        # Or mount as file
        volumeMounts:
        - name: secrets
          mountPath: "/etc/secrets"
          readOnly: true
      volumes:
      - name: secrets
        secret:
          secretName: db-credentials
```

---

## Secret Rotation

**Why Rotate Secrets?**

- Limit exposure window if compromised
- Meet compliance requirements
- Reduce risk from former employees
- Best practice for security hygiene

### Manual Rotation Process

```bash
# 1. Generate new secret
NEW_PASSWORD=$(openssl rand -base64 32)

# 2. Update in secret store
aws secretsmanager update-secret \
  --secret-id prod/database/password \
  --secret-string "$NEW_PASSWORD"

# 3. Update database
psql -c "ALTER USER myapp PASSWORD '$NEW_PASSWORD';"

# 4. Restart applications (to pick up new secret)
kubectl rollout restart deployment/myapp

# 5. Verify applications are healthy
kubectl get pods -w

# 6. Deactivate old secret (after grace period)
```

### Automated Rotation

```python
# rotation_lambda.py - AWS Lambda for automatic rotation
import boto3
import psycopg2
import json

def lambda_handler(event, context):
    """Rotate database password automatically"""
    
    # Get current and new secrets
    secret_id = event['SecretId']
    token = event['ClientRequestToken']
    step = event['Step']
    
    secrets_client = boto3.client('secretsmanager')
    
    if step == 'createSecret':
        # Generate new password
        new_password = generate_secure_password()
        
        # Store as AWSPENDING
        secrets_client.put_secret_value(
            SecretId=secret_id,
            ClientRequestToken=token,
            SecretString=json.dumps({'password': new_password}),
            VersionStages=['AWSPENDING']
        )
    
    elif step == 'setSecret':
        # Update database with new password
        update_database_password(secret_id, token)
    
    elif step == 'testSecret':
        # Verify new password works
        test_database_connection(secret_id, token)
    
    elif step == 'finishSecret':
        # Move AWSCURRENT label to new version
        secrets_client.update_secret_version_stage(
            SecretId=secret_id,
            VersionStage='AWSCURRENT',
            MoveToVersionId=token
        )
```

---

## Secret Detection and Prevention

### Pre-commit Hooks

**Prevent secrets from being committed:**

```bash
# Install git-secrets
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets && sudo make install

# Initialize in repository
cd /path/to/your/repo
git secrets --install

# Add patterns
git secrets --register-aws  # AWS patterns
git secrets --add 'password\s*=\s*.+'  # Generic passwords
git secrets --add 'api[_-]?key\s*=\s*.+'  # API keys

# Scan repository
git secrets --scan-history
```

### TruffleHog

**Scan for secrets in git history:**

```bash
# Install
pip install trufflehog

# Scan repository
trufflehog git https://github.com/yourorg/yourrepo

# Scan with JSON output
trufflehog git file://. --json | jq

# Scan only recent commits
trufflehog git file://. --since-commit HEAD~10
```

### GitHub Secret Scanning

**Enable in repository settings:**

```yaml
# .github/workflows/secret-scan.yml
name: Secret Scanning

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: TruffleHog scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
```

---

## Best Practices

### 1. Never Commit Secrets

✅ Use .gitignore
✅ Enable pre-commit hooks
✅ Use secret scanning tools
✅ Educate team members

### 2. Principle of Least Privilege

```yaml
# Good: Separate secrets per environment
Development:
  DATABASE_PASSWORD: dev_password_123
  API_KEY: sk_test_abc123

Production:
  DATABASE_PASSWORD: prod_complex_password_456
  API_KEY: sk_live_xyz789

# Different teams have access to different environments
```

### 3. Encrypt at Rest

- Use encrypted secret stores
- Enable encryption for databases
- Use encrypted volumes

### 4. Use Short-Lived Credentials

```python
# Generate temporary credentials (AWS STS)
import boto3

sts = boto3.client('sts')

# Assume role for temporary credentials
response = sts.assume_role(
    RoleArn='arn:aws:iam::123456789012:role/MyRole',
    RoleSessionName='MySession',
    DurationSeconds=3600  # 1 hour
)

# Use temporary credentials
temp_credentials = response['Credentials']
# These expire automatically!
```

### 5. Audit Secret Access

```python
# Log secret access
import logging

logger = logging.getLogger(__name__)

def get_secret(secret_name, user):
    """Get secret with audit logging"""
    logger.info(f"Secret '{secret_name}' accessed by {user}")
    # Retrieve secret...
    return secret_value
```

### 6. Implement Secret Rotation

- Rotate secrets regularly (30-90 days)
- Automate rotation process
- Test rotation in non-prod first
- Have rollback plan

---

## Hands-On Exercise

**Task**: Secure an application with proper secret management

**Starting Point (Insecure):**

```python
# app.py - INSECURE
import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="db.example.com",
        database="myapp",
        user="admin",
        password="hardcoded_password_123"  # BAD!
    )

api_key = "sk_live_abc123def456"  # BAD!

def call_api():
    import requests
    headers = {"Authorization": f"Bearer {api_key}"}
    return requests.get("https://api.example.com/data", headers=headers)
```

**Your Task:**

1. Move secrets to environment variables
2. Add validation for missing secrets
3. Implement graceful error handling
4. Add .env file for local development
5. Create Kubernetes secret manifest
6. Add secret scanning to CI/CD

**Solution:**

```python
# app.py - SECURE
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_env_variable(var_name):
    """Get environment variable or raise error"""
    value = os.environ.get(var_name)
    if not value:
        print(f"ERROR: {var_name} environment variable not set", file=sys.stderr)
        sys.exit(1)
    return value

def get_db_connection():
    """Get database connection using environment variables"""
    try:
        return psycopg2.connect(
            host=get_env_variable('DATABASE_HOST'),
            database=get_env_variable('DATABASE_NAME'),
            user=get_env_variable('DATABASE_USER'),
            password=get_env_variable('DATABASE_PASSWORD')
        )
    except Exception as e:
        print(f"Database connection failed: {e}", file=sys.stderr)
        raise

def call_api():
    """Call API using secret from environment"""
    import requests
    
    api_key = get_env_variable('API_KEY')
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(
            "https://api.example.com/data",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API call failed: {e}", file=sys.stderr)
        raise
```

```bash
# .env.example (commit this template)
DATABASE_HOST=localhost
DATABASE_NAME=myapp
DATABASE_USER=user
DATABASE_PASSWORD=change_me
API_KEY=your_api_key_here
```

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  DATABASE_PASSWORD: "actual_secure_password"
  API_KEY: "actual_api_key"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: app
        image: myapp:latest
        envFrom:
        - secretRef:
            name: app-secrets
```

---

## Summary

Key takeaways:
- ✅ Never hardcode secrets in source code
- ✅ Use environment variables or secret stores
- ✅ Implement secret rotation
- ✅ Enable secret scanning
- ✅ Follow least privilege principle
- ✅ Audit secret access
- ✅ Encrypt secrets at rest

**Next**: [Security Testing Fundamentals →](04-security-testing-fundamentals.md)
