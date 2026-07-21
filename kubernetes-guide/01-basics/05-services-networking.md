# Module 05: Services & Networking

## 📚 What You'll Learn
- What is a Service
- Service types (ClusterIP, NodePort, LoadBalancer)
- Service discovery
- DNS in Kubernetes
- Endpoints
- Network basics

---

## 🎯 What is a Service?

**Problem:** Pods are ephemeral (temporary). They get recreated with new IPs.

**Solution:** Services provide a stable endpoint to access Pods.

### Analogy
```
Pods = Employees (come and go)
Service = Company phone number (stays same)

Call company → Receptionist routes to available employee
Call service → Service routes to available pod
```

### Visual
```
        Service (Stable IP: 10.100.200.1)
               ↓
        Load Balancer
        /     |     \
   Pod 1   Pod 2   Pod 3
   (dies)  (OK)    (OK)
     ↓
   Pod 4 (new)
   
Service automatically routes to healthy pods
```

---

## 🔌 Service Types

### 1. ClusterIP (Default)

**Internal access only** - Most common type.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: ClusterIP  # Default
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080
```

```
┌──────────────────────────┐
│       Cluster            │
│                          │
│  Pod → Service → Pod     │
│                          │
│  ❌ Cannot access from   │
│     outside cluster      │
└──────────────────────────┘

Use for: Internal microservices
```

### 2. NodePort

**External access via Node IP + Port**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: NodePort
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080  # 30000-32767
```

```
External User
    ↓
NodeIP:30080
    ↓
Service
    ↓
Pod:8080

Access: http://<node-ip>:30080
```

### 3. LoadBalancer

**Cloud provider load balancer**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: LoadBalancer
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080
```

```
Internet
    ↓
Cloud Load Balancer (External IP)
    ↓
Service
    ↓
Pods

Access: http://<external-ip>
```

### 4. ExternalName

**DNS alias to external service**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-db
spec:
  type: ExternalName
  externalName: database.example.com
```

---

## 🎪 Lab 1: Creating Services

### Step 1: Create Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
```

```bash
kubectl apply -f deployment.yaml
kubectl get pods -l app=nginx
```

### Step 2: Create ClusterIP Service

```yaml
# service-clusterip.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-clusterip
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

```bash
# Create service
kubectl apply -f service-clusterip.yaml

# Get service
kubectl get svc nginx-clusterip

# Output:
# NAME              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
# nginx-clusterip   ClusterIP   10.100.200.50   <none>        80/TCP    10s

# Test from inside cluster
kubectl run test-pod --image=busybox --rm -it -- sh
wget -O- nginx-clusterip
exit
```

### Step 3: Create NodePort Service

```yaml
# service-nodeport.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-nodeport
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080
```

```bash
# Create service
kubectl apply -f service-nodeport.yaml

# Get service
kubectl get svc nginx-nodeport

# Get node IP
kubectl get nodes -o wide

# Access from browser or curl
# Minikube:
minikube ip  # Get IP
curl http://<minikube-ip>:30080

# Or use Minikube service
minikube service nginx-nodeport
```

### Step 4: Create LoadBalancer Service

```yaml
# service-loadbalancer.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-lb
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

```bash
# Create service
kubectl apply -f service-loadbalancer.yaml

# Get service (wait for EXTERNAL-IP)
kubectl get svc nginx-lb --watch

# On cloud providers: Shows external IP
# On Minikube: Use tunnel
minikube tunnel  # In separate terminal

# Access
curl http://<external-ip>
```

---

## 🔍 Service Discovery

### How Pods Find Services

#### 1. Environment Variables

```bash
# Service creates env vars in pods
kubectl exec <pod-name> -- env | grep SERVICE

# Example:
# NGINX_CLUSTERIP_SERVICE_HOST=10.100.200.50
# NGINX_CLUSTERIP_SERVICE_PORT=80
```

#### 2. DNS (Recommended)

```
Service Name: my-service
Namespace: default

