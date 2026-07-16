# Git Installation and Configuration

Complete guide to installing Git on any platform and configuring it for optimal use.

---

## Installation by Operating System

### Windows

**Option 1: Official Installer (Recommended)**

1. Download from: https://git-scm.com/download/win
2. Run the installer
3. Recommended settings:
   - ✅ Use Git from Git Bash only (safer for beginners)
   - ✅ Use OpenSSH
   - ✅ Use the OpenSSL library
   - ✅ Checkout Windows-style, commit Unix-style line endings
   - ✅ Use MinTTY terminal
   - ✅ Default (fast-forward or merge)

**Option 2: Package Manager**

```powershell
# Using Chocolatey
choco install git

# Using Winget
winget install --id Git.Git -e --source winget
```

**Verify Installation:**

```bash
git --version
# Output: git version 2.41.0
```

### macOS

**Option 1: Homebrew (Recommended)**

```bash
# Install Homebrew first if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Git
brew install git
```

**Option 2: Xcode Command Line Tools**

```bash
xcode-select --install
```

**Option 3: Official Installer**

Download from: https://git-scm.com/download/mac

**Verify Installation:**

```bash
git --version
# Output: git version 2.41.0
```

### Linux

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install git
```

**Fedora:**

```bash
sudo dnf install git
```

**Arch Linux:**

```bash
sudo pacman -S git
```

**From Source (Any Linux):**

```bash
# Install dependencies
sudo apt install build-essential libssl-dev libcurl4-gnutls-dev libexpat1-dev gettext unzip

# Download and compile
wget https://github.com/git/git/archive/v2.41.0.tar.gz
tar -zxf v2.41.0.tar.gz
cd git-2.41.0
make prefix=/usr/local all
sudo make prefix=/usr/local install
```

**Verify Installation:**

```bash
git --version
# Output: git version 2.41.0
```

---

## Initial Configuration

After installing Git, configure it with your identity. This is required before making commits.

### Essential Configuration

```bash
# Set your name (appears in commits)
git config --global user.name "Your Name"

# Set your email (appears in commits)
git config --global user.email "your.email@example.com"

# Set default branch name to 'main'
git config --global init.defaultBranch main
```

### Verify Configuration

```bash
# View all configuration
git config --list

# View specific settings
git config user.name
git config user.email
```

---

## Configuration Levels

Git has three levels of configuration:

### 1. System Level (All Users)

```bash
# Applies to all users on the system
git config --system user.name "System Name"

# Location: /etc/gitconfig (Linux/Mac) or C:\ProgramData\Git\config (Windows)
```

### 2. Global Level (Current User)

```bash
# Applies to all repositories for current user
git config --global user.name "Your Name"

# Location: ~/.gitconfig (Linux/Mac) or C:\Users\<username>\.gitconfig (Windows)
```

### 3. Local Level (Current Repository)

```bash
# Applies only to current repository
git config --local user.name "Project Specific Name"

# Location: .git/config in your repository
```

**Priority:** Local > Global > System

---

## Recommended Configuration

### Text Editor

Set your preferred text editor for commit messages:

```bash
# VS Code
git config --global core.editor "code --wait"

# Vim
git config --global core.editor "vim"

# Nano
git config --global core.editor "nano"

# Notepad (Windows)
git config --global core.editor "notepad"

# Sublime Text
git config --global core.editor "subl -n -w"
```

### Line Endings

**Windows:**
```bash
git config --global core.autocrlf true
```

**macOS/Linux:**
```bash
git config --global core.autocrlf input
```

### Color Output

```bash
# Enable colored output
git config --global color.ui auto
```

### Default Branch Name

```bash
# Use 'main' instead of 'master'
git config --global init.defaultBranch main
```

### Pull Behavior

```bash
# Use rebase when pulling (cleaner history)
git config --global pull.rebase false

# Or use merge (default, safer)
git config --global pull.ff only
```

---

## Complete Recommended Configuration

Run these commands for an optimal Git setup:

```bash
# Identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Editor
git config --global core.editor "code --wait"

# Default branch
git config --global init.defaultBranch main

# Line endings (choose based on OS)
git config --global core.autocrlf true      # Windows
# git config --global core.autocrlf input   # Mac/Linux

# Colors
git config --global color.ui auto

# Pull behavior
git config --global pull.rebase false

# Push behavior
git config --global push.default simple

# Credential helper (cache passwords)
git config --global credential.helper cache  # Linux/Mac
# git config --global credential.helper wincred  # Windows
```

---

## SSH Configuration (for GitHub/GitLab)

SSH allows you to connect to Git servers without entering passwords.

### Generate SSH Key

```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Press Enter to accept default location (~/.ssh/id_ed25519)
# Enter passphrase (optional but recommended)
```

### Add SSH Key to SSH Agent

**macOS/Linux:**
```bash
# Start SSH agent
eval "$(ssh-agent -s)"

