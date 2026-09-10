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

## 📖 Understanding Custom Resources (Intuition First)

Kubernetes ships with a fixed vocabulary of nouns: Pod, Service, Deployment, ConfigMap, and so on. Its real superpower, though, is that this vocabulary is *extensible*. A **Custom Resource Definition (CRD)** lets you teach Kubernetes a brand-new noun — like `Database`, `Certificate`, or `KafkaCluster` — so that from that moment on, `kubectl get databases` works exactly like `kubectl get pods`. You're literally adding new words to the cluster's API.

The cleanest way to think about it is in programming terms. A **CRD is a class** — it defines the *shape* of a new kind of object (what fields it has, what values are valid). A **Custom Resource (CR) is an instance** of that class — an actual `Database` named `my-postgres` with `type: postgres` and `version: 15`. Defining the class doesn't create any behavior; it just makes the type available and stored in etcd.

This is the part that trips people up: **creating a custom resource, by itself, does nothing.** A `Database` object you apply is just structured data sitting in the cluster's database. It won't provision a real PostgreSQL server on its own. Something has to be *watching* for these objects and taking action — that something is a controller or operator (the next module). The CRD provides the vocabulary and storage; the controller provides the muscle.

So why bother? Because it lets you offer a **simplified, declarative interface** to complex systems. Instead of asking developers to hand-write a StatefulSet, a Service, ConfigMaps, Secrets, and backup CronJobs, you let them write a single tidy `Database` resource. All the messy detail is hidden behind your custom type. This is exactly how tools like cert-manager (`Certificate`), Prometheus Operator (`Prometheus`), and Istio (`VirtualService`) present clean, purpose-built APIs on top of Kubernetes.

CRDs also let you enforce guardrails through an **OpenAPI schema**. You can require certain fields, restrict values to an allowed set (only `postgres`, `mysql`, or `mongodb`), and validate formats. Invalid resources get rejected at creation time by the API server itself — catching mistakes early instead of at runtime. Understanding the trio of *CRD (the type), CR (the instance), and controller (the actor)* is the foundation for everything in the operator pattern.

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

## 🎯 Interview Quick Points

- A **CRD** extends the Kubernetes API with your own resource types, usable via `kubectl` like built-in ones
- Mental model: **CRD = class (schema), CR = instance (data), Controller/Operator = the actor that does the work**
- Creating a CR alone **does nothing** — it's just data in etcd until a controller watches and acts on it
- CRDs enable a **simplified declarative interface** hiding complex underlying resources
- Naming convention: `plural.group` (e.g., `applications.stable.example.com`); define plural, singular, kind, shortNames
- **scope** is `Namespaced` or `Cluster`
- Use an **OpenAPI v3 schema** to validate fields — `required`, `enum`, `pattern`, min/max — rejecting bad resources at creation
- **Versions** support API evolution; one version is marked `storage: true`
- Real-world CRDs: cert-manager `Certificate`, Prometheus Operator `Prometheus`, Istio `VirtualService`
- CRDs are the lightweight alternative to building a full **aggregated API server**
- Foundational to the **operator pattern** covered next

---

## ⏭️ Next: [Module 19: Operators](./19-operators.md)
