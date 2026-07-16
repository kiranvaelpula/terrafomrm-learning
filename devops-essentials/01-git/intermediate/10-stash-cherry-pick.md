# Git Stash and Cherry-Pick
Temporarily save work and selectively apply commits.

## Git Stash
Save uncommitted changes temporarily.

```bash
# Stash changes
git stash

# List stashes
git stash list

# Apply stash
git stash apply
git stash pop

# Stash with message
git stash save 'WIP: feature'

# Drop stash
git stash drop
```

## Git Cherry-Pick
Apply specific commits from another branch.

```bash
# Pick single commit
git cherry-pick commit-hash

# Pick multiple commits
git cherry-pick hash1 hash2

# Cherry-pick without commit
git cherry-pick -n commit-hash
```

## Use Cases
- Moving commits between branches
- Applying hotfixes
- Selective backporting

**Previous:** [â† Rebase vs Merge](09-rebase-vs-merge.md) | **Next:** [Tags and Releases â†’](11-tags-releases.md)
