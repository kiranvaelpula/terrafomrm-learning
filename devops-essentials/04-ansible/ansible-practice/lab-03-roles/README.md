# Lab 03: Role Development and Testing

> **Create, test, and publish production-ready Ansible roles**

---

## Lab Overview

**Duration:** 3 hours  
**Difficulty:** Intermediate  
**Prerequisites:** Lab 02 completed

### Learning Objectives:
- Create structured roles
- Use Ansible Galaxy
- Test roles with Molecule
- Implement role dependencies
- Publish to Galaxy
- Document roles properly

---

## Exercise 1: Create Web Server Role (45 minutes)

### Task 1.1: Initialize Role Structure

```bash
# Create role scaffold
ansible-galaxy role init webserver

# Structure created:
webserver/
├── defaults/main.yml      # Default variables
├── files/                 # Static files
├── handlers/main.yml      # Handlers
├── meta/main.yml         # Role metadata
├── tasks/main.yml        # Main tasks
├── templates/            # Jinja2 templates
├── tests/                # Test playbooks
└── vars/main.yml         # Role variables
```

### Task 1.2: Implement Role Tasks

```yaml
# roles/webserver/tasks/main.yml
---
- name: Include OS-specific variables
  include_vars: "{{ ansible_os_family }}.yml"

- name: Install web server packages
  package:
    name: "{{ webserver_packages }}"
    state: present

- name: Create web root directory
  file:
    path: "{{ webserver_document_root }}"
    state: directory
    owner: "{{ webserver_user }}"
    group: "{{ webserver_group }}"
    mode: '0755'

- name: Deploy web server configuration
  template:
    src: "{{ webserver_config_template }}"
    dest: "{{ webserver_config_path }}"
    owner: root
    group: root
    mode: '0644'
    validate: "{{ webserver_validate_command }}"
  notify: Restart web server

- name: Deploy site configuration
  template:
    src: site.conf.j2
    dest: "{{ webserver_sites_available }}/{{ webserver_site_name }}.conf"
  notify: Reload web server

- name: Enable site
  file:
    src: "{{ webserver_sites_available }}/{{ webserver_site_name }}.conf"
    dest: "{{ webserver_sites_enabled }}/{{ webserver_site_name }}.conf"
    state: link
  when: webserver_type == "nginx"
  notify: Reload web server

- name: Ensure web server is running
  systemd:
    name: "{{ webserver_service_name }}"
    state: started
    enabled: yes
```

### Task 1.3: Define Role Variables

```yaml
# roles/webserver/defaults/main.yml
---
# Web server type (nginx or apache)
webserver_type: nginx

# Common settings
webserver_http_port: 80
webserver_https_port: 443
webserver_enable_ssl: false
webserver_site_name: default

# Nginx specific
webserver_document_root: /var/www/html
webserver_worker_processes: auto
webserver_worker_connections: 1024

# Application settings
webserver_app_name: myapp
webserver_app_port: 8080
webserver_enable_proxy: false
webserver_proxy_pass: "http://localhost:{{ webserver_app_port }}"

# SSL settings
webserver_ssl_cert_path: /etc/ssl/certs/server.crt
webserver_ssl_key_path: /etc/ssl/private/server.key
webserver_ssl_protocols: "TLSv1.2 TLSv1.3"

# roles/webserver/vars/Debian.yml
---
webserver_packages:
  - nginx
webserver_user: www-data
webserver_group: www-data
webserver_service_name: nginx
webserver_config_path: /etc/nginx/nginx.conf
webserver_config_template: nginx.conf.j2
webserver_sites_available: /etc/nginx/sites-available
webserver_sites_enabled: /etc/nginx/sites-enabled
webserver_validate_command: "nginx -t -c %s"

# roles/webserver/vars/RedHat.yml
---
webserver_packages:
  - nginx
webserver_user: nginx
webserver_group: nginx
webserver_service_name: nginx
webserver_config_path: /etc/nginx/nginx.conf
webserver_config_template: nginx.conf.j2
webserver_sites_available: /etc/nginx/conf.d
webserver_sites_enabled: /etc/nginx/conf.d
webserver_validate_command: "nginx -t -c %s"
```

### Task 1.4: Create Handlers

