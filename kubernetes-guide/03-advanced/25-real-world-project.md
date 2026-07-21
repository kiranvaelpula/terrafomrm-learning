# Module 25: Real-World Project - Complete E-Commerce Platform

## 📚 Project Overview

Build a production-ready e-commerce platform on Kubernetes with:
- Microservices architecture
- High availability
- Auto-scaling
- Monitoring & logging
- CI/CD pipeline
- Security best practices

---

## 🏗️ Architecture

### System Components

```
                    Internet
                       ↓
                [Ingress/TLS]
                       ↓
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   [Frontend]     [API Gateway]   [Admin]
        ↓              ↓              ↓
        └──────────────┼──────────────┘
                       ↓
        ┌──────────────┼──────────────┬──────────────┐
        ↓              ↓              ↓              ↓
  [Product Svc]  [Order Svc]   [User Svc]   [Payment Svc]
        ↓              ↓              ↓              ↓
        └──────────────┼──────────────┴──────────────┘
                       ↓
        ┌──────────────┼──────────────┬──────────────┐
        ↓              ↓              ↓              ↓
   [PostgreSQL]    [Redis]       [RabbitMQ]    [MongoDB]
```

### Tech Stack
- **Frontend**: React (Next.js)
- **Backend**: Node.js microservices
- **Databases**: PostgreSQL, MongoDB, Redis
- **Message Queue**: RabbitMQ
- **Monitoring**: Prometheus + Grafana
- **Logging**: Loki + Promtail
- **Service Mesh**: Istio (optional)
- **CI/CD**: GitLab CI / GitHub Actions + ArgoCD

---

## 🎪 Lab 1: Setup Infrastructure

### Step 1: Create Namespaces

```yaml
# namespaces.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ecommerce-prod
  labels:
    environment: production
    project: ecommerce
    pod-security.kubernetes.io/enforce: restricted

---
apiVersion: v1
kind: Namespace
metadata:
  name: ecommerce-staging
  labels:
    environment: staging
    project: ecommerce

---
apiVersion: v1
kind: Namespace
metadata:
  name: ecommerce-monitoring
  labels:
    name: monitoring
```

```bash
kubectl apply -f namespaces.yaml
```

### Step 2: Setup Storage Classes

```yaml
# storage-classes.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  encrypted: "true"
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer

---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard-hdd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
reclaimPolicy: Delete
allowVolumeExpansion: true
```

### Step 3: Create Secrets

```bash
# Database credentials
kubectl create secret generic postgres-credentials \
  --from-literal=username=ecommerce_user \
  --from-literal=password=$(openssl rand -base64 32) \
  --from-literal=database=ecommerce_db \
  -n ecommerce-prod

# Redis password
kubectl create secret generic redis-password \
  --from-literal=password=$(openssl rand -base64 32) \
  -n ecommerce-prod

# RabbitMQ credentials
kubectl create secret generic rabbitmq-credentials \
  --from-literal=username=ecommerce \
  --from-literal=password=$(openssl rand -base64 32) \
  -n ecommerce-prod

# MongoDB credentials
kubectl create secret generic mongodb-credentials \
  --from-literal=username=ecommerce \
  --from-literal=password=$(openssl rand -base64 32) \
  --from-literal=database=products \
  -n ecommerce-prod

# Payment gateway API key
kubectl create secret generic payment-api-key \
  --from-literal=api-key=your-stripe-api-key \
  -n ecommerce-prod
```


---

## 🎪 Lab 2: Deploy Data Layer

### PostgreSQL (Orders & Users)

```yaml
# postgres-statefulset.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: ecommerce-prod
spec:
  ports:
  - port: 5432
  clusterIP: None
  selector:
    app: postgres

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: ecommerce-prod
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: database
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 20Gi
```


### Redis (Caching)

```yaml
# redis-deployment.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-config
  namespace: ecommerce-prod
data:
  redis.conf: |
    maxmemory 2gb
    maxmemory-policy allkeys-lru
    appendonly yes
    appendfsync everysec

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: ecommerce-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command: ["redis-server", "/etc/redis/redis.conf", "--requirepass", "$(REDIS_PASSWORD)"]
        ports:
        - containerPort: 6379
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-password
              key: password
        volumeMounts:
        - name: redis-config
          mountPath: /etc/redis
        - name: redis-data
          mountPath: /data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "500m"
      volumes:
      - name: redis-config
        configMap:
          name: redis-config
      - name: redis-data
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: ecommerce-prod
spec:
  selector:
    app: redis
  ports:
  - port: 6379
```


