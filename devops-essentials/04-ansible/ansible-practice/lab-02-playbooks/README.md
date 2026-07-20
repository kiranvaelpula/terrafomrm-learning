# Lab 02: Advanced Playbooks and Variables

> **Master complex playbook structures, variables, templates, and handlers**

---

## Lab Overview

**Duration:** 3 hours  
**Difficulty:** Intermediate  
**Prerequisites:** Lab 01 completed

### Learning Objectives:
- Complex playbook structure
- Variable precedence and scoping
- Template usage with Jinja2
- Handler implementation
- Loop patterns
- Error handling
- Testing strategies

---

## Lab Environment

Same setup as Lab 01 plus:
- Git repository for playbook versioning
- Text editor (VS Code recommended)

---

## Exercise 1: Advanced Playbook Structure (40 minutes)

### Task 1.1: Multi-Play Playbook

```yaml
# playbooks/multi_play.yml
---
- name: Prepare database servers
  hosts: databases
  become: true
  tags: database
  
  tasks:
    - name: Install MySQL
      apt:
        name: mysql-server
        state: present
    
    - name: Start MySQL service
      systemd:
        name: mysql
        state: started
        enabled: yes

- name: Configure web servers
  hosts: webservers
  become: true
  tags: webserver
  
  tasks:
    - name: Install Nginx
      apt:
        name: nginx
        state: present
    
    - name: Configure Nginx
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: Reload Nginx
  
  handlers:
    - name: Reload Nginx
      systemd:
        name: nginx
        state: reloaded

- name: Deploy application
  hosts: webservers
  become: true
  tags: deploy
  
  tasks:
    - name: Deploy app files
      synchronize:
        src: /local/app/
        dest: /var/www/html/
```

### Task 1.2: Organize with Roles Structure

```yaml
# playbooks/site.yml
---
- name: Configure all servers
  hosts: all
  become: true
  
  roles:
    - common
    - { role: webserver, when: "'webservers' in group_names" }
    - { role: database, when: "'databases' in group_names" }

# roles/common/tasks/main.yml
---
- name: Update system packages
  apt:
    update_cache: yes
    upgrade: safe

- name: Install common packages
  apt:
    name:
      - vim
      - git
      - htop
      - curl
    state: present

- name: Configure NTP
  template:
    src: ntp.conf.j2
    dest: /etc/ntp.conf
  notify: Restart NTP

# roles/common/handlers/main.yml
---
- name: Restart NTP
  systemd:
    name: ntp
    state: restarted
```

---

## Exercise 2: Variable Mastery (45 minutes)

### Task 2.1: Variable Precedence Testing

```yaml
# inventory/hosts
[webservers]
web01 http_port=8080  # Host var (highest precedence)

[webservers:vars]
http_port=80  # Group var

# group_vars/webservers.yml
http_port: 80
app_name: myapp

# group_vars/all.yml
http_port: 80
environment: production

# playbooks/test_precedence.yml
---
- name: Test variable precedence
  hosts: webservers
  vars:
    http_port: 8000  # Play vars
  
  tasks:
    - name: Show http_port value
      debug:
        msg: "HTTP Port: {{ http_port }}"  # Will be 8080 from host var
    
    - name: Show all variable sources
      debug:
        msg: |
          Play var: {{ http_port }}
          Host var: {{ hostvars[inventory_hostname]['http_port'] }}
          Group var: {{ group_names }}
```

### Task 2.2: Dynamic Variables

```yaml
# playbooks/dynamic_vars.yml
---
- name: Dynamic variable usage
  hosts: all
  vars:
    base_path: "/opt/apps"
    environments:
      development:
        port: 8080
        debug: true
        db_host: "db.dev.local"
      production:
        port: 80
        debug: false
        db_host: "db.prod.local"
    
    current_env: "{{ environment | default('development') }}"
  
  tasks:
    - name: Set environment-specific vars
      set_fact:
        app_port: "{{ environments[current_env].port }}"
        app_debug: "{{ environments[current_env].debug }}"
        database_host: "{{ environments[current_env].db_host }}"
    
    - name: Display configuration
      debug:
        msg: |
          Environment: {{ current_env }}
          Port: {{ app_port }}
          Debug: {{ app_debug }}
          DB Host: {{ database_host }}
    
    - name: Computed variables
      set_fact:
        app_path: "{{ base_path }}/{{ app_name }}/{{ current_env }}"
        log_path: "/var/log/{{ app_name }}/{{ current_env }}"
    
    - name: Use computed vars
      debug:
        msg: "App will be installed to: {{ app_path }}"
```

