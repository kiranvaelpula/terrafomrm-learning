# Python for DevOps

> **Python is the most popular language in DevOps for automation, tooling, API integrations, and infrastructure management.**

---

## 📖 Why Python in DevOps?

Shell scripting is great for simple OS tasks, but when your automation needs grow — complex logic, API interactions, error handling, data parsing — Python becomes essential.

### When to use Python vs Shell:

| Scenario | Use Shell | Use Python |
|----------|-----------|------------|
| Run a few OS commands | ✅ | ❌ overkill |
| Parse JSON/YAML configs | ❌ messy | ✅ native |
| Call REST APIs | ❌ curl + jq hacks | ✅ requests library |
| Complex conditionals/logic | ❌ unreadable | ✅ clean |
| Error handling | ❌ basic (exit codes) | ✅ try/except |
| Work with AWS/Cloud APIs | ❌ AWS CLI + parsing | ✅ boto3 |
| > 50 lines of code | ❌ maintenance nightmare | ✅ |
| Quick file operations | ✅ one-liners | ❌ verbose |

**Rule of thumb:** If you're writing more than 50 lines or doing anything beyond basic OS commands, use Python.

---

## 🎯 What DevOps Engineers Do with Python

| Use Case | Libraries/Tools | Example |
|----------|----------------|---------|
| AWS automation | boto3 | Stop dev instances at night |
| API integration | requests | Health checks, webhook notifications |
| Config management | pyyaml, json | Parse/generate Kubernetes manifests |
| Server management | paramiko, fabric | SSH, deploy to multiple servers |
| Docker automation | docker SDK | Build, run, manage containers |
| Kubernetes | kubernetes client | Scale deployments, pod management |
| Monitoring | psutil, prometheus_client | Custom metrics, system checks |
| CI/CD scripts | subprocess, os | Build pipelines, deployment scripts |
| CLI tools | click, argparse | Custom DevOps commands |
| Log analysis | re (regex), json | Parse and aggregate log data |
| Infrastructure | pulumi, CDK | Infrastructure as code |

---

## 🏗️ Python vs Shell — Side by Side

### Example: Check disk usage and alert

**Shell version:**
```bash
#!/bin/bash
usage=$(df -h / | awk 'NR==2 {print int($5)}')
if [ $usage -gt 80 ]; then
  curl -sf -X POST "$SLACK_WEBHOOK" \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"Disk at ${usage}%\"}"
fi
```

**Python version:**
```python
#!/usr/bin/env python3
import shutil
import requests

usage = shutil.disk_usage("/")
percent = (usage.used / usage.total) * 100

if percent > 80:
    requests.post(SLACK_WEBHOOK, json={
        "text": f"Disk at {percent:.1f}%"
    })
```

Both work. But when you need to check 10 servers, parse the response, retry on failure, log results — Python scales better.

---

## 🔧 Setting Up Python for DevOps

### Install Python

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install python3 python3-pip

# Check version
python3 --version    # Should be 3.8+
pip3 --version
```

### Virtual Environments (CRITICAL for production)

A virtual environment isolates your project's packages from the system Python. Without it, packages conflict between projects.

```bash
# Create a virtual environment
python3 -m venv myproject-env

# Activate it
source myproject-env/bin/activate    # Linux/macOS
# Your prompt changes: (myproject-env) $

# Now pip installs go HERE, not system-wide
pip install boto3 requests pyyaml

# Deactivate when done
deactivate

# Save dependencies to file (for reproducibility)
pip freeze > requirements.txt

# Install from requirements file (on another machine)
pip install -r requirements.txt
```

**Why virtual environments matter:**
```
Project A needs: requests==2.28
Project B needs: requests==2.31
System Python: can only have ONE version

Virtual environments: each project has its own isolated packages
```

### Essential Libraries for DevOps

```bash
pip install boto3        # AWS SDK — manage EC2, S3, RDS, Lambda
pip install requests     # HTTP calls — REST APIs, webhooks
pip install pyyaml       # Parse/generate YAML (K8s, Ansible, configs)
pip install paramiko     # SSH connections to remote servers
pip install docker       # Docker SDK — manage containers
pip install kubernetes   # Kubernetes Python client
pip install psutil       # System monitoring (CPU, memory, disk)
pip install click        # Build CLI tools
pip install jinja2       # Template rendering
pip install schedule     # Task scheduling
pip install python-dotenv # Load .env files
```

---

## 📝 Your First DevOps Python Script

```python
#!/usr/bin/env python3
"""
Server Health Check Script
Checks disk, memory, CPU and reports status.
"""

