# Creating Your First Jenkins Job

## Overview

A Jenkins job (also called a project) is a runnable task that contains configuration for what Jenkins should do. This guide covers creating various types of jobs from simple to complex.

## Job Types

Jenkins offers several project types:

| Type | Use Case | Complexity | Modern? |
|------|----------|------------|---------|
| **Freestyle Project** | Simple tasks, UI configuration | Low | Legacy |
| **Pipeline** | Code-based CI/CD | Medium | ✓ Modern |
| **Multi-branch Pipeline** | Auto-detect branches | Medium-High | ✓ Modern |
| **Multibranch Organization** | Multiple repos | High | ✓ Modern |
| **Folder** | Organization only | Low | ✓ Modern |

## Creating a Freestyle Project

### Step 1: Create New Job

1. Click **"New Item"** (Dashboard)
2. Enter name: `hello-world-job`
3. Select **"Freestyle project"**
4. Click **"OK"**

### Step 2: Configure General Settings

```
Description: My first Jenkins job
✓ Discard old builds
  Days to keep builds: 7
  Max # of builds to keep: 10
```

### Step 3: Add Build Step

**Build** section → **Add build step** → **Execute shell**

**Linux/Mac:**
```bash
echo "Hello from Jenkins!"
echo "Current directory: $(pwd)"
echo "Date: $(date)"
echo "User: $(whoami)"
ls -la
```

**Windows:**
```cmd
echo Hello from Jenkins!
echo Current directory: %CD%
echo Date: %DATE% %TIME%
echo User: %USERNAME%
dir
```

### Step 4: Save and Build

1. Click **"Save"**
2. Click **"Build Now"**
3. Watch build in **Build History**
4. Click build number (#1)
5. Click **"Console Output"**

### Expected Output

```
Started by user admin
Running as SYSTEM
Building in workspace /var/jenkins_home/workspace/hello-world-job
[hello-world-job] $ /bin/sh -xe /tmp/jenkins123.sh
+ echo Hello from Jenkins!
Hello from Jenkins!
+ echo Current directory: /var/jenkins_home/workspace/hello-world-job
Current directory: /var/jenkins_home/workspace/hello-world-job
+ date
Wed Jul 15 10:30:00 UTC 2026
+ whoami
jenkins
Finished: SUCCESS
```

## Creating a Simple Pipeline Job

### Step 1: Create Pipeline

1. **New Item** → Name: `first-pipeline`
2. Select **"Pipeline"**
3. Click **"OK"**

### Step 2: Write Pipeline Script

Scroll to **Pipeline** section, select **Pipeline script**:

```groovy
pipeline {
    agent any
    
    stages {
        stage('Hello') {
            steps {
                echo 'Hello World'
            }
        }
        
        stage('Build') {
            steps {
                echo 'Building...'
                sh 'sleep 2'
            }
        }
        
        stage('Test') {
            steps {
                echo 'Testing...'
                sh 'sleep 2'
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying...'
                sh 'sleep 2'
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
```

### Step 3: Run Pipeline

1. Click **"Save"**
2. Click **"Build Now"**
3. View **Stage View** (shows each stage)
4. Click stage to see logs

## Real-World Examples

### Example 1: Node.js Application Build

```groovy
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Simulating git checkout...'
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing npm packages...'
                // sh 'npm install'
                sh 'echo "npm install completed"'
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                // sh 'npm test'
                sh 'echo "All tests passed"'
            }
        }
        
        stage('Build') {
            steps {
                echo 'Building application...'
                // sh 'npm run build'
                sh 'echo "Build completed"'
            }
        }
    }
}
```

### Example 2: Python Application with Testing

```groovy
pipeline {
    agent any
    
    environment {
        PYTHONPATH = "${workspace}"
    }
    
    stages {
        stage('Setup') {
            steps {
                echo 'Setting up Python environment...'
                // sh 'python -m venv venv'
                // sh '. venv/bin/activate'
                sh 'echo "Virtual environment created"'
            }
        }
        
        stage('Install') {
            steps {
                echo 'Installing dependencies...'
                // sh 'pip install -r requirements.txt'
                sh 'echo "Dependencies installed"'
            }
        }
        
        stage('Lint') {
            steps {
                echo 'Running linter...'
                // sh 'pylint src/'
                sh 'echo "Code quality check passed"'
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running tests...'
                // sh 'pytest tests/'
                sh 'echo "All tests passed"'
            }
        }
    }
}
```

### Example 3: Docker Build and Push

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'myapp'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Build Image') {
            steps {
                echo "Building Docker image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                // sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                sh 'echo "Docker image built successfully"'
            }
        }
        
        stage('Test Image') {
            steps {
                echo 'Testing Docker image...'
                // sh "docker run --rm ${DOCKER_IMAGE}:${DOCKER_TAG} npm test"
                sh 'echo "Image tests passed"'
            }
        }
        
        stage('Push Image') {
            steps {
                echo 'Pushing image to registry...'
                // sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                sh 'echo "Image pushed successfully"'
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up...'
            // sh "docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true"
        }
    }
}
```

## Understanding Build Parameters

### Adding Parameters to Freestyle Job

1. **Configure** job
2. Check **"This project is parameterized"**
3. **Add Parameter** → **String Parameter**

```
Name: ENVIRONMENT
Default Value: dev
Description: Deployment environment
```

4. **Add Parameter** → **Choice Parameter**

```
Name: ACTION
Choices: 
  build
  test
  deploy
