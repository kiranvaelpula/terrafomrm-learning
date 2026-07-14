# Security in the Software Development Lifecycle (SDLC)

## Overview

Security integration throughout the SDLC ensures vulnerabilities are identified and remediated early, reducing costs and improving overall security posture.

## Traditional SDLC vs Secure SDLC

### Traditional SDLC
```
Requirements → Design → Development → Testing → Deployment → Maintenance
                                                      ↓
                                             Security Testing (Late!)
```

**Problems**:
- Security tested only at the end
- Expensive to fix issues late
- Security as a bottleneck
- Delayed releases

### Secure SDLC (DevSecOps)
```
Requirements → Design → Development → Testing → Deployment → Maintenance
     ↓           ↓           ↓           ↓           ↓            ↓
  Security    Threat     SAST/SCA     DAST        Container   Monitoring
  Requirements Model                             Scanning
```

**Benefits**:
- Security built-in from start
- Early vulnerability detection
- Lower remediation costs
- Faster, secure releases

## Security Activities by SDLC Phase

### 1. Planning & Requirements Phase

**Security Activities**:
- Define security requirements
- Identify compliance needs (GDPR, HIPAA, PCI-DSS)
- Risk assessment
- Security user stories

**Example Security Requirements**:
```yaml
Security_Requirements:
  Authentication:
    - Multi-factor authentication required
    - Password complexity: min 12 chars, special chars
    - Session timeout: 15 minutes
  
  Data Protection:
    - Encryption at rest: AES-256
    - Encryption in transit: TLS 1.3
    - PII must be encrypted
  
  Authorization:
    - Role-based access control (RBAC)
    - Principle of least privilege
    - Audit logging for all access
  
  Compliance:
    - GDPR compliant data handling
    - SOC 2 Type II controls
```

**Security User Stories**:
```
As a user, I want my password to be securely stored 
so that it cannot be compromised even if the database is breached.

Acceptance Criteria:
- Passwords hashed using bcrypt with salt
- No plain text storage
- Minimum 12 characters required
```

---

### 2. Design Phase

**Security Activities**:
- Threat modeling
- Security architecture review
- Define security controls
- Data flow analysis

**Threat Modeling Example (STRIDE)**:
```
Application: E-commerce Platform

Threats:
  Spoofing:
    - Attacker impersonates legitimate user
    - Mitigation: MFA, certificate pinning
  
  Tampering:
    - SQL injection in payment processing
    - Mitigation: Parameterized queries, input validation
  
  Repudiation:
    - User denies making purchase
    - Mitigation: Audit logs, digital signatures
  
  Information Disclosure:
    - Credit card data exposed in logs
    - Mitigation: PCI-DSS compliance, tokenization
  
  Denial of Service:
    - DDoS attack on checkout
    - Mitigation: Rate limiting, WAF, CDN
  
  Elevation of Privilege:
    - Admin access via IDOR vulnerability
    - Mitigation: Authorization checks, secure direct object references
```

**Security Architecture Diagram**:
```
┌─────────────────────────────────────────────────┐
│                   User                          │
└──────────────┬──────────────────────────────────┘
               │ HTTPS/TLS 1.3
┌──────────────▼──────────────────────────────────┐
│            WAF/CDN (DDoS Protection)            │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│      API Gateway (Rate Limiting, Auth)          │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│    Microservices (Mutual TLS, mTLS)             │
│    ├── Auth Service (OAuth2/JWT)                │
│    ├── Payment Service (PCI-DSS)                │
│    └── Order Service                            │
└──────────────┬──────────────────────────────────┘
               │ Encrypted
┌──────────────▼──────────────────────────────────┐
│      Database (Encryption at Rest)              │
└─────────────────────────────────────────────────┘
```

---

### 3. Development Phase

**Security Activities**:
- Secure coding practices
- Code reviews with security focus
- IDE security plugins
- Pre-commit hooks

**Secure Coding Examples**:

**❌ Insecure Code**:
```python
# SQL Injection vulnerability
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# Command Injection
def ping_host(host):
    os.system(f"ping -c 1 {host}")

# Hardcoded secrets
API_KEY = "sk_live_51234567890"
DB_PASSWORD = "SuperSecret123"

# Insecure deserialization
import pickle
data = pickle.loads(request.data)
```

