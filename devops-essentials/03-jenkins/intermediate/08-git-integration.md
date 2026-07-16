# Git Integration with Jenkins

## Overview

Git integration is fundamental to Jenkins CI/CD. This guide covers connecting Jenkins with GitHub, GitLab, and Bitbucket, setting up webhooks, and implementing automated build triggers.

## Prerequisites

Before integrating Git:
- Jenkins installed and running
- Git installed on Jenkins server
- Git plugin installed in Jenkins
- Access to Git repository (credentials)

## Installing Git Plugin

```
Manage Jenkins → Manage Plugins → Available
Search: Git Plugin
Install without restart
```

**Essential Git-Related Plugins:**
- Git Plugin
- GitHub Plugin
- GitLab Plugin
- Bitbucket Plugin
- Git Parameter Plugin
- GitHub Branch Source Plugin

## Basic Git Configuration

### 1. Configure Git in Jenkins

**Manage Jenkins → Global Tool Configuration**

```
Git installations:
  Name: Default
  Path to Git executable: git
  ☐ Install automatically
```

### 2. Add Git Credentials

**Manage Jenkins → Manage Credentials → Global → Add Credentials**

**Username/Password:**
```
Kind: Username with password
Username: your-git-username
Password: personal-access-token (not actual password!)
ID: github-credentials
Description: GitHub access
```

**SSH Key:**
```
Kind: SSH Username with private key
Username: git
Private Key: Enter directly
[Paste your private key]
ID: git-ssh-key
Description: Git SSH Key
```

## GitHub Integration

### Method 1: Basic Checkout in Pipeline

```groovy
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/username/repo.git',
                    credentialsId: 'github-credentials'
            }
        }
        
        stage('Build') {
            steps {
                sh 'npm install'
                sh 'npm run build'
            }
        }
    }
}
```

### Method 2: SCM Checkout (Recommended)

```groovy
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
    }
}
```

**Job Configuration:**
- Pipeline → Definition: Pipeline script from SCM
- SCM: Git
- Repository URL: `https://github.com/username/repo.git`
- Credentials: Select from dropdown
- Branch: `*/main` or `*/master`
- Script Path: `Jenkinsfile`

### Method 3: Multibranch Pipeline (Best Practice)

**Create Multibranch Pipeline:**
1. New Item → Multibranch Pipeline
2. Branch Sources → Add source → GitHub
3. Repository HTTPS URL
4. Credentials
5. Behaviors: Discover branches, Discover pull requests

```groovy
// Jenkinsfile in repository
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                echo "Building branch: ${env.BRANCH_NAME}"
                sh 'npm install && npm run build'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to production'
            }
        }
    }
}
```

### GitHub Webhook Setup

**Step 1: Configure Jenkins Job**

```groovy
pipeline {
    agent any
    
    triggers {
        githubPush()  // Enable GitHub webhook trigger
    }
    
    stages {
        stage('Build') {
            steps {
                checkout scm
                sh 'npm run build'
            }
        }
    }
}
```

**Step 2: Configure GitHub Repository**

```
GitHub Repository → Settings → Webhooks → Add webhook

Payload URL: http://your-jenkins-url/github-webhook/
Content type: application/json
Secret: (optional but recommended)

Which events?
● Just the push event
Or select:
  ✓ Pushes
  ✓ Pull requests
  ✓ Branch or tag creation

Active: ✓
```

**Test Webhook:**
```bash
# Make a commit
git add .
git commit -m "Test webhook"
git push origin main

# Build should trigger automatically in Jenkins
```

### GitHub Status Notifications

Report build status back to GitHub:

```groovy
pipeline {
    agent any
    
    options {
        githubProjectProperty(
            projectUrlStr: 'https://github.com/username/repo'
        )
    }
    
    stages {
        stage('Build') {
            steps {
                checkout scm
                sh 'npm run build'
            }
        }
    }
    
    post {
        success {
            githubNotify status: 'SUCCESS',
                        description: 'Build succeeded',
                        context: 'continuous-integration/jenkins'
        }
        failure {
            githubNotify status: 'FAILURE',
                        description: 'Build failed',
                        context: 'continuous-integration/jenkins'
        }
    }
}
```

### Pull Request Builder

Automatically build and test PRs:

