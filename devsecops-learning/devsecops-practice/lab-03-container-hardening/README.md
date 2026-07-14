# Lab 3: Container Security Hardening

## Objectives

By completing this lab, you will:
- Harden Docker containers using security best practices
- Implement multi-stage builds to reduce attack surface
- Scan images for vulnerabilities with Trivy
- Configure runtime security controls
- Create secure base images
- Implement container resource limits

**Duration**: 2 hours

---

## Prerequisites

- Docker installed
- Basic Docker knowledge
- Completed Labs 1 & 2

---

## Part 1: Understanding Container Vulnerabilities

### Common Container Security Issues

```dockerfile
# INSECURE DOCKERFILE - Multiple Issues
FROM ubuntu:latest

# Issue 1: Running as root
USER root

# Issue 2: Installing unnecessary packages
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    vim \
    net-tools \
    build-essential

# Issue 3: Hardcoded secrets
ENV DATABASE_PASSWORD="supersecret123"
ENV API_KEY="sk_live_abc123"

# Issue 4: No health check
# Issue 5: Using latest tag

# Issue 6: Copying unnecessary files
COPY . /app
WORKDIR /app

# Issue 7: Exposing too many ports
EXPOSE 22 80 443 8080

CMD ["python", "app.py"]
```

**Run vulnerability scan:**

```bash
# Install Trivy
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# Scan the insecure image
docker build -t insecure-app:latest .
trivy image insecure-app:latest

# Expected: 100+ vulnerabilities
```

---

## Part 2: Multi-Stage Builds

**Secure Python Application:**

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install dependencies in isolated layer
WORKDIR /build
COPY requirements.txt .

# Use pip with security flags
RUN pip install --no-cache-dir \
    --user \
    --disable-pip-version-check \
    --no-warn-script-location \
    -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Security updates
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Copy only necessary files from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser app.py /app/

# Set up PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Expose only necessary port
EXPOSE 8080

# Use exec form for proper signal handling
CMD ["python", "-u", "app.py"]
```

**Build and compare:**

```bash
# Build both versions
docker build -f Dockerfile.insecure -t insecure:latest .
docker build -f Dockerfile.secure -t secure:latest .

# Compare sizes
docker images | grep -E 'insecure|secure'

# Compare vulnerabilities
trivy image insecure:latest --severity HIGH,CRITICAL
trivy image secure:latest --severity HIGH,CRITICAL

# Expected results:
# insecure: 500MB, 50+ vulnerabilities
# secure: 150MB, 5 vulnerabilities
```

---

## Part 3: Distroless Images

**Ultra-minimal image with no shell:**

```dockerfile
# Multi-stage with distroless
FROM golang:1.21 AS builder

WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

# Use distroless base
FROM gcr.io/distroless/static-debian11

# Copy binary only
COPY --from=builder /build/app /app

# Use numeric UID (no shell to look up users)
USER 65534:65534

EXPOSE 8080
ENTRYPOINT ["/app"]
```

**Benefits of Distroless:**
- No package manager
- No shell
- No unnecessary binaries
- Minimal attack surface
- ~2MB base image

---

## Part 4: Image Scanning with Trivy

**Comprehensive scanning:**

```bash
# Basic vulnerability scan
trivy image myapp:latest

# Scan with severity filter
trivy image --severity HIGH,CRITICAL myapp:latest

# Scan for misconfigurations
trivy config Dockerfile

# Scan for secrets
trivy fs --security-checks secret .

# Generate JSON report
trivy image --format json --output results.json myapp:latest

# CI/CD integration - fail on critical
trivy image --exit-code 1 --severity CRITICAL myapp:latest
```

**Trivy Configuration:**

```yaml
# trivy.yaml
scan:
  security-checks:
    - vuln
    - config
    - secret
  
  severity:
    - CRITICAL
    - HIGH
  
  ignore-unfixed: true
  
  ignorefile: .trivyignore

vulnerability:
  type:
    - os
    - library
  
db:
  repository: "ghcr.io/aquasecurity/trivy-db"
  
output:
  format: table
```

**.trivyignore** (suppress false positives):

```
# Ignore specific CVEs with justification
CVE-2023-12345  # Fixed in next release, not exploitable in our context
CVE-2023-67890  # Dev dependency only, not in production

# Ignore by package
pkg:python/setuptools  # Build-time only
```

---

## Part 5: Runtime Security

### Docker Security Options

```bash
# Run with security best practices
docker run -d \
  --name secure-app \
  --read-only \
  --tmpfs /tmp \
  --security-opt=no-new-privileges:true \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --user 1000:1000 \
  --memory="512m" \
  --cpus="0.5" \
  --pids-limit=100 \
  --restart=unless-stopped \
  myapp:latest
```

**Explanation:**
- `--read-only`: Filesystem is read-only
- `--tmpfs /tmp`: Temporary writable space
- `--security-opt=no-new-privileges`: Prevents privilege escalation
- `--cap-drop=ALL --cap-add=NET_BIND_SERVICE`: Minimal capabilities
- `--user 1000:1000`: Run as non-root
- `--memory="512m"`: Memory limit (prevent DoS)
- `--cpus="0.5"`: CPU limit
- `--pids-limit=100`: Process limit

### Docker Compose with Security

```yaml
# docker-compose.yml
version: '3.9'

