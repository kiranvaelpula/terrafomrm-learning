# DevSecOps Quick Start Guide

Get started with DevSecOps in 30 minutes!

## 🎯 Goal
Set up a basic security scanning pipeline and run your first security tests.

## Prerequisites
- Docker installed
- Git installed
- A sample application repository

## Step 1: Install Security Scanning Tools (5 mins)

```bash
# Install Trivy for container scanning
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Install OWASP Dependency-Check
docker pull owasp/dependency-check

# Install git-secrets
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets
sudo make install
```

## Step 2: Scan Your First Container (5 mins)

```bash
# Scan a Docker image
trivy image nginx:latest

# Scan with severity filter
trivy image --severity HIGH,CRITICAL nginx:latest

# Generate report
trivy image --format json --output trivy-report.json nginx:latest
```

## Step 3: Scan Dependencies (5 mins)

```bash
# For Python projects
pip install safety
safety check

# For Node.js projects
npm audit

# For Java projects with OWASP Dependency-Check
docker run --rm -v $(pwd):/src owasp/dependency-check \
  --scan /src --format HTML --project my-app
```

## Step 4: Secrets Scanning (5 mins)

```bash
# Initialize git-secrets
git secrets --install
git secrets --register-aws

# Scan repository for secrets
git secrets --scan

# Install and use TruffleHog
docker run --rm -v $(pwd):/repo trufflesecurity/trufflehog:latest \
  filesystem /repo
```

## Step 5: Static Code Analysis (5 mins)

```bash
# Using Semgrep
pip install semgrep
semgrep --config=auto .

# Using SonarQube Scanner (Docker)
docker run --rm \
  -e SONAR_HOST_URL="http://localhost:9000" \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli
```

## Step 6: Create a Simple Security Pipeline (5 mins)

Create `.github/workflows/security.yml`:

```yaml
name: Security Scanning

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'
      
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
      
      - name: Dependency Check
        run: npm audit
```

## 🎓 What You've Learned

✅ Container vulnerability scanning
✅ Dependency security checks
✅ Secrets detection
✅ Static code analysis
✅ Automated security pipeline

## Next Steps

1. **Explore Basics**: Read [What is DevSecOps](01-basics/01-what-is-devsecops.md)
2. **Deep Dive**: Learn about [SAST and DAST](02-intermediate/06-sast-dast.md)
3. **Practice**: Work through exercises in `devsecops-practice/`
4. **Build**: Create your own security scanning pipeline

## Common Issues & Solutions

### Issue: Trivy fails to scan
```bash
# Update Trivy database
trivy image --download-db-only
```

### Issue: Too many false positives
```bash
# Create .trivyignore file
echo "CVE-2021-12345" >> .trivyignore
```

### Issue: Secrets scanner finds false positives
```bash
# Add to .gitignore patterns or use allowlist
git secrets --add --allowed 'false_positive_pattern'
```

## Resources

- [OWASP DevSecOps Guideline](https://owasp.org/www-project-devsecops-guideline/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Semgrep Rules](https://semgrep.dev/explore)

---
Ready to dive deeper? Start with [01-basics](01-basics/)!
