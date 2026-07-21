# Kubernetes Interview Guide - 200+ Questions

## 📚 Complete Interview Preparation

This guide contains 200+ interview questions covering beginner to advanced Kubernetes topics.

---

## 🟢 Beginner Level (50 Questions)

### Architecture & Fundamentals

**Q1: What is Kubernetes?**
A: Kubernetes is an open-source container orchestration platform that automates deployment, scaling, and management of containerized applications.

**Q2: Explain the main components of Kubernetes architecture.**
A: 
- **Control Plane**: API Server, etcd, Scheduler, Controller Manager
- **Worker Nodes**: kubelet, kube-proxy, Container Runtime
- **Add-ons**: CoreDNS, Dashboard, Metrics Server

**Q3: What is a Pod?**
A: A Pod is the smallest deployable unit in Kubernetes. It represents one or more containers that share network and storage resources.

**Example:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
```

**Q4: Can a Pod contain multiple containers?**
A: Yes, a Pod can contain multiple containers that share the same network namespace and can communicate via localhost.

**Example (Multi-container pod):**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-container-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    ports:
    - containerPort: 8080
  - name: sidecar
    image: logger:latest
# Both containers share network - can access each other via localhost
```

**Q5: What is etcd?**
A: etcd is a distributed key-value store that stores all cluster data, including configuration, state, and metadata.

**Q6: What is the role of the API Server?**
A: The API Server is the front-end for the Kubernetes control plane. All communication with the cluster goes through it.

**Q7: What does the Scheduler do?**
A: The Scheduler watches for newly created Pods and assigns them to nodes based on resource requirements and constraints.

**Q8: What is kubelet?**
A: kubelet is an agent that runs on each node, ensuring containers are running in Pods as specified.

**Q9: What is kube-proxy?**
A: kube-proxy maintains network rules on nodes, enabling communication to Pods from inside or outside the cluster.

**Q10: What is the difference between Docker and Kubernetes?**
A: Docker runs containers on a single host, while Kubernetes orchestrates containers across multiple hosts with auto-scaling, self-healing, and load balancing.

### Pods & Deployments

**Q11: How do you create a Pod?**
A: 
```bash
# Imperative
kubectl run nginx --image=nginx

# Declarative
kubectl apply -f pod.yaml
```

**Q12: What is a Deployment?**
A: A Deployment provides declarative updates for Pods and ReplicaSets, managing rollouts and rollbacks.

**Example:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
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
```

**Q13: What's the difference between a Pod and a Deployment?**
A: Pod is a single instance; Deployment manages multiple Pod replicas with updates, scaling, and self-healing.

**Example:**
```bash
# Pod - manual management
kubectl run nginx --image=nginx  # Creates 1 pod, if deleted, gone forever

# Deployment - automatic management
kubectl create deployment nginx --image=nginx --replicas=3
# Creates 3 pods, auto-recreates if deleted, supports rolling updates
```

**Q14: How do you scale a Deployment?**
A: `kubectl scale deployment <name> --replicas=5`

**Q15: What is a ReplicaSet?**
A: A ReplicaSet ensures a specified number of Pod replicas are running. Deployments manage ReplicaSets.

**Q16: What are the Pod lifecycle phases?**
A: Pending → Running → Succeeded/Failed → Terminated

**Q17: What is a liveness probe?**
A: A liveness probe checks if a container is alive. If it fails, kubelet restarts the container.

**Example:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    livenessProbe:
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
      failureThreshold: 3
# If /health returns non-200 3 times, pod restarts
```

**Q18: What is a readiness probe?**
A: A readiness probe checks if a container is ready to serve traffic. If it fails, the Pod is removed from Service endpoints.

**Example:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: readiness-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 5
      failureThreshold: 2
# If /ready fails, pod removed from service load balancing
```

**Q19: What's the difference between liveness and readiness probes?**
A: Liveness = container alive (restart if fails); Readiness = container ready for traffic (remove from endpoints if fails).

**Q20: How do you update a Deployment?**
A: 
```bash
kubectl set image deployment/nginx nginx=nginx:1.22
kubectl edit deployment nginx
kubectl apply -f deployment.yaml
```

### Services & Networking

**Q21: What is a Service?**
A: A Service provides a stable endpoint to access a set of Pods, abstracting away Pod IP changes.

**Q22: What are the types of Services?**
A: 
- **ClusterIP**: Internal access only (default)
- **NodePort**: External access via Node IP:Port
- **LoadBalancer**: Cloud load balancer
- **ExternalName**: DNS CNAME alias

**Example (All types):**
```yaml
# ClusterIP - Internal only
apiVersion: v1
kind: Service
metadata:
  name: internal-service
spec:
  type: ClusterIP  # Default
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 8080

---
# NodePort - External access
apiVersion: v1
kind: Service
metadata:
  name: nodeport-service
spec:
  type: NodePort
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080  # Access via NodeIP:30080

---
# LoadBalancer - Cloud LB
apiVersion: v1
kind: Service
metadata:
  name: lb-service
spec:
  type: LoadBalancer
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 8080
# Gets external IP from cloud provider

