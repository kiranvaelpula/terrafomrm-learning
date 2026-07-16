# Docker Installation and Setup

Complete installation guide for all platforms.

## Windows Installation

### Docker Desktop (Recommended)
```powershell
# Download from docker.com
# Install Docker Desktop for Windows
# Requires WSL2

# Verify installation
docker --version
docker run hello-world
```

### System Requirements
- Windows 10/11 Pro, Enterprise, or Education
- WSL2 enabled
- Virtualization enabled in BIOS

### Enable WSL2
```powershell
wsl --install
wsl --set-default-version 2
```

## macOS Installation

### Docker Desktop
```bash
# Download from docker.com
# Install .dmg file

# Verify
docker --version
docker run hello-world
```

## Linux Installation

### Ubuntu/Debian
```bash
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
  "deb [arch=\ signed-by=/etc/apt/keyrings/docker.gpg] \\
  https://download.docker.com/linux/ubuntu \\
  \ stable" | \\
  sudo tee /etc/apt/sources.list.d/docker.list

# Install Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

# Verify
docker --version
sudo docker run hello-world
```

### Post-Installation (Linux)
```bash
# Add user to docker group (avoid sudo)
sudo usermod -aG docker \
newgrp docker

# Test without sudo
docker run hello-world
```

## Verification

```bash
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
```

## Docker Compose Installation

### Windows/Mac
Included with Docker Desktop

### Linux
```bash
# Download binary
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\-\" \\
  -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker-compose --version
```

## Configuration

### Docker Desktop Settings
- Resources: CPU, Memory, Disk
- Network: DNS, Proxies
- Docker Engine: daemon.json

### daemon.json Example
```json
{
  "insecure-registries": [],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

## Troubleshooting

**Docker daemon not running**
```bash
# Windows/Mac: Start Docker Desktop
# Linux:
sudo systemctl start docker
sudo systemctl enable docker
```

**Permission denied**
```bash
# Add user to docker group
sudo usermod -aG docker \
```

**WSL2 issues (Windows)**
```powershell
wsl --update
wsl --set-default-version 2
```

**Previous:** [â† What is Docker](01-what-is-docker.md) | **Next:** [Images and Containers â†’](03-images-containers.md)
