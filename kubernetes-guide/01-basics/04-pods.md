# Module 04: Pods - The Smallest Unit

## 📚 What You'll Learn
- What is a Pod
- Creating and managing Pods
- Pod lifecycle
- Multi-container Pods
- Pod patterns
- Debugging Pods

---

## 🎯 What is a Pod?

A **Pod** is the smallest deployable unit in Kubernetes. It's a wrapper around one or more containers.

### Simple Analogy
```
Pod = Apartment
Containers = Roommates

- Roommates share:
  ✅ Same address (IP)
  ✅ Same kitchen (storage)
  ✅ Same utilities (network)
  
- But each has:
  ✅ Own room (container)
  ✅ Own belongings (files)
```

### Visual Representation
```
┌────────────────────────────┐
│          Pod               │
│  IP: 10.244.1.5            │
│                            │
│  ┌──────────────────────┐  │
│  │  Container: nginx    │  │
│  │  Port: 80            │  │
│  └──────────────────────┘  │
│                            │
│  Shared:                   │
│  - Network namespace       │
│  - Storage volumes         │
│  - IPC namespace           │
└────────────────────────────┘
```

---

## 📝 Creating Your First Pod

### Method 1: Imperative (Quick)

```bash
# Create nginx pod
kubectl run nginx --image=nginx

# Check pod
kubectl get pods

# Output:
# NAME    READY   STATUS    RESTARTS   AGE
# nginx   1/1     Running   0          10s
```

### Method 2: Declarative (Recommended)

```yaml
# pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
    environment: dev
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
```

```bash
# Create pod
kubectl apply -f pod.yaml

# Verify
kubectl get pods
```

---

## 🎪 Lab 1: Creating and Managing Pods

### Step 1: Create Simple Pod

```bash
# Create pod
kubectl run my-nginx --image=nginx

# Watch pod starting
kubectl get pods --watch

# Press Ctrl+C when Running
```

### Step 2: Get Pod Details

```bash
# List pods
kubectl get pods

# More details
kubectl get pods -o wide

# Full information
kubectl describe pod my-nginx

# Get as YAML
kubectl get pod my-nginx -o yaml

# Get as JSON
kubectl get pod my-nginx -o json
```

### Step 3: Execute Commands in Pod

```bash
# Execute command
kubectl exec my-nginx -- ls /usr/share/nginx/html

# Interactive shell
kubectl exec -it my-nginx -- /bin/bash

# Inside container:
ls
cat /etc/nginx/nginx.conf
exit
```

### Step 4: View Logs

```bash
# View logs
kubectl logs my-nginx

# Follow logs (tail -f)
kubectl logs -f my-nginx

# Previous logs (if restarted)
kubectl logs my-nginx --previous
```

### Step 5: Port Forward

```bash
# Forward port 8080 (local) → 80 (pod)
kubectl port-forward my-nginx 8080:80

# In another terminal or browser:
curl localhost:8080
# or visit: http://localhost:8080

# Press Ctrl+C to stop
```

### Step 6: Delete Pod

```bash
# Delete pod
kubectl delete pod my-nginx

# Force delete (if stuck)
kubectl delete pod my-nginx --force --grace-period=0
```

---

## 📋 Complete Pod YAML Example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: advanced-pod
  labels:
    app: myapp
    tier: frontend
    version: v1
  annotations:
    description: "Example pod with all options"
spec:
  # Container specification
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
      protocol: TCP
    
    # Environment variables
    env:
    - name: ENVIRONMENT
      value: "production"
    - name: LOG_LEVEL
      value: "info"
    
    # Resource limits
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
    
    # Health checks
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 30
      periodSeconds: 10
    
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5
    
    # Volume mounts
    volumeMounts:
    - name: html
      mountPath: /usr/share/nginx/html
  
  # Volumes
  volumes:
  - name: html
    emptyDir: {}
  
  # Restart policy
  restartPolicy: Always
```

---

## 🔄 Pod Lifecycle

### Pod Phases

```
Pending
  ↓
  Image pulling...
  ↓
