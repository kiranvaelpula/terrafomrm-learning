# Enterprise Patterns and Production Architecture

> **Production-grade automation patterns for large-scale deployments**

---

## Overview

Enterprise Ansible patterns enable large organizations to scale automation while maintaining control, security, and reliability. This guide covers GitOps workflows, multi-environment strategies, deployment patterns, disaster recovery, and team organization.

---

## 1. GitOps Workflows

### 1.1 GitOps Principles

**Core concepts:**
```yaml
# Git as single source of truth
# All changes through pull requests
# Automated testing and deployment
# Audit trail in version control
```

**Repository structure:**
```bash
ansible-automation/
├── ansible.cfg
├── inventories/
│   ├── production/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   ├── staging/
│   └── development/
├── playbooks/
│   ├── site.yml
│   ├── web_servers.yml
│   └── databases.yml
├── roles/
│   └── requirements.yml
├── .gitlab-ci.yml
└── README.md
```

### 1.2 Branch Strategy

**Environment branches:**
```yaml
# Branch-per-environment pattern
main         → Production
staging      → Staging
development  → Development

# Protection rules:
# - main: Requires 2 approvals, CI passing
# - staging: Requires 1 approval, CI passing
# - development: CI passing
```

**GitLab CI example:**
```yaml
# .gitlab-ci.yml
stages:
  - lint
  - test
  - deploy

variables:
  ANSIBLE_FORCE_COLOR: "true"
  ANSIBLE_HOST_KEY_CHECKING: "false"

lint:
  stage: lint
  image: cytopia/ansible-lint
  script:
    - ansible-lint playbooks/
  only:
    - merge_requests

test:
  stage: test
  image: ansible/ansible:latest
  script:
    - ansible-playbook --syntax-check playbooks/site.yml
    - ansible-playbook --check playbooks/site.yml -i inventories/staging/
  only:
    - merge_requests

deploy_dev:
  stage: deploy
  image: ansible/ansible:latest
  script:
    - ansible-playbook playbooks/site.yml -i inventories/development/
  environment:
    name: development
  only:
    - development

deploy_staging:
  stage: deploy
  image: ansible/ansible:latest
  script:
    - ansible-playbook playbooks/site.yml -i inventories/staging/
  environment:
    name: staging
  when: manual
  only:
    - staging

deploy_production:
  stage: deploy
  image: ansible/ansible:latest
  script:
    - ansible-playbook playbooks/site.yml -i inventories/production/ --limit webservers
  environment:
    name: production
  when: manual
  only:
    - main
  needs:
    - test
```

### 1.3 Pull Request Workflow

**PR template:**
```markdown
## Change Description
Brief description of changes

## Environment Impact
- [ ] Development
- [ ] Staging  
- [ ] Production

## Testing Performed
- [ ] Syntax check passed
- [ ] Dry run (--check) successful
- [ ] Tested in development

## Checklist
- [ ] Variables documented
- [ ] Secrets added to Vault
- [ ] Inventory updated
- [ ] CI pipeline passing
- [ ] Rollback plan documented

## Reviewers
@devops-team @platform-engineering
```

**Automated checks:**
```yaml
# .github/workflows/pr-checks.yml
name: PR Checks
on: [pull_request]

jobs:
  ansible-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run ansible-lint
        uses: ansible/ansible-lint-action@main
  
  syntax-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Syntax check
        run: |
          ansible-playbook --syntax-check playbooks/*.yml
  
  dry-run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check mode
        run: |
          ansible-playbook playbooks/site.yml --check -i inventories/staging/
```

---

## 2. Multi-Environment Patterns

### 2.1 Environment Separation

**Directory structure:**
```bash
inventories/
├── production/
│   ├── hosts.yml
│   ├── group_vars/
│   │   ├── all/
│   │   │   ├── vars.yml
│   │   │   └── vault.yml
│   │   ├── webservers.yml
│   │   └── databases.yml
│   └── host_vars/
│       └── db01.prod.yml
├── staging/
│   ├── hosts.yml
│   └── group_vars/
└── development/
    ├── hosts.yml
    └── group_vars/
```

**Inventory example:**
```yaml
# inventories/production/hosts.yml
all:
  children:
    webservers:
      hosts:
        web01.prod:
          ansible_host: 10.0.1.10
        web02.prod:
          ansible_host: 10.0.1.11
        web03.prod:
          ansible_host: 10.0.1.12
    databases:
      hosts:
        db01.prod:
          ansible_host: 10.0.2.10
          mysql_role: master
        db02.prod:
          ansible_host: 10.0.2.11
          mysql_role: slave
    loadbalancers:
      hosts:
        lb01.prod:
          ansible_host: 10.0.3.10
  vars:
    ansible_user: automation
    ansible_ssh_private_key_file: ~/.ssh/prod_automation_key
    environment_name: production
    environment_tier: prod
```

**Environment-specific variables:**
```yaml
# inventories/production/group_vars/all/vars.yml
---
# Production settings
app_version: "2.1.0"
enable_monitoring: true
enable_ssl: true
backup_retention_days: 30
log_level: "WARNING"

# Resource limits
max_connections: 500
worker_processes: 8
memory_limit: "4G"

# External services
database_host: "db01.prod"
redis_host: "cache.prod.internal"
cdn_url: "https://cdn.production.com"

# SSL certificates
ssl_cert_path: "/etc/ssl/certs/production.crt"
ssl_key_path: "/etc/ssl/private/production.key"
```

### 2.2 Environment Promotion

