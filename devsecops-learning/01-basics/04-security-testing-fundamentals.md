# Security Testing Fundamentals

## Learning Objectives

By the end of this chapter, you will:
- Understand different types of security testing
- Know when to use each testing method
- Implement basic security tests
- Integrate security testing into development workflow
- Understand the security testing pyramid
- Learn testing tools and their purposes

---

## The Security Testing Pyramid

```
                    ┌─────────────┐
                    │   Manual    │
                    │  Pentesting │
                    └─────────────┘
                ┌───────────────────┐
                │    DAST/IAST      │
                │  (Dynamic Tests)  │
                └───────────────────┘
            ┌───────────────────────────┐
            │         SAST              │
            │   (Static Analysis)       │
            └───────────────────────────┘
        ┌─────────────────────────────────┐
        │     Security Unit Tests         │
        │  (Developer-Written Tests)      │
        └─────────────────────────────────┘
```

**Principle**: More automated tests at the bottom, fewer manual tests at the top.

---

## Types of Security Testing

### 1. Static Application Security Testing (SAST)

**What**: Analyzes source code without executing it ("white-box" testing)

**When**: During development, in CI/CD pipeline

**Pros**:
- Fast feedback
- Finds coding errors early
- No need for running application
- Can check entire codebase

**Cons**:
- Higher false positives
- Can't find runtime issues
- Language-specific

**Example Tools**:
- Semgrep
- SonarQube
- Checkmarx
- Fortify

**Basic SAST Example**:

```python
# Vulnerable code that SAST will detect
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # SQL Injection vulnerability - SAST will flag this
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    
    return cursor.fetchone()

# Fixed version
def get_user_secure(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Parameterized query - SAST approves
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    
    return cursor.fetchone()
```

**Running SAST with Semgrep**:

```bash
# Install
pip install semgrep

# Scan with default rules
semgrep --config=auto .

# Scan for specific vulnerabilities
semgrep --config="p/sql-injection" .

# Output to JSON
semgrep --config=auto --json > results.json

# Fail on findings
semgrep --config=auto --error
```

---

### 2. Dynamic Application Security Testing (DAST)

**What**: Tests running application from outside ("black-box" testing)

**When**: In staging/pre-production environment

**Pros**:
- Finds runtime vulnerabilities
- Language-agnostic
- Tests actual deployed configuration
- Lower false positives

**Cons**:
- Slower than SAST
- Requires running application
- Can't test all code paths
- Later in development cycle

**Example Tools**:
- OWASP ZAP
- Burp Suite
- Acunetix
- Qualys

**Basic DAST Example**:

```bash
# OWASP ZAP baseline scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://example.com \
  -r report.html

# Full scan (more thorough)
docker run -t owasp/zap2docker-stable zap-full-scan.py \
  -t https://example.com \
  -r report.html

# API scan
docker run -t owasp/zap2docker-stable zap-api-scan.py \
  -t https://example.com/openapi.json \
  -f openapi \
  -r report.html
```

---

### 3. Interactive Application Security Testing (IAST)

**What**: Analyzes application from inside while it runs ("gray-box" testing)

**When**: During QA testing, integration tests

**Pros**:
- Lower false positives than SAST
- Identifies vulnerable data flows
- Pinpoints exact vulnerable code
- Works during normal testing

**Cons**:
- Requires instrumentation
- Performance overhead
- More complex setup

**Example Tools**:
- Contrast Security
- Synopsys Seeker
- Hdiv Detection

---

### 4. Software Composition Analysis (SCA)

**What**: Scans dependencies for known vulnerabilities

**When**: During build, continuously

**Pros**:
- Identifies vulnerable libraries
- Tracks license compliance
- Automated and fast
- Low false positives

**Cons**:
- Only finds known CVEs
- Doesn't find custom code issues

**Example**:

```bash
# npm audit
npm audit
npm audit fix

# Snyk
npm install -g snyk
snyk test
snyk monitor

# Safety (Python)
pip install safety
safety check

# OWASP Dependency-Check
dependency-check --project MyApp --scan ./
```

---

## Security Unit Tests

**Developer-written tests for security:**

### Example 1: Authentication Tests