```yaml
# roles/webserver/handlers/main.yml
---
- name: Restart web server
  systemd:
    name: "{{ webserver_service_name }}"
    state: restarted

- name: Reload web server
  systemd:
    name: "{{ webserver_service_name }}"
    state: reloaded

- name: Test web server config
  command: "{{ webserver_validate_command }}"
  changed_when: false
```

### Task 1.5: Add Templates

```jinja2
# roles/webserver/templates/nginx.conf.j2
user {{ webserver_user }};
worker_processes {{ webserver_worker_processes }};
pid /run/nginx.pid;

events {
    worker_connections {{ webserver_worker_connections }};
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    gzip on;
    
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}

# roles/webserver/templates/site.conf.j2
server {
    listen {{ webserver_http_port }};
    server_name {{ webserver_site_name }};
    
    root {{ webserver_document_root }};
    index index.html index.htm;
    
    access_log /var/log/nginx/{{ webserver_site_name }}_access.log;
    error_log /var/log/nginx/{{ webserver_site_name }}_error.log;
    
    {% if webserver_enable_proxy %}
    location / {
        proxy_pass {{ webserver_proxy_pass }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    {% else %}
    location / {
        try_files $uri $uri/ =404;
    }
    {% endif %}
    
    {% if webserver_enable_ssl %}
    listen {{ webserver_https_port }} ssl;
    ssl_certificate {{ webserver_ssl_cert_path }};
    ssl_certificate_key {{ webserver_ssl_key_path }};
    ssl_protocols {{ webserver_ssl_protocols }};
    {% endif %}
}
```

---

## Exercise 2: Role Testing with Molecule (60 minutes)

### Task 2.1: Install Molecule

```bash
# Install Molecule with Docker driver
pip install molecule[docker]
pip install molecule-docker
pip install ansible-lint

# Verify installation
molecule --version
```

### Task 2.2: Initialize Molecule

```bash
# Inside role directory
cd roles/webserver
molecule init scenario --driver-name docker

# Creates:
molecule/
└── default/
    ├── converge.yml          # Test playbook
    ├── molecule.yml          # Molecule config
    └── verify.yml            # Verification tests
```

### Task 2.3: Configure Molecule

```yaml
# roles/webserver/molecule/default/molecule.yml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: ubuntu-20
    image: geerlingguy/docker-ubuntu2004-ansible:latest
    pre_build_image: true
    privileged: true
    command: /lib/systemd/systemd
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
  
  - name: centos-8
    image: geerlingguy/docker-centos8-ansible:latest
    pre_build_image: true
    privileged: true
    command: /usr/sbin/init
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro

provisioner:
  name: ansible
  config_options:
    defaults:
      callbacks_enabled: profile_tasks, timer
  playbooks:
    converge: converge.yml
    verify: verify.yml

verifier:
  name: ansible

lint: |
  set -e
  yamllint .
  ansible-lint .
```

### Task 2.4: Write Test Playbook

```yaml
# roles/webserver/molecule/default/converge.yml
---
- name: Converge
  hosts: all
  become: true
  
  roles:
    - role: webserver
      webserver_type: nginx
      webserver_site_name: testsite
      webserver_enable_proxy: true
      webserver_app_port: 3000
```

### Task 2.5: Write Verification Tests

```yaml
# roles/webserver/molecule/default/verify.yml
---
- name: Verify
  hosts: all
  gather_facts: false
  
  tasks:
    - name: Check if Nginx is installed
      package:
        name: nginx
        state: present
      check_mode: true
      register: nginx_check
      failed_when: nginx_check is changed
    
    - name: Verify Nginx is running
      systemd:
        name: nginx
      register: nginx_service
      failed_when: nginx_service.status.ActiveState != 'active'
    
    - name: Check Nginx configuration validity
      command: nginx -t
      changed_when: false
    
    - name: Verify Nginx is listening on port 80
      wait_for:
        port: 80
        state: started
        timeout: 5
    
    - name: Test HTTP response
      uri:
        url: http://localhost
        return_content: true
        status_code: 200
      register: http_response
    
    - name: Verify site configuration exists
      stat:
        path: /etc/nginx/sites-available/testsite.conf
      register: site_config
      failed_when: not site_config.stat.exists
```

### Task 2.6: Run Molecule Tests

