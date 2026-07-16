# PowerShell script to create comprehensive Docker intermediate and advanced content

# Intermediate Topics
$intermediateContent = @{
    "06-multistage-builds.md" = @"
# Multi-stage Docker Builds

Optimize images by using multiple build stages to reduce final image size.

## Overview

Multi-stage builds allow you to use multiple FROM statements in a single Dockerfile. Each FROM instruction can use a different base, and each begins a new stage of the build. You can selectively copy artifacts from one stage to another, leaving behind everything you don't want in the final image.

## Why Multi-stage Builds?

**Without Multi-stage:**
- Build dependencies included in final image
- Larger image sizes (GBs instead of MBs)
- More attack surface
- Slower deployment

**With Multi-stage:**
- Only runtime dependencies in final image
- Smaller images (10x-50x reduction)
- Better security
- Faster deployment

## Basic Example

### Node.js Application

``````dockerfile
# Stage 1: Build
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:18-alpine
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY package*.json ./
EXPOSE 3000
CMD ["node", "dist/index.js"]
``````

**Result:**
- Build stage: 1.2GB (includes dev dependencies, build tools)
- Final image: 150MB (only production artifacts)

## Real-World Examples

### React Application

``````dockerfile
# Build stage
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
``````

### Go Application

``````dockerfile
# Build stage
FROM golang:1.21 AS build
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o myapp

# Production stage
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=build /app/myapp .
EXPOSE 8080
CMD ["./myapp"]
``````

**Size comparison:**
- Build stage: 800MB
- Final image: 15MB

### Java Spring Boot

``````dockerfile
# Build stage
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

# Production stage
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
``````

## Advanced Techniques

### Multiple Build Stages

``````dockerfile
# Stage 1: Dependencies
FROM node:18 AS dependencies
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Test
FROM build AS test
RUN npm run test

# Stage 4: Production
FROM node:18-alpine
WORKDIR /app
COPY --from=dependencies /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package*.json ./
CMD ["node", "dist/index.js"]
``````

### Named Stages for Flexibility

``````dockerfile
FROM node:18 AS base
WORKDIR /app
COPY package*.json ./

FROM base AS development
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]

FROM base AS production-deps
RUN npm ci --only=production

FROM base AS build
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine AS production
WORKDIR /app
COPY --from=production-deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
CMD ["node", "dist/index.js"]
``````

Build specific stage:
``````bash
# Development
docker build --target development -t myapp:dev .

# Production
docker build --target production -t myapp:prod .
``````

## Best Practices

### 1. Order Stages by Frequency of Change

``````dockerfile
# Dependencies change rarely
FROM node:18 AS deps
COPY package*.json ./
RUN npm ci

# Source code changes frequently
FROM deps AS build
COPY . .
RUN npm run build
``````

### 2. Use Specific Tags

``````dockerfile
# Bad: Version changes unexpectedly
FROM node:latest

# Good: Specific version
FROM node:18.17-alpine
``````

### 3. Copy Only What You Need

``````dockerfile
# Copy only built artifacts
COPY --from=build /app/dist ./dist

# Not the entire directory
COPY --from=build /app .
``````

### 4. Leverage Build Cache

``````dockerfile
# Install dependencies first (cached if unchanged)
COPY package*.json ./
RUN npm install

# Copy source code after (changes frequently)
COPY . .
``````

### 5. Use .dockerignore

``````
node_modules
.git
.env
*.log
coverage
.vscode
``````

## Common Patterns

### Python with Poetry

``````dockerfile
FROM python:3.11 AS build
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-dev

FROM python:3.11-slim
WORKDIR /app
COPY --from=build /app/.venv ./.venv
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "main.py"]
``````

### .NET Application

``````dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app
COPY *.csproj ./
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o out

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/out .
ENTRYPOINT ["dotnet", "MyApp.dll"]
``````

## Size Comparison Examples

| Application | Single-stage | Multi-stage | Reduction |
|-------------|--------------|-------------|-----------|
| Node.js API | 950MB | 120MB | 87% |
| React SPA | 1.2GB | 25MB | 98% |
| Go Service | 800MB | 15MB | 98% |
| Java Spring | 650MB | 200MB | 69% |
| Python Flask | 900MB | 150MB | 83% |

## Troubleshooting

### Build Fails at Copy Stage

``````bash
# Check what files exist in build stage
docker build --target build -t debug .
docker run --rm debug ls -la /app
``````

### Inspect Intermediate Stages

``````bash
# Build and tag each stage
docker build --target build -t myapp:build .
docker build --target production -t myapp:prod .