**Promotion playbook:**
```yaml
# playbooks/promote_release.yml
---
- name: Promote release between environments
  hosts: localhost
  gather_facts: false
  
  vars_prompt:
    - name: source_env
      prompt: "Source environment (development/staging)"
      private: false
    
    - name: target_env
      prompt: "Target environment (staging/production)"
      private: false
    
    - name: release_version
      prompt: "Release version"
      private: false
    
    - name: confirm
      prompt: "Confirm promotion? (yes/no)"
      private: false
  
  tasks:
    - name: Validate confirmation
      assert:
        that:
          - confirm == "yes"
        fail_msg: "Promotion cancelled"
    
    - name: Validate environment progression
      assert:
        that:
          - (source_env == "development" and target_env in ["staging", "production"]) or
            (source_env == "staging" and target_env == "production")
        fail_msg: "Invalid environment progression"
    
    - name: Get source environment state
      shell: |
        git show {{ source_env }}:playbooks/site.yml
      register: source_state
      changed_when: false
    
    - name: Create promotion branch
      shell: |
        git checkout -b promote-{{ release_version }}-to-{{ target_env }}
        git merge {{ source_env }} --no-ff -m "Promote {{ release_version }} to {{ target_env }}"
      delegate_to: localhost
    
    - name: Update version file
      copy:
        content: "{{ release_version }}"
        dest: "inventories/{{ target_env }}/VERSION"
    
    - name: Create pull request
      uri:
        url: "https://api.github.com/repos/{{ org }}/{{ repo }}/pulls"
        method: POST
        headers:
          Authorization: "token {{ github_token }}"
        body_format: json
        body:
          title: "Promote {{ release_version }} to {{ target_env }}"
          head: "promote-{{ release_version }}-to-{{ target_env }}"
          base: "{{ target_env }}"
          body: |
            ## Release Promotion
            
            **Version:** {{ release_version }}
            **Source:** {{ source_env }}
            **Target:** {{ target_env }}
            
            ### Changes
            See commit history for details.
            
            ### Deployment Checklist
            - [ ] CI checks passing
            - [ ] Reviewed by team lead
            - [ ] Deployment window scheduled
            - [ ] Rollback plan documented
```

---

## 3. Blue-Green Deployments

### 3.1 Infrastructure Setup

**Inventory with color groups:**
```yaml
# inventories/production/hosts.yml
all:
  children:
    webservers:
      children:
        blue:
          hosts:
            web01-blue.prod:
            web02-blue.prod:
        green:
          hosts:
            web01-green.prod:
            web02-green.prod:
      vars:
        app_port: 8080
    
    loadbalancers:
      hosts:
        lb01.prod:
          active_color: blue  # Initial state
```

**Blue-green deployment playbook:**
```yaml
# playbooks/blue_green_deploy.yml
---
- name: Blue-Green Deployment
  hosts: localhost
  gather_facts: false
  
  vars:
    current_color: "{{ hostvars['lb01.prod']['active_color'] }}"
    new_color: "{{ 'green' if current_color == 'blue' else 'blue' }}"
    app_version: "{{ lookup('env', 'APP_VERSION') }}"
  
  tasks:
    - name: Determine deployment colors
      debug:
        msg: "Deploying {{ app_version }} to {{ new_color }}, current: {{ current_color }}"

- name: Deploy to inactive environment
  hosts: "webservers:&{{ hostvars['localhost']['new_color'] }}"
  serial: "100%"  # Deploy all at once since traffic not routed yet
  
  tasks:
    - name: Stop application
      systemd:
        name: myapp
        state: stopped
    
    - name: Deploy new version
      copy:
        src: "/builds/myapp-{{ hostvars['localhost']['app_version'] }}.jar"
        dest: "/opt/myapp/myapp.jar"
      notify: restart application
    
    - name: Update configuration
      template:
        src: app.conf.j2
        dest: /opt/myapp/config/application.conf
      notify: restart application
    
    - name: Start application
      systemd:
        name: myapp
        state: started
        enabled: true
    
    - name: Wait for application health
      uri:
        url: "http://{{ ansible_host }}:{{ app_port }}/health"
        status_code: 200
      register: health_check
      until: health_check.status == 200
      retries: 30
      delay: 10
  
  handlers:
    - name: restart application
      systemd:
        name: myapp
        state: restarted

- name: Run smoke tests
  hosts: "webservers:&{{ hostvars['localhost']['new_color'] }}"
  
  tasks:
    - name: Test application endpoints
      uri:
        url: "http://{{ ansible_host }}:{{ app_port }}/{{ item }}"
        return_content: true
      loop:
        - health
        - api/status
        - api/version
      register: smoke_tests
    
    - name: Verify version
      assert:
        that:
          - "'{{ hostvars['localhost']['app_version'] }}' in smoke_tests.results[2].content"
        fail_msg: "Version mismatch detected"

- name: Switch load balancer
  hosts: loadbalancers
  
  vars:
    new_color: "{{ hostvars['localhost']['new_color'] }}"
  
  tasks:
    - name: Update load balancer configuration
      template:
        src: haproxy.cfg.j2
        dest: /etc/haproxy/haproxy.cfg
        backup: true
      vars:
        active_color: "{{ new_color }}"
    
    - name: Reload HAProxy
      systemd:
        name: haproxy
        state: reloaded
    
    - name: Wait for traffic switch
      pause:
        seconds: 30
    
    - name: Verify new backend receiving traffic
      shell: |
        echo "show stat" | socat /var/run/haproxy.sock stdio | \
        grep "{{ new_color }}" | grep "UP"
      register: backend_check
      failed_when: backend_check.rc != 0
    
    - name: Update active color in inventory
      lineinfile:
        path: inventories/production/hosts.yml
        regexp: '^(\s+)active_color:.*'
        line: '\1active_color: {{ new_color }}'
        backrefs: true
      delegate_to: localhost

- name: Monitor new deployment
  hosts: "webservers:&{{ hostvars['localhost']['new_color'] }}"
  
  tasks:
    - name: Monitor error rate for 5 minutes
      shell: |
        journalctl -u myapp -n 100 --since "5 minutes ago" | grep -c ERROR || true
      register: error_count
      retries: 5
      delay: 60
    
    - name: Check error threshold
      assert:
        that:
          - error_count.stdout | int < 10
        fail_msg: "High error rate detected: {{ error_count.stdout }} errors"

- name: Drain old environment (optional)
  hosts: "webservers:&{{ hostvars['localhost']['current_color'] }}"
  
  tasks:
    - name: Wait for active connections to drain
      wait_for:
        port: "{{ app_port }}"
        state: drained
        timeout: 300
    
    - name: Stop old version
      systemd:
        name: myapp
        state: stopped
```

