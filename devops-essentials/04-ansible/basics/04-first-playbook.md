# First Playbook

> **Write your first Ansible playbook and automate multi-step tasks**

---

## 📖 Overview

**Playbooks** are Ansible's configuration, deployment, and orchestration language. Written in YAML, they define a series of tasks to execute on managed hosts.

**Why Playbooks?**
- **Repeatable:** Run same automation multiple times
- **Version Controlled:** Store in Git
- **Complex Logic:** Multi-step workflows
- **Idempotent:** Safe to re-run
- **Readable:** Self-documenting YAML

**Time:** 20 minutes  
**Difficulty:** Beginner

---

## 🎯 Playbook Structure

### Basic Anatomy

```yaml
---
# Play 1
- name: Configure web servers
  hosts: webservers
  become: yes
  
  tasks:
    - name: Install Apache
      apt:
        name: apache2
        state: present
    
    - name: Start Apache
      service:
        name: apache2
        state: started
```

### Components Explained

```yaml
---                    # YAML document start
- name:                # Play name (describes what this play does)
  hosts:               # Target hosts/groups from inventory
  become:              # Run as sudo (yes/no)
  vars:                # Variables for this play
  tasks:               # List of tasks to execute
    - name:            # Task name (should be descriptive)
      module:          # Ansible module to use
        param: value   # Module parameters
```

---

## 🚀 Your First Playbook

### Example 1: Simple Playbook

**ping-playbook.yml:**
```yaml
---
- name: Test connectivity to all servers
  hosts: all
  tasks:
    - name: Ping all hosts
      ping:
```

**Run it:**
```bash
ansible-playbook ping-playbook.yml

# Output:
PLAY [Test connectivity to all servers] ****

TASK [Ping all hosts] ****
ok: [web1.example.com]
ok: [web2.example.com]

PLAY RECAP ****
web1.example.com    : ok=1    changed=0
web2.example.com    : ok=1    changed=0
```

---

### Example 2: Install and Start Service

**webserver-setup.yml:**
```yaml
---
- name: Setup web server
  hosts: webservers
  become: yes
  
  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600
    
    - name: Install Apache
      apt:
        name: apache2
        state: present
    
    - name: Ensure Apache is started
      service:
        name: apache2
        state: started
        enabled: yes
    
    - name: Create a simple index page
      copy:
        content: "<h1>Hello from Ansible!</h1>"
        dest: /var/www/html/index.html
        owner: www-data
        group: www-data
        mode: '0644'
```

**Run it:**
```bash
ansible-playbook webserver-setup.yml

# Check the result
curl http://web1.example.com
# Output: <h1>Hello from Ansible!</h1>
```

---

## 📝 YAML Syntax Essentials

### YAML Basics

```yaml
---
# Comments start with #

# Strings (quotes optional for simple strings)
name: John Doe
name: "John Doe"
name: 'John Doe'

# Multi-line strings
description: |
  This is a
  multi-line string

# Numbers
port: 80
memory: 512

# Booleans
enabled: true
enabled: false
enabled: yes  # Also valid
enabled: no   # Also valid

# Lists (two ways)
packages:
  - vim
  - git
  - htop

# Or inline
packages: [vim, git, htop]

# Dictionaries
webserver:
  port: 80
  domain: example.com
  ssl: true

# Lists of dictionaries
users:
  - name: john
    uid: 1001
  - name: jane
    uid: 1002
```

### Common YAML Mistakes

```yaml
# ❌ WRONG - Inconsistent indentation
tasks:
  - name: Task 1
      apt:
        name: vim

# ✅ CORRECT - Use 2 spaces consistently
tasks:
  - name: Task 1
    apt:
      name: vim

# ❌ WRONG - Mixing tabs and spaces
tasks:
→ - name: Task 1    # Tab used

# ✅ CORRECT - Only spaces
tasks:
  - name: Task 1    # 2 spaces

# ❌ WRONG - No space after colon
name:Task 1

# ✅ CORRECT - Space after colon
name: Task 1
```