**Install Plugin:**
```
GitHub Pull Request Builder Plugin
```

**Pipeline for PR:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('PR Validation') {
            when {
                changeRequest()  // Only run on PRs
            }
            steps {
                echo "Building PR #${env.CHANGE_ID}"
                echo "PR Title: ${env.CHANGE_TITLE}"
                echo "PR Author: ${env.CHANGE_AUTHOR}"
                
                checkout scm
                sh 'npm install'
                sh 'npm test'
            }
        }
        
        stage('Main Branch Build') {
            when {
                branch 'main'
            }
            steps {
                echo 'Building main branch'
                checkout scm
                sh 'npm run build'
            }
        }
    }
    
    post {
        always {
            // Comment on PR
            script {
                if (env.CHANGE_ID) {
                    pullRequest.comment("Build ${currentBuild.result}")
                }
            }
        }
    }
}
```

## GitLab Integration

### Basic GitLab Configuration

**Install Plugin:**
```
GitLab Plugin
```

**Configure GitLab Connection:**
```
Manage Jenkins → Configure System → GitLab

Connection name: GitLab
GitLab host URL: https://gitlab.com
Credentials: Add GitLab API token
Test Connection
```

### GitLab Pipeline

```groovy
pipeline {
    agent any
    
    options {
        gitLabConnection('GitLab')
    }
    
    triggers {
        gitlab(
            triggerOnPush: true,
            triggerOnMergeRequest: true,
            branchFilterType: 'All'
        )
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                gitlabCommitStatus('build') {
                    sh 'npm install'
                    sh 'npm run build'
                }
            }
        }
        
        stage('Test') {
            steps {
                gitlabCommitStatus('test') {
                    sh 'npm test'
                }
            }
        }
    }
    
    post {
        success {
            updateGitlabCommitStatus name: 'build', state: 'success'
        }
        failure {
            updateGitlabCommitStatus name: 'build', state: 'failed'
        }
    }
}
```

### GitLab Webhook Setup

```
GitLab Project → Settings → Webhooks

URL: http://your-jenkins-url/project/job-name
Secret Token: (from Jenkins job configuration)

Trigger:
  ✓ Push events
  ✓ Merge request events
  ✓ Tag push events

Enable SSL verification: ✓ (if using HTTPS)
```

### GitLab Merge Request Builder

```groovy
pipeline {
    agent any
    
    stages {
        stage('MR Validation') {
            when {
                expression {
                    env.gitlabActionType == 'MERGE' || env.gitlabActionType == 'NOTE'
                }
            }
            steps {
                echo "Merge Request from: ${env.gitlabSourceBranch}"
                echo "Merge Request to: ${env.gitlabTargetBranch}"
                echo "MR Author: ${env.gitlabUserName}"
                
                checkout scm
                sh 'npm install && npm test'
            }
        }
    }
    
    post {
        success {
            addGitLabMRComment(comment: '✅ Build succeeded!')
        }
        failure {
            addGitLabMRComment(comment: '❌ Build failed!')
        }
    }
}
```

## Bitbucket Integration

### Bitbucket Cloud

**Install Plugin:**
```
Bitbucket Plugin
```

**Pipeline:**
```groovy
pipeline {
    agent any
    
    triggers {
        bitbucketPush()
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://bitbucket.org/workspace/repo.git',
                    credentialsId: 'bitbucket-credentials'
            }
        }
        
        stage('Build') {
            steps {
                sh 'npm install && npm run build'
            }
        }
    }
    
    post {
        always {
            // Send build status to Bitbucket
            bitbucketStatusNotify(
                buildState: currentBuild.result,
                buildKey: env.JOB_NAME,
                buildName: "Build #${env.BUILD_NUMBER}"
            )
        }
    }
}
```

**Bitbucket Webhook:**
```
Bitbucket Repository → Settings → Webhooks → Add webhook

Title: Jenkins CI
URL: http://your-jenkins-url/bitbucket-hook/
Triggers:
  ✓ Repository push
  ✓ Pull request created
  ✓ Pull request updated
