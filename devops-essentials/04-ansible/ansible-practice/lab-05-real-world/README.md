# Lab 05: Real-World Project - Complete LAMP Stack Automation

> **Build production-ready LAMP stack automation with full DevOps lifecycle**

---

## Project Overview

**Duration:** 5 hours  
**Difficulty:** Advanced  
**Prerequisites:** Labs 01-04 completed

### Project Goals:
- Complete LAMP stack automation
- Multi-environment support (dev/staging/prod)
- CI/CD pipeline integration
- Monitoring and logging
- Backup and disaster recovery
- Security hardening
- Documentation

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer (HAProxy)              │
│                    192.168.1.10                         │
└──────────────┬────────────────────────┬─────────────────┘
               │                        │
       ┌───────▼────────┐      ┌───────▼────────┐
       │  Web Server 1  │      │  Web Server 2  │
       │  (Apache+PHP)  │      │  (Apache+PHP)  │
       │  192.168.1.11  │      │  192.168.1.12  │
       └───────┬────────┘      └───────┬────────┘
               │                        │
               └────────┬───────────────┘
                        │
                ┌───────▼────────┐
                │  Database      │
                │  (MySQL 8.0)   │
                │  192.168.1.13  │
                └────────────────┘
```

---

## Phase 1: Project Setup (30 minutes)

### Step 1.1: Initialize Project Structure

```bash
mkdir -p lamp-automation/{inventory,playbooks,roles,group_vars,host_vars,files,templates}
cd lamp-automation

# Create directory structure
lamp-automation/
├── ansible.cfg
├── inventory/
│   ├── development/
│   ├── staging/
│   └── production/
├── playbooks/
│   ├── site.yml
│   ├── deploy.yml
│   ├── backup.yml
│   └── rollback.yml
├── roles/
│   ├── common/
│   ├── haproxy/
│   ├── webserver/
│   ├── database/
│   └── monitoring/
├── group_vars/
│   ├── all/
│   ├── webservers/
│   └── databases/
└── README.md
```

### Step 1.2: Configure Ansible

```ini
# ansible.cfg
[defaults]
inventory = inventory/production
roles_path = roles
host_key_checking = False
retry_files_enabled = False
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400
callbacks_enabled = profile_tasks, timer

[privilege_escalation]
become = True
become_method = sudo
become_user = root

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

### Step 1.3: Create Inventory

```yaml
# inventory/production/hosts.yml
---
all:
  children:
    loadbalancers:
      hosts:
        lb01:
          ansible_host: 192.168.1.10
    
    webservers:
      hosts:
        web01:
          ansible_host: 192.168.1.11
        web02:
          ansible_host: 192.168.1.12
    
    databases:
      hosts:
        db01:
          ansible_host: 192.168.1.13
          mysql_role: master

# inventory/production/group_vars/all/common.yml
---
environment: production
domain_name: example.com
admin_email: admin@example.com
ntp_server: time.google.com
timezone: UTC

# inventory/production/group_vars/webservers/webserver.yml
---
apache_version: "2.4"
php_version: "8.1"
app_name: myapp
app_version: "2.0.0"
document_root: /var/www/html

# inventory/production/group_vars/databases/database.yml
---
mysql_version: "8.0"
mysql_root_password: "{{ vault_mysql_root_password }}"
mysql_databases:
  - name: myapp_prod
    encoding: utf8mb4
    collation: utf8mb4_unicode_ci

mysql_users:
  - name: myapp
    password: "{{ vault_mysql_user_password }}"
    priv: "myapp_prod.*:ALL"
    host: "192.168.1.%"
```

---

## Phase 2: Role Development (120 minutes)

### Step 2.1: Common Role

```bash
ansible-galaxy role init roles/common
```