---

## 🎯 Multiple Plays in One Playbook

```yaml
---
# Play 1: Configure web servers
- name: Setup web servers
  hosts: webservers
  become: yes
  tasks:
    - name: Install Apache
      apt:
        name: apache2
        state: present

# Play 2: Configure database servers
- name: Setup database servers
  hosts: databases
  become: yes
  tasks:
    - name: Install MySQL
      apt:
        name: mysql-server
        state: present

# Play 3: Configure all servers
- name: Configure monitoring on all servers
  hosts: all
  become: yes
  tasks:
    - name: Install monitoring agent
      apt:
        name: telegraf
        state: present
```

---

## 🔧 Task Parameters

### Common Module Parameters

**apt module:**
```yaml
- name: Install multiple packages
  apt:
    name:
      - nginx
      - php-fpm
      - mysql-client
    state: present           # present, absent, latest
    update_cache: yes        # Update apt cache first
    cache_valid_time: 3600   # Cache valid for 1 hour
```

**service module:**
```yaml
- name: Manage service
  service:
    name: nginx
    state: started          # started, stopped, restarted, reloaded
    enabled: yes            # Enable at boot
```

**copy module:**
```yaml
- name: Copy file
  copy:
    src: /local/path/file.txt     # Local source
    dest: /remote/path/file.txt   # Remote destination
    owner: www-data
    group: www-data
    mode: '0644'               # File permissions
    backup: yes                # Backup existing file
```

**file module:**
```yaml
- name: Create directory
  file:
    path: /var/www/myapp
    state: directory          # directory, file, absent, link
    owner: www-data
    group: www-data
    mode: '0755'
    recurse: yes              # Recursive for directories
```

---

## 💪 Variables in Playbooks

### Play-Level Variables

```yaml
---
- name: Setup web server
  hosts: webservers
  become: yes
  vars:
    http_port: 80
    max_clients: 200
    admin_email: admin@example.com
  
  tasks:
    - name: Display variables
      debug:
        msg: "HTTP port is {{ http_port }}"
    
    - name: Create config from template
      copy:
        content: |
          Port={{ http_port }}
          MaxClients={{ max_clients }}
          AdminEmail={{ admin_email }}
        dest: /etc/app/config.ini
```

### Using Variables from Inventory

```yaml
# inventory/hosts
[webservers]
web1 http_port=80 domain=site1.com
web2 http_port=8080 domain=site2.com

# playbook.yml
---
- name: Configure virtual hosts
  hosts: webservers
  tasks:
    - name: Show server config
      debug:
        msg: "{{ inventory_hostname }} serves {{ domain }} on port {{ http_port }}"
```

### Variables from Files

**vars/main.yml:**
```yaml
---
packages:
  - vim
  - git
  - htop

admin_users:
  - alice
  - bob

app_config:
  port: 8080
  threads: 10
```

**playbook.yml:**
```yaml
---
- name: Setup server
  hosts: all
  vars_files:
    - vars/main.yml
  
  tasks:
    - name: Install packages
      apt:
        name: "{{ packages }}"
        state: present
```

---

## 🎯 Conditional Execution

### When Conditions

```yaml
---
- name: OS-specific tasks
  hosts: all
  become: yes
  
  tasks:
    - name: Install Apache on Ubuntu
      apt:
        name: apache2
        state: present
      when: ansible_distribution == "Ubuntu"
    
    - name: Install Apache on CentOS
      yum:
        name: httpd
        state: present
      when: ansible_distribution == "CentOS"
    
    - name: Only on production
      service:
        name: monitoring
        state: started
      when: environment == "production"
    
    - name: Task for specific version
      debug:
        msg: "Running on Ubuntu 20.04"
      when:
        - ansible_distribution == "Ubuntu"
        - ansible_distribution_version == "20.04"
```