```

### Bitbucket Server

```groovy
pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: 'ssh://git@bitbucket.server.com/project/repo.git',
                        credentialsId: 'bitbucket-ssh-key'
                    ]]
                ])
            }
        }
        
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
    }
}
```

## Advanced Git Operations

### Clone Specific Branch

```groovy
stage('Checkout Branch') {
    steps {
        git branch: 'develop',
            url: 'https://github.com/user/repo.git',
            credentialsId: 'github-creds'
    }
}
```

### Clone with Depth (Shallow Clone)

```groovy
stage('Shallow Clone') {
    steps {
        checkout([
            $class: 'GitSCM',
            branches: [[name: '*/main']],
            extensions: [
                [$class: 'CloneOption', depth: 1, shallow: true]
            ],
            userRemoteConfigs: [[
                url: 'https://github.com/user/repo.git',
                credentialsId: 'github-creds'
            ]]
        ])
    }
}
```

### Checkout Multiple Repositories

```groovy
stage('Checkout Repos') {
    steps {
        dir('backend') {
            git branch: 'main',
                url: 'https://github.com/user/backend.git',
                credentialsId: 'github-creds'
        }
        
        dir('frontend') {
            git branch: 'main',
                url: 'https://github.com/user/frontend.git',
                credentialsId: 'github-creds'
        }
    }
}
```

### Git Tag Operations

```groovy
stage('Create Tag') {
    steps {
        script {
            def tag = "v1.0.${BUILD_NUMBER}"
            
            sh """
                git config user.email "jenkins@company.com"
                git config user.name "Jenkins CI"
                git tag -a ${tag} -m "Release ${tag}"
                git push origin ${tag}
            """
        }
    }
}
```

### Git Commit and Push

```groovy
stage('Commit Changes') {
    steps {
        script {
            sh """
                git config user.email "jenkins@company.com"
                git config user.name "Jenkins CI"
                git add .
                git commit -m "Auto-update from build ${BUILD_NUMBER}"
                git push origin main
            """
        }
    }
}
```

### Submodule Handling

```groovy
stage('Checkout with Submodules') {
    steps {
        checkout([
            $class: 'GitSCM',
            branches: [[name: '*/main']],
            extensions: [
                [$class: 'SubmoduleOption',
                 disableSubmodules: false,
                 recursiveSubmodules: true,
                 trackingSubmodules: false]
            ],
            userRemoteConfigs: [[
                url: 'https://github.com/user/repo.git',
                credentialsId: 'github-creds'
            ]]
        ])
    }
}
```

## Branch Strategies

### Feature Branch Workflow

```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                echo "Building branch: ${env.BRANCH_NAME}"
                sh 'npm install && npm run build'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
        
        stage('Deploy to Dev') {
            when {
                branch 'develop'
            }
            steps {
                echo 'Deploying to dev environment'
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'release/*'
            }
            steps {
                echo 'Deploying to staging'
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to production'
            }
        }
    }
}
```

### GitFlow Integration

```groovy
pipeline {
    agent any
    
    environment {
        DEPLOY_ENV = getDeployEnvironment(env.BRANCH_NAME)
    }
    
    stages {
        stage('Build') {
            steps {
                echo "Building for: ${DEPLOY_ENV}"
                sh 'npm run build'
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    switch(DEPLOY_ENV) {
                        case 'development':
                            echo 'Deploy to dev'
                            break
                        case 'staging':
                            echo 'Deploy to staging'
                            break
                        case 'production':
                            echo 'Deploy to production'
                            break
                        default:
                            echo 'No deployment'
                    }
                }
            }
        }
    }
}

def getDeployEnvironment(branch) {
    if (branch == 'develop') {
        return 'development'
    } else if (branch.startsWith('release/')) {
        return 'staging'
    } else if (branch == 'main' || branch == 'master') {
        return 'production'
    }
    return 'none'
}
```

## Git Parameters

Dynamic branch selection:

**Install Plugin:**
```
Git Parameter Plugin
```

**Configuration:**
```groovy
properties([
    parameters([
        gitParameter(
            name: 'BRANCH',
            type: 'PT_BRANCH',
            defaultValue: 'main',
            description: 'Select branch to build'
        )
    ])
])

pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                git branch: "${params.BRANCH}",
                    url: 'https://github.com/user/repo.git',
                    credentialsId: 'github-creds'
            }
        }
        
        stage('Build') {
            steps {
                echo "Building branch: ${params.BRANCH}"
                sh 'npm run build'
            }
        }
    }
}
```

## Working with Git Information

### Extract Git Information

```groovy
stage('Git Info') {
    steps {
        script {
            // Get commit hash
            env.GIT_COMMIT_SHORT = sh(
                script: "git rev-parse --short HEAD",
                returnStdout: true
            ).trim()
            
            // Get commit message
            env.GIT_COMMIT_MSG = sh(
                script: "git log -1 --pretty=%B",
                returnStdout: true
            ).trim()
            
            // Get commit author
            env.GIT_AUTHOR = sh(
                script: "git log -1 --pretty=%an",
                returnStdout: true
            ).trim()
            
            // Get branch name
            env.GIT_BRANCH = sh(
                script: "git rev-parse --abbrev-ref HEAD",
                returnStdout: true
            ).trim()
            
            echo "Commit: ${env.GIT_COMMIT_SHORT}"
            echo "Message: ${env.GIT_COMMIT_MSG}"
            echo "Author: ${env.GIT_AUTHOR}"
            echo "Branch: ${env.GIT_BRANCH}"
        }
    }
}
```

### Version from Git Tag

```groovy
stage('Get Version') {
    steps {
        script {
            env.VERSION = sh(
                script: "git describe --tags --always",
                returnStdout: true
            ).trim()
            
            echo "Building version: ${env.VERSION}"
        }
    }
}
```

## Troubleshooting

### Issue: Webhook Not Triggering

**Check:**
1. Jenkins accessible from internet?
2. Webhook URL correct?
3. Webhook delivery successful in Git platform?
4. Jenkins job configured for webhooks?

**Test Webhook:**
```bash
# GitHub
curl -X POST http://your-jenkins-url/github-webhook/

# GitLab
curl -X POST http://your-jenkins-url/project/job-name \\
  -H "X-Gitlab-Token: your-token"
```

### Issue: Authentication Failed

**Solutions:**
```groovy
// Use personal access token, not password
// GitHub: Settings → Developer settings → Personal access tokens
// GitLab: Settings → Access Tokens
// Bitbucket: Settings → App passwords
```

### Issue: SSL Certificate Error

**Solution:**
```groovy
// Temporarily disable (not recommended for production)
stage('Checkout') {
    steps {
        checkout([
            $class: 'GitSCM',
            extensions: [
                [$class: 'GitSCMStatusChecksExtension',
                 skip: true]
            ],
            userRemoteConfigs: [[
                url: 'https://github.com/user/repo.git'
            ]]
        ])
    }
}
```

### Issue: Large Repository Timeout

**Solution:**
```groovy
// Use shallow clone
stage('Shallow Clone') {
    steps {
        checkout([
            $class: 'GitSCM',
            extensions: [
                [$class: 'CloneOption',
                 depth: 1,
                 noTags: true,
                 shallow: true,
                 timeout: 30]
            ],
            userRemoteConfigs: [[url: 'https://github.com/user/repo.git']]
        ])
    }
}
```

## Best Practices

### 1. Use SSH Keys Over Passwords
```groovy
// More secure, no password expiration
git url: 'git@github.com:user/repo.git',
    credentialsId: 'github-ssh-key'
```

### 2. Shallow Clone for Speed
```groovy
// Faster for large repositories
extensions: [[$class: 'CloneOption', depth: 1, shallow: true]]
```

### 3. Clean Checkout
```groovy
stage('Clean Checkout') {
    steps {
        cleanWs()  // Clean workspace first
        checkout scm
    }
}
```

### 4. Use Multibranch Pipelines
- Automatic branch discovery
- PR/MR support
- Better branch management

### 5. Implement Branch Protection
- Require PR reviews
- Status checks before merge
- Prevent force push

## Summary

You've learned comprehensive Git integration with Jenkins including:
- GitHub, GitLab, and Bitbucket setup
- Webhook configuration
- Branch strategies
- PR/MR automation
- Advanced Git operations
- Troubleshooting common issues

**Key Points:**
- Use webhooks for instant builds
- Multibranch pipelines for complex workflows
- Secure credentials properly
- Implement branch strategies
- Status reporting back to Git platforms

---

**Previous:** [← Declarative vs Scripted](07-declarative-scripted.md) | **Next:** [Docker Integration →](09-docker-integration.md)
