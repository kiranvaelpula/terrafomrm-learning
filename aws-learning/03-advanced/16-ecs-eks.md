# Chapter 16: ECS and EKS - Container Orchestration on AWS

## Overview

Amazon ECS (Elastic Container Service) and EKS (Elastic Kubernetes Service) are AWS's container orchestration platforms. ECS is AWS-native, while EKS runs standard Kubernetes.

**What You'll Learn**
- ECS fundamentals (EC2 and Fargate launch types)
- EKS cluster setup and management
- Container deployment strategies
- Service discovery and load balancing
- Auto-scaling for containers
- Monitoring and logging
- When to choose ECS vs EKS

**Prerequisites**
- Docker knowledge
- Understanding of containers
- VPC and networking basics
- IAM roles and policies

---

## Amazon ECS

### ECS Architecture

**Components:**
```
ECS Cluster
    |
    +-- Task Definition (blueprint)
    |       |
    |       +-- Container Definition
    |       +-- CPU/Memory allocation
    |       +-- Environment variables
    |
    +-- Service (manages tasks)
    |       |
    |       +-- Desired count
    |       +-- Load balancer integration
    |       +-- Auto-scaling
    |
    +-- Task (running container instance)
            |
            +-- Container(s)
```

### Launch Types

**1. EC2 Launch Type**
- You manage EC2 instances
- More control, lower cost
- Good for consistent workloads

**2. Fargate Launch Type**
- Serverless containers
- AWS manages infrastructure
- Pay per task
- Good for variable workloads


### Creating ECS Cluster

**Using Fargate:**
```bash
# Create cluster
aws ecs create-cluster \
  --cluster-name my-fargate-cluster \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=1 \
    capacityProvider=FARGATE_SPOT,weight=3

# Verify cluster
aws ecs describe-clusters --clusters my-fargate-cluster
```

**Using EC2:**
```bash
# Create cluster
aws ecs create-cluster --cluster-name my-ec2-cluster

# Launch EC2 instances with ECS-optimized AMI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --iam-instance-profile Name=ecsInstanceRole \
  --user-data file://ecs-user-data.txt \
  --count 2
```

**ECS User Data Script:**
```bash
#!/bin/bash
echo ECS_CLUSTER=my-ec2-cluster >> /etc/ecs/ecs.config
echo ECS_ENABLE_CONTAINER_METADATA=true >> /etc/ecs/ecs.config
```

### Task Definition

**JSON Format:**
```json
{
  "family": "web-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "nginx",
      "image": "nginx:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "ENV",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/web-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "nginx"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost/ || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

**Register Task Definition:**
```bash
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json
```

### Creating ECS Service

```bash
# Create service with load balancer
aws ecs create-service \
  --cluster my-fargate-cluster \
  --service-name web-service \
  --task-definition web-app:1 \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-12345,subnet-67890],
    securityGroups=[sg-12345],
    assignPublicIp=ENABLED
  }" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,
    containerName=nginx,
    containerPort=80"
```


### ECS Auto Scaling

**Target Tracking:**
```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/my-cluster/web-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/my-cluster/web-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

**scaling-policy.json:**
```json
{
  "TargetValue": 70.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
  },
  "ScaleInCooldown": 300,
  "ScaleOutCooldown": 60
}
```

---

## Amazon EKS

### EKS Architecture

```
EKS Control Plane (AWS Managed)
    |
    +-- API Server
    +-- etcd
    +-- Controller Manager
    +-- Scheduler
    |
Data Plane (Your Managed)
    |
    +-- Worker Nodes (EC2 or Fargate)
            |
            +-- Pods
            +-- kubelet
            +-- kube-proxy
```

### Creating EKS Cluster

**Using eksctl (easiest):**
```bash
# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create cluster
eksctl create cluster \
  --name my-eks-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 4 \
  --managed
```

**Using AWS CLI:**
```bash
# Create cluster
aws eks create-cluster \
  --name my-eks-cluster \
  --role-arn arn:aws:iam::123456789012:role/EKSClusterRole \
  --resources-vpc-config \
    subnetIds=subnet-12345,subnet-67890,
    securityGroupIds=sg-12345

# Wait for cluster to be active
aws eks wait cluster-active --name my-eks-cluster

# Create node group
aws eks create-nodegroup \
  --cluster-name my-eks-cluster \
  --nodegroup-name standard-workers \
  --subnets subnet-12345 subnet-67890 \
  --node-role arn:aws:iam::123456789012:role/EKSNodeRole \
  --instance-types t3.medium \
  --scaling-config minSize=1,maxSize=4,desiredSize=2
```