import os
import sys
import shutil
import subprocess


def check_disk_usage(path="/", threshold=80):
    """Check if disk usage is below threshold."""
    usage = shutil.disk_usage(path)
    percent = (usage.used / usage.total) * 100
    
    if percent > threshold:
        print(f"  ✗ Disk: {percent:.1f}% (threshold: {threshold}%)")
        return False
    
    print(f"  ✓ Disk: {percent:.1f}%")
    return True


def check_memory(threshold=90):
    """Check if memory usage is below threshold."""
    # Read from /proc/meminfo (Linux)
    with open("/proc/meminfo") as f:
        lines = f.readlines()
    
    total = int(lines[0].split()[1])     # MemTotal
    available = int(lines[2].split()[1]) # MemAvailable
    percent = ((total - available) / total) * 100
    
    if percent > threshold:
        print(f"  ✗ Memory: {percent:.1f}% (threshold: {threshold}%)")
        return False
    
    print(f"  ✓ Memory: {percent:.1f}%")
    return True


def check_service(service_name):
    """Check if a systemd service is running."""
    result = subprocess.run(
        ["systemctl", "is-active", service_name],
        capture_output=True, text=True
    )
    
    is_active = result.stdout.strip() == "active"
    symbol = "✓" if is_active else "✗"
    status = "running" if is_active else "STOPPED"
    print(f"  {symbol} {service_name}: {status}")
    return is_active


def main():
    """Run all health checks."""
    print("=" * 40)
    print("  SERVER HEALTH CHECK")
    print(f"  Host: {os.uname().nodename}")
    print("=" * 40)
    
    all_ok = True
    
    print("\n📊 Resources:")
    all_ok &= check_disk_usage()
    all_ok &= check_memory()
    
    print("\n🔧 Services:")
    services = ["nginx", "docker", "sshd"]
    for svc in services:
        all_ok &= check_service(svc)
    
    print("\n" + "=" * 40)
    if all_ok:
        print("  ✓ All checks PASSED")
        sys.exit(0)
    else:
        print("  ✗ Some checks FAILED")
        sys.exit(1)


# This block runs only when script is executed directly
# NOT when imported as a module by another script
if __name__ == "__main__":
    main()
```

### Running the script:

```bash
# Make executable
chmod +x health_check.py

# Run directly
./health_check.py

# Or with python3
python3 health_check.py

# Check exit code (for CI/CD)
python3 health_check.py && echo "Healthy" || echo "Unhealthy"
```

---

## 📂 Python Script Structure Best Practices

```python
#!/usr/bin/env python3
"""Module docstring — what this script does."""

# 1. Standard library imports
import os
import sys
import json
import logging
from datetime import datetime

# 2. Third-party imports
import requests
import boto3
import yaml

# 3. Constants
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
API_URL = os.environ.get("API_URL", "https://api.example.com")
MAX_RETRIES = 3

# 4. Logging setup
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# 5. Functions
def do_something():
    """Docstring explaining what this function does."""
    pass

# 6. Main function
def main():
    """Entry point."""
    logger.info("Script started")
    do_something()
    logger.info("Script completed")

# 7. Entry point guard
if __name__ == "__main__":
    main()
```

---

## 🎯 Interview Quick Points

- Python preferred over shell for complex logic, APIs, and >50 lines of code
- Use virtual environments (`python3 -m venv`) to isolate dependencies
- `pip freeze > requirements.txt` captures exact package versions
- `subprocess.run()` replaces shell commands in Python
- `boto3` is essential for AWS automation
- `requests` library for HTTP/API calls
- Scripts should have `if __name__ == "__main__":` guard
- Use `#!/usr/bin/env python3` as shebang (portable)
- Use `logging` module instead of `print()` in production
- `sys.exit(0)` = success, `sys.exit(1)` = failure (same as shell)
- Python 3.8+ is the minimum for modern DevOps work