DNS Names:
├── my-service                    (same namespace)
├── my-service.default            (with namespace)
├── my-service.default.svc        (with svc)
└── my-service.default.svc.cluster.local (FQDN)
```

**Example:**
```bash
# From any pod in same namespace
curl http://nginx-clusterip

# From different namespace
curl http://nginx-clusterip.default

# Full DNS name
curl http://nginx-clusterip.default.svc.cluster.local
```

---

## 🎪 Lab 2: Service Discovery

### Create Multi-Namespace Setup

```bash
# Create namespaces
kubectl create namespace frontend
kubectl create namespace backend

# Create deployment in backend
kubectl create deployment api --image=nginx --namespace=backend

# Create service
kubectl expose deployment api --port=80 --namespace=backend

# Create test pod in frontend
kubectl run test --image=busybox --namespace=frontend -- sleep 3600

# Test DNS resolution
kubectl exec -it test --namespace=frontend -- sh
wget -O- api.backend
# ✅ Works! Cross-namespace communication
exit
```

---

## 🔗 Endpoints

**Endpoints** = List of pod IPs that match a service selector

```bash
# Create service
kubectl apply -f service.yaml

# View endpoints
kubectl get endpoints <service-name>

# Describe
kubectl describe endpoints <service-name>

# Example output:
# Name:         nginx-clusterip
# Endpoints:    10.244.1.5:80,10.244.1.6:80,10.244.1.7:80
#               ↑ Pod IPs
```

### How It Works

```
1. Service created with selector: app=nginx

2. Endpoint controller watches:
   - Pods matching label
   - Pod readiness status

3. Endpoint object updated:
   - Adds ready pod IPs
   - Removes unready pod IPs

4. kube-proxy uses endpoints:
   - Updates iptables/IPVS rules
   - Routes traffic to pod IPs
```

---

## 🎨 Service Patterns

### 1. Headless Service

**No cluster IP** - Returns pod IPs directly (for StatefulSets)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-headless
spec:
  clusterIP: None  # Headless
  selector:
    app: nginx
  ports:
  - port: 80
```

```bash
# DNS returns all pod IPs
nslookup nginx-headless

# Output:
# Name:   nginx-headless.default.svc.cluster.local
# Address: 10.244.1.5
# Address: 10.244.1.6
# Address: 10.244.1.7
```

### 2. Service Without Selector

**Manual endpoints** - For external services

```yaml
# Service
apiVersion: v1
kind: Service
metadata:
  name: external-database
spec:
  ports:
  - port: 5432
---
# Endpoints
apiVersion: v1
kind: Endpoints
metadata:
  name: external-database
subsets:
- addresses:
  - ip: 192.168.1.100
  ports:
  - port: 5432
```

### 3. Multi-Port Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: multi-port-svc
spec:
  selector:
    app: myapp
  ports:
  - name: http
    port: 80
    targetPort: 8080
  - name: https
    port: 443
    targetPort: 8443
  - name: metrics
    port: 9090
    targetPort: 9090
```

---

## 🌐 Network Basics

### Pod Network

```
Every pod gets:
├── Unique IP address
├── Can communicate with all pods
├── No NAT required
└── Can reach internet
```

### Service Network

```
Service gets:
├── Virtual IP (ClusterIP)
├── Managed by kube-proxy
├── Not routable (exists in iptables)
└── Routes to pod IPs (endpoints)
```

### Communication Flow

```
Pod A (10.244.1.5)
    ↓
Service (10.100.200.50)
    ↓
kube-proxy (iptables rules)
    ↓
Pod B (10.244.2.8)
```

---

## 🔧 Advanced Service Configuration

### Session Affinity

```yaml
apiVersion: v1
kind: Service
metadata:
  name: sticky-service
spec:
  selector:
    app: myapp
  sessionAffinity: ClientIP  # Sticky sessions
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800  # 3 hours
  ports:
  - port: 80
```

### External Traffic Policy

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-svc
spec:
  type: LoadBalancer
  externalTrafficPolicy: Local  # Preserve source IP
  selector:
    app: myapp
  ports:
  - port: 80
```

