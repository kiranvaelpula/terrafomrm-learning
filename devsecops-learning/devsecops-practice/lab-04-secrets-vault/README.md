# Lab 4: Secrets Management with HashiCorp Vault

## Objectives

By completing this lab, you will:
- Install and configure HashiCorp Vault
- Store and retrieve secrets securely
- Implement dynamic database credentials
- Configure automatic secret rotation
- Integrate Vault with applications
- Implement AppRole authentication

**Duration**: 2 hours

---

## Prerequisites

- Docker installed
- Basic understanding of secrets management
- Completed Lab 3

---

## Part 1: Vault Installation and Setup

### Install Vault


```bash
# Using Docker
docker run -d \
  --name vault \
  --cap-add=IPC_LOCK \
  -p 8200:8200 \
  -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' \
  -e 'VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200' \
  vault:latest

# Or install locally (Linux)
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install vault

# Verify installation
vault --version

# Set environment variables
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='myroot'

# Check status
vault status
```

### Initialize Vault (Production Setup)

```bash
# Initialize Vault
vault operator init -key-shares=5 -key-threshold=3

# Output (save these securely!):
# Unseal Key 1: abc123...
# Unseal Key 2: def456...
# Unseal Key 3: ghi789...
# Unseal Key 4: jkl012...
# Unseal Key 5: mno345...
# Initial Root Token: s.xyz789...

# Unseal Vault (need 3 keys)
vault operator unseal  # Enter key 1
vault operator unseal  # Enter key 2
vault operator unseal  # Enter key 3

# Login
vault login
# Token: s.xyz789...
```

---

## Part 2: Basic Secret Management

### Key-Value Secrets (v2)

```bash
# Enable KV secrets engine
vault secrets enable -version=2 kv

# Write a secret
vault kv put kv/myapp/config \
  db_password="supersecret123" \
  api_key="sk_live_abc123" \
  max_connections="100"

# Read secret
vault kv get kv/myapp/config

# Read specific field
vault kv get -field=db_password kv/myapp/config

# Read as JSON
vault kv get -format=json kv/myapp/config | jq

# List secrets
vault kv list kv/myapp

# Delete secret
vault kv delete kv/myapp/config

# Undelete (restore)
vault kv undelete -versions=1 kv/myapp/config

# Permanently destroy
vault kv destroy -versions=1 kv/myapp/config
```

### Secret Versioning

```bash
# Write version 1
vault kv put kv/myapp/db password="oldpassword"

# Write version 2
vault kv put kv/myapp/db password="newpassword"

# Write version 3
vault kv put kv/myapp/db password="newerpassword"

# Read latest version
vault kv get kv/myapp/db

# Read specific version
vault kv get -version=1 kv/myapp/db

# Get version history
vault kv metadata get kv/myapp/db

# Rollback to previous version
vault kv rollback -version=2 kv/myapp/db
```

---

## Part 3: Application Integration

### Python Integration

**Install Python library:**

```bash
pip install hvac
```

**app.py:**

```python
import hvac
import os

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=os.environ.get('VAULT_ADDR', 'http://localhost:8200'),
            token=os.environ.get('VAULT_TOKEN')
        )
        
        if not self.client.is_authenticated():
            raise Exception("Vault authentication failed")
    
    def get_secret(self, path, key=None):
        """Retrieve secret from Vault"""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point='kv'
            )
            
            data = response['data']['data']
            
            if key:
                return data.get(key)
            return data
        
        except Exception as e:
            print(f"Error reading secret: {e}")
            raise
    
    def write_secret(self, path, **secrets):
        """Write secret to Vault"""
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secrets,
                mount_point='kv'
            )
            print(f"Secret written to {path}")
        except Exception as e:
            print(f"Error writing secret: {e}")
            raise
    
    def delete_secret(self, path):
        """Delete secret from Vault"""
        try:
            self.client.secrets.kv.v2.delete_latest_version_of_secret(
                path=path,
                mount_point='kv'
            )
            print(f"Secret deleted from {path}")
        except Exception as e:
            print(f"Error deleting secret: {e}")
            raise

# Usage example
if __name__ == "__main__":
    vault = VaultClient()
    
    # Write secrets
    vault.write_secret(
        'myapp/config',
        db_password='supersecret123',
        api_key='sk_live_abc123'
    )
    
    # Read all secrets
    config = vault.get_secret('myapp/config')
    print(f"Config: {config}")
    
    # Read specific field
    db_pass = vault.get_secret('myapp/config', 'db_password')
    print(f"DB Password: {db_pass}")
```

