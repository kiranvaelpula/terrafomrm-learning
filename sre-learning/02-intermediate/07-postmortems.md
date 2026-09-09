# Blameless Post-Mortems

## Overview

A post-mortem is a written record of an incident: what happened, its impact, the root cause, and what will be done to prevent recurrence. "Blameless" means it focuses on systems, not punishing people.

## 📖 Understanding Blameless Post-Mortems (Intuition First)

Imagine two airlines. In the first, when a pilot makes a mistake, they're punished or fired. What happens? Pilots hide their near-misses, cover up errors, and the airline never learns — so the same mistakes keep causing crashes. In the second airline, pilots can report mistakes and near-misses openly without punishment, so the organization learns from every incident and gets safer over time. Aviation chose the second model, and it's why flying is astonishingly safe. Blameless post-mortems bring that exact philosophy to software.

The core insight is subtle but transformative: **people don't cause outages — systems that allow human mistakes to cause outages do.** When an engineer runs a bad command that takes down production, the blameful question is "why did you run that command?" The blameless question is "how did our system allow one command to take down production without a safety check?" The second question leads to real fixes (add a confirmation, a canary, a permission gate); the first just makes the engineer defensive and teaches everyone to hide mistakes.

This matters because of a psychological reality: **blame makes people hide problems, and hidden problems are far more dangerous than known ones.** If your culture punishes the person who caused an outage, the next person who causes one will cover it up, delay reporting, or quietly work around it — and you lose the chance to learn. A blameless culture makes it *safe* to say "I broke it, here's what happened," which is the only way an organization actually improves.

A good post-mortem is a **learning document, not a trial.** It reconstructs the timeline factually, identifies the *systemic* root cause (usually there are several contributing factors, not one villain), honestly assesses the impact, and — most importantly — produces concrete action items with owners and due dates. A post-mortem that just says "we'll be more careful" is worthless; one that says "add a deploy canary (owner: Sam, due: Friday)" prevents the next incident.

The mature nuance: blameless doesn't mean *accountability-free*. Individuals are still responsible for following processes and doing good work. Blameless means we assume everyone acted reasonably given what they knew at the time, and we fix the system rather than scapegoat a person. It separates "understanding what went wrong" (which requires honesty) from "performance management" (a separate conversation).

---

## When to Write a Post-Mortem

```
- Any SEV1 or SEV2 incident (always)
- Any incident that breached an SLO / burned significant error budget
- Any incident with customer impact
- Any "near miss" worth learning from
- When the same issue recurs (why didn't we fix it last time?)
```

## Post-Mortem Template

```markdown
# Post-Mortem: [Incident Title]

## Summary
One paragraph: what happened, impact, duration.

## Impact
- Users affected: X
- Duration: Y minutes
- Error budget consumed: Z%
- Revenue/SLA impact: ...

## Timeline (facts, times in UTC)
- 14:30 — Deploy of v2.3 completed
- 14:32 — Error rate alert fired
- 14:35 — Incident declared (SEV2), IC: Alice
- 14:45 — Root cause identified (connection pool)
- 14:50 — Mitigated (rolled back)
- 14:55 — Resolved

## Root Cause
The systemic cause (usually multiple contributing factors).
Use "5 Whys" to get past symptoms.

## What Went Well
- Fast detection (2 min)
- Clean rollback

## What Went Wrong
- No canary deploy caught this
- Alert took 2 min (could be faster)

## Action Items (with OWNERS and DUE DATES)
| Action | Owner | Due | Priority |
|--------|-------|-----|----------|
| Add canary deployment | Sam | Aug 20 | High |
| Add connection pool alert | Priya | Aug 18 | High |
| Update runbook | Alex | Aug 22 | Medium |

## Lessons Learned
Key takeaways for the whole org.
```

## The 5 Whys (Root Cause Technique)

```
Problem: Payment service went down.

Why? → The connection pool was exhausted.
Why? → A traffic spike opened more connections than the pool allowed.
Why? → The pool size was set for old, lower traffic levels.
Why? → We never revisited it as traffic grew.
Why? → There's no process to review capacity limits as we scale.
                    ↑
        ROOT CAUSE: missing capacity-review process
        (not "the engineer who set the pool size")
```

## Blameless Language

```
❌ Blameful:   "Bob broke production by pushing bad code."
✅ Blameless:  "A change reached production without a canary stage
                that would have caught the regression."

❌ Blameful:   "Why did you run that command?"
✅ Blameless:  "How did our system allow that command to cause an
                outage without a safeguard?"
```

## Action Item Quality

```
❌ Vague:      "Be more careful with deploys"
✅ Concrete:   "Add automated canary analysis to the deploy pipeline
                (owner: Sam, due: Aug 20)"

Rules for action items:
- Specific and measurable
- Has an OWNER (one person accountable)
- Has a DUE DATE
- Tracked to completion (review in next incident/retro)
```

---

## 🎯 Interview Quick Points

- A post-mortem documents what happened, impact, root cause, and prevention
- **Blameless** = focus on the system that allowed the mistake, not the person
- Analogy: aviation's blameless reporting is why flying is so safe
- Core belief: **blame makes people hide problems; hidden problems are more dangerous**
- Ask "how did the system allow this?" not "why did you do this?"
- Use the **5 Whys** to reach the systemic root cause, not just symptoms
- Every post-mortem must produce **action items with owners and due dates**
- Vague action items ("be more careful") are worthless; be specific
- Blameless ≠ accountability-free — it separates learning from performance management
- Write post-mortems for SEV1/SEV2, SLO breaches, customer impact, and recurring issues
- Track action items to completion — an untracked action item is just a wish

## Next Steps

Continue to [On-Call Best Practices](08-on-call.md).