### Configure kubectl

```bash
# Update kubeconfig
aws eks update-kubeconfig \
  --region us-east-1 \
  --name my-eks-cluster

# Verify connection
kubectl get nodes
kubectl cluster-info
```

### Deploying to EKS

**Deployment YAML:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "250m"
          limits:
            memory: "256Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

**Deploy:**
```bash
kubectl apply -f deployment.yaml

# Check status
kubectl get deployments
kubectl get pods
kubectl get services

# Get load balancer URL
kubectl get svc nginx-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

### EKS with Fargate

**Create Fargate Profile:**
```bash
aws eks create-fargate-profile \
  --cluster-name my-eks-cluster \
  --fargate-profile-name my-fargate-profile \
  --pod-execution-role-arn arn:aws:iam::123456789012:role/EKSFargatePodRole \
  --selectors namespace=default \
  --subnets subnet-private1 subnet-private2
```

**Deploy to Fargate:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: fargate-ns
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
  namespace: fargate-ns
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:latest
```

---

## ECS vs EKS Comparison

| Feature | ECS | EKS |
|---------|-----|-----|
| **Orchestration** | AWS proprietary | Kubernetes |
| **Learning Curve** | Easy | Steep |
| **AWS Integration** | Excellent | Good |
| **Portability** | AWS only | Multi-cloud |
| **Control Plane Cost** | Free | $0.10/hour |
| **Ecosystem** | Limited | Extensive |
| **Best For** | AWS-native apps | K8s experience, portability |

**Choose ECS when:**
- You're AWS-only
- Want simpler management
- Need tight AWS integration
- Team is new to containers

**Choose EKS when:**
- Need Kubernetes features
- Want multi-cloud portability
- Team knows Kubernetes
- Need extensive K8s ecosystem

---

## Service Discovery

### ECS Service Discovery

```bash
# Create namespace
aws servicediscovery create-private-dns-namespace \
  --name local \
  --vpc vpc-12345

# Create service
aws servicediscovery create-service \
  --name backend \
  --dns-config 'NamespaceId="ns-12345",DnsRecords=[{Type="A",TTL="300"}]' \
  --health-check-custom-config FailureThreshold=1

# ECS service with service discovery
aws ecs create-service \
  --cluster my-cluster \
  --service-name backend \
  --task-definition backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --service-registries 'registryArn=arn:aws:servicediscovery:...'
```

### EKS Service Discovery (CoreDNS)

```yaml
# Automatic with ClusterIP services
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  selector:
    app: backend
  ports:
  - port: 8080

# Access from other pods:
# http://backend.default.svc.cluster.local:8080
```

---

## Monitoring and Logging

### ECS with CloudWatch

**Container Insights:**
```bash
# Enable Container Insights
aws ecs update-cluster-settings \
  --cluster my-cluster \
  --settings name=containerInsights,value=enabled
```

**Task Definition Logging:**
```json
{
  "logConfiguration": {
    "logDriver": "awslogs",
    "options": {
      "awslogs-group": "/ecs/my-app",
      "awslogs-region": "us-east-1",
      "awslogs-stream-prefix": "ecs",
      "awslogs-create-group": "true"
    }
  }
}
```

### EKS Monitoring

**Install CloudWatch Container Insights:**
```bash
# Deploy FluentBit and CloudWatch agent
kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/quickstart/cwagent-fluentd-quickstart.yaml
```

**Prometheus and Grafana:**
```bash
# Install Prometheus
kubectl create namespace prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace prometheus
```

---

## Summary

**Key Takeaways:**
- ECS is AWS-native, simpler to use
- EKS provides standard Kubernetes
- Fargate removes server management
- Both support auto-scaling and service discovery
- Container Insights for monitoring
- Choose based on team skills and requirements

**Next Chapter:** [17-api-gateway.md](./17-api-gateway.md) - API Management



