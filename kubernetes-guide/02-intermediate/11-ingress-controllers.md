# Module 11: Ingress Controllers

## What is Ingress?

Ingress is the way you expose your HTTP/HTTPS applications to the outside world with routing rules (like "api.example.com goes to the API service" and "www.example.com goes to the frontend").

**The problem without Ingress:**

Every service that needs internet access requires its own LoadBalancer. Each LoadBalancer costs money (on cloud). If you have 10 services, that's 10 LoadBalancers, 10 public IPs, 10 bills.

```
Without Ingress (expensive):
Internet → LoadBalancer 1 → frontend pods     ($15/month)
Internet → LoadBalancer 2 → api pods          ($15/month)
Internet → LoadBalancer 3 → admin pods        ($15/month)
Total: 3 LoadBalancers = ~$45/month

With Ingress (one entry point):
Internet → 1 LoadBalancer → Ingress Controller → routes to correct service
Total: 1 LoadBalancer = ~$15/month
```

**Ingress = smart reverse proxy with routing rules built into Kubernetes.**

---

## Two Parts: Ingress Resource + Ingress Controller

**Ingress Resource** = the routing rules (YAML you write)
"Send api.example.com to the api-service, send www.example.com to the frontend-service"

**Ingress Controller** = the software that actually implements those rules (NGINX, Traefik, HAProxy, AWS ALB)
"I read the rules and configure myself to route traffic accordingly"

You need BOTH. The Ingress Resource alone does nothing without a Controller installed.

---

## When to Use Ingress vs Other Options

| Method | Use when... |
|---|---|
| ClusterIP | Internal only, pod-to-pod |
| NodePort | Quick testing, direct node access |
| LoadBalancer | Single service exposed, non-HTTP (TCP/UDP) |
| Ingress | Multiple HTTP services, path/host routing, TLS |

---

## Install NGINX Ingress Controller

```bash
# Install via manifest
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Or via Helm (preferred)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# Check it's running
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx    # You'll see the LoadBalancer IP here
```

---

## Example 1: Simple Single-Service Ingress

"Expose my web app at myapp.example.com"

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: simple-ingress
spec:
  ingressClassName: nginx            # Which controller handles this
  rules:
  - host: myapp.example.com         # Domain name
    http:
      paths:
      - path: /                      # All paths
        pathType: Prefix
        backend:
          service:
            name: web-service        # Route to this service
            port:
              number: 80
```

**In plain English:** "When someone visits myapp.example.com, send them to web-service on port 80."

---

## Example 2: Path-Based Routing

"One domain, different paths go to different services."

```
myapp.example.com/api    → api-service
myapp.example.com/web    → frontend-service
myapp.example.com/admin  → admin-service
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-routing
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
      - path: /web
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      - path: /admin
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 3000
```

**When to use:** Monolithic frontend that routes to different backend services by path. Common in microservices architecture.

---

## Example 3: Host-Based Routing (Multiple Domains)

"Different domains go to different services."

```
api.example.com   → api-service
www.example.com   → frontend-service
admin.example.com → admin-service
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-routing
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
  - host: www.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
  - host: admin.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 3000
```

**When to use:** Multiple applications or microservices that each need their own subdomain.

---

## Example 4: TLS/SSL (HTTPS)

"Serve my app over HTTPS with a certificate."

```bash
# Create TLS secret from certificate files
kubectl create secret tls app-tls-cert \
  --cert=tls.crt \
  --key=tls.key
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"   # Force HTTPS
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - myapp.example.com
    secretName: app-tls-cert          # TLS certificate secret
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

**In plain English:** "Serve myapp.example.com over HTTPS using the certificate in `app-tls-cert` secret. Redirect HTTP to HTTPS."

---

## Example 5: Automatic TLS with Cert-Manager

Instead of managing certificates manually, use cert-manager to get free Let's Encrypt certs automatically:

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

```yaml
# ClusterIssuer (one-time setup)
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
    - http01:
        ingress:
          class: nginx

---
# Ingress with automatic certificate
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: auto-tls-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"   # Auto-get certificate
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls              # cert-manager creates this automatically
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

**What happens:** Cert-manager sees the annotation, requests a certificate from Let's Encrypt, stores it in the secret, and auto-renews before expiry. Zero manual work.

---

## Common Annotations (NGINX Ingress)

Annotations control the Ingress Controller's behavior:

```yaml
metadata:
  annotations:
    # Redirect HTTP to HTTPS
    nginx.ingress.kubernetes.io/ssl-redirect: "true"

    # Rewrite URL path
    nginx.ingress.kubernetes.io/rewrite-target: /

    # Rate limiting (requests per second per IP)
    nginx.ingress.kubernetes.io/limit-rps: "10"

    # Upload size limit
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"

    # Timeout settings
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"

    # IP whitelist
    nginx.ingress.kubernetes.io/whitelist-source-range: "10.0.0.0/24,192.168.0.0/16"

    # Basic authentication
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: basic-auth-secret

    # CORS headers
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://frontend.example.com"

    # Websocket support
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
```

---

## pathType Explained

```yaml
- path: /api
  pathType: Prefix     # Matches /api, /api/, /api/users, /api/v1/stuff
  
- path: /api
  pathType: Exact      # Matches ONLY /api, not /api/ or /api/users

- path: /
  pathType: ImplementationSpecific  # Controller decides (avoid this)
```

| pathType | /api matches | /api/ matches | /api/users matches |
|---|---|---|---|
| Prefix | ✅ | ✅ | ✅ |
| Exact | ✅ | ❌ | ❌ |

---

## How the Full Flow Works

```
1. User types: https://api.example.com/users
2. DNS resolves to LoadBalancer IP (the Ingress Controller's external IP)
3. Request hits Ingress Controller (NGINX pod)
4. Controller checks Ingress rules: "api.example.com → api-service"
5. Controller forwards request to api-service:8080
6. Service routes to one of the API pods
7. Response travels back the same path
```

---

## Popular Ingress Controllers

| Controller | Best for |
|---|---|
| NGINX Ingress | General purpose, most popular, well documented |
| Traefik | Auto-discovery, Let's Encrypt built-in, simpler config |
| HAProxy | High performance, advanced load balancing |
| AWS ALB Ingress | Native AWS integration (no separate LB needed) |
| GCE Ingress | Native Google Cloud integration |
| Istio Gateway | When using Istio service mesh |

---

## Troubleshooting

```bash
# Check Ingress resource
kubectl get ingress
kubectl describe ingress my-ingress

# Check Ingress Controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# Check if controller has the LoadBalancer IP
kubectl get svc -n ingress-nginx

# Test locally (add to /etc/hosts)
# <LoadBalancer-IP>  myapp.example.com
curl -H "Host: myapp.example.com" http://<LoadBalancer-IP>/

# Check TLS certificate
kubectl get secret app-tls-cert
kubectl describe certificate myapp-tls   # If using cert-manager
```

---

## ⏭️ Next: [Module 12: Namespaces & Resource Quotas](./12-namespaces-quotas.md)
