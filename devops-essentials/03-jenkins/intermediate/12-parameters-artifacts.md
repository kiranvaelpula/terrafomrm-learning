# Advanced Parameters and Artifact Management

## Overview

Parameters and artifacts are fundamental to building flexible, reusable pipelines. Parameters make pipelines configurable, while artifacts preserve build outputs for deployment, testing, and auditing.

## Build Parameters

### Parameter Types

Jenkins supports multiple parameter types for different use cases:

```groovy
pipeline {
    agent any
    
    parameters {
        // 1. String - Simple text input
        string(
            name: 'BRANCH_NAME',
            defaultValue: 'main',
            description: 'Git branch to build'
        )
        
        // 2. Text - Multi-line input
        text(
            name: 'DEPLOYMENT_CONFIG',
            defaultValue: 'key: value\nport: 8080',
            description: 'YAML configuration'
        )
        
        // 3. Boolean - True/false toggle
        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Execute test suite?'
        )
        
        // 4. Choice - Dropdown selection
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging', 'prod'],
            description: 'Target environment'
        )
        
        // 5. Password - Secure input (masked)
        password(
            name: 'API_KEY',
            defaultValue: '',
            description: 'API key for deployment'
        )
        
        // 6. File - Upload file
        file(
            name: 'CONFIG_FILE',
            description: 'Upload configuration file'
        )
    }
    
    stages {
        stage('Use Parameters') {
            steps {
                echo "Branch: ${params.BRANCH_NAME}"
                echo "Environment: ${params.ENVIRONMENT}"
                echo "Run tests: ${params.RUN_TESTS}"
                
                script {
                    if (params.RUN_TESTS) {
                        echo "Running tests..."
                    }
                }
            }
        }
    }
}
```

### Dynamic Parameters with Active Choices

Install **Active Choices Plugin** for dynamic parameters:

```groovy
@Library('my-shared-library') _

pipeline {
    agent any
    
    parameters {
        // Depends on Active Choices Plugin
        activeChoice(
            choiceType: 'PT_SINGLE_SELECT',
            name: 'AWS_REGION',
            script: groovyScript(
                script: '''
                    return ['us-east-1', 'us-west-2', 'eu-west-1']
                ''',
                fallbackScript: "return ['us-east-1']"
            )
        )
        
        // Reactive parameter - depends on AWS_REGION
        reactiveChoice(
            choiceType: 'PT_CHECKBOX',
            name: 'AVAILABILITY_ZONES',
            referencedParameters: 'AWS_REGION',
            script: groovyScript(
                script: '''
                    if (AWS_REGION == 'us-east-1') {
                        return ['us-east-1a', 'us-east-1b', 'us-east-1c']
                    } else if (AWS_REGION == 'us-west-2') {
                        return ['us-west-2a', 'us-west-2b']
                    }
                    return []
                '''
            )
        )
    }
    
    stages {
        stage('Deploy') {
            steps {
                echo "Deploying to ${params.AWS_REGION}"
                echo "AZs: ${params.AVAILABILITY_ZONES}"
            }
        }
    }
}
```

## Parameter Validation

### Basic Validation

```groovy
pipeline {
    agent any
    
    parameters {
        string(name: 'VERSION', defaultValue: '1.0.0')
    }
    
    stages {
        stage('Validate') {
            steps {
                script {
                    // Validate semantic version
                    if (!params.VERSION.matches(/^\d+\.\d+\.\d+$/)) {
                        error "Invalid version format: ${params.VERSION}"
                    }
                    
                    echo "Valid version: ${params.VERSION}"
                }
            }
        }
    }
}
```

### Advanced Validation with Shared Functions

```groovy
// vars/paramValidation.groovy in shared library
def validateEmail(String email) {
    def pattern = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$/
    if (!email.matches(pattern)) {
        error "Invalid email format: ${email}"
    }
}

def validateUrl(String url) {
    try {
        new URL(url).toURI()
    } catch (Exception e) {
        error "Invalid URL: ${url}"
    }
}

// In Jenkinsfile
@Library('shared-lib') _

pipeline {
    agent any
    
    parameters {
        string(name: 'NOTIF_EMAIL', defaultValue: 'team@example.com')
        string(name: 'WEBHOOK_URL', defaultValue: 'https://hooks.slack.com/services/xxx')
    }
    
    stages {
        stage('Validate') {
            steps {
                script {
                    paramValidation.validateEmail(params.NOTIF_EMAIL)
                    paramValidation.validateUrl(params.WEBHOOK_URL)
                }
            }
        }
    }
}
```

