# Lab 1: Basic Security Scanning

## 🎯 Objectives

By the end of this lab, you will:
- Install and use security scanning tools
- Scan containers for vulnerabilities
- Detect secrets in code repositories
- Run static analysis on source code
- Generate and interpret security reports

## 📋 Prerequisites

- Docker installed
- Git installed
- Python 3.8+

## 🛠️ Tools Used

- Trivy (container scanning)
- git-secrets (secret detection)
- Semgrep (SAST)
- Safety (Python dependency check)

## Lab Exercises

### Exercise 1: Container Scanning with Trivy (15 mins)

**Task**: Scan Docker images and identify vulnerabilities

```bash
# Install Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan a public image
trivy image nginx:1.19

# Scan with severity filter
trivy image --severity HIGH,CRITICAL nginx:1.19

# Scan local Dockerfile
docker build -t vulnerable-app:v1 -f Dockerfile.vulnerable .
trivy image vulnerable-app:v1
```

**Expected Output**: List of CVEs with severity levels

**Questions**:
1. How many CRITICAL vulnerabilities were found?
2. Which CVE has the highest severity?
3. What's the recommended fix?

**Solution**: See `solutions/exercise-1.md`

---

### Exercise 2: Secret Scanning (10 mins)

**Task**: Detect hardcoded secrets in a repository

```bash
# Install git-secrets
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets && sudo make install

# Initialize in sample repo
cd ../sample-app
git secrets --install
git secrets --register-aws

# Scan repository
git secrets --scan

# Scan history
git secrets --scan-history
```

**Vulnerable Code** (in `sample-app/config.py`):
```python
# ❌ SECURITY ISSUE: Hardcoded credentials
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DATABASE_PASSWORD = "SuperSecret123!"
```

**Your Task**:
1. Run git-secrets and identify all secrets
2. Fix the code using environment variables
3. Re-scan to verify

**Fixed Code**:
```python
# ✅ SECURE: Use environment variables
import os

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
```

---

### Exercise 3: Static Code Analysis (15 mins)

**Task**: Find security vulnerabilities in source code

```bash
# Install Semgrep
pip install semgrep

# Scan with default rules
semgrep --config=auto sample-app/

# Scan for specific vulnerabilities
semgrep --config=p/owasp-top-ten sample-app/

# Generate JSON report
semgrep --config=auto --json --output=report.json sample-app/
```

**Vulnerable Code** (in `sample-app/app.py`):
```python
# SQL Injection vulnerability
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# Command Injection vulnerability
def ping_host(host):
    os.system(f"ping -c 1 {host}")

# Path Traversal vulnerability
def read_file(filename):
    with open(f"/var/www/uploads/{filename}") as f:
        return f.read()
```

**Your Task**:
1. Run Semgrep and identify all vulnerabilities
2. Fix each vulnerability
3. Re-scan to verify fixes

---

### Exercise 4: Dependency Scanning (10 mins)

**Task**: Check Python dependencies for known vulnerabilities

```bash
# Install Safety
pip install safety

# Check requirements.txt
safety check --file requirements.txt

# Check installed packages
safety check

# Generate detailed report
safety check --json --output=safety-report.json
```

**Vulnerable requirements.txt**:
```txt
Flask==0.12.2
Django==1.11.0
requests==2.6.0
Jinja2==2.7.3
```

**Your Task**:
1. Identify vulnerable packages
2. Find the CVEs
3. Update to secure versions
4. Re-scan to verify

---

### Exercise 5: Create Security Report (10 mins)

**Task**: Combine all scan results into a comprehensive report

```bash
# Run all scans and collect results
./run-all-scans.sh

# Generate HTML report
python generate-report.py
```

**Report should include**:
- Container vulnerabilities count
- Detected secrets count
- SAST findings by severity
- Dependency vulnerabilities
- Recommendations for remediation

---

## 🧪 Verification

Run the verification script:

```bash
./verify.sh
```

**Expected Results**:
```
✅ Trivy installed and working
✅ No secrets detected in repository
✅ No HIGH/CRITICAL vulnerabilities in code
✅ All dependencies updated
✅ Security report generated
```

## 📊 Success Criteria

- [ ] All tools installed successfully
- [ ] Identified all vulnerabilities in sample code
- [ ] Fixed all security issues
- [ ] Generated comprehensive security report
- [ ] Verification script passes all checks

## 🎓 Key Takeaways

1. **Automation is Key**: Security scanning should be automated in CI/CD
2. **Multiple Tools**: Use different tools for different vulnerability types
3. **Fix Early**: Finding issues early is cheaper than fixing in production
4. **False Positives**: Learn to identify and handle false positives
5. **Continuous**: Security scanning should run continuously, not once

## 📚 Additional Resources

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Semgrep Rules](https://semgrep.dev/explore)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## 🏆 Challenge

**Advanced Exercise**: Create a GitHub Action workflow that:
1. Runs all security scans on every commit
2. Blocks merge if HIGH/CRITICAL issues found
3. Posts scan results as PR comments
4. Generates weekly security reports

See `challenges/github-action-challenge.md` for details.

---

**Next Lab**: [Lab 2: CI/CD Security Pipeline](../lab-02-cicd-security/)
