# Lab 01: Ansible Basics

> **Hands-on practice with installation, inventory, ad-hoc commands, and first playbook**

---

## Lab Overview

**Duration:** 2 hours  
**Difficulty:** Beginner  
**Prerequisites:** Linux basics, SSH knowledge

### Learning Objectives:
- Install and configure Ansible
- Create inventory files
- Run ad-hoc commands
- Write and execute first playbook
- Use basic modules
- Debug and troubleshoot

---

## Lab Environment

### Setup Requirements:

**Control Node:**
- Ubuntu 20.04 or RHEL 8
- Python 3.8+
- 2GB RAM, 10GB disk
- Internet access

**Managed Nodes (3):**
- Ubuntu 20.04 or RHEL 8
- SSH access enabled
- Python 3 installed
- User with sudo privileges

### Network Setup:
```
Control Node: 192.168.1.10
Node 1: 192.168.1.11 (web01)
Node 2: 192.168.1.12 (web02)
Node 3: 192.168.1.13 (db01)
```

---

## Exercise 1: Installation and Setup (20 minutes)

### Task 1.1: Install Ansible on Control Node

```bash
# Update system
sudo apt update

# Install Ansible (Ubuntu/Debian)
sudo apt install ansible -y

# Or RHEL/CentOS
sudo yum install epel-release -y
sudo yum install ansible -y

# Verify installation
ansible --version

# Expected output:
# ansible [core 2.12.x]
#   python version = 3.8.x
```

### Task 1.2: Configure SSH Access

```bash
# Generate SSH key on control node
ssh-keygen -t rsa -b 4096 -f ~/.ssh/ansible_lab -N ""

# Copy key to managed nodes
ssh-copy-id -i ~/.ssh/ansible_lab.pub user@192.168.1.11
ssh-copy-id -i ~/.ssh/ansible_lab.pub user@192.168.1.12
ssh-copy-id -i ~/.ssh/ansible_lab.pub user@192.168.1.13

# Test connection
ssh -i ~/.ssh/ansible_lab user@192.168.1.11 "hostname"
```

### Task 1.3: Configure Ansible

```bash
# Create project directory
mkdir -p ~/ansible-lab
cd ~/ansible-lab

# Create ansible.cfg
cat > ansible.cfg <<EOF
[defaults]
inventory = inventory
remote_user = user
private_key_file = ~/.ssh/ansible_lab
host_key_checking = False
retry_files_enabled = False

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False
EOF
```

**Verification:**
```bash
ansible --version | grep "config file"
# Should show: config file = /home/user/ansible-lab/ansible.cfg
```

---

## Exercise 2: Inventory Management (30 minutes)

### Task 2.1: Create Basic Inventory

```bash
# Create inventory file
cat > inventory <<EOF
# Web servers
[webservers]
web01 ansible_host=192.168.1.11
web02 ansible_host=192.168.1.12

# Database servers
[databases]
db01 ansible_host=192.168.1.13

# All servers
[production:children]
webservers
databases

# Group variables
[webservers:vars]
http_port=80
max_clients=200

[databases:vars]
mysql_port=3306
max_connections=150
EOF
```

### Task 2.2: Verify Inventory

```bash
# List all hosts
ansible all --list-hosts

# Expected output:
#   hosts (3):
#     web01
#     web02
#     db01

# List specific group
ansible webservers --list-hosts

# Show host details
ansible-inventory --list

# Graph inventory
ansible-inventory --graph
```

### Task 2.3: Create Group Variables

```bash
# Create group_vars directory
mkdir -p group_vars

# Web servers variables
cat > group_vars/webservers.yml <<EOF
---
app_name: mywebapp
app_port: 8080
enable_ssl: false
log_level: info
EOF

# Database variables
cat > group_vars/databases.yml <<EOF
---
db_engine: mysql
db_version: "8.0"
backup_enabled: true
backup_retention_days: 7
EOF

# Common variables for all hosts
cat > group_vars/all.yml <<EOF
---
ntp_server: time.google.com
dns_servers:
  - 8.8.8.8
  - 8.8.4.4
timezone: UTC
EOF
```

**Verification:**
```bash
# Check variables for a host
ansible-inventory --host web01 | jq
```

---

## Exercise 3: Ad-hoc Commands (30 minutes)

### Task 3.1: Ping All Hosts

```bash
# Test connectivity
ansible all -m ping

# Expected output for each host:
# web01 | SUCCESS => {
#     "changed": false,
#     "ping": "pong"
# }
```

### Task 3.2: Gather Facts

```bash
# Gather all facts
ansible all -m setup

# Gather specific facts
ansible all -m setup -a "filter=ansible_distribution*"

# Save facts to file
ansible all -m setup --tree /tmp/facts
```

### Task 3.3: Run Shell Commands

