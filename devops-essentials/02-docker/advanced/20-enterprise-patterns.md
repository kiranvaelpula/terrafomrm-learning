# Enterprise Docker Patterns

Best practices and patterns for Docker at enterprise scale.

## Overview

Enterprise Docker deployments require patterns for governance, security, scalability, and operational excellence across large organizations.

## Image Management Patterns

### 1. Golden Base Images

Create standardized base images for the organization.

```dockerfile
# company-base-node:18
FROM node:18-alpine

# Corporate standards
RUN apk add --no-cache \
    ca-certificates \
    curl \
    dumb-init

# Security updates
RUN apk upgrade --no-cache

# Corporate certificates
COPY certs/company-root-ca.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

# Monitoring agent
COPY monitoring-agent /usr/local/bin/
RUN chmod +x /usr/local/bin/monitoring-agent

# Non-root user
RUN addgroup -g 10001 appuser && \
    adduser -D -u 10001 -G appuser appuser

# Labels for tracking
LABEL maintainer="platform-team@company.com" \
      org.company.version="1.0.0" \
      org.company.approved="true"

USER appuser
```

**Usage:**
```dockerfile
FROM company-registry.com/base/node:18

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

CMD ["node", "server.js"]
```

### 2. Image Promotion Pipeline

```
Development → Testing → Staging → Production

dev-registry      → test-registry   → stage-registry  → prod-registry
myapp:dev-abc123  → myapp:test-v1.2 → myapp:stage-v1.2 → myapp:prod-v1.2
```

**GitLab CI Example:**
```yaml
stages:
  - build
  - test
  - promote-test
  - promote-stage
  - promote-prod

build:
  stage: build
  script:
    - docker build -t $DEV_REGISTRY/myapp:$CI_COMMIT_SHA .
    - docker push $DEV_REGISTRY/myapp:$CI_COMMIT_SHA

test:
  stage: test
  script:
    - docker pull $DEV_REGISTRY/myapp:$CI_COMMIT_SHA
    - docker run $DEV_REGISTRY/myapp:$CI_COMMIT_SHA npm test

promote-to-test:
  stage: promote-test
  script:
    - docker pull $DEV_REGISTRY/myapp:$CI_COMMIT_SHA
    - docker tag $DEV_REGISTRY/myapp:$CI_COMMIT_SHA $TEST_REGISTRY/myapp:$VERSION
    - docker push $TEST_REGISTRY/myapp:$VERSION

promote-to-production:
  stage: promote-prod
  when: manual
  only:
    - main
  script:
    - docker pull $STAGE_REGISTRY/myapp:$VERSION
    - docker tag $STAGE_REGISTRY/myapp:$VERSION $PROD_REGISTRY/myapp:$VERSION
    - docker push $PROD_REGISTRY/myapp:$VERSION
```

## Registry Patterns

### Multi-Region Registry Setup

```yaml
# Harbor HA setup
version: '3.8'

services:
  harbor-core:
    image: goharbor/harbor-core:latest
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.labels.region == us-east-1

  harbor-db:
    image: postgres:15
    volumes:
      - harbor-db:/var/lib/postgresql/data
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.type == storage

  harbor-redis:
    image: redis:7-alpine
    deploy:
      replicas: 3

  registry:
    image: goharbor/registry-photon:latest
    volumes:
      - registry-data:/storage
    deploy:
      replicas: 3
```

### Image Caching Strategy

```yaml
# Pull-through cache
version: '3.8'

services:
  registry-cache:
    image: registry:2
    environment:
      REGISTRY_PROXY_REMOTEURL: https://registry-1.docker.io
      REGISTRY_STORAGE_CACHE_BLOBDESCRIPTOR: inmemory
    volumes:
      - registry-cache:/var/lib/registry
    ports:
      - "5000:5000"
```

## Security Patterns

### 1. Image Scanning Pipeline

