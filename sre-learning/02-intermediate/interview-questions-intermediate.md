# SRE Intermediate — Interview Questions

---

## Q1: Walk me through your incident response process.
**A:** Detect (alert/report) → triage (assess severity, declare) → respond (assign Incident Commander, form team) → mitigate (restore service — rollback/scale/failover) → resolve (confirm healthy) → blameless post-mortem. The IC coordinates but doesn't fix; a comms lead shields responders. Priority during the incident is restoring service, not finding root cause.

## Q2: What is the role of an Incident Commander?
**A:** To coordinate the response — assign tasks, track what's tried, manage communication, make decisions — WITHOUT personally fixing things. Separating coordination from remediation lets technical responders focus. Especially important for SEV1s.

## Q3: During an incident, do you find the root cause first or restore service first?
**A:** Restore service first. If a rollback or restart gets users working again, do it even without knowing why it broke. Root cause analysis happens afterward in the blameless post-mortem. Confusing "fix now" with "fully understand" costs downtime.

## Q4: What is a blameless post-mortem and why is it important?
**A:** A post-mortem that focuses on the system that allowed a mistake, not on punishing the person. It's important because blame makes people hide problems, and hidden problems are more dangerous than known ones. Like aviation's blameless reporting, it lets the org learn and improve safety.

## Q5: How do you find the root cause of an incident?
**A:** Techniques like the 5 Whys — keep asking "why" past the symptoms until you reach a systemic cause (e.g., "no process to review capacity limits" rather than "the engineer set the wrong value"). Usually there are multiple contributing factors, not one villain.

## Q6: What makes a good action item in a post-mortem?
**A:** Specific, measurable, with an owner and a due date, and tracked to completion. "Be more careful" is worthless; "add a deploy canary (owner: Sam, due Friday)" prevents recurrence.

## Q7: How do you make on-call sustainable?
**A:** Eliminate alert fatigue (every page urgent + actionable + real), spread load fairly (≤ ~2 incidents/shift), provide good runbooks, compensate on-call, follow up every page with "how do we prevent this," and treat a noisy rotation as a bug to fix through reliability engineering.

## Q8: How do you reduce alert fatigue?
**A:** Only page for alerts that are urgent AND actionable AND real. Non-urgent → ticket. Non-actionable → delete or fix. Alert on symptoms (user impact) and SLO burn rate, not every metric blip. Track false-positive rate and fix noisy alerts.

## Q9: What's the difference between a page and a ticket?
**A:** A page wakes someone up for something urgent and actionable that can't wait. A ticket is for important-but-not-urgent work handled during business hours. Mis-categorizing non-urgent things as pages causes burnout.

## Q10: How do you approach capacity planning?
**A:** Measure current usage, forecast future demand (growth + known events), load test to find per-instance limits, calculate needed capacity, add headroom (N+1/N+2 + spike buffer), configure auto-scaling, and revisit regularly. Running out of capacity is a reliability failure.

## Q11: Vertical vs horizontal scaling?
**A:** Vertical = bigger instance (simple but has a ceiling and resize downtime). Horizontal = more instances (scales further, no single-instance limit, enables HA). Horizontal is generally preferred; auto-scaling automates it based on demand.

## Q12: How much headroom should you keep?
**A:** Enough to survive instance failures (N+1 or N+2 redundancy) plus a buffer for traffic spikes, since auto-scaling takes time to react. A common target is running at ~50-70% utilization so there's room to absorb spikes.

## Q13: What metrics do you track for incidents?
**A:** MTTD (time to detect), MTTA (time to acknowledge), MTTR (time to resolve), and MTBF (time between failures). Lowering MTTR is a primary SRE goal, achieved via better detection, runbooks, and automation.

## Q14: How do you communicate during a major incident?
**A:** Regular cadence updates (even "still investigating"), a comms lead who shields responders from distraction, a customer status page for transparency, a single internal source of truth, and facts only — no speculation or blame.

## Q15: How do you prepare for a known high-traffic event (e.g., Black Friday)?
**A:** Forecast the expected peak, load test to that level plus headroom, pre-scale capacity ahead of demand, run a game day to rehearse, freeze risky changes before the event, ensure on-call coverage and runbooks are ready, and have rollback plans prepared.
