# Module 22: Multi-Cluster Management

## 📚 What You'll Learn
- Multi-cluster architecture patterns
- Federation and cluster federation
- Cross-cluster service discovery
- Multi-cluster load balancing
- Disaster recovery strategies
- Tools for multi-cluster management

---

## 🎯 Why Multi-Cluster?

### Single Cluster Limitations
```
Single Cluster:
├── ❌ Single point of failure
├── ❌ Limited by single region
├── ❌ Resource capacity limits
├── ❌ Blast radius of failures
└── ❌ Compliance constraints
```

### Multi-Cluster Benefits
```
Multiple Clusters:
├── ✅ High availability across regions
├── ✅ Disaster recovery capabilities
├── ✅ Better compliance (data locality)
├── ✅ Resource isolation
├── ✅ Independent scaling
└── ✅ Reduced blast radius
```

---

## 🏗️ Multi-Cluster Patterns

### 1. Active-Passive (DR)
```
Primary Cluster (Active)     Backup Cluster (Passive)
┌─────────────────┐         ┌─────────────────┐
│   Production    │         │   Standby       │
│   Traffic       │ ──────> │   Ready to      │
│   100%          │ Sync    │   Takeover      │
└─────────────────┘         └─────────────────┘
     US-East                     US-West
```

### 2. Active-Active (Multi-Region)
```
Cluster 1 (Active)          Cluster 2 (Active)
┌─────────────────┐         ┌─────────────────┐
│   Production    │         │   Production    │
│   Traffic 50%   │ <────> │   Traffic 50%   │
│   Users: US     │  Sync  │   Users: EU     │
└─────────────────┘         └─────────────────┘
     US-East                     EU-West
```

### 3. Hub-Spoke (Central Management)
```
        Management Cluster (Hub)
              ┌───────┐
              │ ArgoCD│
              │ Config│
              └───┬───┘
        ┌─────────┼─────────┐
        ↓         ↓         ↓
    Cluster A  Cluster B  Cluster C
    (Dev)      (Staging)  (Prod)
```

### 4. Federation (Unified)
```
        Federation Control Plane
              ┌───────┐
              │ KubeFed│
              └───┬───┘
        ┌─────────┼─────────┐
        ↓         ↓         ↓
    Cluster A  Cluster B  Cluster C
    (Replicas: (Replicas: (Replicas:
      3)          3)          3)
```

---

## 🎪 Lab 1: Setup Multiple Clusters

### Step 1: Create Multiple Clusters (Local)

```bash
# Install kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Create first cluster
cat <<EOF | kind create cluster --name cluster1 --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
EOF

# Create second cluster
cat <<EOF | kind create cluster --name cluster2 --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
EOF

# Verify clusters
kind get clusters
kubectl config get-contexts
```

### Step 2: Configure kubectl Contexts

```bash
# List contexts
kubectl config get-contexts

# Rename contexts for clarity
kubectl config rename-context kind-cluster1 cluster1
kubectl config rename-context kind-cluster2 cluster2

# Switch between clusters
kubectl config use-context cluster1
kubectl get nodes

kubectl config use-context cluster2
kubectl get nodes

# View current context
kubectl config current-context
```

### Step 3: Deploy to Multiple Clusters

```yaml
# app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-world
  labels:
    app: hello
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      labels:
        app: hello
    spec:
      containers:
      - name: hello
        image: nginxdemos/hello
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: hello-service
spec:
  selector:
    app: hello
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

```bash
# Deploy to cluster1
kubectl --context cluster1 apply -f app-deployment.yaml

# Deploy to cluster2
kubectl --context cluster2 apply -f app-deployment.yaml

# Verify in both clusters
kubectl --context cluster1 get pods,svc
kubectl --context cluster2 get pods,svc
```

---

## 🔧 kubectx and kubens Tools

### Installation

```bash
# macOS
brew install kubectx

# Linux
sudo git clone https://github.com/ahmetb/kubectx /opt/kubectx
sudo ln -s /opt/kubectx/kubectx /usr/local/bin/kubectx
sudo ln -s /opt/kubectx/kubens /usr/local/bin/kubens

# Windows (via Chocolatey)
choco install kubectx
```

### Usage

```bash
# List contexts
kubectx

# Switch context
kubectx cluster1
kubectx cluster2

# Switch back to previous
kubectx -

