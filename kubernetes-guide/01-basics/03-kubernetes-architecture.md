# Module 03: Kubernetes Architecture

## 📚 What You'll Learn
- Kubernetes cluster components
- Control plane vs Worker nodes
- How components communicate
- The role of etcd, API server, scheduler, and more
- Request flow in Kubernetes

---

## 🏗️ Kubernetes Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │             Control Plane (Master Node)            │    │
│  │                                                     │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │    │
│  │  │   API    │  │  etcd    │  │ Scheduler│        │    │
│  │  │  Server  │  │          │  │          │        │    │
│  │  └──────────┘  └──────────┘  └──────────┘        │    │
│  │  ┌──────────────────────────────────────┐        │    │
│  │  │    Controller Manager                │        │    │
│  │  └──────────────────────────────────────┘        │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Worker Node  │  │ Worker Node  │  │ Worker Node  │    │
│  │              │  │              │  │              │    │
│  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │    │
│  │ │  kubelet │ │  │ │  kubelet │ │  │ │  kubelet │ │    │
│  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │    │
│  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │    │
│  │ │kube-proxy│ │  │ │kube-proxy│ │  │ │kube-proxy│ │    │
│  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │    │
│  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │    │
│  │ │Container │ │  │ │Container │ │  │ │Container │ │    │
│  │ │ Runtime  │ │  │ │ Runtime  │ │  │ │ Runtime  │ │    │
│  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │    │
│  │   (Pods)     │  │   (Pods)     │  │   (Pods)     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Control Plane Components

The **Control Plane** manages the cluster and makes decisions about scheduling, scaling, and maintaining cluster state.

### 1. API Server (kube-apiserver)

**What it does:** Front-end for Kubernetes. All communication goes through it.

```
User/kubectl → API Server → Other Components
     ↓
All requests validated and processed here
```

**Responsibilities:**
- Receives REST API requests
- Validates requests
- Updates etcd
- Entry point for all administrative tasks

**Example interaction:**
```bash
kubectl get pods
    ↓
API Server: "Let me check etcd..."
    ↓
Returns: List of pods
```

### 2. etcd

**What it does:** Distributed key-value store. The "brain" of Kubernetes.

```
etcd stores:
├── Cluster state
├── Configuration
├── Secrets
├── Service discovery info
└── Current state of all objects
```

**Think of it as:** A database that stores everything about your cluster.

**Example data:**
```json
{
  "pods": [
    {"name": "nginx-pod", "status": "Running", "node": "worker-1"},
    {"name": "redis-pod", "status": "Pending", "node": "worker-2"}
  ],
  "services": [...],
  "deployments": [...]
}
```

**Important:**
- Only API server talks to etcd
- Highly available (usually 3-5 replicas)
- Must be backed up regularly

### 3. Scheduler (kube-scheduler)

**What it does:** Decides which node runs which pod.

```
New Pod Created
    ↓
Scheduler: "Which node should run this?"
    ↓
Considers:
├── Resource requirements (CPU, memory)
├── Node availability
├── Affinity rules
├── Taints and tolerations
└── Current load
    ↓
Assigns pod to best node
```

**Example decision process:**
```
Pod needs: 2 CPU, 4GB RAM

Node 1: 1 CPU available ❌
Node 2: 3 CPU, 8GB RAM ✅ (Selected)
Node 3: 4 CPU, 2GB RAM ❌
```

### 4. Controller Manager (kube-controller-manager)

**What it does:** Runs multiple controllers that regulate cluster state.

**Key Controllers:**

#### Node Controller
```
Monitors node health
↓
Node down? → Mark as NotReady
↓
Evict pods after timeout
```

#### Replication Controller
```
Desired: 3 replicas
Current: 2 replicas
↓
Action: Create 1 more pod
```

#### Endpoints Controller
```
Service created
↓
Find matching pods
↓
Update endpoints
```

#### Service Account Controller
```
New namespace created
↓
Create default service account
```

**Example:**
```yaml
# You specify:
replicas: 3

# Controller ensures:
Current pods: 3
# If pod dies, controller creates new one
```

### 5. Cloud Controller Manager (optional)

**What it does:** Interacts with cloud provider APIs (AWS, Azure, GCP).

```
Manages:
├── Load Balancers
├── Storage Volumes
├── Routes
└── Nodes (cloud VMs)
```

---

## 👷 Worker Node Components

Worker nodes run your applications (pods).

### 1. kubelet

**What it does:** Agent that runs on each node. Ensures containers are running.

```
API Server: "Run this pod on your node"
    ↓
kubelet: 
├── Pulls container image
├── Starts containers
├── Monitors container health
├── Reports status to API server
└── Restarts failed containers
```

