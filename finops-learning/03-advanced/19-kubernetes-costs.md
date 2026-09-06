# Kubernetes Cost Management

## Overview

Kubernetes makes cost attribution hard — many teams share one cluster, and pods come and go. This chapter covers seeing and controlling K8s costs.

---

## 📖 Understanding Kubernetes Cost Management (Intuition First)

Kubernetes cost management has a unique challenge: the cloud bill can't see inside the cluster. Imagine renting a large warehouse and subletting shelves to a dozen tenants. Your landlord (AWS) bills you for the whole warehouse — the nodes — but has no idea which tenant (which team's pods) used which shelf. From the outside it's just "one big EC2 bill." The entire discipline of Kubernetes FinOps is about building the internal accounting that AWS can't, so you can fairly attribute that shared warehouse cost back to its tenants.

The reason this is hard is the **layer of abstraction** Kubernetes adds. You pay for nodes (VMs), but you deploy pods, and many pods share a node. A single m5.2xlarge node might host thirty pods from five different teams. The cloud provider sees one instance; you need tooling (like Kubecost or OpenCost) that watches pod-level resource usage and divides the node's cost proportionally. Without that, Kubernetes cost is a black box charged to whoever happens to own the cluster.

The dominant source of waste in Kubernetes is the **gap between requests and usage**. When you deploy a pod you specify resource *requests* (how much CPU/memory to reserve). Kubernetes then packs nodes based on those requests, not actual usage. Engineers, playing it safe, request far more than they use — so nodes fill up with reservations while actually running at 20% utilization. You're paying for reserved-but-idle capacity. Right-sizing requests to match real usage is the single biggest Kubernetes cost lever.

The flip side is **node efficiency** — the packing problem. Even with good requests, if the cluster autoscaler spins up a big node to run one small pod, you waste the rest. Techniques like the cluster autoscaler, bin-packing schedulers, and tools like Karpenter that pick right-sized nodes for pending pods keep nodes densely and efficiently filled. And because much Kubernetes work is fault-tolerant, running worker nodes on **Spot instances** captures huge savings for interruptible workloads.

The mental model to carry: Kubernetes cost management is a **two-level game**. Level one is *inside* the cluster — right-sizing pod requests, setting namespace quotas, and attributing cost to teams. Level two is the *node layer* — packing pods efficiently, autoscaling nodes to match demand, and using Spot where safe. Optimize only one level and you leave money on the table; the wins come from squeezing both the pods onto nodes and the nodes onto the right, cheapest capacity.

---

## Why Kubernetes Cost Is Hard

```
The cloud bill shows: "EC2 instances: $50,000"
But the cluster runs 20 teams' workloads on shared nodes.

WHO owes what? The bill doesn't know about namespaces, pods, or teams.
You need to allocate SHARED infrastructure cost to the workloads using it.
```

## The Allocation Problem

```
Node (8 CPU, 32GB) — $200/month
├── Team A pods: using 4 CPU, 16GB  → owes 50%  → $100
├── Team B pods: using 2 CPU,  8GB  → owes 25%  → $50
└── Idle/unused:        2 CPU,  8GB  → 25% waste → $50 (whose?)

Allocation = distribute node cost by each workload's resource usage.
Plus the tricky part: who pays for IDLE capacity?
```

## Tools for K8s Cost Visibility

| Tool | Purpose |
|------|---------|
| **OpenCost** | CNCF open-source K8s cost monitoring (the standard) |
| **Kubecost** | Commercial (built on OpenCost), richer features |
| **AWS Split Cost Allocation** | Native EKS cost allocation to pods |

```
These map cost to: namespace, deployment, label, team, pod —
so you can do showback/chargeback for a shared cluster.
```

## Key Cost Optimizations

### 1. Right-Size Requests & Limits

```yaml
# Over-requesting wastes money — the scheduler reserves what you request
resources:
  requests:
    cpu: "250m"      # Right-sized based on ACTUAL usage
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
# Requesting 2 CPU "just in case" when you use 0.2 = 90% waste
```

### 2. Autoscaling (three levels)

```
HPA (Horizontal Pod Autoscaler): scale pods with load
VPA (Vertical Pod Autoscaler):   right-size requests automatically
Cluster Autoscaler / Karpenter:  add/remove NODES with demand

Karpenter (AWS) is especially good — provisions the cheapest
node that fits pending pods, and consolidates underused nodes.
```

### 3. Spot Instances for Nodes

```
Run fault-tolerant workloads on Spot node groups (up to 90% cheaper).
Use taints/tolerations to place only interruptible workloads there.
Keep critical/stateful workloads on on-demand.
```

### 4. Bin-Packing & Consolidation

```
Empty space on nodes = wasted money.
Karpenter/Cluster Autoscaler consolidate pods onto fewer nodes
and terminate the empties. Higher node utilization = lower cost.
```

### 5. Namespace Resource Quotas

```yaml
# Cap what a team's namespace can consume (cost guardrail)
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-a-quota
  namespace: team-a
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
```

## Showback Example (OpenCost concept)

```
Monthly cluster cost allocated by namespace:
  team-a:     $4,200  (42%)
  team-b:     $3,100  (31%)
  platform:   $1,800  (18%)
  idle/waste:   $900  ( 9%)  ← target for optimization
  ──────────────────────────
  Total:     $10,000
```

## Common Pitfalls

- **Over-requesting resources** — the #1 K8s waste (reserves capacity you don't use)
- **Ignoring idle cost** — empty node space nobody's accountable for
- **No autoscaling** — running peak capacity 24/7
- **Everything on-demand** — missing Spot savings for stateless workloads
- **No allocation** — can't do showback/chargeback on a shared cluster

---

## 🎯 Interview Quick Points

- The core challenge: the **cloud bill sees nodes, not pods** — you must build internal cost attribution
- You pay for **nodes (VMs)** but deploy **pods**; many pods share a node, hiding per-team cost
- Tools like **Kubecost / OpenCost** watch pod-level usage and split node cost proportionally
- The #1 waste is the **request-vs-usage gap** — engineers over-request, nodes fill with idle reservations
- **Right-sizing pod requests/limits** to actual usage is the single biggest Kubernetes cost lever
- Use **namespace resource quotas** to cap and allocate cost per team
- **Node efficiency (bin-packing)** matters — a big node running one small pod wastes the rest
- **Cluster Autoscaler** and **Karpenter** scale/right-size nodes to match pending pods
- Run fault-tolerant workloads on **Spot node groups** for large savings
- Use **HPA (Horizontal Pod Autoscaler)** to scale pods with demand, not fixed replicas
- Kubernetes cost is a **two-level game**: optimize pods-onto-nodes *and* nodes-onto-cheapest-capacity
- Attribute cost with **labels/namespaces** the way tags work for raw cloud resources
