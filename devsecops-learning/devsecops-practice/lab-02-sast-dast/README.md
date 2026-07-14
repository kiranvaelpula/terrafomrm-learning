# Lab 2: SAST and DAST Integration

## Objectives

By completing this lab, you will:
- Integrate SAST tools (Semgrep, SonarQube) into CI/CD
- Implement DAST scanning with OWASP ZAP
- Configure security gates based on findings
- Handle false positives appropriately
- Build a complete security testing pipeline

**Duration**: 1.5 hours

---

## Prerequisites

- Docker installed
- GitHub account
- Basic Python/JavaScript knowledge
- Completed Lab 1 (Basic Scanning)

---

## Lab Architecture

```
Code Push → SAST (Semgrep) → Build → Deploy to Staging → DAST (ZAP) → Security Gate → Production
```

---

## Part 1: Setup Sample Application

**Create vulnerable web application:**

```bash
mkdir devsecops-lab2
cd devsecops-lab2
```

**app.py** (Intentionally vulnerable):

```python
from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

@app.route('/api/user/<user_id>')
def get_user(user_id):
    # Vulnerability 1: SQL Injection
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    user = cursor.fetchone()
    return jsonify(user) if user else ('Not found', 404)

@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    # Vulnerability 2: Hardcoded credentials
    if username == 'admin' and password == 'admin123':
        return jsonify({'token': 'secret_token_12345'})
    
    return ('Unauthorized', 401)

@app.route('/api/comment', methods=['POST'])
def add_comment():
    comment = request.json.get('text')
    # Vulnerability 3: XSS - No sanitization
    return jsonify({'comment': comment})

@app.route('/api/file')
def read_file():
    # Vulnerability 4: Path traversal
    filename = request.args.get('filename')
    with open(filename, 'r') as f:
        return f.read()

if __name__ == '__main__':
    # Vulnerability 5: Debug mode in production
    app.run(debug=True, host='0.0.0.0')
```

**requirements.txt**:

```
Flask==2.3.0
pytest==7.4.0
```

**Dockerfile**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

# Vulnerability: Running as root
CMD ["python", "app.py"]
```

---

## Part 2: SAST with Semgrep

**Install Semgrep:**

```bash
pip install semgrep
```

**Create Semgrep config** (.semgrep.yml):

```yaml
rules:
  - id: sql-injection-format-string
    pattern: execute(f"... {$VAR} ...")
    message: Potential SQL injection using f-string
    severity: ERROR
    languages: [python]
    metadata:
      cwe: "CWE-89"
      owasp: "A03:2021 - Injection"
  
  - id: hardcoded-password
    pattern: password = "..."
    message: Hardcoded password detected
    severity: ERROR
    languages: [python]
  
  - id: flask-debug-true
    pattern: app.run(..., debug=True, ...)
    message: Flask debug mode enabled
    severity: WARNING
    languages: [python]
```

**Run Semgrep:**

```bash
# Scan with default rules
semgrep --config=auto app.py

# Scan with custom rules
semgrep --config=.semgrep.yml app.py

# Generate JSON report
semgrep --config=auto --json app.py > sast-results.json

# Fail on errors
semgrep --config=auto --error app.py
```

**Expected Output:**

```
app.py
  5: SQL injection detected
  18: Hardcoded credential
  30: XSS vulnerability
  35: Path traversal
  40: Debug mode enabled

Ran 1 files.
Found 5 vulnerabilities.
```

**Exercise 1**: Fix all SQL injection vulnerabilities

<details>
<summary>Solution</summary>

```python
@app.route('/api/user/<int:user_id>')  # Type constraint
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Fixed: Parameterized query
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    return jsonify(user) if user else ('Not found', 404)
```

</details>

---

## Part 3: DAST with OWASP ZAP

**Start the vulnerable application:**

```bash
python app.py
# App runs on http://localhost:5000
```

**Run ZAP Baseline Scan:**

```bash
# Using Docker
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://host.docker.internal:5000 \
  -r zap-report.html

# Or install ZAP locally and run
zap-cli quick-scan http://localhost:5000
```

**Configure ZAP for API Testing:**

**openapi.json**:

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Vulnerable API",
    "version": "1.0.0"
  },
  "paths": {
    "/api/user/{user_id}": {
      "get": {
        "parameters": [{
          "name": "user_id",
          "in": "path",
          "required": true,
          "schema": {"type": "string"}
        }]
      }
    },
    "/api/login": {
      "post": {
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "properties": {
                  "username": {"type": "string"},
                  "password": {"type": "string"}
                }
              }
            }
          }
        }
      }
    }
  }
}
```

**Run API Scan:**

```bash
docker run -t owasp/zap2docker-stable zap-api-scan.py \
  -t http://host.docker.internal:5000 \
  -f openapi \
  -r zap-api-report.html \
  -d openapi.json
```

**Exercise 2**: Analyze ZAP findings and identify top 3 critical issues

<details>
<summary>Expected Findings</summary>

1. SQL Injection in /api/user endpoint
2. XSS in /api/comment endpoint
3. Path Traversal in /api/file endpoint
4. Insecure authentication
5. Missing security headers

