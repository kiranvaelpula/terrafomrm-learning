# Git Tags and Releases
Mark important points in history with tags.

## Tag Types

### Lightweight Tags
```bash
git tag v1.0.0
```

### Annotated Tags
```bash
git tag -a v1.0.0 -m 'Release version 1.0.0'
```

## Tag Operations

```bash
# List tags
git tag
git tag -l 'v1.*'

# Show tag info
git show v1.0.0

# Push tags
git push origin v1.0.0
git push origin --tags

# Delete tag
git tag -d v1.0.0
git push origin --delete v1.0.0
```

## Semantic Versioning
MAJOR.MINOR.PATCH (1.2.3)
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

## Best Practices
- Use annotated tags for releases
- Follow semantic versioning
- Tag after successful deployment

**Previous:** [â† Stash and Cherry-Pick](10-stash-cherry-pick.md) | **Next:** [Pull Requests â†’](12-pull-requests.md)
