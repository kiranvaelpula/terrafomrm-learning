# Module 07: ConfigMaps & Secrets

## 📚 What You'll Learn
- What are ConfigMaps and Secrets
- Creating and using ConfigMaps
- Managing Secrets securely
- Environment variables vs Volume mounts
- Best practices for configuration management

---

## 🎯 Why ConfigMaps and Secrets?

**Problem:** Hardcoding configuration in container images

```dockerfile
# ❌ Bad - Hardcoded in Dockerfile
ENV DATABASE_URL="postgres://prod-db:5432"
ENV API_KEY="secret-key-123"
```

**Solution:** Externalize configuration

```yaml
# ✅ Good - External configuration
env:
- name: DATABASE_URL
  valueFrom:
    configMapKeyRef:
      name: app-config
      key: database-url
```

---

## 📋 ConfigMaps

**ConfigMaps** store non-sensitive configuration data as key-value pairs.

### Creating ConfigMaps

#### Method 1: From Literal Values

```bash
kubectl create configmap app-config \
  --from-literal=database-url=postgres://db:5432 \
  --from-literal=log-level=info \
  --from-literal=max-connections=100
```

#### Method 2: From File

```bash
# app.properties
database-url=postgres://db:5432
log-level=info
max-connections=100

# Create ConfigMap from file
kubectl create configmap app-config --from-file=app.properties
```

#### Method 3: From Env File

```bash
# config.env
DATABASE_URL=postgres://db:5432
LOG_LEVEL=info
MAX_CONNECTIONS=100

kubectl create configmap app-config --from-env-file=config.env
```

#### Method 4: YAML Definition

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database-url: "postgres://db:5432"
  log-level: "info"
  max-connections: "100"
  # Multi-line values
  app.properties: |
    database-url=postgres://db:5432
    log-level=info
    max-connections=100
```

---

## 🎪 Lab 1: Using ConfigMaps

### Step 1: Create ConfigMap

```yaml
# config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-config
data:
  # Simple key-value
  environment: "production"
  log-level: "info"
  api-endpoint: "https://api.example.com"
  
  # Configuration file
  nginx.conf: |
    server {
        listen 80;
        server_name _;
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
    }
```

```bash
kubectl apply -f config.yaml
kubectl get configmaps
kubectl describe configmap web-config
```

### Step 2: Use ConfigMap as Environment Variables

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: env-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'echo "Environment: $ENVIRONMENT" && echo "Log Level: $LOG_LEVEL" && sleep 3600']
    env:
    # Single variable
    - name: ENVIRONMENT
      valueFrom:
        configMapKeyRef:
          name: web-config
          key: environment
    # Another variable
    - name: LOG_LEVEL
      valueFrom:
        configMapKeyRef:
          name: web-config
          key: log-level
```

```bash
kubectl apply -f env-pod.yaml
kubectl logs env-pod
# Output:
# Environment: production
# Log Level: info
```

### Step 3: Load All Keys as Environment Variables

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: env-all-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'env | sort && sleep 3600']
    envFrom:
    - configMapRef:
        name: web-config
```

```bash
kubectl apply -f env-all-pod.yaml
kubectl logs env-all-pod | grep -E 'environment|log-level'
```

### Step 4: Mount as Volume

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: volume-pod
spec:
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: config-volume
      mountPath: /etc/nginx/conf.d
  volumes:
  - name: config-volume
    configMap:
      name: web-config
      items:
      - key: nginx.conf
        path: default.conf
```

```bash
kubectl apply -f volume-pod.yaml
kubectl exec volume-pod -- cat /etc/nginx/conf.d/default.conf
```

---

## 🔐 Secrets

**Secrets** store sensitive data (passwords, tokens, keys).

### Creating Secrets

#### Method 1: From Literal

```bash
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=SuperSecret123
```

#### Method 2: From Files

```bash
# Create files
echo -n 'admin' > username.txt
echo -n 'SuperSecret123' > password.txt

kubectl create secret generic db-secret \
  --from-file=username=username.txt \
  --from-file=password=password.txt

# Clean up files
rm username.txt password.txt
```

