# Project 5: GitOps with ArgoCD

Implement GitOps methodology using ArgoCD for declarative, Git-based deployments.

## 📋 Overview

- **Git as Source of Truth:** All configs in Git
- **Automated Sync:** ArgoCD watches Git and syncs to cluster
- **Declarative Deployments:** Kubernetes manifests define desired state
- **Self-Healing:** Auto-correction if cluster state drifts
- **Rollback:** Git revert = automatic rollback

## 🏗️ Architecture

```
┌──────────────┐
│  Git Repo    │
│  (Manifests) │
└──────┬───────┘
       │
       │ Watches
       ▼
┌──────────────┐      ┌─────────────┐
│   ArgoCD     │─────▶│  Kubernetes │
│   Server     │Syncs │   Cluster   │
└──────────────┘      └─────────────┘
       │
       │ Monitors
       ▼
┌──────────────┐
│ Application  │
│   Status     │
└──────────────┘
```

## 📁 Project Structure

```
project-05-gitops/
├── README.md
├── argocd/
│   ├── application.yaml
│   └── argocd-install.yaml
├── manifests/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── configmap.yaml
├── environments/
│   ├── dev/
│   ├── staging/
│   └── production/
└── Jenkinsfile
```

## 🚀 Quick Start

### Step 1: Install ArgoCD

```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Visit: https://localhost:8080
```

### Step 2: Create Application

```bash
# Apply ArgoCD application
kubectl apply -f argocd/application.yaml

# Or via CLI
argocd app create my-app \
  --repo https://github.com/user/repo.git \
  --path manifests \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace default
```

### Step 3: Sync Application

```bash
# Manual sync
argocd app sync my-app

# Enable auto-sync
argocd app set my-app --sync-policy automated
```

## 📝 ArgoCD Application Config

```yaml
# argocd/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-gitops-app
  namespace: argocd
spec:
  project: default
  
  source:
    repoURL: https://github.com/username/project-05-gitops.git
    targetRevision: main
    path: manifests
  
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

## 🔄 GitOps Workflow

### Update Application

```bash
# 1. Update manifest in Git
vim manifests/deployment.yaml
# Change image version: v1.0 → v2.0

# 2. Commit and push
git add manifests/deployment.yaml
git commit -m "Update to v2.0"
git push origin main

# 3. ArgoCD auto-syncs (if enabled)
# Or manually sync:
argocd app sync my-app
```

### Rollback

```bash
# Option 1: Git revert
git revert HEAD
git push origin main

# Option 2: ArgoCD rollback
argocd app rollback my-app

# Option 3: Sync to specific revision
argocd app sync my-app --revision <commit-hash>
```

## 📝 Jenkins Integration

```groovy
pipeline {
    agent any
    
    stages {
        stage('Update Manifests') {
            steps {
                script {
                    // Update image version in manifest
                    sh """
                        sed -i 's|image:.*|image: myapp:${BUILD_NUMBER}|' manifests/deployment.yaml
                        git add manifests/deployment.yaml
                        git commit -m "Update image to ${BUILD_NUMBER}"
                        git push origin main
                    """
                }
            }
        }
        
        stage('Trigger ArgoCD Sync') {
            steps {
                sh """
                    argocd app sync my-app --grpc-web
                    argocd app wait my-app --health
                """
            }
        }
        
        stage('Verify Deployment') {
            steps {
                sh """
                    kubectl rollout status deployment/my-app
                    curl -f http://my-app/health
                """
            }
        }
    }
}
```

## 🎯 GitOps Principles

1. **Declarative:** Everything defined in Git
2. **Versioned:** Git history = deployment history
3. **Immutable:** New state, not modifications
4. **Automated:** Changes trigger automatic sync
5. **Auditable:** Git log shows all changes

## 🔒 Security Features

```yaml
# Private repository access
spec:
  source:
    repoURL: git@github.com:private/repo.git
    sshPrivateKeySecret:
      name: git-ssh-key
      key: sshPrivateKey

# RBAC for ArgoCD
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-rbac-cm
data:
  policy.csv: |
    p, role:developer, applications, get, */*, allow
    p, role:developer, applications, sync, */*, allow
    g, developers, role:developer
```

## 📊 Monitoring

```bash
# Application health
argocd app get my-app

# Sync status
argocd app list

# View history
argocd app history my-app

# Get logs
kubectl logs -n argocd deployment/argocd-server
```

## ✅ What You Learned

- ✅ GitOps principles and practices
- ✅ ArgoCD installation and configuration
- ✅ Declarative Kubernetes deployments
- ✅ Git-based rollbacks
- ✅ Automated synchronization
- ✅ Self-healing applications

## 📚 Advanced Topics

- **Multi-cluster deployments:** Deploy to multiple clusters
- **App of Apps pattern:** Manage multiple applications
- **Helm charts:** Use Helm with ArgoCD
- **Kustomize:** Environment-specific overlays
- **Progressive delivery:** Canary + GitOps

## 🎓 Best Practices

✅ **Separate repos:** App code vs. manifests  
✅ **Branch protection:** Require reviews for main  
✅ **Automated testing:** Validate manifests in CI  
✅ **Notifications:** Slack/email on sync failures  
✅ **Backup:** Regular Git backups  
✅ **Documentation:** Document all changes  

---

**Congratulations!** You've mastered GitOps with ArgoCD! 🎉

## 📚 Complete Integration Learning Path

You've now completed all 5 integration projects:

1. ✅ [Simple CI/CD](../project-01-simple-cicd/) - Foundation
2. ✅ [Microservices](../project-02-microservices/) - Architecture
3. ✅ [Multi-Environment](../project-03-multi-env/) - Promotion
4. ✅ [Blue-Green](../project-04-blue-green/) - Zero-downtime
5. ✅ [GitOps](../project-05-gitops/) - Modern practices

**You're now ready for production DevOps work!** 🚀