### MongoDB (Product Catalog)

```yaml
# mongodb-statefulset.yaml
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: ecommerce-prod
spec:
  ports:
  - port: 27017
  clusterIP: None
  selector:
    app: mongodb

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
  namespace: ecommerce-prod
spec:
  serviceName: mongodb
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:6
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            secretKeyRef:
              name: mongodb-credentials
              key: username
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mongodb-credentials
              key: password
        - name: MONGO_INITDB_DATABASE
          valueFrom:
            secretKeyRef:
              name: mongodb-credentials
              key: database
        volumeMounts:
        - name: mongodb-storage
          mountPath: /data/db
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
  volumeClaimTemplates:
  - metadata:
      name: mongodb-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 20Gi
```


### RabbitMQ (Message Queue)

```yaml
# rabbitmq-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rabbitmq
  namespace: ecommerce-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rabbitmq
  template:
    metadata:
      labels:
        app: rabbitmq
    spec:
      containers:
      - name: rabbitmq
        image: rabbitmq:3.12-management-alpine
        ports:
        - containerPort: 5672
          name: amqp
        - containerPort: 15672
          name: management
        env:
        - name: RABBITMQ_DEFAULT_USER
          valueFrom:
            secretKeyRef:
              name: rabbitmq-credentials
              key: username
        - name: RABBITMQ_DEFAULT_PASS
          valueFrom:
            secretKeyRef:
              name: rabbitmq-credentials
              key: password
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: rabbitmq
  namespace: ecommerce-prod
spec:
  selector:
    app: rabbitmq
  ports:
  - name: amqp
    port: 5672
  - name: management
    port: 15672
```

```bash
# Deploy all data layer services
kubectl apply -f postgres-statefulset.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f mongodb-statefulset.yaml
kubectl apply -f rabbitmq-deployment.yaml

# Verify
kubectl get pods -n ecommerce-prod
kubectl get pvc -n ecommerce-prod
```


---

## 🎪 Lab 3: Deploy Microservices

### Product Service

```yaml
# product-service.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: product-service-config
  namespace: ecommerce-prod
data:
  NODE_ENV: "production"
  PORT: "8080"
  MONGODB_HOST: "mongodb.ecommerce-prod.svc.cluster.local"
  MONGODB_PORT: "27017"
  REDIS_HOST: "redis.ecommerce-prod.svc.cluster.local"
  REDIS_PORT: "6379"
  LOG_LEVEL: "info"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: product-service
  namespace: ecommerce-prod
  labels:
    app: product-service
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: product-service
  template:
    metadata:
      labels:
        app: product-service
        version: v1
    spec:
      serviceAccountName: ecommerce-sa
      containers:
      - name: product-service
        image: myregistry/product-service:v1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 9090
          name: metrics
        envFrom:
        - configMapRef:
            name: product-service-config
        env:
        - name: MONGODB_USERNAME
          valueFrom:
            secretKeyRef:
              name: mongodb-credentials
              key: username
        - name: MONGODB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mongodb-credentials
              key: password
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-password
              key: password
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: product-service
  namespace: ecommerce-prod
spec:
  selector:
    app: product-service
  ports:
  - name: http
    port: 80
    targetPort: 8080
  - name: metrics
    port: 9090
    targetPort: 9090
```


### Order Service

```yaml
# order-service.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: order-service-config
  namespace: ecommerce-prod
data:
  NODE_ENV: "production"
  PORT: "8080"
  POSTGRES_HOST: "postgres.ecommerce-prod.svc.cluster.local"
  POSTGRES_PORT: "5432"
  RABBITMQ_HOST: "rabbitmq.ecommerce-prod.svc.cluster.local"
  RABBITMQ_PORT: "5672"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
  namespace: ecommerce-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
        version: v1
    spec:
      containers:
      - name: order-service
        image: myregistry/order-service:v1.0.0
        ports:
        - containerPort: 8080
        envFrom:
        - configMapRef:
            name: order-service-config
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
        - name: RABBITMQ_USER
          valueFrom:
            secretKeyRef:
              name: rabbitmq-credentials
              key: username
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-credentials
              key: password
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: order-service
  namespace: ecommerce-prod
spec:
  selector:
    app: order-service
  ports:
  - port: 80
    targetPort: 8080
```


