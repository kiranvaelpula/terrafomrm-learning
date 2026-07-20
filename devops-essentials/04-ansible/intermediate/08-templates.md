# Templates (Jinja2)

> **Generate dynamic configuration files with Jinja2 templating**

---

## 📖 What You'll Learn

- Jinja2 template syntax
- Variable substitution
- Control structures (loops, conditionals)
- Filters and tests
- Template best practices
- Real-world examples

---

## 🎯 Template Basics

### Simple Template

```jinja2
{# templates/hello.j2 #}
Hello {{ name }}!
Welcome to {{ app_name }}.
```

```yaml
# playbook
---
- name: Deploy template
  hosts: localhost
  vars:
    name: "DevOps Engineer"
    app_name: "Ansible Training"
  
  tasks:
    - name: Generate file from template
      template:
        src: templates/hello.j2
        dest: /tmp/hello.txt
```

### Configuration Template

```jinja2
{# templates/nginx.conf.j2 #}
server {
    listen {{ http_port }};
    server_name {{ server_name }};
    root {{ document_root }};
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

---

## 🔤 Variable Substitution

### Basic Substitution

```jinja2
# Simple variable
{{ variable_name }}

# Dictionary access
{{ config.database.host }}
{{ config['database']['port'] }}

# List access
{{ packages[0] }}
{{ packages[-1] }}

