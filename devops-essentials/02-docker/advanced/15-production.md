# Docker in Production

Best practices for running Docker containers in production environments.

## Overview

Production deployment requires careful consideration of reliability, security, scalability, monitoring, and disaster recovery.

## Production-Ready Dockerfile

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && \
    npm cache clean --force
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy artifacts
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --chown=nodejs:nodejs package*.json ./

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js || exit 1

# Switch to non-root user
USER nodejs

# Use dumb-init to handle signals
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/server.js"]
```

## Docker Compose for Production

```yaml
version: '3.8'

services:
  app:
    image: myregistry.com/myapp:${VERSION:-latest}
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      rollback_config:
        parallelism: 1
        delay: 5s
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    environment:
      NODE_ENV: production
      LOG_LEVEL: info
    env_file:
      - .env.production
    networks:
      - app-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "app,environment"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`app.example.com`)"

  db:
    image: postgres:15-alpine
    restart: unless-stopped
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./backups:/backups
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

volumes:
  postgres-data:
    driver: local
  redis-data:
    driver: local

networks:
  app-network:
    driver: bridge

secrets:
  db_password:
    external: true
```

## High Availability Setup

### Load Balancing with Traefik

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - letsencrypt:/letsencrypt
    networks:
      - proxy

  app:
    image: myapp:latest
    deploy:
      replicas: 3
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`app.example.com`)"
      - "traefik.http.routers.app.entrypoints=websecure"
      - "traefik.http.routers.app.tls.certresolver=letsencrypt"
      - "traefik.http.services.app.loadbalancer.healthcheck.path=/health"
    networks:
      - proxy
      - backend

volumes:
  letsencrypt:

networks:
  proxy:
  backend:
```

## Monitoring and Logging

### Prometheus + Grafana

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
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    ports:
      - "9090:9090"
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
      GF_INSTALL_PLUGINS: grafana-piechart-panel
    ports:
      - "3000:3000"
    networks:
      - monitoring
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    networks:
      - monitoring

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    ports:
      - "8080:8080"
    networks:
      - monitoring

volumes:
  prometheus-data:
  grafana-data:

networks:
  monitoring:
```

### Centralized Logging with ELK

```yaml
version: '3.8'

services:
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - elk

  logstash:
    image: logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch
    networks:
      - elk

  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    depends_on:
      - elasticsearch
    networks:
      - elk

  app:
    image: myapp:latest
    logging:
      driver: "fluentd"
      options:
        fluentd-address: localhost:24224
        tag: "docker.{{.Name}}"
    networks:
      - elk

volumes:
  elasticsearch-data:

networks:
  elk:
```

## Backup and Disaster Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup PostgreSQL
docker exec postgres pg_dumpall -U postgres > \
  ${BACKUP_DIR}/postgres_${DATE}.sql

# Backup volumes
docker run --rm \
  -v postgres-data:/data \
  -v ${BACKUP_DIR}:/backup \
  alpine tar czf /backup/postgres_data_${DATE}.tar.gz -C /data .

# Backup Redis
docker exec redis redis-cli BGSAVE
docker cp redis:/data/dump.rdb ${BACKUP_DIR}/redis_${DATE}.rdb

# Upload to S3
aws s3 sync ${BACKUP_DIR} s3://my-backups/$(date +%Y/%m/%d)/

# Cleanup old backups (keep last 7 days)
find ${BACKUP_DIR} -mtime +7 -delete
```

### Restore Script

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1

# Stop services
docker-compose stop app

# Restore database
docker exec -i postgres psql -U postgres < ${BACKUP_FILE}

# Restart services
docker-compose up -d
```

## Zero-Downtime Deployment

### Rolling Updates

```yaml
version: '3.8'

services:
  app:
    image: myapp:${VERSION}
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
        failure_action: rollback
      rollback_config:
        parallelism: 1
        delay: 5s
```

```bash
# Deploy new version
VERSION=v2.0.0 docker-compose up -d

# Rollback if needed
docker-compose rollback
```

### Blue-Green Deployment

```bash
# Deploy green (new version)
docker-compose -f docker-compose.green.yml up -d

# Test green environment
curl http://green.example.com/health

# Switch traffic
# Update load balancer or DNS

# Remove blue (old version)
docker-compose -f docker-compose.blue.yml down
```

## Performance Optimization

### Resource Limits

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Connection Pooling

```javascript
// Database connection pool
const pool = new Pool({
  host: process.env.DB_HOST,
  port: 5432,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  max: 20,  // Maximum pool size
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
});
```

## Security in Production

```yaml
services:
  app:
    image: myapp:latest
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    tmpfs:
      - /tmp
    user: "1001:1001"
```

## Production Checklist

- [ ] Use specific image tags (not latest)
- [ ] Implement health checks
- [ ] Configure resource limits
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Centralize logging (ELK/Loki)
- [ ] Implement automated backups
- [ ] Configure restart policies
- [ ] Use secrets management
- [ ] Enable TLS/SSL
- [ ] Run as non-root user
- [ ] Set up load balancing
- [ ] Implement CI/CD pipelines
- [ ] Configure auto-scaling
- [ ] Document runbooks
- [ ] Test disaster recovery

## Interview Questions

**Q: How do you achieve zero-downtime deployment with Docker?**
A: Use rolling updates, blue-green deployment, or canary releases. Configure health checks and use orchestration tools to manage the transition.

**Q: What's your backup strategy for Dockerized applications?**
A: Regular automated backups of volumes and databases, stored in multiple locations (local + cloud). Test restore procedures regularly.

**Q: How do you monitor Docker containers in production?**
A: Use Prometheus for metrics, Grafana for visualization, and ELK/Loki for logs. Monitor container health, resource usage, and application metrics.

**Next:** [Orchestration Intro →](16-orchestration-intro.md)
