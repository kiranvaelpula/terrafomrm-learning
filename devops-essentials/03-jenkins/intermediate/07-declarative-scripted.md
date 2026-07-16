# Declarative vs Scripted Pipelines

## Overview

Jenkins offers two syntaxes for defining pipelines: **Declarative** (modern, structured) and **Scripted** (flexible, Groovy-based). Understanding both helps you choose the right approach for your needs.

## Quick Comparison

| Feature | Declarative | Scripted |
|---------|-------------|----------|
| **Syntax** | Structured DSL | Groovy code |
| **Learning Curve** | Easy | Moderate |
| **Flexibility** | Moderate | Very High |
| **Error Handling** | Built-in | Manual |
| **Recommended** | ✅ Yes (default) | Complex cases |
| **Validation** | Pre-execution | Runtime |
| **Code Reuse** | Limited | Extensive |

## Declarative Pipeline

### Structure

```groovy
pipeline {
    agent any
    
    options {
        // Pipeline options
    }
    
    parameters {
        // Build parameters
    }
    
    triggers {
        // Build triggers
    }
    
    environment {
        // Environment variables
    }
    
    stages {
        stage('Stage Name') {
            when {
                // Conditional execution
            }
            steps {
                // Build steps
            }
        }
    }
    
    post {
        // Post-build actions
    }
}
```

### Advantages

**1. Simpler Syntax**
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

**2. Built-in Directives**
```groovy
pipeline {
    agent any
    options {
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }
    stages {
        stage('Build') {
            steps {
                sh 'make'
            }
        }
    }
}
```

**3. Pre-execution Validation**
- Syntax checked before running
- Errors caught early
- Better IDE support

**4. Post Conditions**
```groovy
post {
    always { echo 'Always' }
    success { echo 'Success' }
    failure { echo 'Failed' }
    unstable { echo 'Unstable' }
    changed { echo 'Changed' }
}
```

### Limitations

**1. Less Flexible**
```groovy
// Can't dynamically generate stages easily
// Must use script block for complex logic
```

**2. Script Blocks Required for Complex Logic**
```groovy
stage('Complex') {
    steps {
        script {
            // Need script block for Groovy code
            def result = sh(returnStdout: true, script: 'command')
            if (result.contains('success')) {
                echo 'Success!'
            }
        }
    }
}
```

## Scripted Pipeline

### Structure

```groovy
node {
    stage('Stage Name') {
        // Groovy code
    }
}
```

### Advantages

**1. Maximum Flexibility**
```groovy
node {
    // Full Groovy programming
    def stages = ['Build', 'Test', 'Deploy']
    
    for (stage in stages) {
        stage(stage) {
            echo "Running ${stage}"
        }
    }
}
```

**2. Complex Logic**
```groovy
node {
    def result = sh(returnStdout: true, script: 'command')
    
    if (result.contains('error')) {
        currentBuild.result = 'FAILURE'
        error('Build failed')
    }
    
    try {
        stage('Risky Operation') {
            sh 'risky-command'
        }
    } catch (Exception e) {
        echo "Error: ${e.message}"
        currentBuild.result = 'UNSTABLE'
    }
}
```

**3. Dynamic Stage Generation**
```groovy
node {
    def environments = ['dev', 'staging', 'prod']
    
    for (env in environments) {
        stage("Deploy to ${env}") {
            sh "deploy.sh ${env}"
        }
    }
}
```

### Limitations

**1. More Complex**
- Requires Groovy knowledge
- More verbose
- Easier to make mistakes

**2. No Pre-validation**
- Errors found at runtime
- Harder to debug

**3. Manual Error Handling**
```groovy
node {
    try {
        stage('Build') {
            sh 'make'
        }
    } catch (Exception e) {
        currentBuild.result = 'FAILURE'
        throw e
    } finally {
        stage('Cleanup') {
            sh 'make clean'
        }
    }
}
```

## Side-by-Side Comparison

### Example 1: Basic Pipeline

