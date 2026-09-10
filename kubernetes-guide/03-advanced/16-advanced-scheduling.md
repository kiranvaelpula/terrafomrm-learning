# Module 16: Advanced Scheduling

## 📖 Understanding Advanced Scheduling (Intuition First)

By default, the Kubernetes scheduler is like a hotel clerk who just puts each guest in whatever room happens to be free. That's fine most of the time, but sometimes you have specific needs: a guest who requires a ground-floor room, two colleagues who want adjacent rooms, or a VIP who must never be bumped. Advanced scheduling is the set of tools that let you give the scheduler these instructions instead of leaving placement to chance.

The tools split neatly by *who is expressing the preference*. **Affinity** is the pod speaking: "I *want* to go somewhere." **Node affinity** lets a pod demand or prefer certain node types ("put me on an SSD node" or "prefer zone us-east-1a"). **Pod affinity** lets a pod ask to sit near other pods ("keep me on the same node as the cache for low latency"), while **pod anti-affinity** asks for the opposite ("spread my replicas across different nodes so one failure doesn't take them all down"). Anti-affinity is one of the most important high-availability tools you have.

Every affinity rule comes in two strengths, and the distinction is crucial. **Required** (`requiredDuringScheduling...`) is a hard constraint — no matching node, no scheduling; the pod stays Pending. **Preferred** is a soft wish with a weight — the scheduler tries its best but will place the pod elsewhere rather than leave it stuck. Choosing between them is really choosing between "this must happen" and "this would be nice."

**Taints and tolerations** flip the perspective: now the *node* is speaking. A taint is a node saying "keep out unless you have a pass." A toleration is the pass a pod carries to be allowed in. This is how you reserve GPU nodes for GPU workloads, dedicate nodes to a team, or cordon a node for maintenance (a `NoExecute` taint even evicts pods that lack the toleration). Note that a toleration only *permits* a pod onto a tainted node — it doesn't *attract* it there, which is why taints and node affinity are often used together.

Finally, **priority and preemption** handle the "who wins when the cluster is full" question. Each pod can carry a PriorityClass, and when a high-priority pod can't fit, the scheduler will evict lower-priority pods to make room (preemption). This guarantees that critical production workloads aren't blocked by disposable batch jobs. Together, these mechanisms turn scheduling from "wherever it fits" into a deliberate expression of your performance, availability, and business-priority requirements.

---

## 🎯 Node Affinity

### What is Node Affinity?

Node Affinity is a way to tell Kubernetes "I want my pod to run on a specific type of node." It's like saying "put me on a node that has SSD disks" or "prefer nodes in zone us-east-1a."

**When to use:**
- You have different node types (GPU nodes, SSD nodes, high-memory nodes) and certain apps need specific hardware
- You want workloads in specific availability zones for latency reasons
- You want to separate workloads by team or purpose across different node groups

**Two types:**
- `required` — hard rule, pod will NOT schedule if no matching node exists (stays pending)
- `preferred` — soft rule, Kubernetes will TRY to match but will still schedule somewhere else if needed

### Required Node Affinity

"My pod MUST go on a node with SSD disk. If no such node exists, don't schedule at all."

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: with-node-affinity
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disk-type
            operator: In
            values:
            - ssd
  containers:
  - name: nginx
    image: nginx
```

**Explanation:**
- `requiredDuringSchedulingIgnoredDuringExecution` — must match at scheduling time; if node labels change later, pod stays (not evicted)
- `matchExpressions` — the node must have label `disk-type=ssd`
- `operator: In` — the label value must be one of the listed values

### Preferred Node Affinity

"I'd prefer zone us-east-1a (weight 80), and I'd also like m5.large instances (weight 20). But if neither is available, schedule me anywhere."

```yaml
spec:
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 80
        preference:
          matchExpressions:
          - key: zone
            operator: In
            values:
            - us-east-1a
      - weight: 20
        preference:
          matchExpressions:
          - key: instance-type
            operator: In
            values:
            - m5.large
```

**Explanation:**
- `weight` (1-100) — higher weight = stronger preference. Kubernetes scores nodes and picks the highest total
- This pod strongly prefers us-east-1a (80) and weakly prefers m5.large (20)
- If a node matches both, it scores 100. If only zone matches, it scores 80. Kubernetes picks the highest scoring node.

---

## 🤝 Pod Affinity

### What is Pod Affinity?

Pod Affinity says "schedule my pod on the SAME node (or zone) as another pod." It's about co-locating pods together for performance.

**When to use:**
- Your web server needs to be on the same node as its cache (Redis) for low latency
- Two services communicate heavily and benefit from being close together
- You want related pods on the same rack/zone to reduce network hops

### Example

"Put my web pod on the same node where a pod with label `app=cache` is already running."

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: with-pod-affinity
spec:
  affinity:
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - cache
        topologyKey: kubernetes.io/hostname
  containers:
  - name: web
    image: nginx
```

**Explanation:**
- `labelSelector` — find pods with label `app=cache`
- `topologyKey: kubernetes.io/hostname` — "same node" (if you used `topology.kubernetes.io/zone`, it would mean "same zone")
- Result: this web pod will only schedule on a node where a cache pod is already running

---

## ⚡ Pod Anti-Affinity

### What is Pod Anti-Affinity?

The opposite of Pod Affinity — "do NOT put my pod on the same node as another specific pod." It spreads pods apart for high availability.

