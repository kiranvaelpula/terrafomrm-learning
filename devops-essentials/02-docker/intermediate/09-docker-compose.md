# Docker Compose

Define and run multi-container applications.

## Overview

Docker Compose is a tool for defining and running multi-container Docker applications using a YAML file.

## Basic Example

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html

  api:
    build: ./api
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:secret@db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# Stop and remove
docker-compose down

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale api=3

# Rebuild
docker-compose up -d --build

# Execute command
docker-compose exec api npm test

# View running services
docker-compose ps
```

## Full-Stack Example

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:4000

  backend:
    build: ./backend
    ports:
      - "4000:4000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://cache:6379
    depends_on:
      - db
      - cache

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - postgres-data:/var/lib/postgresql/data

  cache:
    image: redis:alpine

volumes:
  postgres-data:
```

## Environment Variables

```yaml
services:
  api:
    environment:
      - DEBUG=true
      - API_KEY=${API_KEY}  # From shell
    env_file:
      - .env
```

**.env file:**
```
DATABASE_URL=postgresql://localhost:5432/mydb
REDIS_URL=redis://localhost:6379
API_KEY=secret-key
```

## Health Checks

```yaml
services:
  api:
    image: myapi
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Multiple Environments

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

**docker-compose.dev.yml:**
```yaml
services:
  app:
    volumes:
      - .:/app
    command: npm run dev
```

**docker-compose.prod.yml:**
```yaml
services:
  app:
    restart: always
    command: npm start
```

## Networks

```yaml
services:
  frontend:
    networks:
      - frontend-net

  api:
    networks:
      - frontend-net
      - backend-net

  db:
    networks:
      - backend-net

networks:
  frontend-net:
  backend-net:
```

## Best Practices

1. Use version control for compose files
2. Keep secrets out of compose files
3. Use .env for environment-specific values
4. Name your networks and volumes
5. Use depends_on with health checks
6. Pin image versions

## Troubleshooting

```bash
# View logs
docker-compose logs -f api

# Check service status
docker-compose ps

# Validate compose file
docker-compose config

# Remove everything
docker-compose down -v --remove-orphans

# Rebuild specific service
docker-compose build --no-cache api
docker-compose up -d api
```

**Next:** [Environment & Configuration →](10-environment-config.md)
