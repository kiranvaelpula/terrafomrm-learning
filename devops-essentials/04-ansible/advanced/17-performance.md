# Performance Optimization

> **Scale Ansible for large infrastructures with performance tuning**

---

## 📖 What You'll Learn

- Performance optimization techniques
- Parallelization strategies
- Fact gathering optimization
- Connection optimization
- Large-scale patterns
- Profiling and benchmarking

---

## ⚡ Quick Wins

### 1. Increase Forks

```ini
# ansible.cfg
[defaults]
forks = 50  # Default is 5
```

```bash
# Command line
ansible-playbook site.yml -f 50
```

### 2. Enable Pipelining

```ini
# ansible.cfg
[ssh_connection]
pipelining = True
```

**Benefit:** Reduces SSH operations by ~75%

### 3. Disable Gathering

```yaml
---
- hosts: all
  gather_facts: no  # Skip if not needed
  tasks:
    - name: Quick task
      command: uptime
```

### 4. Use Strategy

```yaml
---
- hosts: all
  strategy: free  # Don't wait for slow hosts
  tasks:
    - name: Independent task
      command: /quick/script.sh
```

---

## 🚀 Fact Gathering Optimization

### Disable When Not Needed

```yaml
---
- hosts: all
  gather_facts: no
  tasks:
    # No facts required
    - copy:
        src: file.txt
        dest: /tmp/
```

### Gather Selectively

```yaml
---
- hosts: all
  gather_facts: yes
  tasks:
    - name: Gather only network facts
      setup:
        gather_subset:
          - '!all'
          - '!any'
          - network
```

### Fact Caching

```ini
# ansible.cfg
[defaults]
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400  # 24 hours

# Or use Redis
fact_caching = redis
fact_caching_connection = localhost:6379:0
```

### Custom Facts Only

```yaml
---
- hosts: all
  gather_facts: no
  tasks:
    - name: Get custom facts
      setup:
        filter: ansible_local
```

---

## 🔌 Connection Optimization

### SSH Multiplexing

```ini
# ansible.cfg
[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s -o ControlPath=/tmp/ansible-ssh-%h-%p-%r
pipelining = True
```

### Connection Pooling

```ini
[defaults]
# Keep connections alive
timeout = 30

[ssh_connection]
control_path_dir = ~/.ansible/cp
control_path = %(directory)s/ansible-%%C
```

### Persistent Connections

```ini
[persistent_connection]
connect_timeout = 30
command_timeout = 30
```

---

## 📊 Parallel Execution

### Serial Batching

```yaml
---
- hosts: webservers
  serial:
    - 1      # First host
    - 10%    # Then 10%
    - 50%    # Then 50%
    - 100%   # Rest
  tasks:
    - name: Rolling update
      command: /update/script.sh
```

### Async Tasks

```yaml
tasks:
  - name: Long-running task
    command: /long/script.sh
    async: 3600      # Run for up to 1 hour
    poll: 0          # Fire and forget
    register: long_task
  
  - name: Do other work
    command: /quick/task.sh
  
  - name: Check async status
    async_status:
      jid: "{{ long_task.ansible_job_id }}"
    register: job_result
    until: job_result.finished
    retries: 30
    delay: 10
```

### Free Strategy

```yaml
---
- hosts: all
  strategy: free  # Each host runs independently
  tasks:
    - name: Task 1
      command: /script1.sh
    
    - name: Task 2
      command: /script2.sh
```

---

## 🎯 Task Optimization

### Minimize Loops

```yaml
# Slow - multiple SSH connections
- name: Install packages (slow)
  apt:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - git
    - vim

# Fast - single SSH connection
- name: Install packages (fast)
  apt:
    name:
      - nginx
      - git
      - vim
    state: present
```

### Batch Operations

```yaml
# Bad - 100 tasks
- name: Create users
  user:
    name: "{{ item }}"
  loop: "{{ users }}"  # 100 users = 100 SSH connections

# Good - 1 task with loop control
- name: Create users
  user:
    name: "{{ item }}"
  loop: "{{ users }}"
  loop_control:
    pause: 0  # No pause needed
```

### Use Bulk Modules

```yaml
# Instead of multiple file modules
- name: Bulk file operations
  synchronize:
    src: /local/files/
    dest: /remote/files/
    recursive: yes
```

---

## 📦 Module Performance

### Native Modules

```yaml
# Slow - shell/command
- name: Add line (slow)
  command: echo "line" >> /etc/config

# Fast - native module
- name: Add line (fast)
  lineinfile:
    path: /etc/config
    line: "line"
```

### Copy vs Template

```yaml
# Use copy for static files (faster)
- name: Static file
  copy:
    src: static.conf
    dest: /etc/app/config

# Use template only when needed
- name: Dynamic file
  template:
    src: dynamic.conf.j2
    dest: /etc/app/config
  when: needs_templating | bool
```

---