### Task 2.3: Variable Files and Vault

```yaml
# vars/prod_vars.yml
---
db_host: prod-db.example.com
db_port: 3306
cache_servers:
  - cache01.prod
  - cache02.prod

# vars/prod_secrets.yml (encrypted with ansible-vault)
---
db_password: supersecret
api_key: abc123xyz

# playbooks/with_vault.yml
---
- name: Deploy with secrets
  hosts: webservers
  vars_files:
    - ../vars/prod_vars.yml
    - ../vars/prod_secrets.yml
  
  tasks:
    - name: Configure database connection
      template:
        src: db_config.j2
        dest: /etc/app/database.conf
      no_log: true  # Don't log sensitive data
```

**Create and use vault:**
```bash
# Create encrypted file
ansible-vault create vars/prod_secrets.yml

# Edit encrypted file
ansible-vault edit vars/prod_secrets.yml

# Run with vault password
ansible-playbook playbooks/with_vault.yml --ask-vault-pass

# Or use password file
echo "mypassword" > .vault_pass
ansible-playbook playbooks/with_vault.yml --vault-password-file .vault_pass
```

---

## Exercise 3: Templates with Jinja2 (45 minutes)

### Task 3.1: Nginx Configuration Template

```jinja2
# templates/nginx.conf.j2
user {{ nginx_user | default('www-data') }};
worker_processes {{ ansible_processor_vcpus }};
pid /run/nginx.pid;

events {
    worker_connections {{ nginx_worker_connections | default(1024) }};
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    access_log {{ nginx_access_log | default('/var/log/nginx/access.log') }};
    error_log {{ nginx_error_log | default('/var/log/nginx/error.log') }};
    
    # Gzip
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript;
    
    # Virtual Host Configs
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

```jinja2
# templates/site.conf.j2
server {
    listen {{ http_port | default(80) }};
    server_name {{ server_name | default('_') }};
    
    root {{ document_root }};
    index index.html index.htm index.php;
    
    # Logging
    access_log /var/log/nginx/{{ app_name }}_access.log;
    error_log /var/log/nginx/{{ app_name }}_error.log;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    {% if enable_php | default(false) %}
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php{{ php_version }}-fpm.sock;
    }
    {% endif %}
    
    {% if enable_ssl | default(false) %}
    # SSL Configuration
    listen 443 ssl;
    ssl_certificate {{ ssl_cert_path }};
    ssl_certificate_key {{ ssl_key_path }};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    {% endif %}
}
```

### Task 3.2: Application Configuration Template

```jinja2
# templates/app_config.j2
# Application Configuration
# Generated by Ansible on {{ ansible_date_time.iso8601 }}

[application]
name = {{ app_name }}
version = {{ app_version }}
environment = {{ environment }}
debug = {{ app_debug | default(false) | lower }}

[server]
host = {{ ansible_default_ipv4.address }}
port = {{ app_port }}
workers = {{ ansible_processor_vcpus * 2 }}

[database]
host = {{ db_host }}
port = {{ db_port }}
name = {{ db_name }}
user = {{ db_user }}
password = {{ db_password }}
pool_size = {{ db_pool_size | default(10) }}

[cache]
enabled = {{ enable_cache | default(true) | lower }}
{% if enable_cache | default(true) %}
servers = {{ cache_servers | join(',') }}
ttl = {{ cache_ttl | default(300) }}
{% endif %}

[logging]
level = {{ log_level | default('INFO') }}
file = {{ log_path }}/{{ app_name }}.log
max_size = {{ log_max_size | default('100MB') }}
backup_count = {{ log_backup_count | default(5) }}

