# Docker Logging and Debugging

Debug containers and manage logs effectively.

## Container Logs

### Viewing Logs

```bash
# View container logs
docker logs mycontainer

# Follow logs in real-time
docker logs -f mycontainer

# Show timestamps
docker logs -t mycontainer

# Show last N lines
docker logs --tail 100 mycontainer

# Show logs since timestamp
docker logs --since 2024-01-01 mycontainer
docker logs --since 30m mycontainer

# Combine options
docker logs -f --tail 50 --since 10m mycontainer
```

### Docker Compose Logs

```bash
# View all services
docker-compose logs

# Specific service
docker-compose logs api

# Follow logs
docker-compose logs -f

# Tail logs
docker-compose logs -f --tail=100

# Multiple services
docker-compose logs web api db
```

## Debugging Containers

### Interactive Shell

```bash
# Access running container
docker exec -it mycontainer /bin/bash
docker exec -it mycontainer /bin/sh  # Alpine

# As specific user
docker exec -it -u root mycontainer /bin/bash

# Run command without shell
docker exec mycontainer ls -la /app

# Run multiple commands
docker exec mycontainer sh -c "cd /app && npm test"
```

### Inspect Container

```bash
# Full container details
docker inspect mycontainer

# Specific field
docker inspect --format='{{.State.Status}}' mycontainer
docker inspect --format='{{.NetworkSettings.IPAddress}}' mycontainer

# Multiple containers
docker inspect container1 container2

# JSON output with jq
docker inspect mycontainer | jq '.[0].State'
```

### Container Stats

```bash
# Real-time stats
docker stats

# Specific container
docker stats mycontainer

# No streaming (single snapshot)
docker stats --no-stream

# Format output
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Process Information

```bash
# List processes in container
docker top mycontainer

# With specific format
docker top mycontainer aux

# Show all processes
docker exec mycontainer ps aux
```

## Common Debugging Scenarios

### Container Won't Start

```bash
# Check last logs
docker logs mycontainer

# Inspect exit code
docker inspect --format='{{.State.ExitCode}}' mycontainer

# Check events
docker events --filter container=mycontainer

# Try running with different entrypoint
docker run -it --entrypoint /bin/bash myimage
```

### Application Not Responding

```bash
# Check if container is running
docker ps -a | grep mycontainer

# Check resource usage
docker stats mycontainer

# Check processes
docker top mycontainer

# Test network connectivity
docker exec mycontainer ping google.com
docker exec mycontainer curl http://localhost:3000/health

# Check port binding
docker port mycontainer
```

### Network Issues

```bash
# Inspect network configuration
docker inspect mycontainer | grep -A 20 NetworkSettings

# Test connectivity between containers
docker exec container1 ping container2

# Check DNS resolution
docker exec mycontainer nslookup database
docker exec mycontainer cat /etc/resolv.conf

# Verify port exposure
docker ps --format "{{.Names}}\t{{.Ports}}" | grep mycontainer
```

### Volume/Mount Issues

```bash
# Check mounts
docker inspect --format='{{json .Mounts}}' mycontainer | jq

# Verify volume exists
docker volume ls | grep my-volume

# Check permissions
docker exec mycontainer ls -la /data

# Test write access
docker exec mycontainer touch /data/test.txt
```

## Logging Drivers

### Configure Logging Driver

```bash
# JSON file (default)
docker run --log-driver json-file myapp

# Syslog
docker run --log-driver syslog \
  --log-opt syslog-address=tcp://192.168.1.100:514 \
  myapp

# Journald
docker run --log-driver journald myapp

# Fluentd
docker run --log-driver fluentd \
  --log-opt fluentd-address=localhost:24224 \
  myapp

# None (disable logging)
docker run --log-driver none myapp
```

### Log Options

```bash
# Limit log size
docker run \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  myapp

# Add labels
docker run \
  --log-opt labels=app,environment \
  -l app=myapp \
  -l environment=production \
  myapp
```

### Docker Compose Logging

```yaml
version: '3.8'

services:
  app:
    image: myapp
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
        labels: "app,environment"

  logs:
    image: myapp
    logging:
      driver: syslog
      options:
        syslog-address: "tcp://192.168.1.100:514"
```

## Advanced Debugging

### Debug with Different Base Image

```dockerfile
# Original
FROM node:18-alpine
COPY . .
CMD ["node", "server.js"]

