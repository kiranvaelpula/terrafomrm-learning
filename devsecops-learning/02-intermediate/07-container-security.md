# Container Security

## Learning Objectives
- Understand container security challenges
- Scan container images for vulnerabilities
- Implement secure container practices
- Secure container runtime and orchestration

---

## Container Security Landscape

### Security Layers
```
┌─────────────────────────────────────┐
│     Application Code Security       │  ← Code vulnerabilities
├─────────────────────────────────────┤
│    Container Image Security         │  ← Image vulnerabilities
├─────────────────────────────────────┤
│    Container Runtime Security       │  ← Runtime protection
├─────────────────────────────────────┤
│    Host OS Security                 │  ← Kernel, system security
├─────────────────────────────────────┤
│    Orchestration Security           │  ← K8s, Docker Swarm
└─────────────────────────────────────┘
```

---

## Image Scanning with Trivy

### Installation
```bash
# Linux
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# macOS
brew install trivy

# Docker
docker pull aquasec/trivy
```

### Basic Scanning
```bash
# Scan image
trivy image nginx:latest

# Scan with severity filter
trivy image --severity HIGH,CRITICAL nginx:latest

# Output to JSON
trivy image --format json --output results.json nginx:latest

# Scan specific vulnerabilities
trivy image --vuln-type os,library nginx:latest
```

### Scan Local Dockerfile
```bash
# Scan Dockerfile
trivy config Dockerfile

# Scan with policies
trivy config --policy ./policies Dockerfile
```

---

## Dockerfile Security Best Practices

### ❌ Insecure Dockerfile
```dockerfile
FROM ubuntu:latest

# Running as root (bad)
USER root

# Installing unnecessary packages
RUN apt-get update && apt-get install -y \
    curl wget git vim nano netcat \
    python3 python3-pip

# Hardcoded secrets (very bad!)
ENV API_KEY="sk_live_abc123"
ENV DB_PASSWORD="password123"

# No version pinning
RUN pip install flask requests

# Exposing unnecessary ports
EXPOSE 22 3000 5432 8080

# Copying everything
COPY . /app

WORKDIR /app

# Running app as root
CMD ["python3", "app.py"]
```

### ✅ Secure Dockerfile
```dockerfile
# Use specific version, not latest
FROM python:3.11-slim-bullseye

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install only required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Pin versions in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser src/ ./src/

# Don't run as root
USER appuser

# Expose only necessary port
EXPOSE 8080

# Use exec form
CMD ["python", "src/app.py"]

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8080/health || exit 1
```

---

## Multi-Stage Build for Security

```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy only necessary artifacts from builder
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser src/ ./

# Make sure scripts are in PATH
ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')"

CMD ["python", "app.py"]
```

---

## Container Image Scanning in CI/CD

### GitHub Actions
```yaml
name: Container Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Build image
        run: |
          docker build -t myapp:${{ github.sha }} .
      
      - name: Run Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
      
      - name: Upload results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Fail on critical vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          exit-code: '1'
          severity: 'CRITICAL'
```

### GitLab CI
```yaml
container_scan:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  
  variables:
    DOCKER_DRIVER: overlay2
    IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  
  script:
    # Build image
    - docker build -t $IMAGE .
    
    # Scan with Trivy
    - docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
        aquasec/trivy image --severity HIGH,CRITICAL \
        --format json --output trivy-report.json $IMAGE
    
    # Check for vulnerabilities
    - |
      critical=$(cat trivy-report.json | jq '[.Results[].Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length')
      if [ "$critical" -gt 0 ]; then
        echo "Found $critical critical vulnerabilities!"
        exit 1
      fi
  
  artifacts:
    reports:
      container_scanning: trivy-report.json
    when: always
    expire_in: 30 days
```

---

## Runtime Security with Falco

### Installation
```bash
# Install Falco on Kubernetes
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update

helm install falco falcosecurity/falco \
  --namespace falco --create-namespace \
  --set falcosidekick.enabled=true
```

