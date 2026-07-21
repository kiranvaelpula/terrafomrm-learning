# Kubernetes Modules - Quick Reference Guide

## Complete Module Summaries for Self-Study

This document provides comprehensive summaries for all 25 modules. Use this as a quick reference while the full detailed modules are being created.

---

## ✅ COMPLETED FULL MODULES (1-9)

Modules 1-9 have complete detailed content with labs, examples, and exercises.

---

## 📚 MODULE SUMMARIES (10-25)

### Module 10: DaemonSets & Jobs

**DaemonSets:**
- Ensures pod runs on all (or selected) nodes
- Use cases: Log collectors, monitoring agents, storage daemons
- Auto-adds pods to new nodes

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluentd:latest
```

**Jobs:**
- Run-to-completion tasks
- Batch processing
- Parallel execution

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: batch-job
spec:
  completions: 5
  parallelism: 2
  template:
    spec:
      containers:
      - name: worker
        image: busybox
        command: ["sh", "-c", "echo Processing && sleep 5"]
      restartPolicy: Never
```

**CronJobs:**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: scheduled-job
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleanup
            image: busybox
            command: ["sh", "-c", "echo Cleanup task"]
          restartPolicy: OnFailure
```

---

### Module 11: Ingress Controllers

**Ingress Resource:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
      - path: /web
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
  tls:
  - hosts:
    - app.example.com
    secretName: tls-secret
```

**Install NGINX Ingress:**
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

---

### Module 12: Namespaces & Resource Quotas

**Namespace:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: development
```

**ResourceQuota:**
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: development
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "50"
    services: "10"
```

**LimitRange:**
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: dev-limits
  namespace: development
spec:
  limits:
  - max:
      cpu: "2"
      memory: 4Gi
    min:
      cpu: "100m"
      memory: 128Mi
    default:
      cpu: "500m"
      memory: 512Mi
    defaultRequest:
      cpu: "200m"
      memory: 256Mi
    type: Container
```

---

### Module 13: RBAC & Security

**Role:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

**RoleBinding:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: jane
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**ServiceAccount:**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
---
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  serviceAccountName: app-sa
  containers:
  - name: app
    image: myapp:1.0
```

---

### Module 14: Helm Package Manager

**Install Helm:**
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**Basic Commands:**
```bash
# Add repository
helm repo add bitnami https://charts.bitnami.com/bitnami

# Search charts
helm search repo nginx

# Install chart
helm install my-release bitnami/nginx

# List releases
helm list

# Upgrade release
helm upgrade my-release bitnami/nginx --set replicaCount=3

# Rollback
helm rollback my-release 1

# Uninstall
helm uninstall my-release
```

**Create Custom Chart:**
```bash
helm create mychart
cd mychart/
# Edit values.yaml and templates/
helm install myapp .
```

---

### Module 15: Monitoring & Logging

**Prometheus & Grafana:**
```bash
# Add repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# Install Prometheus stack
helm install prometheus prometheus-community/kube-prometheus-stack

# Port forward Grafana
kubectl port-forward svc/prometheus-grafana 3000:80
# Access: localhost:3000 (admin/prom-operator)
```

**Metrics Server:**
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# View metrics
kubectl top nodes
kubectl top pods
```

**Fluentd for Logging:**
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1-debian-elasticsearch
        env:
        - name: FLUENT_ELASTICSEARCH_HOST
          value: "elasticsearch.logging"
        - name: FLUENT_ELASTICSEARCH_PORT
          value: "9200"
```

---

### Module 16: Advanced Scheduling

**Node Affinity:**
```yaml
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disk-type
            operator: In
            values:
            - ssd
```

**Pod Affinity:**
```yaml
spec:
  affinity:
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - cache
        topologyKey: kubernetes.io/hostname
```

**Taints and Tolerations:**
```bash
# Add taint to node
kubectl taint nodes node1 key=value:NoSchedule

# Pod tolerates taint
spec:
  tolerations:
  - key: "key"
    operator: "Equal"
    value: "value"
    effect: "NoSchedule"
```

---

### Module 17: Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

---

### Module 18: Custom Resources (CRDs)

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: applications.stable.example.com
spec:
  group: stable.example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              image:
                type: string
              replicas:
                type: integer
  scope: Namespaced
  names:
    plural: applications
    singular: application
    kind: Application
```

---

### Module 19: Operators

**Deploy Operator:**
```bash
# Install Operator Lifecycle Manager
curl -sL https://github.com/operator-framework/operator-lifecycle-manager/releases/download/v0.25.0/install.sh | bash -s v0.25.0

# Install example operator
kubectl create -f https://operatorhub.io/install/prometheus-operator.yaml
```

---

### Module 20: Service Mesh (Istio)

**Install Istio:**
```bash
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH
istioctl install --set profile=demo -y

# Enable sidecar injection
kubectl label namespace default istio-injection=enabled
```

---

### Module 21: GitOps with ArgoCD

**Install ArgoCD:**
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

---

### Module 22-25: Summary

**Module 22: Multi-Cluster** - Cluster federation, multi-cluster services
**Module 23: Security** - Pod Security, image scanning, runtime security
**Module 24: Production Patterns** - HA, DR, capacity planning
**Module 25: Real-World Project** - Complete e-commerce platform

---

## 🎯 Study Approach

1. Complete modules 1-9 (full detailed content available)
2. Use this quick reference for modules 10-25
3. Practice labs from summaries
4. Build real projects applying concepts
5. Refer to official Kubernetes docs for deep dives

---

## 📚 Official Documentation Links

- Kubernetes.io/docs
- kubectl cheat sheet
- API reference
- Best practices guide

**All detailed modules will be progressively added!**
