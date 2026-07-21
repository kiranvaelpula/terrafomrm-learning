# Module 24: Production Deployment Patterns

## 📚 What You'll Learn
- Production-ready architecture patterns
- High availability strategies
- Zero-downtime deployments
- Monitoring and observability
- Disaster recovery planning
- Cost optimization
- Performance tuning

---

## 🎯 Production Architecture Principles

### Five Pillars of Production Systems
```
1. Reliability    - System works correctly under stress
2. Scalability    - Handle increased load efficiently
3. Observability  - Monitor and debug effectively
4. Security       - Protect against threats
5. Cost Efficiency - Optimize resource usage
```

---

## 🏗️ High Availability Patterns

### Multi-Zone Deployment

```yaml
# multi-zone-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: production
spec:
  replicas: 6
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      # Spread across availability zones
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: web
      # Anti-affinity for different nodes
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: web
              topologyKey: kubernetes.io/hostname
      containers:
      - name: web
        image: myapp:v1.2.3
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
```


### Pod Disruption Budgets

```yaml
# pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-app-pdb
  namespace: production
spec:
  minAvailable: 2  # Always keep at least 2 pods running
  selector:
    matchLabels:
      app: web

---
# Alternative: Use percentage
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
  namespace: production
spec:
  maxUnavailable: 25%  # Max 25% can be down
  selector:
    matchLabels:
      app: api
```

---

## 🎪 Lab 1: Production-Grade Deployment

### Complete Production Setup

```yaml
# production-app.yaml

# Namespace with resource quotas
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    environment: production
    pod-security.kubernetes.io/enforce: restricted

---
# Resource Quota
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "100"
    requests.memory: "200Gi"
    persistentvolumeclaims: "20"
    services.loadbalancers: "5"

---
# Limit Range
apiVersion: v1
kind: LimitRange
metadata:
  name: production-limits
  namespace: production
spec:
  limits:
  - max:
      cpu: "2"
      memory: "4Gi"
    min:
      cpu: "100m"
      memory: "128Mi"
    default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "250m"
      memory: "256Mi"
    type: Container

---
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: production
data:
  app.properties: |
    server.port=8080
    logging.level=INFO
    cache.ttl=3600
    max.connections=100

---
# Secret (from external secrets in production)
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: production
type: Opaque
data:
  database-url: cG9zdGdyZXM6Ly9ob3N0L2RiCg==
  api-key: c3VwZXJzZWNyZXRrZXkK

---
# Service Account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: production
automountServiceAccountToken: false

---
# Deployment with all best practices
apiVersion: apps/v1
kind: Deployment
metadata:
  name: production-app
  namespace: production
  labels:
    app: production-app
    version: v1.2.3
    owner: platform-team
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Zero downtime
  selector:
    matchLabels:
      app: production-app
  template:
    metadata:
      labels:
        app: production-app
        version: v1.2.3
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: app-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
        seccompProfile:
          type: RuntimeDefault
      
      # Spread across zones
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: production-app
      
      # Init container for readiness checks
      initContainers:
      - name: wait-for-db
        image: busybox:1.35
        command: ['sh', '-c', 'until nc -z postgres-service 5432; do echo waiting for db; sleep 2; done;']
      
      containers:
      - name: app
        image: myapp:v1.2.3
        imagePullPolicy: IfNotPresent
        
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP
        - name: metrics
          containerPort: 9090
          protocol: TCP
        
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
        
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        
        # Health checks
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
            scheme: HTTP
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
            scheme: HTTP
          initialDelaySeconds: 30
          periodSeconds: 5
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 2
        
        startupProbe:
          httpGet:
            path: /health/startup
            port: 8080
          initialDelaySeconds: 0
          periodSeconds: 10
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 30
        
        # Security
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
        
        # Volume mounts
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/cache
        - name: logs
          mountPath: /app/logs
      
      # Volumes
      volumes:
      - name: tmp
        emptyDir: {}
      - name: cache
        emptyDir: {}
      - name: logs
        emptyDir: {}
      
      # DNS and scheduling
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      terminationGracePeriodSeconds: 60

---
# Service
apiVersion: v1
kind: Service
metadata:
  name: production-app-service
  namespace: production
  labels:
    app: production-app
spec:
  type: ClusterIP
  selector:
    app: production-app
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800

---
# HorizontalPodAutoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: production-app-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: production-app
  minReplicas: 5
  maxReplicas: 50
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
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 4
        periodSeconds: 30
      selectPolicy: Max

---
# PodDisruptionBudget
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: production-app-pdb
  namespace: production
spec:
  minAvailable: 3
  selector:
    matchLabels:
      app: production-app

---
# Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: production-app-ingress
  namespace: production
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - app.example.com
    secretName: app-tls-cert
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: production-app-service
            port:
              number: 80
```

