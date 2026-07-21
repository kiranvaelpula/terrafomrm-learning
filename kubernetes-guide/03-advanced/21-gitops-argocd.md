# Module 21: GitOps with ArgoCD

## 🎯 Install ArgoCD

```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods
kubectl get pods -n argocd -w

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Access: https://localhost:8080
# Username: admin
# Password: <from above command>
```

## 📝 Create Application

### Method 1: UI
1. Open ArgoCD UI
2. Click "+ NEW APP"
3. Fill in details
4. Click CREATE

### Method 2: CLI

```bash
# Install ArgoCD CLI
brew install argocd  # macOS
choco install argocd # Windows

# Login
argocd login localhost:8080

# Create app
argocd app create myapp \
  --repo https://github.com/myorg/myrepo \
  --path kubernetes/manifests \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace default
```

### Method 3: YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myrepo
    targetRevision: HEAD
    path: kubernetes/manifests
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

```bash
kubectl apply -f application.yaml
```

## 🔄 Sync Strategies

### Manual Sync
```yaml
syncPolicy: {}
```

### Automatic Sync
```yaml
syncPolicy:
  automated:
    prune: true      # Delete resources not in Git
    selfHeal: true   # Force sync if manual changes
```

### Sync Windows
```yaml
syncPolicy:
  syncOptions:
  - CreateNamespace=true
  automated:
    prune: true
  retry:
    limit: 5
    backoff:
      duration: 5s
      factor: 2
      maxDuration: 3m
```

## 📁 App of Apps Pattern

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/apps
    targetRevision: HEAD
    path: apps
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Repository structure:
```
apps/
├── frontend.yaml
├── backend.yaml
├── database.yaml
└── monitoring.yaml
```

## 🎯 Multi-Environment Setup

```yaml
# apps/prod/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-prod
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/myorg/myapp
    targetRevision: v1.2.3
    path: manifests/overlays/prod
  destination:
    namespace: production
---
# apps/staging/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-staging
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/myorg/myapp
    targetRevision: main
    path: manifests/overlays/staging
  destination:
    namespace: staging
```

## 🔧 Kustomize Integration

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
spec:
  source:
    repoURL: https://github.com/myorg/myapp
    path: kustomize/overlays/production
    kustomize:
      images:
      - myapp:v1.2.3
```

## 📊 Health Checks

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
spec:
  # ...
  ignoreDifferences:
  - group: apps
    kind: Deployment
    jsonPointers:
    - /spec/replicas
```

## 🛠️ CLI Commands

```bash
# List applications
argocd app list

# Get application details
argocd app get myapp

# Sync application
argocd app sync myapp

# Rollback
argocd app rollback myapp

# Delete application
argocd app delete myapp

# Watch sync status
argocd app wait myapp --health
```

## ⏭️ Next: [Module 22: Multi-Cluster Management](./22-multi-cluster.md)
