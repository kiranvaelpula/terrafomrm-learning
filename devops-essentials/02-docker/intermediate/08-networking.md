# Docker Networking

Container networking modes and inter-container communication.

## Overview

Docker networking enables containers to communicate with each other, the host, and external networks.

## Network Types

### 1. Bridge (Default)

```bash
# Default bridge
docker run -d --name web nginx

# Custom bridge
docker network create my-bridge
docker run -d --name web --network my-bridge nginx
docker run -d --name app --network my-bridge myapp
```

### 2. Host

```bash
docker run -d --network host nginx
```

### 3. None

```bash
docker run -d --network none nginx
```

### 4. Overlay (Swarm)

```bash
docker network create --driver overlay my-overlay
```

## Practical Example

```bash
# Create network
docker network create app-network

# Database
docker run -d \
  --name db \
  --network app-network \
  -e POSTGRES_PASSWORD=secret \
  postgres:15

# Backend (can access db by name)
docker run -d \
  --name backend \
  --network app-network \
  -e DATABASE_URL=postgresql://postgres:secret@db:5432/mydb \
  mybackend:latest

# Frontend
docker run -d \
  --name frontend \
  --network app-network \
  -p 80:80 \
  myfrontend:latest
```

## Docker Compose Networking

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    networks:
      - backend

  api:
    build: ./api
    networks:
      - backend
      - frontend

  web:
    build: ./web
    networks:
      - frontend
    ports:
      - "80:80"

networks:
  backend:
  frontend:
```

## Network Commands

```bash
# Create network
docker network create my-network

# List networks
docker network ls

# Inspect network
docker network inspect my-network

# Connect container
docker network connect my-network mycontainer

# Disconnect
docker network disconnect my-network mycontainer

# Remove network
docker network rm my-network
```

## DNS and Service Discovery

Containers can reach each other by service name:

```bash
# Container 'web' can ping 'db'
docker exec web ping db
```

## Port Mapping

```bash
# Map container port to host
docker run -p 8080:80 nginx     # host:container

# Random host port
docker run -P nginx

# Specific IP
docker run -p 127.0.0.1:8080:80 nginx

# UDP ports
docker run -p 53:53/udp dnsserver
```

## Advanced Options

### Custom Subnet

```bash
docker network create \
  --driver bridge \
  --subnet 172.25.0.0/16 \
  --gateway 172.25.0.1 \
  custom-bridge
```

### Static IP

```bash
docker run -d \
  --name web \
  --network custom-bridge \
  --ip 172.25.0.10 \
  nginx
```

### Network Aliases

```bash
docker run -d \
  --name web \
  --network my-network \
  --network-alias webapp \
  --network-alias www \
  nginx
```

## Best Practices

1. Use custom bridge networks
2. Isolate sensitive services
3. Use network aliases for flexibility
4. Document port mappings
5. Avoid host network in production

## Troubleshooting

```bash
# Test connectivity
docker exec web ping db

# Check network configuration
docker network inspect my-network

# View container's network
docker inspect mycontainer | grep -A 20 NetworkSettings
```

**Next:** [Docker Compose →](09-docker-compose.md)
