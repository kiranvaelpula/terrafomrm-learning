# Module 23: Kubernetes Security Best Practices

## 📚 What You'll Learn
- Defense in depth strategies
- Pod Security Standards
- Network security and policies
- Secrets management
- RBAC advanced patterns
- Security scanning and auditing
- Compliance and hardening

---

## 🎯 Security Layers

### Defense in Depth
```
┌──────────────────────────────────────┐
│  1. Cluster Access (Authentication)  │
├──────────────────────────────────────┤
│  2. Authorization (RBAC)             │
├──────────────────────────────────────┤
│  3. Admission Control                │
├──────────────────────────────────────┤
│  4. Pod Security Standards           │
├──────────────────────────────────────┤
│  5. Network Policies                 │
├──────────────────────────────────────┤
│  6. Runtime Security                 │
├──────────────────────────────────────┤
│  7. Audit Logging                    │
└──────────────────────────────────────┘
```

---

## 🔐 Pod Security Standards

### Three Policy Levels

**1. Privileged** - Unrestricted (for system pods)
**2. Baseline** - Minimally restrictive (prevents known privilege escalations)
**3. Restricted** - Heavily restricted (follows hardening best practices)

### Enable Pod Security

```yaml
# namespace-with-security.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: secure-namespace
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```


### Restricted Pod Example

```yaml
# secure-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
  namespace: secure-namespace
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: nginx:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      runAsUser: 1000
      capabilities:
        drop:
        - ALL
    volumeMounts:
    - name: cache
      mountPath: /var/cache/nginx
    - name: run
      mountPath: /var/run
  volumes:
  - name: cache
    emptyDir: {}
  - name: run
    emptyDir: {}
```

---

## 🎪 Lab 1: Implement Pod Security Standards

### Step 1: Create Secure Namespace

```bash
# Create namespace with restricted policy
kubectl create namespace production

kubectl label namespace production \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted

# Verify labels
kubectl get namespace production --show-labels
```

### Step 2: Try Insecure Pod (Should Fail)

```yaml
# insecure-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: insecure-pod
  namespace: production
spec:
  containers:
  - name: nginx
    image: nginx
    securityContext:
      privileged: true  # Not allowed in restricted mode
```

```bash
# This should be rejected
kubectl apply -f insecure-pod.yaml
# Error: pods "insecure-pod" is forbidden: violates PodSecurity "restricted:latest"
```

### Step 3: Deploy Secure Pod

```yaml
# secure-web-app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-web
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: secure-web
  template:
    metadata:
      labels:
        app: secure-web
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: nginx
        image: nginxinc/nginx-unprivileged:latest
        ports:
        - containerPort: 8080
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: cache
          mountPath: /var/cache/nginx
        - name: run
          mountPath: /var/run
      volumes:
      - name: cache
        emptyDir: {}
      - name: run
        emptyDir: {}
```

```bash
kubectl apply -f secure-web-app.yaml
kubectl get pods -n production
```

---

## 🔒 Secrets Management

### ❌ Bad Practice

```yaml
# DON'T: Hardcoded secrets
apiVersion: v1
kind: Pod
metadata:
  name: bad-practice
spec:
  containers:
  - name: app
    image: myapp
    env:
    - name: DB_PASSWORD
      value: "hardcoded-password-123"  # NEVER DO THIS
```

### ✅ Good Practice: Kubernetes Secrets

```yaml
# db-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
  namespace: production
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded
  password: c3VwZXJzZWNyZXQ=  # base64 encoded
```

```bash
# Create secret from literals
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password=supersecret \
  -n production

# Use in pod
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  containers:
  - name: app
    image: myapp
    envFrom:
    - secretRef:
        name: db-credentials
```

### ✅ Better: External Secrets Operator

```yaml
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-system --create-namespace

# SecretStore pointing to AWS Secrets Manager
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets
  namespace: production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa

---
# ExternalSecret syncs from AWS
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets
    kind: SecretStore
  target:
    name: db-credentials
    creationPolicy: Owner
  data:
  - secretKey: username
    remoteRef:
      key: prod/db/credentials
      property: username
  - secretKey: password
    remoteRef:
      key: prod/db/credentials
      property: password
```

### ✅ Best: HashiCorp Vault Integration

