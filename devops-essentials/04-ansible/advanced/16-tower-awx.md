# Ansible Tower/AWX

> **Enterprise automation platform with web UI, API, and RBAC**

---

## 📖 What You'll Learn

- Tower vs AWX differences
- Installation and setup
- Organizations and teams
- Projects and inventories
- Job templates and workflows
- RBAC and credentials
- API usage

---

## 🏢 What is Tower/AWX?

**Ansible Tower** (Commercial) / **AWX** (Open Source)

Enterprise features:
- **Web UI** - Visual dashboard and job management
- **REST API** - Programmatic access
- **RBAC** - Role-based access control
- **Job Scheduling** - Cron-style scheduling
- **Notifications** - Slack, email, webhooks
- **Audit Trail** - Complete logging
- **Clustering** - High availability
- **Inventory Management** - Dynamic and static
- **Credential Vault** - Secure secrets storage

**Use cases:**
- Multi-team automation
- Self-service provisioning
- Scheduled maintenance
- Compliance enforcement
- Centralized management

---

## 🚀 Installation

### AWX with Docker Compose

```bash
# Install prerequisites
sudo apt update
sudo apt install -y docker.io docker-compose ansible

# Clone AWX
git clone https://github.com/ansible/awx.git
cd awx/installer

# Configure inventory
cat > inventory <<EOF
[all]
localhost ansible_connection=local

[all:vars]
admin_password=admin123
secret_key=$(openssl rand -base64 30)
awx_web_hostname=awx.example.com
postgres_data_dir=/var/lib/pgdocker
host_port=80
host_port_ssl=443
docker_compose_dir=/var/lib/awx
EOF

# Install
ansible-playbook -i inventory install.yml

# Check status
docker ps
# Access: http://awx.example.com
# Username: admin
# Password: admin123
```

### AWX on Kubernetes

```yaml
# awx-operator.yml
apiVersion: v1
kind: Namespace
metadata:
  name: awx
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: awx-operator
  namespace: awx
spec:
  channel: release-0.30
  name: awx-operator
  source: operatorhubio-catalog
  sourceNamespace: olm
```

```yaml
# awx-instance.yml
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx
  namespace: awx
spec:
  service_type: LoadBalancer
  ingress_type: none
  hostname: awx.k8s.example.com
  admin_user: admin
  admin_email: admin@example.com
```

```bash
kubectl apply -f awx-operator.yml
kubectl apply -f awx-instance.yml

# Get password
kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d
```

---

## 🏗️ Core Concepts

### Organizations

Logical containers for teams, projects, and resources.

```python
# Via API
import requests

tower_url = "https://tower.example.com/api/v2"
auth = ("admin", "password")

# Create organization
org_data = {
    "name": "DevOps Team",
    "description": "Production automation"
}
response = requests.post(
    f"{tower_url}/organizations/",
    json=org_data,
    auth=auth
)
```

### Teams

Groups of users within organizations.

- **Permissions:**
  - Admin
  - Execute
  - Read
  - Use

### Projects

Links to playbook repositories (Git, SVN, etc.)

**Project Configuration:**
- SCM Type: Git
- SCM URL: https://github.com/org/ansible-playbooks.git
- SCM Branch: main
- Update on Launch: Yes

### Inventories

Static or dynamic host lists.

**Dynamic inventory:**
- AWS EC2
- Azure
- GCP
- VMware
- Custom scripts

---

## 🎯 Job Templates

Defined automation jobs.

### Create Job Template

**Settings:**
- Name: Deploy Web Application
- Job Type: Run
- Inventory: Production
- Project: Web App Playbooks
- Playbook: site.yml
- Credentials: SSH Key
- Variables:
```yaml
---
environment: production
app_version: "2.5.1"
```

### Template Options

```yaml
# Extra Variables (JSON)
{
  "environment": "production",
  "deploy_user": "ansible",
  "app_version": "{{ build_number }}"
}

# Job Tags
tags: "deploy,config"
skip_tags: "testing"

# Limits
limit: "webservers:&production"

# Options
- [x] Enable Privilege Escalation
- [x] Allow Simultaneous
- [ ] Enable Fact Cache
- [x] Enable Webhooks
```

---

## 🔐 Credentials

Secure storage for sensitive data.

### Credential Types

**Machine (SSH):**
```yaml
Username: ansible
SSH Private Key: [Upload key]
Private Key Passphrase: [Optional]
Privilege Escalation Method: sudo
```

**Source Control:**
```yaml
Username: git-user
Password/Token: ghp_xxx
```

**Cloud:**
```yaml
# AWS
Access Key: AKIAXXXXXXX
Secret Key: [Secret]

# Azure
Subscription ID: xxx
Client ID: xxx
Client Secret: xxx
Tenant ID: xxx
```

**Vault:**
```yaml
Vault Password: [Secret]
# Or
Vault Password File: /path/to/vault
```

---

## 🔄 Workflows

Chain multiple job templates.

### Workflow Example

```
Start
  ├─> Update Inventory (always)
  │   └─> Deploy to Staging (on success)
  │       ├─> Run Tests (on success)
  │       │   ├─> Deploy to Production (on success)
  │       │   │   └─> Notify Success
  │       │   └─> Rollback Staging (on failure)
  │       └─> Notify Failure (on failure)
  └─> Send Alert (on failure)
```

### Workflow Configuration

