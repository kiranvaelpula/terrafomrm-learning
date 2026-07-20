# Installation & Setup

> **Get Ansible running in 5 minutes and configure your first control node**

---

## 📖 Overview

Installing Ansible is straightforward - it's a **Python package** that runs on your control node (your workstation or a dedicated server). No agents needed on managed hosts!

**Requirements:**
- Python 3.8+ (Python 2.7+ for older versions)
- SSH access to target systems
- Linux, macOS, or WSL2 on Windows

**Installation Time:** 5-10 minutes  
**Difficulty:** Easy

---

## 🚀 Quick Installation

### Ubuntu/Debian

```bash
# Update package index
sudo apt update

# Install Ansible
sudo apt install ansible -y

# Verify installation
ansible --version
```

**Output:**
```yaml
ansible [core 2.14.3]
  config file = /etc/ansible/ansible.cfg
  configured module search path = ['/home/user/.ansible/plugins/modules']
  ansible python module location = /usr/lib/python3/dist-packages/ansible
  ansible collection location = /home/user/.ansible/collections
  executable location = /usr/bin/ansible
  python version = 3.10.6
```

### RHEL/CentOS/Fedora

```bash
# Enable EPEL repository (RHEL/CentOS)
sudo yum install epel-release -y

# Install Ansible
sudo yum install ansible -y

# Or for Fedora
sudo dnf install ansible -y

# Verify
ansible --version
```

### macOS

```bash
# Using Homebrew (recommended)
brew install ansible

# Or using pip
pip3 install ansible

# Verify
ansible --version
```

### pip (All Platforms)

```bash
# Install via pip (latest version)
pip3 install ansible

# Or install specific version
pip3 install ansible==2.14.3

# Install in virtual environment (recommended)
python3 -m venv ansible-venv
source ansible-venv/bin/activate
pip install ansible

# Verify
ansible --version
```

### Windows (WSL2)

```bash
# Install WSL2 first (PowerShell as Admin)
wsl --install

# In WSL2 Ubuntu
sudo apt update
sudo apt install ansible -y

# Verify
ansible --version
```

---

## 🔧 Installation Methods Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **apt/yum** | Simple, managed updates | Older version | Production servers |
| **pip** | Latest version, virtual env | Manual management | Dev workstations |
| **Homebrew** | macOS native, easy updates | macOS only | Mac developers |
| **Source** | Cutting-edge features | Complex, unstable | Testing, development |

**Recommendation:** Use `apt`/`yum` for servers, `pip` in virtualenv for workstations.

---

## 📁 Directory Structure

### Default Ansible Structure

```
/etc/ansible/              # System-wide configuration
├── ansible.cfg           # Main configuration file
├── hosts                 # Default inventory file
└── roles/               # System-wide roles

~/.ansible/               # User-level
├── collections/         # Downloaded collections
├── roles/              # User roles
└── tmp/                # Temporary files

~/ansible/              # Your project (recommended)
├── ansible.cfg        # Project configuration
├── inventory/         # Inventory files
│   ├── production    # Production hosts
│   ├── staging       # Staging hosts
│   └── development   # Dev hosts
├── group_vars/       # Group variables
├── host_vars/        # Host-specific variables
├── roles/            # Custom roles
├── playbooks/        # Your playbooks
└── library/          # Custom modules (optional)
```

### Creating Your Project

```bash
# Create project directory
mkdir -p ~/ansible-project
cd ~/ansible-project

# Create structure
mkdir -p {inventory,group_vars,host_vars,roles,playbooks}

# Create basic files
touch ansible.cfg
touch inventory/hosts

echo "Project structure created!"
tree
```

---

## ⚙️ Configuration (ansible.cfg)

### Configuration Precedence

Ansible looks for configuration in this order:
1. `ANSIBLE_CONFIG` environment variable
2. `./ansible.cfg` (current directory) ⭐ **Recommended**
3. `~/.ansible.cfg` (home directory)
4. `/etc/ansible/ansible.cfg` (system-wide)

### Basic Configuration

**Create `ansible.cfg` in your project:**

```ini
[defaults]
# Inventory file location
inventory = ./inventory/hosts

# Don't check SSH host keys (dev only!)
host_key_checking = False

# Number of parallel processes
forks = 10

# SSH timeout
timeout = 30

# Display output in readable format
stdout_callback = yaml

# Enable color output
ansible_force_color = True

# Retry files location
retry_files_enabled = False

# Roles path
roles_path = ./roles:/etc/ansible/roles

[privilege_escalation]
# Become (sudo) settings
become = False
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
# SSH settings
pipelining = True
control_path = /tmp/ansible-%%h-%%p-%%r
```

