# Docker Interview Questions - Advanced

Comprehensive Docker advanced interview questions for experienced professionals.

## Image Optimization

**Q1: Explain techniques to reduce Docker image size by 90%.**

**A:**

**1. Use minimal base images:**
```dockerfile
# Bad: 1.1GB
FROM ubuntu:22.04

# Better: 180MB
FROM python:3.11-slim

# Best: 50MB
FROM python:3.11-alpine

# Ultimate: 25MB (distroless)
FROM gcr.io/distroless/python3
```

**2. Multi-stage builds:**
```dockerfile
FROM golang:1.21 AS builder  # 800MB
WORKDIR /app
COPY . .
RUN go build -o app

FROM alpine:latest          # Final: 15MB
COPY --from=builder /app/app /app
CMD ["/app"]
```

**3. Remove build artifacts:**
```dockerfile
RUN apt-get update && \
    apt-get install -y build-essential && \
    make && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*
```

**4. Use .dockerignore**
**5. Compress binaries (`upx`)**
**6. Remove debug symbols (`strip`)**

---

**Q2: What is BuildKit and what advantages does it provide?**

**A:** BuildKit is Docker's improved build engine (since 18.09).

**Advantages:**
1. **Parallel build stages** - Faster builds
2. **Better caching** - Smarter invalidation
3. **Cache mounts** - Persist package manager caches
4. **Secrets** - Secure secret handling during build
5. **SSH forwarding** - Clone private repos
6. **Better output** - Progress indication

**Enable:**
```bash
export DOCKER_BUILDKIT=1
docker build .
```

**Cache mount example:**
```dockerfile
RUN --mount=type=cache,target=/root/.npm \
    npm install

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

**Secret example:**
```dockerfile
RUN --mount=type=secret,id=github_token \
    git clone https://$(cat /run/secrets/github_token)@github.com/private/repo
```

---

## Security

**Q3: How do you implement defense-in-depth security for Docker?**

**A:**

**Layer 1: Image Security**
- Use official/verified images
- Scan for vulnerabilities (Trivy, Snyk)
- Sign images (Docker Content Trust)
- Use specific tags, not `latest`
- Minimal base images

**Layer 2: Build Security**
- Multi-stage builds
- No secrets in images
- Scan during CI/CD
- SBOM generation

**Layer 3: Runtime Security**
```yaml
services:
  app:
    image: myapp
    user: "10001:10001"
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    tmpfs:
      - /tmp:noexec
```

**Layer 4: Host Security**
- User namespaces
- AppArmor/SELinux
- Seccomp profiles
- Limit Docker socket access

**Layer 5: Network Security**
- Isolated networks
- TLS for daemon
- Firewall rules
- Service mesh (Istio)

**Layer 6: Monitoring**
- Runtime scanning (Falco)
- Audit logs
- Anomaly detection

---

**Q4: Explain Docker Content Trust and image signing.**

**A:**

Docker Content Trust (DCT) verifies image publisher and integrity using digital signatures.

**Enable:**
```bash
export DOCKER_CONTENT_TRUST=1
```

**Push signed image:**
```bash
docker push myuser/myapp:v1
# Prompts for passphrase
# Creates signing keys
```

**Pull verification:**
```bash
docker pull myuser/myapp:v1
# Fails if signature invalid or missing
```

**Under the hood:**
- Uses Notary (TUF implementation)
- Root key (offline, secure)
- Targets key (signs images)
- Snapshot/timestamp keys

**CI/CD:**
```yaml
deploy:
  script:
    - export DOCKER_CONTENT_TRUST=1
    - export DOCKER_CONTENT_TRUST_ROOT_PASSPHRASE=$ROOT_KEY
    - export DOCKER_CONTENT_TRUST_REPOSITORY_PASSPHRASE=$REPO_KEY
    - docker push myapp:$VERSION
