# SAST and DAST - Static and Dynamic Application Security Testing

## Learning Objectives
- Understand SAST vs DAST approaches
- Implement both testing methods
- Integrate security testing into CI/CD
- Interpret and fix security findings

---

## What is SAST?

**Static Application Security Testing (SAST)** analyzes source code, bytecode, or binaries without executing the application.

### Key Characteristics
- **White-box testing**: Full access to source code
- **Early detection**: Find issues during development
- **Fast feedback**: Integrated into IDE/CI
- **Language-specific**: Tools per programming language

### SAST Workflow
```
Source Code → SAST Tool → Security Findings → Developer Review → Fix
```

---

## What is DAST?

**Dynamic Application Security Testing (DAST)** analyzes running applications to find vulnerabilities.

### Key Characteristics
- **Black-box testing**: No source code access
- **Runtime detection**: Find issues in deployed apps
- **Language-agnostic**: Works with any technology
- **Real-world scenarios**: Tests actual attack vectors

### DAST Workflow
```
Running App → DAST Tool → Vulnerability Scan → Security Report → Remediation
```

---

## SAST vs DAST Comparison

| Aspect | SAST | DAST |
|--------|------|------|
| **Testing Method** | Code analysis | Runtime testing |
| **Access** | Source code required | No code needed |
| **Detection Phase** | Development | QA/Production |
| **Coverage** | Deep code paths | User-facing issues |
| **False Positives** | Higher | Lower |
| **Speed** | Fast (minutes) | Slower (hours) |
| **Cost** | Lower | Higher |
| **Best For** | Logic flaws, coding errors | Config issues, runtime flaws |

---

## Popular SAST Tools

### 1. SonarQube
```yaml
# .gitlab-ci.yml
sonarqube_scan:
  stage: test
  image: sonarsource/sonar-scanner-cli:latest
  script:
    - sonar-scanner 
      -Dsonar.projectKey=my-project
      -Dsonar.sources=src
      -Dsonar.host.url=$SONAR_HOST
      -Dsonar.login=$SONAR_TOKEN
  only:
    - merge_requests
    - develop
```

### 2. Semgrep
```bash
# Install
pip install semgrep

# Scan for OWASP Top 10
semgrep --config=auto .

# Scan with specific rules
semgrep --config "p/owasp-top-ten" --config "p/security-audit" .

# Output to JSON
semgrep --config=auto --json -o findings.json .
```

### 3. Bandit (Python)
```bash
# Install
pip install bandit

# Basic scan
bandit -r ./src

# Exclude test files
bandit -r ./src -x ./src/tests

# Specific severity levels
bandit -r ./src -ll -ii
# -ll: only show high severity
# -ii: only show medium+ confidence
```

### 4. ESLint Security Plugin (JavaScript)
```json
{
  "extends": ["plugin:security/recommended"],
  "plugins": ["security"],
  "rules": {
    "security/detect-object-injection": "error",
    "security/detect-non-literal-regexp": "error",
    "security/detect-unsafe-regex": "error"
  }
}
```

---

## Popular DAST Tools

### 1. OWASP ZAP (Zed Attack Proxy)
```bash
# Pull ZAP Docker image
docker pull owasp/zap2docker-stable

# Quick scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://example.com \
  -r zap-report.html

# Full scan with authentication
docker run -v $(pwd):/zap/wrk/:rw \
  -t owasp/zap2docker-stable zap-full-scan.py \
  -t https://example.com \
  -c zap-config.conf \
  -r zap-full-report.html
```

### 2. Nikto (Web Server Scanner)
```bash
# Install
apt-get install nikto

# Basic scan
nikto -h https://example.com

# Scan with specific port
nikto -h example.com -p 443

# Output to HTML
nikto -h https://example.com -o report.html -Format html
```

### 3. Burp Suite (Manual + Automated)
```bash
# Automated scan via API
curl -X POST https://burp-suite-api/v0.1/scan \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://example.com"],
    "scope": {
      "include": [{"rule": "https://example.com/.*"}]
    }
  }'
```

---

## Implementing SAST in CI/CD

