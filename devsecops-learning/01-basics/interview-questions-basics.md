# DevSecOps Interview Questions - Basics

## Conceptual Questions

### Q1: What is DevSecOps and how does it differ from DevOps?

**Answer**: DevSecOps extends DevOps by integrating security practices throughout the entire software development lifecycle rather than treating security as a final gate. Key differences:
- **DevOps**: Development + Operations (fast delivery)
- **DevSecOps**: Development + Security + Operations (fast + secure delivery)

DevSecOps implements "shift-left security" where security testing and validation happens early in development, not just before deployment.

---

### Q2: Explain the concept of "Shift Left" in security.

**Answer**: Shift Left means moving security earlier in the SDLC:

**Traditional** (Shift Right):
```
Plan → Code → Build → Test → Security Review → Deploy
                                      ↑ (bottleneck)
```

**Shift Left**:
```
Plan (Threat Model) → Code (SAST) → Build (SCA) → Test (DAST) → Deploy (Container Scan) → Monitor
  ↓                     ↓              ↓             ↓               ↓                      ↓
Security            Security       Security     Security        Security               Security
```

Benefits:
- Early vulnerability detection
- Lower remediation costs
- Faster time to market
- Better security culture

---

### Q3: What is the difference between SAST and DAST?

**Answer**:

| Aspect | SAST (Static) | DAST (Dynamic) |
|--------|---------------|----------------|
| **When** | During development | After deployment |
| **What** | Source code analysis | Running application |
| **Access** | Needs source code | Black-box testing |
| **Findings** | Code vulnerabilities | Runtime vulnerabilities |
| **False Positives** | Higher | Lower |
| **Examples** | SQL injection in code | XSS on live site |

**SAST Example**:
```python
# SAST detects this
password = input("Enter password: ")
query = f"SELECT * FROM users WHERE password = '{password}'"  # SQL injection risk
```

**DAST Example**:
```bash
# DAST tests running application
curl -X POST http://app.com/login \
  -d "username=admin'--&password=any"
```

**Best Practice**: Use both! SAST in CI/CD, DAST before production.

---

### Q4: What are the key components of a DevSecOps pipeline?

**Answer**:

```yaml
DevSecOps Pipeline:
  1. Source Code:
     - Git hooks for secret scanning
     - Pre-commit security checks
  
  2. Build:
     - SAST (static code analysis)
     - SCA (dependency scanning)
     - Secret detection
  
  3. Test:
     - DAST (dynamic testing)
     - Security unit tests
     - Penetration testing
  
  4. Deploy:
     - Container scanning
     - IaC security scanning
     - Configuration validation
  
  5. Monitor:
     - Runtime security
     - Vulnerability management
     - Incident response
```

---

### Q5: What is container security and why is it important?

**Answer**: Container security involves securing:

1. **Container Images**:
```bash
# Scan for vulnerabilities
trivy image nginx:latest
```

2. **Container Runtime**:
- Restrict capabilities
- Use non-root users
- Read-only file systems

3. **Container Orchestration** (Kubernetes):
- Pod security policies
- Network policies
- RBAC

**Why Important**:
- Containers share host kernel (privilege escalation risk)
- Images may have vulnerabilities
- Misconfigurations can expose systems
- Supply chain attacks (malicious images)

---

## Practical Questions

### Q6: How would you implement secret scanning in a Git repository?

**Answer**:

```bash
# 1. Install git-secrets
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets && sudo make install

# 2. Initialize in your repo
cd /path/to/your/repo
git secrets --install

# 3. Add patterns
git secrets --register-aws  # AWS credentials
git secrets --add 'password\s*=\s*.+'  # Generic passwords

# 4. Scan existing repo
git secrets --scan-history

# 5. Add pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
git secrets --pre_commit_hook -- "$@"
EOF
chmod +x .git/hooks/pre-commit
```

**Alternative with TruffleHog**:
```bash
docker run --rm -v $(pwd):/repo trufflesecurity/trufflehog:latest \
  filesystem /repo --json
```

---

### Q7: Write a GitHub Actions workflow for basic security scanning.

**Answer**:

```yaml
name: Security Scanning

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload to Security tab
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Run Semgrep SAST
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
      
      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD
      
      - name: Dependency check
        run: |
          npm audit --audit-level=high
          # Or for Python: pip-audit
          # Or for Java: dependency-check
```

