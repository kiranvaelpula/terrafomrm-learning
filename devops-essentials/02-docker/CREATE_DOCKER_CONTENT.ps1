# Create ALL Docker Content - Basics, Intermediate, Advanced, Labs
Write-Host "`n🐳 Creating Docker Content..." -ForegroundColor Cyan

function Create-File {
    param($Path, $Content)
    $dir = Split-Path $Path -Parent
    if ($dir) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $Content | Out-File -FilePath $Path -Encoding utf8
    if (Test-Path $Path) {
        $size = [math]::Round((Get-Item $Path).Length / 1KB, 1)
        Write-Host "✅ $Path (${size}KB)" -ForegroundColor Green
    }
}

$files = @{
    "basics/01-what-is-docker.md" = @"
# What is Docker and Containerization

Understanding Docker and why it revolutionized software deployment.

## Overview

Docker is a platform for developing, shipping, and running applications in containers. Containers package software with everything needed to run, ensuring consistency across environments.

## What is Containerization?

Containerization is packaging an application with its dependencies into a standardized unit.

### Traditional Deployment
``````
Server → OS → Dependencies → App
- Conflicts between apps
- "Works on my machine" problems
- Hard to scale
``````

### Container Deployment
``````
Server → OS → Docker → Container (App + Dependencies)
- Isolated environments
- Consistent across machines
- Easy to scale
``````

## Docker vs Virtual Machines

### Virtual Machines
``````
Hardware
├── Host OS
└── Hypervisor
    ├── Guest OS + App 1
    ├── Guest OS + App 2
    └── Guest OS + App 3
``````

### Containers
``````
Hardware
├── Host OS
└── Docker Engine
    ├── Container 1 (App only)
    ├── Container 2 (App only)
    └── Container 3 (App only)
``````

**Key Differences:**
- **VMs**: Each has full OS (GBs), slower startup
- **Containers**: Share host OS (MBs), instant startup

## Docker Architecture

``````
┌──────────────────────────────────────┐
│        Docker Client (CLI)           │
└──────────────┬───────────────────────┘
               │
               ↓
┌──────────────────────────────────────┐
│        Docker Daemon (Server)        │
│  ┌────────────────────────────────┐  │
│  │        Docker Images           │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │      Running Containers        │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
               │
               ↓
┌──────────────────────────────────────┐
│         Docker Registry              │
│         (Docker Hub)                 │
└──────────────────────────────────────┘
``````

## Key Concepts

### Images
Read-only templates for creating containers.
``````bash
docker pull nginx
docker images
``````

### Containers
Running instances of images.
``````bash
docker run nginx
docker ps
``````

### Dockerfile
Instructions to build an image.
``````dockerfile
FROM node:18
WORKDIR /app
COPY . .
RUN npm install
CMD ["npm", "start"]
``````

### Registry
Storage for Docker images (Docker Hub, private registries).

## Why Use Docker?

**1. Consistency**
``````bash
# Same environment everywhere
Dev → Test → Production
``````

**2. Isolation**
``````bash
# Apps don't interfere with each other
App1 (Node 14) + App2 (Node 18) on same server
``````

**3. Portability**
``````bash
# Run anywhere Docker is installed
Local → Cloud → On-premises
``````

**4. Efficiency**
``````bash
# Lightweight compared to VMs
VM: 2GB, 60s startup
Container: 50MB, instant startup
``````

**5. Scalability**
``````bash
# Easy to scale horizontally
docker-compose up --scale web=5
``````

## Common Use Cases

**Development**
``````bash
# Same environment for all developers
docker-compose up
``````

**Microservices**
``````bash
# Each service in its own container
frontend | backend | database | cache
``````

**CI/CD**
``````bash
# Consistent build and test environments
docker build → docker test → docker deploy
``````

**Legacy Applications**
``````bash
# Run old apps in containers
docker run old-app:python2
``````

## Docker Components

**Docker Engine**: Core runtime
**Docker CLI**: Command-line interface
**Docker Compose**: Multi-container orchestration
**Docker Hub**: Public image registry
**Docker Desktop**: GUI for Windows/Mac

## Quick Example

``````bash
# 1. Pull an image
docker pull nginx

# 2. Run container
docker run -d -p 80:80 nginx

# 3. Check running containers
docker ps

# 4. Stop container
docker stop <container-id>
``````

## Best Practices
1. Use official images when possible
2. Keep containers small
3. One process per container
4. Use .dockerignore
5. Don't store data in containers

**Next:** [Installation →](02-installation-setup.md)
"@

    "basics/02-installation-setup.md" = @"
# Docker Installation and Setup

Complete installation guide for all platforms.

## Windows Installation

### Docker Desktop (Recommended)
``````powershell
# Download from docker.com
# Install Docker Desktop for Windows
# Requires WSL2

# Verify installation
docker --version
docker run hello-world
``````

### System Requirements
- Windows 10/11 Pro, Enterprise, or Education
- WSL2 enabled
- Virtualization enabled in BIOS

### Enable WSL2
``````powershell
wsl --install
wsl --set-default-version 2
``````

## macOS Installation

### Docker Desktop
``````bash
# Download from docker.com
# Install .dmg file

# Verify
docker --version
docker run hello-world
``````

## Linux Installation

### Ubuntu/Debian
``````bash
# Remove old versions
sudo apt remove docker docker-engine docker.io

# Install dependencies
sudo apt update
sudo apt install ca-certificates curl gnupg

# Add Docker's GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \\
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add repository
echo \\
  "deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \\
  https://download.docker.com/linux/ubuntu \\
  \$(lsb_release -cs) stable" | \\
  sudo tee /etc/apt/sources.list.d/docker.list

# Install Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

# Verify
docker --version
sudo docker run hello-world
``````

### Post-Installation (Linux)
``````bash
# Add user to docker group (avoid sudo)
sudo usermod -aG docker \$USER
newgrp docker

# Test without sudo
docker run hello-world
``````

## Verification

``````bash
# Check version
docker --version

# Check info
docker info

# Run hello-world
docker run hello-world

# Check running containers
docker ps

# Check all containers
docker ps -a
``````

## Docker Compose Installation

### Windows/Mac
Included with Docker Desktop

### Linux
``````bash
# Download binary
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)" \\
  -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker-compose --version