### GitHub Actions Example
```yaml
# .github/workflows/sast.yml
name: SAST Security Scan

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  sast-scan:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/owasp-top-ten
      
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r ./src -f json -o bandit-report.json
        continue-on-error: true
      
      - name: Upload findings
        uses: actions/upload-artifact@v3
        with:
          name: sast-reports
          path: |
            bandit-report.json
            semgrep-results.json
      
      - name: Comment PR
        uses: actions/github-script@v6
        with:
          script: |
            const findings = require('./bandit-report.json');
            const critical = findings.filter(f => f.severity === 'HIGH');
            if (critical.length > 0) {
              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: `⚠️ Found ${critical.length} critical security issues!`
              });
            }
```

---

## Implementing DAST in CI/CD

### GitLab CI Example
```yaml
# .gitlab-ci.yml
stages:
  - build
  - deploy
  - dast

deploy_staging:
  stage: deploy
  script:
    - kubectl apply -f k8s/staging/
  environment:
    name: staging
    url: https://staging.example.com

dast_scan:
  stage: dast
  image: owasp/zap2docker-stable
  variables:
    DAST_WEBSITE: https://staging.example.com
  script:
    - mkdir -p /zap/wrk
    - zap-baseline.py 
      -t $DAST_WEBSITE 
      -r zap-baseline-report.html
      -J zap-baseline-report.json
  artifacts:
    when: always
    paths:
      - zap-baseline-report.html
      - zap-baseline-report.json
    expire_in: 30 days
  allow_failure: true
  only:
    - staging
    - production
```

---

## Fixing Common Vulnerabilities

### 1. SQL Injection (SAST Finding)

**Vulnerable Code:**
```python
# BAD: SQL Injection vulnerability
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
```

**Fixed Code:**
```python
# GOOD: Parameterized query
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_id,))

# Or using ORM
def get_user(user_id):
    return User.query.filter_by(id=user_id).first()
```

### 2. XSS - Cross-Site Scripting (DAST Finding)

**Vulnerable Code:**
```javascript
// BAD: Unescaped user input
function displayMessage(msg) {
  document.getElementById('output').innerHTML = msg;
}
```

**Fixed Code:**
```javascript
// GOOD: Escaped output
function displayMessage(msg) {
  const escaped = msg
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;");
  document.getElementById('output').innerHTML = escaped;
}

// BETTER: Use textContent
function displayMessage(msg) {
  document.getElementById('output').textContent = msg;
}
```

### 3. Hardcoded Secrets (SAST Finding)

**Vulnerable Code:**
```python
# BAD: Hardcoded credentials
API_KEY = "sk_live_abc123xyz"
DATABASE_URL = "postgresql://admin:password123@db.example.com/prod"
```

**Fixed Code:**
```python
# GOOD: Environment variables
import os

API_KEY = os.environ.get('API_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')

if not API_KEY:
    raise ValueError("API_KEY environment variable not set")
```

### 4. Insecure Deserialization (SAST Finding)

**Vulnerable Code:**
```python
# BAD: Unsafe pickle usage
import pickle

def load_user_data(data):
    return pickle.loads(data)  # RCE vulnerability
```

**Fixed Code:**
```python
# GOOD: Use safe serialization
import json

def load_user_data(data):
    return json.loads(data)

# Or with validation
from marshmallow import Schema, fields, ValidationError

class UserSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    age = fields.Int(validate=lambda n: 0 < n < 150)

def load_user_data(data):
    schema = UserSchema()
    try:
        return schema.loads(data)
    except ValidationError as err:
        raise ValueError(f"Invalid data: {err.messages}")
```

---

## Integrating Both SAST and DAST

