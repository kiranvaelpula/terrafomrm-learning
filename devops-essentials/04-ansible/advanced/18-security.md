# Security Best Practices

> **Secure your Ansible automation with enterprise security patterns**

---

## 📖 What You'll Learn

- Security fundamentals
- Access control and authentication
- Secrets management
- Audit logging
- Compliance automation
- Best practices

---

## 🔐 Security Principles

### Defense in Depth

**Multiple security layers:**
1. Network security
2. Access control
3. Authentication
4. Encryption
5. Audit logging
6. Monitoring

### Least Privilege

```yaml
# Grant minimum necessary permissions
tasks:
  - name: Run as specific user
    command: /app/script.sh
    become: yes
    become_user: appuser  # Not root
```

---

## 🔑 Access Control

### SSH Key Management

```yaml
# Use SSH keys, not passwords
ansible_ssh_private_key_file: ~/.ssh/ansible_key
ansible_ssh_user: ansible

# Rotate keys regularly
# Use different keys per environment
```

### Bastion/Jump Host

```ini
# ansible.cfg
[ssh_connection]
ssh_args = -o ProxyCommand="ssh -W %h:%p -q bastion-host"
```

```yaml
# inventory
[production]
prod-web01 ansible_ssh_common_args='-o ProxyCommand="ssh -W %h:%p bastion.prod.com"'
```

### Sudo Configuration

```bash
# /etc/sudoers.d/ansible
ansible ALL=(ALL) NOPASSWD: /usr/bin/apt-get, /usr/bin/systemctl
```

```yaml
# Playbook
- name: Restricted sudo
  hosts: all
  become: yes
  become_method: sudo
  become_user: root
  
  tasks:
    - name: Install package
      apt:
        name: nginx
        state: present
```

---

## 🔒 Secrets Management

### Ansible Vault

```yaml
# Encrypt sensitive files
# ansible-vault encrypt vars/secrets.yml

vars_files:
  - vars/secrets.yml

tasks:
  - name: Use secret
    debug:
      msg: "{{ secret_api_key }}"
    no_log: yes  # Don't log secrets
```

### External Secret Managers

**HashiCorp Vault:**
```yaml
---
- name: Use Vault
  hosts: all
  tasks:
    - name: Get secret from Vault
      set_fact:
        db_password: "{{ lookup('hashi_vault', 'secret=secret/data/myapp:password') }}"
      no_log: yes
    
    - name: Use secret
      postgresql_user:
        password: "{{ db_password }}"
      no_log: yes
```

**AWS Secrets Manager:**
```yaml
- name: Get AWS secret
  set_fact:
    api_key: "{{ lookup('aws_secret', 'prod/api_key', region='us-east-1') }}"
  no_log: yes
```

### Environment Variables

```yaml
# Use environment vars for sensitive data
- name: Use env var
  command: /deploy.sh
  environment:
    API_KEY: "{{ lookup('env', 'API_KEY') }}"
  no_log: yes
```

---

## 📝 Audit Logging

### Enable Logging

```ini
# ansible.cfg
[defaults]
log_path = /var/log/ansible/ansible.log
syslog_facility = LOG_LOCAL0
```

### Detailed Logging

```yaml
# callbacks for logging
[defaults]
callbacks_enabled = log_plays, mail, profile_tasks

[callback_log_plays]
log_folder = /var/log/ansible/playbooks
```

### Custom Logging

```yaml
tasks:
  - name: Log action
    lineinfile:
      path: /var/log/ansible_custom.log
      line: "{{ ansible_date_time.iso8601 }} - {{ ansible_user_id }} - {{ ansible_playbook }} - {{ inventory_hostname }}"
      create: yes
    delegate_to: localhost
```

---

## 🛡️ Playbook Security

### No Log for Sensitive Data

```yaml
tasks:
  - name: Set password
    user:
      name: admin
      password: "{{ admin_password }}"
    no_log: yes  # Critical!
  
  - name: Deploy API key
    template:
      src: config.j2
      dest: /etc/app/config
    no_log: yes
```

### Input Validation

