# Create comprehensive Docker intermediate and advanced content
# This script generates all remaining content files

Write-Host "Creating comprehensive Docker content..." -ForegroundColor Cyan

# Function to create file
function Create-ContentFile {
    param(
        [string]$Path,
        [string]$Content
    )
    
    Set-Content -Path $Path -Value $Content -Encoding UTF8
    Write-Host "✓ Created: $Path" -ForegroundColor Green
}

# Networking content
$networkingContent = @"
# Docker Networking

Container networking modes and inter-container communication.

## Overview

Docker networking enables containers to communicate with each other, the host, and external networks. Understanding Docker networking is crucial for building multi-container applications.

## Network Types

### 1. Bridge (Default)

Containers on the same bridge network can communicate.

``````bash
# Default bridge
docker run -d --name web nginx

# Custom bridge
docker network create my-bridge
docker run -d --name web --network my-bridge nginx
docker run -d --name app --network my-bridge myapp
``````

### 2. Host

Container uses host's network directly (no isolation).

``````bash
docker run -d --network host nginx
# nginx accessible on host:80 directly
``````

### 3. None

No networking, complete isolation.

``````bash
docker run -d --network none nginx
``````

### 4. Overlay

For Docker Swarm, connects multiple Docker hosts.

``````bash
docker network create --driver overlay my-overlay
``````

## Practical Examples

### Multi-Container Application

``````bash
# Create network
docker network create app-network

# Database
docker run -d \
  --name db \
  --network app-network \
  -e POSTGRES_PASSWORD=secret \
  postgres:15

# Backend (can access db by name)
docker run -d \
  --name backend \
  --network app-network \
  -e DATABASE_URL=postgresql://postgres:secret@db:5432/mydb \
  mybackend:latest

# Frontend
docker run -d \
  --name frontend \
  --network app-network \
  -p 80:80 \
  myfrontend:latest
``````

### Docker Compose Networking

``````yaml
version: '3.8'

services:
  db:
    image: postgres:15
    networks:
      - backend
    environment:
      POSTGRES_PASSWORD: secret

  api:
    build: ./api
    networks:
      - backend
      - frontend
    depends_on:
      - db

  web:
    build: ./web
    networks:
      - frontend
    ports:
      - "80:80"

networks:
  backend:
  frontend:
``````

## Network Commands

``````bash
# Create network
docker network create my-network

# List networks
docker network ls

# Inspect network
docker network inspect my-network

# Connect running container
docker network connect my-network mycontainer

# Disconnect
docker network disconnect my-network mycontainer

# Remove network
docker network rm my-network

# Prune unused networks
docker network prune
``````

## DNS and Service Discovery

Containers can reach each other by service name:

``````bash
# Container 'web' can ping 'db' directly
docker exec web ping db

# In application code
const dbHost = 'db';  // Not localhost or IP
``````

## Port Mapping

``````bash
# Map container port to host
docker run -p 8080:80 nginx     # host:container

# Random host port
docker run -P nginx

# Specific IP
docker run -p 127.0.0.1:8080:80 nginx

# UDP ports
docker run -p 53:53/udp dnsserver
``````

## Advanced Networking

### Custom Bridge with Subnet

``````bash
docker network create \
  --driver bridge \
  --subnet 172.25.0.0/16 \
  --gateway 172.25.0.1 \
  custom-bridge
``````

### Static IP Assignment

``````bash
docker run -d \
  --name web \
  --network custom-bridge \
  --ip 172.25.0.10 \
  nginx
``````

### Network Aliases

``````bash
docker run -d \
  --name web \
  --network my-network \
  --network-alias webapp \
  --network-alias www \
  nginx
``````

## Best Practices

1. **Use custom bridge networks**
2. **Isolate sensitive services**
3. **Use network aliases for flexibility**
4. **Document port mappings**
5. **Avoid host network in production**

## Troubleshooting

``````bash
# Test connectivity
docker exec web ping db

# Check network configuration
docker network inspect my-network

# View container's network
docker inspect mycontainer | grep -A 20 NetworkSettings
``````

**Next:** [Docker Compose →](09-docker-compose.md)
"@

Create-ContentFile -Path "intermediate/08-networking.md" -Content $networkingContent

# Docker Compose content
$composeContent = @"
# Docker Compose

Define and run multi-container applications.

