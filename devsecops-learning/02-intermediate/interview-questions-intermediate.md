# DevSecOps Interview Questions - Intermediate Level

Comprehensive interview questions covering SAST/DAST, container security, CI/CD security, and more.

---

## SAST and DAST

### Q1: What's the difference between SAST and DAST, and when should you use each?

**Answer:**

**SAST (Static Application Security Testing):**
- Analyzes source code without running it (white-box)
- Faster, integrated into development workflow
- Catches coding errors early
- Higher false positives
- Best for: Logic flaws, coding errors, compliance checks

**DAST (Dynamic Application Security Testing):**
- Tests running applications (black-box)
- Finds runtime vulnerabilities
- Language-agnostic
- Lower false positives
- Best for: Configuration issues, authentication flaws, injection attacks

**When to use:**
```
Development → SAST (daily)
   ↓
CI/CD Build → SAST (every commit)
   ↓
Staging Deploy → DAST (before production)
   ↓
Production → DAST (periodic scans)
```

**Example Pipeline:**
```yaml
# Use both together
stages:
  - sast      # Fast feedback
  - build
  - deploy
  - dast      # Comprehensive testing
```

---

### Q2: How do you handle false positives in security scanning tools?

**Answer:**

**Strategy:**
1. **Verify**: Manually review each finding
2. **Categorize**: True positive vs false positive
3. **Document**: Record suppression reasons
4. **Tune**: Adjust tool configuration

**Implementation:**
```python
# suppressions.json
{
  "suppressions": [
    {
      "rule_id": "SQL_INJECTION",
      "file": "tests/test_db.py",
      "line": 45,
      "reason": "Intentional test case for SQL injection detection",
      "approved_by": "security-team@company.com",
      "expires": "2024-12-31"
    }
  ]
}
```

**Best Practices:**
- Review suppressions quarterly
- Require approval for suppressions
- Set expiration dates
- Track false positive rate as metric
- Tune rules based on your codebase

---

### Q3: Design a security scanning pipeline that runs both SAST and DAST efficiently.

**Answer:**

```yaml
# .gitlab-ci.yml
variables:
  APP_URL: "https://staging.example.com"

stages:
  - sast
  - build
  - deploy-staging
  - dast
  - security-gate

# SAST - Fast Feedback
sast:semgrep:
  stage: sast
  image: returntocorp/semgrep
  script:
    - semgrep --config=auto --json > semgrep-report.json
  artifacts:
    reports:
      sast: semgrep-report.json
  only:
    - merge_requests
    - main

sast:sonarqube:
  stage: sast
  image: sonarsource/sonar-scanner-cli
  script:
    - sonar-scanner -Dsonar.projectKey=myapp
  only:
    - merge_requests
    - main

# Build
build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

# Deploy to Staging
deploy:staging:
  stage: deploy-staging
  script:
    - kubectl set image deployment/app app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -n staging
    - kubectl rollout status deployment/app -n staging
  environment:
    name: staging
    url: $APP_URL

# DAST - Comprehensive Testing
dast:zap:
  stage: dast
  image: owasp/zap2docker-stable
  variables:
    ZAP_TARGET: $APP_URL
  script:
    - |
      zap-baseline.py -t $ZAP_TARGET \
        -r zap-report.html \
        -J zap-report.json \
        -c zap-rules.conf
  artifacts:
    when: always
    paths:
      - zap-report.html
      - zap-report.json
    reports:
      dast: zap-report.json
  only:
    - main

# Security Gate
security:gate:
  stage: security-gate
  script:
    - |
      # Aggregate findings
      critical=$(jq '[.. | .severity? | select(. == "CRITICAL")] | length' *-report.json)
      high=$(jq '[.. | .severity? | select(. == "HIGH")] | length' *-report.json)
      
      echo "Critical: $critical, High: $high"
      
      # Fail if thresholds exceeded
      if [ "$critical" -gt 0 ]; then
        echo "❌ Critical vulnerabilities found!"
        exit 1
      fi
      
      if [ "$high" -gt 5 ]; then
        echo "⚠️  Too many high-severity vulnerabilities!"
        exit 1
      fi
      
      echo "✅ Security gate passed"
  dependencies:
    - sast:semgrep
    - dast:zap
```

