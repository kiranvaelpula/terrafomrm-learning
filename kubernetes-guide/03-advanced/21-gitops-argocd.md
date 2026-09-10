# Module 21: GitOps with ArgoCD

## Understanding GitOps and ArgoCD (Intuition First)

Most teams deploy by running kubectl apply from a laptop or a CI pipeline that pushes changes into the cluster. The problem: the cluster's actual state slowly drifts from any written-down source. Who changed that replica count? Was that hotfix ever committed? GitOps fixes this by making a Git repository the single source of truth for what your cluster should look like.

The core idea is a shift from push to pull. Instead of pushing changes into the cluster, an agent living inside the cluster (ArgoCD) continuously pulls from Git and reconciles the cluster to match what's declared. You deploy by committing to Git; the agent applies it. Every change is a reviewed commit with a full audit trail.

This gives two properties operators love. Drift detection and self-healing: ArgoCD compares live state against Git and reverts manual changes back to the declared state. And trivial rollback: since every version is a Git commit, rolling back is just reverting a commit.

ArgoCD's central object is the Application, linking a source (repo, path, revision) to a destination (cluster, namespace). Its sync policy can be manual (approve) or automated, with prune (delete resources removed from Git) and selfHeal (undo drift).

At scale, the App of Apps pattern uses one root Application to manage many child Applications, and one ArgoCD can target dev, staging, and prod from the same repo. The mental model: describe desired state in Git, let an in-cluster agent make reality match it - continuously and auditably.

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

## Interview Quick Points

- GitOps = Git is the single source of truth for cluster/app desired state
- Shift from push (kubectl apply) to pull (an in-cluster agent syncs from Git)
- You deploy by committing to Git, not by running commands - full audit trail via PRs
- ArgoCD's core object is the Application (source repo/path/revision to destination cluster/namespace)
- Drift detection + self-healing: ArgoCD reverts manual changes back to the Git-declared state
- Rollback = revert a Git commit - no special tooling needed
- Sync policies: manual (approve) vs automated; prune (delete removed resources) and selfHeal (undo drift)
- App of Apps pattern: one root Application manages many child Applications
- One ArgoCD can deploy to multiple clusters (dev/staging/prod) from one repo
- Supports plain manifests, Helm, and Kustomize as sources
- Benefits: consistency, auditability, easy rollback, no config drift
- Flux is a comparable CNCF GitOps alternative to ArgoCD