---
# ExternalName - DNS alias
apiVersion: v1
kind: Service
metadata:
  name: external-db
spec:
  type: ExternalName
  externalName: db.example.com
# Maps to external DNS
```

**Q23: What is ClusterIP?**
A: ClusterIP is the default Service type, providing a virtual IP for internal cluster access only.

**Q24: What is NodePort?**
A: NodePort exposes the Service on each Node's IP at a static port (30000-32767).

**Q25: What is a LoadBalancer Service?**
A: LoadBalancer provisions a cloud load balancer for external access to the Service.

**Q26: How does Service discovery work?**
A: Services are discoverable via DNS (service-name.namespace.svc.cluster.local) and environment variables.

**Q27: What are Endpoints?**
A: Endpoints are the list of Pod IPs that match a Service selector.

**Q28: What is a headless Service?**
A: A headless Service (clusterIP: None) returns Pod IPs directly instead of a virtual IP, used for StatefulSets.

**Q29: How do Pods communicate with each other?**
A: Pods can communicate directly using Pod IPs or via Services using DNS names.

**Q30: What is kube-dns/CoreDNS?**
A: CoreDNS provides DNS-based service discovery within the cluster.

### Configuration

**Q31: What is a ConfigMap?**
A: ConfigMap stores non-sensitive configuration data as key-value pairs.

**Example:**
```yaml
# Create ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_url: "mysql://db:3306"
  log_level: "info"
  app.properties: |
    server.port=8080
    cache.enabled=true

---
# Use in Pod
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    - name: DATABASE_URL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database_url
    # Or load all keys
    envFrom:
    - configMapRef:
        name: app-config
```

**Q32: What is a Secret?**
A: Secret stores sensitive data (passwords, tokens) in base64-encoded format.

**Example:**
```yaml
# Create Secret
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded "admin"
  password: cGFzc3dvcmQxMjM=  # base64 encoded "password123"

---
# Use in Pod
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    - name: DB_USER
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
```

**Command examples:**
```bash
# Create ConfigMap from literal
kubectl create configmap app-config --from-literal=key=value

# Create Secret from literal
kubectl create secret generic db-secret --from-literal=password=mysecret

# Create from file
kubectl create configmap app-config --from-file=config.txt
kubectl create secret generic db-secret --from-file=password.txt
```

**Q35: How do you use ConfigMaps in Pods?**
A: As environment variables, command-line arguments, or mounted as volumes.

**Q36: Are Secrets encrypted by default?**
A: No, Secrets are base64-encoded by default. Encryption at rest must be configured separately.

**Q37: What's the difference between ConfigMap and Secret?**
A: ConfigMap for non-sensitive config; Secret for sensitive data (base64-encoded).

**Q38: How do you update environment variables from ConfigMap?**
A: Update the ConfigMap, then restart Pods with `kubectl rollout restart deployment <name>`.

**Q39: What happens when you update a ConfigMap mounted as volume?**
A: Files in mounted volumes are automatically updated (~1 minute delay).

**Q40: What's the size limit for ConfigMaps and Secrets?**
A: 1MB

### kubectl Commands

**Q41: How do you view all resources?**
A: `kubectl get all`

**Q42: How do you describe a resource?**
A: `kubectl describe <resource-type> <name>`

**Q43: How do you view Pod logs?**
A: `kubectl logs <pod-name>`

**Q44: How do you execute a command in a Pod?**
A: `kubectl exec <pod-name> -- <command>`

**Q45: How do you get an interactive shell in a Pod?**
A: `kubectl exec -it <pod-name> -- /bin/bash`

**Q46: How do you delete a Pod?**
A: `kubectl delete pod <name>`

**Q47: How do you apply a YAML file?**
A: `kubectl apply -f file.yaml`

**Q48: How do you get resource definitions in YAML?**
A: `kubectl get <resource> <name> -o yaml`

**Q49: How do you watch resources in real-time?**
A: `kubectl get <resource> --watch`

**Q50: How do you check cluster information?**
A: `kubectl cluster-info`

---

## 🟡 Intermediate Level (75 Questions)

### Storage & Volumes

**Q51: What is a Volume?**
A: A Volume is storage that persists beyond Pod lifecycle, shared among containers in a Pod.

**Q52: What are the types of Volumes?**
A: emptyDir, hostPath, PersistentVolume, ConfigMap, Secret, NFS, cloud storage (EBS, Azure Disk, GCE PD)

**Q53: What is a PersistentVolume (PV)?**
A: A PV is cluster-wide storage resource provisioned by admin or dynamically.

**Example:**
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

**Q54: What is a PersistentVolumeClaim (PVC)?**
A: A PVC is a user request for storage, binding to an available PV.

**Example (Complete PV + PVC + Pod):**
```yaml
# 1. PersistentVolume
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mysql-pv
spec:
  capacity:
    storage: 5Gi
  accessModes:
  - ReadWriteOnce
  hostPath:
    path: /data/mysql

---
# 2. PersistentVolumeClaim
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

