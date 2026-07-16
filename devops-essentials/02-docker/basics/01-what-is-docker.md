# What is Docker and Containerization

Understanding Docker and why it revolutionized software deployment.

## Overview

Docker is a platform for developing, shipping, and running applications in containers. Containers package software with everything needed to run, ensuring consistency across environments.

## What is Containerization?

Containerization is packaging an application with its dependencies into a standardized unit.

### Traditional Deployment
```
Server → OS → Dependencies → App
- Conflicts between apps
- "Works on my machine" problems
- Hard to scale
```

### Container Deployment
```
Server → OS → Docker → Container (App + Dependencies)
- Isolated environments
- Consistent across machines
- Easy to scale
```

## Docker vs Virtual Machines

### Virtual Machines
```
Hardware
├── Host OS
└── Hypervisor
    ├── Guest OS + App 1
    ├── Guest OS + App 2
    └── Guest OS + App 3
```

### Containers
```
Hardware
├── Host OS
└── Docker Engine
    ├── Container 1 (App only)
    ├── Container 2 (App only)
    └── Container 3 (App only)
```

**Key Differences:**
- **VMs**: Each has full OS (GBs), slower startup
- **Containers**: Share host OS (MBs), instant startup

## Docker Architecture

Docker follows a client-server architecture with three main components working together:

### Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DOCKER HOST                               │
│                                                                   │
│  ┌────────────────────┐           ┌─────────────────────────┐  │
│  │  Docker Client     │           │    Docker Daemon        │  │
│  │  (docker CLI)      │◄─────────►│    (dockerd)            │  │
│  │                    │   REST    │                         │  │
│  │  Commands:         │    API    │  ┌───────────────────┐ │  │
│  │  - docker run      │           │  │ Image Management  │ │  │
│  │  - docker build    │           │  │ - pull/push       │ │  │
│  │  - docker pull     │           │  │ - build/tag       │ │  │
│  │  - docker ps       │           │  │ - image storage   │ │  │
│  └────────────────────┘           │  └───────────────────┘ │  │
│                                    │                         │  │
│                                    │  ┌───────────────────┐ │  │
│                                    │  │Container Runtime  │ │  │
│                                    │  │ - containerd      │ │  │
│                                    │  │ - runc            │ │  │
│                                    │  │ - lifecycle mgmt  │ │  │
│                                    │  └───────────────────┘ │  │
│                                    │                         │  │
│                                    │  ┌───────────────────┐ │  │
│                                    │  │Network Management │ │  │
│                                    │  │ - bridge/host     │ │  │
│                                    │  │ - overlay/macvlan │ │  │
│                                    │  │ - DNS/routing     │ │  │
│                                    │  └───────────────────┘ │  │
│                                    │                         │  │
│                                    │  ┌───────────────────┐ │  │
│                                    │  │Volume Management  │ │  │
│                                    │  │ - bind mounts     │ │  │
│                                    │  │ - named volumes   │ │  │
│                                    │  │ - tmpfs           │ │  │
│                                    │  └───────────────────┘ │  │
│                                    └─────────────────────────┘  │
│                                              │                   │
│                                              ↓                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Local Image Cache                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │  │
│  │  │ nginx:   │  │ node:18  │  │ python:  │  ...          │  │
│  │  │ latest   │  │          │  │ 3.11     │               │  │
│  │  └──────────┘  └──────────┘  └──────────┘               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                              │                   │
│                                              ↓                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Running Containers                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │ Container 1  │  │ Container 2  │  │ Container 3  │   │  │
│  │  │ nginx:latest │  │ node:18 app  │  │ python app   │   │  │
│  │  │ Port: 80     │  │ Port: 3000   │  │ Port: 8000   │   │  │
│  │  │ Volume: data │  │ Network: web │  │ Volume: logs │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             ↕
                    (Internet Connection)
                             ↕
┌─────────────────────────────────────────────────────────────────┐
│                      Docker Registry                             │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Docker Hub (hub.docker.com)             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │ Public Repos │  │ Official     │  │ Private Repos│    │ │
│  │  │ - nginx      │  │ Images       │  │ - myapp      │    │ │
│  │  │ - postgres   │  │ - node       │  │ - company/db │    │ │
│  │  │ - redis      │  │ - python     │  │ - team/api   │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            Private/Enterprise Registries                   │ │
│  │  - Amazon ECR  - Azure ACR  - Google GCR                   │ │
│  │  - Harbor  - GitLab Registry  - JFrog Artifactory          │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Components Explained

#### 1. Docker Client
- **What**: Command-line interface (CLI) that users interact with
- **Purpose**: Send commands to Docker Daemon via REST API
- **Common Commands**:
  - `docker run` - Create and start container
  - `docker build` - Build image from Dockerfile
  - `docker pull` - Download image from registry
  - `docker push` - Upload image to registry
  - `docker ps` - List running containers

#### 2. Docker Daemon (dockerd)
- **What**: Background service running on the host
- **Purpose**: Core engine that manages Docker objects
- **Responsibilities**:
  - **Image Management**: Pull, build, store, and manage images
  - **Container Runtime**: Create, start, stop, and monitor containers
  - **Network Management**: Create virtual networks, DNS, routing
  - **Volume Management**: Handle persistent data storage
  - **API Server**: Listen for Docker API requests

