# Docker Security

Best practices for securing Docker containers and images.

## Overview

Container security involves protecting images, runtime environments, and the Docker daemon itself from vulnerabilities and attacks.

## Image Security

### 1. Use Official and Verified Images

```bash
# Good: Official image
FROM node:18-alpine

# Good: Verified publisher
FROM bitnami/postgresql:15

# Risky: Unknown source
FROM randomuser/nodejs:latest
```

### 2. Scan Images for Vulnerabilities

```bash
# Docker Scout
docker scout cves myapp:latest
docker scout recommendations myapp:latest

# Trivy
trivy image myapp:latest

# Snyk
snyk container test myapp:latest

# Clair
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  arminc/clair-scanner myapp:latest
```

### 3. Sign and Verify Images

```bash
# Enable Docker Content Trust
export DOCKER_CONTENT_TRUST=1

# Push signed image
docker push myusername/myapp:latest

# Pull only signed images
docker pull myusername/myapp:latest
```

### 4. Use Specific Tags

```dockerfile
# Bad: Unpredictable
FROM node:latest

# Good: Specific version
FROM node:18.17.0-alpine3.18

# Best: Digest for immutability
FROM node:18-alpine@sha256:abc123...
```

## Dockerfile Security

### 1. Run as Non-Root User

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Change ownership
RUN chown -R nodejs:nodejs /app

# Switch to non-root user
USER nodejs

EXPOSE 3000
CMD ["node", "server.js"]
```

### 2. Minimize Attack Surface

```dockerfile
# Use minimal base image
FROM gcr.io/distroless/nodejs18-debian11

# Or Alpine with only required packages
FROM node:18-alpine
RUN apk add --no-cache \
    ca-certificates && \
    rm -rf /var/cache/apk/*
```

### 3. Don't Store Secrets in Images

```dockerfile
# Bad: Hardcoded secrets
ENV API_KEY=secret123
ENV DATABASE_PASSWORD=password

# Good: Use secrets at runtime
# Pass via environment variables or Docker secrets
```

```bash
# Runtime secrets
docker run -e API_KEY=$API_KEY myapp

# Docker secrets (Swarm)
echo "secret" | docker secret create api_key -
docker service create --secret api_key myapp
```

### 4. Use COPY Instead of ADD

```dockerfile
# Bad: ADD has unexpected behaviors
ADD https://example.com/file.tar.gz /app/

# Good: COPY is predictable
COPY file.tar.gz /app/
```

### 5. Set Read-Only Root Filesystem

```bash
docker run --read-only --tmpfs /tmp myapp
```

```dockerfile
# In Dockerfile
FROM node:18-alpine
# Application code
RUN mkdir /tmp/app && chown nodejs:nodejs /tmp/app
VOLUME /tmp/app
```

## Runtime Security

### 1. Limit Container Resources

```bash
# Memory limit
docker run -m 512m myapp

# CPU limit
docker run --cpus="1.5" myapp

# Combined
docker run -m 512m --cpus="1" myapp
```

```yaml
# Docker Compose
version: '3.8'
services:
  app:
    image: myapp
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### 2. Drop Unnecessary Capabilities

```bash
# Drop all capabilities and add only needed ones
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE myapp

# Run without capabilities
docker run --cap-drop=ALL myapp
```

```yaml
# Docker Compose
services:
  app:
    image: myapp
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
```

### 3. Use Security Options

```bash
# AppArmor profile
docker run --security-opt apparmor=docker-default myapp

# SELinux label
docker run --security-opt label=level:s0:c100,c200 myapp

# No new privileges
docker run --security-opt no-new-privileges:true myapp
```

### 4. Set User Namespace

```bash
# Enable user namespaces in daemon.json
{
  "userns-remap": "default"
}

# Restart Docker
sudo systemctl restart docker
```

### 5. Use Read-Only Volumes

```bash
docker run -v /config:/config:ro myapp
```

```yaml
services:
  app:
    volumes:
      - ./config:/config:ro
```

## Network Security

### 1. Use Custom Networks

```bash
# Create isolated network
docker network create --driver bridge app-network

# Run containers in custom network
docker run --network app-network myapp
```

### 2. Limit Port Exposure

```bash
# Bad: Expose to all interfaces
docker run -p 5432:5432 postgres

# Good: Bind to localhost only
docker run -p 127.0.0.1:5432:5432 postgres
```

### 3. Enable TLS for Docker Daemon

```bash
# Generate certificates
openssl genrsa -aes256 -out ca-key.pem 4096
openssl req -new -x509 -days 365 -key ca-key.pem -sha256 -out ca.pem

# Configure daemon to use TLS
dockerd --tlsverify \
  --tlscacert=ca.pem \
  --tlscert=server-cert.pem \
  --tlskey=server-key.pem \
  -H=0.0.0.0:2376
```

## Docker Daemon Security

### 1. Secure daemon.json

**/etc/docker/daemon.json:**
```json
{
  "icc": false,
  "userns-remap": "default",
  "no-new-privileges": true,
  "live-restore": true,
  "userland-proxy": false,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### 2. Limit Docker Socket Access

```bash
# Never expose Docker socket in containers
# Bad:
docker run -v /var/run/docker.sock:/var/run/docker.sock myapp

