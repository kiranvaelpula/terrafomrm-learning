# Module 06: Deployments

## 📚 What You'll Learn
- What is a Deployment
- Creating and managing Deployments
- Rolling updates and rollbacks
- Scaling applications
- Deployment strategies

---

## 🎯 What is a Deployment?

A **Deployment** manages ReplicaSets and provides declarative updates for Pods.

### Problem without Deployments:
```
Manual management:
- Create pods manually
- If pod dies, manually recreate
- Update = delete old, create new
- No rollback
- Downtime during updates
```

### With Deployments:
```
Automated management:
✅ Maintains desired number of pods
✅ Self-healing (recreates failed pods)
✅ Rolling updates (zero downtime)
✅ Easy rollbacks
✅ Scaling up/down
✅ Version history
```

---

## 📝 Creating a Deployment

### Basic Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
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
# Create deployment
kubectl apply -f deployment.yaml

# Get deployments
kubectl get deployments

# Get pods created by deployment
kubectl get pods -l app=nginx
```

---

## 🎪 Lab 1: Basic Deployment Operations

### Step 1: Create Deployment

```bash
# Imperative way
kubectl create deployment nginx --image=nginx:1.21 --replicas=3

# Or declarative (recommended)
cat <<EOF | kubectl apply -f -
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
EOF
```

### Step 2: Check Status

```bash
# View deployment
kubectl get deployment nginx-deployment

# Output:
# NAME               READY   UP-TO-DATE   AVAILABLE   AGE
# nginx-deployment   3/3     3            3           30s

# Describe deployment
kubectl describe deployment nginx-deployment

# View ReplicaSets
kubectl get rs

# View Pods
kubectl get pods -l app=nginx
```

### Step 3: Scale Deployment

```bash
# Scale to 5 replicas
kubectl scale deployment nginx-deployment --replicas=5

# Watch pods being created
kubectl get pods -l app=nginx --watch

# Scale down to 2
kubectl scale deployment nginx-deployment --replicas=2
```

### Step 4: Update Image

```bash
# Update to new version
kubectl set image deployment/nginx-deployment nginx=nginx:1.22

# Watch rollout
kubectl rollout status deployment/nginx-deployment

# Check rollout history
kubectl rollout history deployment/nginx-deployment
```

### Step 5: Rollback

```bash
# Undo last rollout
kubectl rollout undo deployment/nginx-deployment

# Rollback to specific revision
kubectl rollout undo deployment/nginx-deployment --to-revision=1

# Check status
kubectl rollout status deployment/nginx-deployment
```

---

## 🔄 Rolling Updates

### How Rolling Updates Work

```
Initial State (v1.0):
Pod1(v1.0)  Pod2(v1.0)  Pod3(v1.0)

Update triggered (v2.0):
Pod1(v1.0)  Pod2(v1.0)  Pod3(v1.0)  Pod4(v2.0)
                                      ↑ New pod starting

Once Pod4 ready:
Pod1(v1.0)  Pod2(v1.0)  Pod3(v1.0)  Pod4(v2.0)
Pod5(v2.0)
↑ Next new pod

Pod1 terminated:
            Pod2(v1.0)  Pod3(v1.0)  Pod4(v2.0)
Pod5(v2.0)

Continue until all updated:
Pod4(v2.0)  Pod5(v2.0)  Pod6(v2.0)
```

### Rolling Update Strategy

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Max extra pods during update
      maxUnavailable: 1  # Max unavailable pods
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

**Parameters:**
- `maxSurge`: Maximum number of extra pods (1 = 4 total during update)
- `maxUnavailable`: Maximum unavailable pods (1 = minimum 2 available)

---

## 🎪 Lab 2: Rolling Update Practice

### Step 1: Create Deployment with Service

```yaml
# app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
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
spec:
  selector:
    app: web
  ports:
  - port: 80
  type: NodePort
```

```bash
kubectl apply -f app-deployment.yaml
```

### Step 2: Monitor Baseline

```bash
# Check current state
kubectl get deployment web-app
kubectl get pods -l app=web

# In another terminal, watch pods
kubectl get pods -l app=web --watch
```

### Step 3: Perform Rolling Update

```bash
# Update image
kubectl set image deployment/web-app nginx=nginx:1.22

# In watch terminal, you'll see:
# - New pods being created
# - Old pods being terminated
# - Never all pods down at once

# Check rollout status
kubectl rollout status deployment/web-app
```

### Step 4: View Rollout History

```bash
# View history
kubectl rollout history deployment/web-app

# View specific revision
kubectl rollout history deployment/web-app --revision=2
```

### Step 5: Test Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/web-app

# Rollback to specific revision
kubectl rollout undo deployment/web-app --to-revision=1

# Pause rollout (for testing)
kubectl rollout pause deployment/web-app

# Resume rollout
kubectl rollout resume deployment/web-app
```

---

## 🎨 Deployment Strategies

### 1. RollingUpdate (Default)

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%
    maxUnavailable: 25%
```

**Pros:** Zero downtime, gradual rollout
**Cons:** Both versions run simultaneously

### 2. Recreate

```yaml
strategy:
  type: Recreate
