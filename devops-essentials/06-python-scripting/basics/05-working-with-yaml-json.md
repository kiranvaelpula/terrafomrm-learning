# Working with YAML and JSON

> **DevOps lives on YAML and JSON — Kubernetes manifests, Docker Compose, Ansible playbooks, API responses, Terraform state. Mastering these in Python is non-negotiable.**

---

## 📖 JSON vs YAML

| Feature | JSON | YAML |
|---------|------|------|
| Syntax | Braces and quotes | Indentation-based |
| Readability | Moderate | High |
| Comments | ❌ Not supported | ✅ Supported (`#`) |
| Used by | APIs, configs, state files | K8s, Ansible, Docker Compose |
| Python module | `json` (built-in) | `pyyaml` (install needed) |
| Data types | string, number, bool, null, array, object | Same + dates, multiline |

```yaml
# Same data in both formats:

# YAML
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  replicas: 3
```

```json
{
  "apiVersion": "apps/v1",
  "kind": "Deployment",
  "metadata": {
    "name": "nginx",
    "labels": {
      "app": "nginx"
    }
  },
  "spec": {
    "replicas": 3
  }
}
```

---

## 📋 Working with JSON

### Reading JSON

```python
import json

# Parse JSON string → Python dict
json_string = '{"name": "web01", "port": 8080, "healthy": true}'
data = json.loads(json_string)      # loads = load string
print(data["name"])                  # "web01"
print(data["port"])                  # 8080
print(type(data))                    # <class 'dict'>

# Read JSON from file
with open("config.json") as f:
    config = json.load(f)            # load = load file

# Access nested data
print(config["database"]["host"])
print(config["servers"][0]["name"])
```

### Writing JSON

```python
# Python dict → JSON string
data = {
    "status": "deployed",
    "version": "2.0.1",
    "timestamp": "2026-08-10T14:30:00Z",
    "servers": ["web01", "web02"]
}

json_string = json.dumps(data)              # Compact single line
json_pretty = json.dumps(data, indent=2)    # Pretty printed
print(json_pretty)

# Write to file
with open("result.json", "w") as f:
    json.dump(data, f, indent=2)
```

### JSON Type Mapping (Python ↔ JSON)

| Python | JSON |
|--------|------|
| dict | object `{}` |
| list | array `[]` |
| str | string `""` |
| int, float | number |
| True/False | true/false |
| None | null |

### Practical: Parse API Response

```python
import requests
import json

# Call an API and work with JSON response
response = requests.get("https://api.github.com/users/octocat")
data = response.json()     # Shortcut for json.loads(response.text)

print(f"User: {data['login']}")
print(f"Repos: {data['public_repos']}")
print(f"Created: {data['created_at']}")

# Pretty print for debugging
print(json.dumps(data, indent=2))
```

---

## 📝 Working with YAML

```bash
pip install pyyaml
```

### Reading YAML

```python
import yaml

# Parse YAML string
yaml_string = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
"""

data = yaml.safe_load(yaml_string)
print(data["metadata"]["name"])      # "nginx"
print(data["spec"]["replicas"])      # 3
print(type(data))                    # <class 'dict'>


# Read YAML file
with open("deployment.yaml") as f:
    manifest = yaml.safe_load(f)

# Read file with MULTIPLE documents (separated by ---)
with open("all-resources.yaml") as f:
    documents = list(yaml.safe_load_all(f))
    for doc in documents:
        print(f"  Kind: {doc['kind']}, Name: {doc['metadata']['name']}")
```

**⚠️ ALWAYS use `yaml.safe_load()`, NEVER `yaml.load()`!**
`yaml.load()` can execute arbitrary Python code from YAML files — a massive security vulnerability.

### Writing YAML

