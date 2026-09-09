# SRE (Site Reliability Engineering) Learning Path

A structured guide to Site Reliability Engineering — from fundamentals to running reliability at scale.

## 📁 Structure

### 01 - Basics
| # | Topic | File |
|---|-------|------|
| 01 | What is SRE | `01-basics/01-what-is-sre.md` |
| 02 | SLIs, SLOs, and SLAs | `01-basics/02-sli-slo-sla.md` |
| 03 | Error Budgets | `01-basics/03-error-budgets.md` |
| 04 | Monitoring & Observability | `01-basics/04-monitoring-observability.md` |
| 05 | Toil & Automation | `01-basics/05-toil-and-automation.md` |
| — | Interview Questions | `01-basics/interview-questions-basics.md` |

### 02 - Intermediate
| # | Topic | File |
|---|-------|------|
| 06 | Incident Management | `02-intermediate/06-incident-management.md` |
| 07 | Blameless Post-Mortems | `02-intermediate/07-postmortems.md` |
| 08 | On-Call Best Practices | `02-intermediate/08-on-call.md` |
| 09 | Capacity Planning | `02-intermediate/09-capacity-planning.md` |
| — | Interview Questions | `02-intermediate/interview-questions-intermediate.md` |

### 03 - Advanced
| # | Topic | File |
|---|-------|------|
| 10 | Reliability & Resilience Patterns | `03-advanced/10-reliability-patterns.md` |
| 11 | Chaos Engineering | `03-advanced/11-chaos-engineering.md` |
| 12 | SRE at Scale & Org Models | `03-advanced/12-sre-at-scale.md` |
| — | Interview Questions | `03-advanced/interview-questions-advanced.md` |

### 🧪 Hands-On Labs (`sre-practice/`)
| Lab | Topic | What You Build |
|-----|-------|----------------|
| 01 | SLO & Error Budget | Error budget + burn-rate calculator |
| 02 | Monitoring | Service instrumented with Golden Signals |
| 03 | Incident Response | Incident simulation + post-mortem generator |
| 04 | Reliability Patterns | Circuit breaker + retry with backoff |
| 05 | Chaos Engineering | Controlled pod-kill experiment |

## 🎯 Learning Path

```
Basics (the foundations)
  → What is SRE → SLIs/SLOs/SLAs → Error Budgets → Monitoring → Toil
        │
Intermediate (running services)
  → Incident Management → Post-Mortems → On-Call → Capacity Planning
        │
Advanced (resilience & scale)
  → Reliability Patterns → Chaos Engineering → SRE at Scale
```

## 🔑 Key Concepts Covered

- SRE vs DevOps, embracing risk
- SLIs, SLOs, SLAs, error budgets, burn rate
- Monitoring vs observability, Four Golden Signals, RED/USE
- Toil elimination and the 50% rule
- Incident management, Incident Commander, MTTR
- Blameless post-mortems, 5 Whys
- Sustainable on-call, alert hygiene
- Capacity planning, auto-scaling, headroom
- Reliability patterns (circuit breaker, retry, bulkhead, graceful degradation)
- Chaos engineering, game days
- SRE at scale, platform engineering, production readiness reviews
