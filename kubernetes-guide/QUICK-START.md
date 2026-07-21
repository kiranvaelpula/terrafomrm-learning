# Kubernetes Quick Start Guide

## 🚀 Get Started in 15 Minutes

This quick start gets you from zero to running your first application on Kubernetes.

---

## ✅ Prerequisites (5 minutes)

### 1. Install kubectl
```bash
# macOS
brew install kubectl

# Windows
choco install kubernetes-cli

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/
```

### 2. Install Minikube
```bash
# macOS
brew install minikube

# Windows
choco install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### 3. Start Cluster
```bash
minikube start
```

---

## 📦 Deploy Your First App (5 minutes)

### Step 1: Create Deployment
```bash
kubectl create deployment hello-k8s --image=nginx
```

### Step 2: Expose as Service
```bash
kubectl expose deployment hello-k8s --type=NodePort --port=80
```

### Step 3: Access Application
```bash
minikube service hello-k8s
```

**🎉 Your app is running on Kubernetes!**

---

## 🎯 Common Commands (5 minutes)

```bash
# View everything
kubectl get all

# View pods
kubectl get pods

# View services
kubectl get svc

# View deployments
kubectl get deployments

# Describe resource
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>

# Execute command
kubectl exec -it <pod-name> -- /bin/bash

# Delete resources
kubectl delete deployment hello-k8s
kubectl delete service hello-k8s

# Stop cluster
minikube stop
```

---

## 📚 Next Steps

### Beginner Path
1. [Module 01: What is Kubernetes?](./01-basics/01-what-is-kubernetes.md)
2. [Module 02: Installation & Setup](./01-basics/02-installation-setup.md)
3. [Module 03: Kubernetes Architecture](./01-basics/03-kubernetes-architecture.md)
4. [Module 04: Pods](./01-basics/04-pods.md)
5. [Module 05: Services & Networking](./01-basics/05-services-networking.md)

### Practice Projects
- Deploy a web application
- Create a multi-tier app (frontend + backend)
- Set up monitoring with Prometheus
- Implement CI/CD pipeline

### Certifications
- CKA (Certified Kubernetes Administrator)
- CKAD (Certified Kubernetes Application Developer)
- CKS (Certified Kubernetes Security Specialist)

---

## 🆘 Troubleshooting

### Cluster Won't Start
```bash
minikube delete
minikube start
```

### Pod Not Running
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Cannot Access Service
```bash
kubectl get svc
minikube service <service-name>
```

---

## 📖 Resources

- [Official Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Interactive Tutorial](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- [Complete Course](./README.md)

---

**Ready to learn more?** Start with [Module 01: What is Kubernetes?](./01-basics/01-what-is-kubernetes.md)
