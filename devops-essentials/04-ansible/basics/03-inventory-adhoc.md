# Inventory & Ad-hoc Commands

> **Master Ansible's inventory system and execute powerful one-liner commands**

---

## 📖 Overview

**Inventory** = List of managed hosts and groups  
**Ad-hoc Commands** = Quick one-liner operations without playbooks

**Learn:**
- Creating and organizing inventories
- Static vs dynamic inventory
- Grouping and variables
- Running ad-hoc commands effectively

**Time:** 15-20 minutes

---

## 📋 Inventory Basics

### What is an Inventory?

An inventory tells Ansible **what** hosts to manage and **how** to connect to them.

**Formats:**
- **INI** format (simple, recommended for small setups)
- **YAML** format (structured, recommended for complex setups)
- **Dynamic** scripts/plugins (cloud environments)

### Simple Inventory (INI)

**inventory/hosts:**
```ini
# Single host
webserver1.example.com

# Multiple hosts
dbserver1.example.com
dbserver2.example.com
appserver.example.com
```

**Test it:**
```bash
# Ping all hosts
ansible all -i inventory/hosts -m ping
```

---

## 🎯 Groups and Patterns

### Basic Groups

```ini
# Web servers
[webservers]
web1.example.com
web2.example.com
web3.example.com

# Database servers
[databases]
db1.example.com
db2.example.com

# Application servers
[appservers]
app1.example.com
app2.example.com
app3.example.com
```

### Group of Groups

```ini
[webservers]
web1.example.com
web2.example.com

[databases]
db1.example.com

[production:children]
webservers
databases

[staging:children]
appservers
```

### Range Patterns

```ini
# Number ranges
[webservers]
web[1:10].example.com  # web1 through web10

# Letter ranges
[databases]
db[a:e].example.com  # dba through dbe

# Padded numbers
[servers]
server[001:100].example.com  # server001 through server100
```

---

## 🔧 Host and Group Variables

### Host-Specific Variables

```ini
[webservers]
web1.example.com ansible_port=2222
web2.example.com ansible_user=admin
web3.example.com ansible_host=192.168.1.100
```

### Group Variables

```ini
[webservers]
web1.example.com
web2.example.com

[webservers:vars]
ansible_user=ubuntu
ansible_port=22
http_port=80
```

### Common Connection Variables

```ini
# SSH connection
ansible_host=192.168.1.10        # Actual IP/hostname
ansible_port=2222                # SSH port (default: 22)
ansible_user=admin               # SSH user
ansible_ssh_private_key_file=~/.ssh/key  # SSH key

# Python interpreter
ansible_python_interpreter=/usr/bin/python3

# Connection type
ansible_connection=ssh           # or local, docker, etc.

# Privilege escalation
ansible_become=true
ansible_become_user=root
ansible_become_method=sudo
```

---

## 📁 Advanced Inventory Organization

### Directory Structure (Recommended)

```
inventory/
├── production/
│   ├── hosts                 # Production hosts
│   ├── group_vars/
│   │   ├── all.yml          # Variables for all hosts
│   │   ├── webservers.yml   # Web server variables
│   │   └── databases.yml    # Database variables
│   └── host_vars/
│       ├── web1.yml         # web1-specific variables
│       └── db1.yml          # db1-specific variables
│
└── staging/
    ├── hosts
    ├── group_vars/
    └── host_vars/
```

### hosts File

**inventory/production/hosts:**
```ini
[webservers]
web1.prod.example.com
web2.prod.example.com

[databases]
db1.prod.example.com

[loadbalancers]
lb1.prod.example.com

[production:children]
webservers
databases
loadbalancers
```

### group_vars/all.yml

```yaml
---
# Variables for ALL hosts
ansible_user: ansible
ansible_ssh_private_key_file: ~/.ssh/ansible_key
ansible_python_interpreter: /usr/bin/python3

# Common variables
ntp_server: ntp.example.com
dns_servers:
  - 8.8.8.8
  - 8.8.4.4

environment: production
```

### group_vars/webservers.yml

```yaml
---
# Variables for webservers group
http_port: 80
https_port: 443
max_connections: 1000

apache_packages:
  - apache2
  - libapache2-mod-php

document_root: /var/www/html
```

### host_vars/web1.yml

```yaml
---
# Variables specific to web1
ansible_host: 192.168.1.10
server_id: 1
backup_enabled: true
monitoring_enabled: true
```

