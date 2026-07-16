# Docker Interview Questions - Intermediate

Comprehensive Docker intermediate interview questions with detailed answers.

## Multi-stage Builds

**Q1: What are multi-stage builds and why use them?**

**A:** Multi-stage builds use multiple FROM statements in a Dockerfile. Each FROM creates a new build stage. You can copy artifacts from one stage to another, leaving behind unwanted content.

**Benefits:**
- Smaller final images (10x-50x reduction)
- Separate build and runtime dependencies
- Better security (fewer tools in production image)
- Cleaner Dockerfiles

**Example:**
```dockerfile
FROM node:18 AS builder
WORKDIR /app
COPY . .
RUN npm install && npm run build

FROM node:18-alpine
COPY --from=builder /app/dist ./dist
CMD ["node", "dist/server.js"]
```

---

**Q2: How do you build only a specific stage in multi-stage Dockerfile?**

**A:** Use the `--target` flag:

```bash
docker build --target builder -t myapp:builder .
docker build --target production -t myapp:prod .
```

This is useful for debugging and creating development vs production images.

---

**Q3: Can you reference external images in COPY --from?**

**A:** Yes! You can copy from any image, not just previous stages:

```dockerfile
FROM alpine
COPY --from=nginx:alpine /usr/share/nginx/html /html
COPY --from=golang:1.21 /usr/local/go /go
```

---

## Volumes and Data Management

**Q4: What's the difference between volumes and bind mounts?**

**A:**

| Feature | Volumes | Bind Mounts |
|---------|---------|-------------|
| Management | Docker managed | User managed |
| Location | Docker storage directory | Anywhere on host |
| Performance | Better on Windows/Mac | Host filesystem speed |
| Portability | Platform independent | Platform specific paths |
| Backup | Easier with Docker commands | Direct file access |

**When to use:**
- **Volumes**: Production data, shared between containers
- **Bind mounts**: Development, config files, logs

---

**Q5: How do you backup and restore Docker volumes?**

**A:**

**Backup:**
```bash
docker run --rm \
  -v myvolume:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/myvolume.tar.gz -C /data .
```

**Restore:**
```bash
docker run --rm \
  -v myvolume:/data \
  -v $(pwd):/backup \
  ubuntu tar xzf /backup/myvolume.tar.gz -C /data
```

---

**Q6: What's the difference between anonymous and named volumes?**

**A:**

**Named volumes:**
```bash
docker volume create my-data
docker run -v my-data:/app/data nginx
```
- Easy to reference
- Survives container removal
- Easy to manage

**Anonymous volumes:**
```bash
docker run -v /app/data nginx
```
- Random name (hard to reference)
- Removed with `docker rm -v`
- Used for temporary data

---

## Networking

**Q7: Explain Docker network types.**

**A:**

**1. Bridge (default):**
- Isolated network for containers
- Containers can communicate by name
- Need port mapping for external access

**2. Host:**
- Container uses host network directly
- No isolation, best performance
- Port conflicts possible

**3. None:**
- No networking
- Complete isolation
- Used for batch jobs

**4. Overlay:**
- Multi-host networking (Swarm)
- Containers across different hosts communicate
- Used in orchestration

---

**Q8: How does Docker DNS work?**

**A:** Docker provides built-in DNS server (127.0.0.11) for container name resolution:

```bash
# Create network
docker network create mynet

# Start containers
docker run -d --name db --network mynet postgres
docker run -d --name api --network mynet myapi

# 'api' can reach 'db' by name
docker exec api ping db  # Works!
```

**Note:** Default bridge network doesn't support DNS. Use custom bridge networks.

---

**Q9: What's the purpose of --link (and why is it deprecated)?**

**A:** `--link` was used for container communication before user-defined networks:

```bash
docker run --name db postgres
docker run --link db:database myapp
```

**Deprecated because:**
- Only works on single host
- Requires container order
- Can't dynamically update
- User-defined networks are better

**Modern approach:**
```bash
docker network create mynet
docker run --name db --network mynet postgres
docker run --name app --network mynet myapp
```

---

## Docker Compose

**Q10: What's the difference between 'docker-compose up' and 'docker-compose start'?**

**A:**

**`docker-compose up`:**
- Creates networks and volumes
- Creates and starts containers
- Rebuilds images if needed
- Shows logs by default

**`docker-compose start`:**
- Only starts existing containers
- Doesn't create anything
- Doesn't rebuild
- No logs output

