# Handlers & Conditionals

> **Master event-driven automation and conditional task execution**

---

## 📖 What You'll Learn

- Handlers for event-driven tasks
- Conditional execution with `when`
- Advanced conditional logic
- Handler best practices
- Real-world patterns

---

## 🔔 Handlers

### What Are Handlers?

Handlers are tasks that only run when notified by other tasks. They run at the end of a play after all tasks complete.

**Common uses:**
- Restarting services after config changes
- Reloading configurations
- Running cleanup tasks
- Triggering dependent actions

### Basic Handler

```yaml
---
- name: Configure web server
  hosts: webservers
  become: yes
  
  tasks:
    - name: Update Apache configuration
      copy:
        src: apache.conf
        dest: /etc/apache2/apache2.conf
      notify: restart apache
  
  handlers:
    - name: restart apache
      service:
        name: apache2
        state: restarted
```

### Multiple Notifications

```yaml
tasks:
  - name: Update config file 1
    copy:
      src: config1.conf
      dest: /etc/app/config1.conf
    notify: restart app
  
  - name: Update config file 2
    copy:
      src: config2.conf
      dest: /etc/app/config2.conf
    notify: restart app

handlers:
  - name: restart app
    service:
      name: myapp
      state: restarted
```

**Note:** Handler runs only once even if notified multiple times.

---

## 🎯 Handler Patterns

### Listen Directive

```yaml
tasks:
  - name: Update nginx config
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: reload web server
  
  - name: Update apache config
    template:
      src: apache.conf.j2
      dest: /etc/apache2/apache2.conf
    notify: reload web server

handlers:
  - name: reload nginx
    service:
      name: nginx
      state: reloaded
    listen: reload web server
  
  - name: reload apache
    service:
      name: apache2
      state: reloaded
    listen: reload web server
```

### Handler Chains

```yaml
tasks:
  - name: Update application
    copy:
      src: app.jar
      dest: /opt/app/app.jar
    notify: restart app

handlers:
  - name: restart app
    service:
      name: myapp
      state: restarted
    notify: verify app
  
  - name: verify app
    uri:
      url: http://localhost:8080/health
      status_code: 200
```

### Flush Handlers

```yaml
tasks:
  - name: Update config
    copy:
      src: config.conf
      dest: /etc/app/config.conf
    notify: restart app
  
  - name: Force handler execution now
    meta: flush_handlers
  
  - name: Run after service restarted
    wait_for:
      port: 8080
      delay: 5
```

---

## ✅ Conditionals: When Clause

### Basic Conditionals

```yaml
tasks:
  - name: Install on Debian systems only
    apt:
      name: nginx
      state: present
    when: ansible_os_family == "Debian"
  
  - name: Install on RedHat systems only
    yum:
      name: httpd
      state: present
    when: ansible_os_family == "RedHat"
```

### Multiple Conditions (AND)

```yaml
tasks:
  - name: Install package
    apt:
      name: special-package
      state: present
    when:
      - ansible_distribution == "Ubuntu"
      - ansible_distribution_version == "20.04"
      - environment == "production"
```

### OR Conditions

```yaml
tasks:
  - name: Install on Debian or Ubuntu
    apt:
      name: package
      state: present
    when: ansible_distribution == "Debian" or ansible_distribution == "Ubuntu"
  
  # Alternative syntax
  - name: Install on specific versions
    apt:
      name: package
      state: present
    when: ansible_distribution_version in ["18.04", "20.04", "22.04"]
```

### Complex Conditions

```yaml
tasks:
  - name: Complex condition
    debug:
      msg: "Condition met"
    when: >
      (ansible_distribution == "Ubuntu" and ansible_distribution_version >= "20.04")
      or
      (ansible_distribution == "Debian" and ansible_distribution_version >= "11")
```

---

## 🔍 Conditional Types

### Based on Variables

```yaml
tasks:
  - name: Deploy to production
    command: /opt/deploy-prod.sh
    when: environment == "production"
  
  - name: Enable debug mode
    lineinfile:
      path: /etc/app/config
      line: "DEBUG=true"
    when: debug_mode | default(false) | bool
  
  - name: Check variable is defined
    debug:
      msg: "Variable is set"
    when: my_variable is defined
```