---
# 3. Use in Pod
apiVersion: v1
kind: Pod
metadata:
  name: mysql
spec:
  containers:
  - name: mysql
    image: mysql:8.0
    volumeMounts:
    - name: mysql-storage
      mountPath: /var/lib/mysql
  volumes:
  - name: mysql-storage
    persistentVolumeClaim:
      claimName: mysql-pvc
```

**Q55: What is a StorageClass?**
A: StorageClass enables dynamic provisioning of PVs with defined parameters.

**Example:**
```yaml
# StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
allowVolumeExpansion: true

---
# PVC using StorageClass (auto-creates PV)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-pvc
spec:
  storageClassName: fast-ssd
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
# PV created automatically!
```

**Q56: What are access modes for PVs?**
A: 
- **ReadWriteOnce (RWO)**: Single node read-write
- **ReadOnlyMany (ROX)**: Multiple nodes read-only
- **ReadWriteMany (RWX)**: Multiple nodes read-write

**Q57: What is dynamic provisioning?**
A: Automatic PV creation when PVC is created, using StorageClass.

**Q58: What is reclaim policy?**
A: Defines what happens to PV after PVC deletion: Retain, Delete, or Recycle.

### StatefulSets & DaemonSets

**Q59: What is a StatefulSet?**
A: StatefulSet manages stateful applications with stable identities, ordered deployment, and persistent storage.

**Example:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  clusterIP: None  # Headless service
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
  serviceName: mysql
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
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
# Creates: mysql-0, mysql-1, mysql-2 with persistent storage
```

**Q62: What is a DaemonSet?**
A: DaemonSet ensures a copy of a Pod runs on all (or selected) nodes.

**Example:**
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      containers:
      - name: node-exporter
        image: prom/node-exporter:latest
        ports:
        - containerPort: 9100
      # Runs on ALL nodes automatically
```

**Q64: What is a Job?**
A: Job creates Pods that run to completion (batch processing).

**Example:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-import
spec:
  completions: 1  # Run once
  backoffLimit: 3  # Retry 3 times if fails
  template:
    spec:
      containers:
      - name: importer
        image: myapp/importer:latest
        command: ["python", "import.py"]
      restartPolicy: Never
```

**Q65: What is a CronJob?**
A: CronJob creates Jobs on a schedule (like cron).

**Example:**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup
spec:
  schedule: "0 2 * * *"  # Every day at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: myapp/backup:latest
            command: ["./backup.sh"]
          restartPolicy: OnFailure
```

### Ingress & Advanced Networking

**Q66: What is an Ingress?**
A: Ingress manages external HTTP(S) access to Services with routing rules.

**Example:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - www.example.com
    secretName: tls-secret
  rules:
  - host: www.example.com
    http:
      paths:
      - path: /app
        pathType: Prefix
        backend:
          service:
            name: app-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
# www.example.com/app → app-service
# www.example.com/api → api-service
```

**Q67: What is an Ingress Controller?**
A: Software that implements Ingress rules (NGINX, Traefik, HAProxy).

**Q68: How does Ingress routing work?**
A: Routes traffic based on hostname and/or URL path to backend Services.

**Q69: How do you enable TLS in Ingress?**
A: Configure TLS certificate in Ingress spec referencing a Secret.

**Q70: What is path-based routing?**
A: Routing to different Services based on URL path (e.g., /api → api-service, /web → web-service).

**Q71: What is host-based routing?**
A: Routing to different Services based on hostname (e.g., api.example.com, web.example.com).

### Namespaces & Resource Management

**Q72: What is a Namespace?**
A: Namespace provides logical isolation for resources within a cluster.

**Q73: What are default namespaces?**
A: default, kube-system, kube-public, kube-node-lease

**Q74: How do you create a Namespace?**
A: `kubectl create namespace <name>`

**Q75: What is a ResourceQuota?**
A: ResourceQuota limits total resource consumption per namespace.

**Q76: What is a LimitRange?**
A: LimitRange sets default and maximum resource limits for containers in a namespace.

**Q77: How do resource requests and limits work?**
A: Requests = minimum guaranteed; Limits = maximum allowed.

**Q78: What happens if a Pod exceeds memory limit?**
A: Pod is killed (OOMKilled - Out Of Memory).

**Q79: What happens if a Pod exceeds CPU limit?**
A: Pod is throttled (CPU limited).

### RBAC & Security

**Q80: What is RBAC?**
A: Role-Based Access Control restricts access based on user roles.

**Q81: What is the difference between Role and ClusterRole?**
A: Role is namespace-scoped; ClusterRole is cluster-wide.

**Q82: What is a RoleBinding?**
A: RoleBinding grants permissions defined in Role to users/groups in a namespace.

**Q83: What is a ClusterRoleBinding?**
A: ClusterRoleBinding grants ClusterRole permissions cluster-wide.

**Q84: What is a ServiceAccount?**
A: ServiceAccount provides identity for Pods to access Kubernetes API.

**Q85: How do you check if a user can perform an action?**
A: `kubectl auth can-i <verb> <resource> --as=<user>`

