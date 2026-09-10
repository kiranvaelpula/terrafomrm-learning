# Module 09: StatefulSets

## What is a StatefulSet?

A StatefulSet is like a Deployment but for applications that need to remember who they are — databases, message queues, distributed systems like Kafka, Elasticsearch, etc.

**The core problem:** A Deployment creates pods with random names (web-abc123, web-xyz789). If a pod dies and restarts, it gets a new name, new IP, and loses its storage. That's fine for stateless web servers, but TERRIBLE for databases.

**StatefulSet guarantees:**
- Pods get fixed names: `mysql-0`, `mysql-1`, `mysql-2` (predictable, ordered)
- Each pod gets its own dedicated storage that follows it forever
- Pods are created and deleted in order (0, 1, 2... not randomly)
- Each pod gets a stable DNS hostname that doesn't change

---

## 📖 Understanding StatefulSets (Intuition First)

Think about the difference between a fleet of identical taxi cabs and a team of named specialists. With taxis, any cab will do — if one breaks down, you grab another and nobody cares which is which. That's a Deployment: interchangeable, anonymous Pods. But now imagine a hospital surgical team where "Surgeon 0" leads, "Nurse 1" preps, and "Anesthetist 2" has their own equipment. Here identity matters — you can't just swap in a random person and expect the same setup. That's a StatefulSet.

Stateful applications like databases have this exact need for identity. A database replica isn't interchangeable: one node is the primary that accepts writes, others are replicas that follow it, and each holds its *own* copy of the data on its *own* disk. If you shuffled their names and storage around randomly (the way a Deployment does), replication would break and data could be corrupted. StatefulSets give three guarantees that solve this: **stable ordered names** (`mysql-0`, `mysql-1`), **stable per-Pod storage** that reattaches to the same Pod after a restart, and **ordered startup/shutdown**.

The stable-name guarantee is what makes clustering possible. Because `mysql-1` always comes back as `mysql-1` with `data-mysql-1` reattached, the rest of the cluster knows exactly who it's talking to. This is powered by a **headless Service** (`clusterIP: None`), which instead of load-balancing gives each Pod its own DNS record. That's the crucial difference from a normal Service — you often need to reach a *specific* member (the primary), not just "any Pod."

Storage identity comes from **volumeClaimTemplates**. Rather than sharing one volume, the StatefulSet stamps out a dedicated PVC per Pod (`data-mysql-0`, `data-mysql-1`, ...). Each Pod's data lives on its own disk, and that disk follows the Pod's identity for its entire life. A safety feature worth remembering: deleting a StatefulSet does **not** delete these PVCs, so your data is protected from accidental wipes.

Ordering matters too. Pods start in sequence (0, then 1, then 2) and scale down in reverse (highest index first). This mirrors how real clusters work — you bring up the primary before the replicas, and when shrinking, you remove replicas first and never accidentally kill the primary. Understanding these three pillars — identity, dedicated storage, and ordering — is the whole point of StatefulSets.

---

## When to Use StatefulSet vs Deployment

| Use StatefulSet when... | Use Deployment when... |
|---|---|
| Each pod needs its own persistent data (database) | All pods are identical and interchangeable |
| Pods need stable network identity (clustering) | Pod names don't matter |
| Order of startup matters (primary before replicas) | All pods can start in parallel |
| You need to address specific pods by name | Any pod can handle any request |

**Real-world examples:**

| Application | Why StatefulSet? |
|---|---|
| MySQL/PostgreSQL | Each instance has its own data files |
| MongoDB replica set | Need to know who is primary (mongo-0) vs secondary |
| Kafka | Each broker needs its own ID and storage |
| Elasticsearch | Each node stores different shards |
| Redis cluster | Need stable IDs for cluster topology |
| ZooKeeper | Ordered startup, each node has an ID |

---

## StatefulSet vs Deployment — Visual

```
Deployment (stateless):
  [pod-abc] [pod-xyz] [pod-def]    ← random names
      ↓         ↓         ↓
  (no storage) (no storage) (no storage)
  
  If pod-xyz dies → new pod-qrs created (different name, doesn't matter)

StatefulSet (stateful):
  [mysql-0]  [mysql-1]  [mysql-2]   ← fixed names
      ↓          ↓          ↓
  [PVC-0]    [PVC-1]    [PVC-2]     ← each has OWN storage
  
  If mysql-1 dies → new mysql-1 created (same name, same storage reattached)
```

---

## Key Parameters Explained

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres-headless     # Required: headless service for DNS
  replicas: 3                        # Number of pods
  podManagementPolicy: OrderedReady  # How pods start/stop
  updateStrategy:                    # How updates happen
    type: RollingUpdate
    rollingUpdate:
      partition: 0
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
        image: postgres:15
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:              # Creates a unique PVC per pod
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 20Gi
```

### serviceName (Required)

```yaml
serviceName: postgres-headless
```

Points to a Headless Service (`clusterIP: None`). This gives each pod a unique DNS name:
```
postgres-0.postgres-headless.default.svc.cluster.local
postgres-1.postgres-headless.default.svc.cluster.local
postgres-2.postgres-headless.default.svc.cluster.local
```

Without this, pods can't find each other by name — crucial for replication setup.

### podManagementPolicy

```yaml
podManagementPolicy: OrderedReady   # default
# or
podManagementPolicy: Parallel
```

- **OrderedReady** (default) — pods start one by one. `postgres-0` must be Running and Ready before `postgres-1` starts. Good for primary/replica setups where primary must exist first.
- **Parallel** — all pods start at the same time. Use when order doesn't matter (e.g., all peers are equal in a cache cluster).

### updateStrategy

```yaml
updateStrategy:
  type: RollingUpdate
  rollingUpdate:
    partition: 2     # Only update pods with index >= 2