**Think of it as:** A supervisor that makes sure your containers are doing their job.

**Example flow:**
```bash
1. API Server → kubelet: "Run nginx pod"
2. kubelet → Container Runtime: "Start nginx container"
3. kubelet → API Server: "nginx is running"
4. (Container crashes)
5. kubelet: "Detected crash, restarting..."
6. kubelet → API Server: "nginx restarted"
```

### 2. kube-proxy

**What it does:** Manages network rules for pod communication.

```
Enables:
├── Pod-to-pod communication
├── Service discovery
├── Load balancing
└── External access to services
```

**How it works:**
```
Request to Service
    ↓
kube-proxy: "Which pod should handle this?"
    ↓
Forwards to appropriate pod
```

**Example:**
```bash
# Service: my-app (3 pods)
Request comes in
    ↓
kube-proxy distributes:
Request 1 → Pod 1
Request 2 → Pod 2
Request 3 → Pod 3
Request 4 → Pod 1 (round-robin)
```

### 3. Container Runtime

**What it does:** Actually runs the containers.

**Options:**
- **containerd** (most common)
- **CRI-O**
- **Docker** (deprecated but still works)

```
kubelet: "Start this container"
    ↓
Container Runtime:
├── Pull image
├── Create container
├── Start container
└── Report status
```

---

## 🔄 How It All Works Together

### Example: Deploying nginx

```
1. User runs:
   kubectl create deployment nginx --image=nginx --replicas=3

2. kubectl → API Server: "Create deployment"

3. API Server:
   ├── Validates request
   ├── Saves to etcd
   └── Responds: "Deployment created"

4. Controller Manager (Deployment Controller):
   ├── Sees new deployment in etcd
   ├── Creates ReplicaSet
   └── ReplicaSet creates 3 pod objects

5. Scheduler:
   ├── Sees 3 unscheduled pods
   ├── Finds best nodes
   └── Assigns: Pod1→Node1, Pod2→Node2, Pod3→Node3

6. kubelet (on each node):
   ├── Sees pod assigned to it
   ├── Pulls nginx image
   ├── Starts container
   └── Reports status: Running

7. Controller Manager:
   ├── Monitors pod count
   └── If pod dies, creates new one

8. kube-proxy:
   └── Updates network rules for pod communication
```

---

## 🎪 Lab: Explore Your Cluster

### Step 1: Check Cluster Info

```bash
# Get cluster information
kubectl cluster-info

# Output:
# Kubernetes control plane is running at https://...
# CoreDNS is running at https://...
```

### Step 2: List All Nodes

```bash
# Get nodes
kubectl get nodes

# Get detailed node info
kubectl get nodes -o wide

# Describe a node
kubectl describe node <node-name>
```

### Step 3: Check Control Plane Pods

```bash
# View system pods
kubectl get pods -n kube-system

# You'll see:
# - kube-apiserver
# - etcd
# - kube-scheduler
# - kube-controller-manager
# - coredns
# - kube-proxy

# Describe API server pod
kubectl describe pod -n kube-system <api-server-pod-name>
```

### Step 4: Check Component Status

```bash
# Check component health
kubectl get componentstatuses

# Or (newer versions)
kubectl get --raw='/readyz?verbose'
```

### Step 5: View Cluster Events

```bash
# See what's happening in cluster
kubectl get events --all-namespaces

# Watch events in real-time
kubectl get events --all-namespaces --watch
```

---

## 📊 Request Flow Example

### Creating a Pod

```
┌──────────┐
│  User    │ kubectl create -f pod.yaml
└────┬─────┘
     │
     ↓
┌────────────────┐
│  API Server    │ 1. Validate YAML
│                │ 2. Authenticate user
│                │ 3. Authorize request
└────┬───────────┘
     │
     ↓
┌────────────┐
│   etcd     │ 4. Store pod definition
└────┬───────┘
     │
     ↓
┌────────────────┐
│  Scheduler     │ 5. Watch for unscheduled pods
│                │ 6. Select best node
│                │ 7. Update pod with node assignment
└────┬───────────┘
     │
     ↓
┌────────────────┐
│  API Server    │ 8. Notify kubelet about new pod
└────┬───────────┘
     │
     ↓
┌────────────────┐
│  kubelet       │ 9. Pull image
│  (on node)     │ 10. Create container
│                │ 11. Start container
│                │ 12. Report status
└────┬───────────┘
     │
     ↓
┌────────────────┐
│  API Server    │ 13. Update pod status in etcd
└────┬───────────┘
     │
     ↓
┌──────────┐
│  User    │ kubectl get pods → Pod Running ✅
└──────────┘
```

