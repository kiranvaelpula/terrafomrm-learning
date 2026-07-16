# Container Orchestration Introduction

Understanding container orchestration and when you need it.

## Overview

Container orchestration automates deployment, scaling, networking, and management of containerized applications across multiple hosts.

## Why Orchestration?

**Without Orchestration:**
- Manual container management on each host
- No automatic scaling
- Manual load balancing
- No self-healing
- Complex networking across hosts
- Manual failover

**With Orchestration:**
- Automated deployment and scaling
- Self-healing (restart failed containers)
- Load balancing built-in
- Service discovery
- Rolling updates and rollbacks
- Resource optimization

## Orchestration Platforms

### 1. Kubernetes (K8s)
- **Best for:** Large-scale, complex applications
- **Pros:** Feature-rich, huge ecosystem, industry standard
- **Cons:** Steep learning curve, complex setup
- **Use when:** Need advanced features, multi-cloud, large teams

### 2. Docker Swarm
- **Best for:** Simple to medium applications
- **Pros:** Easy to learn, native Docker, simple setup
- **Cons:** Limited features compared to K8s
- **Use when:** Want simplicity, already using Docker

### 3. Amazon ECS
- **Best for:** AWS-native applications
- **Pros:** Deep AWS integration, managed service
- **Cons:** Vendor lock-in, AWS only
- **Use when:** All-in on AWS

### 4. Nomad
- **Best for:** Mixed workloads (containers + VMs)
- **Pros:** Simple, flexible, lightweight
- **Cons:** Smaller ecosystem
- **Use when:** Need flexibility beyond containers

## Core Concepts

### 1. Nodes/Hosts
Physical or virtual machines running containers

```
Cluster
├── Manager Node (orchestrator)
├── Worker Node 1 (runs containers)
├── Worker Node 2 (runs containers)
└── Worker Node 3 (runs containers)
```

### 2. Services
Desired state for application containers

```yaml
Service: web-app
  - Replicas: 3
  - Image: myapp:v1
  - Port: 80
  - Resources: 1 CPU, 512MB RAM
```

### 3. Tasks/Pods
Individual container instances

```
Service: web-app (3 replicas)
├── Task 1 (Node 1)
├── Task 2 (Node 2)
└── Task 3 (Node 3)
```

### 4. Load Balancing
Automatic traffic distribution

```
User Request
    ↓
Load Balancer
    ├─→ Container 1 (Node 1)
    ├─→ Container 2 (Node 2)
    └─→ Container 3 (Node 3)
```

### 5. Service Discovery
Containers find each other by name

```
web-app → http://api-service:3000
api-service → http://database:5432
```

### 6. Scaling
Automatic or manual replica adjustment

```bash
# Manual scaling
scale web-app --replicas=10

# Auto-scaling based on CPU
scale web-app --min=3 --max=20 --cpu-percent=75
```

## When You Need Orchestration

### You DON'T need orchestration if:
- Running on single host
- Small number of containers (< 5)
- No high availability requirements
- Development/testing environment
- Simple applications

**Solution:** Use docker-compose

### You NEED orchestration if:
- Multiple hosts/servers
- High availability required
- Need auto-scaling
- Complex microservices
- Production environment
- Need load balancing
- Want self-healing

**Solution:** Use Kubernetes, Swarm, or ECS

## Simple vs Orchestrated Deployment

### Docker Compose (Single Host)

```yaml
version: '3.8'
services:
  web:
    image: nginx
    replicas: 3  # Limited to single host
    ports:
      - "80:80"
```

### Docker Swarm (Multi-Host)

```yaml
version: '3.8'
services:
  web:
    image: nginx
    deploy:
      replicas: 10  # Distributed across nodes
      placement:
        constraints:
          - node.role == worker
    ports:
      - "80:80"
```

## Orchestration Features Comparison

| Feature | Docker Compose | Docker Swarm | Kubernetes | ECS |
|---------|---------------|--------------|------------|-----|
| Multi-host | ❌ | ✅ | ✅ | ✅ |
| Auto-scaling | ❌ | ⚠️ Limited | ✅ | ✅ |
| Load balancing | ❌ | ✅ | ✅ | ✅ |
| Self-healing | ❌ | ✅ | ✅ | ✅ |
| Rolling updates | ⚠️ Limited | ✅ | ✅ | ✅ |
| Learning curve | Easy | Easy | Hard | Medium |
| Setup complexity | Very Low | Low | High | Medium |
| Best for | Development | Simple prod | Enterprise | AWS users |

## Migration Path

### Stage 1: Docker Compose
```bash
# Development
docker-compose up -d
```

### Stage 2: Docker Swarm
```bash
# Initialize Swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml myapp
```

### Stage 3: Kubernetes
```bash
# Convert to K8s
kompose convert -f docker-compose.yml

# Deploy to K8s
kubectl apply -f deployment.yaml
```

## Common Orchestration Tasks

### Deployment
```bash
# Swarm
docker stack deploy -c docker-compose.yml myapp

# Kubernetes
kubectl apply -f deployment.yaml

# ECS
aws ecs create-service --cluster mycluster ...
```

### Scaling
```bash
# Swarm
docker service scale myapp_web=10

# Kubernetes
kubectl scale deployment web --replicas=10

# ECS
aws ecs update-service --desired-count 10
```

### Updates
```bash
# Swarm
docker service update --image myapp:v2 myapp_web

# Kubernetes
kubectl set image deployment/web web=myapp:v2

# ECS
aws ecs update-service --force-new-deployment
```

### Monitoring
```bash
# Swarm
docker service ps myapp_web

# Kubernetes
kubectl get pods -w

# ECS
aws ecs describe-services
```

## Decision Tree

```
Do you need multiple hosts?
├─ No → Use Docker Compose
└─ Yes → Continue

Do you have complex requirements?
├─ No → Use Docker Swarm
└─ Yes → Continue

Are you on AWS?
├─ Yes → Consider ECS
└─ No → Use Kubernetes

Do you need maximum features?
├─ Yes → Use Kubernetes
└─ No → Use Docker Swarm (simpler)
```

## Getting Started

### Start Small
1. Master Docker and docker-compose
2. Try Docker Swarm for multi-host
3. Learn Kubernetes when needed

### Learn Progressively
- Week 1-2: Docker basics
- Week 3-4: Docker Compose
- Week 5-6: Docker Swarm OR Kubernetes basics
- Week 7+: Advanced orchestration features

## Best Practices

1. **Start simple, add complexity as needed**
2. **Use orchestration for production, not development**
3. **Learn one tool well before switching**
4. **Consider team expertise**
5. **Evaluate based on actual needs**

## Interview Questions

**Q: When should you use container orchestration?**
A: When you need to run containers across multiple hosts, require high availability, auto-scaling, load balancing, or self-healing capabilities.

**Q: What's the difference between Docker Compose and Docker Swarm?**
A: Docker Compose runs on a single host for development/testing. Docker Swarm orchestrates containers across multiple hosts for production.

**Q: Which orchestration tool should I choose?**
A: Start with Docker Swarm for simplicity. Choose Kubernetes for complex, large-scale applications. Use ECS if you're all-in on AWS.

**Next:** [Docker Swarm →](17-docker-swarm.md)
