# Jenkins Configuration as Code (JCasC)

## Overview

Configuration as Code (JCasC) allows you to define Jenkins configuration in YAML files, making it version-controlled, reproducible, and portable. This modern approach eliminates manual UI configuration and enables GitOps for Jenkins.

## Why JCasC?

### Traditional Approach Problems
- ❌ Manual UI configuration
- ❌ Not version controlled
- ❌ Difficult to replicate
- ❌ No audit trail
- ❌ Error-prone
- ❌ Time-consuming

### JCasC Benefits
- ✅ Configuration as YAML
- ✅ Version controlled
- ✅ Reproducible environments
- ✅ Automated setup
- ✅ Disaster recovery
- ✅ GitOps workflow

## Installation

### Install Plugin

```
Manage Jenkins → Manage Plugins → Available
Search: Configuration as Code Plugin
Install without restart
```

### Verify Installation

```
Manage Jenkins → Configuration as Code
```

## Basic Configuration

### Simple jenkins.yaml

```yaml
jenkins:
  systemMessage: "Jenkins configured automatically by JCasC"
  numExecutors: 0
  mode: EXCLUSIVE
  scmCheckoutRetryCount: 3
  
  securityRealm:
    local:
      allowsSignup: false
      users:
        - id: "admin"
          password: "${ADMIN_PASSWORD}"
          name: "Administrator"
          
  authorizationStrategy:
    globalMatrix:
      permissions:
        - "Overall/Administer:admin"
        - "Overall/Read:authenticated"
```

### Environment Variables

Use environment variables for secrets:

```yaml
jenkins:
  systemMessage: "Jenkins for ${ENVIRONMENT}"
  
credentials:
  system:
    domainCredentials:
      - credentials:
          - usernamePassword:
              scope: GLOBAL
              id: "github-credentials"
              username: "jenkins-bot"
              password: "${GITHUB_TOKEN}"
```

**Set Variables:**
```bash
# Docker
docker run -e ADMIN_PASSWORD=secret \
           -e GITHUB_TOKEN=ghp_xxx \
           -e ENVIRONMENT=production \
           jenkins/jenkins:lts

# Kubernetes
env:
  - name: ADMIN_PASSWORD
    valueFrom:
      secretKeyRef:
        name: jenkins-secrets
        key: admin-password
```

## Complete Configuration Example

### Full jenkins.yaml