Running
  ↓
  (Container exits)
  ↓
Succeeded or Failed
```

### Detailed States

| Phase | Description |
|-------|-------------|
| **Pending** | Pod accepted, but not running yet |
| **Running** | At least one container running |
| **Succeeded** | All containers completed successfully |
| **Failed** | At least one container failed |
| **Unknown** | Cannot determine pod state |

### Container States

```bash
# Check container states
kubectl describe pod <pod-name>

# Look for:
# - Waiting: Image pull, crash loop
# - Running: Container executing
# - Terminated: Container exited
```

---

## 🎪 Lab 2: Multi-Container Pods

### Sidecar Pattern

```yaml
# sidecar-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-pod
spec:
  containers:
  # Main application
  - name: app
    image: nginx
    ports:
    - containerPort: 80
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/nginx
  
  # Sidecar: Log shipper
  - name: log-shipper
    image: busybox
    command: ['sh', '-c', 'tail -f /logs/access.log']
    volumeMounts:
    - name: shared-logs
      mountPath: /logs
  
  volumes:
  - name: shared-logs
    emptyDir: {}
```

```bash
# Create pod
kubectl apply -f sidecar-pod.yaml

# Check both containers
kubectl get pod sidecar-pod

# Should show: READY 2/2

# View logs from main container
kubectl logs sidecar-pod -c app

# View logs from sidecar
kubectl logs sidecar-pod -c log-shipper

# Exec into specific container
kubectl exec -it sidecar-pod -c app -- /bin/bash
```

---

## 🎨 Common Pod Patterns

### 1. Sidecar Pattern
```
┌─────────────────────┐
│       Pod           │
│  ┌──────┐ ┌──────┐  │
│  │ App  │ │ Log  │  │
│  │      │→│Shipr │  │
│  └──────┘ └──────┘  │
└─────────────────────┘

Use case: Logging, monitoring, proxies
```

### 2. Ambassador Pattern
```
┌─────────────────────┐
│       Pod           │
│  ┌──────┐ ┌──────┐  │
│  │ App  │→│Proxy │→ External
│  │      │ │      │  │ Service
│  └──────┘ └──────┘  │
└─────────────────────┘

Use case: Database proxy, API gateway
```

### 3. Adapter Pattern
```
┌─────────────────────┐
│       Pod           │
│  ┌──────┐ ┌──────┐  │
│  │ App  │→│Adapt-│  │
│  │      │ │ er   │  │
│  └──────┘ └──────┘  │
└─────────────────────┘

Use case: Data format conversion
```

---

## 🏥 Health Checks

### Liveness Probe
```yaml
# Checks if container is alive
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

# If fails → Restart container
```

### Readiness Probe
```yaml
# Checks if container is ready for traffic
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5

# If fails → Remove from service endpoints
```

### Startup Probe
```yaml
# For slow-starting containers
startupProbe:
  httpGet:
    path: /startup
    port: 8080
  failureThreshold: 30
  periodSeconds: 10

# Gives container time to start
```

### Example with All Probes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: health-check-pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    ports:
    - containerPort: 8080
    
    # Startup probe (runs first)
    startupProbe:
      httpGet:
        path: /startup
        port: 8080
      failureThreshold: 30
      periodSeconds: 10
    
    # Liveness probe (after startup)
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 0
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
    
    # Readiness probe
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 0
      periodSeconds: 5
      timeoutSeconds: 3
```

---

## 💻 Resource Management

### Resource Requests & Limits

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-pod
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:  # Minimum required
        memory: "64Mi"
        cpu: "250m"  # 0.25 CPU
      limits:    # Maximum allowed
        memory: "128Mi"
        cpu: "500m"  # 0.5 CPU
```

### CPU Units
```
1000m = 1 CPU
500m = 0.5 CPU
250m = 0.25 CPU
100m = 0.1 CPU
```

### Memory Units
```
128Mi = 128 Mebibytes
1Gi = 1 Gibibyte
1000Mi = ~1Gi
```

### What Happens?
```
Pod requests: 250m CPU, 64Mi memory
↓
Scheduler: Finds node with available resources
↓
Node has: 500m CPU, 128Mi memory available
↓
Pod scheduled ✅