**Key Features:**
- SAST runs on every MR (fast feedback)
- DAST runs only on main branch (slower)
- Security gate aggregates results
- Configurable thresholds
- Artifacts preserved for review

---

## Container Security

### Q4: How do you secure a Docker container throughout its lifecycle?

**Answer:**

**1. Image Build Phase:**
```dockerfile
# Secure Dockerfile
FROM python:3.11-slim-bullseye AS builder

# Build dependencies
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Runtime image
FROM python:3.11-slim-bullseye

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy wheels from builder
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

# Copy application
COPY --chown=appuser:appuser app/ ./

# Security settings
USER appuser
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')"

CMD ["python", "main.py"]
```

**2. Image Scanning:**
```bash
# Scan before push
trivy image --severity HIGH,CRITICAL myapp:latest
```

**3. Runtime Security:**
```yaml
# Kubernetes pod security
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      capabilities:
        drop:
          - ALL
    resources:
      limits:
        memory: "512Mi"
        cpu: "500m"
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  
  volumes:
  - name: tmp
    emptyDir: {}
```

**4. Runtime Monitoring:**
```yaml
# Falco rule
- rule: Unauthorized Process
  condition: spawned_process and container and not proc.name in (allowed_processes)
  output: Unauthorized process in container
  priority: WARNING
```

---

### Q5: Explain container image scanning and how to integrate it into CI/CD.

**Answer:**

**What It Scans:**
- OS packages vulnerabilities
- Application dependencies
- Exposed secrets
- Misconfigurations
- License issues

**Implementation:**
```yaml
# GitHub Actions
name: Container Security

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .
      
      - name: Run Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
      
      - name: Upload to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Check for critical issues
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:${{ github.sha }}
          exit-code: '1'
          severity: 'CRITICAL'
```

**Scanning Strategy:**
```
Pre-commit → Scan Dockerfile (fast)
    ↓
CI Build → Scan image (comprehensive)
    ↓
Registry → Continuous scanning (scheduled)
    ↓
Deployment → Admission control (gate)
```

---

### Q6: What are container runtime security best practices?

**Answer:**

**1. Use Security Profiles:**
```yaml
# AppArmor
apiVersion: v1
kind: Pod
metadata:
  annotations:
    container.apparmor.security.beta.kubernetes.io/app: runtime/default
```

**2. Implement Runtime Monitoring:**
```yaml
# Falco deployment
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: falco
spec:
  template:
    spec:
      containers:
      - name: falco
        image: falcosecurity/falco:latest
        securityContext:
          privileged: true
        volumeMounts:
        - mountPath: /host/var/run/docker.sock
          name: docker-socket
        - mountPath: /dev
          name: dev-fs
```

**3. Network Policies:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-network-policy
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          role: database
    ports:
    - protocol: TCP
      port: 5432
```

**4. Resource Limits:**
```yaml
resources:
  limits:
    memory: "512Mi"
    cpu: "500m"
    ephemeral-storage: "1Gi"
  requests:
    memory: "256Mi"
    cpu: "250m"
```

**5. Read-Only Root Filesystem:**
```yaml
securityContext:
  readOnlyRootFilesystem: true

volumeMounts:
- name: tmp
  mountPath: /tmp
- name: cache
  mountPath: /app/cache
```

---

## CI/CD Security

### Q7: How do you secure secrets in CI/CD pipelines?

**Answer:**

**❌ Never Do:**
```yaml
# BAD: Hardcoded secrets
variables:
  DATABASE_PASSWORD: "mypassword123"
  API_KEY: "sk_live_abc123"