```

**Limitations:**
- Only Docker Hub and private registries with Notary
- Requires key management
- Adds overhead

---

**Q5: What are Linux capabilities and how do you use them with Docker?**

**A:**

Linux capabilities divide root privileges into smaller units.

**Common capabilities:**
- `NET_BIND_SERVICE` - Bind ports < 1024
- `NET_ADMIN` - Network configuration
- `SYS_ADMIN` - Mount, system admin
- `CHOWN` - Change file ownership
- `DAC_OVERRIDE` - Bypass file permissions

**Drop all, add specific:**
```yaml
services:
  web:
    image: nginx
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # Bind to port 80
```

**Why use:**
- Principle of least privilege
- Limit attack surface
- Non-root but with specific privileges

**Check container capabilities:**
```bash
docker run --rm alpine sh -c 'apk add -q libcap; capsh --print'
```

---

## Production Deployment

**Q6: Design a highly available Docker Swarm cluster.**

**A:**

**Architecture:**
```
┌─────────────────── Load Balancer (HAProxy/Nginx) ───────────────────┐
│                           ├─── 3 Manager Nodes ───┤                  │
│                           │  - Raft consensus      │                  │
│                           │  - API endpoints       │                  │
│                           │  - Scheduling          │                  │
│                           └────────────────────────┘                  │
│                                      ↓                                │
│                     ┌────────────────┴────────────────┐              │
│                     ↓                                  ↓              │
│            Worker Nodes (N)                   Worker Nodes (N)        │
│            - Run containers                   - Run containers        │
│            - Different zones                  - Different zones       │
└───────────────────────────────────────────────────────────────────────┘
```

**Setup:**

**1. Initialize first manager:**
```bash
docker swarm init --advertise-addr 192.168.1.10
```

**2. Add managers (odd number, 3-7):**
```bash
# Get manager token
docker swarm join-token manager

# On other managers
docker swarm join --token SWMTKN-... 192.168.1.10:2377
```

**3. Add workers:**
```bash
docker swarm join-token worker
# Join workers in different availability zones
```

**4. Label nodes:**
```bash
docker node update --label-add zone=us-east-1a worker1
docker node update --label-add zone=us-east-1b worker2
docker node update --label-add type=compute worker1
docker node update --label-add type=storage worker3
```

**5. Deploy service with HA:**
```yaml
version: '3.8'
services:
  app:
    image: myapp
    deploy:
      replicas: 5
      placement:
        max_replicas_per_node: 1
        preferences:
          - spread: node.labels.zone
        constraints:
          - node.role == worker
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
        failure_action: rollback
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 10s
      timeout: 5s
      retries: 3
```

**6. Set up monitoring:**
- Prometheus for metrics
- Grafana for visualization
- Alertmanager for alerts
- ELK/Loki for logs

**7. Backup:**
- Manager node state (`/var/lib/docker/swarm`)
- Volumes
- Secrets/configs

---

**Q7: Implement blue-green deployment with zero downtime.**

**A:**

**Strategy:**
1. Deploy new version (green) alongside current (blue)
2. Test green thoroughly
3. Switch traffic to green
4. Keep blue for rollback
5. Remove blue after confirmation

**Implementation:**

**docker-compose.blue.yml:**
```yaml
version: '3.8'
services:
  app-blue:
    image: myapp:v1
    deploy:
      replicas: 3
      labels:
        - "environment=blue"
        - "version=v1"
        - "traefik.enable=true"
        - "traefik.http.routers.app.rule=Host(`app.example.com`)"
        - "traefik.http.services.app-blue.loadbalancer.server.port=3000"
    networks:
      - app-network
```

**docker-compose.green.yml:**
```yaml
version: '3.8'
services:
  app-green:
    image: myapp:v2
    deploy:
      replicas: 3
      labels:
        - "environment=green"
        - "version=v2"
        - "traefik.enable=false"  # Initially disabled
        - "traefik.http.routers.app.rule=Host(`app.example.com`)"
        - "traefik.http.services.app-green.loadbalancer.server.port=3000"
    networks:
      - app-network
```

**Deployment script:**
```bash
#!/bin/bash

# Deploy green
docker stack deploy -c docker-compose.green.yml app

# Wait for health checks
sleep 30

# Test green
curl http://green.internal.example.com/health

# Switch traffic (update load balancer)
docker service update \
  --label-add "traefik.enable=true" \
  app_app-green

docker service update \
  --label-add "traefik.enable=false" \
  app_app-blue

# Monitor for issues
sleep 300

