# Jenkins Intermediate - Interview Questions

## Pipeline as Code

### Q1: What is Pipeline as Code and why is it important?

**Answer:**
Pipeline as Code stores CI/CD pipelines in version control alongside application code.

**Benefits:**
- Version control for pipeline changes
- Code review for pipeline modifications  
- Audit trail and disaster recovery
- Portability across Jenkins instances
- Team collaboration on pipelines

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
    }
}
```

### Q2: Declarative vs Scripted - when to use each?

**Answer:**

**Declarative** (recommended):
- Structured, easy to learn
- Built-in validation
- Best practices enforced

**Scripted**:
- Full Groovy flexibility
- Complex conditional logic
- Legacy pipeline support

```groovy
// Declarative
pipeline {
    agent any
    stages {
        stage('Build') {
            steps { sh 'make' }
        }
    }
}

// Scripted
node {
    stage('Build') {
        sh 'make'
    }
}
```

### Q3: How do you handle secrets in pipelines?

**Answer:**

Use credentials binding:

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-creds',
                        usernameVariable: 'AWS_KEY',
                        passwordVariable: 'AWS_SECRET'
                    )
                ]) {
                    sh 'aws deploy'
                }
            }
        }
    }
}
```

**Best practices:**
- Store secrets in Jenkins Credentials
- Use credential binding plugins
- Never hardcode in Jenkinsfile
- Use external vaults (HashiCorp Vault)
- Mask sensitive output

### Q4: Explain agent configuration options

**Answer:**

```groovy
// Any available agent
agent any

// Specific label
agent { label 'linux' }

// Docker agent
agent {
    docker {
        image 'node:16'
        args '-v /var/run/docker.sock:/var/run/docker.sock'
    }
}

// Kubernetes agent
agent {
    kubernetes {
        yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: maven
    image: maven:3.8
'''
    }
}

// None (define per stage)
agent none
```

### Q5: How do you implement parallel stages?

**Answer:**

```groovy
pipeline {
    agent any
    stages {
        stage('Parallel Tests') {
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
                    steps {
                        sh 'npm run test:e2e'
                    }
                }
            }
        }
    }
}
```

**Use cases:**
- Run tests concurrently
- Multi-platform builds
- Independent deployments
- Faster pipeline execution

## Git Integration

### Q6: How do you configure GitHub webhooks?

**Answer:**

**Steps:**
1. Install GitHub plugin
2. Configure webhook in GitHub repo
3. Use SCM polling or webhook trigger

```groovy
pipeline {
    agent any
    triggers {
        githubPush()  // Triggered by webhook
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
    }
}
```

**Webhook URL:** `http://jenkins.example.com/github-webhook/`

### Q7: How do you build pull requests automatically?

**Answer:**

Use GitHub Branch Source Plugin:

```groovy
pipeline {
    agent any
    stages {
        stage('PR Validation') {
            when {
                changeRequest()
            }
            steps {
                sh 'npm test'
                sh 'npm run lint'
            }
        }
        stage('Merge Build') {
            when {
                branch 'main'
            }
            steps {
                sh 'npm run build'
            }
        }
    }
}
```

### Q8: How do you implement branch strategies?

**Answer:**

```groovy
pipeline {
    agent any
    stages {
        stage('Determine Environment') {
            steps {
                script {
                    env.DEPLOY_ENV = 'dev'
                    if (env.BRANCH_NAME == 'staging') {
                        env.DEPLOY_ENV = 'staging'
                    } else if (env.BRANCH_NAME == 'main') {
                        env.DEPLOY_ENV = 'prod'
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                sh "deploy to ${env.DEPLOY_ENV}"
            }
        }
    }
}
```

## Docker Integration

### Q9: How do you use Docker agents in pipelines?

**Answer:**

