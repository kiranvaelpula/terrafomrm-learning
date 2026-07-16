# Essential Jenkins Plugins

## Overview

Plugins extend Jenkins functionality, providing integrations with tools, cloud platforms, and additional features. This guide covers essential plugins, installation, configuration, and best practices.

## Plugin Management

### Installing Plugins

**Via UI:**
```
Manage Jenkins → Manage Plugins → Available
Search for plugin → Check box → Install without restart
Or: Download now and install after restart
```

**Via Jenkins CLI:**
```bash
java -jar jenkins-cli.jar -s http://jenkins-url/ \
  -auth admin:token \
  install-plugin docker-plugin

# Multiple plugins
java -jar jenkins-cli.jar -s http://jenkins-url/ \
  -auth admin:token \
  install-plugin docker-plugin git-plugin pipeline-plugin
```

**Via Dockerfile:**
```dockerfile
FROM jenkins/jenkins:lts

# Install plugins
RUN jenkins-plugin-cli --plugins \\
    git:latest \\
    docker-workflow:latest \\
    pipeline-stage-view:latest \\
    blueocean:latest
```

### Updating Plugins

```
Manage Jenkins → Manage Plugins → Updates
Select plugins → Download now and install after restart
```

### Plugin Dependencies

Jenkins automatically installs plugin dependencies. View them:
```
Manage Jenkins → Manage Plugins → Installed
Click plugin name → Dependencies tab
```

## Essential Plugins by Category

### 1. Source Control Management

#### Git Plugin
**Purpose:** Git repository integration

**Install:**
```
git
```

**Usage:**
```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/user/repo.git',
                    credentialsId: 'github-creds'
            }
        }
    }
}
```

#### GitHub Plugin
**Purpose:** GitHub-specific features

**Features:**
- Webhook triggers
- Status notifications
- PR builder

**Usage:**
```groovy
pipeline {
    agent any
    triggers {
        githubPush()
    }
    post {
        success {
            githubNotify status: 'SUCCESS'
        }
    }
}
```

#### GitLab Plugin
**Purpose:** GitLab integration

**Usage:**
```groovy
pipeline {
    agent any
    options {
        gitLabConnection('GitLab')
    }
    triggers {
        gitlab(triggerOnPush: true, triggerOnMergeRequest: true)
    }
}
```

#### Bitbucket Plugin
**Purpose:** Bitbucket integration

**Usage:**
```groovy
pipeline {
    agent any
    triggers {
        bitbucketPush()
    }
}
```

### 2. Pipeline and Build

#### Pipeline Plugin
**Purpose:** Core pipeline functionality

**Essential for:**
- Declarative pipelines
- Scripted pipelines
- Jenkinsfile support

#### Blue Ocean
**Purpose:** Modern pipeline UI

**Install:**
```
blueocean
```

**Access:** http://jenkins-url/blue

**Features:**
- Visual pipeline editor
- Better log viewing
- Pipeline visualization
- Git integration

#### Pipeline: Stage View
**Purpose:** Visual stage representation

**Features:**
- Stage duration
- Stage status
- Trend analysis

### 3. Docker Integration

#### Docker Plugin
**Purpose:** Docker agent support

**Usage:**
```groovy
pipeline {
    agent {
        docker {
            image 'node:16'
            args '-v /tmp:/tmp'
        }
    }
    stages {
        stage('Build') {
            steps {
                sh 'node --version'
            }
        }
    }
}
```

#### Docker Pipeline Plugin
**Purpose:** Docker steps in pipeline

**Usage:**
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                script {
                    docker.image('maven:3.8').inside {
                        sh 'mvn clean package'
                    }
                }
            }
        }
    }
}
```

#### Docker Build and Publish
**Purpose:** Build and push Docker images

**Usage:**
```groovy
stage('Docker') {
    steps {
        script {
            def image = docker.build("myapp:${BUILD_NUMBER}")
            docker.withRegistry('https://registry.hub.docker.com', 'docker-creds') {
                image.push()
            }
        }
    }
}
```

### 4. Cloud Platforms

#### Amazon EC2 Plugin
**Purpose:** Dynamic EC2 agents

**Configure:**
```
Manage Jenkins → Configure System → Cloud → Add Amazon EC2

AWS Credentials: [Select IAM credentials]
Region: us-east-1
EC2 Key Pair: jenkins-key
AMI ID: ami-xxxxx
Instance Type: t3.medium
```

#### Kubernetes Plugin
**Purpose:** Dynamic K8s pods

**Configure:**
```
Manage Jenkins → Configure System → Cloud → Kubernetes

