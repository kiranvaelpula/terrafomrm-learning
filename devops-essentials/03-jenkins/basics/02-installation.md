# Jenkins Installation and Setup

## Installation Methods

There are several ways to install Jenkins. Choose based on your environment and requirements.

## Method 1: Docker (Recommended for Learning)

### Why Docker?
- Quick setup (5 minutes)
- No system dependencies
- Easy cleanup
- Portable across OS
- Perfect for development/testing

### Prerequisites
```bash
# Check Docker is installed
docker --version

# Check Docker Compose is installed
docker-compose --version
```

### Basic Docker Installation

```bash
# Pull official Jenkins image
docker pull jenkins/jenkins:lts

# Run Jenkins
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

### Docker with Docker Support (Docker-in-Docker)

```bash
# Run Jenkins with Docker socket mounted
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts

# Install Docker CLI in Jenkins container
docker exec -it --user root jenkins bash
apt-get update
apt-get install -y docker.io
exit
```

### Docker Compose Setup

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  jenkins:
    image: jenkins/jenkins:lts
    container_name: jenkins
    privileged: true
    user: root
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker
    environment:
      - JAVA_OPTS=-Djenkins.install.runSetupWizard=false
    restart: unless-stopped

volumes:
  jenkins_home:
```

Start Jenkins:
```bash
docker-compose up -d
```

## Method 2: Native Installation

### Ubuntu/Debian

```bash
# Add Jenkins repository
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

# Install Java (required)
sudo apt-get update
sudo apt-get install -y fontconfig openjdk-17-jre

# Install Jenkins
sudo apt-get install -y jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Check status
sudo systemctl status jenkins
```

### CentOS/RHEL/Fedora

```bash
# Add Jenkins repository
sudo wget -O /etc/yum.repos.d/jenkins.repo \
    https://pkg.jenkins.io/redhat-stable/jenkins.repo

sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key

# Install Java
sudo yum install -y java-17-openjdk

# Install Jenkins
sudo yum install -y jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Check status
sudo systemctl status jenkins
```

### macOS (Homebrew)

```bash
# Install Java
brew install openjdk@17

# Add Java to PATH
echo 'export PATH="/usr/local/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Install Jenkins
brew install jenkins-lts

# Start Jenkins
brew services start jenkins-lts

# Check if running
brew services list
```

### Windows

1. **Download Jenkins**
   - Visit: https://www.jenkins.io/download/
   - Download Windows installer (.msi)

2. **Install Java** (if not installed)
   - Download JDK 17 from Oracle or Adoptium
   - Install and set JAVA_HOME

3. **Run Installer**
   - Double-click .msi file
   - Follow installation wizard
   - Choose installation directory
   - Select port (default: 8080)
   - Install as Windows service

4. **Start Jenkins**
   ```cmd
   # Start service
   net start jenkins

   # Check status
   sc query jenkins
   ```

## Method 3: Kubernetes

### Using Helm

```bash
# Add Jenkins Helm repository
helm repo add jenkins https://charts.jenkins.io
helm repo update

# Create namespace
kubectl create namespace jenkins

# Install Jenkins
helm install jenkins jenkins/jenkins \
  --namespace jenkins \
  --set controller.serviceType=LoadBalancer \
  --set persistence.enabled=true \
  --set persistence.size=20Gi

# Get admin password
kubectl exec --namespace jenkins -it svc/jenkins -c jenkins -- \
  /bin/cat /run/secrets/additional/chart-admin-password

# Get Jenkins URL
kubectl get svc --namespace jenkins
```

### Manual Kubernetes Deployment

Create `jenkins-deployment.yaml`:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: jenkins
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: jenkins-pvc
  namespace: jenkins
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
  namespace: jenkins
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
  namespace: jenkins
spec:
  type: LoadBalancer
  ports:
  - port: 8080
    targetPort: 8080
    name: http
  - port: 50000
    targetPort: 50000
    name: jnlp
  selector:
    app: jenkins
