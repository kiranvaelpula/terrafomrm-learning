# Playbook Structure & Best Practices

> **Master playbook organization and writing maintainable automation code**

---

## 📖 What You'll Learn

- Playbook anatomy and structure
- Best practices for organization
- Directory layout patterns
- Naming conventions
- Documentation strategies
- Common pitfalls to avoid

---

## 🏗️ Playbook Anatomy

### Basic Structure

```yaml
---
# Playbook metadata
- name: Descriptive playbook name
  hosts: target_hosts
  become: yes
  vars:
    app_port: 8080
  
  tasks:
    - name: Task description
      module_name:
        parameter: value
```

### Complete Example

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: yes
  gather_facts: yes
  
  vars:
    http_port: 80
    max_clients: 200
  
  pre_tasks:
    - name: Update package cache
      apt:
        update_cache: yes
      when: ansible_os_family == "Debian"
  
  tasks:
    - name: Install Apache
      package:
        name: "{{ apache_package }}"
        state: present
    
    - name: Start Apache service
      service:
        name: "{{ apache_service }}"
        state: started
        enabled: yes
  
  post_tasks:
    - name: Verify web server
      uri:
        url: "http://{{ inventory_hostname }}"
        status_code: 200
  
  handlers:
    - name: restart apache
      service:
        name: "{{ apache_service }}"
        state: restarted
```

---

## 📁 Directory Structure

### Project Layout

```
ansible-project/
├── ansible.cfg              # Ansible configuration
├── inventory/
│   ├── production/
│   │   ├── hosts           # Production inventory
│   │   └── group_vars/
│   │       ├── all.yml
│   │       └── webservers.yml
│   └── staging/
│       ├── hosts           # Staging inventory
│       └── group_vars/
├── playbooks/
│   ├── site.yml            # Master playbook
│   ├── webservers.yml      # Web server config
│   └── databases.yml       # Database config
├── roles/
│   ├── common/
│   ├── webserver/
│   └── database/
├── group_vars/
│   ├── all.yml             # Variables for all hosts
│   └── webservers.yml      # Web server variables
├── host_vars/
│   └── web01.yml           # Host-specific variables
├── files/                  # Static files
├── templates/              # Jinja2 templates
├── vars/                   # Additional variables
└── README.md               # Documentation
```

### ansible.cfg Example

```ini
[defaults]
inventory = ./inventory/production/hosts
remote_user = ansible
host_key_checking = False
retry_files_enabled = False
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

---

## 📝 Naming Conventions

### Playbook Names

```yaml
# Good - descriptive and specific
deploy-webserver.yml
configure-database.yml
update-security-patches.yml

# Bad - vague
run.yml
test.yml
playbook1.yml
```

### Task Names

```yaml
# Good - action-oriented and clear
- name: Install Nginx web server
- name: Configure firewall rules for HTTP/HTTPS
- name: Deploy application version 2.5.1

# Bad - unclear or missing
- name: Install
- package: name=nginx
- name: Do stuff
```

### Variable Names

```yaml
# Good - descriptive with scope
web_server_port: 80
db_max_connections: 100
app_environment: production

# Bad - ambiguous
port: 80
max: 100
env: prod
```

---

## 🎯 Best Practices

### 1. Idempotency

```yaml
# Idempotent - safe to run multiple times
- name: Ensure Nginx is installed
  apt:
    name: nginx
    state: present

- name: Ensure Nginx is running
  service:
    name: nginx
    state: started
    enabled: yes
```

### 2. Use Modules, Not Commands

```yaml
# Good - use native modules
- name: Create user
  user:
    name: appuser
    state: present
    shell: /bin/bash

# Bad - using command module
- name: Create user
  command: useradd -s /bin/bash appuser
```

### 3. Check Mode Support

```yaml
# Support --check mode for dry runs
- name: Copy config file
  copy:
    src: app.conf
    dest: /etc/app/app.conf
  check_mode: yes
```

### 4. Error Handling

```yaml
- name: Start service
  service:
    name: myapp
    state: started
  register: result
  failed_when:
    - result.failed
    - "'already running' not in result.msg"
  
- name: Critical task
  command: /opt/app/critical_script.sh
  ignore_errors: no
```

### 5. Use Handlers

```yaml
tasks:
  - name: Update Apache configuration
    template:
      src: apache.conf.j2
      dest: /etc/apache2/apache.conf
    notify: restart apache

handlers:
  - name: restart apache
    service:
      name: apache2
      state: restarted
```

---

## 🔍 Play-Level Directives

### Common Directives