### User Service

```yaml
# user-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: ecommerce-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
        version: v1
    spec:
      containers:
      - name: user-service
        image: myregistry/user-service:v1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: POSTGRES_HOST
          value: "postgres.ecommerce-prod.svc.cluster.local"
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: ecommerce-prod
spec:
  selector:
    app: user-service
  ports:
  - port: 80
    targetPort: 8080
```


### Payment Service

```yaml
# payment-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
  namespace: ecommerce-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: payment-service
  template:
    metadata:
      labels:
        app: payment-service
        version: v1
    spec:
      containers:
      - name: payment-service
        image: myregistry/payment-service:v1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: STRIPE_API_KEY
          valueFrom:
            secretKeyRef:
              name: payment-api-key
              key: api-key
        - name: RABBITMQ_HOST
          value: "rabbitmq.ecommerce-prod.svc.cluster.local"
        - name: RABBITMQ_USER
          valueFrom:
            secretKeyRef:
              name: rabbitmq-credentials
              key: username
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-credentials
              key: password
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: payment-service
  namespace: ecommerce-prod
spec:
  selector:
    app: payment-service
  ports:
  - port: 80
    targetPort: 8080
```


### API Gateway

```yaml
# api-gateway.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: ecommerce-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
        version: v1
    spec:
      containers:
      - name: api-gateway
        image: myregistry/api-gateway:v1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: PRODUCT_SERVICE_URL
          value: "http://product-service.ecommerce-prod.svc.cluster.local"
        - name: ORDER_SERVICE_URL
          value: "http://order-service.ecommerce-prod.svc.cluster.local"
        - name: USER_SERVICE_URL
          value: "http://user-service.ecommerce-prod.svc.cluster.local"
        - name: PAYMENT_SERVICE_URL
          value: "http://payment-service.ecommerce-prod.svc.cluster.local"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: ecommerce-prod
spec:
  selector:
    app: api-gateway
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: ecommerce-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```


### Frontend Application

```yaml
# frontend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: ecommerce-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
        version: v1
    spec:
      containers:
      - name: frontend
        image: myregistry/frontend:v1.0.0
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.example.com"
        - name: NODE_ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: ecommerce-prod
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 3000
```

```bash
# Deploy all microservices
kubectl apply -f product-service.yaml
kubectl apply -f order-service.yaml
kubectl apply -f user-service.yaml
kubectl apply -f payment-service.yaml
kubectl apply -f api-gateway.yaml
kubectl apply -f frontend.yaml

# Verify
kubectl get deployments -n ecommerce-prod
kubectl get services -n ecommerce-prod
```


---

## 🎪 Lab 4: Setup Ingress and TLS

### Install Cert-Manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Verify installation
kubectl get pods -n cert-manager
```

### Configure Let's Encrypt Issuer

```yaml
# letsencrypt-issuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
    - http01:
        ingress:
          class: nginx
```

### Create Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ecommerce-ingress
  namespace: ecommerce-prod
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - www.example.com
    - api.example.com
    secretName: ecommerce-tls
  rules:
  - host: www.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 80
```

```bash
kubectl apply -f letsencrypt-issuer.yaml
kubectl apply -f ingress.yaml

# Check certificate
kubectl get certificate -n ecommerce-prod
kubectl describe certificate ecommerce-tls -n ecommerce-prod
```


---

## 🎪 Lab 5: Setup Monitoring

### Deploy Prometheus Stack

```bash
# Add Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus + Grafana
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace ecommerce-monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set grafana.adminPassword=admin123

# Verify
kubectl get pods -n ecommerce-monitoring
```

### Create ServiceMonitors

```yaml
# servicemonitors.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: product-service-monitor
  namespace: ecommerce-prod
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app: product-service
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics

---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: order-service-monitor
  namespace: ecommerce-prod
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app: order-service
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### Create Alert Rules

```yaml
# prometheus-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: ecommerce-alerts
  namespace: ecommerce-prod
  labels:
    release: prometheus
