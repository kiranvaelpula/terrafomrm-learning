# Project 3: Multi-Environment Deployment

Deploy applications across Development, Staging, and Production environments with proper promotion workflows.

## 📋 Overview

- **3 Environments:** Dev, Staging, Production
- **Environment-Specific Configs:** Different settings per environment
- **Approval Gates:** Manual approval for production
- **Promotion Workflow:** Dev → Staging → Production
- **Rollback Capability:** Quick rollback on failure

## 🏗️ Architecture

```
Git Push → Dev (Auto) → Staging (Approval) → Production (Approval)
    ↓            ↓              ↓                    ↓
  Build        Test         Integration          Smoke Test
```

## 📁 Project Structure

```
project-03-multi-env/
├── README.md
├── app/
│   ├── app.py
│   └── requirements.txt
├── config/
│   ├── dev.env
│   ├── staging.env
│   └── production.env
├── k8s/
│   ├── dev/
│   ├── staging/
│   └── production/
├── Dockerfile
└── Jenkinsfile
```

## 🚀 Quick Start

```bash
# Deploy to dev (automatic)
git push origin develop

# Promote to staging (requires approval)
# Trigger in Jenkins UI

# Promote to production (requires approval)
# Trigger in Jenkins UI with confirmation
```

## 🔧 Environment Configuration

### Development
- **Auto-deploy:** Yes
- **Replicas:** 1
- **Resources:** Minimal
- **Database:** Dev DB

### Staging
- **Auto-deploy:** No (manual approval)
- **Replicas:** 2
- **Resources:** Medium
- **Database:** Staging DB

### Production
- **Auto-deploy:** No (manual approval + confirmation)
- **Replicas:** 5
- **Resources:** High
- **Database:** Production DB

## 📝 Jenkinsfile Structure

```groovy
pipeline {
    agent any
    
    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'production'])
    }
    
    stages {
        stage('Build') { /* ... */ }
        stage('Test') { /* ... */ }
        
        stage('Deploy to Dev') {
            when { environment name: 'ENVIRONMENT', value: 'dev' }
            steps { /* auto deploy */ }
        }
        
        stage('Deploy to Staging') {
            when { environment name: 'ENVIRONMENT', value: 'staging' }
            steps {
                input 'Deploy to staging?'
                /* deploy */
            }
        }
        
        stage('Deploy to Production') {
            when { environment name: 'ENVIRONMENT', value: 'production' }
            steps {
                input message: 'Deploy to PRODUCTION?', submitter: 'admin'
                /* deploy */
            }
        }
    }
}
```

## ✅ What You Learned

- ✅ Multi-environment management
- ✅ Environment-specific configurations
- ✅ Approval workflows
- ✅ Promotion strategies
- ✅ Production safety practices

## 📚 Next Steps

- Move to [Project 4: Blue-Green Deployment](../project-04-blue-green/)