# List namespaces in current cluster
kubens

# Switch namespace
kubens production

# Switch back to previous namespace
kubens -
```

---

## 🎪 Lab 2: Cluster Federation with KubeFed

### Step 1: Install KubeFed

```bash
# Install KubeFed control plane in cluster1
kubectl config use-context cluster1

# Add KubeFed Helm repo
helm repo add kubefed-charts https://raw.githubusercontent.com/kubernetes-sigs/kubefed/master/charts
helm repo update

# Install KubeFed
kubectl create namespace kube-federation-system

helm install kubefed kubefed-charts/kubefed \
  --namespace kube-federation-system \
  --create-namespace

# Verify installation
kubectl get pods -n kube-federation-system
```

### Step 2: Register Clusters

```bash
# Join cluster1 (host cluster)
kubefedctl join cluster1 \
  --cluster-context cluster1 \
  --host-cluster-context cluster1 \
  --v=2

# Join cluster2 (member cluster)
kubefedctl join cluster2 \
  --cluster-context cluster2 \
  --host-cluster-context cluster1 \
  --v=2

# Verify clusters
kubectl get kubefedclusters -n kube-federation-system
```

### Step 3: Federate Resources

```yaml
# federated-deployment.yaml
apiVersion: types.kubefed.io/v1beta1
kind: FederatedDeployment
metadata:
  name: nginx-federated
  namespace: default
spec:
  template:
    metadata:
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
  placement:
    clusters:
    - name: cluster1
    - name: cluster2
  overrides:
  - clusterName: cluster1
    clusterOverrides:
    - path: "/spec/replicas"
      value: 5
  - clusterName: cluster2
    clusterOverrides:
    - path: "/spec/replicas"
      value: 3
```

```bash
# Apply federated deployment
kubectl apply -f federated-deployment.yaml

# Verify in cluster1
kubectl --context cluster1 get deployments

# Verify in cluster2
kubectl --context cluster2 get deployments
```

---

## 🌐 Multi-Cluster Service Mesh (Istio)

### Architecture
```
Cluster 1                    Cluster 2
┌─────────────────┐         ┌─────────────────┐
│ Istio Control   │         │ Istio Control   │
│ Plane           │ <────> │ Plane           │
│                 │  mTLS  │                 │
│ Service A       │ <────> │ Service B       │
└─────────────────┘         └─────────────────┘
```

### Setup Multi-Cluster Istio

```bash
# Install Istio on cluster1
kubectl config use-context cluster1
istioctl install --set profile=demo -y

# Install Istio on cluster2
kubectl config use-context cluster2
istioctl install --set profile=demo -y

# Enable multi-cluster mode
istioctl x create-remote-secret \
  --context=cluster1 \
  --name=cluster1 | \
  kubectl apply -f - --context=cluster2

istioctl x create-remote-secret \
  --context=cluster2 \
  --name=cluster2 | \
  kubectl apply -f - --context=cluster1
```

### Cross-Cluster Service

```yaml
# service-entry.yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-service
spec:
  hosts:
  - service.cluster2.global
  ports:
  - number: 80
    name: http
    protocol: HTTP
  resolution: DNS
  location: MESH_INTERNAL
  endpoints:
  - address: service.cluster2.svc.cluster.local
    ports:
      http: 80
    labels:
      cluster: cluster2
```

---

## 🎪 Lab 3: ArgoCD Multi-Cluster


### Step 1: Install ArgoCD

```bash
# In cluster1 (management cluster)
kubectl config use-context cluster1

# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s

# Get admin password
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
echo "ArgoCD Password: $ARGOCD_PASSWORD"

# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443 &
```

### Step 2: Register Remote Cluster

```bash
# Get cluster2 context
kubectl config use-context cluster2
kubectl config view --minify --flatten > cluster2-config.yaml

# Switch to cluster1
kubectl config use-context cluster1

# Install ArgoCD CLI
brew install argocd  # macOS
# or download from https://github.com/argoproj/argo-cd/releases

# Login to ArgoCD
argocd login localhost:8080 --username admin --password $ARGOCD_PASSWORD --insecure

# Add cluster2 to ArgoCD
argocd cluster add cluster2 --name cluster2

# List clusters
argocd cluster list
```

### Step 3: Deploy Application to Remote Cluster

```yaml
# multi-cluster-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: app-cluster2
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/argoproj/argocd-example-apps
    targetRevision: HEAD
    path: guestbook
  destination:
    server: https://cluster2-api-url  # cluster2 API server
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

