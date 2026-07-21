# Module 18: Custom Resources (CRDs)

## 📝 Create CRD

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: applications.stable.example.com
spec:
  group: stable.example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
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
  scope: Namespaced
  names:
    plural: applications
    singular: application
    kind: Application
    shortNames:
    - app
```

```bash
kubectl apply -f crd.yaml
kubectl get crds
```

## 🎯 Use Custom Resource

```yaml
apiVersion: stable.example.com/v1
kind: Application
metadata:
  name: myapp
spec:
  image: nginx:1.21
  replicas: 3
  port: 80
```

```bash
kubectl apply -f myapp.yaml
kubectl get applications
kubectl describe application myapp
```

## 📊 CRD with Validation

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
        required: ["spec"]
        properties:
          spec:
            type: object
            required: ["type", "version"]
            properties:
              type:
                type: string
                enum: ["postgres", "mysql", "mongodb"]
              version:
                type: string
                pattern: '^\d+\.\d+$'
              storage:
                type: string
                pattern: '^\d+(Gi|Mi)$'
  scope: Namespaced
  names:
    plural: databases
    singular: database
    kind: Database
```

## ⏭️ Next: [Module 19: Operators](./19-operators.md)
