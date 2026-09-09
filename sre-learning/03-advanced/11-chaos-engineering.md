# Chaos Engineering

## Overview

Chaos engineering is the practice of deliberately injecting failures into a system to discover weaknesses before they cause real outages. It's proactive reliability testing.

## 📖 Understanding Chaos Engineering (Intuition First)

Fire drills exist because the worst time to discover your fire escape plan doesn't work is during an actual fire. You'd rather find the locked emergency exit during a calm, controlled drill than when the building is burning. Chaos engineering applies this exact logic to software: deliberately cause failures on purpose, in a controlled way, so you discover your system's weaknesses *before* a real outage discovers them for you at 3 AM.

The counterintuitive core idea is that **you make systems more reliable by intentionally breaking them.** It sounds reckless, but it's the opposite. Every distributed system has hidden assumptions — "this dependency will always respond," "we'll never lose two instances at once," "failover works." Those assumptions are usually untested hope. Chaos engineering turns hope into evidence by actually killing an instance, injecting latency, or cutting a network connection and observing whether the system survives as designed. If it doesn't, you've found a bug in a controlled setting instead of a catastrophe in production.

Netflix pioneered this with **Chaos Monkey** — a tool that randomly terminates production instances during business hours. Why on purpose, in production, during the day? Because it forces engineers to build systems that tolerate instance failure as a normal event, and it surfaces problems while everyone's awake and watching, rather than at 3 AM. If your system can survive Chaos Monkey randomly killing servers all day, it'll survive a real server dying.

The discipline is scientific, not reckless. You form a **hypothesis** ("if we kill one instance, traffic reroutes and users see no impact"), define a **blast radius** (start tiny — one instance, staging first), run the **experiment** while closely monitoring, and either confirm your system is resilient or discover a weakness to fix. It's controlled experimentation with a safety net (an "abort button" to stop immediately), not randomly smashing things.

The mature mindset shift: **failures are not rare surprises to fear, but normal events to be prepared for.** A team practicing chaos engineering builds anti-fragility — their systems and their people get better at handling failure because they practice it regularly. When a real incident hits, it's familiar territory, not uncharted panic.

---

## Principles of Chaos Engineering

```
1. Build a HYPOTHESIS about steady-state behavior
   "Under normal conditions, 99.9% of requests succeed"

2. Introduce REAL-WORLD failure events
   Kill instances, inject latency, exhaust resources, drop network

3. Try to DISPROVE the hypothesis
   Does the system maintain steady state during the failure?

4. Minimize BLAST RADIUS
   Start small (staging, one instance), expand as confidence grows

5. Run in PRODUCTION (eventually)
   Only production reveals real behavior — but start safely
```

## Types of Chaos Experiments

```
INFRASTRUCTURE:
  - Terminate instances/pods randomly (Chaos Monkey)
  - Kill an entire availability zone (Chaos Gorilla)
  - Exhaust CPU/memory/disk

NETWORK:
  - Inject latency between services
  - Drop packets / cause network partitions
  - Simulate DNS failures

APPLICATION:
  - Make a dependency return errors
  - Slow down a downstream service
  - Corrupt responses

STATE:
  - Fill up disk
  - Exhaust connection pools
  - Clock skew
```

## The Experiment Process

```
1. DEFINE steady state (the metric that means "healthy")
2. HYPOTHESIZE ("killing 1 pod won't affect the steady state")
3. PLAN blast radius + abort conditions (safety first)
4. RUN the experiment (start in staging, then prod off-peak)
5. OBSERVE (did steady state hold? monitor closely)
6. LEARN (if it broke → you found a real weakness to fix)
7. AUTOMATE (run regularly to prevent regression)
```

## Chaos Engineering Tools

| Tool | Purpose |
|------|---------|
| **Chaos Monkey** (Netflix) | Randomly terminate instances |
| **Gremlin** | Commercial, wide range of attacks |
| **LitmusChaos** | CNCF, Kubernetes-native chaos |
| **Chaos Mesh** | CNCF, Kubernetes chaos |
| **AWS FIS** | AWS Fault Injection Simulator (managed) |

## Example: Simple Pod-Kill Experiment (Kubernetes)

```yaml
# LitmusChaos experiment — kill a pod and verify recovery
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: payment-pod-delete
spec:
  appinfo:
    appns: production
    applabel: "app=payment"
  experiments:
  - name: pod-delete
    spec:
      components:
        env:
        - name: TOTAL_CHAOS_DURATION
          value: "60"          # run for 60s
        - name: CHAOS_INTERVAL
          value: "10"          # kill a pod every 10s
        - name: PODS_AFFECTED_PERC
          value: "50"          # blast radius: 50% of pods
      probe:                    # verify steady state during chaos
      - name: check-service-availability
        type: httpProbe
        httpProbe/inputs:
          url: http://payment-service/health
          responseCode: "200"
```

## Game Days

```
A "game day" = a scheduled, team-wide chaos exercise.
- Simulate a major incident (e.g., "the primary DB just died")
- The team responds as if it's real (using runbooks, roles, comms)
- Practices incident response AND finds system weaknesses
- Blameless debrief afterward → improvements

Great for rehearsing before high-stakes events (Black Friday).
```

## Safety First

```
- START in staging, not production
- SMALL blast radius first, expand with confidence
- Have an ABORT button (stop the experiment instantly)
- Run during business hours (people awake to respond)
- Communicate before running (don't surprise the on-call)
- Never experiment without monitoring in place
```

---

## 🎯 Interview Quick Points

- Chaos engineering = **deliberately injecting failures to find weaknesses before real outages do**
- Analogy: fire drills — find the locked exit during a drill, not a real fire
- Counterintuitive core: **you make systems more reliable by intentionally breaking them**
- Netflix's **Chaos Monkey** randomly kills instances (in prod, during the day, on purpose)
- It's scientific: **hypothesis → controlled experiment → observe → learn**, not reckless smashing
- Always **minimize blast radius** (staging first, one instance, then expand) and have an abort button
- Experiment types: kill instances, inject latency, network partitions, resource exhaustion
- Tools: Chaos Monkey, Gremlin, LitmusChaos, Chaos Mesh, AWS FIS
- **Game days** rehearse full incident response for the whole team
- Mindset shift: failures are **normal events to prepare for**, not rare surprises to fear
- Run experiments regularly (automate) to catch reliability regressions

## Next Steps

Continue to [SRE at Scale](12-sre-at-scale.md).
