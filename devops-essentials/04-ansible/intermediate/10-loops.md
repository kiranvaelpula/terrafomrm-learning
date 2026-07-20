# Loops & Iteration

> **Automate repetitive tasks efficiently with Ansible loops**

---

## 📖 What You'll Learn

- Loop fundamentals with `loop`
- Legacy loop directives
- Loop control options
- Complex iteration patterns
- Performance optimization
- Real-world examples

---

## 🔄 Basic Loops

### Simple Loop

```yaml
---
- name: Loop basics
  hosts: localhost
  tasks:
    - name: Install multiple packages
      apt:
        name: "{{ item }}"
        state: present
      loop:
        - nginx
        - git
        - vim
        - curl
```

### Loop with Variables

```yaml
vars:
  packages:
    - nginx
    - postgresql
    - redis

tasks:
  - name: Install packages from variable
    apt:
      name: "{{ item }}"
      state: present
    loop: "{{ packages }}"
```

---

## 📊 Loop Types

### 1. Simple List Loop

```yaml
tasks:
  - name: Create multiple directories
    file:
      path: "/opt/{{ item }}"
      state: directory
      mode: '0755'
    loop:
      - app1
      - app2
      - app3
```

### 2. Dictionary Loop

```yaml
tasks:
  - name: Create users
    user:
      name: "{{ item.name }}"
      comment: "{{ item.comment }}"
      state: present
    loop:
      - { name: 'john', comment: 'John Doe' }
      - { name: 'jane', comment: 'Jane Smith' }
      - { name: 'bob', comment: 'Bob Johnson' }
```

### 3. Nested Variables

```yaml
vars:
  users:
    - name: john
      groups: ['wheel', 'docker']
      shell: /bin/bash
    - name: jane
      groups: ['developers']
      shell: /bin/zsh

tasks:
  - name: Create users with attributes
    user:
      name: "{{ item.name }}"
      groups: "{{ item.groups | join(',') }}"
      shell: "{{ item.shell }}"
      state: present
    loop: "{{ users }}"
```

---

## 🎯 Loop Control

### Index Access

```yaml
tasks:
  - name: Create numbered directories
    file:
      path: "/opt/dir{{ item.0 + 1 }}"
      state: directory
    loop: "{{ range(0, 5) | list }}"
  
  - name: Show loop index
    debug:
      msg: "Item {{ ansible_loop.index }}: {{ item }}"
    loop:
      - apple
      - banana
      - cherry
```

### Loop Variables

```yaml
tasks:
  - name: Using loop variables
    debug:
      msg: |
        Index: {{ ansible_loop.index }}
        Index0: {{ ansible_loop.index0 }}
        First: {{ ansible_loop.first }}
        Last: {{ ansible_loop.last }}
        Length: {{ ansible_loop.length }}
        Remaining: {{ ansible_loop.revindex }}
    loop: "{{ items }}"
```

### Loop Control Options

```yaml
tasks:
  - name: Loop with label
    user:
      name: "{{ item.name }}"
      state: present
    loop:
      - { name: 'user1', uid: 1001 }
      - { name: 'user2', uid: 1002 }
    loop_control:
      label: "{{ item.name }}"  # Only show name in output
  
  - name: Loop with pause
    command: /opt/script.sh {{ item }}
    loop: "{{ servers }}"
    loop_control:
      pause: 5  # 5 second pause between iterations
  
  - name: Loop with custom variable name
    debug:
      msg: "Processing {{ server.name }}"
    loop: "{{ servers }}"
    loop_control:
      loop_var: server  # Use 'server' instead of 'item'
```

---

## 🔧 Advanced Loop Patterns

### Loop Over Dictionary

```yaml
vars:
  databases:
    prod:
      host: db.prod.com
      port: 5432
    staging:
      host: db.staging.com
      port: 5432

tasks:
  - name: Configure database connections
    lineinfile:
      path: /etc/app/databases.conf
      line: "{{ item.key }}={{ item.value.host }}:{{ item.value.port }}"
    loop: "{{ databases | dict2items }}"
```

### Nested Loops

```yaml
tasks:
  - name: Create directory structure
    file:
      path: "/opt/{{ item.0 }}/{{ item.1 }}"
      state: directory
    loop: "{{ apps | product(environments) | list }}"
    vars:
      apps:
        - webapp
        - api
      environments:
        - dev
        - staging
        - prod
```

### Cartesian Product

```yaml
tasks:
  - name: Grant permissions
    command: >
      setfacl -m u:{{ item.0 }}:{{ item.1 }} /shared/{{ item.2 }}
    loop: "{{ users | product(permissions, directories) | list }}"
    vars:
      users: ['john', 'jane']
      permissions: ['r', 'rw']
      directories: ['docs', 'data']
```

### Flattening Lists

```yaml
vars:
  package_groups:
    - ['nginx', 'apache2']
    - ['mysql', 'postgresql']
    - ['git', 'vim']

tasks:
  - name: Install all packages
    apt:
      name: "{{ item }}"
      state: present
    loop: "{{ package_groups | flatten }}"
```