### 3.2 HAProxy Configuration Template

**Load balancer template:**
```jinja2
# templates/haproxy.cfg.j2
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
    default_backend {{ active_color }}_backend
    
    # Health check endpoint
    acl is_health path_beg /health
    use_backend {{ active_color }}_backend if is_health

backend blue_backend
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    {% for host in groups['blue'] %}
    server {{ host }} {{ hostvars[host]['ansible_host'] }}:{{ app_port }} check inter 2000 fall 3 rise 2
    {% endfor %}

backend green_backend
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    {% for host in groups['green'] %}
    server {{ host }} {{ hostvars[host]['ansible_host'] }}:{{ app_port }} check inter 2000 fall 3 rise 2
    {% endfor %}

# Admin interface
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats auth admin:{{ haproxy_stats_password }}
```

---

## 4. Canary Deployments

### 4.1 Gradual Rollout Pattern

**Canary deployment playbook:**
```yaml
# playbooks/canary_deploy.yml
---
- name: Canary Deployment
  hosts: webservers
  serial:
    - "10%"   # First 10% of hosts
    - "25%"   # Then 25% more
    - "50%"   # Then 50% more
    - "100%"  # Finally remaining hosts
  max_fail_percentage: 10
  
  vars:
    app_version: "{{ lookup('env', 'APP_VERSION') }}"
    canary_wait_time: 300  # 5 minutes between batches
  
  tasks:
    - name: Display deployment batch
      debug:
        msg: "Deploying to {{ inventory_hostname }} (Batch {{ ansible_play_batch }})"
    
    - name: Deploy application
      include_role:
        name: application
      vars:
        version: "{{ app_version }}"
    
    - name: Health check
      uri:
        url: "http://{{ ansible_host }}:8080/health"
        status_code: 200
      register: health
      until: health.status == 200
      retries: 30
      delay: 10
    
    - name: Monitor metrics
      include_tasks: monitor_canary.yml
      when: ansible_play_batch | length > 1
    
    - name: Wait before next batch
      pause:
        seconds: "{{ canary_wait_time }}"
      run_once: true
      when: not (ansible_play_batch == play_hosts)

# monitor_canary.yml
---
- name: Query Prometheus for error rate
  uri:
    url: "http://prometheus:9090/api/v1/query"
    method: GET
    body_format: json
    body:
      query: 'rate(http_requests_total{status=~"5.."}[5m])'
  register: error_rate
  delegate_to: localhost
  run_once: true

- name: Check error threshold
  assert:
    that:
      - error_rate.json.data.result[0].value[1] | float < 0.01
    fail_msg: "Error rate too high: {{ error_rate.json.data.result[0].value[1] }}"
  run_once: true

- name: Query response time
  uri:
    url: "http://prometheus:9090/api/v1/query"
    method: GET
    body_format: json
    body:
      query: 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))'
  register: response_time
  delegate_to: localhost
  run_once: true

- name: Check response time threshold
  assert:
    that:
      - response_time.json.data.result[0].value[1] | float < 0.5
    fail_msg: "Response time too high: {{ response_time.json.data.result[0].value[1] }}s"
  run_once: true
```

### 4.2 Weighted Traffic Routing

**Nginx canary configuration:**
```jinja2
# templates/nginx_canary.conf.j2
upstream backend_stable {
    {% for host in groups['webservers'] | difference(groups['canary'] | default([])) %}
    server {{ hostvars[host]['ansible_host'] }}:8080;
    {% endfor %}
}

upstream backend_canary {
    {% for host in groups['canary'] | default([]) %}
    server {{ hostvars[host]['ansible_host'] }}:8080;
    {% endfor %}
}

split_clients "${remote_addr}${http_user_agent}" $backend_selection {
    {{ canary_percentage }}% canary;
    * stable;
}

server {
    listen 80;
    server_name _;
    
    location / {
        set $upstream "backend_stable";
        
        if ($backend_selection = "canary") {
            set $upstream "backend_canary";
        }
        
        proxy_pass http://$upstream;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Canary-Version $backend_selection;
    }
}
```

**Gradual percentage increase:**
```yaml
# playbooks/increase_canary.yml
---
- name: Gradually increase canary traffic
  hosts: loadbalancers
  
  vars:
    percentages: [5, 10, 25, 50, 100]
    wait_time: 600  # 10 minutes between increases
  
  tasks:
    - name: Increase canary traffic gradually
      include_tasks: update_canary_weight.yml
      loop: "{{ percentages }}"
      loop_control:
        loop_var: canary_percentage

# update_canary_weight.yml
---
- name: Update Nginx configuration
  template:
    src: nginx_canary.conf.j2
    dest: /etc/nginx/conf.d/canary.conf
  vars:
    canary_percentage: "{{ canary_percentage }}"

- name: Reload Nginx
  systemd:
    name: nginx
    state: reloaded

- name: Wait and monitor
  pause:
    seconds: "{{ wait_time }}"
  when: canary_percentage < 100

- name: Check metrics
  include_tasks: monitor_canary.yml
  when: canary_percentage < 100
```

---

## 5. Disaster Recovery Patterns

### 5.1 Backup and Restore

