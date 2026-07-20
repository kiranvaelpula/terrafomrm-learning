# Variables & Facts

> **Master data management and dynamic information gathering in Ansible**

---

## 📖 What You'll Learn

- Variable types and scopes
- Ansible facts system
- Variable precedence
- Custom facts
- Magic variables
- Best practices

---

## 🔤 Variable Basics

### Defining Variables

```yaml
# In playbook
---
- name: Example playbook
  hosts: webservers
  vars:
    http_port: 80
    server_name: www.example.com
    packages:
      - nginx
      - git
      - vim
  
  tasks:
    - name: Show variable
      debug:
        msg: "Port: {{ http_port }}"
```

### Variable Files

```yaml
# vars/main.yml
---
app_name: myapp
app_port: 8080
app_user: appuser
environment: production

# playbook.yml
---
- name: Deploy application
  hosts: all
  vars_files:
    - vars/main.yml
  
  tasks:
    - name: Show app name
      debug:
        msg: "Deploying {{ app_name }}"
```

---

## 📊 Variable Types

### 1. Simple Variables

```yaml
vars:
  app_port: 8080
  app_name: "myapp"
  is_production: true
  max_connections: 100
```

### 2. Lists

```yaml
vars:
  packages:
    - nginx
    - postgresql
    - redis

tasks:
  - name: Install packages
    apt:
      name: "{{ packages }}"
      state: present
```

### 3. Dictionaries

```yaml
vars:
  database:
    host: db.example.com
    port: 5432
    name: appdb
    user: dbuser

tasks:
  - name: Connect to database
    debug:
      msg: "Connecting to {{ database.host }}:{{ database.port }}"
```

### 4. Nested Structures

```yaml
vars:
  environments:
    production:
      hosts:
        - web01.prod.com
        - web02.prod.com
      port: 80
    staging:
      hosts:
        - web01.staging.com
      port: 8080

tasks:
  - name: Show production hosts
    debug:
      msg: "{{ environments.production.hosts }}"
```

---

## 🎯 Variable Locations

### 1. Inventory Variables

```ini
# inventory/hosts
[webservers]
web01 ansible_host=192.168.1.10 http_port=80
web02 ansible_host=192.168.1.11 http_port=8080

[webservers:vars]
domain=example.com
ssl_enabled=true
```

### 2. Group Variables

```yaml
# group_vars/webservers.yml
---
http_port: 80
https_port: 443
max_clients: 200
server_admin: admin@example.com

# group_vars/all.yml
---
ntp_server: ntp.example.com
dns_servers:
  - 8.8.8.8
  - 8.8.4.4
```

### 3. Host Variables

```yaml
# host_vars/web01.yml
---
server_id: 1
local_ip: 192.168.1.10
is_primary: true

# host_vars/web02.yml
---
server_id: 2
local_ip: 192.168.1.11
is_primary: false
```

### 4. Extra Variables (Command Line)

```bash
# Highest precedence
ansible-playbook site.yml -e "version=2.0 environment=staging"
ansible-playbook site.yml --extra-vars "app_port=9000"

# From file
ansible-playbook site.yml -e "@vars/override.yml"
```

---

## 📋 Variable Precedence (Low to High)

```
1.  Role defaults (defaults/main.yml)
2.  Inventory file or script group vars
3.  Inventory group_vars/all
4.  Playbook group_vars/all
5.  Inventory group_vars/*
6.  Playbook group_vars/*
7.  Inventory file or script host vars
8.  Inventory host_vars/*
9.  Playbook host_vars/*
10. Host facts / cached set_facts
11. Play vars
12. Play vars_prompt
13. Play vars_files
14. Role vars (vars/main.yml)
15. Block vars (only for tasks in block)
16. Task vars (only for the task)
17. Include_vars
18. Set_facts / registered vars
19. Role (and include_role) params
20. Include params
21. Extra vars (-e in CLI)
```

### Precedence Example

```yaml
# group_vars/all.yml
app_port: 8080

# playbook.yml
- name: Test precedence
  hosts: all
  vars:
    app_port: 9000  # This overrides group_vars
  
  tasks:
    - name: Show port
      debug:
        msg: "Port: {{ app_port }}"  # Shows 9000
    
    - name: Override with task var
      debug:
        msg: "Port: {{ app_port }}"
      vars:
        app_port: 3000  # Highest precedence: shows 3000
```

---

## 🔍 Ansible Facts

### Gathering Facts

```yaml
---
- name: Gather and display facts
  hosts: all
  gather_facts: yes
  
  tasks:
    - name: Display OS family
      debug:
        msg: "OS: {{ ansible_os_family }}"
    
    - name: Display IP address
      debug:
        msg: "IP: {{ ansible_default_ipv4.address }}"
    
    - name: Display all facts
      debug:
        var: ansible_facts
```

### Common Facts