**Q86: What is Pod Security Policy (PSP)?**
A: PSP controls security-sensitive aspects of Pod specification (deprecated in favor of Pod Security Standards).

**Q87: What is a SecurityContext?**
A: SecurityContext defines privilege and access control for Pods/containers.

**Q88: What is a NetworkPolicy?**
A: NetworkPolicy controls network traffic between Pods.

### Helm

**Q89: What is Helm?**
A: Helm is a package manager for Kubernetes applications.

**Q90: What is a Helm Chart?**
A: A Chart is a package of Kubernetes manifests and configuration.

**Q91: What is a Helm Release?**
A: A Release is an instance of a Chart deployed to a cluster.

**Q92: How do you install a Helm chart?**
A: `helm install <release-name> <chart>`

**Q93: How do you upgrade a Helm release?**
A: `helm upgrade <release-name> <chart>`

**Q94: How do you rollback a Helm release?**
A: `helm rollback <release-name> <revision>`

**Q95: What is values.yaml in Helm?**
A: values.yaml contains default configuration values for a Chart.

### Monitoring & Logging

**Q96: What is Metrics Server?**
A: Metrics Server collects resource metrics (CPU, memory) for pods and nodes.

**Q97: How do you view resource usage?**
A: `kubectl top nodes` and `kubectl top pods`

**Q98: What is Prometheus?**
A: Prometheus is a monitoring and alerting system for metrics.

**Q99: What is Grafana?**
A: Grafana is a visualization platform for metrics dashboards.

**Q100: How do you aggregate logs in Kubernetes?**
A: Using log aggregators like Fluentd, Fluent Bit, or Logstash (EFK/ELK stack).

**Q101: What is Loki?**
A: Loki is a log aggregation system designed to work with Grafana, similar to Prometheus but for logs.

**Q102: How do you export metrics from applications?**
A: Expose /metrics endpoint in Prometheus format, create ServiceMonitor to scrape.

**Q103: What is a ServiceMonitor?**
A: ServiceMonitor is a custom resource used by Prometheus Operator to configure scraping.

**Q104: What is alerting in Prometheus?**
A: Prometheus evaluates alert rules and sends notifications via Alertmanager.

**Q105: How do you access logs from multiple pods?**
A: `kubectl logs -l app=myapp --all-containers=true`

### Autoscaling

**Q106: What is Horizontal Pod Autoscaler (HPA)?**
A: HPA automatically scales the number of Pods based on CPU/memory or custom metrics.

**Example:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Scale when avg CPU > 70%
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

# Command to create:
# kubectl autoscale deployment myapp --cpu-percent=70 --min=2 --max=10
```

**Q108: What is Vertical Pod Autoscaler (VPA)?**
A: VPA automatically adjusts CPU and memory requests/limits for containers.

**Q109: What is Cluster Autoscaler?**
A: Cluster Autoscaler automatically adjusts the number of nodes based on resource requests.

**Q110: What's the difference between HPA and VPA?**
A: HPA scales number of pods; VPA scales pod resources (CPU/memory).

**Q111: Can you use HPA and VPA together?**
A: Not recommended for the same metrics (CPU/memory), but possible for different metrics.

**Q112: What metrics can trigger HPA?**
A: CPU, memory, custom metrics (from Prometheus), external metrics.

**Q113: How does HPA calculate desired replicas?**
A: desiredReplicas = ceil[currentReplicas * (currentMetric / targetMetric)]

**Q114: What is the cooldown period for HPA?**
A: Scale-up: 3 minutes; Scale-down: 5 minutes (configurable).

**Q115: What are HPA stabilization windows?**
A: Time windows that prevent rapid fluctuations in scaling decisions.

### Updates & Rollbacks

**Q116: What is a rolling update?**
A: Gradually replacing old Pods with new ones to achieve zero-downtime deployment.

**Q117: What is maxSurge?**
A: Maximum number of extra Pods created during rolling update.

**Q118: What is maxUnavailable?**
A: Maximum number of Pods that can be unavailable during update.

**Q119: How do you perform a blue-green deployment?**
A: Create new Deployment (green), switch Service selector to green, delete old (blue).

**Q120: What is a canary deployment?**
A: Gradually rolling out changes to a small subset before full deployment.

**Q121: How do you pause a rollout?**
A: `kubectl rollout pause deployment/<name>`

**Q122: How do you resume a paused rollout?**
A: `kubectl rollout resume deployment/<name>`

**Q123: How do you check rollout history?**
A: `kubectl rollout history deployment/<name>`

**Q124: How do you rollback to a specific revision?**
A: `kubectl rollout undo deployment/<name> --to-revision=2`

**Q125: What is the change-cause annotation?**
A: Annotation to track why a rollout occurred (shown in history).

---

## 🔴 Advanced Level (75 Questions)

### Advanced Scheduling

**Q126: What is node affinity?**
A: Rules to constrain Pods to nodes with specific labels (soft or hard constraints).

**Example:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: affinity-pod
spec:
  affinity:
    nodeAffinity:
      # Hard constraint - MUST match
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
      # Soft constraint - PREFER to match
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1
        preference:
          matchExpressions:
          - key: zone
            operator: In
            values:
            - us-east-1a
  containers:
  - name: nginx
    image: nginx
# Must run on node with disktype=ssd
# Prefers zone=us-east-1a
```

