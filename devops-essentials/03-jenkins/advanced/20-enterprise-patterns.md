# Enterprise Jenkins Patterns

## Overview

Scaling Jenkins for enterprise use requires careful architecture, governance, and operational patterns. This guide covers proven strategies for multi-team environments, high availability, and enterprise-grade CI/CD.

## Enterprise Architecture

### Single Master (Anti-Pattern)

**Problems:**
- Single point of failure
- Resource contention
- Poor isolation between teams
- Difficult to scale
- Security boundaries unclear

```
┌─────────────────┐
│  Jenkins Master │  ← All teams share
│   (Overloaded)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Agents  │
    └─────────┘
```

### Multi-Master Pattern (Recommended)

**Benefits:**
✅ Team isolation
✅ Independent scaling
✅ Failure containment
✅ Security boundaries
✅ Technology diversity

```
Team A          Team B          Team C
┌──────┐       ┌──────┐       ┌──────┐
│Master│       │Master│       │Master│
└──┬───┘       └──┬───┘       └──┬───┘
   │              │              │
┌──┴───┐      ┌──┴───┐      ┌──┴───┐
│Agents│      │Agents│      │Agents│
└──────┘      └──────┘      └──────┘
```

### Shared Services Pattern

```
┌─────────────────────────────────────┐
│      Shared Services Layer          │
│  ┌────────┐  ┌────────┐  ┌────────┐│
│  │Artifact│  │  SCM   │  │Security││
│  │Registry│  │(GitHub)│  │ (Vault)││
│  └────────┘  └────────┘  └────────┘│
└─────────────────────────────────────┘
           │         │         │
    ┌──────┴────┬────┴────┬────┴──────┐
    │           │         │            │
┌───▼───┐  ┌───▼───┐  ┌───▼───┐  ┌───▼───┐
│Team A │  │Team B │  │Team C │  │Team D │
│Master │  │Master │  │Master │  │Master │
└───────┘  └───────┘  └───────┘  └───────┘
```

## Multi-Tenancy

### Isolation Strategies

**1. Folder-Based Isolation:**
```groovy
// Configure folders per team
folder('team-a') {
    description('Team A Projects')
    authorization {
        permission('hudson.model.Item.Read', 'team-a-users')
        permission('hudson.model.Item.Build', 'team-a-users')
        permission('hudson.model.Item.Configure', 'team-a-admins')
    }
}

folder('team-b') {
    description('Team B Projects')
    authorization {
        permission('hudson.model.Item.Read', 'team-b-users')
        permission('hudson.model.Item.Build', 'team-b-users')
        permission('hudson.model.Item.Configure', 'team-b-admins')
    }
}
```

**2. Label-Based Agent Isolation:**
```groovy
pipeline {
    agent {
        label 'team-a && docker'  // Only team-a agents
    }
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
    }
}
```

**3. Namespace Isolation (Kubernetes):**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: jenkins-team-a
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
  namespace: jenkins-team-a
spec:
  replicas: 1
  template:
    spec:
      serviceAccountName: jenkins-team-a
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

### Resource Quotas

**Per-team limits:**
```yaml
# Kubernetes ResourceQuota
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-a-quota
  namespace: jenkins-team-a
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    persistentvolumeclaims: "10"
    pods: "50"
```

**Jenkins configuration:**
```groovy
// Limit concurrent builds per folder
folder('team-a') {
    properties {
        throttleJobProperty {
            maxConcurrentPerNode(5)
            maxConcurrentTotal(10)
            categories(['team-a'])
        }
    }
}
```

## High Availability

### Active-Passive HA

```
┌──────────────┐
│Load Balancer │
└──────┬───────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌──▼──┐
│Active│  │Standby│
│Master│  │Master │
└──┬──┘  └──┬──┘
   │        │
   └────┬───┘
        │
┌───────▼────────┐
│Shared Storage  │
│(NFS/EFS/GlusterFS)│
└────────────────┘
```