```

**✅ Good Practices:**

**1. CI/CD Variables (Encrypted):**
```yaml
# GitLab CI - use protected variables
deploy:
  script:
    - echo "Deploying with $DATABASE_PASSWORD"
  only:
    - main
```

**2. External Secret Management:**
```yaml
# GitHub Actions - use secrets
- name: Deploy
  env:
    DATABASE_PASSWORD: ${{ secrets.DATABASE_PASSWORD }}
    API_KEY: ${{ secrets.API_KEY }}
  run: |
    ./deploy.sh
```

**3. Vault Integration:**
```yaml
# Retrieve from HashiCorp Vault
before_script:
  - export VAULT_TOKEN=$(cat /vault/token)
  - export DB_PASSWORD=$(vault kv get -field=password secret/database)
  
deploy:
  script:
    - kubectl create secret generic db-creds --from-literal=password=$DB_PASSWORD
```

**4. OIDC Token Exchange:**
```yaml
# GitHub Actions - OIDC
- name: Configure AWS Credentials
  uses: aws-actions/configure-aws-credentials@v2
  with:
    role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
    aws-region: us-east-1
# No long-lived credentials!
```

**Best Practices:**
- Use short-lived tokens
- Rotate secrets regularly
- Limit secret scope
- Audit secret access
- Never log secrets
- Use secret scanning tools

---

### Q8: Design a secure deployment pipeline with multiple approval gates.

**Answer:**

```yaml
# .github/workflows/secure-deploy.yml
name: Secure Deployment Pipeline

on:
  push:
    branches: [main]

jobs:
  # Security Checks
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: SAST
        run: semgrep --config=auto
      
      - name: Secret Scanning
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD
      
      - name: Dependency Check
        run: |
          pip install safety
          safety check --json
  
  # Build and Test
  build:
    needs: security-scan
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v3
      
      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .
      
      - name: Container scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:${{ github.sha }}
          exit-code: '1'
          severity: 'CRITICAL'
      
      - name: Push to registry
        run: docker push myapp:${{ github.sha }}
  
  # Deploy to Staging
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.example.com
    steps:
      - name: Deploy
        run: kubectl set image deployment/app app=myapp:${{ github.sha }} -n staging
      
      - name: Run DAST
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'https://staging.example.com'
  
  # Manual Approval Gate
  approve-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production-approval
    steps:
      - name: Request Approval
        run: echo "Waiting for production approval..."
  
  # Deploy to Production
  deploy-production:
    needs: approve-production
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com
    steps:
      - name: Deploy with Blue-Green
        run: |
          # Deploy new version
          kubectl apply -f k8s/production/
          
          # Wait for health checks
          kubectl rollout status deployment/app -n production
          
          # Switch traffic
          kubectl patch service app -p '{"spec":{"selector":{"version":"new"}}}'
      
      - name: Notify
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Production deployment completed'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

**Approval Gates:**
1. **Automated** → Security scans must pass
2. **Automated** → Tests must pass
3. **Automated** → Staging deployment successful
4. **Manual** → Security/Ops team approval
5. **Automated** → Production deployment
6. **Automated** → Smoke tests pass

---

## Compliance and Policy

### Q9: How do you implement compliance-as-code in a DevSecOps pipeline?

**Answer:**

**Using Open Policy Agent (OPA):**

**1. Define Policies:**
```rego
# policy/kubernetes.rego
package kubernetes.admission

deny[msg] {
    input.request.kind.kind == "Pod"
    input.request.object.spec.containers[_].securityContext.privileged == true
    msg := "Privileged containers are not allowed"
}

deny[msg] {
    input.request.kind.kind == "Pod"
    not input.request.object.spec.securityContext.runAsNonRoot
    msg := "Containers must run as non-root"
}

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.resources.limits.memory
    msg := sprintf("Container %v must have memory limits", [container.name])
}
```