## Artifact Management

### Archiving Artifacts

```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh '''
                    mkdir -p dist
                    echo "Application v1.0" > dist/app.jar
                    echo "<html>Build Report</html>" > dist/report.html
                '''
            }
        }
        
        stage('Archive') {
            steps {
                // Archive build outputs
                archiveArtifacts(
                    artifacts: 'dist/**/*',
                    fingerprint: true,
                    onlyIfSuccessful: true,
                    allowEmptyArchive: false
                )
                
                // Archive specific patterns
                archiveArtifacts(
                    artifacts: '**/*.jar,**/*.war,**/dist/**',
                    excludes: '**/*-test.jar',
                    fingerprint: true
                )
            }
        }
    }
}
```

### Artifact Patterns

```groovy
// Common artifact patterns
archiveArtifacts artifacts: '**/*.jar'           // All JARs
archiveArtifacts artifacts: 'target/**/*.jar'    // Maven output
archiveArtifacts artifacts: 'build/libs/*.jar'   // Gradle output
archiveArtifacts artifacts: 'dist/**/*'          // Distribution folder
archiveArtifacts artifacts: '**/reports/**'      // Test reports

// Multiple patterns with exclusions
archiveArtifacts(
    artifacts: 'build/**/*.jar, dist/**/*.war',
    excludes: '**/test*.jar, **/*-snapshot.jar'
)
```

## Artifact Retrieval

### Copy Artifacts from Another Job

Install **Copy Artifact Plugin**:

```groovy
pipeline {
    agent any
    
    stages {
        stage('Copy Artifacts') {
            steps {
                // Copy from last successful build
                copyArtifacts(
                    projectName: 'build-job',
                    filter: '**/*.jar',
                    target: 'artifacts/',
                    selector: lastSuccessful()
                )
                
                // Copy from specific build
                copyArtifacts(
                    projectName: 'build-job',
                    filter: 'dist/**/*',
                    selector: specific('42')
                )
                
                // Copy with build parameters
                copyArtifacts(
                    projectName: 'build-job',
                    filter: '**/*.war',
                    parameters: 'ENVIRONMENT=prod,VERSION=2.0'
                )
            }
        }
    }
}
```

### Stash and Unstash (Within Pipeline)

```groovy
pipeline {
    agent none
    
    stages {
        stage('Build') {
            agent { label 'build-node' }
            steps {
                sh 'mvn clean package'
                
                // Stash artifacts for later stages
                stash(
                    name: 'build-artifacts',
                    includes: 'target/**/*.jar,target/**/*.war'
                )
                
                // Stash with exclusions
                stash(
                    name: 'test-results',
                    includes: 'target/surefire-reports/**',
                    excludes: '**/*.log'
                )
            }
        }
        
        stage('Test') {
            agent { label 'test-node' }
            steps {
                // Retrieve stashed artifacts
                unstash 'build-artifacts'
                
                sh 'java -jar target/app.jar --test'
            }
        }
        
        stage('Deploy') {
            agent { label 'deploy-node' }
            steps {
                unstash 'build-artifacts'
                
                sh 'kubectl apply -f k8s/'
            }
        }
    }
}
```

## Artifact Storage Strategies

### Jenkins Master Storage

**Default behavior** - stored on Jenkins master:

```groovy
// Configure retention
pipeline {
    options {
        // Keep artifacts for 30 days or last 10 builds
        buildDiscarder(logRotator(
            artifactDaysToKeepStr: '30',
            artifactNumToKeepStr: '10'
        ))
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'make build'
                archiveArtifacts 'build/**'
            }
        }
    }
}
```

**Pros:**
- Simple setup
- Fast access
- No external dependencies

**Cons:**
- Limited disk space
- No redundancy
- Scalability issues

### Artifactory Integration

Install **Artifactory Plugin**:

```groovy
pipeline {
    agent any
    
    environment {
        ARTIFACTORY_URL = 'https://artifactory.company.com'
        ARTIFACTORY_REPO = 'libs-release-local'
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        
        stage('Upload to Artifactory') {
            steps {
                script {
                    def server = Artifactory.server('artifactory-server')
                    def uploadSpec = """{
                        "files": [{
                            "pattern": "target/*.jar",
                            "target": "${ARTIFACTORY_REPO}/com/example/app/${env.BUILD_NUMBER}/"
                        }]
                    }"""
                    
                    server.upload(uploadSpec)
                    
                    // Publish build info
                    def buildInfo = Artifactory.newBuildInfo()
                    server.publishBuildInfo(buildInfo)
                }
            }
        }
        
        stage('Download from Artifactory') {
            steps {
                script {
                    def server = Artifactory.server('artifactory-server')
                    def downloadSpec = """{
                        "files": [{
                            "pattern": "${ARTIFACTORY_REPO}/com/example/app/latest/*.jar",
                            "target": "artifacts/"
                        }]
                    }"""
                    
                    server.download(downloadSpec)
                }
            }
        }
    }
}
```

