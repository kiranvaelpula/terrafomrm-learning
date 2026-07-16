# Pipeline as Code with Jenkinsfile

## Overview

Pipeline as Code treats your CI/CD pipeline as software - versioned, reviewed, and evolved alongside your application code. The Jenkinsfile is the heart of this approach, defining your entire build, test, and deployment process.

## Why Pipeline as Code?

### Traditional Approach (Freestyle Jobs)
- Configuration stored in Jenkins UI
- Hard to version control
- Difficult to replicate
- No code review for pipeline changes
- Manual recreation if Jenkins crashes

### Pipeline as Code Benefits
- ✅ Version controlled with application
- ✅ Code review for pipeline changes
- ✅ Audit trail of modifications
- ✅ Portable across Jenkins instances
- ✅ Supports complex workflows
- ✅ Enables GitOps practices

## Jenkinsfile Basics

### Location
```
project-root/
├── Jenkinsfile          # Default name
├── src/
├── tests/
└── README.md
```

### Basic Structure

```groovy
pipeline {
    agent any                    // Where to run
    
    stages {                     // What to do
        stage('Build') {
            steps {
                // Build commands
            }
        }
    }
    
    post {                       // What to do after
        always {
            // Cleanup, notifications
        }
    }
}
```

## Pipeline Syntax Types

Jenkins supports two syntaxes:

| Feature | Declarative | Scripted |
|---------|-------------|----------|
| **Syntax** | Predefined structure | Groovy code |
| **Learning Curve** | Easy | Moderate |
| **Flexibility** | Limited | Very flexible |
| **Recommended** | ✅ Yes (modern) | For complex cases |

**Use Declarative unless you have specific needs requiring Scripted.**

## Declarative Pipeline Structure

### Complete Example

```groovy
pipeline {
    // 1. Agent - where to run
    agent {
        docker {
            image 'node:16'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }
    
    // 2. Options - pipeline configuration
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
    }
    
    // 3. Triggers - when to run
    triggers {
        pollSCM('H/15 * * * *')
        cron('H 2 * * *')
    }
    
    // 4. Parameters - input values
    parameters {
        string(name: 'ENVIRONMENT', defaultValue: 'dev')
        choice(name: 'ACTION', choices: ['build', 'deploy'])
        booleanParam(name: 'RUN_TESTS', defaultValue: true)
    }
    
    // 5. Environment - variables
    environment {
        APP_NAME = 'myapp'
        VERSION = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = 'docker.io'
        CREDS = credentials('docker-hub-credentials')
    }
    
    // 6. Stages - pipeline steps
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                sh 'npm install'
                sh 'npm run build'
            }
        }
        
        stage('Test') {
            when {
                expression { params.RUN_TESTS == true }
            }
            steps {
                sh 'npm test'
                junit 'test-results/*.xml'
            }
        }
        
        stage('Docker Build') {
            steps {
                script {
                    docker.build("${APP_NAME}:${VERSION}")
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
                expression { params.ACTION == 'deploy' }
            }
            steps {
                sh "kubectl set image deployment/${APP_NAME} ${APP_NAME}=${APP_NAME}:${VERSION}"
            }
        }
    }
    
    // 7. Post - after stages complete
    post {
        always {
            cleanWs()
        }
        success {
            slackSend color: 'good', message: "Build ${BUILD_NUMBER} succeeded"
        }
        failure {
            slackSend color: 'danger', message: "Build ${BUILD_NUMBER} failed"
            emailext subject: "Build Failed: ${JOB_NAME}",
                     body: "Build ${BUILD_NUMBER} failed. Check ${BUILD_URL}",
                     to: 'team@example.com'
        }
    }
}
```

## Agent Configuration

### Types of Agents

#### 1. Any Available Agent
```groovy
agent any  // Use any available agent
```

#### 2. Label-based Agent
```groovy
agent {
    label 'linux && docker'  // Agent with specific labels
}
```

#### 3. Docker Agent
```groovy
agent {
    docker {
        image 'maven:3.8.6-openjdk-11'
        args '-v $HOME/.m2:/root/.m2'
        label 'docker-host'
    }
}
```

#### 4. Dockerfile Agent
```groovy
agent {
    dockerfile {
        filename 'Dockerfile.build'
        dir 'docker'
        additionalBuildArgs '--build-arg version=1.0'
    }
}
```

#### 5. Kubernetes Agent
```groovy
agent {
    kubernetes {
        yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: maven
    image: maven:3.8.6
    command: ['cat']
    tty: true
        '''
    }
}
```

#### 6. Stage-Specific Agent
```groovy
pipeline {
    agent none  // No default agent
    
    stages {
        stage('Build') {
            agent {
                docker 'node:16'
            }
            steps {
                sh 'npm install && npm run build'
            }
        }
        
        stage('Test') {
            agent {
                docker 'node:16-alpine'
            }
            steps {
                sh 'npm test'
            }
        }
    }
}
```

## Environment Variables

### Types of Variables