```json
{
  "name": "Production Deployment Workflow",
  "nodes": [
    {
      "id": 1,
      "unified_job_template": "update-inventory",
      "success_nodes": [2],
      "failure_nodes": [6]
    },
    {
      "id": 2,
      "unified_job_template": "deploy-staging",
      "success_nodes": [3],
      "failure_nodes": [6]
    },
    {
      "id": 3,
      "unified_job_template": "run-tests",
      "success_nodes": [4],
      "failure_nodes": [5]
    },
    {
      "id": 4,
      "unified_job_template": "deploy-production",
      "success_nodes": [7]
    },
    {
      "id": 5,
      "unified_job_template": "rollback-staging"
    },
    {
      "id": 6,
      "unified_job_template": "notify-failure"
    },
    {
      "id": 7,
      "unified_job_template": "notify-success"
    }
  ]
}
```

---

## 👥 RBAC (Role-Based Access Control)

### Permission Levels

**System Roles:**
- System Administrator
- System Auditor

**Organization Roles:**
- Admin
- Execute
- Project Admin
- Inventory Admin
- Credential Admin
- Workflow Admin
- Notification Admin
- Job Template Admin

### Example RBAC Setup

```python
# Create team
team_data = {
    "name": "Web Team",
    "organization": org_id
}

# Assign role
role_data = {
    "user": user_id,
    "role": "execute",
    "content_object": job_template_id
}
```

---

## 🔌 API Usage

### Authentication

```python
import requests

# Token authentication
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}

# Basic auth
auth = ("username", "password")
```

### Launch Job

```python
# Launch job template
job_data = {
    "extra_vars": {
        "environment": "production",
        "version": "2.5.1"
    },
    "limit": "webservers"
}

response = requests.post(
    f"{tower_url}/job_templates/{template_id}/launch/",
    json=job_data,
    headers=headers
)

job_id = response.json()["id"]
```

### Monitor Job

```python
# Get job status
response = requests.get(
    f"{tower_url}/jobs/{job_id}/",
    headers=headers
)

status = response.json()["status"]
# Status: pending, waiting, running, successful, failed

# Get job output
response = requests.get(
    f"{tower_url}/jobs/{job_id}/stdout/",
    headers=headers
)
print(response.text)
```

### Automation Script

```python
#!/usr/bin/env python3
"""
Tower API automation example
"""
import requests
import time

class TowerAPI:
    def __init__(self, url, token):
        self.url = url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def launch_job(self, template_id, extra_vars=None):
        """Launch job template"""
        data = {"extra_vars": extra_vars or {}}
        response = requests.post(
            f"{self.url}/job_templates/{template_id}/launch/",
            json=data,
            headers=self.headers
        )
        return response.json()["id"]
    
    def wait_for_job(self, job_id, timeout=3600):
        """Wait for job completion"""
        start = time.time()
        while time.time() - start < timeout:
            response = requests.get(
                f"{self.url}/jobs/{job_id}/",
                headers=self.headers
            )
            status = response.json()["status"]
            
            if status in ["successful", "failed", "error", "canceled"]:
                return status
            
            time.sleep(10)
        
        return "timeout"

# Usage
tower = TowerAPI("https://tower.example.com/api/v2", "token")

# Launch deployment
job_id = tower.launch_job(
    template_id=42,
    extra_vars={"version": "2.5.1"}
)

# Wait for completion
status = tower.wait_for_job(job_id)
print(f"Job completed with status: {status}")
```

---

## 📊 Notifications

### Configure Notifications

**Slack:**
```json
{
  "name": "Slack Notifications",
  "notification_type": "slack",
  "notification_configuration": {
    "token": "xoxb-xxx",
    "channels": ["#deployments"],
    "hex_color": "#00FF00"
  }
}
```

**Email:**
```json
{
  "name": "Email Notifications",
  "notification_type": "email",
  "notification_configuration": {
    "host": "smtp.example.com",
    "port": 587,
    "username": "notifications@example.com",
    "password": "secret",
    "sender": "tower@example.com",
    "recipients": ["team@example.com"],
    "use_tls": true
  }
}
```

**Webhook:**
```json
{
  "name": "Webhook Notification",
  "notification_type": "webhook",
  "notification_configuration": {
    "url": "https://api.example.com/webhook",
    "http_method": "POST",
    "headers": {
      "Authorization": "Bearer token"
    }
  }
}
```

---

## 📅 Scheduling

### Create Schedule

```json
{
  "name": "Nightly Backup",
  "rrule": "DTSTART:20260720T020000Z RRULE:FREQ=DAILY;INTERVAL=1",
  "unified_job_template": job_template_id,
  "enabled": true
}
```

**Schedule formats:**
- Daily: `FREQ=DAILY;INTERVAL=1`
- Weekly: `FREQ=WEEKLY;BYDAY=MO,WE,FR`
- Monthly: `FREQ=MONTHLY;BYMONTHDAY=1`

---

## ✅ Best Practices

1. **Use Organizations** - Separate teams and resources
2. **Implement RBAC** - Least privilege access
3. **Source Control Projects** - Git for all playbooks
4. **Credential Vault** - Never hardcode secrets
5. **Workflows** - Complex automation chains
6. **Notifications** - Alert on failures
7. **Audit Logs** - Review regularly
8. **API Automation** - CI/CD integration
9. **High Availability** - Cluster for production
10. **Backup** - Regular database backups

---

## 🔗 What's Next?

- **Next:** [Enterprise Patterns](20-enterprise-patterns.md)
- **Previous:** [Dynamic Inventory](15-dynamic-inventory.md)
- **Related:** [CI/CD Integration](19-cicd-integration.md)

---

**Pro Tip:** Use Tower/AWX for team collaboration and AWX for learning - they share the same features!