#### 3. Container Runtime (containerd & runc)
- **containerd**: Industry-standard container runtime
- **runc**: Low-level tool to spawn and run containers
- **Purpose**: Actually execute containers according to OCI standards

#### 4. Docker Registry
- **What**: Storage and distribution system for Docker images
- **Types**:
  - **Docker Hub**: Default public registry
  - **Private Registries**: ECR, ACR, GCR, Harbor
- **Purpose**: Store, version, and share Docker images

### How Docker Works - Step-by-Step Workflow

```
Step 1: User Issues Command
┌──────────────────────────────┐
│ $ docker run -d -p 80:80     │
│   nginx:latest               │
└──────────────────────────────┘
            ↓

Step 2: Client Processes Command
┌──────────────────────────────┐
│ Docker Client                │
│ - Parse command              │
│ - Send to Daemon via API     │
└──────────────────────────────┘
            ↓

Step 3: Daemon Checks Local Images
┌──────────────────────────────┐
│ Docker Daemon                │
│ - Check: nginx:latest local? │
│ - If NO → Pull from registry │
└──────────────────────────────┘
            ↓

Step 4: Pull from Registry (if needed)
┌──────────────────────────────┐
│ Docker Hub                   │
│ - Download nginx:latest      │
│ - Store in local cache       │
└──────────────────────────────┘
            ↓

Step 5: Create Container
┌──────────────────────────────┐
│ Docker Daemon                │
│ - Create container from image│
│ - Allocate network/storage   │
│ - Configure port mapping     │
└──────────────────────────────┘
            ↓

Step 6: Start Container
┌──────────────────────────────┐
│ Container Runtime            │
│ - containerd spawns process  │
│ - runc executes container    │
│ - Container is now running   │
└──────────────────────────────┘
            ↓

Step 7: Return to User
┌──────────────────────────────┐
│ Container ID: abc123def456   │
│ Status: Running on port 80   │
└──────────────────────────────┘
```

### Real-World Example

Let's trace a complete workflow:

```bash
# 1. Build custom image
$ docker build -t myapp:v1 .
   ↓ Client → Daemon
   ↓ Daemon reads Dockerfile
   ↓ Daemon builds layers
   ↓ Image stored locally

# 2. Run container
$ docker run -d -p 3000:3000 myapp:v1
   ↓ Client → Daemon
   ↓ Daemon finds image locally
   ↓ Daemon creates container
   ↓ Container starts on port 3000

# 3. Push to registry
$ docker push myuser/myapp:v1
   ↓ Client → Daemon
   ↓ Daemon authenticates with registry
   ↓ Daemon uploads image layers
   ↓ Image available on Docker Hub

# 4. Pull on another machine
$ docker pull myuser/myapp:v1
   ↓ Client → Daemon
   ↓ Daemon downloads from registry
   ↓ Image stored locally
   ↓ Ready to run
```

### Key Architecture Principles

1. **Decoupled Components**: Client and daemon can run on different machines
2. **REST API**: All communication via standardized API
3. **Layered Images**: Images built from reusable layers
4. **Isolation**: Containers isolated via Linux namespaces and cgroups
5. **Distribution**: Registry enables sharing across teams/machines

## Key Concepts

### Images
Read-only templates for creating containers.
```bash
docker pull nginx
docker images
```

### Containers
Running instances of images.
```bash
docker run nginx
docker ps
```

### Dockerfile
Instructions to build an image.
```dockerfile
FROM node:18
WORKDIR /app
COPY . .
RUN npm install
CMD ["npm", "start"]
```

### Registry
Storage for Docker images (Docker Hub, private registries).

## Why Use Docker?

**1. Consistency**
```bash
# Same environment everywhere
Dev → Test → Production
```

**2. Isolation**
```bash
# Apps don't interfere with each other
App1 (Node 14) + App2 (Node 18) on same server
```

**3. Portability**
```bash
# Run anywhere Docker is installed
Local → Cloud → On-premises
```

**4. Efficiency**
```bash
# Lightweight compared to VMs
VM: 2GB, 60s startup
Container: 50MB, instant startup
```

**5. Scalability**
```bash
# Easy to scale horizontally
docker-compose up --scale web=5
```

## Common Use Cases

**Development**
```bash
# Same environment for all developers
docker-compose up
```

**Microservices**
```bash
# Each service in its own container
frontend | backend | database | cache
```

**CI/CD**
```bash
# Consistent build and test environments
docker build → docker test → docker deploy
```

**Legacy Applications**
```bash
# Run old apps in containers
docker run old-app:python2
```

## Docker Components

**Docker Engine**: Core runtime
**Docker CLI**: Command-line interface
**Docker Compose**: Multi-container orchestration
**Docker Hub**: Public image registry
**Docker Desktop**: GUI for Windows/Mac

## Quick Example

```bash
# 1. Pull an image
docker pull nginx

# 2. Run container
docker run -d -p 80:80 nginx

# 3. Check running containers
docker ps

# 4. Stop container
docker stop <container-id>
```

## Best Practices
1. Use official images when possible
2. Keep containers small
3. One process per container
4. Use .dockerignore
5. Don't store data in containers

**Next:** [Installation →](02-installation-setup.md)