```python
import yaml

# Python dict → YAML
config = {
    "apiVersion": "v1",
    "kind": "Service",
    "metadata": {
        "name": "my-service",
        "namespace": "production"
    },
    "spec": {
        "selector": {"app": "myapp"},
        "ports": [
            {"port": 80, "targetPort": 8080}
        ],
        "type": "ClusterIP"
    }
}

# Write to file
with open("service.yaml", "w") as f:
    yaml.dump(config, f, default_flow_style=False)
    # default_flow_style=False → block style (readable)

# To string
yaml_str = yaml.dump(config, default_flow_style=False)
print(yaml_str)

# Write multiple documents
documents = [service_manifest, deployment_manifest, configmap_manifest]
with open("all.yaml", "w") as f:
    yaml.dump_all(documents, f, default_flow_style=False)
```

---

## 🛠️ Practical DevOps Examples

### Update Kubernetes Deployment Image

```python
#!/usr/bin/env python3
"""Update container image in a Kubernetes deployment YAML."""

import yaml
import sys

def update_image(manifest_path, new_image):
    """Update the first container's image in a deployment."""
    # Read
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)
    
    # Validate
    if manifest.get("kind") != "Deployment":
        print(f"ERROR: Expected Deployment, got {manifest.get('kind')}")
        sys.exit(1)
    
    # Modify
    containers = manifest["spec"]["template"]["spec"]["containers"]
    old_image = containers[0]["image"]
    containers[0]["image"] = new_image
    
    # Write back
    with open(manifest_path, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False)
    
    print(f"Updated: {old_image} → {new_image}")

if __name__ == "__main__":
    update_image("deployment.yaml", "myapp:v2.0.1")
```

### Generate Config from Template

```python
#!/usr/bin/env python3
"""Generate environment-specific configs from a template."""

import yaml
import os

# Base config (shared across environments)
base_config = {
    "app_name": "my-webapp",
    "log_level": "INFO",
    "health_check_path": "/health"
}

# Environment-specific overrides
environments = {
    "dev": {
        "replicas": 1,
        "resources": {"cpu": "100m", "memory": "256Mi"},
        "domain": "dev.example.com",
        "debug": True
    },
    "staging": {
        "replicas": 2,
        "resources": {"cpu": "250m", "memory": "512Mi"},
        "domain": "staging.example.com",
        "debug": False
    },
    "production": {
        "replicas": 5,
        "resources": {"cpu": "500m", "memory": "1Gi"},
        "domain": "app.example.com",
        "debug": False
    }
}

# Generate config for each environment
for env_name, env_config in environments.items():
    config = {**base_config, **env_config, "environment": env_name}
    
    output_path = f"configs/{env_name}.yaml"
    os.makedirs("configs", exist_ok=True)
    
    with open(output_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"Generated: {output_path}")
```

### Parse and Analyze JSON Logs

```python
#!/usr/bin/env python3
"""Analyze JSON-formatted application logs."""

import json
from collections import Counter

errors = Counter()
total = 0

with open("app.log") as f:
    for line in f:
        try:
            entry = json.loads(line.strip())
            total += 1
            
            if entry.get("level") == "ERROR":
                errors[entry.get("message", "unknown")] += 1
                
        except json.JSONDecodeError:
            continue    # Skip non-JSON lines

print(f"Total entries: {total}")
print(f"Total errors: {sum(errors.values())}")
print("\nTop 5 errors:")
for error, count in errors.most_common(5):
    print(f"  {count:4d} | {error[:80]}")
```

---

## 🎯 Interview Quick Points

- `json.loads()` = string → dict, `json.load()` = file → dict
- `json.dumps()` = dict → string, `json.dump()` = dict → file
- `indent=2` for human-readable JSON output
- **Always** use `yaml.safe_load()` (never `yaml.load()` — security risk)
- `yaml.safe_load_all()` for multi-document YAML (separated by `---`)
- `yaml.dump(data, default_flow_style=False)` for readable YAML
- YAML is a superset of JSON (valid JSON is valid YAML)
- Both convert to Python dicts/lists — same operations apply
- `.json()` method on requests response = `json.loads(response.text)`
- Common pattern: read YAML → modify dict → write YAML back