---

## 🔄 Loops

### Simple Loop

```yaml
---
- name: Install multiple packages
  hosts: webservers
  become: yes
  
  tasks:
    - name: Install packages
      apt:
        name: "{{ item }}"
        state: present
      loop:
        - vim
        - git
        - htop
        - curl
        - wget
```

### Loop with Dictionaries

```yaml
---
- name: Create users
  hosts: all
  become: yes
  
  tasks:
    - name: Create multiple users
      user:
        name: "{{ item.name }}"
        uid: "{{ item.uid }}"
        groups: "{{ item.groups }}"
        state: present
      loop:
        - { name: alice, uid: 1001, groups: "sudo,developers" }
        - { name: bob, uid: 1002, groups: "developers" }
        - { name: charlie, uid: 1003, groups: "operators" }
```

---

## 🎨 Idempotency

### What is Idempotency?

**Idempotent** = Same result no matter how many times you run it

```yaml
# ✅ Idempotent - Safe to run multiple times
- name: Ensure Apache is installed
  apt:
    name: apache2
    state: present

# ❌ NOT Idempotent - Creates new file each time
- name: Append to file
  shell: echo "log entry" >> /var/log/app.log

# ✅ Idempotent alternative
- name: Ensure line exists in file
  lineinfile:
    path: /var/log/app.log
    line: "log entry"
    state: present
```

### Test Idempotency

```bash
# Run playbook first time
ansible-playbook site.yml

# Output: changed=5

# Run playbook second time (should be idempotent)
ansible-playbook site.yml

# Output: changed=0  ✅ Perfect!
```

---

## 🧪 Checking and Testing

### Syntax Check

```bash
# Check syntax without running
ansible-playbook --syntax-check playbook.yml

# Output (if valid):
playbook: playbook.yml
```

### Dry Run (Check Mode)

```bash
# See what would change without making changes
ansible-playbook --check playbook.yml

# With diff to see file changes
ansible-playbook --check --diff playbook.yml
```

### Step-by-Step Execution

```bash
# Prompt before each task
ansible-playbook --step playbook.yml

# Output:
Perform task: TASK: Install Apache (N)o/(y)es/(c)ontinue: 
```

### Limit to Specific Hosts

```bash
# Run only on specific hosts
ansible-playbook playbook.yml --limit web1

# Run on multiple hosts
ansible-playbook playbook.yml --limit "web1,web2"

# Run on group
ansible-playbook playbook.yml --limit webservers
```

---

## 📊 Real-World Example: LAMP Stack

**lamp-stack.yml:**
```yaml
---
- name: Install LAMP stack
  hosts: webservers
  become: yes
  vars:
    mysql_root_password: "SecurePassword123"
    domain: example.com
  
  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600
    
    - name: Install LAMP packages
      apt:
        name:
          - apache2
          - mysql-server
          - php
          - php-mysql
          - libapache2-mod-php
        state: present
    
    - name: Start and enable Apache
      service:
        name: apache2
        state: started
        enabled: yes
    
    - name: Start and enable MySQL
      service:
        name: mysql
        state: started
        enabled: yes
    
    - name: Create web directory
      file:
        path: /var/www/{{ domain }}
        state: directory
        owner: www-data
        group: www-data
        mode: '0755'
    
    - name: Deploy PHP test page
      copy:
        content: |
          <?php
          phpinfo();
          ?>
        dest: /var/www/{{ domain }}/info.php
        owner: www-data
        group: www-data
        mode: '0644'
    
    - name: Create Apache virtual host config
      copy:
        content: |
          <VirtualHost *:80>
              ServerName {{ domain }}
              DocumentRoot /var/www/{{ domain }}
              
              <Directory /var/www/{{ domain }}>
                  AllowOverride All
                  Require all granted
              </Directory>
              
              ErrorLog ${APACHE_LOG_DIR}/{{ domain }}_error.log
              CustomLog ${APACHE_LOG_DIR}/{{ domain }}_access.log combined
          </VirtualHost>
        dest: /etc/apache2/sites-available/{{ domain }}.conf
      notify: Restart Apache
    
    - name: Enable site
      command: a2ensite {{ domain }}.conf
      args:
        creates: /etc/apache2/sites-enabled/{{ domain }}.conf
      notify: Restart Apache
    
    - name: Disable default site
      command: a2dissite 000-default.conf
      args:
        removes: /etc/apache2/sites-enabled/000-default.conf
      notify: Restart Apache
  
  handlers:
    - name: Restart Apache
      service:
        name: apache2
        state: restarted
```