---

## 🔍 Key Concepts

### Master vs Worker

| Master (Control Plane) | Worker Nodes |
|------------------------|--------------|
| Makes decisions | Executes decisions |
| Schedules workloads | Runs workloads |
| Stores cluster state | Reports node state |
| Manages cluster | Runs containers |

### Desired State vs Current State

```
Desired State (what you want):
- 3 nginx pods running
- Version: v1.21
- 2GB memory each

Current State (what exists):
- 2 nginx pods running (one crashed)
- Version: v1.21
- 2GB memory each

Kubernetes constantly works to match current → desired
```

### Declarative vs Imperative

**Declarative (Recommended):**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 3
  # ...

# Apply
kubectl apply -f deployment.yaml
```

**Imperative:**
```bash
# Direct commands
kubectl create deployment nginx --image=nginx --replicas=3
kubectl scale deployment nginx --replicas=5
kubectl set image deployment/nginx nginx=nginx:1.21
```

---

## 🧩 Add-on Components

### CoreDNS
```
Purpose: Internal DNS for service discovery

Example:
Pod wants to access "my-service"
↓
CoreDNS resolves: my-service → 10.100.200.1
```

### Dashboard
```
Web UI for Kubernetes cluster
```

### Metrics Server
```
Collects resource metrics (CPU, memory)
Required for: kubectl top, HPA
```

### Ingress Controller
```
Manages external access to services
Acts as smart load balancer
```

---

## 💡 Architecture Best Practices

### High Availability

```
Production Setup:
├── 3+ Control Plane nodes (odd number)
├── 3+ etcd instances
├── Multiple worker nodes
└── Load balancer for API server
```

### Separation of Concerns

```
Control Plane:
- Don't run workloads
- Dedicated nodes
- Higher resources

Worker Nodes:
- Run application workloads
- Can be scaled independently
- Can use spot instances (AWS)
```

### Security

```
├── API server: TLS encryption
├── etcd: Encrypted at rest
├── RBAC: Role-based access
└── Network policies: Pod isolation
```

---

## 📝 Quiz

1. What is the role of the API server?
2. What does etcd store?
3. What decides which node runs a pod?
4. What is kubelet responsible for?
5. What is the difference between desired state and current state?
6. Which component restarts containers if they crash?
7. What does kube-proxy do?

### Answers:
1. Front-end for Kubernetes, handles all API requests
2. Cluster state, configuration, all object definitions
3. Scheduler (kube-scheduler)
4. Running containers on the node, reporting status
5. Desired = what you want, Current = what exists now
6. kubelet (on the worker node)
7. Manages network rules, enables service discovery and load balancing

---

## 🎓 Challenge Exercise

### Architecture Exploration

1. Draw the architecture of your cluster
2. List all control plane components in your cluster
3. Count how many worker nodes you have
4. Find the API server endpoint
5. Check etcd is running
6. View logs of the scheduler
7. Explain (in your own words) what happens when you create a deployment

**Bonus:**
- What happens if the API server goes down?
- What happens if a worker node goes down?
- How does Kubernetes ensure high availability?

---

## 🔧 Common Architecture Patterns

### Single-Node Cluster
```
┌─────────────────────┐
│   All-in-One Node   │
│  (Control + Worker) │
│                     │
│  ← Development only │
└─────────────────────┘
```

### Multi-Node Cluster
```
┌─────────────┐
│Control Plane│
└──────┬──────┘
       │
   ┌───┴───┬─────┐
   │       │     │
┌──▼───┐┌──▼─┐┌──▼─┐
│Worker││Work││Work│
└──────┘└────┘└────┘

← Production
```

### High Availability
```
┌────┐ ┌────┐ ┌────┐
│ CP │ │ CP │ │ CP │ ← 3 Control Planes
└─┬──┘ └─┬──┘ └─┬──┘
  │      │      │
  └──┬───┴───┬──┘
     │       │
  ┌──▼─┐  ┌──▼─┐  ┌────┐
  │Work│  │Work│  │Work│ ← N Workers
  └────┘  └────┘  └────┘
```

---

## ⏭️ Next Steps

Ready to run your first pod? Continue to [Module 04: Pods](./04-pods.md)

---

## 📚 Additional Resources

- [Kubernetes Components](https://kubernetes.io/docs/concepts/overview/components/)
- [Cluster Architecture](https://kubernetes.io/docs/concepts/architecture/)
- [Interactive Architecture Diagram](https://kubernetes.io/docs/concepts/architecture/cloud-controller/)

---

**🎉 Congratulations!** You now understand how Kubernetes works under the hood!