```yaml
# roles/common/tasks/main.yml
---
- name: Update apt cache
  apt:
    update_cache: yes
    cache_valid_time: 3600

- name: Install common packages
  apt:
    name:
      - vim
      - git
      - htop
      - curl
      - wget
      - net-tools
      - unzip
    state: present

- name: Set timezone
  timezone:
    name: "{{ timezone }}"

- name: Configure NTP
  apt:
    name: ntp
    state: present

- name: Start NTP service
  systemd:
    name: ntp
    state: started
    enabled: yes

- name: Create application user
  user:
    name: "{{ app_name }}"
    shell: /bin/bash
    create_home: yes
```

### Step 2.2: HAProxy Role

```yaml
# roles/haproxy/tasks/main.yml
---
- name: Install HAProxy
  apt:
    name: haproxy
    state: present

- name: Configure HAProxy
  template:
    src: haproxy.cfg.j2
    dest: /etc/haproxy/haproxy.cfg
    validate: 'haproxy -c -f %s'
  notify: Restart HAProxy

- name: Enable HAProxy
  systemd:
    name: haproxy
    state: started
    enabled: yes

# roles/haproxy/templates/haproxy.cfg.j2
global
    log /dev/log local0
    maxconn 4096
    user haproxy
    group haproxy
    daemon

defaults
    log global
    mode http
    option httplog
    option dontlognull
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend http_front
    bind *:80
    default_backend web_backend
    
    # Health check endpoint
    acl is_health path_beg /health
    use_backend web_backend if is_health

backend web_backend
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    {% for host in groups['webservers'] %}
    server {{ host }} {{ hostvars[host]['ansible_host'] }}:80 check inter 2000 fall 3 rise 2
    {% endfor %}

listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats auth admin:{{ vault_haproxy_stats_password }}
```

### Step 2.3: Webserver Role

```yaml
# roles/webserver/tasks/main.yml
---
- name: Install Apache and PHP
  apt:
    name:
      - apache2
      - php{{ php_version }}
      - php{{ php_version }}-mysql
      - php{{ php_version }}-curl
      - php{{ php_version }}-json
      - php{{ php_version }}-mbstring
      - php{{ php_version }}-xml
      - libapache2-mod-php{{ php_version }}
    state: present

- name: Enable Apache modules
  apache2_module:
    name: "{{ item }}"
    state: present
  loop:
    - rewrite
    - headers
    - ssl
  notify: Restart Apache

- name: Create document root
  file:
    path: "{{ document_root }}"
    state: directory
    owner: www-data
    group: www-data
    mode: '0755'

- name: Deploy virtual host configuration
  template:
    src: vhost.conf.j2
    dest: /etc/apache2/sites-available/{{ app_name }}.conf
  notify: Reload Apache

- name: Enable site
  command: a2ensite {{ app_name }}.conf
  args:
    creates: /etc/apache2/sites-enabled/{{ app_name }}.conf
  notify: Reload Apache

- name: Disable default site
  command: a2dissite 000-default.conf
  args:
    removes: /etc/apache2/sites-enabled/000-default.conf
  notify: Reload Apache

- name: Deploy application
  synchronize:
    src: ../../files/app/
    dest: "{{ document_root }}/"
    delete: yes
  notify: Reload Apache

- name: Set permissions
  file:
    path: "{{ document_root }}"
    owner: www-data
    group: www-data
    recurse: yes

# roles/webserver/templates/vhost.conf.j2
<VirtualHost *:80>
    ServerName {{ domain_name }}
    ServerAdmin {{ admin_email }}
    DocumentRoot {{ document_root }}
    
    <Directory {{ document_root }}>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    # PHP configuration
    <FilesMatch \.php$>
        SetHandler application/x-httpd-php
    </FilesMatch>
    
    # Logging
    ErrorLog ${APACHE_LOG_DIR}/{{ app_name }}_error.log
    CustomLog ${APACHE_LOG_DIR}/{{ app_name }}_access.log combined
    
    # Health check endpoint
    <Location /health>
        SetHandler server-status
    </Location>
</VirtualHost>
```

### Step 2.4: Database Role

