# Module 13: RBAC & Security

## What is RBAC?

Role-Based Access Control (RBAC) controls who can do what in your cluster. Instead of giving everyone full admin access, you define roles with specific permissions and assign them to users or service accounts.

**When to use:**
- Always. Every production cluster should have RBAC enabled.
- Developers should only access their own namespaces
- CI/CD pipelines should only deploy, not delete infrastructure
- Monitoring tools should only read metrics, not modify resources

**Core concept:** "Who (Subject) can do What (Verbs) on Which resources (Resources)"

---

## Key RBAC Components

| Component | Scope | Purpose |
|---|---|---|
| Role | Namespace | Defines permissions within a namespace |
| ClusterRole | Cluster-wide | Defines permissions across all namespaces |
| RoleBinding | Namespace | Assigns a Role to a user/group in a namespace |
| ClusterRoleBinding | Cluster-wide | Assigns a ClusterRole to a user/group globally |

---

## 🔐 Role & RoleBinding

**Role** = "what actions are allowed"
**RoleBinding** = "who gets those permissions"

```yaml
# Role: can read pods in the default namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
rules:
- apiGroups: [""]              # "" = core API group (pods, services, etc.)
  resources: ["pods"]          # Which resources
  verbs: ["get", "list", "watch"]  # What actions

---
# RoleBinding: give jane the pod-reader role
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: jane                   # Who gets the permission
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader             # Which role to assign
  apiGroup: rbac.authorization.k8s.io
```

**In plain English:** "Jane can view pods in the default namespace, but can't create, edit, or delete them."

---

## ClusterRole & ClusterRoleBinding

Same as Role/RoleBinding but applies across ALL namespaces.

```yaml
# ClusterRole: can read nodes (cluster-wide resource)
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list", "watch"]

---
# ClusterRoleBinding: give the ops-team group this permission
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-nodes-global
subjects:
- kind: Group
  name: ops-team
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: node-reader
  apiGroup: rbac.authorization.k8s.io
```

**When to use ClusterRole vs Role:**
- **Role** — for namespace-scoped resources (pods, services, deployments)
- **ClusterRole** — for cluster-scoped resources (nodes, namespaces, PVs) or when you want the same permissions across all namespaces

---

## Service Accounts

Pods use ServiceAccounts (not user accounts) to interact with the API. By default, pods get a default ServiceAccount with minimal permissions.

```yaml
# Create a service account for your app
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: production
automountServiceAccountToken: false   # Don't mount token unless needed

---
# Give it specific permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-role
  namespace: production
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]              # Can only READ configmaps

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-binding
  namespace: production
subjects:
- kind: ServiceAccount
  name: app-sa
  namespace: production
roleRef:
  kind: Role
  name: app-role
  apiGroup: rbac.authorization.k8s.io
```

**Best practice:** Every app gets its own ServiceAccount with minimum required permissions. Never use the default ServiceAccount in production.

---

## Common Verbs

| Verb | Meaning |
|---|---|
| get | Read a single resource |
| list | Read all resources of a type |
| watch | Stream changes in real-time |
| create | Create new resources |
| update | Modify existing resources |
| patch | Partially modify resources |
| delete | Delete resources |
| * | All actions (use carefully) |

---

## Useful Commands

```bash
# Check if you can do something
kubectl auth can-i create pods
kubectl auth can-i delete nodes

# Check as a specific user
kubectl auth can-i create pods --as=jane -n production

# Check as a service account
kubectl auth can-i list secrets --as=system:serviceaccount:production:app-sa

# View roles in a namespace
kubectl get roles -n production
kubectl get rolebindings -n production

# View cluster roles
kubectl get clusterroles
kubectl get clusterrolebindings
```

---

## ⏭️ Next: [Module 14: Helm Package Manager](./14-helm.md)