# Inspect each
docker run --rm myapp:build du -sh /app/*
``````

### Debug with Shell

``````dockerfile
FROM node:18 AS build
WORKDIR /app
COPY . .
RUN npm run build
# Add temporary shell for debugging
RUN ls -la /app/dist
CMD ["/bin/bash"]
``````

## Interview Questions

**Q: What is the main benefit of multi-stage builds?**
A: Reduced image size by excluding build dependencies and tools from the final image.

**Q: Can you reference artifacts from any stage?**
A: Yes, using `COPY --from=<stage-name>` or `COPY --from=<stage-index>`.

**Q: How do you build only a specific stage?**
A: Use `docker build --target <stage-name> -t image:tag .`

**Q: Do all stages run during build?**
A: Only stages needed for the target stage and those referenced with `--from` are built.

**Next:** [Volumes →](07-volumes.md)
"@

    "07-volumes.md" = @"
# Docker Volumes

Persist and share data between containers and the host system.

## Overview

Volumes are the preferred mechanism for persisting data generated by and used by Docker containers. Unlike bind mounts, volumes are completely managed by Docker.

## Why Use Volumes?

**Problems with Container Storage:**
- Data lost when container is removed
- Hard to move data between containers
- Performance issues on Windows/Mac
- Tight coupling with host filesystem

**Benefits of Volumes:**
- Data persists after container deletion
- Easy to backup and migrate
- Better performance on all platforms
- Managed by Docker
- Safe to share between containers

## Volume Types

### 1. Named Volumes (Recommended)

Managed by Docker, stored in Docker's storage directory.

``````bash
# Create volume
docker volume create my-data

# Use in container
docker run -v my-data:/app/data nginx

# List volumes
docker volume ls

# Inspect volume
docker volume inspect my-data

# Remove volume
docker volume rm my-data
``````

**Output of inspect:**
``````json
[
    {
        "Name": "my-data",
        "Driver": "local",
        "Mountpoint": "/var/lib/docker/volumes/my-data/_data",
        "Labels": {},
        "Scope": "local"
    }
]
``````

### 2. Anonymous Volumes

Created automatically, harder to reference.

``````bash
# Docker creates random name
docker run -v /app/data nginx

# List shows random name
docker volume ls
# DRIVER    VOLUME NAME
# local     f4d3b5c2a1e8...
``````

### 3. Bind Mounts

Mount host directory directly.

``````bash
# Linux/Mac
docker run -v /host/path:/container/path nginx

# Windows
docker run -v C:\host\path:/container/path nginx

# Read-only mount
docker run -v /host/path:/container/path:ro nginx
``````

### 4. tmpfs Mounts (Linux only)

Store in host memory, not persisted.

``````bash
docker run --tmpfs /app/cache:rw,size=100m nginx
``````

## Practical Examples

### PostgreSQL Database

``````bash
# Create volume
docker volume create postgres-data

# Run PostgreSQL with volume
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=secret \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:15

# Data persists even after container removal
docker rm -f postgres
docker run -d \
  --name postgres-new \
  -e POSTGRES_PASSWORD=secret \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:15
# Previous data still available
``````

### MongoDB with Data and Config

``````bash
# Create volumes
docker volume create mongo-data
docker volume create mongo-config

# Run MongoDB
docker run -d \
  --name mongodb \
  -v mongo-data:/data/db \
  -v mongo-config:/data/configdb \
  mongo:7
``````

### Nginx with Custom Config

``````bash
# Bind mount for development
docker run -d \
  --name web \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v $(pwd)/html:/usr/share/nginx/html:ro \
  -p 80:80 \
  nginx
``````

### Node.js Development

``````bash
# Bind mount source code for live reload
docker run -d \
  --name node-dev \
  -v $(pwd):/app \
  -v /app/node_modules \
  -w /app \
  -p 3000:3000 \
  node:18 \
  npm run dev
``````

**Note:** `-v /app/node_modules` creates anonymous volume to prevent host overwriting.

## Docker Compose with Volumes

### Named Volumes

``````yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: secret

  app:
    image: myapp
    volumes:
      - app-data:/app/data
    depends_on:
      - db

volumes:
  postgres-data:
  app-data:
``````

### Bind Mounts for Development

``````yaml
version: '3.8'

services:
  web:
    build: .
    volumes:
      - ./src:/app/src           # Source code
      - ./public:/app/public     # Static files
      - /app/node_modules        # Preserve node_modules
    ports:
      - "3000:3000"
    command: npm run dev
``````

### Sharing Volumes Between Services

``````yaml
version: '3.8'

services:
  app:
    image: myapp
    volumes:
      - shared-data:/data

  backup:
    image: backup-tool
    volumes:
      - shared-data:/data:ro  # Read-only access

volumes:
  shared-data:
``````

## Volume Management Commands

``````bash
# Create volume
docker volume create my-volume

# Create with options
docker volume create --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw \
  --opt device=:/path/to/share \
  my-nfs-volume

# List volumes
docker volume ls

# Filter volumes
docker volume ls --filter dangling=true

# Inspect volume
docker volume inspect my-volume

# Remove volume
docker volume rm my-volume

# Remove all unused volumes
docker volume prune

# Force remove (careful!)
docker volume prune -af

# Copy data from container to volume
docker cp mycontainer:/app/data/. /var/lib/docker/volumes/my-volume/_data/
``````

## Backup and Restore

### Backup Volume Data

``````bash
# Method 1: Using tar
docker run --rm \
  -v postgres-data:/data \
  -v $(pwd):/backup \
  ubuntu \
  tar czf /backup/postgres-backup.tar.gz -C /data .

# Method 2: Using postgres dump
docker exec postgres pg_dumpall -U postgres > backup.sql
``````

### Restore Volume Data

``````bash
# Restore from tar
docker run --rm \
  -v postgres-data:/data \
  -v $(pwd):/backup \
  ubuntu \
  tar xzf /backup/postgres-backup.tar.gz -C /data

# Restore postgres dump
docker exec -i postgres psql -U postgres < backup.sql
``````

### Automated Backup Script

``````bash
#!/bin/bash
VOLUME_NAME="postgres-data"
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

docker run --rm \
  -v $VOLUME_NAME:/data \
  -v $BACKUP_DIR:/backup \
  ubuntu \
  tar czf /backup/${VOLUME_NAME}_${DATE}.tar.gz -C /data .

echo "Backup completed: ${VOLUME_NAME}_${DATE}.tar.gz"

# Keep only last 7 backups
ls -t $BACKUP_DIR | tail -n +8 | xargs -I {} rm $BACKUP_DIR/{}
``````

## Best Practices

### 1. Use Named Volumes for Production

``````bash
# Good
docker volume create db-data
docker run -v db-data:/data postgres

# Avoid for production
docker run -v /host/path:/data postgres
``````

### 2. Never Store Volumes in Container Layer

``````dockerfile
# Bad: Data lost on container removal
RUN mkdir /data
# No volume specified

# Good: Use VOLUME instruction
VOLUME /data
``````

### 3. Use Read-Only Mounts When Possible

``````bash
docker run -v config.json:/app/config.json:ro myapp
``````

### 4. Separate Data and Config

``````bash
docker run \
  -v app-data:/app/data \
  -v app-config:/app/config:ro \
  myapp
``````

### 5. Use Volume Labels

``````bash
docker volume create \
  --label project=myapp \
  --label environment=production \
  myapp-prod-data
``````

## Performance Considerations

### Volume Drivers

``````bash
# Default local driver (good performance)
docker volume create --driver local my-volume

# NFS for shared storage (network latency)
docker volume create --driver local \
  --opt type=nfs \
  --opt o=addr=nfs-server,rw \
  --opt device=:/path/to/dir \
  nfs-volume

# Cloud storage (AWS EBS, Azure Disk)
docker volume create --driver rexray/ebs \
  --opt size=10 \
  cloud-volume
``````

### Optimize for Windows/Mac

``````yaml
# Use delegated/cached for better performance
services:
  app:
    volumes:
      - ./src:/app/src:delegated  # Host writes are delayed
      - ./data:/app/data:cached   # Container writes are delayed
``````

## Troubleshooting

### Volume Not Mounting

``````bash
# Check if volume exists
docker volume ls | grep my-volume

# Inspect volume
docker volume inspect my-volume

# Check container mounts
docker inspect mycontainer | grep -A 10 Mounts
``````

### Permission Issues

``````bash
# Check file ownership in volume
docker run --rm -v my-volume:/data alpine ls -la /data

# Fix permissions
docker run --rm -v my-volume:/data alpine chown -R 1000:1000 /data
``````

### Volume Full

``````bash
# Check volume size
docker system df -v

# Clean up unused volumes
docker volume prune
``````

## Interview Questions

**Q: What's the difference between volumes and bind mounts?**
A: Volumes are managed by Docker, stored in Docker's directory, and work consistently across platforms. Bind mounts directly mount host filesystem paths and have host-specific paths.

**Q: How do you backup a Docker volume?**
A: Run a container that mounts both the volume and a backup location, then use tar or copy commands to archive the data.

**Q: Do volumes persist after container deletion?**
A: Yes, named volumes persist until explicitly removed with `docker volume rm`.

**Q: Can multiple containers use the same volume?**
A: Yes, multiple containers can mount and access the same volume simultaneously.

**Next:** [Networking →](08-networking.md)
"@
}

# Create intermediate files
foreach ($file in $intermediateContent.Keys) {
    $path = "devops-essentials/02-docker/intermediate/$file"
    Set-Content -Path $path -Value $intermediateContent[$file] -Encoding UTF8
    Write-Host "Created: $path" -ForegroundColor Green
}

Write-Host "`n✓ Docker intermediate content created successfully!" -ForegroundColor Cyan
"@
</invoke>