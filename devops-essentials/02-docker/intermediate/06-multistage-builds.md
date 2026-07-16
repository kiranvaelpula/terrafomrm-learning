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

```dockerfile
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
```

**Result:**
- Build stage: 1.2GB (includes dev dependencies, build tools)
- Final image: 150MB (only production artifacts)

## Real-World Examples

### React Application

```dockerfile
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
```

### Go Application

```dockerfile
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
```

**Size comparison:**
- Build stage: 800MB
- Final image: 15MB

### Java Spring Boot

```dockerfile
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
```

## Advanced Techniques

### Multiple Build Stages

```dockerfile
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
```

### Named Stages for Flexibility

```dockerfile
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
```

Build specific stage:
```bash
# Development
docker build --target development -t myapp:dev .

# Production
docker build --target production -t myapp:prod .
```

## Best Practices

### 1. Order Stages by Frequency of Change

```dockerfile
# Dependencies change rarely
FROM node:18 AS deps
COPY package*.json ./
RUN npm ci

# Source code changes frequently
FROM deps AS build
COPY . .
RUN npm run build
```

### 2. Use Specific Tags

```dockerfile
# Bad: Version changes unexpectedly
FROM node:latest

# Good: Specific version
FROM node:18.17-alpine
```

### 3. Copy Only What You Need

```dockerfile
# Copy only built artifacts
COPY --from=build /app/dist ./dist

# Not the entire directory
COPY --from=build /app .
```

### 4. Leverage Build Cache

```dockerfile
# Install dependencies first (cached if unchanged)
COPY package*.json ./
RUN npm install

# Copy source code after (changes frequently)
COPY . .
```

### 5. Use .dockerignore

```
node_modules
.git
.env
*.log
coverage
.vscode
```

## Common Patterns

### Python with Poetry

```dockerfile
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
```

### .NET Application

```dockerfile
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
```

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

```bash
# Check what files exist in build stage
docker build --target build -t debug .
docker run --rm debug ls -la /app
```

### Inspect Intermediate Stages

```bash
# Build and tag each stage
docker build --target build -t myapp:build .
docker build --target production -t myapp:prod .

# Inspect each
docker run --rm myapp:build du -sh /app/*
```

### Debug with Shell

```dockerfile
FROM node:18 AS build
WORKDIR /app
COPY . .
RUN npm run build
# Add temporary shell for debugging
RUN ls -la /app/dist
CMD ["/bin/bash"]
```

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