``````

## Configuration

### Docker Desktop Settings
- Resources: CPU, Memory, Disk
- Network: DNS, Proxies
- Docker Engine: daemon.json

### daemon.json Example
``````json
{
  "insecure-registries": [],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
``````

## Troubleshooting

**Docker daemon not running**
``````bash
# Windows/Mac: Start Docker Desktop
# Linux:
sudo systemctl start docker
sudo systemctl enable docker
``````

**Permission denied**
``````bash
# Add user to docker group
sudo usermod -aG docker \$USER
``````

**WSL2 issues (Windows)**
``````powershell
wsl --update
wsl --set-default-version 2
``````

**Previous:** [← What is Docker](01-what-is-docker.md) | **Next:** [Images and Containers →](03-images-containers.md)
"@

    "basics/03-images-containers.md" = @"
# Docker Images and Containers

Understanding the relationship between images and containers.

## Docker Images

### What is an Image?
Read-only template for creating containers.

``````bash
# List images
docker images
docker image ls

# Pull image
docker pull nginx
docker pull nginx:1.24

# Remove image
docker rmi nginx
docker image rm nginx
``````

### Image Layers
Images are built in layers (each instruction in Dockerfile).

``````dockerfile
FROM ubuntu:22.04      # Layer 1
RUN apt update         # Layer 2
RUN apt install nginx  # Layer 3
COPY index.html /var/www  # Layer 4
``````

### Image Naming
``````
registry/repository:tag
docker.io/library/nginx:1.24
``````

## Docker Containers

### What is a Container?
Running instance of an image.

``````bash
# Run container
docker run nginx

# Run in background
docker run -d nginx

# Run with name
docker run --name my-nginx nginx

# Run with port mapping
docker run -p 8080:80 nginx
``````

### Container Lifecycle

``````
Created → Running → Stopped → Removed
   ↓         ↓         ↓         ↓
  run      start     stop       rm
``````

### Container Commands

``````bash
# List running containers
docker ps

# List all containers
docker ps -a

# Start container
docker start <container-id>

# Stop container
docker stop <container-id>

# Restart container
docker restart <container-id>

# Remove container
docker rm <container-id>

# Remove all stopped
docker container prune
``````

## Practical Examples

### Run Nginx
``````bash
docker run -d -p 80:80 --name web nginx
# Access: http://localhost
``````

### Run with Environment Variables
``````bash
docker run -e MYSQL_ROOT_PASSWORD=secret mysql
``````

### Run Interactive Container
``````bash
docker run -it ubuntu bash
``````

### Execute Command in Running Container
``````bash
docker exec -it web bash
docker exec web ls /etc
``````

### View Logs
``````bash
docker logs web
docker logs -f web  # Follow
``````

### Copy Files
``````bash
# From container to host
docker cp web:/etc/nginx/nginx.conf ./nginx.conf

# From host to container
docker cp ./index.html web:/usr/share/nginx/html/
``````

## Best Practices
1. Use specific image tags
2. Clean up stopped containers
3. Don't run as root in containers
4. Use volumes for persistent data
5. One process per container

**Previous:** [← Installation](02-installation-setup.md) | **Next:** [Dockerfile Basics →](04-dockerfile-basics.md)
"@

    "basics/04-dockerfile-basics.md" = @"
# Writing Dockerfiles

Learn to create custom Docker images with Dockerfiles.

## Dockerfile Basics

A Dockerfile is a text file with instructions to build an image.

### Basic Structure
``````dockerfile
FROM base-image
WORKDIR /app
COPY . .
RUN build-commands
EXPOSE port
CMD ["start-command"]
``````

## Common Instructions

### FROM
Base image to build upon.
``````dockerfile
FROM node:18
FROM ubuntu:22.04
FROM python:3.11-slim
``````

### WORKDIR
Set working directory.
``````dockerfile
WORKDIR /app
# All subsequent commands run from /app
``````

### COPY
Copy files from host to image.
``````dockerfile
COPY package.json .
COPY . /app
``````

### ADD
Like COPY but supports URLs and auto-extracts archives.
``````dockerfile
ADD https://example.com/file.tar.gz /tmp/
``````

### RUN
Execute commands during build.
``````dockerfile
RUN apt-get update && apt-get install -y nginx
RUN npm install
RUN pip install -r requirements.txt
``````

### CMD
Default command when container starts.
``````dockerfile
CMD ["npm", "start"]
CMD ["python", "app.py"]
CMD ["nginx", "-g", "daemon off;"]
``````

### ENTRYPOINT
Configurable entry point.
``````dockerfile
ENTRYPOINT ["python"]
CMD ["app.py"]
# Can override CMD: docker run image script.py
``````

### EXPOSE
Document which ports the container listens on.
``````dockerfile
EXPOSE 80
EXPOSE 3000
``````

### ENV
Set environment variables.
``````dockerfile
ENV NODE_ENV=production
ENV PORT=3000
``````

### ARG
Build-time variables.
``````dockerfile
ARG VERSION=1.0
RUN echo \$VERSION
``````

## Example Dockerfiles

### Node.js Application
``````dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .

EXPOSE 3000

USER node

CMD ["npm", "start"]
``````

### Python Application
``````dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
``````

### Java Application
``````dockerfile
FROM openjdk:17-slim

WORKDIR /app

COPY target/*.jar app.jar

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]
``````

## Building Images

``````bash
# Build from Dockerfile
docker build -t my-app .

# Build with tag
docker build -t my-app:1.0 .

# Build with build arg
docker build --build-arg VERSION=2.0 -t my-app .

# Build without cache
docker build --no-cache -t my-app .
``````

## .dockerignore

Exclude files from image.

``````
node_modules
npm-debug.log
.git
.env
*.md
.DS_Store
``````

## Best Practices

1. **Use specific base images**
``````dockerfile
# ✅ Good
FROM node:18.16-alpine

# ❌ Bad
FROM node:latest
``````

2. **Minimize layers**
``````dockerfile
# ✅ Good
RUN apt-get update && apt-get install -y \\
    nginx \\
    curl \\
 && rm -rf /var/lib/apt/lists/*

# ❌ Bad
RUN apt-get update
RUN apt-get install -y nginx
RUN apt-get install -y curl
``````

3. **Order instructions by change frequency**
``````dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./  # Changes rarely
RUN npm install
COPY . .               # Changes often
``````

4. **Use non-root user**
``````dockerfile
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
``````

**Previous:** [← Images and Containers](03-images-containers.md) | **Next:** [Basic Commands →](05-basic-commands.md)
"@

    "basics/05-basic-commands.md" = @"
# Essential Docker Commands

Master the Docker commands you'll use daily.

## Image Commands

``````bash
# Pull image
docker pull nginx
docker pull nginx:1.24

# List images
docker images
docker image ls

# Remove image
docker rmi nginx
docker image rm nginx

# Build image
docker build -t my-app .

# Tag image
docker tag my-app:latest my-app:1.0

# Push to registry
docker push my-app:1.0

# Image history
docker history nginx

# Inspect image
docker inspect nginx
``````

## Container Commands

``````bash
# Run container
docker run nginx
docker run -d nginx              # Detached
docker run -p 8080:80 nginx     # Port mapping
docker run --name web nginx      # Named
docker run -it ubuntu bash       # Interactive

# List containers
docker ps                        # Running
docker ps -a                     # All

# Start/Stop
docker start web
docker stop web
docker restart web

# Remove container
docker rm web
docker rm -f web                 # Force remove

# Execute command
docker exec web ls
docker exec -it web bash

# Logs
docker logs web
docker logs -f web               # Follow

# Stats
docker stats
docker stats web
``````

## Volume Commands

``````bash
# Create volume
docker volume create my-data

# List volumes
docker volume ls

# Inspect volume
docker volume inspect my-data

# Remove volume
docker volume rm my-data

# Remove unused
docker volume prune

# Use volume
docker run -v my-data:/data nginx
``````

## Network Commands

``````bash
# List networks
docker network ls

# Create network
docker network create my-net

# Connect container
docker network connect my-net web

# Disconnect
docker network disconnect my-net web

# Inspect network
docker network inspect my-net

# Remove network
docker network rm my-net
``````

## System Commands

``````bash
# System info
docker info
docker version

# Disk usage
docker system df

# Clean up
docker system prune              # Remove unused data
docker system prune -a           # Remove all unused

# Events
docker events

# Top processes
docker top web
``````

## Docker Compose Commands

``````bash
# Start services
docker-compose up
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs
docker-compose logs -f

# List services
docker-compose ps

# Execute command
docker-compose exec web bash

# Build images
docker-compose build

# Scale services
docker-compose up --scale web=3
``````

## Useful Combinations

**Clean everything**
``````bash
docker stop \$(docker ps -aq)
docker rm \$(docker ps -aq)
docker rmi \$(docker images -q)
docker volume prune -f
docker network prune -f
``````

**Enter running container**
``````bash
docker exec -it \$(docker ps -q -f name=web) bash
``````

**Copy from container**
``````bash
docker cp web:/app/logs ./logs
``````

**Previous:** [← Dockerfile Basics](04-dockerfile-basics.md) | **Next:** [Interview Questions →](interview-questions-basics.md)
"@

    "basics/interview-questions-basics.md" = @"
# Docker Interview Questions - Basics

## Q1: What is Docker?
**Answer:** Docker is a containerization platform that packages applications with their dependencies into isolated containers, ensuring consistency across environments.

## Q2: Container vs Virtual Machine?
**Answer:** 
- **Container**: Shares host OS, lightweight (MBs), instant startup
- **VM**: Full OS per instance, heavy (GBs), slow startup

## Q3: What is a Docker image?
**Answer:** Read-only template containing application code, runtime, libraries, and dependencies. Used to create containers.

## Q4: What is a Docker container?
**Answer:** Running instance of a Docker image. Isolated, lightweight, and portable execution environment.

## Q5: Explain Dockerfile
**Answer:** Text file with instructions to build a Docker image. Contains commands like FROM, COPY, RUN, CMD.

## Q6: What is Docker Hub?
**Answer:** Public registry for Docker images. Hosts official and community images.

## Q7: CMD vs ENTRYPOINT?
**Answer:**
- **CMD**: Default command, easily overridden
- **ENTRYPOINT**: Main command, arguments can be appended

## Q8: What is docker-compose?
**Answer:** Tool for defining and running multi-container applications using YAML configuration.

## Q9: How to share data between containers?
**Answer:** Use Docker volumes or bind mounts to share persistent data.

## Q10: Port mapping?
**Answer:** \`-p host:container\` maps container port to host port. Example: \`-p 8080:80\`

**Previous:** [← Basic Commands](05-basic-commands.md) | **Next:** [Multi-stage Builds →](../intermediate/06-multistage-builds.md)
"@
}

foreach ($file in $files.Keys) {
    Create-File -Path $file -Content $files[$file]
}

Write-Host "`n✅ Docker Basics Created!" -ForegroundColor Green
Write-Host "Run CREATE_DOCKER_INTERMEDIATE.ps1 next" -ForegroundColor Cyan