Kubernetes URL: https://k8s-api-server
Kubernetes Namespace: jenkins
Credentials: [K8s service account]
```

**Usage:**
```groovy
pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: maven
    image: maven:3.8
    command: ['cat']
    tty: true
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
    }
}
```

#### Azure VM Agents
**Purpose:** Dynamic Azure VMs

### 5. Testing and Quality

#### JUnit Plugin
**Purpose:** Publish test results

**Usage:**
```groovy
stage('Test') {
    steps {
        sh 'mvn test'
        junit '**/target/surefire-reports/*.xml'
    }
}
```

#### JaCoCo Plugin
**Purpose:** Code coverage

**Usage:**
```groovy
stage('Coverage') {
    steps {
        jacoco(
            execPattern: '**/target/jacoco.exec',
            classPattern: '**/target/classes',
            sourcePattern: '**/src/main/java'
        )
    }
}
```

#### Cobertura Plugin
**Purpose:** Code coverage reporting

**Usage:**
```groovy
stage('Coverage') {
    steps {
        cobertura(
            coberturaReportFile: 'coverage/cobertura-coverage.xml',
            onlyStable: false
        )
    }
}
```

#### SonarQube Scanner
**Purpose:** Code quality analysis

**Configure:**
```
Manage Jenkins → Configure System → SonarQube servers
Name: SonarQube
Server URL: http://sonarqube.company.com
Token: [SonarQube token]
```

**Usage:**
```groovy
stage('SonarQube') {
    steps {
        withSonarQubeEnv('SonarQube') {
            sh 'mvn sonar:sonar'
        }
    }
}

stage('Quality Gate') {
    steps {
        timeout(time: 5, unit: 'MINUTES') {
            waitForQualityGate abortPipeline: true
        }
    }
}
```

#### Performance Plugin
**Purpose:** Performance test reporting

**Usage:**
```groovy
stage('Performance') {
    steps {
        performanceReport(
            sourceDataFiles: 'results/*.jtl',
            errorUnstableThreshold: 10
        )
    }
}
```

### 6. Deployment and Infrastructure

#### Kubernetes CLI Plugin
**Purpose:** kubectl commands

**Usage:**
```groovy
stage('Deploy') {
    steps {
        withKubeConfig([credentialsId: 'kubeconfig']) {
            sh 'kubectl apply -f deployment.yaml'
            sh 'kubectl rollout status deployment/myapp'
        }
    }
}
```

#### AWS Steps
**Purpose:** AWS CLI operations

**Usage:**
```groovy
stage('Deploy to S3') {
    steps {
        withAWS(credentials: 'aws-creds', region: 'us-east-1') {
            s3Upload(
                bucket: 'my-bucket',
                path: 'artifacts/',
                includePathPattern: '**/*.jar'
            )
        }
    }
}
```

#### Terraform Plugin
**Purpose:** Infrastructure as Code

**Usage:**
```groovy
stage('Terraform') {
    steps {
        sh 'terraform init'
        sh 'terraform plan -out=tfplan'
        sh 'terraform apply tfplan'
    }
}
```

#### Ansible Plugin
**Purpose:** Configuration management

**Usage:**
```groovy
stage('Configure') {
    steps {
        ansiblePlaybook(
            playbook: 'deploy.yml',
            inventory: 'inventory/production',
            credentialsId: 'ansible-ssh-key'
        )
    }
}
```

### 7. Notifications

#### Email Extension Plugin
**Purpose:** Advanced email notifications

**Usage:**
```groovy
post {
    failure {
        emailext(
            subject: "Build Failed: ${JOB_NAME} #${BUILD_NUMBER}",
            body: """
                Build failed.
                Check console: ${BUILD_URL}console
            """,
            to: 'team@company.com',
            attachLog: true
        )
    }
}
```

#### Slack Notification Plugin
**Purpose:** Slack messages

**Configure:**
```
Manage Jenkins → Configure System → Slack

Workspace: your-workspace
Credential: [Slack token]
Default channel: #builds
```

**Usage:**
```groovy
post {
    success {
        slackSend(
            color: 'good',
            message: "Build succeeded: ${JOB_NAME} #${BUILD_NUMBER}"
        )
    }
    failure {
        slackSend(
            color: 'danger',
            message: "Build failed: ${JOB_NAME} #${BUILD_NUMBER}"
        )
    }
}
```

#### Microsoft Teams Notification
**Purpose:** Teams messages

**Usage:**
```groovy
office365ConnectorSend(
    message: "Build completed",
    status: "Success",
    webhookUrl: "${TEAMS_WEBHOOK}"
)
```

### 8. Security and Credentials

#### Credentials Plugin
**Purpose:** Secure credential storage

**Built-in, essential for:**
- Passwords
- SSH keys
- Tokens
- Certificates

#### Role-based Authorization Strategy
**Purpose:** Fine-grained permissions

**Configure:**
```
Manage Jenkins → Manage and Assign Roles

Global roles: admin, developer, viewer
Project roles: frontend-dev, backend-dev
```

#### LDAP Plugin
**Purpose:** LDAP authentication

#### Active Directory Plugin
**Purpose:** AD authentication

#### HashiCorp Vault Plugin
**Purpose:** External secrets

**Usage:**
```groovy
def secrets = [
    [path: 'secret/data/app', secretValues: [
        [envVar: 'PASSWORD', vaultKey: 'password']
    ]]
]