**Q130: What are taints and tolerations?**
A: Taints repel Pods from nodes; tolerations allow Pods to schedule on tainted nodes.

**Example:**
```bash
# Add taint to node
kubectl taint nodes node1 key=value:NoSchedule

# Pods without toleration won't schedule on node1
```

```yaml
# Pod with toleration
apiVersion: v1
kind: Pod
metadata:
  name: tolerant-pod
spec:
  tolerations:
  - key: "key"
    operator: "Equal"
    value: "value"
    effect: "NoSchedule"
  containers:
  - name: nginx
    image: nginx
# This pod CAN schedule on node1
```

**Q131: What are the taint effects?**
A: NoSchedule, PreferNoSchedule, NoExecute

**Q132: What is topology spread constraints?**
A: Controls how Pods are spread across failure domains (zones, nodes).

**Q133: What is pod priority and preemption?**
A: Higher priority Pods can evict lower priority Pods when resources are scarce.

**Q134: What is a PriorityClass?**
A: Defines priority level for Pods (higher value = higher priority).

**Q135: What are node selectors?**
A: Simple key-value matching to constrain Pods to specific nodes.

**Q136: How do you mark a node as unschedulable?**
A: `kubectl cordon <node-name>`

**Q137: How do you drain a node?**
A: `kubectl drain <node-name> --ignore-daemonsets`

**Q138: What is descheduler?**
A: Component that evicts Pods based on policies to improve cluster balance.

**Q139: What are init containers?**
A: Containers that run before app containers, used for setup tasks.

**Q140: What are sidecar containers?**
A: Helper containers running alongside main container (logging, proxying, monitoring).

### Network Policies

**Q141: What is a NetworkPolicy?**
A: Rules controlling traffic flow between Pods and network endpoints.