**✅ Secure Code**:
```python
# Parameterized queries
def get_user(username):
    query = "SELECT * FROM users WHERE username = ?"
    return db.execute(query, (username,))

# Input validation + subprocess
import subprocess
import re

def ping_host(host):
    if not re.match(r'^[a-zA-Z0-9.-]+$', host):
        raise ValueError("Invalid hostname")
    
    result = subprocess.run(
        ['ping', '-c', '1', host],
        capture_output=True,
        timeout=5,
        text=True
    )
    return result.stdout

# Environment variables
import os
API_KEY = os.getenv('API_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Safe deserialization
import json
data = json.loads(request.data)
```

**Pre-commit Hook** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash

# Run secret scanning
git secrets --pre_commit_hook -- "$@"

# Run linting
flake8 .

# Run security checks
bandit -r . -f json -o bandit-report.json

if [ $? -ne 0 ]; then
    echo "❌ Security issues found. Commit blocked."
    exit 1
fi

echo "✅ Security checks passed"
```

**IDE Security Plugin** (VS Code settings.json):
```json
{
  "extensions": [
    "GitLab.gitlab-workflow",  // GitLab security scanning
    "Snyk.snyk-vulnerability-scanner",
    "MS-SarifVSCode.sarif-viewer"
  ],
  "snyk.enabled": true,
  "snyk.scanOnSave": true
}
```

---

### 4. Build & Integration Phase

**Security Activities**:
- SAST (Static Application Security Testing)
- SCA (Software Composition Analysis)
- Dependency scanning
- Secret detection

**CI/CD Security Pipeline**:
```yaml
name: Secure Build Pipeline

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      # 1. SAST - Static Analysis
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/owasp-top-ten
            p/secrets
      
      # 2. SCA - Dependency Check
      - name: Dependency Check
        run: |
          npm audit --audit-level=high
          # or
          pip-audit
          # or
          mvn dependency-check:check
      
      # 3. Secret Scanning
      - name: TruffleHog Secret Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD
      
      # 4. License Compliance
      - name: License Check
        run: |
          pip install pip-licenses
          pip-licenses --fail-on="GPL;AGPL"
      
      # 5. Build if all checks pass
      - name: Build Application
        run: |
          docker build -t myapp:${{ github.sha }} .
      
      # 6. Sign artifacts
      - name: Sign Container
        run: |
          cosign sign myapp:${{ github.sha }}
```

---

### 5. Testing Phase

**Security Activities**:
- DAST (Dynamic Application Security Testing)
- Penetration testing
- Security unit tests
- Fuzzing

**DAST Example with OWASP ZAP**:
```yaml
# .github/workflows/dast.yml
name: DAST Scan

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  dast:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Test Environment
        run: |
          kubectl apply -f k8s/test/
          kubectl wait --for=condition=ready pod -l app=myapp
      
      - name: Run OWASP ZAP Scan
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'https://test.myapp.com'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'
      
      - name: Upload Results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: results.sarif
```

**Security Unit Tests**:
```python
import pytest
from app import authenticate, hash_password

def test_password_hashing():
    """Ensure passwords are properly hashed"""
    password = "MyPassword123!"
    hashed = hash_password(password)
    
    # Should not be plain text
    assert hashed != password
    
    # Should use strong algorithm (bcrypt/argon2)
    assert hashed.startswith('$2b$') or hashed.startswith('$argon2')
    
    # Should be salted (different hash each time)
    hashed2 = hash_password(password)
    assert hashed != hashed2

def test_sql_injection_protection():
    """Ensure SQL injection is prevented"""
    malicious_input = "admin' OR '1'='1"
    
    with pytest.raises(ValueError):
        authenticate(malicious_input, "password")

def test_rate_limiting():
    """Ensure rate limiting is enforced"""
    for i in range(100):
        response = app.test_client().post('/login', data={})
    
    # Should get 429 Too Many Requests
    assert response.status_code == 429

def test_session_timeout():
    """Ensure sessions expire after inactivity"""
    # Create session
    session = create_session(user_id=1)
    
    # Simulate 16 minutes passing
    session.last_activity = datetime.now() - timedelta(minutes=16)
    
    # Should be invalid
    assert not is_session_valid(session)
```

---

### 6. Deployment Phase

**Security Activities**:
- Container image scanning
- Infrastructure as Code (IaC) scanning
- Configuration validation
- Secrets management

**Container Scanning**:
```bash
# Scan before push
trivy image --severity HIGH,CRITICAL myapp:latest

# Fail if critical vulnerabilities
trivy image --exit-code 1 --severity CRITICAL myapp:latest

