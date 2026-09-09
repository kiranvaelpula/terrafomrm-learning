# Lab 05: Chaos Experiment

## 🎯 Objective
Run a controlled chaos experiment — kill pods and verify the system recovers and maintains its steady state — the scientific way.

## 📋 Prerequisites
```bash
# A local Kubernetes cluster
kind create cluster        # or minikube start

# A sample deployment to experiment on
kubectl create deployment nginx --image=nginx --replicas=3
kubectl expose deployment nginx --port=80
```

## 🧪 Steps

### Step 1: Define the hypothesis & steady state
"If we kill 1 of 3 nginx pods, the service stays available (steady state = HTTP 200) because Kubernetes reschedules it."

### Step 2: Establish steady state
Confirm the service responds normally before injecting failure.

### Step 3: Inject failure (small blast radius)
Run `chaos_experiment.py` — it kills ONE pod and watches recovery.

### Step 4: Observe & learn
Did the service stay available? Did Kubernetes recreate the pod? If not, you found a weakness.

## ✅ Expected Output
```
Steady state check: service responding (3/3 pods ready)
CHAOS: deleting pod nginx-abc123
Watching recovery...
  t+2s: 2/3 pods ready, service still responding ✓
  t+8s: 3/3 pods ready (Kubernetes recreated the pod) ✓
Hypothesis CONFIRMED: service survived pod loss
```

## 🏋️ Exercises
1. Increase blast radius (kill 2 of 3 pods) — does it still hold?
2. Inject latency instead of killing (network chaos)
3. Use LitmusChaos or Chaos Mesh for declarative experiments
4. Run it as a scheduled "game day" and involve the team

## ⚠️ Safety
- Run in a LOCAL/test cluster, never production for this lab
- Start with the smallest blast radius (1 pod)
- Always have monitoring to observe the impact
- Have a way to stop/abort

## 🔑 Key Concepts Practiced
- Chaos engineering scientific method (hypothesis → experiment → observe)
- Steady-state definition
- Blast radius control
- Verifying resilience (self-healing via Kubernetes)