## 🏗️ Playbook Structure

### Include vs Import

```yaml
# Import - static, faster parsing
- import_tasks: tasks/common.yml

# Include - dynamic, slower but flexible
- include_tasks: "tasks/{{ ansible_os_family }}.yml"
```

### Task Organization

```yaml
# Group related tasks
- name: Setup application
  block:
    - name: Install packages
      apt: name={{ packages }}
    
    - name: Configure service
      template: src=app.conf.j2 dest=/etc/app/
    
    - name: Start service
      service: name=app state=started
  when: deploy_app | bool
```

---

## 💾 Large Inventory Optimization

### Limit Hosts

```bash
# Run on subset
ansible-playbook site.yml --limit webservers

# Run on pattern
ansible-playbook site.yml --limit "web*"

# Run on single host
ansible-playbook site.yml --limit web01
```

### Inventory Caching

```ini
# ansible.cfg
[inventory]
cache = yes
cache_plugin = jsonfile
cache_timeout = 3600
cache_connection = /tmp/ansible_inventory
```

### Host Batching

```yaml
---
- name: Large deployment
  hosts: all
  serial: 100  # Process 100 at a time
  tasks:
    - name: Deploy
      command: /deploy.sh
```

---

## 📈 Profiling

### Callback Plugins

```ini
# ansible.cfg
[defaults]
callbacks_enabled = timer, profile_tasks, profile_roles
```

**timer** - Total playbook execution time  
**profile_tasks** - Time per task  
**profile_roles** - Time per role

### Custom Profiling

```yaml
---
- hosts: all
  tasks:
    - name: Start timer
      set_fact:
        start_time: "{{ ansible_date_time.epoch }}"
    
    - name: Long task
      command: /long/script.sh
    
    - name: Calculate duration
      debug:
        msg: "Duration: {{ ansible_date_time.epoch | int - start_time | int }}s"
```

---

## 🎨 Advanced Patterns

### Mitogen Strategy

```bash
# Install
pip install mitogen

# ansible.cfg
[defaults]
strategy_plugins = /path/to/mitogen/ansible_mitogen/plugins/strategy
strategy = mitogen_linear

# Or in playbook
- hosts: all
  strategy: mitogen_linear
```

**Performance gain:** 1.25x to 7x faster

### Connection Pooling

```ini
[defaults]
# Persistent connection
[persistent_connection]
connect_timeout = 30
command_timeout = 30
```

### Optimized Playbook

```yaml
---
- name: High-performance deployment
  hosts: all
  strategy: mitogen_linear
  gather_facts: no
  
  pre_tasks:
    - name: Gather minimal facts
      setup:
        gather_subset:
          - '!all'
          - network
      when: facts_needed | default(false)
  
  tasks:
    - name: Bulk package install
      package:
        name: "{{ packages }}"
        state: present
    
    - name: Async long task
      command: /long/process.sh
      async: 3600
      poll: 0
      register: async_task
    
    - name: Quick tasks
      copy:
        src: "{{ item }}"
        dest: /etc/app/
      loop:
        - file1.conf
        - file2.conf
    
    - name: Wait for async
      async_status:
        jid: "{{ async_task.ansible_job_id }}"
      register: result
      until: result.finished
      retries: 60
```

---

## 📊 Benchmarking

### Before Optimization

```bash
time ansible-playbook site.yml
```

### Measure Impact

```bash
# Test with different forks
time ansible-playbook site.yml -f 5
time ansible-playbook site.yml -f 10
time ansible-playbook site.yml -f 20
time ansible-playbook site.yml -f 50

# Test with profiling
ANSIBLE_CALLBACK_WHITELIST=profile_tasks ansible-playbook site.yml
```

### Metrics to Track

- **Total execution time**
- **Time per task**
- **Time per host**
- **SSH connections**
- **API calls (for dynamic inventory)**
- **Memory usage**

---

## ✅ Performance Checklist

### Configuration
- [ ] forks = 50 (or higher)
- [ ] pipelining = True
- [ ] gathering = smart
- [ ] fact_caching enabled
- [ ] SSH multiplexing configured

### Playbooks
- [ ] gather_facts = no when possible
- [ ] Use bulk operations
- [ ] Minimize loops
- [ ] Use native modules
- [ ] Leverage async for long tasks

### Inventory
- [ ] Cache dynamic inventory
- [ ] Use --limit when possible
- [ ] Batch large deployments

### Monitoring
- [ ] Enable profiling callbacks
- [ ] Measure before/after
- [ ] Track bottlenecks
- [ ] Monitor resource usage

---

## 🔗 What's Next?

- **Next:** [Security Best Practices](18-security.md)
- **Previous:** [Tower/AWX](16-tower-awx.md)
- **Related:** [Loops](../intermediate/10-loops.md)

---

**Pro Tip:** Start with forks, pipelining, and fact caching - these three changes alone can give you 2-5x performance improvement!