```

Deploy:
```bash
kubectl apply -f jenkins-deployment.yaml
```

## Initial Setup Wizard

### Step 1: Unlock Jenkins

1. **Access Jenkins**
   - Open browser: `http://localhost:8080`

2. **Get Initial Password**

   **Docker:**
   ```bash
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```

   **Native Linux:**
   ```bash
   sudo cat /var/lib/jenkins/secrets/initialAdminPassword
   ```

   **Native macOS:**
   ```bash
   cat ~/.jenkins/secrets/initialAdminPassword
   ```

   **Native Windows:**
   ```cmd
   type C:\ProgramData\Jenkins\.jenkins\secrets\initialAdminPassword
   ```

3. **Enter Password**
   - Copy password
   - Paste in browser
   - Click Continue

### Step 2: Customize Jenkins

Choose one option:

#### Option A: Install Suggested Plugins (Recommended)
- Click "Install suggested plugins"
- Wait for installation (5-10 minutes)
- Includes common plugins

#### Option B: Select Plugins to Install
- Choose specific plugins
- Good for minimal installation
- Can add more later

**Essential Suggested Plugins:**
- Git
- GitHub
- Pipeline
- Docker
- Credentials
- SSH Agents
- Email Extension
- Build Timeout

### Step 3: Create Admin User

Fill in details:
- Username: `admin` (or your choice)
- Password: Strong password
- Full name: Your name
- Email: Your email

Or click "Skip and continue as admin" (not recommended)

### Step 4: Instance Configuration

- Jenkins URL: `http://your-server:8080`
- Click "Save and Finish"
- Click "Start using Jenkins"

## Post-Installation Configuration

### 1. Configure System Settings

**Navigate to:** Manage Jenkins → Configure System

#### Set Number of Executors
```
# of executors: 2 (adjust based on server)
```

#### Configure Email Notifications
```
SMTP server: smtp.gmail.com
SMTP port: 587
Use SMTP Authentication: ✓
Username: your-email@gmail.com
Password: app-specific password
Use SSL: ✓
```

#### Set Environment Variables
```
Name: JAVA_HOME
Value: /usr/lib/jvm/java-17-openjdk-amd64
```

### 2. Security Configuration

**Navigate to:** Manage Jenkins → Configure Global Security

#### Enable Security
```
✓ Enable security
```

#### Security Realm
```
Jenkins' own user database
✓ Allow users to sign up (disable after creating users)
```

#### Authorization
```
Matrix-based security
Or
Role-Based Strategy (requires plugin)
```

#### Agent Protocols
```
✓ TCP port for inbound agents: 50000
```

### 3. Plugin Configuration

**Navigate to:** Manage Jenkins → Manage Plugins

#### Essential Plugins to Install

```bash
# Version Control
- Git
- GitHub
- GitLab
- Bitbucket

# Build Tools
- Maven Integration
- Gradle
- NodeJS
- Python

# Containers
- Docker
- Docker Pipeline
- Kubernetes
- Kubernetes CLI

# Pipeline
- Pipeline
- Pipeline: Stage View
- Blue Ocean

# Testing
- JUnit
- Performance
- Test Results Analyzer

# Notifications
- Email Extension
- Slack Notification
- Microsoft Teams

# Code Quality
- SonarQube Scanner
- Warnings Next Generation
- Code Coverage API

# Credentials
- Credentials Binding
- SSH Agent
- AWS Credentials

# Utilities
- Workspace Cleanup
- Timestamper
- Build Timeout
- AnsiColor
```

Install plugins:
```
1. Go to "Available" tab
2. Search for plugin
3. Check checkbox
4. Click "Install without restart"
5. Or "Download now and install after restart"
```

### 4. Configure Tools

**Navigate to:** Manage Jenkins → Global Tool Configuration

#### JDK Configuration
```
Name: JDK17
JAVA_HOME: /usr/lib/jvm/java-17-openjdk-amd64
Or ✓ Install automatically
```