### Custom Falco Rules
```yaml
# custom-rules.yaml
- rule: Unauthorized Process in Container
  desc: Detect unauthorized process execution
  condition: >
    spawned_process and
    container and
    not proc.name in (node, python, java, nginx)
  output: >
    Unauthorized process started in container
    (user=%user.name command=%proc.cmdline container=%container.name
    image=%container.image.repository)
  priority: WARNING

- rule: Write to Non-Application Directory
  desc: Detect writes to system directories
  condition: >
    open_write and
    container and
    fd.name startswith /etc or
    fd.name startswith /usr or
    fd.name startswith /bin
  output: >
    Write to system directory detected
    (file=%fd.name container=%container.name image=%container.image)
  priority: ERROR

- rule: Unexpected Network Connection
  desc: Detect outbound connections to unexpected hosts
  condition: >
    outbound and
    container and
    not fd.sip in (allowed_ips)
  output: >
    Unexpected network connection
    (connection=%fd.name container=%container.name dest=%fd.sip:%fd.sport)
  priority: WARNING
```

---

## Container Security Policies

### Pod Security Policy (PSP) - Deprecated but illustrative
```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false  # Don't allow privileged
  
  # Don't allow privilege escalation
  allowPrivilegeEscalation: false
  
  # Required to prevent escalations
  requiredDropCapabilities:
    - ALL
  
  # Allow core volume types
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  
  # Don't allow host access
  hostNetwork: false
  hostIPC: false
  hostPID: false
  
  # Require non-root user
  runAsUser:
    rule: 'MustRunAsNonRoot'
  
  # Don't allow write to root filesystem
  readOnlyRootFilesystem: true
  
  # Require specific fsGroup
  fsGroup:
    rule: 'RunAsAny'
  
  seLinux:
    rule: 'RunAsAny'
  
  supplementalGroups:
    rule: 'RunAsAny'
```

### Pod Security Standards (Current)
```yaml
# Restricted namespace
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

---

## Secure Container Deployment

### Security Context
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  # Security at pod level
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  
  containers:
  - name: app
    image: myapp:1.0.0
    
    # Security at container level
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      runAsUser: 1000
      capabilities:
        drop:
          - ALL
        add:
          - NET_BIND_SERVICE
    
    # Resource limits
    resources:
      limits:
        cpu: "1"
        memory: "512Mi"
      requests:
        cpu: "100m"
        memory: "128Mi"
    
    # Volume mounts
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: cache
      mountPath: /app/cache
  
  volumes:
  - name: tmp
    emptyDir: {}
  - name: cache
    emptyDir: {}
```

---

## Image Signing and Verification

### Cosign (Sigstore)
```bash
# Install cosign
wget https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64
chmod +x cosign-linux-amd64
sudo mv cosign-linux-amd64 /usr/local/bin/cosign

# Generate key pair
cosign generate-key-pair

# Sign image
cosign sign --key cosign.key myregistry.io/myapp:v1.0.0

# Verify signature
cosign verify --key cosign.pub myregistry.io/myapp:v1.0.0
```

### Admission Controller for Verification
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cosign-policy
  namespace: cosign-system
data:
  policy.yaml: |
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: cosign-policy
    data:
      policy: |
        {
          "authorities": [
            {
              "key": {
                "data": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
              }
            }
          ]
        }
```

---

## Private Registry Security

### Harbor Configuration
```yaml
# docker-compose.yml for Harbor
version: '3'
services:
  registry:
    image: goharbor/harbor-registryctl:v2.8.0
    environment:
      - REGISTRY_AUTH=htpasswd
      - REGISTRY_AUTH_HTPASSWD_REALM=Harbor Registry
      - REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd
    volumes:
      - ./registry-data:/storage
      - ./auth:/auth
  
  core:
    image: goharbor/harbor-core:v2.8.0
    environment:
      - TRIVY_ADAPTER_URL=http://trivy:8080
    depends_on:
      - registry
      - trivy
  
  trivy:
    image: goharbor/trivy-adapter-photon:v2.8.0
    environment:
      - SCANNER_TRIVY_VULN_TYPE=os,library
      - SCANNER_TRIVY_SEVERITY=UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL
