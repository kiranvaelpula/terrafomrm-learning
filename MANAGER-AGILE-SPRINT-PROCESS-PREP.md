# Engineering Manager Interview Prep — Agile & Sprint Model Process

**Focus**: Scrum, Sprint Lifecycle, Agile Ceremonies, Metrics
**Format**: Concepts → Process → Interview Questions with Answers

---

## 📖 PART 1: Agile Fundamentals

### What is Agile?

Agile is an iterative approach to software delivery that builds software incrementally in short cycles, rather than delivering everything at the end (Waterfall).

**Agile Manifesto — 4 core values:**
1. **Individuals and interactions** over processes and tools
2. **Working software** over comprehensive documentation
3. **Customer collaboration** over contract negotiation
4. **Responding to change** over following a plan

### Agile vs Waterfall

| Aspect | Waterfall | Agile |
|--------|-----------|-------|
| Approach | Sequential phases | Iterative cycles |
| Delivery | One big release at end | Small frequent releases |
| Change | Hard/expensive to change | Embraces change |
| Feedback | At the end | Continuous |
| Risk | High (discover issues late) | Low (fail fast, adjust) |
| Best for | Fixed, well-known requirements | Evolving requirements |

### Scrum vs Kanban

| Aspect | Scrum | Kanban |
|--------|-------|--------|
| Cadence | Fixed sprints (1-4 weeks) | Continuous flow |
| Roles | PO, Scrum Master, Dev Team | No prescribed roles |
| Commitment | Sprint backlog committed | Pull work as capacity allows |
| Change mid-cycle | Discouraged during sprint | Anytime |
| Metrics | Velocity, burndown | Cycle time, WIP limits |
| Best for | Feature development | Support/ops, unpredictable work |

---

## 📖 PART 2: The Scrum Framework

### The 3 Roles

| Role | Responsibility |
|------|---------------|
| **Product Owner (PO)** | Owns the backlog, prioritizes, defines "what" and "why", represents the customer |
| **Scrum Master** | Facilitates the process, removes blockers, coaches team, shields from distractions |
| **Development Team** | Self-organizing, builds the product, estimates and commits to work |

### The Sprint Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    SPRINT (2 weeks typical)                    │
│                                                                │
│  ┌────────────┐   ┌──────────────────┐   ┌────────┐  ┌──────┐│
│  │  Sprint    │──▶│   Daily Standups  │──▶│ Sprint │─▶│Retro ││
│  │  Planning  │   │  (every day)      │   │ Review │  │      ││
│  └────────────┘   │  + Development    │   │ (demo) │  └──────┘│
│                   │  + Refinement     │   └────────┘         │
│                   └──────────────────┘                       │
│                                                                │
└─────────────────────────────────────────────────────────────┘
        │                                              │
    Backlog                                    Next Sprint
    (ready)                                    Planning
```

### The 5 Scrum Ceremonies

| Ceremony | When | Duration | Purpose | Who |
|----------|------|----------|---------|-----|
| **Sprint Planning** | Start of sprint | 2-4 hrs | Decide what to build this sprint | Whole team |
| **Daily Standup** | Every day | 15 min | Sync, surface blockers | Dev team |
| **Backlog Refinement** | Mid-sprint | 1 hr | Groom & estimate upcoming work | Team + PO |
| **Sprint Review** | End of sprint | 1-2 hrs | Demo working software to stakeholders | Team + stakeholders |
| **Sprint Retrospective** | End of sprint | 1 hr | Improve the process | Dev team + SM |

### The 3 Scrum Artifacts

| Artifact | What it is |
|----------|-----------|
| **Product Backlog** | Prioritized list of ALL desired work (owned by PO) |
| **Sprint Backlog** | Subset of items committed for the current sprint |
| **Increment** | The working, potentially shippable product at sprint end |

---

## 📖 PART 3: Sprint Planning in Detail

### How Sprint Planning Works

```
1. PO presents prioritized backlog items
2. Team discusses each item, asks clarifying questions
3. Team estimates effort (story points)
4. Team pulls items into sprint based on CAPACITY (not wishful thinking)
5. Items broken into tasks
6. Team commits to the Sprint Goal
```

### Estimation Techniques

**Story Points (relative sizing):**
- Estimate complexity/effort relative to other work, not hours
- Common scale: Fibonacci (1, 2, 3, 5, 8, 13, 21)
- Removes false precision of hour estimates

**Planning Poker:**
- Each team member privately picks an estimate
- Reveal simultaneously (avoids anchoring)
- Discuss outliers, re-estimate until consensus

**T-Shirt Sizing:**
- XS, S, M, L, XL for high-level early estimation

### Capacity Planning

```
Team capacity = (team members × sprint days × focus factor) − PTO − meetings − on-call

