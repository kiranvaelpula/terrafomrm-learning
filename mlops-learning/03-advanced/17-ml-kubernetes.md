# ML on Kubernetes

## Overview

Kubernetes (K8s) orchestrates containerized ML workloads, providing scalability, reliability, and resource management for production ML systems.

## 📖 Understanding ML on Kubernetes (Intuition First)

Think of Kubernetes as an air traffic controller for containers. You have limited runways (GPUs, CPUs, memory) and lots of planes wanting to land and take off (training jobs, serving containers). The controller decides who goes where and when, reroutes around failures, and scales the number of active gates up and down as traffic changes — all automatically. For ML, that orchestration is enormously valuable because ML workloads are bursty, resource-hungry, and expensive.

Why Kubernetes specifically for ML? Because ML has two very different workload shapes that both benefit from orchestration. **Training** is a heavy, temporary burst — you need a pile of GPUs for a few hours, then release them (paying for idle GPUs is painfully expensive). **Serving** is long-running and must scale with user traffic — quiet at night, slammed at peak. Kubernetes handles both: it schedules training jobs onto GPU nodes and tears them down when done, and it autoscales serving replicas up and down based on load. The alternative — manually managing GPU servers — doesn't scale and wastes money.

Kubernetes also gives ML the same production-grade properties it gives any service: **high availability** (if a node dies, workloads reschedule elsewhere), **rolling updates** (deploy a new model version with no downtime), **resource isolation** (one team's runaway job can't starve another's), and **portability** (the same setup runs on any cloud or on-prem). This is why serious ML platforms are built on Kubernetes.

On top of raw Kubernetes, the ML ecosystem adds specialized tools. **Kubeflow** brings ML-specific pipelines, notebooks, and training operators. **KServe/Seldon** handle model serving with autoscaling and canary rollouts. GPU scheduling, node pools, and tools like the NVIDIA device plugin let Kubernetes manage GPUs intelligently. The mental model: Kubernetes is the foundation that makes ML training and serving scalable, resilient, and cost-efficient — and the ML tools sit on top to make it ML-aware.

## Why Kubernetes for ML?

✅ Scalable training and serving  
✅ Resource management (GPU, CPU)  
✅ High availability  
✅ Rolling updates  
✅ Auto-scaling  
✅ Multi-tenancy

## Basic Concepts

### Pods
Smallest deployable unit, contains one or more containers

### Deployments
Manages replica sets and rolling updates

### Services
Exposes pods to network traffic

### ConfigMaps & Secrets
Configuration and sensitive data

## Deploying ML Model

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-model
  template:
    metadata:
      labels:
        app: ml-model
    spec:
      containers:
      - name: model
        image: myregistry/ml-model:v1
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        env:
        - name: MODEL_PATH
          value: "/models/model.pkl"
---
apiVersion: v1
kind: Service
metadata:
  name: ml-model-service
spec:
  selector:
    app: ml-model
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f deployment.yaml
kubectl get pods
kubectl get services
```

## Kubeflow

End-to-end ML platform on Kubernetes:

- **Notebooks:** JupyterHub for development
- **Pipelines:** Workflow orchestration
- **Training:** Distributed training
- **Serving:** Model deployment (KServe)

## KServe (Model Serving)

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: sklearn-iris
spec:
  predictor:
    sklearn:
      storageUri: "s3://my-bucket/model"
      resources:
        limits:
          cpu: "1"
          memory: "2Gi"
```

## GPU Support

```yaml
resources:
  limits:
    nvidia.com/gpu: 1  # Request 1 GPU
```

## Auto-scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-model-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-model
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Best Practices

✅ Use health checks  
✅ Set resource limits  
✅ Use namespaces for organization  
✅ Implement proper logging  
✅ Use secrets for credentials  
✅ Monitor resource usage

---

## 🎯 Interview Quick Points

- Kubernetes orchestrates containerized ML workloads — like air traffic control for containers
- Handles two ML workload shapes: **bursty training** (grab GPUs, release when done) and **long-running serving** (autoscale with traffic)
- Prevents paying for idle GPUs — schedules training jobs and tears them down
- Provides HA (reschedule on node failure), rolling updates (zero-downtime deploys), resource isolation, portability
- **Kubeflow** adds ML pipelines, notebooks, training operators on top of K8s
- **KServe/Seldon** handle model serving with autoscaling and canary rollouts
- GPU scheduling via node pools + NVIDIA device plugin
- The foundation for scalable, resilient, cost-efficient ML platforms
- Same K8s benefits any service gets, applied to ML training and serving
- Manual GPU server management doesn't scale — K8s automates it

**Next:** [Distributed Training](18-distributed-training.md)
