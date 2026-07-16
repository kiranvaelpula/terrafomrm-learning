# Lab 3: Docker Compose

Master multi-container applications with Docker Compose.

## Learning Objectives

- Write docker-compose.yml files
- Manage multi-container applications
- Use volumes and networks
- Scale services
- Debug Compose applications

## Prerequisites

- Docker Compose installed
- Completed Labs 1 & 2

## Exercise 1: Simple Web + Database

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

**Commands:**
```bash
docker-compose up -d
docker-compose ps
docker-compose logs
docker-compose down
```

---

## Exercise 2: Full-Stack Application

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  frontend:
    image: node:18-alpine
    working_dir: /app
    volumes:
      - ./frontend:/app
    command: npm start
    ports:
      - "3000:3000"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "4000:4000"
    environment:
      DATABASE_URL: postgresql://db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

volumes:
  postgres-data:
```

---

## Exercise 3: Networks and Scaling

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    deploy:
      replicas: 3
    networks:
      - frontend

  api:
    build: ./api
    networks:
      - frontend
      - backend

  db:
    image: postgres:15
    networks:
      - backend

networks:
  frontend:
  backend:
```

**Scale services:**
```bash
docker-compose up -d --scale web=5
docker-compose ps
```

---

## Exercise 4: Health Checks

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  app:
    build: .
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5
```

---

## Challenge: WordPress Stack

**Create:**
- WordPress
- MySQL
- Persistent volumes
- Custom network
- Health checks

<details>
<summary>Solution</summary>

```yaml
version: '3.8'

services:
  wordpress:
    image: wordpress:latest
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: secret
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wordpress-data:/var/www/html
    depends_on:
      db:
        condition: service_healthy
    networks:
      - wordpress-network

  db:
    image: mysql:8
    environment:
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: secret
      MYSQL_ROOT_PASSWORD: rootsecret
    volumes:
      - db-data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - wordpress-network

volumes:
  wordpress-data:
  db-data:

networks:
  wordpress-network:
```
</details>

---

## Lab Complete!

**Next:** [Lab 4 - Networking](../lab-04-networking/)