**Run it:**
```bash
ansible-playbook lamp-stack.yml

# Test
curl http://web1.example.com/info.php
```

---

## 🎭 Handlers

### What are Handlers?

**Handlers** = Tasks that run only when notified and only once at the end

```yaml
---
- name: Configure web server
  hosts: webservers
  become: yes
  
  tasks:
    - name: Update Apache config
      copy:
        src: apache.conf
        dest: /etc/apache2/apache2.conf
      notify: Restart Apache    # Notify handler
    
    - name: Update PHP config
      copy:
        src: php.ini
        dest: /etc/php/7.4/apache2/php.ini
      notify: Restart Apache    # Same handler
  
  handlers:
    - name: Restart Apache
      service:
        name: apache2
        state: restarted
```

**Behavior:**
- Handler runs **only if** notified
- Handler runs **once** even if notified multiple times
- Handler runs **at the end** of the play

---

## 🔍 Debug and Information

### Debug Module

```yaml
---
- name: Debug examples
  hosts: localhost
  vars:
    app_version: 2.5.1
  
  tasks:
    - name: Show a simple message
      debug:
        msg: "Deploying version {{ app_version }}"
    
    - name: Show variable value
      debug:
        var: ansible_distribution
    
    - name: Show multiple variables
      debug:
        msg: "OS: {{ ansible_distribution }} {{ ansible_distribution_version }}"
    
    - name: Conditional debug
      debug:
        msg: "This is production!"
      when: environment == "production"
```

### Gathering Facts

```yaml
---
- name: Show system information
  hosts: all
  
  tasks:
    - name: Display OS family
      debug:
        msg: "OS Family: {{ ansible_os_family }}"
    
    - name: Display IP address
      debug:
        msg: "IP: {{ ansible_default_ipv4.address }}"
    
    - name: Display memory
      debug:
        msg: "Memory: {{ ansible_memtotal_mb }} MB"
```

---

## 📋 Playbook Best Practices

1. **Descriptive Names**
```yaml
# ❌ Bad
- name: Task 1
  apt: name=nginx

# ✅ Good
- name: Install Nginx web server
  apt:
    name: nginx
    state: present
```

2. **Use state Parameter**
```yaml
# Always specify desired state
- name: Ensure Apache is installed
  apt:
    name: apache2
    state: present    # present, absent, latest

- name: Ensure Apache is running
  service:
    name: apache2
    state: started    # started, stopped, restarted
```

3. **One Task, One Purpose**
```yaml
# ❌ Bad - Multiple actions in shell
- name: Setup app
  shell: |
    mkdir /app
    chown www-data /app
    systemctl restart apache2

# ✅ Good - Separate tasks
- name: Create app directory
  file:
    path: /app
    state: directory
    owner: www-data

- name: Restart Apache
  service:
    name: apache2
    state: restarted
```

4. **Use become Wisely**
```yaml
# ✅ Play-level (all tasks need sudo)
- name: System setup
  hosts: all
  become: yes
  tasks:
    - name: Install package
      apt: name=vim

# ✅ Task-level (only specific tasks need sudo)
- name: Mixed tasks
  hosts: all
  tasks:
    - name: Check home directory
      command: pwd
    
    - name: Install package
      apt: name=vim
      become: yes
```