**Declarative:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'npm install'
                sh 'npm run build'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
    }
}
```

**Scripted:**
```groovy
node {
    stage('Build') {
        sh 'npm install'
        sh 'npm run build'
    }
    
    stage('Test') {
        sh 'npm test'
    }
}
```

### Example 2: With Parameters

**Declarative:**
```groovy
pipeline {
    agent any
    
    parameters {
        string(name: 'ENVIRONMENT', defaultValue: 'dev')
        choice(name: 'ACTION', choices: ['build', 'deploy'])
    }
    
    stages {
        stage('Execute') {
            steps {
                echo "Environment: ${params.ENVIRONMENT}"
                echo "Action: ${params.ACTION}"
            }
        }
    }
}
```

**Scripted:**
```groovy
properties([
    parameters([
        string(name: 'ENVIRONMENT', defaultValue: 'dev'),
        choice(name: 'ACTION', choices: ['build', 'deploy'])
    ])
])

node {
    stage('Execute') {
        echo "Environment: ${params.ENVIRONMENT}"
        echo "Action: ${params.ACTION}"
    }
}
```

### Example 3: Conditional Execution

**Declarative:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Deploy') {
            when {
                branch 'main'
                environment name: 'DEPLOY', value: 'true'
            }
            steps {
                sh 'deploy.sh'
            }
        }
    }
}
```

**Scripted:**
```groovy
node {
    stage('Deploy') {
        if (env.BRANCH_NAME == 'main' && env.DEPLOY == 'true') {
            sh 'deploy.sh'
        }
    }
}
```

### Example 4: Parallel Execution

**Declarative:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Tests') {
            parallel {
                stage('Unit') {
                    steps {
                        sh 'npm run test:unit'
                    }
                }
                stage('Integration') {
                    steps {
                        sh 'npm run test:integration'
                    }
                }
            }
        }
    }
}
```

**Scripted:**
```groovy
node {
    stage('Tests') {
        parallel(
            'Unit': {
                sh 'npm run test:unit'
            },
            'Integration': {
                sh 'npm run test:integration'
            }
        )
    }
}
```

### Example 5: Try-Catch

**Declarative:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                script {
                    try {
                        sh 'npm run build'
                    } catch (Exception e) {
                        echo "Build failed: ${e.message}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
    }
}
```

**Scripted:**
```groovy
node {
    stage('Build') {
        try {
            sh 'npm run build'
        } catch (Exception e) {
            echo "Build failed: ${e.message}"
            currentBuild.result = 'UNSTABLE'
        }
    }
}
```

## When to Use Each

### Use Declarative When:

✅ Starting with Jenkins pipelines  
✅ Standard CI/CD workflows  
✅ Team has mixed skill levels  
✅ Want pre-execution validation  
✅ Need clear, maintainable code  
✅ Following best practices

**Example Use Cases:**
- Standard web application builds
- Microservices deployment
- Simple test automation
- Typical CD workflows

### Use Scripted When:

✅ Complex conditional logic needed  
✅ Dynamic stage generation  
✅ Advanced Groovy features required  
✅ Complex error handling  
✅ Need maximum flexibility  
✅ Team comfortable with Groovy

**Example Use Cases:**
- Dynamic multi-environment deployments
- Complex approval workflows
- Advanced build orchestration
- Legacy system integration

## Mixing Both Approaches

You can use `script` blocks within Declarative pipelines:

```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                // Declarative steps
                sh 'npm install'
                
                // Scripted logic
                script {
                    def version = sh(
                        returnStdout: true,
                        script: 'git describe --tags'
                    ).trim()
                    
                    env.APP_VERSION = version
                    
                    if (version.contains('rc')) {
                        echo 'Release candidate detected'
                        env.DEPLOY_ENV = 'staging'
                    } else {
                        env.DEPLOY_ENV = 'production'
                    }
                }
                
                // Back to declarative
                echo "Deploying version ${env.APP_VERSION} to ${env.DEPLOY_ENV}"
            }
        }
    }
}
```

## Real-World Examples

### Example 1: Declarative with Script Blocks

