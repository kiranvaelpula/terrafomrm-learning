# Incident Management

## Overview

Incident management is the structured process of responding to unplanned service disruptions to restore service as quickly as possible while minimizing impact.

## 📖 Understanding Incident Management (Intuition First)

When a building catches fire, you don't want everyone improvising — one person grabbing a hose, another calling for help, a third running in circles. You want the fire department's system: a clear commander, defined roles, a communication plan, and a practiced procedure. Incident management brings that same discipline to production outages, because chaos during an outage makes everything worse and slower.

The core problem incident management solves is that outages are high-stress, high-stakes, and involve multiple people who need to coordinate fast. Without structure, you get the classic failure modes: five engineers all investigating the same thing while nobody looks at the actual root cause; the CEO calling for updates and distracting the very people fixing it; two people making conflicting changes that make it worse. A defined process prevents this by giving everyone a role and a script.

The key idea borrowed from emergency services is the **Incident Commander (IC)** — one person who coordinates the response but doesn't necessarily fix things themselves. The IC's job is to keep the response organized: assign tasks, track what's been tried, manage communication, and make decisions. This frees the technical responders to focus purely on diagnosis and remediation without being interrupted by "any update?" messages. Separating *coordination* from *fixing* is the single biggest lever for calm, fast incident response.

There's also a crucial mindset: during an incident, **the goal is to restore service, not to find the root cause.** These are different activities. If restarting a service or rolling back a deploy gets users working again, do that first — even if you don't yet know *why* it broke. Root cause analysis is important, but it happens *after* in the blameless post-mortem, not while customers are down. Confusing "fix it now" with "understand it fully" costs precious downtime.

Finally, incident management is a *practiced* skill, not a document you write and forget. The best teams run drills (game days, chaos engineering), keep runbooks current, and continuously improve their process through post-mortems. When the real fire comes, muscle memory beats reading the manual.

---

## Incident Severity Levels

```
SEV1 (Critical): Major outage, many users affected, revenue impact
                 → All hands, immediate response, exec awareness
SEV2 (High):     Significant degradation, some users affected
                 → Urgent response, on-call + team
SEV3 (Medium):   Minor issue, limited impact, workaround exists
                 → Handle during business hours
SEV4 (Low):      Cosmetic or negligible impact
                 → Backlog / normal priority
```

## Incident Response Roles

```
INCIDENT COMMANDER (IC): Coordinates, decides, delegates — does NOT fix
COMMUNICATIONS LEAD:     Updates stakeholders/customers, shields responders
OPERATIONS/TECH LEAD:    Actually investigates and remediates
SCRIBE:                  Records timeline of actions and findings

For small incidents, one person may wear several hats.
For SEV1, separate the roles — the IC especially should NOT be fixing.
```

## The Incident Lifecycle

```
1. DETECT     — alert fires / user reports (faster detection = lower MTTR)
2. TRIAGE     — assess severity, declare the incident, page responders
3. RESPOND    — assign IC, form response team, communicate
4. MITIGATE   — RESTORE SERVICE (rollback, scale, failover) — priority #1
5. RESOLVE    — confirm service is healthy
6. POST-MORTEM — blameless analysis, action items (after, not during)
```

## Key Metrics (MTTx)

```
MTTD — Mean Time To Detect    (alert → someone knows)
MTTA — Mean Time To Acknowledge (alert → responder engaged)
MTTR — Mean Time To Resolve/Recover (incident start → service restored)
MTBF — Mean Time Between Failures (reliability measure)

Lowering MTTR is a primary SRE goal — better detection, runbooks,
and automation all reduce it.
```

## Communication During an Incident

```
- Regular cadence updates (even "still investigating" every 30 min)
- Separate the fixers from the communicators (IC shields the team)
- Status page for customers (transparency builds trust)
- Internal channel (Slack/Teams) as single source of truth
- Facts only — no speculation, no blame
```

## Example: Incident Declaration & Tracking

```python
from datetime import datetime
from enum import Enum

class Severity(Enum):
    SEV1 = "Critical"; SEV2 = "High"; SEV3 = "Medium"; SEV4 = "Low"

class Incident:
    def __init__(self, title, severity, commander):
        self.title = title
        self.severity = severity
        self.commander = commander
        self.started = datetime.utcnow()
        self.timeline = []
        self.status = "investigating"

    def log(self, action, who):
        entry = {"time": datetime.utcnow(), "action": action, "who": who}
        self.timeline.append(entry)  # feeds the post-mortem later
        print(f"[{entry['time']:%H:%M:%S}] {who}: {action}")

    def mitigate(self, action, who):
        self.log(f"MITIGATION: {action}", who)
        self.status = "mitigated"

    def resolve(self, who):
        self.status = "resolved"
        duration = (datetime.utcnow() - self.started).seconds // 60
        self.log(f"RESOLVED (MTTR: {duration} min)", who)

# Usage
inc = Incident("Payment API 5xx errors", Severity.SEV1, commander="alice")
inc.log("Detected via error-rate alert", "monitoring")
inc.log("DB connection pool exhausted", "bob")
inc.mitigate("Scaled connection pool + added replicas", "bob")
inc.resolve("alice")
```

---

## 🎯 Interview Quick Points

- Incident management brings **structure to chaos** (like the fire department's system)
- The **Incident Commander coordinates but doesn't fix** — separates coordination from remediation
- During an incident, **restore service first; find root cause later** (in the post-mortem)
- Severity levels (SEV1-4) determine response urgency and who's involved
- Key roles: Incident Commander, Comms Lead, Ops/Tech Lead, Scribe
- **MTTR** (mean time to resolve) is a primary metric SREs work to lower
- Communicate on a regular cadence — even "still investigating" builds trust
- Shield the responders from distraction (comms lead handles stakeholders)
- Practice with game days/chaos engineering — muscle memory beats the manual
- Everything feeds the **blameless post-mortem** (next topic)

## Next Steps

Continue to [Post-Mortems](07-postmortems.md).