```yaml
# Install Vault injector
helm repo add hashicorp https://helm.releases.hashicorp.com
helm install vault hashicorp/vault

# Vault annotation-based injection
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vault-example
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "myapp"
        vault.hashicorp.com/agent-inject-secret-database-config.txt: "database/config"
    spec:
      serviceAccountName: myapp
      containers:
      - name: app
        image: myapp:latest
```

---

## 🎪 Lab 2: RBAC Security Patterns

### Principle of Least Privilege

```yaml
# read-only-role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]

---
# developer-role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer
  namespace: production
rules:
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
- apiGroups: [""]
  resources: ["pods", "pods/log", "services", "configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]  # Read only, no create/delete

---
# admin-role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: namespace-admin
  namespace: production
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

### Service Account Security

```yaml
# secure-service-account.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: production
automountServiceAccountToken: false  # Don't auto-mount unless needed

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
spec:
  template:
    spec:
      serviceAccountName: app-sa
      automountServiceAccountToken: false  # Explicit disable
      containers:
      - name: app
        image: myapp
```

### Bind Roles to Service Accounts

```yaml
# rolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-developer-binding
  namespace: production
subjects:
- kind: ServiceAccount
  name: app-sa
  namespace: production
roleRef:
  kind: Role
  name: developer
  apiGroup: rbac.authorization.k8s.io
```

---

## 🌐 Network Security

### Default Deny All Policy

```yaml
# default-deny.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### Allow Specific Traffic

```yaml
# allow-frontend-to-backend.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080

---
# allow-backend-to-database.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-backend-to-db
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432

---
# allow-dns.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

---

## 🎪 Lab 3: Implement Network Segmentation

### Step 1: Create Multi-Tier Application

```yaml
# three-tier-app.yaml
# Frontend
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
      tier: web
  template:
    metadata:
      labels:
        app: frontend
        tier: web
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80

---
# Backend
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
      tier: api
  template:
    metadata:
      labels:
        app: backend
        tier: api
    spec:
      containers:
      - name: api
        image: myapi:latest
        ports:
        - containerPort: 8080

---
# Database
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: database
  namespace: production
spec:
  replicas: 1
  selector:
    matchLabels:
      app: database
      tier: data
  template:
    metadata:
      labels:
        app: database
        tier: data
    spec:
      containers:
      - name: postgres
        image: postgres:14
        ports:
        - containerPort: 5432
```

### Step 2: Apply Network Policies

```yaml
# network-segmentation.yaml
# 1. Default deny all
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

---
# 2. Frontend: Allow ingress from LoadBalancer, egress to backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      tier: web
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector: {}  # Allow from ingress controller
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: api
    ports:
    - protocol: TCP
      port: 8080
  - to:  # DNS
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53

---
# 3. Backend: Allow from frontend, egress to database
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      tier: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: web
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: data
    ports:
    - protocol: TCP
      port: 5432
  - to:  # DNS
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53

---
# 4. Database: Allow only from backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      tier: data
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: api
    ports:
    - protocol: TCP
      port: 5432
```

```bash
# Apply policies
kubectl apply -f network-segmentation.yaml

# Test connectivity
kubectl exec -it frontend-pod -n production -- curl backend-service:8080  # Should work
kubectl exec -it frontend-pod -n production -- curl database-service:5432  # Should fail
```

---

## 🔍 Security Scanning

### Container Image Scanning with Trivy

```bash
# Install Trivy
brew install trivy  # macOS
apt-get install trivy  # Ubuntu

# Scan image
trivy image nginx:latest

# Scan for HIGH and CRITICAL only
trivy image --severity HIGH,CRITICAL nginx:latest

# Scan with specific format
trivy image --format json --output results.json nginx:latest

# Scan Kubernetes cluster
trivy k8s --report summary cluster
```

### Admission Controller with OPA Gatekeeper

```bash
# Install Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml

# Verify installation
kubectl get pods -n gatekeeper-system
```

```yaml
# constraint-template.yaml
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        
        violation[{"msg": msg, "details": {"missing_labels": missing}}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("You must provide labels: %v", [missing])
        }

