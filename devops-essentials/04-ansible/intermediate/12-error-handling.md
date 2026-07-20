# Error Handling & Testing

> **Build reliable automation with proper error handling and testing strategies**

---

## 📖 What You'll Learn

- Error handling strategies
- Failed_when and changed_when
- Blocks with rescue and always
- Testing playbooks
- Validation techniques
- Debugging methods

---

## ⚠️ Error Handling Basics

### Default Behavior

```yaml
tasks:
  - name: This will fail
    command: /bin/false
    # Playbook stops here
  
  - name: This won't run
    debug:
      msg: "Never reached"
```

### Ignore Errors

```yaml
tasks:
  - name: Try to stop service
    service:
      name: myapp
      state: stopped
    ignore_errors: yes
  
  - name: This runs regardless
    debug:
      msg: "Continues even if service stop failed"
```

---

## 🎯 Failed_when

### Custom Failure Conditions

```yaml
tasks:
  - name: Check disk space
    command: df -h /
    register: disk_space
    failed_when: "'100%' in disk_space.stdout"
  
  - name: Run script with specific failure
    command: /opt/script.sh
    register: result
    failed_when:
      - result.rc != 0
      - result.rc != 2  # 2 is acceptable
  
  - name: Check service
    command: systemctl status myapp
    register: service_status
    failed_when:
      - service_status.rc != 0
      - "'inactive' not in service_status.stdout"
```

### Never Fail

```yaml
tasks:
  - name: Check if file exists
    command: test -f /etc/myapp/config
    register: file_check
    failed_when: false  # Never fail
    changed_when: false  # Never report changed
  
  - name: Create file if missing
    copy:
      dest: /etc/myapp/config
      content: "default config"
    when: file_check.rc != 0
```

---

## 🔄 Changed_when

### Control Change Status

```yaml
tasks:
  - name: Check configuration
    command: /opt/check_config.sh
    register: config_check
    changed_when: "'UPDATED' in config_check.stdout"
  
  - name: Never report changed
    command: uptime
    changed_when: false
  
  - name: Always report changed
    command: /opt/alert.sh
    changed_when: true
```

### Complex Change Logic

```yaml
tasks:
  - name: Update application
    command: /opt/update.sh
    register: update_result
    changed_when:
      - update_result.rc == 0
      - "'No updates' not in update_result.stdout"
      - update_result.stdout_lines | length > 0
```

---

## 🛡️ Blocks for Error Handling

### Block, Rescue, Always

```yaml
tasks:
  - name: Attempt risky operation
    block:
      - name: Stop service
        service:
          name: myapp
          state: stopped
      
      - name: Update application
        copy:
          src: newapp.jar
          dest: /opt/app/app.jar
      
      - name: Start service
        service:
          name: myapp
          state: started
    
    rescue:
      - name: Rollback on failure
        copy:
          src: oldapp.jar
          dest: /opt/app/app.jar
      
      - name: Restart service
        service:
          name: myapp
          state: started
      
      - name: Send alert
        debug:
          msg: "Deployment failed, rolled back"
    
    always:
      - name: Log deployment attempt
        lineinfile:
          path: /var/log/deployments.log
          line: "{{ ansible_date_time.iso8601 }} - Deployment attempted"
      
      - name: Cleanup temp files
        file:
          path: /tmp/deployment
          state: absent
```

### Nested Blocks

```yaml
tasks:
  - name: Primary operation
    block:
      - name: Try primary method
        command: /primary/method.sh
    
    rescue:
      - name: Try fallback
        block:
          - name: Use fallback method
            command: /fallback/method.sh
        
        rescue:
          - name: Last resort
            command: /emergency/method.sh
          
          - fail:
              msg: "All methods failed"
```

---

## ✅ Assertions

### Validating Conditions

```yaml
tasks:
  - name: Check required variables
    assert:
      that:
        - app_name is defined
        - app_version is defined
        - app_environment in ['dev', 'staging', 'prod']
      fail_msg: "Required variables missing or invalid"
      success_msg: "All required variables present"
  
  - name: Validate system requirements
    assert:
      that:
        - ansible_memtotal_mb >= 4096
        - ansible_processor_cores >= 2
        - ansible_distribution in ['Ubuntu', 'Debian']
      fail_msg: "System requirements not met"
```

### Complex Assertions

```yaml
tasks:
  - name: Check service status
    command: systemctl is-active {{ item }}
    register: services
    loop:
      - nginx
      - mysql
      - redis
    changed_when: false
    failed_when: false
  
  - name: Assert all services running
    assert:
      that:
        - item.rc == 0
      fail_msg: "Service {{ item.item }} is not running"
    loop: "{{ services.results }}"
```

---

## 🔍 Testing Playbooks

### Syntax Check

