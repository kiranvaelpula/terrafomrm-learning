# Working with Remote Repositories

Master remote repositories to collaborate with teams, backup your code, and leverage platforms like GitHub, GitLab, and Bitbucket.

---

## Overview

Remote repositories are versions of your project hosted on the internet or network. They enable collaboration, serve as backups, and integrate with CI/CD pipelines. Understanding remotes is essential for modern development workflows.

**What you'll learn:**
- Understanding remote repositories
- Cloning and connecting to remotes
- Pushing and pulling changes
- Managing remote branches
- Working with GitHub/GitLab/Bitbucket

---

## What is a Remote Repository?

A remote repository is a Git repository hosted on a server (GitHub, GitLab, Bitbucket, or your own server) that multiple people can access.

### Local vs Remote

```
Your Computer (Local)          Server (Remote)
┌────────────────────┐        ┌────────────────────┐
│   Local Repo       │◄──────►│  Remote Repo       │
│   - Working Dir    │  push  │  - Main branch     │
│   - Staging Area   │  pull  │  - Feature branch  │
│   - Git Directory  │  fetch │  - Full history    │
└────────────────────┘        └────────────────────┘
```

### Why Use Remotes?

**1. Collaboration**
- Multiple developers work on same project
- Share code changes easily
- Review each other's work

**2. Backup**
- Code is safe on remote server
- Recover from local disasters
- Access from multiple machines

**3. CI/CD Integration**
- Automatic testing on push
- Automatic deployment
- Code quality checks

**4. Code Review**
- Pull requests / Merge requests
- Team reviews before merging
- Discussion on code changes

---

## Remote Repository Basics

### Viewing Remotes

```bash
# List remotes
git remote

# List remotes with URLs
git remote -v

# Show remote details
git remote show origin
```

**Example output:**
```bash
$ git remote -v
origin  https://github.com/user/repo.git (fetch)
origin  https://github.com/user/repo.git (push)
```

### Adding a Remote

```bash
# Add remote
git remote add <name> <url>

# Common usage
git remote add origin https://github.com/user/repo.git

# Add multiple remotes
git remote add upstream https://github.com/original/repo.git
git remote add backup https://gitlab.com/user/repo.git
```

### Renaming a Remote

```bash
# Rename remote
git remote rename <old-name> <new-name>

# Example
git remote rename origin upstream
```

### Removing a Remote

```bash
# Remove remote
git remote remove <name>
git remote rm <name>

# Example
git remote remove backup
```

### Changing Remote URL

```bash
# Change URL
git remote set-url <name> <new-url>

# Example: Switch from HTTPS to SSH
git remote set-url origin git@github.com:user/repo.git

# View change
git remote -v
```

---

## Cloning Repositories

### git clone

Download a complete copy of a remote repository.

```bash
# Clone repository
git clone <url>

# Clone to specific directory
git clone <url> <directory-name>

# Clone specific branch
git clone -b <branch> <url>

# Shallow clone (recent history only)
git clone --depth 1 <url>

# Clone without checkout
git clone --no-checkout <url>
```

**Examples:**

```bash
# HTTPS clone
git clone https://github.com/user/repo.git

# SSH clone
git clone git@github.com:user/repo.git

# Clone to custom directory
git clone https://github.com/user/repo.git my-project

# Clone only main branch
git clone -b main --single-branch https://github.com/user/repo.git

# Fast clone (last commit only)
git clone --depth 1 https://github.com/user/huge-repo.git
```

**What clone does:**
1. Creates directory
2. Initializes `.git`
3. Downloads all data
4. Checks out main branch
5. Sets up "origin" remote

---

## Fetching and Pulling

### git fetch

Download changes from remote without merging.

```bash
# Fetch from origin
git fetch

# Fetch from specific remote
git fetch origin

# Fetch specific branch
git fetch origin main

# Fetch all remotes
git fetch --all

# Fetch and prune (remove deleted remote branches)
git fetch --prune
git fetch -p
```

**What fetch does:**
```
Remote:     A---B---C---D---E
                         ↓
Local:      A---B---C
            ↓ fetch downloads D and E
Local:      A---B---C
                    \
origin/main:         D---E (tracked but not merged)
```

**Example:**
```bash
$ git fetch origin
remote: Counting objects: 5, done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 5 (delta 2), reused 0 (delta 0)
Unpacking objects: 100% (5/5), done.
From https://github.com/user/repo
   a3f8d92..b4e9c83  main     -> origin/main

# View fetched changes
$ git log origin/main --oneline
b4e9c83 Latest remote commit
a3f8d92 My last commit
```

### git pull

Fetch and merge changes in one command.

