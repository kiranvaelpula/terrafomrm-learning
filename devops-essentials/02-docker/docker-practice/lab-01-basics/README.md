# Lab 1: Docker Basics

Master fundamental Docker commands and concepts through hands-on exercises.

## Learning Objectives

By the end of this lab, you will be able to:
- Run Docker containers
- Manage container lifecycle
- Work with Docker images
- Understand container basics
- Use basic Docker commands

## Prerequisites

- Docker installed and running
- Command line access
- Basic terminal knowledge

## Lab Exercises

### Exercise 1: Run Your First Container

**Objective:** Learn basic container execution

```bash
# Run a simple container
docker run hello-world

# What happened?
# 1. Docker checked for 'hello-world' image locally
# 2. Downloaded it from Docker Hub
# 3. Created a container
# 4. Ran the container
# 5. Container exited after printing message
```

**Questions:**
1. Where did the image come from?
2. Is the container still running?
3. How do you see stopped containers?

**Answers:**
```bash
# Check images
docker images

# See all containers (including stopped)
docker ps -a

# See only running containers
docker ps
```

---

### Exercise 2: Interactive Containers

**Objective:** Work with interactive containers

```bash
# Run Ubuntu interactively
docker run -it ubuntu bash

# Inside the container, try:
ls /
whoami
cat /etc/os-release
apt-get update
apt-get install -y curl
curl https://example.com
exit

# Container stops when you exit
```

**Task:** Run an Alpine container and install `vim`

<details>
<summary>Solution</summary>

```bash
docker run -it alpine sh
apk update
apk add vim
vim test.txt
# Type something, save and exit
cat test.txt
exit
```
</details>

---

### Exercise 3: Detached Containers

**Objective:** Run containers in the background

```bash
# Run nginx in detached mode
docker run -d --name my-nginx nginx

# Check it's running
docker ps

# Check logs
docker logs my-nginx

# Follow logs in real-time
docker logs -f my-nginx
# Press Ctrl+C to exit

# Stop the container
docker stop my-nginx

# Start it again
docker start my-nginx

# Restart
docker restart my-nginx
```

**Task:** Run a Redis container in detached mode with name "my-redis"

<details>
<summary>Solution</summary>

```bash
docker run -d --name my-redis redis
docker ps
docker logs my-redis
```
</details>

---

### Exercise 4: Port Mapping

**Objective:** Expose container ports to host

```bash
# Run nginx with port mapping
docker run -d -p 8080:80 --name web nginx

# Test it
curl http://localhost:8080
# Or open browser: http://localhost:8080

# Check port mapping
docker port web

# Run another nginx on different port
docker run -d -p 8081:80 --name web2 nginx
curl http://localhost:8081
```

**Task:** Run an Apache httpd container on port 9000

<details>
<summary>Solution</summary>

```bash
docker run -d -p 9000:80 --name apache httpd
curl http://localhost:9000
```
</details>

---

### Exercise 5: Executing Commands in Running Containers

**Objective:** Run commands inside running containers

```bash
# Start a container
docker run -d --name test-container nginx

# Execute command in running container
docker exec test-container ls /usr/share/nginx/html

# Interactive shell
docker exec -it test-container bash

# Inside container:
cd /usr/share/nginx/html
echo "<h1>Hello from Docker!</h1>" > index.html
exit

# Test the change
curl http://localhost  # if port mapped
```

**Task:** Create a file in the nginx container at `/tmp/test.txt` with your name

<details>
<summary>Solution</summary>

```bash
docker exec test-container sh -c "echo 'Your Name' > /tmp/test.txt"
docker exec test-container cat /tmp/test.txt
```
</details>

---

### Exercise 6: Copying Files

**Objective:** Copy files between host and container

```bash
# Create a local file
echo "<h1>My Custom Page</h1>" > index.html

# Copy to running container
docker cp index.html test-container:/usr/share/nginx/html/

# Verify
docker exec test-container cat /usr/share/nginx/html/index.html

# Copy from container to host
docker cp test-container:/etc/nginx/nginx.conf ./nginx-backup.conf
cat nginx-backup.conf
```

**Task:** Create a file `test.txt` locally and copy it to `/tmp/` in the container

<details>
<summary>Solution</summary>

```bash
echo "Test content" > test.txt
docker cp test.txt test-container:/tmp/
docker exec test-container cat /tmp/test.txt
```
</details>

---

### Exercise 7: Environment Variables

**Objective:** Pass configuration via environment variables

```bash
# Run MySQL with environment variables
docker run -d \
  --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=secret123 \
  -e MYSQL_DATABASE=testdb \
  mysql:8

# Check environment variables
docker exec mysql-db env

# Connect to MySQL
docker exec -it mysql-db mysql -p
# Password: secret123
SHOW DATABASES;
exit
```

