# Module 11: Ingress Controllers

## 📚 What You'll Learn
- Ingress resources and controllers
- Path-based and host-based routing
- TLS/SSL termination
- NGINX Ingress Controller
- Load balancing strategies

---

## 🎯 What is Ingress?

**Ingress** manages external HTTP(S) access to services with routing rules.

```
Without Ingress:
Internet → LoadBalancer Service (per app) → Pods
Cost: Multiple load balancers

With Ingress:
Internet → Single LoadBalancer → Ingress Controller → Services → Pods
Cost: One load balancer for many apps
```

---

## 📝 Basic Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: simple-ingress
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

---

## 🎪 Lab 1: Install NGINX Ingress Controller

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Check installation
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx

# For Minikube
minikube addons enable ingress
```

---

## 🛣️ Path-Based Routing

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-routing
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
      - path: /web
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
      - path: /admin
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 3000
```

---

## 🌐 Host-Based Routing

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-routing
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
  - host: web.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
  - host: admin.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 3000
```

---

## 🔒 TLS/SSL Configuration

```bash
# Create TLS secret
kubectl create secret tls tls-secret \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: tls-secret
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

---

## 🎪 Lab 2: Complete Ingress Setup

```yaml
# Step 1: Deploy applications
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: hashicorp/http-echo
        args: ["-text=API Response"]
        ports:
        - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  selector:
    app: api
  ports:
  - port: 80
    targetPort: 5678
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: hashicorp/http-echo
        args: ["-text=Web Response"]
        ports:
        - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 5678
---
# Step 2: Create Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: complete-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.local
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
```

```bash
# Test
# Add to /etc/hosts: 127.0.0.1 myapp.local

curl http://myapp.local/api
curl http://myapp.local/web
```

---

## 🔧 Advanced Annotations

```yaml
metadata:
  annotations:
    # Rewrite URLs
    nginx.ingress.kubernetes.io/rewrite-target: /
    
    # SSL Redirect
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    
    # Rate limiting
    nginx.ingress.kubernetes.io/limit-rps: "10"
    
    # Authentication
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: basic-auth
    
    # CORS
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "*"
    
    # Custom timeout
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    
    # Whitelist IPs
    nginx.ingress.kubernetes.io/whitelist-source-range: "10.0.0.0/24,192.168.0.0/16"
```

---

## 💡 Best Practices

```yaml
# 1. Use ingressClassName
spec:
  ingressClassName: nginx

# 2. Set resource limits on Ingress Controller
resources:
  requests:
    cpu: 100m
    memory: 90Mi
  limits:
    cpu: 1000m
    memory: 500Mi

# 3. Enable monitoring
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "10254"

# 4. Configure timeouts appropriately
nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
```

---

## ⏭️ Next: [Module 12: Namespaces & Resource Quotas](./12-namespaces-quotas.md)
