# Chapter 29: Secrets Manager & KMS - Secrets and Encryption

## Overview

AWS Secrets Manager stores and rotates sensitive credentials (passwords, API keys), while AWS KMS (Key Management Service) manages the encryption keys that protect your data across AWS.

## 📖 Understanding Secrets Manager & KMS (Intuition First)

Think about how a hotel handles valuables. Guests don't tape their cash and passports to the room door — they put them in a safe. And the hotel doesn't hand out master keys freely; there's a controlled key system where each key opens only what it should, access is logged, and locks get changed regularly. Secrets Manager is the safe for your application's sensitive credentials, and KMS is the master key-management system that controls the encryption keys locking everything down. Together they answer two questions every secure system must: *where do I keep secrets safely?* and *who controls the keys that protect my data?*

The problem these solve is that developers, left to their own devices, do dangerous things with secrets: hardcode database passwords in source code, commit API keys to Git, or paste credentials into config files that end up in backups and logs. This is one of the most common and catastrophic security failures — leaked credentials are behind a huge share of breaches. **Secrets Manager gives secrets a proper home**: encrypted, access-controlled, audited, and — crucially — *retrievable at runtime* so they never need to live in code.

The standout feature of Secrets Manager is **automatic rotation.** A password that never changes is a password that's one leak away from disaster forever. Secrets Manager can automatically rotate credentials on a schedule (e.g., generate a new database password every 30 days and update both the secret and the database), so even if a secret leaks, its useful lifetime is short. This turns "we should rotate credentials someday" (which never happens manually) into an automated, reliable process.

**KMS operates one layer deeper** — it's about the encryption keys themselves. Nearly everything in AWS can be encrypted (S3 objects, EBS volumes, RDS databases, Secrets Manager secrets), and KMS is the central service that creates, stores, and controls access to the keys that do that encryption. The elegant part is **envelope encryption**: KMS doesn't encrypt your huge dataset directly; it encrypts a small "data key" that encrypts your data. This is fast, scalable, and means the powerful master key never leaves KMS's hardened hardware. Every use of a key is logged in CloudTrail, so you have a full audit trail of who decrypted what, when.

The relationship to internalize: **KMS manages keys; Secrets Manager manages secrets (and uses KMS to encrypt them).** A common interview point is distinguishing them, and also Secrets Manager vs SSM Parameter Store — Parameter Store is a cheaper, simpler option for config and basic secrets (no built-in rotation), while Secrets Manager costs more but adds automatic rotation and tighter integration. Choosing the right tool for credentials and encryption is fundamental to secure cloud architecture.

---

## AWS Secrets Manager

```
Stores: database credentials, API keys, OAuth tokens, any sensitive string/JSON
Features:
  - Encrypted at rest (using KMS)
  - Fine-grained access control (IAM policies)
  - AUTOMATIC ROTATION on a schedule
  - Retrieved at runtime via API (never hardcoded)
  - Every access logged in CloudTrail
```

### Storing and Retrieving a Secret

```python
import boto3
import json

client = boto3.client("secretsmanager")

# Store a secret
client.create_secret(
    Name="prod/db/credentials",
    SecretString=json.dumps({"username": "admin", "password": "S3cr3t!"})
)

# Retrieve at runtime (NEVER hardcode the secret in your app)
resp = client.get_secret_value(SecretId="prod/db/credentials")
creds = json.loads(resp["SecretString"])
db_password = creds["password"]   # used to connect, never written to disk/code
```

### Automatic Rotation

```
1. Secrets Manager triggers a Lambda on a schedule (e.g., every 30 days)
2. The Lambda generates a new password
3. Updates the credential in the database (or service)
4. Updates the secret value in Secrets Manager
5. Apps always fetch the current version → seamless rotation

Even a leaked secret has a short useful life.
```

## AWS KMS (Key Management Service)

```
Manages encryption keys used across AWS services.
Key types:
  - AWS-managed keys   — AWS creates/manages (simplest)
  - Customer-managed keys (CMK) — you control policy, rotation, access
  - AWS-owned keys     — fully behind the scenes

Every key usage is logged in CloudTrail (full audit trail).
```