```bash
# Check syntax
ansible-playbook site.yml --syntax-check

# Multiple playbooks
ansible-playbook *.yml --syntax-check
```

### Check Mode (Dry Run)

```yaml
# playbook.yml
---
- name: Deploy application
  hosts: webservers
  
  tasks:
    - name: Update package cache
      apt:
        update_cache: yes
      check_mode: no  # Always run, even in check mode
    
    - name: Install package
      apt:
        name: nginx
        state: present
      # Will simulate in check mode
    
    - name: Dangerous operation
      command: rm -rf /tmp/old
      check_mode: yes  # Never actually run
      when: not ansible_check_mode
```

```bash
# Run in check mode
ansible-playbook site.yml --check

# With diff
ansible-playbook site.yml --check --diff
```

### Diff Mode

```yaml
tasks:
  - name: Update config
    template:
      src: app.conf.j2
      dest: /etc/app/app.conf
    diff: yes  # Show changes
```

```bash
ansible-playbook site.yml --diff
```

---

## 🧪 Testing Strategies

### Unit Testing with Molecule

```bash
# Install Molecule
pip install molecule molecule-docker

# Initialize
cd roles/myrole
molecule init scenario

# Test
molecule test
```

**molecule.yml:**
```yaml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: instance
    image: ubuntu:20.04
    pre_build_image: true
provisioner:
  name: ansible
verifier:
  name: ansible
```

**verify.yml:**
```yaml
---
- name: Verify
  hosts: all
  tasks:
    - name: Check nginx is installed
      command: nginx -v
      register: nginx_version
      failed_when: nginx_version.rc != 0
    
    - name: Check nginx is running
      service_facts:
      failed_when: "'nginx.service' not in services"
```

### Integration Testing

```yaml
---
- name: Integration test
  hosts: test-servers
  tasks:
    - name: Deploy application
      include_role:
        name: myapp
    
    - name: Wait for service
      wait_for:
        port: 8080
        timeout: 30
    
    - name: Test health endpoint
      uri:
        url: http://localhost:8080/health
        status_code: 200
        return_content: yes
      register: health_check
    
    - name: Validate response
      assert:
        that:
          - health_check.json.status == "healthy"
          - health_check.json.version == app_version
```

### Smoke Tests

```yaml
---
- name: Post-deployment smoke tests
  hosts: newly_deployed
  
  tasks:
    - name: Test web server response
      uri:
        url: "http://{{ inventory_hostname }}"
        status_code: 200
        timeout: 10
      retries: 3
      delay: 5
    
    - name: Test database connection
      command: >
        psql -h {{ db_host }} -U {{ db_user }} -d {{ db_name }} -c "SELECT 1"
      environment:
        PGPASSWORD: "{{ db_password }}"
      register: db_test
      failed_when: "'1 row' not in db_test.stdout"
      no_log: yes
    
    - name: Test API endpoint
      uri:
        url: "http://{{ inventory_hostname }}/api/status"
        return_content: yes
      register: api_status
      failed_when: api_status.json.status != "ok"
```

---

## 🐛 Debugging

### Debug Module

```yaml
tasks:
  - name: Show variable
    debug:
      var: my_variable
  
  - name: Show message
    debug:
      msg: "Value is {{ my_variable }}"
  
  - name: Show all variables
    debug:
      var: hostvars[inventory_hostname]
  
  - name: Conditional debug
    debug:
      msg: "This is production!"
    when: environment == "production"
  
  - name: Debug with verbosity
    debug:
      msg: "Only with -v flag"
      verbosity: 1
```

### Debugging Failed Tasks

```bash
# Run with verbose output
ansible-playbook site.yml -v
ansible-playbook site.yml -vv
ansible-playbook site.yml -vvv  # SSH level
ansible-playbook site.yml -vvvv # Connection debug

# Start at specific task
ansible-playbook site.yml --start-at-task="Install package"

# Step through tasks
ansible-playbook site.yml --step
```

### Register and Debug

```yaml
tasks:
  - name: Run command
    command: /opt/script.sh
    register: script_output
  
  - name: Show output
    debug:
      var: script_output
  
  - name: Show specific fields
    debug:
      msg: |
        Return code: {{ script_output.rc }}
        Stdout: {{ script_output.stdout }}
        Stderr: {{ script_output.stderr }}
```

---

## 📚 Complete Error Handling Example