# If absolutely necessary, use read-only
docker run -v /var/run/docker.sock:/var/run/docker.sock:ro myapp
```

### 3. Enable Docker Bench Security

```bash
# Run Docker Bench Security
docker run --rm --net host --pid host --userns host --cap-add audit_control \
  -v /var/lib:/var/lib \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/lib/systemd:/usr/lib/systemd \
  -v /etc:/etc \
  --label docker_bench_security \
  docker/docker-bench-security
```

## Secrets Management

### 1. Docker Secrets (Swarm Mode)

```bash
# Create secret
echo "my-password" | docker secret create db_password -

# Use in service
docker service create \
  --name myapp \
  --secret db_password \
  myapp

# Access in container: /run/secrets/db_password
```

### 2. Environment Variables

```bash
# Pass from shell
docker run -e DB_PASSWORD=$DB_PASSWORD myapp

# From file
docker run --env-file .env myapp
```

### 3. External Secret Managers

```yaml
# Using HashiCorp Vault
services:
  app:
    image: myapp
    environment:
      VAULT_ADDR: https://vault.example.com
      VAULT_TOKEN: ${VAULT_TOKEN}
```

## Security Scanning in CI/CD

### GitHub Actions

```yaml
name: Security Scan

on: [push]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .
      
      - name: Run Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

### GitLab CI

```yaml
security_scan:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
        aquasec/trivy image --exit-code 1 --severity CRITICAL \
        $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

## Compliance and Auditing

### 1. Enable Audit Logging

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5",
    "labels": "production"
  }
}
```

### 2. Monitor Container Activity

```bash
# View events
docker events --filter type=container

# Monitor specific container
docker events --filter container=myapp

# Export logs
docker logs myapp > /var/log/myapp.log
```

### 3. Regular Security Audits

```bash
# Check for outdated images
docker images --filter "dangling=true"

# List running containers with security info
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"

# Inspect security settings
docker inspect --format='{{.HostConfig.SecurityOpt}}' myapp
```

## Best Practices Checklist

- [ ] Use official/verified base images
- [ ] Scan images for vulnerabilities
- [ ] Run containers as non-root users
- [ ] Use specific image tags, not latest
- [ ] Never store secrets in images
- [ ] Limit container resources (CPU/memory)
- [ ] Drop unnecessary Linux capabilities
- [ ] Use read-only filesystems where possible
- [ ] Enable Docker Content Trust
- [ ] Isolate containers with custom networks
- [ ] Bind ports to localhost only when appropriate
- [ ] Regular security audits with Docker Bench
- [ ] Implement secrets management
- [ ] Enable audit logging
- [ ] Keep Docker and base images updated

## Security Tools

| Tool | Purpose | Command |
|------|---------|---------|
| Trivy | Vulnerability scanning | `trivy image myapp:latest` |
| Docker Scout | CVE detection | `docker scout cves myapp:latest` |
| Snyk | Security testing | `snyk container test myapp:latest` |
| Clair | Static analysis | Via API or scanner |
| Docker Bench | CIS compliance | `docker run docker/docker-bench-security` |
| Anchore | Policy enforcement | Via Anchore Engine |

## Interview Questions

**Q: Why should containers not run as root?**
A: Running as root increases security risk. If a container is compromised, the attacker has root privileges which could affect the host system.

**Q: How do you scan Docker images for vulnerabilities?**
A: Use tools like Trivy, Docker Scout, Snyk, or Clair. Integrate scanning into CI/CD pipelines.

**Q: What is Docker Content Trust?**
A: A security feature that verifies the publisher and integrity of images using digital signatures. Enable with `DOCKER_CONTENT_TRUST=1`.

**Q: How do you pass secrets to containers securely?**
A: Use Docker secrets (Swarm), environment variables passed at runtime, or external secret managers like Vault. Never hardcode secrets in images.

**Q: What are Linux capabilities in Docker?**
A: Fine-grained permissions that allow containers to perform specific privileged operations without full root access. Use `--cap-drop` and `--cap-add` to manage them.

**Next:** [Production Deployment →](15-production.md)