#### Git Configuration
```
Name: Default
Path to Git executable: git
Or ✓ Install automatically
```

#### Maven Configuration
```
Name: Maven3
MAVEN_HOME: /usr/share/maven
Or ✓ Install automatically
```

#### Docker Configuration
```
Name: docker
Installation root: /usr/bin/docker
```

### 5. Configure Credentials

**Navigate to:** Manage Jenkins → Manage Credentials → Global → Add Credentials

#### Username with Password
```
Kind: Username with password
Scope: Global
Username: your-username
Password: your-password
ID: github-credentials
Description: GitHub credentials
```

#### SSH Private Key
```
Kind: SSH Username with private key
Scope: Global
ID: ssh-key
Username: git
Private Key: Enter directly (paste key)
```

#### Secret Text
```
Kind: Secret text
Scope: Global
Secret: your-secret-token
ID: api-token
Description: API Token
```

## Testing Installation

### Create Test Job

1. **New Item** → `test-job` → Freestyle project

2. **Build Steps** → Execute shell:
   ```bash
   echo "Jenkins is working!"
   echo "Java version:"
   java -version
   echo "Git version:"
   git --version
   echo "Docker version:"
   docker --version
   ```

3. **Save** and **Build Now**

4. Check **Console Output** for success

## Backup Configuration

### Manual Backup (Docker)
```bash
# Stop Jenkins
docker stop jenkins

# Backup jenkins_home
docker run --rm \
  -v jenkins_home:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/jenkins-backup-$(date +%Y%m%d).tar.gz /data

# Start Jenkins
docker start jenkins
```

### Manual Backup (Native)
```bash
# Stop Jenkins
sudo systemctl stop jenkins

# Backup JENKINS_HOME
sudo tar czf jenkins-backup-$(date +%Y%m%d).tar.gz \
  /var/lib/jenkins/

# Start Jenkins
sudo systemctl start jenkins
```

### Automated Backup Script

Create `backup-jenkins.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/backups/jenkins"
JENKINS_HOME="/var/lib/jenkins"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="jenkins-backup-${DATE}.tar.gz"

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Create backup
tar czf ${BACKUP_DIR}/${BACKUP_FILE} \
  --exclude='workspace/*' \
  --exclude='caches/*' \
  --exclude='*.log' \
  ${JENKINS_HOME}

# Keep only last 7 backups
find ${BACKUP_DIR} -name "jenkins-backup-*.tar.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}"
```

Schedule with cron:
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup-jenkins.sh
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8080
lsof -i :8080
# Or
netstat -tulpn | grep 8080

# Kill process
kill -9 <PID>

# Or change Jenkins port
# Edit /etc/default/jenkins
HTTP_PORT=8081
```

### Permission Issues (Docker)
```bash
# Fix volume permissions
docker exec --user root jenkins chown -R jenkins:jenkins /var/jenkins_home
```

### Out of Memory
```bash
# Increase Java heap size
# Edit /etc/default/jenkins (Linux)
JAVA_OPTS="-Xmx2048m -Xms1024m"

# Or Docker
docker run -d \
  -e JAVA_OPTS="-Xmx2048m" \
  jenkins/jenkins:lts
```

### Cannot Connect to Docker
```bash
# Add Jenkins user to docker group
sudo usermod -aG docker jenkins

# Restart Jenkins
sudo systemctl restart jenkins
```

## Next Steps

Now that Jenkins is installed:

1. **Create Your First Job** → `03-first-job.md`
2. **Explore the UI** → `04-ui-navigation.md`
3. **Set Up Build Triggers** → `05-build-triggers.md`

## Summary

You've successfully installed Jenkins using your preferred method. The installation includes:
- Jenkins server running and accessible
- Initial admin user created
- Essential plugins installed
- Basic security configured
- System tools configured
- Credentials system set up

---

**Previous:** [← What is Jenkins](01-what-is-jenkins.md) | **Next:** [Create First Job →](03-first-job.md)