# Custom settings per environment
{% if environment == 'production' %}
[production]
enable_profiling = false
enable_debug_toolbar = false
{% elif environment == 'development' %}
[development]
enable_profiling = true
enable_debug_toolbar = true
reload_on_change = true
{% endif %}
```

### Task 3.3: Dynamic Host List Template

```jinja2
# templates/hosts.j2
# /etc/hosts - Generated by Ansible
127.0.0.1 localhost
{{ ansible_default_ipv4.address }} {{ ansible_hostname }} {{ ansible_fqdn }}

# Web Servers
{% for host in groups['webservers'] %}
{{ hostvars[host]['ansible_host'] }} {{ host }} {{ host }}.{{ domain_name }}
{% endfor %}

# Database Servers
{% for host in groups['databases'] %}
{{ hostvars[host]['ansible_host'] }} {{ host }} {{ host }}.{{ domain_name }}
{% endfor %}

# Conditional entries
{% if enable_monitoring | default(false) %}
# Monitoring servers
{{ monitoring_server }} monitoring.{{ domain_name }}
{% endif %}
```

---

## Exercise 4: Handlers and Conditionals (30 minutes)

### Task 4.1: Handler Patterns

```yaml
# playbooks/handlers_example.yml
---
- name: Configure services with handlers
  hosts: webservers
  become: true
  
  tasks:
    - name: Update Nginx config
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        validate: 'nginx -t -c %s'
      notify:
        - Reload Nginx
        - Clear cache
    
    - name: Update site config
      template:
        src: site.conf.j2
        dest: /etc/nginx/sites-available/{{ app_name }}
      notify: Reload Nginx
    
    - name: Enable site
      file:
        src: /etc/nginx/sites-available/{{ app_name }}
        dest: /etc/nginx/sites-enabled/{{ app_name }}
        state: link
      notify: Reload Nginx
    
    - name: Update application code
      git:
        repo: "{{ app_repo }}"
        dest: "{{ app_path }}"
        version: "{{ app_version }}"
      notify:
        - Restart application
        - Run database migrations
  
  handlers:
    - name: Reload Nginx
      systemd:
        name: nginx
        state: reloaded
    
    - name: Restart application
      systemd:
        name: "{{ app_name }}"
        state: restarted
    
    - name: Clear cache
      file:
        path: /var/cache/{{ app_name }}
        state: absent
    
    - name: Run database migrations
      command: "{{ app_path }}/manage.py migrate"
      args:
        chdir: "{{ app_path }}"
```

### Task 4.2: Advanced Conditionals

```yaml
# playbooks/conditionals.yml
---
- name: Conditional task execution
  hosts: all
  become: true
  
  tasks:
    - name: Ubuntu-specific tasks
      block:
        - name: Update apt cache
          apt:
            update_cache: yes
        
        - name: Install Ubuntu packages
          apt:
            name:
              - ubuntu-specific-package
            state: present
      when: ansible_distribution == "Ubuntu"
    
    - name: RHEL-specific tasks
      block:
        - name: Install RHEL packages
          yum:
            name:
              - rhel-specific-package
            state: present
      when: ansible_distribution == "RedHat"
    
    - name: Install package based on OS family
      package:
        name: "{{ item }}"
        state: present
      loop:
        - vim
        - git
      when: ansible_os_family in ["Debian", "RedHat"]
    
    - name: Conditional based on facts
      debug:
        msg: "This server has enough memory"
      when: ansible_memtotal_mb >= 4096
    
    - name: Multiple conditions (AND)
      debug:
        msg: "Production web server"
      when:
        - inventory_hostname in groups['webservers']
        - environment == 'production'
        - ansible_memtotal_mb >= 8192
    
    - name: Multiple conditions (OR)
      debug:
        msg: "Development or staging"
      when: environment == 'development' or environment == 'staging'
    
    - name: Complex conditionals
      debug:
        msg: "Meets all criteria"
      when: >
        (ansible_distribution == "Ubuntu" and ansible_distribution_major_version >= "20") or
        (ansible_distribution == "RedHat" and ansible_distribution_major_version >= "8")