**When to use:**
- You have 3 replicas of a web app and want each on a different node (so if one node dies, you don't lose all replicas)
- You don't want two database pods on the same node
- Spreading pods across zones for disaster recovery

### Example

"Each replica of my web app must be on a DIFFERENT node."

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
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
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - web
            topologyKey: kubernetes.io/hostname
      containers:
      - name: web
        image: nginx
```

**Explanation:**
- "Don't put me on a node where another pod with `app=web` already exists"
- Since all replicas have label `app=web`, each one avoids the others
- Result: 3 replicas spread across 3 different nodes
- If you only have 2 nodes, the 3rd replica stays pending (because `required` is a hard rule)

---

## 🏷️ Taints and Tolerations

### What are Taints and Tolerations?

**Taints** = applied to NODES — "I repel pods unless they tolerate me"
**Tolerations** = applied to PODS — "I can tolerate that taint, let me in"

Think of it as: taints are like a "no entry" sign on a node. Tolerations are like a special pass that lets specific pods ignore the sign.

**When to use:**
- You have GPU nodes and only want GPU workloads there (taint the node, add toleration to GPU pods)
- You have dedicated nodes for a specific team
- You want to drain a node for maintenance (taint it with NoExecute, existing pods get evicted)

**Three taint effects:**
- `NoSchedule` — new pods won't schedule here (existing pods stay)
- `PreferNoSchedule` — soft version, try to avoid but not guaranteed
- `NoExecute` — new pods won't schedule AND existing pods get evicted

### Commands

```bash
# Add taint to node
kubectl taint nodes node1 key=value:NoSchedule
kubectl taint nodes node1 gpu=true:NoSchedule
kubectl taint nodes node1 dedicated=special:NoExecute

# Remove taint
kubectl taint nodes node1 key:NoSchedule-
```

### Pod with Tolerations

"I can handle the gpu=true taint, and I can survive the dedicated=special taint for 1 hour."

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-toleration
spec:
  tolerations:
  - key: "gpu"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
  - key: "dedicated"
    operator: "Equal"
    value: "special"
    effect: "NoExecute"
    tolerationSeconds: 3600
  containers:
  - name: gpu-app
    image: nvidia/cuda:11.0-base
```

**Explanation:**
- First toleration: "I can schedule on nodes tainted with `gpu=true:NoSchedule`"
- Second toleration: "I can stay on nodes tainted with `dedicated=special:NoExecute`, but only for 3600 seconds (1 hour), then evict me"
- `tolerationSeconds` — only applies to NoExecute; it's a timer for how long the pod stays before getting kicked out

### Taints vs Affinity — What's the difference?

- **Affinity** = pod says "I WANT to go here" (pod chooses node)
- **Taint/Toleration** = node says "ONLY these pods can come here" (node restricts pods)

Use them together: taint the GPU node so random pods don't land there, AND add node affinity to GPU pods so they actively seek GPU nodes.

---

## 📊 Priority and Preemption

### What is Priority and Preemption?

Priority tells Kubernetes "this pod is more important than that pod." If the cluster is full and a high-priority pod needs to run, Kubernetes will EVICT (kill) lower-priority pods to make room. That's preemption.

**When to use:**
- Critical production workloads should never be blocked by batch jobs
- You want payment processing to preempt background report generation
- Dev/test workloads should yield to production if resources are tight

### Example

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
globalDefault: false
description: "High priority class"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: low-priority
value: 100
globalDefault: true
description: "Low priority class"
---
apiVersion: v1
kind: Pod
metadata:
  name: high-priority-pod
spec:
  priorityClassName: high-priority
  containers:
  - name: nginx
    image: nginx
```

**Explanation:**
- `value` — higher number = more important. `1000000` beats `100`
- `globalDefault: true` — if a pod doesn't specify a priority class, it gets this one (low-priority)
- `globalDefault: false` — must be explicitly assigned to a pod
- When the cluster is full and `high-priority-pod` needs to schedule, Kubernetes finds pods with lower priority and evicts them to free up resources

**Real-world scenario:**
- Cluster is full with batch jobs (priority 100)
- A production API pod (priority 1000000) needs to schedule
- Kubernetes evicts enough batch jobs to make room for the API pod
- Batch jobs go back to pending and reschedule when resources free up

---

## Quick Reference

| Concept | Applied To | Purpose |
|---|---|---|
| Node Affinity | Pod → Node | "Put me on THIS type of node" |
| Pod Affinity | Pod → Pod | "Put me NEAR this other pod" |
| Pod Anti-Affinity | Pod → Pod | "Put me AWAY from this other pod" |
| Taints | Node | "Keep pods away from me" |
| Tolerations | Pod | "I can handle that taint" |
| Priority | Pod | "I'm more important, don't evict me" |
| Preemption | Pod | "Evict others if needed to make room for me" |

---

## 🎯 Interview Quick Points

- Advanced scheduling controls **where pods land** instead of leaving it to the default scheduler
- **Node affinity** = pod prefers/requires specific node types (labels like disk-type, zone, instance-type)
- **Pod affinity** = co-locate pods (low latency); **pod anti-affinity** = spread pods apart (high availability)
- Every rule is **required** (hard, pod stays Pending if unmet) or **preferred** (soft, weighted best-effort)
- `IgnoredDuringExecution` means rules apply at scheduling time only — running pods aren't evicted if labels change later
- **Taints** are on nodes ("keep out"); **tolerations** are on pods ("I have a pass")
- Taint effects: **NoSchedule** (block new), **PreferNoSchedule** (soft), **NoExecute** (block new + evict existing)
- A toleration only *permits* a pod onto a tainted node; use node affinity to actively *attract* it there
- **topologyKey** defines the boundary: `kubernetes.io/hostname` = per-node, `topology.kubernetes.io/zone` = per-zone
- **PriorityClass** + **preemption** let critical pods evict lower-priority ones when the cluster is full
- Common combo: taint GPU nodes + add tolerations + node affinity so only GPU workloads run there
- Anti-affinity across replicas is a key pattern for surviving single-node failures

---

## ⏭️ Next: [Module 17: Network Policies](./17-network-policies.md)