#### Method 3: YAML (Base64 Encoded)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=          # base64 encoded 'admin'
  password: U3VwZXJTZWNyZXQxMjM=  # base64 encoded 'SuperSecret123'
```

```bash
# Encode values
echo -n 'admin' | base64
# Output: YWRtaW4=

echo -n 'SuperSecret123' | base64
# Output: U3VwZXJTZWNyZXQxMjM=

# Decode
echo 'YWRtaW4=' | base64 --decode
# Output: admin
```

#### Method 4: YAML (Plain Text with stringData)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
stringData:  # Plain text (automatically encoded)
  username: admin
  password: SuperSecret123
```

---

## 🎪 Lab 2: Using Secrets

### Step 1: Create Secrets

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: database-credentials
type: Opaque
stringData:
  DB_USERNAME: admin
  DB_PASSWORD: SuperSecret123
  DB_HOST: postgres.default.svc.cluster.local
---
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
type: Opaque
stringData:
  stripe-key: sk_test_1234567890
  sendgrid-key: SG.1234567890abcdef
```

```bash
kubectl apply -f secrets.yaml
kubectl get secrets
```

### Step 2: Use Secret as Environment Variables

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-env-pod
spec:
  containers:
  - name: app
    image: postgres:14
    env:
    - name: POSTGRES_USER
      valueFrom:
        secretKeyRef:
          name: database-credentials
          key: DB_USERNAME
    - name: POSTGRES_PASSWORD
      valueFrom:
        secretKeyRef:
          name: database-credentials
          key: DB_PASSWORD
```

### Step 3: Load All Secret Keys

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-all-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'echo "User: $DB_USERNAME" && sleep 3600']
    envFrom:
    - secretRef:
        name: database-credentials
```

### Step 4: Mount Secret as Volume

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-volume-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'cat /etc/secrets/DB_USERNAME && sleep 3600']
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: database-credentials
```

```bash
kubectl apply -f secret-volume-pod.yaml
kubectl exec secret-volume-pod -- ls /etc/secrets
# Output:
# DB_HOST
# DB_PASSWORD
# DB_USERNAME

kubectl exec secret-volume-pod -- cat /etc/secrets/DB_USERNAME
# Output: admin
```

---

## 🔑 Secret Types

```yaml
# Generic/Opaque (default)
type: Opaque

# Docker registry credentials
type: kubernetes.io/dockerconfigjson

# TLS certificates
type: kubernetes.io/tls

# Service account token
type: kubernetes.io/service-account-token

# Basic auth
type: kubernetes.io/basic-auth

# SSH auth
type: kubernetes.io/ssh-auth
```

### Docker Registry Secret

```bash
kubectl create secret docker-registry docker-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=myuser \
  --docker-password=mypassword \
  --docker-email=myemail@example.com
```

```yaml
# Use in Pod
apiVersion: v1
kind: Pod
metadata:
  name: private-pod
spec:
  containers:
  - name: app
    image: myregistry.com/private-image:latest
  imagePullSecrets:
  - name: docker-secret
```

### TLS Secret

```bash
kubectl create secret tls tls-secret \
  --cert=path/to/tls.cert \
  --key=path/to/tls.key
```

---

## 🎪 Lab 3: Complete Application with Config

```yaml
# complete-app.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  environment: "production"
  log-level: "info"
  api-endpoint: "https://api.example.com"
  cache-ttl: "3600"
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  database-url: "postgres://db.example.com:5432/mydb"
  api-key: "sk_live_1234567890"
  jwt-secret: "super-secret-jwt-key"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: app
        image: myapp:1.0
        ports:
        - containerPort: 8080
        
        # Environment from ConfigMap
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: environment
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: log-level
        
        # Environment from Secret
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: api-key
        
        # Load all from ConfigMap
        envFrom:
        - configMapRef:
            name: app-config
            prefix: CONFIG_
        
        # Mount secrets as files
        volumeMounts:
        - name: secrets
          mountPath: /etc/secrets
          readOnly: true
      
      volumes:
      - name: secrets
        secret:
          secretName: app-secrets
```