Description: Action to perform
```

5. **Build step** using parameters:

```bash
echo "Environment: ${ENVIRONMENT}"
echo "Action: ${ACTION}"

if [ "${ACTION}" = "deploy" ]; then
    echo "Deploying to ${ENVIRONMENT}..."
fi
```

### Parameters in Pipeline

```groovy
pipeline {
    agent any
    
    parameters {
        string(
            name: 'ENVIRONMENT',
            defaultValue: 'dev',
            description: 'Deployment environment'
        )
        choice(
            name: 'ACTION',
            choices: ['build', 'test', 'deploy'],
            description: 'Action to perform'
        )
        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run tests?'
        )
    }
    
    stages {
        stage('Environment Info') {
            steps {
                echo "Environment: ${params.ENVIRONMENT}"
                echo "Action: ${params.ACTION}"
                echo "Run Tests: ${params.RUN_TESTS}"
            }
        }
        
        stage('Build') {
            when {
                expression { params.ACTION == 'build' || params.ACTION == 'deploy' }
            }
            steps {
                echo 'Building application...'
            }
        }
        
        stage('Test') {
            when {
                expression { params.RUN_TESTS == true }
            }
            steps {
                echo 'Running tests...'
            }
        }
        
        stage('Deploy') {
            when {
                expression { params.ACTION == 'deploy' }
            }
            steps {
                echo "Deploying to ${params.ENVIRONMENT}..."
            }
        }
    }
}
```

## Job Configuration Best Practices

### 1. Descriptive Naming

❌ **Bad:**
```
job1
test
build-v2
```

✅ **Good:**
```
backend-api-build
frontend-deploy-prod
integration-tests-nightly
```

### 2. Use Descriptions

```groovy
pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
    }
    
    stages {
        // ... stages here
    }
}
```

### 3. Environment Variables

```groovy
pipeline {
    agent any
    
    environment {
        // Global variables
        APP_NAME = 'my-application'
        BUILD_ENV = 'production'
        
        // Credentials
        DOCKER_CREDS = credentials('docker-hub-credentials')
        AWS_CREDS = credentials('aws-credentials')
    }
    
    stages {
        stage('Use Variables') {
            steps {
                echo "Building ${APP_NAME} for ${BUILD_ENV}"
                sh 'echo "Docker user: $DOCKER_CREDS_USR"'
            }
        }
    }
}
```

### 4. Error Handling

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
                        currentBuild.result = 'FAILURE'
                        error('Build stage failed')
                    }
                }
            }
        }
    }
    
    post {
        failure {
            echo 'Sending failure notification...'
            // emailext subject: 'Build Failed', body: '...'
        }
    }
}
```

## Common Build Steps

### Execute Shell Commands

```groovy
stage('Run Commands') {
    steps {
        sh '''
            #!/bin/bash
            set -e
            
            echo "Multi-line shell script"
            ls -la
            pwd
            
            if [ -f "package.json" ]; then
                echo "Node.js project detected"
                npm install
                npm test
            fi
        '''
    }
}
```

