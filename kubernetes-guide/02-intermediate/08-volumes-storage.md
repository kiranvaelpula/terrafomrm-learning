# Module 08: Volumes & Storage

## 📚 What You'll Learn
- Volume types and use cases
- PersistentVolumes (PV) and PersistentVolumeClaims (PVC)
- StorageClasses and dynamic provisioning
- Volume modes and access patterns
- Best practices for storage

---

## 🎯 Why Volumes?

**Problem:** Container filesystem is ephemeral — when a container restarts or a pod dies, all data inside it is lost. Your database data, uploaded files, logs — gone.

**Solution:** Volumes provide storage that lives outside the container lifecycle. Data persists across container restarts and (with PVs) across pod rescheduling.

---

## 📖 Understanding Volumes & Storage (Intuition First)

Containers were designed to be disposable — you can throw one away and start a fresh copy at any moment. That's wonderful for stateless apps but a disaster for anything that needs to *remember* something, like a database. When a container dies, its internal filesystem vanishes with it, like a whiteboard wiped clean. Volumes exist to give containers a way to write data somewhere that survives the container's death.

The key insight behind Kubernetes storage is a clean **separation of "what I need" from "where it comes from."** Imagine renting storage space: you (the developer) just say "I need a 10GB fast locker" — that request is a **PersistentVolumeClaim (PVC)**. The actual locker in the warehouse is a **PersistentVolume (PV)**, and the *catalog* of locker types available (fast SSD, cheap HDD) is a **StorageClass**. You don't care which physical disk you get, only that your claim is satisfied. This decoupling means developers never hard-code cloud-specific disk details, and the same manifests work across AWS, Azure, or on-prem.

In the old days, an admin manually pre-created PVs and developers claimed them (**static provisioning**). Modern clusters use **dynamic provisioning**: you create a PVC referencing a StorageClass, and Kubernetes automatically calls the cloud to create a real disk and a matching PV on the spot. This is why production almost always uses StorageClasses — no human has to provision storage by hand.

Not all storage needs are the same, which is why there are different **volume types** and **access modes**. An `emptyDir` is scratch space that lives only as long as the Pod — great for temporary caches or sharing files between containers in the same Pod. A PVC-backed volume survives Pod deletion — essential for databases. Access modes describe sharing: `ReadWriteOnce` (one node, typical for databases), `ReadOnlyMany`, and `ReadWriteMany` (shared writable storage across many Pods, like NFS).

Finally, the **reclaim policy** decides what happens to the underlying disk when you delete a claim: `Retain` keeps the data for safety (manual cleanup), while `Delete` tears down the disk automatically. Understanding this trio — PVC (request), PV (actual storage), StorageClass (the provisioner) — plus access modes and reclaim policies, is the mental model that makes all Kubernetes storage click.

---

## �️ Understanding PV, PVC, and StorageClass

### The Analogy

Think of it like renting storage:
- **PersistentVolume (PV)** = the actual storage space (a physical locker in a warehouse)
- **PersistentVolumeClaim (PVC)** = your request/rental contract ("I need a 10GB locker")
- **StorageClass** = the type of locker available (SSD fast locker, HDD cheap locker)

### Why This Separation?

**Without PV/PVC:** Your pod definition has storage details hardcoded (disk type, AWS EBS ID, etc.). If you move to a different cloud, you rewrite everything. Developers need to know infrastructure details.

**With PV/PVC:** Developers just say "I need 10GB of fast storage" (PVC). The admin or cloud provider handles where it actually comes from (PV). Clean separation of concerns.

### How They Connect

```
Developer creates:     PVC ("I need 10GB, fast storage")
                         ↓ binds to
Admin/Cloud provides:  PV  ("Here's a 10GB SSD disk")
                         ↓ used by
Pod mounts:            Volume from the PVC
```

### When to Use What

| Scenario | What to Use |
|---|---|
| Temporary cache, shared between containers in same pod | emptyDir |
| Database that must keep data after pod restart | PVC + PV |
| Logs that must survive pod deletion | PVC + PV |
| Static config files | ConfigMap (not a volume in this sense) |
| Quick dev/test, don't care about persistence | emptyDir |
| Production database (MySQL, PostgreSQL) | PVC with StorageClass (dynamic provisioning) |
| Shared file storage across multiple pods | PVC with ReadWriteMany access mode |

