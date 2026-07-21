# Module 19: Kubernetes Operators

## 🎯 What are Operators?

Operators = CRDs + Controllers that automate application management

## 🛠️ Install Operator Lifecycle Manager

```bash
curl -sL https://github.com/operator-framework/operator-lifecycle-manager/releases/download/v0.25.0/install.sh | bash -s v0.25.0

kubectl get pods -n olm
```

## 📦 Install Prometheus Operator

```bash
kubectl create -f https://operatorhub.io/install/prometheus.yaml

# Check operator
kubectl get csv -n operators
```

## 📝 Use Prometheus Operator

```yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: prometheus
spec:
  replicas: 2
  serviceAccountName: prometheus
  serviceMonitorSelector:
    matchLabels:
      team: frontend
  resources:
    requests:
      memory: 400Mi
```

## 🔧 Popular Operators

- **Prometheus Operator** - Monitoring
- **PostgreSQL Operator** - Database management
- **Elasticsearch Operator** - Search and analytics
- **Istio Operator** - Service mesh
- **Cert-Manager** - Certificate management

## ⏭️ Next: [Module 20: Service Mesh (Istio)](./20-service-mesh.md)
