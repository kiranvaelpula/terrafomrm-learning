# SRE Hands-On Labs

Practical, implementable labs to apply SRE concepts. Each builds on the learning modules.

## 🧪 Labs Overview

| Lab | Topic | What You Build | Difficulty |
|-----|-------|----------------|------------|
| 01 | SLO & Error Budget Calculator | Track SLOs and error budget burn | Beginner |
| 02 | Monitoring & Golden Signals | Instrument a service with metrics + alerts | Beginner |
| 03 | Incident Response Simulation | Run an incident with roles + timeline | Intermediate |
| 04 | Reliability Patterns | Implement circuit breaker + retry | Intermediate |
| 05 | Chaos Experiment | Kill pods and verify recovery | Advanced |

## 🔧 Prerequisites

```bash
python3 -m venv sre-env
source sre-env/bin/activate      # Linux/macOS
pip install prometheus-client requests flask

# For chaos labs (optional):
# A local Kubernetes (kind/minikube) + LitmusChaos or Chaos Mesh
```

## 🎯 Learning Path

```
Lab 01 (SLOs/error budget) — the SRE foundation
   → Lab 02 (monitoring)
      → Lab 03 (incident response)
         → Lab 04 (reliability patterns)
            → Lab 05 (chaos engineering)
```

Each lab folder has a README (objective, steps, exercises) and runnable code.
