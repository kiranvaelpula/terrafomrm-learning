# Ansible Basic Modules

## What are Ansible Modules?

Modules are the building blocks of Ansible. Each module does ONE specific thing — install a package, copy a file, start a service, create a user, etc. You combine modules in playbooks to automate complex tasks.

**Analogy:** If a playbook is a recipe, modules are the individual actions — "chop onions", "boil water", "add salt." Each action is a module.

**Key point:** You don't write shell scripts with Ansible. You use modules. Modules are idempotent — they check if the desired state already exists before making changes. Run it 10 times, same result.

---

## Most Common Modules

| Module | Purpose |
|---|---|
| `apt` / `yum` / `dnf` | Install/remove packages |
| `copy` | Copy files to remote servers |
| `template` | Copy files with variables (Jinja2) |
| `file` | Create/delete files/directories, set permissions |
| `service` / `systemd` | Start/stop/restart services |
| `user` | Create/manage user accounts |
| `command` / `shell` | Run shell commands (use as last resort) |
| `lineinfile` | Add/modify a line in a file |
| `git` | Clone/pull Git repos |
| `docker_container` | Manage Docker containers |
| `uri` | Make HTTP requests |
| `debug` | Print variables/messages for debugging |

---

## 1. Package Management (apt / yum)

### Install packages

```yaml
# For Debian/Ubuntu
- name: Install nginx
  apt:
    name: nginx
    state: present          # present = install, absent = remove
    update_cache: yes       # Run apt update first

# For RHEL/CentOS
- name: Install nginx
  yum:
    name: nginx
    state: present

# Install multiple packages
- name: Install required packages
  apt:
    name:
      - nginx
      - git
      - curl
      - docker.io
    state: present
    update_cache: yes
```

### Remove packages

```yaml
- name: Remove apache (we use nginx)
  apt:
    name: apache2
    state: absent           # absent = uninstall
    purge: yes              # Also remove config files
```

### Install specific version

```yaml
- name: Install specific Node.js version
  apt:
    name: nodejs=18.17.0-1nodesource1
    state: present
```

**When to use:** Any time you need software installed on servers.

---

## 2. Copy Module

Copy files from your local machine (control node) to remote servers.

```yaml
# Copy a single file
- name: Copy nginx config
  copy:
    src: ./files/nginx.conf           # Local path
    dest: /etc/nginx/nginx.conf       # Remote path
    owner: root
    group: root
    mode: '0644'                      # File permissions

# Copy with inline content
- name: Create index.html
  copy:
    content: |
      <html>
        <body><h1>Hello from Ansible!</h1></body>
      </html>
    dest: /var/www/html/index.html
    mode: '0644'

# Copy entire directory
- name: Copy website files
  copy:
    src: ./website/                    # Trailing slash = copy contents
    dest: /var/www/html/
    owner: www-data
    group: www-data
```

**When to use:** Static config files, scripts, certificates — anything that doesn't need variables.

---

## 3. Template Module (Jinja2)

Like `copy`, but the file can contain variables that get filled in per server.

**Template file** (`templates/nginx.conf.j2`):
```nginx
server {
    listen {{ http_port }};
    server_name {{ domain_name }};
    root {{ web_root }};

    location / {
        proxy_pass http://127.0.0.1:{{ app_port }};
    }
}
```

**Playbook:**
```yaml
- name: Deploy nginx config from template
  template:
    src: templates/nginx.conf.j2
    dest: /etc/nginx/sites-available/myapp.conf
    owner: root
    group: root
    mode: '0644'
  vars:
    http_port: 80
    domain_name: "myapp.example.com"
    web_root: "/var/www/myapp"
    app_port: 3000
  notify: restart nginx              # Trigger handler if file changed
```

**When to use:** Config files that differ per environment/server (ports, hostnames, IPs).

**Copy vs Template:**
- `copy` = static file, same everywhere
- `template` = dynamic file with variables (`{{ variable }}`)

---

## 4. File Module

Create/delete files and directories, set permissions and ownership.

```yaml
# Create a directory
- name: Create app directory
  file:
    path: /opt/myapp
    state: directory
    owner: deploy
    group: deploy
    mode: '0755'

# Create an empty file
- name: Create log file
  file:
    path: /var/log/myapp.log
    state: touch
    owner: appuser
    mode: '0644'

# Delete a file
- name: Remove old config
  file:
    path: /etc/old-config.conf
    state: absent

# Create a symlink
- name: Link current release
  file:
    src: /opt/myapp/releases/v2.0
    dest: /opt/myapp/current
    state: link

# Set permissions recursively
- name: Fix permissions on web directory
  file:
    path: /var/www/html
    state: directory
    owner: www-data
    group: www-data
    recurse: yes
```

