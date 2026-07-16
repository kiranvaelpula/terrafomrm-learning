# Git Performance Optimization
Optimize Git for large repositories.

## Shallow Clone
```bash
git clone --depth 1 url
```

## Sparse Checkout
Checkout only specific directories.

```bash
git sparse-checkout init
git sparse-checkout set dir1 dir2
```

## Git LFS
Handle large files.

```bash
git lfs install
git lfs track '*.psd'
git add .gitattributes
```

## Repository Maintenance
```bash
# Garbage collection
git gc

# Aggressive GC
git gc --aggressive

# Optimize repository
git repack -a -d
```

## Configuration
```bash
# Increase cache
git config --global core.preloadindex true
git config --global core.fscache true
```

**Previous:** [â† Git Hooks](15-git-hooks.md) | **Next:** [Monorepo Strategies â†’](17-monorepo-strategies.md)