spec:
  groups:
  - name: ecommerce
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: |
        rate(http_requests_total{namespace="ecommerce-prod",status=~"5.."}[5m]) > 0.05
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate on {{ $labels.service }}"
        description: "Error rate is {{ $value | humanizePercentage }}"
    
    - alert: ServiceDown
      expr: up{namespace="ecommerce-prod"} == 0
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "Service {{ $labels.job }} is down"
    
    - alert: HighMemoryUsage
      expr: |
        container_memory_usage_bytes{namespace="ecommerce-prod"} / 
        container_spec_memory_limit_bytes > 0.9
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High memory usage in {{ $labels.pod }}"
    
    - alert: PodCrashLooping
      expr: |
        rate(kube_pod_container_status_restarts_total{namespace="ecommerce-prod"}[15m]) > 0
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Pod {{ $labels.pod }} is crash looping"
```

```bash
kubectl apply -f servicemonitors.yaml
kubectl apply -f prometheus-rules.yaml
```


### Access Grafana

```bash
# Port forward Grafana
kubectl port-forward -n ecommerce-monitoring svc/prometheus-grafana 3000:80

# Access: http://localhost:3000
# Username: admin
# Password: admin123
```

### Import Dashboards

```yaml
# grafana-dashboard-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ecommerce-dashboard
  namespace: ecommerce-monitoring
  labels:
    grafana_dashboard: "1"
data:
  ecommerce-overview.json: |
    {
      "dashboard": {
        "title": "E-Commerce Platform Overview",
        "panels": [
          {
            "title": "Request Rate",
            "targets": [{"expr": "sum(rate(http_requests_total{namespace=\"ecommerce-prod\"}[5m]))"}]
          },
          {
            "title": "Error Rate",
            "targets": [{"expr": "sum(rate(http_requests_total{namespace=\"ecommerce-prod\",status=~\"5..\"}[5m]))"}]
          },
          {
            "title": "Response Time (p95)",
            "targets": [{"expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"}]
          },
          {
            "title": "Active Pods",
            "targets": [{"expr": "count(up{namespace=\"ecommerce-prod\"} == 1)"}]
          }
        ]
      }
    }
```

---

## 🎪 Lab 6: Setup Logging

### Deploy Loki Stack

```bash
# Install Loki + Promtail
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  --namespace ecommerce-monitoring \
  --set promtail.enabled=true \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=50Gi

# Verify
kubectl get pods -n ecommerce-monitoring -l app=loki
```

### Add Loki Datasource to Grafana

```yaml
# loki-datasource.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-loki-datasource
  namespace: ecommerce-monitoring
  labels:
    grafana_datasource: "1"
data:
  loki-datasource.yaml: |
    apiVersion: 1
    datasources:
    - name: Loki
      type: loki
      access: proxy
      url: http://loki:3100
      jsonData:
        maxLines: 1000
```

```bash
kubectl apply -f loki-datasource.yaml

# Restart Grafana to pick up datasource
kubectl rollout restart deployment prometheus-grafana -n ecommerce-monitoring
```


---

## 🎪 Lab 7: Setup Network Policies

```yaml
# network-policies.yaml

# Default deny all
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: ecommerce-prod
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

---
# Allow frontend to API gateway
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-to-gateway
  namespace: ecommerce-prod
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 8080
  - to:  # DNS
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53

---
# Allow API gateway to services
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: gateway-to-services
  namespace: ecommerce-prod
spec:
  podSelector:
    matchLabels:
      app: api-gateway
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: product-service
    - podSelector:
        matchLabels:
          app: order-service
    - podSelector:
        matchLabels:
          app: user-service
    - podSelector:
        matchLabels:
          app: payment-service
    ports:
    - protocol: TCP
      port: 8080

---
# Allow services to databases
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: services-to-databases
  namespace: ecommerce-prod
spec:
  podSelector:
    matchLabels:
      app: product-service
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mongodb
    ports:
    - protocol: TCP
      port: 27017
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379