Example:
5 engineers × 10 days = 50 person-days
Focus factor 70% (meetings, interrupts) = 35 effective days
Minus 3 days PTO = 32 days
Minus on-call rotation = ~28 effective person-days
```

**Key point:** Never plan at 100% capacity. Real capacity accounts for meetings, interrupts, PTO, on-call, and unknowns.

### Definition of Ready vs Definition of Done

| Definition of Ready (DoR) | Definition of Done (DoD) |
|---------------------------|--------------------------|
| Story is clear and understood | Code written and reviewed |
| Acceptance criteria defined | Tests pass (unit + integration) |
| Dependencies identified | Documentation updated |
| Estimated by team | Deployed to staging |
| Small enough for one sprint | Acceptance criteria met |

---

## 📖 PART 4: Sprint Metrics

### Velocity
- Story points completed per sprint (averaged over time)
- Used for forecasting, NOT for comparing teams or as a performance target
- "We average 30 points/sprint" → helps predict how much fits in future sprints

### Burndown Chart
```
Points
 40 │●
    │ ╲___  ← ideal line
 30 │    ╲___●
    │        ╲___
 20 │  actual────●___
    │              ╲___
 10 │                  ●___
    │                      ╲
  0 └──────────────────────●──▶ Days
    1   2   3   4   5   6   7   8   9  10

Shows work remaining vs time. Above the line = behind schedule.
```

### Other Useful Metrics

| Metric | What it tells you |
|--------|-------------------|
| Velocity | How much work fits per sprint (forecasting) |
| Burndown | Progress within a sprint |
| Burnup | Scope + progress (shows scope creep) |
| Cycle time | How long from start to done |
| Lead time | How long from request to delivery |
| Sprint predictability | % of committed work actually completed |
| Escaped defects | Bugs found after release (quality) |

**⚠️ Interview trap:** Never say you use velocity to measure individual performance or compare teams. Velocity is a forecasting tool, not a productivity weapon.

---

## 📋 PART 5: Interview Questions & Answers

### Q1: Walk me through your sprint process.

**Sample Answer:**
"We run two-week sprints. It starts with sprint planning where the PO presents prioritized, refined backlog items and the team pulls in work based on realistic capacity — not ideal capacity. We commit to a sprint goal. During the sprint, we have a 15-minute daily standup focused on blockers, and a mid-sprint refinement session to keep the next sprint's backlog ready. At the end, we demo working software to stakeholders in the sprint review, then hold a retrospective to improve our process. Throughout, I track velocity for forecasting and use a board so status is always visible. I'm pragmatic — if a ceremony stops adding value, we adjust it in the retro."

---

### Q2: How do you handle scope creep during a sprint?

**Sample Answer:**
"The sprint scope is protected once committed — that's the whole point of the sprint boundary. If new work comes in mid-sprint, I ask: is it a true emergency (production down)? If yes, we handle it and something else drops out, transparently. If it's just a new request, it goes to the backlog for the PO to prioritize into a future sprint. I protect the team from constant re-prioritization because context-switching kills productivity. The PO and I manage the backlog; the team focuses on the committed sprint. If scope changes are constant, that's a signal to shorten sprints or move to Kanban."

---

### Q3: What do you do when the team consistently can't finish committed work?

**Sample Answer:**
"First I look at whether we're over-committing. Often teams plan at ideal capacity and ignore meetings, interrupts, and on-call. I'd pull actual velocity data and plan to that number, not optimism. Second, I check if stories are too big — large stories that don't finish should be broken down. Third, I look at whether unplanned work (bugs, support) is eating the sprint, and if so, I'd reserve capacity for it. The retro is where we diagnose this with the team. The goal is predictable delivery, and consistent misses usually mean our planning is wrong, not that the team is slow."

---

### Q4: How do you estimate work? Why story points over hours?

**Sample Answer:**
"We use story points with planning poker. Points measure relative complexity and effort, not hours. The reason is that humans are terrible at estimating absolute time but decent at relative comparison — 'this is about twice as complex as that.' Points also remove the pressure and false precision of hour estimates, and they account for uncertainty. Over a few sprints, velocity emerges and we can forecast reliably. I never convert points to hours or use them to judge individuals — they're a team forecasting tool."

---

### Q5: What's the difference between a Scrum Master and a Project Manager?

**Sample Answer:**
"A Scrum Master is a servant-leader and facilitator — they remove blockers, coach the team on process, and protect it from distractions, but they don't assign work or own the timeline. A traditional Project Manager is more directive — owning scope, schedule, budget, and assigning tasks. In Scrum, the team self-organizes and the PO owns priorities, so the Scrum Master's job is to make the team effective, not to command it. As an EM, I often blend elements — I care about delivery like a PM but lead through empowerment like a Scrum Master."

---

### Q6: How do you run an effective sprint retrospective?

**Sample Answer:**
"Psychological safety first — no blame, or people won't be honest. I use formats like Start/Stop/Continue or What went well/What didn't/What to try. The critical output is one or two concrete action items with an owner and a due date — not a wish list of ten things nobody does. Next retro, we review whether those actions happened. A retro without follow-through is just venting. I also rotate facilitation so the team owns their improvement, not me."

---

### Q7: A stakeholder wants to add a high-priority feature mid-sprint. What do you do?

**Sample Answer:**
"I make the tradeoff explicit rather than just saying yes or no. I'd tell the stakeholder: 'We can bring this in, but the sprint is committed — so something of equal size has to come out. Which would you like to defer?' That turns it into a prioritization decision they own, not a capacity miracle. If it's a genuine production emergency, we handle it immediately and adjust the sprint transparently. The principle is protecting the team's focus while staying responsive to real business needs. Constant mid-sprint injections are a signal to revisit our process."

---

### Q8: How do you decide sprint length?

**Sample Answer:**
"It depends on the team and the work. Two weeks is the sweet spot for most teams — long enough to deliver meaningful work, short enough to get frequent feedback and adjust. One-week sprints suit fast-changing priorities but have high ceremony overhead. Longer sprints (3-4 weeks) reduce overhead but delay feedback and let problems hide longer. I'd also consider release cadence and how volatile requirements are. Whatever we pick, we keep it consistent so velocity is meaningful."

---

### Q9: How do you handle bugs and support work alongside sprint commitments?

**Sample Answer:**
"Unplanned work is real, so I plan for it rather than pretend it won't happen. A few approaches: reserve a percentage of capacity (say 20%) for bugs and support in each sprint; or run a rotating 'support engineer' who handles interrupts so the rest of the team stays focused; or for ops-heavy teams, use Kanban instead of Scrum. Critical production bugs always take priority and we adjust the sprint transparently. The key is not letting unplanned work silently destroy sprint commitments — make it visible and planned for."

---

### Q10: How do you measure if your team is doing well in Agile?

**Sample Answer:**
"I look at a balanced set of signals, not one number. Predictability — do we deliver what we commit? Quality — escaped defects, incident rate. Cycle time — are we getting faster at delivering? Business outcomes — are we shipping things that matter? And team health — engagement, sustainable pace, low attrition. I deliberately avoid using velocity as a target because the moment you weaponize it, teams inflate estimates and it becomes meaningless. Metrics should inform decisions and spark conversations, not judge people."

---

### Q11: How do you transition a team from Waterfall to Agile?

**Sample Answer:**
"Gradually and with buy-in, not by decree. I start by explaining the 'why' — faster feedback, less risk, more adaptability. I'd introduce one thing at a time: start with a backlog and short iterations, add standups, then reviews and retros. I'd bring in a Scrum Master or coach if the org is new to it. I set expectations that early sprints will be rough — velocity is unknown, estimates will be off — and that's normal. I measure improvement over time and celebrate small wins. The biggest challenge is usually cultural — getting stakeholders comfortable with incremental delivery instead of one big plan."

---

### Q12: What's the difference between epics, stories, and tasks?

**Sample Answer:**
```
Epic     → Large body of work spanning multiple sprints
             e.g., "User Authentication System"
   │
   ├── Story  → User-facing feature, fits in one sprint
   │            e.g., "As a user, I can reset my password"
   │      │
   │      ├── Task → Technical work to complete a story
   │      │          e.g., "Create password reset API endpoint"
   │      └── Task → e.g., "Build reset email template"
   │
   └── Story  → e.g., "As a user, I can log in with Google"