---

## ECS Capacity Providers

**What are Capacity Providers?**
- Manage compute capacity for ECS
- Mix EC2 and Fargate
- Automatic scaling strategies
- Cost optimization

**Capacity Provider Strategy:**
```bash
# Create Auto Scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name ecs-asg \
  --launch-template LaunchTemplateName=ecs-template \
  --min-size 1 \
  --max-size 10 \
  --desired-capacity 2 \
  --vpc-zone-identifier "subnet-1,subnet-2"

# Create capacity provider
aws ecs create-capacity-provider \
  --name my-capacity-provider \
  --auto-scaling-group-provider '{
    "autoScalingGroupArn": "arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:abc:autoScalingGroupName/ecs-asg",
    "managedScaling": {
      "status": "ENABLED",
      "targetCapacity": 80,
      "minimumScalingStepSize": 1,
      "maximumScalingStepSize": 10
    },
    "managedTerminationProtection": "ENABLED"
  }'

# Associate with cluster
aws ecs put-cluster-capacity-providers \
  --cluster my-cluster \
  --capacity-providers my-capacity-provider FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=my-capacity-provider,weight=1,base=2 \
    capacityProvider=FARGATE_SPOT,weight=4
```

**Capacity Provider Strategy Explained:**
```
base=2: Start 2 tasks on EC2
weight=1: 20% on EC2 capacity provider
weight=4: 80% on Fargate Spot

Example with 10 tasks:
- 2 on EC2 (base)
- Remaining 8 split: 1.6 EC2 (20%), 6.4 Fargate Spot (80%)
- Actual: 4 on EC2, 6 on Fargate Spot
```

---

## ECS Task Placement


**Placement Strategies:**
```bash
# Spread across AZs
aws ecs create-service \
  --cluster my-cluster \
  --service-name web-service \
  --task-definition web-app \
  --desired-count 6 \
  --placement-strategy type=spread,field=attribute:ecs.availability-zone

# Binpack (minimize instances)
aws ecs create-service \
  --cluster my-cluster \
  --service-name web-service \
  --task-definition web-app \
  --desired-count 10 \
  --placement-strategy type=binpack,field=memory

# Random
aws ecs create-service \
  --cluster my-cluster \
  --service-name web-service \
  --task-definition web-app \
  --desired-count 5 \
  --placement-strategy type=random
```

**Placement Constraints:**
```bash
# Only place on instances with SSD
aws ecs create-service \
  --cluster my-cluster \
  --service-name web-service \
  --task-definition web-app \
  --desired-count 3 \
  --placement-constraints type=memberOf,expression="attribute:storage == ssd"

# One task per instance
aws ecs create-service \
  --cluster my-cluster \
  --service-name web-service \
  --task-definition web-app \
  --desired-count 5 \
  --placement-constraints type=distinctInstance
```

---

## ECS Service Mesh with App Mesh

**What is App Mesh?**
- Service mesh for microservices
- Traffic routing and load balancing
- Observability (metrics, logs, traces)
- Security (TLS encryption)

**App Mesh Architecture:**
```
Service A → Envoy Proxy → Service B
    ↓
  X-Ray Tracing
  CloudWatch Metrics
```


**Create App Mesh:**
```bash
# Create mesh
aws appmesh create-mesh --mesh-name my-mesh

# Create virtual node
aws appmesh create-virtual-node \
  --mesh-name my-mesh \
  --virtual-node-name service-a \
  --spec '{
    "listeners": [{
      "portMapping": {"port": 8080, "protocol": "http"}
    }],
    "serviceDiscovery": {
      "awsCloudMap": {
        "serviceName": "service-a",
        "namespaceName": "local"
      }
    }
  }'

# Create virtual service
aws appmesh create-virtual-service \
  --mesh-name my-mesh \
  --virtual-service-name service-a.local \
  --spec '{
    "provider": {
      "virtualNode": {"virtualNodeName": "service-a"}
    }
  }'
```

---

## EKS Advanced Configuration

### Kubernetes Fundamentals for EKS

**Pods - Smallest Deployable Unit:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "128Mi"
        cpu: "250m"
      limits:
        memory: "256Mi"
        cpu: "500m"
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5
```

**ReplicaSets - Maintain Desired Pod Count:**
```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: nginx-replicaset
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
```

**Deployments - Declarative Updates:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: host
```

