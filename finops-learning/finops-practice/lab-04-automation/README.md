# Automated Cost Optimization

**Lab Objective**: Hands-on practice with FinOps concepts

---

## Overview

This lab will guide you through implementing automated cost optimization in a real AWS environment.

**Prerequisites:**
- AWS account with billing access
- AWS CLI configured
- Basic Python knowledge

**Time Required**: 60-90 minutes

---

## Lab Steps

### Step 1: Environment Setup
```bash
pip install boto3
aws configure   # EC2 + Cost Explorer access
```
Tag non-prod instances you want auto-managed with `AutoStop=true` (opt-in prevents surprises).

### Step 2: Implementation — Auto-Stop Non-Prod (Lambda)
```python
import boto3

def lambda_handler(event, context):
    """Stop opted-in non-prod instances nightly. EventBridge cron trigger."""
    ec2 = boto3.resource("ec2")
    instances = ec2.instances.filter(Filters=[
        {"Name": "instance-state-name", "Values": ["running"]},
        {"Name": "tag:Environment", "Values": ["dev", "staging"]},
        {"Name": "tag:AutoStop", "Values": ["true"]},
    ])
    ids = [i.id for i in instances]
    if ids:
        ec2.instances.filter(InstanceIds=ids).stop()
    print(f"Stopped {len(ids)} instances: {ids}")
    return {"stopped": len(ids)}

# EventBridge schedule: cron(0 20 * * ? *)  → 8 PM daily
```

### Step 3: Verification
- Confirm instances stop at the scheduled time (check EC2 console/CloudWatch logs)
- Verify prod is untouched (no AutoStop tag)
- Add a morning start rule (cron 8 AM) if teams need them during the day

### Step 4: Optimization
- Add idle-volume cleanup and old-snapshot deletion on a weekly schedule
- Run in **dry-run** mode first (log what *would* happen)
- Notify owners before any deletion; keep actions **idempotent**

---

## Expected Outcomes

After completing this lab, you will:
- Automate cost savings with Lambda + EventBridge
- Use opt-in tags to safely target resources
- Understand safe automation practices (dry-run, notify, idempotent)

---

## 🎯 Interview Quick Points
- Automate repetitive savings (stop non-prod, delete idle resources) with Lambda + EventBridge
- Use **opt-in tags** (AutoStop=true) so automation never surprises anyone
- Start with **dry-run/reporting**, then enable actions once trusted
- Make automation **idempotent** and **notify owners** before destructive actions
- Non-prod off 12 hrs/day ≈ 50% savings on that compute