**Configuration:**
```yaml
# Active Jenkins
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: jenkins-active
spec:
  serviceName: jenkins
  replicas: 1
  template:
    spec:
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts
        volumeMounts:
        - name: jenkins-home
          mountPath: /var/jenkins_home
  volumeClaimTemplates:
  - metadata:
      name: jenkins-home
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi
```

### Active-Active Pattern

**Use CloudBees Jenkins Operations Center or:**

```
         ┌─────────────┐
         │   Ingress   │
         └──────┬──────┘
                │
       ┌────────┴────────┐
       │                 │
┌──────▼──────┐   ┌──────▼──────┐
│  Master 1   │   │  Master 2   │
│ (Read-Write)│   │ (Read-Write)│
└──────┬──────┘   └──────┬──────┘
       │                 │
       └────────┬────────┘
                │
      ┌─────────▼─────────┐
      │  PostgreSQL HA    │
      │  (Build History)  │
      └───────────────────┘
```

### Disaster Recovery

**Backup Strategy:**
```bash
#!/bin/bash
# jenkins-backup.sh

JENKINS_HOME="/var/jenkins_home"
BACKUP_DIR="/backups/jenkins"
DATE=$(date +%Y%m%d_%H%M%S)

# Stop Jenkins (optional)
# systemctl stop jenkins

# Backup critical data
tar -czf "$BACKUP_DIR/jenkins-$DATE.tar.gz" \
  --exclude='*/workspace/*' \
  --exclude='*/caches/*' \
  --exclude='*/logs/*' \
  "$JENKINS_HOME/config.xml" \
  "$JENKINS_HOME/jobs/" \
  "$JENKINS_HOME/users/" \
  "$JENKINS_HOME/secrets/" \
  "$JENKINS_HOME/plugins/" \
  "$JENKINS_HOME/credentials.xml"

# Upload to S3
aws s3 cp "$BACKUP_DIR/jenkins-$DATE.tar.gz" \
  s3://jenkins-backups/

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "jenkins-*.tar.gz" -mtime +30 -delete

# Start Jenkins
# systemctl start jenkins
```

**Automated backup pipeline:**
```groovy
pipeline {
    agent any
    
    triggers {
        cron('H 2 * * *')  // Daily at 2 AM
    }
    
    stages {
        stage('Backup') {
            steps {
                sh '/usr/local/bin/jenkins-backup.sh'
            }
        }
        
        stage('Verify') {
            steps {
                sh '''
                    # Verify backup integrity
                    LATEST=$(ls -t /backups/jenkins/*.tar.gz | head -1)
                    tar -tzf "$LATEST" > /dev/null
                '''
            }
        }
        
        stage('Upload Offsite') {
            steps {
                withAWS(credentials: 'aws-backup-creds') {
                    s3Upload(
                        bucket: 'jenkins-dr-backups',
                        path: 'daily/',
                        includePathPattern: '*.tar.gz'
                    )
                }
            }
        }
    }
    
    post {
        failure {
            mail to: 'ops@company.com',
                 subject: 'Jenkins Backup Failed',
                 body: "Check ${env.BUILD_URL}"
        }
    }
}
```

## Governance & Compliance

### Pipeline Approval Process

```groovy
// Jenkinsfile
@Library('enterprise-lib') _

pipeline {
    agent any
    
    stages {
        stage('Security Scan') {
            steps {
                script {
                    // Required security scan
                    securityScan()
                    
                    // Quality gate
                    def result = qualityGate()
                    if (result.status != 'PASSED') {
                        error "Quality gate failed"
                    }
                }
            }
        }
        
        stage('Compliance Check') {
            steps {
                script {
                    // Check for required approvals
                    complianceCheck(
                        requiredApprovers: 2,
                        approverGroups: ['security-team', 'qa-team']
                    )
                }
            }
        }
        
        stage('Deploy to Prod') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // Require VP approval for production
                    input(
                        message: 'Deploy to production?',
                        submitter: 'vp-engineering,cto'
                    )
                    
                    deploy('production')
                }
            }
        }
    }
    
    post {
        always {
            // Audit trail
            auditLog(
                action: 'DEPLOYMENT',
                target: env.BRANCH_NAME,
                user: env.BUILD_USER
            )
        }
    }
}
```