**Usage:**
```bash
# Use production inventory
ansible-playbook -i inventory/production site.yml

# Use staging inventory
ansible-playbook -i inventory/staging site.yml
```

---

## 📝 YAML Inventory Format

### YAML Inventory Example

**inventory.yml:**
```yaml
---
all:
  children:
    webservers:
      hosts:
        web1.example.com:
          ansible_host: 192.168.1.10
        web2.example.com:
          ansible_host: 192.168.1.11
      vars:
        http_port: 80
        ansible_user: ubuntu
    
    databases:
      hosts:
        db1.example.com:
          ansible_host: 192.168.1.20
          mysql_port: 3306
        db2.example.com:
          ansible_host: 192.168.1.21
          mysql_port: 3307
      vars:
        ansible_user: dbadmin
        ansible_become: true
    
    production:
      children:
        webservers:
        databases:
      vars:
        environment: production
        monitoring_enabled: true
```

**Usage:**
```bash
ansible-playbook -i inventory.yml site.yml
```

---

## 🎯 Target Patterns

### Pattern Types

```bash
# All hosts
ansible all -m ping

# Single host
ansible web1.example.com -m ping

# Single group
ansible webservers -m ping

# Multiple groups (OR)
ansible webservers:databases -m ping

# Intersection (AND)
ansible webservers:&production -m ping

# Exclusion (NOT)
ansible webservers:!staging -m ping

# Complex patterns
ansible webservers:&production:!web1.example.com -m ping

# Wildcards
ansible "web*.example.com" -m ping
ansible "~web[0-9]+" -m ping  # Regex

# Range
ansible "web[1:5]" -m ping
```

### Pattern Examples

```bash
# All production web servers except web1
ansible webservers:&production:!web1 -m ping

# Either webservers or databases in staging
ansible "webservers:databases:&staging" -m ping

# All servers starting with 'prod'
ansible "prod*" -m ping
```

---

## ⚡ Ad-hoc Commands

### What are Ad-hoc Commands?

Quick, **one-line commands** for:
- Testing connectivity
- Running quick commands
- Gathering information
- Making rapid changes
- Troubleshooting

**Syntax:**
```bash
ansible <pattern> -m <module> -a "<arguments>" [options]
```

### Basic Ad-hoc Examples

**1. Ping Test:**
```bash
# Test all hosts
ansible all -m ping

# Test web servers
ansible webservers -m ping

# Test specific host
ansible web1.example.com -m ping
```

**2. Run Shell Commands:**
```bash
# Check uptime
ansible all -m command -a "uptime"

# Check disk space
ansible all -m command -a "df -h"

# Check memory
ansible all -m command -a "free -m"

# Get hostname
ansible all -m command -a "hostname"
```

**3. File Operations:**
```bash
# Create file
ansible webservers -m file -a "path=/tmp/test.txt state=touch"

# Create directory
ansible webservers -m file -a "path=/tmp/mydir state=directory mode=0755"

# Delete file
ansible webservers -m file -a "path=/tmp/test.txt state=absent"

# Change permissions
ansible webservers -m file -a "path=/tmp/script.sh mode=0755"

# Change ownership
ansible webservers -m file -a "path=/var/www owner=www-data group=www-data"
```

**4. Package Management:**
```bash
# Install package (Ubuntu/Debian)
ansible webservers -m apt -a "name=nginx state=present" -b

# Install multiple packages
ansible webservers -m apt -a "name=vim,git,htop state=present" -b

# Update package
ansible webservers -m apt -a "name=nginx state=latest" -b

# Remove package
ansible webservers -m apt -a "name=apache2 state=absent" -b

# Update all packages
ansible all -m apt -a "upgrade=dist" -b

# Install on RedHat/CentOS
ansible webservers -m yum -a "name=nginx state=present" -b
```

**5. Service Management:**
```bash
# Start service
ansible webservers -m service -a "name=nginx state=started" -b

# Stop service
ansible webservers -m service -a "name=apache2 state=stopped" -b

# Restart service
ansible webservers -m service -a "name=nginx state=restarted" -b

# Enable service at boot
ansible webservers -m service -a "name=nginx enabled=yes" -b

# Check service status
ansible webservers -m service -a "name=nginx" -b
```