### Based on Facts

```yaml
tasks:
  - name: Configure based on memory
    lineinfile:
      path: /etc/app/config
      line: "MAX_MEMORY={{ (ansible_memtotal_mb * 0.8) | int }}MB"
    when: ansible_memtotal_mb > 4000
  
  - name: Install on systems with SSD
    package:
      name: performance-tools
      state: present
    when: "'ssd' in ansible_devices.sda.model | lower"
```

### Based on Registered Variables

```yaml
tasks:
  - name: Check if file exists
    stat:
      path: /etc/app/config
    register: config_file
  
  - name: Create config if missing
    copy:
      src: default.conf
      dest: /etc/app/config
    when: not config_file.stat.exists
  
  - name: Run command
    command: /opt/script.sh
    register: script_result
    ignore_errors: yes
  
  - name: Handle failure
    debug:
      msg: "Script failed"
    when: script_result.failed
```

---

## 🔄 Conditionals with Loops

```yaml
tasks:
  - name: Install packages selectively
    apt:
      name: "{{ item.name }}"
      state: present
    loop:
      - { name: "nginx", install: true }
      - { name: "apache2", install: false }
      - { name: "mysql", install: true }
    when: item.install | bool
  
  - name: Create users in production only
    user:
      name: "{{ item }}"
      state: present
    loop:
      - user1
      - user2
      - user3
    when: environment == "production"
```

---

## 🎨 Advanced Patterns

### Conditional Blocks

```yaml
tasks:
  - name: Production setup
    block:
      - name: Install production packages
        apt:
          name: "{{ production_packages }}"
          state: present
      
      - name: Configure production settings
        template:
          src: prod.conf.j2
          dest: /etc/app/config
      
      - name: Enable monitoring
        service:
          name: monitoring-agent
          state: started
          enabled: yes
    when: environment == "production"
```

### Conditional Imports

```yaml
tasks:
  - name: Include Debian tasks
    include_tasks: debian.yml
    when: ansible_os_family == "Debian"
  
  - name: Include RedHat tasks
    include_tasks: redhat.yml
    when: ansible_os_family == "RedHat"
```

### Failed When

```yaml
tasks:
  - name: Run script
    command: /opt/check_status.sh
    register: result
    failed_when:
      - result.rc != 0
      - "'WARNING' not in result.stderr"
  
  - name: Check service
    command: systemctl is-active myapp
    register: service_status
    failed_when: false  # Never fail
    changed_when: false  # Never report changed
```

### Changed When

```yaml
tasks:
  - name: Check configuration
    command: /opt/verify_config.sh
    register: verify_result
    changed_when: "'UPDATED' in verify_result.stdout"
  
  - name: Idempotent command
    command: /opt/setup.sh
    register: setup_result
    changed_when: setup_result.stdout != ""
```

---

## 📋 Complete Examples

### Web Server Configuration

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: yes
  
  vars:
    web_server: "{{ 'apache2' if ansible_os_family == 'Debian' else 'httpd' }}"
    config_path: "{{ '/etc/apache2' if ansible_os_family == 'Debian' else '/etc/httpd' }}"
  
  tasks:
    - name: Install web server
      package:
        name: "{{ web_server }}"
        state: present
      notify: start web server
    
    - name: Deploy main configuration
      template:
        src: "{{ ansible_os_family | lower }}_web.conf.j2"
        dest: "{{ config_path }}/{{ web_server }}.conf"
      notify: reload web server
    
    - name: Deploy SSL configuration
      template:
        src: ssl.conf.j2
        dest: "{{ config_path }}/ssl.conf"
      when: ssl_enabled | default(false) | bool
      notify: reload web server
    
    - name: Enable site in production
      file:
        src: "{{ config_path }}/sites-available/{{ site_name }}"
        dest: "{{ config_path }}/sites-enabled/{{ site_name }}"
        state: link
      when:
        - environment == "production"
        - ansible_os_family == "Debian"
      notify: reload web server
  
  handlers:
    - name: start web server
      service:
        name: "{{ web_server }}"
        state: started
        enabled: yes
    
    - name: reload web server
      service:
        name: "{{ web_server }}"
        state: reloaded