# If all good, remove blue
# docker stack rm app-blue

# If issues, rollback
# docker service update --label-add "traefik.enable=true" app_app-blue
# docker service update --label-add "traefik.enable=false" app_app-green
```

---

## Performance

**Q8: How do you diagnose and fix a slow Docker build?**

**A:**

**Diagnosis:**

**1. Analyze build time:**
```bash
time docker build -t myapp .
```

**2. Use BuildKit for detailed output:**
```bash
DOCKER_BUILDKIT=1 docker build --progress=plain -t myapp .
```

**3. Identify slow steps:**
Look for steps taking > 30 seconds

**Fixes:**

**1. Order by change frequency:**
```dockerfile
# Bad
COPY . .
RUN npm install

# Good
COPY package*.json ./
RUN npm install
COPY . .
```

**2. Use cache mounts:**
```dockerfile
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production
```

**3. Parallel stages:**
```dockerfile
FROM base AS deps
RUN npm install

FROM base AS builder
COPY --from=deps /node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS tester
COPY --from=deps /node_modules ./node_modules
COPY . .
RUN npm test
```

**4. Use .dockerignore:**
```
node_modules
.git
*.log
coverage
```

**5. Multi-stage builds**
**6. Use smaller base images**
**7. Build on faster disks (SSD)**
**8. Increase Docker resources**

**Benchmark:**
```bash
# Before: 5 minutes
# After optimizations: 30 seconds
```

---

**Q9: Container is consuming 100% CPU. Root cause analysis approach?**

**A:**

**Step 1: Confirm the issue**
```bash
docker stats --no-stream
# Look for CPUPerc
```

**Step 2: Check running processes**
```bash
docker top container-id
docker exec container-id ps aux
```

**Step 3: Profile the application**
```bash
# Node.js
docker exec container-id npm install -g clinic
docker exec container-id clinic doctor -- node app.js

# Python
docker exec container-id pip install py-spy
docker exec container-id py-spy top --pid 1

# Go
docker exec container-id go tool pprof http://localhost:6060/debug/pprof/profile
```

**Step 4: Check logs**
```bash
docker logs --tail 1000 container-id | grep -i error
```

**Step 5: Common causes**
- Infinite loops
- Memory leaks causing GC thrashing
- Inefficient algorithms
- Too many concurrent requests
- Resource contention

**Step 6: Immediate mitigation**
```bash
# Limit CPU
docker update --cpus=1.0 container-id

# Or restart with limits
docker run --cpus=1.0 -m 512m myapp
```

**Step 7: Long-term fixes**
- Optimize code
- Add caching
- Implement rate limiting
- Scale horizontally
- Use connection pooling

---

## Multi-Architecture

**Q10: Build a multi-architecture image for AMD64 and ARM64.**

**A:**

**Setup:**
```bash
# Install QEMU for cross-platform building
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

# Create buildx builder
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap
```

**Dockerfile:**
```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.21 AS builder
ARG TARGETOS
ARG TARGETARCH

WORKDIR /app
COPY . .

# Build for target architecture
RUN GOOS=$TARGETOS GOARCH=$TARGETARCH \
    go build -o myapp .

FROM alpine:latest
COPY --from=builder /app/myapp /myapp
CMD ["/myapp"]
```

**Build and push:**
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t myuser/myapp:latest \
  --push \
  .
```

**Verify:**
```bash
docker buildx imagetools inspect myuser/myapp:latest
```

**CI/CD (GitHub Actions):**
```yaml
- name: Set up QEMU
  uses: docker/setup-qemu-action@v2

- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v2

- name: Build and push
  uses: docker/build-push-action@v4
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: myuser/myapp:latest
```

---

## Enterprise Patterns

**Q11: Design an enterprise Docker registry strategy.**

**A:**

**Architecture:**