**Example:**
```yaml
# Default deny all traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
spec:
  podSelector: {}  # Applies to all pods
  policyTypes:
  - Ingress
  - Egress

---
# Allow frontend → backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080

---
# Allow backend → database
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-backend-to-db
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
  - to:  # Allow DNS
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

**Q142: What are the default NetworkPolicy behaviors?**
A: By default, all traffic is allowed. Policies are additive.

**Q143: How do you create a default deny-all policy?**
A: Create NetworkPolicy with empty ingress/egress rules and podSelector: {}.

**Q144: What are ingress rules in NetworkPolicy?**
A: Rules controlling incoming traffic to Pods.

**Q145: What are egress rules in NetworkPolicy?**
A: Rules controlling outgoing traffic from Pods.

**Q146: Can NetworkPolicy filter by IP address?**
A: Yes, using ipBlock in ingress/egress rules.

**Q147: What CNI plugins support NetworkPolicy?**
A: Calico, Cilium, Weave Net (not flannel alone).

**Q148: How do you allow DNS traffic?**
A: Create egress rule allowing UDP port 53 to kube-system namespace.

**Q149: How do you debug NetworkPolicy?**
A: Test connectivity with busybox/curl pods, check CNI plugin logs.

**Q150: Can NetworkPolicy work across namespaces?**
A: Yes, using namespaceSelector in rules.

### Custom Resources & Operators

**Q151: What is a Custom Resource Definition (CRD)?**
A: Extension of Kubernetes API to create custom resource types.

**Q152: What is a Custom Resource (CR)?**
A: Instance of a CRD.

**Q153: What is an Operator?**
A: Software that uses CRDs and custom controllers to manage applications.

**Q154: What is the Operator Pattern?**
A: Encoding operational knowledge in software to automate application management.

**Q155: What is a Controller?**
A: Control loop that watches resources and reconciles desired state with actual state.

**Q156: What is the reconciliation loop?**
A: Continuous process: observe → analyze → act to maintain desired state.

**Q157: How do you create a CRD?**
A: Define CRD YAML with schema, apply with kubectl.

**Q158: What is Operator SDK?**
A: Framework for building Operators (Go, Ansible, Helm).

**Q159: What is Kubebuilder?**
A: SDK for building Kubernetes APIs using CRDs.

**Q160: Give examples of popular Operators.**
A: Prometheus Operator, Cert-Manager, ETCD Operator, MySQL Operator.

### Service Mesh

**Q161: What is a Service Mesh?**
A: Infrastructure layer for managing service-to-service communication.

**Q162: What is Istio?**
A: Service mesh providing traffic management, security, and observability.

**Q163: What is a sidecar proxy in service mesh?**
A: Proxy (Envoy) injected alongside application container to handle traffic.

**Q164: What is Envoy?**
A: High-performance proxy used by Istio and other service meshes.

**Q165: What is Linkerd?**
A: Lightweight service mesh focused on simplicity and performance.

**Q166: What is mTLS?**
A: Mutual TLS provides encrypted, authenticated communication between services.

**Q167: What is traffic splitting in service mesh?**
A: Routing percentage of traffic to different versions (canary, A/B testing).

**Q168: What is circuit breaking?**
A: Pattern that stops requests to failing services to prevent cascade failures.

**Q169: What is retry and timeout in service mesh?**
A: Automatic retry of failed requests and timeout for slow requests.

**Q170: What is observability in service mesh?**
A: Distributed tracing, metrics, and logs for service interactions.

### GitOps & CI/CD

**Q171: What is GitOps?**
A: Operational model where Git is single source of truth for infrastructure and applications.

**Q172: What is ArgoCD?**
A: GitOps continuous delivery tool for Kubernetes.

**Q173: What is Flux?**
A: GitOps operator for keeping clusters in sync with configuration sources.

**Q174: What is declarative vs imperative GitOps?**
A: Declarative: describe desired state in Git; Imperative: run commands to change state.

**Q175: What is the App of Apps pattern?**
A: ArgoCD application that manages other applications.

**Q176: What is sync policy in ArgoCD?**
A: Configuration for automatic or manual syncing (prune, self-heal).

**Q177: What is drift detection?**
A: Identifying differences between Git state and cluster state.

**Q178: How do you handle secrets in GitOps?**
A: Use Sealed Secrets, External Secrets Operator, or SOPS.

**Q179: What is progressive delivery?**
A: Gradual rollout with automated analysis and rollback (Flagger, Argo Rollouts).

**Q180: What is Argo Rollouts?**
A: Controller for advanced deployment strategies (blue-green, canary).

### Multi-Cluster & Federation

**Q181: What is KubeFed?**
A: Kubernetes Federation for managing multiple clusters.

**Q182: Why use multiple clusters?**
A: HA, disaster recovery, multi-region, compliance, isolation.

**Q183: What is cluster federation?**
A: Coordinating multiple Kubernetes clusters as single entity.

**Q184: What is Submariner?**
A: Enables direct networking between pods across clusters.

**Q185: How do you manage multiple cluster contexts?**
A: Use kubectl config use-context or kubectx tool.

**Q186: What is cluster API?**
A: Declarative API for cluster lifecycle management.

**Q187: What is Rancher?**
A: Platform for managing multiple Kubernetes clusters.

**Q188: How do you deploy to multiple clusters?**
A: ArgoCD with cluster registration, or KubeFed with FederatedDeployment.

**Q189: What is cross-cluster service discovery?**
A: Services in one cluster discovering services in another (Submariner, Istio multi-cluster).

**Q190: What is multi-cluster ingress?**
A: Global load balancing across clusters (GKE, EKS multi-cluster ingress).

### Security Best Practices

**Q191: What are Pod Security Standards?**
A: Three levels: Privileged, Baseline, Restricted.

**Q192: What is the Restricted security standard?**
A: Heavily restricted profile following hardening best practices.

**Q193: How do you prevent privilege escalation?**
A: Set allowPrivilegeEscalation: false in securityContext.

**Q194: What is AppArmor?**
A: Linux security module for mandatory access control.

**Q195: What is seccomp?**
A: Linux feature to filter syscalls made by containers.

**Q196: How do you scan images for vulnerabilities?**
A: Use Trivy, Clair, Anchore, or Snyk.

**Q197: What is OPA (Open Policy Agent)?**
A: Policy engine for fine-grained access control.

**Q198: What is Gatekeeper?**
A: OPA-based admission controller for enforcing policies.

**Q199: What is Falco?**
A: Runtime security tool detecting anomalous behavior.

**Q200: How do you secure etcd?**
A: Enable TLS, encryption at rest, limit access, regular backups.

### Production & Operations

**Q201: What is a PodDisruptionBudget?**
A: Limits number of pods that can be down simultaneously during voluntary disruptions.

**Example:**
```yaml
# Ensure at least 2 pods always available
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: myapp

---
# Alternative: max 25% can be unavailable
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb-percent
spec:
  maxUnavailable: 25%
  selector:
    matchLabels:
      app: myapp
# During node drain, ensures PDB is respected
```

**Q202: What is graceful shutdown?**
A: Process allowing pods to finish requests before termination (preStop hook, SIGTERM).

**Example:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: graceful-pod
spec:
  terminationGracePeriodSeconds: 60  # Wait 60s before SIGKILL
  containers:
  - name: app
    image: myapp:latest
    lifecycle:
      preStop:
        exec:
          command: ["/bin/sh", "-c", "sleep 15"]  # Drain connections
    ports:
    - containerPort: 8080

# Process:
# 1. Pod receives SIGTERM
# 2. preStop hook executes (sleep 15)
# 3. Container gets SIGTERM
# 4. After 60s, SIGKILL if still running
```

**Q203: What is terminationGracePeriodSeconds?**
A: Time kubernetes waits before forcefully killing a pod (default 30s).

**Q204: How do you perform zero-downtime deployment?**
A: Set maxUnavailable=0, proper readiness probes, PDB, graceful shutdown.

**Q205: What is the preStop hook?**
A: Lifecycle hook executed before container termination.