```yaml
# roles/database/tasks/main.yml
---
- name: Install MySQL
  apt:
    name:
      - mysql-server
      - mysql-client
      - python3-pymysql
    state: present

- name: Start MySQL service
  systemd:
    name: mysql
    state: started
    enabled: yes

- name: Set MySQL root password
  mysql_user:
    name: root
    password: "{{ mysql_root_password }}"
    login_unix_socket: /var/run/mysqld/mysqld.sock
    state: present
  no_log: true

- name: Create MySQL configuration
  template:
    src: my.cnf.j2
    dest: /etc/mysql/my.cnf
  notify: Restart MySQL

- name: Create databases
  mysql_db:
    name: "{{ item.name }}"
    encoding: "{{ item.encoding }}"
    collation: "{{ item.collation }}"
    state: present
    login_user: root
    login_password: "{{ mysql_root_password }}"
  loop: "{{ mysql_databases }}"
  no_log: true

- name: Create MySQL users
  mysql_user:
    name: "{{ item.name }}"
    password: "{{ item.password }}"
    priv: "{{ item.priv }}"
    host: "{{ item.host }}"
    state: present
    login_user: root
    login_password: "{{ mysql_root_password }}"
  loop: "{{ mysql_users }}"
  no_log: true

- name: Configure firewall for MySQL
  ufw:
    rule: allow
    port: '3306'
    proto: tcp
    from_ip: 192.168.1.0/24
```

---

## Phase 3: Main Playbooks (60 minutes)

### Step 3.1: Site Playbook

```yaml
# playbooks/site.yml
---
- name: Configure all servers
  hosts: all
  roles:
    - common

- name: Configure load balancer
  hosts: loadbalancers
  roles:
    - haproxy

- name: Configure web servers
  hosts: webservers
  roles:
    - webserver

- name: Configure database servers
  hosts: databases
  roles:
    - database
```

### Step 3.2: Deployment Playbook

```yaml
# playbooks/deploy.yml
---
- name: Deploy application
  hosts: webservers
  serial: 1  # Rolling deployment
  
  tasks:
    - name: Pull latest code
      git:
        repo: https://github.com/company/myapp.git
        dest: /tmp/myapp
        version: "{{ app_version }}"
    
    - name: Run tests
      command: php /tmp/myapp/vendor/bin/phpunit
      args:
        chdir: /tmp/myapp
      changed_when: false
    
    - name: Backup current version
      archive:
        path: "{{ document_root }}"
        dest: "/backup/myapp_{{ ansible_date_time.epoch }}.tar.gz"
    
    - name: Deploy new version
      synchronize:
        src: /tmp/myapp/
        dest: "{{ document_root }}/"
        delete: yes
        rsync_opts:
          - "--exclude=.git"
    
    - name: Set permissions
      file:
        path: "{{ document_root }}"
        owner: www-data
        group: www-data
        recurse: yes
    
    - name: Run database migrations
      command: php {{ document_root }}/artisan migrate --force
      args:
        chdir: "{{ document_root }}"
    
    - name: Clear cache
      command: php {{ document_root }}/artisan cache:clear
      args:
        chdir: "{{ document_root }}"
    
    - name: Reload Apache
      systemd:
        name: apache2
        state: reloaded
    
    - name: Health check
      uri:
        url: "http://{{ ansible_host }}/health"
        status_code: 200
      register: health
      until: health.status == 200
      retries: 10
      delay: 5
    
    - name: Wait before next server
      pause:
        seconds: 30
      when: inventory_hostname != ansible_play_hosts[-1]
```

### Step 3.3: Backup Playbook

