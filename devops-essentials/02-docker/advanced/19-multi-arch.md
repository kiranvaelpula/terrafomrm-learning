# Multi-Architecture Docker Images

Build and deploy Docker images for multiple CPU architectures.

## Overview

Multi-architecture (multi-arch) images allow a single image tag to support multiple CPU architectures (AMD64, ARM64, etc.), automatically selecting the right variant for the host.

## Why Multi-Architecture?

**Use Cases:**
- ARM-based cloud instances (AWS Graviton, Azure)
- Apple Silicon (M1/M2/M3) Macs
- Raspberry Pi and edge devices
- Cost optimization (ARM is often cheaper)
- Power efficiency

**Benefits:**
- Single image tag works everywhere
- Simplified deployment
- Better developer experience
- Future-proof applications

## Architecture Types

| Architecture | Also Known As | Common Platforms |
|--------------|---------------|------------------|
| linux/amd64 | x86_64, x64 | Most servers, Intel/AMD CPUs |
| linux/arm64 | aarch64, ARM64 | AWS Graviton, Apple Silicon, Raspberry Pi 4 |
| linux/arm/v7 | armhf, ARMv7 | Raspberry Pi 3, older ARM devices |
| linux/arm/v6 | armel, ARMv6 | Raspberry Pi Zero, Pi 1 |
| windows/amd64 | - | Windows containers |

## Building Multi-Arch Images

### Method 1: Docker Buildx (Recommended)

```bash
# Create and use builder
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap

# Build for multiple architectures
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t myusername/myapp:latest \
  --push \
  .

# Build and load locally (single architecture only)
docker buildx build \
  --platform linux/amd64 \
  -t myapp:latest \
  --load \
  .
```

### Method 2: Docker Manifest

```bash
# Build for each architecture
docker build -t myapp:amd64 --platform linux/amd64 .
docker build -t myapp:arm64 --platform linux/arm64 .

# Push individual images
docker push myapp:amd64
docker push myapp:arm64

# Create and push manifest
docker manifest create myapp:latest \
  myapp:amd64 \
  myapp:arm64

docker manifest push myapp:latest
```

## Dockerfile for Multi-Arch

### Basic Multi-Arch Dockerfile

```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.21 AS builder
ARG TARGETOS
ARG TARGETARCH

WORKDIR /app
COPY . .

# Build for target architecture
RUN GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o myapp .

FROM alpine:latest
COPY --from=builder /app/myapp /myapp
CMD ["/myapp"]
```

### Node.js Multi-Arch

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Expose port
EXPOSE 3000

CMD ["node", "server.js"]
```

### Python Multi-Arch

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

CMD ["python", "app.py"]
```

## Architecture-Specific Code

### Conditional Builds

```dockerfile
FROM alpine:latest

# Install architecture-specific packages
RUN apk add --no-cache \
    $(if [ "$(uname -m)" = "x86_64" ]; then echo "package-amd64"; else echo "package-arm64"; fi)
```

### Build Arguments

```dockerfile
FROM ubuntu:22.04

ARG TARGETARCH

# Install architecture-specific binary
RUN if [ "$TARGETARCH" = "amd64" ]; then \
      wget https://example.com/app-amd64 -O /usr/local/bin/app; \
    elif [ "$TARGETARCH" = "arm64" ]; then \
      wget https://example.com/app-arm64 -O /usr/local/bin/app; \
    fi && \
    chmod +x /usr/local/bin/app
```

## Testing Multi-Arch Images

### Inspect Image

```bash
# Check supported architectures
docker manifest inspect myusername/myapp:latest

# Show platforms
docker buildx imagetools inspect myusername/myapp:latest
```

### Test on Different Architectures

```bash
# Test ARM64 on AMD64 host (using QEMU)
docker run --platform linux/arm64 myapp:latest

# Test AMD64 on ARM64 host
docker run --platform linux/amd64 myapp:latest
```

### QEMU Setup for Cross-Platform Building

```bash
# Install QEMU
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

# Verify QEMU is installed
docker buildx ls
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Build Multi-Arch

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v2
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          platforms: linux/amd64,linux/arm64,linux/arm/v7
          push: true
          tags: |
            myusername/myapp:latest
            myusername/myapp:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### GitLab CI

```yaml
build-multiarch:
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
    - docker buildx create --use --name multiarch
  script:
    - docker buildx build \
        --platform linux/amd64,linux/arm64 \
        -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA \
        -t $CI_REGISTRY_IMAGE:latest \
        --push \
        .