```yaml
# System Information
ansible_hostname              # node01
ansible_fqdn                 # node01.example.com
ansible_os_family            # Debian, RedHat
ansible_distribution         # Ubuntu, CentOS
ansible_distribution_version # 20.04, 8.5

# Network Information
ansible_default_ipv4.address    # 192.168.1.10
ansible_default_ipv4.interface  # eth0
ansible_all_ipv4_addresses      # List of all IPs
ansible_dns.nameservers         # DNS servers

# Hardware Information
ansible_processor_cores       # 4
ansible_memtotal_mb          # 16384
ansible_devices              # Disk information
ansible_mounts               # Mounted filesystems

# Python Information
ansible_python_version       # 3.8.10
ansible_python_executable    # /usr/bin/python3
```

### Using Facts in Tasks

```yaml
tasks:
  - name: Install package based on OS
    package:
      name: "{{ 'httpd' if ansible_os_family == 'RedHat' else 'apache2' }}"
      state: present
  
  - name: Set timezone based on location
    timezone:
      name: "{{ 'America/New_York' if 'US' in ansible_fqdn else 'Europe/London' }}"
  
  - name: Configure memory based on RAM
    lineinfile:
      path: /etc/app/config
      line: "memory={{ (ansible_memtotal_mb * 0.7) | int }}MB"
```

---

## 🎨 Fact Gathering Control

### Disable Fact Gathering

```yaml
---
- name: Quick playbook
  hosts: all
  gather_facts: no  # Faster execution
  
  tasks:
    - name: Do something
      debug:
        msg: "No facts needed"
```

### Selective Fact Gathering

```yaml
---
- name: Gather minimal facts
  hosts: all
  gather_facts: yes
  
  tasks:
    - name: Gather only network facts
      setup:
        gather_subset:
          - '!all'
          - '!min'
          - network
    
    - name: Show network facts
      debug:
        var: ansible_default_ipv4
```

### Fact Caching

```ini
# ansible.cfg
[defaults]
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400  # 24 hours
```

---

## 🛠️ Custom Facts

### Creating Custom Facts

```bash
# /etc/ansible/facts.d/app.fact
#!/bin/bash
cat <<EOF
{
  "app_name": "myapp",
  "app_version": "2.5.1",
  "deployed_at": "$(date -I)"
}
EOF
```

```yaml
# playbook to deploy custom fact
---
- name: Deploy custom facts
  hosts: all
  become: yes
  
  tasks:
    - name: Create facts directory
      file:
        path: /etc/ansible/facts.d
        state: directory
        mode: '0755'
    
    - name: Deploy custom fact
      copy:
        dest: /etc/ansible/facts.d/app.fact
        mode: '0755'
        content: |
          #!/bin/bash
          cat <<EOF
          {
            "name": "myapp",
            "version": "{{ app_version }}",
            "environment": "{{ app_environment }}"
          }
          EOF
    
    - name: Reload facts
      setup:
        filter: ansible_local
    
    - name: Show custom fact
      debug:
        msg: "App: {{ ansible_local.app.name }} v{{ ansible_local.app.version }}"
```

### JSON Custom Facts

```json
# /etc/ansible/facts.d/server_info.fact
{
  "server_role": "webserver",
  "backup_enabled": true,
  "monitoring_enabled": true,
  "maintainer": "devops-team"
}
```

---

## ✨ Magic Variables

### Inventory Variables

```yaml
tasks:
  # Current host
  - debug: msg="{{ inventory_hostname }}"       # web01
  
  # Full inventory name
  - debug: msg="{{ inventory_hostname_short }}" # web01 (without domain)
  
  # Groups this host belongs to
  - debug: msg="{{ group_names }}"              # ['webservers', 'production']
  
  # All groups
  - debug: msg="{{ groups }}"                   # {'webservers': ['web01', 'web02'], ...}
  
  # All hosts in inventory
  - debug: msg="{{ groups['all'] }}"            # All hosts
```

### Playbook Variables

```yaml
tasks:
  # Playbook directory
  - debug: msg="{{ playbook_dir }}"  # /path/to/playbook/directory
  
  # Current role
  - debug: msg="{{ role_name }}"     # current_role_name
  
  # Play hosts
  - debug: msg="{{ play_hosts }}"    # Hosts in current play
  
  # Ansible version
  - debug: msg="{{ ansible_version.full }}"  # 2.9.27
```

### Execution Variables

```yaml
tasks:
  # Check mode status
  - debug: msg="Running in check mode"
    when: ansible_check_mode
  
  # Connection variables
  - debug: msg="{{ ansible_user }}"          # SSH user
  - debug: msg="{{ ansible_port }}"          # SSH port
  - debug: msg="{{ ansible_connection }}"    # Connection type
```

---

## 🔧 Registered Variables

### Basic Registration

```yaml
tasks:
  - name: Run command
    command: whoami
    register: command_result
  
  - name: Show result
    debug:
      var: command_result
  
  - name: Show stdout
    debug:
      msg: "User: {{ command_result.stdout }}"
```

### Common Uses

```yaml
tasks:
  # Check if file exists
  - name: Check file
    stat:
      path: /etc/app/config
    register: config_file
  
  - name: Use result
    debug:
      msg: "Config exists"
    when: config_file.stat.exists
  
  # Get service status
  - name: Check service
    service_facts:
    register: services
  
  - name: Show nginx status
    debug:
      msg: "Nginx is {{ services.ansible_facts.services['nginx.service'].state }}"
```

