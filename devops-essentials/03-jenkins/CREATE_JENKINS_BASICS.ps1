# PowerShell script to create comprehensive Jenkins basics content

Write-Host "Creating Jenkins Basics Content..." -ForegroundColor Green

# Create 02-installation.md
$installation = @"
# Jenkins Installation and Setup

Complete guide to installing Jenkins on different platforms and initial configuration.

---

## Overview

Jenkins can be installed in multiple ways:
- Docker (Recommended for learning)
- Native installation (Windows, Linux, macOS)
- Cloud platforms (AWS, Azure, GCP)
- Kubernetes

---

## Method 1: Docker Installation (Recommended)

### Why Docker?

**Advantages:**
- Quick setup (< 5 minutes)
- Isolated environment
- Easy cleanup
- Consistent across platforms
- Perfect for learning

### Installation Steps

**1. Install Docker:**
```bash
# Check Docker installation
docker --version

# Pull Jenkins image
docker pull jenkins/jenkins:lts
```

**2. Run Jenkins container:**
```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

**Parameters explained:**
- `-d`: Run in background
- `--name jenkins`: Container name
- `-p 8080:8080`: Web UI port
- `-p 50000:50000`: Agent port
- `-v jenkins_home:/var/jenkins_home`: Persistent data

**3. Get initial password:**
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

**4. Access Jenkins:**
- Open browser: http://localhost:8080
- Enter password from step 3
- Install suggested plugins
- Create first admin user

### Jenkins with Docker Support

To run Docker commands inside Jenkins:

```bash
docker run -d \
  --name jenkins-docker \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -u root \
  jenkins/jenkins:lts

# Install Docker inside Jenkins
docker exec -u root jenkins-docker apt-get update
docker exec -u root jenkins-docker apt-get install -y docker.io
```

---

## Method 2: Native Installation

### Ubuntu/Debian

```bash
# Add Jenkins repository
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

# Install Jenkins
sudo apt-get update
sudo apt-get install -y openjdk-11-jdk
sudo apt-get install -y jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Check status
sudo systemctl status jenkins

# Get initial password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

### CentOS/RHEL

```bash
# Add repository
sudo wget -O /etc/yum.repos.d/jenkins.repo \
    https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key

# Install
sudo yum install -y java-11-openjdk
sudo yum install -y jenkins

# Start
sudo systemctl start jenkins
sudo systemctl enable jenkins
```

### Windows

**1. Download:**
- Download Jenkins MSI from: https://www.jenkins.io/download/
- Run installer

**2. Installation:**
- Accept defaults
- Jenkins installs as Windows service
- Opens browser automatically

**3. Configuration:**
- Service runs on port 8080
- Default location: `C:\Program Files\Jenkins`

### macOS

```bash
# Using Homebrew
brew install jenkins-lts

# Start Jenkins
brew services start jenkins-lts

# Or run directly
jenkins-lts
```

---

## Method 3: Cloud Installation

### AWS EC2

```bash
#!/bin/bash
# Launch t2.medium Ubuntu instance
# Open ports 8080, 50000

# Install Java
sudo apt-get update
sudo apt-get install -y openjdk-11-jdk

# Install Jenkins
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install -y jenkins

# Start Jenkins
sudo systemctl start jenkins

# Get password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

**Security Group:**
- Port 8080: Jenkins UI
- Port 50000: Agent communication
- Port 22: SSH access

### Azure VM

```bash
# Create VM with Ubuntu
az vm create \
  --resource-group jenkins-rg \
  --name jenkins-vm \
  --image UbuntuLTS \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys

# Open ports
az vm open-port --port 8080 --resource-group jenkins-rg --name jenkins-vm
az vm open-port --port 50000 --resource-group jenkins-rg --name jenkins-vm

# SSH and install Jenkins
ssh azureuser@<public-ip>
# Follow Ubuntu installation steps
```

### GCP Compute Engine

```bash
# Create instance
gcloud compute instances create jenkins-server \
  --machine-type=n1-standard-1 \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB \
  --tags=jenkins

# Create firewall rules
gcloud compute firewall-rules create jenkins-ui \
  --allow tcp:8080 \
  --target-tags jenkins

gcloud compute firewall-rules create jenkins-agent \
  --allow tcp:50000 \
  --target-tags jenkins

# SSH and install
gcloud compute ssh jenkins-server
# Follow Ubuntu installation steps
```

---

## Method 4: Kubernetes Installation

### Using Helm

```bash
# Add Jenkins Helm repository
helm repo add jenkins https://charts.jenkins.io
helm repo update

# Install Jenkins
helm install jenkins jenkins/jenkins \
  --set controller.serviceType=LoadBalancer \
  --set persistence.size=10Gi

# Get admin password
kubectl exec --namespace default -it svc/jenkins -c jenkins -- /bin/cat /run/secrets/additional/chart-admin-password

# Get external IP
kubectl get svc jenkins
```

### Using YAML

```yaml
# jenkins-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jenkins
  template:
    metadata:
      labels:
        app: jenkins
    spec:
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts
        ports:
        - containerPort: 8080
        - containerPort: 50000
        volumeMounts:
        - name: jenkins-home
          mountPath: /var/jenkins_home
      volumes:
      - name: jenkins-home
        persistentVolumeClaim:
          claimName: jenkins-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: jenkins
spec:
  type: LoadBalancer
  ports:
  - port: 8080
    targetPort: 8080
    name: ui
  - port: 50000
    targetPort: 50000
    name: agent
  selector:
    app: jenkins