### Execute Batch Commands (Windows)

```groovy
stage('Windows Commands') {
    steps {
        bat '''
            echo Running on Windows
            dir
            echo Build completed
        '''
    }
}
```

### Archive Artifacts

```groovy
stage('Archive') {
    steps {
        sh 'tar czf build-artifacts.tar.gz dist/'
        archiveArtifacts artifacts: 'build-artifacts.tar.gz',
                        fingerprint: true,
                        allowEmptyArchive: false
    }
}
```

### Publish Test Results

```groovy
stage('Test Results') {
    steps {
        sh 'npm test -- --reporter=junit'
        junit 'test-results/*.xml'
    }
}
```

## Job Organization

### Creating Folders

1. **New Item** → Name: `frontend`
2. Select **"Folder"**
3. Click **"OK"**
4. Add description
5. Save

### Folder Structure Example

```
jenkins/
├── frontend/
│   ├── build-job
│   ├── test-job
│   └── deploy-job
├── backend/
│   ├── api-build
│   ├── api-tests
│   └── api-deploy
└── infrastructure/
    ├── terraform-plan
    └── terraform-apply
```

## Monitoring Job Execution

### Console Output

- Real-time build logs
- Command output
- Error messages
- Exit codes

### Build History

- Build numbers
- Build status (success/failure)
- Build duration
- Build parameters

### Workspace Browser

- View files in workspace
- Download artifacts
- Inspect build environment

## Hands-On Exercise

### Exercise 1: Create Multi-Stage Build

Create a pipeline with:
1. Checkout stage (simulated)
2. Build stage (echo message, sleep 3 seconds)
3. Test stage (echo message, sleep 2 seconds)
4. Deploy stage (echo message, sleep 2 seconds)
5. Add post-build success/failure messages

<details>
<summary>Solution</summary>

```groovy
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                sh 'sleep 1'
            }
        }
        
        stage('Build') {
            steps {
                echo 'Building application...'
                sh 'sleep 3'
                echo 'Build completed'
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh 'sleep 2'
                echo 'All tests passed'
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh 'sleep 2'
                echo 'Deployment successful'
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
        always {
            echo 'Pipeline execution finished'
        }
    }
}
```
</details>

### Exercise 2: Parameterized Build

Create a pipeline that:
1. Accepts environment parameter (dev, staging, prod)
2. Accepts boolean for running tests
3. Only deploys if environment is not 'dev'

<details>
<summary>Solution</summary>

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
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Execute tests?'
        )
    }
    
    stages {
        stage('Build') {
            steps {
                echo "Building for ${params.ENVIRONMENT}"
            }
        }
        
        stage('Test') {
            when {
                expression { params.RUN_TESTS == true }
            }
            steps {
                echo 'Executing tests...'
            }
        }
        
        stage('Deploy') {
            when {
                expression { params.ENVIRONMENT != 'dev' }
            }
            steps {
                echo "Deploying to ${params.ENVIRONMENT}"
            }
        }
    }
}
```
</details>

## Troubleshooting

### Build Stays in Queue

**Symptoms:** Build shows in queue but never starts

**Solutions:**
- Check available executors (Manage Jenkins → Nodes)
- Check agent labels match job requirements
- Verify agents are online

### Permission Denied Errors

**Symptoms:** `sh: permission denied`

**Solutions:**
```bash
# Make script executable
chmod +x script.sh

# Or in pipeline
sh 'chmod +x script.sh && ./script.sh'
```

### Workspace Issues

**Symptoms:** Old files interfering with build

**Solutions:**
```groovy
pipeline {
    options {
        skipDefaultCheckout()
    }
    
    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
                // Then checkout
            }
        }
    }
}
```

## Summary

You've learned to:
- Create Freestyle and Pipeline jobs
- Configure build steps and parameters
- Organize jobs with folders
- Implement error handling
- Monitor and troubleshoot builds

**Key Points:**
- Pipelines are modern and code-based
- Use parameters for flexibility
- Organize with folders
- Monitor console output
- Clean workspaces regularly

---

**Previous:** [← Installation](02-installation.md) | **Next:** [UI Navigation →](04-ui-navigation.md)