```bash
# Deploy everything
kubectl apply -f production-app.yaml

# Verify deployment
kubectl get all -n production
kubectl get hpa -n production
kubectl get pdb -n production
kubectl get ingress -n production
```

---

## 🚀 Deployment Strategies

### 1. Rolling Update (Default)

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Add 1 new pod before removing old
      maxUnavailable: 0  # Zero downtime
```

**Use case:** Standard production deployments

### 2. Blue-Green Deployment

```yaml
# Blue (current)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: app
        image: myapp:v1.0

---
# Green (new)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: app
        image: myapp:v2.0

---
# Service (switch by updating selector)
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp
    version: blue  # Change to 'green' to switch
  ports:
  - port: 80
```

```bash
# Deploy green
kubectl apply -f app-green.yaml

# Test green
kubectl port-forward deploy/app-green 8080:80

# Switch traffic to green
kubectl patch service app-service -p '{"spec":{"selector":{"version":"green"}}}'

# Rollback if needed
kubectl patch service app-service -p '{"spec":{"selector":{"version":"blue"}}}'

# Delete blue after validation
kubectl delete deployment app-blue
```

**Use case:** Quick rollback needed, database migrations

### 3. Canary Deployment

```yaml
# Stable version (90%)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: myapp
      track: stable
  template:
    metadata:
      labels:
        app: myapp
        track: stable
        version: v1.0
    spec:
      containers:
      - name: app
        image: myapp:v1.0

---
# Canary version (10%)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
      track: canary
  template:
    metadata:
      labels:
        app: myapp
        track: canary
        version: v2.0
    spec:
      containers:
      - name: app
        image: myapp:v2.0

---
# Service routes to both
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp  # Matches both stable and canary
  ports:
  - port: 80
```

```bash
# Deploy canary (10% traffic)
kubectl apply -f app-canary.yaml

# Monitor metrics
kubectl top pods -l track=canary
kubectl logs -l track=canary --tail=100

# Gradually increase canary
kubectl scale deployment app-canary --replicas=3  # 25%
kubectl scale deployment app-stable --replicas=9  # 75%

# Full rollout
kubectl scale deployment app-canary --replicas=12
kubectl scale deployment app-stable --replicas=0

# Rename canary to stable
kubectl delete deployment app-stable
kubectl patch deployment app-canary -p '{"metadata":{"name":"app-stable"}}'
```

**Use case:** Testing new version with real traffic, A/B testing

### 4. A/B Testing with Istio

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: app-ab-test
spec:
  hosts:
  - app.example.com
  http:
  - match:
    - headers:
        user-type:
          exact: "premium"
    route:
    - destination:
        host: app-service
        subset: v2
  - route:
    - destination:
        host: app-service
        subset: v1
      weight: 90
    - destination:
        host: app-service
        subset: v2
      weight: 10

---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: app-destinations
spec:
  host: app-service
  subsets:
  - name: v1
    labels:
      version: v1.0
  - name: v2
    labels:
      version: v2.0
```

**Use case:** Feature flags, user-based routing

---

## 🎪 Lab 2: Zero-Downtime Deployment

### Setup

```yaml
# app-v1.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
  namespace: production
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 0
  selector:
    matchLabels:
      app: demo
  template:
    metadata:
      labels:
        app: demo
        version: v1
    spec:
      containers:
      - name: app
        image: nginxdemos/hello:plain-text
        ports:
        - containerPort: 80
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        lifecycle:
          preStop:
            exec:
              command: ["sleep", "15"]  # Give time to drain connections
---
apiVersion: v1
kind: Service
metadata:
  name: app-service
  namespace: production
spec:
  selector:
    app: demo
  ports:
  - port: 80
  type: LoadBalancer
```

