# Module 18: Custom Resources (CRDs)

## What are Custom Resource Definitions?

Kubernetes comes with built-in resources like Pods, Services, Deployments. But what if you want to create your OWN resource type — like `Database`, `Application`, or `Certificate`? That's what CRDs let you do.

A CRD extends the Kubernetes API so you can manage your own custom objects using `kubectl` just like built-in resources.

**When to use:**
- You want to manage application-specific configurations as Kubernetes objects
- You're building an operator that automates complex tasks (e.g., "when someone creates a `Database` object, automatically provision a PostgreSQL instance")
- You want declarative management of things Kubernetes doesn't natively understand (certificates, DNS records, message queues)
- Your team wants a simplified interface — instead of 5 YAML files, users create 1 custom resource

**Real-world examples:**
- `Certificate` (cert-manager) — create a cert resource, operator gets you a real TLS certificate
- `Prometheus` (prometheus-operator) — create a Prometheus resource, operator deploys a monitoring stack
- `VirtualService` (Istio) — custom traffic routing rules

---

## 📝 Create CRD

This defines a NEW resource type called `Application`. After applying this, anyone can create `Application` objects in the cluster.

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: applications.stable.example.com    # Must be: plural.group
spec:
  group: stable.example.com               # API group (like a namespace for your API)
  versions:
  - name: v1                              # Version of your API
    served: true                          # Is this version active?
    storage: true                         # Is this the storage version?
    schema:
      openAPIV3Schema:                    # Validation rules
        type: object
        properties:
          spec:
            type: object
            properties:
              image:
                type: string
              replicas:
                type: integer
                minimum: 1
                maximum: 10
              port:
                type: integer
          status:
            type: object
            properties:
              availableReplicas:
                type: integer
  scope: Namespaced                       # Lives in a namespace (vs Cluster-wide)
  names:
    plural: applications                  # kubectl get applications
    singular: application                 # kubectl get application myapp
    kind: Application                     # The YAML "kind" field
    shortNames:
    - app                                 # kubectl get app (shortcut)
```

**In plain English:** "I'm telling Kubernetes: there's a new type of thing called `Application`. It has an image (string), replicas (number 1-10), and a port (number). People can create them in any namespace."

```bash
kubectl apply -f crd.yaml
kubectl get crds
```

---

## 🎯 Use Custom Resource

Once the CRD is registered, you can create instances of it — these are called Custom Resources (CRs).

```yaml
apiVersion: stable.example.com/v1      # group/version from the CRD
kind: Application                       # kind from the CRD
metadata:
  name: myapp
spec:
  image: nginx:1.21
  replicas: 3
  port: 80
```

**In plain English:** "Create an Application called myapp with nginx image, 3 replicas, on port 80."

```bash
kubectl apply -f myapp.yaml
kubectl get applications            # List all applications
kubectl get app                     # Same thing, using shortName
kubectl describe application myapp  # Details
kubectl delete application myapp    # Delete it
```

**Important:** Creating a custom resource ALONE doesn't do anything. It's just data stored in etcd. You need a controller/operator (Module 19) watching for these objects and actually doing something — like creating Deployments, Services, etc.

---

## 📊 CRD with Validation

You can add strict validation so users can't create invalid resources.

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databases.db.example.com
spec:
  group: db.example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        required: ["spec"]                    # spec is mandatory
        properties:
          spec:
            type: object
            required: ["type", "version"]     # These fields are mandatory
            properties:
              type:
                type: string
                enum: ["postgres", "mysql", "mongodb"]   # Only these values allowed
              version:
                type: string
                pattern: '^\d+\.\d+$'          # Must match X.Y format
              storage:
                type: string
                pattern: '^\d+(Gi|Mi)$'        # Must be like "10Gi" or "512Mi"
  scope: Namespaced
  names:
    plural: databases
    singular: database
    kind: Database
```

**In plain English:** "A Database must have a type (only postgres, mysql, or mongodb), a version (format X.Y), and optionally a storage size (like 10Gi). If someone tries to create a Database with type 'redis', Kubernetes rejects it."

**When to use validation:**
- Prevent invalid configurations from being created
- Enforce team standards (only approved database types)
- Catch errors early instead of at runtime

---

## Key Concepts Summary

| Term | What it is |
|---|---|
| CRD | The definition/schema (like a class in programming) |
| CR (Custom Resource) | An instance of that CRD (like an object of that class) |
| Controller/Operator | Code that watches CRs and takes action |
| group | API namespace (e.g., `stable.example.com`) |
| kind | The resource type name used in YAML |
| scope | `Namespaced` or `Cluster` (affects visibility) |

---

## ⏭️ Next: [Module 19: Operators](./19-operators.md)
