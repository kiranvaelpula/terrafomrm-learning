# Git Troubleshooting and Recovery
Solve common Git problems.

## Undo Last Commit
```bash
# Keep changes
git reset --soft HEAD~1

# Discard changes
git reset --hard HEAD~1
```

## Recover Deleted Branch
```bash
# Find commit
git reflog

# Recreate branch
git branch recovered-branch commit-hash
```

## Fix Detached HEAD
```bash
# Create branch from current state
git checkout -b new-branch

# Or return to branch
git checkout main
```

## Recover Lost Commits
```bash
# View reflog
git reflog

# Checkout lost commit
git checkout commit-hash

# Create branch
git checkout -b recovery
```

## Fix Merge Conflicts
```bash
git merge --abort
# Or resolve conflicts
git add resolved-files
git commit
```

## Repository Corruption
```bash
# Check integrity
git fsck

# Recover
git reflog expire --expire=now --all
git gc --prune=now
```

**Previous:** [â† Enterprise Git](19-enterprise-git.md) | **Next:** [Interview Questions â†’](interview-questions-advanced.md)
