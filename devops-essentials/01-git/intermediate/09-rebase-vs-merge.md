# Git Rebase vs Merge
Understand when to rebase and when to merge.

## Merge
Creates a merge commit, preserves history.

```bash
git checkout main
git merge feature-branch
```

Pros: Safe, preserves context
Cons: Can clutter history

## Rebase
Replays commits on top of another branch.

```bash
git checkout feature-branch
git rebase main
```

Pros: Clean linear history
Cons: Rewrites history

## When to Use
- **Merge**: For shared branches, preserving history
- **Rebase**: For local branches, cleaning up

## Golden Rule
Never rebase public/shared branches!

**Previous:** [â† Resolving Conflicts](08-resolving-conflicts.md) | **Next:** [Stash and Cherry-pick â†’](10-stash-cherry-pick.md)