### Load Balancer Source Ranges

```yaml
apiVersion: v1
kind: Service
metadata:
  name: restricted-lb
spec:
  type: LoadBalancer
  loadBalancerSourceRanges:
  - 192.168.1.0/24  # Only allow this network
  selector:
    app: myapp
  ports:
  - port: 80
```

---

## 🎪 Lab 3: Complete Service Example

```yaml
# complete-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  labels:
    app: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
        version: v1
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
          name: http
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: web-service
  labels:
    app: web
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
  - name: http
    port: 80
    targetPort: http
    protocol: TCP
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600
```

```bash
# Deploy
kubectl apply -f complete-service.yaml

# Check deployment
kubectl get deployments
kubectl get pods -l app=web

# Check service
kubectl get svc web-service
kubectl describe svc web-service

# Check endpoints
kubectl get endpoints web-service

# Test access
# On Minikube:
minikube service web-service --url

# On cloud:
kubectl get svc web-service
# Access via EXTERNAL-IP
```

---

## 🐛 Troubleshooting Services

### Issue 1: Service Not Working

```bash
# 1. Check service exists
kubectl get svc

# 2. Check selector matches pods
kubectl describe svc <service-name>
kubectl get pods --show-labels

# 3. Check endpoints
kubectl get endpoints <service-name>
# Should show pod IPs

# 4. If no endpoints:
#    - Selector doesn't match
#    - Pods not ready
#    - No pods running
```

### Issue 2: Cannot Access Service

```bash
# 1. Check from inside cluster
kubectl run test --image=busybox --rm -it -- sh
wget -O- <service-name>
exit

# 2. Check from same namespace
kubectl exec <pod> -- curl <service-name>

# 3. Check DNS
kubectl exec <pod> -- nslookup <service-name>

# 4. Check endpoints are healthy
kubectl get endpoints <service-name>
```

### Issue 3: LoadBalancer Pending

```bash
# Check service
kubectl get svc <service-name>

# If EXTERNAL-IP shows <pending>:

# On Minikube:
minikube tunnel  # Required

# On cloud (AWS EKS):
# - Check security groups
# - Check IAM permissions
# - Check AWS Load Balancer Controller
```

---

## 📝 Quick Reference

### Create Services

```bash
# Expose deployment
kubectl expose deployment nginx --port=80 --type=ClusterIP

# Expose pod
kubectl expose pod nginx --port=80 --type=NodePort

# From YAML
kubectl apply -f service.yaml
```

### View Services

```bash
kubectl get svc
kubectl get svc -A
kubectl describe svc <name>
kubectl get endpoints <name>
```

### Test Services

```bash
# From inside cluster
kubectl run test --image=busybox --rm -it -- wget -O- <service-name>

# Port forward
kubectl port-forward svc/<service-name> 8080:80

# Minikube
minikube service <service-name>
minikube service <service-name> --url
```

### Delete Services

```bash
kubectl delete svc <service-name>
kubectl delete -f service.yaml
```

---

## 📝 Quiz

1. What are the four service types?
2. What's the difference between ClusterIP and NodePort?
3. How do pods discover services?
4. What are endpoints?
5. What is a headless service?
6. Which service type provisions a cloud load balancer?
7. Can you access a ClusterIP service from outside the cluster?

---

## 🎓 Challenge Exercise

1. Create a deployment with 3 nginx replicas
2. Expose it with a ClusterIP service
3. Test access from another pod
4. Change to NodePort and access from your browser
5. Create a headless service and query DNS
6. Add session affinity
7. Scale deployment to 5 replicas and verify endpoints update

**Bonus:**
- Create services in different namespaces and test cross-namespace communication
- Set up a multi-port service
- Configure external traffic policy

---

## ⏭️ Next Steps

Continue to [Module 06: Deployments](./06-deployments.md)

---

**🎉 Congratulations!** You now understand Kubernetes networking and services!
