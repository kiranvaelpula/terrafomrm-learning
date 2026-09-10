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

## 📖 Understanding Namespaces & Quotas (Intuition First)

Picture a large office building shared by several companies. It's one physical building (your cluster), but each company gets its own floor with its own name on the door, its own rooms, and its own keycard access. Nobody from the third floor can wander into the fifth floor's offices. **Namespaces are those floors** — a way to carve a single physical cluster into isolated logical spaces for different teams, environments, or projects.

The reason namespaces matter is that clusters are expensive and often shared. Rather than spinning up separate clusters for dev, staging, and prod (costly and hard to manage), you run them side by side in one cluster, separated by namespace. Namespaces give you three things: **organization** (resources grouped logically), **name scoping** (two teams can both have a Service called `api` without clashing), and a **boundary for access control** — RBAC rules can grant a team access to only their namespace.

But isolation alone isn't enough. If the dev team's runaway deployment could gobble up every CPU in the cluster, it would starve the production apps sharing the same hardware. That's the "noisy neighbor" problem, and it's what **ResourceQuota** solves. A ResourceQuota is a cap on the *total* resources a whole namespace can consume — like telling the third-floor company "you get at most 20 CPUs and 40GB of RAM, period." Try to create a pod that would exceed the cap, and Kubernetes rejects it.

**LimitRange** works at a different scale: instead of capping the namespace total, it governs *individual* containers. It sets sensible defaults (so a pod that forgets to declare limits still gets some) and enforces per-container minimums and maximums (so nobody requests a single 64-CPU monster or an accidentally tiny amount). Think of ResourceQuota as the floor's total electricity budget, and LimitRange as the rule that no single appliance can draw more than a certain wattage.

You almost always use them together: LimitRange guarantees every pod has reasonable limits, and ResourceQuota ensures the sum of all pods never exceeds the namespace's allocation. One important gotcha — once a ResourceQuota exists, every pod *must* declare requests/limits or it gets rejected, which is exactly why LimitRange's defaults are so handy.

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

## 🎯 Interview Quick Points

- **Namespaces** are virtual clusters that isolate teams, environments, and projects within one physical cluster
- They provide organization, **name scoping** (same resource name allowed in different namespaces), and an RBAC boundary
- Built-in namespaces: **default**, **kube-system** (system components), **kube-public**, **kube-node-lease**
- Not everything is namespaced — cluster-scoped resources like **nodes, PVs, and namespaces themselves** are not
- **ResourceQuota** caps *total* resource consumption for an entire namespace (CPU, memory, pod count, PVCs, etc.)
- **LimitRange** sets **per-container** defaults, minimums, and maximums
- Use both together: LimitRange guarantees pods have limits; ResourceQuota caps the namespace total
- Gotcha: once a ResourceQuota exists, **every pod must declare requests/limits** or it's rejected — LimitRange defaults prevent this
- ResourceQuota solves the **noisy-neighbor** problem in multi-tenant clusters
- Set a default namespace with `kubectl config set-context --current --namespace=<name>` to avoid typing `-n` repeatedly
- Namespaces do **not** provide network isolation by default — that requires NetworkPolicies

---

## ⏭️ Next: [Module 13: RBAC & Security](./13-rbac-security.md)