```groovy
pipeline {
    agent {
        docker {
            image 'node:16-alpine'
            args '-v $HOME/.npm:/root/.npm'
        }
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

**Benefits:**
- Clean build environment
- Consistent tooling
- No server configuration
- Easy version management

### Q10: How do you build and push Docker images?

**Answer:**

```groovy
pipeline {
    agent any
    environment {
        DOCKER_REGISTRY = 'docker.io'
        IMAGE_NAME = 'myapp'
    }
    stages {
        stage('Build Image') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}:${BUILD_NUMBER}")
                }
            }
        }
        stage('Push Image') {
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-creds') {
                        docker.image("${IMAGE_NAME}:${BUILD_NUMBER}").push()
                        docker.image("${IMAGE_NAME}:${BUILD_NUMBER}").push('latest')
                    }
                }
            }
        }
    }
}
```

### Q11: Explain Docker-in-Docker vs Docker socket mounting

**Answer:**

**Docker Socket Mounting** (recommended):
```groovy
agent {
    docker {
        image 'docker:latest'
        args '-v /var/run/docker.sock:/var/run/docker.sock'
    }
}
```

**Pros:**
- Simpler setup
- Shares host Docker daemon
- Better performance

**Docker-in-Docker:**
```dockerfile
FROM docker:dind
```

**Pros:**
- Complete isolation
- Independent Docker daemon

**Cons:**
- Complex setup
- Security implications
- Performance overhead

## Testing

### Q12: How do you integrate test reporting?

**Answer:**

```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
    }
    post {
        always {
            junit 'target/surefire-reports/*.xml'
            
            publishHTML([
                reportDir: 'target/site/jacoco',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])
        }
    }
}
```

### Q13: How do you implement quality gates?

**Answer:**

```groovy
pipeline {
    agent any
    stages {
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'mvn sonar:sonar'
                }
            }
        }
        stage('Quality Gate') {
            steps {
                timeout(time: 1, unit: 'HOURS') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }
}
```

## Parameters and Artifacts

### Q14: What parameter types are available?

**Answer:**

```groovy
pipeline {
    agent any
    parameters {
        string(name: 'VERSION', defaultValue: '1.0.0')
        choice(name: 'ENV', choices: ['dev', 'staging', 'prod'])
        booleanParam(name: 'RUN_TESTS', defaultValue: true)
        password(name: 'API_KEY', defaultValue: '')
        text(name: 'CONFIG', defaultValue: '')
        file(name: 'UPLOAD')
    }
    stages {
        stage('Use Params') {
            steps {
                echo "Version: ${params.VERSION}"
                echo "Environment: ${params.ENV}"
            }
        }
    }
}
```

### Q15: How do you manage artifacts between jobs?

**Answer:**

**Archive artifacts:**
```groovy
archiveArtifacts(
    artifacts: 'target/*.jar',
    fingerprint: true
)
```

**Copy artifacts:**
```groovy
copyArtifacts(
    projectName: 'build-job',
    filter: '**/*.jar',
    selector: lastSuccessful()
)
```

**Stash/Unstash within pipeline:**
```groovy
stash name: 'build', includes: 'target/**'
unstash 'build'
```

## Plugins

### Q16: What are essential Jenkins plugins?

**Answer:**

**Core Plugins:**
- Pipeline: Pipeline as Code support
- Git: Git SCM integration
- Docker: Docker integration
- Credentials: Secrets management
- Blue Ocean: Modern UI

**Testing:**
- JUnit: Test reporting
- Cobertura/JaCoCo: Coverage
- HTML Publisher: Custom reports

**Notifications:**
- Email Extension: Email notifications
- Slack: Slack integration
- JIRA: Issue tracking

### Q17: How do you troubleshoot plugin issues?

**Answer:**

**Steps:**
1. Check plugin compatibility
2. Review Jenkins logs
3. Update plugins
4. Check for conflicts

```groovy
// List installed plugins
Jenkins.instance.pluginManager.plugins.each {
    println "${it.shortName}: ${it.version}"
}

// Check for updates
Jenkins.instance.pluginManager.plugins.findAll {
    it.hasUpdate()
}
```

## Advanced Topics

### Q18: How do you implement retry logic?

**Answer:**

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                retry(3) {
                    sh 'kubectl apply -f deployment.yaml'
                }
            }
        }
    }
}
```

### Q19: How do you handle timeouts?

**Answer:**

```groovy
pipeline {
    agent any
    options {
        timeout(time: 1, unit: 'HOURS')
    }
    stages {
        stage('Long Running') {
            steps {
                timeout(time: 30, unit: 'MINUTES') {
                    sh './long-script.sh'
                }
            }
        }
    }
}
```

### Q20: Explain post actions