```
"Epics are broken into stories, stories into tasks. Stories are written from the user's perspective with acceptance criteria. Tasks are the technical steps engineers create to deliver a story."

---

## 📋 PART 6: Quick-Fire Sprint Questions

| Question | One-Liner Answer |
|----------|-----------------|
| Ideal sprint length? | "Two weeks for most teams — balances delivery and feedback." |
| Who owns the backlog? | "Product Owner prioritizes; team estimates." |
| What's a sprint goal? | "A single objective the sprint delivers — gives focus and coherence." |
| Velocity for performance reviews? | "Never — it's a forecasting tool, not a productivity metric." |
| Can scope change mid-sprint? | "Protected once committed; emergencies swap something out transparently." |
| What's a spike? | "A time-boxed research task to reduce uncertainty before estimating." |
| Story points vs hours? | "Relative complexity, not time — humans estimate relative better than absolute." |
| Definition of Done? | "Shared checklist that means a story is truly complete, not just 'code written'." |
| Standup goes long? | "Enforce the parking lot — take deep dives offline with relevant people." |
| Team over-commits every sprint? | "Plan to actual velocity, not ideal capacity; break down big stories." |

---

## 🎯 Interview Tips for Agile Questions

1. **Be pragmatic, not dogmatic** — "I follow Scrum but adapt it; the framework serves the team, not the other way around."
2. **Protect the team** — show you shield engineers from churn and context-switching.
3. **Metrics inform, never judge** — never weaponize velocity.
4. **Emphasize outcomes over output** — shipping the right thing matters more than closing tickets.
5. **Show continuous improvement** — the retro and adapting the process is the heart of Agile.
6. **Have real examples** — a time you fixed a broken process, handled scope creep, or improved predictability.