### Nexus Repository Integration

```groovy
pipeline {
    agent any
    
    environment {
        NEXUS_URL = 'https://nexus.company.com'
        NEXUS_REPO = 'maven-releases'
        NEXUS_CREDS = credentials('nexus-credentials')
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        
        stage('Upload to Nexus') {
            steps {
                script {
                    // Using Nexus Artifact Uploader Plugin
                    nexusArtifactUploader(
                        nexusVersion: 'nexus3',
                        protocol: 'https',
                        nexusUrl: "${NEXUS_URL}",
                        groupId: 'com.example',
                        version: "${env.BUILD_NUMBER}",
                        repository: "${NEXUS_REPO}",
                        credentialsId: 'nexus-credentials',
                        artifacts: [
                            [
                                artifactId: 'myapp',
                                classifier: '',
                                file: 'target/myapp.jar',
                                type: 'jar'
                            ],
                            [
                                artifactId: 'myapp',
                                classifier: 'sources',
                                file: 'target/myapp-sources.jar',
                                type: 'jar'
                            ]
                        ]
                    )
                }
            }
        }
    }
}
```

### Amazon S3 Storage

Install **S3 Plugin**:

```groovy
pipeline {
    agent any
    
    environment {
        AWS_REGION = 'us-east-1'
        S3_BUCKET = 'my-build-artifacts'
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }
        
        stage('Upload to S3') {
            steps {
                withAWS(credentials: 'aws-credentials', region: "${AWS_REGION}") {
                    // Upload directory
                    s3Upload(
                        bucket: "${S3_BUCKET}",
                        path: "builds/${env.JOB_NAME}/${env.BUILD_NUMBER}/",
                        includePathPattern: '**/*',
                        workingDir: 'dist'
                    )
                    
                    // Upload specific files
                    s3Upload(
                        bucket: "${S3_BUCKET}",
                        path: "releases/",
                        file: 'dist/app.tar.gz'
                    )
                }
            }
        }
        
        stage('Download from S3') {
            steps {
                withAWS(credentials: 'aws-credentials', region: "${AWS_REGION}") {
                    s3Download(
                        bucket: "${S3_BUCKET}",
                        path: "builds/${env.JOB_NAME}/${env.BUILD_NUMBER}/",
                        file: 'downloaded-artifacts/'
                    )
                }
            }
        }
    }
}
```

## Advanced Artifact Patterns

### Multi-Module Projects

```groovy
pipeline {
    agent any
    
    stages {
        stage('Build All Modules') {
            steps {
                sh '''
                    cd backend && mvn clean package
                    cd ../frontend && npm run build
                    cd ../api && go build
                '''
            }
        }
        
        stage('Archive by Module') {
            parallel {
                stage('Backend Artifacts') {
                    steps {
                        dir('backend') {
                            archiveArtifacts(
                                artifacts: 'target/*.jar',
                                fingerprint: true
                            )
                        }
                    }
                }
                
                stage('Frontend Artifacts') {
                    steps {
                        dir('frontend') {
                            archiveArtifacts(
                                artifacts: 'dist/**/*',
                                fingerprint: true
                            )
                        }
                    }
                }
                
                stage('API Artifacts') {
                    steps {
                        dir('api') {
                            archiveArtifacts(
                                artifacts: 'api-server',
                                fingerprint: true
                            )
                        }
                    }
                }
            }
        }
    }
}
```

### Conditional Artifact Archiving

```groovy
pipeline {
    agent any
    
    parameters {
        choice(name: 'BUILD_TYPE', choices: ['dev', 'staging', 'prod'])
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
        
        stage('Archive') {
            steps {
                script {
                    // Different artifacts for different environments
                    if (params.BUILD_TYPE == 'prod') {
                        // Production: archive optimized build
                        archiveArtifacts(
                            artifacts: 'dist-prod/**/*',
                            fingerprint: true
                        )
                    } else {
                        // Dev/Staging: include debug symbols
                        archiveArtifacts(
                            artifacts: 'dist/**/*,debug/**/*',
                            fingerprint: true
                        )
                    }
                    
                    // Always archive logs
                    archiveArtifacts(
                        artifacts: 'logs/**/*.log',
                        allowEmptyArchive: true
                    )
                }
            }
        }
    }
}
```