---

## 🔄 Updating ConfigMaps and Secrets

### Environment Variables (Not Auto-Updated)

```bash
# Update ConfigMap
kubectl edit configmap app-config

# Pods need restart to see new values
kubectl rollout restart deployment web-app
```

### Volume Mounts (Auto-Updated)

```bash
# Update ConfigMap
kubectl edit configmap app-config

# Wait ~1 minute
# Files in mounted volumes automatically updated
# Application needs to reload config
```

---

## 🛡️ Security Best Practices

### 1. Never Commit Secrets to Git

```bash
# .gitignore
secrets.yaml
*.secret
.env
```

### 2. Use RBAC to Restrict Access

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]
  resourceNames: ["specific-secret"]  # Limit to specific secrets
```

### 3. Enable Encryption at Rest

```bash
# On control plane
kube-apiserver \
  --encryption-provider-config=/etc/kubernetes/encryption-config.yaml
```

### 4. Use External Secret Managers

- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Google Secret Manager

### 5. Rotate Secrets Regularly

```bash
# Update secret
kubectl create secret generic db-secret \
  --from-literal=password=NewPassword456 \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods
kubectl rollout restart deployment myapp
```

---

## 📊 ConfigMap vs Secret Comparison

| Feature | ConfigMap | Secret |
|---------|-----------|--------|
| Purpose | Non-sensitive config | Sensitive data |
| Storage | Plain text | Base64 encoded |
| Size limit | 1MB | 1MB |
| Encryption | No | Optional |
| Use cases | App settings | Passwords, tokens |

---

## 🐛 Troubleshooting

### Issue 1: ConfigMap Not Found

```bash
# Check if exists
kubectl get configmap app-config

# Describe
kubectl describe configmap app-config

# Check namespace
kubectl get configmap app-config -n <namespace>
```

### Issue 2: Secret Not Mounting

```bash
# Check secret exists
kubectl get secret app-secrets

# Check pod events
kubectl describe pod <pod-name>

# Check if mounted
kubectl exec <pod-name> -- ls /etc/secrets
```

### Issue 3: Environment Variables Not Set

```bash
# Check pod environment
kubectl exec <pod-name> -- env

# Check if ConfigMap/Secret exists
kubectl get configmap,secret

# Restart pod
kubectl delete pod <pod-name>
```

---

## 📝 Quick Reference

```bash
# ConfigMaps
kubectl create configmap <name> --from-literal=key=value
kubectl create configmap <name> --from-file=file.txt
kubectl get configmaps
kubectl describe configmap <name>
kubectl edit configmap <name>
kubectl delete configmap <name>

# Secrets
kubectl create secret generic <name> --from-literal=key=value
kubectl create secret generic <name> --from-file=file.txt
kubectl get secrets
kubectl describe secret <name>
kubectl get secret <name> -o yaml
kubectl delete secret <name>

# View secret values
kubectl get secret <name> -o jsonpath='{.data.key}' | base64 --decode
```

---

## 📝 Quiz

1. What's the difference between ConfigMap and Secret?
2. Are Secrets encrypted by default?
3. How do you update environment variables from ConfigMap?
4. What happens when you update a ConfigMap mounted as volume?
5. What's the size limit for ConfigMaps and Secrets?
6. How do you create a Secret from a file?
7. What are the different Secret types?

---

## 🎓 Challenge Exercise

1. Create a ConfigMap with app configuration
2. Create a Secret with database credentials
3. Create a Deployment that uses both
4. Use ConfigMap as environment variables
5. Mount Secret as volume
6. Update ConfigMap and trigger pod restart
7. Create a TLS Secret
8. Create a Docker registry Secret

**Bonus:**
- Set up automatic secret rotation
- Integrate with external secret manager
- Implement RBAC for secrets

---

## ⏭️ Next Steps

Ready for intermediate topics? Continue to [Module 08: Volumes & Storage](../02-intermediate/08-volumes-storage.md)

---

**🎉 Congratulations!** You've completed the Kubernetes Basics! You now understand configuration management with ConfigMaps and Secrets!