**`state` options:**
| State | What it does |
|---|---|
| `directory` | Create directory (and parents) |
| `file` | Check file exists (doesn't create) |
| `touch` | Create empty file |
| `link` | Create symbolic link |
| `absent` | Delete file/directory |

---

## 5. Service / Systemd Module

Manage services (start, stop, restart, enable on boot).

```yaml
# Start and enable nginx
- name: Start nginx
  service:
    name: nginx
    state: started         # started, stopped, restarted, reloaded
    enabled: yes           # Start on boot

# Restart a service
- name: Restart application
  service:
    name: myapp
    state: restarted

# Using systemd module (more features)
- name: Reload systemd and start service
  systemd:
    name: myapp
    state: started
    enabled: yes
    daemon_reload: yes     # Run systemctl daemon-reload first
```

**`state` options:**
| State | Meaning |
|---|---|
| `started` | Start if not running (no-op if already running) |
| `stopped` | Stop if running |
| `restarted` | Always restart (even if running) |
| `reloaded` | Reload config without restart |

---

## 6. User Module

Create and manage system users.

```yaml
# Create a user
- name: Create deploy user
  user:
    name: deploy
    shell: /bin/bash
    groups: sudo,docker       # Additional groups
    append: yes               # Append to groups (don't replace)
    create_home: yes
    state: present

# Create user with SSH key
- name: Create user with authorized key
  user:
    name: deploy
    shell: /bin/bash
    generate_ssh_key: yes

# Remove a user
- name: Remove old user
  user:
    name: olduser
    state: absent
    remove: yes               # Also remove home directory
```

---

## 7. Command / Shell Module

Run arbitrary commands. **Use as last resort** — prefer specific modules when available.

```yaml
# command module (no shell features — pipes, redirects don't work)
- name: Check disk space
  command: df -h
  register: disk_output       # Save output to variable

- name: Show disk space
  debug:
    var: disk_output.stdout

# shell module (full shell features — pipes, redirects work)
- name: Find large files
  shell: find /var/log -size +100M | head -5
  register: large_files

# Only run if a condition is met
- name: Run migration only if needed
  command: python manage.py migrate
  args:
    chdir: /opt/myapp         # Run from this directory
    creates: /opt/myapp/.migrated   # Skip if this file exists
```

**command vs shell:**
| | command | shell |
|---|---|---|
| Pipes (`\|`) | ❌ | ✅ |
| Redirects (`>`) | ❌ | ✅ |
| Environment vars | ❌ | ✅ |
| Safer | ✅ | ❌ (shell injection risk) |

**When to use:** Only when no specific module exists for what you need.

---

## 8. Lineinfile Module

Add, modify, or remove a single line in a file.

```yaml
# Add a line to a file
- name: Add environment variable
  lineinfile:
    path: /etc/environment
    line: 'APP_ENV=production'
    state: present

# Modify an existing line (find and replace)
- name: Change SSH port
  lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^#?Port'              # Find line starting with Port or #Port
    line: 'Port 2222'             # Replace with this
  notify: restart sshd

# Remove a line
- name: Remove insecure option
  lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^PermitRootLogin yes'
    state: absent

# Add line after a specific line
- name: Add config after section header
  lineinfile:
    path: /etc/app.conf
    insertafter: '^\[database\]'
    line: 'host=10.0.1.5'
```

**When to use:** Quick config changes — one line at a time. For complex files, use `template` instead.

---

## 9. Git Module

Clone or update Git repositories.

```yaml
- name: Clone application repo
  git:
    repo: https://github.com/myorg/myapp.git
    dest: /opt/myapp
    version: main              # Branch, tag, or commit hash
    force: yes                 # Discard local changes

- name: Deploy specific release
  git:
    repo: https://github.com/myorg/myapp.git
    dest: /opt/myapp
    version: v2.1.0            # Deploy this tag
```

---

## 10. Debug Module

Print messages and variables — essential for troubleshooting.

```yaml
- name: Show a variable
  debug:
    var: ansible_hostname

- name: Print a message
  debug:
    msg: "Deploying to {{ inventory_hostname }} on port {{ app_port }}"

- name: Show command output
  command: whoami
  register: result

- name: Display result
  debug:
    var: result.stdout
```

---

## Complete Playbook Example

Putting modules together — deploy a web app from scratch:

```yaml
---
- name: Deploy web application
  hosts: webservers
  become: yes

  vars:
    app_user: deploy
    app_dir: /opt/myapp
    app_port: 3000

  tasks:
    - name: Install required packages
      apt:
        name:
          - nginx
          - git
          - nodejs
          - npm
        state: present
        update_cache: yes

    - name: Create app user
      user:
        name: "{{ app_user }}"
        shell: /bin/bash
        create_home: yes

    - name: Create app directory
      file:
        path: "{{ app_dir }}"
        state: directory
        owner: "{{ app_user }}"
        mode: '0755'

    - name: Clone application
      git:
        repo: https://github.com/myorg/myapp.git
        dest: "{{ app_dir }}"
        version: main
      become_user: "{{ app_user }}"

    - name: Install npm dependencies
      command: npm install --production
      args:
        chdir: "{{ app_dir }}"
      become_user: "{{ app_user }}"

    - name: Deploy nginx config
      template:
        src: templates/nginx-app.conf.j2
        dest: /etc/nginx/sites-available/myapp.conf
      notify: restart nginx

    - name: Enable nginx site
      file:
        src: /etc/nginx/sites-available/myapp.conf
        dest: /etc/nginx/sites-enabled/myapp.conf
        state: link
      notify: restart nginx

    - name: Start application
      service:
        name: myapp
        state: started
        enabled: yes

  handlers:
    - name: restart nginx
      service:
        name: nginx
        state: restarted
```

---

## Module Idempotency

**Why modules are better than shell commands:**

```yaml
# ❌ Not idempotent (runs apt install every time, even if already installed)
- command: apt install nginx

# ✅ Idempotent (checks first, only installs if missing)
- apt:
    name: nginx
    state: present
```

Run the playbook 10 times — first run makes changes, next 9 say "ok" (no changes). That's idempotency.

---

## Interview Tips

**Q: What Ansible modules have you used?**
> "I regularly use apt/yum for packages, template for dynamic configs, service for managing daemons, file for permissions, and git for deployments. I avoid command/shell unless no specific module exists."

**Q: Why use modules instead of shell commands?**
> "Modules are idempotent — they check desired state before acting. Shell commands run every time regardless. Modules also handle error checking, cross-platform differences, and provide consistent output."

---

## Next Steps

Continue to: [Interview Questions - Basics →](./interview-questions-basics.md)
