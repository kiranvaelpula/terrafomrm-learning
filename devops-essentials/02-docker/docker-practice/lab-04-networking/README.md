# Lab 4: Docker Networking

Master container networking and inter-container communication.

## Learning Objectives

- Understand network types
- Create custom networks
- Connect containers
- Implement service discovery
- Troubleshoot network issues

## Prerequisites

- Completed Labs 1-3

## Exercise 1: Network Types

**Create networks:**
```bash
# Bridge network
docker network create my-bridge

# Host network (uses host's network)
docker run --network host nginx

# None (no networking)
docker run --network none alpine
```

**Inspect:**
```bash
docker network ls
docker network inspect my-bridge
```

---

## Exercise 2: Container Communication

**Start containers:**
```bash
# Create network
docker network create app-network

# Start database
docker run -d \
  --name postgres \
  --network app-network \
  -e POSTGRES_PASSWORD=secret \
  postgres:15

# Start app (can reach db by name)
docker run -d \
  --name api \
  --network app-network \
  -e DATABASE_URL=postgresql://postgres:5432/mydb \
  myapi

# Test connectivity
docker exec api ping postgres
docker exec api nslookup postgres
```

---

## Exercise 3: Custom DNS

**docker-compose.yml:**
```yaml
services:
  app:
    image: myapp
    networks:
      - mynetwork
    dns:
      - 8.8.8.8
      - 1.1.1.1
    dns_search:
      - company.internal

networks:
  mynetwork:
```

---

## Exercise 4: Port Publishing

**Different methods:**
```bash
# Specific port
docker run -p 8080:80 nginx

# Random port
docker run -P nginx

# Specific IP
docker run -p 127.0.0.1:8080:80 nginx

# UDP
docker run -p 53:53/udp dnsserver
```

---

## Challenge: Multi-tier Application

**Create:**
- Frontend (port 3000)
- Backend API (port 4000)
- Database (no exposed port)
- Redis cache (no exposed port)
- All in custom networks

<details>
<summary>Solution</summary>

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    networks:
      - frontend-net

  backend:
    build: ./backend
    ports:
      - "4000:4000"
    networks:
      - frontend-net
      - backend-net

  database:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    networks:
      - backend-net

  cache:
    image: redis:alpine
    networks:
      - backend-net

networks:
  frontend-net:
  backend-net:
```
</details>

---

## Lab Complete!

**Next:** [Lab 5 - Production](../lab-05-production/)