```
┌──────────── PRODUCTION REGISTRY ────────────┐
│  registry.prod.company.com                  │
│  - Signed images only                       │
│  - Immutable tags                           │
│  - Strict policies                          │
└─────────────────────────────────────────────┘
                    ↑
                    │ Promotion
┌──────────── STAGING REGISTRY ───────────────┐
│  registry.stage.company.com                 │
│  - Security scanned                         │
│  - Integration tested                       │
│  - Compliance checked                       │
└─────────────────────────────────────────────┘
                    ↑
                    │ Promotion
┌──────────── TEST REGISTRY ──────────────────┐
│  registry.test.company.com                  │
│  - Unit tested                              │
│  - Basic scans                              │
└─────────────────────────────────────────────┘
                    ↑
                    │ Build
┌──────────── DEV REGISTRY ───────────────────┐
│  registry.dev.company.com                   │
│  - Feature branches                         │
│  - Short retention                          │
└─────────────────────────────────────────────┘
```

**Components:**

**1. Harbor (Primary Registry):**
```yaml
version: '3.8'
services:
  harbor-core:
    image: goharbor/harbor-core:v2.9.0
    deploy:
      replicas: 3
      
  harbor-db:
    image: postgres:15
    volumes:
      - harbor-db:/var/lib/postgresql/data
      
  registry:
    image: goharbor/registry-photon:v2.9.0
    volumes:
      - registry-data:/storage
    deploy:
      replicas: 3
```

**2. Image Promotion Pipeline:**
```yaml
# .gitlab-ci.yml
stages:
  - build
  - scan
  - promote-test
  - promote-stage
  - promote-prod

build:
  script:
    - docker build -t $DEV_REGISTRY/myapp:$CI_COMMIT_SHA .
    - docker push $DEV_REGISTRY/myapp:$CI_COMMIT_SHA

security-scan:
  script:
    - trivy image --severity CRITICAL,HIGH $DEV_REGISTRY/myapp:$CI_COMMIT_SHA

promote-to-test:
  script:
    - docker pull $DEV_REGISTRY/myapp:$CI_COMMIT_SHA
    - docker tag $DEV_REGISTRY/myapp:$CI_COMMIT_SHA $TEST_REGISTRY/myapp:$VERSION
    - docker push $TEST_REGISTRY/myapp:$VERSION

promote-to-production:
  when: manual
  script:
    - docker pull $STAGE_REGISTRY/myapp:$VERSION
    - docker tag $STAGE_REGISTRY/myapp:$VERSION $PROD_REGISTRY/myapp:$VERSION
    - docker push $PROD_REGISTRY/myapp:$VERSION
    - # Sign image
    - docker trust sign $PROD_REGISTRY/myapp:$VERSION
```

**3. Policies (OPA):**
```rego
package registry

deny[msg] {
  input.image contains ":latest"
  msg = "latest tag not allowed"
}

deny[msg] {
  not startswith(input.image, "registry.company.com/")
  msg = "images must come from approved registry"
}

deny[msg] {
  vulnerabilities := input.scan.vulnerabilities
  critical := [v | v := vulnerabilities[_]; v.severity == "CRITICAL"]
  count(critical) > 0
  msg = "critical vulnerabilities found"
}
```

**4. Monitoring:**
- Registry metrics (Prometheus)
- Pull/push rates
- Storage usage
- Failed authentications
- Vulnerability scan results

---

**Q12: Implement cost optimization for Docker at scale.**

**A:**

**1. Image Optimization:**
```dockerfile
# Before: 1.2GB
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3

# After: 50MB
FROM python:3.11-alpine
```
**Savings:** 96% storage reduction

**2. Resource Right-sizing:**
```yaml
services:
  app:
    deploy:
      resources:
        # Based on actual usage metrics
        limits:
          cpus: '0.5'      # Was: 2
          memory: 512M     # Was: 2G
        reservations:
          cpus: '0.25'
          memory: 256M
```
**Savings:** 75% compute cost reduction

**3. Spot Instances:**
```yaml
services:
  batch-worker:
    deploy:
      placement:
        constraints:
          - node.labels.instance-type == spot
      restart_policy:
        condition: any
```
**Savings:** 60-90% on compute

**4. Auto-scaling:**
```yaml
services:
  app:
    deploy:
      replicas: 3  # Minimum
      # Scale based on metrics
      labels:
        - "autoscaler.max=10"
        - "autoscaler.metric=cpu"
        - "autoscaler.target=75"
```

**5. Registry Cleanup:**
```bash
# Remove old images
docker image prune -a --filter "until=720h"  # 30 days

# Harbor garbage collection
docker exec harbor-core harbor-gc
```

