# Docker Performance Tuning

Optimize Docker for better performance and resource utilization.

## Container Performance

### Resource Limits

```bash
# Memory limit
docker run -m 512m myapp

# CPU limit (1.5 cores)
docker run --cpus="1.5" myapp

# Combined limits
docker run -m 1g --cpus="2" myapp

# Memory reservation
docker run --memory-reservation=256m -m 512m myapp

# CPU shares (relative weight)
docker run --cpu-shares=512 myapp
```

### Monitor Resource Usage

```bash
# Real-time stats
docker stats

# Single container
docker stats mycontainer

# Format output
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# No streaming
docker stats --no-stream
```

## Storage Performance

### Choose Right Storage Driver

```bash
# Check current driver
docker info | grep "Storage Driver"

# Configure in /etc/docker/daemon.json
{
  "storage-driver": "overlay2"
}
```

**Storage Driver Performance:**
- **overlay2**: Best for most use cases (recommended)
- **aufs**: Legacy, slower
- **devicemapper**: Avoid in production
- **zfs**: Good for specific workloads
- **btrfs**: Good for specific workloads

### Volume Performance

```bash
# Named volume (good performance)
docker run -v data:/app/data myapp

# Bind mount with delegated (better performance on Mac/Windows)
docker run -v $(pwd):/app:delegated myapp

# tmpfs for temporary data (best performance)
docker run --tmpfs /tmp myapp
```

### Clean Up Regularly

```bash
# Remove unused data
docker system prune

# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune

# Aggressive cleanup
docker system prune -a --volumes
```

## Network Performance

### Use Host Network (when appropriate)

```bash
# Best performance but no isolation
docker run --network host myapp
```

### Optimize Bridge Network

```bash
# Create custom bridge with better settings
docker network create \
  --driver bridge \
  --opt com.docker.network.bridge.name=docker1 \
  --opt com.docker.network.driver.mtu=1500 \
  my-bridge
```

### Use Internal Networks

```bash
# Internal network (no external access = better performance)
docker network create --internal backend
```

## Build Performance

### Use BuildKit

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build with parallel stages
docker build --build-arg BUILDKIT_INLINE_CACHE=1 .
```

### Optimize Dockerfile

```dockerfile
# Bad: Invalidates cache often
FROM node:18
WORKDIR /app
COPY . .
RUN npm install

# Good: Cache dependencies
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
```

### Use Cache Mounts

```dockerfile
# Cache npm packages
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production

# Cache pip packages
FROM python:3.11
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Cache Go modules
FROM golang:1.21
WORKDIR /app
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download
```

### Multi-stage Builds

```dockerfile
# Smaller final image = faster deployment
FROM node:18 AS builder
WORKDIR /app
COPY . .
RUN npm run build

FROM node:18-alpine
COPY --from=builder /app/dist ./dist
CMD ["node", "dist/server.js"]
```

## Runtime Performance

### Use Specific Base Images

```dockerfile
# Faster startup, smaller size
FROM node:18-alpine
# vs
FROM node:18  # Larger, slower
```

### Reduce Startup Time

```dockerfile
# Use slim or alpine variants
FROM python:3.11-slim

# Minimize layers
RUN apt-get update && \
    apt-get install -y package1 package2 && \
    rm -rf /var/lib/apt/lists/*

# Pre-compile Python
RUN python -m compileall .
```

### Connection Pooling

```javascript
// Database connection pool
const pool = new Pool({
  max: 20,
  min: 5,
  idleTimeoutMillis: 30000
});

// Redis connection pool
const redis = new Redis({
  maxRetriesPerRequest: 3,
  enableReadyCheck: true,
  lazyConnect: true
});
```

## Docker Daemon Performance

### daemon.json Configuration

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  },
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 10
}
```

### System Tuning

```bash
# Increase file descriptors
ulimit -n 64000

# Kernel parameters for better networking
sysctl -w net.ipv4.ip_forward=1
sysctl -w net.bridge.bridge-nf-call-iptables=1

# For high-load systems
sysctl -w net.core.somaxconn=1024
sysctl -w net.ipv4.tcp_max_syn_backlog=2048
```

## Monitoring and Profiling

### cAdvisor

```bash
docker run -d \
  --name=cadvisor \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --publish=8080:8080 \
  gcr.io/cadvisor/cadvisor:latest
```

### Prometheus + Grafana

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

  node-exporter:
    image: prom/node-exporter
    ports:
      - "9100:9100"
```

## Performance Testing

### Load Testing

```bash
# Apache Bench
docker run --rm \
  -v $(pwd):/tmp \
  jordi/ab \
  ab -n 10000 -c 100 http://myapp/

# wrk
docker run --rm \
  williamyeh/wrk \
  wrk -t12 -c400 -d30s http://myapp/

# Hey
docker run --rm \
  rakyll/hey \
  hey -n 10000 -c 100 http://myapp/
```

### Benchmarking

```bash
# Container startup time
time docker run --rm alpine echo "hello"

# Image pull time
time docker pull nginx:alpine

# Build time
time docker build -t myapp .
```

## Optimization Checklist

### Image Optimization
- [ ] Use minimal base images (Alpine, distroless)
- [ ] Multi-stage builds
- [ ] Minimize layers
- [ ] Use .dockerignore
- [ ] Order commands by change frequency

### Runtime Optimization
- [ ] Set appropriate resource limits
- [ ] Use health checks
- [ ] Connection pooling
- [ ] Proper logging configuration
- [ ] Regular cleanup of unused resources

### Network Optimization
- [ ] Use host network when appropriate
- [ ] Custom bridge networks
- [ ] Internal networks for backend services
- [ ] Proper DNS configuration

### Storage Optimization
- [ ] Use overlay2 driver
- [ ] Regular pruning
- [ ] tmpfs for temporary data
- [ ] Named volumes for persistence

## Real-World Example

```yaml
version: '3.8'

services:
  app:
    image: myapp:latest
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    environment:
      NODE_ENV: production
      NODE_OPTIONS: "--max-old-space-size=896"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    command: postgres -c max_connections=200 -c shared_buffers=256MB
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          memory: 512M
    networks:
      - app-network

volumes:
  postgres-data:

networks:
  app-network:
    driver: bridge
```

## Troubleshooting Performance Issues

```bash
# High CPU usage
docker stats --no-stream
docker top mycontainer

# High memory usage
docker stats mycontainer
docker inspect --format='{{.HostConfig.Memory}}' mycontainer

# Slow network
docker exec mycontainer ping -c 4 google.com
docker network inspect my-network

# Disk I/O
docker stats --format "{{.Container}}: {{.BlockIO}}"

# Check logs for errors
docker logs --tail 100 mycontainer
```

## Interview Questions

**Q: How do you optimize Docker image size?**
A: Use Alpine/distroless base images, multi-stage builds, minimize layers, use .dockerignore, and remove unnecessary files in the same RUN command.

**Q: What's the impact of resource limits on performance?**
A: Resource limits prevent containers from consuming all host resources but can throttle performance if set too low. Balance between isolation and performance.

**Q: How do you monitor Docker container performance?**
A: Use docker stats, cAdvisor, Prometheus+Grafana, or cloud provider monitoring tools. Monitor CPU, memory, network, and disk I/O.

**Next:** [Multi-Architecture Images →](19-multi-arch.md)