# Debug version
FROM node:18  # Full image with more tools
COPY . .
RUN apt-get update && apt-get install -y curl vim net-tools
CMD ["node", "server.js"]
```

### Debugging Multi-stage Build

```bash
# Build up to specific stage
docker build --target builder -t myapp:debug .

# Run debug stage
docker run -it myapp:debug /bin/bash

# Inspect build cache
docker build --no-cache --progress=plain .
```

### Using Debug Tools

```bash
# Install debugging tools in running container
docker exec -it mycontainer /bin/bash

# In Alpine
apk add --no-cache curl vim htop

# In Debian/Ubuntu
apt-get update && apt-get install -y curl vim htop net-tools

# Check network connections
netstat -tulpn

# Monitor resources
htop

# Check disk usage
df -h
```

## Log Aggregation

### ELK Stack

```yaml
version: '3.8'

services:
  app:
    image: myapp
    logging:
      driver: fluentd
      options:
        fluentd-address: localhost:24224
        tag: myapp

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node

  logstash:
    image: logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
```

### Fluentd Configuration

```yaml
services:
  fluentd:
    image: fluent/fluentd:v1.16
    ports:
      - "24224:24224"
    volumes:
      - ./fluent.conf:/fluentd/etc/fluent.conf
      - fluentd-logs:/fluentd/log
```

## Health Checks for Debugging

```dockerfile
FROM node:18
WORKDIR /app
COPY . .

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

CMD ["node", "server.js"]
```

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' mycontainer

# View health check logs
docker inspect --format='{{json .State.Health}}' mycontainer | jq
```

## Debugging Scripts

### Container Debugging Script

```bash
#!/bin/bash
# debug-container.sh

CONTAINER=$1

echo "=== Container Status ==="
docker ps -a | grep $CONTAINER

echo -e "\n=== Recent Logs ==="
docker logs --tail 50 $CONTAINER

echo -e "\n=== Resource Usage ==="
docker stats --no-stream $CONTAINER

echo -e "\n=== Processes ==="
docker top $CONTAINER

echo -e "\n=== Network ==="
docker inspect --format='{{.NetworkSettings.IPAddress}}' $CONTAINER

echo -e "\n=== Mounts ==="
docker inspect --format='{{json .Mounts}}' $CONTAINER | jq

echo -e "\n=== Health Status ==="
docker inspect --format='{{.State.Health.Status}}' $CONTAINER
```

Usage:
```bash
chmod +x debug-container.sh
./debug-container.sh mycontainer
```

## Best Practices

1. **Use structured logging**
```javascript
// JSON logging
console.log(JSON.stringify({
  level: 'info',
  message: 'User logged in',
  userId: 123,
  timestamp: new Date().toISOString()
}));
```

2. **Configure log rotation**
```bash
docker run \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  myapp
```

3. **Use health checks**
4. **Implement proper error handling**
5. **Use debugging tools containers**
```bash
# Debugging sidecar
docker run -d --network container:myapp nicolaka/netshoot
```

6. **Preserve logs on container restart**
7. **Use centralized logging in production**

## Troubleshooting Checklist

```bash
# 1. Is container running?
docker ps -a | grep mycontainer

# 2. Check logs
docker logs --tail 100 mycontainer

# 3. Check resources
docker stats --no-stream mycontainer

# 4. Inspect configuration
docker inspect mycontainer

# 5. Check processes
docker top mycontainer

# 6. Test network
docker exec mycontainer ping google.com

# 7. Verify volumes
docker inspect --format='{{json .Mounts}}' mycontainer | jq

# 8. Check events
docker events --filter container=mycontainer --since 1h
```

## Interview Questions

**Q: How do you view logs of a stopped container?**
A: Use `docker logs <container-id>`. Logs persist until the container is removed with `docker rm`.

**Q: What's the difference between CMD and ENTRYPOINT for debugging?**
A: ENTRYPOINT is harder to override, use `--entrypoint` flag. CMD can be easily replaced by providing command after image name.

**Q: How do you limit log file size?**
A: Use `--log-opt max-size=10m --log-opt max-file=3` to limit size and rotation.

**Q: What tools would you use for debugging networking issues?**
A: curl, ping, netstat, nslookup, dig, tcpdump. Or use nicolaka/netshoot container.

**Next:** [Interview Questions →](interview-questions-intermediate.md)