```yaml
---
- name: Example playbook
  hosts: webservers
  
  # Privilege escalation
  become: yes
  become_user: root
  become_method: sudo
  
  # Fact gathering
  gather_facts: yes
  
  # Execution control
  serial: 2                    # Run on 2 hosts at a time
  max_fail_percentage: 25      # Fail if >25% hosts fail
  any_errors_fatal: no         # Continue despite errors
  
  # Connection settings
  remote_user: deploy
  connection: ssh
  
  tasks:
    - name: Example task
      debug:
        msg: "Hello World"
```

### Serial Execution

```yaml
---
- name: Rolling update
  hosts: webservers
  serial:
    - 1      # First host
    - 25%    # Then 25% of remaining
    - 100%   # Then rest
  
  tasks:
    - name: Update application
      # ... update tasks
```

---

## 📋 Task Organization

### Using Blocks

```yaml
tasks:
  - name: Web server configuration
    block:
      - name: Install Apache
        apt:
          name: apache2
          state: present
      
      - name: Start Apache
        service:
          name: apache2
          state: started
    
    rescue:
      - name: Handle failure
        debug:
          msg: "Apache installation failed"
    
    always:
      - name: Log action
        lineinfile:
          path: /var/log/ansible.log
          line: "Apache config attempted"
```

### Task Inclusion

```yaml
# main.yml
---
- name: Complete setup
  hosts: all
  
  tasks:
    - name: Include common tasks
      include_tasks: tasks/common.yml
    
    - name: Include web tasks
      include_tasks: tasks/webserver.yml
      when: "'webservers' in group_names"

# tasks/common.yml
---
- name: Update system
  apt:
    upgrade: yes
    update_cache: yes

- name: Install base packages
  apt:
    name:
      - vim
      - git
      - curl
    state: present
```

---

## 🎨 Multi-Play Playbooks

```yaml
---
# Play 1: Update all servers
- name: Update all servers
  hosts: all
  become: yes
  
  tasks:
    - name: Update packages
      apt:
        upgrade: dist
        update_cache: yes

# Play 2: Configure web servers
- name: Configure web servers
  hosts: webservers
  become: yes
  
  tasks:
    - name: Install Nginx
      apt:
        name: nginx
        state: present

# Play 3: Configure databases
- name: Configure databases
  hosts: databases
  become: yes
  
  tasks:
    - name: Install PostgreSQL
      apt:
        name: postgresql
        state: present
```

---

## 🔐 Security Best Practices

### 1. Use Vault for Secrets

```yaml
# vars/secrets.yml (encrypted with ansible-vault)
db_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          ...encrypted...

# playbook
- name: Database setup
  hosts: databases
  vars_files:
    - vars/secrets.yml
  
  tasks:
    - name: Create database user
      postgresql_user:
        name: appuser
        password: "{{ db_password }}"
```

### 2. Avoid Logging Sensitive Data

```yaml
- name: Set password
  user:
    name: appuser
    password: "{{ user_password }}"
  no_log: yes
```

### 3. Validate Input

```yaml
- name: Validate environment variable
  assert:
    that:
      - app_environment in ['dev', 'staging', 'production']
    fail_msg: "Invalid environment: {{ app_environment }}"
```

---

## 📊 Documentation Standards

### Playbook Header

```yaml
---
# Playbook: Web Server Configuration
# Description: Installs and configures Nginx web servers
# Author: DevOps Team
# Date: 2026-07-20
# Version: 1.2.0
#
# Requirements:
#   - Ansible 2.9+
#   - Target: Ubuntu 20.04+
#   - Privileges: sudo access required
#
# Usage:
#   ansible-playbook -i inventory/production webserver.yml
#
# Tags:
#   - setup: Initial installation
#   - config: Configuration updates
#   - deploy: Application deployment

- name: Configure Nginx web servers
  hosts: webservers
  become: yes
  
  tasks:
    # ... tasks
```

### Inline Comments

```yaml
tasks:
  # Install web server package
  - name: Install Nginx
    apt:
      name: nginx
      state: present
    tags: [setup, packages]
  
  # Configure virtual hosts
  # Note: This template includes SSL configuration
  - name: Deploy virtual host configuration
    template:
      src: vhost.conf.j2
      dest: "/etc/nginx/sites-available/{{ site_name }}.conf"
    notify: reload nginx
    tags: [config, vhosts]
```

---

## 🚀 Performance Tips

### 1. Limit Fact Gathering

```yaml
- name: Quick playbook
  hosts: all
  gather_facts: no  # Disable if not needed
  
  tasks:
    - name: Setup fact gathering only when needed
      setup:
        gather_subset:
          - min
      when: ansible_facts is not defined
```

### 2. Use Async Tasks