### Envelope Encryption (how KMS scales)

```
KMS doesn't encrypt your huge data directly. Instead:
  1. KMS generates a DATA KEY
  2. Your data is encrypted with the data key (fast, local)
  3. The data key itself is encrypted by the KMS master key (CMK)
  4. The encrypted data key is stored alongside your data
  5. To decrypt: KMS decrypts the data key, then you decrypt the data

The master key (CMK) NEVER leaves KMS's hardened hardware (HSM).
This is fast, scalable, and secure.
```

### Using KMS

```python
import boto3

kms = boto3.client("kms")

# Encrypt small data directly (< 4KB)
resp = kms.encrypt(KeyId="alias/my-key", Plaintext=b"sensitive data")
ciphertext = resp["CiphertextBlob"]

# Decrypt
resp = kms.decrypt(CiphertextBlob=ciphertext)
plaintext = resp["Plaintext"]

# For large data, use envelope encryption via generate_data_key
data_key = kms.generate_data_key(KeyId="alias/my-key", KeySpec="AES_256")
# data_key["Plaintext"] → encrypt your data locally
# data_key["CiphertextBlob"] → store alongside the encrypted data
```

## Where KMS Is Used (encryption everywhere)

```
- S3: server-side encryption (SSE-KMS)
- EBS: encrypted volumes
- RDS/Aurora: encrypted databases
- Secrets Manager: encrypts stored secrets
- DynamoDB: encryption at rest
- Lambda: encrypt environment variables
KMS is the central key authority for encrypting data at rest across AWS.
```

## Secrets Manager vs SSM Parameter Store

| Factor | Secrets Manager | SSM Parameter Store |
|--------|-----------------|---------------------|
| Purpose | Secrets (credentials) | Config + secrets |
| Automatic rotation | ✅ Built-in | ❌ (manual) |
| Cost | Per secret + API calls (higher) | Free tier (standard params) |
| Encryption | KMS | KMS (SecureString) |
| Cross-account | ✅ | Limited |
| Best for | DB credentials, rotating secrets | App config, simpler secrets, cost-sensitive |

**Rule of thumb:** Parameter Store for config and simple/low-cost secrets; Secrets Manager when you need automatic rotation or tighter integration (e.g., RDS credentials).

## Security Best Practices

```
- NEVER hardcode secrets in code or commit them to Git
- Fetch secrets at runtime from Secrets Manager / Parameter Store
- Enable automatic rotation for credentials
- Use customer-managed KMS keys for sensitive data (control + audit)
- Enable KMS key rotation (annual)
- Apply least-privilege IAM to who can read secrets / use keys
- Audit access via CloudTrail
- Encrypt everything at rest (S3, EBS, RDS) — it's cheap and easy
```

---

## 🎯 Interview Quick Points

- **Secrets Manager** stores/rotates credentials; **KMS** manages the encryption keys
- Analogy: Secrets Manager = the hotel safe; KMS = the master key-control system
- Solves the #1 mistake: hardcoding secrets in code / committing keys to Git
- Secrets are **fetched at runtime via API** — never live in source or config files
- **Automatic rotation** is Secrets Manager's killer feature — limits a leaked secret's lifespan
- **KMS uses envelope encryption**: master key encrypts a data key; data key encrypts data
- The **master key (CMK) never leaves KMS's hardware (HSM)**
- KMS powers encryption at rest across S3, EBS, RDS, DynamoDB, Secrets Manager, Lambda
- Every key/secret access is **logged in CloudTrail** for audit
- **Secrets Manager vs Parameter Store**: Secrets Manager adds rotation (costs more); Parameter Store is cheaper for config/simple secrets
- Best practices: least-privilege access, enable rotation, encrypt everything, audit via CloudTrail
- KMS key types: AWS-managed (simple) vs customer-managed (full control + policy)

## Next Steps

You've completed the AWS advanced topics. Review the [interview questions](interview-questions-advanced.md) to test your knowledge.
