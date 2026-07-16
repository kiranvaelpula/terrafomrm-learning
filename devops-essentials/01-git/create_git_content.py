#!/usr/bin/env python3
"""
Generate comprehensive Git learning content for all remaining topics.
This script creates full content for basics, intermediate, and advanced Git topics.
"""

import os
from pathlib import Path

def create_basic_commands_content():
    """Create comprehensive basic Git commands content."""
    return '''# Basic Git Commands

Master the essential Git commands that you'll use daily in your development workflow.

---

## Overview

This guide covers the fundamental Git commands every developer needs. These commands form the foundation of your Git workflow and you'll use them constantly.

**Command Categories:**
- Repository initialization
- File staging and committing  
- Viewing history and status
- Undoing changes
- Basic navigation

---

## Repository Commands

### git init

Initialize a new Git repository in the current directory.

```bash
# Create new repository
git init

# Initialize with specific branch name
git init --initial-branch=main
git init -b main

# Create directory and initialize
git init my-project
```

**What it does:**
- Creates `.git` directory
- Sets up internal Git structure
- Makes current directory a Git repository

**When to use:**
- Starting a new project
- Adding Git to existing project

### git clone

Copy an existing repository from a remote location.

```bash
# Clone repository
git clone https://github.com/user/repo.git

# Clone to specific directory
git clone https://github.com/user/repo.git my-folder

# Clone specific branch
git clone -b develop https://github.com/user/repo.git

# Shallow clone (recent history only)
git clone --depth 1 https://github.com/user/repo.git

# Clone via SSH
git clone git@github.com:user/repo.git
```

**What it does:**
- Downloads entire repository
- Creates remote connection named "origin"
- Checks out default branch

---

## File Tracking Commands

### git status

Show the status of your working directory and staging area.

```bash
# View status
git status

# Short format
git status -s
git status --short

# Branch information
git status -sb
```

**Example output:**
```bash
$ git status
On branch main
Changes to be committed:
  new file:   index.html
Changes not staged for commit:
  modified:   README.md
Untracked files:
  style.css
```

### git add

Add files to the staging area.

```bash
# Add specific file
git add filename.txt

# Add all files
git add .
git add -A

# Interactive staging
git add -i

# Patch mode
git add -p
```

### git commit

Save staged changes to the repository.

```bash
# Commit with message
git commit -m "Add user login feature"

# Commit all tracked changes
git commit -am "Update all files"

# Amend last commit
git commit --amend -m "New message"

# Empty commit
git commit --allow-empty -m "Trigger CI"
```

---

## Viewing History

### git log

Show commit history.

```bash
# Full log
git log

# One line per commit
git log --oneline

# With graph
git log --graph --oneline --all

# Last N commits
git log -5

# By date
git log --since="2 weeks ago"

# By author
git log --author="John"

# Search messages
git log --grep="bug fix"

# Show changes
git log -p

# File history
git log -- filename.txt
```

### git diff

Show changes between commits, working directory, and staging area.

```bash
# Unstaged changes
git diff

# Staged changes
git diff --staged

# Compare commits
git diff commit1 commit2

# Compare branches
git diff main feature-branch

# Specific file
git diff filename.txt
```

---

## Undoing Changes

### git restore

Restore files in working directory (Git 2.23+).

```bash
# Discard changes
git restore filename.txt

# Unstage file
git restore --staged filename.txt

# Restore from commit
git restore --source=HEAD~2 filename.txt
```

### git reset

Reset current HEAD to specified state.

```bash
# Unstage file
git reset filename.txt

# Reset to previous commit (keep changes)
git reset --soft HEAD~1

# Reset to previous commit (discard staged)
git reset HEAD~1

# Reset to previous commit (discard all)
git reset --hard HEAD~1
```

### git rm

Remove files from Git.

```bash
# Remove file
git rm filename.txt

# Remove from Git but keep file
git rm --cached filename.txt

# Remove directory
git rm -r directory/
```

### git mv

Rename or move files.

```bash
# Rename file
git mv oldname.txt newname.txt

# Move file
git mv file.txt directory/
```

---

## Best Practices

1. **Commit Often**: Make small, logical commits
2. **Write Clear Messages**: Descriptive commit messages
3. **Review Before Committing**: Use git diff and git status
4. **Use .gitignore**: Don't commit generated files
5. **Use Branches**: Never work directly on main

---

## Common Pitfalls

- **Committing Too Much**: Review changes before git add .
- **Vague Commit Messages**: Be specific and clear
- **Not Using .gitignore**: Accidentally committing dependencies
- **Working Directly on Main**: Always use feature branches

---

## Hands-On Exercise

```bash
# Initialize repository
mkdir git-practice
cd git-practice
git init

# Create and commit file
echo "# Git Practice" > README.md
git add README.md
git commit -m "Initial commit"

# Make changes
echo "## Features" >> README.md
git add README.md
git commit -m "Add features section"

# View history
git log --oneline
```

---

## Quick Reference

```bash
# Repository
git init                    # Initialize repository
git clone <url>            # Clone repository

# Status & Info  
git status                 # Show status
git log                    # Show history
git diff                   # Show changes

# Staging & Committing
git add <file>            # Stage file
git commit -m "msg"       # Commit

# Undoing
git restore <file>        # Discard changes
git reset HEAD~1          # Undo commit
```

---

**Previous:** [← Installation](02-installation-configuration.md) | **Next:** [Git Workflow →](04-git-workflow.md)
'''

def write_file(filepath, content):
    """Write content to file, creating directories if needed."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding='utf-8')
    print(f"✅ Created: {filepath}")

def main():
    """Generate all Git content."""
    base_path = Path("devops-essentials/01-git")
    
    # Fix truncated basic commands file
    print("\n🔧 Fixing truncated file...")
    write_file(
        base_path / "basics" / "03-basic-commands.md",
        create_basic_commands_content()
    )
    
    print("\n✅ Basic commands file recreated successfully!")
    print("\nNext: Run this script with additional content generation for intermediate and advanced topics.")

if __name__ == "__main__":
    main()