### Production-Ready Configuration

```ini
[defaults]
inventory = ./inventory/production
host_key_checking = True  # Enable for security
forks = 20  # More parallelism
timeout = 60
vault_password_file = ~/.ansible-vault-pass
log_path = ./logs/ansible.log
retry_files_enabled = True
retry_files_save_path = ./retry

# Callback plugins for better output
stdout_callback = yaml
callback_whitelist = timer, profile_tasks

# Connection settings
remote_user = ansible
private_key_file = ~/.ssh/ansible_key

[privilege_escalation]
become = True
become_method = sudo
become_user = root

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s

[colors]
# Customize output colors
highlight = white
verbose = blue
warn = bright purple
error = red
debug = dark gray
deprecate = purple
skip = cyan
unreachable = red
ok = green
changed = yellow
diff_add = green
diff_remove = red
diff_lines = cyan
```

---

## 🎯 SSH Setup for Ansible

### SSH Key Generation

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "ansible-automation" -f ~/.ssh/ansible_key

# Or RSA (if ed25519 not supported)
ssh-keygen -t rsa -b 4096 -C "ansible-automation" -f ~/.ssh/ansible_rsa

# Set proper permissions
chmod 600 ~/.ssh/ansible_key
chmod 644 ~/.ssh/ansible_key.pub
```

### Copy SSH Key to Managed Nodes

**Method 1: ssh-copy-id (Easiest)**
```bash
# Copy to single host
ssh-copy-id -i ~/.ssh/ansible_key.pub user@server1.example.com

# Copy to multiple hosts
for host in server{1..5}.example.com; do
    ssh-copy-id -i ~/.ssh/ansible_key.pub user@$host
done
```

**Method 2: Manual Copy**
```bash
# On control node
cat ~/.ssh/ansible_key.pub

# On managed node
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "PASTE_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**Method 3: Using Password (One-Time)**
```bash
# Test connection with password
ansible all -i 'server1.example.com,' -m ping \
    --ask-pass --user=yourusername

# Copy SSH keys via playbook
ansible-playbook setup-ssh-keys.yml --ask-pass
```

### SSH Configuration (~/.ssh/config)

```bash
# Simplify SSH connections
cat >> ~/.ssh/config << 'EOF'

# Ansible managed hosts
Host ansible-*
    User ansible
    IdentityFile ~/.ssh/ansible_key
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null

# Production servers
Host prod-*
    User ansible
    IdentityFile ~/.ssh/ansible_key
    ForwardAgent no
    
# Bastion/Jump host
Host bastion.example.com
    User ansible
    IdentityFile ~/.ssh/bastion_key

# Servers via bastion
Host 10.0.*.*
    ProxyJump bastion.example.com
    User ansible
    IdentityFile ~/.ssh/ansible_key
EOF

chmod 600 ~/.ssh/config
```

---

## 🧪 Verify Installation

### Test 1: Version Check

```bash
# Check Ansible version
ansible --version

# Check Python version
python3 --version

# Check pip packages
pip3 list | grep ansible
```

**Expected Output:**
```
ansible                  2.14.3
ansible-core             2.14.3
```

### Test 2: Localhost Ping

```bash
# Test Ansible can run
ansible localhost -m ping

# Expected output
localhost | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

### Test 3: Ad-hoc Command

```bash
# Run command on localhost
ansible localhost -m command -a "date"

# Expected output
localhost | CHANGED | rc=0 >>
Mon Jul 20 10:30:45 UTC 2026
```

### Test 4: Check Configuration

```bash
# Show current configuration
ansible-config dump

# Show specific settings
ansible-config dump | grep -i inventory

# Validate configuration
ansible-config view
```

---

## 🔐 Sudo/Privilege Escalation Setup

### Configure Passwordless Sudo on Managed Nodes

**On each managed node:**

```bash
# Create ansible user
sudo useradd -m -s /bin/bash ansible

# Set password (initial setup)
sudo passwd ansible

# Add to sudoers
echo "ansible ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ansible

# Set permissions
sudo chmod 0440 /etc/sudoers.d/ansible