**Comprehensive backup playbook:**
```yaml
# playbooks/disaster_recovery/backup.yml
---
- name: Comprehensive System Backup
  hosts: all
  serial: 5  # Backup 5 hosts at a time
  
  vars:
    backup_root: "/backup"
    backup_timestamp: "{{ ansible_date_time.iso8601_basic_short }}"
    backup_retention_days: 30
    s3_bucket: "company-disaster-recovery"
  
  tasks:
    - name: Create backup directory
      file:
        path: "{{ backup_root }}/{{ backup_timestamp }}"
        state: directory
        mode: '0750'
    
    - name: Backup application data
      archive:
        path: /opt/application/data
        dest: "{{ backup_root }}/{{ backup_timestamp }}/app_data.tar.gz"
        format: gz
    
    - name: Backup configuration
      archive:
        path:
          - /etc/myapp
          - /etc/nginx
          - /etc/systemd/system/myapp.service
        dest: "{{ backup_root }}/{{ backup_timestamp }}/config.tar.gz"
        format: gz
    
    - name: Database backup
      shell: |
        mysqldump --all-databases --single-transaction \
          --routines --triggers --events \
          | gzip > {{ backup_root }}/{{ backup_timestamp }}/database.sql.gz
      when: "'databases' in group_names"
    
    - name: Generate backup manifest
      template:
        src: backup_manifest.json.j2
        dest: "{{ backup_root }}/{{ backup_timestamp }}/manifest.json"
    
    - name: Upload to S3
      aws_s3:
        bucket: "{{ s3_bucket }}"
        object: "{{ inventory_hostname }}/{{ backup_timestamp }}/{{ item }}"
        src: "{{ backup_root }}/{{ backup_timestamp }}/{{ item }}"
        mode: put
        encrypt: true
      loop:
        - app_data.tar.gz
        - config.tar.gz
        - database.sql.gz
        - manifest.json
      delegate_to: localhost
    
    - name: Remove old local backups
      find:
        paths: "{{ backup_root }}"
        age: "{{ backup_retention_days }}d"
        recurse: true
      register: old_backups
    
    - name: Delete old backups
      file:
        path: "{{ item.path }}"
        state: absent
      loop: "{{ old_backups.files }}"
```

**Restore playbook:**
```yaml
# playbooks/disaster_recovery/restore.yml
---
- name: Disaster Recovery - Restore
  hosts: all
  serial: 1  # Restore one host at a time
  
  vars_prompt:
    - name: restore_timestamp
      prompt: "Enter backup timestamp to restore (YYYYMMDDTHHMMSS)"
      private: false
    
    - name: confirm_restore
      prompt: "WARNING: This will overwrite current data. Type 'RESTORE' to confirm"
      private: false
  
  tasks:
    - name: Validate confirmation
      assert:
        that:
          - confirm_restore == "RESTORE"
        fail_msg: "Restore cancelled - confirmation not provided"
      run_once: true
    
    - name: Stop services
      systemd:
        name: "{{ item }}"
        state: stopped
      loop:
        - myapp
        - nginx
    
    - name: Download backup from S3
      aws_s3:
        bucket: "{{ s3_bucket }}"
        object: "{{ inventory_hostname }}/{{ restore_timestamp }}/{{ item }}"
        dest: "/tmp/restore/{{ item }}"
        mode: get
      loop:
        - app_data.tar.gz
        - config.tar.gz
        - database.sql.gz
        - manifest.json
      delegate_to: localhost
    
    - name: Verify backup integrity
      shell: |
        gunzip -t {{ item }}
      loop:
        - /tmp/restore/app_data.tar.gz
        - /tmp/restore/config.tar.gz
        - /tmp/restore/database.sql.gz
    
    - name: Backup current state (just in case)
      archive:
        path: /opt/application
        dest: /tmp/pre_restore_backup_{{ ansible_date_time.epoch }}.tar.gz
    
    - name: Restore application data
      unarchive:
        src: /tmp/restore/app_data.tar.gz
        dest: /opt/application/
        remote_src: true
    
    - name: Restore configuration
      unarchive:
        src: /tmp/restore/config.tar.gz
        dest: /
        remote_src: true
    
    - name: Restore database
      shell: |
        gunzip < /tmp/restore/database.sql.gz | mysql
      when: "'databases' in group_names"
    
    - name: Start services
      systemd:
        name: "{{ item }}"
        state: started
      loop:
        - myapp
        - nginx
    
    - name: Verify services
      wait_for:
        port: 8080
        timeout: 60
    
    - name: Health check
      uri:
        url: "http://localhost:8080/health"
        status_code: 200
      register: health
      until: health.status == 200
      retries: 10
      delay: 5
    
    - name: Cleanup restore files
      file:
        path: /tmp/restore
        state: absent
```

### 5.2 Disaster Recovery Testing

**DR drill playbook:**
```yaml
# playbooks/disaster_recovery/dr_drill.yml
---
- name: Disaster Recovery Drill
  hosts: localhost
  gather_facts: false
  
  vars:
    dr_environment: "dr-test"
    drill_date: "{{ ansible_date_time.date }}"
  
  tasks:
    - name: Create DR test environment
      ec2_instance:
        name: "{{ item }}-dr-drill"
        instance_type: t3.medium
        image_id: ami-0c55b159cbfafe1f0
        region: us-west-2
        vpc_subnet_id: subnet-dr-test
        tags:
          Environment: "{{ dr_environment }}"
          DrillDate: "{{ drill_date }}"
      loop:
        - web-server
        - app-server
        - db-server
      register: dr_instances
    
    - name: Wait for instances
      wait_for:
        host: "{{ item.public_ip }}"
        port: 22
        timeout: 300
      loop: "{{ dr_instances.results }}"
    
    - name: Add to dynamic inventory
      add_host:
        name: "{{ item.instance.tags.Name }}"
        ansible_host: "{{ item.public_ip }}"
        groups: dr_drill
      loop: "{{ dr_instances.results }}"

- name: Restore to DR environment
  hosts: dr_drill
  
  tasks:
    - name: Run restore playbook
      include_tasks: restore.yml
    
    - name: Run smoke tests
      include_tasks: ../testing/smoke_tests.yml
    
    - name: Verify application functionality
      uri:
        url: "http://{{ ansible_host }}:8080/{{ item }}"
        return_content: true
      loop:
        - health
        - api/status
        - api/test-data
    
    - name: Generate DR drill report
      template:
        src: dr_report.j2
        dest: "/tmp/dr_drill_report_{{ drill_date }}.html"
      delegate_to: localhost
      run_once: true

- name: Cleanup DR drill environment
  hosts: localhost
  
  tasks:
    - name: Terminate drill instances
      ec2_instance:
        instance_ids: "{{ item.instance.id }}"
        state: absent
      loop: "{{ dr_instances.results }}"
      when: auto_cleanup | default(true)
```

