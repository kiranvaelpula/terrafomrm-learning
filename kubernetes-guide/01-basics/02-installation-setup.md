# Module 02: Installation & Setup

## 📚 What You'll Learn
- Installing kubectl (Kubernetes CLI)
- Setting up local Kubernetes (Minikube, Kind, Docker Desktop)
- Connecting to cloud Kubernetes (EKS, AKS, GKE)
- Verifying your installation
- Essential kubectl commands

---

## 🎯 Installation Options

### Local Development:
1. **Minikube** - Full-featured, recommended for learning
2. **Kind** - Kubernetes in Docker, lightweight
3. **Docker Desktop** - Built-in, easiest for Windows/Mac
4. **K3s** - Lightweight Kubernetes

### Cloud Platforms:
1. **AWS EKS** - Amazon Elastic Kubernetes Service
2. **Azure AKS** - Azure Kubernetes Service
3. **Google GKE** - Google Kubernetes Engine

---

## 📦 Step 1: Install kubectl

kubectl is the command-line tool to interact with Kubernetes.

### macOS

```bash
# Using Homebrew (Recommended)
brew install kubectl

# Verify installation
kubectl version --client
```

### Windows

```powershell
# Using Chocolatey
choco install kubernetes-cli

# Or using Scoop
scoop install kubectl

# Verify installation
kubectl version --client
```

### Linux

```bash
# Download latest version
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Make it executable
chmod +x kubectl

# Move to PATH
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client
```

### Verify kubectl

```bash
kubectl version --client

# Output should show:
# Client Version: v1.28.x
```

---

## 🚀 Step 2: Choose Your Kubernetes Environment

---

## Option A: Minikube (Recommended for Learning)

### Why Minikube?
- ✅ Full Kubernetes features
- ✅ Easy to use
- ✅ Works on all platforms
- ✅ Great for learning

### Install Minikube

#### macOS
```bash
brew install minikube
```

#### Windows
```powershell
choco install minikube
```

#### Linux
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### Start Minikube

```bash
# Start with default settings
minikube start

# Or customize resources
minikube start --cpus=2 --memory=4096 --disk-size=20g

# Check status
minikube status

# Output:
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured
```

### Useful Minikube Commands

```bash
# Stop cluster
minikube stop

# Delete cluster
minikube delete

# SSH into node
minikube ssh

# Open dashboard
minikube dashboard

# Get cluster IP
minikube ip

# List addons
minikube addons list

# Enable addon
minikube addons enable metrics-server
minikube addons enable ingress
```

---

## Option B: Kind (Kubernetes in Docker)

### Why Kind?
- ✅ Very lightweight
- ✅ Fast startup
- ✅ Good for CI/CD
- ✅ Multiple clusters easy

### Install Kind

#### macOS
```bash
brew install kind
```

#### Windows
```powershell
choco install kind
```

#### Linux
```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

### Create Cluster

```bash
# Create default cluster
kind create cluster

# Create named cluster
kind create cluster --name my-cluster

# Create multi-node cluster
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
EOF

# List clusters
kind get clusters

# Delete cluster
kind delete cluster --name my-cluster
```

---

## Option C: Docker Desktop

### Why Docker Desktop?
- ✅ Easiest setup
- ✅ Built-in
- ✅ Good for Mac/Windows

### Enable Kubernetes

1. Open Docker Desktop
2. Go to Settings → Kubernetes
3. Check "Enable Kubernetes"
4. Click "Apply & Restart"
5. Wait for green indicator

### Verify

```bash
kubectl config get-contexts

# Should see:
# docker-desktop
```

---

## Option D: Cloud Kubernetes

### AWS EKS

```bash
# Install eksctl
brew install eksctl  # macOS
choco install eksctl # Windows

# Create cluster (takes ~15 minutes)
eksctl create cluster \
  --name my-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 2

# Configure kubectl
aws eks update-kubeconfig --name my-cluster --region us-east-1

# Verify
kubectl get nodes
```

### Azure AKS

```bash
# Install Azure CLI
brew install azure-cli  # macOS
choco install azure-cli # Windows

# Login
az login

# Create resource group
az group create --name myResourceGroup --location eastus

# Create cluster
az aks create \
  --resource-group myResourceGroup \
  --name myAKSCluster \
  --node-count 2 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group myResourceGroup --name myAKSCluster

# Verify
kubectl get nodes
```

### Google GKE

```bash
# Install gcloud CLI
brew install google-cloud-sdk  # macOS

# Login
gcloud auth login

# Set project
gcloud config set project PROJECT_ID

# Create cluster
gcloud container clusters create my-cluster \
  --num-nodes=2 \
  --zone=us-central1-a

# Get credentials
gcloud container clusters get-credentials my-cluster --zone=us-central1-a

# Verify
kubectl get nodes
```

---

## 🎪 Lab: Verify Your Installation

### Step 1: Check kubectl

```bash
# Check version
kubectl version

# Should see both client and server versions
```

### Step 2: Check Cluster

```bash
# Get cluster information
kubectl cluster-info

# Output should show:
# Kubernetes control plane is running at https://...
# CoreDNS is running at https://...
```

### Step 3: Check Nodes

```bash
# List nodes
kubectl get nodes

# Output:
# NAME       STATUS   ROLES           AGE   VERSION
# minikube   Ready    control-plane   5m    v1.28.3
```

### Step 4: Check Components

```bash
# Check all system pods
kubectl get pods -n kube-system

