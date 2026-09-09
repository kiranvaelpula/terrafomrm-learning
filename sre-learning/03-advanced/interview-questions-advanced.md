# SRE Advanced — Interview Questions

---

## Q1: How do you prevent cascading failures in a distributed system?
**A:** Multiple patterns working together: circuit breakers (stop calling a failing service, fail fast), timeouts (never hang on a dependency), bulkheads (isolate resource pools so one bad dependency can't starve others), graceful degradation (serve reduced experience), and load shedding (drop low-priority requests under extreme load). The goal is to fail partially, not totally.

## Q2: Explain the circuit breaker pattern.
**A:** Like an electrical breaker. It has three states: CLOSED (calls flow normally), OPEN (after too many failures, stop calling and fail fast immediately), and HALF-OPEN (after a cooldown, allow a test call to check recovery). It prevents a broken dependency from hanging every request and exhausting your resources, which would cause a cascade.

## Q3: Why use retries with exponential backoff and jitter?
**A:** Transient failures often succeed on retry, but naive immediate retries can hammer a struggling service and make it worse. Exponential backoff increases the delay between attempts; jitter (randomness) prevents all clients retrying in sync (the "thundering herd" that re-overloads the service).

## Q4: What is chaos engineering and why do it?
**A:** Deliberately injecting failures into a system to find weaknesses before real outages do — like a fire drill. It's scientific: form a hypothesis about steady state, inject a real failure with a minimized blast radius, and verify the system survives. Netflix's Chaos Monkey randomly kills instances to force resilient design.

## Q5: How would you run a chaos experiment safely?
**A:** Start in staging, not production. Minimize blast radius (one instance first, then expand). Define a clear hypothesis and steady-state metric. Have an abort button to stop instantly. Run during business hours with people watching. Communicate to on-call first. Never experiment without monitoring in place.

## Q6: How does SRE scale in a large organization?
**A:** Through leverage, not headcount. A small SRE team builds tools, platforms, and standards that let thousands of developers do reliability work themselves — self-service monitoring, safe deploy pipelines, golden-path templates. You can't hire one SRE per service; that just recreates the ops bottleneck.

## Q7: What is platform engineering and how does it relate to SRE?
**A:** Platform engineering builds an Internal Developer Platform — a paved road of self-service tools, golden paths, and guardrails — so product teams get reliability, deployment, and observability built in without needing an SRE beside them. It's the modern way SRE scales: SREs become platform builders rather than firefighters.

## Q8: What is a Production Readiness Review?
**A:** A checklist a service must meet before going live (or getting SRE support): SLOs defined, monitoring/alerting in place, runbooks written, load tested, failure handling, on-call ownership, tested rollback, capacity plan. It's a scaling tool — it lets SRE define standards without doing the work for every team.

## Q9: Explain "you build it, you run it."
**A:** Teams own the reliability of what they build, rather than SRE owning everything (which doesn't scale). SRE provides the platform, standards, and consultation, and directly owns only the most critical shared services. This keeps SRE from being a bottleneck for every service.

## Q10: What is the bulkhead pattern?
**A:** Named after watertight ship compartments. You isolate resources (thread/connection pools) per dependency so that one overloaded or hung dependency exhausts only its own pool, not the shared resources — keeping the rest of the system healthy. One flooded compartment doesn't sink the ship.

## Q11: How do you handle a dependency that's slow but not fully down?
**A:** This is often more dangerous than a hard failure because requests pile up waiting. Use timeouts (don't wait forever), circuit breakers (trip on slowness/error thresholds), bulkheads (isolate its resource pool), and graceful degradation (serve without it if it's non-critical). Slow dependencies cause resource exhaustion and cascades.

## Q12: What is idempotency and why does it matter for reliability?
**A:** An idempotent operation produces the same result whether done once or many times. It's critical for safe retries — if a network blip causes a payment request to retry, an idempotency key ensures the customer isn't charged twice. Without it, retries (a core reliability pattern) become dangerous.

## Q13: How do you measure the success of an SRE team at scale?
**A:** Not by fires put out, but by fires prevented. Track: % of services with SLOs, % meeting SLOs, platform adoption rate, MTTR trend (decreasing), incidents per service (decreasing), SRE toil % (< 50%), and how much teams can operate self-service. The best SRE org is almost invisible because reliability is built in.

## Q14: How would you improve reliability of an existing unreliable service?
**A:** Start by measuring — define SLIs/SLOs to know current reliability and set a target. Add observability (metrics, logs, traces) to see what's failing. Identify the top failure modes from incidents/post-mortems. Apply reliability patterns (retries, circuit breakers, timeouts, redundancy). Load test to find limits and add capacity/headroom. Use the error budget to justify prioritizing reliability work over features.

## Q15: A service keeps having the same incident repeatedly. How do you handle it?
**A:** Recurring incidents signal that past post-mortem action items weren't completed or the real root cause was never fixed. I'd do a thorough blameless post-mortem using the 5 Whys to find the systemic cause, create concrete action items with owners and due dates, and track them to completion. If it keeps recurring, I'd treat it as an error-budget priority and freeze feature work on that service until it's fixed — and add a chaos experiment or test to prevent regression.