```yaml
- name: Validate input
  assert:
    that:
      - environment in ['dev', 'staging', 'prod']
      - app_port | int >= 1024
      - app_port | int <= 65535
    fail_msg: "Invalid input parameters"
```

### Safe Command Execution

```yaml
# Bad - command injection risk
- command: "cat {{ user_input }}"

# Good - use quote filter
- command: "cat {{ user_input | quote }}"

# Better - use modules
- slurp:
    path: "{{ user_input }}"
```

---

## 🔍 Security Scanning

### Ansible Lint

```bash
# Install
pip install ansible-lint

# Run
ansible-lint playbook.yml

# Custom rules
ansible-lint -r .ansible-lint-rules/ playbook.yml
```

**`.ansible-lint`:**
```yaml
---
skip_list:
  - '204'  # Lines > 160 chars
  
warn_list:
  - experimental

exclude_paths:
  - .github/
  - test/
```

### Security Rules

```yaml
# Force no_log for sensitive modules
- name: Security check
  assert:
    that:
      - item.no_log is defined
      - item.no_log | bool
  loop: "{{ playbook.tasks }}"
  when: item.module in ['user', 'postgresql_user', 'mysql_user']
```

---

## 🏢 Compliance Automation

### CIS Benchmarks

```yaml
---
- name: CIS Security Hardening
  hosts: all
  become: yes
  
  tasks:
    - name: Disable root SSH login
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^PermitRootLogin'
        line: 'PermitRootLogin no'
      notify: restart sshd
    
    - name: Require key-based SSH
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^PasswordAuthentication'
        line: 'PasswordAuthentication no'
      notify: restart sshd
    
    - name: Set password policy
      lineinfile:
        path: /etc/login.defs
        regexp: '^PASS_MAX_DAYS'
        line: 'PASS_MAX_DAYS 90'
    
    - name: Enable firewall
      ufw:
        state: enabled
        policy: deny
    
    - name: Allow SSH
      ufw:
        rule: allow
        port: '22'
        proto: tcp
  
  handlers:
    - name: restart sshd
      service:
        name: sshd
        state: restarted
```

### STIG Compliance

```yaml
---
- name: Apply STIG controls
  hosts: all
  become: yes
  
  tasks:
    - name: Set file permissions
      file:
        path: "{{ item.path }}"
        mode: "{{ item.mode }}"
      loop:
        - { path: '/etc/passwd', mode: '0644' }
        - { path: '/etc/shadow', mode: '0000' }
        - { path: '/etc/group', mode: '0644' }
    
    - name: Configure audit rules
      copy:
        dest: /etc/audit/rules.d/stig.rules
        content: |
          -w /etc/passwd -p wa -k identity
          -w /etc/group -p wa -k identity
          -w /etc/shadow -p wa -k identity
          -w /var/log/lastlog -p wa -k logins
      notify: restart auditd
```

---

## 🔐 Network Security

### Firewall Configuration

```yaml
---
- name: Configure firewall
  hosts: webservers
  become: yes
  
  tasks:
    - name: Install firewalld
      package:
        name: firewalld
        state: present
    
    - name: Start firewalld
      service:
        name: firewalld
        state: started
        enabled: yes
    
    - name: Allow HTTP
      firewalld:
        service: http
        permanent: yes
        state: enabled
    
    - name: Allow HTTPS
      firewalld:
        service: https
        permanent: yes
        state: enabled
    
    - name: Limit SSH to management network
      firewalld:
        port: 22/tcp
        permanent: yes
        state: enabled
        source: 10.0.0.0/8
    
    - name: Reload firewall
      command: firewall-cmd --reload
```

### SELinux/AppArmor

```yaml
- name: Enable SELinux
  selinux:
    policy: targeted
    state: enforcing

- name: Set SELinux context
  sefcontext:
    target: '/opt/app(/.*)?'
    setype: httpd_sys_content_t
    state: present

- name: Apply context
  command: restorecon -Rv /opt/app
```

---

## 📚 Complete Security Example