```yaml
---
- name: Production deployment with comprehensive error handling
  hosts: webservers
  serial: 1  # Rolling deployment
  any_errors_fatal: no
  max_fail_percentage: 25
  
  vars:
    deployment_log: /var/log/deployments.log
    max_retries: 3
  
  pre_tasks:
    - name: Validate prerequisites
      block:
        - name: Check required variables
          assert:
            that:
              - app_version is defined
              - app_environment is defined
              - app_environment in ['staging', 'production']
            fail_msg: "Missing or invalid variables"
        
        - name: Check system resources
          assert:
            that:
              - ansible_memfree_mb > 1000
              - ansible_mounts | selectattr('mount', 'equalto', '/') | map(attribute='size_available') | first > 5000000000
            fail_msg: "Insufficient system resources"
        
        - name: Verify existing installation
          stat:
            path: /opt/app/current
          register: current_install
          failed_when: not current_install.stat.exists
      
      rescue:
        - name: Log validation failure
          lineinfile:
            path: "{{ deployment_log }}"
            line: "{{ ansible_date_time.iso8601 }} - Validation failed on {{ inventory_hostname }}"
          delegate_to: localhost
        
        - fail:
            msg: "Pre-deployment validation failed"
  
  tasks:
    - name: Deploy application
      block:
        # Remove from load balancer
        - name: Disable in load balancer
          haproxy:
            state: disabled
            host: "{{ inventory_hostname }}"
            backend: web_backend
          delegate_to: "{{ groups['loadbalancers'][0] }}"
          register: lb_disable
          retries: "{{ max_retries }}"
          delay: 5
          until: lb_disable is success
        
        # Backup current version
        - name: Backup current application
          archive:
            path: /opt/app/current
            dest: "/opt/app/backups/backup-{{ ansible_date_time.epoch }}.tar.gz"
          register: backup
        
        # Deploy new version
        - name: Deploy new application version
          copy:
            src: "app-{{ app_version }}.jar"
            dest: /opt/app/app.jar
          register: deploy
        
        # Restart service
        - name: Restart application
          service:
            name: myapp
            state: restarted
          register: restart
        
        # Health check
        - name: Wait for application startup
          wait_for:
            port: 8080
            timeout: 60
          register: startup
        
        - name: Health check
          uri:
            url: "http://{{ inventory_hostname }}:8080/health"
            status_code: 200
            return_content: yes
          register: health
          retries: 5
          delay: 10
          until: health.status == 200
        
        # Enable in load balancer
        - name: Enable in load balancer
          haproxy:
            state: enabled
            host: "{{ inventory_hostname }}"
            backend: web_backend
          delegate_to: "{{ groups['loadbalancers'][0] }}"
      
      rescue:
        - name: Deployment failed, initiating rollback
          debug:
            msg: "Deployment failed at {{ inventory_hostname }}, rolling back"
        
        - name: Stop failed application
          service:
            name: myapp
            state: stopped
          ignore_errors: yes
        
        - name: Restore from backup
          unarchive:
            src: "{{ backup.dest }}"
            dest: /opt/app/
            remote_src: yes
          when: backup is defined and backup.dest is defined
        
        - name: Restart application
          service:
            name: myapp
            state: started
          retries: 3
          delay: 5
        
        - name: Verify rollback
          uri:
            url: "http://{{ inventory_hostname }}:8080/health"
            status_code: 200
          retries: 5
          delay: 5
        
        - name: Enable in load balancer
          haproxy:
            state: enabled
            host: "{{ inventory_hostname }}"
            backend: web_backend
          delegate_to: "{{ groups['loadbalancers'][0] }}"
          ignore_errors: yes
        
        - name: Send alert
          mail:
            to: ops@example.com
            subject: "Deployment Failed on {{ inventory_hostname }}"
            body: "Deployment of version {{ app_version }} failed. System rolled back."
          delegate_to: localhost
        
        - fail:
            msg: "Deployment failed and rolled back"
      
      always:
        - name: Log deployment attempt
          lineinfile:
            path: "{{ deployment_log }}"
            line: "{{ ansible_date_time.iso8601 }} - {{ inventory_hostname }} - {{ app_version }} - {{ 'SUCCESS' if health is defined and health.status == 200 else 'FAILED' }}"
            create: yes
          delegate_to: localhost
        
        - name: Cleanup temp files
          file:
            path: /tmp/deployment
            state: absent
          ignore_errors: yes
```

---

## ✅ Best Practices

1. **Use blocks** - Group related tasks with error handling
2. **Assert early** - Validate before starting
3. **Failed_when** - Define explicit failure conditions
4. **Changed_when** - Control change reporting
5. **Use no_log** - Hide sensitive data
6. **Register results** - Capture for debugging
7. **Retry important tasks** - Use retries and until
8. **Test thoroughly** - Check mode, molecule, integration tests
9. **Log operations** - Track what happened
10. **Plan rollback** - Always have a recovery path

---

## 🔗 What's Next?

- **Next:** [Ansible Roles](../advanced/13-roles.md)
- **Previous:** [Ansible Vault](11-ansible-vault.md)
- **Review:** [Intermediate Interview Questions](interview-questions-intermediate.md)

---

**🎉 Congratulations!** You've completed the Intermediate Ansible track. You now have solid playbook skills and error handling capabilities. Ready for advanced topics!
