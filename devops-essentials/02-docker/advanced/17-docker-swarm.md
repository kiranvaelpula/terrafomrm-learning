# Docker Swarm

Native Docker orchestration for multi-host container deployments.

## Overview

Docker Swarm is Docker's native clustering and orchestration tool, providing a simple way to manage containers across multiple hosts.

## Swarm Architecture

```
                    Manager Nodes (Raft consensus)
                    ┌────────────────────────┐
                    │   Manager 1 (Leader)   │
                    │   - Scheduling         │
                    │   - API endpoint       │
                    └────────────────────────┘
                            ↕
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                   ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Worker 1    │  │  Worker 2    │  │  Worker 3    │
│  - Task 1    │  │  - Task 2    │  │  - Task 3    │
│  - Task 4    │  │  - Task 5    │  │  - Task 6    │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Initialize Swarm

### Single Node (Development)

```bash
# Initialize Swarm on current node
docker swarm init

# Output:
# Swarm initialized: current node (abc123) is now a manager.
# Token for workers: SWMTKN-1-xxxxx...
```

### Multi-Node (Production)

```bash
# On manager node
docker swarm init --advertise-addr 192.168.1.10

# Get worker join token
docker swarm join-token worker

# Get manager join token
docker swarm join-token manager

# On worker nodes
docker swarm join --token SWMTKN-1-xxxxx... 192.168.1.10:2377

# View nodes
docker node ls
```

## Services

### Create Service

```bash
# Basic service
docker service create --name web nginx

# With replicas
docker service create \
  --name web \
  --replicas 3 \
  nginx

# With port mapping
docker service create \
  --name web \
  --replicas 3 \
  --publish 80:80 \
  nginx

# With resource limits
docker service create \
  --name api \
  --replicas 5 \
  --limit-cpu 0.5 \
  --limit-memory 512M \
  --reserve-cpu 0.25 \
  --reserve-memory 256M \
  --publish 3000:3000 \
  myapi:latest
```

### Manage Services

```bash
# List services
docker service ls

# Inspect service
docker service inspect web

# View service logs
docker service logs web
docker service logs -f web  # Follow

# List tasks (containers)
docker service ps web

# Scale service
docker service scale web=10

# Update service
docker service update --image nginx:alpine web

# Remove service
docker service rm web
```

## Stack Deployment

### docker-compose.yml for Swarm

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      placement:
        constraints:
          - node.role == worker
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    ports:
      - "80:80"
    networks:
      - frontend
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3

  api:
    image: myapi:latest
    deploy:
      replicas: 5
      update_config:
        parallelism: 2
        delay: 10s
      placement:
        constraints:
          - node.labels.type == compute
    environment:
      DATABASE_URL: postgresql://db:5432/mydb
    networks:
      - frontend
      - backend
    secrets:
      - db_password

  db:
    image: postgres:15-alpine
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.type == storage
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - backend
    secrets:
      - db_password

volumes:
  postgres-data:
    driver: local

networks:
  frontend:
    driver: overlay
  backend:
    driver: overlay

secrets:
  db_password:
    external: true
```

### Deploy Stack

```bash
# Create secret
echo "mypassword" | docker secret create db_password -

# Deploy stack
docker stack deploy -c docker-compose.yml myapp

# List stacks
docker stack ls

# List stack services
docker stack services myapp

# List stack tasks
docker stack ps myapp

# Remove stack
docker stack rm myapp
```

## Secrets Management

```bash
# Create secret from stdin
echo "my-secret-value" | docker secret create api_key -

# Create secret from file
docker secret create ssl_cert ./cert.pem

# List secrets
docker secret ls

# Inspect secret (content not shown)
docker secret inspect api_key

# Remove secret
docker secret rm api_key
```

**Use in service:**
```yaml
services:
  app:
    image: myapp
    secrets:
      - api_key
      - ssl_cert

secrets:
  api_key:
    external: true
  ssl_cert:
    file: ./cert.pem
```

**Access in container:**
```bash
# Secrets available at /run/secrets/
cat /run/secrets/api_key
cat /run/secrets/ssl_cert
```

## Networks

```bash
# Create overlay network
docker network create --driver overlay my-network

# Create with encryption
docker network create \
  --driver overlay \
  --opt encrypted \
  secure-network

# Attach service to network
docker service update --network-add my-network web

# Remove network from service
docker service update --network-rm my-network web
```

