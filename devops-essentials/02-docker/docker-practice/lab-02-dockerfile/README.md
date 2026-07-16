# Lab 2: Dockerfile Basics

Learn to build custom Docker images using Dockerfiles.

## Learning Objectives

- Write Dockerfiles
- Build custom images
- Understand image layers
- Use build cache effectively
- Tag and version images

## Prerequisites

- Completed Lab 1
- Text editor
- Basic understanding of containers

## Exercise 1: Simple Dockerfile

**Objective:** Create your first Dockerfile

```dockerfile
# Dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y curl

CMD ["curl", "--version"]
```

**Build and run:**
```bash
docker build -t my-curl .
docker run my-curl
```

**Task:** Create a Dockerfile that installs `wget` instead

---

## Exercise 2: Node.js Application

**Objective:** Build a real application image

**app.js:**
```javascript
const http = require('http');
const server = http.createServer((req, res) => {
  res.writeHead(200);
  res.end('Hello from Docker!\n');
});
server.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

**Dockerfile:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY app.js .

EXPOSE 3000

CMD ["node", "app.js"]
```

**Build and run:**
```bash
docker build -t my-node-app .
docker run -p 3000:3000 my-node-app
curl http://localhost:3000
```

---

## Exercise 3: Multi-stage Build

**Objective:** Optimize image size

**Dockerfile:**
```dockerfile
# Build stage
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/server.js"]
```

**Compare sizes:**
```bash
docker build -t myapp:single-stage -f Dockerfile.single .
docker build -t myapp:multi-stage -f Dockerfile.multi .
docker images | grep myapp
```

---

## Exercise 4: Using .dockerignore

**Create .dockerignore:**
```
node_modules
.git
*.md
.env
.vscode
coverage
```

**Build and compare:**
```bash
# Without .dockerignore
docker build -t app:without .

# With .dockerignore
docker build -t app:with .
```

---

## Exercise 5: Environment Variables

**Dockerfile:**
```dockerfile
FROM node:18-alpine

ENV NODE_ENV=production
ENV PORT=3000

WORKDIR /app
COPY . .

EXPOSE $PORT

CMD ["node", "server.js"]
```

**Build with args:**
```bash
docker build --build-arg NODE_ENV=development -t myapp .
```

---

## Challenge: Python Flask App

**Create complete Dockerfile for:**
```python
# app.py
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Flask in Docker!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Requirements:**
- Use Python 3.11
- Install Flask
- Run as non-root user
- Expose port 5000
- Optimize for size

<details>
<summary>Solution</summary>

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask

COPY app.py .

RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
```
</details>

---

## Lab Complete!

**Next:** [Lab 3 - Docker Compose](../lab-03-compose/)