### Artifact Versioning

```groovy
pipeline {
    agent any
    
    environment {
        VERSION = sh(
            script: "git describe --tags --always",
            returnStdout: true
        ).trim()
    }
    
    stages {
        stage('Build') {
            steps {
                sh """
                    echo "Building version ${VERSION}"
                    make VERSION=${VERSION} build
                """
            }
        }
        
        stage('Archive with Version') {
            steps {
                script {
                    // Rename artifacts with version
                    sh """
                        mkdir -p versioned-artifacts
                        cp build/app.jar versioned-artifacts/app-${VERSION}.jar
                        cp build/app.war versioned-artifacts/app-${VERSION}.war
                    """
                    
                    archiveArtifacts(
                        artifacts: "versioned-artifacts/*-${VERSION}.*",
                        fingerprint: true
                    )
                }
            }
        }
    }
}
```

## Real-World Examples

### Example 1: Multi-Environment Deployment

```groovy
pipeline {
    agent any
    
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging', 'prod'],
            description: 'Deployment environment'
        )
        booleanParam(
            name: 'SKIP_TESTS',
            defaultValue: false,
            description: 'Skip test execution'
        )
        string(
            name: 'VERSION_TAG',
            defaultValue: 'latest',
            description: 'Version tag for deployment'
        )
    }
    
    stages {
        stage('Validate') {
            steps {
                script {
                    echo "Environment: ${params.ENVIRONMENT}"
                    echo "Version: ${params.VERSION_TAG}"
                    
                    // Production requires explicit version
                    if (params.ENVIRONMENT == 'prod' && params.VERSION_TAG == 'latest') {
                        error "Production deployments require explicit version tag"
                    }
                }
            }
        }
        
        stage('Build') {
            steps {
                sh "mvn clean package -DskipTests=${params.SKIP_TESTS}"
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts(
                    artifacts: 'target/*.jar',
                    fingerprint: true
                )
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    def config = [
                        dev: [replicas: 1, resources: 'small'],
                        staging: [replicas: 2, resources: 'medium'],
                        prod: [replicas: 5, resources: 'large']
                    ]
                    
                    def envConfig = config[params.ENVIRONMENT]
                    
                    sh """
                        kubectl set image deployment/myapp \\
                            myapp=myapp:${params.VERSION_TAG} \\
                            -n ${params.ENVIRONMENT}
                        
                        kubectl scale deployment/myapp \\
                            --replicas=${envConfig.replicas} \\
                            -n ${params.ENVIRONMENT}
                    """
                }
            }
        }
    }
    
    post {
        success {
            echo "Deployment to ${params.ENVIRONMENT} successful!"
        }
    }
}
```

### Example 2: Artifact Promotion Pipeline

```groovy
pipeline {
    agent any
    
    parameters {
        string(
            name: 'BUILD_NUMBER_TO_PROMOTE',
            description: 'Build number to promote from dev to prod'
        )
    }
    
    stages {
        stage('Fetch Dev Artifact') {
            steps {
                copyArtifacts(
                    projectName: 'dev-build-job',
                    selector: specific("${params.BUILD_NUMBER_TO_PROMOTE}"),
                    filter: '**/*.jar',
                    target: 'artifacts/'
                )
            }
        }
        
        stage('Run Integration Tests') {
            steps {
                sh '''
                    java -jar artifacts/app.jar &
                    PID=$!
                    sleep 5
                    ./run-integration-tests.sh
                    kill $PID
                '''
            }
        }
        
        stage('Upload to Prod Artifactory') {
            steps {
                script {
                    def server = Artifactory.server('artifactory-prod')
                    def uploadSpec = """{
                        "files": [{
                            "pattern": "artifacts/*.jar",
                            "target": "prod-releases/"
                        }]
                    }"""
                    server.upload(uploadSpec)
                }
            }
        }
        
        stage('Tag for Production') {
            steps {
                archiveArtifacts(
                    artifacts: 'artifacts/*.jar',
                    fingerprint: true
                )
                
                // Tag the build
                sh """
                    echo "promoted-from-build-${params.BUILD_NUMBER_TO_PROMOTE}" > PROMOTION_TAG
                """
            }
        }
    }
}
```

### Example 3: Microservices Build with Shared Artifacts

