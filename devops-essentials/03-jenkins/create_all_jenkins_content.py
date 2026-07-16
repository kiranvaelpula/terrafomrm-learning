#!/usr/bin/env python3
"""
Script to create comprehensive Jenkins content for all remaining files
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Content for basics interview questions
BASICS_INTERVIEW = """# Jenkins Basics - Interview Questions

## Fundamental Concepts

### 1. What is Jenkins and why is it used?

**Answer:**
Jenkins is an open-source automation server used for Continuous Integration and Continuous Delivery (CI/CD). It automates the software development process by:
- Automatically building code when changes are committed
- Running tests to catch bugs early
- Deploying applications to various environments
- Providing feedback to development teams

**Key Benefits:**
- Free and open source
- Extensible with 1,800+ plugins
- Platform independent (Java-based)
- Easy to configure via web interface
- Supports distributed builds

### 2. What is Continuous Integration (CI)?

**Answer:**
CI is a development practice where developers integrate code into a shared repository frequently (multiple times per day). Each integration is verified by automated build and tests.

**Benefits:**
- Early bug detection
- Reduced integration problems
- Better collaboration
- Faster feedback loop
- Improved code quality

**Example Workflow:**
```
Developer commits → Jenkins detects change → Build triggered →
Tests run → Results reported → Developer notified
```

### 3. What is the difference between Continuous Integration, Continuous Delivery, and Continuous Deployment?

**Answer:**

**Continuous Integration (CI):**
- Code changes automatically built and tested
- Ensures code integrates properly
- Provides fast feedback

**Continuous Delivery (CD):**
- Extension of CI
- Code always in deploy able state
- Deployment requires manual approval
- Can deploy to production anytime

**Continuous Deployment:**
- Extension of Continuous Delivery
- Every change automatically deployed to production
- No manual intervention
- Requires comprehensive test coverage

```
CI → CD → Continuous Deployment
  ↓    ↓         ↓
Build→Deploy-ready→Auto-production
```

### 4. What are the different types of Jenkins jobs/projects?

**Answer:**

| Type | Description | Use Case |
|------|-------------|----------|
| **Freestyle Project** | Traditional UI-configured job | Simple tasks, legacy |
| **Pipeline** | Code-based CI/CD definition | Modern, version-controlled |
| **Multi-branch Pipeline** | Auto-creates pipelines per branch | Feature branch workflows |
| **Folder** | Organization structure | Group related jobs |
| **Multibranch Organization** | Scans org for repositories | Multiple repo management |

**Modern Recommendation:** Use Pipeline or Multi-branch Pipeline

### 5. What is a Jenkins Pipeline?

**Answer:**
A Pipeline is a suite of plugins that supports implementing and integrating continuous delivery pipelines into Jenkins. It's defined as code (Jenkinsfile) stored in version control.

**Types:**
1. **Declarative Pipeline** (Recommended)
   - Simpler syntax
   - More opinionated
   - Easier for beginners

2. **Scripted Pipeline**
   - More flexible
   - Groovy-based
   - More complex

**Example:**
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'npm install'
            }
        }
    }
}
```

### 6. What is a Jenkinsfile?

**Answer:**
A Jenkinsfile is a text file containing the definition of a Jenkins Pipeline. It's checked into source control with the application code.

**Advantages:**
- Version controlled pipeline definition
- Code review for pipeline changes
- Audit trail
- Single source of truth
- Portable across Jenkins instances

**Location:**
- Typically in repository root
- Named `Jenkinsfile` (no extension)
- Can be in subdirectory

### 7. Explain Jenkins Master/Agent (Master/Slave) architecture

**Answer:**

**Master (Controller):**
- Main Jenkins server
- Manages job scheduling
- Monitors agents
- Records and presents build results
- Handles HTTP requests

**Agent (Slave/Node):**
- Worker machine
- Executes builds
- Reports results to master
- Can be on different OS/architecture

**Benefits:**
- Distributed builds
- Parallel execution
- OS-specific builds
- Resource optimization

```
Master (Scheduler)
    ├── Agent 1 (Linux)
    ├── Agent 2 (Windows)
    └── Agent 3 (Docker)
