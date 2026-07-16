# Git Interview Questions - Intermediate Level

## Branching Questions

### Q1: What is a Git branch?
**Answer:** A lightweight movable pointer to a commit that allows parallel development without affecting the main codebase.

### Q2: Difference between merge and rebase?
**Answer:** Merge creates a merge commit preserving history. Rebase replays commits creating linear history. Never rebase shared branches.

### Q3: How to resolve merge conflicts?
**Answer:** 
1. git status to identify conflicts
2. Edit files removing conflict markers
3. git add resolved files
4. git commit to complete merge

## Workflow Questions

### Q4: Explain GitFlow workflow
**Answer:** Uses main (production), develop (integration), feature/* (new features), hotfix/* (emergency fixes), and release/* (release prep) branches.

### Q5: What is cherry-pick?
**Answer:** Applies specific commits from one branch to another without merging entire branch.

### Q6: When to use git stash?
**Answer:** Temporarily save uncommitted changes when switching branches or pulling updates.

## Tag Questions

### Q7: Difference between lightweight and annotated tags?
**Answer:** Lightweight is just a pointer. Annotated includes tagger name, email, date, and message - recommended for releases.

### Q8: How to tag a specific commit?
**Answer:** \git tag -a v1.0.0 commit-hash -m 'message'\

## Pull Request Questions

### Q9: What makes a good PR?
**Answer:** Small focused changes, clear description, linked issues, passing tests, responsive to feedback.

### Q10: How to update PR with new commits?
**Answer:** Make changes locally, commit, and push to same branch. PR updates automatically.

**Previous:** [â† Pull Requests](12-pull-requests.md) | **Next:** [Git Internals â†’](../advanced/13-git-internals.md)