**2. Test Policies:**
```rego
# policy/kubernetes_test.rego
test_deny_privileged {
    deny["Privileged containers are not allowed"] with input as {
        "request": {
            "kind": {"kind": "Pod"},
            "object": {
                "spec": {
                    "containers": [{
                        "securityContext": {"privileged": true}
                    }]
                }
            }
        }
    }
}
```

**3. Enforce in CI/CD:**
```yaml
policy-check:
  stage: validate
  image: openpolicyagent/opa:latest
  script:
    - opa test policy/
    - opa eval --data policy/ --input k8s/deployment.yaml "data.kubernetes.admission.deny"
```

**4. Runtime Enforcement:**
```yaml
# OPA Gatekeeper in Kubernetes
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-labels
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
  parameters:
    labels: ["app", "owner", "environment"]
```

---

### Q10: Explain the concept of "security as code" and how to implement it.

**Answer:**

**Security as Code** means defining security controls, policies, and configurations in code that can be versioned, tested, and automated.

**Implementation:**

**1. Infrastructure Security:**
```hcl
# terraform/security_groups.tf
resource "aws_security_group" "app" {
  name = "app-sg"
  
  # Only allow HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Deny all outbound by default
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Security = "high"
    Compliance = "pci-dss"
  }
}

# Validate with Checkov
# checkov -f security_groups.tf
```

**2. Application Security:**
```python
# security/config.py
from dataclasses import dataclass

@dataclass
class SecurityConfig:
    """Security configuration as code"""
    
    # Authentication
    session_timeout_minutes: int = 30
    max_login_attempts: int = 3
    password_min_length: int = 12
    require_mfa: bool = True
    
    # Authorization
    default_role: str = "user"
    admin_ips: list = field(default_factory=lambda: ["10.0.0.0/8"])
    
    # API Security
    rate_limit_per_minute: int = 100
    allowed_origins: list = field(default_factory=lambda: ["https://example.com"])
    
    # Data Protection
    encrypt_at_rest: bool = True
    encrypt_in_transit: bool = True
    data_retention_days: int = 90
    
    def validate(self):
        """Validate security configuration"""
        assert self.password_min_length >= 12
        assert self.require_mfa is True
        assert self.encrypt_at_rest is True

# security/tests/test_config.py
def test_security_config():
    config = SecurityConfig()
    config.validate()  # Ensure secure defaults
```

**3. Security Tests as Code:**
```python
# tests/security/test_auth.py
import pytest
from app import create_app

def test_no_auth_returns_401():
    app = create_app()
    client = app.test_client()
    
    response = client.get('/api/protected')
    assert response.status_code == 401

def test_sql_injection_prevented():
    client = app.test_client()
    
    # Attempt SQL injection
    response = client.post('/api/login', json={
        'username': "admin' OR '1'='1",
        'password': "password"
    })
    
    assert response.status_code != 200

def test_xss_sanitized():
    response = client.post('/api/comment', json={
        'text': '<script>alert("XSS")</script>'
    })
    
    data = response.get_json()
    assert '<script>' not in data['text']
```

**4. Security Pipeline:**
```yaml
# .github/workflows/security.yml
name: Security as Code

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: IaC Security
        run: checkov -d terraform/
      
      - name: Security Config Tests
        run: pytest tests/security/
      
      - name: SAST
        run: semgrep --config=auto
      
      - name: Dependency Check
        run: safety check
```

**Benefits:**
- Version controlled security
- Automated testing
- Consistent enforcement
- Auditability
- Fast feedback

---

## Additional Practice

**Scenario Questions:**
1. How would you respond to a critical vulnerability found in production?
2. Design a zero-trust network architecture for microservices
3. Implement secret rotation in a Kubernetes cluster
4. Create a security incident response pipeline

---

**Next**: [Advanced Topics →](../03-advanced/)
