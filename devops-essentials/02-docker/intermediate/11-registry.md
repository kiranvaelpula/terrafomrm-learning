# Docker Registry

Working with Docker Hub and private registries.

## Overview

A Docker registry is a storage and distribution system for Docker images. Docker Hub is the default public registry, but you can also use private registries.

## Docker Hub

### Authentication

```bash
# Login to Docker Hub
docker login

# Login with username
docker login -u myusername

# Logout
docker logout
```

### Pushing Images

```bash
# Tag image with Docker Hub username
docker tag myapp:latest myusername/myapp:latest
docker tag myapp:latest myusername/myapp:v1.0.0

# Push to Docker Hub
docker push myusername/myapp:latest
docker push myusername/myapp:v1.0.0

# Push all tags
docker push --all-tags myusername/myapp
```

### Pulling Images

```bash
# Pull from Docker Hub
docker pull myusername/myapp:latest

# Pull specific version
docker pull myusername/myapp:v1.0.0

# Pull without running
docker pull nginx:alpine
```

## Private Registries

### Using Private Registry

```bash
# Login to private registry
docker login registry.company.com

# Tag for private registry
docker tag myapp:latest registry.company.com/myapp:latest

# Push to private registry
docker push registry.company.com/myapp:latest

# Pull from private registry
docker pull registry.company.com/myapp:latest
```

### Running Local Registry

```bash
# Start local registry
docker run -d \
  -p 5000:5000 \
  --name registry \
  -v registry-data:/var/lib/registry \
  registry:2

# Tag for local registry
docker tag myapp:latest localhost:5000/myapp:latest

# Push to local registry
docker push localhost:5000/myapp:latest

# Pull from local registry
docker pull localhost:5000/myapp:latest
```

### Secure Local Registry

```bash
# With TLS and authentication
docker run -d \
  -p 5000:5000 \
  --name registry \
  -v registry-data:/var/lib/registry \
  -v $(pwd)/certs:/certs \
  -v $(pwd)/auth:/auth \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key \
  -e REGISTRY_AUTH=htpasswd \
  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd \
  -e REGISTRY_AUTH_HTPASSWD_REALM="Registry Realm" \
  registry:2
```

## Cloud Registries

### Amazon ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag myapp:latest \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
docker push \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
```

### Google Container Registry (GCR)

```bash
# Configure authentication
gcloud auth configure-docker

# Tag and push
docker tag myapp:latest gcr.io/my-project/myapp:latest
docker push gcr.io/my-project/myapp:latest
```

### Azure Container Registry (ACR)

```bash
# Login to ACR
az acr login --name myregistry

# Tag and push
docker tag myapp:latest myregistry.azurecr.io/myapp:latest
docker push myregistry.azurecr.io/myapp:latest
```

## Image Tagging Strategies

### Semantic Versioning

```bash
# Tag with version
docker tag myapp:latest myusername/myapp:1.0.0
docker tag myapp:latest myusername/myapp:1.0
docker tag myapp:latest myusername/myapp:1
docker tag myapp:latest myusername/myapp:latest

# Push all versions
docker push myusername/myapp:1.0.0
docker push myusername/myapp:1.0
docker push myusername/myapp:1
docker push myusername/myapp:latest
```

### Git-based Tagging

```bash
# Tag with git commit
GIT_COMMIT=$(git rev-parse --short HEAD)
docker tag myapp:latest myusername/myapp:${GIT_COMMIT}
docker push myusername/myapp:${GIT_COMMIT}

# Tag with git branch
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
docker tag myapp:latest myusername/myapp:${GIT_BRANCH}
docker push myusername/myapp:${GIT_BRANCH}
```

### Environment-based Tagging

```bash
# Environment tags
docker tag myapp:latest myusername/myapp:dev
docker tag myapp:latest myusername/myapp:staging
docker tag myapp:latest myusername/myapp:production
```

## Docker Compose with Private Registry

```yaml
version: '3.8'

services:
  app:
    image: registry.company.com/myapp:latest
    ports:
      - "3000:3000"

  db:
    image: registry.company.com/postgres:15-custom
    environment:
      POSTGRES_PASSWORD: secret
```

```bash
# Login before running
docker login registry.company.com
docker-compose up -d
```

## Registry Management

### List Images in Registry

```bash
# Docker Hub (via API)
curl -s https://hub.docker.com/v2/repositories/myusername/ | jq

# Private registry
curl -X GET http://localhost:5000/v2/_catalog

# List tags for image
curl -X GET http://localhost:5000/v2/myapp/tags/list
```

### Delete Images

```bash
# Delete from Docker Hub (use web UI)

# Delete from local registry
# Enable deletion in config
docker run -d \
  -p 5000:5000 \
  -e REGISTRY_STORAGE_DELETE_ENABLED=true \
  registry:2

# Get digest
curl -I -H "Accept: application/vnd.docker.distribution.manifest.v2+json" \
  http://localhost:5000/v2/myapp/manifests/latest

# Delete by digest
curl -X DELETE http://localhost:5000/v2/myapp/manifests/sha256:abc123...
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Build and Push

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          push: true
          tags: myusername/myapp:latest
```

### GitLab CI

```yaml
build:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
```

## Best Practices

1. **Use specific tags, avoid latest in production**
```bash
# Bad
docker pull myapp:latest

# Good
docker pull myapp:1.2.3
```

2. **Implement multi-stage builds to reduce size**
3. **Scan images for vulnerabilities**
```bash
docker scan myusername/myapp:latest
```

4. **Use private registries for proprietary code**
5. **Implement image signing for security**
6. **Tag images with multiple identifiers**
7. **Clean up old images regularly**

## Security

### Image Signing

```bash
# Enable Docker Content Trust
export DOCKER_CONTENT_TRUST=1

# Push signed image
docker push myusername/myapp:latest

# Pull only signed images
docker pull myusername/myapp:latest
```

### Vulnerability Scanning

```bash
# Docker Hub scanning (automatic for public repos)

# Trivy scanning
trivy image myusername/myapp:latest

# Clair scanning
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  arminc/clair-scanner --ip your-ip myusername/myapp:latest
```

## Troubleshooting

### Authentication Issues

```bash
# Check credentials
cat ~/.docker/config.json

# Re-login
docker logout
docker login

# Test with curl
curl -u username:password https://registry.company.com/v2/_catalog
```

### Push/Pull Failures

```bash
# Check image exists
docker images | grep myapp

# Verify tag format
docker images myusername/myapp

# Check network connectivity
curl -I https://registry.company.com

# Increase timeout
export DOCKER_CLIENT_TIMEOUT=300
```

### Disk Space Issues

```bash
# Check registry storage
docker exec registry du -sh /var/lib/registry

# Run garbage collection
docker exec registry bin/registry garbage-collect /etc/docker/registry/config.yml
```

## Interview Questions

**Q: What's the difference between Docker Hub and a private registry?**
A: Docker Hub is a public registry service by Docker, while private registries are self-hosted or cloud-hosted services for storing proprietary images.

**Q: How do you secure a Docker registry?**
A: Use TLS for encryption, implement authentication, scan images for vulnerabilities, use image signing, and restrict network access.

**Q: What's the best practice for tagging images?**
A: Use semantic versioning (1.2.3), include git commit SHA, avoid using only 'latest' in production, and maintain multiple tags.

**Next:** [Logging & Debugging →](12-logging-debugging.md)
