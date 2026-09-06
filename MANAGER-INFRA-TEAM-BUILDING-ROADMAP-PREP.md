# Engineering Manager Interview Prep — Building an Infrastructure Team & Roadmap

**Focus**: Setting up a new infrastructure/platform team from scratch, building the roadmap, hiring, and rolling out capabilities for new requirements
**Format**: Framework → Roadmap → Interview Q&As

---

## 🎯 How to Answer This Question

When an interviewer asks *"How would you set up a new infrastructure team / roadmap for new requirements?"* they are testing three dimensions at once:

1. **People** — how you hire, structure, and grow the team
2. **Process** — how you plan, prioritize, and operate
3. **Technology** — the actual infrastructure roadmap

The winning answer is structured, phased, and balances all three. Don't jump straight to "I'd set up Kubernetes." Start with understanding the business need, then people, then process, then technology — in that order.

**The golden framing:** *"I start with the business goals and requirements, not the technology. Technology serves the business, not the other way around."*

---

## 📖 PART 1: The Discovery Phase (Before Any Roadmap)

Never propose a roadmap without understanding the context first. Say this explicitly in an interview — it shows maturity.

```
Questions I'd answer first:
├── What are the BUSINESS goals? (growth, cost, compliance, speed?)
├── What are the REQUIREMENTS? (scale, latency, regions, security?)
├── What EXISTS today? (current infra, tech debt, tools)
├── What's the TEAM situation? (size, skills, gaps)
├── What's the TIMELINE and BUDGET?
├── Who are the STAKEHOLDERS? (dev teams, security, finance, leadership)
└── What are the CONSTRAINTS? (compliance, existing contracts, skills)
```

**Interview line:** *"I'd spend the first few weeks listening — 1:1s with stakeholders, auditing what exists, understanding the real requirements — before committing to a roadmap. Building on wrong assumptions is the most expensive mistake."*

---

## 📖 PART 2: The Phased Roadmap (Crawl → Walk → Run)

Present the roadmap in phases, not a giant list. This shows you deliver incrementally and prove value early.

### Phase 0: Foundation (Month 0-1)
```
- Understand requirements and current state (discovery)
- Define team structure and hire/allocate people
- Establish ways of working (agile cadence, on-call, docs)
- Set up source control, basic CI/CD, cloud accounts
- Define guardrails: security baseline, tagging, naming standards
```

### Phase 1: Core Platform (Month 2-4)
```
- Infrastructure as Code (Terraform) — everything version-controlled
- Cloud landing zone (accounts, networking, IAM, org structure)
- CI/CD pipelines for the dev teams
- Container platform (ECS/EKS) if needed
- Centralized secrets management (Vault / Secrets Manager)
- Basic observability (metrics, logs, dashboards)
```

### Phase 2: Reliability & Scale (Month 4-8)
```
- Monitoring, alerting, SLOs/SLIs
- Auto-scaling and high availability
- Disaster recovery / backup strategy
- Security hardening (scanning, least privilege, compliance)
- Self-service platform for dev teams (paved road)
- Cost management / FinOps practices
```

### Phase 3: Optimization & Maturity (Month 8+)
```
- Platform engineering (internal developer platform)
- Advanced automation (auto-remediation, policy-as-code)
- Multi-region / DR maturity
- Continuous cost optimization
- GitOps, progressive delivery (canary/blue-green)
- Metrics-driven improvement (DORA metrics)
```

**Interview line:** *"I sequence for early value — a working CI/CD pipeline and IaC in the first couple months proves the team's worth and builds trust, before tackling the harder reliability and scale work."*

---

## 📖 PART 3: Building the Team (People)

### Team Structure

```
Infrastructure / Platform Team (example for a mid-size org)
├── Team Lead / EM (you)
├── Senior Infra/Platform Engineers (2-3) — design, mentor, hard problems
├── Mid-level Engineers (2-3) — build and operate
├── SRE / Reliability focus (1-2) — monitoring, incident response, SLOs
└── Security/Cloud specialist (1) — or embed security via DevSecOps
```

