# Create all Advanced Git files and Labs

Write-Host "Creating advanced Git content..." -ForegroundColor Cyan

function Create-GitFile {
    param($Path, $Content)
    $dir = Split-Path $Path -Parent
    if ($dir) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $Content | Out-File -FilePath $Path -Encoding utf8
    if (Test-Path $Path) {
        Write-Host "✅ $Path" -ForegroundColor Green
    }
}

$files = @{
    "advanced/13-git-internals.md" = @"
# Git Internals
Understanding Git's internal architecture.

## Git Objects
- **Blob**: File contents
- **Tree**: Directory structure  
- **Commit**: Snapshot with metadata
- **Tag**: Named reference

## The .git Directory
``````
.git/
├── objects/    # All Git objects
├── refs/       # Branch/tag references
├── HEAD        # Current branch pointer
└── config      # Repository configuration
``````

## How Git Stores Data
Git uses SHA-1 hashes to identify objects.

``````bash
# View object
git cat-file -p commit-hash

# View object type
git cat-file -t hash
``````

## Refs and HEAD
``````bash
# View HEAD
cat .git/HEAD

# View branch ref
cat .git/refs/heads/main
``````

**Previous:** [← Interview Questions](../intermediate/interview-questions-intermediate.md) | **Next:** [Advanced Operations →](14-advanced-operations.md)
"@

    "advanced/14-advanced-operations.md" = @"
# Advanced Git Operations
Master advanced Git commands and techniques.

## Git Filter-Branch
Rewrite repository history.

``````bash
# Remove file from history
git filter-branch --tree-filter 'rm -f passwords.txt' HEAD
``````

## Git Subtree
Manage project dependencies.

``````bash
# Add subtree
git subtree add --prefix=lib/project url main

# Pull updates
git subtree pull --prefix=lib/project url main
``````

## Git Submodules
Include other repositories.

``````bash
# Add submodule
git submodule add url path

# Clone with submodules
git clone --recursive url

# Update submodules
git submodule update --init --recursive
``````

## Git Bisect
Binary search for bug introduction.

``````bash
git bisect start
git bisect bad
git bisect good commit-hash
# Test each commit
git bisect good/bad
git bisect reset
``````

**Previous:** [← Git Internals](13-git-internals.md) | **Next:** [Git Hooks →](15-git-hooks.md)
"@

    "advanced/15-git-hooks.md" = @"
# Git Hooks
Automate workflows with Git hooks.

## Hook Types
- **pre-commit**: Before commit
- **pre-push**: Before push
- **post-merge**: After merge
- **commit-msg**: Validate commit message

## Creating Hooks
``````bash
# Location
.git/hooks/

# Make executable
chmod +x .git/hooks/pre-commit
``````

## Example: Pre-commit Hook
``````bash
#!/bin/sh
# Run tests before commit
npm test
if [ \$? -ne 0 ]; then
    echo "Tests failed"
    exit 1
fi
``````

## Example: Commit-msg Hook
``````bash
#!/bin/sh
# Validate commit message format
commit_msg=\$(cat \$1)
if ! echo "\$commit_msg" | grep -qE "^(feat|fix|docs):"; then
    echo "Invalid commit message format"
    exit 1
fi
``````

**Previous:** [← Advanced Operations](14-advanced-operations.md) | **Next:** [Performance →](16-performance.md)
"@

    "advanced/16-performance.md" = @"
# Git Performance Optimization
Optimize Git for large repositories.

## Shallow Clone
``````bash
git clone --depth 1 url
``````

## Sparse Checkout
Checkout only specific directories.

``````bash
git sparse-checkout init
git sparse-checkout set dir1 dir2
``````

## Git LFS
Handle large files.

``````bash
git lfs install
git lfs track '*.psd'
git add .gitattributes
``````

## Repository Maintenance
``````bash
# Garbage collection
git gc

# Aggressive GC
git gc --aggressive

# Optimize repository
git repack -a -d
``````

## Configuration
``````bash
# Increase cache
git config --global core.preloadindex true
git config --global core.fscache true
``````

**Previous:** [← Git Hooks](15-git-hooks.md) | **Next:** [Monorepo Strategies →](17-monorepo-strategies.md)
"@

    "advanced/17-monorepo-strategies.md" = @"
# Monorepo vs Multi-repo Strategies
Choosing repository organization strategy.

## Monorepo
Single repository for multiple projects.

### Advantages
- Atomic changes across projects
- Simplified dependency management
- Single source of truth

### Disadvantages
- Large repository size
- Complex CI/CD
- Access control challenges

### Tools
- Nx, Turborepo, Lerna
- Git sparse-checkout
- Git LFS for large files

## Multi-repo
Separate repositories per project.

### Advantages
- Smaller repositories
- Independent deployments
- Clear boundaries

### Disadvantages
- Cross-project changes difficult
- Dependency versioning complexity

## Choosing Strategy
Consider team size, project relationships, and tooling.

**Previous:** [← Performance](16-performance.md) | **Next:** [Security →](18-security.md)
"@

    "advanced/18-security.md" = @"
# Git Security Best Practices
Secure your Git workflow.

## Never Commit Secrets
``````bash
# Use .gitignore
echo '.env' >> .gitignore
echo 'secrets/' >> .gitignore
``````

## Remove Committed Secrets
``````bash
# Use BFG Repo-Cleaner
bfg --replace-text passwords.txt

# Or filter-branch
git filter-branch --tree-filter 'rm -f secret.key' HEAD

# Force push
git push --force
``````

## GPG Signing
Sign commits cryptographically.

``````bash
# Generate GPG key
gpg --gen-key

# Configure Git
git config --global user.signingkey KEY_ID
git config --global commit.gpgsign true

# Sign commit
git commit -S -m 'message'
``````

## Branch Protection
- Require pull request reviews
- Require status checks
- Enforce signed commits
- Restrict force pushes

**Previous:** [← Monorepo Strategies](17-monorepo-strategies.md) | **Next:** [Enterprise Git →](19-enterprise-git.md)
"@

    "advanced/19-enterprise-git.md" = @"
# Git in Enterprise
Scale Git for large organizations.

## Centralized Git
- GitLab, GitHub Enterprise, Bitbucket
- LDAP/AD integration
- Audit logging
- Compliance features

## Access Control
``````bash
# Team-based permissions
# Branch protection rules
# Required reviews
# CI/CD integration
``````

## Backup and Disaster Recovery
``````bash
# Mirror repositories
git clone --mirror url backup.git

# Restore from mirror
git clone backup.git restored-repo
``````

## Performance at Scale
- Use Git LFS
- Implement sparse checkout
- Repository sharding
- Caching proxies

## Compliance
- Audit logs
- Signed commits
- Branch policies
- Retention policies

**Previous:** [← Security](18-security.md) | **Next:** [Troubleshooting →](20-troubleshooting.md)
"@

    "advanced/20-troubleshooting.md" = @"
# Git Troubleshooting and Recovery
Solve common Git problems.

## Undo Last Commit
``````bash
# Keep changes
git reset --soft HEAD~1

# Discard changes
git reset --hard HEAD~1
``````

## Recover Deleted Branch
``````bash
# Find commit
git reflog

# Recreate branch
git branch recovered-branch commit-hash
``````

## Fix Detached HEAD
``````bash
# Create branch from current state
git checkout -b new-branch

# Or return to branch
git checkout main
``````

## Recover Lost Commits
``````bash
# View reflog
git reflog

# Checkout lost commit
git checkout commit-hash

# Create branch
git checkout -b recovery
``````

## Fix Merge Conflicts
``````bash
git merge --abort
# Or resolve conflicts
git add resolved-files
git commit
``````

## Repository Corruption
``````bash
# Check integrity
git fsck

# Recover
git reflog expire --expire=now --all
git gc --prune=now
``````

**Previous:** [← Enterprise Git](19-enterprise-git.md) | **Next:** [Interview Questions →](interview-questions-advanced.md)
"@

    "advanced/interview-questions-advanced.md" = @"
# Git Interview Questions - Advanced Level

### Q1: Explain Git internals
**Answer:** Git stores data as snapshots using four object types: blobs (file contents), trees (directory structure), commits (snapshots with metadata), and tags (named references). All identified by SHA-1 hashes.

### Q2: How does Git garbage collection work?
**Answer:** git gc removes unreachable objects, compresses files, and optimizes repository. Runs automatically or manually via \`git gc\`.

### Q3: What is Git reflog?
**Answer:** Local history of HEAD changes. Used to recover lost commits, deleted branches, or undo operations.

### Q4: Explain Git hooks
**Answer:** Scripts that run automatically on Git events (pre-commit, pre-push, etc.). Used for testing, linting, commit message validation.

### Q5: How to handle large files in Git?
**Answer:** Use Git LFS (Large File Storage) to store large files externally while keeping repository lightweight.

### Q6: Monorepo vs multi-repo?
**Answer:** Monorepo: single repo for multiple projects (atomic changes, simplified deps). Multi-repo: separate repos (smaller size, independent deploys).

### Q7: How to sign commits?
**Answer:** Use GPG keys. Configure with \`git config --global commit.gpgsign true\`. Sign with \`git commit -S\`.

### Q8: Explain Git bisect
**Answer:** Binary search to find commit that introduced bug. Mark commits as good/bad until bug source identified.

### Q9: How to recover deleted branch?
**Answer:** Use \`git reflog\` to find commit, then \`git branch branch-name commit-hash\`.

### Q10: Git security best practices?
**Answer:** Never commit secrets, use .gitignore, sign commits with GPG, enable branch protection, audit repository access, scan for secrets.

**Previous:** [← Troubleshooting](20-troubleshooting.md) | **Next:** [Labs →](../git-practice/)
"@

    "git-practice/lab-01-basics/README.md" = @"
# Lab 1: Git Basics

## Objective
Learn fundamental Git operations by creating your first repository.

## Prerequisites
- Git installed
- Text editor

## Exercises

### Exercise 1: Initialize Repository
``````bash
mkdir my-first-repo
cd my-first-repo
git init
``````

### Exercise 2: Create and Commit Files
``````bash
echo '# My Project' > README.md
git add README.md
git commit -m 'Initial commit'
``````

### Exercise 3: Make Changes
``````bash
echo 'Description' >> README.md
git add README.md
git commit -m 'Add description'
``````

### Exercise 4: View History
``````bash
git log
git log --oneline
``````

## Success Criteria
- Repository initialized
- Multiple commits made
- Can view history

**Next:** [Lab 2: Branching →](../lab-02-branching/)
"@

    "git-practice/lab-02-branching/README.md" = @"
# Lab 2: Branching Workflow

## Objective
Practice feature branch workflow.

## Exercises

### Exercise 1: Create Feature Branch
``````bash
git checkout -b feature/new-feature
``````

### Exercise 2: Make Changes
``````bash
echo 'Feature code' > feature.txt
git add feature.txt
git commit -m 'Add new feature'
``````

### Exercise 3: Merge to Main
``````bash
git checkout main
git merge feature/new-feature
``````

### Exercise 4: Clean Up
``````bash
git branch -d feature/new-feature
``````

## Success Criteria
- Feature branch created
- Changes merged
- Branch deleted

**Previous:** [← Lab 1](../lab-01-basics/) | **Next:** [Lab 3 →](../lab-03-collaboration/)
"@

    "git-practice/lab-03-collaboration/README.md" = @"
# Lab 3: Collaboration with Remotes

## Objective
Learn remote repository operations.

## Exercises

### Exercise 1: Clone Repository
``````bash
git clone https://github.com/user/repo.git
``````

### Exercise 2: Create Feature Branch
``````bash
git checkout -b feature/collaboration
echo 'New feature' > collab.txt
git add collab.txt
git commit -m 'Add collaboration feature'
``````

### Exercise 3: Push Branch
``````bash
git push origin feature/collaboration
``````

### Exercise 4: Pull Updates
``````bash
git checkout main
git pull origin main
``````

## Success Criteria
- Repository cloned
- Branch pushed to remote
- Updates pulled successfully

**Previous:** [← Lab 2](../lab-02-branching/) | **Next:** [Lab 4 →](../lab-04-advanced/)
"@

    "git-practice/lab-04-advanced/README.md" = @"
# Lab 4: Advanced Operations

## Objective
Practice rebase, stash, and cherry-pick.

## Exercises

### Exercise 1: Rebase
``````bash
git checkout feature-branch
git rebase main
``````

### Exercise 2: Stash Changes
``````bash
echo 'WIP' >> file.txt
git stash
git stash list
git stash pop
``````

### Exercise 3: Cherry-pick
``````bash
git cherry-pick commit-hash
``````

## Success Criteria
- Successfully rebased branch
- Used stash for WIP
- Cherry-picked specific commit

**Previous:** [← Lab 3](../lab-03-collaboration/) | **Next:** [Lab 5 →](../lab-05-gitflow/)
"@

    "git-practice/lab-05-gitflow/README.md" = @"
# Lab 5: GitFlow Implementation

## Objective
Implement complete GitFlow workflow.

## Exercises

### Exercise 1: Setup Branches
``````bash
git checkout -b develop
git push origin develop
``````

### Exercise 2: Feature Development
``````bash
git checkout -b feature/user-auth develop
# Develop feature
git checkout develop
git merge feature/user-auth
``````

### Exercise 3: Release Branch
``````bash
git checkout -b release/1.0.0 develop
# Bug fixes only
git checkout main
git merge release/1.0.0
git tag v1.0.0
``````

### Exercise 4: Hotfix
``````bash
git checkout -b hotfix/critical-bug main
# Fix bug
git checkout main
git merge hotfix/critical-bug
git checkout develop
git merge hotfix/critical-bug
``````

## Success Criteria
- GitFlow branches created
- Feature merged to develop
- Release tagged on main
- Hotfix applied to both branches

**Previous:** [← Lab 4](../lab-04-advanced/)
"@
}

foreach ($file in $files.Keys) {
    Create-GitFile -Path $file -Content $files[$file]
}

Write-Host "`n✅ Advanced files and labs created!" -ForegroundColor Green
Write-Host "Total: $($files.Count) files" -ForegroundColor Cyan