```groovy
pipeline {
    agent any
    
    environment {
        APP_NAME = 'myapp'
    }
    
    stages {
        stage('Determine Version') {
            steps {
                script {
                    if (env.BRANCH_NAME == 'main') {
                        env.VERSION = "1.0.${BUILD_NUMBER}"
                    } else {
                        env.VERSION = "0.0.${BUILD_NUMBER}-${env.BRANCH_NAME}"
                    }
                }
                echo "Building version: ${env.VERSION}"
            }
        }
        
        stage('Build') {
            steps {
                sh "docker build -t ${APP_NAME}:${VERSION} ."
            }
        }
        
        stage('Test') {
            steps {
                script {
                    try {
                        sh "docker run --rm ${APP_NAME}:${VERSION} npm test"
                    } catch (Exception e) {
                        currentBuild.result = 'UNSTABLE'
                        echo "Tests failed but continuing"
                    }
                }
            }
        }
    }
}
```

### Example 2: Scripted with Functions

```groovy
def buildApp() {
    sh 'npm install'
    sh 'npm run build'
}

def testApp() {
    sh 'npm test'
}

def deployApp(environment) {
    sh "deploy.sh ${environment}"
}

node {
    try {
        stage('Checkout') {
            checkout scm
        }
        
        stage('Build') {
            buildApp()
        }
        
        stage('Test') {
            testApp()
        }
        
        if (env.BRANCH_NAME == 'main') {
            stage('Deploy') {
                deployApp('production')
            }
        }
    } catch (Exception e) {
        currentBuild.result = 'FAILURE'
        throw e
    } finally {
        stage('Cleanup') {
            cleanWs()
        }
    }
}
```

## Migration Guide

### Converting Scripted to Declarative

**Before (Scripted):**
```groovy
node {
    stage('Build') {
        sh 'npm install'
        sh 'npm run build'
    }
    
    stage('Test') {
        sh 'npm test'
    }
}
```

**After (Declarative):**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'npm install'
                sh 'npm run build'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
    }
}
```

### Handling Complex Logic

**Scripted:**
```groovy
node {
    def environments = ['dev', 'staging', 'prod']
    for (env in environments) {
        stage("Deploy ${env}") {
            sh "deploy.sh ${env}"
        }
    }
}
```

**Declarative:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Deploy All') {
            steps {
                script {
                    def environments = ['dev', 'staging', 'prod']
                    for (env in environments) {
                        stage("Deploy ${env}") {
                            sh "deploy.sh ${env}"
                        }
                    }
                }
            }
        }
    }
}
```

## Best Practices

### 1. Prefer Declarative

Start with Declarative and use `script` blocks only when needed:

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'make'  // Declarative
                
                script {   // Scripted when needed
                    if (fileExists('custom.config')) {
                        sh 'make custom'
                    }
                }
            }
        }
    }
}
```

### 2. Keep Script Blocks Small

❌ **Bad:**
```groovy
steps {
    script {
        // 100 lines of Groovy code
    }
}
```

✅ **Good:**
```groovy
steps {
    script {
        def version = getVersion()
    }
    echo "Version: ${version}"
}
```

### 3. Use Shared Libraries

Extract complex logic to shared libraries:

```groovy
@Library('my-shared-library') _

pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                buildApplication()  // From shared library
            }
        }
    }
}
```

### 4. Document Script Blocks

```groovy
steps {
    script {
        // Calculate deployment environment based on branch
        // main -> production, develop -> staging, others -> dev
        env.DEPLOY_ENV = calculateEnvironment(env.BRANCH_NAME)
    }
}
```

## Summary

**Declarative Pipeline:**
- Easier to learn and maintain
- Structured and consistent
- Pre-execution validation
- Recommended for most use cases

**Scripted Pipeline:**
- Maximum flexibility
- Full Groovy power
- Better for complex scenarios
- Requires more expertise

**Recommendation:** Start with Declarative and use `script` blocks for complex logic when needed.

---

**Previous:** [← Pipeline as Code](06-pipeline-as-code.md) | **Next:** [Git Integration →](08-git-integration.md)