```

---

## Exercise 5: Loops and Iteration (30 minutes)

### Task 5.1: Simple Loops

```yaml
# playbooks/loops.yml
---
- name: Loop examples
  hosts: all
  become: true
  
  tasks:
    - name: Install multiple packages
      apt:
        name: "{{ item }}"
        state: present
      loop:
        - nginx
        - git
        - vim
        - htop
    
    - name: Create multiple directories
      file:
        path: "{{ item }}"
        state: directory
        mode: '0755'
      loop:
        - /opt/app
        - /opt/app/config
        - /opt/app/logs
        - /opt/app/data
    
    - name: Create multiple users
      user:
        name: "{{ item.name }}"
        groups: "{{ item.groups }}"
        shell: "{{ item.shell }}"
        state: present
      loop:
        - { name: 'alice', groups: 'developers', shell: '/bin/bash' }
        - { name: 'bob', groups: 'developers', shell: '/bin/bash' }
        - { name: 'charlie', groups: 'ops', shell: '/bin/zsh' }
```

### Task 5.2: Advanced Loop Patterns

```yaml
- name: Loop with conditional
  apt:
    name: "{{ item }}"
    state: present
  loop: "{{ packages }}"
  when: item not in ['unwanted-package']

- name: Loop with register
  command: "echo {{ item }}"
  loop:
    - one
    - two
    - three
  register: echo_results

- name: Display loop results
  debug:
    msg: "{{ item.stdout }}"
  loop: "{{ echo_results.results }}"

- name: Nested loops (with_nested deprecated, use loop + product)
  debug:
    msg: "{{ item[0] }} - {{ item[1] }}"
  loop: "{{ ['web', 'db'] | product(['dev', 'prod']) | list }}"

- name: Loop with index
  debug:
    msg: "{{ ansible_loop.index }}: {{ item }}"
  loop:
    - first
    - second
    - third
  loop_control:
    label: "Processing {{ item }}"

- name: Loop with dict
  debug:
    msg: "{{ item.key }} = {{ item.value }}"
  loop: "{{ my_dict | dict2items }}"
  vars:
    my_dict:
      key1: value1
      key2: value2
```

---

## Lab Challenges

### Challenge 1: Complete Application Stack

Create playbooks that deploy a complete 3-tier application:
- Database tier (MySQL with replication)
- Application tier (Node.js app)
- Web tier (Nginx reverse proxy)
- Use templates for all configurations
- Implement proper handlers
- Include error handling

### Challenge 2: Multi-Environment Deployment

Create an inventory and playbooks that support:
- Development, staging, production environments
- Different configurations per environment
- Encrypted secrets per environment
- Environment promotion workflow

### Challenge 3: Configuration Management

Build a playbook that:
- Ensures system configuration compliance
- Uses templates for all config files
- Implements handlers for service restarts
- Validates configurations before applying
- Generates a compliance report

---

## Validation

```bash
# Syntax check
ansible-playbook playbooks/*.yml --syntax-check

# Dry run
ansible-playbook playbooks/site.yml --check --diff

# Run with tags
ansible-playbook playbooks/site.yml --tags webserver

# Test templates
ansible all -m template -a "src=templates/app_config.j2 dest=/tmp/test.conf" --check

# Verify handlers triggered
ansible-playbook playbooks/handlers_example.yml -vv | grep "RUNNING HANDLER"
```

---

## Lab Completion

**Congratulations!** You have completed Lab 02.

### Skills Acquired:
- ✅ Complex playbook structures
- ✅ Variable precedence and scoping
- ✅ Jinja2 template mastery
- ✅ Handler patterns
- ✅ Loop techniques
- ✅ Conditional logic
- ✅ Error handling

### Next Steps:
- Lab 03: Role Development
- Study [Advanced Topics](../../advanced/README.md)

---

**Duration:** ~3 hours  
**Difficulty:** Intermediate  
**Status:** Complete