```groovy
pipeline {
    agent any
    
    stages {
        stage('Build Common Library') {
            steps {
                dir('common-lib') {
                    sh 'npm run build'
                    stash name: 'common-lib', includes: 'dist/**'
                }
            }
        }
        
        stage('Build Services') {
            parallel {
                stage('Auth Service') {
                    steps {
                        dir('auth-service') {
                            unstash 'common-lib'
                            sh '''
                                cp -r dist/* node_modules/common-lib/
                                npm run build
                            '''
                            stash name: 'auth-service', includes: 'dist/**'
                        }
                    }
                }
                
                stage('API Service') {
                    steps {
                        dir('api-service') {
                            unstash 'common-lib'
                            sh '''
                                cp -r dist/* node_modules/common-lib/
                                npm run build
                            '''
                            stash name: 'api-service', includes: 'dist/**'
                        }
                    }
                }
                
                stage('Web Service') {
                    steps {
                        dir('web-service') {
                            unstash 'common-lib'
                            sh '''
                                cp -r dist/* node_modules/common-lib/
                                npm run build
                            '''
                            stash name: 'web-service', includes: 'dist/**'
                        }
                    }
                }
            }
        }
        
        stage('Package All Services') {
            steps {
                unstash 'auth-service'
                unstash 'api-service'
                unstash 'web-service'
                
                sh '''
                    mkdir -p release
                    cd auth-service && tar -czf ../release/auth-service.tar.gz dist/
                    cd ../api-service && tar -czf ../release/api-service.tar.gz dist/
                    cd ../web-service && tar -czf ../release/web-service.tar.gz dist/
                '''
                
                archiveArtifacts(
                    artifacts: 'release/*.tar.gz',
                    fingerprint: true
                )
            }
        }
    }
}
```

## Artifact Fingerprinting

### What is Fingerprinting?

Fingerprinting tracks artifact usage across jobs using MD5 checksums:

```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
                
                // Archive with fingerprint
                archiveArtifacts(
                    artifacts: 'target/*.jar',
                    fingerprint: true  // Enable tracking
                )
            }
        }
    }
}
```

**Benefits:**
- Track where artifacts are used
- Detect artifact reuse across jobs
- Verify artifact integrity
- Audit artifact flow

### Fingerprint Usage Example

```groovy
// Producer job - creates artifact
pipeline {
    agent any
    stages {
        stage('Build Library') {
            steps {
                sh './gradlew build'
                archiveArtifacts artifacts: 'build/libs/*.jar', fingerprint: true
            }
        }
    }
}

// Consumer job - uses artifact
pipeline {
    agent any
    stages {
        stage('Use Library') {
            steps {
                copyArtifacts(
                    projectName: 'library-build',
                    filter: '**/*.jar',
                    fingerprintArtifacts: true  // Track usage
                )
                
                sh 'mvn install:install-file -Dfile=library.jar'
            }
        }
    }
}
```

## Best Practices

### Parameters

1. **Use Descriptive Names and Descriptions**
   ```groovy
   parameters {
       string(
           name: 'DEPLOY_REGION',  // Clear, specific name
           defaultValue: 'us-east-1',
           description: 'AWS region for deployment (e.g., us-east-1, eu-west-1)'
       )
   }
   ```

2. **Provide Safe Defaults**
   ```groovy
   parameters {
       choice(
           name: 'ENVIRONMENT',
           choices: ['dev', 'staging', 'prod'],
           description: 'Target environment'
       )
       // Dev as default - safest option
   }
   ```

3. **Validate Input Early**
   ```groovy
   stages {
       stage('Validate') {
           steps {
               script {
                   if (!params.VERSION.matches(/^\d+\.\d+\.\d+$/)) {
                       error "Invalid version: ${params.VERSION}"
                   }
               }
           }
       }
   }
   ```

4. **Limit Parameter Complexity**
   - Too many parameters make pipelines hard to use
   - Consider configuration files for complex setups
   - Use sensible defaults

### Artifacts

1. **Archive Only What's Needed**
   ```groovy
   // BAD - archives everything
   archiveArtifacts '**/*'
   
   // GOOD - specific patterns
   archiveArtifacts 'target/*.jar, dist/bundle.js'
   ```

2. **Use Exclusions**
   ```groovy
   archiveArtifacts(
       artifacts: 'build/**/*',
       excludes: '**/*.log, **/*-test.jar, **/node_modules/**'
   )
   ```