```yaml
jenkins:
  # System Settings
  systemMessage: |
    Welcome to Jenkins configured with JCasC
    Environment: ${ENVIRONMENT:-production}
  
  numExecutors: 0
  mode: EXCLUSIVE
  scmCheckoutRetryCount: 3
  
  # Quiet Period
  quietPeriod: 5
  
  # Security
  disableRememberMe: false
  remotingSecurity:
    enabled: true
  
  # Location
  location:
    url: "${JENKINS_URL}"
    adminAddress: "jenkins@company.com"
  
  # Security Realm (Authentication)
  securityRealm:
    local:
      allowsSignup: false
      users:
        - id: "admin"
          password: "${ADMIN_PASSWORD}"
          name: "Administrator"
          
  # Authorization Strategy
  authorizationStrategy:
    roleBased:
      roles:
        global:
          - name: "admin"
            description: "Jenkins administrators"
            permissions:
              - "Overall/Administer"
            entries:
              - user: "admin"
          
          - name: "developer"
            description: "Developers"
            permissions:
              - "Overall/Read"
              - "Job/Build"
              - "Job/Read"
              - "Job/Workspace"
            entries:
              - user: "dev-team"
        
        items:
          - name: "frontend-dev"
            description: "Frontend developers"
            pattern: "frontend-.*"
            permissions:
              - "Job/Build"
              - "Job/Cancel"
              - "Job/Configure"
              - "Job/Read"
            entries:
              - user: "frontend-team"
  
  # Clouds
  clouds:
    - kubernetes:
        name: "kubernetes"
        serverUrl: "https://kubernetes.default"
        namespace: "jenkins"
        jenkinsUrl: "http://jenkins:8080"
        jenkinsTunnel: "jenkins-agent:50000"
        containerCapStr: "100"
        maxRequestsPerHostStr: "32"
        retentionTimeout: 5
        connectTimeout: 10
        readTimeout: 20
        
        templates:
          - name: "jenkins-agent"
            namespace: "jenkins"
            label: "kubernetes pod"
            nodeUsageMode: NORMAL
            containers:
              - name: "jnlp"
                image: "jenkins/inbound-agent:latest"
                alwaysPullImage: false
                workingDir: "/home/jenkins/agent"
                ttyEnabled: true
                resourceRequestCpu: "500m"
                resourceRequestMemory: "512Mi"
                resourceLimitCpu: "1"
                resourceLimitMemory: "1Gi"

# Credentials
credentials:
  system:
    domainCredentials:
      - credentials:
          # Username/Password
          - usernamePassword:
              scope: GLOBAL
              id: "github-credentials"
              username: "jenkins-bot"
              password: "${GITHUB_TOKEN}"
              description: "GitHub Bot Account"
          
          # Secret Text
          - string:
              scope: GLOBAL
              id: "api-token"
              secret: "${API_TOKEN}"
              description: "API Authentication Token"
          
          # SSH Key
          - basicSSHUserPrivateKey:
              scope: GLOBAL
              id: "ssh-deploy-key"
              username: "git"
              privateKeySource:
                directEntry:
                  privateKey: "${SSH_PRIVATE_KEY}"
              description: "SSH Deployment Key"
          
          # AWS Credentials
          - aws:
              scope: GLOBAL
              id: "aws-credentials"
              accessKey: "${AWS_ACCESS_KEY_ID}"
              secretKey: "${AWS_SECRET_ACCESS_KEY}"
              description: "AWS Access"

# Tool Configuration
tool:
  git:
    installations:
      - name: "Default"
        home: "git"
  
  jdk:
    installations:
      - name: "JDK17"
        properties:
          - installSource:
              installers:
                - jdkInstaller:
                    id: "jdk-17.0.5+8"
  
  maven:
    installations:
      - name: "Maven 3.8.6"
        properties:
          - installSource:
              installers:
                - maven:
                    id: "3.8.6"
  
  nodejs:
    installations:
      - name: "NodeJS 16"
        properties:
          - installSource:
              installers:
                - nodeJSInstaller:
                    id: "16.18.1"
                    npmPackagesRefreshHours: 72

# Unclassified (Plugin-specific)
unclassified:
  location:
    url: "${JENKINS_URL}"
    adminAddress: "jenkins@company.com"
  
  globalLibraries:
    libraries:
      - name: "shared-library"
        defaultVersion: "main"
        retriever:
          modernSCM:
            scm:
              git:
                remote: "https://github.com/company/jenkins-shared-library.git"
                credentialsId: "github-credentials"
  
  gitHubPluginConfig:
    configs:
      - name: "GitHub"
        apiUrl: "https://api.github.com"
        credentialsId: "github-credentials"
        manageHooks: true
  
  gitLabServers:
    servers:
      - name: "GitLab"
        serverUrl: "https://gitlab.com"
        credentialsId: "gitlab-token"
        manageHooks: true
  
  slackNotifier:
    teamDomain: "company"
    tokenCredentialId: "slack-token"
    room: "#builds"
  
  sonarGlobalConfiguration:
    installations:
      - name: "SonarQube"
        serverUrl: "https://sonar.company.com"
        credentialsId: "sonar-token"

# Job DSL
jobs:
  - script: >
      pipelineJob('example-pipeline') {
        definition {
          cpsScm {
            scm {
              git {
                remote {
                  url('https://github.com/company/app.git')
                  credentials('github-credentials')
                }
                branch('*/main')
              }
            }
            scriptPath('Jenkinsfile')
          }
        }
      }
```

## Loading Configuration

### Method 1: Environment Variable

```bash
export CASC_JENKINS_CONFIG=/var/jenkins_home/jenkins.yaml
```

### Method 2: System Property

```bash
java -Djenkins.model.Jenkins.slaveAgentPort=50000 \
     -Dcasc.jenkins.config=/path/to/jenkins.yaml \
     -jar jenkins.war
```

### Method 3: Docker

**Dockerfile:**
```dockerfile
FROM jenkins/jenkins:lts

# Install plugins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# Copy JCasC configuration
COPY jenkins.yaml /var/jenkins_home/jenkins.yaml

# Set JCasC configuration
ENV CASC_JENKINS_CONFIG=/var/jenkins_home/jenkins.yaml

# Skip setup wizard
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"
```

**Build and Run:**
```bash
docker build -t jenkins-configured .

docker run -d \
  -p 8080:8080 \
  -p 50000:50000 \
  -e ADMIN_PASSWORD=secret \
  -e GITHUB_TOKEN=ghp_xxx \
  jenkins-configured
```

### Method 4: Kubernetes

**ConfigMap:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: jenkins-casc-config
  namespace: jenkins
data:
  jenkins.yaml: |
    jenkins:
      systemMessage: "Jenkins configured with JCasC"
      numExecutors: 0
      securityRealm:
        local:
          allowsSignup: false
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
  namespace: jenkins