# Generate compliance report
trivy image --compliance docker-cis myapp:latest
```

**IaC Security Scanning**:
```bash
# Scan Terraform
tfsec .
checkov -d .

# Scan Kubernetes manifests
kubesec scan deployment.yaml
kube-score score deployment.yaml

# Scan Helm charts
helm lint --strict ./chart
```

**Secure Deployment Example**:
```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
spec:
  template:
    spec:
      # Security Context
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      
      containers:
      - name: app
        image: myapp:v1.2.3  # Specific version, not :latest
        
        # Container security
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          capabilities:
            drop:
              - ALL
        
        # Resource limits (prevent DoS)
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "100m"
            memory: "128Mi"
        
        # Environment from secrets
        env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
```

---

### 7. Operations & Maintenance Phase

**Security Activities**:
- Continuous monitoring
- Security logging and alerting
- Incident response
- Patch management

**Security Monitoring**:
```python
# monitoring/security_metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Track security events
failed_login_attempts = Counter(
    'failed_login_attempts_total',
    'Total number of failed login attempts',
    ['username', 'ip_address']
)

authentication_duration = Histogram(
    'authentication_duration_seconds',
    'Time spent in authentication'
)

active_sessions = Gauge(
    'active_sessions',
    'Number of active user sessions'
)

# Security alerts
def check_brute_force(username, ip):
    attempts = failed_login_attempts.labels(username, ip)
    
    if attempts > 5:
        send_alert(
            severity='HIGH',
            title=f'Potential brute force from {ip}',
            details=f'{attempts} failed attempts for user {username}'
        )
        block_ip(ip, duration=3600)  # Block for 1 hour
```

**Security Logging**:
```python
import logging
import json
from datetime import datetime

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger('security')
        
    def log_authentication(self, user_id, ip, success):
        self.logger.info(json.dumps({
            'event': 'authentication',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'ip_address': ip,
            'success': success,
            'user_agent': request.headers.get('User-Agent')
        }))
    
    def log_authorization_failure(self, user_id, resource, action):
        self.logger.warning(json.dumps({
            'event': 'authorization_failure',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'severity': 'MEDIUM'
        }))
    
    def log_data_access(self, user_id, data_type, record_count):
        self.logger.info(json.dumps({
            'event': 'data_access',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'data_type': data_type,
            'record_count': record_count
        }))
```

---

## Security Gates

Implement quality gates at each phase:

```yaml
# Quality Gates Configuration
gates:
  pre_commit:
    - secret_scan: BLOCK
    - linting: WARN
  
  build:
    - sast_critical: BLOCK
    - sast_high: WARN
    - dependency_critical: BLOCK
    - license_gpl: BLOCK
  
  test:
    - dast_critical: BLOCK
    - dast_high: WARN
    - code_coverage: WARN_IF_BELOW_80
  
  deploy:
    - container_critical: BLOCK
    - container_high: WARN
    - iac_critical: BLOCK
  
  production:
    - runtime_security: ALERT
    - compliance_check: BLOCK
```

## Security Metrics to Track

```yaml
Metrics:
  Mean_Time_To_Detect: < 5 minutes
  Mean_Time_To_Remediate: < 24 hours
  Vulnerability_Density: < 10 per 1000 LOC
  False_Positive_Rate: < 10%
  Security_Test_Coverage: > 80%
  Critical_Vulnerabilities_Open: 0
  High_Vulnerabilities_Open: < 5
  Deployment_Frequency: Daily
  Security_Training_Completion: 100%
```

## Best Practices

1. **Automate Everything**: Manual security checks don't scale
2. **Fail Fast**: Catch issues early in the pipeline
3. **Continuous Learning**: Update rules and patterns regularly
4. **Developer-Friendly**: Make security easy to adopt
5. **Measure Impact**: Track metrics to show improvement
6. **Security Champions**: Embed security experts in teams
7. **Regular Audits**: Periodic security reviews
8. **Incident Response**: Have a plan and practice it

## Common Pitfalls

❌ Security testing only at the end  
❌ No automation  
❌ Ignoring false positives leads to alert fatigue  
❌ No security training for developers  
❌ Blocking developers with slow security reviews  
❌ Not tracking metrics  
❌ No incident response plan  

## Next Steps

Continue to [Threat Modeling](03-threat-modeling.md) to learn how to identify security risks during the design phase.

---

**Remember**: Security is not a phase—it's a continuous practice integrated throughout the entire SDLC.
