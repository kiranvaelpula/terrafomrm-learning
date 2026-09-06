# GPU and AI Workload Cost Management

## Overview

GPU and AI/ML workloads are among the most expensive cloud costs. Managing them requires strategies specific to their bursty, compute-intensive nature.

---

## 📖 Understanding GPU & AI Costs (Intuition First)

Managing GPU and AI costs is like renting industrial machinery by the minute instead of buying office chairs. A regular CPU instance is cheap and forgiving — leave one idle and you waste pocket change. A GPU instance can cost 10–40x more per hour, so leaving one idle overnight is like leaving a rented excavator running in an empty lot. The stakes per mistake are dramatically higher, which means the discipline has to be dramatically tighter.

The reason AI workloads need their own cost playbook is that their **spending profile is fundamentally different**. Two distinct phases dominate: **training** (a huge, bursty, expensive job that runs for hours or days on many GPUs, then stops) and **inference** (serving the trained model, which runs continuously but should scale with demand). Training is about finishing fast and then *turning the expensive hardware off*; inference is about not paying for idle capacity between requests. Optimizing them requires opposite instincts.

The single biggest source of GPU waste is **idle time**. GPUs sit expensive and unused during data loading, between experiments, on weekends, or when a notebook is left open. Because the per-hour cost is so high, even modest idleness translates to enormous waste. The core discipline is ruthless: use the GPU only when it's actually computing, and release it the instant it's not — through auto-shutdown, job queues, and Spot instances for interruptible training runs.

There are AI-specific levers that don't exist elsewhere. **Spot instances** are especially powerful for training because training can checkpoint and resume after an interruption, capturing 70–90% savings. **Right-sizing the GPU type** matters enormously — using a top-end GPU for a job a cheaper one could handle burns money. And on the inference side, techniques like **batching, model quantization, and autoscaling to zero** cut the cost of serving without retraining anything.

Finally, AI cost management ties directly back to **unit economics**, but with a twist: the meaningful unit becomes "cost per training run," "cost per 1,000 inferences," or "cost per token" for LLMs. Because AI is often the fastest-growing line on a modern cloud bill, leadership increasingly wants these numbers. Framing GPU spend in terms of cost per model or per prediction is what turns a scary, opaque bill into a decision leaders can reason about.

---

## Why GPU Costs Are Different

```
A GPU instance (e.g., p4d.24xlarge) can cost $30+/HOUR on-demand.
That's ~$22,000/month if left running 24/7.
One forgotten GPU instance = a shocking bill.

GPU workloads are also BURSTY:
- Training: intense for hours/days, then idle
- Inference: variable load
- Experimentation: sporadic
Paying on-demand 24/7 for bursty work is enormous waste.
```

## Key Cost-Saving Strategies

### 1. Spot Instances for Training

```
Training is often FAULT-TOLERANT (checkpointing) → perfect for Spot.
Spot GPUs are up to 70-90% cheaper than on-demand.

Risk: Spot can be reclaimed → use checkpointing to resume.
```

```python
# Request Spot GPU instances for training
import boto3
ec2 = boto3.client("ec2")

ec2.request_spot_instances(
    InstanceCount=4,
    LaunchSpecification={
        "InstanceType": "p3.2xlarge",
        "ImageId": "ami-xxxxx",
    },
    Type="one-time",
    # Save checkpoints to S3 so reclaim doesn't lose progress
)
```

### 2. Right-Size the GPU

```
Don't use an A100 when a T4 would do:
- T4 (g4dn): inference, small models — cheap
- V100 (p3): mid-size training
- A100 (p4d): large model training — expensive

Match the GPU to the workload. Inference rarely needs top-tier GPUs.
```

### 3. Auto-Stop Idle GPU Instances

```python
# Idle GPU detection — stop if GPU utilization ~0 for 30 min
import boto3

def stop_idle_gpus():
    cloudwatch = boto3.client("cloudwatch")
    ec2 = boto3.client("ec2")

    # Get GPU instances (tagged)
    instances = ec2.describe_instances(
        Filters=[{"Name": "tag:WorkloadType", "Values": ["gpu"]},
                 {"Name": "instance-state-name", "Values": ["running"]}]
    )
    for res in instances["Reservations"]:
        for inst in res["Instances"]:
            util = get_gpu_utilization(cloudwatch, inst["InstanceId"])
            if util < 5:  # < 5% for the period = idle
                ec2.stop_instances(InstanceIds=[inst["InstanceId"]])
                print(f"Stopped idle GPU: {inst['InstanceId']}")
```

### 4. Savings Plans for Steady Inference

```
Training → Spot (bursty, fault-tolerant)
Steady inference → Savings Plans / Reserved (predictable baseline)
```

### 5. Managed Services & Serverless Inference

```
- SageMaker Serverless Inference — pay per request, scales to zero
- Batch inference — process in bulk during off-peak on Spot
- Model optimization (quantization, distillation) → smaller/cheaper GPUs
```

## GPU Cost Optimization for LLMs / GenAI

```
- Use smaller models where they suffice (don't run a 70B model for simple tasks)
- Quantization (int8/int4) → fit on smaller/cheaper GPUs
- Batch requests → higher GPU utilization per dollar
- Cache responses → avoid redundant inference
- Consider API models (Bedrock/OpenAI) vs self-hosting — do the math on volume
```

## Cost Monitoring for GPU Workloads

```yaml
Track:
  gpu_utilization: aim > 70% when running (else you're wasting the GPU)
  cost_per_training_run: trend over time
  cost_per_1k_inferences: unit economics for serving
  spot_vs_ondemand_ratio: maximize spot for fault-tolerant work
  idle_gpu_hours: should be near zero
```

## Common Pitfalls

- **Forgotten instances** — a GPU left running overnight/weekend is a huge bill
- **Over-provisioned GPUs** — using A100s for work a T4 could do
- **On-demand for everything** — ignoring Spot for fault-tolerant training
- **Low utilization** — paying for a GPU that sits mostly idle
- **Self-hosting small volumes** — API models can be cheaper below a break-even point

---

## 🎯 Interview Quick Points

- GPU instances cost **10–40x** more per hour than CPU, so idle time is far more expensive
- AI cost has two very different profiles: **training** (bursty, huge) and **inference** (continuous, scale with demand)
- Training discipline: **finish fast, then turn the expensive hardware off**; inference: **don't pay for idle**
- The #1 GPU waste is **idle time** — data loading, between experiments, weekends, forgotten notebooks
- **Spot instances** shine for training (70–90% savings) because jobs can **checkpoint and resume** after interruption
- **Right-size the GPU type** — using a top-end GPU for a small job burns money
- Inference levers: **batching, model quantization, and autoscaling (even to zero)** cut serving cost
- Track AI-specific unit economics: **cost per training run, per 1,000 inferences, or per token (LLMs)**
- Use **auto-shutdown, job queues, and scheduling** to ensure GPUs run only when actually computing
- AWS options include EC2 GPU instances, **SageMaker (with SageMaker Savings Plans)**, and Spot for training
- AI is often the **fastest-growing line** on a modern cloud bill — leadership wants cost-per-model visibility
- **Data transfer and storage** for large datasets/checkpoints add up — factor them into total AI cost
