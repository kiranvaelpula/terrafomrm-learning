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

## 📖 Understanding Operators (Intuition First)

The previous module ended on a cliffhanger: a Custom Resource is just data — it needs *something* to act on it. That something is an **Operator**, and the idea is beautifully simple. Take the CRD (which gives you a new resource type) and pair it with a controller (code that watches for those resources and does real work). The result captures the knowledge of a human expert as software: `Operator = CRD + Controller`.

The best way to grasp it is the "software SRE" analogy. Imagine you had to run a production PostgreSQL cluster by hand — provisioning nodes, configuring replication, taking backups, failing over when the primary dies, upgrading versions carefully. A skilled database administrator knows all these procedures. An Operator *encodes that expertise into a program* that lives in your cluster and performs those tasks automatically, 24/7, without getting tired or making 3 AM mistakes. You declare "I want a 3-replica PostgreSQL with daily backups," and the Operator handles the how.

The engine that makes this work is the same one at the heart of Kubernetes itself: the **reconciliation loop**. The Operator continuously watches its custom resources, compares the *desired* state (what your CR says) against the *actual* state (what's really running), and takes whatever actions close the gap. If a database pod crashes, the loop notices the mismatch and recreates it, reattaching its storage. This is what makes Operators **self-healing** — they don't just set things up once, they keep them correct forever.

The payoff is enormous for **stateful, operationally complex** software. Stateless apps are easy — a Deployment handles them. But databases, message queues, and search clusters need careful lifecycle management (ordered startup, backups, failover, safe upgrades) that plain YAML can't express. An Operator turns 200 lines of fragile manifests plus tribal knowledge into a 15-line declaration of intent. That's why the ecosystem has Operators for PostgreSQL, Kafka (Strimzi), Elasticsearch (ECK), Prometheus, and more.

Knowing when *not* to reach for one matters too. For simple stateless apps, an Operator is overkill — a Deployment (or Helm chart) is simpler and sufficient. Operators earn their complexity when you need automated day-2 operations: backups, failover, scaling, and zero-downtime upgrades of stateful systems. Tools like the Operator Framework, Kubebuilder, and OLM (a "package manager for operators") make building and installing them practical.

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

## 🎯 Interview Quick Points

- **Operator = CRD + Controller** — a custom resource type plus code that acts on it
- Operators **encode human operational expertise** (a "software SRE/DBA") into automation that runs 24/7
- Powered by the **reconciliation loop**: watch CRs, compare desired vs actual, act to close the gap, repeat
- This loop is what makes Operators **self-healing** — they maintain state continuously, not just at install
- Best for **stateful, operationally complex** systems: databases, Kafka, Elasticsearch, monitoring stacks
- Automate **day-2 operations**: backups, failover, scaling, and safe/zero-downtime upgrades
- Overkill for simple stateless apps — use a Deployment or Helm chart instead
- Popular Operators: Prometheus Operator, PostgreSQL (Zalando/CrunchyData), Strimzi (Kafka), ECK (Elasticsearch), cert-manager
- Build with **Operator SDK / Kubebuilder**; distribute and install via **OLM** and **OperatorHub**
- Operators encapsulate complexity — users declare intent (15 lines) instead of managing ~200 lines of manifests
- Difference from Helm: Helm installs once; an Operator **continuously manages** the app's lifecycle afterward

---

## ⏭️ Next: [Module 20: Service Mesh (Istio)](./20-service-mesh.md)
