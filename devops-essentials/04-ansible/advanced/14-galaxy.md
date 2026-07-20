# Ansible Galaxy

> **Leverage community roles and share your own automation with Ansible Galaxy**

---

## 📖 What You'll Learn

- What is Ansible Galaxy
- Finding and using community roles
- Installing roles from Galaxy
- Creating and publishing roles
- Galaxy CLI commands
- Best practices for role consumption

---

## 🌌 What is Ansible Galaxy?

**Ansible Galaxy** is a hub for finding, reusing, and sharing Ansible content:
- **Public repository** of community roles
- **Role management** via CLI
- **Collections** of roles, modules, and plugins
- **Quality ratings** and downloads tracking
- **Free hosting** for open-source roles

**Website:** https://galaxy.ansible.com

---

## 🔍 Finding Roles

### Search on Website

Visit https://galaxy.ansible.com and search for:
- Web servers (nginx, apache)
- Databases (postgresql, mysql, mongodb)
- Languages (python, java, node)
- Tools (docker, kubernetes, jenkins)
- Cloud providers (aws, azure, gcp)

### Search via CLI

```bash
# Search for roles
ansible-galaxy search nginx

# Search with filters
ansible-galaxy search nginx --platforms Ubuntu

# Search by author
ansible-galaxy search --author geerlingguy

# Search with specific tags
ansible-galaxy search --tags webserver
```

---

## 📥 Installing Roles

### Basic Installation

```bash
# Install from Galaxy
ansible-galaxy install geerlingguy.nginx

# Install specific version
ansible-galaxy install geerlingguy.nginx,2.8.0

# Install to custom directory
ansible-galaxy install geerlingguy.nginx -p ./roles

# Install multiple roles
ansible-galaxy install geerlingguy.nginx geerlingguy.mysql
```

### Using requirements.yml

```yaml
# requirements.yml
---
roles:
  # From Galaxy
  - name: geerlingguy.nginx
    version: 2.8.0
  
  - name: geerlingguy.mysql
    version: 3.3.2
  
  # From GitHub
  - name: my-custom-role
    src: https://github.com/username/ansible-role-custom.git
    version: main
  
  - name: company-role
    src: git+https://github.com/company/ansible-roles.git
    scm: git
    version: v1.0.0

collections:
  - name: community.general
    version: 4.8.0
  
  - name: ansible.posix
    version: 1.4.0
```

```bash
# Install from requirements file
ansible-galaxy install -r requirements.yml

# Force reinstall
ansible-galaxy install -r requirements.yml --force

# Install to specific path
ansible-galaxy install -r requirements.yml -p ./roles
```

---

## 📋 Managing Installed Roles

### List Installed Roles

```bash
# List all installed roles
ansible-galaxy list

# List roles in specific path
ansible-galaxy list -p ./roles
```

### Role Information

```bash
# Show role info
ansible-galaxy info geerlingguy.nginx

# Show role README
ansible-galaxy info geerlingguy.nginx --offline
```

### Removing Roles

```bash
# Remove a role
ansible-galaxy remove geerlingguy.nginx

# Remove from specific path
ansible-galaxy remove geerlingguy.nginx -p ./roles
```

---

## 🎭 Using Galaxy Roles

### Basic Usage

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: yes
  
  roles:
    - geerlingguy.nginx
```

### With Variables

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: yes
  
  vars:
    nginx_vhosts:
      - listen: "80"
        server_name: "example.com"
        root: "/var/www/html"
        index: "index.html"
  
  roles:
    - geerlingguy.nginx
```

### In requirements

```yaml
# playbook.yml
---
- name: Deploy LAMP stack
  hosts: webservers
  become: yes
  
  roles:
    - geerlingguy.apache
    - geerlingguy.mysql
    - geerlingguy.php
```

```bash
# Install dependencies
ansible-galaxy install -r requirements.yml

# Run playbook
ansible-playbook playbook.yml
```

---

## 📦 Collections

### What are Collections?

Collections bundle multiple content types:
- Roles
- Modules
- Plugins
- Documentation

### Installing Collections