```bash
# Pull from current branch's remote
git pull

# Pull from specific remote and branch
git pull origin main

# Pull with rebase instead of merge
git pull --rebase

# Pull from specific remote
git pull upstream main

# Pull all branches
git pull --all
```

**What pull does:**
```bash
# git pull is equivalent to:
git fetch
git merge origin/main
```

**Example:**
```bash
$ git pull origin main
From https://github.com/user/repo
 * branch            main       -> FETCH_HEAD
Updating a3f8d92..b4e9c83
Fast-forward
 file.txt | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

### Fetch vs Pull

| Feature | git fetch | git pull |
|---------|-----------|----------|
| **Download** | ✅ Yes | ✅ Yes |
| **Merge** | ❌ No | ✅ Yes |
| **Safe** | ✅ Always | ⚠️ Can conflict |
| **When** | To review first | To integrate immediately |

**Best practice:**
```bash
# ✅ Safe: Review before merging
git fetch origin
git log origin/main --oneline
git diff main origin/main
git merge origin/main

# ⚠️ Quick but risky
git pull origin main
```

---

## Pushing Changes

### git push

Upload local commits to remote repository.

```bash
# Push to origin (current branch)
git push

# Push to specific remote and branch
git push origin main

# Push and set upstream
git push -u origin feature-branch
git push --set-upstream origin feature-branch

# Push all branches
git push --all

# Push tags
git push --tags

# Force push (dangerous!)
git push --force
git push -f

# Force push safely (with lease)
git push --force-with-lease
```

**Examples:**

```bash
# First push of new branch
$ git checkout -b feature/new-ui
$ git commit -am "Add new UI"
$ git push -u origin feature/new-ui
# Now 'git push' will automatically push to origin/feature/new-ui

# Regular push
$ git commit -am "Update UI colors"
$ git push
# Pushes to configured upstream

# Push different branch
$ git push origin develop

# Push and create remote branch
$ git checkout -b hotfix/bug-123
$ git commit -am "Fix critical bug"
$ git push -u origin hotfix/bug-123
```

### Push Errors and Solutions

**Error: Non-fast-forward**
```bash
$ git push origin main
! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs

# Solution: Pull first
$ git pull origin main
$ git push origin main
```

**Error: Diverged histories**
```bash
# Solution 1: Merge
$ git pull origin main
# Resolve conflicts if any
$ git push origin main

# Solution 2: Rebase
$ git pull --rebase origin main
# Resolve conflicts if any
$ git push origin main
```

**Force Push (Use Carefully!)**
```bash
# ⚠️ Overwrites remote history
git push --force origin main

# ✅ Safer: Only push if remote hasn't changed
git push --force-with-lease origin main
```

---

## Working with Remote Branches

### Viewing Remote Branches

```bash
# List remote branches
git branch -r

# List all branches (local and remote)
git branch -a

# View remote branch details
git remote show origin
```

**Example output:**
```bash
$ git branch -a
* main
  feature/login
  remotes/origin/main
  remotes/origin/feature/login
  remotes/origin/develop
```

### Tracking Remote Branches

```bash
# Create local branch tracking remote
git checkout -b local-name origin/remote-name

# Shorter syntax (same name)
git checkout --track origin/feature-branch
git checkout feature-branch  # Auto-tracks if name matches

# Set existing branch to track remote
git branch -u origin/main
git branch --set-upstream-to=origin/main
```

**Example:**
```bash
# Remote branch exists: origin/feature/dashboard
$ git checkout --track origin/feature/dashboard
Branch 'feature/dashboard' set up to track remote branch 'feature/dashboard' from 'origin'.
Switched to a new branch 'feature/dashboard'

# Now you can just use 'git push' and 'git pull'
```

### Deleting Remote Branches

```bash
# Delete remote branch
git push origin --delete branch-name
git push origin :branch-name  # Old syntax

# Delete local reference to remote branch
git branch -dr origin/branch-name
```

**Example:**
```bash
# Delete feature branch after merge
$ git push origin --delete feature/old-feature
To https://github.com/user/repo.git
 - [deleted]         feature/old-feature

# Clean up local reference
$ git fetch --prune
```

---

## Common Remote Workflows

### Workflow 1: Contributing to Open Source

```bash
# 1. Fork repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOU/repo.git
cd repo

# 3. Add upstream remote
git remote add upstream https://github.com/ORIGINAL/repo.git

# 4. Create feature branch
git checkout -b feature/my-contribution

# 5. Make changes and commit
git add .
git commit -m "Add awesome feature"

# 6. Push to your fork
git push origin feature/my-contribution

# 7. Create pull request on GitHub

# 8. Keep your fork updated
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

