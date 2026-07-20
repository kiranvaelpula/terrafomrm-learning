# Ansible Roles

> **Create reusable, modular automation with roles - the foundation of scalable Ansible**

---

## 📖 What You'll Learn

- Role structure and anatomy
- Creating and organizing roles
- Role dependencies
- Role defaults and variables
- Using roles in playbooks
- Best practices for role development

---

## 🎯 What are Roles?

Roles are Ansible's way to organize automation into reusable units. They provide:
- **Modularity** - Break complex automation into manageable pieces
- **Reusability** - Use same role across projects
- **Sharing** - Distribute via Ansible Galaxy
- **Organization** - Standard directory structure
- **Abstraction** - Hide complexity from playbooks

**When to use roles:**
- Configuring specific services (nginx, mysql)
- Setting up applications
- Common system configurations
- Repeatable patterns across hosts

---

## 📁 Role Structure

### Standard Directory Layout

```
roles/
└── webserver/
    ├── defaults/
    │   └── main.yml          # Default variables (lowest precedence)
    ├── files/
    │   ├── nginx.conf        # Static files
    │   └── index.html
    ├── handlers/
    │   └── main.yml          # Handlers
    ├── meta/
    │   └── main.yml          # Role metadata and dependencies
    ├── tasks/
    │   ├── main.yml          # Main task list
    │   ├── install.yml       # Subtasks
    │   └── configure.yml
    ├── templates/
    │   ├── vhost.j2          # Jinja2 templates
    │   └── nginx.conf.j2
    ├── tests/
    │   ├── inventory         # Test inventory
    │   └── test.yml          # Test playbook
    ├── vars/
    │   └── main.yml          # Role variables (higher precedence)
    └── README.md             # Documentation
```

### Minimal Role

```
roles/simple/
├── tasks/
│   └── main.yml
└── README.md
```

---

## 🚀 Creating Roles

### Using ansible-galaxy

```bash
# Create role structure
ansible-galaxy init webserver

# Create in specific directory
ansible-galaxy init --init-path roles/ webserver

# Result:
# roles/webserver/ with full directory structure
```

### Manual Creation

```bash
# Create directories
mkdir -p roles/myapp/{tasks,handlers,templates,files,vars,defaults,meta}

# Create main task file
cat > roles/myapp/tasks/main.yml <<EOF
---
- name: Install myapp
  apt:
    name: myapp
    state: present
EOF
```

---

## 📝 Role Components

### Tasks (tasks/main.yml)

```yaml
---
# Main task file
- name: Include OS-specific variables
  include_vars: "{{ ansible_os_family }}.yml"

- name: Install web server
  package:
    name: "{{ webserver_package }}"
    state: present

- name: Deploy configuration
  template:
    src: nginx.conf.j2
    dest: "{{ webserver_config_path }}"
  notify: restart webserver

- name: Ensure service is running
  service:
    name: "{{ webserver_service }}"
    state: started
    enabled: yes
```

### Task Includes

```yaml
# tasks/main.yml
---
- name: Include installation tasks
  include_tasks: install.yml

- name: Include configuration tasks
  include_tasks: configure.yml

- name: Include security tasks
  include_tasks: security.yml
  when: enable_security | bool

# tasks/install.yml
---
- name: Update package cache
  apt:
    update_cache: yes
  when: ansible_os_family == "Debian"

- name: Install packages
  package:
    name: "{{ item }}"
    state: present
  loop: "{{ required_packages }}"
```

### Defaults (defaults/main.yml)

```yaml
---
# Default variables - can be overridden
webserver_port: 80
webserver_ssl_port: 443
webserver_worker_processes: auto
webserver_worker_connections: 1024
enable_ssl: false
enable_security: true
required_packages:
  - nginx
  - openssl
```

### Vars (vars/main.yml)

```yaml
---
# Role variables - higher precedence
webserver_config_path: /etc/nginx/nginx.conf
webserver_service: nginx
webserver_user: www-data
webserver_group: www-data
```