spec:
  template:
    spec:
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts
        env:
        - name: CASC_JENKINS_CONFIG
          value: /var/jenkins_home/casc_configs
        - name: ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: jenkins-secrets
              key: admin-password
        volumeMounts:
        - name: jenkins-casc-config
          mountPath: /var/jenkins_home/casc_configs
      volumes:
      - name: jenkins-casc-config
        configMap:
          name: jenkins-casc-config
```

## Validation and Export

### Validate Configuration

```bash
# Via UI
Manage Jenkins → Configuration as Code → Check Configuration

# Via CLI
curl -X POST http://jenkins-url/configuration-as-code/checkNewSource \
  --user admin:token \
  --data-urlencode newSource@jenkins.yaml
```

### Export Current Configuration

```bash
# Via UI
Manage Jenkins → Configuration as Code → View Configuration

# Via CLI
curl http://jenkins-url/configuration-as-code/export \
  --user admin:token \
  > current-config.yaml
```

### Reload Configuration

```bash
# Via UI
Manage Jenkins → Configuration as Code → Reload existing configuration

# Via CLI
curl -X POST http://jenkins-url/configuration-as-code/reload \
  --user admin:token
```

## Advanced Patterns

### Multiple Configuration Files

```bash
# Point to directory
export CASC_JENKINS_CONFIG=/var/jenkins_home/casc_configs/

# Files loaded in alphabetical order
casc_configs/
├── 01-jenkins.yaml
├── 02-credentials.yaml
├── 03-clouds.yaml
└── 04-tools.yaml
```

### Environment-Specific Config

**base.yaml:**
```yaml
jenkins:
  numExecutors: 0
  mode: EXCLUSIVE
```

**production.yaml:**
```yaml
jenkins:
  systemMessage: "Production Jenkins"
  location:
    url: "https://jenkins.prod.company.com"
```

**staging.yaml:**
```yaml
jenkins:
  systemMessage: "Staging Jenkins"
  location:
    url: "https://jenkins.staging.company.com"
```

**Docker Compose:**
```yaml
services:
  jenkins-prod:
    image: jenkins/jenkins:lts
    environment:
      - CASC_JENKINS_CONFIG=/configs/base.yaml:/configs/production.yaml
    volumes:
      - ./base.yaml:/configs/base.yaml
      - ./production.yaml:/configs/production.yaml
```

### Secrets Management

#### Using Vault

```yaml
jenkins:
  securityRealm:
    local:
      users:
        - id: "admin"
          password: "${vault:/secret/jenkins/admin-password}"
```

**Configuration:**
```bash
export CASC_VAULT_URL=https://vault.company.com
export CASC_VAULT_TOKEN=s.xxxxx
export CASC_VAULT_ENGINE_VERSION=2
```

#### Using AWS Secrets Manager

```yaml
credentials:
  system:
    domainCredentials:
      - credentials:
          - string:
              id: "api-key"
              secret: "${awsSecretsManager:jenkins/api-key}"
```

#### Using File Secrets

```yaml
jenkins:
  securityRealm:
    local:
      users:
        - id: "admin"
          password: "${readFile:/run/secrets/admin-password}"
```

## Real-World Examples

### Minimal Startup

```yaml
jenkins:
  systemMessage: "Jenkins is ready"
  numExecutors: 0
  
  securityRealm:
    local:
      allowsSignup: false
      users:
        - id: "${JENKINS_ADMIN_USER:-admin}"
          password: "${JENKINS_ADMIN_PASSWORD}"
  
  authorizationStrategy:
    loggedInUsersCanDoAnything:
      allowAnonymousRead: false

unclassified:
  location:
    url: "${JENKINS_URL}"
```

### Enterprise Configuration

```yaml
jenkins:
  systemMessage: "Enterprise Jenkins"
  numExecutors: 0
  mode: EXCLUSIVE
  quietPeriod: 5
  scmCheckoutRetryCount: 3
  
  securityRealm:
    ldap:
      configurations:
        - server: "ldap://ldap.company.com"
          rootDN: "dc=company,dc=com"
          userSearchBase: "ou=users"
          userSearch: "uid={0}"
          groupSearchBase: "ou=groups"
          inhibitInferRootDN: false
  
  authorizationStrategy:
    roleBased:
      roles:
        global:
          - name: "admin"
            permissions:
              - "Overall/Administer"
            entries:
              - group: "jenkins-admins"
          - name: "developer"
            permissions:
              - "Overall/Read"
              - "Job/Build"
              - "Job/Read"
            entries:
              - group: "developers"
  
  clouds:
    - kubernetes:
        name: "kubernetes"
        serverUrl: "https://kubernetes.default"
        namespace: "jenkins"
        jenkinsUrl: "http://jenkins:8080"
        
  globalNodeProperties:
    - envVars:
        env:
          - key: "ENVIRONMENT"
            value: "production"
          - key: "REGION"
            value: "us-east-1"

