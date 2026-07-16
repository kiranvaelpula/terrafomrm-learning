# Lab 1: Jenkins Setup & Configuration

Master Jenkins installation, initial configuration, and create your first jobs.

## Learning Objectives

By the end of this lab, you will be able to:
- Install Jenkins using multiple methods
- Configure Jenkins initial settings
- Create freestyle and pipeline jobs
- Understand Jenkins architecture
- Navigate the Jenkins UI

## Prerequisites

- Docker installed (recommended) OR
- Java 11 or 17 installed (for native installation)
- 4GB RAM minimum
- Command line access
- Web browser

## Lab Duration

**Estimated Time:** 60-90 minutes

---

## Exercise 1: Install Jenkins with Docker

**Objective:** Quick Jenkins setup using Docker

```bash
# Pull Jenkins LTS image
docker pull jenkins/jenkins:lts

# Run Jenkins
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts

# Check it's running
docker ps

# Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

**Access Jenkins:**
- Open browser: http://localhost:8080
- Paste the initial admin password
- Click "Install suggested plugins"
- Wait for plugin installation (3-5 minutes)

**Create Admin User:**
- Username: admin
- Password: (choose a secure password)
- Full name: Your Name
- Email: your.email@example.com
- Click "Save and Continue"

✅ **Checkpoint:** Jenkins is accessible at http://localhost:8080

---


## Exercise 2: Configure Jenkins System Settings

**Objective:** Set up essential Jenkins configurations

### Step 1: Configure System

Navigate to: **Manage Jenkins** > **Configure System**

```yaml
System Configuration:
  # of executors: 2
  Usage: Use this node as much as possible
  
  Jenkins Location:
    Jenkins URL: http://localhost:8080/
    System Admin e-mail address: admin@localhost
    
  Email Notification:
    SMTP server: smtp.gmail.com
    Use SMTP Authentication: (if needed)
    Default user e-mail suffix: @example.com
```

### Step 2: Install Additional Plugins

**Manage Jenkins** > **Manage Plugins** > **Available**

Install these essential plugins:
- Pipeline
- Git
- Docker Pipeline
- Blue Ocean
- Warnings Next Generation
- Test Results Analyzer

```bash
# Alternative: Install via CLI
docker exec jenkins jenkins-plugin-cli --plugins \
  pipeline-model-definition \
  git \
  docker-workflow \
  blueocean \
  warnings-ng
```

### Step 3: Configure Global Tool Configuration

**Manage Jenkins** > **Global Tool Configuration**

**Maven:**
- Name: Maven-3.8
- Install automatically: ✓
- Version: 3.8.6

**Git:**
- Name: Default
- Path to Git executable: git

**Docker:**
- Name: docker
- Install automatically: ✓

✅ **Checkpoint:** Essential plugins installed and tools configured

---

## Exercise 3: Create Your First Freestyle Job

**Objective:** Build a simple freestyle project

### Step 1: Create New Item

1. Click "New Item"
2. Name: `hello-jenkins-freestyle`
3. Select: "Freestyle project"
4. Click "OK"

### Step 2: Configure Job

**General:**
- Description: "My first Jenkins freestyle job"
- Discard old builds: Keep max 10 builds

**Build Steps:**
Add "Execute shell" build step:

```bash
#!/bin/bash
echo "Hello from Jenkins!"
echo "Build number: $BUILD_NUMBER"
echo "Workspace: $WORKSPACE"
echo "Job name: $JOB_NAME"

# Create a file
echo "Build completed at $(date)" > build-info.txt
cat build-info.txt