```

### Database Setup with Conditionals

```yaml
---
- name: Setup database
  hosts: databases
  become: yes
  
  tasks:
    - name: Check if database exists
      command: psql -lqt
      become_user: postgres
      register: db_list
      changed_when: false
      failed_when: false
    
    - name: Create database
      postgresql_db:
        name: "{{ db_name }}"
        state: present
      become_user: postgres
      when: db_name not in db_list.stdout
      notify: initialize database
    
    - name: Check database version
      postgresql_query:
        db: "{{ db_name }}"
        query: "SELECT version FROM schema_version LIMIT 1"
      become_user: postgres
      register: db_version
      when: db_name in db_list.stdout
      failed_when: false
    
    - name: Run migrations
      command: "/opt/app/migrate.sh"
      when:
        - db_version.rowcount is defined
        - db_version.rowcount > 0
        - db_version.query_result[0].version < target_version
      notify: restart application
  
  handlers:
    - name: initialize database
      command: "/opt/app/init_db.sh"
      become_user: postgres
    
    - name: restart application
      service:
        name: myapp
        state: restarted
```

### Rolling Update Pattern

```yaml
---
- name: Rolling update
  hosts: webservers
  serial: 1
  
  tasks:
    - name: Remove from load balancer
      haproxy:
        state: disabled
        host: "{{ inventory_hostname }}"
        backend: web_backend
      delegate_to: "{{ groups['loadbalancers'][0] }}"
      notify: add to load balancer
    
    - name: Wait for connections to drain
      wait_for:
        timeout: 30
    
    - name: Update application
      copy:
        src: "app-{{ app_version }}.jar"
        dest: /opt/app/app.jar
      notify: restart app
    
    - name: Flush handlers to restart now
      meta: flush_handlers
    
    - name: Wait for application startup
      wait_for:
        port: 8080
        delay: 10
        timeout: 60
    
    - name: Verify application health
      uri:
        url: "http://{{ inventory_hostname }}:8080/health"
        status_code: 200
      retries: 5
      delay: 5
  
  handlers:
    - name: restart app
      service:
        name: myapp
        state: restarted
    
    - name: add to load balancer
      haproxy:
        state: enabled
        host: "{{ inventory_hostname }}"
        backend: web_backend
      delegate_to: "{{ groups['loadbalancers'][0] }}"
```

---

## ✅ Best Practices

1. **Keep handlers simple:** One action per handler
2. **Use listen for groups:** Group related handlers
3. **Name handlers clearly:** Describe the action
4. **Test conditionals:** Verify logic with --check
5. **Use flush_handlers wisely:** Only when necessary
6. **Document complex conditions:** Add comments
7. **Prefer failed_when:** Over ignore_errors
8. **Chain handlers carefully:** Avoid long chains

---

## ❌ Common Pitfalls

### Handler Not Running

```yaml
# Bad - handler name mismatch
tasks:
  - name: Update config
    copy:
      src: config.conf
      dest: /etc/app/config.conf
    notify: restart_app  # Wrong name!

handlers:
  - name: restart app   # Correct name
    service:
      name: app
      state: restarted

# Good - exact match
tasks:
  - name: Update config
    copy:
      src: config.conf
      dest: /etc/app/config.conf
    notify: restart app

handlers:
  - name: restart app
    service:
      name: app
      state: restarted
```

### Conditional Syntax Errors

```yaml
# Bad - incorrect comparison
when: ansible_os_family = "Debian"  # Single =

# Good - correct comparison
when: ansible_os_family == "Debian"

# Bad - wrong boolean conversion
when: ssl_enabled == "true"  # String comparison

# Good - proper boolean check
when: ssl_enabled | bool
```

---

## 🔗 What's Next?

- **Next:** [Loops & Iteration](10-loops.md)
- **Previous:** [Templates](08-templates.md)
- **Related:** [Error Handling](12-error-handling.md)

---

**Pro Tip:** Use `--step` flag to execute playbook one task at a time for debugging handlers!