```

---

## Initial Configuration

### 1. Unlock Jenkins

Access http://localhost:8080 and enter initial admin password.

### 2. Install Plugins

**Suggested Plugins (automatically selected):**
- Git plugin
- GitHub plugin
- Pipeline plugin
- Credentials plugin
- SSH Agents plugin
- Email Extension plugin

**Additional Recommended:**
- Docker plugin
- Kubernetes plugin
- Blue Ocean
- Configuration as Code

### 3. Create Admin User

Fill in:
- Username
- Password
- Full name
- Email address

### 4. Jenkins URL Configuration

Set Jenkins URL (e.g., http://localhost:8080 or public domain)

---

## Essential Configuration

### System Configuration

**Navigate to:** Manage Jenkins → Configure System

**1. # of executors:**
```
Recommended: Number of CPU cores
```

**2. Labels:**
```
master, docker, linux
```

**3. Usage:**
- Use this node as much as possible (default)
- Only build jobs with label expressions matching this node

### Global Tool Configuration

**Navigate to:** Manage Jenkins → Global Tool Configuration

**1. JDK Installation:**
```
Name: JDK-11
JAVA_HOME: /usr/lib/jvm/java-11-openjdk-amd64
```

**2. Git:**
```
Name: Default
Path to Git executable: git
```

**3. Maven:**
```
Name: Maven-3.9
Install automatically: Yes
Version: 3.9.0
```

**4. Docker:**
```
Name: Docker
Docker URL: unix:///var/run/docker.sock
```

### Security Configuration

**Navigate to:** Manage Jenkins → Configure Global Security

**1. Security Realm:**
```
Jenkins' own user database
Allow users to sign up: Unchecked
```

**2. Authorization:**
```
Matrix-based security or Project-based Matrix Authorization
```

**3. CSRF Protection:**
```
Enable: Yes (default)
```

---

## Verification

### Check Installation

```bash
# Check Jenkins status (Linux)
sudo systemctl status jenkins

# Check Java version
java -version

# Check Jenkins version
# Navigate to: Manage Jenkins → System Information
```

### Test First Job

```bash
# Create test job
1. New Item → Freestyle project → "test-job"
2. Build → Execute shell
3. Command: echo "Hello Jenkins"
4. Save → Build Now
5. Check Console Output
```

---

## Directory Structure

### Linux

```
/var/lib/jenkins/              # Jenkins home
├── jobs/                      # Job configurations
├── workspace/                 # Job workspaces
├── plugins/                   # Installed plugins
├── users/                     # User configurations
└── secrets/                   # Secrets and keys
```

### Docker

```
/var/jenkins_home/             # Jenkins home (inside container)
Host volume: jenkins_home      # Persistent storage
```

### Windows

```
C:\Program Files\Jenkins\      # Installation
C:\Users\<user>\.jenkins\     # Jenkins home
```

---

## Common Post-Installation Tasks

### 1. Configure Email Notifications

```
Manage Jenkins → Configure System → Extended E-mail Notification

SMTP Server: smtp.gmail.com
SMTP Port: 587
Credentials: Add Gmail app password
Use SSL: Yes
```

### 2. Set up Backup

```bash
# Backup Jenkins home
tar -czf jenkins-backup.tar.gz /var/lib/jenkins/

# Automate with cron
0 2 * * * tar -czf /backup/jenkins-$(date +\%Y\%m\%d).tar.gz /var/lib/jenkins/
```

### 3. Install Additional Plugins

```
Manage Jenkins → Manage Plugins → Available

Search and install:
- Docker Pipeline
- Kubernetes
- Blue Ocean
- Role-based Authorization Strategy
- Configuration as Code
```

---

## Troubleshooting

### Port 8080 Already in Use

```bash
# Linux: Change port
sudo nano /etc/default/jenkins
# Change: HTTP_PORT=8080 to HTTP_PORT=8081

# Docker: Use different port
docker run -p 8081:8080 jenkins/jenkins:lts
```

### Cannot Connect to Jenkins

```bash
# Check firewall
sudo ufw allow 8080/tcp

# Check Jenkins is running
sudo systemctl status jenkins

# Check logs
sudo journalctl -u jenkins -f
```

### Permission Denied Errors

```bash
# Fix permissions
sudo chown -R jenkins:jenkins /var/lib/jenkins

# Docker: Run as root
docker run -u root jenkins/jenkins:lts
```

---

## Best Practices

1. **Use Docker for learning**: Easy setup and cleanup
2. **Regular backups**: Automate Jenkins home backup
3. **Use HTTPS**: Set up reverse proxy with SSL
4. **Update regularly**: Keep Jenkins and plugins updated
5. **Limit executors**: Don't run too many jobs simultaneously
6. **Use agents**: Don't run builds on master
7. **Monitor resources**: Jenkins can consume significant resources

---

## Production Setup Checklist

- [ ] Install on dedicated server/VM
- [ ] Set up HTTPS with valid certificate
- [ ] Configure authentication (LDAP, SAML, OAuth)
- [ ] Enable security and CSRF protection
- [ ] Set up automated backups
- [ ] Configure monitoring and logging
- [ ] Set up master-agent architecture
- [ ] Implement Role-Based Access Control
- [ ] Document configuration
- [ ] Test disaster recovery

---

## Next Steps

Continue to:
- **[Creating Your First Job](03-first-job.md)** →
- Learn to create and configure Jenkins jobs
- Understand different job types

---

**Estimated Setup Time:**
- Docker: 5-10 minutes
- Native: 15-20 minutes
- Cloud: 20-30 minutes
- Kubernetes: 30-45 minutes
"@

Set-Content -Path "devops-essentials/03-jenkins/basics/02-installation.md" -Value $installation -Encoding UTF8
Write-Host "Created: 02-installation.md" -ForegroundColor Cyan

Write-Host "`nJenkins basics content created successfully!" -ForegroundColor Green