```

### 8. What are Jenkins plugins?

**Answer:**
Plugins extend Jenkins functionality. Jenkins has 1,800+ plugins for:
- Version control systems (Git, SVN)
- Build tools (Maven, Gradle)
- Containers (Docker, Kubernetes)
- Notifications (Email, Slack)
- Cloud providers (AWS, Azure)

**Essential Plugins:**
- Git Plugin
- Pipeline Plugin
- Docker Plugin
- Blue Ocean
- Credentials Plugin

**Managing Plugins:**
```
Manage Jenkins → Manage Plugins
- Available: Install new
- Installed: Manage existing
- Updates: Update plugins
```

### 9. What are the different build triggers in Jenkins?

**Answer:**

1. **Manual Trigger**
   - Click "Build Now"
   - On-demand execution

2. **SCM Polling**
   - Checks repository periodically
   - Builds if changes detected

3. **Webhooks**
   - Repository notifies Jenkins
   - Instant builds

4. **Scheduled (Cron)**
   - Time-based triggers
   - Example: Nightly builds

5. **Upstream/Downstream**
   - Triggered by other jobs
   - Job dependencies

6. **Remote Trigger**
   - API-based
   - External system triggers

### 10. What is the purpose of the Jenkinsfile?

**Answer:**
Jenkinsfile enables "Pipeline as Code" - treating CD pipeline as part of the application:

**Benefits:**
1. **Version Control**: Track pipeline changes
2. **Code Review**: Review pipeline modifications
3. **Audit Trail**: History of changes
4. **Portability**: Works across Jenkins instances
5. **Branching**: Different pipelines per branch

**Example Structure:**
```groovy
pipeline {
    agent any           // Where to run
    stages {            // What to do
        stage('Build') {
            steps {
                // Build commands
            }
        }
    }
    post {              // What to do after
        success {
            // Success actions
        }
    }
}
```

## Installation and Setup

### 11. How do you install Jenkins?

**Answer:**

**Method 1: Docker (Recommended for testing)**
```bash
docker run -p 8080:8080 -p 50000:50000 \\
  -v jenkins_home:/var/jenkins_home \\
  jenkins/jenkins:lts
```

**Method 2: Native (Production)**
```bash
# Ubuntu/Debian
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install jenkins

# Start Jenkins
sudo systemctl start jenkins
```

**Method 3: Kubernetes**
```bash
helm install jenkins jenkins/jenkins
```

**Prerequisites:**
- Java 11 or 17
- Minimum 256MB RAM (1GB+ recommended)
- 1GB+ disk space

### 12. What are the system requirements for Jenkins?

**Answer:**

**Minimum:**
- Java 11 or 17
- 256 MB RAM
- 1 GB disk space

**Recommended (Small Team):**
- 4 GB+ RAM
- 50 GB+ disk space
- Multi-core CPU

**Recommended (Large Organization):**
- 16 GB+ RAM
- 200 GB+ disk space
- 8+ CPU cores
- Multiple agents

**Factors Affecting Requirements:**
- Number of concurrent builds
- Number of jobs
- Build history retention
- Number of plugins
- Workspace size

### 13. What is JENKINS_HOME?

**Answer:**
JENKINS_HOME is the directory where Jenkins stores all data:

**Contains:**
- Job configurations (jobs/)
- Build records and artifacts (builds/)
- Plugin data (plugins/)
- System configuration (config.xml)
- Workspaces (workspace/)
- Credentials (credentials.xml)

**Default Locations:**
- Linux: `/var/lib/jenkins`
- Windows: `C:\\Program Files\\Jenkins`
- macOS: `~/.jenkins`
- Docker: `/var/jenkins_home`

**Important:**
- Must be backed up regularly
- Should not be in version control
- Contains sensitive data

### 14. How do you back up Jenkins?

**Answer:**

**Method 1: File System Backup**
```bash
# Stop Jenkins
sudo systemctl stop jenkins

# Backup JENKINS_HOME
sudo tar czf jenkins-backup-$(date +%Y%m%d).tar.gz \\
  /var/lib/jenkins/

