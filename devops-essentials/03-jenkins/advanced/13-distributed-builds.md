# Distributed Jenkins (Master-Agent Architecture)

## Overview

Distributed builds allow Jenkins to scale horizontally by distributing workload across multiple agents. This guide covers master-agent architecture, agent configuration, and scaling strategies.

## Architecture

### Master/Controller

**Responsibilities:**
- Schedule builds
- Monitor agents
- Manage configuration
- Serve UI
- Store build results

**Should NOT:**
- Execute builds (security risk)
- Heavy computation
- Run user code

### Agents/Nodes

**Responsibilities:**
- Execute builds
- Report status to master
- Maintain workspace
- Clean up after builds

**Types:**
- **Permanent Agents:** Always connected
- **Cloud Agents:** Provisioned on-demand
- **Docker Agents:** Container-based
- **Kubernetes Pods:** Dynamic pods

## Master Configuration

### Restrict Master Execution

```
Manage Jenkins → Configure System
# of executors: 0 (recommended)
Or: 1 (for emergencies only)

Usage: Only build jobs with label restrictions
```

### Security Best Practices

```
Manage Jenkins → Configure Global Security
Agent → Controller Security: Enable

Agent → Controller Access Control:
✓ Enable Agent → Controller Access Control
```

## Agent Types

### 1. Permanent SSH Agents

**Add Agent:**
```
Manage Jenkins → Manage Nodes and Clouds → New Node

Node name: linux-agent-01
Type: Permanent Agent

Configuration:
  Remote root directory: /home/jenkins
  Labels: linux docker maven
  Usage: Use this node as much as possible
  Launch method: Launch agents via SSH
  Host: 192.168.1.100
  Credentials: [SSH key]
  Host Key Verification Strategy: Manually trusted key
```

**Agent Machine Setup:**
```bash
# Create jenkins user
sudo useradd -m -s /bin/bash jenkins

# Setup SSH
sudo su - jenkins
mkdir ~/.ssh
chmod 700 ~/.ssh

# Add master's public key
echo "ssh-rsa AAAAB3..." >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Install Java
sudo apt-get install -y openjdk-11-jre

# Install tools
sudo apt-get install -y git docker.io maven
sudo usermod -aG docker jenkins
```

### 2. JNLP Agents

**Configure Master:**
```
Manage Jenkins → Configure Global Security
Agents:
  TCP port for inbound agents: Fixed 50000
```

**Add Agent:**
```
Manage Jenkins → Manage Nodes → New Node

Launch method: Launch agent by connecting it to the master
```

**Start Agent (Linux):**
```bash
# Download agent.jar
curl -O http://jenkins-master:8080/jnlpJars/agent.jar

# Run agent
java -jar agent.jar \\
  -jnlpUrl http://jenkins-master:8080/computer/agent-name/slave-agent.jnlp \\
  -secret SECRET_KEY \\
  -workDir /home/jenkins
```

**Run as Service:**
```bash
# Create systemd service
sudo cat > /etc/systemd/system/jenkins-agent.service <<EOF
[Unit]
Description=Jenkins Agent
After=network.target

[Service]
Type=simple
User=jenkins
WorkingDirectory=/home/jenkins
ExecStart=/usr/bin/java -jar /home/jenkins/agent.jar \\
  -jnlpUrl http://jenkins-master:8080/computer/agent-01/slave-agent.jnlp \\
  -secret SECRET \\
  -workDir /home/jenkins
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable jenkins-agent
sudo systemctl start jenkins-agent
```

### 3. Windows Agents

**Launch via WMI:**
```
Launch method: Let Jenkins control this Windows slave as a Windows service

Administrator credentials required
```

**Launch via JNLP (Windows):**
```powershell
# Download agent.jar
Invoke-WebRequest -Uri "http://jenkins-master:8080/jnlpJars/agent.jar" \\
  -OutFile agent.jar

# Run agent
java -jar agent.jar `
  -jnlpUrl http://jenkins-master:8080/computer/win-agent/slave-agent.jnlp `
  -secret SECRET_KEY `
  -workDir C:\\Jenkins
```

### 4. Docker Agents

**Install Plugin:**
```
Docker Plugin
```

**Configure:**
```
Manage Jenkins → Manage Nodes and Clouds → Configure Clouds → Docker

Docker Host URI: unix:///var/run/docker.sock
Or: tcp://docker-host:2376

Docker Agent templates:
  Labels: docker
  Docker Image: jenkins/inbound-agent:latest
  Remote File System Root: /home/jenkins
```