### The Lifecycle

```
1. StorageClass exists (admin creates once, or cloud provides defaults)
2. Developer creates PVC: "Give me 10Gi of fast-ssd class"
3. StorageClass automatically provisions a PV (dynamic provisioning)
4. PVC binds to PV (status: Bound)
5. Pod mounts the PVC
6. Pod writes data → data stored on PV
7. Pod dies → PV still has data
8. New pod mounts same PVC → data is still there ✅
```

### Static vs Dynamic Provisioning

**Static** (old way): Admin manually creates PVs ahead of time. Developers claim them.
```
Admin creates: PV-1 (50Gi), PV-2 (100Gi), PV-3 (20Gi)
Developer creates PVC: "I need 20Gi" → binds to PV-3
```

**Dynamic** (modern way): Developer creates PVC with a StorageClass. Kubernetes automatically creates the PV on-demand.
```
Developer creates PVC with storageClassName: fast-ssd
→ Cloud automatically creates an EBS/disk
→ PV is created automatically
→ PVC binds to it
```

Always use dynamic provisioning in production. No manual PV management needed.

---

## 📦 Volume Types

### 1. emptyDir - Temporary Storage

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: emptydir-pod
spec:
  containers:
  - name: writer
    image: busybox
    command: ['sh', '-c', 'echo "Hello" > /data/hello.txt && sleep 3600']
    volumeMounts:
    - name: shared-data
      mountPath: /data
  - name: reader
    image: busybox
    command: ['sh', '-c', 'cat /data/hello.txt && sleep 3600']
    volumeMounts:
    - name: shared-data
      mountPath: /data
  volumes:
  - name: shared-data
    emptyDir: {}
```

**Use cases:** Temporary scratch space, sharing between containers

### 2. hostPath - Node Storage

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hostpath-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: host-volume
      mountPath: /usr/share/nginx/html
  volumes:
  - name: host-volume
    hostPath:
      path: /data/website
      type: DirectoryOrCreate
```

**⚠️ Warning:** Not portable, ties Pod to specific node

### 3. PersistentVolume (PV) - Cluster Storage

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-example
spec:
  capacity:
    storage: 10Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/data
```

### 4. PersistentVolumeClaim (PVC) - Storage Request

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-example
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: manual
```

---

## 🎪 Lab 1: PV and PVC

### Step 1: Create PersistentVolume

```yaml
# pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: task-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/data
```

```bash
kubectl apply -f pv.yaml
kubectl get pv
```

### Step 2: Create PersistentVolumeClaim

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: task-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 500Mi
  storageClassName: manual
```

```bash
kubectl apply -f pvc.yaml
kubectl get pvc
# Should show STATUS: Bound
```

### Step 3: Use PVC in Pod

```yaml
# pod-with-pvc.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pvc-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: storage
      mountPath: /usr/share/nginx/html
  volumes:
  - name: storage
    persistentVolumeClaim:
      claimName: task-pvc
```

```bash
kubectl apply -f pod-with-pvc.yaml

# Write data
kubectl exec pvc-pod -- sh -c 'echo "Hello PV!" > /usr/share/nginx/html/index.html'

# Delete and recreate pod
kubectl delete pod pvc-pod
kubectl apply -f pod-with-pvc.yaml

# Data persists
kubectl exec pvc-pod -- cat /usr/share/nginx/html/index.html
```

---

## 🔧 StorageClass - Dynamic Provisioning

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-storage
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  fsType: ext4
  encrypted: "true"
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

### Dynamic PVC

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: fast-storage
  resources:
    requests:
      storage: 10Gi
```

**Workflow:**
```
1. Create PVC with storageClassName
2. StorageClass provisions PV automatically
3. PVC binds to new PV
4. Pod uses PVC
```

---

## 📊 Access Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **ReadWriteOnce (RWO)** | Single node read-write | Databases |
| **ReadOnlyMany (ROX)** | Multiple nodes read-only | Static content |
| **ReadWriteMany (RWX)** | Multiple nodes read-write | Shared storage |
| **ReadWriteOncePod** | Single pod read-write | Exclusive access |

