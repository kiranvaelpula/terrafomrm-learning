# Module 10: DaemonSets & Jobs

## DaemonSets

### What is a DaemonSet?

A DaemonSet ensures that ONE copy of a pod runs on EVERY node (or selected nodes) in your cluster. When a new node is added, the pod is automatically scheduled on it. When a node is removed, the pod is garbage collected.

**Analogy:** Think of it like installing antivirus on every computer in an office. Every machine gets one copy, new machines get it automatically, and you don't decide which specific machine runs it — all of them do.

```
3-node cluster with DaemonSet:

Node 1: [fluentd pod]
Node 2: [fluentd pod]
Node 3: [fluentd pod]

Add Node 4 → automatically gets [fluentd pod]
Remove Node 2 → pod is removed
```

### When to Use DaemonSet vs Deployment

| Use DaemonSet when... | Use Deployment when... |
|---|---|
| Need exactly one pod per node | Need N pods spread across cluster |
| Collecting node-level data (logs, metrics) | Running your application |
| Running node-level networking | Don't care which specific nodes |
| Need access to host filesystem/network | Don't need host access |

### Real-World DaemonSet Use Cases

| Application | Why DaemonSet? |
|---|---|
| Fluentd / Filebeat | Collects logs from every node's `/var/log` |
| Prometheus Node Exporter | Exposes node CPU/memory/disk metrics |
| Calico / Weave / Cilium | Network plugin must run on every node |
| kube-proxy | Routes traffic on every node (built-in DaemonSet) |
| CSI node driver | Storage driver needed on every node |
| Datadog Agent | Monitoring agent per node |

---

### Example 1: Log Collector (Fluentd)

"Collect all container logs from every node and ship them to Elasticsearch."

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: logging
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd:latest
        resources:
          requests:
            memory: "200Mi"
            cpu: "100m"
          limits:
            memory: "500Mi"
            cpu: "200m"
        volumeMounts:
        - name: varlog
          mountPath: /var/log              # Node's log directory
        - name: containers
          mountPath: /var/lib/docker/containers
          readOnly: true                   # Only reading, not writing
      volumes:
      - name: varlog
        hostPath:
          path: /var/log                   # Mount host's /var/log into pod
      - name: containers
        hostPath:
          path: /var/lib/docker/containers
```

**Why DaemonSet:** Logs exist on every node's filesystem. You need a collector on EVERY node to capture them all.

---

### Example 2: Node Monitoring (Prometheus Node Exporter)

"Expose hardware metrics (CPU, memory, disk) from every node."

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostNetwork: true              # Use node's network (access node metrics)
      hostPID: true                  # See node's processes
      containers:
      - name: node-exporter
        image: prom/node-exporter:latest
        ports:
        - containerPort: 9100
          hostPort: 9100             # Expose on node's port directly
        resources:
          requests:
            memory: "100Mi"
            cpu: "50m"
          limits:
            memory: "200Mi"
            cpu: "100m"
```

**Why DaemonSet:** Each node has its own CPU/memory/disk. You need an exporter on each one to get per-node metrics.

---

### Example 3: DaemonSet on Specific Nodes Only

"Run GPU driver only on nodes with GPUs."

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: nvidia-driver
spec:
  selector:
    matchLabels:
      app: nvidia-driver
  template:
    metadata:
      labels:
        app: nvidia-driver
    spec:
      nodeSelector:
        gpu: "true"                  # Only nodes labeled gpu=true
      tolerations:
      - key: "nvidia.com/gpu"
        operator: "Exists"
        effect: "NoSchedule"
      containers:
      - name: nvidia-driver
        image: nvidia/driver:latest
```

**Why nodeSelector:** You don't want GPU drivers on nodes without GPUs. Label your GPU nodes with `gpu=true`, and the DaemonSet only runs there.

---

### DaemonSet Key Parameters

```yaml
spec:
  updateStrategy:
    type: RollingUpdate          # or OnDelete
    rollingUpdate:
      maxUnavailable: 1          # Update one node at a time
  revisionHistoryLimit: 10       # Keep 10 old versions for rollback
```

- **RollingUpdate** — automatically updates pods on each node one by one
- **OnDelete** — only updates a pod when you manually delete it (more control)
- **maxUnavailable** — how many nodes can be without the pod during update

---

## Jobs

### What is a Job?

A Job creates pods that run a task to completion and then stop. Unlike Deployments (which keep pods running forever), Jobs are for one-time or batch tasks.

**Analogy:** A Deployment is like a waiter (always working). A Job is like a delivery person (delivers the package, then done).

### When to Use a Job

| Scenario | Use Job? |
|---|---|
| Run database migration | ✅ Job |
| Process a batch of images | ✅ Job |
| Send bulk emails | ✅ Job |
| Run a web server | ❌ Deployment |
| One-time data import | ✅ Job |
| Generate a report | ✅ Job |

---

### Example 1: Simple One-Time Task

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: database-migration
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: myapp:latest
        command: ["python", "manage.py", "migrate"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
      restartPolicy: Never       # Don't restart on failure
  backoffLimit: 3                # Retry up to 3 times if it fails
```