**Services - Network Access:**
```yaml
# ClusterIP (internal only)
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080

---
# LoadBalancer (external access via ELB)
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
spec:
  type: LoadBalancer
  selector:
    app: frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80

---
# NodePort
apiVersion: v1
kind: Service
metadata:
  name: nodeport-service
spec:
  type: NodePort
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
    nodePort: 30080
```

**ConfigMaps and Secrets:**
```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  app.properties: |
    environment=production
    log_level=info
    max_connections=100
  config.json: |
    {
      "api_url": "https://api.example.com",
      "timeout": 30
    }

---
# Secret
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded
  password: cGFzc3dvcmQxMjM=

---
# Using ConfigMap and Secret
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:1.0
        envFrom:
        - configMapRef:
            name: app-config
        env:
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        volumeMounts:
        - name: config-volume
          mountPath: /etc/config
      volumes:
      - name: config-volume
        configMap:
          name: app-config
```

---

## EKS Managed Node Groups

**Benefits:**
- Automated provisioning
- Automated updates
- Managed scaling
- Spot instance support

**Creating Managed Node Group:**
```bash
# Create managed node group
aws eks create-nodegroup \
  --cluster-name my-eks-cluster \
  --nodegroup-name standard-workers \
  --node-role arn:aws:iam::123456789012:role/EKSNodeRole \
  --subnets subnet-111 subnet-222 subnet-333 \
  --instance-types t3.medium t3.large \
  --scaling-config minSize=2,maxSize=10,desiredSize=3 \
  --disk-size 20 \
  --labels environment=production,team=platform \
  --tags Key=Environment,Value=Production

# Create Spot node group (70% cost savings)
aws eks create-nodegroup \
  --cluster-name my-eks-cluster \
  --nodegroup-name spot-workers \
  --node-role arn:aws:iam::123456789012:role/EKSNodeRole \
  --subnets subnet-111 subnet-222 \
  --capacity-type SPOT \
  --instance-types t3.medium t3.large t3.xlarge \
  --scaling-config minSize=0,maxSize=20,desiredSize=5

# Update node group
aws eks update-nodegroup-config \
  --cluster-name my-eks-cluster \
  --nodegroup-name standard-workers \
  --scaling-config minSize=3,maxSize=15,desiredSize=5
```

---

## EKS Autoscaling

### Cluster Autoscaler

**Deploy Cluster Autoscaler:**
```bash
# Create IAM policy
cat > cluster-autoscaler-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "autoscaling:DescribeAutoScalingGroups",
        "autoscaling:DescribeAutoScalingInstances",
        "autoscaling:DescribeLaunchConfigurations",
        "autoscaling:DescribeScalingActivities",
        "autoscaling:DescribeTags",
        "ec2:DescribeInstanceTypes",
        "ec2:DescribeLaunchTemplateVersions"
      ],
      "Resource": ["*"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "autoscaling:SetDesiredCapacity",
        "autoscaling:TerminateInstanceInAutoScalingGroup",
        "ec2:DescribeImages",
        "ec2:GetInstanceTypesFromInstanceRequirements",
        "eks:DescribeNodegroup"
      ],
      "Resource": ["*"]
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name AmazonEKSClusterAutoscalerPolicy \
  --policy-document file://cluster-autoscaler-policy.json

# Create service account with IRSA
eksctl create iamserviceaccount \
  --cluster=my-eks-cluster \
  --namespace=kube-system \
  --name=cluster-autoscaler \
  --attach-policy-arn=arn:aws:iam::123456789012:policy/AmazonEKSClusterAutoscalerPolicy \
  --override-existing-serviceaccounts \
  --approve

# Deploy Cluster Autoscaler
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
  labels:
    app: cluster-autoscaler
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      labels:
        app: cluster-autoscaler
    spec:
      serviceAccountName: cluster-autoscaler
      containers:
      - image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.26.2
        name: cluster-autoscaler
        resources:
          limits:
            cpu: 100m
            memory: 600Mi
          requests:
            cpu: 100m
            memory: 600Mi
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/my-eks-cluster
        - --balance-similar-node-groups
        - --skip-nodes-with-system-pods=false
EOF
```