```bash
# Check uptime
ansible all -m command -a "uptime"

# Check disk space
ansible all -m shell -a "df -h | grep -v loop"

# Check memory
ansible all -m command -a "free -h"

# Get OS information
ansible all -m command -a "cat /etc/os-release"
```

### Task 3.4: Package Management

```bash
# Update package cache
ansible all -m apt -a "update_cache=yes" --become

# Install package on web servers
ansible webservers -m apt -a "name=nginx state=present" --become

# Check installed version
ansible webservers -m shell -a "nginx -v"

# Remove package
ansible webservers -m apt -a "name=nginx state=absent" --become
```

### Task 3.5: File Operations

```bash
# Create directory
ansible all -m file -a "path=/tmp/ansible-test state=directory mode=0755" --become

# Create file
ansible all -m file -a "path=/tmp/ansible-test/test.txt state=touch mode=0644" --become

# Copy content to file
ansible all -m copy -a "content='Hello from Ansible\n' dest=/tmp/ansible-test/test.txt" --become

# Read file
ansible all -m command -a "cat /tmp/ansible-test/test.txt"

# Delete file
ansible all -m file -a "path=/tmp/ansible-test state=absent" --become
```

### Task 3.6: User Management

```bash
# Create user
ansible all -m user -a "name=testuser state=present shell=/bin/bash" --become

# Set user password (hashed)
ansible all -m user -a "name=testuser password={{ 'password123' | password_hash('sha512') }} update_password=always" --become

# Remove user
ansible all -m user -a "name=testuser state=absent remove=yes" --become
```

---

## Exercise 4: First Playbook (40 minutes)

### Task 4.1: Simple Playbook

```yaml
# playbooks/hello.yml
---
- name: My First Playbook
  hosts: all
  gather_facts: true
  
  tasks:
    - name: Print greeting
      debug:
        msg: "Hello from {{ inventory_hostname }}!"
    
    - name: Display OS information
      debug:
        msg: "Running {{ ansible_distribution }} {{ ansible_distribution_version }}"
    
    - name: Show current date/time
      debug:
        msg: "Current time: {{ ansible_date_time.iso8601 }}"
```

**Run the playbook:**
```bash
ansible-playbook playbooks/hello.yml
```

### Task 4.2: Install and Configure Web Server

```yaml
# playbooks/webserver.yml
---
- name: Configure Web Servers
  hosts: webservers
  become: true
  
  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"
    
    - name: Install Nginx
      apt:
        name: nginx
        state: present
    
    - name: Start and enable Nginx
      systemd:
        name: nginx
        state: started
        enabled: yes
    
    - name: Create web root directory
      file:
        path: /var/www/html/myapp
        state: directory
        owner: www-data
        group: www-data
        mode: '0755'
    
    - name: Deploy index page
      copy:
        content: |
          <!DOCTYPE html>
          <html>
          <head><title>{{ inventory_hostname }}</title></head>
          <body>
            <h1>Hello from {{ inventory_hostname }}</h1>
            <p>Configured by Ansible</p>
            <p>Server: {{ ansible_hostname }}</p>
            <p>IP: {{ ansible_default_ipv4.address }}</p>
          </body>
          </html>
        dest: /var/www/html/index.html
        owner: www-data
        group: www-data
        mode: '0644'
      notify: Restart Nginx
  
  handlers:
    - name: Restart Nginx
      systemd:
        name: nginx
        state: restarted
```

**Run the playbook:**
```bash
ansible-playbook playbooks/webserver.yml
```

**Verify:**
```bash
curl http://192.168.1.11
curl http://192.168.1.12
```

### Task 4.3: System Configuration Playbook

```yaml
# playbooks/system_config.yml
---
- name: Configure System Settings
  hosts: all
  become: true
  
  vars:
    packages_to_install:
      - vim
      - git
      - htop
      - curl
      - wget
    
    users_to_create:
      - name: devuser
        shell: /bin/bash
      - name: opuser
        shell: /bin/bash
  
  tasks:
    - name: Set hostname
      hostname:
        name: "{{ inventory_hostname }}"
    
    - name: Set timezone
      timezone:
        name: "{{ timezone }}"
    
    - name: Install packages
      apt:
        name: "{{ packages_to_install }}"
        state: present
    
    - name: Create users
      user:
        name: "{{ item.name }}"
        shell: "{{ item.shell }}"
        state: present
        create_home: yes
      loop: "{{ users_to_create }}"
    
    - name: Configure sudoers
      lineinfile:
        path: /etc/sudoers.d/ansible-users
        line: "{{ item.name }} ALL=(ALL) NOPASSWD:ALL"
        create: yes
        mode: '0440'
        validate: 'visudo -cf %s'
      loop: "{{ users_to_create }}"
    
    - name: Update /etc/hosts
      lineinfile:
        path: /etc/hosts
        line: "{{ hostvars[item]['ansible_host'] }} {{ item }}"
        state: present
      loop: "{{ groups['all'] }}"
    
    - name: Disable unnecessary services
      systemd:
        name: "{{ item }}"
        state: stopped
        enabled: no
      loop:
        - bluetooth
      ignore_errors: yes
```