withVault([vaultSecrets: secrets]) {
    sh 'deploy.sh'
}
```

### 9. Build Tools

#### Maven Integration Plugin
**Purpose:** Maven project support

**Usage:**
```groovy
stage('Maven Build') {
    steps {
        sh 'mvn clean install'
    }
}
```

#### Gradle Plugin
**Purpose:** Gradle support

**Usage:**
```groovy
stage('Gradle Build') {
    steps {
        sh './gradlew build'
    }
}
```

#### NodeJS Plugin
**Purpose:** Node.js environment

**Configure:**
```
Manage Jenkins → Global Tool Configuration → NodeJS

Name: NodeJS 16
Version: 16.x
```

**Usage:**
```groovy
pipeline {
    agent any
    tools {
        nodejs 'NodeJS 16'
    }
    stages {
        stage('Build') {
            steps {
                sh 'npm install'
                sh 'npm run build'
            }
        }
    }
}
```

### 10. Monitoring and Reporting

#### Prometheus Metrics Plugin
**Purpose:** Expose metrics

**Access:** http://jenkins-url/prometheus

**Metrics:**
- Build duration
- Queue size
- Executor usage
- Job success/failure rates

#### Build Monitor Plugin
**Purpose:** Dashboard view

#### Dashboard View Plugin
**Purpose:** Custom dashboards

#### HTML Publisher Plugin
**Purpose:** Publish HTML reports

**Usage:**
```groovy
publishHTML([
    reportDir: 'target/site/jacoco',
    reportFiles: 'index.html',
    reportName: 'Coverage Report',
    keepAll: true
])
```

## Plugin Configuration Best Practices

### 1. Minimal Installation

Install only what you need:
```groovy
// Dockerfile with minimal plugins
FROM jenkins/jenkins:lts
RUN jenkins-plugin-cli --plugins \\
    git \\
    workflow-aggregator \\
    docker-workflow \\
    kubernetes \\
    blueocean
```

### 2. Regular Updates

```bash
# Check for security updates
curl -s https://updates.jenkins.io/current/update-center.json | \\
  jq '.warnings[] | select(.type=="plugin")'
```

### 3. Test Plugin Updates

```
1. Test in dev Jenkins first
2. Review release notes
3. Check compatibility
4. Have rollback plan
```

### 4. Lock Plugin Versions

**plugins.txt:**
```
git:4.11.3
docker-workflow:1.28
blueocean:1.25.3
```

### 5. Configuration as Code

```yaml
# jenkins.yaml
jenkins:
  systemMessage: "Jenkins configured via JCasC"
  
plugins:
  requiredGroups:
    - name: "Essential"
      plugins:
        - git
        - workflow-aggregator
        - docker-workflow
```

## Plugin Development

### Creating Custom Plugin

**Structure:**
```
my-plugin/
├── pom.xml
├── src/
│   └── main/
│       ├── java/
│       │   └── com/example/
│       │       └── MyPlugin.java
│       └── resources/
│           └── index.jelly
```

**pom.xml:**
```xml
<project>
    <parent>
        <groupId>org.jenkins-ci.plugins</groupId>
        <artifactId>plugin</artifactId>
        <version>4.40</version>
    </parent>
    
    <artifactId>my-plugin</artifactId>
    <version>1.0-SNAPSHOT</version>
    <packaging>hpi</packaging>
    
    <name>My Custom Plugin</name>
</project>
```

**Build:**
```bash
mvn clean package
# Creates target/my-plugin.hpi
```

**Install:**
```
Manage Jenkins → Manage Plugins → Advanced
Upload Plugin: my-plugin.hpi
```

## Troubleshooting Plugins

### Plugin Conflicts

**Issue:** Plugins not working after update

**Solution:**
```
Manage Jenkins → Manage Plugins → Installed
Check for warnings/conflicts
Downgrade conflicting plugins if needed
```

### Out of Memory

**Issue:** Jenkins crashes after plugin install

**Solution:**
```bash
# Increase Java heap
# Edit /etc/default/jenkins
JAVA_ARGS="-Xmx4096m -Xms2048m"

# Restart
sudo systemctl restart jenkins
```

### Plugin Not Loading

**Check logs:**
```bash
# Linux
tail -f /var/log/jenkins/jenkins.log

# Docker
docker logs -f jenkins
```

## Recommended Plugin Sets

### Minimal CI/CD
```
- git
- workflow-aggregator (Pipeline)
- docker-workflow
- credentials
- ssh-agents
```

### Full-Featured
```
Above + 
- blueocean
- github
- kubernetes
- sonarqube
- slack-notification
- email-ext
- junit
- jacoco
```

### Enterprise
```
Above +
- role-strategy
- ldap
- configuration-as-code
- prometheus
- job-dsl
- shared-libraries
```

## Summary

Essential Jenkins plugins enable:
- SCM integration (Git, GitHub, GitLab)
- Cloud platforms (AWS, Azure, K8s)
- Container support (Docker)
- Testing and quality (JUnit, SonarQube)
- Notifications (Slack, Email)
- Security (RBAC, Vault)
- Modern UI (Blue Ocean)

**Best Practices:**
- Install only needed plugins
- Keep plugins updated
- Test updates in dev first
- Use Configuration as Code
- Monitor plugin performance

---

**Previous:** [← Testing](10-testing.md) | **Next:** [Parameters & Artifacts →](12-parameters-artifacts.md)