---
# Allow ingress to frontend and gateway
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress
  namespace: ecommerce-prod
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 3000
```

```bash
kubectl apply -f network-policies.yaml
kubectl get networkpolicies -n ecommerce-prod
```


---

## 🎪 Lab 8: CI/CD with ArgoCD

### Install ArgoCD

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s

# Get admin password
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
echo "ArgoCD Password: $ARGOCD_PASSWORD"

# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

### Create ArgoCD Application

```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ecommerce-prod
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/ecommerce-k8s
    targetRevision: main
    path: kubernetes/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: ecommerce-prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
  ignoreDifferences:
  - group: apps
    kind: Deployment
    jsonPointers:
    - /spec/replicas

---
# App of Apps pattern
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ecommerce-apps
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/ecommerce-k8s
    targetRevision: main
    path: argocd/applications
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: myorg

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [frontend, api-gateway, product-service, order-service, user-service, payment-service]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/${{ matrix.service }}
        tags: |
          type=sha,prefix={{branch}}-
          type=semver,pattern={{version}}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: ./services/${{ matrix.service }}
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Update Kubernetes manifests
      run: |
        cd kubernetes/overlays/production
        kustomize edit set image ${{ matrix.service }}=${{ steps.meta.outputs.tags }}
        git config user.name github-actions
        git config user.email github-actions@github.com
        git add .
        git commit -m "Update ${{ matrix.service }} to ${{ steps.meta.outputs.tags }}"
        git push
```


---

## 🎪 Lab 9: Backup and Disaster Recovery

### Install Velero

```bash
# Install Velero CLI
wget https://github.com/vmware-tanzu/velero/releases/download/v1.12.0/velero-v1.12.0-linux-amd64.tar.gz
tar -xvf velero-v1.12.0-linux-amd64.tar.gz
sudo mv velero-v1.12.0-linux-amd64/velero /usr/local/bin/

# Create S3 bucket for backups (AWS example)
aws s3 mb s3://ecommerce-k8s-backups --region us-east-1

# Install Velero
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.8.0 \
  --bucket ecommerce-k8s-backups \
  --backup-location-config region=us-east-1 \
  --snapshot-location-config region=us-east-1 \
  --secret-file ./credentials-velero
```

### Create Backup Schedules

```bash
# Daily backup of production namespace
velero schedule create ecommerce-prod-daily \
  --schedule="0 2 * * *" \
  --include-namespaces ecommerce-prod \
  --ttl 720h0m0s

# Hourly backup of critical data
velero schedule create ecommerce-critical-hourly \
  --schedule="0 * * * *" \
  --include-namespaces ecommerce-prod \
  --include-resources persistentvolumeclaims,persistentvolumes \
  --ttl 168h0m0s

# Weekly full cluster backup
velero schedule create full-cluster-weekly \
  --schedule="0 0 * * 0" \
  --ttl 2160h0m0s
```

### Test Restore

```bash
# Create a test backup
velero backup create test-backup --include-namespaces ecommerce-prod

# Check backup status
velero backup describe test-backup
velero backup logs test-backup

# Simulate disaster - delete namespace
kubectl delete namespace ecommerce-prod

# Restore from backup
velero restore create --from-backup test-backup

# Verify restoration
kubectl get all -n ecommerce-prod
```


---

## 🎪 Lab 10: Load Testing

### Install k6

```bash
# Install k6
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

### Create Load Test Script

```javascript
// loadtest.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
    http_req_failed: ['rate<0.01'],   // Error rate should be below 1%
  },
};

const BASE_URL = 'https://api.example.com';

export default function () {
  // Homepage
  let response = http.get(`${BASE_URL}/`);
  check(response, {
    'homepage status is 200': (r) => r.status === 200,
  });
  sleep(1);

  // List products
  response = http.get(`${BASE_URL}/api/products`);
  check(response, {
    'products list status is 200': (r) => r.status === 200,
  });
  sleep(1);

  // Get product detail
  response = http.get(`${BASE_URL}/api/products/1`);
  check(response, {
    'product detail status is 200': (r) => r.status === 200,
  });
  sleep(2);

  // Search
  response = http.get(`${BASE_URL}/api/products?search=laptop`);
  check(response, {
    'search status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
```

```bash
# Run load test
k6 run loadtest.js

# Run with custom VUs
k6 run --vus 100 --duration 10m loadtest.js

# Output to InfluxDB
k6 run --out influxdb=http://localhost:8086/k6 loadtest.js
```

### Monitor During Load Test

