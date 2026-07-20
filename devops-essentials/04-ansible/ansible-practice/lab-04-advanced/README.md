# Lab 04: Advanced Ansible Topics

> **Dynamic inventory, performance optimization, CI/CD integration, and security**

---

## Lab Overview

**Duration:** 4 hours  
**Difficulty:** Advanced  
**Prerequisites:** Labs 01-03 completed

### Learning Objectives:
- Implement dynamic inventory
- Optimize Ansible performance
- Integrate with CI/CD pipelines
- Apply security best practices
- Use Ansible Vault
- Implement monitoring

---

## Exercise 1: Dynamic Inventory (60 minutes)

### Task 1.1: AWS Dynamic Inventory

```yaml
# inventory/aws_ec2.yml
---
plugin: aws_ec2
regions:
  - us-east-1
  - us-west-2

filters:
  tag:Managed: ansible
  instance-state-name: running

keyed_groups:
  - key: tags.Environment
    prefix: env
  - key: tags.Role
    prefix: role
  - key: placement.availability_zone
    prefix: az

hostnames:
  - tag:Name

compose:
  ansible_host: public_ip_address
  ansible_user: "'ubuntu' if 'ubuntu' in (tags.OS | default('')) else 'ec2-user'"
```

**Usage:**
```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# Test inventory
ansible-inventory -i inventory/aws_ec2.yml --list
ansible-inventory -i inventory/aws_ec2.yml --graph

# Use in playbook
ansible-playbook -i inventory/aws_ec2.yml playbooks/site.yml
```

### Task 1.2: Multi-Cloud Dynamic Inventory Script

```python
#!/usr/bin/env python3
# inventory/dynamic_inventory.py

import json
import boto3  # AWS
from azure.identity import DefaultAzureCredential  # Azure
from azure.mgmt.compute import ComputeManagementClient

def get_aws_instances():
    ec2 = boto3.client('ec2')
    instances = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )
    
    inventory = {'all': {'hosts': []}, '_meta': {'hostvars': {}}}
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            host_name = instance['InstanceId']
            inventory['all']['hosts'].append(host_name)
            inventory['_meta']['hostvars'][host_name] = {
                'ansible_host': instance.get('PublicIpAddress', instance['PrivateIpAddress']),
                'cloud_provider': 'aws',
                'instance_type': instance['InstanceType'],
                'availability_zone': instance['Placement']['AvailabilityZone']
            }
    
    return inventory

def get_azure_instances():
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, 'subscription-id')
    
    inventory = {'all': {'hosts': []}, '_meta': {'hostvars': {}}}
    
    for vm in compute_client.virtual_machines.list_all():
        host_name = vm.name
        inventory['all']['hosts'].append(host_name)
        inventory['_meta']['hostvars'][host_name] = {
            'ansible_host': vm.id,  # Get actual IP via network interface
            'cloud_provider': 'azure',
            'vm_size': vm.hardware_profile.vm_size,
            'location': vm.location
        }
    
    return inventory

def merge_inventories(*inventories):
    merged = {'all': {'hosts': []}, '_meta': {'hostvars': {}}}
    
    for inv in inventories:
        merged['all']['hosts'].extend(inv['all']['hosts'])
        merged['_meta']['hostvars'].update(inv['_meta']['hostvars'])
    
    return merged

if __name__ == '__main__':
    aws_inv = get_aws_instances()
    azure_inv = get_azure_instances()
    final_inv = merge_inventories(aws_inv, azure_inv)
    
    print(json.dumps(final_inv, indent=2))
```

**Usage:**
```bash
chmod +x inventory/dynamic_inventory.py
ansible-playbook -i inventory/dynamic_inventory.py playbooks/site.yml
```

---

## Exercise 2: Performance Optimization (45 minutes)

### Task 2.1: Optimize ansible.cfg

```ini
# ansible.cfg
[defaults]
# Connection settings
forks = 100
host_key_checking = False
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400

# SSH optimization
[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s -o Compression=yes
pipelining = True
control_path_dir = /tmp/ansible-ssh-%%h-%%p-%%r

# Callback plugins for better output
[defaults]
callbacks_enabled = profile_tasks, timer
stdout_callback = yaml
```

### Task 2.2: Performance-Optimized Playbook

```yaml
# playbooks/optimized_deploy.yml
---
- name: Optimized deployment
  hosts: all
  strategy: free  # Fastest for independent tasks
  gather_facts: false  # Skip if not needed
  
  tasks:
    - name: Gather minimal facts
      setup:
        gather_subset:
          - '!all'
          - '!min'
          - network
      when: facts_needed | default(false)
    
    - name: Use async for long-running tasks
      command: /usr/bin/long-running-task
      async: 3600
      poll: 0
      register: long_task
    
    - name: Continue with other work
      package:
        name: nginx
        state: present
    
    - name: Check async task status
      async_status:
        jid: "{{ long_task.ansible_job_id }}"
      register: job_result
      until: job_result.finished
      retries: 30
      delay: 10

- name: Rolling updates with serial
  hosts: webservers
  serial: "25%"  # Update 25% at a time
  max_fail_percentage: 10
  
  tasks:
    - name: Update application
      include_role:
        name: deploy_app
```