### OS-Specific Variables

```yaml
# vars/Debian.yml
---
webserver_package: nginx
webserver_config_dir: /etc/nginx
webserver_log_dir: /var/log/nginx

# vars/RedHat.yml
---
webserver_package: httpd
webserver_config_dir: /etc/httpd
webserver_log_dir: /var/log/httpd
```

### Handlers (handlers/main.yml)

```yaml
---
- name: restart webserver
  service:
    name: "{{ webserver_service }}"
    state: restarted

- name: reload webserver
  service:
    name: "{{ webserver_service }}"
    state: reloaded

- name: validate webserver config
  command: "{{ webserver_binary }} -t"
  changed_when: false
```

### Templates (templates/nginx.conf.j2)

```jinja2
user {{ webserver_user }};
worker_processes {{ webserver_worker_processes }};
pid /var/run/nginx.pid;

events {
    worker_connections {{ webserver_worker_connections }};
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;

    {% if enable_ssl %}
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    {% endif %}

    include /etc/nginx/mime.types;
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

### Meta (meta/main.yml)

```yaml
---
galaxy_info:
  author: Your Name
  description: Web server configuration role
  company: Your Company
  license: MIT
  min_ansible_version: 2.9
  
  platforms:
    - name: Ubuntu
      versions:
        - focal
        - jammy
    - name: Debian
      versions:
        - buster
        - bullseye
  
  galaxy_tags:
    - webserver
    - nginx
    - web

dependencies:
  - role: common
    vars:
      install_python: yes
  - role: firewall
    vars:
      firewall_rules:
        - port: 80
        - port: 443
```

---

## 🎭 Using Roles

### Basic Usage

```yaml
---
- name: Configure web servers
  hosts: webservers
  roles:
    - webserver
```

### With Variables

```yaml
---
- name: Configure web servers
  hosts: webservers
  roles:
    - role: webserver
      vars:
        webserver_port: 8080
        enable_ssl: true
```

### Pre/Post Tasks

```yaml
---
- name: Deploy application
  hosts: appservers
  
  pre_tasks:
    - name: Announce deployment
      debug:
        msg: "Starting deployment"
  
  roles:
    - common
    - webserver
    - application
  
  post_tasks:
    - name: Verify deployment
      uri:
        url: http://localhost
        status_code: 200
```

### Conditional Roles

```yaml
---
- name: Configure servers
  hosts: all
  roles:
    - role: webserver
      when: "'webservers' in group_names"
    
    - role: database
      when: "'databases' in group_names"
```

### Role Tags

```yaml
---
- name: Full stack deployment
  hosts: all
  roles:
    - { role: common, tags: ['common', 'setup'] }
    - { role: webserver, tags: ['web', 'setup'] }
    - { role: application, tags: ['app', 'deploy'] }

# Run only web setup
# ansible-playbook site.yml --tags web
```

---

## 🔗 Role Dependencies

### Simple Dependencies

```yaml
# roles/application/meta/main.yml
---
dependencies:
  - common
  - webserver
  - database
```

### Dependencies with Variables

```yaml
# roles/wordpress/meta/main.yml
---
dependencies:
  - role: nginx
    vars:
      nginx_port: 80
      php_fpm: yes
  
  - role: mysql
    vars:
      mysql_databases:
        - name: wordpress
          user: wp_user
          password: "{{ wp_db_password }}"
  
  - role: php
    vars:
      php_version: "8.1"
      php_modules:
        - php-mysql
        - php-curl
        - php-gd
```

### Conditional Dependencies

```yaml
# roles/app/meta/main.yml
---
dependencies:
  - role: ssl
    when: enable_ssl | default(false) | bool
  
  - role: backup
    when: environment == "production"
