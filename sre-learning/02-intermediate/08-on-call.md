# On-Call Best Practices

## Overview

On-call is the practice of having engineers available to respond to incidents outside normal hours. Done well, it's sustainable and effective; done badly, it burns people out and drives attrition.

## 📖 Understanding On-Call (Intuition First)

On-call is like being a firefighter on standby. You're living your normal life, but you carry a pager, and when the alarm sounds you must respond quickly — even at 3 AM. It's a necessary reality for any service that needs to be reliable around the clock, because software fails at inconvenient times and someone has to respond. The question isn't *whether* to have on-call, but how to make it humane and effective rather than a source of dread and burnout.

The central tension is between **reliability and human sustainability.** You could achieve fast response by paging someone constantly — but you'd destroy your engineers, who'd quit. Or you could protect people by ignoring alerts — but your service would be unreliable. Good on-call practice threads this needle: respond reliably to *real* problems while ruthlessly eliminating the noise, toil, and unfair load that make on-call miserable.

The biggest enemy of healthy on-call is **alert fatigue.** If the pager cries wolf constantly — false alarms, non-actionable alerts, things that could wait until morning — engineers become numb, start ignoring pages, and eventually miss the real emergency buried in the noise. This is why SRE insists every page must be *urgent and actionable*. If you can't do anything about an alert, or it can wait, it should be a ticket, not a page. Protecting the pager's signal-to-noise ratio is protecting your ability to respond at all.

Sustainability is engineered, not hoped for. Healthy rotations spread the load fairly (Google's guideline: no more than ~2 incidents per on-call shift), compensate on-call fairly, provide good runbooks so responders aren't figuring things out from scratch at 3 AM, and follow up every page with the question "how do we prevent this from paging anyone again?" On-call load that's too high isn't a badge of honor — it's a signal that the system needs more reliability engineering.

The mature view: **on-call is a feedback loop for reliability.** Every page is data. A well-run team treats a noisy on-call rotation as a bug to be fixed — feeding pages back into automation, better alerting, and reliability work until the pager goes quiet. The goal isn't heroic responders who never sleep; it's a system so well-engineered that on-call is boring.

---

## Types of On-Call

```
Primary/Secondary:  Primary responds; secondary is backup if primary misses
Follow-the-sun:     Hand off between geographic regions (no night shifts!)
Rotation:           Team members take turns (e.g., 1 week each)
```

## What Makes On-Call Healthy

```
✅ Fair rotation      — load spread evenly, not always the same people
✅ Sustainable load   — ~≤ 2 incidents per shift (Google guideline)
✅ Actionable alerts  — every page is urgent AND you can act on it
✅ Good runbooks      — clear steps, not figuring it out at 3 AM
✅ Compensation       — on-call is paid/time-off, not free labor
✅ Handoffs           — clean context transfer between shifts
✅ Follow-up          — every page → "how do we prevent this next time?"
✅ Escalation path    — clear who to call if you're stuck
```

## What Makes On-Call Toxic

```
❌ Alert fatigue      — constant non-actionable pages → numbness
❌ Unfair load        — same heroes always on call / always paged
❌ No runbooks        — responders reinvent the wheel every incident
❌ No follow-up       — same issue pages repeatedly, never fixed
❌ No compensation    — resentment, burnout, attrition
❌ Blame culture      — fear of making it worse paralyzes responders
```

## Alert Hygiene (Protecting the Signal)

```
Every alert should pass this test:
  1. Is it URGENT? (needs action now, can't wait for morning)
  2. Is it ACTIONABLE? (the responder can actually do something)
  3. Is it REAL? (not a flaky false positive)

If NO to any → it should NOT page. Make it a ticket or delete it.

Page  = urgent + actionable  → wakes someone up
Ticket = important but not urgent → handled in business hours
Log   = informational → no human action
```

## Runbook Example (What Responders Need)

```markdown
# Runbook: Payment Service High Error Rate

## Alert: PaymentErrorRateHigh
## Severity: SEV2

## Quick Checks (in order)
1. Check dashboard: [link] — is it errors or latency?
2. Recent deploy? `kubectl rollout history deployment/payment`
   → If yes and correlates: `kubectl rollout undo deployment/payment`
3. DB connections maxed? Check [dashboard link]
   → If yes: scale pool or add replicas: `kubectl scale ... --replicas=6`
4. Downstream dependency down? Check [dependency dashboard]

## Escalation
- If not resolved in 15 min → page secondary
- If DB issue → page DBA on-call: [contact]

## Related
- Post-mortems: [links to past similar incidents]
```

## On-Call Load Metrics

```yaml
Track to keep on-call healthy:
  pages_per_shift: aim ≤ 2
  pages_outside_business_hours: minimize
  false_positive_rate: < 5% (else fix alerting)
  actionable_alert_rate: > 95%
  time_to_acknowledge: track for responsiveness
  repeat_pages: same issue paging twice = unfixed root cause
```

---

## 🎯 Interview Quick Points

- On-call = engineers available to respond to incidents outside normal hours
- The tension: **reliability vs human sustainability** — good practice balances both
- **Alert fatigue** is the #1 enemy — noisy pages make people miss real emergencies
- Every page must be **urgent AND actionable AND real** — else make it a ticket
- Sustainable load: Google's guideline is **≤ 2 incidents per shift**
- **Follow-the-sun** rotations avoid night shifts by handing off across regions
- Good runbooks let responders act fast at 3 AM instead of improvising
- On-call should be **compensated** (pay or time off) — not free labor
- Every page is feedback: ask "how do we stop this from paging anyone again?"
- The goal: engineer reliability so well that **on-call is boring**
- Track pages/shift and false-positive rate to keep on-call healthy

## Next Steps

Continue to [Capacity Planning](09-capacity-planning.md).