### Task 2.3: Mitogen Strategy Plugin

```bash
# Install Mitogen
pip install mitogen

# Configure ansible.cfg
[defaults]
strategy_plugins = /path/to/mitogen/ansible_mitogen/plugins/strategy
strategy = mitogen_linear

# Or use in playbook
- hosts: all
  strategy: mitogen_linear
  tasks:
    - name: Fast task execution
      command: uptime
```

**Performance comparison:**
```bash
# Benchmark standard vs mitogen
time ansible-playbook site.yml
# Standard: 45 seconds

time ansible-playbook site.yml  # with mitogen
# Mitogen: 12 seconds (3-4x faster!)
```

---

## Exercise 3: CI/CD Integration (60 minutes)

### Task 3.1: GitLab CI Pipeline

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
  image: cytopia/ansible-lint:latest
  script:
    - ansible-lint playbooks/
    - yamllint .
  only:
    - merge_requests
    - main

test:
  stage: test
  image: ansible/ansible:latest
  script:
    - ansible-playbook --syntax-check playbooks/*.yml
    - ansible-playbook --check playbooks/site.yml -i inventory/staging
  only:
    - merge_requests

deploy_staging:
  stage: deploy
  image: ansible/ansible:latest
  script:
    - echo "$ANSIBLE_VAULT_PASSWORD" > .vault_pass
    - ansible-playbook playbooks/site.yml -i inventory/staging --vault-password-file .vault_pass
  environment:
    name: staging
  only:
    - main

deploy_production:
  stage: deploy
  image: ansible/ansible:latest
  script:
    - echo "$ANSIBLE_VAULT_PASSWORD" > .vault_pass
    - ansible-playbook playbooks/site.yml -i inventory/production --vault-password-file .vault_pass
  environment:
    name: production
  when: manual
  only:
    - main
```

### Task 3.2: GitHub Actions Pipeline

```yaml
# .github/workflows/ansible.yml
name: Ansible CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run ansible-lint
        uses: ansible/ansible-lint-action@main
        with:
          path: "playbooks/"
  
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Ansible
        run: |
          sudo apt-get update
          sudo apt-get install -y ansible
      
      - name: Syntax check
        run: ansible-playbook --syntax-check playbooks/*.yml
      
      - name: Dry run
        run: ansible-playbook playbooks/site.yml -i inventory/staging --check
  
  deploy_staging:
    needs: [lint, test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: staging
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
      
      - name: Deploy to staging
        run: |
          echo "${{ secrets.VAULT_PASSWORD }}" > .vault_pass
          ansible-playbook playbooks/site.yml -i inventory/staging --vault-password-file .vault_pass
  
  deploy_production:
    needs: [deploy_staging]
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: |
          echo "${{ secrets.VAULT_PASSWORD }}" > .vault_pass
          ansible-playbook playbooks/site.yml -i inventory/production --vault-password-file .vault_pass
```

### Task 3.3: Jenkins Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        ANSIBLE_FORCE_COLOR = 'true'
        ANSIBLE_HOST_KEY_CHECKING = 'false'
    }
    
    stages {
        stage('Lint') {
            steps {
                sh 'ansible-lint playbooks/'
                sh 'yamllint .'
            }
        }
        
        stage('Test') {
            steps {
                sh 'ansible-playbook --syntax-check playbooks/*.yml'
                sh 'ansible-playbook --check playbooks/site.yml -i inventory/staging'
            }
        }
        
        stage('Deploy Staging') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([string(credentialsId: 'ansible-vault-password', variable: 'VAULT_PASS')]) {
                    sh '''
                        echo $VAULT_PASS > .vault_pass
                        ansible-playbook playbooks/site.yml -i inventory/staging --vault-password-file .vault_pass
                    '''
                }
            }
        }
        
        stage('Deploy Production') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                withCredentials([string(credentialsId: 'ansible-vault-password', variable: 'VAULT_PASS')]) {
                    sh '''
                        echo $VAULT_PASS > .vault_pass
                        ansible-playbook playbooks/site.yml -i inventory/production --vault-password-file .vault_pass
                    '''
                }
            }
        }
    }
    
    post {
        always {
            sh 'rm -f .vault_pass'
        }
        success {
            slackSend(color: 'good', message: "Deployment successful: ${env.JOB_NAME} ${env.BUILD_NUMBER}")
        }
        failure {
            slackSend(color: 'danger', message: "Deployment failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}")
        }
    }
}
```

---

## Exercise 4: Security Best Practices (45 minutes)

### Task 4.1: Ansible Vault

```bash
# Create encrypted file
ansible-vault create secrets.yml

# Edit encrypted file
ansible-vault edit secrets.yml

# Encrypt existing file
ansible-vault encrypt inventory/group_vars/production/vault.yml

# Decrypt file
ansible-vault decrypt secrets.yml

# View encrypted file
ansible-vault view secrets.yml

# Rekey (change password)
ansible-vault rekey secrets.yml
```

**Vault file content:**
```yaml
# inventory/group_vars/production/vault.yml
---
vault_db_password: supersecret123
vault_api_key: abc-xyz-789
vault_aws_access_key: AKIAIOSFODNN7EXAMPLE
vault_aws_secret_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

### Task 4.2: Secure Playbook

```yaml
# playbooks/secure_deploy.yml
---
- name: Secure deployment
  hosts: all
  become: true
  
  vars_files:
    - ../inventory/group_vars/{{ environment }}/vault.yml
  
  tasks:
    - name: Configure database connection
      template:
        src: db_config.j2
        dest: /etc/app/database.conf
        mode: '0600'
        owner: appuser
        group: appuser
      no_log: true  # Don't log sensitive data
    
    - name: Set API key environment variable
      lineinfile:
        path: /etc/environment
        line: "API_KEY={{ vault_api_key }}"
        state: present
      no_log: true
    
    - name: Install SSL certificates
      copy:
        content: "{{ vault_ssl_cert }}"
        dest: /etc/ssl/certs/app.crt
        mode: '0644'
      no_log: true
```

### Task 4.3: Security Hardening Playbook

```yaml
# playbooks/security_hardening.yml
---
- name: Security hardening
  hosts: all
  become: true
  
  tasks:
    - name: Update all packages
      apt:
        upgrade: safe
        update_cache: yes
    
    - name: Install security packages
      apt:
        name:
          - fail2ban
          - ufw
          - unattended-upgrades
        state: present
    
    - name: Configure firewall
      ufw:
        rule: "{{ item.rule }}"
        port: "{{ item.port }}"
        proto: "{{ item.proto }}"
      loop:
        - { rule: 'allow', port: '22', proto: 'tcp' }
        - { rule: 'allow', port: '80', proto: 'tcp' }
        - { rule: 'allow', port: '443', proto: 'tcp' }
    
    - name: Enable firewall
      ufw:
        state: enabled
    
    - name: Configure SSH hardening
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: "{{ item.regexp }}"
        line: "{{ item.line }}"
      loop:
        - { regexp: '^#?PermitRootLogin', line: 'PermitRootLogin no' }
        - { regexp: '^#?PasswordAuthentication', line: 'PasswordAuthentication no' }
        - { regexp: '^#?X11Forwarding', line: 'X11Forwarding no' }
      notify: Restart SSH
    
    - name: Set up automatic security updates
      copy:
        content: |
          APT::Periodic::Update-Package-Lists "1";
          APT::Periodic::Download-Upgradeable-Packages "1";
          APT::Periodic::AutocleanInterval "7";
          APT::Periodic::Unattended-Upgrade "1";
        dest: /etc/apt/apt.conf.d/20auto-upgrades
  
  handlers:
    - name: Restart SSH
      systemd:
        name: sshd
        state: restarted
```

---

## Lab Challenges

### Challenge 1: Build Complete CI/CD Pipeline
- Automated testing on every commit
- Deploy to staging automatically
- Manual approval for production
- Rollback capability
- Notifications on Slack/Email

### Challenge 2: Multi-Cloud Management
- Dynamic inventory for AWS + Azure + GCP
- Unified playbooks across clouds
- Cost optimization automation
- Disaster recovery setup

### Challenge 3: Security Compliance
- Implement CIS benchmarks
- Automated security scanning
- Vulnerability remediation
- Compliance reporting

---

## Validation

```bash
# Test dynamic inventory
ansible-inventory -i inventory/aws_ec2.yml --list

# Performance benchmark
time ansible-playbook site.yml

# Security scan
ansible-lint --profile=safety playbooks/

# CI/CD test
git commit -am "test" && git push  # Watch pipeline run
```

---

## Lab Completion

**Congratulations!** You have completed Lab 04.

### Skills Acquired:
- ✅ Dynamic inventory implementation
- ✅ Performance optimization
- ✅ CI/CD integration
- ✅ Security best practices
- ✅ Vault usage
- ✅ Production-ready patterns

### Next Steps:
- Lab 05: Real-World Project

---

**Duration:** ~4 hours  
**Difficulty:** Advanced  
**Status:** Complete