```bash
# Watch HPA scaling
watch kubectl get hpa -n ecommerce-prod

# Watch pod count
watch kubectl get pods -n ecommerce-prod

# Monitor resource usage
kubectl top pods -n ecommerce-prod
kubectl top nodes

# Check Prometheus metrics
# Open Grafana and watch real-time dashboards
```


---

## 📊 Project Verification Checklist

### Infrastructure
```
☐ Kubernetes cluster running (3+ nodes)
☐ Multiple availability zones configured
☐ Storage classes defined
☐ Namespaces created (prod, staging, monitoring)
☐ Resource quotas and limits set
```

### Data Layer
```
☐ PostgreSQL running with persistent storage
☐ MongoDB running with persistent storage
☐ Redis deployed and accessible
☐ RabbitMQ deployed with management UI
☐ All databases have backups configured
```

### Application Layer
```
☐ All microservices deployed (6 services)
☐ All services have health checks
☐ Resource limits configured for all pods
☐ HPA configured for scalable services
☐ Pod Disruption Budgets in place
```

### Networking
```
☐ Ingress controller installed
☐ TLS certificates issued (Let's Encrypt)
☐ DNS configured correctly
☐ Network policies implemented
☐ Services accessible via domain names
```

### Security
```
☐ RBAC configured
☐ Pod Security Standards enforced
☐ Secrets stored securely (not in Git)
☐ Network policies restrict traffic
☐ Image scanning implemented
☐ Security scanning passed
```

### Monitoring
```
☐ Prometheus collecting metrics
☐ Grafana dashboards created
☐ Alert rules configured
☐ Loki collecting logs
☐ All services exposing metrics
```

### CI/CD
```
☐ ArgoCD installed and configured
☐ GitOps repository structure created
☐ GitHub Actions/GitLab CI configured
☐ Automated image builds working
☐ Automated deployments working
```

### Backup & DR
```
☐ Velero installed
☐ Backup schedules configured
☐ Backup restoration tested
☐ DR procedures documented
☐ RTO/RPO defined
```

### Testing
```
☐ Load testing completed
☐ Auto-scaling verified
☐ Failover tested
☐ Performance benchmarks met
☐ Security tests passed
```


---

## 🐛 Common Issues and Solutions

### Issue 1: Pods Not Starting

```bash
# Check pod status
kubectl get pods -n ecommerce-prod
kubectl describe pod <pod-name> -n ecommerce-prod

# Check events
kubectl get events -n ecommerce-prod --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n ecommerce-prod

# Common fixes:
# - Image pull errors: Check image name and registry credentials
# - CrashLoopBackOff: Check application logs
# - Resource limits: Increase CPU/memory
# - Volume mount issues: Verify PVC exists and is bound
```

### Issue 2: Service Connectivity Issues

```bash
# Test DNS resolution
kubectl run test-pod --image=busybox -it --rm -- nslookup product-service.ecommerce-prod.svc.cluster.local

# Test service endpoint
kubectl run test-pod --image=curlimages/curl -it --rm -- curl http://product-service.ecommerce-prod.svc.cluster.local

# Check service and endpoints
kubectl get svc -n ecommerce-prod
kubectl get endpoints -n ecommerce-prod

# Check network policies
kubectl get networkpolicies -n ecommerce-prod
kubectl describe networkpolicy <policy-name> -n ecommerce-prod
```

### Issue 3: Database Connection Failures

```bash
# Verify database is running
kubectl get pods -l app=postgres -n ecommerce-prod

# Check database logs
kubectl logs -l app=postgres -n ecommerce-prod

# Test connection from application pod
kubectl exec -it <app-pod> -n ecommerce-prod -- sh
# Inside pod:
nc -zv postgres.ecommerce-prod.svc.cluster.local 5432

# Verify secrets
kubectl get secret postgres-credentials -n ecommerce-prod -o yaml
```

### Issue 4: High Memory/CPU Usage

```bash
# Check resource usage
kubectl top pods -n ecommerce-prod
kubectl top nodes

# Check resource limits
kubectl describe pod <pod-name> -n ecommerce-prod | grep -A 5 "Limits"

# Adjust resources
kubectl set resources deployment <deployment-name> \
  --limits=cpu=1000m,memory=1Gi \
  --requests=cpu=500m,memory=512Mi \
  -n ecommerce-prod

# Enable VPA for recommendations
kubectl apply -f vpa.yaml
kubectl describe vpa <vpa-name> -n ecommerce-prod
```

