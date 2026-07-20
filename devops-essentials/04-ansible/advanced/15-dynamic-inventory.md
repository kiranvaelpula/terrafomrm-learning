# Dynamic Inventory

> **Automatically discover and manage infrastructure with dynamic inventory sources**

---

## 📖 What You'll Learn

- Dynamic inventory concepts
- AWS EC2 dynamic inventory
- Cloud provider integrations
- Custom inventory scripts
- Inventory plugins
- Best practices

---

## 🎯 What is Dynamic Inventory?

**Static inventory** - Manual host lists in files:
```ini
[webservers]
web01.example.com
web02.example.com
```

**Dynamic inventory** - Automatically discovered from external sources:
- Cloud providers (AWS, Azure, GCP)
- Virtualization platforms (VMware, OpenStack)
- Container orchestrators (Kubernetes, Docker)
- CMDBs and monitoring systems
- Custom sources via scripts/plugins

**Benefits:**
- No manual host management
- Always up-to-date
- Automatic grouping by tags/attributes
- Scales with infrastructure
- Single source of truth

---

## 🔌 Inventory Plugins

Modern Ansible uses **inventory plugins** (preferred over scripts).

### Available Plugins

```bash
# List all inventory plugins
ansible-doc -t inventory -l

# Common plugins:
# - aws_ec2
# - azure_rm
# - gcp_compute
# - openstack
# - vmware_vm_inventory
# - docker_swarm
# - kubernetes (k8s)
```

### Plugin Documentation

```bash
# View plugin documentation
ansible-doc -t inventory aws_ec2
ansible-doc -t inventory azure_rm
```

---

## ☁️ AWS EC2 Dynamic Inventory

### Prerequisites

```bash
# Install boto3
pip install boto3

# Configure AWS credentials
aws configure
# Or use environment variables:
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_DEFAULT_REGION="us-east-1"
```

### Basic Configuration

```yaml
# inventory/aws_ec2.yml
---
plugin: aws_ec2

regions:
  - us-east-1
  - us-west-2

# Filter instances
filters:
  instance-state-name: running

# Create groups
keyed_groups:
  # Group by instance type
  - key: instance_type
    prefix: type
  
  # Group by availability zone
  - key: placement.availability_zone
    prefix: az
  
  # Group by tag
  - key: tags.Environment
    prefix: env
  
  # Group by security group
  - key: security_groups | map(attribute='group_name') | list
    prefix: sg

# Set hostnames
hostnames:
  - tag:Name
  - private-ip-address

# Compose variables
compose:
  ansible_host: public_ip_address
  ansible_user: ubuntu
```

### Using AWS Inventory

```bash
# List inventory
ansible-inventory -i inventory/aws_ec2.yml --list

# Graph view
ansible-inventory -i inventory/aws_ec2.yml --graph

# Run playbook
ansible-playbook -i inventory/aws_ec2.yml site.yml

# Target specific group
ansible-playbook -i inventory/aws_ec2.yml -l env_production site.yml
```

### Advanced AWS Configuration

```yaml
# inventory/aws_ec2.yml
---
plugin: aws_ec2

# Multiple regions
regions:
  - us-east-1
  - us-west-2
  - eu-west-1

# Filters
filters:
  instance-state-name: running
  tag:Managed: ansible

# Include/exclude by tags
include_filters:
  - tag:Environment: production
  - tag:Environment: staging

exclude_filters:
  - tag:Status: deprecated

# Grouping
keyed_groups:
  # By instance type
  - key: instance_type
    prefix: type
    separator: ""
  
  # By environment tag
  - key: tags.Environment | default('untagged')
    prefix: env
  
  # By role tag
  - key: tags.Role | default('norole')
    prefix: role
  
  # By application tag
  - key: tags.Application
    prefix: app

# Hostname preferences (in order)
hostnames:
  - tag:Name
  - dns-name
  - private-ip-address

# Compose custom variables
compose:
  ansible_host: public_ip_address | default(private_ip_address)
  ansible_user: "{{ 'ubuntu' if 'ubuntu' in (tags.OS | default('')) else 'ec2-user' }}"
  environment: tags.Environment | default('unknown')
  application: tags.Application | default('none')

# Cache settings
cache: yes
cache_plugin: jsonfile
cache_timeout: 3600
cache_connection: /tmp/aws_inventory
```