---

## 📝 Loop Filters

### With subelements

```yaml
vars:
  users:
    - name: john
      authorized:
        - ssh-rsa AAAAB3...
        - ssh-rsa AAAAB4...
    - name: jane
      authorized:
        - ssh-rsa AAAAB5...

tasks:
  - name: Add SSH keys
    authorized_key:
      user: "{{ item.0.name }}"
      key: "{{ item.1 }}"
    loop: "{{ users | subelements('authorized') }}"
```

### With sequence

```yaml
tasks:
  - name: Create numbered files
    file:
      path: "/tmp/file{{ item }}.txt"
      state: touch
    loop: "{{ range(1, 11) | list }}"  # 1 to 10
  
  - name: Create with step
    debug:
      msg: "Number: {{ item }}"
    loop: "{{ range(0, 100, 10) | list }}"  # 0, 10, 20, ..., 90
```

### With fileglob

```yaml
tasks:
  - name: Process all config files
    template:
      src: "{{ item }}"
      dest: "/etc/app/{{ item | basename }}"
    loop: "{{ lookup('fileglob', 'configs/*.conf', wantlist=True) }}"
```

### With inventory

```yaml
tasks:
  - name: Configure all web servers
    debug:
      msg: "{{ item }}: {{ hostvars[item]['ansible_default_ipv4']['address'] }}"
    loop: "{{ groups['webservers'] }}"
```

---

## 🎨 Conditional Loops

### When with Loop

```yaml
tasks:
  - name: Install packages conditionally
    apt:
      name: "{{ item.name }}"
      state: present
    loop:
      - { name: 'nginx', install: true }
      - { name: 'apache2', install: false }
      - { name: 'mysql', install: true }
    when: item.install | bool
```

### Loop Until

```yaml
tasks:
  - name: Wait for service to be ready
    uri:
      url: "http://{{ item }}/health"
      status_code: 200
    register: result
    until: result.status == 200
    retries: 10
    delay: 5
    loop: "{{ groups['webservers'] }}"
```

### Failed When in Loop

```yaml
tasks:
  - name: Check services
    command: systemctl is-active {{ item }}
    register: service_status
    loop:
      - nginx
      - mysql
      - redis
    failed_when:
      - service_status.rc != 0
      - "'inactive' in service_status.stderr"
```

---

## 🚀 Performance Optimization

### Async with Loop

```yaml
tasks:
  - name: Run tasks in parallel
    command: /opt/long_script.sh {{ item }}
    async: 300
    poll: 0
    loop: "{{ servers }}"
    register: async_results
  
  - name: Wait for completion
    async_status:
      jid: "{{ item.ansible_job_id }}"
    loop: "{{ async_results.results }}"
    register: async_status
    until: async_status.finished
    retries: 30
    delay: 10
```

### Batch Processing

```yaml
tasks:
  - name: Process in batches
    command: /opt/process.sh {{ item }}
    loop: "{{ large_list }}"
    loop_control:
      pause: 1
    throttle: 5  # Max 5 concurrent executions
```

---

## 📚 Complete Examples

### User Management

```yaml
---
- name: Comprehensive user management
  hosts: all
  become: yes
  
  vars:
    users:
      - name: john
        uid: 1001
        groups: ['wheel', 'docker']
        ssh_keys:
          - "ssh-rsa AAAAB3NzaC1..."
          - "ssh-rsa AAAAB3NzaC2..."
      - name: jane
        uid: 1002
        groups: ['developers']
        ssh_keys:
          - "ssh-rsa AAAAB3NzaC3..."
      - name: bob
        uid: 1003
        groups: ['operators', 'docker']
        ssh_keys: []
  
  tasks:
    - name: Create users
      user:
        name: "{{ item.name }}"
        uid: "{{ item.uid }}"
        groups: "{{ item.groups | join(',') }}"
        state: present
      loop: "{{ users }}"
      loop_control:
        label: "{{ item.name }}"
    
    - name: Add SSH keys
      authorized_key:
        user: "{{ item.0.name }}"
        key: "{{ item.1 }}"
        state: present
      loop: "{{ users | subelements('ssh_keys', skip_missing=True) }}"
      loop_control:
        label: "{{ item.0.name }}"
    
    - name: Create home directories structure
      file:
        path: "/home/{{ item.0.name }}/{{ item.1 }}"
        state: directory
        owner: "{{ item.0.name }}"
        mode: '0755'
      loop: "{{ users | product(directories) | list }}"
      vars:
        directories: ['bin', 'projects', 'tmp']
      loop_control:
        label: "{{ item.0.name }}/{{ item.1 }}"
```

### Package Installation

```yaml
---
- name: Install packages across OS families
  hosts: all
  become: yes
  
  vars:
    common_packages:
      - vim
      - git
      - curl
      - wget
    
    os_specific_packages:
      Debian:
        - apache2
        - libapache2-mod-php
      RedHat:
        - httpd
        - php
  
  tasks:
    - name: Install common packages
      package:
        name: "{{ item }}"
        state: present
      loop: "{{ common_packages }}"
    
    - name: Install OS-specific packages
      package:
        name: "{{ item }}"
        state: present
      loop: "{{ os_specific_packages[ansible_os_family] }}"
      when: ansible_os_family in os_specific_packages
```

