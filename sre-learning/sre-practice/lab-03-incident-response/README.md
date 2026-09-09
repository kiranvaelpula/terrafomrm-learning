# Lab 03: Incident Response Simulation

## 🎯 Objective
Simulate an incident end-to-end — declare it, assign roles, track a timeline, mitigate, resolve, and generate a post-mortem skeleton.

## 📋 Prerequisites
```bash
python3 --version   # no external libs
```

## 🧪 Steps

### Step 1: Declare an incident
Run `incident_sim.py`. It creates an incident with severity and an Incident Commander.

### Step 2: Log the response timeline
Each action is timestamped and recorded (this feeds the post-mortem).

### Step 3: Mitigate and resolve
Restore service first, then mark resolved — see MTTR calculated.

### Step 4: Generate the post-mortem skeleton
The tool outputs a blameless post-mortem template pre-filled with the timeline.

## ✅ Expected Output
```
[14:30:00] monitoring: Detected via error-rate alert
[14:35:00] alice: Incident declared SEV1, IC assigned
[14:45:00] bob: MITIGATION: rolled back deploy v2.3
[14:47:00] alice: RESOLVED (MTTR: 17 min)

--- Post-Mortem Skeleton generated ---
```

## 🏋️ Exercises
1. Add the comms-lead role posting status updates on a cadence
2. Implement severity-based escalation (SEV1 auto-pages more people)
3. Add the 5 Whys prompt to the post-mortem generation
4. Track action items with owners and due dates

## 🔑 Key Concepts Practiced
- Incident lifecycle (detect → triage → mitigate → resolve → post-mortem)
- Incident roles (IC, comms, ops, scribe)
- MTTR measurement
- Blameless post-mortem structure