---

## 🌩️ Azure Dynamic Inventory

### Prerequisites

```bash
# Install Azure SDK
pip install azure-cli

# Login
az login
```

### Azure Configuration

```yaml
# inventory/azure_rm.yml
---
plugin: azure_rm

# Authentication
auth_source: auto

# Include VMs
include_vm_resource_groups:
  - production-rg
  - staging-rg

# Filter
conditional_groups:
  webservers: "'web' in tags.role"
  databases: "'db' in tags.role"
  production: "tags.environment == 'production'"

# Grouping
keyed_groups:
  - prefix: tag
    key: tags
  
  - prefix: location
    key: location

# Hostname
hostvar_expressions:
  ansible_host: public_ipv4_addresses[0] | default(private_ipv4_addresses[0])
  ansible_user: "'azureuser'"
```

---

## 🔷 GCP Dynamic Inventory

### Prerequisites

```bash
# Install GCP SDK
pip install google-auth

# Authenticate
gcloud auth application-default login
```

### GCP Configuration

```yaml
# inventory/gcp_compute.yml
---
plugin: gcp_compute

# Projects
projects:
  - my-project-id

# Filters
filters:
  - status = RUNNING
  - labels.environment = production

# Grouping
keyed_groups:
  - key: labels.environment
    prefix: env
  
  - key: labels.role
    prefix: role
  
  - key: zone
    prefix: zone

# Hostname
hostnames:
  - name

compose:
  ansible_host: networkInterfaces[0].accessConfigs[0].natIP
  ansible_user: "'debian'"
```

---

## 🐳 Docker Dynamic Inventory

### Docker Swarm

```yaml
# inventory/docker_swarm.yml
---
plugin: docker_swarm

docker_host: unix://var/run/docker.sock

# Include containers
include_host_uri: yes
verbose_output: yes

# Grouping
keyed_groups:
  - key: labels
    prefix: label

# Compose
compose:
  ansible_connection: docker
  ansible_user: root
```

---

## ☸️ Kubernetes Dynamic Inventory

### Configuration

```yaml
# inventory/k8s.yml
---
plugin: kubernetes.core.k8s

# Connections (uses kubectl config)
connections:
  - namespaces:
      - default
      - production

# Grouping
keyed_groups:
  - key: labels
    prefix: label
  
  - key: namespace
    prefix: namespace

# Compose
compose:
  ansible_connection: kubectl
  ansible_kubectl_pod: metadata.name
  ansible_kubectl_namespace: metadata.namespace
```

---

## 📝 Custom Inventory Scripts

### Simple Python Script

```python
#!/usr/bin/env python3
"""
Custom dynamic inventory script
Returns JSON inventory format
"""

import json
import argparse

def get_inventory():
    """Return full inventory"""
    return {
        '_meta': {
            'hostvars': {
                'host1.example.com': {
                    'ansible_user': 'ubuntu',
                    'ansible_host': '192.168.1.10'
                },
                'host2.example.com': {
                    'ansible_user': 'centos',
                    'ansible_host': '192.168.1.11'
                }
            }
        },
        'webservers': {
            'hosts': ['host1.example.com', 'host2.example.com'],
            'vars': {
                'http_port': 80
            }
        },
        'databases': {
            'hosts': ['host2.example.com'],
            'vars': {
                'db_port': 5432
            }
        }
    }

def get_host(hostname):
    """Return variables for specific host"""
    inventory = get_inventory()
    return inventory['_meta']['hostvars'].get(hostname, {})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--host', action='store')
    args = parser.parse_args()

    if args.list:
        print(json.dumps(get_inventory(), indent=2))
    elif args.host:
        print(json.dumps(get_host(args.host), indent=2))
```

```bash
# Make executable
chmod +x inventory/custom.py

# Test
./inventory/custom.py --list
./inventory/custom.py --host host1.example.com

# Use with ansible
ansible-playbook -i inventory/custom.py site.yml
```

---

## 🔗 Multiple Inventory Sources

### Directory-Based Inventory

