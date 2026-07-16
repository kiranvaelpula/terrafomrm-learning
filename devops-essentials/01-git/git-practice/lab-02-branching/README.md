# Lab 2: Branching Workflow

## Objective
Practice feature branch workflow.

## Exercises

### Exercise 1: Create Feature Branch
```bash
git checkout -b feature/new-feature
```

### Exercise 2: Make Changes
```bash
echo 'Feature code' > feature.txt
git add feature.txt
git commit -m 'Add new feature'
```

### Exercise 3: Merge to Main
```bash
git checkout main
git merge feature/new-feature
```

### Exercise 4: Clean Up
```bash
git branch -d feature/new-feature
```

## Success Criteria
- Feature branch created
- Changes merged
- Branch deleted

**Previous:** [â† Lab 1](../lab-01-basics/) | **Next:** [Lab 3 â†’](../lab-03-collaboration/)