### Loop with Registration

```yaml
tasks:
  - name: Check multiple files
    stat:
      path: "{{ item }}"
    loop:
      - /etc/config1
      - /etc/config2
      - /etc/config3
    register: file_stats
  
  - name: Show results
    debug:
      msg: "{{ item.item }} exists: {{ item.stat.exists }}"
    loop: "{{ file_stats.results }}"
```

---

## 🔐 Variable Security

### Using ansible-vault

```yaml
# Encrypt variable file
# ansible-vault encrypt vars/secrets.yml

# vars/secrets.yml
---
db_password: supersecret
api_key: abc123xyz

# playbook.yml
---
- name: Use encrypted variables
  hosts: databases
  vars_files:
    - vars/secrets.yml
  
  tasks:
    - name: Configure database
      postgresql_user:
        name: appuser
        password: "{{ db_password }}"
      no_log: yes  # Don't log sensitive data
```

### Prompted Variables

```yaml
---
- name: Deploy with prompted password
  hosts: all
  vars_prompt:
    - name: db_password
      prompt: "Enter database password"
      private: yes
    
    - name: app_version
      prompt: "Enter app version to deploy"
      default: "latest"
  
  tasks:
    - name: Use prompted variable
      debug:
        msg: "Deploying version {{ app_version }}"
      no_log: "{{ 'password' in item }}"
```

---

## 🎭 Variable Manipulation

### Filters

```yaml
vars:
  app_name: "MyApp"
  version: "2.5.1"
  items: [1, 2, 3, 4, 5]

tasks:
  # String filters
  - debug: msg="{{ app_name | lower }}"           # myapp
  - debug: msg="{{ app_name | upper }}"           # MYAPP
  - debug: msg="{{ version | replace('.', '-') }}" # 2-5-1
  
  # List filters
  - debug: msg="{{ items | first }}"              # 1
  - debug: msg="{{ items | last }}"               # 5
  - debug: msg="{{ items | length }}"             # 5
  - debug: msg="{{ items | max }}"                # 5
  - debug: msg="{{ items | sum }}"                # 15
  
  # Default filter
  - debug: msg="{{ undefined_var | default('N/A') }}"
```

### Conditional Expressions

```yaml
tasks:
  - name: Set based on condition
    set_fact:
      app_port: "{{ 443 if ssl_enabled else 80 }}"
  
  - name: Complex condition
    set_fact:
      environment_type: >-
        {{ 'production' if inventory_hostname in groups['prod']
           else 'staging' if inventory_hostname in groups['stage']
           else 'development' }}
```

---

## 📚 Complete Example

```yaml
---
- name: Comprehensive variable example
  hosts: webservers
  gather_facts: yes
  
  vars:
    # Simple variables
    app_name: myapp
    app_version: 2.5.1
    
    # Dictionary
    database:
      host: "{{ groups['databases'][0] }}"
      port: 5432
      name: "{{ app_name }}_db"
    
    # List
    required_packages:
      - nginx
      - python3
      - git
  
  vars_files:
    - vars/{{ ansible_os_family | lower }}.yml
    - vars/{{ app_environment }}.yml
  
  tasks:
    - name: Set facts based on system
      set_fact:
        web_server: "{{ 'httpd' if ansible_os_family == 'RedHat' else 'nginx' }}"
        config_path: "{{ '/etc/httpd' if ansible_os_family == 'RedHat' else '/etc/nginx' }}"
    
    - name: Check available memory
      set_fact:
        can_deploy: "{{ ansible_memfree_mb > 1000 }}"
    
    - name: Display gathered information
      debug:
        msg: |
          Host: {{ inventory_hostname }}
          OS: {{ ansible_distribution }} {{ ansible_distribution_version }}
          IP: {{ ansible_default_ipv4.address }}
          App: {{ app_name }} v{{ app_version }}
          Database: {{ database.host }}:{{ database.port }}
          Web Server: {{ web_server }}
          Can Deploy: {{ can_deploy }}
    
    - name: Deploy configuration
      template:
        src: app.conf.j2
        dest: "{{ config_path }}/{{ app_name }}.conf"
      vars:
        server_name: "{{ inventory_hostname }}"
        listen_port: "{{ http_port | default(80) }}"
      when: can_deploy | bool
```

---

## 🎯 Best Practices

1. **Use meaningful names:** `web_server_port` not `port`
2. **Group related variables:** Use dictionaries for complex config
3. **Set defaults:** Use `default()` filter or role defaults
4. **Document variables:** Add comments explaining purpose
5. **Secure sensitive data:** Always use ansible-vault
6. **Avoid global variables:** Scope appropriately
7. **Use facts wisely:** Cache facts for performance
8. **Test variable precedence:** Understand override behavior

---

## 🔗 What's Next?

- **Next:** [Templates (Jinja2)](08-templates.md)
- **Previous:** [Playbook Structure](06-playbook-structure.md)
- **Related:** [Ansible Vault](11-ansible-vault.md)

---

**Pro Tip:** Use `ansible-playbook --list-vars playbook.yml` to see all variables that will be used!
