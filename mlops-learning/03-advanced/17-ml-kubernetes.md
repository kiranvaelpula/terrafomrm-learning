# ML on Kubernetes

## Overview

Kubernetes (K8s) orchestrates containerized ML workloads, providing scalability, reliability, and resource management for production ML systems.

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

**Next:** [Distributed Training](18-distributed-training.md)