**6. Resource Monitoring:**
```yaml
# Prometheus alerts
- alert: HighResourceWaste
  expr: (container_memory_usage / container_spec_memory_limit) < 0.3
  annotations:
    summary: "Container {{ $labels.name }} using < 30% of allocated memory"
```

**7. Cost Allocation:**
```yaml
services:
  app:
    labels:
      - "cost-center=engineering"
      - "team=backend"
      - "project=api"
    # Export to billing
```

**Result:**
- 60% reduction in compute costs
- 80% reduction in storage costs
- Better resource utilization

---

## Scenario-Based Questions

**Q13: Production database container crashed. Recovery strategy?**

**A:**

**Immediate Response:**

**1. Check container status:**
```bash
docker ps -a | grep db
docker inspect --format='{{.State}}' db-container
```

**2. Check logs:**
```bash
docker logs --tail 200 db-container
# Look for: OOM, disk full, corruption
```

**3. Check host resources:**
```bash
df -h
free -h
docker system df
```

**Quick Recovery:**

**If volume intact:**
```bash
# Restart container
docker start db-container

# Or recreate with same volume
docker run -d \
  --name db-new \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:15
```

**If data corruption:**
```bash
# Restore from backup
docker run --rm \
  -v postgres-data:/data \
  -v /backups:/backup \
  ubuntu bash -c "cd /data && rm -rf * && tar xzf /backup/latest.tar.gz"

# Start container
docker start db-container
```

**Root Cause Analysis:**

**1. OOM Kill:**
```bash
dmesg | grep -i "killed process"
# Solution: Increase memory limit
```

**2. Disk Full:**
```bash
df -h
# Solution: Clean up logs, increase disk
```

**3. Corruption:**
```bash
# Check volume
docker run --rm -v postgres-data:/data ubuntu ls -la /data
# Solution: Restore from backup
```

**Prevention:**
```yaml
services:
  db:
    image: postgres:15
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
      restart_policy:
        condition: any
        delay: 5s
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 10s
      retries: 5
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - /backups:/backups  # Automated backups
```

**Backup Strategy:**
```bash
# Automated hourly backups
0 * * * * docker exec postgres pg_dumpall > /backups/$(date +\%Y\%m\%d_\%H).sql
```

---

**Q14: Implement disaster recovery for Docker Swarm cluster.**

**A:**

**DR Strategy:**

**1. Backup Components:**

**Manager nodes:**
```bash
# Stop Docker on manager
systemctl stop docker

# Backup Swarm state
tar czf swarm-backup.tar.gz -C /var/lib/docker/swarm .

# Backup certificates
tar czf certs-backup.tar.gz -C /var/lib/docker/swarm/certificates .

# Start Docker
systemctl start docker
```

**Volumes:**
```bash
# Backup all volumes
for vol in $(docker volume ls -q); do
  docker run --rm \
    -v $vol:/data \
    -v /backup:/backup \
    alpine tar czf /backup/$vol-$(date +%Y%m%d).tar.gz -C /data .
done
```

**Configurations:**
```bash
# Export configs
docker config ls -q | while read config; do
  docker config inspect $config > configs/$config.json
done

# Export secrets metadata (values can't be retrieved)
docker secret ls -q | while read secret; do
  docker secret inspect $secret > secrets/$secret.json
done
```

**2. Automated Backup Script:**
```bash
#!/bin/bash
BACKUP_DIR="/dr-backups/$(date +%Y/%m/%d)"
mkdir -p $BACKUP_DIR

# Backup Swarm state
if [ "$(docker info --format '{{.Swarm.ControlAvailable}}')" == "true" ]; then
  systemctl stop docker
  tar czf $BACKUP_DIR/swarm.tar.gz -C /var/lib/docker/swarm .
  systemctl start docker
fi

# Backup volumes
docker volume ls -q | while read vol; do
  docker run --rm \
    -v $vol:/data:ro \
    -v $BACKUP_DIR:/backup \
    alpine tar czf /backup/$vol.tar.gz -C /data .
done

# Upload to S3
aws s3 sync $BACKUP_DIR s3://company-dr/$(date +%Y/%m/%d)/

# Retention: 30 days
find /dr-backups -mtime +30 -delete
```

