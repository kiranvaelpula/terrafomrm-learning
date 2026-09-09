# What is SRE?

## Overview

**SRE** (Site Reliability Engineering) is a discipline that applies software engineering practices to IT operations problems, with the goal of creating scalable and highly reliable software systems. It originated at Google.

## 📖 Understanding SRE (Intuition First)

Imagine a busy restaurant. In a traditional setup, the kitchen (developers) cooks food and throws it over a wall to the waiters (operations), who deal with hungry, angry customers when something goes wrong. The two teams blame each other — "the food was fine when it left the kitchen!" versus "you sent it out cold!" This wall between "build it" and "run it" is exactly the old Dev vs Ops divide, and it's slow, tense, and unreliable.

SRE tears down that wall by asking a radical question: *what if operations was a software engineering problem?* Instead of humans manually restarting servers and fighting fires at 3 AM, what if we wrote software to make systems heal themselves, and treated reliability as a feature we engineer — measurably, deliberately — rather than hope for?

Google coined the famous line: *"SRE is what happens when you ask a software engineer to design an operations team."* An SRE is someone who can write code AND run systems, and who spends their time automating away the manual toil rather than doing it by hand forever. The whole philosophy is to replace human effort and heroics with engineering.

The other radical SRE idea is that **100% reliability is the wrong target**. It's counterintuitive — surely more reliable is always better? But chasing perfection is astronomically expensive and pointless, because your users can't even tell the difference between 99.99% and 100% (their own wifi is less reliable than that). So SRE says: pick a realistic reliability target, and use the "allowed" unreliability as a *budget* to spend on shipping features fast. This "error budget" concept is what makes SRE both reliable AND fast, resolving the eternal tension between the two.

So at its heart, SRE is about **making reliability measurable, engineering it deliberately, automating away toil, and balancing reliability against velocity with data instead of arguments.** It's ops reimagined by engineers.

---

## SRE vs DevOps

People often confuse these. A useful framing:

```
DevOps = a PHILOSOPHY/culture (break down Dev-Ops silos, automate, collaborate)
SRE    = a specific IMPLEMENTATION of that philosophy (with concrete practices)

"class SRE implements interface DevOps"  ← Google's own analogy
```

| Aspect | DevOps | SRE |
|--------|--------|-----|
| Nature | Culture/philosophy | Concrete engineering discipline |
| Focus | Dev + Ops collaboration | Reliability as an engineering goal |
| Defines | Principles | Specific practices (SLO, error budget, toil) |
| Metrics | Varies | SLIs, SLOs, error budgets |
| Origin | Community movement | Google |

---

## Core SRE Principles

```
1. Embrace risk — 100% reliability is the wrong target; use error budgets
2. Service Level Objectives (SLOs) — define and measure reliability
3. Eliminate toil — automate repetitive manual work
4. Monitoring & observability — you can't fix what you can't see
5. Automation — engineer away manual operations
6. Release engineering — safe, repeatable deployments
7. Simplicity — complexity is the enemy of reliability
8. Blameless culture — learn from failures, don't punish
```

## What SREs Actually Do

```
- Define and track SLIs/SLOs/error budgets
- Build monitoring, alerting, and dashboards
- Automate operations (self-healing, auto-scaling, runbooks)
- Lead incident response and write blameless post-mortems
- Do capacity planning and performance engineering
- Reduce toil through engineering
- Partner with dev teams on reliability (production readiness reviews)
- Manage on-call in a sustainable way
```

## The 50% Rule

```
Google's guideline: SREs should spend
  ≤ 50% of time on OPERATIONS (toil, on-call, tickets)
  ≥ 50% of time on ENGINEERING (automation, tools, improvements)

If ops work exceeds 50%, that's a signal to push work back to dev
or invest in more automation. This prevents SRE from becoming
a pure ops team drowning in toil.
```

---

## 🎯 Interview Quick Points

- SRE = applying software engineering to operations problems (originated at Google)
- Famous definition: "what happens when you ask a software engineer to design an operations team"
- **DevOps is the philosophy; SRE is a concrete implementation** of it
- **100% reliability is the wrong target** — it's expensive and users can't tell
- **Error budgets** use allowed unreliability as a budget to ship features fast
- Core concepts: **SLIs, SLOs, error budgets, toil elimination, blameless culture**
- The **50% rule** — SREs cap ops work at 50%, spend the rest engineering
- SRE resolves the reliability-vs-velocity tension with data, not arguments
- Key mindset: automate away toil rather than doing manual work forever
- Blameless post-mortems — learn from failure without punishing people

## Next Steps

Continue to [SLIs, SLOs, and SLAs](02-sli-slo-sla.md).
