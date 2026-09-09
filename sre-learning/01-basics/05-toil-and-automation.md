# Toil & Automation

## Overview

Toil is the repetitive, manual, automatable work that scales with your system but adds no lasting value. Eliminating toil through automation is a core SRE responsibility.

## 📖 Understanding Toil & Automation (Intuition First)

Imagine you're bailing water out of a leaky boat with a bucket. You can bail all day — it's real work, it keeps you afloat — but you're not getting anywhere, and if the boat gets bigger, you'll need more and more people bailing forever. **That bucket-work is toil.** It's necessary in the moment, but it's manual, repetitive, and it scales linearly with the size of the problem. The alternative — fixing the leak or installing an automatic pump — is *engineering*. It takes effort up front but then the problem is solved permanently.

SRE draws a sharp line here because operations teams have a natural death spiral: as the system grows, the manual work grows, so they hire more people to do more manual work, who are then too busy doing manual work to build the automation that would eliminate it. They bail faster and faster and never fix the leak. SRE explicitly rejects this by capping toil (the 50% rule) and demanding that engineers spend the freed time building pumps, not buying bigger buckets.

Toil has specific characteristics: it's **manual, repetitive, automatable, reactive, has no enduring value, and scales with system growth.** Restarting a stuck service by hand every night is toil. Manually provisioning a server for each request is toil. Copy-pasting the same runbook steps during every incident is toil. The test is: could a machine do this? If yes, and you keep doing it by hand, it's toil you should automate.

But — and this is the mature nuance — **not all toil is worth automating.** If a task takes 5 minutes and happens once a year, spending two weeks automating it is a waste. The decision is economic: does the time saved over the automation's lifetime exceed the cost to build and maintain it? SREs automate the toil that's frequent and expensive enough to justify it, and consciously tolerate the rest.

The payoff of winning the war on toil is compounding: every bit of toil you automate frees time to automate more, and it makes systems more reliable (machines don't fatigue or fat-finger commands at 3 AM). A team that has automated its toil scales *sub-linearly* — handling 10x the systems without 10x the people. That leverage is the entire economic argument for SRE.

---

## What Counts as Toil?

Toil has these characteristics (the more that apply, the more it's toil):

```
□ Manual        — a human has to do it
□ Repetitive    — done over and over
□ Automatable   — a machine could do it
□ Reactive      — interrupt-driven, not proactive
□ No lasting value — the system isn't better after (just maintained)
□ Scales with growth — more system = more of this work
```

## Toil vs Engineering Work

| Toil | Engineering Work |
|------|------------------|
| Manually restarting services | Building auto-restart/self-healing |
| Hand-provisioning servers | Infrastructure as Code |
| Manually applying the same fix | Automating the fix |
| Copy-pasting runbook steps | Turning the runbook into a script |
| Manually reviewing every deploy | Automated deployment pipeline |

## The 50% Rule

```
SREs should spend:
  ≤ 50% on operational work (toil, on-call, tickets)
  ≥ 50% on engineering (automation, tooling, reliability improvements)

Exceeding 50% toil is a red flag → push work back or automate.
```

## Should You Automate It? (The Economics)

```
Automate when:  time_saved_over_lifetime  >  cost_to_build_and_maintain

Example WORTH automating:
  Task takes 15 min, done daily = 91 hrs/year
  Automation takes 40 hrs to build → pays back in < 6 months ✅

Example NOT worth automating:
  Task takes 5 min, done once a year = 5 min/year
  Automation takes 2 weeks → never pays back ❌
```

## Levels of Automation

```
1. No automation      — human does everything manually
2. Documented         — a runbook tells the human the steps
3. Scripted           — human runs a script that does the steps
4. Self-service       — anyone can trigger it, no expert needed
5. Fully automated    — system does it with no human at all
6. Self-healing       — system detects AND fixes the problem itself

Progress up this ladder over time; you don't need to jump to 6.
```

## Example: Automating a Common Toil Task

```python
#!/usr/bin/env python3
"""Auto-remediate: restart pods stuck in CrashLoopBackOff.
Replaces the toil of an engineer manually checking and restarting."""

from kubernetes import client, config

config.load_incluster_config()
v1 = client.CoreV1Api()

def remediate_crashloops(namespace="production", restart_threshold=5):
    pods = v1.list_namespaced_pod(namespace=namespace)
    for pod in pods.items:
        for cs in (pod.status.container_statuses or []):
            waiting = cs.state.waiting
            if waiting and waiting.reason == "CrashLoopBackOff" \
               and cs.restart_count > restart_threshold:
                print(f"Deleting stuck pod {pod.metadata.name} (will recreate)")
                v1.delete_namespaced_pod(pod.metadata.name, namespace)
                # Log the action for the post-mortem/audit trail

# Run on a schedule — no human needed for this routine toil
```

---

## 🎯 Interview Quick Points

- **Toil** = manual, repetitive, automatable work that scales with the system and adds no lasting value
- Analogy: bailing a leaky boat with a bucket vs fixing the leak (engineering)
- Toil characteristics: manual, repetitive, automatable, reactive, no enduring value, scales with growth
- The **50% rule** caps SRE toil at 50%, freeing time to engineer it away
- Without capping toil, ops teams enter a death spiral: more system → more manual work → no time to automate
- **Not all toil is worth automating** — decide economically (time saved vs cost to build)
- Automation ladder: manual → runbook → script → self-service → fully automated → self-healing
- Automating toil makes systems **more reliable** (no 3 AM human errors) and lets teams scale sub-linearly
- The compounding payoff: automating toil frees time to automate more
- Distinguish toil from genuine engineering/project work in interviews

## Next Steps

Continue to [Incident Management](../02-intermediate/06-incident-management.md).