### Policy Enforcement

**Shared library for policy:**
```groovy
// vars/enforcePolicy.groovy
def call(Map config) {
    // Ensure all pipelines follow standards
    
    // 1. Must have quality gates
    if (!config.qualityGate) {
        error "Quality gate is required"
    }
    
    // 2. Must scan for secrets
    if (!config.secretScan) {
        error "Secret scanning is required"
    }
    
    // 3. Must have approval for production
    if (env.BRANCH_NAME == 'main' && !config.productionApproval) {
        error "Production approval is required"
    }
    
    // 4. Must tag Docker images properly
    if (config.docker && !config.imageTag?.matches(/v\d+\.\d+\.\d+/)) {
        error "Docker images must use semantic versioning"
    }
    
    echo "✅ Policy checks passed"
}
```

**Usage:**
```groovy
@Library('enterprise-lib') _

pipeline {
    agent any
    stages {
        stage('Policy Check') {
            steps {
                script {
                    enforcePolicy(
                        qualityGate: true,
                        secretScan: true,
                        productionApproval: true,
                        docker: true,
                        imageTag: env.VERSION
                    )
                }
            }
        }
    }
}
```

### Audit Logging

```groovy
// vars/auditLog.groovy
def call(Map params) {
    def logEntry = [
        timestamp: new Date().format('yyyy-MM-dd HH:mm:ss'),
        job: env.JOB_NAME,
        build: env.BUILD_NUMBER,
        action: params.action,
        user: params.user ?: env.BUILD_USER,
        target: params.target,
        result: currentBuild.result,
        branch: env.BRANCH_NAME,
        commit: env.GIT_COMMIT
    ]
    
    // Write to audit log
    writeJSON file: 'audit.json', json: logEntry
    
    // Send to centralized logging
    sh """
        curl -X POST https://logs.company.com/audit \
          -H 'Content-Type: application/json' \
          -d '${groovy.json.JsonOutput.toJson(logEntry)}'
    """
    
    // Store in artifact
    archiveArtifacts artifacts: 'audit.json', fingerprint: true
}
```

## Configuration Management

### Jenkins Configuration as Code (JCasC)

**Complete enterprise setup:**
```yaml
# jenkins.yaml
jenkins:
  systemMessage: "Enterprise Jenkins - Production"
  numExecutors: 0  # No builds on master
  mode: EXCLUSIVE
  
  securityRealm:
    ldap:
      configurations:
        - server: "ldaps://ldap.company.com"
          rootDN: "dc=company,dc=com"
          userSearchBase: "ou=users"
          userSearch: "uid={0}"
          groupSearchBase: "ou=groups"
          
  authorizationStrategy:
    projectMatrix:
      permissions:
        - "Overall/Administer:admins"
        - "Overall/Read:authenticated"
        - "Job/Read:authenticated"
        - "Job/Build:developers"
        - "Job/Configure:team-leads"
        
  clouds:
    - kubernetes:
        name: "kubernetes"
        serverUrl: "https://kubernetes.default"
        namespace: "jenkins-agents"
        jenkinsUrl: "http://jenkins:8080"
        maxRequestsPerHostStr: "32"
        templates:
          - name: "maven"
            label: "maven"
            containers:
              - name: "maven"
                image: "maven:3.8-jdk-11"
                command: "/bin/sh -c"
                args: "cat"
                ttyEnabled: true
                resourceRequestCpu: "500m"
                resourceLimitCpu: "1000m"
                resourceRequestMemory: "1Gi"
                resourceLimitMemory: "2Gi"

credentials:
  system:
    domainCredentials:
      - credentials:
          - usernamePassword:
              scope: GLOBAL
              id: "github-token"
              username: "jenkins-bot"
              password: "${GITHUB_TOKEN}"
              description: "GitHub Access Token"
          
          - aws:
              scope: GLOBAL
              id: "aws-credentials"
              accessKey: "${AWS_ACCESS_KEY}"
              secretKey: "${AWS_SECRET_KEY}"
              description: "AWS Credentials"

unclassified:
  location:
    url: "https://jenkins.company.com"
    adminAddress: "jenkins-admin@company.com"
    
  mailer:
    smtpHost: "smtp.company.com"
    smtpPort: "587"
    useSsl: true
    charset: "UTF-8"
    
  slackNotifier:
    teamDomain: "company"
    tokenCredentialId: "slack-token"
    room: "#builds"

tool:
  git:
    installations:
      - name: "Default"
        home: "/usr/bin/git"
  
  maven:
    installations:
      - name: "Maven 3.8"
        properties:
          - installSource:
              installers:
                - maven:
                    id: "3.8.6"
```

