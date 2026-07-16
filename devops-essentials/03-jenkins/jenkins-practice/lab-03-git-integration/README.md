# Lab 3: Git Integration

Master Git integration, webhooks, and automated CI workflows with Jenkins.

## Learning Objectives

- Integrate Jenkins with GitHub/GitLab
- Configure webhooks for automatic builds
- Implement branch-based strategies
- Handle pull/merge requests
- Use Git credentials securely

## Prerequisites

- Labs 1-2 completed
- GitHub or GitLab account
- Git installed locally
- Sample repository (will create)

## Lab Duration

**Estimated Time:** 60-90 minutes

---

## Exercise 1: Setup Git Repository

**Objective:** Create sample repository

```bash
# Create local repository
mkdir my-jenkins-app
cd my-jenkins-app

# Initialize Git
git init

# Create application files
cat > app.py <<EOF
def hello():
    return "Hello from Jenkins + Git!"

if __name__ == "__main__":
    print(hello())
EOF

cat > test_app.py <<EOF
import app

def test_hello():
    assert app.hello() == "Hello from Jenkins + Git!"
    print("✅ Test passed!")

if __name__ == "__main__":
    test_hello()
EOF

cat > Jenkinsfile <<EOF
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                echo 'Code checked out'
            }
        }
        stage('Build') {
            steps {
                sh 'echo "Building..."'
            }
        }
        stage('Test') {
            steps {
                sh 'python3 test_app.py'
            }
        }
    }
}
EOF

# Commit files
git add .
git commit -m "Initial commit"
```

**Push to GitHub:**
```bash
# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/my-jenkins-app.git
git branch -M main
git push -u origin main
```

✅ **Checkpoint:** Repository created and pushed to GitHub

---

## Exercise 2: Configure Git Credentials in Jenkins

**Objective:** Secure Git authentication

### Step 1: Add GitHub Credentials

**Manage Jenkins** > **Manage Credentials** > **System** > **Global credentials**

Click "Add Credentials":
- Kind: Username with password
- Username: your GitHub username
- Password: GitHub Personal Access Token
- ID: github-credentials
- Description: GitHub Access

**Create GitHub Token:**
1. GitHub Settings > Developer settings > Personal access tokens
2. Generate new token (classic)
3. Scopes: `repo`, `admin:repo_hook`
4. Copy token

### Step 2: Test Credentials

Create pipeline: `test-git-credentials`

```groovy
pipeline {
    agent any
    stages {
        stage('Test Git') {
            steps {
                git credentialsId: 'github-credentials',
                    url: 'https://github.com/YOUR_USERNAME/my-jenkins-app.git',
                    branch: 'main'
                    
                sh 'ls -la'
                sh 'cat Jenkinsfile'
            }
        }
    }
}
```

✅ **Checkpoint:** Jenkins can access private repository

---

## Exercise 3: Pipeline from SCM

**Objective:** Use Jenkinsfile from repository

### Create Multibranch Pipeline

1. New Item → `my-jenkins-app-multibranch`
2. Type: "Multibranch Pipeline"

**Configuration:**
- Branch Sources: Git
- Project Repository: https://github.com/YOUR_USERNAME/my-jenkins-app.git
- Credentials: github-credentials
- Behaviors:
  - Discover branches
  - Discover pull requests from origin
- Build Configuration:
  - Mode: by Jenkinsfile
  - Script Path: Jenkinsfile

**Save and Scan Repository**

Watch Jenkins:
- Discover branches
- Create jobs for each branch
- Execute Jenkinsfile

✅ **Checkpoint:** Multibranch pipeline created from Git

---

## Exercise 4: Configure GitHub Webhook

**Objective:** Automatic builds on push

### Step 1: Configure Jenkins

**Manage Jenkins** > **Configure System**

Find "GitHub" section:
- Add GitHub Server
- API URL: https://api.github.com
- Credentials: github-credentials
- Test connection

### Step 2: Configure Repository Webhook

In GitHub repository:
1. Settings > Webhooks > Add webhook
2. Payload URL: `http://YOUR_JENKINS_URL/github-webhook/`
3. Content type: application/json
4. Events: "Just the push event"
5. Active: ✓

### Step 3: Configure Job

Edit multibranch pipeline:
- **Build Triggers:**
  - ☑ GitHub hook trigger for GITScm polling

### Step 4: Test Webhook

```bash
# Make a change
echo "# Updated" >> README.md
git add README.md
git commit -m "Test webhook"
git push

# Watch Jenkins - build should start automatically!
```

✅ **Checkpoint:** Pushes trigger builds automatically

---

## Exercise 5: Branch-Based Deployment

**Objective:** Different behavior per branch

Update Jenkinsfile:

```groovy
pipeline {
    agent any
    
    environment {
        DEPLOY_ENV = "${getBranchEnvironment()}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "Branch: ${env.BRANCH_NAME}"
                echo "Deploy to: ${DEPLOY_ENV}"
            }
        }
        
        stage('Build') {
            steps {
                sh 'echo "Building..."'
                sh 'python3 -m py_compile app.py'
            }
        }
        
        stage('Test') {
            steps {
                sh 'python3 test_app.py'
            }
        }
        
        stage('Deploy to Dev') {
            when {
                branch 'develop'
            }
            steps {
                echo 'Deploying to development...'
                sh 'echo "Deployed to DEV at $(date)"'
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'staging'
            }
            steps {
                echo 'Deploying to staging...'
                sh 'echo "Deployed to STAGING at $(date)"'
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                echo 'Deploying to production...'
                sh 'echo "Deployed to PROD at $(date)"'
            }
        }
    }
    
    post {
        success {
            echo "✅ Build successful for ${env.BRANCH_NAME}"
        }
    }
}

def getBranchEnvironment() {
    switch(env.BRANCH_NAME) {
        case 'main': return 'production'
        case 'staging': return 'staging'
        case 'develop': return 'development'
        default: return 'feature'
    }
}
```

**Test with branches:**
```bash
# Create develop branch
git checkout -b develop
git push -u origin develop

# Create staging branch
git checkout -b staging
git push -u origin staging

# Trigger builds and observe different deployment stages
```

✅ **Checkpoint:** Different branches deploy to different environments

---

## Exercise 6: Pull Request Builder

**Objective:** Validate PRs before merge

Update Jenkinsfile for PR validation:

```groovy
pipeline {
    agent any
    
    stages {
        stage('PR Validation') {
            when {
                changeRequest()
            }
            steps {
                echo "Validating PR #${env.CHANGE_ID}"
                echo "Source: ${env.CHANGE_BRANCH}"
                echo "Target: ${env.CHANGE_TARGET}"
                echo "Author: ${env.CHANGE_AUTHOR}"
            }
        }
        
        stage('Build') {
            steps {
                sh 'echo "Building application..."'
            }
        }
        
        stage('Test') {
            steps {
                sh 'python3 test_app.py'
            }
        }
        
        stage('Code Quality') {
            when {
                changeRequest()
            }
            steps {
                echo 'Running code quality checks...'
                sh '''
                    # Example: pylint, flake8, etc.
                    echo "Code quality: PASSED"
                '''
            }
        }
        
        stage('Security Scan') {
            when {
                changeRequest()
            }
            steps {
                echo 'Running security scan...'
                sh 'echo "No vulnerabilities found"'
            }
        }
    }
    
    post {
        success {
            script {
                if (env.CHANGE_ID) {
                    echo "✅ PR #${env.CHANGE_ID} is ready to merge"
                }
            }
        }
        failure {
            script {
                if (env.CHANGE_ID) {
                    echo "❌ PR #${env.CHANGE_ID} has issues"
                }
            }
        }
    }
}
```

**Test:**
1. Create feature branch
2. Make changes
3. Open pull request on GitHub
4. Watch Jenkins validate PR

✅ **Checkpoint:** PRs are automatically validated

---

## Exercise 7: Git Operations in Pipeline

**Objective:** Advanced Git commands

```groovy
pipeline {
    agent any
    
    stages {
        stage('Git Info') {
            steps {
                script {
                    // Get commit info
                    def commitHash = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
                    def commitMsg = sh(returnStdout: true, script: 'git log -1 --pretty=%B').trim()
                    def commitAuthor = sh(returnStdout: true, script: 'git log -1 --pretty=%an').trim()
                    
                    echo "Commit: ${commitHash}"
                    echo "Message: ${commitMsg}"
                    echo "Author: ${commitAuthor}"
                    
                    // Create tag
                    sh "git tag build-${BUILD_NUMBER}"
                    
                    // Push tag (with credentials)
                    withCredentials([usernamePassword(
                        credentialsId: 'github-credentials',
                        usernameVariable: 'GIT_USER',
                        passwordVariable: 'GIT_PASS'
                    )]) {
                        sh '''
                            git config user.name "Jenkins"
                            git config user.email "jenkins@example.com"
                            git push https://${GIT_USER}:${GIT_PASS}@github.com/YOUR_USERNAME/my-jenkins-app.git \
                              build-${BUILD_NUMBER}
                        '''
                    }
                }
            }
        }
    }
}
```

✅ **Checkpoint:** Git operations execute within pipeline

---

## Validation

Verify all integrations:

```bash
# 1. Repository accessible
git clone https://github.com/YOUR_USERNAME/my-jenkins-app.git

# 2. Webhook delivers
curl -X POST http://YOUR_JENKINS_URL/github-webhook/

# 3. Multibranch discovers branches
# Check Jenkins UI

# 4. PR builder works
# Create and check PR
```

---

## Troubleshooting

**Issue:** Webhook not triggering  
**Solution:**
- Check webhook deliveries in GitHub
- Verify Jenkins URL is accessible
- Check firewall rules

**Issue:** Credentials not working  
**Solution:**
- Regenerate GitHub token
- Update credentials in Jenkins
- Check token permissions

**Issue:** Branch not discovered  
**Solution:**
- Manual scan: "Scan Multibranch Pipeline Now"
- Check branch filters
- Verify Jenkinsfile exists in branch

---

## Summary

What you learned:
- ✅ Integrate Jenkins with Git
- ✅ Configure secure credentials
- ✅ Create multibranch pipelines
- ✅ Set up GitHub webhooks
- ✅ Implement branch strategies
- ✅ Validate pull requests
- ✅ Perform Git operations in pipelines

---

**Previous:** [First Pipeline](../lab-02-first-pipeline/) | **Next:** [Docker Integration](../lab-04-docker-integration/)