```bash
# Install collection
ansible-galaxy collection install community.general

# Specific version
ansible-galaxy collection install community.general:==4.8.0

# From requirements
ansible-galaxy collection install -r requirements.yml
```

### Using Collections

```yaml
---
- name: Use collection modules
  hosts: all
  
  tasks:
    - name: Use docker module from collection
      community.docker.docker_container:
        name: myapp
        image: nginx:latest
        state: started
    
    - name: Use another collection module
      community.general.timezone:
        name: America/New_York
```

---

## 🚀 Creating Your Own Role

### Initialize Role Structure

```bash
# Create role
ansible-galaxy init my-role

# Create in specific directory
ansible-galaxy init --init-path roles/ my-role
```

### Role Metadata (meta/main.yml)

```yaml
---
galaxy_info:
  author: Your Name
  description: Description of your role
  company: Your Company (optional)
  
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
    - name: EL
      versions:
        - 7
        - 8
  
  galaxy_tags:
    - system
    - webserver
    - nginx
    - automation

dependencies: []
```

### README.md Template

```markdown
# Ansible Role: My Role

Brief description of what this role does.

## Requirements

- Ansible 2.9 or higher
- Supported platforms: Ubuntu 20.04+, Debian 10+

## Role Variables

Available variables with defaults (from `defaults/main.yml`):

```yaml
my_role_port: 8080
my_role_user: app
my_role_debug: false
```

## Dependencies

- geerlingguy.common (if needed)

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: username.my_role
      vars:
        my_role_port: 9000
```

## License

MIT

## Author Information