---

## 6. Multi-Region Architecture

### 6.1 Active-Active Configuration

**Multi-region inventory:**
```yaml
# inventories/multi-region/hosts.yml
all:
  children:
    us_east:
      children:
        us_east_webservers:
          hosts:
            web01.us-east:
            web02.us-east:
        us_east_databases:
          hosts:
            db01.us-east:
      vars:
        aws_region: us-east-1
        datacenter: us-east
    
    us_west:
      children:
        us_west_webservers:
          hosts:
            web01.us-west:
            web02.us-west:
        us_west_databases:
          hosts:
            db01.us-west:
      vars:
        aws_region: us-west-2
        datacenter: us-west
    
    eu_central:
      children:
        eu_central_webservers:
          hosts:
            web01.eu-central:
            web02.eu-central:
        eu_central_databases:
          hosts:
            db01.eu-central:
      vars:
        aws_region: eu-central-1
        datacenter: eu-central
```

**Multi-region deployment:**
```yaml
# playbooks/multi_region_deploy.yml
---
- name: Deploy to all regions
  hosts: all
  strategy: free  # Deploy to all regions simultaneously
  
  vars:
    app_version: "{{ lookup('env', 'APP_VERSION') }}"
  
  tasks:
    - name: Deploy application
      include_role:
        name: application
      vars:
        version: "{{ app_version }}"
        region: "{{ aws_region }}"
    
    - name: Configure region-specific settings
      template:
        src: app_config.j2
        dest: /opt/application/config/{{ datacenter }}.conf
      vars:
        primary_db: "db01.{{ datacenter }}"
        replica_db: "db01.{{ 'us-west' if datacenter == 'us-east' else 'us-east' }}"
    
    - name: Health check
      uri:
        url: "http://{{ ansible_host }}:8080/health"
        status_code: 200
      register: health
      until: health.status == 200
      retries: 30
      delay: 10

- name: Update global load balancer
  hosts: localhost
  
  tasks:
    - name: Update Route53 health checks
      route53_health_check:
        state: present
        fqdn: "web01.{{ item }}.example.com"
        type: HTTPS
        resource_path: /health
        port: 443
        request_interval: 30
        failure_threshold: 3
      loop:
        - us-east
        - us-west
        - eu-central
    
    - name: Update Route53 weighted routing
      route53:
        state: present
        zone: example.com
        record: app.example.com
        type: A
        value: "{{ item.ip }}"
        weight: "{{ item.weight }}"
        identifier: "{{ item.region }}"
        health_check: "{{ item.healthcheck_id }}"
      loop:
        - { region: 'us-east', ip: '10.0.1.10', weight: 100, healthcheck_id: 'hc-us-east' }
        - { region: 'us-west', ip: '10.1.1.10', weight: 100, healthcheck_id: 'hc-us-west' }
        - { region: 'eu-central', ip: '10.2.1.10', weight: 100, healthcheck_id: 'hc-eu' }
```

### 6.2 Database Replication

**Multi-region database setup:**
```yaml
# playbooks/database_replication.yml
---
- name: Configure master database
  hosts: us_east_databases
  
  tasks:
    - name: Enable binary logging
      mysql_variables:
        variable: log_bin
        value: mysql-bin
    
    - name: Set server ID
      mysql_variables:
        variable: server_id
        value: 1
    
    - name: Create replication user
      mysql_user:
        name: replicator
        host: '%'
        password: "{{ replication_password }}"
        priv: '*.*:REPLICATION SLAVE'
        state: present
    
    - name: Get master status
      mysql_replication:
        mode: getmaster
      register: master_status

- name: Configure replica databases
  hosts: us_west_databases:eu_central_databases
  
  tasks:
    - name: Set unique server ID
      mysql_variables:
        variable: server_id
        value: "{{ groups['all'].index(inventory_hostname) + 2 }}"
    
    - name: Configure replication
      mysql_replication:
        mode: changeprimary
        primary_host: "{{ hostvars[groups['us_east_databases'][0]]['ansible_host'] }}"
        primary_user: replicator
        primary_password: "{{ replication_password }}"
        primary_log_file: "{{ hostvars[groups['us_east_databases'][0]]['master_status']['File'] }}"
        primary_log_pos: "{{ hostvars[groups['us_east_databases'][0]]['master_status']['Position'] }}"
    
    - name: Start replication
      mysql_replication:
        mode: startreplica
    
    - name: Verify replication status
      mysql_replication:
        mode: getreplica
      register: replica_status
    
    - name: Check replication health
      assert:
        that:
          - replica_status.Slave_IO_Running == "Yes"
          - replica_status.Slave_SQL_Running == "Yes"
          - replica_status.Seconds_Behind_Master | int < 10
        fail_msg: "Replication not healthy on {{ inventory_hostname }}"
```

---

## 7. Scaling Strategies

### 7.1 Horizontal Scaling