</details>

---

## Part 4: CI/CD Integration

**GitHub Actions Workflow** (.github/workflows/security.yml):

```yaml
name: Security Testing Pipeline

on: [push, pull_request]

jobs:
  sast:
    name: Static Analysis (SAST)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/owasp-top-ten
            p/secrets
      
      - name: Upload SAST results
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: semgrep.sarif
  
  build:
    name: Build Application
    runs-on: ubuntu-latest
    needs: sast
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t vulnapp:${{ github.sha }} .
      
      - name: Save image
        run: docker save vulnapp:${{ github.sha }} > app.tar
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: app-image
          path: app.tar
  
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Download image
        uses: actions/download-artifact@v3
        with:
          name: app-image
      
      - name: Load image
        run: docker load < app.tar
      
      - name: Run container
        run: |
          docker run -d -p 5000:5000 \
            --name vulnapp \
            vulnapp:${{ github.sha }}
          sleep 10
      
      - name: Wait for app to be ready
        run: |
          timeout 30 bash -c 'until curl -f http://localhost:5000/health; do sleep 1; done'
  
  dast:
    name: Dynamic Analysis (DAST)
    runs-on: ubuntu-latest
    needs: deploy-staging
    steps:
      - uses: actions/checkout@v3
      
      - name: ZAP Baseline Scan
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'http://localhost:5000'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'
      
      - name: Upload DAST results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: zap-report
          path: report_html.html
  
  security-gate:
    name: Security Gate
    runs-on: ubuntu-latest
    needs: [sast, dast]
    steps:
      - name: Check findings
        run: |
          # Download all results
          # Parse and count critical/high findings
          # Fail if thresholds exceeded
          
          CRITICAL=$(jq '.runs[].results[] | select(.level=="error")' results.sarif | wc -l)
          
          if [ "$CRITICAL" -gt 0 ]; then
            echo "❌ Security gate FAILED: $CRITICAL critical issues"
            exit 1
          fi
          
          echo "✅ Security gate PASSED"
```

---

## Part 5: Handling Findings

**Create findings dashboard:**

```python
# security_dashboard.py
import json
from collections import Counter

def analyze_findings(sast_file, dast_file):
    """Analyze security findings"""
    with open(sast_file) as f:
        sast = json.load(f)
    
    with open(dast_file) as f:
        dast = json.load(f)
    
    findings = {
        'total': 0,
        'by_severity': Counter(),
        'by_category': Counter(),
        'by_tool': {'sast': 0, 'dast': 0}
    }
    
    # Process SAST findings
    for result in sast.get('results', []):
        findings['total'] += 1
        findings['by_severity'][result['level']] += 1
        findings['by_category'][result['ruleId']] += 1
        findings['by_tool']['sast'] += 1
    
    # Process DAST findings
    for alert in dast.get('site', [{}])[0].get('alerts', []):
        findings['total'] += 1
        findings['by_severity'][alert['riskdesc']] += 1
        findings['by_category'][alert['alert']] += 1
        findings['by_tool']['dast'] += 1
    
    return findings

# Generate report
findings = analyze_findings('sast-results.json', 'dast-results.json')
print(f"Total findings: {findings['total']}")
print(f"By severity: {dict(findings['by_severity'])}")
print(f"SAST: {findings['by_tool']['sast']}, DAST: {findings['by_tool']['dast']}")
```

---

## Part 6: Security Gate Configuration

**security-gate.json**:

```json
{
  "thresholds": {
    "critical": 0,
    "high": 5,
    "medium": 20
  },
  "exceptions": [
    {
      "rule": "flask-debug-true",
      "file": "app.py",
      "reason": "Dev environment only",
      "expires": "2024-12-31"
    }
  ],
  "require_all_passed": true,
  "fail_on_new_findings": true
}
```

---

## Exercises

### Exercise 3: Fix All Vulnerabilities

Fix the 5 vulnerabilities identified:

1. SQL Injection
2. Hardcoded credentials
3. XSS
4. Path traversal
5. Debug mode

Verify with:

```bash
semgrep --config=auto app.py
# Should show 0 errors
```

### Exercise 4: Configure Security Gate

Create a security gate that:
- Blocks deployment if critical issues exist
- Allows up to 3 high-severity issues
- Sends notifications to Slack

### Exercise 5: Optimize Scan Time

Current pipeline takes ~10 minutes. Optimize to under 5 minutes by:
- Running SAST and build in parallel
- Caching dependencies
- Using incremental scanning

---

## Verification

Run the complete pipeline:

```bash
# Local testing
./run-security-tests.sh

# Expected output
✅ SAST: 0 critical issues
✅ Build: Success
✅ DAST: 0 critical issues
✅ Security Gate: PASSED
```

---

## Key Takeaways

- ✅ SAST finds code-level vulnerabilities early
- ✅ DAST finds runtime issues in deployed app
- ✅ Both are needed for complete coverage
- ✅ Security gates prevent insecure deployments
- ✅ Automation is critical for scale

**Next Lab**: [Container Security Hardening →](../lab-03-container-hardening/README.md)
