# Module 20: Service Mesh with Istio

## What is a Service Mesh?

In a microservices architecture, services talk to each other constantly. A service mesh is an infrastructure layer that handles all this service-to-service communication — traffic routing, security, observability — without changing your application code.

**The problem it solves:**
- How do you encrypt traffic between services?
- How do you route 10% of traffic to a new version for testing?
- How do you see which service is calling which?
- How do you retry failed requests automatically?
- How do you set timeouts and circuit breakers?

Without a mesh, each service needs to implement this logic itself. With a mesh, all of this is handled by a sidecar proxy injected alongside every pod.

**When to use:**
- You have many microservices (10+) that communicate heavily
- You need mutual TLS (mTLS) between all services for security/compliance
- You want canary deployments, A/B testing, or traffic splitting without code changes
- You need detailed observability (which service called which, latency, error rates)
- You want circuit breakers and retries without coding them into each service

**When NOT to use:**
- Simple applications with few services (overhead isn't worth it)
- You're just starting out (adds complexity)
- Your team isn't ready for the operational burden

---

## 📖 Understanding Service Mesh (Intuition First)

When you break a big application into dozens of microservices, you gain flexibility but inherit a new headache: those services now spend all day talking to each other over the network, and networks are unreliable and insecure. Every service suddenly needs to handle retries, timeouts, encryption, load balancing, and tracing. The naive fix is to build all that logic into each service — but then you're re-implementing the same plumbing in every codebase and every language. A **service mesh** pulls that plumbing *out* of your apps and into the infrastructure.

The trick that makes this possible is the **sidecar proxy**. Alongside every one of your application pods, the mesh injects a small proxy container (Envoy, in Istio's case). Your app is told nothing about it; it just makes normal network calls. But those calls are transparently intercepted by the sidecar, which applies all the smart behavior — encrypting the connection, retrying failures, load balancing, recording metrics — before forwarding on to the destination's sidecar. It's like giving every service a personal assistant who handles all its phone calls according to company policy.

This splits the system into two planes, a distinction worth remembering. The **data plane** is the fleet of sidecar proxies that actually carry your traffic. The **control plane** (Istiod) is the brain that configures them — you give it high-level rules, and it programs every proxy accordingly. You change behavior by editing config, not by redeploying apps.

The three headline capabilities all flow from this design. **Traffic management**: because every request passes through a proxy, you can split traffic by percentage or by request attributes — enabling canary releases and A/B tests declaratively, with zero application changes. **Security**: the mesh can enforce **mutual TLS** everywhere, encrypting all service-to-service traffic and verifying each service's identity, again without touching your code. **Observability**: since the proxies see every request, you get uniform metrics, distributed traces, and a live map of who-calls-whom for free.

The honest caveat: a service mesh is powerful but not free. It adds latency, resource overhead, and real operational complexity. For a handful of services it's usually overkill — you're better off starting simpler. The mesh earns its keep once you have many services, strict security or compliance requirements (mTLS everywhere), or a need for sophisticated traffic control and observability that would be painful to hand-roll.

---

## How Istio Works

```
Your Pod:
┌──────────────────────────────────┐
│  ┌──────────┐  ┌──────────────┐ │
│  │ Your App │←→│ Envoy Proxy  │ │  ← sidecar (injected automatically)
│  └──────────┘  └──────────────┘ │
└──────────────────────────────────┘
         ↕ All traffic goes through Envoy
┌──────────────────────────────────┐
│  ┌──────────┐  ┌──────────────┐ │
│  │ Other App│←→│ Envoy Proxy  │ │
│  └──────────┘  └──────────────┘ │
└──────────────────────────────────┘
```

- **Data Plane** = Envoy sidecar proxies (handle actual traffic)
- **Control Plane** = Istiod (tells proxies what rules to follow)

Your app doesn't know the proxy exists. It sends traffic normally, and the proxy intercepts and applies rules (mTLS, routing, retries, etc.).

---

## 🌐 Install Istio

```bash
# Download Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH

# Install Istio
istioctl install --set profile=demo -y

# Enable sidecar injection for a namespace
# Any pod created here will automatically get an Envoy sidecar
kubectl label namespace default istio-injection=enabled

# Verify
kubectl get pods -n istio-system
```

**What `istio-injection=enabled` does:** Every new pod in that namespace automatically gets a sidecar proxy container injected. You don't change your Deployment YAML at all.

---

## 📝 Deploy Sample Application

A normal deployment — nothing Istio-specific in the YAML. The sidecar is injected automatically.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: productpage
spec:
  ports:
  - port: 9080
  selector:
    app: productpage
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: productpage-v1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: productpage
      version: v1
  template:
    metadata:
      labels:
        app: productpage
        version: v1          # Version label is important for traffic routing
    spec:
      containers:
      - name: productpage
        image: docker.io/istio/examples-bookinfo-productpage-v1:1.17.0
        ports:
        - containerPort: 9080
```

---

## 🚦 Traffic Management

### VirtualService — "Where should traffic go?"

A VirtualService lets you control routing rules without changing your app. This is the killer feature of a service mesh.

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews                  # When someone calls the "reviews" service...
  http:
  - match:
    - headers:
        end-user:
          exact: jason       # If the header says user is "jason"...
    route:
    - destination:
        host: reviews
        subset: v2           # Send to v2 (he's our tester)
  - route:
    - destination:
        host: reviews
        subset: v1           # Everyone else gets v1
```

**In plain English:** "If user jason is making the request, show him version 2. Everyone else sees version 1." You just implemented A/B testing without touching any application code.

**When to use VirtualService:**
- Canary releases (send 5% traffic to new version)
- A/B testing (specific users see new features)
- Header-based routing (mobile users get different backend)
- Fault injection for testing (delay 50% of requests to test resilience)

### DestinationRule — "What are the versions?"

A DestinationRule defines the subsets (versions) that VirtualService can route to.

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  trafficPolicy:
    loadBalancer:
      simple: RANDOM            # Load balancing strategy
  subsets:
  - name: v1
    labels:
      version: v1              # Pods with label version=v1
  - name: v2
    labels:
      version: v2              # Pods with label version=v2
  - name: v3
    labels:
      version: v3              # Pods with label version=v3
```

**In plain English:** "The reviews service has 3 versions. v1 = pods labeled version:v1, v2 = pods labeled version:v2, etc. Use random load balancing."

---

## 🎯 Canary Deployment

"Send 50% of mobile traffic to v2, keep everything else on v1."

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-canary
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        user-agent:
          regex: ".*Mobile.*"       # Mobile users only
    route:
    - destination:
        host: reviews
        subset: v2
      weight: 50                    # 50% get v2
    - destination:
        host: reviews
        subset: v1
      weight: 50                    # 50% get v1
  - route:
    - destination:
        host: reviews
        subset: v1                  # Desktop users always get v1
```

**In plain English:** "For mobile users, split traffic 50/50 between v1 and v2. Desktop users always see v1."

**Typical canary workflow:**
1. Start with 5% to v2 → monitor errors
2. Increase to 25% → monitor
3. Increase to 50% → monitor
4. If all good → 100% to v2, delete v1
5. If errors → 0% to v2 (instant rollback)

---

## 🔒 Security with mTLS

Mutual TLS encrypts ALL traffic between services and verifies identity. Without it, any pod can impersonate any service.

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
    mode: STRICT             # ALL traffic must be encrypted
```

**In plain English:** "Every service in this namespace must use encrypted connections. If a service tries to send unencrypted traffic, it gets rejected."

**Modes:**
- `STRICT` — must be mTLS, reject plain text
- `PERMISSIVE` — accept both (useful during migration)
- `DISABLE` — no mTLS

**When to use:** Always in production. It gives you encryption in transit + service identity verification with zero code changes.

---

## 📊 Observability

One of the biggest benefits — you get visibility into all traffic automatically, without adding any code to your services.

```bash
# Install observability tools
kubectl apply -f samples/addons/kiali.yaml       # Service mesh dashboard
kubectl apply -f samples/addons/prometheus.yaml   # Metrics
kubectl apply -f samples/addons/grafana.yaml      # Dashboards
kubectl apply -f samples/addons/jaeger.yaml       # Distributed tracing

# Access Kiali (service mesh visualization)
istioctl dashboard kiali
```

**What you get for free:**
- Traffic flow visualization (which service calls which)
- Request rates, error rates, latency per service
- Distributed tracing (follow a request through 10 services)
- Health status of all services

---

## Summary: When to Use Each Feature

| Feature | Problem it Solves |
|---|---|
| VirtualService | Traffic routing, canary, A/B testing |
| DestinationRule | Define versions, load balancing policies |
| PeerAuthentication | Encrypt service-to-service traffic (mTLS) |
| Gateway | Ingress traffic from outside the mesh |
| ServiceEntry | Allow traffic to external services |
| Kiali | Visualize the service mesh |

---

## 🎯 Interview Quick Points

- A **service mesh** handles service-to-service communication (routing, security, observability) without app code changes
- Works via **sidecar proxies** (Envoy) injected next to every pod that transparently intercept traffic
- Split into **data plane** (the proxies carrying traffic) and **control plane** (Istiod configuring them)
- `istio-injection=enabled` on a namespace auto-injects sidecars — no Deployment YAML changes needed
- **VirtualService** = routing rules (canary, A/B, weighted splits, header-based, fault injection)
- **DestinationRule** = defines subsets/versions and load-balancing policies
- **PeerAuthentication** enables **mTLS**; modes are STRICT, PERMISSIVE (migration), DISABLE
- **Gateway** manages ingress into the mesh; **ServiceEntry** allows reaching external services
- Free observability: metrics, distributed tracing, and topology (via Kiali, Prometheus, Grafana, Jaeger)
- Enables **progressive canary** rollouts and instant rollback by shifting traffic weights
- Trade-offs: added latency, resource overhead, and operational complexity — overkill for few services
- Best fit: many microservices, mandatory mTLS/compliance, and advanced traffic/observability needs

---

## ⏭️ Next: [Module 21: GitOps with ArgoCD](./21-gitops-argocd.md)