# List workspace
ls -la
```

**Post-build Actions:**
- Add "Archive the artifacts": `*.txt`

Click "Save"

### Step 3: Run the Build

1. Click "Build Now"
2. Watch build progress in "Build History"
3. Click on build #1
4. Check "Console Output"
5. View "Workspace"

**Expected Output:**
```
Hello from Jenkins!
Build number: 1
Workspace: /var/jenkins_home/workspace/hello-jenkins-freestyle
Job name: hello-jenkins-freestyle
Build completed at [timestamp]
```

✅ **Checkpoint:** Freestyle job runs successfully

---

## Exercise 4: Create Your First Pipeline Job

**Objective:** Learn Jenkinsfile basics

### Step 1: Create Pipeline Job

1. New Item → `hello-jenkins-pipeline`
2. Select: "Pipeline"
3. OK

### Step 2: Write Pipeline Script

In **Pipeline** section, select "Pipeline script" and enter:

```groovy
pipeline {
    agent any
    
    environment {
        APP_NAME = 'HelloJenkins'
        VERSION = '1.0.0'
    }
    
    stages {
        stage('Preparation') {
            steps {
                echo "Preparing build for ${APP_NAME} v${VERSION}"
                echo "Build number: ${BUILD_NUMBER}"
                echo "Node name: ${NODE_NAME}"
            }
        }
        
        stage('Build') {
            steps {
                echo 'Building application...'
                sh '''
                    echo "Compiling source code"
                    echo "Running build at $(date)" > build.log
                    sleep 2
                    echo "Build complete"
                '''
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh '''
                    echo "Running unit tests"
                    echo "Test result: PASSED" > test-results.txt
                    sleep 1
                '''
            }
        }
        
        stage('Package') {
            steps {
                echo 'Creating artifacts...'
                sh '''
                    echo "Packaging application"
                    tar -czf app-${BUILD_NUMBER}.tar.gz *.log *.txt
                    ls -lh *.tar.gz
                '''
                archiveArtifacts artifacts: '*.tar.gz', fingerprint: true
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
            echo 'Cleaning up...'
            sh 'ls -la'
        }
    }
}
```

### Step 3: Run Pipeline

1. Click "Build Now"
2. Watch "Stage View"
3. Check each stage's logs
4. View archived artifacts

✅ **Checkpoint:** Pipeline with multiple stages executes successfully

---

## Exercise 5: Create a Parameterized Build

**Objective:** Use build parameters

### Create New Pipeline: `parameterized-build`

```groovy
pipeline {
    agent any
    
    parameters {
        string(name: 'USERNAME', defaultValue: 'DevOps', description: 'Enter your name')
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'production'], description: 'Select environment')
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run tests?')
        text(name: 'NOTES', defaultValue: 'Build notes', description: 'Build notes')
    }
    
    stages {
        stage('Show Parameters') {
            steps {
                echo "Hello, ${params.USERNAME}!"
                echo "Deploying to: ${params.ENVIRONMENT}"
                echo "Run tests: ${params.RUN_TESTS}"
                echo "Notes: ${params.NOTES}"
            }
        }
        
        stage('Build') {
            steps {
                script {
                    if (params.ENVIRONMENT == 'production') {
                        echo '⚠️ Building for PRODUCTION'
                        input message: 'Approve production build?', ok: 'Proceed'
                    }
                }
                echo 'Building application...'
            }
        }
        
        stage('Test') {
            when {
                expression { params.RUN_TESTS == true }
            }
            steps {
                echo 'Running tests...'
                sh 'echo "Test passed" > test-report.txt'
            }
        }
        
        stage('Deploy') {
            steps {
                echo "Deploying to ${params.ENVIRONMENT}..."
                sh """
                    echo "Deployed to ${params.ENVIRONMENT} by ${params.USERNAME}" > deploy.log
                    cat deploy.log
                """
            }
        }
    }
}
```

**Run Build:**
1. Click "Build with Parameters"
2. Fill in parameters
3. Click "Build"
4. Observe different behavior based on parameters

✅ **Checkpoint:** Parameterized pipeline works with different inputs

---

## Exercise 6: Configure Build Triggers

**Objective:** Automate build execution

### Method 1: Periodic Builds

Edit `hello-jenkins-pipeline`:

**Build Triggers:**
- ☑ Build periodically
- Schedule: `H/15 * * * *` (every 15 minutes)

### Method 2: Poll SCM (when connected to Git)

**Build Triggers:**
- ☑ Poll SCM
- Schedule: `H/5 * * * *` (check every 5 minutes)

### Method 3: Trigger Builds Remotely

**Build Triggers:**
- ☑ Trigger builds remotely
- Authentication Token: `mytoken123`

**Trigger via curl:**
```bash
curl -X POST http://localhost:8080/job/hello-jenkins-pipeline/build?token=mytoken123
```

✅ **Checkpoint:** Understand different trigger mechanisms

---

## Validation

Run all validation checks:

```bash
# Check Jenkins is running
curl -I http://localhost:8080

# List all jobs via CLI
docker exec jenkins java -jar /var/jenkins_home/war/WEB-INF/jenkins-cli.jar \
  -s http://localhost:8080/ list-jobs

# Check job status
curl http://localhost:8080/job/hello-jenkins-pipeline/lastBuild/api/json | jq
```

**Expected Results:**
- Jenkins responds on port 8080
- At least 3 jobs created
- Jobs have build history
- Artifacts are archived

---

## Troubleshooting

**Issue:** Cannot access Jenkins at http://localhost:8080  
**Solution:**
```bash
# Check container is running
docker ps | grep jenkins

# Check logs
docker logs jenkins

# Restart Jenkins
docker restart jenkins
```

**Issue:** "Permission denied" in shell scripts  
**Solution:**
```groovy
// Add shebang
sh '''#!/bin/bash
echo "Commands here"
'''
```

**Issue:** Plugins won't install  
**Solution:**
```bash
# Restart Jenkins
docker restart jenkins

# Check Jenkins logs
docker logs -f jenkins
```

**Issue:** Build queue stuck  
**Solution:**
- Navigate to "Manage Jenkins" > "Manage Nodes and Clouds"
- Check executor availability
- Increase number of executors if needed

---

## Clean Up

```bash
# Stop Jenkins
docker stop jenkins

# Remove container (keeps data in volume)
docker rm jenkins

# Remove volume (deletes all data)
docker volume rm jenkins_home

# Or remove everything
docker stop jenkins && docker rm jenkins && docker volume rm jenkins_home
```

---

## Additional Challenges

1. **Challenge 1:** Create a multi-branch pipeline
2. **Challenge 2:** Set up email notifications for failed builds
3. **Challenge 3:** Create a pipeline that deploys based on branch name
4. **Challenge 4:** Configure Jenkins to run on a custom port (e.g., 9090)
5. **Challenge 5:** Install Jenkins using native package (without Docker)

---

## Summary

What you learned:
- ✅ Install Jenkins using Docker
- ✅ Configure initial Jenkins settings
- ✅ Install plugins
- ✅ Create freestyle jobs
- ✅ Write Jenkinsfile for pipelines
- ✅ Use build parameters
- ✅ Configure build triggers
- ✅ Archive artifacts
- ✅ Navigate Jenkins UI
- ✅ Troubleshoot common issues

---

## Next Steps

- [ ] Complete Lab 2: First Pipeline
- [ ] Explore Blue Ocean UI
- [ ] Read Jenkins documentation
- [ ] Experiment with different pipeline syntaxes

**Congratulations!** You've completed Jenkins Setup & Configuration Lab.

---

**Next Lab:** [First Pipeline](../lab-02-first-pipeline/)

