# Git Hooks
Automate workflows with Git hooks.

## Hook Types
- **pre-commit**: Before commit
- **pre-push**: Before push
- **post-merge**: After merge
- **commit-msg**: Validate commit message

## Creating Hooks
```bash
# Location
.git/hooks/

# Make executable
chmod +x .git/hooks/pre-commit
```

## Example: Pre-commit Hook
```bash
#!/bin/sh
# Run tests before commit
npm test
if [ \True -ne 0 ]; then
    echo "Tests failed"
    exit 1
fi
```

## Example: Commit-msg Hook
```bash
#!/bin/sh
# Validate commit message format
commit_msg=\
if ! echo "\" | grep -qE "^(feat|fix|docs):"; then
    echo "Invalid commit message format"
    exit 1
fi
```

**Previous:** [â† Advanced Operations](14-advanced-operations.md) | **Next:** [Performance â†’](16-performance.md)