### Database Connection with Vault

```python
import psycopg2
from vault_client import VaultClient

def get_db_connection():
    """Get database connection using Vault secrets"""
    vault = VaultClient()
    
    # Retrieve database credentials
    db_config = vault.get_secret('myapp/database')
    
    conn = psycopg2.connect(
        host=db_config['host'],
        database=db_config['database'],
        user=db_config['username'],
        password=db_config['password'],
        port=db_config.get('port', 5432)
    )
    
    return conn

# Usage
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print(cursor.fetchone())
    conn.close()
except Exception as e:
    print(f"Database connection failed: {e}")
```

---

## Part 4: Dynamic Database Credentials

### Setup PostgreSQL Database Engine

```bash
# Enable database secrets engine
vault secrets enable database

# Configure PostgreSQL connection
vault write database/config/mydb \
  plugin_name=postgresql-database-plugin \
  allowed_roles="readonly,readwrite" \
  connection_url="postgresql://{{username}}:{{password}}@postgres:5432/myapp?sslmode=disable" \
  username="vault" \
  password="vaultpassword"

# Rotate root credentials (best practice)
vault write -force database/rotate-root/mydb
```

### Create Database Roles

```bash
# Readonly role
vault write database/roles/readonly \
  db_name=mydb \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# Readwrite role
vault write database/roles/readwrite \
  db_name=mydb \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"
```

### Generate Dynamic Credentials

```bash
# Generate readonly credentials (valid for 1 hour)
vault read database/creds/readonly

# Output:
# Key                Value
# ---                -----
# lease_id           database/creds/readonly/abc123
# lease_duration     1h
# lease_renewable    true
# password           A1a-xyz789
# username           v-token-readonly-abc123

# Use these credentials to connect to database
psql -h localhost -U v-token-readonly-abc123 -d myapp
```

### Python Integration for Dynamic Credentials

```python
import hvac
import psycopg2
import time
from threading import Thread

class DynamicDatabaseConnection:
    def __init__(self, vault_client, role_name):
        self.vault = vault_client
        self.role_name = role_name
        self.credentials = None
        self.connection = None
        self.lease_id = None
        self._renew_thread = None
        
        self._get_credentials()
        self._start_renewal()
    
    def _get_credentials(self):
        """Get dynamic database credentials"""
        response = self.vault.client.read(
            f'database/creds/{self.role_name}'
        )
        
        self.credentials = response['data']
        self.lease_id = response['lease_id']
        self.lease_duration = response['lease_duration']
        
        print(f"Got credentials: {self.credentials['username']}")
    
    def _start_renewal(self):
        """Start background thread to renew lease"""
        def renew_lease():
            while True:
                # Renew at 50% of lease duration
                sleep_time = self.lease_duration // 2
                time.sleep(sleep_time)
                
                try:
                    self.vault.client.sys.renew_lease(self.lease_id)
                    print(f"Renewed lease {self.lease_id}")
                except Exception as e:
                    print(f"Failed to renew lease: {e}")
                    # Get new credentials
                    self._get_credentials()
                    self._reconnect()
        
        self._renew_thread = Thread(target=renew_lease, daemon=True)
        self._renew_thread.start()
    
    def get_connection(self):
        """Get database connection"""
        if not self.connection or self.connection.closed:
            self.connection = psycopg2.connect(
                host='localhost',
                database='myapp',
                user=self.credentials['username'],
                password=self.credentials['password']
            )
        return self.connection
    
    def _reconnect(self):
        """Reconnect with new credentials"""
        if self.connection and not self.connection.closed:
            self.connection.close()
        self.get_connection()
    
    def revoke(self):
        """Revoke the lease"""
        try:
            self.vault.client.sys.revoke_lease(self.lease_id)
            print(f"Revoked lease {self.lease_id}")
        except Exception as e:
            print(f"Failed to revoke lease: {e}")

# Usage
vault_client = VaultClient()
db = DynamicDatabaseConnection(vault_client, 'readonly')

conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM users LIMIT 10")
print(cursor.fetchall())

# Automatically renewed in background
time.sleep(3600)  # Credentials still valid

# Revoke when done
db.revoke()
```

