# Essential Docker Commands

Master the Docker commands you'll use daily.

## Image Commands

```bash
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
```

## Container Commands

```bash
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
```

## Volume Commands

```bash
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
```

## Network Commands

```bash
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
```

## System Commands

```bash
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
```

## Docker Compose Commands

```bash
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
```

## Useful Combinations

**Clean everything**
```bash
docker stop \
docker rm \
docker rmi \
docker volume prune -f
docker network prune -f
```

**Enter running container**
```bash
docker exec -it \ bash
```

**Copy from container**
```bash
docker cp web:/app/logs ./logs
```

**Previous:** [â† Dockerfile Basics](04-dockerfile-basics.md) | **Next:** [Interview Questions â†’](interview-questions-basics.md)
