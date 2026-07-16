# Understanding Git Workflow

Master the Git workflow to manage code changes efficiently and collaborate effectively with your team.

---

## Overview

A Git workflow is a recipe or recommendation for how to use Git to accomplish work in a consistent and productive manner. Understanding workflows helps teams collaborate smoothly and maintain clean project history.

**What you'll learn:**
- The basic Git workflow cycle
- How files move through Git states
- Common workflow patterns
- Branch-based workflows
- Team collaboration workflows

---

## The Basic Git Workflow

### The Three-State Architecture

Every file in Git exists in one of three states:

```
Working Directory → Staging Area → Git Repository
   (Modified)         (Staged)      (Committed)
```

**1. Working Directory**
- Where you modify files
- Your actual project files
- Changes are local and not tracked yet

**2. Staging Area (Index)**
- Holds changes ready to be committed
- Allows selective commits
- Prepares snapshot for repository

**3. Git Repository (.git directory)**
- Permanent storage of committed snapshots
- Complete project history
- Safely stored metadata

### Workflow Visualization

```
┌─────────────────┐
│     Working     │  1. Modify files
│    Directory    │  
└────────┬────────┘
         │ git add
         ↓
┌─────────────────┐
│  Staging Area   │  2. Stage changes
│     (Index)     │
└────────┬────────┘
         │ git commit
         ↓
┌─────────────────┐
│      .git       │  3. Commit to repo
│   Repository    │
└─────────────────┘
```

---

## The Development Cycle

### Step-by-Step Workflow

**1. Check Status**
```bash
git status
# Know where you stand before starting
```

**2. Make Changes**
```bash
# Edit files in your editor
vim app.js
# Or
code .
```

**3. Review Changes**
```bash
# See what changed
git diff

# Check status
git status
```

**4. Stage Changes**
```bash
# Stage specific files
git add app.js

# Or stage all changes
git add .

# Or stage selectively
git add -p  # Interactive staging
```

**5. Review Staged Changes**
```bash
# See what will be committed
git diff --staged

# Verify staging area
git status
```

**6. Commit Changes**
```bash
# Commit with message
git commit -m "Add user login feature"

# Or open editor for detailed message
git commit
```

**7. View History**
```bash
# See your commit
git log --oneline

# Or detailed view
git log
```

---

## Complete Workflow Example

### Scenario: Adding a New Feature

```bash
# 1. Start fresh - check status
$ git status
On branch main
nothing to commit, working tree clean

# 2. Create new feature branch
$ git checkout -b feature/user-auth
Switched to a new branch 'feature/user-auth'

# 3. Create new file
$ echo "function login() {}" > auth.js

# 4. Check what changed
$ git status
On branch feature/user-auth
Untracked files:
  auth.js

# 5. Stage the new file
$ git add auth.js

# 6. Verify staging
$ git status
On branch feature/user-auth
Changes to be committed:
  new file:   auth.js

# 7. Commit
$ git commit -m "Add authentication module"
[feature/user-auth a3f8d92] Add authentication module
 1 file changed, 1 insertion(+)
 create mode 100644 auth.js

# 8. Continue working - modify file
$ echo "function logout() {}" >> auth.js

# 9. See the changes
$ git diff
diff --git a/auth.js b/auth.js
+function logout() {}

# 10. Stage and commit
$ git add auth.js
$ git commit -m "Add logout function"

# 11. View history
$ git log --oneline
b4e9c83 (HEAD -> feature/user-auth) Add logout function
a3f8d92 Add authentication module
c2f7d91 (main) Initial commit

# 12. Merge to main
$ git checkout main
$ git merge feature/user-auth

# 13. Clean up branch
$ git branch -d feature/user-auth
```

---

## Common Workflow Patterns

### 1. Feature Development Workflow

```bash
# Start new feature
git checkout -b feature/shopping-cart

# Work on feature
# ... make changes ...
git add .
git commit -m "Add cart item model"

# ... more changes ...
git add .
git commit -m "Implement add to cart"

# ... more changes ...
git add .
git commit -m "Add cart total calculation"

# Feature complete - merge to main
git checkout main
git merge feature/shopping-cart

# Optional: Delete feature branch
git branch -d feature/shopping-cart
```