```bash
# Full test sequence
molecule test

# Step-by-step testing
molecule create      # Create instances
molecule converge    # Run playbook
molecule verify      # Run verification
molecule idempotence # Test idempotency
molecule destroy     # Clean up

# Quick testing during development
molecule converge
molecule verify

# Login to test instance
molecule login -h ubuntu-20
```

---

## Exercise 3: Role Dependencies (30 minutes)

### Task 3.1: Define Dependencies

```yaml
# roles/webserver/meta/main.yml
---
galaxy_info:
  role_name: webserver
  author: Your Name
  description: Production-ready web server configuration
  company: Your Company
  license: MIT
  min_ansible_version: 2.9
  
  platforms:
    - name: Ubuntu
      versions:
        - focal
        - jammy
    - name: EL
      versions:
        - 8
        - 9
  
  galaxy_tags:
    - web
    - nginx
    - apache
    - webserver

dependencies:
  - role: common
    vars:
      common_packages:
        - curl
        - wget
  
  - role: firewall
    vars:
      firewall_allowed_tcp_ports:
        - "{{ webserver_http_port }}"
        - "{{ webserver_https_port }}"
    when: webserver_enable_firewall | default(false)
```

### Task 3.2: Use Role with Dependencies

```yaml
# playbooks/deploy_web.yml
---
- name: Deploy web servers
  hosts: webservers
  become: true
  
  roles:
    - role: webserver
      webserver_type: nginx
      webserver_enable_ssl: true
      webserver_enable_firewall: true
```

---

## Exercise 4: Publish to Galaxy (30 minutes)

### Task 4.1: Prepare Role for Publishing

```yaml
# roles/webserver/README.md
# Ansible Role: Webserver

Production-ready web server configuration for Nginx and Apache.

## Requirements

- Ansible >= 2.9
- Supported OS: Ubuntu 20.04+, RHEL 8+

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `webserver_type` | `nginx` | Web server type (nginx/apache) |
| `webserver_http_port` | `80` | HTTP port |
| `webserver_enable_ssl` | `false` | Enable HTTPS |

## Dependencies

- common
- firewall (optional)

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: webserver
      webserver_type: nginx
      webserver_enable_ssl: true
```

## Testing

```bash
molecule test
```

## License

MIT

## Author

Your Name (your.email@example.com)
```

### Task 4.2: Publish to Galaxy

```bash
# Login to Galaxy
ansible-galaxy login

# Import role
ansible-galaxy role import github_user repository_name

# Or publish from CLI
cd roles/webserver
ansible-galaxy role import --api-key=YOUR_API_KEY github_user ansible-role-webserver
```

### Task 4.3: Use Published Role

```yaml
# requirements.yml
---
roles:
  - name: yourname.webserver
    version: 1.0.0

# Install role
$ ansible-galaxy install -r requirements.yml

# Use in playbook
- hosts: webservers
  roles:
    - yourname.webserver
```

---

## Lab Challenges

### Challenge 1: Database Role
Create a MySQL/PostgreSQL role with:
- Multi-database support
- Replication configuration
- Backup automation
- Full Molecule test suite

### Challenge 2: Application Deployment Role
Build a role that:
- Deploys any application
- Supports multiple deployment strategies
- Includes rollback capability
- Has comprehensive tests

### Challenge 3: Monitoring Role
Create a role for:
- Installing Prometheus + Grafana
- Configuring dashboards
- Setting up alerts
- Molecule tests for all components

---

## Validation

```bash
# Test role syntax
ansible-playbook roles/webserver/tests/test.yml --syntax-check

# Run Molecule tests
cd roles/webserver
molecule test

# Test role in playbook
ansible-playbook playbooks/test_webserver.yml --check

# Verify idempotency
ansible-playbook playbooks/test_webserver.yml
ansible-playbook playbooks/test_webserver.yml  # Should show 0 changes
```

---

## Lab Completion

**Congratulations!** You have completed Lab 03.

### Skills Acquired:
- ✅ Role structure and organization
- ✅ Role variables and defaults
- ✅ Molecule testing framework
- ✅ Role dependencies
- ✅ Galaxy publishing
- ✅ Professional documentation

### Next Steps:
- Lab 04: Advanced Topics
- Lab 05: Real-World Project

---

**Duration:** ~3 hours  
**Difficulty:** Intermediate  
**Status:** Complete