**Use in Pipeline:**
```groovy
pipeline {
    agent {
        docker {
            image 'maven:3.8'
            label 'docker'
        }
    }
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
    }
}
```

### 5. Kubernetes Agents

**Install Plugin:**
```
Kubernetes Plugin
```

**Configure:**
```
Manage Jenkins → Manage Nodes and Clouds → Configure Clouds → Kubernetes

Kubernetes URL: https://k8s-api-server:6443
Kubernetes Namespace: jenkins
Credentials: [K8s service account]

Pod Template:
  Name: jenkins-agent
  Labels: kubernetes pod
  Containers:
    - Name: jnlp
      Docker image: jenkins/inbound-agent:latest
```

**Use in Pipeline:**
```groovy
pipeline {
    agent {
        kubernetes {
            label 'k8s-agent'
            yaml '''
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins: agent
spec:
  serviceAccountName: jenkins
  containers:
  - name: maven
    image: maven:3.8-openjdk-11
    command:
    - cat
    tty: true
    resources:
      requests:
        memory: "2Gi"
        cpu: "1"
      limits:
        memory: "4Gi"
        cpu: "2"
  - name: docker
    image: docker:20-dind
    securityContext:
      privileged: true
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run
  volumes:
  - name: docker-sock
    emptyDir: {}
            '''
        }
    }
    
    stages {
        stage('Build') {
            steps {
                container('maven') {
                    sh 'mvn clean package'
                }
            }
        }
        
        stage('Docker') {
            steps {
                container('docker') {
                    sh 'docker build -t myapp .'
                }
            }
        }
    }
}
```

## Cloud Agents

### AWS EC2 Agents

**Install Plugin:**
```
Amazon EC2 Plugin
```

**Configure:**
```
Manage Jenkins → Manage Nodes and Clouds → Configure Clouds → Amazon EC2

AWS Credentials: [IAM credentials]
Region: us-east-1
EC2 Key Pair: jenkins-key

AMI Configuration:
  AMI ID: ami-0c55b159cbfafe1f0
  Instance Type: t3.medium
  Security group: jenkins-agents
  Labels: ec2 linux
  Remote FS root: /home/jenkins
  Remote user: ec2-user
  Init script:
    #!/bin/bash
    sudo yum install -y java-11-openjdk git docker
    sudo systemctl start docker
    sudo usermod -aG docker ec2-user
```

**Use in Pipeline:**
```groovy
pipeline {
    agent {
        label 'ec2'
    }
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
    }
}
```

### Azure VM Agents

**Install Plugin:**
```
Azure VM Agents Plugin
```

**Configure:**
```
Cloud Name: Azure
Subscription ID: [Azure subscription]
Credentials: [Azure service principal]

VM Template:
  Image: Ubuntu 20.04
  VM Size: Standard_D2s_v3
  Region: East US
  Labels: azure linux
```

### GCP Agents

**Install Plugin:**
```
Google Compute Engine Plugin
```

## Agent Labels

### Static Labels

```
Agent Configuration:
  Labels: linux maven docker aws
```

**Use:**
```groovy
pipeline {
    agent {
        label 'linux && docker'
    }
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t myapp .'
            }
        }
    }
}
```

### Dynamic Labels

```groovy
pipeline {
    agent {
        label getAgentLabel()
    }
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
    }
}

def getAgentLabel() {
    if (env.BRANCH_NAME == 'main') {
        return 'production-builder'
    } else {
        return 'dev-builder'
    }
}
```

## Scaling Strategies

### 1. Auto-Scaling Groups (AWS)

**ASG Configuration:**
```
Min: 1
Max: 10
Desired: 2
Scale up: CPU > 70% or Queue > 5
Scale down: CPU < 30% and Queue == 0
```

### 2. Kubernetes Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: jenkins-agent-hpa
  namespace: jenkins
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: jenkins-agent
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 3. Queue-Based Scaling

**Groovy Script:**
```groovy
import hudson.model.*

def queue = Jenkins.instance.queue
def queueSize = queue.items.length

if (queueSize > 5) {
    // Scale up
    triggerScaleUp()
} else if (queueSize == 0) {
    // Scale down idle agents
    triggerScaleDown()
}
```

## Load Balancing

### Even Distribution

```
Agent Usage: Use this node as much as possible
```

### Specialized Agents

```
Agent Usage: Only build jobs with label restrictions

Job Configuration:
  Restrict where this project can be run: maven-agents
```

### Fair Share