### 2. Bug Fix Workflow

```bash
# Create hotfix branch
git checkout -b hotfix/login-validation

# Fix the bug
# ... edit files ...

# Test the fix
# ... run tests ...

# Commit fix
git add .
git commit -m "Fix: Validate email format in login"

# Merge to main
git checkout main
git merge hotfix/login-validation

# Tag the fix version
git tag v1.2.1

# Clean up
git branch -d hotfix/login-validation
```

### 3. Experimental Workflow

```bash
# Try something risky
git checkout -b experiment/new-algorithm

# Experiment freely
# ... make changes ...
git add .
git commit -m "Try new sorting algorithm"

# If experiment succeeds
git checkout main
git merge experiment/new-algorithm

# If experiment fails
git checkout main
git branch -D experiment/new-algorithm  # Force delete
```

---

## Branch-Based Workflows

### 1. Simple Feature Branch Workflow

```
main:     A---B---C---F---G
                   /     /
feature1:         D-----E
```

**Usage:**
```bash
# Create feature branch
git checkout -b feature/new-ui

# Work and commit
git add .
git commit -m "Update UI components"

# Merge when done
git checkout main
git merge feature/new-ui
```

### 2. Git Flow (Detailed Workflow)

```
main:       A---------E-------G
             \       /         \
develop:      B--C--D-----F-----H
               \       /
feature:        I--J--K
```

**Branches:**
- `main`: Production code
- `develop`: Integration branch
- `feature/*`: New features
- `hotfix/*`: Emergency fixes
- `release/*`: Release preparation

**Example:**
```bash
# Setup
git checkout -b develop

# Start feature
git checkout -b feature/payment develop

# Work on feature
git add .
git commit -m "Add payment integration"

# Merge to develop
git checkout develop
git merge feature/payment

# Create release
git checkout -b release/1.0 develop

# Bug fixes in release
git commit -am "Fix payment validation"

# Merge to main and develop
git checkout main
git merge release/1.0
git tag v1.0

git checkout develop
git merge release/1.0
```

### 3. GitHub Flow (Simplified)

```
main:  A---B---D---F
            \  /    \
feature:     C       E---G
```

**Steps:**
```bash
# 1. Create branch from main
git checkout main
git checkout -b feature/add-search

# 2. Work and commit regularly
git add .
git commit -m "Add search input"
git commit -m "Implement search logic"

# 3. Push and create pull request
git push origin feature/add-search

# 4. After review and approval, merge
git checkout main
git merge feature/add-search

# 5. Deploy main (automatically or manually)
```

### 4. Trunk-Based Development

```
main:  A---B---C---D---E---F---G
            \   /    \  /
short-      X---Y    Z--W
lived:
```

**Characteristics:**
- Work on main or very short-lived branches
- Commit frequently
- Use feature flags for incomplete features

```bash
# Short-lived branch
git checkout -b quick-fix

# Small change
git add .
git commit -m "Fix typo in header"

# Immediate merge
git checkout main
git merge quick-fix
git branch -d quick-fix

# Or work directly on main (with feature flags)
git checkout main
# ... make changes ...
git commit -am "Add feature behind flag"
```

---

## Team Collaboration Workflow

### Centralized Workflow

```
     Remote Repository
            │
    ┌───────┼───────┐
    │       │       │
  Dev A   Dev B   Dev C
```

**Process:**
```bash
# Clone repository
git clone <url>

# Make changes
git add .
git commit -m "Add feature"

# Pull latest changes
git pull origin main

# Push changes
git push origin main
```

### Feature Branch Workflow

```
         Remote Repository
          main    feature1  feature2
            │       │         │
    ┌───────┼───────┼─────────┤
    │       │       │         │
  Dev A   Dev B   Dev C     Dev D
```