# Test
sudo -u ansible sudo whoami  # Should output: root
```

### Test Privilege Escalation

```bash
# Test without sudo
ansible localhost -m command -a "whoami"
# Output: your_username

# Test with sudo
ansible localhost -b -m command -a "whoami"
# Output: root

# Test with different user
ansible localhost -b --become-user=postgres -m command -a "whoami"
# Output: postgres
```

---

## 📦 Installing Collections & Roles

### Ansible Collections

**What are collections?** Packaged content including modules, plugins, roles, and playbooks.

```bash
# List installed collections
ansible-galaxy collection list

# Install collection from Ansible Galaxy
ansible-galaxy collection install community.general

# Install specific version
ansible-galaxy collection install community.general:5.8.0

# Install from requirements file
cat > requirements.yml << 'EOF'
collections:
  - name: community.general
    version: ">=5.0.0"
  - name: ansible.posix
  - name: community.docker
    version: "3.4.0"
EOF

ansible-galaxy collection install -r requirements.yml

# Install to specific path
ansible-galaxy collection install community.general \
    -p ./collections
```

### Ansible Roles from Galaxy

```bash
# Search for roles
ansible-galaxy search nginx

# Install role
ansible-galaxy install geerlingguy.nginx

# Install specific version
ansible-galaxy install geerlingguy.nginx,3.1.4

# Install from requirements
cat > requirements.yml << 'EOF'
roles:
  - name: geerlingguy.nginx
    version: 3.1.4
  - src: https://github.com/username/ansible-role-example
    name: custom-role
EOF

ansible-galaxy install -r requirements.yml

# List installed roles
ansible-galaxy list
```

---

## 🎯 Environment-Specific Setup

### Development Environment

```ini
# dev-ansible.cfg
[defaults]
inventory = ./inventory/dev
host_key_checking = False
retry_files_enabled = False
forks = 5

[privilege_escalation]
become = False  # Usually not needed in dev
```

### Production Environment

```ini
# prod-ansible.cfg
[defaults]
inventory = ./inventory/production
host_key_checking = True  # Security!
vault_password_file = ~/.ansible-vault-pass
log_path = /var/log/ansible/ansible.log
retry_files_enabled = True
forks = 50  # More parallelism

[privilege_escalation]
become = True
become_method = sudo

[ssh_connection]
pipelining = True
control_path = /tmp/ansible-%%h-%%r
```

**Usage:**
```bash
# Use dev config
ANSIBLE_CONFIG=dev-ansible.cfg ansible-playbook site.yml

# Use prod config
ANSIBLE_CONFIG=prod-ansible.cfg ansible-playbook site.yml
```

---

## 🔍 Troubleshooting

### Issue 1: "command not found: ansible"

**Solution:**
```bash
# Check if installed
which ansible

# If using pip, check PATH
echo $PATH

# Add to PATH (add to ~/.bashrc)
export PATH="$PATH:$HOME/.local/bin"
source ~/.bashrc
```

### Issue 2: SSH Connection Fails

**Solution:**
```bash
# Test SSH manually first
ssh -i ~/.ssh/ansible_key user@target-host

# Common issues:
# 1. Wrong permissions
chmod 600 ~/.ssh/ansible_key

# 2. SSH key not copied
ssh-copy-id -i ~/.ssh/ansible_key.pub user@target-host

# 3. Wrong user
ansible all -m ping -u correct-username

# Verbose output for debugging
ansible all -m ping -vvv
```

### Issue 3: Permission Denied (sudo)

**Solution:**
```bash
# Test sudo access
ssh user@target-host "sudo whoami"

# If password required, use --ask-become-pass
ansible all -m ping -b --ask-become-pass

# Configure passwordless sudo (see above)
echo "user ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/user
```

### Issue 4: Python Not Found

**Solution:**
```bash
# Specify Python interpreter
ansible all -m ping -e "ansible_python_interpreter=/usr/bin/python3"

# Or in inventory
[webservers]
server1 ansible_python_interpreter=/usr/bin/python3

# Or in group_vars
# group_vars/all.yml
ansible_python_interpreter: /usr/bin/python3
```

### Issue 5: Slow Performance

**Solution:**
```ini
# ansible.cfg optimizations
[defaults]
forks = 20  # Increase parallelism