**Answer:**

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
    }
    post {
        always {
            echo 'Always runs'
            cleanWs()
        }
        success {
            echo 'Only on success'
            slackSend message: 'Build succeeded'
        }
        failure {
            echo 'Only on failure'
            mail to: 'team@example.com', subject: 'Build failed'
        }
        unstable {
            echo 'Build unstable'
        }
        changed {
            echo 'Build status changed'
        }
    }
}
```

## Scenario-Based Questions

### Q21: Design a multi-environment deployment pipeline

**Answer:**

```groovy
pipeline {
    agent any
    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'])
    }
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
        stage('Deploy to Dev') {
            when {
                expression { params.ENVIRONMENT == 'dev' }
            }
            steps {
                sh 'deploy-dev.sh'
            }
        }
        stage('Deploy to Staging') {
            when {
                expression { params.ENVIRONMENT == 'staging' }
            }
            steps {
                input 'Deploy to staging?'
                sh 'deploy-staging.sh'
            }
        }
        stage('Deploy to Prod') {
            when {
                expression { params.ENVIRONMENT == 'prod' }
            }
            steps {
                input 'Deploy to production?'
                sh 'deploy-prod.sh'
            }
        }
    }
}
```

### Q22: Implement blue-green deployment

**Answer:**

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy Green') {
            steps {
                sh 'kubectl apply -f green-deployment.yaml'
                sh 'kubectl wait --for=condition=available deployment/green'
            }
        }
        stage('Smoke Test') {
            steps {
                sh 'curl http://green-service/health'
            }
        }
        stage('Switch Traffic') {
            steps {
                input 'Switch to green?'
                sh 'kubectl patch service app -p '{"spec":{"selector":{"version":"green"}}}''
            }
        }
        stage('Cleanup Blue') {
            steps {
                sh 'kubectl delete deployment blue'
            }
        }
    }
}
```

### Q23: Handle microservices build pipeline

**Answer:**

```groovy
pipeline {
    agent none
    stages {
        stage('Build Services') {
            parallel {
                stage('Auth Service') {
                    agent { label 'docker' }
                    steps {
                        dir('auth-service') {
                            sh 'docker build -t auth:${BUILD_NUMBER} .'
                            sh 'docker push auth:${BUILD_NUMBER}'
                        }
                    }
                }
                stage('API Service') {
                    agent { label 'docker' }
                    steps {
                        dir('api-service') {
                            sh 'docker build -t api:${BUILD_NUMBER} .'
                            sh 'docker push api:${BUILD_NUMBER}'
                        }
                    }
                }
                stage('Web Service') {
                    agent { label 'docker' }
                    steps {
                        dir('web-service') {
                            sh 'docker build -t web:${BUILD_NUMBER} .'
                            sh 'docker push web:${BUILD_NUMBER}'
                        }
                    }
                }
            }
        }
    }
}
```

## Best Practices

### Q24: What are Jenkins pipeline best practices?

**Answer:**

1. **Use Declarative Pipeline** - Easier to maintain
2. **Version Control Jenkinsfile** - Store with code
3. **Use Shared Libraries** - Reuse common code
4. **Implement Proper Error Handling** - Retry, timeout
5. **Clean Workspace** - Avoid stale data
6. **Use Docker Agents** - Consistent environment
7. **Implement Quality Gates** - Ensure code quality
8. **Secure Credentials** - Never hardcode secrets
9. **Parallel Execution** - Faster pipelines
10. **Comprehensive Logging** - Easy debugging

### Q25: How do you optimize pipeline performance?

**Answer:**

**Strategies:**
```groovy
pipeline {
    agent any
    options {
        // Skip checkout for faster restarts
        skipDefaultCheckout()
        // Limit build history
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // Parallel stages
        parallelsAlwaysFailFast()
    }
    stages {
        stage('Parallel Build') {
            parallel {
                stage('Build') { steps { sh 'make' } }
                stage('Test') { steps { sh 'test' } }
            }
        }
    }
}
```

**Performance tips:**
- Use parallel stages
- Implement caching
- Use Docker agents efficiently
- Clean workspace selectively
- Optimize Git checkout

## Summary

Key concepts covered:
- Pipeline as Code fundamentals
- Git and Docker integration
- Testing and quality gates
- Parameters and artifacts
- Best practices and optimization

**Next:** Practice labs for hands-on experience

---

**Previous:** [Parameters & Artifacts](12-parameters-artifacts.md)  
**Next:** [Distributed Builds](../advanced/13-distributed-builds.md)
