# Engineering Manager Interview Prep — Migration Strategy & Implementation

**Focus**: Large-Scale Migrations, Monolith→Microservices, Database Migration, Cloud Migration
**Format**: Frameworks → Process → Scenarios → Interview Q&As

---

## 📖 PART 1: Migration Fundamentals

### The 7 Rs of Migration (AWS Framework)

When migrating applications (especially to cloud), each app falls into one of these strategies:

| Strategy | What it means | When to use |
|----------|--------------|-------------|
| **Rehost** ("Lift & Shift") | Move as-is, no code changes | Fast migration, tight deadline |
| **Replatform** ("Lift, tinker & shift") | Minor optimizations (e.g., managed DB) | Some cloud benefit, low risk |
| **Repurchase** ("Drop & shop") | Move to SaaS product | Replace with COTS/SaaS |
| **Refactor / Re-architect** | Rewrite for cloud-native | High long-term value apps |
| **Retire** | Decommission | App no longer needed |
| **Retain** | Keep as-is (for now) | Not ready / no business case |
| **Relocate** | Move without conversion (e.g., VMware) | Hypervisor-level move |

**Interview gold:** "Not every app deserves the same treatment. I assess each against the 7 Rs — some get lifted and shifted for speed, high-value ones get refactored, and dead ones get retired. You can't boil the ocean."

---

## 📖 PART 2: Large-Scale Migration — 100+ Applications

This is THE common EM interview scenario. Here's the structured approach.

### Phase 1: Discovery & Assessment (don't skip this!)

```
1. INVENTORY everything
   - All applications, their owners, dependencies
   - Tech stack, traffic, data volume, criticality
   - Use tools: AWS Migration Hub, CloudEndure, discovery agents

2. DEPENDENCY MAPPING
   - Which apps talk to which? Shared databases?
   - Application dependency mapping tools
   - Identify tightly-coupled clusters that must move together

3. CATEGORIZE & PRIORITIZE
   - Business criticality (tier 1 / 2 / 3)
   - Migration complexity (easy / medium / hard)
   - Risk level
```

### Phase 2: Categorize Applications into a Matrix

```
                 LOW COMPLEXITY          HIGH COMPLEXITY
              ┌─────────────────────┬─────────────────────┐
   HIGH       │ Migrate EARLY        │ Plan CAREFULLY       │
   VALUE      │ (quick wins)         │ (refactor, phased)   │
              ├─────────────────────┼─────────────────────┤
   LOW        │ Rehost / batch       │ RETIRE or RETAIN     │
   VALUE      │ (lift & shift)       │ (not worth effort)   │
              └─────────────────────┴─────────────────────┘
```

### Phase 3: Wave Planning (the key to 100+ apps)

You don't migrate 100 apps at once. You group them into **waves**:

```
WAVE 0: Pilot (2-5 low-risk apps)
   → Prove the process, build runbooks, train the team

WAVE 1: Quick wins (10-15 simple, low-dependency apps)
   → Build momentum, refine tooling

WAVE 2-N: Progressively complex apps
   → Group by dependency clusters (apps that share a DB move together)
   → 10-20 apps per wave, 2-4 week cycles

FINAL WAVE: Most complex, critical apps
   → By now the team is expert, tooling is mature
```

### Phase 4: Execution Pattern (per app)

```
For each application:
1. Assess    → Confirm strategy (7 Rs)
2. Prepare   → Set up target environment, IaC
3. Migrate   → Move app + data
4. Validate  → Test functionality, performance, integration
5. Cutover   → Switch traffic (with rollback plan)
6. Optimize  → Right-size, tune, monitor
7. Decommission → Shut down old infrastructure
```

### Phase 5: Team Structure for Large Migrations

```
┌──────────────────────────────────────────┐
│         Migration Program Lead (you)        │
├──────────────────────────────────────────┤
│  Migration Factory Team (repeatable process)│
│    - Landing zone / platform team           │
│    - Migration engineers (execute waves)     │
│    - App teams (domain knowledge)            │
│    - QA / validation                         │
│    - Cutover / rollback specialists          │
└──────────────────────────────────────────┘
```

**"Migration Factory" concept:** Build a repeatable, assembly-line process so each wave gets faster. Standardize tooling, runbooks, and automation so migrating app #50 is far faster than app #1.

