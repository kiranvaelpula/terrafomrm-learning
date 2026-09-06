# FinOps Automation and Orchestration

## Overview

FinOps automation replaces manual cost management with event-driven, scheduled, and policy-based systems that detect and fix waste automatically.

---

## 📖 Understanding FinOps Automation (Intuition First)

FinOps automation is like installing a smart thermostat instead of walking around the house adjusting every radiator by hand. The manual version works for a while, but you forget rooms, you're not home when it matters, and the savings depend entirely on your discipline. The automated version applies the right policy continuously, 24/7, without anyone remembering to act. FinOps automation is that thermostat for cloud spend — it turns optimization from a thing people *do* into a thing the system *does*.

The reason automation is essential (not optional) is that **manual FinOps doesn't scale and doesn't stick**. A human running a weekly cleanup script will eventually get busy, go on vacation, or leave the company — and the waste creeps back. Cloud environments change every hour, so the only way to keep them efficient is to have machines watching and acting at the same speed the environment changes. Humans set the policy; machines enforce it relentlessly.

The natural progression is a ladder of increasing autonomy. First comes **notify** — automation detects an issue and tells a human ("this volume is unattached"). Next is **recommend** — it suggests the specific fix. Then **semi-automated** — it acts with approval or only in safe environments (auto-stopping dev at night). Finally **fully automated** — it remediates directly for well-understood, low-risk cases. You climb this ladder as trust in the automation grows, always keeping humans in the loop where the blast radius is large.

The golden rule is **match automation aggressiveness to blast radius**. Auto-deleting an orphaned dev snapshot is safe and reversible enough to fully automate. Auto-terminating a production database because it looks idle is how you cause an outage. Good FinOps automation is bold in low-risk environments and cautious — notify-only — where a mistake would hurt. Guardrails, dry-runs, and environment awareness keep automation from becoming its own kind of disaster.

Done well, automation frees the FinOps team from the treadmill of manual cleanup so they can focus on the high-value work machines can't do: strategy, commitment planning, architecture guidance, and building the culture. The point of automating the boring parts is to make room for the parts that actually require human judgment.

---

## Automation Patterns

```
1. SCHEDULED (cron/EventBridge):
   - Nightly: stop dev/staging instances
   - Weekly: report unattached volumes, old snapshots
   - Monthly: right-sizing recommendations

2. EVENT-DRIVEN (respond to events):
   - New untagged resource created → auto-tag or alert
   - Cost anomaly detected → notify + investigate
   - Budget threshold crossed → alert / restrict

3. POLICY-BASED (guardrails):
   - Deny expensive instance types (SCPs)
   - Require tags before resource creation
   - Auto-delete resources past TTL
```

## Example: Auto-Stop Non-Prod at Night (Lambda + EventBridge)

```python
import boto3

def lambda_handler(event, context):
    """Stop all dev/staging instances nightly. Triggered by EventBridge cron."""
    ec2 = boto3.resource("ec2")

    instances = ec2.instances.filter(
        Filters=[
            {"Name": "instance-state-name", "Values": ["running"]},
            {"Name": "tag:Environment", "Values": ["dev", "staging"]},
            {"Name": "tag:AutoStop", "Values": ["true"]},  # opt-in tag
        ]
    )

    ids = [i.id for i in instances]
    if ids:
        ec2.instances.filter(InstanceIds=ids).stop()
        print(f"Stopped {len(ids)} non-prod instances: {ids}")

    return {"stopped": len(ids)}

# EventBridge rule: cron(0 20 * * ? *)  → 8 PM daily
# Estimated saving: dev fleet off 12 hrs/day = ~50% of dev compute cost
```

## Example: Auto-Tag Enforcement

```python
def enforce_tags(event, context):
    """Triggered when a resource is created without required tags."""
    required = ["Environment", "Owner", "CostCenter"]
    resource_arn = event["detail"]["resource-arn"]
    tags = get_tags(resource_arn)

    missing = [t for t in required if t not in tags]
    if missing:
        # Option 1: notify owner
        notify(f"Resource {resource_arn} missing tags: {missing}")
        # Option 2: apply default tags
        # Option 3: quarantine/stop the resource until tagged
```

## Example: Scheduled Waste Report

```python
import boto3
from datetime import datetime, timezone, timedelta

def weekly_waste_report():
    ec2 = boto3.client("ec2")
    report = []

    # Unattached volumes
    vols = ec2.describe_volumes(
        Filters=[{"Name": "status", "Values": ["available"]}]
    )["Volumes"]
    report.append(f"Unattached volumes: {len(vols)} (~${sum(v['Size']*0.08 for v in vols):.0f}/mo)")

    # Old snapshots (> 90 days)
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    snaps = ec2.describe_snapshots(OwnerIds=["self"])["Snapshots"]
    old = [s for s in snaps if s["StartTime"] < cutoff]
    report.append(f"Snapshots > 90 days: {len(old)}")

    # Unused Elastic IPs
    eips = [a for a in ec2.describe_addresses()["Addresses"] if "InstanceId" not in a]
    report.append(f"Unused Elastic IPs: {len(eips)} (~${len(eips)*3.6:.0f}/mo)")

    send_slack("\n".join(report))
```

## Automation Tools

| Tool | Purpose |
|------|---------|
| AWS Lambda + EventBridge | Scheduled/event-driven automation |
| AWS Config | Detect non-compliant (untagged) resources |
| AWS Instance Scheduler | Managed start/stop scheduling |
| Cloud Custodian | Policy-as-code for cost governance |
| Terraform + Infracost | Cost gates in IaC pipelines |

## Best Practices

- **Start with read-only/reporting** automation, then add actions once trusted
- **Opt-in tags** (like `AutoStop=true`) prevent surprises
- **Dry-run mode** first — log what *would* happen before doing it
- **Notify owners** before deleting anything
- **Idempotent** automation — safe to run repeatedly

---

## 🎯 Interview Quick Points

- Automation turns optimization from a thing people **do** into a thing the system **does** continuously
- Manual FinOps **doesn't scale and doesn't stick** — environments change hourly, humans get busy
- The autonomy ladder: **notify → recommend → semi-automated (with approval) → fully automated**
- Golden rule: **match automation aggressiveness to blast radius** — bold in dev, cautious in prod
- Fully automate **safe, reversible, low-risk** actions (delete orphaned dev snapshots, stop dev at night)
- Keep **humans in the loop** where a mistake causes an outage (never auto-terminate a prod DB)
- Common building blocks: **EventBridge + Lambda**, scheduled cleanups, tag enforcement, budget actions
- Use **dry-runs, guardrails, and environment awareness** so automation doesn't cause its own incidents
- Automation frees the FinOps team for **strategy, commitment planning, and culture** — the human work
- **Idempotency and logging** matter — automated actions must be safe to re-run and fully auditable
- Tie automation to **tags** so it targets the right resources and respects ownership
- Start with notify-only, **build trust**, then increase autonomy as results prove reliable