## Rolling Updates

```bash
# Update image
docker service update --image myapp:v2 api

# Update with configuration
docker service update \
  --image myapp:v2 \
  --update-parallelism 2 \
  --update-delay 10s \
  --update-order start-first \
  api

# Rollback
docker service rollback api

# Update environment variable
docker service update --env-add NEW_VAR=value api

# Update resource limits
docker service update \
  --limit-cpu 1 \
  --limit-memory 1G \
  api
```

## Node Management

```bash
# List nodes
docker node ls

# Inspect node
docker node inspect worker1

# Promote worker to manager
docker node promote worker1

# Demote manager to worker
docker node demote manager2

# Add label to node
docker node update --label-add type=compute worker1
docker node update --label-add type=storage worker2

# Drain node (stop accepting tasks)
docker node update --availability drain worker1

# Activate node
docker node update --availability active worker1

# Remove node
docker node rm worker1
```

## Placement Constraints

```yaml
services:
  db:
    image: postgres
    deploy:
      placement:
        constraints:
          - node.role == manager
          - node.labels.type == storage
        preferences:
          - spread: node.labels.zone

  cache:
    image: redis
    deploy:
      placement:
        constraints:
          - node.role == worker
          - node.hostname != node1

  web:
    image: nginx
    deploy:
      placement:
        max_replicas_per_node: 2
```

## Health Checks and Monitoring

```yaml
services:
  app:
    image: myapp
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      replicas: 3
```

```bash
# Monitor service health
docker service ps app

# View logs
docker service logs -f app

# Check task distribution
docker service ps --format "{{.Node}}: {{.CurrentState}}" app
```

## Load Balancing

Swarm provides automatic load balancing:

```bash
# Create service with published port
docker service create \
  --name web \
  --replicas 3 \
  --publish 80:80 \
  nginx
```

**Traffic flow:**
```
Client → Port 80 (any node)
    ↓
Ingress Network (load balancer)
    ├─→ Container 1 (Node 1)
    ├─→ Container 2 (Node 2)
    └─→ Container 3 (Node 3)
```

## Production Example

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    command:
      - "--providers.docker.swarmMode=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    deploy:
      placement:
        constraints:
          - node.role == manager
    networks:
      - proxy

  app:
    image: myapp:latest
    deploy:
      replicas: 5
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      rollback_config:
        parallelism: 1
      resources:
        limits:
          cpus: '1'
          memory: 1G
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.app.rule=Host(`app.example.com`)"
        - "traefik.http.services.app.loadbalancer.server.port=3000"
    networks:
      - proxy
      - backend
    secrets:
      - api_key

  db:
    image: postgres:15-alpine
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.type == storage
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - backend
    secrets:
      - db_password

volumes:
  postgres-data:
    driver: local

networks:
  proxy:
    driver: overlay
  backend:
    driver: overlay
    internal: true

secrets:
  api_key:
    external: true
  db_password:
    external: true
```

## Best Practices

1. **Use at least 3 managers for HA**
2. **Separate manager and worker nodes in production**
3. **Use secrets for sensitive data**
4. **Implement health checks**
5. **Use overlay networks for service communication**
6. **Label nodes for placement control**
7. **Configure update strategies**
8. **Monitor service health**
9. **Use stack files for deployment**
10. **Regular backups of Swarm state**

## Troubleshooting

```bash
# Check Swarm status
docker info | grep Swarm

# View manager status
docker node ls

# Check service logs
docker service logs --tail 100 myservice

# Inspect failed tasks
docker service ps --no-trunc myservice

# Force service update
docker service update --force myservice

# Check network connectivity
docker run --rm --network my-network alpine ping service-name
```

## Interview Questions

**Q: What's the difference between Docker Swarm and Kubernetes?**
A: Swarm is simpler, easier to learn, and tightly integrated with Docker. Kubernetes is more feature-rich, has a larger ecosystem, but has a steeper learning curve.

**Q: How does Docker Swarm handle service discovery?**
A: Swarm provides built-in DNS-based service discovery. Services can reach each other using service names.

**Q: How do you achieve high availability in Swarm?**
A: Use multiple manager nodes (odd number, minimum 3), distribute workers across availability zones, and implement health checks with restart policies.

**Next:** [Performance Tuning →](18-performance.md)
