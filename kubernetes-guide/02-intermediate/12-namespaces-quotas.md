# Module 12: Namespaces & Resource Quotas

## 📚 Namespaces for Isolation

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: development
  labels:
    env: dev
```

```bash
kubectl create namespace production
kubectl get namespaces
kubectl config set-context --current --namespace=development
```

## 📊 ResourceQuota

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
    persistentvolumeclaims: "20"
```

## 📏 LimitRange

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
      memory: "4Gi"
    min:
      cpu: "100m"
      memory: "128Mi"
    default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "200m"
      memory: "256Mi"
    type: Container
```

## ⏭️ Next: [Module 13: RBAC & Security](./13-rbac-security.md)
