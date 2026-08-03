# Module 12: Namespaces & Resource Quotas

## What are Namespaces?

Namespaces are virtual clusters inside your physical cluster. They provide isolation between teams, environments, or projects running on the same cluster.

**When to use:**
- Separate dev, staging, and prod environments on one cluster
- Isolate teams so they can't accidentally mess with each other's resources
- Apply resource limits per team/project
- Control access with RBAC (team A can only access namespace A)

**Default namespaces:**
- `default` — where resources go if you don't specify a namespace
- `kube-system` — Kubernetes system components (DNS, scheduler, etc.)
- `kube-public` — publicly readable (rarely used)
- `kube-node-lease` — node heartbeat data

---

## 📚 Creating and Using Namespaces

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

# Set default namespace for your context (so you don't type -n every time)
kubectl config set-context --current --namespace=development

# Run commands in a specific namespace
kubectl get pods -n production
```

---

## 📊 ResourceQuota

**What is it?** A hard limit on total resources a namespace can consume. Prevents one team from eating all cluster resources.

**When to use:**
- Multi-tenant clusters where you charge back by resource usage
- Preventing a runaway deployment from consuming all CPU/memory
- Enforcing cost budgets per team

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: development
spec:
  hard:
    requests.cpu: "10"              # Total CPU requests can't exceed 10 cores
    requests.memory: 20Gi           # Total memory requests can't exceed 20Gi
    limits.cpu: "20"                # Total CPU limits can't exceed 20 cores
    limits.memory: 40Gi             # Total memory limits can't exceed 40Gi
    pods: "50"                      # Max 50 pods in this namespace
    services: "10"                  # Max 10 services
    persistentvolumeclaims: "20"    # Max 20 PVCs
```

**In plain English:** "The development namespace can use at most 10 CPU cores, 20GB RAM, and 50 pods total. If someone tries to create a pod that would push the total over the limit, it gets rejected."

**Important:** Once a ResourceQuota exists in a namespace, ALL pods must specify resource requests/limits — otherwise they'll be rejected.

---

## 📏 LimitRange

**What is it?** Default resource limits for individual containers. If someone forgets to set limits, LimitRange fills in defaults.

**When to use:**
- Ensure every pod has resource limits (prevents a single pod from hogging the node)
- Set minimum sizes so people don't accidentally request too little
- Provide sensible defaults so developers don't need to think about it

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: dev-limits
  namespace: development
spec:
  limits:
  - max:
      cpu: "2"                    # No single container can request more than 2 CPUs
      memory: "4Gi"               # No single container can use more than 4Gi
    min:
      cpu: "100m"                 # Must request at least 100m CPU
      memory: "64Mi"              # Must request at least 64Mi memory
    default:                      # If not specified, apply these limits
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:               # If not specified, apply these requests
      cpu: "250m"
      memory: "256Mi"
    type: Container
```

**In plain English:** "Every container in dev namespace gets 250m CPU and 256Mi memory by default. Nobody can request more than 2 CPUs or 4Gi memory per container."

---

## ResourceQuota vs LimitRange

| | ResourceQuota | LimitRange |
|---|---|---|
| Scope | Entire namespace (total) | Individual container |
| Purpose | Cap total usage | Set per-pod defaults/limits |
| Example | "Namespace can't exceed 20 CPUs total" | "No single pod can use more than 2 CPUs" |

You typically use BOTH together — LimitRange ensures every pod has limits, ResourceQuota caps the total.

---

## ⏭️ Next: [Module 13: RBAC & Security](./13-rbac-security.md)