---

## Part 5: AppRole Authentication

### Setup AppRole

```bash
# Enable AppRole auth method
vault auth enable approle

# Create policy for application
vault policy write myapp-policy - <<EOF
path "kv/data/myapp/*" {
  capabilities = ["read", "list"]
}

path "database/creds/readonly" {
  capabilities = ["read"]
}
EOF

# Create AppRole
vault write auth/approle/role/myapp \
  token_policies="myapp-policy" \
  token_ttl=1h \
  token_max_ttl=4h \
  secret_id_ttl=24h

# Get RoleID (can be public)
vault read auth/approle/role/myapp/role-id

# Generate SecretID (keep private)
vault write -f auth/approle/role/myapp/secret-id
```

### Application Authentication

```python
import hvac
import os

class VaultAppRoleClient:
    def __init__(self, role_id, secret_id):
        self.client = hvac.Client(
            url=os.environ.get('VAULT_ADDR', 'http://localhost:8200')
        )
        
        # Authenticate using AppRole
        response = self.client.auth.approle.login(
            role_id=role_id,
            secret_id=secret_id
        )
        
        # Token is automatically set
        self.token = response['auth']['client_token']
        print(f"Authenticated with token: {self.token[:10]}...")
    
    def get_secret(self, path):
        """Retrieve secret"""
        response = self.client.secrets.kv.v2.read_secret_version(
            path=path,
            mount_point='kv'
        )
        return response['data']['data']

# Usage
role_id = os.environ.get('VAULT_ROLE_ID')
secret_id = os.environ.get('VAULT_SECRET_ID')

vault = VaultAppRoleClient(role_id, secret_id)
config = vault.get_secret('myapp/config')
print(config)
```

---

## Part 6: Secret Rotation

### Manual Rotation

```bash
# Rotate database root credentials
vault write -force database/rotate-root/mydb

# Rotate static credentials
vault write kv/data/myapp/api \
  api_key="new_rotated_key_xyz789"
```

### Automated Rotation Script

```python
import hvac
import schedule
import time
import secrets
import string

class SecretRotator:
    def __init__(self, vault_client):
        self.vault = vault_client
    
    def generate_password(self, length=32):
        """Generate secure random password"""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def rotate_database_password(self, path):
        """Rotate database password"""
        new_password = self.generate_password()
        
        # 1. Update in Vault
        self.vault.write_secret(
            path,
            password=new_password
        )
        
        # 2. Update actual database
        # (implementation depends on database)
        
        print(f"Rotated password at {path}")
    
    def rotate_api_key(self, path, api_provider):
        """Rotate API key"""
        # 1. Generate new key with API provider
        new_key = api_provider.create_new_key()
        
        # 2. Update in Vault
        self.vault.write_secret(
            path,
            api_key=new_key
        )
        
        # 3. Wait for propagation
        time.sleep(60)
        
        # 4. Revoke old key
        old_key = self.vault.get_secret(path, 'api_key')
        api_provider.revoke_key(old_key)
        
        print(f"Rotated API key at {path}")

# Schedule rotation
rotator = SecretRotator(vault_client)

# Rotate daily at 2 AM
schedule.every().day.at("02:00").do(
    rotator.rotate_database_password,
    'myapp/database'
)

# Rotate API keys weekly
schedule.every().sunday.at("03:00").do(
    rotator.rotate_api_key,
    'myapp/api',
    api_provider
)

while True:
    schedule.run_pending()
    time.sleep(3600)
```

