# Resolving Merge Conflicts
Handle conflicts when branches diverge.

## Understanding Conflicts
Conflicts occur when same lines are changed in different branches.

## Conflict Markers
```
<<<<<<< HEAD
Current branch changes
=======
Merging branch changes
>>>>>>> feature-branch
```

## Resolution Steps
```bash
# 1. Identify conflicts
git status

# 2. Open and edit files
# Remove markers, keep desired changes

# 3. Stage resolved files
git add resolved-file.txt

# 4. Complete merge
git commit
```

## Prevention
- Pull frequently
- Communicate with team
- Keep changes small

**Previous:** [â† Branching Strategies](07-branching-strategies.md) | **Next:** [Rebase vs Merge â†’](09-rebase-vs-merge.md)
