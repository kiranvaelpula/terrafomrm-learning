# Writing Dockerfiles

Learn to create custom Docker images with Dockerfiles.

## Dockerfile Basics

A Dockerfile is a text file with instructions to build an image.

### Basic Structure
```dockerfile
FROM base-image
WORKDIR /app
COPY . .
RUN build-commands
EXPOSE port
CMD ["start-command"]
```

## Common Instructions

### FROM
Base image to build upon.
```dockerfile
FROM node:18
FROM ubuntu:22.04
FROM python:3.11-slim
```

### WORKDIR
Set working directory.
```dockerfile
WORKDIR /app
# All subsequent commands run from /app
```

### COPY
Copy files from host to image.
```dockerfile
COPY package.json .
COPY . /app
```

### ADD
Like COPY but supports URLs and auto-extracts archives.
```dockerfile
ADD https://example.com/file.tar.gz /tmp/
```

### RUN
Execute commands during build.
```dockerfile
RUN apt-get update && apt-get install -y nginx
RUN npm install
RUN pip install -r requirements.txt
```

### CMD
Default command when container starts.
```dockerfile
CMD ["npm", "start"]
CMD ["python", "app.py"]
CMD ["nginx", "-g", "daemon off;"]
```

### ENTRYPOINT
Configurable entry point.
```dockerfile
ENTRYPOINT ["python"]
CMD ["app.py"]
# Can override CMD: docker run image script.py
```

### EXPOSE
Document which ports the container listens on.
```dockerfile
EXPOSE 80
EXPOSE 3000
```

### ENV
Set environment variables.
```dockerfile
ENV NODE_ENV=production
ENV PORT=3000
```

### ARG
Build-time variables.
```dockerfile
ARG VERSION=1.0
RUN echo \
```

## Example Dockerfiles

### Node.js Application
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .

EXPOSE 3000

USER node

CMD ["npm", "start"]
```

### Python Application
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
```

### Java Application
```dockerfile
FROM openjdk:17-slim

WORKDIR /app

COPY target/*.jar app.jar

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]
```

## Building Images

```bash
# Build from Dockerfile
docker build -t my-app .

# Build with tag
docker build -t my-app:1.0 .

# Build with build arg
docker build --build-arg VERSION=2.0 -t my-app .

# Build without cache
docker build --no-cache -t my-app .
```

## .dockerignore

Exclude files from image.

```
node_modules
npm-debug.log
.git
.env
*.md
.DS_Store
```

## Best Practices

1. **Use specific base images**
```dockerfile
# âœ… Good
FROM node:18.16-alpine

# âŒ Bad
FROM node:latest
```

2. **Minimize layers**
```dockerfile
# âœ… Good
RUN apt-get update && apt-get install -y \\
    nginx \\
    curl \\
 && rm -rf /var/lib/apt/lists/*

# âŒ Bad
RUN apt-get update
RUN apt-get install -y nginx
RUN apt-get install -y curl
```

3. **Order instructions by change frequency**
```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./  # Changes rarely
RUN npm install
COPY . .               # Changes often
```

4. **Use non-root user**
```dockerfile
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
```

**Previous:** [â† Images and Containers](03-images-containers.md) | **Next:** [Basic Commands â†’](05-basic-commands.md)
