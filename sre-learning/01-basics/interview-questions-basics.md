# SRE Basics — Interview Questions

---

## Q1: What is SRE and how is it different from DevOps?
**A:** SRE (Site Reliability Engineering) applies software engineering to operations problems, originated at Google. DevOps is a culture/philosophy of breaking down Dev-Ops silos; SRE is a concrete implementation of it with specific practices — SLOs, error budgets, toil elimination. Google's framing: "class SRE implements interface DevOps."

## Q2: What are SLIs, SLOs, and SLAs?
**A:** SLI is the measurement (e.g., 99.95% of requests succeeded). SLO is the internal target (e.g., aim for 99.9%). SLA is a contractual promise to customers with penalties (e.g., 99.5% or you get credits). Relationship: SLA < SLO < actual performance, so there's a buffer before breaching contracts.

## Q3: Why is 100% reliability the wrong target?
**A:** It's exponentially expensive, and users can't tell the difference — their own network is less reliable than 99.99%. Chasing 100% also means never shipping features (all change is risk). Instead, pick a realistic SLO and spend the allowed unreliability as an error budget.

## Q4: What is an error budget?
**A:** Error budget = 100% − SLO. It's the amount of unreliability you're allowed. It turns reliability into a budget you can spend on risky feature launches. Budget remaining → ship fast; budget exhausted → freeze risky releases and focus on reliability. It resolves the dev-velocity vs ops-stability tension with data.

## Q5: What is toil?
**A:** Manual, repetitive, automatable work that scales with the system and adds no enduring value — like manually restarting services. SREs aim to eliminate toil through automation, capping it at 50% of their time (the 50% rule).

## Q6: What are the Four Golden Signals?
**A:** Latency, Traffic, Errors, and Saturation. They're the four metrics to monitor for any user-facing system. If you could only monitor four things, monitor these.

## Q7: Difference between monitoring and observability?
**A:** Monitoring answers known questions with pre-defined dashboards/alerts ("is it broken?"). Observability lets you explore unknown questions to understand "why is it broken?" via the three pillars: metrics, logs, and traces.

## Q8: What are the three pillars of observability?
**A:** Metrics (numbers over time), logs (discrete events), and traces (the path of one request across services). Metrics tell you something's wrong, logs tell you what happened, traces tell you where.

## Q9: How do you decide what to alert on?
**A:** Alert on symptoms (user impact) not causes (one server's CPU), alert on SLO burn rate rather than every metric blip, and make every alert actionable. Non-actionable alerts cause fatigue and get ignored.

## Q10: What is the 50% rule?
**A:** SREs should spend no more than 50% of their time on operational work (toil, on-call, tickets) and at least 50% on engineering (automation, tooling). Exceeding 50% toil is a signal to push work back to dev or invest in automation.

## Q11: How do you decide whether to automate a task?
**A:** Economically — automate when the time saved over the automation's lifetime exceeds the cost to build and maintain it. A frequent, expensive task is worth automating; a rare, quick one isn't.

## Q12: What does "blameless" mean in SRE?
**A:** Post-mortems focus on systemic causes, not blaming individuals. People make mistakes; the goal is to fix the system that allowed the mistake. Blame makes people hide problems, which is far more dangerous than the mistakes themselves.

## Q13: What is burn rate?
**A:** How fast you're consuming your error budget. A 10x burn rate means you'll exhaust the budget 10x faster than sustainable. Fast burn → page immediately; slow burn → ticket. Burn-rate alerting is the modern SLO-based approach.

## Q14: How many nines is 99.9%, in downtime?
**A:** 99.9% ("three nines") allows about 8.76 hours of downtime per year, or ~43 minutes per month. Each additional nine reduces allowed downtime by ~10x and costs exponentially more.

## Q15: What does an SRE actually do day-to-day?
**A:** Define/track SLOs and error budgets, build monitoring and alerting, automate operations to reduce toil, lead incident response and write blameless post-mortems, do capacity planning, and partner with dev teams on production readiness — spending at least half their time on engineering.