---

### Q8: How do you scan Docker images for vulnerabilities?

**Answer**:

**Using Trivy**:
```bash
# Scan specific image
trivy image nginx:1.20

# Scan with severity filter
trivy image --severity HIGH,CRITICAL nginx:1.20

# Generate report
trivy image --format json --output report.json nginx:1.20

# Scan local image before pushing
docker build -t myapp:latest .
trivy image myapp:latest

# Fail build on critical vulnerabilities
trivy image --exit-code 1 --severity CRITICAL myapp:latest
```

**Using Docker Scan**:
```bash
docker scan nginx:1.20
```

**Using Snyk**:
```bash
snyk container test nginx:1.20
```

**In Dockerfile**:
```dockerfile
FROM nginx:1.20

# Add to CI/CD
RUN trivy fs /

# Use minimal base images
FROM alpine:3.14
```

---

### Q9: What tools would you use for dependency scanning?

**Answer**:

**JavaScript/Node.js**:
```bash
# Built-in npm audit
npm audit
npm audit fix

# Using Snyk
npm install -g snyk
snyk test
snyk monitor

# Using OWASP Dependency-Check
dependency-check --project MyApp --scan ./
```

**Python**:
```bash
# Using Safety
pip install safety
safety check

# Using pip-audit
pip install pip-audit
pip-audit

# Using Snyk
snyk test --file=requirements.txt
```

**Java**:
```bash
# Using OWASP Dependency-Check
mvn dependency-check:check

# Using Snyk
snyk test --file=pom.xml
```

**Gradle**:
```bash
./gradlew dependencyCheckAnalyze
```

---

### Q10: How do you implement security in Infrastructure as Code?

**Answer**:

**1. Scan Terraform with tfsec**:
```bash
# Install
brew install tfsec

# Scan
tfsec .

# Scan with specific checks
tfsec --minimum-severity HIGH .
```

Example issue:
```hcl
# ❌ Bad: Public S3 bucket
resource "aws_s3_bucket" "bad" {
  bucket = "my-bucket"
  acl    = "public-read"  # tfsec will flag this
}

# ✅ Good: Private bucket
resource "aws_s3_bucket" "good" {
  bucket = "my-bucket"
  acl    = "private"
}
```

**2. Scan with Checkov**:
```bash
# Install
pip install checkov

# Scan Terraform
checkov -d .

# Scan Kubernetes manifests
checkov -f deployment.yaml
```

**3. Use Policy as Code**:
```python
# Sentinel policy for Terraform
import "tfplan/v2" as tfplan

# Ensure all S3 buckets are private
main = rule {
  all tfplan.resource_changes as _, rc {
    rc.type is "aws_s3_bucket" implies
    rc.change.after.acl is "private"
  }
}
```

---

## Scenario-Based Questions

### Q11: A developer accidentally committed AWS credentials to GitHub. What steps do you take?

**Answer**:

**Immediate Actions** (First 5 minutes):
```bash
# 1. Revoke the credentials immediately
aws iam delete-access-key --access-key-id AKIAXXXXXX

# 2. Create new credentials
aws iam create-access-key --user-name username

# 3. Audit recent activity
aws cloudtrail lookup-events --lookup-attributes \
  AttributeKey=AccessKeyId,AttributeValue=AKIAXXXXXX
```

**Remove from Git History**:
```bash
# Using git-filter-repo
pip install git-filter-repo
git filter-repo --path .env --invert-paths

# Or using BFG Repo-Cleaner
java -jar bfg.jar --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**Prevention**:
```bash
# 1. Install git-secrets
git secrets --install
git secrets --register-aws

# 2. Add pre-commit hook
# 3. Use secret management (AWS Secrets Manager, Vault)
# 4. Enable GitHub secret scanning
# 5. Implement AWS IAM policies to limit blast radius
```

**Communication**:
- Notify security team
- Document incident
- Review access logs
- Post-mortem to prevent recurrence

---

### Q12: You need to implement security scanning in an existing CI/CD pipeline without breaking builds. How do you approach this?

**Answer**:

**Phase 1: Baseline (Week 1-2)**
```yaml
# Add scanning in "audit mode" - don't fail builds
- name: Security Scan (Audit Only)
  run: |
    trivy image myapp:latest || true  # Don't fail
    semgrep --config=auto . --json > results.json || true
  continue-on-error: true