```
inventory/
├── 00-static.ini           # Static hosts
├── 10-aws_ec2.yml          # AWS dynamic
├── 20-azure_rm.yml         # Azure dynamic
└── 30-custom.py            # Custom script
```

```bash
# Ansible combines all sources
ansible-playbook -i inventory/ site.yml

# List merged inventory
ansible-inventory -i inventory/ --list
```

### Configuration

```ini
# ansible.cfg
[defaults]
inventory = ./inventory/

[inventory]
enable_plugins = aws_ec2, azure_rm, gcp_compute, host_list, ini
cache = yes
cache_plugin = jsonfile
cache_timeout = 3600
cache_connection = /tmp/ansible_inventory
```

---

## 🎨 Advanced Patterns

### Combining Static and Dynamic

```yaml
# inventory/static.yml
---
all:
  children:
    loadbalancers:
      hosts:
        lb01.example.com:
          ansible_host: 10.0.1.10
    
    # Dynamic groups referenced here
    webservers:
      vars:
        http_port: 80
```

```yaml
# inventory/aws_ec2.yml
---
plugin: aws_ec2
regions:
  - us-east-1

keyed_groups:
  - key: tags.Role
    prefix: ""  # No prefix, use tag value directly

# Creates 'webservers' group from tags
```

### Inventory Constructing

```yaml
# inventory/constructed.yml
---
plugin: constructed

# Source from other inventories
strict: false

# Create groups based on variables
groups:
  # Group by OS
  ubuntu: ansible_distribution == "Ubuntu"
  centos: ansible_distribution == "CentOS"
  
  # Group by memory
  high_memory: ansible_memtotal_mb >= 16384
  low_memory: ansible_memtotal_mb < 4096
  
  # Combined conditions
  prod_webservers: >
    'webservers' in group_names and
    environment == 'production'

# Compose new variables
compose:
  fqdn: ansible_hostname + "." + dns_domain
  is_production: environment == 'production'
```

---

## 📚 Complete Example

### Multi-Cloud Setup

```
inventory/
├── group_vars/
│   ├── all.yml
│   ├── webservers.yml
│   └── databases.yml
├── host_vars/
│   └── special-host.yml
├── 00-static.ini
├── 10-aws_ec2.yml
├── 20-azure_rm.yml
├── 30-gcp_compute.yml
└── 99-constructed.yml
```

**00-static.ini:**
```ini
[control]
ansible-controller ansible_connection=local
```

**10-aws_ec2.yml:**
```yaml
plugin: aws_ec2
regions: [us-east-1, us-west-2]
filters:
  instance-state-name: running
  tag:Managed: ansible

keyed_groups:
  - key: tags.Environment
    prefix: env
  - key: tags.Role
    prefix: role

compose:
  ansible_host: public_ip_address
```

**99-constructed.yml:**
```yaml
plugin: constructed

groups:
  production_web: >
    'env_production' in group_names and
    'role_webserver' in group_names
  
  all_databases: >
    'role_database' in group_names

compose:
  deployment_group: >
    environment + "_" + role
```

**Playbook:**
```yaml
---
- name: Deploy to multi-cloud
  hosts: production_web
  tasks:
    - debug:
        msg: "Deploying to {{ inventory_hostname }} in {{ deployment_group }}"
```

---

## ✅ Best Practices

1. **Use inventory plugins** - Preferred over scripts
2. **Cache inventory** - Improve performance
3. **Tag resources** - Enable auto-grouping
4. **Test inventory** - Use --list and --graph
5. **Combine sources** - Mix static and dynamic
6. **Use constructed plugin** - Create custom groups
7. **Document tags** - Standard tagging scheme
8. **Secure credentials** - Use IAM roles, not keys
9. **Version control** - Track inventory configs
10. **Monitor API limits** - Cache to avoid rate limits

---

## 🔗 What's Next?

- **Next:** [Ansible Tower/AWX](16-tower-awx.md)
- **Previous:** [Galaxy](14-galaxy.md)
- **Related:** [Variables & Facts](../intermediate/07-variables-facts.md)

---

**Pro Tip:** Use caching for dynamic inventory to speed up playbook execution and avoid API rate limits!