```yaml
# Scan in CI/CD
security-scan:
  stage: security
  image: aquasec/trivy:latest
  script:
    - trivy image --severity HIGH,CRITICAL --exit-code 1 $IMAGE
  allow_failure: false

policy-check:
  stage: security
  image: openpolicyagent/conftest:latest
  script:
    - conftest test Dockerfile --policy policy/
```

### 2. Runtime Security

```yaml
services:
  app:
    image: myapp:latest
    security_opt:
      - no-new-privileges:true
      - seccomp:default.json
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
    user: "10001:10001"
```

### 3. Secrets Management

```yaml
# Using HashiCorp Vault
services:
  app:
    image: myapp:latest
    environment:
      VAULT_ADDR: https://vault.company.com
      VAULT_ROLE: myapp-prod
    volumes:
      - /var/run/secrets:/secrets:ro
    entrypoint:
      - /vault-init.sh  # Fetch secrets before starting app
```

## Deployment Patterns

### 1. Blue-Green Deployment

```yaml
# blue-stack.yml
version: '3.8'
services:
  app:
    image: myapp:v1
    labels:
      environment: blue
    networks:
      - app-network

# green-stack.yml
version: '3.8'
services:
  app:
    image: myapp:v2
    labels:
      environment: green
    networks:
      - app-network

# Load balancer switches between blue and green
```

### 2. Canary Deployment

```yaml
version: '3.8'

services:
  app-stable:
    image: myapp:v1
    deploy:
      replicas: 9  # 90% of traffic
      labels:
        - "traefik.http.services.app.loadbalancer.weight=90"

  app-canary:
    image: myapp:v2
    deploy:
      replicas: 1  # 10% of traffic
      labels:
        - "traefik.http.services.app.loadbalancer.weight=10"
```

### 3. Rolling Deployment with Health Checks

```yaml
version: '3.8'

services:
  app:
    image: myapp:latest
    deploy:
      replicas: 10
      update_config:
        parallelism: 2
        delay: 30s
        order: start-first
        failure_action: rollback
        monitor: 60s
      rollback_config:
        parallelism: 5
        delay: 0s
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 60s
```

## Monitoring and Observability

### Centralized Monitoring Stack

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=90d'
    deploy:
      replicas: 2
      placement:
        constraints:
          - node.role == manager

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-data:/var/lib/grafana
      - ./dashboards:/etc/grafana/provisioning/dashboards
    environment:
      GF_AUTH_LDAP_ENABLED: "true"
      GF_AUTH_LDAP_CONFIG_FILE: /etc/grafana/ldap.toml
      GF_INSTALL_PLUGINS: grafana-piechart-panel,grafana-clock-panel

  loki:
    image: grafana/loki:latest
    command: -config.file=/etc/loki/config.yaml
    volumes:
      - ./loki-config.yaml:/etc/loki/config.yaml
      - loki-data:/loki

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    command: -config.file=/etc/promtail/config.yaml

  jaeger:
    image: jaegertracing/all-in-one:latest
    environment:
      COLLECTOR_ZIPKIN_HOST_PORT: :9411
    ports:
      - "16686:16686"
```

## Multi-Tenancy Pattern

```yaml
# Tenant isolation with labels and networks
version: '3.8'

services:
  tenant-a-app:
    image: myapp:latest
    networks:
      - tenant-a
    deploy:
      placement:
        constraints:
          - node.labels.tenant == a
      resources:
        limits:
          cpus: '2'
          memory: 2G
    labels:
      tenant: "a"
      cost-center: "engineering"

  tenant-b-app:
    image: myapp:latest
    networks:
      - tenant-b
    deploy:
      placement:
        constraints:
          - node.labels.tenant == b
      resources:
        limits:
          cpus: '1'
          memory: 1G
    labels:
      tenant: "b"
      cost-center: "sales"

networks:
  tenant-a:
    driver: overlay
    internal: true
  tenant-b:
    driver: overlay
    internal: true