```

---

## Container Secrets Management

### ❌ Bad Practice
```dockerfile
# Never do this!
ENV DATABASE_PASSWORD=mypassword123
ENV API_KEY=sk_live_abc123xyz
```

### ✅ Good Practice - Kubernetes Secrets
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  database-password: "encoded-password"
  api-key: "encoded-api-key"

---
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: myapp:1.0.0
    env:
    - name: DATABASE_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: database-password
    - name: API_KEY
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: api-key
```

### ✅ Better - External Secrets Operator
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  
  target:
    name: app-secrets
    creationPolicy: Owner
  
  data:
  - secretKey: database-password
    remoteRef:
      key: prod/database/password
  - secretKey: api-key
    remoteRef:
      key: prod/api/key
```

---

## Security Scanning Automation

### Complete Pipeline Script
```python
#!/usr/bin/env python3
"""
Container security scanning pipeline
"""
import json
import subprocess
import sys

def scan_image(image_name):
    """Scan container image with Trivy"""
    result = subprocess.run(
        ['trivy', 'image', '--format', 'json', image_name],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def check_vulnerabilities(scan_results):
    """Check for critical vulnerabilities"""
    critical_vulns = []
    
    for result in scan_results.get('Results', []):
        for vuln in result.get('Vulnerabilities', []):
            if vuln['Severity'] == 'CRITICAL':
                critical_vulns.append({
                    'id': vuln['VulnerabilityID'],
                    'package': vuln['PkgName'],
                    'version': vuln['InstalledVersion'],
                    'fixed_version': vuln.get('FixedVersion', 'N/A')
                })
    
    return critical_vulns

def main():
    image = sys.argv[1] if len(sys.argv) > 1 else 'nginx:latest'
    
    print(f"Scanning {image}...")
    results = scan_image(image)
    
    critical = check_vulnerabilities(results)
    
    if critical:
        print(f"\n❌ Found {len(critical)} critical vulnerabilities:")
        for vuln in critical:
            print(f"  - {vuln['id']}: {vuln['package']} {vuln['version']}")
            print(f"    Fix: upgrade to {vuln['fixed_version']}")
        sys.exit(1)
    else:
        print("\n✅ No critical vulnerabilities found!")
        sys.exit(0)

if __name__ == '__main__':
    main()
```

---

## Security Best Practices Checklist

### Image Security
- [ ] Use minimal base images (alpine, distroless)
- [ ] Pin specific versions, not `latest`
- [ ] Scan images before deployment
- [ ] Sign and verify images
- [ ] Use multi-stage builds
- [ ] Remove unnecessary tools from images
- [ ] Update base images regularly

### Runtime Security
- [ ] Run as non-root user
- [ ] Use read-only root filesystem
- [ ] Drop unnecessary capabilities
- [ ] Set resource limits
- [ ] Enable security profiles (AppArmor/SELinux)
- [ ] Monitor runtime behavior
- [ ] Implement network policies

### Secrets Management
- [ ] Never hardcode secrets
- [ ] Use secret management tools
- [ ] Rotate secrets regularly
- [ ] Encrypt secrets at rest
- [ ] Limit secret access (RBAC)
- [ ] Audit secret access

### Registry Security
- [ ] Use private registries
- [ ] Enable image scanning
- [ ] Implement access controls
- [ ] Enable audit logging
- [ ] Use vulnerability policies
- [ ] Regular cleanup of old images

---

## Next Steps

1. Set up Trivy scanning in your CI/CD
2. Review and secure your Dockerfiles
3. Implement runtime security monitoring
4. Configure pod security standards
5. Set up image signing

---

**Next**: [Secrets Management →](08-secrets-management.md)
