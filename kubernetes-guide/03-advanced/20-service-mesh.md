# Module 20: Service Mesh with Istio

## 🌐 Install Istio

```bash
# Download Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH

# Install Istio
istioctl install --set profile=demo -y

# Enable sidecar injection
kubectl label namespace default istio-injection=enabled

# Verify
kubectl get pods -n istio-system
```

## 📝 Deploy Sample Application

```yaml
apiVersion: v1
kind: Service
metadata:
  name: productpage
spec:
  ports:
  - port: 9080
  selector:
    app: productpage
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: productpage-v1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: productpage
      version: v1
  template:
    metadata:
      labels:
        app: productpage
        version: v1
    spec:
      containers:
      - name: productpage
        image: docker.io/istio/examples-bookinfo-productpage-v1:1.17.0
        ports:
        - containerPort: 9080
```

## 🚦 Traffic Management

### VirtualService

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        end-user:
          exact: jason
    route:
    - destination:
        host: reviews
        subset: v2
  - route:
    - destination:
        host: reviews
        subset: v1
```

### DestinationRule

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  trafficPolicy:
    loadBalancer:
      simple: RANDOM
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
  - name: v3
    labels:
      version: v3
```

## 🎯 Canary Deployment

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-canary
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        user-agent:
          regex: ".*Mobile.*"
    route:
    - destination:
        host: reviews
        subset: v2
      weight: 50
    - destination:
        host: reviews
        subset: v1
      weight: 50
  - route:
    - destination:
        host: reviews
        subset: v1
```

## 🔒 Security with mTLS

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
    mode: STRICT
```

## 📊 Observability

```bash
# Install Kiali dashboard
kubectl apply -f samples/addons/kiali.yaml

# Install Prometheus
kubectl apply -f samples/addons/prometheus.yaml

# Install Grafana
kubectl apply -f samples/addons/grafana.yaml

# Install Jaeger
kubectl apply -f samples/addons/jaeger.yaml

# Access Kiali
istioctl dashboard kiali
```

## ⏭️ Next: [Module 21: GitOps with ArgoCD](./21-gitops-argocd.md)