### Issue 5: Ingress Not Working

```bash
# Check ingress
kubectl get ingress -n ecommerce-prod
kubectl describe ingress ecommerce-ingress -n ecommerce-prod

# Check ingress controller
kubectl get pods -n ingress-nginx

# Check certificate
kubectl get certificate -n ecommerce-prod
kubectl describe certificate ecommerce-tls -n ecommerce-prod

# Test locally
curl -H "Host: www.example.com" http://<ingress-ip>/

# Check DNS
nslookup www.example.com
```


---

## 💡 Production Best Practices Applied

### 1. High Availability
- ✅ Multiple replicas for all services
- ✅ Multi-zone deployment with topology spread
- ✅ Pod Disruption Budgets prevent downtime
- ✅ Anti-affinity rules spread pods across nodes

### 2. Scalability
- ✅ Horizontal Pod Autoscaling configured
- ✅ Resource requests and limits defined
- ✅ Cluster Autoscaler can add nodes
- ✅ Stateless design allows easy scaling

### 3. Security
- ✅ Pod Security Standards enforced
- ✅ Network policies isolate services
- ✅ RBAC with least privilege
- ✅ Secrets not in Git (use External Secrets in prod)
- ✅ TLS for all external traffic
- ✅ Regular image scanning

### 4. Observability
- ✅ Prometheus metrics collection
- ✅ Grafana dashboards
- ✅ Structured logging with Loki
- ✅ Alert rules for critical issues
- ✅ Distributed tracing (optional: Jaeger)

### 5. Reliability
- ✅ Health checks (liveness, readiness, startup)
- ✅ Graceful shutdown with preStop hooks
- ✅ Retry logic and circuit breakers
- ✅ Rate limiting on ingress
- ✅ Backup and restore procedures

### 6. GitOps
- ✅ Infrastructure as Code
- ✅ ArgoCD for automated deployments
- ✅ Git as single source of truth
- ✅ Automated CI/CD pipeline
- ✅ Easy rollback capability

---

## 📈 Performance Optimization Tips

### Database Optimization
```yaml
# PostgreSQL connection pooling
env:
- name: DB_POOL_SIZE
  value: "20"
- name: DB_POOL_TIMEOUT
  value: "30"

# Redis caching strategy
- name: CACHE_TTL
  value: "3600"
- name: CACHE_STRATEGY
  value: "write-through"
```

### Application Optimization
```yaml
# Resource right-sizing based on VPA
resources:
  requests:
    memory: "384Mi"  # 20% buffer over actual usage
    cpu: "300m"
  limits:
    memory: "512Mi"  # 33% buffer over requests
    cpu: "500m"

# Enable gzip compression
annotations:
  nginx.ingress.kubernetes.io/enable-compression: "true"
  nginx.ingress.kubernetes.io/gzip-level: "6"
```

### Caching Strategy
```yaml
# CDN for static assets
annotations:
  nginx.ingress.kubernetes.io/configuration-snippet: |
    add_header Cache-Control "public, max-age=31536000, immutable";

# Redis for session storage
- name: SESSION_STORE
  value: "redis"
- name: SESSION_TTL
  value: "86400"
```

---

## 🎓 Bonus Challenges

### Challenge 1: Implement Service Mesh
- Install Istio or Linkerd
- Configure mTLS between services
- Implement traffic splitting for canary deployments
- Add circuit breakers and retries
- Configure observability with service mesh metrics

### Challenge 2: Multi-Region Deployment
- Deploy to multiple regions
- Configure global load balancing
- Implement data replication
- Test failover between regions
- Optimize for latency

### Challenge 3: Chaos Engineering
- Install Chaos Mesh or Litmus
- Test pod failures
- Simulate network latency
- Test resource exhaustion
- Verify system resilience

### Challenge 4: Advanced Security
- Implement OPA Gatekeeper policies
- Add Falco for runtime security
- Configure external secrets management (Vault)
- Implement certificate rotation
- Add security scanning in CI/CD