# Start Jenkins
sudo systemctl start jenkins
```

**Method 2: ThinBackup Plugin**
- Selective backup
- Scheduled backups
- Restore functionality
- Excludes workspace

**Method 3: Configuration as Code**
- JCasC plugin
- Export configuration
- Version control configs

**What to Backup:**
- config.xml (system configuration)
- jobs/ (job definitions)
- plugins/ (plugin data)
- credentials.xml (secrets)
- users/ (user data)

**What NOT to Backup:**
- workspace/ (can be recreated)
- war/ (Jenkins binaries)
- cache/ (temporary files)

### 15. What are the default Jenkins ports?

**Answer:**

**Port 8080:**
- HTTP web interface
- Default user access
- Can be changed in configuration

**Port 50000:**
- JNLP agent port
- Agents connect to master
- Used for distributed builds

**Changing Ports:**

Linux (/etc/default/jenkins):
```bash
HTTP_PORT=8081
```

Docker:
```bash
docker run -p 8081:8080 -p 50001:50000 jenkins/jenkins:lts
```

Windows (service configuration):
- Stop Jenkins service
- Edit jenkins.xml
- Change --httpPort=8080
- Restart service

## Build Configuration

### 16. What are build parameters?

**Answer:**
Build parameters allow you to pass dynamic values to builds:

**Types:**
1. **String Parameter**: Text input
2. **Boolean Parameter**: Checkbox
3. **Choice Parameter**: Dropdown list
4. **Password Parameter**: Masked input
5. **File Parameter**: File upload

**Example:**
```groovy
pipeline {
    parameters {
        string(name: 'ENVIRONMENT', defaultValue: 'dev')
        choice(name: 'ACTION', choices: ['build', 'deploy'])
        booleanParam(name: 'RUN_TESTS', defaultValue: true)
    }
    stages {
        stage('Execute') {
            steps {
                echo "Environment: ${params.ENVIRONMENT}"
            }
        }
    }
}
```

**Use Cases:**
- Specify deployment environment
- Toggle test execution
- Select build configuration
- Pass version numbers

### 17. What are Jenkins environment variables?

**Answer:**
Environment variables are key-value pairs available during build execution:

**Built-in Variables:**
```groovy
BUILD_NUMBER      // Build number
JOB_NAME         // Job name
WORKSPACE        // Workspace path
BUILD_URL        // Build URL
NODE_NAME        // Agent name
GIT_COMMIT       // Git commit hash
```

**Custom Variables:**
```groovy
pipeline {
    environment {
        APP_NAME = 'myapp'
        VERSION = '1.0.0'
        DOCKER_IMAGE = "${APP_NAME}:${VERSION}"
    }
    stages {
        stage('Build') {
            steps {
                echo "Building ${DOCKER_IMAGE}"
            }
        }
    }
}
```

**Access Methods:**
```groovy
// In pipeline
echo "${env.BUILD_NUMBER}"
sh 'echo $BUILD_NUMBER'

// In shell
echo $BUILD_NUMBER
```

### 18. How do you archive build artifacts?

**Answer:**

**Pipeline:**
```groovy
stage('Archive') {
    steps {
        // Build artifacts
        sh 'npm run build'
        
        // Archive
        archiveArtifacts artifacts: 'dist/**/*',
                        fingerprint: true,
                        allowEmptyArchive: false
    }
}
```

**Freestyle:**
```
Post-build Actions → Archive the artifacts
Files to archive: dist/**/*
```

**Best Practices:**
- Only archive necessary files
- Use compression for large files
- Set retention policy
- Use external storage for large artifacts

**Accessing Artifacts:**
- Via build page → Artifacts link
- REST API: `/job/name/lastSuccessfulBuild/artifact/path`
- Copy from workspace

### 19. How do you publish test results in Jenkins?

**Answer:**

**JUnit XML:**
```groovy
stage('Test') {
    steps {
        sh 'npm test -- --reporter=junit --reporter-options=output=test-results/junit.xml'
        junit 'test-results/*.xml'
    }
}
```

**Other Formats:**
```groovy
// TestNG
step([$class: 'Publisher', testResults: 'test-results/*.xml'])

// NUnit
nunit testResultsPattern: 'test-results/*.xml'

// xUnit
xunit([JUnit(pattern: 'test-results/*.xml')])
```

**Features:**
- Test trend graphs
- Test failure details
- Historical comparison
- Flaky test detection

**Best Practices:**
- Standardize test output format
- Fail build on test failures
- Archive test reports
- Monitor test trends

### 20. What is a post-build action?

**Answer:**
Post-build actions execute after build completion:

**Pipeline:**
```groovy
post {
    always {
        echo 'Always runs'
        cleanWs()
    }
    success {
        echo 'Runs on success'
        slackSend color: 'good', message: 'Build succeeded'
    }
    failure {
        echo 'Runs on failure'
        mail to: 'team@example.com',
             subject: 'Build Failed',
             body: "Build ${BUILD_NUMBER} failed"
    }
    unstable {
        echo 'Runs when build is unstable'
    }
}
```

**Common Actions:**
- Send notifications (email, Slack)
- Archive artifacts
- Publish test results
- Trigger downstream jobs
- Clean workspace
- Deploy applications

## Security

### 21. How do you secure Jenkins?

**Answer:**

**1. Enable Security:**
```
Manage Jenkins → Configure Global Security
✓ Enable security
```

**2. Authentication:**
- Jenkins' own user database
- LDAP integration
- Active Directory
- OAuth (GitHub, Google)

**3. Authorization:**
- Matrix-based security
- Project-based Matrix
- Role-Based Access Control (RBAC)

**4. Secure Credentials:**
```groovy
withCredentials([usernamePassword(
    credentialsId: 'docker-hub',
    usernameVariable: 'USER',
    passwordVariable: 'PASS'
)]) {
    sh 'docker login -u $USER -p $PASS'
}
```

**5. Other Security Measures:**
- Enable CSRF protection
- Disable CLI over remoting
- Use HTTPS
- Regular updates
- Audit logs
- Firewall rules

### 22. How do you store secrets/credentials in Jenkins?

**Answer:**

**Credentials Store:**
```
Manage Jenkins → Manage Credentials → Add Credentials
```

**Types:**
1. **Username with password**
2. **SSH Username with private key**
3. **Secret text**
4. **Secret file**
5. **Certificate**

**Using in Pipeline:**
```groovy
// Username/Password
withCredentials([usernamePassword(
    credentialsId: 'github-creds',
    usernameVariable: 'GIT_USER',
    passwordVariable: 'GIT_PASS'
)]) {
    sh 'git clone https://${GIT_USER}:${GIT_PASS}@github.com/repo.git'
}