5. **Comments and Documentation**
```yaml
---
# Purpose: Configure production web servers
# Author: DevOps Team
# Last Updated: 2026-07-20

- name: Setup production web servers
  hosts: webservers
  become: yes
  
  # Variables for web server configuration
  vars:
    http_port: 80
    https_port: 443
  
  tasks:
    # Phase 1: Install required packages
    - name: Install Apache and PHP
      apt:
        name: [apache2, php]
        state: present
```

---

## 🎓 Interview Questions

### Q1: What's the difference between a play and a task?
**A:**
- **Play:** High-level grouping that targets specific hosts. One playbook can have multiple plays.
- **Task:** Individual action within a play (calls a module).

```yaml
---
# This is a PLAY
- name: Configure web servers
  hosts: webservers
  
  # These are TASKS
  tasks:
    - name: Install Apache    # Task 1
      apt: name=apache2
    
    - name: Start Apache      # Task 2
      service: name=apache2 state=started
```

### Q2: What is idempotency and why is it important?
**A:** **Idempotency** means running a playbook multiple times produces the same result - no unnecessary changes.

**Why important:**
- Safe to re-run playbooks
- No duplicate resources
- Predictable outcomes
- Enables continuous configuration management

**Example:**
```yaml
# Idempotent - checks if package exists first
- name: Ensure Apache is installed
  apt: name=apache2 state=present

# First run: installs Apache (changed=1)
# Second run: already installed (changed=0)
```

### Q3: When would you use handlers vs regular tasks?
**A:**

**Use Handlers for:**
- Service restarts (only when config changes)
- Cache clearing
- Triggering deployments
- Any action that should run only when something changes

**Use Regular Tasks for:**
- Standard configurations
- File operations
- Package installations
- Sequential operations

**Example:**
```yaml
tasks:
  - name: Update nginx config
    copy: src=nginx.conf dest=/etc/nginx/
    notify: Reload Nginx    # Handler
  
  - name: Install package
    apt: name=vim          # Regular task

handlers:
  - name: Reload Nginx
    service: name=nginx state=reloaded
```

### Q4: How do you test a playbook without making changes?
**A:** Multiple methods:

```bash
# 1. Syntax check
ansible-playbook --syntax-check playbook.yml

# 2. Dry run (check mode)
ansible-playbook --check playbook.yml

# 3. Dry run with diff
ansible-playbook --check --diff playbook.yml

# 4. Limit to test server
ansible-playbook playbook.yml --limit test-server

# 5. Step-by-step
ansible-playbook --step playbook.yml
```

### Q5: What's the difference between copy and template modules?
**A:**

**copy:**
- Copies files as-is
- No variable substitution
- Static content

```yaml
- name: Copy static file
  copy:
    src: file.txt
    dest: /tmp/file.txt
```

**template:**
- Uses Jinja2 templating
- Variable substitution
- Dynamic content

```yaml
# template.j2
Server={{ inventory_hostname }}
Port={{ http_port }}

# Task
- name: Deploy config from template
  template:
    src: template.j2
    dest: /etc/app/config.ini
```

---

## 📚 Next Steps

You've mastered playbook basics! Next up:

👉 **[Basic Modules Deep Dive](05-basic-modules.md)**

**You can now:**
- ✅ Write YAML playbooks
- ✅ Use variables and loops
- ✅ Implement idempotent tasks
- ✅ Use handlers effectively
- ✅ Test playbooks safely
- ✅ Apply best practices

**Practice Challenge:**
Create a playbook that:
1. Installs Nginx
2. Creates a custom web page
3. Configures a virtual host
4. Restarts Nginx only if config changes
5. Is fully idempotent

---

**Status:** First Playbook Complete ✅  
**Time:** 20 minutes  
**Difficulty:** Beginner  
**Next:** Dive deeper into modules!
