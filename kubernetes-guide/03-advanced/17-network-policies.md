# Module 17: Network Policies

## What are Network Policies?

By default, every pod in Kubernetes can talk to every other pod — no restrictions. That's convenient for development but dangerous in production. Network Policies are like firewall rules for your pods — they control which pods can communicate with which other pods.

**When to use:**
- You want to isolate sensitive workloads (databases should only accept traffic from backend, not from frontend)
- Compliance requirements mandate network segmentation
- You want to limit the blast radius if one pod gets compromised
- Multi-tenant clusters where teams shouldn't access each other's services

**Important:** Network Policies only work if your cluster has a CNI plugin that supports them (Calico, Cilium, Weave Net). If you're using a basic flannel setup, policies will be created but NOT enforced.

---

## 🔒 Deny All Traffic

"Lock everything down first, then open specific doors."

This is the starting point for a secure setup — deny all ingress and egress for every pod in the namespace.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: production
spec:
  podSelector: {}       # Empty = applies to ALL pods in this namespace
  policyTypes:
  - Ingress             # Block all incoming traffic
  - Egress              # Block all outgoing traffic
```

**In plain English:** "No pod in the production namespace can receive traffic from anyone, and no pod can send traffic to anyone." You then create specific policies to allow only what's needed.

**When to use:** Always start with this in production. It's the "deny by default, allow explicitly" approach — same philosophy as traditional firewalls.

---

## ✅ Allow Specific Traffic

"Only the frontend can talk to the backend, and only on port 8080."

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend          # This policy applies to backend pods
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend     # Only allow traffic FROM frontend pods
    ports:
    - protocol: TCP
      port: 8080            # Only on port 8080
```

**In plain English:** "Backend pods can receive incoming traffic, but ONLY from pods labeled `app: frontend`, and ONLY on port 8080. Everything else is still blocked."

**When to use:** Standard three-tier architecture — frontend talks to backend, backend talks to database. Each layer only accepts connections from the layer above it.

---

## 🌐 Allow External Traffic

"Allow traffic from the internet, except from a specific internal network."

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-external
spec:
  podSelector:
    matchLabels:
      app: web              # Applies to web pods
  policyTypes:
  - Ingress
  ingress:
  - from:
    - ipBlock:
        cidr: 0.0.0.0/0          # Allow from anywhere
        except:
        - 192.168.1.0/24          # Except this internal range
    ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 443
```

**In plain English:** "Web pods can receive traffic from any IP address on ports 80 and 443, except from the 192.168.1.0/24 network."

**When to use:**
- Public-facing web servers that need internet access
- When you want to block specific IP ranges (known bad actors, internal networks that shouldn't hit public endpoints directly)

---

## 🔄 Allow DNS

"Let all pods resolve DNS names, otherwise nothing works."

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
spec:
  podSelector: {}           # All pods
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system   # DNS runs in kube-system
    ports:
    - protocol: UDP
      port: 53                # DNS uses UDP port 53
```

**In plain English:** "Every pod is allowed to send DNS queries (UDP port 53) to the kube-system namespace where CoreDNS lives."

**When to use:** ALWAYS include this when you have a deny-all egress policy. Without DNS, your pods can't resolve service names like `backend-service.production.svc.cluster.local` — they just see timeouts. This is the most common mistake people make with network policies.

---

## Common Patterns Summary

| Scenario | What to do |
|---|---|
| Start fresh in production | Deny all, then whitelist |
| Frontend → Backend only | Ingress policy on backend allowing frontend label |
| Backend → Database only | Ingress policy on database allowing backend label |
| Allow internet to web tier | ipBlock with 0.0.0.0/0 on specific ports |
| Pods need DNS | Always allow egress to kube-system on UDP 53 |
| Cross-namespace communication | Use `namespaceSelector` in addition to `podSelector` |

---

## ⏭️ Next: [Module 18: Custom Resources (CRDs)](./18-custom-resources.md)