### Horizontal Pod Autoscaler (HPA)

**CPU-based HPA:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 15
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```

**Custom Metrics HPA:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-deployment
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
```

### Vertical Pod Autoscaler (VPA)

```bash
# Install VPA
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler
./hack/vpa-up.sh
```

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: nginx-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  updatePolicy:
    updateMode: "Auto"  # or "Off", "Initial", "Recreate"
  resourcePolicy:
    containerPolicies:
    - containerName: nginx
      minAllowed:
        cpu: 100m
        memory: 50Mi
      maxAllowed:
        cpu: 1
        memory: 500Mi
      controlledResources: ["cpu", "memory"]
```

---

## EKS Storage

### EBS CSI Driver

**Install EBS CSI Driver:**
```bash
# Create IAM role
eksctl create iamserviceaccount \
  --name ebs-csi-controller-sa \
  --namespace kube-system \
  --cluster my-eks-cluster \
  --role-name AmazonEKS_EBS_CSI_DriverRole \
  --role-only \
  --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
  --approve

# Install EBS CSI driver
helm repo add aws-ebs-csi-driver https://kubernetes-sigs.github.io/aws-ebs-csi-driver
helm install aws-ebs-csi-driver aws-ebs-csi-driver/aws-ebs-csi-driver \
  --namespace kube-system \
  --set controller.serviceAccount.create=false \
  --set controller.serviceAccount.name=ebs-csi-controller-sa
```

**StorageClass:**
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-sc
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
  kmsKeyId: "arn:aws:kms:us-east-1:123456789012:key/abc-123"

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ebs-claim
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: ebs-sc
  resources:
    requests:
      storage: 10Gi

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-with-storage
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:1.0
        volumeMounts:
        - name: persistent-storage
          mountPath: /data
      volumes:
      - name: persistent-storage
        persistentVolumeClaim:
          claimName: ebs-claim
```

### EFS CSI Driver

**Install EFS CSI Driver:**
```bash
# Create EFS filesystem
aws efs create-file-system \
  --region us-east-1 \
  --performance-mode generalPurpose \
  --throughput-mode bursting \
  --encrypted \
  --tags Key=Name,Value=eks-efs

# Create mount targets in each subnet
aws efs create-mount-target \
  --file-system-id fs-12345678 \
  --subnet-id subnet-111 \
  --security-groups sg-12345

# Install EFS CSI driver
helm repo add aws-efs-csi-driver https://kubernetes-sigs.github.io/aws-efs-csi-driver/
helm install aws-efs-csi-driver aws-efs-csi-driver/aws-efs-csi-driver \
  --namespace kube-system
```

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: efs-sc
provisioner: efs.csi.aws.com
parameters:
  provisioningMode: efs-ap
  fileSystemId: fs-12345678
  directoryPerms: "700"

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: efs-claim
spec:
  accessModes:
    - ReadWriteMany  # Multiple pods can mount
  storageClassName: efs-sc
  resources:
    requests:
      storage: 5Gi
```

---

## EKS Networking

### AWS Load Balancer Controller

**Install AWS Load Balancer Controller:**
```bash
# Create IAM policy
curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json

aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json

# Create service account
eksctl create iamserviceaccount \
  --cluster=my-eks-cluster \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --attach-policy-arn=arn:aws:iam::123456789012:policy/AWSLoadBalancerControllerIAMPolicy \
  --override-existing-serviceaccounts \
  --approve

# Install controller
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  --set clusterName=my-eks-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  -n kube-system
```

**Ingress (ALB):**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:123456789012:certificate/abc-123
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
    alb.ingress.kubernetes.io/ssl-redirect: '443'
    alb.ingress.kubernetes.io/healthcheck-path: /health
    alb.ingress.kubernetes.io/healthcheck-interval-seconds: '30'
    alb.ingress.kubernetes.io/healthcheck-timeout-seconds: '5'
    alb.ingress.kubernetes.io/success-codes: '200'
    alb.ingress.kubernetes.io/target-group-attributes: deregistration_delay.timeout_seconds=30
spec:
  ingressClassName: alb
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

### VPC CNI Plugin

**Custom Networking:**
```yaml
apiVersion: crd.k8s.amazonaws.com/v1alpha1
kind: ENIConfig
metadata:
  name: us-east-1a