```yaml
# playbooks/backup.yml
---
- name: Backup databases
  hosts: databases
  
  vars:
    backup_dir: /backup/mysql
    backup_retention_days: 7
  
  tasks:
    - name: Create backup directory
      file:
        path: "{{ backup_dir }}"
        state: directory
        mode: '0750'
    
    - name: Dump all databases
      mysql_db:
        name: all
        state: dump
        target: "{{ backup_dir }}/all_databases_{{ ansible_date_time.date }}.sql"
        login_user: root
        login_password: "{{ mysql_root_password }}"
      no_log: true
    
    - name: Compress backup
      archive:
        path: "{{ backup_dir }}/all_databases_{{ ansible_date_time.date }}.sql"
        dest: "{{ backup_dir}}/all_databases_{{ ansible_date_time.date }}.sql.gz"
        format: gz
        remove: yes
    
    - name: Upload to S3
      aws_s3:
        bucket: company-backups
        object: "mysql/{{ inventory_hostname }}/all_databases_{{ ansible_date_time.date }}.sql.gz"
        src: "{{ backup_dir }}/all_databases_{{ ansible_date_time.date }}.sql.gz"
        mode: put
        encrypt: yes
      delegate_to: localhost
    
    - name: Remove old backups
      find:
        paths: "{{ backup_dir }}"
        age: "{{ backup_retention_days }}d"
        patterns: "*.sql.gz"
      register: old_backups
    
    - name: Delete old backups
      file:
        path: "{{ item.path }}"
        state: absent
      loop: "{{ old_backups.files }}"
```

---

## Phase 4: CI/CD Integration (45 minutes)

```yaml
# .gitlab-ci.yml
stages:
  - test
  - deploy_dev
  - deploy_staging
  - deploy_prod

variables:
  ANSIBLE_FORCE_COLOR: "true"
  ANSIBLE_HOST_KEY_CHECKING: "false"

test:
  stage: test
  image: cytopia/ansible-lint:latest
  script:
    - ansible-lint playbooks/
    - ansible-playbook --syntax-check playbooks/*.yml
  only:
    - merge_requests
    - main

deploy_dev:
  stage: deploy_dev
  image: ansible/ansible:latest
  script:
    - ansible-playbook -i inventory/development playbooks/site.yml
  environment:
    name: development
  only:
    - main

deploy_staging:
  stage: deploy_staging
  image: ansible/ansible:latest
  script:
    - ansible-playbook -i inventory/staging playbooks/site.yml
  environment:
    name: staging
  when: manual
  only:
    - main

deploy_prod:
  stage: deploy_prod
  image: ansible/ansible:latest
  script:
    - ansible-playbook -i inventory/production playbooks/site.yml
  environment:
    name: production
  when: manual
  only:
    - tags
```

---

## Phase 5: Monitoring (30 minutes)

```yaml
# roles/monitoring/tasks/main.yml
---
- name: Install node_exporter
  apt:
    deb: https://github.com/prometheus/node_exporter/releases/download/v1.5.0/node_exporter_1.5.0_amd64.deb

- name: Create node_exporter service
  systemd:
    name: node_exporter
    state: started
    enabled: yes

- name: Install monitoring agents
  apt:
    name:
      - collectd
      - telegraf
    state: present
```

---

## Project Validation

```bash
# Test connectivity
ansible all -i inventory/production -m ping

# Syntax check
ansible-playbook playbooks/site.yml --syntax-check

# Dry run
ansible-playbook -i inventory/production playbooks/site.yml --check

# Deploy
ansible-playbook -i inventory/production playbooks/site.yml

# Verify deployment
curl http://192.168.1.10
curl http://192.168.1.10/health

# Check HAProxy stats
open http://192.168.1.10:8404/stats
```

---

## Lab Completion

**Congratulations!** You have completed all Ansible labs and built a production-ready LAMP stack automation.

### Skills Mastered:
- ✅ Complete infrastructure automation
- ✅ Multi-tier architecture deployment
- ✅ CI/CD pipeline integration
- ✅ Monitoring and logging
- ✅ Backup and recovery
- ✅ Security hardening
- ✅ Production best practices

### Portfolio Project:
This project demonstrates:
- Real-world automation skills
- Production-ready code
- DevOps best practices
- Complete lifecycle management

**You are now ready for DevOps/Automation Engineer roles!**

---

**Duration:** ~5 hours  
**Difficulty:** Advanced  
**Status:** Complete  
**Portfolio Ready:** ✅