---
# constraint.yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-app-and-owner-labels
spec:
  match:
    kinds:
    - apiGroups: ["apps"]
      kinds: ["Deployment"]
    namespaces:
    - production
  parameters:
    labels:
    - "app"
    - "owner"
    - "environment"
```

---

## 🎪 Lab 4: Implement Runtime Security

### Falco for Runtime Detection

```bash
# Install Falco
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco --namespace falco --create-namespace

# View alerts
kubectl logs -f -n falco -l app.kubernetes.io/name=falco
```

### Custom Falco Rules

```yaml
# falco-rules-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: falco-custom-rules
  namespace: falco
data:
  custom-rules.yaml: |
    - rule: Unauthorized Process in Container
      desc: Detect unauthorized process execution
      condition: >
        spawned_process and container and
        not proc.name in (nginx, node, python, java)
      output: >
        Unauthorized process started in container
        (user=%user.name command=%proc.cmdline container=%container.name)
      priority: WARNING
      
    - rule: Write Below Root
      desc: Detect attempts to write to root filesystem
      condition: >
        open_write and container and
        fd.name startswith "/"
      output: >
        File write below root directory
        (file=%fd.name command=%proc.cmdline)
      priority: ERROR
```

---

## 📊 Audit Logging

### Enable Audit Policy

```yaml
# audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
# Log pod changes at RequestResponse level
- level: RequestResponse
  resources:
  - group: ""
    resources: ["pods"]
  verbs: ["create", "update", "patch", "delete"]

# Log authentication attempts
- level: Metadata
  omitStages:
  - RequestReceived
  nonResourceURLs:
  - /api*
  - /version

# Log secret access
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets"]
  verbs: ["get", "list", "watch"]

# Catch-all rule
- level: Metadata
  omitStages:
  - RequestReceived
```

### Configure API Server

```bash
# Add to kube-apiserver flags
--audit-policy-file=/etc/kubernetes/audit-policy.yaml
--audit-log-path=/var/log/kubernetes/audit.log
--audit-log-maxage=30
--audit-log-maxbackup=10
--audit-log-maxsize=100
```

### Parse Audit Logs

```bash
# Search for failed authentication
cat /var/log/kubernetes/audit.log | jq 'select(.responseStatus.code >= 400 and .verb == "create" and .objectRef.resource == "tokenreviews")'

# Find secret access
cat /var/log/kubernetes/audit.log | jq 'select(.objectRef.resource == "secrets" and .verb == "get")'

# Identify deleted resources
cat /var/log/kubernetes/audit.log | jq 'select(.verb == "delete")'
```

---

## 🛡️ Cluster Hardening

### CIS Kubernetes Benchmark

```bash
# Install kube-bench
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml

# Run benchmark
kubectl logs job/kube-bench

# Review results
kubectl logs job/kube-bench | grep -i "FAIL"
```

### Critical Hardening Steps

```yaml
# 1. Disable anonymous authentication
apiVersion: v1
kind: ConfigMap
metadata:
  name: kube-apiserver-config
data:
  anonymous-auth: "false"

# 2. Enable encryption at rest
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <BASE64_ENCODED_SECRET>
  - identity: {}

# 3. Restrict kubelet permissions
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
authentication:
  anonymous:
    enabled: false
  webhook:
    enabled: true
authorization:
  mode: Webhook
```

---

## 💡 Security Checklist

### Cluster Level
```
☐ Enable RBAC
☐ Use Pod Security Standards
☐ Enable audit logging
☐ Encrypt etcd data at rest
☐ Use network policies
☐ Restrict API server access
☐ Regular security updates
☐ Run CIS benchmark
☐ Enable admission controllers
☐ Configure resource quotas
```

### Application Level
```
☐ Run as non-root user
☐ Use read-only root filesystem
☐ Drop all capabilities
☐ Don't use hostNetwork/hostPID
☐ Scan images for vulnerabilities
☐ Use trusted image registries
☐ Implement secrets management
☐ Set resource limits
☐ Use security contexts
☐ Validate input data
```

### Operational
```
☐ Regular backups
☐ Disaster recovery plan
☐ Incident response procedures
☐ Security monitoring
☐ Log aggregation
☐ Vulnerability scanning
☐ Penetration testing
☐ Security training
☐ Access reviews
☐ Compliance audits
```

---

## 🐛 Troubleshooting Security Issues

### Issue 1: Pod Rejected by Security Policy

```bash
# Check policy violations
kubectl get events -n production | grep -i "violates"