Created by [Your Name](https://github.com/username)
```

---

## 📤 Publishing to Galaxy

### Prerequisites

```bash
# Sign up at galaxy.ansible.com
# Link your GitHub account
# Create API token
```

### Prepare for Publishing

1. **Create GitHub repository**
```bash
# Repository name format
ansible-role-rolename
```

2. **Add required files**
```
ansible-role-myapp/
├── README.md          # Required
├── meta/
│   └── main.yml       # Required with galaxy_info
├── defaults/
│   └── main.yml
├── tasks/
│   └── main.yml
├── handlers/
│   └── main.yml
└── tests/
    └── test.yml
```

3. **Test locally**
```bash
# Test the role
ansible-playbook tests/test.yml

# Lint the role
ansible-lint .
```

### Import to Galaxy

```bash
# Option 1: Use Galaxy website
# - Login to galaxy.ansible.com
# - My Content > Add Content
# - Select GitHub repository

# Option 2: Use CLI
ansible-galaxy login
ansible-galaxy import username rolename
```

### Versioning

```bash
# Create git tags for versions
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0

# Galaxy will auto-import new versions
```

---

## 🎯 Best Practices

### Using Galaxy Roles

1. **Pin versions** in requirements.yml
```yaml
roles:
  - name: geerlingguy.nginx
    version: 2.8.0  # Don't use 'latest'
```

2. **Review before using**
```bash
# Check role quality
# - Downloads count
# - Star rating
# - Last updated date
# - Documentation quality
```

3. **Test in staging first**
```yaml
# Test role in isolated environment
- hosts: test-servers
  roles:
    - geerlingguy.nginx
```

4. **Override defaults carefully**
```yaml
# Document your overrides
vars:
  # Override: Use custom port
  nginx_port: 8080
  
  # Override: Disable SSL
  nginx_ssl: false
```

### Creating Galaxy Roles

1. **Clear documentation**
- Complete README
- All variables documented
- Usage examples
- Dependencies listed

2. **Semantic versioning**
- MAJOR.MINOR.PATCH
- v1.0.0, v1.1.0, v2.0.0

3. **Support multiple platforms**
```yaml
platforms:
  - name: Ubuntu
    versions: [focal, jammy]
  - name: Debian
    versions: [buster, bullseye]
```

4. **Meaningful tags**
```yaml
galaxy_tags:
  - webserver
  - nginx
  - http
  - ssl
```

5. **Include tests**
```yaml
# tests/test.yml
---
- hosts: localhost
  remote_user: root
  roles:
    - ansible-role-myapp
```

---

## 📚 Popular Roles

### Infrastructure

```yaml
# Web servers
- geerlingguy.nginx
- geerlingguy.apache

# Databases
- geerlingguy.mysql
- geerlingguy.postgresql
- geerlingguy.redis

# Languages
- geerlingguy.php
- geerlingguy.nodejs
- geerlingguy.python

# Tools
- geerlingguy.docker
- geerlingguy.jenkins
- geerlingguy.git
```

### Example requirements.yml

```yaml
---
roles:
  # Base system
  - name: geerlingguy.security
    version: 2.1.0
  
  - name: geerlingguy.firewall
    version: 2.7.0
  
  # Web stack
  - name: geerlingguy.nginx
    version: 2.8.0
  
  - name: geerlingguy.php
    version: 4.8.0
  
  # Database
  - name: geerlingguy.mysql
    version: 3.3.2
  
  # Caching
  - name: geerlingguy.redis
    version: 1.7.0
  
  # Tools
  - name: geerlingguy.git
    version: 3.1.0
  
  - name: geerlingguy.composer
    version: 1.9.1

collections:
  - name: community.general
  - name: community.mysql
  - name: community.postgresql
```

---

## 🔧 Configuration

### ansible.cfg

```ini
[defaults]
# Role path
roles_path = ./roles:/usr/share/ansible/roles

# Galaxy settings
[galaxy]
server = https://galaxy.ansible.com
ignore_certs = False

# Token file (optional)
token_path = ~/.ansible/galaxy_token
```

### Environment Variables

```bash
# Galaxy API token
export ANSIBLE_GALAXY_TOKEN="your_token_here"

# Server URL
export ANSIBLE_GALAXY_SERVER="https://galaxy.ansible.com"

# Role path
export ANSIBLE_ROLES_PATH="./roles:/usr/share/ansible/roles"
```

---

## 🛠️ Advanced Usage

### Private Galaxy Server

```yaml
# ansible.cfg
[galaxy]
server_list = release_galaxy, my_galaxy

[galaxy_server.release_galaxy]
url = https://galaxy.ansible.com

[galaxy_server.my_galaxy]
url = https://galaxy.mycompany.com
token = my_private_token
```

### Installing from Private Repos

```yaml
# requirements.yml
---
roles:
  - name: private-role
    src: git+ssh://git@github.com/company/private-role.git
    scm: git
    version: main
  
  - name: internal-role
    src: https://gitlab.company.com/ansible/roles/internal-role.git
    scm: git
    version: v1.2.0
```

### CI/CD Integration

```yaml
# .gitlab-ci.yml
install_roles:
  stage: prepare
  script:
    - ansible-galaxy install -r requirements.yml --force
  artifacts:
    paths:
      - roles/
    expire_in: 1 hour

deploy:
  stage: deploy
  dependencies:
    - install_roles
  script:
    - ansible-playbook -i inventory site.yml
```

---

## 🔍 Troubleshooting

### Common Issues

**Role not found:**
```bash
# Check installed roles
ansible-galaxy list

# Reinstall
ansible-galaxy install geerlingguy.nginx --force
```

**Version conflicts:**
```yaml
# Pin specific versions in requirements.yml
- name: geerlingguy.nginx
  version: "2.8.0"  # Exact version
```

**Permission errors:**
```bash
# Install to user directory
ansible-galaxy install geerlingguy.nginx -p ~/.ansible/roles

# Or update ansible.cfg
[defaults]
roles_path = ~/.ansible/roles:/usr/share/ansible/roles
```

---

## ✅ Summary

**Ansible Galaxy provides:**
- ✅ Thousands of community roles
- ✅ Easy role discovery and installation
- ✅ Version management
- ✅ Collections support
- ✅ Free hosting for open-source

**Best practices:**
1. Pin versions in requirements.yml
2. Review roles before using
3. Test in staging first
4. Document customizations
5. Contribute back to community

---

## 🔗 What's Next?

- **Next:** [Dynamic Inventory](15-dynamic-inventory.md)
- **Previous:** [Roles](13-roles.md)
- **Practice:** Publish your first role!

---

**Pro Tip:** Start with popular, well-maintained roles from trusted authors (like geerlingguy) before trying lesser-known roles!
