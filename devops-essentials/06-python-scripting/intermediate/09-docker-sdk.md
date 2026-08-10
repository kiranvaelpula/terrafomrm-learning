# Docker SDK for Python

> **Manage Docker containers, images, and networks programmatically. Build custom orchestration, cleanup tools, and deployment automation.**

---

## 📖 Setup

```bash
pip install docker
```

```python
import docker

# Connect to local Docker daemon (via /var/run/docker.sock)
client = docker.from_env()

# Verify connection
print(client.version()['Version'])   # e.g., "24.0.5"
```

---

## 🐳 Container Operations

```python
# List running containers
for container in client.containers.list():
    print(f"  {container.name}: {container.status} ({container.image.tags})")

# List ALL containers (including stopped)
all_containers = client.containers.list(all=True)

# Run a container (like docker run)
container = client.containers.run(
    "nginx:latest",
    name="web-server",
    ports={'80/tcp': 8080},      # Map container 80 → host 8080
    detach=True,                 # Run in background
    environment={"ENV": "prod"}, # Environment variables
    volumes={'/host/data': {'bind': '/data', 'mode': 'rw'}},
    restart_policy={"Name": "unless-stopped"}
)
print(f"Started: {container.name} ({container.short_id})")

# Container management
container.stop(timeout=10)       # Graceful stop
container.start()                # Start stopped container
container.restart()              # Restart
container.remove(force=True)     # Remove (force if running)

# Execute command inside running container
result = container.exec_run("nginx -t")
print(f"Exit code: {result.exit_code}")
print(f"Output: {result.output.decode()}")

# View logs
logs = container.logs(tail=50, timestamps=True).decode()
print(logs)

# Stream logs (follow)
for log in container.logs(stream=True, follow=True):
    print(log.decode().strip())
```

---

## 🖼️ Image Operations

```python
# Pull image
image = client.images.pull("python", tag="3.11-slim")
print(f"Pulled: {image.tags}")

# Build image from Dockerfile
image, build_logs = client.images.build(
    path=".",                    # Build context
    tag="myapp:latest",
    rm=True,                    # Remove intermediate containers
    buildargs={"VERSION": "2.0.1"}
)
for log in build_logs:
    if 'stream' in log:
        print(log['stream'].strip())

# List images
for img in client.images.list():
    if img.tags:
        print(f"  {img.tags[0]}: {img.short_id}")

# Remove image
client.images.remove("old-image:v1")

# Prune unused images
pruned = client.images.prune()
print(f"Freed: {pruned['SpaceReclaimed'] / (1024**2):.0f} MB")
```

---

## 🛠️ Practical: Docker Cleanup Script

```python
#!/usr/bin/env python3
"""Clean up Docker: remove stopped containers, dangling images, unused volumes."""

import docker
from datetime import datetime, timezone, timedelta

client = docker.from_env()

def cleanup_containers(max_age_hours=24):
    """Remove stopped containers older than max_age_hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    removed = 0
    
    for container in client.containers.list(all=True, filters={"status": "exited"}):
        # Parse finished time
        finished = container.attrs['State']['FinishedAt']
        if 'T' in finished:
            finish_time = datetime.fromisoformat(finished.replace('Z', '+00:00'))
            if finish_time < cutoff:
                container.remove()
                removed += 1
    
    print(f"  Removed {removed} stopped containers")

def cleanup_images():
    """Remove dangling images (untagged)."""
    pruned = client.images.prune(filters={"dangling": True})
    count = len(pruned.get('ImagesDeleted', []) or [])
    space = pruned.get('SpaceReclaimed', 0) / (1024**2)
    print(f"  Removed {count} dangling images ({space:.0f} MB freed)")

def cleanup_volumes():
    """Remove unused volumes."""
    pruned = client.volumes.prune()
    count = len(pruned.get('VolumesDeleted', []) or [])
    print(f"  Removed {count} unused volumes")

if __name__ == "__main__":
    print("Docker Cleanup")
    print("=" * 30)
    cleanup_containers()
    cleanup_images()
    cleanup_volumes()
    print("\n✓ Cleanup complete")
```

---

## 🎯 Interview Quick Points

- `docker.from_env()` connects to local Docker daemon
- `client.containers.run(detach=True)` = `docker run -d`
- `container.exec_run()` = `docker exec`
- `client.images.build()` = `docker build`
- `client.images.prune()` removes dangling images
- Good for custom orchestration, testing, CI/CD pipelines
- Handle `docker.errors.NotFound`, `docker.errors.APIError`
- Docker SDK talks to the same socket as `docker` CLI