**Auto-scaling playbook:**
```yaml
# playbooks/auto_scale.yml
---
- name: Scale based on metrics
  hosts: localhost
  gather_facts: false
  
  vars:
    target_cpu_percent: 70
    min_instances: 2
    max_instances: 10
    scale_up_threshold: 80
    scale_down_threshold: 30
  
  tasks:
    - name: Get current metrics
      uri:
        url: "http://prometheus:9090/api/v1/query"
        method: GET
        body_format: json
        body:
          query: 'avg(100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100))'
      register: cpu_metrics
    
    - name: Calculate current CPU usage
      set_fact:
        current_cpu: "{{ cpu_metrics.json.data.result[0].value[1] | float }}"
        current_instances: "{{ groups['webservers'] | length }}"
    
    - name: Determine scaling action
      set_fact:
        scale_action: >-
          {% if current_cpu > scale_up_threshold and current_instances < max_instances %}
          scale_up
          {% elif current_cpu < scale_down_threshold and current_instances > min_instances %}
          scale_down
          {% else %}
          no_action
          {% endif %}
    
    - name: Scale up
      ec2_instance:
        name: "web{{ current_instances | int + 1 }}.prod"
        instance_type: t3.medium
        image_id: ami-app-server
        region: us-east-1
        vpc_subnet_id: subnet-prod
        security_group: sg-webservers
        tags:
          Role: webserver
          Environment: production
        user_data: |
          #!/bin/bash
          /usr/local/bin/bootstrap-webserver.sh
      when: scale_action == "scale_up"
      register: new_instance
    
    - name: Add to load balancer
      elb_target_group:
        name: prod-webservers-tg
        protocol: http
        port: 80
        vpc_id: vpc-prod
        target_type: instance
        targets:
          - Id: "{{ new_instance.instance_ids[0] }}"
            Port: 80
      when: scale_action == "scale_up"
    
    - name: Scale down
      block:
        - name: Select instance to terminate
          set_fact:
            instance_to_terminate: "{{ groups['webservers'] | sort | last }}"
        
        - name: Drain connections
          elb_target:
            target_group_arn: "{{ target_group_arn }}"
            target_id: "{{ hostvars[instance_to_terminate]['ec2_id'] }}"
            state: draining
        
        - name: Wait for drain
          pause:
            seconds: 300
        
        - name: Terminate instance
          ec2_instance:
            instance_ids: "{{ hostvars[instance_to_terminate]['ec2_id'] }}"
            state: absent
      when: scale_action == "scale_down"
    
    - name: Log scaling action
      lineinfile:
        path: /var/log/ansible/autoscale.log
        line: "{{ ansible_date_time.iso8601 }} - {{ scale_action }} - CPU: {{ current_cpu }}% - Instances: {{ current_instances }}"
        create: true
      delegate_to: localhost
```

### 7.2 Performance Testing

**Load testing playbook:**
```yaml
# playbooks/performance_test.yml
---
- name: Performance and Load Testing
  hosts: localhost
  gather_facts: false
  
  vars:
    target_url: "https://app.production.com"
    test_duration: 600  # 10 minutes
    concurrent_users: [10, 50, 100, 200, 500]
  
  tasks:
    - name: Install testing tools
      pip:
        name:
          - locust
          - requests
    
    - name: Create test scenarios
      copy:
        content: |
          from locust import HttpUser, task, between
          
          class WebsiteUser(HttpUser):
              wait_time = between(1, 3)
              
              @task(3)
              def index_page(self):
                  self.client.get("/")
              
              @task(2)
              def api_status(self):
                  self.client.get("/api/status")
              
              @task(1)
              def api_data(self):
                  self.client.get("/api/data")
        dest: /tmp/locustfile.py
    
    - name: Run load tests
      shell: |
        locust -f /tmp/locustfile.py \
          --host={{ target_url }} \
          --users={{ item }} \
          --spawn-rate=10 \
          --run-time={{ test_duration }}s \
          --headless \
          --only-summary \
          --csv=/tmp/results_{{ item }}_users
      loop: "{{ concurrent_users }}"
    
    - name: Analyze results
      shell: |
        awk -F, 'NR>1 {sum+=$10; count++} END {print sum/count}' \
          /tmp/results_{{ item }}_users_stats.csv
      loop: "{{ concurrent_users }}"
      register: response_times
    
    - name: Generate performance report
      template:
        src: performance_report.j2
        dest: /tmp/performance_report_{{ ansible_date_time.date }}.html
      vars:
        test_results: "{{ response_times.results }}"
```

---

## 8. Team Organization

### 8.1 Role-Based Access Control

**RBAC structure:**
```yaml
# group_vars/all/rbac.yml
---
ansible_teams:
  platform_engineering:
    members:
      - alice
      - bob
    permissions:
      - full_access
    can_run:
      - all_playbooks
  
  application_team:
    members:
      - charlie
      - diana
    permissions:
      - deploy_applications
      - view_logs
    can_run:
      - deploy.yml
      - rollback.yml
    cannot_run:
      - infrastructure.yml
  
  security_team:
    members:
      - eve
      - frank
    permissions:
      - audit_access
      - security_updates
    can_run:
      - security_patch.yml
      - compliance_check.yml
  
  readonly_team:
    members:
      - grace
    permissions:
      - read_only
    can_run:
      - check_status.yml
```

**Enforcing RBAC:**
```yaml
# playbooks/enforce_rbac.yml
---
- name: Enforce RBAC
  hosts: localhost
  gather_facts: false
  
  tasks:
    - name: Get current user
      set_fact:
        current_user: "{{ lookup('env', 'USER') }}"
    
    - name: Determine user's team
      set_fact:
        user_team: "{{ item.key }}"
      loop: "{{ ansible_teams | dict2items }}"
      when: current_user in item.value.members
    
    - name: Check playbook permission
      assert:
        that:
          - >-
            (ansible_play_name in ansible_teams[user_team].can_run) or
            ('all_playbooks' in ansible_teams[user_team].can_run)
        fail_msg: "User {{ current_user }} not authorized to run {{ ansible_play_name }}"
    
    - name: Log access attempt
      lineinfile:
        path: /var/log/ansible/access.log
        line: "{{ ansible_date_time.iso8601 }} - {{ current_user }} - {{ ansible_play_name }} - ALLOWED"
        create: true
```

### 8.2 Code Review Process