**What happens:** Pod runs the migration, completes, stops. If it fails, Kubernetes retries up to 3 times.

---

### Example 2: Parallel Processing

"Process 100 items with 5 workers running at the same time."

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: image-processing
spec:
  completions: 100          # Total tasks to complete
  parallelism: 5            # Run 5 pods at the same time
  template:
    spec:
      containers:
      - name: processor
        image: image-processor:latest
        env:
        - name: QUEUE_URL
          value: "redis://queue:6379"
      restartPolicy: Never
  backoffLimit: 10
```

**What happens:**
- 5 pods start immediately
- Each grabs a task from the queue, processes it, completes
- Kubernetes creates new pods until 100 completions reached
- Maximum 5 running at any time

---

### Job Key Parameters

| Parameter | Meaning |
|---|---|
| `completions` | Total successful runs needed |
| `parallelism` | Max pods running simultaneously |
| `backoffLimit` | Max retries before marking as failed |
| `activeDeadlineSeconds` | Max time the job can run before being killed |
| `restartPolicy` | `Never` (create new pod on fail) or `OnFailure` (restart same pod) |

---

## CronJobs

### What is a CronJob?

A CronJob creates Jobs on a schedule — like cron on Linux. It's for recurring tasks.

### When to Use

| Scenario | Use CronJob? |
|---|---|
| Nightly database backup | ✅ |
| Hourly report generation | ✅ |
| Weekly cleanup of old data | ✅ |
| Send monthly invoices | ✅ |
| Run app continuously | ❌ Deployment |

---

### Example 1: Nightly Backup

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
spec:
  schedule: "0 2 * * *"            # Every day at 2:00 AM
  concurrencyPolicy: Forbid         # Don't run if previous is still running
  successfulJobsHistoryLimit: 7     # Keep last 7 successful job records
  failedJobsHistoryLimit: 3         # Keep last 3 failed job records
  startingDeadlineSeconds: 300      # If missed by 5 min, skip it
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip > /backup/db-$(date +%Y%m%d).sql.gz
              echo "Backup completed at $(date)"
            env:
            - name: DB_HOST
              value: "postgres-service"
            - name: DB_USER
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: username
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: password
            - name: DB_NAME
              value: "production"
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

---

### Example 2: Weekly Cleanup

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: old-data-cleanup
spec:
  schedule: "0 3 * * 0"            # Every Sunday at 3:00 AM
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleanup
            image: postgres:15
            command:
            - /bin/sh
            - -c
            - |
              psql -h postgres-service -U admin -d production -c \
                "DELETE FROM logs WHERE created_at < NOW() - INTERVAL '90 days';"
              psql -h postgres-service -U admin -d production -c "VACUUM ANALYZE;"
          restartPolicy: OnFailure
```

---

### Schedule Syntax

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sunday=0)
│ │ │ │ │
* * * * *

Examples:
"0 * * * *"      → Every hour (at minute 0)
"*/15 * * * *"   → Every 15 minutes
"0 2 * * *"      → Daily at 2:00 AM
"0 0 * * 0"      → Weekly on Sunday at midnight
"0 0 1 * *"      → Monthly on the 1st at midnight
"0 9-17 * * 1-5" → Every hour from 9 AM to 5 PM, Monday to Friday
```

---

### CronJob Key Parameters

| Parameter | Meaning |
|---|---|
| `concurrencyPolicy: Forbid` | Skip if previous job still running |
| `concurrencyPolicy: Allow` | Run even if previous is still running |
| `concurrencyPolicy: Replace` | Kill previous job, start new one |
| `startingDeadlineSeconds` | How late a job can start before being skipped |
| `successfulJobsHistoryLimit` | How many completed jobs to keep |
| `failedJobsHistoryLimit` | How many failed jobs to keep |

---

## Quick Reference

```bash
# DaemonSets
kubectl get daemonsets
kubectl get pods -o wide             # See which node each pod is on
kubectl rollout status daemonset fluentd

# Jobs
kubectl get jobs
kubectl logs job/database-migration
kubectl delete job database-migration

# CronJobs
kubectl get cronjobs
kubectl describe cronjob database-backup

# Manually trigger a CronJob (create job from it)
kubectl create job --from=cronjob/database-backup manual-backup-now
```

---

## Summary

| Resource | Purpose | Runs on | Lifetime |
|---|---|---|---|
| DaemonSet | One pod per node | Every node (or selected) | Forever |
| Job | Run task to completion | Any available node | Until done |
| CronJob | Scheduled recurring tasks | Any available node | Runs on schedule |

---

## ⏭️ Next: [Module 11: Ingress Controllers](./11-ingress-controllers.md)