**Task:** Run PostgreSQL with custom user and password

<details>
<summary>Solution</summary>

```bash
docker run -d \
  --name postgres-db \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=mypass \
  -e POSTGRES_DB=mydb \
  postgres:15
  
docker exec -it postgres-db psql -U myuser -d mydb
```
</details>

---

### Exercise 8: Container Resource Inspection

**Objective:** View container details and resource usage

```bash
# Start a container
docker run -d --name resource-test nginx

# Inspect container
docker inspect resource-test

# View specific info
docker inspect --format='{{.State.Status}}' resource-test
docker inspect --format='{{.NetworkSettings.IPAddress}}' resource-test

# View resource usage
docker stats resource-test

# View all containers' stats
docker stats

# Stop stats with Ctrl+C
```

**Task:** Find the IP address and exposed ports of your container

<details>
<summary>Solution</summary>

```bash
docker inspect --format='{{.NetworkSettings.IPAddress}}' resource-test
docker inspect --format='{{.Config.ExposedPorts}}' resource-test
# or
docker port resource-test
```
</details>

---

### Exercise 9: Container Cleanup

**Objective:** Remove containers and images

```bash
# List all containers
docker ps -a

# Stop a container
docker stop test-container

# Remove a container
docker rm test-container

# Remove running container (force)
docker rm -f my-nginx

# Remove all stopped containers
docker container prune

# List images
docker images

# Remove an image
docker rmi hello-world

# Remove unused images
docker image prune -a
```

**Task:** Clean up all containers and images from previous exercises

<details>
<summary>Solution</summary>

```bash
# Stop all containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all images
docker rmi $(docker images -q)
```
</details>

---

### Exercise 10: Container Logs and Events

**Objective:** Monitor container activity

```bash
# Run container
docker run -d --name log-test nginx

# View logs
docker logs log-test

# View last 10 lines
docker logs --tail 10 log-test

# View with timestamps
docker logs -t log-test

# Follow logs
docker logs -f log-test &
# Generate some logs
curl http://localhost
# Check logs again

# View container events
docker events --filter container=log-test &
docker restart log-test
# See events
```

---

## Challenge: Web Server with Custom Content

**Objective:** Combine everything you've learned

**Task:** Create a nginx container that:
1. Runs on port 8888
2. Has a custom HTML page
3. Has a custom nginx configuration
4. Is named "my-web-server"

<details>
<summary>Solution</summary>

```bash
# Create custom HTML
echo "<h1>My Web Server</h1><p>Running in Docker!</p>" > index.html

# Create nginx config
cat > nginx.conf <<EOF
events {
    worker_connections 1024;
}
http {
    server {
        listen 80;
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
    }
}
EOF

# Run container
docker run -d \
  --name my-web-server \
  -p 8888:80 \
  nginx

# Copy files
docker cp index.html my-web-server:/usr/share/nginx/html/
docker cp nginx.conf my-web-server:/etc/nginx/nginx.conf

# Reload nginx
docker exec my-web-server nginx -s reload

# Test
curl http://localhost:8888
```
</details>

---

## Lab Summary

**Commands Learned:**
```bash
# Container lifecycle
docker run
docker start/stop/restart
docker rm
docker ps

# Interaction
docker exec
docker logs
docker cp

# Inspection
docker inspect
docker stats
docker port

# Cleanup
docker container prune
docker image prune
```

**Key Concepts:**
- ✅ Containers are isolated processes
- ✅ Images are templates for containers
- ✅ Port mapping exposes services
- ✅ Environment variables configure containers
- ✅ Containers can be interactive or detached
- ✅ Multiple containers can run simultaneously

---

## Verification Checklist

- [ ] Run hello-world successfully
- [ ] Start interactive container
- [ ] Run container in detached mode
- [ ] Map ports and access via browser
- [ ] Execute commands in running container
- [ ] Copy files to/from container
- [ ] Use environment variables
- [ ] Inspect container details
- [ ] View and follow logs
- [ ] Clean up containers and images

---

## Next Steps

✅ Lab 1 Complete!

Continue to:
- **Lab 2:** [Dockerfile Basics](../lab-02-dockerfile/)
- Learn how to build custom images
- Create reproducible containers
- Understand image layers

---

## Troubleshooting

**Container exits immediately?**
```bash
docker logs <container-name>
docker inspect --format='{{.State.ExitCode}}' <container-name>
```

**Port already in use?**
```bash
# Use different port
docker run -p 8081:80 nginx
```

**Permission denied?**
```bash
# Run as root (if needed)
docker exec -u root <container> <command>
```

**Can't connect to Docker?**
```bash
# Check Docker is running
docker version
```

---

## Additional Resources

- [Docker Run Reference](https://docs.docker.com/engine/reference/run/)
- [Docker CLI](https://docs.docker.com/engine/reference/commandline/cli/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)