#### 1. Built-in Variables
```groovy
stage('Info') {
    steps {
        echo "Build Number: ${BUILD_NUMBER}"
        echo "Job Name: ${JOB_NAME}"
        echo "Workspace: ${WORKSPACE}"
        echo "Build URL: ${BUILD_URL}"
        echo "Branch: ${BRANCH_NAME}"
        echo "Git Commit: ${GIT_COMMIT}"
    }
}
```

#### 2. Custom Variables
```groovy
environment {
    APP_NAME = 'myapp'
    VERSION = "1.0.${BUILD_NUMBER}"
    DEPLOY_TO = 'production'
}
```

#### 3. Credentials as Variables
```groovy
environment {
    // Username/Password
    DOCKER_CREDS = credentials('docker-credentials-id')
    // DOCKER_CREDS_USR and DOCKER_CREDS_PSW created
    
    // Secret Text
    API_TOKEN = credentials('api-token-id')
    
    // SSH Key
    SSH_KEY = credentials('ssh-key-id')
}

stages {
    stage('Use Credentials') {
        steps {
            sh 'docker login -u $DOCKER_CREDS_USR -p $DOCKER_CREDS_PSW'
            sh 'curl -H "Authorization: Bearer $API_TOKEN" api.example.com'
        }
    }
}
```

#### 4. Dynamic Variables
```groovy
stage('Dynamic') {
    steps {
        script {
            env.GIT_TAG = sh(
                script: 'git describe --tags --always',
                returnStdout: true
            ).trim()
            
            echo "Git Tag: ${env.GIT_TAG}"
        }
    }
}
```

## Parameters

### Parameter Types

```groovy
parameters {
    // String input
    string(
        name: 'ENVIRONMENT',
        defaultValue: 'dev',
        description: 'Target environment'
    )
    
    // Text area
    text(
        name: 'DESCRIPTION',
        defaultValue: 'Build description',
        description: 'Build notes'
    )
    
    // Boolean checkbox
    booleanParam(
        name: 'RUN_TESTS',
        defaultValue: true,
        description: 'Run tests?'
    )
    
    // Choice dropdown
    choice(
        name: 'DEPLOY_ENV',
        choices: ['dev', 'staging', 'production'],
        description: 'Deployment environment'
    )
    
    // Password (masked)
    password(
        name: 'SECRET_KEY',
        defaultValue: '',
        description: 'Secret key for deployment'
    )
    
    // File upload
    file(
        name: 'CONFIG_FILE',
        description: 'Configuration file to use'
    )
}

stages {
    stage('Use Parameters') {
        steps {
            echo "Environment: ${params.ENVIRONMENT}"
            echo "Deploy to: ${params.DEPLOY_ENV}"
            echo "Run tests: ${params.RUN_TESTS}"
        }
    }
}
```

## Conditional Execution

### When Directive

```groovy
stage('Deploy to Production') {
    when {
        // Multiple conditions (all must be true)
        allOf {
            branch 'main'
            environment name: 'DEPLOY_ENV', value: 'production'
            expression { params.APPROVED == true }
        }
    }
    steps {
        echo 'Deploying to production...'
    }
}

stage('Deploy to Staging') {
    when {
        // Any condition can be true
        anyOf {
            branch 'develop'
            branch 'staging'
        }
    }
    steps {
        echo 'Deploying to staging...'
    }
}

stage('Skip on Main') {
    when {
        not {
            branch 'main'
        }
    }
    steps {
        echo 'Running on non-main branch'
    }
}
```

### Common When Conditions

```groovy
when {
    branch 'main'                           // Specific branch
    branch pattern: 'feature/.*', comparator: 'REGEXP'  // Regex
    
    environment name: 'ENV', value: 'prod'  // Environment variable
    
    expression {                            // Groovy expression
        params.DEPLOY == true
    }
    
    changelog '.*\\[deploy\\].*'            // Commit message contains
    
    changeset 'src/**/*.js'                 // Files changed
    
    buildingTag()                           // Building a tag
    
    tag pattern: 'v\\d+\\.\\d+\\.\\d+', comparator: 'REGEXP'  // Tag pattern
}
```

## Parallel Execution

### Parallel Stages

```groovy
stage('Tests') {
    parallel {
        stage('Unit Tests') {
            steps {
                sh 'npm run test:unit'
            }
        }
        
        stage('Integration Tests') {
            steps {
                sh 'npm run test:integration'
            }
        }
        
        stage('E2E Tests') {
            agent {
                docker 'cypress/base:16'
            }
            steps {
                sh 'npm run test:e2e'
            }
        }
        
        stage('Security Scan') {
            steps {
                sh 'npm audit'
            }
        }
    }
}
```

### Parallel with Fail Fast

```groovy
options {
    parallelsAlwaysFailFast()  // Stop all if one fails
}

stage('Parallel Tests') {
    failFast true  // Stage-level fail fast
    parallel {
        // Stages here
    }
}
```

## Script Blocks

When you need Groovy code within declarative pipeline:

```groovy
stage('Complex Logic') {
    steps {
        script {
            // Conditional logic
            if (env.BRANCH_NAME == 'main') {
                env.DEPLOY_ENV = 'production'
            } else {
                env.DEPLOY_ENV = 'staging'
            }
            
            // Loops
            def environments = ['dev', 'staging', 'prod']
            for (env_name in environments) {
                echo "Deploying to ${env_name}"
            }
            
            // Try-catch
            try {
                sh 'risky-command'
            } catch (Exception e) {
                echo "Command failed: ${e.message}"
                currentBuild.result = 'UNSTABLE'
            }
            
            // Custom functions
            def version = getVersion()
            echo "Version: ${version}"
        }
    }
}

// Define functions outside pipeline
def getVersion() {
    return sh(
        script: 'git describe --tags --always',
        returnStdout: true
    ).trim()
}
```

## Post Actions

### Post Blocks

```groovy
post {
    // Always run
    always {
        junit '**/test-results/*.xml'
        cleanWs()
    }
    
    // Only on success
    success {
        archiveArtifacts 'dist/**/*'
        slackSend color: 'good', message: 'Build succeeded!'
    }
    
    // Only on failure
    failure {
        emailext subject: "Build Failed: ${JOB_NAME} #${BUILD_NUMBER}",
                 body: "Check console output at ${BUILD_URL}",
                 to: 'team@example.com'
    }
    
    // When build is unstable
    unstable {
        echo 'Build is unstable'
    }
    
    // When status changed
    changed {
        echo 'Build status changed'
    }
    
    // When status fixed
    fixed {
        echo 'Build was broken, now fixed'
    }
    
    // When status regression
    regression {
        echo 'Build was working, now broken'
    }
    
    // When aborted
    aborted {
        echo 'Build was aborted'
    }
    
    // Manual cleanup
    cleanup {
        echo 'Cleanup regardless of status'
    }
}
```

## Real-World Examples

### Example 1: Node.js Application

```groovy
pipeline {
    agent {
        docker {
            image 'node:16'
        }
    }
    
    environment {
        npm_config_cache = 'npm-cache'
    }
    
    stages {
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
                sh 'npm test -- --coverage'
                publishHTML([
                    reportDir: 'coverage',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report'
                ])
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
}
```

### Example 2: Java Maven Project

```groovy
pipeline {
    agent {
        docker {
            image 'maven:3.8.6-openjdk-11'
            args '-v $HOME/.m2:/root/.m2'
        }
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }
        
        stage('Test') {
            steps {
                sh 'mvn test'
                junit '**/target/surefire-reports/*.xml'
            }
        }
        
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
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'mvn deploy'
            }
        }
    }
}
```

### Example 3: Multi-Stage Docker Build

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "myorg/myapp"
        DOCKER_TAG = "${BUILD_NUMBER}"
        REGISTRY = credentials('docker-registry')
    }
    
    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }
        
        stage('Test Image') {
            steps {
                script {
                    dockerImage.inside {
                        sh 'npm test'
                    }
                }
            }
        }
        
        stage('Push Image') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-credentials') {
                        dockerImage.push("${DOCKER_TAG}")
                        dockerImage.push("latest")
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                sh """
                    kubectl set image deployment/myapp \\
                        myapp=${DOCKER_IMAGE}:${DOCKER_TAG}
                """
            }
        }
    }
    
    post {
        always {
            sh "docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true"
        }
    }
}
```

## Best Practices

### 1. Keep Jenkinsfile Simple
❌ **Bad:**
```groovy
// 500 lines of complex Groovy code
```

✅ **Good:**
```groovy
// Call shared libraries or external scripts
@Library('my-shared-library') _
buildApp()
```

### 2. Use Declarative Over Scripted
❌ **Bad:**
```groovy
node {
    stage('Build') {
        // Scripted syntax
    }
}
```

✅ **Good:**
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            // Declarative syntax
        }
    }
}
```

### 3. Fail Fast
```groovy
options {
    timeout(time: 30, unit: 'MINUTES')
    parallelsAlwaysFailFast()
}
```

### 4. Clean Workspace
```groovy
post {
    always {
        cleanWs()
    }
}
```

### 5. Use Credentials Properly
```groovy
environment {
    CREDS = credentials('credential-id')
}
// Never echo credentials!
```

## Troubleshooting

### Common Issues

**Issue: Pipeline not triggering**
```groovy
// Add triggers
triggers {
    pollSCM('H/15 * * * *')
}
```

**Issue: Workspace pollution**
```groovy
options {
    skipDefaultCheckout()
}
stages {
    stage('Clean Checkout') {
        steps {
            cleanWs()
            checkout scm
        }
    }
}
```

**Issue: Build timeout**
```groovy
options {
    timeout(time: 1, unit: 'HOURS')
}
```

## Summary

Pipeline as Code with Jenkinsfile:
- Treats pipeline as software
- Version controlled and reviewable
- Supports complex workflows
- Portable and reproducible
- Declarative syntax recommended
- Extensive configuration options

**Key takeaways:**
- Store Jenkinsfile in repository root
- Use declarative syntax for simplicity
- Leverage environment variables
- Implement proper error handling
- Clean up resources in post blocks

---

**Previous:** [← Build Triggers](../basics/05-build-triggers.md) | **Next:** [Declarative vs Scripted →](07-declarative-scripted.md)