**6. User Management:**
```bash
# Create user
ansible all -m user -a "name=john state=present" -b

# Create user with home directory
ansible all -m user -a "name=jane state=present create_home=yes shell=/bin/bash" -b

# Add user to group
ansible all -m user -a "name=john groups=sudo append=yes" -b

# Remove user
ansible all -m user -a "name=john state=absent remove=yes" -b

# Set password (encrypted)
ansible all -m user -a "name=john password='$6$rounds=656000$...'" -b
```

**7. Copy Files:**
```bash
# Copy file to remote
ansible webservers -m copy -a "src=/local/file.txt dest=/remote/file.txt"

# Copy with permissions
ansible webservers -m copy -a "src=script.sh dest=/tmp/script.sh mode=0755"

# Copy with ownership
ansible webservers -m copy -a "src=config.conf dest=/etc/app/config.conf owner=root group=root mode=0644" -b
```

**8. Gather Facts:**
```bash
# Gather all facts
ansible web1 -m setup

# Filter specific facts
ansible web1 -m setup -a "filter=ansible_os_family"
ansible web1 -m setup -a "filter=ansible_distribution*"
ansible web1 -m setup -a "filter=ansible_memory_mb"

# Save facts to file
ansible web1 -m setup --tree /tmp/facts
```

---

## 🔐 Privilege Escalation

### Using Sudo (become)

```bash
# Run with sudo
ansible all -m command -a "whoami" -b
# Output: root

# Specify become user
ansible all -m command -a "whoami" -b --become-user=postgres
# Output: postgres

# Ask for sudo password
ansible all -m command -a "apt update" -b --ask-become-pass

# Become method
ansible all -m command -a "whoami" -b --become-method=su
```

---

## 📊 Real-World Ad-hoc Use Cases

### Use Case 1: Quick System Audit

```bash
# Check OS version on all servers
ansible all -m command -a "cat /etc/os-release" | grep -i "pretty_name"

# Check kernel version
ansible all -m command -a "uname -r"

# Check disk usage
ansible all -m command -a "df -h /" | grep -v ">>>"

# Check memory
ansible all -m command -a "free -h"

# Check running services
ansible all -m command -a "systemctl list-units --type=service --state=running" -b
```

### Use Case 2: Emergency Patch

```bash
# Update security patches across fleet
ansible all -m apt -a "upgrade=dist update_cache=yes" -b

# Restart services after patch
ansible webservers -m service -a "name=nginx state=restarted" -b

# Verify services running
ansible webservers -m command -a "systemctl status nginx" -b
```

### Use Case 3: Configuration Drift Detection

```bash
# Check nginx configuration
ansible webservers -m command -a "nginx -t" -b

# Verify file exists
ansible webservers -m stat -a "path=/etc/nginx/nginx.conf"

# Compare file checksums
ansible webservers -m stat -a "path=/etc/hosts" | grep checksum
```

### Use Case 4: Log Collection

```bash
# Get last 10 lines of syslog
ansible all -m shell -a "tail -10 /var/log/syslog" -b

# Search for errors
ansible webservers -m shell -a "grep -i error /var/log/nginx/error.log | tail -20" -b

# Fetch log files
ansible webservers -m fetch -a "src=/var/log/app.log dest=/tmp/logs/ flat=no"
```

---

## 💡 Ad-hoc Command Options

### Common Options

```bash
# Specify inventory
ansible all -i inventory/production -m ping

# Specify user
ansible all -u ubuntu -m ping

# Use specific SSH key
ansible all --private-key ~/.ssh/mykey -m ping

# Run in parallel (forks)
ansible all -f 50 -m ping  # 50 hosts at once

# Verbose output
ansible all -m ping -v    # Verbose
ansible all -m ping -vv   # More verbose
ansible all -m ping -vvv  # Debug

# Check mode (dry-run)
ansible all -m apt -a "name=nginx state=present" --check

# One-line mode
ansible all -m ping -o

# Limit to subset
ansible all -m ping --limit webservers
ansible all -m ping --limit "web1,web2"
```

---

## 🎯 Module Documentation

```bash
# List all modules
ansible-doc -l

# Show module documentation
ansible-doc ping
ansible-doc copy
ansible-doc service

# Show examples only
ansible-doc -s command

# Search modules
ansible-doc -l | grep docker
```

---

## 🧪 Testing and Debugging

### Test Connectivity