```bash
# Apply to cluster1 (management cluster)
kubectl --context cluster1 apply -f multi-cluster-app.yaml

# ArgoCD will deploy to cluster2
argocd app get app-cluster2
argocd app sync app-cluster2

# Verify deployment in cluster2
kubectl --context cluster2 get all -n default
```

---

## 🔄 Cross-Cluster Communication

### 1. DNS-Based Discovery

```yaml
# external-name-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: remote-service
  namespace: default
spec:
  type: ExternalName
  externalName: service.cluster2.example.com
  ports:
  - port: 80
```

### 2. Submariner for Service Discovery

```bash
# Install Submariner broker on cluster1
subctl deploy-broker --kubeconfig cluster1-config.yaml

# Join cluster1
subctl join --kubeconfig cluster1-config.yaml broker-info.subm

# Join cluster2
subctl join --kubeconfig cluster2-config.yaml broker-info.subm

# Verify connectivity
subctl show all
```

### 3. Service Export/Import

```yaml
# In cluster1 - Export service
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ServiceExport
metadata:
  name: my-service
  namespace: default

---
# In cluster2 - Import service
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ServiceImport
metadata:
  name: my-service
  namespace: default
spec:
  type: ClusterSetIP
  ports:
  - port: 80
    protocol: TCP
```

---

## 🎪 Lab 4: Multi-Cluster Monitoring

### Deploy Prometheus Federation

```yaml
# prometheus-federation.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      
    scrape_configs:
    - job_name: 'federate-cluster1'
      scrape_interval: 15s
      honor_labels: true
      metrics_path: '/federate'
      params:
        'match[]':
        - '{job="kubernetes-apiservers"}'
        - '{job="kubernetes-nodes"}'
        - '{job="kubernetes-pods"}'
      static_configs:
      - targets:
        - 'prometheus-cluster1.monitoring.svc:9090'
        
    - job_name: 'federate-cluster2'
      scrape_interval: 15s
      honor_labels: true
      metrics_path: '/federate'
      params:
        'match[]':
        - '{job="kubernetes-apiservers"}'
        - '{job="kubernetes-nodes"}'
        - '{job="kubernetes-pods"}'
      static_configs:
      - targets:
        - 'prometheus-cluster2.monitoring.svc:9090'
```

### Grafana Multi-Cluster Dashboard

```yaml
# grafana-datasources.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
  namespace: monitoring
data:
  datasources.yaml: |
    apiVersion: 1
    datasources:
    - name: Cluster1-Prometheus
      type: prometheus
      access: proxy
      url: http://prometheus-cluster1.monitoring.svc:9090
      isDefault: true
      
    - name: Cluster2-Prometheus
      type: prometheus
      access: proxy
      url: http://prometheus-cluster2.monitoring.svc:9090
```

---

## 🛡️ Multi-Cluster Security

### 1. Certificate Management

```yaml
# cert-manager for multiple clusters
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - dns01:
        cloudDNS:
          project: my-project
          serviceAccountSecretRef:
            name: clouddns-sa
            key: key.json
```

### 2. Secret Replication

```yaml
# external-secrets for multi-cluster
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "external-secrets"
```

### 3. Network Policies Across Clusters

```yaml
# allow-cross-cluster.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-cross-cluster
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Ingress
  ingress:
  - from:
    - ipBlock:
        cidr: 10.0.0.0/8  # Cluster2 CIDR
    ports:
    - protocol: TCP
      port: 80
```

---

## 🎪 Lab 5: Disaster Recovery Scenario

### Setup Active-Passive DR

```bash
# Step 1: Deploy to primary (cluster1)
kubectl --context cluster1 apply -f app-deployment.yaml

# Step 2: Setup Velero for backups
kubectl --context cluster1 create namespace velero

helm install velero vmware-tanzu/velero \
  --namespace velero \
  --set configuration.provider=aws \
  --set configuration.backupStorageLocation.bucket=my-backup-bucket \
  --set configuration.backupStorageLocation.config.region=us-east-1 \
  --set snapshotsEnabled=false

# Step 3: Create backup
velero backup create full-backup --include-namespaces=default,production

# Step 4: Simulate disaster (cluster1 fails)
echo "Cluster1 is down! Switching to cluster2..."

# Step 5: Restore to secondary (cluster2)
kubectl --context cluster2 create namespace velero

helm install velero vmware-tanzu/velero \
  --namespace velero \
  --set configuration.provider=aws \
  --set configuration.backupStorageLocation.bucket=my-backup-bucket \
  --set configuration.backupStorageLocation.config.region=us-west-2 \
  --set snapshotsEnabled=false

# Restore from backup
velero restore create --from-backup full-backup

# Step 6: Verify restoration
kubectl --context cluster2 get all -n default
kubectl --context cluster2 get all -n production
```