### Hiring Strategy

```
1. Prioritize by roadmap needs — hire for the NEXT phase, not everything at once
2. Start with senior anchors — they set standards and mentor
3. Balance skills — cloud, IaC, networking, security, automation, coding
4. Culture fit — collaborative, ownership mindset, blameless attitude
5. Mix of build (new) and run (operate) mindsets
6. Consider build vs buy vs contract for specialized gaps
```

### Skills Matrix to Cover

| Area | Skills needed |
|------|--------------|
| Cloud | AWS/Azure/GCP, networking, IAM |
| IaC | Terraform, CloudFormation |
| Containers | Docker, Kubernetes/ECS |
| CI/CD | Jenkins/GitHub Actions/GitLab |
| Observability | Prometheus, Grafana, ELK, tracing |
| Security | DevSecOps, secrets, compliance |
| Scripting | Python, Bash, Go |
| Reliability | SRE practices, SLOs, incident mgmt |

**Interview line:** *"I hire against the roadmap — bring in senior anchors first to set standards, then build out around them. I look for ownership mindset and collaboration as much as raw technical skill."*

---

## 📖 PART 4: Ways of Working (Process)

```
1. AGILE CADENCE — sprints or Kanban (Kanban often fits infra/ops better)
2. ON-CALL rotation — sustainable, with runbooks and blameless post-mortems
3. DOCUMENTATION — everything documented (runbooks, architecture, decisions/ADRs)
4. INTAKE PROCESS — how dev teams request infra (self-service where possible)
5. STANDARDS — IaC everywhere, peer review, tagging, naming, security baselines
6. METRICS — track DORA metrics (deploy frequency, lead time, MTTR, change fail rate)
7. FEEDBACK — regular retros, treat internal dev teams as customers
```

**Key philosophy — "Platform as a Product":** The infra team's customers are the developers. Build a **paved road** (self-service, standardized, easy) so dev teams move fast safely, rather than the infra team being a ticket-driven bottleneck.

---

## 📋 PART 5: Interview Q&As

### Q1: How would you set up a new infrastructure team and roadmap for new requirements?

**Sample Answer:**
"I'd approach it in four layers: discovery, people, process, then technology — in that order.

First, **discovery** — I don't propose a roadmap on day one. I spend the first few weeks understanding the business goals, the actual requirements (scale, compliance, timeline, budget), what already exists, and the team's current skills. Building on wrong assumptions is the costliest mistake.

Second, **people** — I define the team structure and hire against the roadmap, starting with senior anchors who set standards and mentor, then building around them. I cover the key skill areas: cloud, IaC, containers, CI/CD, observability, security.

Third, **process** — I establish ways of working: an agile cadence, sustainable on-call with blameless post-mortems, documentation standards, and an intake process for dev teams. I treat the platform as a product and dev teams as customers.

Fourth, **technology** — I sequence the roadmap in phases for early value: Foundation (IaC, CI/CD, cloud landing zone), then Reliability & Scale (monitoring, HA, DR, security), then Optimization (self-service platform, cost management, advanced automation). I deliver a working pipeline early to prove value and build trust before the harder work.

Throughout, I'd measure with DORA metrics and iterate. The key principle is: start with business goals, sequence for early value, and build a paved road so dev teams move fast safely."

---

### Q2: How do you prioritize what to build first?

**Sample Answer:**
"I prioritize by business impact and dependency. Foundational capabilities come first because everything else depends on them — you can't do reliable deployments without IaC and CI/CD. Then I look at what unblocks the most people or removes the biggest risk. A value-vs-effort matrix helps: quick, high-value wins first to build momentum and trust. I also weigh risk — if there's a compliance deadline or a stability crisis, that jumps the queue. I validate priorities with stakeholders so it's not just my opinion."

---

### Q3: How do you balance delivering features vs building infrastructure/paying down tech debt?