### Version Control JCasC

```bash
# Store configuration in Git
jenkins-config/
├── jenkins.yaml
├── credentials.yaml (encrypted)
├── jobs/
│   ├── team-a.yaml
│   ├── team-b.yaml
│   └── shared.yaml
└── plugins.txt
```

**Auto-reload on changes:**
```groovy
pipeline {
    agent any
    
    triggers {
        pollSCM('H/5 * * * *')
    }
    
    stages {
        stage('Apply Configuration') {
            steps {
                checkout scm
                
                // Validate YAML
                sh 'yamllint jenkins.yaml'
                
                // Apply configuration
                sh '''
                    kubectl create configmap jenkins-config \
                      --from-file=jenkins.yaml \
                      --dry-run=client -o yaml | \
                    kubectl apply -f -
                '''
                
                // Reload Jenkins (or restart pod)
                sh 'kubectl rollout restart deployment/jenkins'
            }
        }
    }
}
```

## Centralized Pipeline Templates

### Template Repository Structure

```
pipeline-templates/
├── java/
│   ├── maven-build.groovy
│   ├── gradle-build.groovy
│   └── spring-boot.groovy
├── nodejs/
│   ├── npm-build.groovy
│   └── react-app.groovy
├── python/
│   ├── pip-build.groovy
│   └── django-app.groovy
├── docker/
│   ├── docker-build.groovy
│   └── multiarch-build.groovy
└── shared/
    ├── security-scan.groovy
    ├── compliance.groovy
    └── deployment.groovy
```

### Template Usage

**Template definition:**
```groovy
// pipeline-templates/java/maven-build.groovy
def call(Map config = [:]) {
    pipeline {
        agent {
            kubernetes {
                yaml libraryResource('pod-templates/maven.yaml')
            }
        }
        
        options {
            buildDiscarder(logRotator(numToKeepStr: '30'))
            timeout(time: config.timeout ?: 30, unit: 'MINUTES')
        }
        
        stages {
            stage('Build') {
                steps {
                    container('maven') {
                        sh "mvn clean package ${config.mvnArgs ?: ''}"
                    }
                }
            }
            
            stage('Test') {
                steps {
                    container('maven') {
                        sh 'mvn test'
                        junit 'target/surefire-reports/*.xml'
                    }
                }
            }
            
            stage('Quality Gate') {
                steps {
                    script {
                        securityScan()
                        sonarQube()
                    }
                }
            }
            
            stage('Package') {
                steps {
                    container('maven') {
                        sh 'mvn deploy'
                    }
                }
            }
        }
    }
}
```

**Project usage:**
```groovy
@Library('enterprise-templates@v2.0') _

mavenBuild {
    mvnArgs = '-P production'
    timeout = 45
}
```

## Cost Optimization

### Agent Cost Tracking

```groovy
// Track agent usage and costs
@NonCPS
def trackAgentCost(agentType, duration) {
    def costPerHour = [
        'kubernetes': 0.05,
        'ec2-spot': 0.10,
        'ec2-ondemand': 0.30,
        'docker': 0.08
    ]
    
    def hours = duration / 3600000  // Convert ms to hours
    def cost = hours * costPerHour[agentType]
    
    // Send to cost tracking system
    sh """
        curl -X POST https://costs.company.com/api/usage \
          -d '{
            "service": "jenkins",
            "team": "${env.TEAM}",
            "agent": "${agentType}",
            "duration_hours": ${hours},
            "cost_usd": ${cost},
            "job": "${env.JOB_NAME}",
            "build": "${env.BUILD_NUMBER}"
          }'
    """
    
    return cost
}

pipeline {
    agent { label 'kubernetes' }
    
    stages {
        stage('Build') {
            steps {
                script {
                    def startTime = System.currentTimeMillis()
                    
                    sh 'make build'
                    
                    def duration = System.currentTimeMillis() - startTime
                    def cost = trackAgentCost('kubernetes', duration)
                    
                    echo "Build cost: \$${cost}"
                }
            }
        }
    }
}
```

