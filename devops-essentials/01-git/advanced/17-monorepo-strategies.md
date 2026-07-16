# Monorepo vs Multi-repo Strategies
Choosing repository organization strategy.

## Monorepo
Single repository for multiple projects.

### Advantages
- Atomic changes across projects
- Simplified dependency management
- Single source of truth

### Disadvantages
- Large repository size
- Complex CI/CD
- Access control challenges

### Tools
- Nx, Turborepo, Lerna
- Git sparse-checkout
- Git LFS for large files

## Multi-repo
Separate repositories per project.

### Advantages
- Smaller repositories
- Independent deployments
- Clear boundaries

### Disadvantages
- Cross-project changes difficult
- Dependency versioning complexity

## Choosing Strategy
Consider team size, project relationships, and tooling.

**Previous:** [â† Performance](16-performance.md) | **Next:** [Security â†’](18-security.md)