**Process:**
```bash
# Create feature branch
git checkout -b feature/my-feature

# Work and commit
git add .
git commit -m "Implement feature"

# Push feature branch
git push origin feature/my-feature

# Create pull request (on GitHub/GitLab)
# After review, merge via PR

# Update local main
git checkout main
git pull origin main
```

---

## Real-World Workflow Scenarios

### Scenario 1: Daily Development

```bash
# Morning: Start work
git checkout main
git pull origin main
git checkout -b feature/dashboard-widgets

# Throughout day: Regular commits
# 10 AM
git add components/Widget.js
git commit -m "Create widget component"

# 12 PM
git add components/Widget.css
git commit -m "Style widget component"

# 2 PM
git add tests/Widget.test.js
git commit -m "Add widget tests"

# End of day: Push work
git push origin feature/dashboard-widgets

# Next day: Continue
git pull origin feature/dashboard-widgets
# ... continue working ...
```

### Scenario 2: Code Review Workflow

```bash
# 1. Create feature branch
git checkout -b feature/api-integration

# 2. Implement feature
# ... multiple commits ...

# 3. Push and create pull request
git push origin feature/api-integration

# 4. Reviewer requests changes
# Make requested changes locally

git add .
git commit -m "Address review comments"
git push origin feature/api-integration

# 5. After approval, merge (usually via PR interface)

# 6. Update local repository
git checkout main
git pull origin main
git branch -d feature/api-integration
```

### Scenario 3: Handling Conflicts

```bash
# Your work
git checkout -b feature/update-docs
echo "New docs" >> README.md
git commit -am "Update README"

# Try to merge to main
git checkout main
git pull origin main  # Someone else changed README too!

# Attempt merge
git merge feature/update-docs
# CONFLICT in README.md

# Resolve conflict
vim README.md  # Edit file, resolve conflicts
git add README.md
git commit -m "Merge feature/update-docs"

# Push resolved merge
git push origin main
```

---

## Workflow Best Practices

### 1. Commit Frequently

```bash
# ✅ Good: Small, logical commits
git add auth.js
git commit -m "Add login function"

git add auth.js
git commit -m "Add logout function"

git add auth.test.js
git commit -m "Add auth tests"

# ❌ Bad: One huge commit
# ... work all day ...
git add .
git commit -m "Added authentication"
```

### 2. Write Clear Commit Messages

```bash
# ✅ Good: Clear and specific
git commit -m "Fix null pointer in payment validation"

git commit -m "Add user authentication

- Implement JWT token generation  
- Add password hashing with bcrypt
- Create middleware for protected routes"

# ❌ Bad: Vague messages
git commit -m "fixed stuff"
git commit -m "updates"
git commit -m "working now"
```

### 3. Pull Before Push

```bash
# ✅ Good: Avoid conflicts
git pull origin main
# ... resolve any conflicts ...
git push origin main

# ❌ Bad: Push without pulling
git push origin main
# ERROR: Updates were rejected because remote contains work...
```

### 4. Review Before Committing

```bash
# ✅ Good: Review changes
git status
git diff
git diff --staged
git commit -m "Clear message based on review"

# ❌ Bad: Blind commit
git add .
git commit -m "changes"
```

### 5. Use Branches

```bash
# ✅ Good: Feature branches
git checkout -b feature/new-dashboard
# ... work on feature ...
git merge feature/new-dashboard

# ❌ Bad: Work directly on main
git checkout main
# ... make changes ...  (risky!)
```

---

## Common Pitfalls

### Pitfall 1: Large Commits

```bash
# ❌ Problem
# ... work for 3 days ...
git add .
git commit -m "Various updates"

# ✅ Solution
# Commit logical chunks
git add feature1.js
git commit -m "Add feature 1"

git add feature2.js
git commit -m "Add feature 2"
```

### Pitfall 2: Forgetting to Pull

```bash
# ❌ Problem
git push origin main
# ERROR: rejected (fetch first)

# ✅ Solution
git pull origin main
# Resolve conflicts if any
git push origin main
```

### Pitfall 3: Working on Main