```

---

## 📚 Complete Role Example

### Database Role

```
roles/postgresql/
├── defaults/
│   └── main.yml
├── files/
│   └── pg_hba.conf
├── handlers/
│   └── main.yml
├── tasks/
│   ├── main.yml
│   ├── install.yml
│   ├── configure.yml
│   └── databases.yml
├── templates/
│   └── postgresql.conf.j2
├── vars/
│   └── main.yml
└── meta/
    └── main.yml
```

**defaults/main.yml:**
```yaml
---
postgresql_version: "14"
postgresql_port: 5432
postgresql_max_connections: 100
postgresql_shared_buffers: "128MB"
postgresql_databases: []
postgresql_users: []
```

**tasks/main.yml:**
```yaml
---
- name: Include installation
  include_tasks: install.yml

- name: Include configuration
  include_tasks: configure.yml

- name: Include database setup
  include_tasks: databases.yml
  when: postgresql_databases | length > 0
```

**tasks/install.yml:**
```yaml
---
- name: Add PostgreSQL repository
  apt_repository:
    repo: "deb http://apt.postgresql.org/pub/repos/apt {{ ansible_distribution_release }}-pgdg main"
    state: present
  when: ansible_os_family == "Debian"

- name: Install PostgreSQL
  apt:
    name:
      - "postgresql-{{ postgresql_version }}"
      - "postgresql-contrib-{{ postgresql_version }}"
      - python3-psycopg2
    state: present
    update_cache: yes
```

**tasks/configure.yml:**
```yaml
---
- name: Deploy PostgreSQL configuration
  template:
    src: postgresql.conf.j2
    dest: "/etc/postgresql/{{ postgresql_version }}/main/postgresql.conf"
    owner: postgres
    group: postgres
    mode: '0644'
  notify: restart postgresql

- name: Deploy pg_hba configuration
  copy:
    src: pg_hba.conf
    dest: "/etc/postgresql/{{ postgresql_version }}/main/pg_hba.conf"
    owner: postgres
    group: postgres
    mode: '0640'
  notify: restart postgresql

- name: Ensure PostgreSQL is started
  service:
    name: postgresql
    state: started
    enabled: yes
```

**tasks/databases.yml:**
```yaml
---
- name: Create databases
  postgresql_db:
    name: "{{ item.name }}"
    state: present
  become_user: postgres
  loop: "{{ postgresql_databases }}"

- name: Create database users
  postgresql_user:
    name: "{{ item.name }}"
    password: "{{ item.password }}"
    db: "{{ item.db }}"
    priv: ALL
    state: present
  become_user: postgres
  loop: "{{ postgresql_users }}"
  no_log: yes
```

**handlers/main.yml:**
```yaml
---
- name: restart postgresql
  service:
    name: postgresql
    state: restarted

- name: reload postgresql
  service:
    name: postgresql
    state: reloaded
```

**Using the role:**
```yaml
---
- name: Setup database servers
  hosts: databases
  become: yes
  
  roles:
    - role: postgresql
      vars:
        postgresql_version: "14"
        postgresql_max_connections: 200
        postgresql_databases:
          - name: myapp
          - name: reporting
        postgresql_users:
          - name: app_user
            password: "{{ vault_db_password }}"
            db: myapp
```

---

## ✅ Best Practices

1. **One role, one purpose** - Keep roles focused
2. **Use defaults** - Provide sensible defaults
3. **Document everything** - Comprehensive README
4. **Tag appropriately** - Enable selective execution
5. **Test thoroughly** - Use Molecule
6. **Version control** - Track changes
7. **Follow conventions** - Standard directory structure
8. **Parameterize** - Avoid hardcoded values
9. **Handle OS differences** - Support multiple platforms
10. **Keep it simple** - Don't over-engineer

---

## 🔗 What's Next?

- **Next:** [Ansible Galaxy](14-galaxy.md)
- **Previous:** [Error Handling](../intermediate/12-error-handling.md)
- **Practice:** Create your own role!

---

**Pro Tip:** Start with a simple role and refactor existing playbooks into roles as patterns emerge. Don't create roles prematurely!
