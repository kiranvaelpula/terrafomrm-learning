# Lab 1: Git Basics

## Objective
Learn fundamental Git operations by creating your first repository.

## Prerequisites
- Git installed
- Text editor

## Exercises

### Exercise 1: Initialize Repository
```bash
mkdir my-first-repo
cd my-first-repo
git init
```

### Exercise 2: Create and Commit Files
```bash
echo '# My Project' > README.md
git add README.md
git commit -m 'Initial commit'
```

### Exercise 3: Make Changes
```bash
echo 'Description' >> README.md
git add README.md
git commit -m 'Add description'
```

### Exercise 4: View History
```bash
git log
git log --oneline
```

## Success Criteria
- Repository initialized
- Multiple commits made
- Can view history

**Next:** [Lab 2: Branching â†’](../lab-02-branching/)
