# Pull Requests and Code Review
Collaborate effectively with pull requests.

## Creating Pull Requests

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m 'Add new feature'

# 3. Push to remote
git push origin feature/new-feature

# 4. Create PR on GitHub/GitLab
```

## PR Best Practices
1. Keep PRs small and focused
2. Write clear descriptions
3. Link to issues
4. Request specific reviewers
5. Respond to feedback promptly

## Code Review Process
- Review code, not people
- Ask questions, don't demand changes
- Provide constructive feedback
- Approve or request changes

## After Merge
```bash
git checkout main
git pull origin main
git branch -d feature/new-feature
```

**Previous:** [â† Tags and Releases](11-tags-releases.md) | **Next:** [Interview Questions â†’](interview-questions-intermediate.md)
