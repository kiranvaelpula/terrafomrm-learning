# Git Security Best Practices
Secure your Git workflow.

## Never Commit Secrets
```bash
# Use .gitignore
echo '.env' >> .gitignore
echo 'secrets/' >> .gitignore
```

## Remove Committed Secrets
```bash
# Use BFG Repo-Cleaner
bfg --replace-text passwords.txt

# Or filter-branch
git filter-branch --tree-filter 'rm -f secret.key' HEAD

# Force push
git push --force
```

## GPG Signing
Sign commits cryptographically.

```bash
# Generate GPG key
gpg --gen-key

# Configure Git
git config --global user.signingkey KEY_ID
git config --global commit.gpgsign true

# Sign commit
git commit -S -m 'message'
```

## Branch Protection
- Require pull request reviews
- Require status checks
- Enforce signed commits
- Restrict force pushes

**Previous:** [â† Monorepo Strategies](17-monorepo-strategies.md) | **Next:** [Enterprise Git â†’](19-enterprise-git.md)