```python
# test_auth.py
import pytest
from app import app

def test_login_requires_credentials():
    """Test that login requires username and password"""
    client = app.test_client()
    
    # No credentials
    response = client.post('/api/login', json={})
    assert response.status_code == 400
    
    # Missing password
    response = client.post('/api/login', json={'username': 'admin'})
    assert response.status_code == 400

def test_login_with_invalid_credentials():
    """Test that invalid credentials are rejected"""
    client = app.test_client()
    
    response = client.post('/api/login', json={
        'username': 'admin',
        'password': 'wrong_password'
    })
    assert response.status_code == 401

def test_sql_injection_prevention():
    """Test that SQL injection is prevented"""
    client = app.test_client()
    
    # Attempt SQL injection
    response = client.post('/api/login', json={
        'username': "admin' OR '1'='1",
        'password': "password"
    })
    assert response.status_code == 401  # Should fail, not return success

def test_xss_prevention():
    """Test that XSS is prevented"""
    client = app.test_client()
    
    response = client.post('/api/comment', json={
        'text': '<script>alert("XSS")</script>'
    })
    
    data = response.get_json()
    # Script tags should be escaped or removed
    assert '<script>' not in data['text']
```

### Example 2: Authorization Tests

```python
# test_authorization.py
def test_user_cannot_access_admin_endpoint():
    """Test that regular users can't access admin endpoints"""
    client = app.test_client()
    
    # Login as regular user
    login_response = client.post('/api/login', json={
        'username': 'user',
        'password': 'user_password'
    })
    token = login_response.get_json()['token']
    
    # Try to access admin endpoint
    response = client.get(
        '/api/admin/users',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 403  # Forbidden

def test_cannot_modify_other_users_data():
    """Test that users can only modify their own data"""
    client = app.test_client()
    
    # Login as user1
    login = client.post('/api/login', json={
        'username': 'user1',
        'password': 'password1'
    })
    token = login.get_json()['token']
    
    # Try to update user2's profile
    response = client.put(
        '/api/users/user2/profile',
        json={'email': 'hacked@evil.com'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 403
```

### Example 3: Input Validation Tests

```python
# test_input_validation.py
def test_email_validation():
    """Test that invalid emails are rejected"""
    client = app.test_client()
    
    invalid_emails = [
        'not-an-email',
        '@example.com',
        'user@',
        'user @example.com',
        '<script>alert("xss")</script>@example.com'
    ]
    
    for email in invalid_emails:
        response = client.post('/api/register', json={
            'username': 'testuser',
            'email': email,
            'password': 'Password123!'
        })
        assert response.status_code == 400

def test_password_complexity():
    """Test that weak passwords are rejected"""
    client = app.test_client()
    
    weak_passwords = [
        '123456',          # Too simple
        'password',        # Common password
        'abc',             # Too short
        'alllowercase',    # No uppercase/numbers
        'ALLUPPERCASE',    # No lowercase/numbers
    ]
    
    for password in weak_passwords:
        response = client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': password
        })
        assert response.status_code == 400
        assert 'password' in response.get_json()['error'].lower()
```

---

## Security Testing in CI/CD

### GitHub Actions Example

```yaml
# .github/workflows/security.yml
name: Security Testing

on: [push, pull_request]

jobs:
  # SAST
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/owasp-top-ten
  
  # SCA (Dependency Scanning)
  sca:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Snyk
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
  
  # Security Unit Tests
  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run security tests
        run: |
          pytest tests/security/ -v --cov=app
  
  # DAST (on staging)
  dast:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: ZAP Scan
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'https://staging.example.com'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'
```

---

## Vulnerability Severity Levels

### CVSS (Common Vulnerability Scoring System)

```yaml
Severity Levels:
  Critical (9.0-10.0):
    - Immediate action required
    - Can lead to complete system compromise
    - Example: Remote code execution
  
  High (7.0-8.9):
    - Fix within days
    - Significant security impact
    - Example: SQL injection, XSS
  
  Medium (4.0-6.9):
    - Fix within weeks
    - Moderate impact
    - Example: Information disclosure
  
  Low (0.1-3.9):
    - Fix in regular maintenance
    - Minor impact
    - Example: Verbose error messages
```

### Prioritization Example

```python
# vulnerability_prioritizer.py
def prioritize_vulnerability(vuln):
    """Prioritize vulnerabilities based on multiple factors"""
    score = vuln['cvss_score']
    
    # Adjust based on context
    if vuln['exploitable']:
        score += 2
    
    if vuln['has_public_exploit']:
        score += 2
    
    if vuln['internet_facing']:
        score += 1
    
    if vuln['contains_pii']:
        score += 1.5
    
    # Calculate priority
    if score >= 9:
        return 'P0-Critical'
    elif score >= 7:
        return 'P1-High'
    elif score >= 4:
        return 'P2-Medium'
    else:
        return 'P3-Low'
```

