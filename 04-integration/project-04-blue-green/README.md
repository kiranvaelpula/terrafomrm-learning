# Project 4: Blue-Green Deployment

Implement zero-downtime deployments using blue-green strategy.

## 📋 Overview

- **Zero Downtime:** Switch traffic between environments
- **Quick Rollback:** Instant switch back to previous version
- **Risk Mitigation:** Test new version before switching traffic
- **Gradual Migration:** Optional percentage-based traffic shifting

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
┌──────▼──────────┐
│  Load Balancer  │
│   (Traffic      │
│    Switching)   │
└────┬─────┬──────┘
     │     │
     │     │ (Switch)
     │     │
┌────▼─┐ ┌─▼────┐
│ Blue │ │Green │
│ v1.0 │ │ v2.0 │
└──────┘ └──────┘
(Active) (Standby)
```

## 📁 Project Structure

```
project-04-blue-green/
├── README.md
├── app/
│   ├── app.py
│   └── requirements.txt
├── k8s/
│   ├── blue-deployment.yaml
│   ├── green-deployment.yaml
│   └── service.yaml
├── Dockerfile
└── Jenkinsfile
```

## 🚀 Deployment Process

### Step 1: Deploy Green (New Version)
```bash
# Deploy new version to green environment
kubectl apply -f k8s/green-deployment.yaml

# Wait for rollout
kubectl rollout status deployment/app-green
```

### Step 2: Smoke Test Green
```bash
# Test green environment
curl http://green-service/health
curl http://green-service/
```

### Step 3: Switch Traffic
```bash
# Update service to point to green
kubectl patch service app -p '{"spec":{"selector":{"version":"green"}}}'
```

### Step 4: Cleanup Blue (Optional)
```bash
# Keep blue for quick rollback, or scale down
kubectl scale deployment/app-blue --replicas=0
```

## 📝 Jenkinsfile

```groovy
pipeline {
    agent any
    
    environment {
        CURRENT_COLOR = ''
        NEW_COLOR = ''
    }
    
    stages {
        stage('Determine Colors') {
            steps {
                script {
                    // Get current active color
                    CURRENT_COLOR = sh(returnStdout: true, 
                        script: 'kubectl get svc app -o jsonpath="{.spec.selector.version}"'
                    ).trim()
                    NEW_COLOR = (CURRENT_COLOR == 'blue') ? 'green' : 'blue'
                }
            }
        }
        
        stage('Deploy New Version') {
            steps {
                sh "kubectl apply -f k8s/${NEW_COLOR}-deployment.yaml"
                sh "kubectl rollout status deployment/app-${NEW_COLOR}"
            }
        }
        
        stage('Smoke Test') {
            steps {
                sh "curl -f http://app-${NEW_COLOR}/health"
            }
        }
        
        stage('Switch Traffic') {
            steps {
                input 'Switch traffic to new version?'
                sh "kubectl patch svc app -p '{\"spec\":{\"selector\":{\"version\":\"${NEW_COLOR}\"}}}'"
            }
        }
        
        stage('Verify') {
            steps {
                sh 'sleep 10'
                sh 'curl -f http://app-service/health'
            }
        }
    }
    
    post {
        failure {
            sh "kubectl patch svc app -p '{\"spec\":{\"selector\":{\"version\":\"${CURRENT_COLOR}\"}}}'"
        }
    }
}
```

## 🔄 Rollback Process

```bash
# Immediate rollback - switch traffic back
kubectl patch service app -p '{"spec":{"selector":{"version":"blue"}}}'

# Verify rollback
curl http://app-service/health
```

## ✅ What You Learned

- ✅ Blue-green deployment strategy
- ✅ Zero-downtime deployments
- ✅ Traffic switching techniques
- ✅ Quick rollback mechanisms
- ✅ Production deployment safety

## 📚 Next Steps

- Implement canary deployments
- Add automated rollback triggers
- Move to [Project 5: GitOps](../project-05-gitops/)