```

**Phase 2: Visibility (Week 3-4)**
```yaml
# Upload results, track trends
- name: Upload Results
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: results.sarif

# Generate reports
- name: Generate Report
  run: |
    python generate_security_report.py
    # Email to team
```

**Phase 3: Thresholds (Week 5-6)**
```yaml
# Fail only on critical issues
- name: Security Gate
  run: |
    CRITICAL=$(jq '.results[] | select(.severity=="CRITICAL") | length' results.json)
    if [ $CRITICAL -gt 0 ]; then
      echo "Found $CRITICAL critical vulnerabilities"
      exit 1
    fi
```

**Phase 4: Full Enforcement (Week 7+)**
```yaml
# Fail on high+ severity
- name: Security Enforcement
  run: |
    trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:latest
```

**Key Principles**:
- Start permissive, gradually tighten
- Fix existing issues before enforcing
- Provide clear remediation guidance
- Measure and communicate progress

---

### Q13: How would you secure a Kubernetes cluster from a DevSecOps perspective?

**Answer**:

**1. Pod Security**:
```yaml
# PodSecurityPolicy
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  volumes:
    - 'configMap'
    - 'secret'
```

**2. Network Policies**:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

**3. RBAC**:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
```

**4. Scanning**:
```bash
# Scan manifests
kubesec scan deployment.yaml

# Scan cluster configuration
kube-bench

# Runtime security
falco  # Detects anomalous behavior
```

**5. Image Security**:
```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    image: myapp:v1.2.3  # Use specific versions
    imagePullPolicy: Always
    securityContext:
      runAsNonRoot: true
      readOnlyRootFilesystem: true
      allowPrivilegeEscalation: false
```

---

## Quick Answer Questions

### Q14: What is the OWASP Top 10?

**Answer**: Top 10 critical web application security risks:
1. Broken Access Control
2. Cryptographic Failures
3. Injection
4. Insecure Design
5. Security Misconfiguration
6. Vulnerable Components
7. Authentication Failures
8. Software and Data Integrity Failures
9. Logging and Monitoring Failures
10. Server-Side Request Forgery (SSRF)

---

### Q15: What is a CVE?

**Answer**: **Common Vulnerabilities and Exposures** - A standardized identifier for publicly known security vulnerabilities. Format: CVE-YEAR-NUMBER (e.g., CVE-2021-44228 for Log4Shell).

---

### Q16: What is SBOM?

**Answer**: **Software Bill of Materials** - A comprehensive list of all components, libraries, and dependencies in software, used for vulnerability management and compliance.

---

### Q17: Name three secrets management tools.

**Answer**:
1. **HashiCorp Vault** - Enterprise secret management
2. **AWS Secrets Manager** - Cloud-native AWS solution
3. **Azure Key Vault** - Microsoft Azure solution

Others: Google Secret Manager, CyberArk, 1Password

---

### Q18: What is Zero Trust Security?

**Answer**: Security model based on "never trust, always verify":
- No implicit trust based on location
- Verify every access request
- Least privilege access
- Micro-segmentation
- Continuous monitoring

---

### Q19: What is defense in depth?

**Answer**: Layered security approach:
```
Application Security (SAST, DAST)
    ↓
Container Security (Image scanning)
    ↓
Kubernetes Security (RBAC, Policies)
    ↓
Network Security (Firewalls, VPN)
    ↓
Infrastructure Security (Hardening)
    ↓
Physical Security
```

---

### Q20: What is the principle of least privilege?

**Answer**: Grant minimum permissions necessary:
```yaml
# ❌ Bad: Overly permissive
permissions: admin

# ✅ Good: Specific permissions
permissions:
  - read:packages
  - write:deployments
```

---

## Tips for DevSecOps Interviews

1. **Understand the "Why"**: Know why security practices matter, not just how
2. **Be Tool-Agnostic**: Understand concepts, then discuss specific tools
3. **Show Automation**: Emphasize automated security in CI/CD
4. **Balance Security & Speed**: Show how security enables faster delivery
5. **Real Examples**: Have concrete examples from your experience

---

**Next Level**: Ready for intermediate? Check out [Intermediate Interview Questions](../02-intermediate/interview-questions-intermediate.md)