credentials:
  system:
    domainCredentials:
      - credentials:
          - aws:
              id: "aws-credentials"
              scope: GLOBAL
              accessKey: "${AWS_ACCESS_KEY_ID}"
              secretKey: "${AWS_SECRET_ACCESS_KEY}"
          
          - usernamePassword:
              id: "github-app"
              scope: GLOBAL
              username: "jenkins-bot"
              password: "${GITHUB_TOKEN}"

tool:
  git:
    installations:
      - name: "git"
        home: "/usr/bin/git"
  
  jdk:
    installations:
      - name: "JDK17"
        home: "/usr/lib/jvm/java-17-openjdk"
  
  maven:
    installations:
      - name: "Maven"
        home: "/usr/share/maven"

unclassified:
  globalLibraries:
    libraries:
      - name: "pipeline-library"
        defaultVersion: "main"
        implicit: false
        allowVersionOverride: true
        retriever:
          modernSCM:
            scm:
              git:
                remote: "https://github.com/company/pipeline-library.git"
                credentialsId: "github-app"
  
  slackNotifier:
    teamDomain: "company"
    tokenCredentialId: "slack-token"
    room: "#ci-notifications"
```

## GitOps Workflow

### Repository Structure

```
jenkins-config/
├── base/
│   ├── jenkins.yaml
│   ├── credentials.yaml
│   └── tools.yaml
├── environments/
│   ├── dev/
│   │   └── jenkins.yaml
│   ├── staging/
│   │   └── jenkins.yaml
│   └── production/
│       └── jenkins.yaml
├── .gitignore
└── README.md
```

### Automated Updates

**GitHub Actions:**
```yaml
name: Update Jenkins Configuration

on:
  push:
    branches: [main]
    paths:
      - 'production/**'

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Update ConfigMap
        run: |
          kubectl create configmap jenkins-casc-config \
            --from-file=production/jenkins.yaml \
            --dry-run=client -o yaml | \
          kubectl apply -f -
      
      - name: Reload Configuration
        run: |
          curl -X POST \
            https://jenkins.company.com/configuration-as-code/reload \
            -u ${{ secrets.JENKINS_USER }}:${{ secrets.JENKINS_TOKEN }}
```

## Best Practices

### 1. Version Control Everything

```bash
git add jenkins.yaml
git commit -m "Update Jenkins configuration"
git push
```

### 2. Use Environment Variables for Secrets

❌ **Never:**
```yaml
password: "hardcoded-secret"
```

✅ **Always:**
```yaml
password: "${ADMIN_PASSWORD}"
```

### 3. Validate Before Applying

```bash
# Test configuration
curl -X POST http://localhost:8080/configuration-as-code/checkNewSource \
  --data-urlencode newSource@jenkins.yaml
```

### 4. Start Simple, Expand Gradually

```yaml
# Stage 1: Basic
jenkins:
  systemMessage: "Hello"

# Stage 2: Add security
jenkins:
  systemMessage: "Hello"
  securityRealm:
    local:
      users: [...]

# Stage 3: Add clouds, tools, etc.
```

### 5. Document Your Configuration

```yaml
# Jenkins system configuration
# Owner: DevOps Team
# Last Updated: 2026-01-15

jenkins:
  # Set to 0 - builds run on agents only
  numExecutors: 0
```

## Troubleshooting

### Configuration Not Loading

**Check:**
```bash
# Verify environment variable
echo $CASC_JENKINS_CONFIG

# Check Jenkins logs
docker logs jenkins | grep -i casc

# Validate YAML syntax
yamllint jenkins.yaml
```

### Secrets Not Resolving

**Check:**
```bash
# Environment variable set?
env | grep PASSWORD

# Correct syntax?
${VARIABLE_NAME}  # Not $VARIABLE_NAME
```

### Plugin Version Conflicts

**Solution:**
```yaml
# Specify compatible versions in plugins.txt
configuration-as-code:1.55
configuration-as-code-support:1.19
```

## Summary

JCasC enables modern Jenkins management:
- Configuration as code
- Version controlled
- Reproducible environments
- Automated setup
- GitOps workflow
- No manual UI configuration

**Key Benefits:**
- Disaster recovery
- Environment parity
- Audit trail
- Team collaboration
- Infrastructure as Code

**Production Ready:**
- Use environment variables for secrets
- Version control configuration
- Validate before applying
- Implement GitOps workflow
- Regular backups

---

**Previous:** [← Blue Ocean](17-blue-ocean.md) | **Next:** [Performance →](19-performance.md)