**Run the playbook:**
```bash
ansible-playbook playbooks/system_config.yml
```

---

## Exercise 5: Debugging and Troubleshooting (20 minutes)

### Task 5.1: Check Mode (Dry Run)

```bash
# Run in check mode (no changes)
ansible-playbook playbooks/webserver.yml --check

# Show diff of changes
ansible-playbook playbooks/webserver.yml --check --diff
```

### Task 5.2: Step-by-Step Execution

```bash
# Execute tasks one by one
ansible-playbook playbooks/webserver.yml --step
```

### Task 5.3: Start at Specific Task

```bash
# Start from specific task
ansible-playbook playbooks/webserver.yml --start-at-task="Install Nginx"
```

### Task 5.4: Verbose Output

```bash
# Increase verbosity
ansible-playbook playbooks/webserver.yml -v    # verbose
ansible-playbook playbooks/webserver.yml -vv   # more verbose
ansible-playbook playbooks/webserver.yml -vvv  # very verbose
ansible-playbook playbooks/webserver.yml -vvvv # debug mode
```

### Task 5.5: Debug Playbook

```yaml
# playbooks/debug_example.yml
---
- name: Debug Examples
  hosts: localhost
  gather_facts: yes
  
  vars:
    my_variable: "Hello World"
    my_list:
      - item1
      - item2
      - item3
    my_dict:
      key1: value1
      key2: value2
  
  tasks:
    - name: Print variable
      debug:
        var: my_variable
    
    - name: Print with message
      debug:
        msg: "The variable value is: {{ my_variable }}"
    
    - name: Print list
      debug:
        var: my_list
    
    - name: Print dictionary
      debug:
        var: my_dict
    
    - name: Conditional debug
      debug:
        msg: "This is Ubuntu"
      when: ansible_distribution == "Ubuntu"
    
    - name: Print all variables (use carefully!)
      debug:
        var: hostvars[inventory_hostname]
      run_once: true
```

---

## Lab Challenges

### Challenge 1: Multi-tier Application

Create a playbook that:
- Installs MySQL on db01
- Configures web servers to connect to database
- Deploys a simple PHP application
- Ensures services are running and enabled

### Challenge 2: Inventory with Variables

Create an inventory with:
- Development, staging, production groups
- Different variables per environment
- Host-specific customizations

### Challenge 3: Facts Gathering

Write a playbook that:
- Gathers facts from all hosts
- Generates a report (HTML/Markdown)
- Includes CPU, memory, disk, network info
- Saves report to control node

---

## Validation

### Verification Commands:

```bash
# 1. Verify Ansible installation
ansible --version

# 2. Verify inventory
ansible-inventory --list

# 3. Test connectivity
ansible all -m ping

# 4. Check syntax
ansible-playbook playbooks/*.yml --syntax-check

# 5. Verify web servers
curl http://192.168.1.11
curl http://192.168.1.12

# 6. Check services
ansible webservers -m shell -a "systemctl status nginx"
```

### Expected Results:

- ✅ Ansible installed and configured
- ✅ All hosts reachable via SSH
- ✅ Inventory properly structured
- ✅ Ad-hoc commands execute successfully
- ✅ Playbooks run without errors
- ✅ Web servers respond on port 80
- ✅ Services started and enabled

---

## Common Issues and Solutions

### Issue 1: SSH Connection Failed
```bash
# Error: Permission denied (publickey,password)
# Solution: Verify SSH key is copied
ssh-copy-id -i ~/.ssh/ansible_lab.pub user@host

# Or check SSH config
ssh -i ~/.ssh/ansible_lab user@host -vvv
```

### Issue 2: Privilege Escalation Failed
```bash
# Error: Missing sudo password
# Solution: Add to inventory
ansible_become_pass=yourpassword

# Or use --ask-become-pass
ansible-playbook playbook.yml --ask-become-pass
```

### Issue 3: Module Not Found
```bash
# Error: The module X was not found
# Solution: Update Ansible or check spelling
ansible-doc -l | grep module_name
```

---

## Lab Completion

**Congratulations!** You have completed Lab 01: Ansible Basics.

### Skills Acquired:
- ✅ Ansible installation and configuration
- ✅ Inventory management
- ✅ Ad-hoc command execution
- ✅ Basic playbook creation
- ✅ Module usage
- ✅ Debugging techniques

### Next Steps:
- Complete Lab 02: Playbooks and Variables
- Review [Intermediate Topics](../../intermediate/README.md)
- Practice with more complex scenarios

---

**Duration:** ~2 hours  
**Difficulty:** Beginner  
**Status:** Complete