**Workflow:**
```bash
docker-compose up -d        # First time
docker-compose stop         # Stop containers
docker-compose start        # Restart stopped containers
docker-compose down         # Remove everything
```

---

**Q11: How do you scale services in Docker Compose?**

**A:**

**Compose file:**
```yaml
services:
  web:
    image: nginx
    ports:
      - "8080-8082:80"  # Port range
```

**Scale:**
```bash
docker-compose up -d --scale web=3
```

**Note:** 
- Can't use specific port mapping (8080:80)
- Use port ranges or no host port
- Load balancer needed for distribution

---

**Q12: Explain depends_on and its limitations.**

**A:**

```yaml
services:
  web:
    image: myapp
    depends_on:
      - db

  db:
    image: postgres
```

**What it does:**
- Controls startup order
- `db` starts before `web`

**What it DOESN'T do:**
- Wait for `db` to be ready
- Check if `db` is healthy

**Solution - Use healthchecks:**
```yaml
services:
  db:
    image: postgres
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 5s

  web:
    depends_on:
      db:
        condition: service_healthy
```

---

**Q13: How do you use multiple Compose files?**

**A:**

**Base file (docker-compose.yml):**
```yaml
services:
  app:
    image: myapp
    ports:
      - "3000:3000"
```

**Development override (docker-compose.dev.yml):**
```yaml
services:
  app:
    volumes:
      - .:/app
    command: npm run dev
```

**Production override (docker-compose.prod.yml):**
```yaml
services:
  app:
    restart: always
    command: npm start
```

**Usage:**
```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

---

## Environment and Configuration

**Q14: What are the different ways to pass environment variables?**

**A:**

**1. Dockerfile:**
```dockerfile
ENV NODE_ENV=production
ENV PORT=3000
```

**2. Command line:**
```bash
docker run -e NODE_ENV=production -e PORT=3000 myapp
```

**3. Environment file:**
```bash
docker run --env-file .env myapp
```

**4. Docker Compose:**
```yaml
services:
  app:
    environment:
      - NODE_ENV=production
    env_file:
      - .env
```

**Priority (highest to lowest):**
1. Command line (`-e`)
2. Compose `environment`
3. `env_file`
4. Dockerfile `ENV`

---

**Q15: How do you handle secrets in Docker?**

**A:**

**Development:**
- Environment variables
- `.env` files (not committed)

**Production:**

**1. Docker Secrets (Swarm):**
```bash
echo "password" | docker secret create db_pass -
docker service create --secret db_pass myapp
# Access: /run/secrets/db_pass
```

**2. External Secret Managers:**
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager

**3. Kubernetes Secrets:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
data:
  password: cGFzc3dvcmQ=  # base64
```

**Never:**
- Hardcode in Dockerfile
- Commit to git
- Pass as build args
- Store in images

---

## Registry and Distribution

**Q16: How do you push an image to a private registry?**

**A:**

```bash
# Login to registry
docker login registry.company.com

# Tag image with registry prefix
docker tag myapp:latest registry.company.com/myapp:latest

# Push
docker push registry.company.com/myapp:latest

# Pull
docker pull registry.company.com/myapp:latest
```

**Docker Compose:**
```yaml
services:
  app:
    image: registry.company.com/myapp:latest
```

**CI/CD Example:**
```bash
#!/bin/bash
docker build -t $REGISTRY/myapp:$VERSION .
docker push $REGISTRY/myapp:$VERSION
```

---

**Q17: Explain image tagging best practices.**

**A:**

**Bad:**
```bash
docker tag myapp:latest myapp:latest
```

**Good:**
```bash
# Semantic versioning
docker tag myapp:latest myapp:1.2.3
docker tag myapp:latest myapp:1.2
docker tag myapp:latest myapp:1

# Git commit
docker tag myapp:latest myapp:abc123

# Environment
docker tag myapp:latest myapp:prod-1.2.3

# Timestamp
docker tag myapp:latest myapp:2024-01-15
```

**Never use `latest` in production!**

---

## Logging and Debugging

**Q18: How do you debug a container that exits immediately?**

**A:**

**1. Check logs:**
```bash
docker logs container-id
```

**2. Check exit code:**
```bash
docker inspect --format='{{.State.ExitCode}}' container-id
```

**3. Override entrypoint:**
```bash
docker run -it --entrypoint /bin/sh myapp
```

**4. Check events:**
```bash
docker events --filter container=container-id
```

**5. Run with different command:**
```bash
docker run -it myapp /bin/bash
```

---

**Q19: What logging drivers does Docker support?**