### Workflow 2: Team Development

```bash
# Morning: Get latest code
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/user-dashboard

# Work on feature
git add .
git commit -m "Add dashboard layout"
git push -u origin feature/user-dashboard

# Continue throughout day
# ... make changes ...
git commit -am "Add dashboard widgets"
git push  # Pushes to origin/feature/user-dashboard

# End of day
git push

# Next day: Continue work
git pull  # Get any updates from remote
# ... continue working ...
```

### Workflow 3: Syncing Fork with Upstream

```bash
# Setup (once)
git remote add upstream https://github.com/original/repo.git

# Regular sync
git fetch upstream
git checkout main
git merge upstream/main
git push origin main

# Or use rebase
git fetch upstream
git rebase upstream/main
git push origin main
```

---

## Authentication Methods

### HTTPS Authentication

**Basic method:**
```bash
git clone https://github.com/user/repo.git
# Prompts for username and password/token
```

**Cache credentials:**
```bash
# Cache for 15 minutes
git config --global credential.helper 'cache --timeout=900'

# Store permanently (less secure)
git config --global credential.helper store

# Windows: Use Windows Credential Manager
git config --global credential.helper wincred

# macOS: Use Keychain
git config --global credential.helper osxkeychain
```

**Personal Access Token (PAT):**
```bash
# GitHub requires PAT instead of password
# Generate at: GitHub → Settings → Developer settings → Personal access tokens

# Use PAT as password when prompted
Username: your-username
Password: ghp_xxxxxxxxxxxxxxxxxxxx
```

### SSH Authentication

**Generate SSH key:**
```bash
# Generate key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Start SSH agent
eval "$(ssh-agent -s)"

# Add key to agent
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub
# Add to GitHub: Settings → SSH and GPG keys
```

**Use SSH URL:**
```bash
# Clone with SSH
git clone git@github.com:user/repo.git

# Change existing repository to SSH
git remote set-url origin git@github.com:user/repo.git
```

**Test connection:**
```bash
# GitHub
ssh -T git@github.com

# GitLab
ssh -T git@gitlab.com

# Bitbucket
ssh -T git@bitbucket.org
```

---

## Multiple Remotes

### Use Cases for Multiple Remotes

**1. Fork workflow**
```bash
origin    → Your fork
upstream  → Original repository
```

**2. Multiple deployment targets**
```bash
origin    → Main repository
staging   → Staging server
production → Production server
```

**3. Mirror repositories**
```bash
github    → GitHub mirror
gitlab    → GitLab mirror
bitbucket → Bitbucket mirror
```

### Managing Multiple Remotes

```bash
# Add multiple remotes
git remote add origin https://github.com/user/repo.git
git remote add gitlab https://gitlab.com/user/repo.git
git remote add bitbucket https://bitbucket.org/user/repo.git

# View all remotes
git remote -v

# Fetch from all
git fetch --all

# Push to specific remote
git push github main
git push gitlab main
git push bitbucket main

# Push to all remotes
git remote | xargs -L1 git push --all
```

---

## Best Practices

### 1. Pull Before Push

```bash
# ✅ Good: Avoid conflicts
git pull origin main
git push origin main

# ❌ Bad: Push without pulling
git push origin main
# ERROR: Updates were rejected...
```

### 2. Use Branches for Features

```bash
# ✅ Good: Feature branches
git checkout -b feature/new-feature
git push -u origin feature/new-feature

# ❌ Bad: Work on main directly
git checkout main
# ... make changes ...
git push origin main
```

### 3. Meaningful Push Messages

```bash
# Ensure commits have clear messages
git log --oneline  # Review before pushing

# If needed, amend last commit
git commit --amend -m "Better message"
git push --force-with-lease
```

### 4. Regularly Fetch Updates

```bash
# Daily routine
git fetch origin
git status  # Check if behind

# Or set up alias
git config --global alias.sync '!git fetch --all && git status'
git sync
```

### 5. Clean Up Old Branches

```bash
# Delete local merged branches
git branch --merged | grep -v "\*" | xargs -n 1 git branch -d

# Delete remote branches
git push origin --delete old-feature

# Prune remote references
git fetch --prune
```

---

## Common Pitfalls

### Pitfall 1: Pushing Secrets

```bash
# ❌ Problem: Committed API key
git add .env
git commit -m "Add config"
git push origin main  # Oops! Secret is public

# ✅ Solution: Use .gitignore
echo ".env" >> .gitignore
git rm --cached .env
git commit -m "Remove secrets"
git push origin main

# Rotate compromised secrets!
```

### Pitfall 2: Force Pushing Shared Branches