```

**How it works:**
```
1. Terminate all old pods
2. Wait for termination
3. Create all new pods

Downtime: YES
```

**Use case:** When you can't run two versions simultaneously

### 3. Blue-Green (Manual)

```yaml
# Blue deployment (current)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: app
        image: myapp:1.0
---
# Green deployment (new)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: app
        image: myapp:2.0
---
# Service (switch by changing selector)
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp
    version: blue  # Switch to 'green' when ready
  ports:
  - port: 80
```

### 4. Canary (Manual)

```yaml
# Main deployment (90%)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
        version: stable
    spec:
      containers:
      - name: app
        image: myapp:1.0
---
# Canary deployment (10%)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
        version: canary
    spec:
      containers:
      - name: app
        image: myapp:2.0
```

---

## 📊 Auto-scaling

### Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

```bash
# Create HPA
kubectl apply -f hpa.yaml

# Or using kubectl
kubectl autoscale deployment web-app --cpu-percent=70 --min=2 --max=10

# View HPA
kubectl get hpa

# Watch scaling
kubectl get hpa --watch
```

---

## 🎪 Lab 3: Complete Production Deployment

```yaml
# production-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: production-app
  labels:
    app: myapp
    environment: production
spec:
  replicas: 5
  
  # Update strategy
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  
  # How long to wait before marking failed
  progressDeadlineSeconds: 600
  
  # Keep history
  revisionHistoryLimit: 10
  
  selector:
    matchLabels:
      app: myapp
  
  template:
    metadata:
      labels:
        app: myapp
        version: v1.0
    spec:
      containers:
      - name: app
        image: nginx:1.21
        ports:
        - containerPort: 80
          name: http
        
        # Resource limits
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
        
        # Health checks
        livenessProbe:
          httpGet:
            path: /healthz
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        # Environment variables
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "info"
      
      # Anti-affinity for high availability
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - myapp
              topologyKey: kubernetes.io/hostname
---
apiVersion: v1
kind: Service
metadata:
  name: production-service
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: production-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: production-app
  minReplicas: 5
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 🐛 Troubleshooting Deployments

### Issue 1: Pods Not Starting

```bash
# Check deployment status
kubectl get deployment <name>

# Check events
kubectl describe deployment <name>

# Check pod status
kubectl get pods -l app=<label>
kubectl describe pod <pod-name>

# Common causes:
# - Image pull errors
# - Insufficient resources
# - Failed health checks
```

### Issue 2: Rollout Stuck

```bash
# Check rollout status
kubectl rollout status deployment/<name>

# Check events
kubectl describe deployment <name>

# Rollback if needed
kubectl rollout undo deployment/<name>

# Common causes:
# - Readiness probe failing
# - Not enough resources
# - Image doesn't exist
```

### Issue 3: Pods Crashing

```bash
# View logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous

# Check events
kubectl describe pod <pod-name>

# Common causes:
# - Application errors
# - OOMKilled (out of memory)
# - CrashLoopBackOff
```

---

## 📝 Best Practices

### 1. Always Use Deployments (Not Pods Directly)

```bash
# ❌ Don't
kubectl run nginx --image=nginx

# ✅ Do
kubectl create deployment nginx --image=nginx
```

### 2. Set Resource Limits

```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "100m"
  limits:
    memory: "128Mi"
    cpu: "200m"
```

### 3. Always Use Health Checks

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
```

### 4. Use Labels Wisely

```yaml
labels:
  app: myapp
  tier: frontend
  environment: production
  version: v1.0
```

### 5. Keep Revision History

```yaml
spec:
  revisionHistoryLimit: 10
```

---

## 📝 Quick Reference

```bash
# Create
kubectl create deployment nginx --image=nginx --replicas=3

# Get
kubectl get deployments
kubectl get deployment nginx -o yaml

# Scale
kubectl scale deployment nginx --replicas=5

# Update
kubectl set image deployment/nginx nginx=nginx:1.22
kubectl edit deployment nginx

# Rollout
kubectl rollout status deployment/nginx
kubectl rollout history deployment/nginx
kubectl rollout undo deployment/nginx
kubectl rollout pause deployment/nginx
kubectl rollout resume deployment/nginx

# Auto-scale
kubectl autoscale deployment nginx --cpu-percent=70 --min=2 --max=10

# Delete
kubectl delete deployment nginx
```

---

## 📝 Quiz

1. What does a Deployment manage?
2. What's the difference between Recreate and RollingUpdate?
3. How do you rollback a deployment?
4. What is maxSurge and maxUnavailable?
5. What happens during a rolling update?
6. How do you scale a deployment?
7. What is HPA?

---

## 🎓 Challenge Exercise

1. Create a deployment with 5 replicas
2. Add liveness and readiness probes
3. Set resource requests and limits
4. Configure rolling update strategy
5. Create a service to expose it
6. Update to new image version
7. Monitor the rollout
8. Rollback to previous version
9. Set up HPA for auto-scaling
10. Test scaling under load

---

## ⏭️ Next Steps

Continue to [Module 07: ConfigMaps & Secrets](./07-configmaps-secrets.md)

---

**🎉 Congratulations!** You now master Kubernetes Deployments!
