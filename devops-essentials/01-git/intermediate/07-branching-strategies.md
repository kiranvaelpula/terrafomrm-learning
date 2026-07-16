# Git Branching Strategies
Learn different branching workflows for team collaboration.

## GitFlow
Feature branches, develop, main, hotfix, release branches.

```bash
# Start feature
git checkout -b feature/new-feature develop

# Finish feature
git checkout develop
git merge feature/new-feature
```

## GitHub Flow
Simplified: main branch + feature branches.

```bash
git checkout -b feature-name
# Work and commit
git push origin feature-name
# Create PR
```

## Trunk-Based Development
Short-lived branches, frequent integration.

```bash
git checkout -b quick-feature
# Small changes
git checkout main
git merge quick-feature
```

## Best Practices
- Choose strategy based on team size
- Document your workflow
- Automate with CI/CD

**Previous:** [â† Branching and Merging](06-branching-merging.md) | **Next:** [Resolving Conflicts â†’](08-resolving-conflicts.md)