**3. Restore Procedure:**

**Step 1: Restore manager:**
```bash
# Stop Docker
systemctl stop docker

# Clear existing
rm -rf /var/lib/docker/swarm

# Restore from backup
tar xzf swarm-backup.tar.gz -C /var/lib/docker/swarm

# Start Docker
systemctl start docker
docker swarm init --force-new-cluster
```

**Step 2: Restore volumes:**
```bash
for backup in /backup/*.tar.gz; do
  vol=$(basename $backup .tar.gz)
  docker volume create $vol
  docker run --rm \
    -v $vol:/data \
    -v /backup:/backup \
    alpine tar xzf /backup/$backup -C /data
done
```

**Step 3: Redeploy services:**
```bash
docker stack deploy -c docker-compose.yml myapp
```

**4. DR Testing:**
```bash
# Monthly DR drill
# 1. Restore in test environment
# 2. Verify data integrity
# 3. Test application functionality
# 4. Document recovery time
```

**RPO/RTO:**
- RPO: 1 hour (hourly backups)
- RTO: 30 minutes (automated restore)

---

**Q15: Debug intermittent network issues between containers.**

**A:**

**Symptoms:**
- Random connection timeouts
- DNS resolution failures
- Packet loss

**Investigation:**

**1. Check DNS:**
```bash
# Test DNS resolution
docker exec app1 nslookup app2
docker exec app1 ping app2

# Check DNS server
docker exec app1 cat /etc/resolv.conf
# Should be 127.0.0.11 (Docker DNS)
```

**2. Check network configuration:**
```bash
# Inspect network
docker network inspect my-network

# Check container network
docker inspect --format='{{.NetworkSettings.Networks}}' app1
```

**3. Test connectivity:**
```bash
# Ping between containers
docker exec app1 ping -c 10 app2

# TCP connection test
docker exec app1 nc -zv app2 3000

# Trace route
docker exec app1 traceroute app2
```

**4. Check for port conflicts:**
```bash
# List all port mappings
docker ps --format "{{.Names}}\t{{.Ports}}"

# Check host ports
netstat -tulpn | grep LISTEN
```

**5. Monitor network performance:**
```bash
# Real-time network stats
docker stats --format "table {{.Container}}\t{{.NetIO}}"

# Detailed network info
docker exec app1 netstat -s
```

**Common Causes & Solutions:**

**1. DNS caching issues:**
```yaml
services:
  app:
    dns:
      - 8.8.8.8
      - 1.1.1.1
    dns_search:
      - company.internal
```

**2. MTU mismatch:**
```bash
# Check MTU
docker network inspect my-network | grep mtu

# Create network with correct MTU
docker network create --driver bridge --opt com.docker.network.driver.mtu=1450 my-network
```

**3. Connection pooling exhaustion:**
```javascript
// Increase pool size
const pool = new Pool({
  max: 50,  // Increased from 20
  connectionTimeoutMillis: 5000
});
```

**4. Network congestion:**
```bash
# Limit bandwidth if needed
docker run --network-bandwidth 1m myapp
```

**5. Firewall rules:**
```bash
# Check iptables
iptables -L -n -v

# Check Docker chains
iptables -t nat -L -n -v | grep DOCKER
```

**Prevention:**
```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost/health"]
      interval: 10s
      timeout: 5s
      retries: 3
    networks:
      - app-network
    deploy:
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

networks:
  app-network:
    driver: overlay
    driver_opts:
      com.docker.network.driver.mtu: 1450
```

---

## Total: 15 Advanced Questions + Scenarios

These questions cover:
- ✅ Image optimization
- ✅ Security (DCT, capabilities, defense-in-depth)
- ✅ Production deployment (HA, blue-green)
- ✅ Performance tuning
- ✅ Multi-architecture
- ✅ Enterprise patterns
- ✅ Cost optimization
- ✅ Disaster recovery
- ✅ Troubleshooting

For more questions, see:
- [Basics Interview Questions](../basics/interview-questions-basics.md)
- [Intermediate Interview Questions](../intermediate/interview-questions-intermediate.md)