```yaml
- name: Long-running task
  command: /opt/app/long_script.sh
  async: 300      # Run for up to 5 minutes
  poll: 10        # Check status every 10 seconds
```

### 3. Optimize with Tags

```yaml
- name: Full stack deployment
  hosts: all
  
  tasks:
    - name: Install packages
      apt:
        name: "{{ item }}"
      loop: "{{ packages }}"
      tags: [packages, setup]
    
    - name: Deploy application
      copy:
        src: app/
        dest: /opt/app/
      tags: [deploy]

# Run only specific parts
# ansible-playbook site.yml --tags "deploy"
```

---

## ❌ Common Pitfalls

### 1. Hardcoded Values

```yaml
# Bad
- name: Start service
  service:
    name: apache2
    state: started

# Good
- name: Start service
  service:
    name: "{{ web_server_service }}"
    state: started
```

### 2. Missing Idempotency

```yaml
# Bad - runs every time
- name: Add line to file
  command: echo "line" >> /etc/config

# Good - idempotent
- name: Add line to file
  lineinfile:
    path: /etc/config
    line: "line"
    state: present
```

### 3. Ignoring Return Values

```yaml
# Bad - no verification
- name: Deploy application
  command: /opt/deploy.sh

# Good - check results
- name: Deploy application
  command: /opt/deploy.sh
  register: deploy_result
  failed_when: deploy_result.rc != 0

- name: Verify deployment
  assert:
    that:
      - "'SUCCESS' in deploy_result.stdout"
    fail_msg: "Deployment verification failed"
```

---

## 📚 Complete Example

### Production-Ready Playbook

```yaml
---
# Production Web Server Deployment
# Version: 2.0.0
# Updated: 2026-07-20

- name: Deploy web application to production
  hosts: webservers
  become: yes
  gather_facts: yes
  
  vars_files:
    - vars/production.yml
    - vars/secrets.yml
  
  pre_tasks:
    - name: Verify environment
      assert:
        that:
          - app_environment == "production"
          - app_version is defined
        fail_msg: "Environment validation failed"
    
    - name: Create backup
      archive:
        path: /opt/app
        dest: "/backup/app-{{ ansible_date_time.iso8601 }}.tar.gz"
      tags: [backup]
  
  tasks:
    - name: Update system packages
      apt:
        update_cache: yes
        cache_valid_time: 3600
      tags: [setup]
    
    - name: Install required packages
      apt:
        name: "{{ required_packages }}"
        state: present
      tags: [setup, packages]
    
    - name: Deploy application code
      synchronize:
        src: "{{ app_source_path }}"
        dest: "{{ app_dest_path }}"
        delete: yes
        recursive: yes
      notify: restart application
      tags: [deploy]
    
    - name: Deploy configuration
      template:
        src: app.conf.j2
        dest: "{{ app_config_path }}"
        owner: "{{ app_user }}"
        group: "{{ app_group }}"
        mode: '0644'
        validate: "{{ app_binary }} -t -c %s"
      notify: reload application
      tags: [config]
    
    - name: Ensure application is running
      service:
        name: "{{ app_service }}"
        state: started
        enabled: yes
      tags: [service]
  
  post_tasks:
    - name: Verify application health
      uri:
        url: "http://{{ inventory_hostname }}/health"
        status_code: 200
        timeout: 30
      retries: 3
      delay: 10
      tags: [verify]
    
    - name: Log deployment
      lineinfile:
        path: /var/log/deployments.log
        line: "{{ ansible_date_time.iso8601 }} - {{ app_version }} - {{ ansible_user_id }}"
        create: yes
      tags: [always]
  
  handlers:
    - name: restart application
      service:
        name: "{{ app_service }}"
        state: restarted
    
    - name: reload application
      service:
        name: "{{ app_service }}"
        state: reloaded
```

---

## 🎯 Key Takeaways

1. **Structure Matters:** Organize playbooks logically with clear directory structure
2. **Be Descriptive:** Use clear names for plays, tasks, and variables
3. **Stay Idempotent:** Ensure playbooks can run multiple times safely
4. **Handle Errors:** Plan for failures with proper error handling
5. **Document Everything:** Add comments and maintain README files
6. **Use Native Modules:** Prefer modules over shell/command
7. **Test Thoroughly:** Always test with --check before running
8. **Keep It DRY:** Don't Repeat Yourself - use includes and roles

---

## 🔗 What's Next?

- **Next:** [Variables & Facts](07-variables-facts.md)
- **Previous:** [Basic Modules](../basics/05-basic-modules.md)
- **Related:** [Error Handling](12-error-handling.md)

---

**Pro Tip:** Start with simple, flat playbooks and refactor into roles only when patterns emerge. Premature optimization leads to complexity!
