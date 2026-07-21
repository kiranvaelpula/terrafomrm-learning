# Module 09: StatefulSets

## 📚 What You'll Learn
- StatefulSets vs Deployments
- Stable network identities
- Ordered deployment and scaling
- Persistent storage per pod
- Deploying stateful applications

---

## 🎯 What are StatefulSets?

**StatefulSets** manage stateful applications that require:
- Stable, unique network identifiers
- Stable, persistent storage
- Ordered, graceful deployment and scaling
- Ordered, automated rolling updates

### StatefulSet vs Deployment

| Feature | Deployment | StatefulSet |
|---------|------------|-------------|
| Pod names | Random | Predictable (pod-0, pod-1) |
| Network identity | Random IP | Stable hostname |
| Storage | Shared or none | Dedicated PVC per pod |
| Scaling | Parallel | Sequential |
| Use case | Stateless apps | Databases, clusters |

---

## 📝 Basic StatefulSet

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-headless
spec:
  clusterIP: None  # Headless service
  selector:
    app: nginx
  ports:
  - port: 80
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: nginx-headless
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
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
```

**Pod Names:**
```
web-0.nginx-headless.default.svc.cluster.local
web-1.nginx-headless.default.svc.cluster.local
web-2.nginx-headless.default.svc.cluster.local
```

---

## 🎪 Lab 1: Deploy MySQL with StatefulSet

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-headless
spec:
  clusterIP: None
  selector:
    app: mysql
  ports:
  - port: 3306
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql-headless
  replicas: 3
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
          value: password
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
```

```bash
kubectl apply -f mysql-statefulset.yaml

# Watch ordered creation
kubectl get pods -w

# Each pod gets own PVC
kubectl get pvc

# Access specific pod
kubectl exec -it mysql-0 -- mysql -p
```

---

## 🔄 Scaling and Updates

### Ordered Scaling
```bash
# Scale up (creates mysql-3, mysql-4)
kubectl scale statefulset mysql --replicas=5

# Scale down (deletes mysql-4, mysql-3)
kubectl scale statefulset mysql --replicas=3
```

### Rolling Updates
```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 2  # Only update pods >= partition
```

---

## 💡 Best Practices

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: production-db
spec:
  serviceName: db-headless
  replicas: 3
  podManagementPolicy: OrderedReady  # or Parallel
  updateStrategy:
    type: RollingUpdate
  template:
    spec:
      containers:
      - name: postgres
        image: postgres:14
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command: ["pg_isready"]
          initialDelaySeconds: 30
        readinessProbe:
          exec:
            command: ["pg_isready"]
          initialDelaySeconds: 5
```

---

## ⏭️ Next: [Module 10: DaemonSets & Jobs](./10-daemonsets-jobs.md)