---

## False Positives vs False Negatives

### Handling False Positives

**False Positive**: Tool reports vulnerability that isn't actually exploitable

```python
# Example: SAST flags this as SQL injection
def get_user_by_id(user_id):
    # user_id is validated and type-checked
    assert isinstance(user_id, int)
    
    query = f"SELECT * FROM users WHERE id = {user_id}"
    # This is safe because user_id is an integer
    # But SAST might still flag it
```

**Suppression**:

```yaml
# semgrep-suppressions.yaml
rules:
  - id: sql-injection
    paths:
      - app/models.py
    justification: "Integer parameters are type-checked"
    expiration: "2024-12-31"
```

### Reducing False Positives

1. **Tune scanner rules** for your codebase
2. **Provide context** to tools
3. **Review and suppress** legitimate findings
4. **Train team** on common patterns
5. **Update tools** regularly

---

## Security Testing Checklist

### Before Code Commit
- [ ] Run security unit tests
- [ ] Run SAST locally
- [ ] Check for hardcoded secrets
- [ ] Review security-sensitive code changes

### In CI/CD Pipeline
- [ ] SAST on every commit
- [ ] SCA on dependencies
- [ ] Security unit tests pass
- [ ] No critical vulnerabilities
- [ ] Code coverage on security tests

### Before Deployment
- [ ] DAST scan completed
- [ ] Penetration test (for major releases)
- [ ] Security review approved
- [ ] Vulnerability remediation plan

### In Production
- [ ] Runtime monitoring active
- [ ] Security logs configured
- [ ] Incident response ready
- [ ] Regular security scans

---

## Hands-On Exercise

**Task**: Add security testing to a simple web application

**Application Code**:

```python
# app.py
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/api/users/<user_id>')
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Vulnerable to SQL injection!
    cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
    user = cursor.fetchone()
    return jsonify(user)

@app.route('/api/comment', methods=['POST'])
def add_comment():
    comment = request.json.get('text')
    # Vulnerable to XSS!
    return jsonify({'comment': comment})

if __name__ == '__main__':
    app.run()
```

**Your Tasks**:

1. **Write Security Unit Tests**:
   - Test SQL injection prevention
   - Test XSS prevention
   - Test authentication

2. **Fix Vulnerabilities**:
   - Use parameterized queries
   - Sanitize user input
   - Add authentication

3. **Add SAST**:
   - Run Semgrep
   - Fix findings
   - Add to CI/CD

4. **Add SCA**:
   - Scan dependencies
   - Update vulnerable packages

**Solution**:

```python
# app_secure.py
from flask import Flask, request, jsonify
import sqlite3
import html

app = Flask(__name__)

@app.route('/api/users/<int:user_id>')  # Type validation
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Parameterized query - SQL injection prevented
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    return jsonify(user)

@app.route('/api/comment', methods=['POST'])
def add_comment():
    comment = request.json.get('text', '')
    # Sanitize input - XSS prevented
    safe_comment = html.escape(comment)
    return jsonify({'comment': safe_comment})

if __name__ == '__main__':
    app.run()
```

```python
# tests/test_security.py
import pytest
from app_secure import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_sql_injection_prevented(client):
    """Test SQL injection is blocked"""
    response = client.get("/api/users/1' OR '1'='1")
    # Should return 404 (not found) not 200 (found)
    assert response.status_code == 404

def test_xss_sanitized(client):
    """Test XSS is sanitized"""
    response = client.post('/api/comment', json={
        'text': '<script>alert("XSS")</script>'
    })
    data = response.get_json()
    # Script should be escaped
    assert '&lt;script&gt;' in data['comment']
    assert '<script>' not in data['comment']
```

---

## Summary

Key takeaways:
- ✅ Use multiple types of security testing (SAST, DAST, SCA)
- ✅ Write security-focused unit tests
- ✅ Integrate security testing into CI/CD
- ✅ Prioritize vulnerabilities by severity and context
- ✅ Handle false positives appropriately
- ✅ Test early and often

**Next**: [Building Your First Security Pipeline →](05-first-security-pipeline.md)