**Q206: What is resource overcommitment?**
A: Allowing sum of resource requests to exceed node capacity.

**Q207: What are Quality of Service (QoS) classes?**
A: Guaranteed (requests=limits), Burstable (has requests), BestEffort (no requests/limits).

**Q208: Which pods are evicted first during resource pressure?**
A: BestEffort → Burstable → Guaranteed.

**Q209: What is kubelet eviction?**
A: Process of terminating pods when node resources are low.

**Q210: What are eviction signals?**
A: memory.available, nodefs.available, imagefs.available, pid.available.

**Q211: How do you backup Kubernetes?**
A: Backup etcd, use Velero for cluster resources and volumes.

**Q212: What is Velero?**
A: Backup and restore tool for Kubernetes clusters.

**Q213: What is disaster recovery in Kubernetes?**
A: Plan for restoring cluster and applications after failure.

**Q214: How do you upgrade a Kubernetes cluster?**
A: Upgrade control plane first, then worker nodes (rolling upgrade).

**Q215: What is the upgrade strategy for worker nodes?**
A: Drain → Upgrade → Uncordon (one node at a time).

**Q216: What are immutable infrastructure principles?**
A: Never modify, always replace with new version.

**Q217: How do you handle database migrations?**
A: Use init containers or Jobs before application deployment.

**Q218: What is health check endpoint?**
A: HTTP endpoint (/health) returning 200 if application is healthy.

**Q219: What metrics should you monitor?**
A: Error rate, latency, throughput, saturation (RED/USE methods).

**Q220: What is chaos engineering in Kubernetes?**
A: Deliberately introducing failures to test resilience (Chaos Mesh, Litmus).

---

## 📝 Scenario-Based Questions

### Troubleshooting Scenarios

### Troubleshooting Scenarios

**Scenario 1: Pod Not Starting**
Q: A Pod is stuck in Pending state. How do you troubleshoot?
A: 
1. `kubectl describe pod <name>` - Check events
2. Look for: insufficient resources, volume not available, image pull errors
3. Check node capacity: `kubectl describe node`
4. Check PVC status if using volumes
5. Check resource quotas: `kubectl describe quota -n <namespace>`

**Scenario 2: Service Not Accessible**
Q: Can't access a Service from another Pod. How do you debug?
A:
1. Check Service exists: `kubectl get svc`
2. Verify selector matches Pods: `kubectl describe svc`
3. Check Endpoints: `kubectl get endpoints`
4. Test DNS: `kubectl run test --rm -it --image=busybox -- nslookup <service-name>`
5. Check Pod status and readiness probes
6. Verify NetworkPolicy isn't blocking traffic

**Scenario 3: Deployment Rolling Update Failed**
Q: Deployment update is stuck. What do you do?
A:
1. Check rollout status: `kubectl rollout status deployment/<name>`
2. Describe deployment: `kubectl describe deployment <name>`
3. Check pod events and logs
4. Verify new image exists and is pullable
5. Check readiness probes
6. Rollback: `kubectl rollout undo deployment/<name>`
7. Fix issue and retry

**Scenario 4: High Memory Usage**
Q: Pods are being OOMKilled. How do you resolve?
A:
1. Check pod events: `kubectl describe pod`
2. Review resource limits: too low?
3. Check application for memory leaks
4. Monitor with `kubectl top pod`
5. Increase memory limits if justified
6. Consider VPA for recommendations

**Scenario 5: CrashLoopBackOff**
Q: Pod keeps crashing. How do you debug?
A:
1. Check logs: `kubectl logs <pod> --previous`
2. Describe pod for events
3. Check application configuration
4. Verify environment variables and secrets
5. Check liveness probe settings (might be too aggressive)
6. Test container locally

**Scenario 6: ImagePullBackOff**
Q: Pod can't pull image. What do you check?
A:
1. Verify image name and tag
2. Check image exists in registry
3. Verify imagePullSecrets if private registry
4. Check network connectivity to registry
5. Verify registry authentication
6. Check node can resolve registry DNS

**Scenario 7: Node NotReady**
Q: Node shows NotReady status. How do you troubleshoot?
A:
1. `kubectl describe node <name>`
2. Check kubelet status: `systemctl status kubelet`
3. Check kubelet logs: `journalctl -u kubelet`
4. Verify network connectivity
5. Check disk space and memory
6. Verify CNI plugin is running

**Scenario 8: DNS Not Working**
Q: Pods can't resolve service names. What's wrong?
A:
1. Check CoreDNS pods: `kubectl get pods -n kube-system -l k8s-app=kube-dns`
2. Check CoreDNS logs
3. Test DNS: `nslookup kubernetes.default`
4. Verify kube-dns service exists
5. Check NetworkPolicy allowing DNS (port 53)
6. Restart CoreDNS pods if needed

**Scenario 9: Storage Issues**
Q: PVC is stuck in Pending. How do you fix?
A:
1. `kubectl describe pvc <name>`
2. Check if PV available matching PVC requirements
3. Verify StorageClass exists
4. Check provisioner logs (if dynamic)
5. Verify access modes are supported
6. Check volume size is available