### Automated Failover Script

```bash
#!/bin/bash
# dr-failover.sh

PRIMARY_CONTEXT="cluster1"
SECONDARY_CONTEXT="cluster2"
HEALTH_CHECK_URL="http://app.cluster1.example.com/health"

# Check primary cluster health
if ! curl -f -s "$HEALTH_CHECK_URL" > /dev/null; then
    echo "Primary cluster unhealthy! Initiating failover..."
    
    # Update DNS to point to secondary
    aws route53 change-resource-record-sets \
        --hosted-zone-id Z1234567890 \
        --change-batch '{
            "Changes": [{
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": "app.example.com",
                    "Type": "A",
                    "TTL": 60,
                    "ResourceRecords": [{"Value": "secondary-cluster-ip"}]
                }
            }]
        }'
    
    echo "Failover complete! Traffic now routed to secondary cluster."
else
    echo "Primary cluster healthy."
fi
```

---

## 📊 Multi-Cluster Management Tools

### 1. Rancher

```bash
# Install Rancher
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable

kubectl create namespace cattle-system

helm install rancher rancher-stable/rancher \
  --namespace cattle-system \
  --set hostname=rancher.example.com \
  --set replicas=3

# Import clusters via Rancher UI
# Dashboard provides unified view of all clusters
```

### 2. Google Anthos

```bash
# Register clusters with Anthos
gcloud container hub memberships register cluster1 \
  --context=cluster1 \
  --service-account-key-file=./service-account.json

gcloud container hub memberships register cluster2 \
  --context=cluster2 \
  --service-account-key-file=./service-account.json

# View registered clusters
gcloud container hub memberships list
```

### 3. Azure Arc

```bash
# Connect clusters to Azure Arc
az connectedk8s connect \
  --name cluster1 \
  --resource-group my-rg \
  --kube-context cluster1

az connectedk8s connect \
  --name cluster2 \
  --resource-group my-rg \
  --kube-context cluster2

# View connected clusters
az connectedk8s list --resource-group my-rg
```

---

## 💡 Best Practices

### 1. Cluster Naming Convention

```bash
# Environment-Region-Purpose
prod-us-east-web
prod-eu-west-web
staging-us-east-web
dev-local-test
```

### 2. Resource Placement Strategy

```yaml
# Use labels for intelligent placement
apiVersion: v1
kind: Pod
metadata:
  labels:
    topology.kubernetes.io/region: us-east-1
    topology.kubernetes.io/zone: us-east-1a
    environment: production
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: topology.kubernetes.io/region
            operator: In
            values:
            - us-east-1
```

### 3. Unified Configuration Management

```yaml
# Use ConfigMaps synced across clusters
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  annotations:
    sync-to-clusters: "cluster1,cluster2,cluster3"
data:
  api-endpoint: https://api.example.com
  feature-flags: '{"newUI": true, "beta": false}'
```

### 4. Health Monitoring

```yaml
# Deploy health monitors in each cluster
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-health-monitor
spec:
  replicas: 1
  selector:
    matchLabels:
      app: health-monitor
  template:
    metadata:
      labels:
        app: health-monitor
    spec:
      containers:
      - name: monitor
        image: monitoring/cluster-health:latest
        env:
        - name: CLUSTER_NAME
          value: "cluster1"
        - name: ALERT_WEBHOOK
          value: "https://alerts.example.com/webhook"
```

---

## 🐛 Troubleshooting Multi-Cluster

### Issue 1: Cross-Cluster Communication Fails

```bash
# Check network connectivity
kubectl --context cluster1 run test-pod --image=busybox --rm -it -- sh
# Inside pod
nslookup service.cluster2.global
ping service-ip

# Check service mesh configuration
istioctl proxy-config listeners pod-name -n namespace
istioctl proxy-config routes pod-name -n namespace

# Verify certificates
kubectl --context cluster1 get secrets -n istio-system
kubectl --context cluster2 get secrets -n istio-system
```