```

## Real-World Example

### Full Application Stack

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    image: myusername/myapp:latest
    build:
      context: .
      platforms:
        - linux/amd64
        - linux/arm64
    ports:
      - "3000:3000"

  db:
    image: postgres:15-alpine  # Multi-arch official image
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine  # Multi-arch official image

volumes:
  postgres-data:
```

### Build Script

```bash
#!/bin/bash
# build-multiarch.sh

IMAGE_NAME="myusername/myapp"
VERSION=${1:-latest}

# Setup buildx
docker buildx create --use --name multiarch 2>/dev/null || docker buildx use multiarch

# Build and push for multiple architectures
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t ${IMAGE_NAME}:${VERSION} \
  -t ${IMAGE_NAME}:latest \
  --push \
  .

echo "Built and pushed ${IMAGE_NAME}:${VERSION} for amd64, arm64, and armv7"

# Display manifest
docker buildx imagetools inspect ${IMAGE_NAME}:${VERSION}
```

## Performance Considerations

### Native vs Emulated

```
Build Time Comparison (approximate):
- Native ARM64: 2 minutes
- Emulated ARM64 on AMD64: 15 minutes
- Native AMD64: 1.5 minutes
```

### Optimization Tips

1. **Use native builders when possible**
```yaml
# GitHub Actions with ARM64 runner
jobs:
  build-arm64:
    runs-on: ubuntu-latest-arm64
    steps:
      - name: Build ARM64
        run: docker build -t myapp:arm64 .
```

2. **Cache aggressively**
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --cache-from type=registry,ref=myapp:buildcache \
  --cache-to type=registry,ref=myapp:buildcache,mode=max \
  -t myapp:latest \
  --push \
  .
```

3. **Build architectures separately**
```bash
# Build AMD64 (fast, native)
docker buildx build --platform linux/amd64 -t myapp:amd64 --push .

# Build ARM64 (slower, emulated)
docker buildx build --platform linux/arm64 -t myapp:arm64 --push .

# Create manifest
docker manifest create myapp:latest myapp:amd64 myapp:arm64
docker manifest push myapp:latest
```

## Common Issues

### Issue 1: QEMU Not Installed

```bash
# Error: exec user process caused: exec format error

# Solution: Install QEMU
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

### Issue 2: Platform Not Supported

```bash
# Some base images don't support all architectures

# Check available platforms
docker manifest inspect node:18-alpine
```

### Issue 3: Architecture-Specific Dependencies

```dockerfile
# Solution: Conditional installation
FROM alpine:latest
ARG TARGETARCH

RUN if [ "$TARGETARCH" = "amd64" ]; then \
      apk add --no-cache package-x86; \
    elif [ "$TARGETARCH" = "arm64" ]; then \
      apk add --no-cache package-arm; \
    fi
```

## Best Practices

1. **Test on target architectures**
2. **Use official multi-arch base images**
3. **Leverage buildx for building**
4. **Cache builds for faster CI/CD**
5. **Document supported architectures**
6. **Use manifest lists for distribution**
7. **Consider native builders for production**

## Verification

```bash
# Check your current architecture
docker version --format '{{.Server.Arch}}'
uname -m

# Pull and inspect image
docker pull myapp:latest
docker inspect myapp:latest | grep Architecture

# Run on specific platform
docker run --platform linux/arm64 myapp:latest

# List available platforms for image
docker manifest inspect myapp:latest | jq -r '.manifests[].platform | "\(.os)/\(.architecture)"'
```

## Interview Questions

**Q: What is a multi-architecture Docker image?**
A: A single image tag that supports multiple CPU architectures, automatically selecting the appropriate variant for the host system.

**Q: How do you build multi-arch images?**
A: Use Docker Buildx with `--platform` flag or create manifest lists that reference architecture-specific images.

**Q: Why would you need multi-arch images?**
A: To support different hardware platforms (ARM vs x86), enable deployment on ARM-based cloud instances, support Apple Silicon Macs, and improve portability.

**Q: What's the difference between building natively and using emulation?**
A: Native builds are much faster but require access to that architecture. Emulation (via QEMU) is slower but allows building for any architecture from a single machine.

**Next:** [Enterprise Patterns →](20-enterprise-patterns.md)