```groovy
pipeline {
    options {
        throttleJobProperty(
            categories: ['heavy-builds'],
            maxConcurrentPerNode: 2,
            maxConcurrentTotal: 10
        )
    }
}
```

## Monitoring Agents

### Built-in Monitoring

```
Manage Jenkins → Manage Nodes and Clouds

View:
- Agent status (online/offline)
- Disk space
- Response time
- Clock difference
- Build executors
```

### Prometheus Metrics

**Install Plugin:**
```
Prometheus Metrics Plugin
```

**Metrics:**
```
jenkins_node_online{node="agent-01"} 1
jenkins_node_builds_count{node="agent-01"} 42
jenkins_node_executors{node="agent-01"} 2
```

**Grafana Dashboard:**
```
- Agent availability
- Build distribution
- Resource utilization
- Queue length
```

## Maintenance

### Taking Agent Offline

```groovy
// Mark offline
Jenkins.instance.getNode('agent-01').setTemporarilyOffline(true, 
    new hudson.slaves.OfflineCause.ByCLI("Maintenance"))

// Bring online
Jenkins.instance.getNode('agent-01').setTemporarilyOffline(false, null)
```

### Cleaning Workspaces

**Automated Cleanup:**
```groovy
pipeline {
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
```

**Manual Cleanup:**
```
Node Configuration → Wipe Out Workspace
```

### Agent Health Checks

```groovy
// Groovy script
Jenkins.instance.nodes.each { node ->
    def computer = node.toComputer()
    
    if (computer.isOffline()) {
        println "${node.name} is OFFLINE: ${computer.offlineCause}"
    } else {
        def diskSpace = computer.getDiskSpaceMonitor()
        def responseTime = computer.getResponseTime()
        
        println "${node.name}: Disk=${diskSpace} Response=${responseTime}ms"
    }
}
```

## Security Best Practices

### 1. Isolate Agent Network

```
Agents in private subnet
Master in public subnet (or behind LB)
Agent → Master traffic only
```

### 2. Agent-to-Master Security

```
Manage Jenkins → Configure Global Security
Agent → Controller Security:
  ✓ Enable Agent → Controller Access Control
  
Whitelist specific classes/methods only
```

### 3. Credential Isolation

```
Use folder-scoped credentials
Agents can only access necessary credentials
```

### 4. Container Isolation

```groovy
agent {
    docker {
        image 'maven:3.8'
        args '--read-only --tmpfs /tmp --user 1000:1000'
    }
}
```

## Troubleshooting

### Agent Won't Connect

**Check:**
```bash
# Firewall
telnet jenkins-master 50000

# SSH
ssh jenkins@agent-ip

# Java version
java -version

# Disk space
df -h
```

### Slow Builds

**Investigate:**
```
1. Agent resource utilization (CPU, RAM, disk)
2. Network latency between master and agent
3. Workspace size
4. Too many concurrent builds
```

**Solutions:**
```
- Add more agents
- Increase agent resources
- Distribute builds better
- Clean workspaces regularly
```

### Agent Disconnects

**Common Causes:**
```
- Network issues
- Out of memory
- Disk full
- Java process killed
```

**Fix:**
```bash
# Check logs
tail -f /var/log/jenkins/agent.log

# Monitor resources
htop
df -h

# Increase Java heap
java -Xmx2g -jar agent.jar ...
```

## Best Practices

### 1. Designate Agent Types

```
- Build agents (general purpose)
- Test agents (with test tools)
- Deploy agents (production access)
- Heavy agents (large builds)
```

### 2. Use Labels Effectively

```
Labels: linux, docker, maven, aws, zone-us-east
```

### 3. Implement Auto-Scaling

```
Start with minimum agents
Scale up based on queue
Scale down during idle
```

### 4. Regular Maintenance

```
- Update agent software
- Clean workspaces
- Monitor disk space
- Review agent usage
```

### 5. Use Immutable Agents

```
Containers/VMs from images
Fresh agent per build
No state carried over
```

## Summary

Distributed Jenkins enables:
- Horizontal scaling
- Workload distribution
- Resource optimization
- Fault tolerance
- Specialized build environments

**Key Components:**
- Master (controller, no builds)
- Permanent agents (SSH, JNLP)
- Cloud agents (AWS, Azure, GCP)
- Container agents (Docker, K8s)
- Proper labels and distribution

**Critical for Production:**
- Never run builds on master
- Use auto-scaling
- Implement monitoring
- Regular maintenance
- Security isolation

---

**Previous:** [← Pipeline Libraries](14-pipeline-libraries.md) | **Next:** [Security →](15-security.md)
