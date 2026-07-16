# Branching and Merging
Master Git branching and merging for parallel development.

## Branch Basics
Branches allow independent development lines.

### Creating Branches
```bash
git branch feature-name
git checkout -b feature-name
git switch -c feature-name
```

### Switching Branches
```bash
git checkout branch-name
git switch branch-name
```

### Listing Branches
```bash
git branch
git branch -a
git branch -v
```

### Deleting Branches
```bash
git branch -d branch-name
git branch -D branch-name
```

## Merging
Integrate changes from one branch to another.

### Fast-Forward Merge
```bash
git checkout main
git merge feature-branch
```

### Three-Way Merge
```bash
git merge --no-ff feature-branch
```

### Merge Conflicts
```bash
# When conflict occurs
git status
# Edit conflicted files
git add resolved-file.txt
git commit
```

## Best Practices
1. Keep branches short-lived
2. Merge frequently
3. Delete merged branches
4. Use descriptive names

**Previous:** [Remote Repositories](../basics/05-remote-repositories.md) | **Next:** [Branching Strategies â†’](07-branching-strategies.md)
