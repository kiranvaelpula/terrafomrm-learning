# Git Internals
Understanding Git's internal architecture.

## Git Objects
- **Blob**: File contents
- **Tree**: Directory structure  
- **Commit**: Snapshot with metadata
- **Tag**: Named reference

## The .git Directory
```
.git/
â”œâ”€â”€ objects/    # All Git objects
â”œâ”€â”€ refs/       # Branch/tag references
â”œâ”€â”€ HEAD        # Current branch pointer
â””â”€â”€ config      # Repository configuration
```

## How Git Stores Data
Git uses SHA-1 hashes to identify objects.

```bash
# View object
git cat-file -p commit-hash

# View object type
git cat-file -t hash
```

## Refs and HEAD
```bash
# View HEAD
cat .git/HEAD

# View branch ref
cat .git/refs/heads/main
```

**Previous:** [â† Interview Questions](../intermediate/interview-questions-intermediate.md) | **Next:** [Advanced Operations â†’](14-advanced-operations.md)
