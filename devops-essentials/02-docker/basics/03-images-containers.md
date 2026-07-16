# Docker Images and Containers

Understanding the relationship between images and containers.

## Docker Images

### What is an Image?
Read-only template for creating containers.

```bash
# List images
docker images
docker image ls

# Pull image
docker pull nginx
docker pull nginx:1.24

# Remove image
docker rmi nginx
docker image rm nginx
```

### Image Layers
Images are built in layers (each instruction in Dockerfile).

```dockerfile
FROM ubuntu:22.04      # Layer 1
RUN apt update         # Layer 2
RUN apt install nginx  # Layer 3
COPY index.html /var/www  # Layer 4
```

### Image Naming
```
registry/repository:tag
docker.io/library/nginx:1.24
```

## Docker Containers

### What is a Container?
Running instance of an image.

```bash
# Run container
docker run nginx

# Run in background
docker run -d nginx

# Run with name
docker run --name my-nginx nginx

# Run with port mapping
docker run -p 8080:80 nginx
```

### Container Lifecycle

```
Created â†’ Running â†’ Stopped â†’ Removed
   â†“         â†“         â†“         â†“
  run      start     stop       rm
```

### Container Commands

```bash
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
```

## Practical Examples

### Run Nginx
```bash
docker run -d -p 80:80 --name web nginx
# Access: http://localhost
```

### Run with Environment Variables
```bash
docker run -e MYSQL_ROOT_PASSWORD=secret mysql
```

### Run Interactive Container
```bash
docker run -it ubuntu bash
```

### Execute Command in Running Container
```bash
docker exec -it web bash
docker exec web ls /etc
```

### View Logs
```bash
docker logs web
docker logs -f web  # Follow
```

### Copy Files
```bash
# From container to host
docker cp web:/etc/nginx/nginx.conf ./nginx.conf

# From host to container
docker cp ./index.html web:/usr/share/nginx/html/
```

## Best Practices
1. Use specific image tags
2. Clean up stopped containers
3. Don't run as root in containers
4. Use volumes for persistent data
5. One process per container

**Previous:** [â† Installation](02-installation-setup.md) | **Next:** [Dockerfile Basics â†’](04-dockerfile-basics.md)