spec:
  subnet: subnet-111
  securityGroups:
  - sg-12345

---
apiVersion: crd.k8s.amazonaws.com/v1alpha1
kind: ENIConfig
metadata:
  name: us-east-1b
spec:
  subnet: subnet-222
  securityGroups:
  - sg-12345
```

**Enable Custom Networking:**
```bash
kubectl set env daemonset aws-node \
  -n kube-system \
  AWS_VPC_K8S_CNI_CUSTOM_NETWORK_CFG=true

kubectl set env daemonset aws-node \
  -n kube-system \
  ENI_CONFIG_LABEL_DEF=topology.kubernetes.io/zone
```

---

## EKS Security

### Pod Security Standards

**Pod Security Policy (Deprecated) → Pod Security Admission:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: restricted-ns
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
  - to:  # Allow DNS
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

### IRSA (IAM Roles for Service Accounts)

**Benefits:**
- No need for instance roles
- Fine-grained permissions per pod
- Automatic credential rotation

**Setup IRSA:**
```bash
# Create IAM policy
cat > s3-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name S3AccessPolicy \
  --policy-document file://s3-policy.json

# Create service account with IRSA
eksctl create iamserviceaccount \
  --name s3-access-sa \
  --namespace default \
  --cluster my-eks-cluster \
  --attach-policy-arn arn:aws:iam::123456789012:policy/S3AccessPolicy \
  --approve
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-with-s3
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      serviceAccountName: s3-access-sa  # Use IRSA
      containers:
      - name: app
        image: myapp:1.0
        env:
        - name: AWS_REGION
          value: us-east-1
```

---

## EKS Cost Optimization

### Cost Breakdown

**Sample 10-node EKS Cluster:**
```
Control Plane:                $73/month
10 × t3.medium nodes:         $300/month
EBS volumes (500 GB):         $50/month
ELB (2 load balancers):       $32/month
Data transfer:                $20/month
---------------------------------------
Total:                        $475/month
```

### Cost Optimization Strategies

**1. Use Spot Instances (70% savings):**
```bash
# Create Spot node group
eksctl create nodegroup \
  --cluster my-eks-cluster \
  --name spot-ng \
  --node-type t3.medium \
  --nodes 5 \
  --nodes-min 2 \
  --nodes-max 10 \
  --spot
```

**2. Use Fargate for Low-Utilization Workloads:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: fargate-pod
  namespace: fargate-ns
spec:
  containers:
  - name: app
    image: myapp:1.0
# Automatically runs on Fargate if namespace matches Fargate profile
```

**3. Right-Size Pods with VPA**

**4. Use Cluster Autoscaler**

**5. Reserved Instances for Baseline:**
```
Baseline: 3 × t3.medium Reserved (40% off) = $180/month
Variable: Spot instances for additional capacity
```

**Optimized Cost:**
```
Control Plane:                $73/month
3 × t3.medium (Reserved):     $180/month (40% off)
7 × t3.medium (Spot):         $63/month (70% off)
Storage:                      $40/month (gp3)
ELB:                          $32/month
Data transfer:                $15/month
---------------------------------------
Total:                        $403/month (15% savings)
```

---

## Summary

**Key Takeaways:**
- ECS is AWS-native, simpler to use, no control plane cost
- EKS provides standard Kubernetes with extensive ecosystem
- Fargate removes server management for both ECS and EKS
- Use Capacity Providers for ECS cost optimization
- EKS supports Managed Node Groups, Spot instances, and Fargate
- Kubernetes provides powerful primitives: Pods, Deployments, Services
- HPA for horizontal scaling, VPA for vertical scaling, Cluster Autoscaler for nodes
- EBS CSI for block storage, EFS CSI for shared storage
- AWS Load Balancer Controller for Ingress (ALB/NLB)
- IRSA for fine-grained IAM permissions per pod
- Network Policies for pod-to-pod security
- App Mesh for service mesh capabilities
- Spot instances provide 70% cost savings
- Choose ECS for simplicity, EKS for Kubernetes features

**Next Chapter:** [17-api-gateway.md](./17-api-gateway.md) - API Management