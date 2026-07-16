# Docker Image Optimization

Techniques to minimize image size and improve build performance.

## Overview

Optimizing Docker images reduces storage costs, speeds up deployment, and improves security by minimizing attack surface.

## Image Size Optimization

### 1. Use Minimal Base Images

```dockerfile
# Bad: Full OS (1.1GB)
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3
COPY app.py .
CMD ["python3", "app.py"]

# Better: Python slim (180MB)
FROM python:3.11-slim
COPY app.py .
CMD ["python", "app.py"]

# Best: Alpine (50MB)
FROM python:3.11-alpine
COPY app.py .
CMD ["python", "app.py"]

# Minimal: Distroless (25MB)
FROM gcr.io/distroless/python3
COPY app.py .
CMD ["app.py"]
```

### 2. Multi-stage Builds

```dockerfile
# Before: 800MB
FROM golang:1.21
WORKDIR /app
COPY . .
RUN go build -o myapp
CMD ["./myapp"]

# After: 15MB
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -o myapp

FROM alpine:latest
COPY --from=builder /app/myapp /myapp
CMD ["/myapp"]
```

### 3. Minimize Layers

```dockerfile
# Bad: Many layers
FROM node:18
RUN npm install -g npm@latest
RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y curl
RUN apt-get clean

# Good: Combined layers
FROM node:18
RUN npm install -g npm@latest && \
    apt-get update && \
    apt-get install -y git curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### 4. Order Commands by Change Frequency

```dockerfile
# Bad: Source code changes invalidate dependencies
FROM node:18
WORKDIR /app
COPY . .
RUN npm install
CMD ["node", "server.js"]

# Good: Dependencies cached separately
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
CMD ["node", "server.js"]
```

## Build Performance

### 1. Use .dockerignore

**.dockerignore:**
```
node_modules
.git
.github
.vscode
.env*
*.log
*.md
Dockerfile
docker-compose.yml
.dockerignore
coverage
.nyc_output
dist
build
```

### 2. Leverage Build Cache

```dockerfile
# Cache package installation
FROM python:3.11-slim
WORKDIR /app

# Install dependencies first (cached if unchanged)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code (changes frequently)
COPY . .
CMD ["python", "app.py"]
```

### 3. Use BuildKit

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build with BuildKit
docker build --progress=plain .

# Parallel builds
docker build --build-arg BUILDKIT_INLINE_CACHE=1 .
```

### 4. Cache Package Managers

```dockerfile
# Node.js with npm cache
FROM node:18 AS builder
WORKDIR /app
RUN --mount=type=cache,target=/root/.npm \
    npm install

# Python with pip cache
FROM python:3.11
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Go with module cache
FROM golang:1.21 AS builder
WORKDIR /app
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download
```

## Advanced Optimization Techniques

### 1. Distroless Images

```dockerfile
# Node.js distroless
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

FROM gcr.io/distroless/nodejs18-debian11
WORKDIR /app
COPY --from=builder /app /app
CMD ["server.js"]
```

### 2. Scratch Images (Go)

```dockerfile
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

FROM scratch
COPY --from=builder /app/app /app
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
ENTRYPOINT ["/app"]
```

### 3. Compress Binaries

```dockerfile
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN go build -ldflags="-s -w" -o app .
RUN upx --best --lzma app

FROM alpine:latest
COPY --from=builder /app/app /app
CMD ["/app"]
```

### 4. Remove Debug Symbols

```dockerfile
# Go
RUN go build -ldflags="-s -w" -o app

# C/C++
RUN gcc -o app app.c && strip app

# Rust
RUN cargo build --release
RUN strip target/release/app
```

## Layer Optimization

### 1. Combine RUN Commands

```dockerfile
# Bad: 3 layers
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# Good: 1 layer
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
```

### 2. Clean Up in Same Layer