---

## Part 7: CI/CD Integration

### GitHub Actions with Vault

```yaml
# .github/workflows/deploy.yml
name: Deploy with Vault Secrets

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Import Secrets from Vault
        uses: hashicorp/vault-action@v2
        with:
          url: https://vault.example.com
          method: approle
          roleId: ${{ secrets.VAULT_ROLE_ID }}
          secretId: ${{ secrets.VAULT_SECRET_ID }}
          secrets: |
            kv/data/myapp/prod database_password | DATABASE_PASSWORD ;
            kv/data/myapp/prod api_key | API_KEY ;
            database/creds/readonly username | DB_USER ;
            database/creds/readonly password | DB_PASS
      
      - name: Deploy Application
        run: |
          echo "DATABASE_PASSWORD=${{ env.DATABASE_PASSWORD }}" >> .env
          echo "API_KEY=${{ env.API_KEY }}" >> .env
          ./deploy.sh
```

### Kubernetes Integration

```yaml
# vault-secrets-operator.yaml
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultAuth
metadata:
  name: vault-auth
  namespace: default
spec:
  method: kubernetes
  mount: kubernetes
  kubernetes:
    role: myapp
    serviceAccount: myapp
---
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultStaticSecret
metadata:
  name: myapp-secrets
  namespace: default
spec:
  vaultAuthRef: vault-auth
  mount: kv
  path: myapp/config
  refreshAfter: 1h
  destination:
    create: true
    name: myapp-secrets
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      serviceAccountName: myapp
      containers:
      - name: app
        image: myapp:latest
        envFrom:
        - secretRef:
            name: myapp-secrets
```

---

## Exercises

### Exercise 1: Build Complete Vault Integration

Create an application that:
1. Authenticates using AppRole
2. Retrieves database credentials
3. Connects to database with dynamic credentials
4. Automatically renews credentials
5. Revokes credentials on shutdown

### Exercise 2: Implement Secret Rotation

Build a rotation system that:
1. Rotates secrets every 30 days
2. Sends notifications before rotation
3. Maintains 24-hour overlap for zero-downtime
4. Logs all rotation events
5. Has rollback capability

### Exercise 3: Multi-Environment Setup

Configure Vault for:
- Development (local)
- Staging (AWS)
- Production (AWS with HA)
- Different access policies per environment
- Separate authentication methods

---

## Verification

```bash
# Test Vault availability
vault status

# Test authentication
vault login -method=approle role_id=$ROLE_ID secret_id=$SECRET_ID

# Test secret retrieval
vault kv get kv/myapp/config

# Test dynamic credentials
vault read database/creds/readonly

# Test policy
vault policy read myapp-policy

# Audit log
vault audit enable file file_path=/var/log/vault_audit.log
vault audit list
```

---

## Security Best Practices

✅ **Authentication:**
- Use AppRole for services
- Use short-lived tokens
- Implement token renewal
- Rotate SecretIDs regularly

✅ **Access Control:**
- Principle of least privilege
- Separate policies per application
- Use namespaces for isolation
- Regular policy audits

✅ **Operations:**
- Enable audit logging
- Monitor Vault health
- Backup regularly
- Test disaster recovery

✅ **High Availability:**
- Run multiple Vault instances
- Use Consul for storage backend
- Implement automatic unsealing
- Geographic redundancy

---

## Troubleshooting

```bash
# Check Vault seal status
vault status

# View audit logs
tail -f /var/log/vault_audit.log | jq

# Test connectivity
curl -k https://vault.example.com/v1/sys/health

# Debug authentication
VAULT_LOG_LEVEL=debug vault login

# Check token capabilities
vault token capabilities kv/myapp/config
```

---

## Key Takeaways

- ✅ Vault centralizes secret management
- ✅ Dynamic credentials improve security
- ✅ Automatic rotation reduces risk
- ✅ AppRole enables machine authentication
- ✅ Proper policies ensure least privilege
- ✅ Audit logs provide visibility

**Next Lab**: [Kubernetes Security →](../lab-05-kubernetes-security/README.md)
