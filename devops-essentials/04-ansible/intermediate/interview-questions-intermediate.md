# Ansible Interview Questions - Intermediate Level

> **50+ intermediate questions covering playbooks, variables, templates, handlers, and more**

---

## 📋 Table of Contents

1. [Playbook Structure](#playbook-structure) (10 questions)
2. [Variables & Facts](#variables-facts) (12 questions)
3. [Templates](#templates) (8 questions)
4. [Handlers & Conditionals](#handlers-conditionals) (10 questions)
5. [Loops](#loops) (5 questions)
6. [Vault](#vault) (5 questions)
7. [Scenario-Based](#scenario-based) (10 questions)

---

## Playbook Structure

### Q1: What is the difference between `include` and `import` in Ansible?

**Answer:**

**Import (Static):**
- Processed at playbook parse time
- Cannot use loops
- Cannot be conditional at task level
- Better performance
- Use with `import_tasks`, `import_playbook`, `import_role`

```yaml
# Processed before execution
- import_tasks: setup.yml
```

**Include (Dynamic):**
- Processed during playbook execution
- Can use loops
- Can be conditional
- More flexible
- Use with `include_tasks`, `include_role`

```yaml
# Processed during execution
- include_tasks: "{{ ansible_os_family | lower }}.yml"
- include_tasks: deploy.yml
  when: environment == "production"
```

**When to use each:**
- Import: Static, predictable includes
- Include: Dynamic, conditional includes

---

### Q2: Explain the execution order in an Ansible playbook.

**Answer:**

Execution order within a play:


1. **Variable loading** - Load all variables
2. **Fact gathering** - Gather facts if enabled
3. **Pre_tasks** - Run before roles
4. **Pre_tasks handlers** - Triggered by pre_tasks
5. **Roles** - Execute roles
6. **Tasks** - Execute main tasks
7. **Tasks handlers** - Triggered by roles and tasks
8. **Post_tasks** - Run after tasks
9. **Post_tasks handlers** - Triggered by post_tasks

```yaml
- name: Execution order example
  hosts: all
  gather_facts: yes           # Step 2
  
  pre_tasks:                  # Step 3
    - name: Update cache
      apt: update_cache=yes
  
  roles:                      # Step 5
    - common
  
  tasks:                      # Step 6
    - name: Deploy app
      copy: src=app dest=/opt/
  
  post_tasks:                 # Step 8
    - name: Verify deployment
      uri: url=http://localhost
  
  handlers:                   # Steps 4, 7, 9
    - name: restart app
      service: name=app state=restarted
```

---

### Q3: What are blocks in Ansible and when would you use them?

**Answer:**

Blocks allow grouping tasks with error handling:

```yaml
- name: Block example
  block:
    - name: Install package
      apt:
        name: myapp
        state: present
    
    - name: Start service
      service:
        name: myapp
        state: started
  
  rescue:
    - name: Handle failure
      debug:
        msg: "Installation failed, rolling back"
    
    - name: Cleanup
      file:
        path: /opt/myapp
        state: absent
  
  always:
    - name: Log attempt
      lineinfile:
        path: /var/log/ansible.log
        line: "Attempted myapp installation"
```

**Use cases:**
- Error handling with rescue
- Cleanup with always
- Applying common directives (become, when) to multiple tasks
- Organizing related tasks

---

### Q4: How do you optimize playbook performance?

**Answer:**

**1. Disable fact gathering when not needed:**
```yaml
- hosts: all
  gather_facts: no
```

**2. Use fact caching:**
```ini
# ansible.cfg
[defaults]
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/facts
fact_caching_timeout = 86400
```

**3. Enable pipelining:**
```ini
[ssh_connection]
pipelining = True
```

**4. Use async for long-running tasks:**
```yaml
- command: /long/running/script.sh
  async: 300
  poll: 10
```

**5. Limit host patterns:**
```bash
ansible-playbook site.yml --limit webservers
```

**6. Use mitogen strategy:**
```yaml
- hosts: all
  strategy: mitogen_linear
```

---

### Q5: What is the difference between `serial`, `throttle`, and `forks`?

**Answer:**

**Forks (Global):**
- Ansible.cfg setting
- Number of parallel processes
- Applies to all playbooks
```ini
[defaults]
forks = 10
```

**Serial (Play-level):**
- Limits hosts per batch
- Rolling updates
- Can use percentage
```yaml
- hosts: webservers
  serial: 2  # Or "25%" or [1, 3, 5]
```

**Throttle (Task-level):**
- Limits concurrent task execution
- For resource-intensive tasks
```yaml
- name: Heavy task
  command: /heavy/operation
  throttle: 1  # Only 1 at a time
```

**Example combining all:**
```yaml
# ansible.cfg: forks = 10

- hosts: all  # 100 hosts
  serial: 25%  # Process 25 hosts at a time
  tasks:
    - name: Update packages
      apt: upgrade=dist
      throttle: 5  # Only 5 concurrent updates
```

---

## Variables & Facts

### Q6: Explain variable precedence in Ansible (from lowest to highest).

**Answer:**

Variable precedence (22 levels, key ones):

1. Role defaults (`role/defaults/main.yml`)
2. Inventory file group vars
3. Inventory `group_vars/all`
4. Playbook `group_vars/all`
5. Inventory `group_vars/*`
6. Playbook `group_vars/*`
7. Inventory `host_vars/*`
8. Playbook `host_vars/*`
9. Host facts
10. Registered vars
11. Set_facts
12. Play vars
13. Play vars_files
14. Role vars (`role/vars/main.yml`)
15. Block vars
16. Task vars
17. Extra vars (`-e` CLI)

**Practical example:**
```yaml
# group_vars/all.yml
app_port: 8080

# playbook.yml
- hosts: all
  vars:
    app_port: 9000  # Overrides group_vars
  tasks:
    - debug:
        msg: "{{ app_port }}"  # Shows 9000
      vars:
        app_port: 7000  # Highest: shows 7000
```

**Rule of thumb:** More specific = higher precedence

---

### Q7: How do you work with nested variables and dictionaries?

**Answer:**

**Accessing nested data:**
```yaml
vars:
  database:
    primary:
      host: db1.example.com
      port: 5432
    replica:
      host: db2.example.com
      port: 5432

tasks:
  # Dot notation
  - debug: msg="{{ database.primary.host }}"
  
  # Bracket notation (required for vars with special chars)
  - debug: msg="{{ database['primary']['host'] }}"
  
  # Using with_dict/loop
  - debug:
      msg: "{{ item.key }}: {{ item.value.host }}"
    loop: "{{ database | dict2items }}"
```

**Merging dictionaries:**
```yaml
vars:
  defaults:
    timeout: 30
    retries: 3
  
  custom:
    timeout: 60
    debug: true
  
  final: "{{ defaults | combine(custom) }}"
  # Result: {timeout: 60, retries: 3, debug: true}
```

**Deep merging:**
```yaml
# ansible.cfg
[defaults]
hash_behaviour = merge

# Now nested dicts merge instead of replace
```

---

### Q8: What are magic variables in Ansible? Give examples.

**Answer:**

Magic variables are special variables automatically set by Ansible:

**Inventory variables:**
```yaml
inventory_hostname       # web01.example.com
inventory_hostname_short # web01
group_names             # ["webservers", "production"]
groups                  # All groups and their hosts
groups['webservers']    # Hosts in webservers group
```

**Playbook variables:**
```yaml
playbook_dir       # /path/to/playbook
role_path          # /path/to/roles/rolename
ansible_play_hosts # Hosts in current play
play_hosts         # Same as above
```

**Execution variables:**
```yaml
ansible_check_mode    # True if --check mode
ansible_version.full  # Ansible version
ansible_user         # SSH user
```

**Using hostvars:**
```yaml
# Access another host's variables
- debug:
    msg: "{{ hostvars['web01']['ansible_default_ipv4']['address'] }}"

# Generate hosts file
- lineinfile:
    path: /etc/hosts
    line: "{{ hostvars[item]['ansible_default_ipv4']['address'] }} {{ item }}"
  loop: "{{ groups['webservers'] }}"
```

---

### Q9: How do you create and use custom facts?

**Answer:**

**Creating custom facts:**

1. Create fact script:
```bash
# /etc/ansible/facts.d/app.fact
#!/bin/bash
cat <<EOF
{
  "app_name": "myapp",
  "version": "2.5.1",
  "deployed": "$(date -I)",
  "port": 8080
}
EOF
```

2. Deploy via playbook:
```yaml
- name: Deploy custom facts
  hosts: all
  become: yes
  tasks:
    - name: Create facts directory
      file:
        path: /etc/ansible/facts.d
        state: directory
        mode: '0755'
    
    - name: Deploy fact script
      copy:
        dest: /etc/ansible/facts.d/app.fact
        mode: '0755'
        content: |
          #!/bin/bash
          echo '{"version": "{{ app_version }}", "env": "{{ environment }}"}'
    
    - name: Reload facts
      setup:
        filter: ansible_local
    
    - name: Use custom fact
      debug:
        msg: "App version: {{ ansible_local.app.version }}"
```

**JSON facts (simpler):**
```json
// /etc/ansible/facts.d/server.fact
{
  "role": "webserver",
  "tier": "frontend",
  "monitoring": true
}
```

Access: `{{ ansible_local.server.role }}`

---

### Q10: How do you handle undefined variables?

**Answer:**

**Methods to handle undefined variables:**

**1. Default filter:**
```yaml
- debug:
    msg: "{{ undefined_var | default('N/A') }}"

# Default with different variable
- debug:
    msg: "{{ undefined_var | default(other_var) }}"

# Omit parameter if undefined
- user:
    name: myuser
    comment: "{{ user_comment | default(omit) }}"
```

**2. Conditional checks:**
```yaml
- name: Only if defined
  debug:
    msg: "{{ my_var }}"
  when: my_var is defined

- name: Only if undefined
  debug:
    msg: "Variable not set"
  when: my_var is undefined
```

**3. Assert required variables:**
```yaml
- name: Check required vars
  assert:
    that:
      - app_name is defined
      - app_version is defined
      - environment in ['dev', 'staging', 'prod']
    fail_msg: "Required variables missing"
```

**4. Set defaults in roles:**
```yaml
# roles/myapp/defaults/main.yml
app_port: 8080
app_timeout: 30
debug_mode: false
```

**5. Mandatory filter:**
```yaml
- debug:
    msg: "{{ required_var | mandatory }}"
  # Fails if required_var is undefined
```

---

## Templates

### Q11: What is Jinja2 and how is it used in Ansible?

**Answer:**

Jinja2 is a templating engine for Python, used by Ansible for:
- Generating dynamic configuration files
- String manipulation
- Conditional content
- Loops in templates

**Basic template:**
```jinja2
{# templates/nginx.conf.j2 #}
server {
    listen {{ http_port | default(80) }};
    server_name {{ server_name }};
    
    {% if ssl_enabled %}
    listen 443 ssl;
    ssl_certificate {{ ssl_cert }};
    {% endif %}
    
    location / {
        proxy_pass http://{{ backend_host }}:{{ backend_port }};
    }
}
```

**Deploying:**
```yaml
- name: Deploy nginx config
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    validate: 'nginx -t -c %s'
  notify: reload nginx
```

---

### Q12: How do you use loops in Jinja2 templates?

**Answer:**

**Simple loop:**
```jinja2
{% for package in packages %}
Package: {{ package }}
{% endfor %}
```

**Loop with conditions:**
```jinja2
{% for user in users %}
{% if user.active %}
User {{ loop.index }}: {{ user.name }} ({{ user.email }})
{% endif %}
{% endfor %}
```

**Loop variables:**
```jinja2
{% for item in items %}
{{ loop.index }}     - Current iteration (1-indexed)
{{ loop.index0 }}    - Current iteration (0-indexed)
{{ loop.first }}     - True if first iteration
{{ loop.last }}      - True if last iteration
{{ loop.length }}    - Total items
{{ loop.revindex }}  - Reverse index
{% endfor %}
```

**Dictionary loops:**
```jinja2
{% for key, value in config.items() %}
{{ key }} = {{ value }}
{% endfor %}
```

**Practical example - generate hosts file:**
```jinja2
# /etc/hosts
127.0.0.1 localhost

# Application servers
{% for host in groups['appservers'] %}
{{ hostvars[host]['ansible_default_ipv4']['address'] }}  {{ host }}
{% endfor %}

# Database servers  
{% for host in groups['databases'] %}
{{ hostvars[host]['ansible_default_ipv4']['address'] }}  {{ host }} {{ host }}.db
{% endfor %}
```

---

### Q13: Explain Jinja2 filters with examples.

**Answer:**

Filters transform variables:

**String filters:**
```jinja2
{{ "hello" | upper }}              # HELLO
{{ "WORLD" | lower }}              # world
{{ "hello world" | title }}        # Hello World
{{ "  text  " | trim }}            # text
{{ "hello" | center(10) }}         #   hello   
{{ name | default("Unknown") }}    # Default value
```

**List filters:**
```jinja2
{{ [1,2,3,4,5] | first }}          # 1
{{ [1,2,3,4,5] | last }}           # 5
{{ [1,2,3,4,5] | length }}         # 5
{{ [1,2,3,4,5] | min }}            # 1
{{ [1,2,3,4,5] | max }}            # 5
{{ [1,2,3,4,5] | sum }}            # 15
{{ [1,2,3,4,5] | random }}         # Random item
{{ items | sort }}                 # Sorted list
{{ items | unique }}               # Remove duplicates
{{ items | join(", ") }}           # Join with separator
```

**Ansible-specific:**
```jinja2
{{ password | password_hash('sha512') }}
{{ text | b64encode }}
{{ text | to_json }}
{{ text | to_yaml }}
{{ text | to_nice_json }}
{{ text | from_json }}
{{ "192.168.1.1" | ipaddr }}
{{ path | basename }}
{{ path | dirname }}
```

**Chaining filters:**
```jinja2
{{ server_name | default("localhost") | upper }}
{{ items | select("defined") | list }}
```

---

## Handlers & Conditionals

### Q14: When do handlers run and how can you control their execution?

**Answer:**

**Handler execution timing:**
- Run at end of play by default
- Run only once even if notified multiple times
- Run in order they're defined, not notified
- Don't run if play fails (unless forced)

**Controlling execution:**

**1. Flush handlers (run immediately):**
```yaml
tasks:
  - name: Update config
    copy: src=config dest=/etc/app/config
    notify: restart app
  
  - name: Run handlers now
    meta: flush_handlers
  
  - name: Task after restart
    wait_for: port=8080
```

**2. Force handlers on failure:**
```yaml
- hosts: all
  force_handlers: yes
  tasks:
    - name: Update config
      copy: src=config dest=/etc/app/config
      notify: restart app
    
    - name: This might fail
      command: /bin/false
  
  # Handler still runs even though play failed
  handlers:
    - name: restart app
      service: name=app state=restarted
```

**3. Listen directive (group handlers):**
```yaml
tasks:
  - name: Update web config
    template: src=web.conf.j2 dest=/etc/web.conf
    notify: reload services

handlers:
  - name: reload nginx
    service: name=nginx state=reloaded
    listen: reload services
  
  - name: reload apache
    service: name=apache2 state=reloaded
    listen: reload services
```

---

### Q15: What are the different types of conditionals in Ansible?

**Answer:**

**1. When clause:**
```yaml
- name: Install on Debian
  apt: name=package state=present
  when: ansible_os_family == "Debian"
```

**2. Failed_when:**
```yaml
- command: /opt/script.sh
  register: result
  failed_when:
    - result.rc != 0
    - "'WARNING' not in result.stderr"
```

**3. Changed_when:**
```yaml
- command: /opt/check.sh
  register: result
  changed_when: result.stdout != "OK"
```

**4. Check_mode (--check):**
```yaml
- name: Will run in check mode
  debug: msg="Checking"
  check_mode: yes

- name: Won't run in check mode
  command: /dangerous/command
  check_mode: no
```

**5. Block conditionals:**
```yaml
- block:
    - name: Task 1
      ...
    - name: Task 2
      ...
  when: environment == "production"
```

**6. Conditional imports:**
```yaml
- include_tasks: debian.yml
  when: ansible_os_family == "Debian"

- include_tasks: redhat.yml
  when: ansible_os_family == "RedHat"
```

---

### Q16: How do you handle different scenarios with complex conditionals?

**Answer:**

**Multiple conditions (AND):**
```yaml
when:
  - ansible_distribution == "Ubuntu"
  - ansible_distribution_version >= "20.04"
  - environment == "production"
```

**OR conditions:**
```yaml
when: ansible_distribution == "Ubuntu" or ansible_distribution == "Debian"

# Alternative for lists:
when: ansible_distribution in ["Ubuntu", "Debian", "RedHat"]
```

**Complex conditions:**
```yaml
when: >
  (ansible_distribution == "Ubuntu" and ansible_distribution_version >= "20.04")
  or
  (ansible_distribution == "Debian" and ansible_distribution_version >= "11")
```

**Based on registered variables:**
```yaml
- stat: path=/etc/app/config
  register: config

- name: Create if missing
  copy: src=default.conf dest=/etc/app/config
  when: not config.stat.exists

- name: Update if old
  copy: src=new.conf dest=/etc/app/config
  when:
    - config.stat.exists
    - config.stat.mtime < (ansible_date_time.epoch | int - 86400)
```

**Defined/undefined checks:**
```yaml
when: my_var is defined
when: my_var is undefined
when: my_var is defined and my_var | length > 0
```

---

## Scenario-Based Questions

### Q17: How would you implement a zero-downtime rolling deployment?

**Answer:**

```yaml
---
- name: Rolling deployment
  hosts: webservers
  serial: 1  # One host at a time
  
  tasks:
    # Remove from load balancer
    - name: Disable in load balancer
      haproxy:
        state: disabled
        host: "{{ inventory_hostname }}"
        backend: web_backend
        wait: yes
      delegate_to: "{{ groups['loadbalancers'][0] }}"
    
    # Wait for connections to drain
    - name: Wait for connection drain
      wait_for:
        timeout: 30
      delegate_to: localhost
    
    # Deploy new version
    - name: Deploy application
      copy:
        src: "app-{{ app_version }}.jar"
        dest: /opt/app/app.jar
      notify: restart app
    
    # Force restart now
    - meta: flush_handlers
    
    # Wait for app to start
    - name: Wait for application
      wait_for:
        port: 8080
        delay: 5
        timeout: 60
    
    # Verify health
    - name: Check application health
      uri:
        url: "http://{{ inventory_hostname }}:8080/health"
        status_code: 200
        return_content: yes
      register: health_check
      retries: 5
      delay: 5
      until: health_check.status == 200
    
    # Re-enable in load balancer
    - name: Enable in load balancer
      haproxy:
        state: enabled
        host: "{{ inventory_hostname }}"
        backend: web_backend
      delegate_to: "{{ groups['loadbalancers'][0] }}"
  
  handlers:
    - name: restart app
      service:
        name: myapp
        state: restarted
```

---

### Q18: How do you manage environment-specific configurations?

**Answer:**

**Directory structure:**
```
inventory/
├── production/
│   ├── hosts
│   └── group_vars/
│       ├── all.yml
│       └── webservers.yml
├── staging/
│   ├── hosts
│   └── group_vars/
│       ├── all.yml
│       └── webservers.yml
└── development/
    ├── hosts
    └── group_vars/
        ├── all.yml
        └── webservers.yml
```

**Environment-specific variables:**
```yaml
# group_vars/all.yml (common)
app_name: myapp
log_level: info

# production/group_vars/all.yml
environment: production
app_port: 80
db_host: db.prod.example.com
debug_mode: false
replicas: 3

# staging/group_vars/all.yml
environment: staging
app_port: 8080
db_host: db.staging.example.com
debug_mode: true
replicas: 1
```

**Running:**
```bash
ansible-playbook -i inventory/production site.yml
ansible-playbook -i inventory/staging site.yml
```

**Template usage:**
```jinja2
# templates/app.conf.j2
[app]
name = {{ app_name }}
environment = {{ environment }}
debug = {{ debug_mode | lower }}

[database]
host = {{ db_host }}
{% if environment == "production" %}
pool_size = 100
{% else %}
pool_size = 10
{% endif %}
```

---

### Q19: How would you automate OS-specific package installation?

**Answer:**

**Method 1: Using vars per OS:**
```yaml
# vars/Debian.yml
packages:
  - nginx
  - python3-pip
web_service: nginx

# vars/RedHat.yml  
packages:
  - httpd
  - python3-pip
web_service: httpd

# playbook.yml
- hosts: all
  tasks:
    - name: Include OS-specific vars
      include_vars: "{{ ansible_os_family }}.yml"
    
    - name: Install packages
      package:
        name: "{{ packages }}"
        state: present
    
    - name: Start web service
      service:
        name: "{{ web_service }}"
        state: started
```

**Method 2: Conditional tasks:**
```yaml
- name: Install on Debian
  apt:
    name:
      - nginx
      - python3-pip
    state: present
  when: ansible_os_family == "Debian"

- name: Install on RedHat
  yum:
    name:
      - httpd
      - python3-pip
    state: present
  when: ansible_os_family == "RedHat"
```

**Method 3: Package module (auto-detects):**
```yaml
- name: Install common packages
  package:
    name:
      - "{{ 'nginx' if ansible_os_family == 'Debian' else 'httpd' }}"
      - python3-pip
    state: present
```

---

### Q20: How do you test Ansible playbooks before production?

**Answer:**

**1. Syntax check:**
```bash
ansible-playbook site.yml --syntax-check
```

**2. Check mode (dry run):**
```bash
ansible-playbook site.yml --check
```

**3. Diff mode (show changes):**
```bash
ansible-playbook site.yml --check --diff
```

**4. Limit to specific hosts:**
```bash
ansible-playbook site.yml --limit test-server
```

**5. Tags for partial runs:**
```yaml
tasks:
  - name: Install packages
    apt: name=nginx state=present
    tags: [packages, setup]
  
  - name: Deploy app
    copy: src=app dest=/opt/
    tags: [deploy]

# Run only deploy tasks
# ansible-playbook site.yml --tags deploy
```

**6. Molecule testing:**
```bash
# Install molecule
pip install molecule molecule-docker

# Initialize
molecule init role my-role

# Test
molecule test
```

**7. Test environment:**
```yaml
# Use separate inventory
ansible-playbook -i inventory/test site.yml

# Verify tasks
- name: Verify installation
  command: nginx -v
  register: nginx_version
  failed_when: nginx_version.rc != 0

- name: Check service
  service_facts:
  failed_when: "'nginx.service' not in services"
```

**8. Ansible-lint:**
```bash
# Install
pip install ansible-lint

# Run
ansible-lint playbook.yml
```

---

## 🎯 Study Tips

1. **Practice all examples** - Run them in your lab
2. **Understand why** - Don't just memorize answers
3. **Create your own scenarios** - Build real projects
4. **Read documentation** - Official docs are comprehensive
5. **Join community** - Ansible forums, Reddit, Stack Overflow

---

## 📚 Additional Resources

- [Official Ansible Docs](https://docs.ansible.com/)
- [Ansible Galaxy](https://galaxy.ansible.com/)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)

---

**Ready for advanced topics?** → [Ansible Roles](../advanced/13-roles.md)

**Need basics review?** → [Interview Questions - Basics](../basics/interview-questions-basics.md)