```

## Cost Optimization

### Resource Right-Sizing

```yaml
services:
  app:
    image: myapp:latest
    deploy:
      resources:
        # Based on actual usage metrics
        limits:
          cpus: '1.5'
          memory: 1.5G
        reservations:
          cpus: '0.75'
          memory: 768M
      # Scale based on time
      labels:
        - "autoscaler.min=2"
        - "autoscaler.max=10"
        - "autoscaler.schedule=0 0 * * * 2-6"  # Scale up weekdays
```

### Spot Instance Strategy

```yaml
# Use spot instances for non-critical workloads
services:
  batch-processor:
    image: batch-app:latest
    deploy:
      placement:
        constraints:
          - node.labels.instance-type == spot
      restart_policy:
        condition: any  # Handle spot termination
        delay: 5s
```

## Compliance and Governance

### Image Policy

```rego
# Open Policy Agent policy
package docker

deny[msg] {
  input.config.User == ""
  msg = "Image must not run as root"
}

deny[msg] {
  input.config.Image contains ":latest"
  msg = "Image must use specific version tags"
}

deny[msg] {
  not startswith(input.config.Image, "company-registry.com/")
  msg = "Image must come from approved registry"
}
```

### Audit Logging

```yaml
services:
  audit-logger:
    image: audit-logger:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - audit-logs:/logs
    environment:
      LOG_LEVEL: info
      EXPORT_TO: s3://audit-logs/
```

## Disaster Recovery

### Backup Strategy

```bash
#!/bin/bash
# Enterprise backup script

BACKUP_DIR="/backup/$(date +%Y/%m/%d)"
mkdir -p $BACKUP_DIR

# Backup all volumes
for volume in $(docker volume ls -q); do
  echo "Backing up volume: $volume"
  docker run --rm \
    -v $volume:/source:ro \
    -v $BACKUP_DIR:/backup \
    alpine \
    tar czf /backup/${volume}.tar.gz -C /source .
done

# Backup Docker configs and secrets
docker config ls --format '{{.Name}}' | while read config; do
  docker config inspect $config > $BACKUP_DIR/config-${config}.json
done

docker secret ls --format '{{.Name}}' | while read secret; do
  # Note: Secret values cannot be retrieved
  docker secret inspect $secret > $BACKUP_DIR/secret-${secret}-metadata.json
done

# Upload to S3
aws s3 sync $BACKUP_DIR s3://company-backups/docker/$(date +%Y/%m/%d)/

# Retention: keep 30 days
find /backup -mtime +30 -delete
```

## Enterprise Checklist

- [ ] Golden base images with security patches
- [ ] Private registry with HA
- [ ] Image scanning in CI/CD
- [ ] Image promotion pipeline
- [ ] Secrets management (Vault, AWS Secrets Manager)
- [ ] Centralized logging (ELK, Loki)
- [ ] Monitoring (Prometheus, Grafana)
- [ ] Distributed tracing (Jaeger, Zipkin)
- [ ] Resource quotas and limits
- [ ] Multi-tenancy isolation
- [ ] Compliance policies (OPA)
- [ ] Automated backups
- [ ] Disaster recovery plan
- [ ] Cost allocation and optimization
- [ ] Documentation and runbooks

## Interview Questions

**Q: How do you manage Docker images across multiple environments?**
A: Use image promotion pipelines, separate registries per environment, immutable tags with version numbers, and automated testing at each stage.

**Q: What's your strategy for secrets management in Docker?**
A: Use external secret managers (Vault, AWS Secrets Manager), Docker secrets for Swarm, or Kubernetes secrets. Never hardcode secrets in images or environment variables.

**Q: How do you implement multi-tenancy with Docker?**
A: Use network isolation, resource quotas, node placement constraints, and labels. Consider separate clusters for strong isolation requirements.

**Q: What's your approach to Docker security at scale?**
A: Image scanning, signed images, minimal base images, non-root users, security policies (OPA), runtime security, and regular audits.

**Next:** [Interview Questions →](interview-questions-advanced.md)