# With default
{{ variable_name | default('default_value') }}
```

### Example

```jinja2
{# templates/app.conf.j2 #}
[application]
name = {{ app_name }}
version = {{ app_version | default('1.0.0') }}
port = {{ app_port }}

[database]
host = {{ db_config.host }}
port = {{ db_config.port }}
name = {{ db_config.name }}
user = {{ db_config.user }}
```

---

## 🔄 Control Structures

### Conditionals

```jinja2
{# If statement #}
{% if ansible_os_family == "Debian" %}
Package manager: apt
{% endif %}

{# If-else #}
{% if environment == "production" %}
Debug = False
{% else %}
Debug = True
{% endif %}

{# If-elif-else #}
{% if cpu_cores >= 8 %}
workers = 8
{% elif cpu_cores >= 4 %}
workers = 4
{% else %}
workers = 2
{% endif %}
```

### Loops

```jinja2
{# Simple loop #}
{% for package in packages %}
{{ package }}
{% endfor %}

{# Loop with index #}
{% for user in users %}
{{ loop.index }}. {{ user.name }} - {{ user.email }}
{% endfor %}

{# Loop over dictionary #}
{% for key, value in config.items() %}
{{ key }} = {{ value }}
{% endfor %}

{# Conditional in loop #}
{% for server in servers %}
{% if server.enabled %}
server {{ server.name }} {{ server.ip }}:{{ server.port }}
{% endif %}
{% endfor %}
```

---

## 🎨 Filters

### String Filters

```jinja2
{# Case conversion #}
{{ app_name | upper }}          # MYAPP
{{ app_name | lower }}          # myapp
{{ app_name | title }}          # Myapp
{{ app_name | capitalize }}     # Myapp

{# String manipulation #}
{{ "  text  " | trim }}         # "text"
{{ "hello world" | replace("world", "ansible") }}
{{ "/path/to/file.txt" | basename }}     # file.txt
{{ "/path/to/file.txt" | dirname }}      # /path/to
{{ "file.txt" | splitext | first }}      # file

{# Encoding #}
{{ password | b64encode }}
{{ password | b64decode }}
{{ string | to_json }}
{{ string | to_yaml }}
```

### List Filters

```jinja2
{# List operations #}
{{ items | first }}             # First item
{{ items | last }}              # Last item
{{ items | length }}            # List length
{{ items | min }}               # Minimum value
{{ items | max }}               # Maximum value
{{ items | sum }}               # Sum of values
{{ items | sort }}              # Sorted list
{{ items | unique }}            # Remove duplicates
{{ items | reverse }}           # Reverse list
{{ items | join(', ') }}        # Join with separator
```

### Number Filters

```jinja2
{# Math operations #}
{{ 42.5 | round }}              # 43
{{ 42.5 | round(0, 'floor') }}  # 42
{{ 42.5 | round(0, 'ceil') }}   # 43
{{ 10 | pow(2) }}               # 100
{{ -5 | abs }}                  # 5
{{ value | int }}               # Convert to integer
{{ value | float }}             # Convert to float
```

### Default and Conditional Filters

```jinja2
{# Default values #}
{{ variable | default('N/A') }}
{{ variable | default(omit) }}  # Skip parameter if undefined

{# Ternary operator #}
{{ (ssl_enabled) | ternary('https', 'http') }}
{{ (is_production) | ternary(443, 8080) }}
```

---

## 🧪 Tests

### Common Tests

```jinja2
{# Existence tests #}
{% if variable is defined %}
Variable is defined
{% endif %}

{% if variable is undefined %}
Variable is not defined
{% endif %}

{# Type tests #}
{% if value is number %}
{% if value is string %}
{% if value is boolean %}
{% if value is iterable %}

{# Comparison tests #}
{% if version is version('2.0', '>=') %}
{% if path is file %}
{% if path is directory %}
{% if value is match('.*\.txt$') %}

{# List tests #}
{% if 'item' in list %}
{% if list is empty %}
```

### Example

```jinja2
{# templates/config.j2 #}
[server]
{% if http_port is defined %}
port = {{ http_port }}
{% else %}
port = 80
{% endif %}

{% if ssl_enabled is defined and ssl_enabled %}
ssl = on
ssl_port = {{ ssl_port | default(443) }}
{% endif %}

{% if workers is number %}
workers = {{ workers }}
{% else %}
workers = {{ ansible_processor_cores }}
{% endif %}
```

---

## 📝 Complete Examples

### Nginx Virtual Host

```jinja2
{# templates/vhost.conf.j2 #}
{% if ssl_enabled | default(false) %}
# HTTPS Configuration
server {
    listen 80;
    server_name {{ server_name }};
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name {{ server_name }};
    
    ssl_certificate {{ ssl_cert_path }};
    ssl_certificate_key {{ ssl_key_path }};
    ssl_protocols TLSv1.2 TLSv1.3;
    
    root {{ document_root }};
    index index.html index.php;
    
    access_log {{ log_dir }}/{{ server_name }}-access.log;
    error_log {{ log_dir }}/{{ server_name }}-error.log;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    {% if php_enabled | default(false) %}
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
    }
    {% endif %}
}
{% else %}
# HTTP Configuration
server {
    listen {{ http_port | default(80) }};
    server_name {{ server_name }};
    
    root {{ document_root }};
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
{% endif %}
```

### Application Configuration

```jinja2
{# templates/app.ini.j2 #}
[main]
app_name = {{ app_name }}
version = {{ app_version }}
environment = {{ app_environment | upper }}
debug = {{ (app_environment != 'production') | lower }}

[server]
host = {{ bind_address | default('0.0.0.0') }}
port = {{ app_port }}
workers = {{ workers | default(ansible_processor_cores * 2) }}
timeout = {{ timeout | default(30) }}

[database]
{% for db_name, db_config in databases.items() %}
[database.{{ db_name }}]
host = {{ db_config.host }}
port = {{ db_config.port | default(5432) }}
name = {{ db_config.name }}
user = {{ db_config.user }}
max_connections = {{ db_config.max_conn | default(100) }}
{% endfor %}

[cache]
{% if cache_enabled | default(true) %}
enabled = true
backend = {{ cache_backend | default('redis') }}
host = {{ cache_host | default('localhost') }}
port = {{ cache_port | default(6379) }}
ttl = {{ cache_ttl | default(3600) }}
{% else %}
enabled = false
{% endif %}

[logging]
level = {{ log_level | default('INFO') }}
format = {{ log_format | default('%(asctime)s - %(name)s - %(levelname)s - %(message)s') }}
{% if log_files is defined %}
handlers = {{ log_files | join(',') }}
{% endif %}

[features]
{% for feature, enabled in features.items() | default([]) %}
{{ feature }} = {{ enabled | lower }}
{% endfor %}
```

### Hosts File

```jinja2
{# templates/hosts.j2 #}
# Generated by Ansible on {{ ansible_date_time.iso8601 }}
# DO NOT EDIT MANUALLY

127.0.0.1   localhost localhost.localdomain

{% for host in groups['all'] %}
{% if hostvars[host]['ansible_default_ipv4'] is defined %}
{{ hostvars[host]['ansible_default_ipv4']['address'] }}    {{ hostvars[host]['inventory_hostname'] }} {{ hostvars[host]['inventory_hostname_short'] }}
{% endif %}
{% endfor %}

# Application servers
{% for host in groups['appservers'] | default([]) %}
{{ hostvars[host]['ansible_default_ipv4']['address'] }}    {{ host }}
{% endfor %}

# Database servers
{% for host in groups['databases'] | default([]) %}
{{ hostvars[host]['ansible_default_ipv4']['address'] }}    {{ host }}
{% endfor %}
```

### Systemd Service

```jinja2
{# templates/service.j2 #}
[Unit]
Description={{ service_description | default(app_name + ' Service') }}
After=network.target
{% if dependencies is defined %}
Requires={{ dependencies | join(' ') }}
{% endif %}

[Service]
Type={{ service_type | default('simple') }}
User={{ app_user }}
Group={{ app_group }}
WorkingDirectory={{ app_dir }}
ExecStart={{ app_binary }} {{ app_args | default('') }}
ExecReload=/bin/kill -HUP $MAINPID
KillMode={{ kill_mode | default('mixed') }}
Restart={{ restart_policy | default('on-failure') }}
RestartSec={{ restart_sec | default(5) }}

{% if environment_vars is defined %}
{% for key, value in environment_vars.items() %}
Environment="{{ key }}={{ value }}"
{% endfor %}
{% endif %}

{% if resource_limits is defined %}
LimitNOFILE={{ resource_limits.nofile | default(65536) }}
LimitNPROC={{ resource_limits.nproc | default(32768) }}
{% endif %}

[Install]
WantedBy=multi-user.target
```

---

## 🛠️ Template Module Options

### Basic Usage

```yaml
tasks:
  - name: Deploy configuration
    template:
      src: app.conf.j2
      dest: /etc/app/app.conf
      owner: root
      group: root
      mode: '0644'
```

### With Validation

```yaml
tasks:
  - name: Deploy nginx config
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
      validate: 'nginx -t -c %s'
    notify: reload nginx
```

### With Backup

```yaml
tasks:
  - name: Deploy config with backup
    template:
      src: config.j2
      dest: /etc/app/config
      backup: yes
```

---

## 🎓 Advanced Techniques

### Macros

```jinja2
{# Define macro #}
{% macro render_server(name, ip, port) %}
server {
    name {{ name }};
    address {{ ip }}:{{ port }};
}
{% endmacro %}

{# Use macro #}
{% for server in servers %}
{{ render_server(server.name, server.ip, server.port) }}
{% endfor %}
```

### Template Inheritance

```jinja2
{# templates/base.j2 #}
<configuration>
    {% block server %}
    <server>
        <port>{{ port | default(8080) }}</port>
    </server>
    {% endblock %}
    
    {% block database %}
    {% endblock %}
</configuration>

{# templates/app.j2 #}
{% extends "base.j2" %}

{% block database %}
<database>
    <host>{{ db_host }}</host>
    <port>{{ db_port }}</port>
</database>
{% endblock %}
```

### Including Templates

```jinja2
{# templates/main.conf.j2 #}
[main]
app = {{ app_name }}

{% include 'templates/database.j2' %}
{% include 'templates/cache.j2' %}

{# templates/database.j2 #}
[database]
host = {{ db_host }}
port = {{ db_port }}
```

### Whitespace Control

```jinja2
{# Remove whitespace #}
{% for item in items -%}
{{ item }}
{%- endfor %}

{# Keep one line #}
{% for item in items %}
{{ item }}
{% endfor %}
```

---

## ✅ Best Practices

1. **Add comments:** Document complex logic
2. **Use meaningful names:** Clear variable names
3. **Default values:** Handle undefined variables
4. **Validate output:** Use validate parameter
5. **Test templates:** Use --check mode
6. **Version control:** Track template changes
7. **Keep it simple:** Complex logic belongs in playbook
8. **Use filters:** Leverage built-in transformations

---

## 🔗 What's Next?

- **Next:** [Handlers & Conditionals](09-handlers-conditionals.md)
- **Previous:** [Variables & Facts](07-variables-facts.md)
- **Related:** [Playbook Structure](06-playbook-structure.md)

---

**Pro Tip:** Use `ansible-playbook --syntax-check` to validate template syntax before deploying!
