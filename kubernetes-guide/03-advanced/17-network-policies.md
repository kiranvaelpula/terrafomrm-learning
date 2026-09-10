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

## 📖 Understanding Network Policies (Intuition First)

By default a Kubernetes cluster is like an open-plan office with no interior doors — anyone can walk up to anyone else's desk. Every pod can reach every other pod, across every namespace. That openness is great for getting started, but in production it's a serious risk: if an attacker compromises one pod, they can freely probe and reach everything else, including your database. Network Policies are the interior doors and keycards that let you say "only these people can enter this room."

The essential mental model is **firewall rules for pods, expressed in Kubernetes labels instead of IP addresses**. Because pod IPs are ephemeral, you don't write rules like "allow 10.1.2.3." Instead you write "allow pods labeled `app=frontend` to reach pods labeled `app=backend` on port 8080." As pods come and go, the rules keep applying because they're based on identity (labels), not fleeting addresses.

There's a subtle but critical behavior around how policies combine. As long as *no* policy selects a pod, that pod is wide open. The moment *any* policy selects it for a given direction (ingress or egress), that pod becomes **default-deny** for that direction, and only the explicitly listed traffic is allowed. This is why the standard secure pattern is "deny all, then allow specific" — you apply a deny-all policy to lock everything down, then add narrow allow rules that open just the doors you need, exactly like a traditional firewall's whitelist approach.

Policies have two directions that people often confuse. **Ingress** governs traffic *coming into* the selected pods; **egress** governs traffic *going out*. A three-tier app typically uses ingress rules: the backend accepts ingress only from the frontend, the database accepts ingress only from the backend. Egress rules matter when you want to restrict what a pod can call out to — for example, preventing a compromised pod from phoning home to the internet.

Two gotchas are worth burning into memory. First, Network Policies only do anything if your **CNI plugin enforces them** (Calico, Cilium, Weave) — with plain flannel they're silently ignored. Second, if you apply a deny-all egress policy, you **must** explicitly allow DNS (UDP/TCP port 53 to kube-system), or every pod loses the ability to resolve service names and you'll chase mysterious timeouts. This DNS omission is the single most common Network Policy mistake.

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

## 🎯 Interview Quick Points

- By default **all pods can talk to all pods**; Network Policies add pod-level firewall rules
- Rules are based on **labels/selectors**, not IPs, so they survive pod churn
- A pod is **wide open until some policy selects it** — then it becomes default-deny for that direction, allowing only listed traffic
- Standard secure pattern: **deny-all first, then explicitly allow** what's needed
- **Ingress** = incoming traffic to selected pods; **Egress** = outgoing traffic from them
- `podSelector: {}` selects all pods in the namespace
- Use `namespaceSelector` (often with `podSelector`) for cross-namespace rules; `ipBlock` for external CIDR ranges
- Policies are **only enforced by CNI plugins that support them** (Calico, Cilium, Weave) — flannel ignores them
- **Always allow DNS egress** (port 53 to kube-system) when using deny-all egress, or name resolution breaks — the most common mistake
- Network Policies are **namespaced** and additive (no explicit deny rules; absence of allow = denied once selected)
- Primary benefits: workload isolation, compliance segmentation, and limiting breach blast radius

---

## ⏭️ Next: [Module 18: Custom Resources (CRDs)](./18-custom-resources.md)