If pod exceeds limits:
- CPU: Throttled
- Memory: Killed (OOMKilled)
```

---

## 🎪 Lab 3: Debugging Pods

### Common Issues

#### 1. ImagePullBackOff

```bash
# Symptom
kubectl get pods
# nginx   0/1   ImagePullBackOff   0   2m

# Diagnose
kubectl describe pod nginx

# Look for:
# Failed to pull image "nginx:wrong-tag": not found

# Fix
# Use correct image tag
```

#### 2. CrashLoopBackOff

```bash
# Symptom
kubectl get pods
# app   0/1   CrashLoopBackOff   5   5m

# Diagnose
kubectl logs app
kubectl logs app --previous  # Previous run

# Common causes:
# - Application error
# - Missing environment variables
# - Wrong command/args
```

#### 3. Pending

```bash
# Symptom
kubectl get pods
# big-app   0/1   Pending   0   2m

# Diagnose
kubectl describe pod big-app

# Look for:
# - Insufficient CPU/memory
# - No nodes available
# - Volume not available
```

### Debugging Commands

```bash
# 1. Check pod status
kubectl get pods
kubectl get pods -o wide

# 2. Describe pod (most useful!)
kubectl describe pod <pod-name>

# 3. Check logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous
kubectl logs <pod-name> -c <container-name>

# 4. Execute commands
kubectl exec <pod-name> -- ls /app
kubectl exec -it <pod-name> -- /bin/bash

# 5. Check events
kubectl get events --sort-by='.lastTimestamp'

# 6. Port forward for testing
kubectl port-forward <pod-name> 8080:80

# 7. Get YAML
kubectl get pod <pod-name> -o yaml

# 8. Watch for changes
kubectl get pods --watch
```

---

## 📝 Quick Reference

### Create Pods

```bash
# Imperative
kubectl run nginx --image=nginx
kubectl run nginx --image=nginx --port=80 --labels="app=web"

# Declarative
kubectl apply -f pod.yaml
kubectl create -f pod.yaml
```

### View Pods

```bash
kubectl get pods
kubectl get pods -o wide
kubectl get pods -A  # All namespaces
kubectl get pods --show-labels
kubectl get pods -l app=nginx  # Filter by label
```

### Interact with Pods

```bash
kubectl logs <pod>
kubectl logs -f <pod>  # Follow
kubectl exec <pod> -- <command>
kubectl exec -it <pod> -- /bin/bash
kubectl port-forward <pod> 8080:80
kubectl cp <pod>:/path/file ./file  # Copy from pod
kubectl cp ./file <pod>:/path/file  # Copy to pod
```

### Delete Pods

```bash
kubectl delete pod <pod-name>
kubectl delete -f pod.yaml
kubectl delete pods --all
```

---

## 📝 Quiz

1. What is a Pod?
2. Can a Pod contain multiple containers?
3. What's the difference between liveness and readiness probes?
4. What does "CrashLoopBackOff" mean?
5. What happens if a container exceeds its memory limit?
6. How do containers in the same pod communicate?
7. What command shows why a pod failed to start?

---

## 🎓 Challenge Exercise

1. Create a pod running nginx
2. Add a liveness probe checking port 80
3. Add a readiness probe checking /index.html
4. Set resource requests: 100m CPU, 64Mi memory
5. Set resource limits: 200m CPU, 128Mi memory
6. Add labels: app=web, tier=frontend
7. Exec into the pod and create /usr/share/nginx/html/health.html
8. Port forward and test in browser
9. View logs
10. Delete the pod

**Bonus:**
- Create a multi-container pod with nginx + busybox
- Make them share a volume
- Have busybox write logs that nginx serves

---

## ⏭️ Next Steps

Continue to [Module 05: Services & Networking](./05-services-networking.md)

---

**🎉 Congratulations!** You now understand Pods and can create and debug them!