[ssh_connection]
pipelining = True  # Reduce SSH connections
control_path = /tmp/ansible-%%h-%%r
```

---

## ✅ Installation Checklist

**Complete these steps to verify setup:**

- [ ] Ansible installed (`ansible --version` works)
- [ ] Python 3.8+ available
- [ ] SSH keys generated
- [ ] SSH keys copied to managed nodes
- [ ] Passwordless SSH working
- [ ] `ansible.cfg` created
- [ ] Inventory file created (covered in next lesson)
- [ ] Sudo/privilege escalation configured
- [ ] Localhost ping successful
- [ ] Collections/roles installed (if needed)

**Test command:**
```bash
ansible localhost -m ping && echo "✅ Ansible ready!"
```

---

## 🚀 Next Steps

Now that Ansible is installed and configured, you're ready to:

1. **Create your inventory** → [Next: Inventory & Ad-hoc Commands](03-inventory-adhoc.md)
2. **Run your first commands**
3. **Write your first playbook**

**Quick Test:**
```bash
# Create simple inventory
echo "localhost ansible_connection=local" > inventory/hosts

# Test
ansible -i inventory/hosts localhost -m ping

# You're ready! 🎉
```

---

## 📚 Additional Resources

### Official Documentation
- [Ansible Installation Guide](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
- [Configuration Settings](https://docs.ansible.com/ansible/latest/reference_appendices/config.html)
- [SSH Configuration](https://docs.ansible.com/ansible/latest/user_guide/connection_details.html)

### Useful Commands Reference

```bash
# Version and info
ansible --version
ansible-config dump
ansible-config view
ansible-doc -l  # List all modules

# Galaxy
ansible-galaxy collection list
ansible-galaxy role list
ansible-galaxy search nginx

# Testing
ansible localhost -m ping
ansible localhost -m setup  # Gather facts
ansible localhost -m command -a "uptime"
```

---

## 💡 Best Practices

1. **Use Virtual Environments:** Keep Ansible isolated per project
2. **Project-Level Config:** Store `ansible.cfg` in project root
3. **SSH Keys:** Use dedicated key for Ansible automation
4. **Passwordless Sudo:** Essential for automation
5. **Version Control:** Store configuration in Git (except secrets!)
6. **Separate Environments:** Different configs for dev/staging/prod
7. **Documentation:** Document your setup and configuration choices

---

## 🎓 Interview Questions

### Q1: Why doesn't Ansible require agents on managed nodes?
**A:** Ansible uses SSH (or WinRM) to connect to nodes and execute Python modules. It copies modules over SSH, executes them, and retrieves results. This agentless architecture means:
- No daemon processes to maintain
- Lower security surface area
- Simpler setup and management
- Only requires SSH access

### Q2: What's the difference between ansible and ansible-core?
**A:** 
- **ansible-core:** Minimal package with core Ansible functionality, basic modules, and plugins
- **ansible:** Full package including ansible-core plus community collections with 1000+ modules
- Most users want `ansible` (full package)

### Q3: What's the configuration precedence order?
**A:** Highest to lowest priority:
1. Command-line options (`-i`, `-u`, etc.)
2. Environment variables (`ANSIBLE_CONFIG`, `ANSIBLE_INVENTORY`)
3. `./ansible.cfg` (current directory) ⭐ Recommended
4. `~/.ansible.cfg` (user home)
5. `/etc/ansible/ansible.cfg` (system-wide)

### Q4: How do you handle multiple environments (dev/staging/prod)?
**A:** Best practices:
```bash
project/
├── ansible.cfg  # Default/dev
├── prod-ansible.cfg  # Production
├── inventory/
│   ├── dev/
│   ├── staging/
│   └── production/

# Usage
ANSIBLE_CONFIG=prod-ansible.cfg ansible-playbook site.yml
```

### Q5: What's SSH pipelining and why enable it?
**A:** SSH pipelining reduces the number of SSH connections needed by sending multiple commands in one connection. Benefits:
- Faster execution (30-50% speed improvement)
- Fewer SSH handshakes
- Lower network overhead

Enable in `ansible.cfg`:
```ini
[ssh_connection]
pipelining = True
```

**Note:** Requires `requiretty` to be disabled in sudoers.

---

**Status:** Installation Complete ✅  
**Next:** [Inventory & Ad-hoc Commands →](03-inventory-adhoc.md)

**Time Invested:** 10-15 minutes  
**Skill Gained:** Ansible installation & configuration mastery
