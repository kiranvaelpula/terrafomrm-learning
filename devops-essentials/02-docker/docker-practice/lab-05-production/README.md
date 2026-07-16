# Lab 5: Production Deployment

Prepare and deploy Docker applications for production.

## Learning Objectives

- Production-ready Dockerfiles
- Security hardening
- Resource limits
- Health checks
- Logging and monitoring
- Backup strategies

## Prerequisites

- Completed Labs 1-4

## Exercise 1: Production Dockerfile

**Best practices:**
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:18-alpine
RUN apk add --no-cache dumb-init
WORKDIR /app

# Non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
    
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules

USER nodejs

HEALTHCHECK --interval=30s --timeout=3s \
  CMD node healthcheck.js

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/server.js"]
```

---

## Exercise 2: Production Compose

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  app:
    image: registry.company.com/myapp:${VERSION}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      rollback_config:
        parallelism: 1
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    environment:
      NODE_ENV: production
    env_file:
      - .env.production
    secrets:
      - db_password
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    deploy:
      resources:
        limits:
          memory: 2G
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./backups:/backups
    secrets:
      - db_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 10s
      retries: 5
    networks:
      - app-network

volumes:
  postgres-data:
    driver: local

networks:
  app-network:
    driver: bridge

secrets:
  db_password:
    external: true
```

---

## Exercise 3: Monitoring Stack

**docker-compose.monitoring.yml:**
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
      - '--storage.tsdb.retention.time=30d'
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    ports:
      - "8080:8080"

volumes:
  prometheus-data:
  grafana-data:
```

---

## Exercise 4: Backup Script

**backup.sh:**
```bash
#!/bin/bash
BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup database
docker exec postgres pg_dumpall -U postgres > \
  $BACKUP_DIR/database.sql

# Backup volumes
docker run --rm \
  -v postgres-data:/data:ro \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/postgres-data.tar.gz -C /data .

# Upload to S3
aws s3 sync $BACKUP_DIR s3://my-backups/$(date +%Y/%m/%d)/

# Keep only last 7 days
find /backups -mtime +7 -delete
```

---

## Exercise 5: Security Hardening

**Secure configuration:**
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
      - /tmp:noexec,nosuid,size=100m
    user: "1001:1001"
```

---

## Challenge: Complete Production Stack

**Deploy:**
- Application (3 replicas)
- Database with backup
- Redis cache
- Load balancer (Traefik)
- Monitoring (Prometheus/Grafana)
- Logging (ELK or Loki)
- Automated backups
- Health checks
- Resource limits
- Security hardening

<details>
<summary>Solution Files</summary>

See full solution in `production-example/` directory:
- docker-compose.yml
- docker-compose.prod.yml
- Dockerfile
- backup.sh
- monitoring/
- security/

Run:
```bash
docker-compose -f docker-compose.yml \
  -f docker-compose.prod.yml \
  up -d
```
</details>

---

## Verification Checklist

- [ ] Multi-stage Dockerfile
- [ ] Non-root user
- [ ] Health checks
- [ ] Resource limits
- [ ] Logging configuration
- [ ] Secrets management
- [ ] Backup strategy
- [ ] Monitoring setup
- [ ] Security hardening
- [ ] Rolling updates

---

## Lab Complete!

🎉 **Congratulations!** You've completed all Docker labs!

**You now know:**
- ✅ Docker basics and commands
- ✅ Building custom images
- ✅ Multi-container applications
- ✅ Networking and communication
- ✅ Production deployment
- ✅ Security and monitoring
- ✅ Backup and recovery

**Next Steps:**
- Practice with real projects
- Explore Docker Swarm or Kubernetes
- Learn CI/CD integration
- Study advanced patterns

---

## Additional Resources

- [Docker Production Checklist](https://docs.docker.com/config/containers/start-containers-automatically/)
- [Security Best Practices](https://docs.docker.com/engine/security/)
- [Monitoring Guide](https://docs.docker.com/config/daemon/prometheus/)
