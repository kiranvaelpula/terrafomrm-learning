# Module 10: DaemonSets & Jobs

## 📚 What You'll Learn
- DaemonSets for node-level services
- Jobs for batch processing
- CronJobs for scheduled tasks
- Parallel job execution
- Best practices

---

## 🎯 DaemonSets

**DaemonSet** ensures a copy of a Pod runs on all (or some) nodes.

### Use Cases
- Log collectors (Fluentd, Filebeat)
- Monitoring agents (Prometheus Node Exporter)
- Storage daemons (Ceph, GlusterFS)
- Network plugins (Calico, Weave)

### Basic DaemonSet

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  labels:
    app: fluentd
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
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

```bash
kubectl apply -f daemonset.yaml
kubectl get daemonset
kubectl get pods -o wide  # One pod per node
```

### Node Selector DaemonSet

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: gpu-daemon
spec:
  selector:
    matchLabels:
      app: gpu-daemon
  template:
    metadata:
      labels:
        app: gpu-daemon
    spec:
      nodeSelector:
        gpu: "true"  # Only nodes with this label
      containers:
      - name: nvidia-driver
        image: nvidia/cuda:11.0-base
```

---

## 📦 Jobs

**Job** creates Pods that run to completion.

### Basic Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pi-calculation
spec:
  template:
    spec:
      containers:
      - name: pi
        image: perl:5.34
        command: ["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"]
      restartPolicy: Never
  backoffLimit: 4  # Retry limit
```

```bash
kubectl apply -f job.yaml
kubectl get jobs
kubectl get pods
kubectl logs <pod-name>
```

### Parallel Jobs

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: parallel-job
spec:
  completions: 10      # Total successful completions needed
  parallelism: 3       # Max pods running in parallel
  template:
    spec:
      containers:
      - name: worker
        image: busybox
        command: ["sh", "-c", "echo Processing item && sleep 5"]
      restartPolicy: Never
```

### Work Queue Pattern

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: queue-job
spec:
  completions: 50
  parallelism: 10
  template:
    spec:
      containers:
      - name: worker
        image: gcr.io/myproject/worker:latest
        env:
        - name: QUEUE_URL
          value: "redis://queue:6379"
      restartPolicy: Never
```

---

## ⏰ CronJobs

**CronJob** creates Jobs on a schedule.

### Basic CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job
spec:
  schedule: "0 2 * * *"  # Every day at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: backup-tool:latest
            command:
            - /bin/sh
            - -c
            - echo "Running backup at $(date)"
          restartPolicy: OnFailure
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
```

### Schedule Syntax

```
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
# │ │ │ │ │
# * * * * *

Examples:
"0 * * * *"      # Every hour
"*/15 * * * *"   # Every 15 minutes
"0 2 * * *"      # Daily at 2 AM
"0 0 * * 0"      # Weekly on Sunday
"0 0 1 * *"      # Monthly on 1st
```

### Advanced CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-cleanup
spec:
  schedule: "0 3 * * 0"  # Weekly Sunday 3 AM
  concurrencyPolicy: Forbid  # Don't run concurrent jobs
  startingDeadlineSeconds: 300
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleanup
            image: postgres:14
            env:
            - name: PGHOST
              value: postgres
            - name: PGUSER
              valueFrom:
                secretKeyRef:
                  name: db-creds
                  key: username
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-creds
                  key: password
            command:
            - /bin/sh
            - -c
            - |
              psql -c "DELETE FROM logs WHERE created_at < NOW() - INTERVAL '90 days';"
              psql -c "VACUUM ANALYZE;"
          restartPolicy: OnFailure
```

---

## 🎪 Lab: Complete Example

```yaml
# monitoring-daemonset.yaml
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
      hostNetwork: true
      hostPID: true
      containers:
      - name: node-exporter
        image: prom/node-exporter:latest
        ports:
        - containerPort: 9100
          hostPort: 9100
        resources:
          requests:
            memory: "100Mi"
            cpu: "50m"
          limits:
            memory: "200Mi"
            cpu: "100m"
---
# backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-backup
spec:
  schedule: "0 1 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: alpine:latest
            command:
            - /bin/sh
            - -c
            - |
              echo "Starting backup..."
              tar -czf /backup/data-$(date +%Y%m%d).tar.gz /data
              echo "Backup complete"
            volumeMounts:
            - name: data
              mountPath: /data
            - name: backup
              mountPath: /backup
          volumes:
          - name: data
            persistentVolumeClaim:
              claimName: app-data
          - name: backup
            persistentVolumeClaim:
              claimName: backup-storage
          restartPolicy: OnFailure
---
# batch-processing-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: image-processing
spec:
  completions: 100
  parallelism: 10
  template:
    spec:
      containers:
      - name: processor
        image: image-processor:latest
        env:
        - name: WORKER_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: REDIS_URL
          value: redis://queue:6379
      restartPolicy: Never
  backoffLimit: 3
```

---

## 📝 Quick Reference

```bash
# DaemonSets
kubectl get daemonsets
kubectl describe daemonset <name>
kubectl delete daemonset <name>

# Jobs
kubectl get jobs
kubectl describe job <name>
kubectl delete job <name>
kubectl logs job/<job-name>

# CronJobs
kubectl get cronjobs
kubectl describe cronjob <name>
kubectl delete cronjob <name>

# Manually trigger CronJob
kubectl create job --from=cronjob/<cronjob-name> <job-name>
```

---

## 💡 Best Practices

```yaml
# 1. Set resource limits for DaemonSets
resources:
  requests:
    memory: "100Mi"
    cpu: "50m"
  limits:
    memory: "200Mi"
    cpu: "100m"

# 2. Use proper restart policies
restartPolicy: Never  # For Jobs
restartPolicy: OnFailure  # For CronJobs

# 3. Set job history limits
successfulJobsHistoryLimit: 3
failedJobsHistoryLimit: 1

# 4. Use concurrency policy
concurrencyPolicy: Forbid  # No concurrent runs
```

---

## ⏭️ Next: [Module 11: Ingress Controllers](./11-ingress-controllers.md)
