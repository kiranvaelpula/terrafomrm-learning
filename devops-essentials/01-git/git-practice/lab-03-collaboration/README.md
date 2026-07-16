# Lab 3: Collaboration with Remotes

## Objective
Learn remote repository operations.

## Exercises

### Exercise 1: Clone Repository
```bash
git clone https://github.com/user/repo.git
```

### Exercise 2: Create Feature Branch
```bash
git checkout -b feature/collaboration
echo 'New feature' > collab.txt
git add collab.txt
git commit -m 'Add collaboration feature'
```

### Exercise 3: Push Branch
```bash
git push origin feature/collaboration
```

### Exercise 4: Pull Updates
```bash
git checkout main
git pull origin main
```

## Success Criteria
- Repository cloned
- Branch pushed to remote
- Updates pulled successfully

**Previous:** [â† Lab 2](../lab-02-branching/) | **Next:** [Lab 4 â†’](../lab-04-advanced/)