### Deploy and Test

```bash
# Deploy v1
kubectl apply -f app-v1.yaml

# Generate continuous traffic
while true; do curl http://<service-ip>; sleep 0.5; done

# In another terminal, update to v2
kubectl set image deployment/app app=nginxdemos/hello:0.3 -n production

# Watch rollout
kubectl rollout status deployment/app -n production

# Should see no errors in curl loop (zero downtime)
```

### Rollback if Needed

```bash
# Undo last rollout
kubectl rollout undo deployment/app -n production

# Rollback to specific revision
kubectl rollout history deployment/app -n production
kubectl rollout undo deployment/app --to-revision=2 -n production
```

---

## 📊 Monitoring and Observability

### Prometheus Monitoring

```yaml
# servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: app-monitor
  namespace: production
spec:
  selector:
    matchLabels:
      app: production-app
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics

---
# prometheusrule.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: app-alerts
  namespace: production
spec:
  groups:
  - name: app
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected"
        description: "Error rate is {{ $value }} for {{ $labels.instance }}"
    
    - alert: HighMemoryUsage
      expr: container_memory_usage_bytes{pod=~"production-app-.*"} / container_spec_memory_limit_bytes > 0.9
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High memory usage"
        description: "Memory usage is {{ $value }} for {{ $labels.pod }}"
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Production App Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{namespace=\"production\"}[5m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{namespace=\"production\",status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

### Logging with Fluent Bit

```yaml
# fluentbit-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: logging
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush        5
        Daemon       Off
        Log_Level    info
        
    [INPUT]
        Name              tail
        Path              /var/log/containers/*production*.log
        Parser            docker
        Tag               kube.*
        Refresh_Interval  5
        
    [FILTER]
        Name                kubernetes
        Match               kube.*
        Kube_URL            https://kubernetes.default.svc:443
        
    [OUTPUT]
        Name               es
        Match              *
        Host               elasticsearch.logging.svc
        Port               9200
        Logstash_Format    On
        Retry_Limit        False
```

---

## 🎪 Lab 3: Complete Monitoring Stack

```bash
# Install Prometheus Operator
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Install Loki for logs
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  --namespace logging \
  --create-namespace \
  --set grafana.enabled=true

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Default credentials
# Username: admin
# Password: prom-operator

# Add Loki datasource in Grafana
# URL: http://loki.logging.svc:3100
```

---

## 💰 Cost Optimization

### Resource Right-Sizing

```yaml
# Use VPA for recommendations
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: production-app
  updatePolicy:
    updateMode: "Off"  # Recommendation only
```

```bash
# Install VPA
kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vertical-pod-autoscaler-0.13.0/vpa-v0.13.0.yaml

# Get recommendations
kubectl describe vpa app-vpa
```

### Cluster Autoscaler

```yaml
# cluster-autoscaler.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
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
      - name: cluster-autoscaler
        image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.27.0
        command:
        - ./cluster-autoscaler
        - --v=4
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/my-cluster
```

### Spot Instances

```yaml
# spot-node-pool.yaml
apiVersion: v1
kind: Node
metadata:
  labels:
    node.kubernetes.io/instance-type: spot

---
# Tolerate spot interruptions
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      tolerations:
      - key: "spotInstance"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: node.kubernetes.io/instance-type
                operator: In
                values:
                - spot
```

---

## 🔄 Backup and Disaster Recovery

### Velero Backup Strategy

```bash
# Install Velero
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.7.0 \
  --bucket my-backup-bucket \
  --backup-location-config region=us-east-1 \
  --snapshot-location-config region=us-east-1 \
  --secret-file ./credentials-velero

# Scheduled backups
velero schedule create daily-backup \
  --schedule="0 2 * * *" \
  --include-namespaces production \
  --ttl 720h0m0s

# Backup specific resources
velero backup create manual-backup \
  --include-namespaces production \
  --include-resources deployments,services,configmaps,secrets

# Restore
velero restore create --from-backup daily-backup-20240101
```

### Etcd Backup

```bash
# Backup etcd
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify backup
ETCDCTL_API=3 etcdctl snapshot status /backup/etcd-snapshot.db

# Restore etcd (emergency only)
ETCDCTL_API=3 etcdctl snapshot restore /backup/etcd-snapshot.db \
  --data-dir=/var/lib/etcd-restore
```

---

## 📝 Production Checklist

### Pre-Deployment
```
☐ Code review completed
☐ Unit tests pass (>80% coverage)
☐ Integration tests pass
☐ Security scan passed
☐ Image vulnerabilities checked
☐ Resource limits defined
☐ Health checks configured
☐ Monitoring configured
☐ Logging configured
☐ Backup strategy defined
☐ Rollback plan ready
☐ Documentation updated
```

### Deployment
```
☐ Deploy to staging first
☐ Run smoke tests
☐ Check metrics/logs
☐ Gradual rollout (canary)
☐ Monitor error rates
☐ Validate functionality
☐ Performance testing
☐ Load testing
```

### Post-Deployment
```
☐ Monitor for 24 hours
☐ Check alerts
☐ Review logs
☐ Verify metrics
☐ Customer feedback
☐ Incident report (if any)
☐ Lessons learned
```

---

## 💡 Best Practices Summary

### Reliability
- Multiple replicas across zones
- Pod Disruption Budgets
- Health checks (liveness, readiness, startup)
- Graceful shutdown
- Circuit breakers

### Scalability
- Horizontal Pod Autoscaling
- Cluster Autoscaling
- Resource limits and requests
- Efficient algorithms
- Caching strategies

### Observability
- Structured logging
- Metrics collection
- Distributed tracing
- Alerting rules
- Dashboards

### Security
- Pod Security Standards
- Network Policies
- RBAC
- Secrets management
- Regular updates

### Cost
- Right-size resources
- Use spot instances
- Auto-scaling
- Resource quotas
- Clean up unused resources

---

## 📝 Quiz

### Questions:
1. What is the difference between maxSurge and maxUnavailable?
2. When would you use Blue-Green vs Canary deployment?
3. What is a Pod Disruption Budget and why is it important?
4. How do you achieve zero-downtime deployments?
5. What are the key metrics to monitor in production?
6. How does Cluster Autoscaler differ from HPA?
7. What should be included in a disaster recovery plan?

### Answers:
1. maxSurge: extra pods during update; maxUnavailable: how many can be down simultaneously
2. Blue-Green: instant switch/rollback, database changes; Canary: gradual rollout, risk mitigation
3. PDB ensures minimum pods available during voluntary disruptions (node drains, updates)
4. Set maxUnavailable:0, proper health checks, graceful shutdown, preStop hooks
5. Error rate, latency, throughput, resource usage, saturation
6. HPA scales pods; Cluster Autoscaler scales nodes based on pod resource requests
7. Backup strategy, RPO/RTO, restore procedures, failover plan, communication plan

---

## 🎓 Challenge Exercise

### Project: Production-Ready E-commerce Platform

**Requirements:**
1. Deploy multi-tier app (frontend, backend, database, cache)
2. Implement HA with multi-zone deployment
3. Configure HPA and Cluster Autoscaler
4. Set up monitoring with Prometheus/Grafana
5. Implement logging with Loki
6. Configure backups with Velero
7. Network policies for security
8. Canary deployment strategy
9. Cost optimization with spot instances
10. Document DR procedures

**Bonus:**
- Service mesh with Istio
- GitOps with ArgoCD
- Chaos engineering with Chaos Mesh
- Performance testing with k6

---

## 💡 Key Takeaways

✅ Production requires high availability and fault tolerance
✅ Zero-downtime deployments are achievable with proper configuration
✅ Monitoring and observability are critical
✅ Always have rollback strategy
✅ Disaster recovery planning is mandatory
✅ Cost optimization is ongoing work
✅ Security should be built-in, not added later

---

## ⏭️ Next Steps

Ready for the final project? Continue to [Module 25: Real-World Project](./25-real-world-project.md)

---

## 📚 Additional Resources

- [Production Best Practices](https://kubernetes.io/docs/setup/best-practices/)
- [Deployment Strategies](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy)
- [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator)
- [Velero Documentation](https://velero.io/docs/)
- [Cloud Native Cost Optimization](https://www.cncf.io/blog/2021/06/29/finops-for-kubernetes/)

---

**🎉 Congratulations!** You now understand production deployment patterns and can build reliable, scalable systems on Kubernetes!
