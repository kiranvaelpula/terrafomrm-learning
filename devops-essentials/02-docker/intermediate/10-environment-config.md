# Environment Configuration

Manage environment variables and configuration in Docker containers.

## Overview

Environment variables are the primary way to configure containerized applications without rebuilding images.

## Setting Environment Variables

### 1. Command Line

```bash
# Single variable
docker run -e DATABASE_URL=postgresql://localhost/mydb nginx

# Multiple variables
docker run \
  -e NODE_ENV=production \
  -e PORT=3000 \
  -e DATABASE_URL=postgresql://localhost/mydb \
  myapp
```

### 2. Environment File

**.env:**
```
NODE_ENV=production
DATABASE_URL=postgresql://localhost:5432/mydb
REDIS_URL=redis://localhost:6379
API_KEY=secret-key-here
JWT_SECRET=super-secret
LOG_LEVEL=info
```

```bash
docker run --env-file .env myapp
```

### 3. Dockerfile

```dockerfile
FROM node:18
ENV NODE_ENV=production
ENV PORT=3000
WORKDIR /app
COPY . .
CMD ["node", "server.js"]
```

### 4. Docker Compose

```yaml
version: '3.8'

services:
  app:
    image: myapp
    environment:
      - NODE_ENV=production
      - PORT=3000
      - DATABASE_URL=postgresql://db:5432/mydb
    env_file:
      - .env
```

## Best Practices

### 1. Never Commit Secrets

**.gitignore:**
```
.env
.env.local
.env.production
*.key
*.pem
secrets/
```

### 2. Use Default Values

```javascript
const port = process.env.PORT || 3000;
const dbUrl = process.env.DATABASE_URL || 'postgresql://localhost/mydb';
```

### 3. Validate Required Variables

```javascript
const requiredEnvVars = ['DATABASE_URL', 'API_KEY'];

requiredEnvVars.forEach(varName => {
  if (!process.env[varName]) {
    throw new Error(`Missing: ${varName}`);
  }
});
```

## Multi-Environment Setup

**docker-compose.yml:**
```yaml
services:
  app:
    image: myapp
    env_file:
      - .env.common
      - .env.${ENV:-development}
```

**.env.development:**
```
NODE_ENV=development
DATABASE_URL=postgresql://localhost:5432/dev_db
DEBUG=true
```

**.env.production:**
```
NODE_ENV=production
DATABASE_URL=postgresql://prod-db:5432/prod_db
DEBUG=false
```

```bash
# Development
ENV=development docker-compose up

# Production
ENV=production docker-compose up
```

## Real-World Example

```yaml
services:
  app:
    build: .
    environment:
      - NODE_ENV=production
      - PORT=3000
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/myapp
      - REDIS_URL=redis://cache:6379
      - JWT_SECRET=${JWT_SECRET}
      - STRIPE_API_KEY=${STRIPE_API_KEY}
    env_file:
      - .env.production
```

## Debugging

```bash
# View environment variables
docker exec mycontainer env

# Specific variable
docker exec mycontainer printenv DATABASE_URL

# Using docker inspect
docker inspect mycontainer | grep -A 20 "Env"
```

## Security

1. Never log sensitive env vars
2. Use secrets management for production
3. Rotate secrets regularly
4. Limit access to .env files

**Next:** [Docker Registry →](11-registry.md)
