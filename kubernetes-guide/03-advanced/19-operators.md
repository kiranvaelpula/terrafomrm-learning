# Module 19: Kubernetes Operators

## What are Operators?

An Operator is a pattern that combines a CRD (Custom Resource Definition) with a Controller that watches for changes and automates complex tasks.

**Formula:** Operator = CRD + Controller

Think of it this way:
- **CRD** = "Here's what I want" (the desired state, like "I want a 3-node PostgreSQL cluster")
- **Controller** = "I'll make it happen and keep it running" (the automation logic)

**When to use:**
- You need to automate complex, stateful application management (databases, message queues, monitoring stacks)
- Manual operational tasks are repetitive (backup, failover, scaling, upgrading)
- You want self-healing — if a database node dies, the operator creates a new one and reattaches storage
- Your team shouldn't need to know the internals of running a complex system

**Real-world analogy:** An operator is like hiring a dedicated DBA who lives inside your cluster. You tell them "I want a PostgreSQL cluster with 3 replicas and daily backups" and they handle everything — provisioning, configuration, failover, backups, upgrades — automatically.

---

## 🎯 How Operators Work

```
You create:    Database CR (desired state)
                    ↓
Operator sees:  "New database requested"
                    ↓
Operator does:  Creates StatefulSet, Services, ConfigMaps, Secrets,
                sets up replication, schedules backups
                    ↓
Operator loops: Continuously checks if actual state = desired state
                If something drifts → fixes it automatically
```

**The reconciliation loop:**
1. Watch for changes to custom resources
2. Compare desired state (CR) with actual state (cluster)
3. Take action to make actual = desired
4. Repeat forever

---

## 🛠️ Install Operator Lifecycle Manager (OLM)

OLM helps you install, update, and manage operators. Think of it as a "package manager for operators."

```bash
curl -sL https://github.com/operator-framework/operator-lifecycle-manager/releases/download/v0.25.0/install.sh | bash -s v0.25.0

kubectl get pods -n olm
```

**When to use OLM:** When you want to install community operators from OperatorHub with automatic updates and dependency management.

---

## 📦 Install Prometheus Operator

```bash
kubectl create -f https://operatorhub.io/install/prometheus.yaml

# Check operator is running
kubectl get csv -n operators
```

After installing, the operator watches for `Prometheus`, `ServiceMonitor`, and `AlertManager` custom resources. You don't manually create pods and configs — you just declare what you want.

---

## 📝 Use Prometheus Operator

Instead of manually deploying Prometheus (StatefulSet, ConfigMaps, RBAC, etc.), you just create this:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: prometheus
spec:
  replicas: 2                        # HA setup
  serviceAccountName: prometheus
  serviceMonitorSelector:
    matchLabels:
      team: frontend                 # Auto-discover ServiceMonitors with this label
  resources:
    requests:
      memory: 400Mi
```

**In plain English:** "I want 2 Prometheus instances that automatically monitor anything labeled `team: frontend`." The operator handles everything else — deploying pods, configuring scrape targets, managing storage.

**Without an operator:** You'd write ~200 lines of YAML (StatefulSet, ConfigMap, ServiceAccount, RBAC, Service, etc.) and manually update configs every time a new service appears.

**With an operator:** 15 lines. The operator handles the rest.

---

## 🔧 Popular Operators

| Operator | What it automates |
|---|---|
| **Prometheus Operator** | Monitoring stack (Prometheus, Alertmanager, Grafana) |
| **PostgreSQL Operator** (Zalando/CrunchyData) | PostgreSQL clusters, replication, backups, failover |
| **Elasticsearch Operator** (ECK) | Elasticsearch clusters, Kibana, APM |
| **Istio Operator** | Service mesh installation and management |
| **Cert-Manager** | TLS certificate provisioning and renewal |
| **Strimzi** | Apache Kafka clusters |
| **Redis Operator** | Redis clusters with HA |
| **ArgoCD** | GitOps continuous delivery |

---

## When to Use an Operator vs Plain YAML

| Scenario | Use Plain YAML | Use an Operator |
|---|---|---|
| Simple stateless app | ✅ | Overkill |
| Stateful app (database) | Complex, error-prone | ✅ Handles lifecycle |
| Need automated backups | Manual scripting | ✅ Built-in |
| Need automated failover | Custom scripts | ✅ Handles it |
| Upgrades with zero downtime | Risky manually | ✅ Rolling upgrades |
| One-off deployment | ✅ | Unnecessary |
| Repeated across teams | ✅ with Helm | ✅ Even better |

---

## Where to Find Operators

- **OperatorHub.io** — https://operatorhub.io (curated catalog)
- **Artifact Hub** — https://artifacthub.io (broader search)
- **GitHub** — search for "[technology] operator kubernetes"

---

## ⏭️ Next: [Module 20: Service Mesh (Istio)](./20-service-mesh.md)