```bash
# Basic ping
ansible all -m ping

# With verbose output
ansible all -m ping -vvv

# Test specific SSH settings
ansible web1 -m ping -vvv \
    -u ubuntu \
    --private-key ~/.ssh/ansible_key

# Test sudo access
ansible all -m command -a "whoami" -b
```

### Debug Inventory

```bash
# List all hosts
ansible all --list-hosts

# List hosts in group
ansible webservers --list-hosts

# Show inventory graph
ansible-inventory --graph

# Show inventory variables
ansible-inventory --host web1

# Export inventory as JSON
ansible-inventory --list

# Verify inventory file
ansible-inventory -i inventory/hosts --list
```

---

## ⚠️ Best Practices

1. **Use Groups:** Organize hosts logically
2. **Variable Hierarchy:** Use `group_vars` and `host_vars`
3. **Separate Environments:** Different inventories for dev/staging/prod
4. **Document Variables:** Comment your inventory files
5. **Use Patterns:** Master targeting patterns
6. **Idempotent Modules:** Prefer `copy` over `command`
7. **Check Mode:** Test with `--check` first
8. **Version Control:** Store inventory in Git (encrypt secrets!)

---

## 🎓 Interview Questions

### Q1: What's the difference between static and dynamic inventory?
**A:**

**Static Inventory:**
- Fixed list of hosts in INI/YAML files
- Manually maintained
- Best for: Small, stable infrastructure

**Dynamic Inventory:**
- Queries external sources (AWS, Azure, GCP, etc.)
- Auto-discovers hosts
- Best for: Cloud, auto-scaling environments

Example dynamic inventory:
```bash
# AWS EC2 dynamic inventory
ansible-playbook -i aws_ec2.yml site.yml
```

### Q2: What's the inventory variable precedence?
**A:** From lowest to highest priority:
1. `group_vars/all`
2. `group_vars/groupname`
3. `host_vars/hostname`
4. Inventory file host variables
5. Inventory file group variables
6. Playbook group_vars
7. Playbook host_vars
8. Host facts
9. Registered variables
10. Extra vars (`-e` on command line) ⭐ Highest

### Q3: How do you handle inventory for multiple environments?
**A:** Best practice structure:
```
inventory/
├── production/
│   ├── hosts
│   ├── group_vars/
│   └── host_vars/
├── staging/
│   ├── hosts
│   ├── group_vars/
│   └── host_vars/
└── development/
    ├── hosts
    ├── group_vars/
    └── host_vars/
```

Usage:
```bash
ansible-playbook -i inventory/production site.yml
ansible-playbook -i inventory/staging site.yml
```

### Q4: When would you use ad-hoc commands vs playbooks?
**A:**

**Use Ad-hoc Commands for:**
- Quick tests (ping, connectivity)
- One-time tasks
- Troubleshooting
- Information gathering
- Rapid response (restart service, etc.)

**Use Playbooks for:**
- Complex multi-step tasks
- Repeatable processes
- Configuration management
- Application deployment
- Version-controlled automation

### Q5: What's the command vs shell module difference?
**A:**

**command module:**
- Executes commands directly (no shell)
- More secure (no shell injection)
- Can't use pipes, redirects, variables
- Faster
```bash
ansible all -m command -a "ls -la"  # Works
ansible all -m command -a "ls | grep test"  # Fails
```

**shell module:**
- Executes through shell (/bin/sh)
- Supports pipes, redirects, variables
- Less secure
- Slower
```bash
ansible all -m shell -a "ls | grep test"  # Works
ansible all -m shell -a "echo $HOME"  # Works
```

---

## 📚 Next Steps

Mastered inventory and ad-hoc commands! Next:

👉 **[Writing Your First Playbook](04-first-playbook.md)**

**You can now:**
- ✅ Create inventories (INI and YAML)
- ✅ Organize hosts in groups
- ✅ Use variables effectively
- ✅ Run powerful ad-hoc commands
- ✅ Target hosts with patterns
- ✅ Debug inventory issues

**Practice Challenge:**
Create an inventory with 3 web servers, 2 databases, and run these ad-hoc commands:
1. Ping all hosts
2. Check disk space on web servers
3. Restart nginx on all web servers
4. Gather OS facts from databases

---

**Status:** Inventory & Ad-hoc Mastered ✅  
**Time:** 15-20 minutes  
**Difficulty:** Beginner  
**Next:** Playbooks (the real power!)