**Scenario 10: Ingress Not Working**
Q: Can't access application via Ingress. How do you debug?
A:
1. Check Ingress resource: `kubectl describe ingress`
2. Verify Ingress controller is running
3. Check backend Service and Pods are ready
4. Test Service directly: `kubectl port-forward`
5. Check DNS records
6. Verify TLS certificate if using HTTPS
7. Check Ingress controller logs

**Scenario 11: Certificate Issues**
Q: TLS certificate not being issued. What do you check?
A:
1. Check cert-manager pods: `kubectl get pods -n cert-manager`
2. Describe Certificate resource
3. Check CertificateRequest and Order
4. Verify ClusterIssuer configuration
5. Check cert-manager logs
6. Verify DNS or HTTP challenge can be completed

**Scenario 12: HPA Not Scaling**
Q: HPA not scaling despite high CPU. Why?
A:
1. Check HPA status: `kubectl describe hpa`
2. Verify metrics-server is running
3. Check pods have resource requests defined
4. Verify metrics are available: `kubectl top pods`
5. Check HPA target utilization
6. Review HPA events for errors

**Scenario 13: StatefulSet Pod Stuck**
Q: StatefulSet pod won't start after node failure. What to do?
A:
1. Check pod status and events
2. Verify PVC is available
3. If node is gone, force delete pod: `kubectl delete pod <name> --force --grace-period=0`
4. Check PV access mode (RWO requires node reattachment)
5. Verify StatefulSet pod management policy

**Scenario 14: Network Policy Blocking Traffic**
Q: After applying NetworkPolicy, services stopped working. How to fix?
A:
1. List NetworkPolicies: `kubectl get netpol`
2. Review policy rules
3. Check if DNS is allowed (port 53 UDP)
4. Verify egress rules for external traffic
5. Test with temporary allow-all policy
6. Fix specific rules incrementally

**Scenario 15: Performance Degradation**
Q: Application performance suddenly degraded. How do you investigate?
A:
1. Check resource usage: `kubectl top pods/nodes`
2. Review pod count and HPA behavior
3. Check for noisy neighbors
4. Review application logs
5. Check database/external service latency
6. Monitor network latency
7. Check for recent changes/deployments

**Scenario 16: Cluster Upgrade Failed**
Q: Control plane upgrade failed. What's your recovery plan?
A:
1. Check what failed: API server, etcd, controller manager?
2. Review upgrade logs
3. Restore etcd from backup if needed
4. Verify all control plane components are compatible versions
5. Check certificates haven't expired
6. Roll back to previous version if necessary

**Scenario 17: RBAC Permission Denied**
Q: User can't perform action. How do you grant access?
A:
1. Check what permission is needed
2. Verify user/service account identity
3. Create appropriate Role/ClusterRole
4. Create RoleBinding/ClusterRoleBinding
5. Test: `kubectl auth can-i <verb> <resource> --as=<user>`
6. Review existing bindings for conflicts

**Scenario 18: Application Can't Connect to Database**
Q: Application pods can't connect to database. Debug steps?
A:
1. Verify database pod is running
2. Check database service endpoints
3. Test connectivity: exec into app pod, curl/nc database
4. Verify connection string and credentials
5. Check NetworkPolicy rules
6. Verify database is accepting connections
7. Check application logs for specific error

**Scenario 19: Secrets Not Being Updated**
Q: Updated Secret but application still uses old value. Why?
A:
1. If environment variables: must restart pods
2. If mounted volume: check if auto-update enabled
3. Restart deployment: `kubectl rollout restart deployment`
4. Verify Secret was actually updated
5. Check if application caches values

**Scenario 20: Resource Quota Exceeded**
Q: Can't create new pods due to quota. What do you do?
A:
1. Check quota: `kubectl describe quota -n <namespace>`
2. Check current usage
3. Delete unused resources
4. Scale down non-critical deployments
5. Request quota increase if justified
6. Move workloads to different namespace

---

## 🎯 Interview Tips

### Preparation Strategy
1. Understand fundamentals deeply
2. Practice kubectl commands daily
3. Set up local cluster for hands-on practice
4. Build real projects
5. Review common scenarios
6. Study official documentation

### During Interview
1. Think out loud
2. Ask clarifying questions
3. Start with simple solutions
4. Mention alternatives
5. Discuss trade-offs
6. Show troubleshooting skills

### Common Topics to Master
- Pod lifecycle and scheduling
- Services and networking
- Storage and StatefulSets
- Deployments and updates
- RBAC and security
- Troubleshooting techniques
- Production best practices

---

## 📚 Study Resources

- Official Kubernetes documentation
- kubectl cheat sheet
- Kubernetes patterns book
- CKA/CKAD exam curriculum
- Hands-on labs and projects
- Community forums and blogs

---

## ⏭️ Next Steps

1. Review answers and understand concepts
2. Practice labs for each topic
3. Build sample projects
4. Join study groups
5. Take practice exams
6. Get certified (CKA/CKAD/CKS)

---

**Good luck with your interviews! 🚀**

[Back to Main Guide](./README.md)