# Add your key
ssh-add ~/.ssh/id_ed25519
```

**Windows:**
```powershell
# Start SSH agent service
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent

# Add your key
ssh-add ~/.ssh/id_ed25519
```

### Add SSH Key to GitHub/GitLab

```bash
# Copy public key to clipboard

# macOS
pbcopy < ~/.ssh/id_ed25519.pub

# Linux (with xclip)
xclip -selection clipboard < ~/.ssh/id_ed25519.pub

# Windows (Git Bash)
cat ~/.ssh/id_ed25519.pub | clip

# Or just display it and copy manually
cat ~/.ssh/id_ed25519.pub
```

Then:
1. Go to GitHub: Settings → SSH and GPG keys → New SSH key
2. Paste the key
3. Give it a descriptive title (e.g., "Work Laptop")
4. Click "Add SSH key"

### Test SSH Connection

```bash
# Test GitHub connection
ssh -T git@github.com
# Output: Hi username! You've successfully authenticated...

# Test GitLab connection
ssh -T git@gitlab.com
```

---

## Git Aliases (Shortcuts)

Create shortcuts for commonly used commands:

```bash
# Status
git config --global alias.st status

# Checkout
git config --global alias.co checkout

# Commit
git config --global alias.ci commit

# Branch
git config --global alias.br branch

# Pretty log
git config --global alias.lg "log --oneline --graph --all --decorate"

# Last commit
git config --global alias.last "log -1 HEAD"

# Unstage
git config --global alias.unstage "reset HEAD --"
```

Usage:
```bash
# Instead of 'git status'
git st

# Instead of 'git checkout main'
git co main

# Pretty log
git lg
```

---

## Configuration File

View and edit your configuration file directly:

```bash
# View configuration file
cat ~/.gitconfig

# Edit in default editor
git config --global --edit
```

Example `.gitconfig`:

```ini
[user]
    name = John Doe
    email = john.doe@example.com

[core]
    editor = code --wait
    autocrlf = true

[init]
    defaultBranch = main

[color]
    ui = auto

[alias]
    st = status
    co = checkout
    ci = commit
    br = branch
    lg = log --oneline --graph --all --decorate

[pull]
    rebase = false

[push]
    default = simple
```

---

## Git Credential Management

### Cache Credentials (Temporary)

```bash
# Cache for 15 minutes (900 seconds)
git config --global credential.helper 'cache --timeout=900'

# Cache for 1 hour (3600 seconds)
git config --global credential.helper 'cache --timeout=3600'
```

### Store Credentials (Permanent)

**Warning:** Stores passwords in plain text. Use SSH instead for better security.

```bash
# Store credentials (Linux/Mac)
git config --global credential.helper store

# Windows (uses Windows Credential Manager)
git config --global credential.helper wincred
```

---

## Troubleshooting Installation

### Check Installation Path

```bash
which git       # Linux/Mac
where git       # Windows
```

### Update Git

```bash
# macOS (Homebrew)
brew upgrade git

# Linux (Ubuntu/Debian)
sudo apt update && sudo apt upgrade git

# Windows
# Download and run latest installer from git-scm.com
```

### Configuration Not Working

```bash
# Check configuration location
git config --list --show-origin

# Clear specific config
git config --global --unset user.name

# Reset all global config
rm ~/.gitconfig
```

---

## Verification Checklist

After installation and configuration, verify everything:

```bash
# ✅ Git installed
git --version

# ✅ User configured
git config user.name
git config user.email

# ✅ Editor configured
git config core.editor

# ✅ SSH working (if using SSH)
ssh -T git@github.com

# ✅ Can create repo
mkdir test-repo && cd test-repo
git init
echo "# Test" > README.md
git add README.md
git commit -m "Test commit"
# Should work without errors

# Clean up
cd .. && rm -rf test-repo
```

---

## Platform-Specific Tips

### Windows

- Use **Git Bash** for Unix-like commands
- Or use **PowerShell** with PSReadLine
- Configure line endings properly
- Use Windows Credential Manager

### macOS

- Use Homebrew for easy updates
- macOS includes Git (but often outdated)
- Use Keychain for credential storage

### Linux

- Install from distribution package manager
- Usually most up-to-date on rolling distributions
- Use SSH for authentication

---

## Next Steps

Now that Git is installed and configured:

1. **Learn Basic Commands** → [Basic Git Commands](03-basic-commands.md)
2. **Understand Workflow** → [Git Workflow](04-git-workflow.md)
3. **Practice** → [First Repository Lab](../git-practice/lab-01-basics/)

---

## Quick Reference

```bash
# Installation verification
git --version

# Essential configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main

# View configuration
git config --list
git config --global --edit

# SSH setup
ssh-keygen -t ed25519 -C "your.email@example.com"
ssh-add ~/.ssh/id_ed25519
ssh -T git@github.com
```

---

**Previous:** [← What is Git](01-what-is-git.md) | **Next:** [Basic Git Commands →](03-basic-commands.md)