# Should see pods running:
# - kube-apiserver
# - kube-controller-manager
# - kube-scheduler
# - kube-proxy
# - coredns
# - etcd
```

### Step 5: Create Your First Pod

```bash
# Run nginx
kubectl run nginx --image=nginx

# Check pod
kubectl get pods

# Should see:
# NAME    READY   STATUS    RESTARTS   AGE
# nginx   1/1     Running   0          10s

# Delete pod
kubectl delete pod nginx
```

---

## 🔧 Essential kubectl Commands

### Context Management

```bash
# List contexts
kubectl config get-contexts

# Switch context
kubectl config use-context minikube

# Current context
kubectl config current-context

# View config
kubectl config view
```

### Resource Management

```bash
# Get resources
kubectl get pods
kubectl get deployments
kubectl get services
kubectl get nodes

# Get all resources
kubectl get all

# Get with more details
kubectl get pods -o wide

# Describe resource
kubectl describe pod <pod-name>

# Get resource as YAML
kubectl get pod <pod-name> -o yaml

# Get resource as JSON
kubectl get pod <pod-name> -o json
```

### Help Commands

```bash
# General help
kubectl help

# Command-specific help
kubectl get --help
kubectl create --help

# Explain resource
kubectl explain pod
kubectl explain pod.spec
kubectl explain pod.spec.containers
```

---

## 🛠️ Install Helpful Tools

### kubectx & kubens

Switch contexts and namespaces easily.

```bash
# Install
brew install kubectx  # macOS
choco install kubectx # Windows

# Switch context
kubectx minikube

# Switch namespace
kubens kube-system

# List contexts
kubectx

# List namespaces
kubens
```

### k9s

Terminal UI for Kubernetes.

```bash
# Install
brew install k9s  # macOS
choco install k9s # Windows

# Run
k9s
```

### Helm

Package manager for Kubernetes.

```bash
# Install
brew install helm  # macOS
choco install kubernetes-helm # Windows

# Verify
helm version
```

### kubectl Autocomplete

#### Bash
```bash
echo 'source <(kubectl completion bash)' >> ~/.bashrc
source ~/.bashrc
```

#### Zsh
```bash
echo 'source <(kubectl completion zsh)' >> ~/.zshrc
source ~/.zshrc
```

#### PowerShell
```powershell
kubectl completion powershell | Out-String | Invoke-Expression
```

---

## 📋 Configuration Files

### kubeconfig Location

```bash
# Default location
~/.kube/config

# View config
kubectl config view

# Use different config
kubectl --kubeconfig=/path/to/config get pods
```

### Example kubeconfig

```yaml
apiVersion: v1
kind: Config
clusters:
- cluster:
    server: https://192.168.49.2:8443
    certificate-authority: /path/to/ca.crt
  name: minikube
contexts:
- context:
    cluster: minikube
    user: minikube
  name: minikube
current-context: minikube
users:
- name: minikube
  user:
    client-certificate: /path/to/client.crt
    client-key: /path/to/client.key
```

---

## 🐛 Troubleshooting

### Issue: kubectl not found

```bash
# Check if kubectl is in PATH
which kubectl  # macOS/Linux
where kubectl  # Windows

# If not, add to PATH or reinstall
```

### Issue: Cannot connect to cluster

```bash
# Check cluster is running
minikube status  # for Minikube
docker ps        # for Kind/Docker Desktop

# Check kubeconfig
kubectl config view

# Try different context
kubectl config use-context docker-desktop
```

### Issue: Pods not starting

```bash
# Check pod status
kubectl get pods

# Describe pod
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check events
kubectl get events
```

### Issue: Minikube won't start

```bash
# Delete and recreate
minikube delete
minikube start

# Check Docker is running
docker ps

# Check system resources
# Ensure 2GB+ RAM available
```

---

## 📝 Quiz

1. What is kubectl?
2. What are three ways to run Kubernetes locally?
3. How do you check if your cluster is running?
4. What command lists all pods?
5. Where is the kubeconfig file stored?

### Answers:
1. Command-line tool to interact with Kubernetes
2. Minikube, Kind, Docker Desktop (or K3s, MicroK8s)
3. `kubectl cluster-info` or `kubectl get nodes`
4. `kubectl get pods`
5. `~/.kube/config`

---

## 🎓 Challenge Exercise

### Complete Setup Challenge

1. Install kubectl
2. Set up a local Kubernetes cluster (choose one: Minikube, Kind, or Docker Desktop)
3. Verify cluster is running
4. Create a pod running nginx
5. Access the nginx welcome page
6. Delete the pod
7. Install at least one helpful tool (k9s, kubectx, or Helm)

**Bonus:**
- Set up kubectl autocomplete
- Create a multi-node cluster with Kind
- Enable Minikube dashboard

---

## 💡 Best Practices

### ✅ Do:
- Use contexts to manage multiple clusters
- Enable kubectl autocomplete
- Install helpful tools (k9s, kubectx)
- Keep kubectl updated
- Use namespaces for organization

### ❌ Don't:
- Run production workloads on local clusters
- Share kubeconfig files
- Run everything as default namespace
- Forget to clean up resources

---

## ⏭️ Next Steps

Cluster is running? Great! Continue to [Module 03: Kubernetes Architecture](./03-kubernetes-architecture.md)

---

## 📚 Additional Resources

- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Kind Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [kubectl Book](https://kubectl.docs.kubernetes.io/)

---

**🎉 Congratulations!** You now have a working Kubernetes cluster and know the essential commands!