services:
  app:
    image: myapp:latest
    build:
      context: .
      dockerfile: Dockerfile
    
    # Security settings
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    user: "1000:1000"
    
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    
    # Temporary volumes
    tmpfs:
      - /tmp
      - /var/run
    
    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s
    
    # Secrets management
    secrets:
      - db_password
      - api_key
    
    environment:
      - DATABASE_HOST=db
      - DATABASE_NAME=myapp
      - DATABASE_USER=appuser
    
    ports:
      - "8080:8080"
    
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15-alpine
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /var/run/postgresql
    volumes:
      - db-data:/var/lib/postgresql/data
    secrets:
      - db_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  db-data:
    driver: local

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    file: ./secrets/api_key.txt
```

---

## Part 6: Container Image Signing

**Sign images with Cosign:**

```bash
# Install Cosign
curl -O -L "https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64"
sudo mv cosign-linux-amd64 /usr/local/bin/cosign
sudo chmod +x /usr/local/bin/cosign

# Generate keypair
cosign generate-key-pair

# Sign image
cosign sign --key cosign.key myapp:v1.0.0

# Verify signature
cosign verify --key cosign.pub myapp:v1.0.0

# Verify in CI/CD
if ! cosign verify --key cosign.pub myapp:v1.0.0; then
  echo "Image signature verification failed!"
  exit 1
fi
```

---

## Part 7: Advanced Hardening

### AppArmor Profile

```bash
# apparmor-profile
#include <tunables/global>

profile docker-myapp flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  
  # Allow network
  network inet stream,
  network inet6 stream,
  
  # Allow reading app files
  /app/** r,
  
  # Allow writing to tmp
  /tmp/** rw,
  
  # Deny everything else
  deny /proc/** w,
  deny /sys/** w,
  deny /etc/** w,
}
```

```bash
# Load profile
sudo apparmor_parser -r -W apparmor-profile

# Run container with profile
docker run --security-opt apparmor=docker-myapp myapp:latest
```

### Seccomp Profile

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "syscalls": [
    {
      "names": [
        "accept",
        "accept4",
        "bind",
        "connect",
        "listen",
        "read",
        "write",
        "close",
        "exit",
        "exit_group"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

```bash
# Run with seccomp profile
docker run --security-opt seccomp=seccomp-profile.json myapp:latest
```

---

## Exercises

### Exercise 1: Harden a Dockerfile

Given this insecure Dockerfile, fix all security issues:

```dockerfile
FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3 python3-pip
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENV SECRET_KEY="hardcoded_secret"
EXPOSE 8080
CMD python3 app.py
```

<details>
<summary>Solution</summary>

```dockerfile
# Use specific version
FROM python:3.11-slim AS builder

# Security updates
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Copy dependencies and app
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser app.py /app/

ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser
WORKDIR /app

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

EXPOSE 8080
CMD ["python", "-u", "app.py"]
```

</details>

### Exercise 2: Implement Complete Scanning Pipeline

Create a GitHub Actions workflow that:
1. Builds the Docker image
2. Scans for vulnerabilities with Trivy
3. Scans for secrets
4. Fails if critical vulnerabilities found
5. Signs the image
6. Pushes to registry

### Exercise 3: Create Minimal Go Application

Build a Go application using distroless images:
- Final image size < 10MB
- Zero CVEs
- No shell access
- Health check endpoint

---

## Verification Checklist

Run these checks on your hardened container:

```bash
# 1. Check image size
docker images myapp:latest

# 2. Vulnerability scan
trivy image --severity CRITICAL myapp:latest
# Expected: 0 critical vulnerabilities

# 3. Verify non-root user
docker run --rm myapp:latest id
# Expected: uid=1000 (not root)

# 4. Verify no shell
docker exec -it myapp sh
# Expected: OCI runtime exec failed (for distroless)

# 5. Check capabilities
docker inspect myapp | jq '.[0].HostConfig.CapDrop'
# Expected: ["ALL"]

# 6. Verify read-only filesystem
docker inspect myapp | jq '.[0].HostConfig.ReadonlyRootfs'
# Expected: true
```

---

## Security Comparison

### Before vs After

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Image Size | 500 MB | 150 MB | 70% reduction |
| Critical CVEs | 25 | 0 | 100% reduction |
| High CVEs | 75 | 5 | 93% reduction |
| Layers | 15 | 8 | 47% reduction |
| Running as Root | Yes | No | ✅ |
| Shell Access | Yes | No | ✅ |
| Secrets Exposed | Yes | No | ✅ |

---

## Best Practices Summary

✅ **Image Building:**
- Use specific base image tags (not `latest`)
- Use minimal base images (alpine, distroless)
- Multi-stage builds
- Run as non-root user
- Regular security updates

✅ **Vulnerability Management:**
- Scan images in CI/CD
- Fix critical vulnerabilities immediately
- Use `.trivyignore` for justified exceptions
- Regular base image updates

✅ **Runtime Security:**
- Read-only filesystem
- Drop all capabilities
- Resource limits
- No new privileges
- Health checks

✅ **Secrets:**
- Never hardcode in images
- Use Docker secrets or K8s secrets
- Mount as files, not environment variables

✅ **Compliance:**
- Sign images
- Verify signatures
- Maintain SBOM
- Audit image usage

---

## Additional Resources

- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [NIST Container Security](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)

**Next Lab**: [Secrets Management with HashiCorp Vault →](../lab-04-secrets-vault/README.md)
