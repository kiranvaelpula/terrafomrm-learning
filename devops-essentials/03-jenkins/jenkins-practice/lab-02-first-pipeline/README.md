# Lab 2: First Jenkins Pipeline

Master Jenkinsfile creation, multi-stage pipelines, and pipeline best practices.

## Learning Objectives

By the end of this lab, you will be able to:
- Write declarative pipelines
- Create multi-stage pipelines
- Use environment variables
- Implement error handling
- Use post actions
- Work with workspaces

## Prerequisites

- Lab 1 completed
- Jenkins running
- Basic understanding of Groovy syntax

## Lab Duration

**Estimated Time:** 60-90 minutes

---

## Exercise 1: Basic Pipeline Structure

**Objective:** Understand pipeline anatomy

### Create Pipeline: `pipeline-basics`

```groovy
pipeline {
    agent any  // Run on any available agent
    
    stages {
        stage('Hello') {
            steps {
                echo 'Hello, Jenkins Pipeline!'
            }
        }
    }
}
```

**Run and observe:**
- Stage view
- Console output
- Build time

### Add More Stages

```groovy
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                // In real scenario: checkout scm
            }
        }
        
        stage('Build') {
            steps {
                echo 'Building application...'
                sh '''
                    echo "Source files" > source.txt
                    echo "Compiling..."
                    sleep 2
                    echo "Build successful"
                '''
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh '''
                    echo "Running unit tests..."
                    sleep 1
                    echo "Tests passed"
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh 'echo "Deployed at $(date)"'
            }
        }
    }
}
```

✅ **Checkpoint:** Multi-stage pipeline executes sequentially

---


## Exercise 2: Environment Variables

**Objective:** Use environment variables in pipelines

```groovy
pipeline {
    agent any
    
    environment {
        APP_NAME = 'MyApplication'
        APP_VERSION = '1.0.0'
        BUILD_USER = 'jenkins'
        DEPLOY_ENV = 'development'
    }
    
    stages {
        stage('Show Environment') {
            steps {
                echo "Application: ${APP_NAME}"
                echo "Version: ${APP_VERSION}"
                echo "Build User: ${BUILD_USER}"
                echo "Environment: ${DEPLOY_ENV}"
                
                // Access Jenkins built-in variables
                echo "Build Number: ${BUILD_NUMBER}"
                echo "Job Name: ${JOB_NAME}"
                echo "Workspace: ${WORKSPACE}"
                echo "Node: ${NODE_NAME}"
            }
        }
        
        stage('Build with Variables') {
            steps {
                sh '''
                    echo "Building ${APP_NAME} v${APP_VERSION}"
                    echo "Build #${BUILD_NUMBER}"
                    echo "${APP_NAME}-${APP_VERSION}-${BUILD_NUMBER}" > artifact.txt
                    cat artifact.txt
                '''
            }
        }
    }
}
```

✅ **Checkpoint:** Environment variables work correctly

---

## Exercise 3: Conditional Execution

**Objective:** Execute stages based on conditions

```groovy
pipeline {
    agent any
    
    environment {
        DEPLOY_TO_PROD = 'false'
    }
    
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        
        stage('Test') {
            steps {
                echo 'Testing...'
            }
        }
        
        stage('Deploy to Dev') {
            when {
                expression { DEPLOY_TO_PROD == 'false' }
            }
            steps {
                echo 'Deploying to Development...'
            }
        }
        
        stage('Deploy to Production') {
            when {
                expression { DEPLOY_TO_PROD == 'true' }
            }
            steps {
                echo 'Deploying to Production...'
            }
        }
    }
}
```

**Try with different conditions:**
```groovy
when {
    branch 'main'  // Only on main branch
}

when {
    environment name: 'DEPLOY', value: 'true'
}

when {
    expression { BUILD_NUMBER.toInteger() > 5 }
}

when {
    allOf {
        branch 'main'
        environment name: 'DEPLOY', value: 'true'
    }
}
```

✅ **Checkpoint:** Conditional stages execute correctly

---

## Exercise 4: Post Actions

**Objective:** Cleanup and notifications

```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
                sh 'echo "Build artifact" > build.txt'
            }
        }
        
        stage('Test') {
            steps {
                echo 'Testing...'
                // Simulate random failure
                sh '''
                    if [ $((RANDOM % 2)) -eq 0 ]; then
                        echo "Tests passed"
                    else
                        echo "Tests failed"
                        exit 1
                    fi
                '''
            }
        }
    }
    
    post {
        always {
            echo 'This runs always'
            sh 'ls -la'
        }
        
        success {
            echo '✅ Build succeeded!'
            sh 'echo "Success log" > success.log'
        }
        
        failure {
            echo '❌ Build failed!'
            sh 'echo "Failure log" > failure.log'
        }
        
        unstable {
            echo '⚠️ Build is unstable'
        }
        
        changed {
            echo 'Build status changed'
        }
        
        cleanup {
            echo 'Final cleanup'
            sh 'rm -f *.txt *.log || true'
        }
    }
}
```

✅ **Checkpoint:** Post actions execute based on build status

---

## Exercise 5: Parallel Stages

**Objective:** Run stages concurrently