```dockerfile
RUN apt-get update && \
    apt-get install -y \
      build-essential \
      python3-dev && \
    # Build application \
    python3 setup.py install && \
    # Clean up in same layer \
    apt-get purge -y build-essential python3-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*
```

### 3. Use --no-install-recommends

```dockerfile
# Install only required packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      curl && \
    rm -rf /var/lib/apt/lists/*
```

## Package Manager Optimization

### npm

```dockerfile
# Use ci instead of install
RUN npm ci --only=production

# Clear cache
RUN npm ci --only=production && \
    npm cache clean --force

# Remove unnecessary files
RUN npm ci --only=production && \
    rm -rf /root/.npm /tmp/*
```

### pip

```dockerfile
# Don't cache
RUN pip install --no-cache-dir -r requirements.txt

# Install only what's needed
RUN pip install --no-cache-dir \
    --no-deps \
    -r requirements.txt

# Use wheels
RUN pip install --no-cache-dir \
    --prefer-binary \
    -r requirements.txt
```

### apt

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      package1 \
      package2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
```

## Real-World Optimization Examples

### Node.js Application

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy source
COPY . .

# Build
RUN npm run build

# Production image
FROM node:18-alpine
WORKDIR /app

# Copy built artifacts
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

# Remove dev dependencies
RUN npm prune --production

# Security: non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
USER nodejs

CMD ["node", "dist/server.js"]
```

**Result:** 950MB → 120MB (87% reduction)

### Python Application

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      gcc \
      python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Production image
FROM python:3.11-slim
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy wheels and install
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels

# Copy application
COPY . .

CMD ["python", "app.py"]
```

**Result:** 900MB → 200MB (78% reduction)

## Measurement and Analysis

### Check Image Size

```bash
# List images with size
docker images

# Check specific image
docker images myapp:latest

# Analyze layers
docker history myapp:latest

# Detailed layer analysis
docker history --no-trunc myapp:latest

# Human-readable sizes
docker history --human myapp:latest
```

### Use dive Tool

```bash
# Install dive
brew install dive  # Mac
# or download from GitHub

# Analyze image
dive myapp:latest

# Show efficiency score
dive myapp:latest --ci
```

### Docker Scout

```bash
# Analyze image
docker scout quickview myapp:latest

# Get recommendations
docker scout recommendations myapp:latest
```

## Build Arguments for Optimization

```dockerfile
FROM node:18 AS base
WORKDIR /app

FROM base AS development
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]

FROM base AS production-deps
COPY package*.json ./
RUN npm ci --only=production

FROM base AS builder
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM base AS production
COPY --from=production-deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
CMD ["node", "dist/server.js"]
```

```bash
# Build development
docker build --target development -t myapp:dev .

# Build production
docker build --target production -t myapp:prod .
```

## Best Practices Checklist

- [ ] Use minimal base images (Alpine, distroless, scratch)
- [ ] Implement multi-stage builds
- [ ] Order Dockerfile commands by change frequency
- [ ] Use .dockerignore to exclude unnecessary files
- [ ] Combine RUN commands to reduce layers
- [ ] Clean up in the same layer
- [ ] Use --no-cache flags for package managers
- [ ] Remove build dependencies after use
- [ ] Compress binaries when possible
- [ ] Use BuildKit for improved caching
- [ ] Regular image audits with dive or scout
- [ ] Pin versions for reproducibility

## Interview Questions

**Q: What's the difference between Alpine and distroless images?**
A: Alpine uses musl libc and has a shell, making it ~5MB. Distroless has only runtime dependencies, no shell or package manager, making it more secure but harder to debug.

**Q: How do you reduce Docker image size?**
A: Use minimal base images, multi-stage builds, combine RUN commands, use .dockerignore, remove unnecessary files in the same layer, and choose appropriate package manager options.

**Q: What is BuildKit and why use it?**
A: BuildKit is Docker's improved build engine with better performance, caching, and parallel build support. Enable with `DOCKER_BUILDKIT=1`.

**Next:** [Security →](14-security.md)