```yaml
# Example: ReadWriteMany
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: shared-storage
spec:
  accessModes:
  - ReadWriteMany  # Multiple pods can write
  resources:
    requests:
      storage: 100Gi
  storageClassName: nfs-storage
```

---

## 🎪 Lab 2: Complete Storage Setup

```yaml
# storage-setup.yaml

# StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer

---
# PersistentVolume
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mysql-pv
spec:
  capacity:
    storage: 5Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: standard
  hostPath:
    path: /mnt/mysql-data

---
# PersistentVolumeClaim
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: standard

---
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: rootpassword
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: mysql-storage
          mountPath: /var/lib/mysql
      volumes:
      - name: mysql-storage
        persistentVolumeClaim:
          claimName: mysql-pvc
```

---

## 🔄 Volume Reclaim Policies

```yaml
persistentVolumeReclaimPolicy: Retain  # Manual cleanup
persistentVolumeReclaimPolicy: Delete  # Auto-delete
persistentVolumeReclaimPolicy: Recycle # Deprecated
```

**Behavior:**
- **Retain**: PV remains after PVC deletion (manual cleanup)
- **Delete**: PV and underlying storage deleted with PVC
- **Recycle**: Basic scrub (rm -rf /volume/*) - deprecated

---

## ☁️ Cloud Storage Integration

### AWS EBS

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-sc
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
allowVolumeExpansion: true
```

### Azure Disk

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: azure-disk
provisioner: disk.csi.azure.com
parameters:
  skuName: Premium_LRS
  kind: Managed
```

### GCE Persistent Disk

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gce-pd
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
  replication-type: regional-pd
```

---

## 💡 Best Practices

### 1. Use StorageClasses for Dynamic Provisioning

```yaml
# ✅ Good
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data
spec:
  storageClassName: fast-ssd
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 10Gi
```

### 2. Set Resource Limits

```yaml
resources:
  requests:
    storage: 10Gi
  limits:
    storage: 20Gi
```

### 3. Enable Volume Expansion

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: expandable
provisioner: kubernetes.io/aws-ebs
allowVolumeExpansion: true
```

### 4. Use Appropriate Access Modes

```yaml
# Database (single writer)
accessModes: [ReadWriteOnce]

# Static content (many readers)
accessModes: [ReadOnlyMany]

# Shared files (many writers)
accessModes: [ReadWriteMany]
```

---

## 📝 Quick Reference

```bash
# PersistentVolumes
kubectl get pv
kubectl describe pv <name>
kubectl delete pv <name>

# PersistentVolumeClaims
kubectl get pvc
kubectl describe pvc <name>
kubectl delete pvc <name>

# StorageClasses
kubectl get sc
kubectl describe sc <name>

# Volume expansion
kubectl edit pvc <name>  # Update storage size
kubectl get pvc <name> --watch  # Watch resize
```

---

## 🎯 Interview Quick Points

- Container filesystems are **ephemeral** — data is lost on restart; **volumes** provide persistence beyond the container lifecycle
- **PVC** = a developer's storage request; **PV** = the actual storage; **StorageClass** = the provisioner/catalog of storage types
- This separation lets developers request storage without knowing cloud-specific details (portability + separation of concerns)
- **Static provisioning** = admin pre-creates PVs; **dynamic provisioning** = StorageClass auto-creates PVs on demand (preferred in production)
- **emptyDir** = temporary, dies with the Pod (scratch/shared space); **hostPath** = ties a Pod to a node (avoid in production)
- Access modes: **ReadWriteOnce (RWO)** for databases, **ReadOnlyMany (ROX)**, **ReadWriteMany (RWX)** for shared writable storage
- Reclaim policies: **Retain** (keep data, manual cleanup), **Delete** (auto-remove disk); **Recycle** is deprecated
- A PVC's status becomes **Bound** once matched to a PV
- **volumeBindingMode: WaitForFirstConsumer** delays PV creation until a Pod is scheduled (ensures correct zone placement)
- **allowVolumeExpansion: true** enables growing a PVC later without recreating it
- Cloud provisioners use **CSI drivers** (e.g., ebs.csi.aws.com, disk.csi.azure.com, pd.csi.storage.gke.io)

---

## ⏭️ Next: [Module 09: StatefulSets](./09-statefulsets.md)