```yaml
---
- name: Secure production deployment
  hosts: production
  become: yes
  
  vars_files:
    - vault/production.yml
  
  pre_tasks:
    - name: Verify execution environment
      assert:
        that:
          - ansible_user != 'root'
          - environment == 'production'
          - deploy_approved | default(false) | bool
        fail_msg: "Security requirements not met"
    
    - name: Log deployment start
      lineinfile:
        path: /var/log/ansible_deployments.log
        line: "{{ ansible_date_time.iso8601 }} - {{ ansible_user_id }} - START - {{ ansible_playbook }}"
        create: yes
      delegate_to: localhost
  
  tasks:
    # Security hardening
    - name: Apply security baseline
      include_role:
        name: security_baseline
      tags: [security]
    
    # Validate before deployment
    - name: Check application signature
      stat:
        path: "{{ app_package }}"
        checksum_algorithm: sha256
      register: app_stat
    
    - name: Verify checksum
      assert:
        that:
          - app_stat.stat.checksum == expected_checksum
        fail_msg: "Package checksum mismatch"
    
    # Secure deployment
    - name: Create app user
      user:
        name: "{{ app_user }}"
        system: yes
        shell: /usr/sbin/nologin
        home: /opt/app
        create_home: no
    
    - name: Deploy application
      unarchive:
        src: "{{ app_package }}"
        dest: /opt/app
        owner: "{{ app_user }}"
        group: "{{ app_group }}"
        mode: '0750'
      no_log: yes
    
    - name: Deploy encrypted config
      template:
        src: app.conf.j2
        dest: /opt/app/config/app.conf
        owner: "{{ app_user }}"
        group: "{{ app_group }}"
        mode: '0600'
      no_log: yes
    
    - name: Set SELinux context
      sefcontext:
        target: '/opt/app(/.*)?'
        setype: bin_t
      when: ansible_selinux.status == "enabled"
    
    # Network security
    - name: Configure firewall
      firewalld:
        port: "{{ app_port }}/tcp"
        permanent: yes
        state: enabled
        source: "{{ allowed_networks }}"
    
    # Start service securely
    - name: Start application
      systemd:
        name: "{{ app_service }}"
        state: started
        enabled: yes
  
  post_tasks:
    - name: Verify deployment
      uri:
        url: "https://{{ inventory_hostname }}/health"
        validate_certs: yes
        status_code: 200
      retries: 5
      delay: 10
    
    - name: Log successful deployment
      lineinfile:
        path: /var/log/ansible_deployments.log
        line: "{{ ansible_date_time.iso8601 }} - {{ ansible_user_id }} - SUCCESS - {{ ansible_playbook }}"
      delegate_to: localhost
  
  handlers:
    - name: reload firewall
      command: firewall-cmd --reload
```

---

## ✅ Security Checklist

### Access Control
- [ ] Use SSH keys, not passwords
- [ ] Implement bastion hosts
- [ ] Restrict sudo access
- [ ] Rotate credentials regularly
- [ ] Use different keys per environment

### Secrets Management
- [ ] Encrypt with Ansible Vault
- [ ] Use external secret managers
- [ ] Enable no_log for sensitive tasks
- [ ] Don't commit secrets to git
- [ ] Rotate secrets regularly

### Logging & Monitoring
- [ ] Enable audit logging
- [ ] Log all playbook executions
- [ ] Monitor for suspicious activity
- [ ] Centralize logs
- [ ] Set up alerts

### Network Security
- [ ] Configure firewalls
- [ ] Use encrypted connections
- [ ] Limit network access
- [ ] Enable SELinux/AppArmor
- [ ] Regular security scans

### Compliance
- [ ] Implement CIS benchmarks
- [ ] Apply STIG controls
- [ ] Document security controls
- [ ] Regular compliance audits
- [ ] Automated compliance checks

### Code Security
- [ ] Use ansible-lint
- [ ] Validate inputs
- [ ] Avoid command injection
- [ ] Review code changes
- [ ] Security testing in CI/CD

---

## 🔗 What's Next?

- **Next:** [Enterprise Patterns](20-enterprise-patterns.md)
- **Previous:** [Performance](17-performance.md)
- **Related:** [Ansible Vault](../intermediate/11-ansible-vault.md)

---

**Pro Tip:** Security is not a feature, it's a requirement. Build it into every playbook from the start!