```bash
# ❌ Problem
git checkout main
# ... make risky changes ...

# ✅ Solution
git checkout -b experiment/risky-feature
# ... make changes safely ...
# If good: merge; if bad: delete branch
```

### Pitfall 4: Not Using .gitignore

```bash
# ❌ Problem
git add .
# Accidentally commits node_modules/

# ✅ Solution
echo "node_modules/" >> .gitignore
git add .gitignore
git add .  # Now ignores node_modules/
```

---

## Hands-On Exercise

### Exercise 1: Basic Workflow

```bash
# 1. Initialize repository
mkdir workflow-practice
cd workflow-practice
git init

# 2. Create initial file
echo "# Workflow Practice" > README.md
git add README.md
git commit -m "Initial commit"

# 3. Create feature branch
git checkout -b feature/add-content

# 4. Add content
echo "## Features" >> README.md
git add README.md
git commit -m "Add features section"

# 5. Add more content
echo "- Feature 1" >> README.md
git add README.md
git commit -m "Add feature 1"

# 6. View history
git log --oneline --graph --all

# 7. Merge to main
git checkout main
git merge feature/add-content

# 8. Clean up
git branch -d feature/add-content

# 9. Final history
git log --oneline
```

### Exercise 2: Conflict Resolution

```bash
# 1. Create two branches
git checkout -b branch-a
echo "Line from branch A" >> file.txt
git add file.txt
git commit -m "Add line in branch A"

git checkout main
git checkout -b branch-b
echo "Line from branch B" >> file.txt
git add file.txt
git commit -m "Add line in branch B"

# 2. Merge first branch
git checkout main
git merge branch-a

# 3. Try merge second branch (conflict!)
git merge branch-b
# CONFLICT in file.txt

# 4. Resolve conflict
cat file.txt  # See conflict markers
vim file.txt  # Edit and resolve
git add file.txt
git commit -m "Resolve merge conflict"

# 5. Clean up
git branch -d branch-a branch-b
```

---

## Interview Tips

**Explain the Git workflow**
> The Git workflow consists of three main stages: modifying files in the working directory, staging changes with `git add`, and committing them with `git commit`. This allows developers to selectively group changes into meaningful commits.

**What is the staging area?**
> The staging area (or index) is an intermediate area where changes are prepared before committing. It allows you to selectively choose which changes to include in the next commit, providing fine-grained control over your project history.

**Why use feature branches?**
> Feature branches isolate development work from the main codebase, allowing safe experimentation, easier code review, and the ability to work on multiple features simultaneously without interference.

**What's the difference between Git Flow and GitHub Flow?**
> Git Flow is more complex with multiple long-lived branches (main, develop, feature, release, hotfix), suited for scheduled releases. GitHub Flow is simpler with just main and short-lived feature branches, suited for continuous deployment.

**How do you handle merge conflicts?**
> Pull the latest changes, attempt the merge, identify conflicted files, manually edit to resolve conflicts (removing conflict markers), stage the resolved files with `git add`, and complete with `git commit`.

---

## Workflow Comparison

| Workflow | Complexity | Use Case | Team Size |
|----------|-----------|----------|-----------|
| **Simple Feature Branch** | Low | Small projects | 1-5 |
| **Git Flow** | High | Scheduled releases | 5+ |
| **GitHub Flow** | Medium | Continuous deployment | Any |
| **Trunk-Based** | Medium | Rapid iteration | 5+ |
| **Centralized** | Low | Simple projects | 1-3 |

---

## Quick Reference

```bash
# Basic cycle
git status           # Check state
git add <files>      # Stage changes
git commit -m "msg"  # Commit
git log              # View history

# Branch workflow
git checkout -b feature/x    # Create branch
# ... work and commit ...
git checkout main            # Switch to main
git merge feature/x          # Merge
git branch -d feature/x      # Delete branch

# Team workflow
git pull origin main         # Get updates
# ... work ...
git push origin main         # Share work
```

---

**Previous:** [← Basic Git Commands](03-basic-commands.md) | **Next:** [Remote Repositories →](05-remote-repositories.md)