```groovy
pipeline {
    agent any
    
    stages {
        stage('Prepare') {
            steps {
                echo 'Preparing build environment...'
            }
        }
        
        stage('Parallel Tests') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        echo 'Running unit tests...'
                        sh 'sleep 3 && echo "Unit tests passed" > unit-tests.txt'
                    }
                }
                
                stage('Integration Tests') {
                    steps {
                        echo 'Running integration tests...'
                        sh 'sleep 4 && echo "Integration tests passed" > int-tests.txt'
                    }
                }
                
                stage('UI Tests') {
                    steps {
                        echo 'Running UI tests...'
                        sh 'sleep 5 && echo "UI tests passed" > ui-tests.txt'
                    }
                }
            }
        }
        
        stage('Report') {
            steps {
                echo 'Generating test report...'
                sh '''
                    echo "=== Test Results ==="
                    cat unit-tests.txt
                    cat int-tests.txt
                    cat ui-tests.txt
                '''
            }
        }
    }
}
```

✅ **Checkpoint:** Parallel stages run simultaneously

---

## Exercise 6: Input and Approvals

**Objective:** Manual approval steps

```groovy
pipeline {
    agent any
    
    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'], description: 'Deployment environment')
    }
    
    stages {
        stage('Build') {
            steps {
                echo 'Building application...'
                sh 'echo "v1.0.${BUILD_NUMBER}" > version.txt'
            }
        }
        
        stage('Deploy to Dev') {
            when {
                expression { params.ENVIRONMENT == 'dev' }
            }
            steps {
                echo 'Deploying to dev...'
            }
        }
        
        stage('Approve Staging') {
            when {
                expression { params.ENVIRONMENT == 'staging' }
            }
            steps {
                input message: 'Deploy to staging?', ok: 'Deploy'
                echo 'Deploying to staging...'
            }
        }
        
        stage('Approve Production') {
            when {
                expression { params.ENVIRONMENT == 'prod' }
            }
            steps {
                input(
                    message: 'Deploy to production?',
                    ok: 'Yes, deploy to PROD',
                    submitter: 'admin',
                    parameters: [
                        string(name: 'APPROVER', description: 'Your name')
                    ]
                )
                echo "Deploying to production (approved by ${APPROVER})..."
            }
        }
    }
}
```

✅ **Checkpoint:** Manual approval workflow functions

---

## Exercise 7: Error Handling

**Objective:** Handle failures gracefully

```groovy
pipeline {
    agent any
    
    stages {
        stage('Risky Build') {
            steps {
                script {
                    try {
                        echo 'Attempting risky operation...'
                        sh 'exit 1'  // Simulate failure
                    } catch (Exception e) {
                        echo "Build failed: ${e.message}"
                        echo 'Attempting recovery...'
                        sh 'echo "Recovered" > recovery.log'
                    }
                }
            }
        }
        
        stage('Retry on Failure') {
            steps {
                retry(3) {
                    echo 'Attempting operation (will retry up to 3 times)...'
                    sh '''
                        if [ ! -f success.flag ]; then
                            echo "Attempt failed"
                            touch success.flag
                            exit 1
                        fi
                        echo "Success!"
                    '''
                }
            }
        }
        
        stage('Timeout') {
            steps {
                timeout(time: 1, unit: 'MINUTES') {
                    echo 'Operation with timeout...'
                    sh 'sleep 10'  // Will succeed
                }
            }
        }
    }
}
```

✅ **Checkpoint:** Error handling mechanisms work

---

## Exercise 8: Working with Artifacts

**Objective:** Archive and use build artifacts

```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                echo 'Creating artifacts...'
                sh '''
                    mkdir -p dist
                    echo "Application v${BUILD_NUMBER}" > dist/app.txt
                    echo "Configuration" > dist/config.txt
                    echo "Documentation" > dist/README.txt
                    tar -czf myapp-${BUILD_NUMBER}.tar.gz dist/
                '''
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts(
                    artifacts: '*.tar.gz',
                    fingerprint: true,
                    onlyIfSuccessful: true
                )
            }
        }
        
        stage('Stash Files') {
            steps {
                stash(
                    name: 'build-artifacts',
                    includes: 'dist/**'
                )
            }
        }
        
        stage('Use Stashed Files') {
            steps {
                unstash 'build-artifacts'
                sh 'ls -R dist/'
            }
        }
    }
}
```

✅ **Checkpoint:** Artifacts are archived and accessible

---

## Validation

**Check Your Work:**

1. All pipelines run successfully
2. Stage view shows all stages
3. Environment variables are accessible
4. Conditional stages work
5. Post actions execute
6. Parallel stages run concurrently
7. Manual approvals pause execution
8. Error handling prevents pipeline failure
9. Artifacts are archived

---

## Troubleshooting

**Issue:** Pipeline syntax error  
**Solution:** Use "Pipeline Syntax" generator in Jenkins UI

**Issue:** Environment variables not working  
**Solution:** Use `${VAR}` syntax in Groovy, `$VAR` in shell

**Issue:** Parallel stages fail  
**Solution:** Ensure stages are independent

---

## Summary

What you learned:
- ✅ Write declarative pipelines
- ✅ Create multi-stage workflows
- ✅ Use environment variables
- ✅ Implement conditional execution
- ✅ Add post-build actions
- ✅ Run parallel stages
- ✅ Implement manual approvals
- ✅ Handle errors and retries
- ✅ Work with artifacts

---

## Next Steps

- [ ] Complete Lab 3: Git Integration
- [ ] Experiment with scripted pipelines
- [ ] Explore Blue Ocean pipeline editor

**Congratulations!** You've mastered Jenkins pipelines.

---

**Previous:** [Setup](../lab-01-setup/) | **Next:** [Git Integration](../lab-03-git-integration/)