### Resource Optimization

```groovy
// Auto-scale based on queue
pipeline {
    agent none
    
    stages {
        stage('Check Queue') {
            steps {
                script {
                    def queueLength = Jenkins.instance.queue.items.length
                    
                    if (queueLength > 20) {
                        // Scale up
                        sh '''
                            kubectl scale deployment jenkins-agent \
                              --replicas=10 -n jenkins
                        '''
                    } else if (queueLength < 5) {
                        // Scale down
                        sh '''
                            kubectl scale deployment jenkins-agent \
                              --replicas=2 -n jenkins
                        '''
                    }
                }
            }
        }
    }
}
```

## Security at Scale

### Secret Management

```groovy
// Centralized secret management
def getSecret(String secretPath) {
    withVault([
        vaultUrl: 'https://vault.company.com',
        vaultCredentialId: 'vault-token',
        engineVersion: 2
    ]) {
        def secrets = [
            [path: secretPath, engineVersion: 2, secretValues: [
                [envVar: 'SECRET_VALUE', vaultKey: 'value']
            ]]
        ]
        
        wrap([$class: 'VaultBuildWrapper', vaultSecrets: secrets]) {
            return env.SECRET_VALUE
        }
    }
}

pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                script {
                    def apiKey = getSecret('secret/data/prod/api-key')
                    sh "deploy --api-key=${apiKey}"
                }
            }
        }
    }
}
```

### Network Policies

```yaml
# Kubernetes NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: jenkins-master
  namespace: jenkins
spec:
  podSelector:
    matchLabels:
      app: jenkins-master
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: jenkins-agents
    ports:
    - protocol: TCP
      port: 50000
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443  # HTTPS only
```

## Monitoring Enterprise Jenkins

### SLIs/SLOs

**Service Level Indicators:**
```yaml
SLIs:
  availability:
    target: 99.9%
    measurement: "Uptime monitoring"
  
  build_success_rate:
    target: 95%
    measurement: "Successful builds / Total builds"
  
  build_duration_p95:
    target: "< 15 minutes"
    measurement: "95th percentile build time"
  
  queue_time_p95:
    target: "< 2 minutes"
    measurement: "95th percentile queue wait time"
```

**Monitoring dashboard:**
```python
# Generate SLO report
from prometheus_api_client import PrometheusConnect

prom = PrometheusConnect(url="http://prometheus:9090")

# Availability
uptime = prom.custom_query(
    query='avg_over_time(up{job="jenkins"}[30d])'
)

# Build success rate
success_rate = prom.custom_query(
    query='''
    sum(rate(jenkins_builds_success_build_count_total[30d])) /
    sum(rate(jenkins_builds_total_build_count[30d])) * 100
    '''
)

# Report
print(f"Availability: {uptime[0]['value'][1]}%")
print(f"Success Rate: {success_rate[0]['value'][1]}%")
```

## Summary

Enterprise patterns for Jenkins:
- Multi-master architecture for isolation
- Multi-tenancy with proper governance
- High availability and disaster recovery
- Configuration as code (JCasC)
- Centralized templates and policies
- Cost optimization and tracking
- Security and compliance
- Comprehensive monitoring

**Key Principles:**
- Isolate teams and workloads
- Automate everything
- Monitor and optimize continuously
- Enforce standards through code
- Plan for failure and recovery

## Next Steps

- **Practice Labs** → Hands-on exercises
- **Real-World Projects** → Apply patterns
- **Interview Preparation** → Advanced questions

---

**Previous:** [Performance](19-performance.md)  
**Next:** [Interview Questions](interview-questions-advanced.md)