### Configuration Deployment

```yaml
---
- name: Deploy configurations to multiple environments
  hosts: localhost
  
  vars:
    environments:
      - name: dev
        servers: ['dev-web01', 'dev-web02']
        config:
          port: 8080
          debug: true
      - name: staging
        servers: ['stage-web01']
        config:
          port: 8080
          debug: false
      - name: prod
        servers: ['prod-web01', 'prod-web02', 'prod-web03']
        config:
          port: 80
          debug: false
  
  tasks:
    - name: Deploy configs to all environments
      template:
        src: app.conf.j2
        dest: "/tmp/{{ item.0.name }}-{{ item.1 }}.conf"
      loop: "{{ environments | subelements('servers') }}"
      vars:
        environment: "{{ item.0.name }}"
        server: "{{ item.1 }}"
        port: "{{ item.0.config.port }}"
        debug: "{{ item.0.config.debug }}"
      loop_control:
        label: "{{ item.0.name }}/{{ item.1 }}"
```

### Service Management

```yaml
---
- name: Manage services across hosts
  hosts: webservers
  become: yes
  
  vars:
    services:
      - name: nginx
        state: started
        enabled: yes
        ports: [80, 443]
      - name: mysql
        state: started
        enabled: yes
        ports: [3306]
      - name: redis
        state: started
        enabled: yes
        ports: [6379]
  
  tasks:
    - name: Ensure services are running
      service:
        name: "{{ item.name }}"
        state: "{{ item.state }}"
        enabled: "{{ item.enabled }}"
      loop: "{{ services }}"
      loop_control:
        label: "{{ item.name }}"
    
    - name: Wait for service ports
      wait_for:
        port: "{{ item.1 }}"
        delay: 2
        timeout: 30
      loop: "{{ services | subelements('ports') }}"
      loop_control:
        label: "{{ item.0.name }}:{{ item.1 }}"
    
    - name: Verify service status
      command: systemctl is-active {{ item.name }}
      register: service_check
      loop: "{{ services }}"
      changed_when: false
      failed_when: service_check.stdout != 'active'
      loop_control:
        label: "{{ item.name }}"
```

---

## 🔍 Register with Loops

### Capturing Loop Results

```yaml
tasks:
  - name: Check multiple files
    stat:
      path: "{{ item }}"
    loop:
      - /etc/config1.conf
      - /etc/config2.conf
      - /etc/config3.conf
    register: file_stats
  
  - name: Show results
    debug:
      msg: "{{ item.item }} exists: {{ item.stat.exists }}"
    loop: "{{ file_stats.results }}"
    loop_control:
      label: "{{ item.item }}"
  
  - name: Create missing files
    file:
      path: "{{ item.item }}"
      state: touch
    loop: "{{ file_stats.results }}"
    when: not item.stat.exists
    loop_control:
      label: "{{ item.item }}"
```

---

## ❌ Common Pitfalls

### Don't Use with_items (Legacy)

```yaml
# Bad - legacy syntax
- name: Old way
  debug: msg="{{ item }}"
  with_items:
    - one
    - two

# Good - modern syntax
- name: New way
  debug: msg="{{ item }}"
  loop:
    - one
    - two
```

### Handle Empty Lists

```yaml
# Bad - fails if packages is undefined
- name: Install packages
  apt: name="{{ item }}" state=present
  loop: "{{ packages }}"

# Good - handle empty/undefined
- name: Install packages
  apt: name="{{ item }}" state=present
  loop: "{{ packages | default([]) }}"
  when: packages is defined and packages | length > 0
```

### Large Lists Performance

```yaml
# Bad - processes sequentially
- name: Slow processing
  command: /long/task {{ item }}
  loop: "{{ large_list }}"

# Good - use async
- name: Fast processing
  command: /long/task {{ item }}
  async: 300
  poll: 0
  loop: "{{ large_list }}"
  register: jobs

- name: Wait for completion
  async_status:
    jid: "{{ item.ansible_job_id }}"
  loop: "{{ jobs.results }}"
  register: job_results
  until: job_results.finished
  retries: 30
```

---

## 🎯 Best Practices

1. **Use modern `loop`** - Avoid legacy `with_*` directives
2. **Label complex loops** - Improve readability in output
3. **Handle undefined** - Use `default()` filter
4. **Batch large operations** - Use throttle and pause
5. **Register selectively** - Only when needed
6. **Use async for long tasks** - Improve performance
7. **Flatten when possible** - Simplify nested structures
8. **Add conditionals wisely** - Filter in loop when possible

---

## 🔗 What's Next?

- **Next:** [Ansible Vault](11-ansible-vault.md)
- **Previous:** [Handlers & Conditionals](09-handlers-conditionals.md)
- **Related:** [Variables & Facts](07-variables-facts.md)

---

**Pro Tip:** Use `loop_control` with `label` to keep output clean when looping over complex data structures!