3. **Enable Fingerprinting**
   ```groovy
   archiveArtifacts(
       artifacts: 'dist/**',
       fingerprint: true  // Always enable
   )
   ```

4. **Configure Retention**
   ```groovy
   options {
       buildDiscarder(logRotator(
           numToKeepStr: '30',
           artifactNumToKeepStr: '10'  // Keep fewer artifacts
       ))
   }
   ```

5. **Use External Storage for Large Artifacts**
   - Jenkins master has limited space
   - Use S3, Artifactory, or Nexus for large artifacts
   - Keep Jenkins storage lean

6. **Version Your Artifacts**
   ```groovy
   sh "cp build/app.jar build/app-${VERSION}.jar"
   archiveArtifacts "build/app-${VERSION}.jar"
   ```

## Troubleshooting

### Common Issues

**1. "No artifacts found"**
```groovy
// Problem: Wrong path or pattern
archiveArtifacts 'target/*.jar'  // But files are in build/

// Solution: Verify paths
sh 'ls -R build/'  // Check actual location
archiveArtifacts 'build/libs/*.jar'
```

**2. "Disk space exhausted"**
```groovy
// Solution: Configure aggressive retention
options {
    buildDiscarder(logRotator(
        daysToKeepStr: '7',
        numToKeepStr: '10',
        artifactDaysToKeepStr: '3',
        artifactNumToKeepStr: '5'
    ))
}
```

**3. "Stash size too large"**
```groovy
// Problem: Trying to stash large artifacts
stash includes: 'node_modules/**'  // Too large!

// Solution: Use selective stashing or artifacts
stash includes: 'dist/**', excludes: '**/node_modules/**'
```

**4. "Copy artifacts failed"**
```groovy
// Problem: Job or build doesn't exist
copyArtifacts projectName: 'wrong-job-name'

// Solution: Verify job name and handle failures
script {
    try {
        copyArtifacts(
            projectName: 'build-job',
            selector: lastSuccessful(),
            optional: true  // Don't fail if missing
        )
    } catch (Exception e) {
        echo "No artifacts available: ${e.message}"
    }
}
```

## Hands-On Exercise

### Exercise 1: Parameterized Build

Create a pipeline with multiple parameter types:

```groovy
pipeline {
    agent any
    
    parameters {
        string(name: 'APP_NAME', defaultValue: 'myapp')
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'])
        booleanParam(name: 'RUN_TESTS', defaultValue: true)
    }
    
    stages {
        stage('Build') {
            steps {
                echo "Building ${params.APP_NAME} for ${params.ENVIRONMENT}"
                sh 'mvn clean package'
            }
        }
        
        stage('Test') {
            when {
                expression { params.RUN_TESTS == true }
            }
            steps {
                sh 'mvn test'
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts 'target/*.jar'
            }
        }
    }
}
```

**Try:**
1. Run with different parameter combinations
2. Add validation for APP_NAME
3. Add a password parameter for deployment credentials

### Exercise 2: Artifact Management

Create a producer-consumer pipeline:

**Producer:**
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh '''
                    mkdir -p output
                    echo "Library v1.0" > output/library.txt
                    tar -czf library.tar.gz output/
                '''
                archiveArtifacts artifacts: 'library.tar.gz', fingerprint: true
            }
        }
    }
}
```

**Consumer:**
```groovy
pipeline {
    agent any
    stages {
        stage('Fetch') {
            steps {
                copyArtifacts(
                    projectName: 'producer-job',
                    filter: 'library.tar.gz',
                    selector: lastSuccessful()
                )
                sh 'tar -xzf library.tar.gz'
                sh 'cat output/library.txt'
            }
        }
    }
}
```

**Try:**
1. Create both jobs
2. Run producer first
3. Run consumer and verify artifact retrieval
4. Add fingerprinting tracking

## Summary

Parameters and artifacts are essential for flexible, reusable pipelines:

**Parameters:**
- Make pipelines configurable
- Support multiple data types
- Enable dynamic behavior
- Require validation

**Artifacts:**
- Preserve build outputs
- Enable job chaining
- Support various storage backends
- Need retention policies

**Best Practices:**
- Validate parameters early
- Archive selectively
- Use external storage for large artifacts
- Enable fingerprinting
- Configure retention policies

## Next Steps

- **Security** → Learn about securing Jenkins
- **Distributed Builds** → Scale with agents
- **Monitoring** → Track pipeline health
- **Practice Labs** → Hands-on exercises

---

**Previous:** [Plugins →](11-plugins.md)  
**Next:** [Interview Questions →](interview-questions-intermediate.md)