### Issue 2: Federated Resources Not Syncing

```bash
# Check KubeFed status
kubectl get kubefedclusters -n kube-federation-system
kubectl describe kubefedcluster cluster2 -n kube-federation-system

# Check federated resource status
kubectl get federateddeployment nginx-federated -o yaml

# View sync status
kubectl get federatedobjects -n default
```

### Issue 3: Context Confusion

```bash
# Always verify current context
kubectl config current-context

# Use --context flag explicitly
kubectl --context cluster1 get pods
kubectl --context cluster2 get pods

# Create aliases
alias k1='kubectl --context cluster1'
alias k2='kubectl --context cluster2'

k1 get pods
k2 get pods
```

---

## 📝 Quick Reference

```bash
# Context Management
kubectl config get-contexts
kubectl config use-context <name>
kubectl config current-context
kubectx  # List contexts
kubectx <name>  # Switch context

# Multi-Cluster Deployment
kubectl --context cluster1 apply -f deployment.yaml
kubectl --context cluster2 apply -f deployment.yaml

# Cross-Cluster Commands
for ctx in cluster1 cluster2 cluster3; do
  kubectl --context $ctx get pods -A
done

# Federation
kubefedctl join <cluster> --host-cluster-context <host>
kubectl get kubefedclusters -n kube-federation-system

# ArgoCD Multi-Cluster
argocd cluster add <context>
argocd cluster list
argocd app create --dest-server <cluster-url>
```

---

## 📝 Quiz

### Questions:
1. What are the main benefits of multi-cluster architecture?
2. Explain the difference between Active-Passive and Active-Active patterns.
3. How does KubeFed distribute workloads across clusters?
4. What is the purpose of Submariner in multi-cluster setups?
5. How would you implement disaster recovery with multiple clusters?
6. What tools can help manage multiple Kubernetes clusters?
7. Explain the Hub-Spoke pattern for multi-cluster management.

### Answers:
1. High availability, disaster recovery, compliance, resource isolation, reduced blast radius
2. Active-Passive: One cluster serves traffic, backup is standby. Active-Active: Both clusters serve traffic simultaneously
3. Uses FederatedDeployment resources to replicate and manage deployments across member clusters
4. Enables direct network connectivity and service discovery between clusters
5. Regular backups with Velero, automated health checks, DNS failover, restore procedures
6. Rancher, ArgoCD, KubeFed, Google Anthos, Azure Arc, AWS EKS Anywhere
7. Central management cluster (hub) controls and deploys to multiple workload clusters (spokes)

---

## 🎓 Challenge Exercise

### Project: Build Multi-Region Application

**Requirements:**
1. Create 3 clusters (us-east, us-west, eu-west)
2. Deploy a web application to all clusters
3. Configure ArgoCD for GitOps deployment
4. Set up cross-cluster service discovery
5. Implement monitoring across all clusters
6. Create disaster recovery plan
7. Test failover scenario

**Bonus:**
- Add Istio for service mesh
- Implement canary deployments across clusters
- Create unified logging dashboard
- Set up automated backups with Velero

---

## 💡 Key Takeaways

✅ Multi-cluster provides high availability and disaster recovery
✅ Different patterns serve different use cases (DR, multi-region, federation)
✅ Tools like ArgoCD, KubeFed simplify multi-cluster management
✅ Cross-cluster communication requires service mesh or Submariner
✅ Always verify context before running kubectl commands
✅ Implement automated health checks and failover procedures
✅ Use unified monitoring and logging across all clusters

---

## ⏭️ Next Steps

Ready to secure your clusters? Continue to [Module 23: Security Best Practices](./23-security-best-practices.md)

---

## 📚 Additional Resources

- [KubeFed Documentation](https://github.com/kubernetes-sigs/kubefed)
- [Submariner](https://submariner.io/)
- [ArgoCD Multi-Cluster](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/#clusters)
- [Istio Multi-Cluster](https://istio.io/latest/docs/setup/install/multicluster/)
- [Rancher](https://rancher.com/)

---

**🎉 Congratulations!** You now understand multi-cluster Kubernetes architecture and can deploy applications across multiple clusters!
