# Fine-Tuning LLMs

> **Fine-tuning adapts a pre-trained model to your specific task, style, or domain by further training it on your own labeled examples.**

---

## 📖 What is Fine-Tuning? (The Core Idea)

A foundation model already knows language, facts, and reasoning from its pre-training. **Fine-tuning** takes that model and trains it a little more — on *your* specific examples — so it becomes specialized for your task or adopts a particular behavior.

```
Foundation Model (knows general language, broad knowledge)
        │
        ▼ train further on YOUR curated examples
Fine-Tuned Model (specialized for your specific task/style)
```

### The School Analogy

Think of a foundation model as a smart, well-educated new graduate:
- They know a lot generally (pre-training)
- **Fine-tuning** is like on-the-job training at your company — they learn your specific processes, your writing style, your way of doing things

You're not teaching them language from scratch — you're specializing their existing intelligence for your needs.

---

## 🎯 When to Fine-Tune (And When NOT To)

This is the most important decision, and where people go wrong. Fine-tuning is powerful but often the *wrong* tool. Here's the decision framework:

```
Need to add KNOWLEDGE / facts?              → Use RAG (NOT fine-tuning)
Need current / changing information?         → Use RAG
Need to change BEHAVIOR / style / format?    → Fine-tune
Need a specific output structure always?     → Fine-tune
Need a specialized skill/tone?               → Fine-tune
Simple task, a good prompt already works?    → Just prompt engineering
```

### The Golden Rule

**Fine-tuning teaches behavior, not knowledge.** This trips people up constantly.

```
❌ WRONG: "Our chatbot doesn't know our product catalog,
           let's fine-tune it on the catalog."
   → Fine-tuning won't reliably teach facts, and the catalog changes.
   → Use RAG instead — retrieve the catalog at query time.

✅ RIGHT: "Our chatbot's tone is too casual and it doesn't follow
           our response format."
   → This is behavior — fine-tuning is the right tool.
```

### Order of Preference (Try Cheapest First)

```
1. Prompt engineering  (free, instant)       ← always try first
2. RAG                 (cheap, for knowledge) ← for facts/data
3. Fine-tuning         (expensive, for behavior) ← only when needed
```

Only reach for fine-tuning when prompting and RAG genuinely can't achieve what you need. It's the most expensive and slowest option.

---

## 🧠 Types of Fine-Tuning

### 1. Full Fine-Tuning

Update **all** of the model's parameters (billions of them).

```
+ Most powerful — can deeply change the model
− Extremely expensive (many GPUs, lots of memory)
− Risk of "catastrophic forgetting" — the model can lose
  general abilities while learning your narrow task
− You get a full copy of a huge model to host
```

Rarely necessary for most use cases.

### 2. PEFT (Parameter-Efficient Fine-Tuning)

Update only a **small subset** of parameters — far cheaper, nearly as effective. This is what most people actually use.

**LoRA (Low-Rank Adaptation)** — the most popular PEFT method:

```
The insight: instead of updating billions of weights,
FREEZE the original model and add small "adapter" matrices,
training only those.

Original model weights:  FROZEN     (billions of parameters)
LoRA adapters:           TRAINABLE  (millions — ~100-1000x fewer)

Result: ~90%+ of full fine-tuning quality, at a tiny fraction
        of the cost and memory. And you can swap adapters in/out.
```

Why this works: research found that the *changes* needed to adapt a model to a new task are "low-rank" — they can be represented compactly. So you don't need to touch the whole model.

