# Module 08: Volumes & Storage

## 📚 What You'll Learn
- Volume types and use cases
- PersistentVolumes (PV) and PersistentVolumeClaims (PVC)
- StorageClasses and dynamic provisioning
- Volume modes and access patterns
- Best practices for storage

---

## 🎯 Why Volumes?

**Problem:** Container filesystem is ephemeral - data lost when container restarts.

**Solution:** Volumes provide persistent storage that survives container restarts.

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

## ⏭️ Next: [Module 09: StatefulSets](./09-statefulsets.md)
