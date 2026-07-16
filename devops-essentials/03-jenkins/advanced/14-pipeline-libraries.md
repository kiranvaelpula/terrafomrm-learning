# Shared Pipeline Libraries

## Overview

Shared Pipeline Libraries enable code reuse across Jenkins pipelines. Instead of duplicating common logic in every Jenkinsfile, extract shared functions, steps, and entire pipeline templates into centralized libraries that any project can consume.

## Why Shared Libraries?

### Without Shared Libraries
```groovy
// Every project duplicates this code
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                script {
                    // 50 lines of common build logic
                    sh 'mvn clean package'
                    archiveArtifacts '**/*.jar'
                    // Docker build
                    // Notifications
                    // etc.
                }
            }
        }
    }
}
```

### With Shared Libraries
```groovy
@Library('my-shared-library') _

standardPipeline {
    language = 'java'
    deployTarget = 'kubernetes'
}
```

**Benefits:**
- ✅ DRY (Don't Repeat Yourself)
- ✅ Centralized updates
- ✅ Easier maintenance
- ✅ Consistent practices
- ✅ Versioned and tested
- ✅ Team collaboration

## Library Structure

### Standard Directory Layout

```
my-shared-library/
├── vars/                    # Global variables (steps)
│   ├── standardPipeline.groovy
│   ├── buildDocker.groovy
│   └── deployApp.groovy
├── src/                     # Shared classes
│   └── com/
│       └── example/
│           ├── BuildHelper.groovy
│           └── DeployHelper.groovy
├── resources/               # Non-Groovy files
│   ├── scripts/
│   │   └── deploy.sh
│   └── templates/
│       └── Dockerfile.template
└── test/                    # Unit tests
    └── groovy/
        └── StandardPipelineTest.groovy
```

### File Types

**1. vars/ - Global Variables**
- Accessible as global functions
- Simplest to use
- Great for pipeline steps

**2. src/ - Classes**
- Full Groovy classes
- Complex logic
- Testable

**3. resources/ - Non-code**
- Scripts, templates, config
- Loaded via libraryResource()

## Creating a Shared Library

### Step 1: Create Git Repository

```bash
git init my-shared-library
cd my-shared-library
mkdir -p vars src/com/example resources/scripts
```

### Step 2: Create vars/buildDocker.groovy

```groovy
// vars/buildDocker.groovy
def call(Map config) {
    // Default values
    def imageName = config.imageName ?: 'myapp'
    def imageTag = config.imageTag ?: env.BUILD_NUMBER
    def dockerRegistry = config.registry ?: 'docker.io'
    def dockerfile = config.dockerfile ?: 'Dockerfile'
    
    echo "Building Docker image: ${imageName}:${imageTag}"
    
    script {
        def image = docker.build(
            "${dockerRegistry}/${imageName}:${imageTag}",
            "-f ${dockerfile} ."
        )
        
        if (config.push) {
            docker.withRegistry("https://${dockerRegistry}", config.credentialsId) {
                image.push()
                image.push('latest')
            }
        }
        
        return image
    }
}
```

### Step 3: Create vars/standardPipeline.groovy

```groovy
// vars/standardPipeline.groovy
def call(Map config) {
    pipeline {
        agent any
        
        options {
            timestamps()
            buildDiscarder(logRotator(numToKeepStr: '10'))
            timeout(time: 1, unit: 'HOURS')
        }
        
        stages {
            stage('Checkout') {
                steps {
                    checkout scm
                }
            }
            
            stage('Build') {
                steps {
                    script {
                        if (config.language == 'java') {
                            sh 'mvn clean package'
                        } else if (config.language == 'nodejs') {
                            sh 'npm install && npm run build'
                        } else if (config.language == 'python') {
                            sh 'pip install -r requirements.txt'
                        }
                    }
                }
            }
            
            stage('Test') {
                steps {
                    script {
                        if (config.language == 'java') {
                            sh 'mvn test'
                        } else if (config.language == 'nodejs') {
                            sh 'npm test'
                        } else if (config.language == 'python') {
                            sh 'pytest'
                        }
                    }
                }
            }
            
            stage('Docker Build') {
                when {
                    expression { config.buildDocker }
                }
                steps {
                    script {
                        buildDocker(
                            imageName: config.imageName,
                            push: true,
                            credentialsId: 'docker-hub-creds'
                        )
                    }
                }
            }
            
            stage('Deploy') {
                when {
                    branch 'main'
                }
                steps {
                    script {
                        if (config.deployTarget == 'kubernetes') {
                            sh 'kubectl apply -f k8s/'
                        } else if (config.deployTarget == 'aws') {
                            sh 'aws deploy push'
                        }
                    }
                }
            }
        }
        
        post {
            success {
                script {
                    if (config.notifications?.slack) {
                        slackSend(
                            channel: config.notifications.slack,
                            color: 'good',
                            message: "Build succeeded: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
                        )
                    }
                }
            }
            failure {
                script {
                    if (config.notifications?.slack) {
                        slackSend(
                            channel: config.notifications.slack,
                            color: 'danger',
                            message: "Build failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
                        )
                    }
                }
            }
        }
    }
}
```

### Step 4: Create src/com/example/BuildHelper.groovy

```groovy
// src/com/example/BuildHelper.groovy
package com.example

class BuildHelper implements Serializable {
    def script
    
    BuildHelper(script) {
        this.script = script
    }
    
    def buildJavaApp(Map config = [:]) {
        def mvnArgs = config.mvnArgs ?: 'clean package'
        def skipTests = config.skipTests ?: false
        
        if (skipTests) {
            mvnArgs += ' -DskipTests'
        }
        
        script.sh "mvn ${mvnArgs}"
    }
    
    def buildNodeApp(Map config = [:]) {
        def buildCommand = config.buildCommand ?: 'npm run build'
        
        script.sh """
            npm ci
            ${buildCommand}
        """
    }
    
    def getVersion() {
        def version = script.sh(
            script: 'git describe --tags --always',
            returnStdout: true
        ).trim()
        
        return version
    }
}
```

### Step 5: Commit and Push

```bash
git add .
git commit -m "Initial shared library"
git push origin main
```

## Configuring Jenkins

### Global Library Configuration

**Navigate to:** Manage Jenkins → Configure System → Global Pipeline Libraries

**Configure:**
- **Name**: `my-shared-library`
- **Default version**: `main`
- **Retrieval method**: Modern SCM
- **Source**: Git
- **Project Repository**: `https://github.com/company/my-shared-library.git`
- **Credentials**: (if private repo)

**Load implicitly**: ☑️ (auto-load for all pipelines)

### Via Jenkinsfile (Dynamic)

```groovy
// Load specific version
@Library('my-shared-library@v1.2.0') _

// Load from branch
@Library('my-shared-library@develop') _

// Load multiple libraries
@Library(['library1@main', 'library2@v2.0']) _

// Import specific classes
@Library('my-shared-library') import com.example.BuildHelper
```

## Using Shared Libraries

### Example 1: Simple Step Usage

**vars/sayHello.groovy:**
```groovy
def call(String name = 'World') {
    echo "Hello, ${name}!"
}
```

**Jenkinsfile:**
```groovy
@Library('my-shared-library') _

pipeline {
    agent any
    stages {
        stage('Greet') {
            steps {
                sayHello('Jenkins')
            }
        }
    }
}
```

### Example 2: Complex Build Pipeline

**vars/javaBuildPipeline.groovy:**
```groovy
def call(Map config) {
    pipeline {
        agent any
        
        environment {
            MAVEN_OPTS = '-Xmx1024m'
        }
        
        stages {
            stage('Build') {
                steps {
                    sh "mvn clean package ${config.mvnArgs ?: ''}"
                }
            }
            
            stage('Test') {
                steps {
                    sh 'mvn test'
                    junit 'target/surefire-reports/*.xml'
                }
            }
            
            stage('Quality Gate') {
                steps {
                    script {
                        def qualityGate = waitForQualityGate()
                        if (qualityGate.status != 'OK') {
                            error "Quality gate failed: ${qualityGate.status}"
                        }
                    }
                }
            }
            
            stage('Archive') {
                steps {
                    archiveArtifacts artifacts: 'target/*.jar', fingerprint: true
                }
            }
        }
    }
}
```

**Jenkinsfile:**
```groovy
@Library('my-shared-library') _

javaBuildPipeline {
    mvnArgs = '-P production'
}
```

### Example 3: Using Classes

**Jenkinsfile:**
```groovy
@Library('my-shared-library') import com.example.BuildHelper

pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                script {
                    def builder = new BuildHelper(this)
                    builder.buildJavaApp(skipTests: false)
                    
                    def version = builder.getVersion()
                    echo "Building version: ${version}"
                }
            }
        }
    }
}
```

### Example 4: Loading Resources

**resources/scripts/deploy.sh:**
```bash
#!/bin/bash
echo "Deploying to $1"
kubectl apply -f k8s/ --namespace=$1
```

**vars/deployToK8s.groovy:**
```groovy
def call(String namespace) {
    def deployScript = libraryResource 'scripts/deploy.sh'
    writeFile file: 'deploy.sh', text: deployScript
    sh "chmod +x deploy.sh"
    sh "./deploy.sh ${namespace}"
}
```

**Jenkinsfile:**
```groovy
@Library('my-shared-library') _

pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                deployToK8s('production')
            }
        }
    }
}
```

## Advanced Patterns

### Pattern 1: Configurable Pipeline Template

**vars/microservicePipeline.groovy:**
```groovy
def call(Map config) {
    pipeline {
        agent any
        
        stages {
            stage('Checkout') {
                steps {
                    checkout scm
                }
            }
            
            stage('Build') {
                steps {
                    script {
                        // Custom build step if provided
                        if (config.buildStep) {
                            config.buildStep()
                        } else {
                            // Default build
                            sh 'make build'
                        }
                    }
                }
            }
            
            stage('Test') {
                parallel {
                    stage('Unit Tests') {
                        steps {
                            script {
                                if (config.unitTests) {
                                    config.unitTests()
                                }
                            }
                        }
                    }
                    stage('Integration Tests') {
                        steps {
                            script {
                                if (config.integrationTests) {
                                    config.integrationTests()
                                }
                            }
                        }
                    }
                }
            }
            
            stage('Docker') {
                steps {
                    script {
                        buildDocker(
                            imageName: config.serviceName,
                            push: env.BRANCH_NAME == 'main',
                            credentialsId: config.dockerCreds
                        )
                    }
                }
            }
            
            stage('Deploy') {
                when {
                    branch 'main'
                }
                steps {
                    script {
                        if (config.deployStep) {
                            config.deployStep()
                        }
                    }
                }
            }
        }
        
        post {
            always {
                script {
                    if (config.postAlways) {
                        config.postAlways()
                    }
                }
            }
        }
    }
}
```

**Usage:**
```groovy
@Library('my-shared-library') _

microservicePipeline {
    serviceName = 'auth-service'
    dockerCreds = 'docker-hub'
    
    buildStep = {
        sh 'npm install'
        sh 'npm run build'
    }
    
    unitTests = {
        sh 'npm run test:unit'
    }
    
    integrationTests = {
        sh 'npm run test:integration'
    }
    
    deployStep = {
        sh 'kubectl apply -f k8s/ -n production'
    }
    
    postAlways = {
        junit 'test-results/*.xml'
        cleanWs()
    }
}
```

### Pattern 2: Multi-Environment Deployment

**vars/multiEnvDeploy.groovy:**
```groovy
def call(Map config) {
    def environments = config.environments ?: ['dev', 'staging', 'prod']
    
    pipeline {
        agent any
        
        parameters {
            choice(
                name: 'DEPLOY_TO',
                choices: environments,
                description: 'Target environment'
            )
        }
        
        stages {
            stage('Build') {
                steps {
                    script {
                        config.build()
                    }
                }
            }
            
            stage('Deploy to Dev') {
                when {
                    expression { params.DEPLOY_TO == 'dev' }
                }
                steps {
                    script {
                        deployToEnvironment('dev', config)
                    }
                }
            }
            
            stage('Deploy to Staging') {
                when {
                    expression { params.DEPLOY_TO == 'staging' }
                }
                steps {
                    input 'Deploy to staging?'
                    script {
                        deployToEnvironment('staging', config)
                    }
                }
            }
            
            stage('Deploy to Prod') {
                when {
                    expression { params.DEPLOY_TO == 'prod' }
                }
                steps {
                    input 'Deploy to PRODUCTION?'
                    script {
                        deployToEnvironment('prod', config)
                    }
                }
            }
        }
    }
}

def deployToEnvironment(String env, Map config) {
    echo "Deploying to ${env}"
    
    withCredentials([string(
        credentialsId: "${env}-api-key",
        variable: 'API_KEY'
    )]) {
        config.deploy(env)
    }
}
```

### Pattern 3: Notification Helper

**vars/notifyBuild.groovy:**
```groovy
def call(String buildStatus = 'STARTED', Map config = [:]) {
    buildStatus = buildStatus ?: 'SUCCESS'
    
    def colorCode = [
        'STARTED': '#0000FF',
        'SUCCESS': '#00FF00',
        'FAILURE': '#FF0000',
        'UNSTABLE': '#FFFF00'
    ][buildStatus]
    
    def message = """
        *${buildStatus}*: Job ${env.JOB_NAME} [${env.BUILD_NUMBER}]
        Branch: ${env.BRANCH_NAME}
        Duration: ${currentBuild.durationString}
        ${env.BUILD_URL}
    """.stripIndent()
    
    // Slack
    if (config.slack) {
        slackSend(
            channel: config.slack.channel,
            color: colorCode,
            message: message
        )
    }
    
    // Email
    if (config.email) {
        emailext(
            subject: "${buildStatus}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: message,
            to: config.email.recipients
        )
    }
    
    // Teams
    if (config.teams) {
        office365ConnectorSend(
            webhookUrl: config.teams.webhook,
            message: message,
            color: colorCode
        )
    }
}
```

**Usage:**
```groovy
@Library('my-shared-library') _

pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                notifyBuild('STARTED', [
                    slack: [channel: '#builds'],
                    email: [recipients: 'team@example.com']
                ])
                
                sh 'make build'
            }
        }
    }
    
    post {
        success {
            notifyBuild('SUCCESS', [slack: [channel: '#builds']])
        }
        failure {
            notifyBuild('FAILURE', [
                slack: [channel: '#builds'],
                email: [recipients: 'team@example.com']
            ])
        }
    }
}
```

## Library Versioning

### Semantic Versioning

```bash
# Tag library versions
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0

git tag -a v1.1.0 -m "Added notification features"
git push origin v1.1.0
```

### Using Specific Versions

```groovy
// Use specific version
@Library('my-shared-library@v1.0.0') _

// Use latest from branch
@Library('my-shared-library@main') _

// Use commit SHA
@Library('my-shared-library@abc123') _
```

### Version Strategy

**Development:**
```groovy
@Library('my-shared-library@develop') _
```

**Staging:**
```groovy
@Library('my-shared-library@release/1.x') _
```

**Production:**
```groovy
@Library('my-shared-library@v1.2.3') _
```

## Testing Shared Libraries

### Unit Tests with Spock

**test/groovy/BuildHelperSpec.groovy:**
```groovy
import com.example.BuildHelper
import spock.lang.Specification

class BuildHelperSpec extends Specification {
    
    def script = Mock()
    def helper = new BuildHelper(script)
    
    def "should build Java app with default args"() {
        when:
        helper.buildJavaApp()
        
        then:
        1 * script.sh('mvn clean package')
    }
    
    def "should skip tests when requested"() {
        when:
        helper.buildJavaApp(skipTests: true)
        
        then:
        1 * script.sh('mvn clean package -DskipTests')
    }
    
    def "should get version from git"() {
        given:
        script.sh(_) >> 'v1.2.3'
        
        when:
        def version = helper.getVersion()
        
        then:
        version == 'v1.2.3'
    }
}
```

### Integration Tests

Create test Jenkinsfile that uses library and validate:

```groovy
// test/integration/Jenkinsfile
@Library('my-shared-library@testing') _

pipeline {
    agent any
    stages {
        stage('Test Library') {
            steps {
                script {
                    // Test each function
                    sayHello('Test')
                    
                    def builder = new com.example.BuildHelper(this)
                    assert builder.getVersion() != null
                }
            }
        }
    }
}
```

## Best Practices

### 1. Keep Libraries Simple

```groovy
// GOOD - Simple, focused function
def buildJava() {
    sh 'mvn clean package'
}

// BAD - Too complex, hard to maintain
def buildEverything(lang, test, deploy, notify) {
    // 200 lines of conditional logic
}
```

### 2. Use Parameters for Flexibility

```groovy
// GOOD
def buildDocker(Map config) {
    def imageName = config.imageName ?: 'default'
    def tag = config.tag ?: 'latest'
    // ...
}

// BAD
def buildDocker(imageName, tag, registry, push, cleanup) {
    // Too many required params
}
```

### 3. Version Your Libraries

```groovy
// GOOD - Specific version
@Library('my-lib@v2.1.0') _

// BAD - Always latest (unpredictable)
@Library('my-lib@main') _
```

### 4. Document Everything

```groovy
/**
 * Builds Docker image and optionally pushes to registry
 *
 * @param config Map with:
 *   - imageName: Name of Docker image (required)
 *   - tag: Image tag (default: BUILD_NUMBER)
 *   - push: Whether to push (default: false)
 *   - registry: Docker registry URL (default: docker.io)
 *   - credentialsId: Jenkins credentials for registry
 *
 * @return Docker image object
 *
 * Example:
 *   buildDocker(imageName: 'myapp', push: true)
 */
def call(Map config) {
    // Implementation
}
```

### 5. Handle Errors Gracefully

```groovy
def call(Map config) {
    try {
        // Main logic
        sh 'make build'
    } catch (Exception e) {
        echo "Build failed: ${e.message}"
        // Cleanup or fallback
        throw e  // Re-throw if should fail pipeline
    } finally {
        // Always cleanup
        cleanWs()
    }
}
```

### 6. Avoid Global State

```groovy
// GOOD - Pass data explicitly
def deploy(String version, String env) {
    sh "deploy --version=${version} --env=${env}"
}

// BAD - Rely on global variables
def deploy() {
    sh "deploy --version=${VERSION} --env=${ENV}"
}
```

## Common Patterns

### Pattern: Approval Gate

**vars/approvalGate.groovy:**
```groovy
def call(String environment, String approvers) {
    timeout(time: 24, unit: 'HOURS') {
        input(
            message: "Deploy to ${environment}?",
            submitter: approvers,
            parameters: [
                booleanParam(
                    name: 'CONFIRM',
                    defaultValue: false,
                    description: 'Confirm deployment'
                )
            ]
        )
    }
}
```

### Pattern: Retry with Backoff

**vars/retryWithBackoff.groovy:**
```groovy
def call(int maxRetries, Closure action) {
    int retryCount = 0
    while (retryCount < maxRetries) {
        try {
            action()
            return  // Success
        } catch (Exception e) {
            retryCount++
            if (retryCount >= maxRetries) {
                throw e
            }
            def waitTime = retryCount * 10  // Backoff
            echo "Retry ${retryCount}/${maxRetries} after ${waitTime}s"
            sleep waitTime
        }
    }
}
```

**Usage:**
```groovy
retryWithBackoff(3) {
    sh 'kubectl apply -f deployment.yaml'
}
```

## Troubleshooting

### Issue 1: Library Not Loading

**Symptoms:**
```
library not found: my-shared-library
```

**Solutions:**
1. Check library name matches configuration
2. Verify Git repository URL and credentials
3. Ensure branch/tag exists
4. Check Jenkins logs for detailed errors

### Issue 2: Class Not Found

**Symptoms:**
```
unable to resolve class com.example.BuildHelper
```

**Solutions:**
1. Verify class is in src/com/example/
2. Use @Grab for external dependencies
3. Import class explicitly:
   ```groovy
   @Library('lib') import com.example.BuildHelper
   ```

### Issue 3: Serialization Errors

**Symptoms:**
```
java.io.NotSerializableException
```

**Solutions:**
1. Implement Serializable in classes
2. Mark non-serializable fields as @NonCPS
3. Avoid complex objects in pipeline variables

## Real-World Example

**Complete microservices library:**

```groovy
// vars/microservicePipeline.groovy
@Library('my-shared-library') _

def call(Map config) {
    pipeline {
        agent {
            kubernetes {
                yaml libraryResource('pod-templates/build-pod.yaml')
            }
        }
        
        environment {
            SERVICE_NAME = config.serviceName
            DOCKER_REGISTRY = 'registry.company.com'
        }
        
        stages {
            stage('Init') {
                steps {
                    script {
                        notifyBuild('STARTED', config.notifications)
                    }
                }
            }
            
            stage('Build') {
                steps {
                    container('builder') {
                        script {
                            def builder = new com.example.BuildHelper(this)
                            builder.buildApp(config)
                        }
                    }
                }
            }
            
            stage('Test') {
                parallel {
                    stage('Unit') {
                        steps {
                            container('builder') {
                                runTests('unit', config)
                            }
                        }
                    }
                    stage('Integration') {
                        steps {
                            container('builder') {
                                runTests('integration', config)
                            }
                        }
                    }
                    stage('Security Scan') {
                        steps {
                            container('security') {
                                sh 'trivy scan .'
                            }
                        }
                    }
                }
            }
            
            stage('Docker Build & Push') {
                steps {
                    container('docker') {
                        script {
                            buildDocker(
                                imageName: config.serviceName,
                                push: true,
                                scan: true
                            )
                        }
                    }
                }
            }
            
            stage('Deploy Dev') {
                steps {
                    script {
                        deployToK8s('dev', config.serviceName)
                    }
                }
            }
            
            stage('Deploy Prod') {
                when {
                    branch 'main'
                }
                steps {
                    script {
                        approvalGate('production', 'release-managers')
                        deployToK8s('prod', config.serviceName)
                    }
                }
            }
        }
        
        post {
            success {
                notifyBuild('SUCCESS', config.notifications)
            }
            failure {
                notifyBuild('FAILURE', config.notifications)
            }
            always {
                cleanWs()
            }
        }
    }
}
```

**Usage in project:**

```groovy
@Library('microservices-library@v2.0.0') _

microservicePipeline {
    serviceName = 'payment-service'
    language = 'nodejs'
    
    notifications = [
        slack: [channel: '#deployments'],
        email: [recipients: 'team@company.com']
    ]
}
```

## Summary

Shared Pipeline Libraries enable:
- Code reuse across pipelines
- Centralized updates and maintenance
- Consistent practices across teams
- Versioned, testable pipeline code
- Simplified Jenkinsfiles

**Key concepts:**
- vars/ for global functions
- src/ for classes
- resources/ for non-code files
- Semantic versioning
- Testing and documentation

## Next Steps

- **Monitoring** → Track pipeline performance
- **Configuration as Code** → JCasC for Jenkins setup
- **Enterprise Patterns** → Scale Jenkins for large teams

---

**Previous:** [Distributed Builds](13-distributed-builds.md)  
**Next:** [Security](15-security.md)