---

## 📖 PART 3: Monolith → Microservices Migration

### Why Migrate? (and when NOT to)

**Good reasons:**
- Independent scaling of components
- Independent deployment (teams ship without coordinating)
- Technology flexibility per service
- Fault isolation
- Team autonomy (Conway's Law alignment)

**When NOT to:**
- Small app / small team (microservices add operational overhead)
- No clear domain boundaries
- "Because it's trendy" — a distributed monolith is worse than a monolith

**Interview gold:** "Microservices solve organizational and scaling problems, not code-quality problems. A badly-designed monolith becomes a badly-designed distributed system — now with network calls. I'd only recommend it when the team size, scaling needs, or deployment friction justify the operational cost."

### The Strangler Fig Pattern (the standard approach)

Named after a vine that gradually grows around a tree until it replaces it. You incrementally replace the monolith piece by piece — never a big-bang rewrite.

```
STEP 1: Monolith handles everything
   ┌─────────────────────────┐
   │       MONOLITH          │
   │  (Orders, Users, Cart)  │
   └─────────────────────────┘

STEP 2: Add a proxy/API gateway in front
   ┌──────────┐
   │ API GW   │──────▶ MONOLITH
   └──────────┘

STEP 3: Extract ONE service, route its traffic to it
   ┌──────────┐──────▶ MONOLITH (Users, Cart)
   │ API GW   │
   └──────────┘──────▶ Orders Service (NEW) ✓

STEP 4: Repeat — extract service by service
   ┌──────────┐──────▶ Users Service
   │ API GW   │──────▶ Orders Service
   └──────────┘──────▶ Cart Service

STEP 5: Monolith is fully replaced, decommission it
```

### How to Decide What to Extract First

```
Extract services that are:
1. Loosely coupled (few dependencies) — easier
2. High business value or high change frequency — most benefit
3. Different scaling needs — e.g., payment vs reporting
4. Clear bounded context (Domain-Driven Design)

Start with a LOW-RISK, HIGH-VALUE service to prove the pattern.
```

### Domain-Driven Design (DDD) for Boundaries

- Identify **bounded contexts** — natural business domains (Orders, Inventory, Payments)
- Each microservice = one bounded context
- Avoid splitting by technical layers (don't make a "database service")
- Services own their data — no shared databases

### Key Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Shared database | Split data per service (database-per-service) |
| Distributed transactions | Saga pattern, eventual consistency |
| Service communication | API gateway, service mesh, async messaging (Kafka/RabbitMQ) |
| Data consistency | Event-driven architecture, CQRS |
| Debugging across services | Distributed tracing (Jaeger, X-Ray), centralized logging |
| Testing | Contract testing, service virtualization |

---

## 📖 PART 4: Database Migration

### Types of Database Migration

| Type | Example |
|------|---------|
| Homogeneous | MySQL → MySQL (same engine, e.g., on-prem to RDS) |
| Heterogeneous | Oracle → PostgreSQL (different engine) |
| Re-platform | Self-managed → Managed (RDS, Aurora) |
| Re-architect | Monolithic DB → per-service databases |

### The Standard Database Migration Process

```
1. ASSESS
   - Schema, size, dependencies, downtime tolerance
   - Compatibility (heterogeneous needs schema conversion)

2. SCHEMA CONVERSION (for heterogeneous)
   - AWS SCT (Schema Conversion Tool)
   - Convert Oracle PL/SQL → PostgreSQL, etc.

3. INITIAL DATA LOAD (bulk)
   - Full copy of existing data

4. CONTINUOUS REPLICATION (CDC — Change Data Capture)
   - AWS DMS keeps source and target in sync
   - Captures ongoing changes during migration

5. VALIDATION
   - Row counts, data integrity, application testing

6. CUTOVER
   - Point application to new DB (during low-traffic window)
   - Keep source as fallback

7. MONITOR & DECOMMISSION old DB
```

### Minimizing Downtime — CDC Approach

```
Source DB (live) ──── bulk load ────▶ Target DB
      │                                    ▲
      │                                    │
      └──── CDC (ongoing changes) ─────────┘
            (via AWS DMS / Debezium)

App keeps writing to source → target stays in sync →
brief cutover window → switch app to target → done.
This achieves near-zero downtime.
```

### Splitting a Shared Database (monolith → microservices)

The hardest part of microservices migration:

```
1. Identify which tables belong to which service (by bounded context)
2. Stop cross-service JOINs — replace with API calls or events
3. Move tables to service-owned databases one at a time
4. Use the Strangler pattern for data too — dual-write during transition
5. Handle referential integrity at the application layer, not DB
```

### Migration Tools

| Tool | Purpose |
|------|---------|
| AWS DMS | Database migration + CDC replication |
| AWS SCT | Schema conversion (heterogeneous) |
| Debezium | Open-source CDC |
| Flyway / Liquibase | Schema version control / migrations |
| pg_dump / mysqldump | Logical backups for homogeneous moves |
| GoldenGate | Oracle replication |

---

## � PART 4.5: DEEP TECHNICAL IMPLEMENTATION

This section covers the hands-on technical details — actual tools, configs, and architecture patterns you'd implement.

### A. Server-to-Cloud Migration (Technical)

**Discovery tooling:**
```bash
# AWS Application Discovery Service — agent-based discovery
# Collects: running processes, network connections, performance data

# Agentless discovery via VMware
aws discovery start-data-collection-by-agent-ids --agent-ids <ids>

# Export discovered data for dependency analysis
aws discovery start-export-task --export-data-format CSV

# Third-party tools: 
#   - CloudEndure / AWS MGN (Application Migration Service)
#   - Migration Evaluator (formerly TSO Logic) for cost modeling
#   - Device42, Dynatrace, Datadog for dependency mapping
```

**Rehost (lift & shift) with AWS MGN:**
```
1. Install AWS Replication Agent on source servers
2. Agent does block-level continuous replication to a staging area in AWS
3. Launch test instances → validate
4. Cutover: launch production instances from latest replicated state
5. Source can be decommissioned

Near-zero downtime: continuous replication means cutover is minutes.
```

**Replatform example — move app to containers:**
```dockerfile
# Take a legacy app running on a VM, containerize it
FROM openjdk:11-jre-slim
COPY app.jar /app/app.jar
COPY config/ /app/config/
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```
```yaml
# Deploy to EKS/ECS instead of managing VMs
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legacy-app
spec:
  replicas: 3
  selector:
    matchLabels: {app: legacy-app}
  template:
    metadata:
      labels: {app: legacy-app}
    spec:
      containers:
      - name: legacy-app
        image: registry/legacy-app:v1
        resources:
          requests: {cpu: "250m", memory: "512Mi"}
          limits: {cpu: "500m", memory: "1Gi"}
        readinessProbe:
          httpGet: {path: /health, port: 8080}
          initialDelaySeconds: 10
        livenessProbe:
          httpGet: {path: /health, port: 8080}
          initialDelaySeconds: 30
```

**Infrastructure as Code — the migration factory backbone:**
```hcl
# Reusable Terraform module — this is how you standardize 100+ app migrations
module "app_migration" {
  source = "./modules/standard-app"

  app_name     = "orders-service"
  environment  = "production"
  instance_type = "t3.large"
  min_capacity  = 2
  max_capacity  = 10
  vpc_id        = data.aws_vpc.main.id
  health_check_path = "/health"
}
# Each app = one module call. Add app #50 = copy-paste + change vars.
# This IS the migration factory — repeatable, version-controlled, auditable.
```

---

### B. Monolith → Microservices (Technical)

**Strangler Fig with API Gateway routing:**
```nginx
# nginx as the strangler facade — route by path
upstream monolith    { server monolith:8080; }
upstream orders_svc  { server orders-service:8081; }
upstream users_svc   { server users-service:8082; }

server {
    listen 80;

    # NEW: extracted services get routed to microservices
    location /api/orders { proxy_pass http://orders_svc; }
    location /api/users  { proxy_pass http://users_svc; }

    # EVERYTHING ELSE: still goes to the monolith
    location / { proxy_pass http://monolith; }
}
# As you extract each service, add a location block. Monolith shrinks over time.
```

**Database-per-service — breaking the shared DB:**
```
BEFORE (shared DB — the anti-pattern):
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ Orders   │   │ Users    │   │ Payments │
   └────┬─────┘   └────┬─────┘   └────┬─────┘
        └──────────────┼──────────────┘
                  ┌─────▼─────┐
                  │ Shared DB │  ← cross-service JOINs, tight coupling
                  └───────────┘

AFTER (database-per-service):
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ Orders   │   │ Users    │   │ Payments │
   └────┬─────┘   └────┬─────┘   └────┬─────┘
   ┌────▼─────┐   ┌────▼─────┐   ┌────▼─────┐
   │ Orders DB│   │ Users DB │   │ Pay DB   │
   └──────────┘   └──────────┘   └──────────┘
   No JOINs across services — communicate via API/events.
```

**Handling distributed transactions — Saga pattern:**
```
Problem: Order creation spans Orders, Payment, Inventory services.
No single DB transaction can span them.

CHOREOGRAPHY SAGA (event-driven):
  Order Service    → publishes "OrderCreated"
  Payment Service  → listens, charges card → publishes "PaymentCompleted"
  Inventory Service→ listens, reserves stock → publishes "StockReserved"

  If Payment FAILS → publishes "PaymentFailed"
  Order Service    → listens → compensating action: cancel order

Key: eventual consistency + compensating transactions (not rollback).
```

```python
# Compensating transaction example (rollback logic in code, not DB)
def create_order_saga(order):
    try:
        order_id = orders_service.create(order)          # Step 1
        payment_id = payment_service.charge(order)         # Step 2
        inventory_service.reserve(order)                    # Step 3
    except PaymentError:
        orders_service.cancel(order_id)                    # Compensate step 1
        raise
    except InventoryError:
        payment_service.refund(payment_id)                # Compensate step 2
        orders_service.cancel(order_id)                    # Compensate step 1
        raise
```

**Dual-write / data sync during migration:**
```python
# During transition, write to BOTH old monolith DB and new service DB
def create_order(order):
    # Write to new microservice (source of truth going forward)
    new_id = orders_db.insert(order)
    
    # ALSO write to monolith DB (until fully migrated) — keeps legacy reads working
    try:
        monolith_db.insert(order)
    except Exception as e:
        logger.warning(f"Dual-write to monolith failed: {e}")
        # Reconciliation job fixes drift later
    
    return new_id
# Once all readers migrate off the monolith DB, remove the dual-write.
```

**Service communication patterns:**
```
Synchronous (request-response):
   REST / gRPC through API Gateway or Service Mesh (Istio/Linkerd)
   Use for: queries needing immediate response

Asynchronous (event-driven):
   Kafka / RabbitMQ / SNS+SQS
   Use for: decoupling, events, workflows that can be eventually consistent

Service Mesh (Istio) handles: mTLS, retries, circuit breaking, tracing
```

**Observability across services (critical for microservices):**
```yaml
# Distributed tracing — follow a request across all services
# OpenTelemetry + Jaeger/AWS X-Ray

# Each service propagates a trace ID
# Request → API GW (trace-id: abc) → Orders (abc) → Payment (abc) → DB
# Jaeger shows the full waterfall: which service was slow

# Centralized logging: EFK (Elasticsearch/Fluentd/Kibana) or Loki
# Metrics: Prometheus + Grafana per service
```

---

### C. Database Migration (Technical)

**AWS DMS setup for near-zero-downtime CDC:**
```
1. Create replication instance (the compute that does the work)
2. Create source endpoint (e.g., on-prem Oracle)
3. Create target endpoint (e.g., RDS PostgreSQL)
4. Create migration task with type:
   "Full load + CDC" = bulk copy THEN ongoing replication
```

```bash
# Create the DMS replication task
aws dms create-replication-task \
  --replication-task-identifier oracle-to-postgres \
  --source-endpoint-arn <source-arn> \
  --target-endpoint-arn <target-arn> \
  --replication-instance-arn <instance-arn> \
  --migration-type full-load-and-cdc \
  --table-mappings file://table-mappings.json
```

**Schema conversion (heterogeneous — Oracle → PostgreSQL):**
```
AWS SCT (Schema Conversion Tool):
1. Connect to source Oracle DB
2. SCT analyzes schema, generates conversion report
3. Auto-converts: tables, indexes, views, ~80% of stored procedures
4. Manual fixes: complex PL/SQL, Oracle-specific features
5. Apply converted schema to target PostgreSQL
```

**CDC with Debezium (open-source alternative):**
```yaml
# Debezium connector — captures MySQL binlog changes → Kafka
{
  "name": "mysql-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.hostname": "source-mysql",
    "database.server.id": "184054",
    "database.include.list": "production",
    "table.include.list": "production.orders,production.users",
    "topic.prefix": "cdc"
  }
}
# Every INSERT/UPDATE/DELETE on source → Kafka topic → consumer writes to target
```

**Validation before cutover:**
```sql
-- Row count comparison
SELECT COUNT(*) FROM source.orders;   -- must match
SELECT COUNT(*) FROM target.orders;

-- Checksum / hash validation on critical tables
SELECT MD5(CAST(array_agg(t.* ORDER BY id) AS text)) FROM target.orders t;
```
```bash
# AWS DMS data validation (built-in)
# Enable ValidationSettings in the task — DMS compares source vs target row-by-row
aws dms describe-table-statistics --replication-task-arn <arn>
# Shows: ValidationState = "Validated" / "Mismatch"
```

**Cutover sequence (near-zero downtime):**
```
1. Bulk load complete + CDC caught up (replication lag ~0)
2. Enable read-only / maintenance mode on app (seconds)
3. Verify CDC lag = 0 (source and target fully in sync)
4. Update app connection string → point to new DB
5. Smoke test against new DB
6. Disable maintenance mode → traffic flows to new DB
7. Keep source DB running as fallback for X days
8. Decommission source after confidence period

Actual downtime = the connection string swap = seconds to a couple minutes.
```

**Schema versioning with Flyway (for ongoing migrations):**
```sql
-- V1__create_orders.sql
CREATE TABLE orders (id SERIAL PRIMARY KEY, ...);

-- V2__add_status_column.sql
ALTER TABLE orders ADD COLUMN status VARCHAR(20) DEFAULT 'pending';
```
```bash
flyway migrate    # Applies versioned migrations in order, tracks state
# Every schema change is version-controlled and repeatable across environments
```

---

## 📋 PART 5: Interview Questions & Answers

### Q1: You have 100+ applications to migrate to the cloud. How do you approach it?

**Sample Answer:**
"I never try to migrate 100 apps at once — that's how migrations fail. My approach has five phases.

First, **discovery and assessment** — I inventory every application, map dependencies, and capture criticality, tech stack, and traffic. You can't migrate what you don't understand.

Second, **categorization** — I apply the 7 Rs framework. Some apps get rehosted (lift and shift) for speed, high-value ones get refactored, dead ones get retired. I plot them on a value-vs-complexity matrix.

Third, **wave planning** — I group apps into waves. Wave 0 is a small pilot of 2-5 low-risk apps to prove the process and build runbooks. Then quick wins to build momentum, then progressively complex waves, grouping apps that share dependencies so they move together.

Fourth, I build a **migration factory** — a repeatable, standardized, automated process so migrating app #50 is far faster than app #1. Standardized IaC, runbooks, and validation.

Fifth, **execution per app** — assess, prepare target, migrate, validate, cutover with a rollback plan, optimize, decommission old infra.

Throughout, I track progress against a dashboard, communicate to stakeholders regularly, and hold retros between waves to improve. The key principles are: don't boil the ocean, prove the process on low-risk apps first, and make it repeatable."

---

### Q2: How do you migrate a monolith to microservices?

**Sample Answer:**
"I use the **Strangler Fig pattern** — incremental replacement, never a big-bang rewrite, because big-bang rewrites are extremely risky and often fail.

I put an API gateway in front of the monolith. Then I extract one service at a time — starting with a low-risk, high-value component with a clear bounded context. I route that service's traffic to the new microservice while the monolith handles everything else. Then I repeat, service by service, until the monolith is fully replaced and can be decommissioned.

I use Domain-Driven Design to find the boundaries — each service maps to a bounded context like Orders or Payments, not technical layers. The hardest part is usually the data: services should own their data, so I split the shared database gradually, replacing cross-service JOINs with API calls or events.

Importantly, I'd first challenge whether we even need microservices. They solve scaling and organizational problems, not code quality. A distributed monolith is worse than a monolith. If the justification is solid — independent scaling, deployment friction, team autonomy — then Strangler Fig is the safe path."

---

### Q3: How do you migrate a database with minimal downtime?

**Sample Answer:**
"The key is Change Data Capture (CDC). Here's the flow:

First, do a bulk load of all existing data to the target database. Then set up CDC replication — using AWS DMS or Debezium — so any changes to the source during migration are continuously replicated to the target. The application keeps running against the source while the target stays in sync.

Once the target is caught up and validated — row counts, data integrity, application testing — I schedule a brief cutover during a low-traffic window. I switch the application to the target database, keeping the source as a fallback for a period in case we need to roll back.

For heterogeneous migrations, like Oracle to PostgreSQL, there's an extra schema conversion step first using a tool like AWS SCT. This approach achieves near-zero downtime — the actual cutover is seconds to minutes, not hours."

---

### Q4: How do you handle rollback if a migration goes wrong?

**Sample Answer:**
"Every migration must have a rollback plan before we start — I never migrate without a way back. For applications, I keep the old environment running until the new one is proven stable, and use DNS or load balancer switching so I can flip traffic back instantly. For databases, I keep the source live and in sync (or as a fallback) during the cutover window, so if validation fails I point the app back to it. I also define clear rollback triggers upfront — specific error rates, performance thresholds, or data integrity failures — so the decision to roll back is objective, not panicked. And I test the rollback procedure itself, not just the migration. A rollback plan you haven't tested is a hope, not a plan."

---

### Q5: How do you prioritize which applications to migrate first?

**Sample Answer:**
"I use a value-vs-complexity matrix. Low-complexity, high-value apps go first — they're quick wins that build momentum and prove the process. High-complexity, high-value apps get careful planning and often refactoring. Low-value, high-complexity apps I question whether to migrate at all — often they should be retired or retained. And I always start with a pilot of low-risk apps to validate tooling and build runbooks before touching anything critical. I also group by dependency — apps sharing a database or tightly coupled must move together in the same wave."

---

### Q6: How do you migrate without disrupting the business / ongoing development?

**Sample Answer:**
"A few strategies. First, I run migration as a parallel workstream with a dedicated migration team, so feature development doesn't stop entirely. Second, I use phased waves so the business only ever has a small portion in flight at once. Third, I schedule cutovers during low-traffic windows and communicate them well in advance. Fourth, I freeze major changes to an app only during its specific migration window, not the whole program. And I over-communicate — stakeholders always know what's moving, when, and what to expect. The goal is the business barely notices."

---

### Q7: What are the biggest risks in a large migration and how do you mitigate them?

**Sample Answer:**

| Risk | Mitigation |
|------|-----------|
| Hidden dependencies | Thorough discovery + dependency mapping upfront |
| Data loss/corruption | CDC replication, validation, keep source as fallback |
| Extended downtime | CDC for near-zero downtime cutover |
| Scope creep / cost overrun | Wave planning, fixed scope per wave, track budget |
| Team burnout | Sustainable pace, migration factory reduces toil |
| Business disruption | Pilot first, phased waves, tested rollback |
| "Big bang" failure | Never big-bang — always incremental |

"The single biggest risk is trying to do too much at once. Incremental, wave-based migration with tested rollback plans de-risks everything."

---

### Q8: How do you measure success of a migration?

**Sample Answer:**
"I track both delivery and outcome metrics. Delivery: apps migrated per wave, on-schedule percentage, budget adherence. Technical: downtime during cutover (target near-zero), post-migration incident rate, performance vs baseline. Business outcomes: cost savings (especially for cloud migrations), improved deployment frequency, better scalability. And team health — migrations are marathons, so sustainable pace matters. Ultimately success is: everything moved, nothing broke, we're saving money or moving faster, and the team isn't burned out."

---

### Q9 (Technical): How exactly do you achieve near-zero downtime in a DB migration?

**Sample Answer:**
"The mechanism is Change Data Capture. I use AWS DMS or Debezium in 'full load + CDC' mode. First it bulk-copies all existing rows to the target. Then CDC reads the source's transaction log — the binlog in MySQL or redo logs in Oracle — and streams every ongoing INSERT, UPDATE, and DELETE to the target in near real-time. The application keeps writing to the source the whole time while the target stays in sync with minimal replication lag.

For the actual cutover: I wait until replication lag hits zero, put the app in a brief read-only or maintenance mode for a few seconds, confirm source and target are fully synced, swap the connection string to the target, smoke test, and lift maintenance mode. The real downtime is just the connection swap — seconds to a couple minutes. I keep the source running as a fallback for a few days. For heterogeneous migrations like Oracle to Postgres, there's a schema conversion step first with AWS SCT, and I validate with row counts and checksums before cutover."

---

### Q10 (Technical): How do you handle data consistency when breaking a shared database in microservices?

**Sample Answer:**
"This is the hardest part of microservices migration. The end goal is database-per-service — each service owns its data and no one else touches it directly. Getting there:

First, I identify which tables belong to which bounded context. Then I eliminate cross-service JOINs — those get replaced with API calls or, better, asynchronous events so services aren't tightly coupled at runtime.

For the transition, I use a dual-write pattern — the app writes to both the old shared DB and the new service DB — with a reconciliation job to catch any drift. Once all readers have migrated off the old table, I remove the dual-write.

For transactions that span services — like an order touching payment and inventory — I can't use a single ACID transaction anymore, so I use the Saga pattern with compensating transactions. If payment succeeds but inventory fails, I trigger a compensating action to refund the payment. It's eventual consistency instead of immediate consistency, and the business has to accept that tradeoff — which is why I involve product early."

---

### Q11 (Technical): What tooling and automation do you use to migrate 100+ apps efficiently?

**Sample Answer:**
"The core idea is a migration factory built on automation. For discovery I use AWS Application Discovery Service or tools like Device42 to inventory and map dependencies. For rehosting I use AWS MGN which does block-level replication for near-zero-downtime lift-and-shift.

The backbone is Infrastructure as Code — I build reusable Terraform modules so each app migration is a parameterized module call, not bespoke work. Standardized CI/CD pipelines handle build, test, and deploy uniformly. For containerized targets, standardized Dockerfiles and Helm charts. For databases, DMS with templated task configs.

Everything is version-controlled and repeatable, so migrating app #50 is copy-paste-configure, not reinvention. I also build automated validation — smoke tests, health checks, and data validation — into the pipeline so each migration self-verifies. That's what makes 100+ apps feasible: you're not doing 100 unique projects, you're running the same automated assembly line 100 times, getting faster each wave."

---

## 📋 PART 6: Quick-Fire Migration Questions

| Question | One-Liner Answer |
|----------|-----------------|
| 100 apps — migrate all at once? | "Never. Wave-based, pilot first, prove the process, then scale." |
| Monolith to microservices approach? | "Strangler Fig — incremental extraction, never big-bang rewrite." |
| Near-zero downtime DB migration? | "CDC replication (DMS/Debezium) — sync target, brief cutover, keep fallback." |
| First apps to migrate? | "Low-complexity, high-value quick wins after a low-risk pilot." |
| Do you always go microservices? | "No — they solve scaling/org problems, not code quality. Often a monolith is right." |
| How to split shared database? | "By bounded context, database-per-service, replace JOINs with APIs/events." |
| Rollback strategy? | "Keep old env live, DNS/LB switching, tested rollback triggers defined upfront." |
| Migration team structure? | "A migration factory — repeatable process, standardized tooling, gets faster each wave." |
| Heterogeneous DB migration? | "Schema conversion first (SCT), then bulk load + CDC." |
| 7 Rs of migration? | "Rehost, Replatform, Repurchase, Refactor, Retire, Retain, Relocate." |

---

## 🎯 Interview Tips for Migration Questions

1. **Always start with discovery** — "You can't migrate what you don't understand."
2. **Never big-bang** — incremental, wave-based, or Strangler Fig for everything.
3. **Prove it on a pilot first** — low-risk apps validate the process.
4. **Build a repeatable factory** — standardization makes later waves fast.
5. **Always have a tested rollback** — "A rollback plan you haven't tested is just hope."
6. **Right tool per app** — the 7 Rs; not everything gets the same treatment.
7. **Challenge microservices** — show maturity by questioning whether they're needed.
8. **Communicate relentlessly** — stakeholders should never be surprised.
9. **Data is the hard part** — for both DB migration and microservices, data is where it gets tricky.
10. **Use real numbers** — "migrated 120 apps across 8 waves in 9 months with zero data loss."
