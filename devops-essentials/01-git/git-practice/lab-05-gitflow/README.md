# Lab 5: GitFlow Implementation

## Objective
Implement complete GitFlow workflow.

## Exercises

### Exercise 1: Setup Branches
```bash
git checkout -b develop
git push origin develop
```

### Exercise 2: Feature Development
```bash
git checkout -b feature/user-auth develop
# Develop feature
git checkout develop
git merge feature/user-auth
```

### Exercise 3: Release Branch
```bash
git checkout -b release/1.0.0 develop
# Bug fixes only
git checkout main
git merge release/1.0.0
git tag v1.0.0
```

### Exercise 4: Hotfix
```bash
git checkout -b hotfix/critical-bug main
# Fix bug
git checkout main
git merge hotfix/critical-bug
git checkout develop
git merge hotfix/critical-bug
```

## Success Criteria
- GitFlow branches created
- Feature merged to develop
- Release tagged on main
- Hotfix applied to both branches

**Previous:** [â† Lab 4](../lab-04-advanced/)