# Describe pod for details
kubectl describe pod failing-pod -n production

# Check namespace labels
kubectl get namespace production --show-labels

# Fix: Update pod security context
kubectl edit deployment myapp -n production
# Add appropriate securityContext
```

### Issue 2: Network Policy Blocking Traffic

```bash
# List all network policies
kubectl get networkpolicies -n production

# Describe policy
kubectl describe networkpolicy policy-name -n production

# Test connectivity
kubectl run test-pod --image=busybox -it --rm -- sh
# Inside pod
wget -O- http://service-name:port

# Debug: Temporarily allow all
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-all-temp
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - {}
  egress:
  - {}
EOF
```

### Issue 3: RBAC Permission Denied

```bash
# Check user permissions
kubectl auth can-i create pods --as=user@example.com -n production

# List user's roles
kubectl get rolebindings -n production -o json | \
  jq '.items[] | select(.subjects[]?.name=="user@example.com")'

# Check service account permissions
kubectl auth can-i list secrets --as=system:serviceaccount:production:app-sa -n production

# Grant permission
kubectl create rolebinding temp-access \
  --clusterrole=view \
  --user=user@example.com \
  -n production
```

---

## 📝 Quick Reference

```bash
# Pod Security
kubectl label namespace production pod-security.kubernetes.io/enforce=restricted
kubectl get psp

# Secrets
kubectl create secret generic mysecret --from-literal=key=value
kubectl get secrets
kubectl describe secret mysecret

# RBAC
kubectl create serviceaccount mysa
kubectl create role myrole --verb=get,list --resource=pods
kubectl create rolebinding mybinding --role=myrole --serviceaccount=default:mysa
kubectl auth can-i create pods --as=system:serviceaccount:default:mysa

# Network Policies
kubectl get networkpolicies
kubectl describe networkpolicy policy-name

# Security Scanning
trivy image myimage:tag
trivy k8s cluster

# Audit
kubectl get events -n namespace
kubectl logs -l component=kube-apiserver -n kube-system | grep audit
```

---

## 📝 Quiz

### Questions:
1. What are the three Pod Security Standard levels?
2. How do you prevent privilege escalation in a pod?
3. What is the principle of least privilege in RBAC?
4. How do network policies improve security?
5. What tools can scan for vulnerabilities in container images?
6. How should secrets be managed in production?
7. What is defense in depth?

### Answers:
1. Privileged, Baseline, and Restricted
2. Set allowPrivilegeEscalation: false and drop all capabilities
3. Grant only the minimum permissions needed for a task
4. They restrict network traffic between pods, implementing microsegmentation
5. Trivy, Clair, Anchore, Snyk
6. Use external secrets management (Vault, AWS Secrets Manager) with ExternalSecrets Operator
7. Multiple layers of security controls, so if one fails, others still protect

---

## 🎓 Challenge Exercise

### Project: Secure a Three-Tier Application

**Requirements:**
1. Deploy frontend, backend, and database with Pod Security Standards
2. Implement RBAC with least privilege
3. Configure network policies for microsegmentation
4. Set up secrets management with External Secrets
5. Enable audit logging
6. Scan images with Trivy
7. Implement OPA Gatekeeper policies
8. Configure Falco for runtime detection

**Bonus:**
- Run CIS benchmark and fix issues
- Implement mTLS with service mesh
- Set up centralized logging
- Create security dashboard

---

## 💡 Key Takeaways

✅ Security is multi-layered (defense in depth)
✅ Always use Pod Security Standards
✅ Implement network policies for traffic control
✅ Never store secrets in code or configs
✅ Use RBAC with least privilege principle
✅ Scan images before deployment
✅ Enable audit logging for compliance
✅ Regular security assessments and updates

---

## ⏭️ Next Steps

Ready for production deployment patterns? Continue to [Module 24: Production Deployment Patterns](./24-production-patterns.md)

---

## 📚 Additional Resources

- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [OWASP Kubernetes Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html)
- [Falco Documentation](https://falco.org/docs/)

---

**🎉 Congratulations!** You now understand Kubernetes security best practices and can secure production clusters!
