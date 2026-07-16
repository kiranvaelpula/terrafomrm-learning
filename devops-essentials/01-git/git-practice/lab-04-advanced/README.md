# Lab 4: Advanced Operations

## Objective
Practice rebase, stash, and cherry-pick.

## Exercises

### Exercise 1: Rebase
```bash
git checkout feature-branch
git rebase main
```

### Exercise 2: Stash Changes
```bash
echo 'WIP' >> file.txt
git stash
git stash list
git stash pop
```

### Exercise 3: Cherry-pick
```bash
git cherry-pick commit-hash
```

## Success Criteria
- Successfully rebased branch
- Used stash for WIP
- Cherry-picked specific commit

**Previous:** [â† Lab 3](../lab-03-collaboration/) | **Next:** [Lab 5 â†’](../lab-05-gitflow/)