**A:**

**Common drivers:**
- `json-file` (default) - Local JSON files
- `journald` - systemd journal
- `syslog` - Syslog server
- `fluentd` - Fluentd
- `awslogs` - AWS CloudWatch
- `gcplogs` - Google Cloud Logging
- `splunk` - Splunk
- `none` - No logging

**Configure:**
```bash
docker run --log-driver=syslog \
  --log-opt syslog-address=tcp://192.168.1.100:514 \
  myapp
```

**Compose:**
```yaml
services:
  app:
    logging:
      driver: syslog
      options:
        syslog-address: "tcp://192.168.1.100:514"
```

---

**Q20: How do you limit log file size?**

**A:**

```bash
docker run \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  myapp
```

**daemon.json (global):**
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

**Compose:**
```yaml
services:
  app:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

---

## Scenario-Based Questions

**Q21: Your container is using 100% CPU. How do you troubleshoot?**

**A:**

**1. Check stats:**
```bash
docker stats container-id
```

**2. Check processes:**
```bash
docker top container-id
```

**3. Inspect logs:**
```bash
docker logs --tail 100 container-id
```

**4. Enter container:**
```bash
docker exec -it container-id /bin/bash
top
```

**5. Limit resources:**
```bash
docker update --cpus=1 container-id
```

---

**Q22: How do you implement zero-downtime deployment?**

**A:**

**Rolling update strategy:**

```yaml
version: '3.8'
services:
  app:
    image: myapp:v2
    deploy:
      replicas: 5
      update_config:
        parallelism: 1    # Update 1 at a time
        delay: 10s        # Wait between updates
        order: start-first # Start new before stopping old
      rollback_config:
        parallelism: 2
```

**Steps:**
1. Deploy new version alongside old
2. Health check passes
3. Route traffic to new
4. Remove old version

**Requirements:**
- Health checks
- Load balancer
- Graceful shutdown
- Rolling updates

---

**Q23: How do you share data between containers?**

**A:**

**1. Named volume:**
```yaml
services:
  app1:
    volumes:
      - shared-data:/data
  
  app2:
    volumes:
      - shared-data:/data

volumes:
  shared-data:
```

**2. Volumes-from (deprecated):**
```bash
docker run -v /data --name data-container alpine
docker run --volumes-from data-container app1
docker run --volumes-from data-container app2
```

**3. Bind mount:**
```bash
docker run -v $(pwd)/shared:/data app1
docker run -v $(pwd)/shared:/data app2
```

**Best practice:** Use named volumes in production.

---

**Q24: Your application needs to connect to a database. How do you configure it?**

**A:**

```yaml
version: '3.8'

services:
  app:
    image: myapp
    environment:
      DATABASE_URL: postgresql://db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
    networks:
      - backend

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 5s
      retries: 5
    secrets:
      - db_password

volumes:
  postgres-data:

networks:
  backend:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

**Key points:**
- Use DNS (service name)
- Health checks
- Secrets for passwords
- Persistent volumes
- Isolated network

---

**Q25: How do you reduce Docker build time?**

**A:**

**1. Order by change frequency:**
```dockerfile
# Dependencies rarely change
COPY package*.json ./
RUN npm install

# Source changes frequently
COPY . .
```

**2. Use .dockerignore:**
```
node_modules
.git
*.log
```

**3. Leverage BuildKit:**
```bash
DOCKER_BUILDKIT=1 docker build .
```

**4. Use cache mounts:**
```dockerfile
RUN --mount=type=cache,target=/root/.npm \
    npm install
```

**5. Multi-stage builds:**
```dockerfile
FROM node:18 AS deps
COPY package*.json ./
RUN npm install

FROM node:18
COPY --from=deps /node_modules ./node_modules
COPY . .
```

**6. Parallel stages with BuildKit**
**7. Use specific base image tags**
**8. Minimize layers**

---

## Quick Fire Round

**Q26: Command to see container resource usage?**
**A:** `docker stats`

**Q27: How to copy files from container to host?**
**A:** `docker cp container:/path/file.txt ./local/`

**Q28: Remove all stopped containers?**
**A:** `docker container prune`

**Q29: View container processes?**
**A:** `docker top container-id`

**Q30: Inspect network configuration?**
**A:** `docker network inspect network-name`

---

## Total: 30 Intermediate Questions

For more questions, see:
- [Basics Interview Questions](../basics/interview-questions-basics.md)
- [Advanced Interview Questions](../advanced/interview-questions-advanced.md)