**Pre-commit hooks:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/ansible/ansible-lint
    rev: v6.14.0
    hooks:
      - id: ansible-lint
        files: \.(yaml|yml)$
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
  
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.29.0
    hooks:
      - id: yamllint
        args: [-c=.yamllint.yml]
```

**Automated review checklist:**
```yaml
# .github/workflows/review-checklist.yml
name: Automated Review Checklist

on: [pull_request]

jobs:
  review_checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check for documentation
        run: |
          if ! grep -r "^# " playbooks/*.yml; then
            echo "::error::Playbooks must include documentation comments"
            exit 1
          fi
      
      - name: Check for tags
        run: |
          if ! grep -r "tags:" playbooks/*.yml; then
            echo "::warning::Consider adding tags to tasks"
          fi
      
      - name: Check for error handling
        run: |
          if ! grep -r "block:\|rescue:\|always:" playbooks/*.yml; then
            echo "::warning::Consider adding error handling"
          fi
      
      - name: Check for idempotency
        run: |
          ansible-playbook playbooks/*.yml --check --diff
      
      - name: Security scan
        run: |
          ansible-lint --profile=safety playbooks/
      
      - name: Complexity check
        run: |
          find playbooks -name "*.yml" -exec wc -l {} \; | awk '$1 > 300 {print "::warning file=" $2 "::Playbook exceeds 300 lines"}'
      
      - name: Post checklist comment
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Automated Review Checklist
              
              - [x] Syntax check passed
              - [x] Ansible-lint passed
              - [x] Idempotency verified
              - [ ] Peer review complete
              - [ ] Documentation updated
              - [ ] Tested in staging
              `
            })
```

---

## 9. Production Best Practices

### 9.1 Deployment Checklist

**Pre-deployment verification:**
```yaml
# playbooks/pre_deployment_checks.yml
---
- name: Pre-Deployment Verification
  hosts: localhost
  gather_facts: false
  
  vars:
    deployment_checklist:
      - name: "Backup completed"
        command: "ls -l /backup/$(date +%Y%m%d)* | wc -l"
        expected: "> 0"
      
      - name: "CI pipeline passed"
        command: "curl -s https://ci.company.com/api/v1/pipelines/latest/status"
        expected: "success"
      
      - name: "All tests passing"
        command: "ansible-playbook playbooks/test_suite.yml --check"
        expected: "0"
      
      - name: "Staging verification done"
        command: "curl -s https://staging.company.com/health"
        expected: "200"
      
      - name: "Security scan clean"
        command: "trivy fs --severity HIGH,CRITICAL ."
        expected: "0"
      
      - name: "Database migrations ready"
        command: "ls -1 migrations/*.sql | wc -l"
        expected: ">= 0"
      
      - name: "Rollback plan exists"
        command: "test -f docs/rollback_{{ deployment_version }}.md"
        expected: "0"
      
      - name: "Monitoring alerts configured"
        command: "curl -s http://prometheus:9090/api/v1/rules | jq '.data.groups[].rules[].alert' | wc -l"
        expected: "> 0"
      
      - name: "On-call engineer notified"
        command: "curl -s https://pagerduty.com/api/v1/oncalls"
        expected: "contains: 'on-call'"
  
  tasks:
    - name: Run checklist items
      shell: "{{ item.command }}"
      register: check_results
      loop: "{{ deployment_checklist }}"
      ignore_errors: true
    
    - name: Evaluate results
      set_fact:
        failed_checks: |
          {% set failures = [] %}
          {% for item in check_results.results %}
          {% if item.rc != 0 %}
          {% set _ = failures.append(deployment_checklist[loop.index0].name) %}
          {% endif %}
          {% endfor %}
          {{ failures }}
    
    - name: Display results
      debug:
        msg: |
          Deployment Pre-checks Summary:
          Passed: {{ check_results.results | selectattr('rc', 'equalto', 0) | list | length }}
          Failed: {{ failed_checks | length }}
          {% if failed_checks | length > 0 %}
          Failed Checks:
          {% for check in failed_checks %}
            - {{ check }}
          {% endfor %}
          {% endif %}
    
    - name: Fail if critical checks failed
      fail:
        msg: "{{ failed_checks | length }} pre-deployment checks failed. Deployment blocked."
      when: failed_checks | length > 0
    
    - name: Log successful pre-checks
      lineinfile:
        path: /var/log/ansible/deployments.log
        line: "{{ ansible_date_time.iso8601 }} - PRE-CHECK PASSED - Ready for deployment"
        create: true
```

### 9.2 Post-Deployment Validation

**Comprehensive validation:**
```yaml
# playbooks/post_deployment_validation.yml
---
- name: Post-Deployment Validation
  hosts: all
  serial: "100%"
  
  vars:
    validation_timeout: 300
    health_check_retries: 30
  
  tasks:
    - name: Wait for service to stabilize
      pause:
        seconds: 30
    
    - name: Check service status
      systemd:
        name: myapp
      register: service_status
      failed_when: service_status.status.ActiveState != "active"
    
    - name: Verify application health
      uri:
        url: "http://{{ ansible_host }}:8080/health"
        status_code: 200
        return_content: true
      register: health_check
      until: health_check.status == 200
      retries: "{{ health_check_retries }}"
      delay: 10
    
    - name: Check application version
      uri:
        url: "http://{{ ansible_host }}:8080/api/version"
        return_content: true
      register: version_check
      failed_when: deployment_version not in version_check.content
    
    - name: Verify database connectivity
      shell: |
        mysql -h {{ database_host }} -u {{ db_user }} -p{{ db_password }} \
          -e "SELECT 1" > /dev/null 2>&1
      register: db_check
      failed_when: db_check.rc != 0
    
    - name: Check API endpoints
      uri:
        url: "http://{{ ansible_host }}:8080/api/{{ item }}"
        status_code: 200
      loop:
        - users
        - products
        - orders
      register: api_checks
    
    - name: Verify log files
      stat:
        path: /var/log/myapp/application.log
      register: log_file
      failed_when: not log_file.stat.exists
    
    - name: Check for errors in logs
      shell: |
        tail -n 100 /var/log/myapp/application.log | grep -i "error\|exception" | wc -l
      register: error_count
      failed_when: error_count.stdout | int > 5
    
    - name: Verify resource usage
      shell: |
        ps aux | grep myapp | awk '{sum+=$3} END {print sum}'
      register: cpu_usage
      failed_when: cpu_usage.stdout | float > 80.0
    
    - name: Check memory usage
      shell: |
        ps aux | grep myapp | awk '{sum+=$4} END {print sum}'
      register: mem_usage
      failed_when: mem_usage.stdout | float > 80.0
    
    - name: Verify SSL certificate
      openssl_certificate_info:
        path: /etc/ssl/certs/myapp.crt
      register: cert_info
      failed_when: 
        - cert_info.expired
        - (cert_info.not_after | to_datetime('%Y%m%d%H%M%SZ') - ansible_date_time.epoch | int) < 604800
    
    - name: Test connectivity to external services
      wait_for:
        host: "{{ item.host }}"
        port: "{{ item.port }}"
        timeout: 30
      loop:
        - { host: "api.external.com", port: 443 }
        - { host: "redis.internal", port: 6379 }
        - { host: "kafka.internal", port: 9092 }

- name: Smoke Tests
  hosts: localhost
  
  tasks:
    - name: Run end-to-end test suite
      shell: |
        pytest tests/smoke/ --junitxml=/tmp/smoke-results.xml
      register: smoke_tests
      failed_when: smoke_tests.rc != 0
    
    - name: Check metrics in Prometheus
      uri:
        url: "http://prometheus:9090/api/v1/query"
        method: GET
        body_format: json
        body:
          query: 'up{job="myapp"}'
      register: metrics_check
      failed_when: metrics_check.json.data.result | length == 0
    
    - name: Verify no alerts firing
      uri:
        url: "http://prometheus:9090/api/v1/alerts"
      register: alerts
      failed_when: alerts.json.data.alerts | selectattr('state', 'equalto', 'firing') | list | length > 0
    
    - name: Generate validation report
      template:
        src: validation_report.j2
        dest: "/tmp/validation_{{ ansible_date_time.iso8601_basic_short }}.html"
    
    - name: Send success notification
      slack:
        token: "{{ slack_token }}"
        channel: "#deployments"
        msg: |
          ✅ Deployment Successful!
          Version: {{ deployment_version }}
          Environment: {{ environment_name }}
          Validation: All checks passed
          Duration: {{ deployment_duration }}
```

---

## 10. Common Patterns and Anti-Patterns

### 10.1 Good Patterns

**Pattern: Immutable infrastructure**
```yaml
# Build AMI, deploy new instances
- name: Immutable deployment
  hosts: localhost
  tasks:
    - name: Build application AMI
      ec2_ami:
        instance_id: "{{ build_instance_id }}"
        name: "myapp-{{ version }}-{{ ansible_date_time.epoch }}"
        wait: true
      register: new_ami
    
    - name: Launch new instances
      ec2_instance:
        image_id: "{{ new_ami.image_id }}"
        instance_type: t3.medium
        count: 3
    
    - name: Terminate old instances
      ec2_instance:
        instance_ids: "{{ old_instance_ids }}"
        state: absent
```

**Pattern: Feature flags**
```yaml
# Gradual feature rollout
- name: Deploy with feature flags
  hosts: webservers
  tasks:
    - name: Configure feature flags
      template:
        src: features.json.j2
        dest: /opt/app/config/features.json
      vars:
        features:
          new_checkout: "{{ '100' if environment == 'production' else '50' }}"
          beta_ui: "{{ '10' if environment == 'production' else '100' }}"
```

**Pattern: Circuit breaker**
```yaml
# Prevent cascading failures
- name: Configure circuit breaker
  hosts: all
  tasks:
    - name: Install Envoy proxy
      package:
        name: envoy
    
    - name: Configure circuit breaker
      template:
        src: envoy_circuit_breaker.yaml.j2
        dest: /etc/envoy/envoy.yaml
      vars:
        max_connections: 1024
        max_pending_requests: 1024
        max_retries: 3
```

### 10.2 Anti-Patterns to Avoid

**❌ Anti-pattern: Hardcoded values**
```yaml
# BAD
- name: Deploy application
  copy:
    src: /home/john/myapp.jar
    dest: /opt/app/  # Hardcoded path
```

**✅ Good practice:**
```yaml
# GOOD
- name: Deploy application
  copy:
    src: "{{ build_artifact_path }}"
    dest: "{{ app_install_dir }}"
```

**❌ Anti-pattern: No error handling**
```yaml
# BAD
- name: Risky operation
  shell: rm -rf /tmp/cache/*
```

**✅ Good practice:**
```yaml
# GOOD
- name: Safe cache cleanup
  block:
    - name: Check if cache exists
      stat:
        path: /tmp/cache
      register: cache_dir
    
    - name: Clear cache safely
      file:
        path: /tmp/cache
        state: absent
      when: cache_dir.stat.exists
  rescue:
    - name: Log error
      debug:
        msg: "Cache cleanup failed, continuing..."
```

---

## Summary

Enterprise Ansible patterns enable:

- **GitOps workflows** - Version-controlled infrastructure
- **Multi-environment management** - Consistent deployments
- **Zero-downtime deployments** - Blue-green, canary patterns  
- **Disaster recovery** - Automated backup and restore
- **Multi-region architecture** - Global scale
- **Auto-scaling** - Dynamic capacity
- **Team collaboration** - RBAC, code review
- **Production reliability** - Comprehensive validation

Master these patterns for enterprise-grade automation at scale.

---

**Next:** [Interview Questions - Advanced](interview-questions-advanced.md)  
**Previous:** [CI/CD Integration](19-cicd-integration.md)  
**Home:** [Ansible Learning Path](../README.md)