**Sample Answer:**
"It's a constant negotiation, and I make the tradeoff visible rather than hiding it. I'd allocate a percentage of capacity to platform/tech-debt work — often 20-30% — so it doesn't get perpetually deprioritized. I frame infrastructure investment in business terms: 'this reduces deployment time 50%' or 'this prevents the outages that cost us last quarter.' Leadership supports infra work when they see it as an enabler of feature velocity, not a competing cost. And I pick infrastructure work that unblocks feature teams, so the two goals align."

---

### Q4: How do you handle the transition from the old setup to the new one?

**Sample Answer:**
"Incrementally, never big-bang. I'd run old and new in parallel, migrate workloads in waves starting with low-risk ones, prove the new approach on a pilot, and keep rollback options. I'd bring the team and stakeholders along with clear communication so nobody's surprised. The Strangler Fig pattern applies to infrastructure too — gradually replace the old system piece by piece rather than a risky cutover. And I'd standardize with IaC so the new environment is reproducible and auditable."

---

### Q5: What if you inherit a team with skill gaps for the new requirements?

**Sample Answer:**
"I assess honestly, then close gaps through a mix of upskilling, hiring, and temporary help. I'd invest in training and pair less-experienced engineers with seniors on real work — people grow fastest on stretch assignments with a safety net. For urgent specialized gaps, I might bring in a contractor or consultant short-term while the team ramps. I'd also make build-vs-buy decisions realistically — sometimes a managed service beats building in-house when the team lacks depth in that area. The goal is to meet the roadmap without burning out the team or blocking on hiring."

---

### Q6: How do you measure the success of the infrastructure team?

**Sample Answer:**
"I use DORA metrics as the backbone: deployment frequency, lead time for changes, mean time to recovery, and change failure rate — they tie infra work to delivery outcomes. Beyond those: system reliability (uptime, SLO adherence), cost efficiency (unit economics, waste reduction), security posture, and developer satisfaction — since dev teams are our customers, their ability to ship fast and safely is a direct measure of our success. And team health — sustainable on-call, low attrition. I avoid vanity metrics like 'number of tickets closed.'"

---

### Q7: How do you make the infrastructure team an enabler rather than a bottleneck?

**Sample Answer:**
"By building a **paved road** — self-service, standardized infrastructure that dev teams can use without filing tickets and waiting on us. The 'Platform as a Product' mindset: we build golden paths (templates, modules, pipelines) so the easy way is also the safe, compliant way. Guardrails (policy-as-code, IaC modules, cost gates) let teams move fast without breaking things. Ticket-driven ops doesn't scale; self-service with guardrails does. The measure is that dev teams rarely need to wait on us to ship."

---

## 📋 PART 6: Quick-Fire Points

| Question | One-Liner |
|----------|-----------|
| Where do you start? | "Business goals and requirements — not technology. Discovery first." |
| Roadmap structure? | "Phased: Foundation → Reliability/Scale → Optimization. Early value first." |
| Hiring approach? | "Against the roadmap; senior anchors first, then build around them." |
| Team philosophy? | "Platform as a product — dev teams are our customers; build a paved road." |
| Old → new transition? | "Incremental, wave-based, parallel-run, tested rollback. Never big-bang." |
| Feature vs infra balance? | "Reserve ~20-30% capacity; frame infra as a velocity enabler in business terms." |
| Success metrics? | "DORA metrics + reliability + cost + developer satisfaction." |
| Avoid being a bottleneck? | "Self-service + guardrails, not ticket-driven ops." |
| Skill gaps? | "Upskill + hire + contract; make honest build-vs-buy calls." |

---

## 🎯 Final Interview Tips

1. **Structure your answer** — discovery → people → process → technology. Don't ramble.
2. **Start with business, not tech** — the #1 signal of a mature manager.
3. **Phase the roadmap** — show you deliver incremental value, not a big-bang plan.
4. **Balance people/process/tech** — juniors talk only tech; managers cover all three.
5. **"Platform as a product"** — mention treating dev teams as customers; it's a strong signal.
6. **Use real numbers/examples** — a time you built or scaled a team or platform.
7. **Mention guardrails and self-service** — shows you scale beyond ticket-ops.
8. **Close with metrics** — DORA metrics show you measure outcomes, not activity.
