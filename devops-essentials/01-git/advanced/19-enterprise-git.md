# Git in Enterprise
Scale Git for large organizations.

## Centralized Git
- GitLab, GitHub Enterprise, Bitbucket
- LDAP/AD integration
- Audit logging
- Compliance features

## Access Control
```bash
# Team-based permissions
# Branch protection rules
# Required reviews
# CI/CD integration
```

## Backup and Disaster Recovery
```bash
# Mirror repositories
git clone --mirror url backup.git

# Restore from mirror
git clone backup.git restored-repo
```

## Performance at Scale
- Use Git LFS
- Implement sparse checkout
- Repository sharding
- Caching proxies

## Compliance
- Audit logs
- Signed commits
- Branch policies
- Retention policies

**Previous:** [â† Security](18-security.md) | **Next:** [Troubleshooting â†’](20-troubleshooting.md)