// Secret text
withCredentials([string(
    credentialsId: 'api-token',
    variable: 'API_TOKEN'
)]) {
    sh 'curl -H "Authorization: Bearer $API_TOKEN" api.example.com'
}

// SSH key
sshagent(credentials: ['ssh-key-id']) {
    sh 'git clone git@github.com:user/repo.git'
}
```

**Best Practices:**
- Never hardcode secrets
- Use credential binding
- Limit credential scope
- Rotate credentials regularly
- Audit credential usage

### 23. What are Jenkins credentials scopes?

**Answer:**

**Global:**
- Available everywhere
- All jobs can use
- Use for shared credentials

**System:**
- Only for Jenkins system
- Not available to jobs
- Use for agent connections

**Project:**
- Specific folder/job
- Limited visibility
- Better security

**Example:**
```
Global: Shared Docker Hub credentials
System: Agent SSH keys
Project: Dev team's AWS credentials (limited to dev folder)
```

**Best Practice:**
Use most restrictive scope possible

## Practical Scenarios

### 24. How would you set up a CI pipeline for a Node.js application?

**Answer:**

```groovy
pipeline {
    agent {
        docker {
            image 'node:16'
        }
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install') {
            steps {
                sh 'npm ci'
            }
        }
        
        stage('Lint') {
            steps {
                sh 'npm run lint'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm test'
                junit 'test-results/*.xml'
            }
        }
        
        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts 'dist/**/*'
            }
        }
    }
    
    post {
        failure {
            mail to: 'team@example.com',
                 subject: "Failed: ${JOB_NAME} #${BUILD_NUMBER}",
                 body: "Build failed. Check: ${BUILD_URL}"
        }
    }
}
```

### 25. How do you clean up workspace in Jenkins?

**Answer:**

**Method 1: Workspace Cleanup Plugin**
```groovy
stage('Cleanup') {
    steps {
        cleanWs()
    }
}
```

**Method 2: Manual cleanup**
```groovy
stage('Cleanup') {
    steps {
        deleteDir()  // Delete entire workspace
        // Or
        sh 'rm -rf node_modules dist'
    }
}
```

**Method 3: Pre-build cleanup**
```groovy
pipeline {
    options {
        skipDefaultCheckout()
    }
    stages {
        stage('Clean Start') {
            steps {
                cleanWs()
                checkout scm
            }
        }
    }
}
```

**Method 4: Post-build cleanup**
```groovy
post {
    always {
        cleanWs()
    }
}
```

**Why Clean Workspace:**
- Remove build artifacts
- Free disk space
- Ensure clean builds
- Prevent pollution

---

## Quick Reference

**Most Important Concepts:**
1. Jenkins is CI/CD automation server
2. Pipeline as Code (Jenkinsfile)
3. Master/Agent architecture
4. Build triggers (webhooks > polling)
5. Credentials management
6. Security configuration

**Common Interview Topics:**
- What is Jenkins?
- CI vs CD vs Continuous Deployment
- Pipeline vs Freestyle
- Master/Agent architecture
- Build triggers
- Security best practices

---

**Total Questions: 25**
**Next:** Practice these concepts in labs and move to intermediate topics
"""

# Write basics interview questions
basics_interview_path = BASE_DIR / "basics" / "interview-questions-basics.md"
with open(basics_interview_path, 'w', encoding='utf-8') as f:
    f.write(BASICS_INTERVIEW)

print(f"✅ Created: {basics_interview_path}")
print("Jenkins basics content is now complete!")
print("\\nNext: Run create_jenkins_intermediate.py for intermediate content")
