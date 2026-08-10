# Working with APIs (requests library)

> **Most DevOps automation involves API calls — REST APIs, webhooks, cloud provider APIs, monitoring endpoints. The `requests` library makes this effortless.**

---

## 📖 What are REST APIs?

APIs let programs talk to each other over HTTP. In DevOps you interact with:
- Cloud APIs (AWS, GCP, Azure)
- CI/CD systems (Jenkins, GitHub Actions)
- Monitoring (Prometheus, Datadog, PagerDuty)
- Communication (Slack, Teams webhooks)
- Container registries, Vault, Kubernetes API

```
Your Script ──HTTP Request──▶ API Server
                              │
Your Script ◀──JSON Response── │
```

---

## 🔧 Setup

```bash
pip install requests
```

---

## 🎯 HTTP Methods

```python
import requests

# GET — Retrieve data
response = requests.get("https://api.example.com/servers")

# POST — Create something new
response = requests.post("https://api.example.com/servers", json={...})

# PUT — Update/replace entire resource
response = requests.put("https://api.example.com/servers/1", json={...})

# PATCH — Partially update a resource
response = requests.patch("https://api.example.com/servers/1", json={...})

# DELETE — Remove a resource
response = requests.delete("https://api.example.com/servers/1")
```

---

## 📋 GET Requests (Retrieve Data)

```python
import requests

# Simple GET
response = requests.get("https://api.github.com/users/octocat")

# Response object properties
print(response.status_code)    # 200
print(response.ok)             # True (status < 400)
print(response.json())         # Parse body as JSON → dict
print(response.text)           # Raw text body
print(response.headers)        # Response headers (dict-like)
print(response.url)            # Final URL (after redirects)
print(response.elapsed)        # Time taken

# GET with query parameters
params = {
    "state": "open",
    "per_page": 10,
    "sort": "created"
}
response = requests.get(
    "https://api.github.com/repos/org/repo/issues",
    params=params       # Appends ?state=open&per_page=10&sort=created
)

# GET with authentication
headers = {
    "Authorization": f"Bearer {os.environ['API_TOKEN']}",
    "Accept": "application/json"
}
response = requests.get("https://api.example.com/data", headers=headers)
```

---

## 📤 POST Requests (Create Data)

```python
# POST with JSON body (most common)
payload = {
    "name": "new-server",
    "environment": "production",
    "instance_type": "t3.large"
}

response = requests.post(
    "https://api.example.com/servers",
    json=payload,                          # Automatically sets Content-Type
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 201:            # 201 = Created
    new_server = response.json()
    print(f"Created server: {new_server['id']}")
```

---

## 🛡️ Error Handling for API Calls

```python
import requests
import sys

def api_call(method, url, **kwargs):
    """Make API call with proper error handling."""
    try:
        response = requests.request(
            method, url,
            timeout=10,          # ALWAYS set timeout (prevents hanging forever)
            **kwargs
        )
        response.raise_for_status()   # Raises HTTPError for 4xx/5xx
        return response
        
    except requests.exceptions.Timeout:
        print(f"ERROR: Request to {url} timed out")
        return None
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Cannot connect to {url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: HTTP {e.response.status_code}: {e.response.text[:200]}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Unexpected error: {e}")
        return None


# Usage
response = api_call("GET", "https://api.example.com/health")
if response:
    data = response.json()
```

---

## 🔄 Retry Logic

```python
import time
import requests

def api_call_with_retry(url, max_retries=3, backoff=2):
    """Call API with exponential backoff retry."""
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except (requests.exceptions.RequestException) as e:
            if attempt == max_retries:
                raise
            
            wait = backoff ** attempt
            print(f"  Attempt {attempt} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)

# Usage
data = api_call_with_retry("https://api.example.com/status")
```

---

## 🛠️ Practical DevOps API Scripts

### Multi-Endpoint Health Checker

```python
#!/usr/bin/env python3
"""Check health of multiple API endpoints."""

import requests
import sys
import time

ENDPOINTS = [
    {"name": "API",      "url": "https://api.example.com/health"},
    {"name": "Frontend", "url": "https://app.example.com"},
    {"name": "Auth",     "url": "https://auth.example.com/status"},
    {"name": "Database", "url": "http://db-proxy:5432/health"},
]

def check_endpoint(name, url, timeout=5):
    """Check single endpoint health."""
    start = time.time()
    try:
        response = requests.get(url, timeout=timeout)
        elapsed = (time.time() - start) * 1000    # ms
        
        if response.status_code == 200:
            return True, f"OK ({elapsed:.0f}ms)"
        else:
            return False, f"HTTP {response.status_code} ({elapsed:.0f}ms)"
            
    except requests.exceptions.Timeout:
        return False, "TIMEOUT"
    except requests.exceptions.ConnectionError:
        return False, "CONNECTION REFUSED"
    except Exception as e:
        return False, str(e)


def main():
    print("╔══════════════════════════════════════╗")
    print("║       HEALTH CHECK REPORT            ║")
    print("╚══════════════════════════════════════╝")
    
    failed = []
    
    for endpoint in ENDPOINTS:
        ok, message = check_endpoint(endpoint["name"], endpoint["url"])
        symbol = "✓" if ok else "✗"
        print(f"  {symbol} {endpoint['name']:12} — {message}")
        
        if not ok:
            failed.append(endpoint["name"])
    
    print()
    if failed:
        print(f"  ❌ {len(failed)} endpoint(s) DOWN: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("  ✅ All endpoints healthy")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

### Slack Notification Function

```python
import requests
import os

def send_slack(message, color="good", title=None):
    """Send notification to Slack webhook."""
    webhook = os.environ.get("SLACK_WEBHOOK")
    if not webhook:
        print("WARNING: SLACK_WEBHOOK not set, skipping notification")
        return
    
    payload = {
        "attachments": [{
            "color": color,       # "good"=green, "warning"=yellow, "danger"=red
            "title": title or "Notification",
            "text": message,
            "footer": f"DevOps Bot | {os.uname().nodename}"
        }]
    }
    
    try:
        response = requests.post(webhook, json=payload, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"WARNING: Slack notification failed: {e}")


# Usage
send_slack("✅ Deployment v2.0.1 successful", color="good", title="Deploy")
send_slack("❌ Build failed", color="danger", title="CI/CD Alert")
```

---

## 🔐 Authentication Patterns

```python
# Bearer token (most common)
headers = {"Authorization": f"Bearer {token}"}
requests.get(url, headers=headers)

# Basic auth (username:password)
requests.get(url, auth=("username", "password"))

# API key in header
headers = {"X-API-Key": api_key}
requests.get(url, headers=headers)

# API key in query string
requests.get(url, params={"api_key": api_key})

# Session (reuse connection + cookies)
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {token}"})
session.get("https://api.example.com/endpoint1")    # Token included automatically
session.get("https://api.example.com/endpoint2")    # Same session
```

---

## 🎯 Interview Quick Points

- `requests.get()`, `.post()`, `.put()`, `.delete()` for HTTP methods
- `.json()` parses response body as Python dict
- `.status_code` gives HTTP status code
- `.raise_for_status()` throws exception on 4xx/5xx errors
- **Always use `timeout`** to prevent scripts hanging forever
- `json=` parameter auto-serializes dict and sets Content-Type header
- Use sessions (`requests.Session()`) for multiple calls to same API
- Implement retry with exponential backoff for transient failures
- Handle `ConnectionError`, `Timeout`, `HTTPError` separately
- `.ok` property is True when status < 400
- `params=dict` adds query string parameters to URL