## Overview

Docker Compose is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure application services.

## Why Docker Compose?

**Without Compose:**
``````bash
# Start each container manually
docker network create myapp
docker run -d --name db --network myapp postgres
docker run -d --name redis --network myapp redis
docker run -d --name api --network myapp -p 3000:3000 myapi
docker run -d --name web --network myapp -p 80:80 myweb
``````

**With Compose:**
``````bash
docker-compose up -d
``````

## Basic Example

### docker-compose.yml

``````yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
    networks:
      - frontend

  api:
    build: ./api
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:secret@db:5432/mydb
    networks:
      - frontend
      - backend
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - backend

volumes:
  db-data:

networks:
  frontend:
  backend:
``````

## Common Commands

``````bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose stop

# Stop and remove
docker-compose down

# View logs
docker-compose logs
docker-compose logs -f api

# Scale services
docker-compose up -d --scale api=3

# Rebuild images
docker-compose build
docker-compose up -d --build

# Execute command
docker-compose exec api npm test

# View running services
docker-compose ps
``````

## Real-World Examples

### Full-Stack Application

``````yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/src:/app/src
    environment:
      - REACT_APP_API_URL=http://localhost:4000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "4000:4000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://cache:6379
    volumes:
      - ./backend:/app
      - /app/node_modules
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
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  cache:
    image: redis:alpine
    ports:
      - "6379:6379"

volumes:
  postgres-data:
``````

### Development Environment

``````yaml
version: '3.8'

services:
  app:
    build:
      context: .
      target: development
    volumes:
      - .:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    command: npm run dev
    environment:
      - NODE_ENV=development
      - CHOKIDAR_USEPOLLING=true

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: dev
    ports:
      - "5432:5432"
    volumes:
      - db-dev:/var/lib/postgresql/data

volumes:
  db-dev:
``````

## Advanced Features

### Environment Variables

``````yaml
services:
  api:
    environment:
      - DEBUG=true
      - API_KEY=$${API_KEY}  # From shell
    env_file:
      - .env
      - .env.production
``````

**.env file:**
``````
DATABASE_URL=postgresql://localhost:5432/mydb
REDIS_URL=redis://localhost:6379
API_KEY=secret-key
``````

### Build Arguments

``````yaml
services:
  app:
    build:
      context: .
      args:
        - NODE_VERSION=18
        - BUILD_ENV=production
``````

### Health Checks

``````yaml
services:
  api:
    image: myapi
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
``````

### Extending Services

**base.yml:**
``````yaml
services:
  app:
    image: myapp
    environment:
      - LOG_LEVEL=info
``````

**docker-compose.yml:**
``````yaml
services:
  app:
    extends:
      file: base.yml
      service: app
    ports:
      - "3000:3000"
``````

### Profiles

``````yaml
services:
  app:
    image: myapp

  db:
    image: postgres
    profiles:
      - debug

  adminer:
    image: adminer
    profiles:
      - debug
    ports:
      - "8080:8080"
``````

``````bash
# Run without debug services
docker-compose up

# Run with debug services
docker-compose --profile debug up
``````

## Best Practices

1. **Use version control for compose files**
2. **Keep secrets out of compose files**
3. **Use .env for environment-specific values**
4. **Name your networks and volumes**
5. **Use depends_on with health checks**
6. **Pin image versions**

## Multiple Environment Files

``````bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
``````

**docker-compose.dev.yml:**
``````yaml
services:
  app:
    build:
      target: development
    volumes:
      - .:/app
    command: npm run dev
``````

**docker-compose.prod.yml:**
``````yaml
services:
  app:
    build:
      target: production
    restart: always
``````

## Troubleshooting

``````bash
# View logs
docker-compose logs -f

# Check service status
docker-compose ps

# Validate compose file
docker-compose config

# Remove everything
docker-compose down -v --remove-orphans

# Rebuild specific service
docker-compose build --no-cache api
docker-compose up -d api
``````

**Next:** [Environment & Configuration →](10-environment-config.md)
"@

Create-ContentFile -Path "intermediate/09-docker-compose.md" -Content $composeContent

Write-Host "`n✓ Docker intermediate content created successfully!" -ForegroundColor Green
Write-Host "Files created: 08-networking.md, 09-docker-compose.md" -ForegroundColor Cyan
"@
</invoke>