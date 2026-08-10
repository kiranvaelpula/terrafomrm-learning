# Kubernetes Python Client

> **Manage Kubernetes resources programmatically — deployments, pods, services, scaling, and custom automation that kubectl can't easily do.**

---

## 📖 Setup

```bash
pip install kubernetes
```

```python
from kubernetes import client, config

# Load kubeconfig (local development — reads ~/.kube/config)
config.load_kube_config()

# OR from inside a pod running in K8s (uses service account)
# config.load_incluster_config()

# API clients
v1 = client.CoreV1Api()           # Pods, Services, ConfigMaps, Secrets, Namespaces
apps_v1 = client.AppsV1Api()      # Deployments, StatefulSets, DaemonSets
batch_v1 = client.BatchV1Api()    # Jobs, CronJobs
```

---

## 🔍 Read Operations

```python
# List pods in a namespace
pods = v1.list_namespaced_pod(namespace="production")
for pod in pods.items:
    status = pod.status.phase
    restarts = sum(
        cs.restart_count for cs in (pod.status.container_statuses or [])
    )
    print(f"  {pod.metadata.name}: {status} (restarts: {restarts})")

# List deployments
deployments = apps_v1.list_namespaced_deployment(namespace="production")
for dep in deployments.items:
    ready = dep.status.ready_replicas or 0
    desired = dep.spec.replicas
    print(f"  {dep.metadata.name}: {ready}/{desired} ready")

# Get a specific resource
pod = v1.read_namespaced_pod(name="nginx-abc123", namespace="default")
service = v1.read_namespaced_service(name="my-service", namespace="default")
```

---

## ✏️ Write Operations

```python
# Scale a deployment
body = {"spec": {"replicas": 5}}
apps_v1.patch_namespaced_deployment_scale(
    name="myapp", namespace="production", body=body
)
print("Scaled to 5 replicas")

# Update container image (rolling update)
dep = apps_v1.read_namespaced_deployment("myapp", "production")
dep.spec.template.spec.containers[0].image = "myapp:v2.0.1"
apps_v1.replace_namespaced_deployment("myapp", "production", dep)
print("Image updated — rolling update triggered")

# Delete a pod (triggers restart via ReplicaSet)
v1.delete_namespaced_pod(name="myapp-abc123", namespace="default")
```

---

## 🛠️ Practical: Pod Health Report

```python
#!/usr/bin/env python3
"""Generate Kubernetes pod health report across namespaces."""

from kubernetes import client, config
import sys

config.load_kube_config()
v1 = client.CoreV1Api()

def get_pod_health(namespaces=None):
    """Check pod health across namespaces."""
    if namespaces is None:
        namespaces = ["production", "staging", "monitoring"]
    
    issues = []
    
    for ns in namespaces:
        try:
            pods = v1.list_namespaced_pod(namespace=ns)
        except client.exceptions.ApiException as e:
            print(f"  Cannot access namespace '{ns}': {e.reason}")
            continue
        
        print(f"\n{'─'*50}")
        print(f"  Namespace: {ns} ({len(pods.items)} pods)")
        print(f"{'─'*50}")
        
        for pod in pods.items:
            name = pod.metadata.name
            phase = pod.status.phase
            
            # Count restarts
            restarts = 0
            if pod.status.container_statuses:
                restarts = sum(cs.restart_count for cs in pod.status.container_statuses)
            
            # Flag issues
            if phase != "Running" or restarts > 5:
                symbol = "⚠️ "
                issues.append(f"{ns}/{name}: {phase}, restarts={restarts}")
            else:
                symbol = "  "
            
            print(f"  {symbol}{name:45} {phase:10} restarts={restarts}")
    
    return issues

if __name__ == "__main__":
    print("Kubernetes Pod Health Report")
    print("=" * 50)
    
    issues = get_pod_health()
    
    if issues:
        print(f"\n{'='*50}")
        print(f"⚠️  {len(issues)} issue(s) found:")
        for issue in issues:
            print(f"  • {issue}")
        sys.exit(1)
    else:
        print("\n✅ All pods healthy")
```

---

## 🎯 Interview Quick Points

- `config.load_kube_config()` for local, `load_incluster_config()` for in-pod
- `CoreV1Api` for pods, services, configmaps, secrets
- `AppsV1Api` for deployments, statefulsets, daemonsets
- `patch_*` for partial updates, `replace_*` for full replacement
- `list_namespaced_pod()` returns all pods in a namespace
- Check `pod.status.container_statuses[].restart_count` for issues
- Catch `client.exceptions.ApiException` for K8s API errors
- Used for: custom operators, auto-scaling, health reports, cleanup scripts
