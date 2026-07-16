# Advanced Git Operations
Master advanced Git commands and techniques.

## Git Filter-Branch
Rewrite repository history.

```bash
# Remove file from history
git filter-branch --tree-filter 'rm -f passwords.txt' HEAD
```

## Git Subtree
Manage project dependencies.

```bash
# Add subtree
git subtree add --prefix=lib/project url main

# Pull updates
git subtree pull --prefix=lib/project url main
```

## Git Submodules
Include other repositories.

```bash
# Add submodule
git submodule add url path

# Clone with submodules
git clone --recursive url

# Update submodules
git submodule update --init --recursive
```

## Git Bisect
Binary search for bug introduction.

```bash
git bisect start
git bisect bad
git bisect good commit-hash
# Test each commit
git bisect good/bad
git bisect reset
```

**Previous:** [â† Git Internals](13-git-internals.md) | **Next:** [Git Hooks â†’](15-git-hooks.md)