### Challenge 5: Cost Optimization
- Implement spot instances for non-critical workloads
- Right-size all resources based on VPA
- Configure cluster autoscaler with proper scaling policies
- Implement pod priority and preemption
- Monitor and optimize cloud costs

---

## 📝 Project Documentation Template

### Architecture Document
```markdown
# E-Commerce Platform Architecture

## Overview
- System diagram
- Component descriptions
- Technology stack

## Infrastructure
- Cluster specifications
- Node configuration
- Storage configuration

## Services
- Microservices list
- API documentation
- Database schemas

## Security
- Authentication/Authorization
- Network security
- Data encryption

## Operations
- Deployment procedures
- Monitoring setup
- Backup/restore procedures
- Incident response plan
```

### Runbook Template
```markdown
# Operations Runbook

## Daily Operations
- Health checks
- Log review
- Metric review

## Common Issues
- Issue: [Description]
- Symptoms: [What you see]
- Diagnosis: [How to identify]
- Resolution: [How to fix]

## Emergency Procedures
- Service outage response
- Data loss recovery
- Security incident response

## Contacts
- On-call rotation
- Escalation procedures
- External contacts
```

---

## 📝 Quiz

### Questions:
1. What are the key components of the e-commerce architecture?
2. How does the system achieve high availability?
3. Explain the monitoring setup used in the project.
4. What is the disaster recovery strategy?
5. How does GitOps work with ArgoCD in this setup?
6. What security measures are implemented?
7. How would you troubleshoot a service that's not responding?
8. What load testing tools and strategies were used?

### Answers:
1. Frontend, API Gateway, 4 microservices (product, order, user, payment), databases (PostgreSQL, MongoDB, Redis, RabbitMQ)
2. Multi-zone deployment, multiple replicas, PDBs, anti-affinity rules, HPA, health checks
3. Prometheus for metrics, Grafana for visualization, Loki for logs, ServiceMonitors, AlertRules
4. Velero for backups, scheduled daily/hourly, tested restore procedures, documented RPO/RTO
5. ArgoCD watches Git repo, automatically syncs changes to cluster, enables rollback via Git revert
6. Pod Security Standards, Network Policies, RBAC, TLS encryption, secrets management, image scanning
7. Check pod status, logs, events; verify service endpoints; test network connectivity; check resource usage
8. k6 for load testing, gradual ramp-up strategy, monitor HPA scaling, verify performance thresholds

---

## 💡 Key Takeaways

✅ Production systems require multiple layers of resilience
✅ Monitoring and observability are critical for operations
✅ Security must be designed in from the start
✅ GitOps provides reliable, auditable deployments
✅ Automation reduces human error and improves reliability
✅ Regular testing (load, failover, security) is essential
✅ Documentation is crucial for team collaboration
✅ Always plan for disaster recovery

---

## 🎉 Congratulations!

You've completed a comprehensive real-world Kubernetes project! You now have:

✅ Production-ready architecture knowledge
✅ Hands-on experience with microservices deployment
✅ Monitoring and logging setup expertise
✅ CI/CD pipeline implementation skills
✅ Security best practices understanding
✅ Disaster recovery planning experience
✅ Load testing and performance tuning skills
✅ Complete operational runbook

---

## 📚 Additional Resources

- [Kubernetes Production Patterns](https://github.com/gravitational/workshop/tree/master/k8sprod)
- [12-Factor App Methodology](https://12factor.net/)
- [SRE Book by Google](https://sre.google/books/)
- [Kubernetes Patterns Book](https://k8spatterns.io/)
- [CNCF Landscape](https://landscape.cncf.io/)
- [Kubernetes The Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way)

---

## ⏭️ What's Next?

You've completed all 25 modules! Here are suggested next steps:

1. **Practice**: Deploy this project in your own cluster
2. **Customize**: Adapt it to your use case
3. **Contribute**: Share your improvements with the community
4. **Certify**: Prepare for CKA, CKAD, or CKS certifications
5. **Learn More**: Explore service mesh, chaos engineering, eBPF
6. **Build**: Create your own production systems

---

**🎊 You're now ready to build and operate production Kubernetes systems! Keep learning and building! 🚀**

[← Back to Module 24](./24-production-patterns.md) | [Return to Main Guide](../README.md) | [Interview Guide](../INTERVIEW-GUIDE.md)