```bash
# ❌ Problem: Force push to shared branch
git push --force origin main  # Everyone else's work is lost!

# ✅ Solution: Never force push shared branches
# Or use --force-with-lease
git push --force-with-lease origin main
```

### Pitfall 3: Not Setting Upstream

```bash
# ❌ Problem
git push
# fatal: The current branch has no upstream branch

# ✅ Solution
git push -u origin feature-branch
# Now 'git push' works
```

### Pitfall 4: Wrong Remote

```bash
# ❌ Problem: Pushing to wrong remote
git push upstream main  # Error! No write access

# ✅ Solution: Check remotes
git remote -v
git push origin main
```

---

## Real-World Scenarios

### Scenario 1: Collaborating on Feature

```bash
# Developer A
git checkout -b feature/new-api
git commit -am "Add API endpoint"
git push -u origin feature/new-api

# Developer B
git fetch origin
git checkout feature/new-api
git commit -am "Add API tests"
git push origin feature/new-api

# Developer A
git pull origin feature/new-api
# See Developer B's tests
```

### Scenario 2: Emergency Hotfix

```bash
# Production bug discovered!
git checkout main
git pull origin main

# Create hotfix
git checkout -b hotfix/critical-bug
# ... fix bug ...
git commit -am "Fix critical security vulnerability"

# Push immediately
git push -u origin hotfix/critical-bug

# Create PR for quick review and merge
# After merge:
git checkout main
git pull origin main
git branch -d hotfix/critical-bug
```

### Scenario 3: Syncing Multiple Repositories

```bash
# Push to multiple hosting services
git push github main
git push gitlab main

# Or create script
#!/bin/bash
for remote in github gitlab bitbucket; do
  git push $remote main
done
```

---

## Hands-On Exercise

### Exercise 1: Basic Remote Operations

```bash
# 1. Create local repository
mkdir remote-practice
cd remote-practice
git init
echo "# Remote Practice" > README.md
git add README.md
git commit -m "Initial commit"

# 2. Create repository on GitHub (via web interface)

# 3. Add remote
git remote add origin https://github.com/YOUR-USERNAME/remote-practice.git

# 4. Push to remote
git push -u origin main

# 5. Make change locally
echo "## Changes" >> README.md
git commit -am "Add changes section"
git push

# 6. Make change on GitHub (via web interface)

# 7. Pull changes
git pull origin main

# 8. View history
git log --oneline --graph
```

### Exercise 2: Working with Branches

```bash
# 1. Create and push feature branch
git checkout -b feature/add-content
echo "Content" > content.txt
git add content.txt
git commit -m "Add content file"
git push -u origin feature/add-content

# 2. Create another branch
git checkout -b feature/add-styles
echo "body { margin: 0; }" > styles.css
git add styles.css
git commit -m "Add styles"
git push -u origin feature/add-styles

# 3. Merge first feature
git checkout main
git merge feature/add-content
git push origin main

# 4. Delete merged branch
git branch -d feature/add-content
git push origin --delete feature/add-content

# 5. View all branches
git branch -a
```

---

## Interview Tips

**What is a remote repository?**
> A remote repository is a version of your project hosted on a network server (like GitHub) that multiple developers can access for collaboration, serving as a central point for sharing code and as a backup.

**Difference between fetch and pull?**
> `git fetch` downloads changes from remote but doesn't merge them, letting you review first. `git pull` does fetch and merge in one command. Fetch is safer for reviewing changes before integration.

**How do you resolve push rejection?**
> Pull the latest changes with `git pull`, resolve any conflicts, and then push again. The rejection occurs when the remote has commits your local repository doesn't have.

**What is origin?**
> Origin is the default name for the remote repository from which you cloned. It's just a conventional naming alias for the remote URL, and you can have multiple remotes with different names.

**Explain force push and when to use it**
> Force push (`--force`) overwrites the remote branch with your local version, discarding remote commits. Use it only on your own branches or with `--force-with-lease` to avoid overwriting others' work. Never force push shared branches.

---

## Quick Reference

```bash
# Viewing remotes
git remote -v
git remote show origin

# Managing remotes
git remote add <name> <url>
git remote remove <name>
git remote rename <old> <new>
git remote set-url <name> <url>

# Cloning
git clone <url>
git clone <url> <directory>

# Fetching
git fetch
git fetch origin
git fetch --all

# Pulling
git pull
git pull origin main
git pull --rebase

# Pushing
git push
git push -u origin branch
git push --all
git push --tags

# Remote branches
git branch -r
git branch -a
git push origin --delete branch
```

---

**Previous:** [← Git Workflow](04-git-workflow.md) | **Next:** [Interview Questions →](interview-questions-basics.md)