### Complete Pipeline
```yaml
# Complete security testing pipeline
name: Security Testing Pipeline

on:
  pull_request:
  push:
    branches: [main]

jobs:
  # SAST runs on every commit
  sast:
    name: Static Analysis
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
      
      - name: Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: p/security-audit
      
      - name: Check Quality Gate
        run: |
          status=$(curl -s -u $SONAR_TOKEN: \
            $SONAR_HOST_URL/api/qualitygates/project_status?projectKey=$PROJECT_KEY \
            | jq -r '.projectStatus.status')
          
          if [ "$status" != "OK" ]; then
            echo "Quality gate failed!"
            exit 1
          fi

  # Build and deploy to staging
  deploy-staging:
    needs: sast
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: |
          # Your deployment commands here
          echo "Deployed to https://staging.example.com"

  # DAST runs after deployment
  dast:
    name: Dynamic Analysis
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - name: ZAP Scan
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'https://staging.example.com'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'
      
      - name: Upload DAST Results
        uses: actions/upload-artifact@v3
        with:
          name: dast-report
          path: report_html.html

  # Security gate - block if critical issues
  security-gate:
    needs: [sast, dast]
    runs-on: ubuntu-latest
    steps:
      - name: Check findings
        run: |
          # Logic to parse and evaluate security findings
          # Fail if critical vulnerabilities found
          critical_count=$(jq '.[] | select(.severity=="CRITICAL") | .severity' findings.json | wc -l)
          
          if [ $critical_count -gt 0 ]; then
            echo "❌ Found $critical_count critical vulnerabilities!"
            echo "❌ Deployment blocked"
            exit 1
          fi
          
          echo "✅ Security checks passed"
```

---

## Best Practices

### SAST Best Practices
1. **Run Early**: Integrate into IDE and pre-commit hooks
2. **Fail Fast**: Block builds on critical findings
3. **Baseline**: Track progress, don't aim for zero immediately
4. **Tune Rules**: Reduce false positives over time
5. **Developer Training**: Help devs understand findings
6. **Incremental**: Fix new issues, track legacy issues

### DAST Best Practices
1. **Test Realistically**: Use staging environment similar to prod
2. **Authenticate**: Scan authenticated areas of the app
3. **Schedule Wisely**: Run DAST during low-traffic periods
4. **Scope Correctly**: Define what to scan and what to exclude
5. **Iterate**: Start with baseline scans, add full scans gradually
6. **Correlate**: Link DAST findings with SAST results

### Combined Approach
```
Development → SAST (IDE) → SAST (CI) → Build → Deploy Staging → DAST → Security Gate → Production
```

---

## Handling False Positives

### Example: Reviewing Findings
```python
# findings_review.py
import json

def review_findings(findings_file, suppress_file):
    """Review and suppress false positives"""
    
    with open(findings_file) as f:
        findings = json.load(f)
    
    with open(suppress_file) as f:
        suppressions = json.load(f)
    
    real_issues = []
    
    for finding in findings:
        # Check if suppressed
        is_suppressed = any(
            s['rule_id'] == finding['rule_id'] and
            s['file'] == finding['file'] and
            s['reason']  # Must have reason
            for s in suppressions
        )
        
        if not is_suppressed:
            real_issues.append(finding)
    
    return real_issues

# suppressions.json
{
  "suppressions": [
    {
      "rule_id": "SQL_INJECTION",
      "file": "tests/test_db.py",
      "reason": "Test file with intentional SQL injection examples"
    }
  ]
}
```

---

## Metrics to Track

### Security Testing KPIs
```yaml
SAST Metrics:
  - scan_duration: < 10 minutes
  - critical_findings: 0
  - high_findings: < 5
  - false_positive_rate: < 20%
  - time_to_fix: < 2 days

DAST Metrics:
  - scan_coverage: > 80% of endpoints
  - scan_duration: < 2 hours
  - critical_vulnerabilities: 0
  - mean_time_to_remediate: < 7 days
  - retest_pass_rate: > 95%

Combined:
  - security_debt: trending down
  - vulnerabilities_per_release: < 3
  - security_test_coverage: > 90%
```

---

## Next Steps

1. Set up SAST tool in your project
2. Run first scan and review findings
3. Deploy staging environment
4. Configure DAST scanner
5. Integrate both into CI/CD
6. Establish security gates
7. Train team on remediation

---

## Additional Resources

- [OWASP SAST Guide](https://owasp.org/www-community/Source_Code_Analysis_Tools)
- [OWASP DAST Guide](https://owasp.org/www-community/Vulnerability_Scanning_Tools)
- [Semgrep Rules](https://semgrep.dev/explore)
- [ZAP Documentation](https://www.zaproxy.org/docs/)

**Next**: [Container Security →](07-container-security.md)