```

- **RollingUpdate** (default) — updates pods one at a time, starting from highest index (2, then 1, then 0)
- **partition** — only pods with ordinal >= partition get updated. Great for canary testing:
  - `partition: 2` → only `postgres-2` gets updated
  - Monitor it, if good → set `partition: 0` to update all

### volumeClaimTemplates

```yaml
volumeClaimTemplates:
- metadata:
    name: data
  spec:
    accessModes: ["ReadWriteOnce"]
    resources:
      requests:
        storage: 20Gi
```

Creates a UNIQUE PVC for each pod automatically:
```
data-postgres-0 → 20Gi disk (pod 0's data)
data-postgres-1 → 20Gi disk (pod 1's data)
data-postgres-2 → 20Gi disk (pod 2's data)
```

If `postgres-1` dies and restarts, it gets `data-postgres-1` reattached — data is preserved.

**Important:** Deleting a StatefulSet does NOT delete the PVCs. Your data is safe. You must manually delete PVCs if you want to remove storage.

---

## Complete Example: PostgreSQL with Replication

```yaml
# Headless Service (required for stable DNS)
apiVersion: v1
kind: Service
metadata:
  name: postgres-headless
spec:
  clusterIP: None            # Headless — no load balancing
  selector:
    app: postgres
  ports:
  - port: 5432

---
# Regular Service (for clients to connect via load-balanced IP)
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  selector:
    app: postgres
    role: primary             # Only route to primary
  ports:
  - port: 5432

---
# StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres-headless
  replicas: 3
  podManagementPolicy: OrderedReady
  updateStrategy:
    type: RollingUpdate
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
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
        livenessProbe:
          exec:
            command: ["pg_isready", "-U", "postgres"]
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command: ["pg_isready", "-U", "postgres"]
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 20Gi
```

**What this creates:**
```
postgres-0 → Primary (handles writes)
    DNS: postgres-0.postgres-headless.default.svc.cluster.local
    Storage: data-postgres-0 (20Gi)

postgres-1 → Replica (reads only)
    DNS: postgres-1.postgres-headless.default.svc.cluster.local
    Storage: data-postgres-1 (20Gi)

postgres-2 → Replica (reads only)
    DNS: postgres-2.postgres-headless.default.svc.cluster.local
    Storage: data-postgres-2 (20Gi)
```

---

## Scaling Behavior

```bash
# Scale up: creates pods in order
kubectl scale statefulset postgres --replicas=5
# Creates: postgres-3, then postgres-4 (in order)

# Scale down: deletes pods in REVERSE order
kubectl scale statefulset postgres --replicas=3
# Deletes: postgres-4 first, then postgres-3
```

**Why reverse order?** In database clusters, higher-numbered pods are usually replicas. You want to remove replicas first, never the primary (postgres-0).

---

## Deletion Behavior

```bash
# Delete StatefulSet but keep pods running
kubectl delete statefulset postgres --cascade=orphan

# Delete StatefulSet and pods (PVCs are preserved!)
kubectl delete statefulset postgres

# Manually delete PVCs (only when you want to lose data)
kubectl delete pvc data-postgres-0 data-postgres-1 data-postgres-2
```

---

## Common Interview Questions

**Q: When would you NOT use StatefulSet?**
A: For stateless apps (web servers, REST APIs, frontend). Use Deployment instead — simpler, scales faster, no ordering overhead.

**Q: What happens if postgres-1 pod dies?**
A: Kubernetes recreates a pod named exactly `postgres-1`, reattaches `data-postgres-1` PVC, and it comes back with all its data.

**Q: Why do you need a Headless Service?**
A: So each pod gets its own DNS record. A regular Service gives one IP that load-balances — useless when you need to talk to a specific pod (like the primary database).

---

## 🎯 Interview Quick Points

- A **StatefulSet** manages stateful apps needing stable identity, storage, and ordering (databases, Kafka, Elasticsearch, ZooKeeper)
- Provides **stable ordered Pod names** (`app-0`, `app-1`) that persist across restarts — unlike Deployment's random names
- Each Pod gets **dedicated persistent storage** via `volumeClaimTemplates` that reattaches on restart
- Requires a **headless Service** (`clusterIP: None`) so each Pod gets its own stable DNS record
- Pods are created **in order** (0→1→2) and deleted in **reverse order** (highest first)
- `podManagementPolicy`: **OrderedReady** (sequential, default) vs **Parallel** (all at once)
- **RollingUpdate** with `partition` enables canary-style staged updates (only Pods ≥ partition update)
- Deleting a StatefulSet **preserves the PVCs** — data is safe; you must delete PVCs manually to lose data
- If `app-1` dies, K8s recreates a Pod named exactly `app-1` and reattaches `data-app-1` with all its data
- Use a **Deployment** instead for stateless, interchangeable workloads (web servers, APIs)
- Scaling down removes replicas first, protecting the primary (usually Pod 0)

---

## Quick Reference

```bash
kubectl get statefulsets
kubectl describe statefulset postgres
kubectl get pods -l app=postgres        # See ordered pods
kubectl get pvc                          # See per-pod storage
kubectl rollout status statefulset postgres
kubectl rollout undo statefulset postgres
```

---

## ⏭️ Next: [Module 10: DaemonSets & Jobs](./10-daemonsets-jobs.md)