**QLoRA** = LoRA + **quantization** (compressing the model's numbers to use less memory). This lets you fine-tune surprisingly large models on a *single* consumer GPU.

### Comparison

| Method | Cost | Quality | Use when |
|--------|------|---------|----------|
| Full fine-tuning | Very high | Highest | Rarely — huge budgets, deep changes |
| LoRA | Low-medium | ~90-95% of full | Most fine-tuning needs |
| QLoRA | Lowest | ~85-90% of full | Limited GPU resources |

---

## 🛠️ Fine-Tuning Workflow (Step by Step)

```
1. PREPARE DATA (this is 80% of the work)
   - Collect examples: input → desired output pairs
   - Format as JSONL
   - Clean, deduplicate, ensure quality
   - Split into training and validation sets
   - Quality > quantity: 100s of GOOD examples often beats
     1000s of mediocre ones

2. TRAIN
   - Choose a base model (size, open vs closed)
   - Set hyperparameters (learning rate, epochs)
   - Run training (managed service or your own GPUs)
   - Monitor for overfitting

3. EVALUATE
   - Test on held-out validation data (data it never trained on)
   - Compare against the base model — is it actually better?
   - Check it didn't lose general abilities

4. DEPLOY
   - Host the fine-tuned model (or adapter)
   - Monitor performance in production
   - Retrain periodically as needs evolve
```

### Training Data Format

The data teaches the model by example. Format is typically JSONL — one example per line:

```json
{"messages": [{"role": "user", "content": "Summarize this incident: DB pool exhausted, payment svc down 5 min"}, {"role": "assistant", "content": "SEV2 | payment-svc | Root cause: DB connection pool exhaustion | Duration: 5min | Action: scaled pool"}]}
{"messages": [{"role": "user", "content": "Summarize this incident: API gateway 504s during deploy"}, {"role": "assistant", "content": "SEV2 | api-gateway | Root cause: deploy overlap | Duration: 8min | Action: rollback"}]}
```

After seeing enough of these, the model learns your *exact* incident summary format and style — something that would be tedious to specify in every prompt.

---

## 💻 Fine-Tuning Example (OpenAI Managed)

Managed services handle the GPU complexity for you:

```python
from openai import OpenAI
client = OpenAI()

# 1. Upload your training data
file = client.files.create(
    file=open("training_data.jsonl", "rb"),
    purpose="fine-tune"
)

# 2. Start the fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=file.id,
    model="gpt-4o-mini-2024-07-18",
    hyperparameters={"n_epochs": 3}   # How many passes over the data
)

# 3. Once complete, use YOUR custom model
response = client.chat.completions.create(
    model="ft:gpt-4o-mini:my-org:custom:abc123",  # Your fine-tuned model ID
    messages=[{"role": "user", "content": "Summarize this incident: ..."}]
)
# It now responds in your trained format automatically
```

---

## ⚠️ Fine-Tuning Pitfalls (Learn From Others' Mistakes)

| Pitfall | What happens | How to avoid |
|---------|--------------|--------------|
| **Overfitting** | Model memorizes training data, fails on new inputs | Use validation set, fewer epochs, more diverse data |
| **Catastrophic forgetting** | Model loses general abilities | Use PEFT/LoRA, don't over-train |
| **Poor data quality** | "Garbage in, garbage out" | Curate carefully — quality over quantity |
| **Too few examples** | Not enough signal to learn | Ensure sufficient, varied examples |
| **Fine-tuning for knowledge** | Wrong tool, unreliable, gets stale | Use RAG instead |
| **Ignoring cost** | Bills add up | Use PEFT, evaluate if it's even needed |

**The #1 mistake:** trying to fine-tune to add knowledge. If you find yourself thinking "I'll fine-tune it on our docs so it knows our product" — stop, and use RAG instead.

---

## 📊 Cost & Effort Comparison

| Approach | Cost | Effort | Time | Adds Knowledge? | Changes Behavior? |
|----------|------|--------|------|-----------------|-------------------|
| Prompt engineering | Free | Low | Minutes | No | Somewhat |
| RAG | Low | Medium | Hours-days | **Yes** | No |
| LoRA fine-tuning | Medium | Medium-high | Days | Weakly | **Yes** |
| Full fine-tuning | High | High | Days-weeks | Weakly | **Yes (deeply)** |

---

## 🎯 Interview Quick Points

- Fine-tuning adapts a pre-trained model to your task/style
- **Fine-tune for BEHAVIOR/style; use RAG for KNOWLEDGE** (know this cold)
- Order of preference: prompt engineering → RAG → fine-tuning (cheapest first)
- **LoRA** = freeze the model, train small adapters (~90% quality, tiny cost)
- **QLoRA** = LoRA + quantization (fine-tune large models on one GPU)
- Data **quality matters more than quantity** — curate carefully
- Main risks: overfitting, catastrophic forgetting, wasted cost
- The #1 mistake: fine-tuning to add facts (use RAG instead)
- Managed services (OpenAI, Bedrock) hide the GPU complexity
