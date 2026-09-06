# LLMs and Foundation Models

> **Large Language Models (LLMs) are foundation models trained on vast text corpora that can understand and generate human language for a wide range of tasks.**

---

## 📖 What is a Foundation Model?

Before foundation models, if you wanted AI to do five different tasks — translate, summarize, classify sentiment, answer questions, and generate code — you'd typically train five separate models, each on task-specific labeled data. This was expensive and slow.

A **foundation model** changes that. It's a single large model pre-trained on broad, general data. Because it learned language so deeply, you can then *adapt* it to many tasks — often just by asking it differently (prompting), without any additional training.

```
        ┌─────────────────────────┐
        │   Foundation Model      │  Trained ONCE on massive general data
        │   (e.g., GPT-4, Claude) │
        └───────────┬─────────────┘
      ┌─────────────┼─────────────┬──────────────┐
      ▼             ▼             ▼              ▼
 Summarization  Code Gen    Translation    Q&A       ← One model, many tasks
```

The name "foundation" is deliberate — it's a *foundation* you build applications on top of, rather than something you build from scratch each time.

### Why This Was Revolutionary

The old way:
```
Task A → collect data → train model A
Task B → collect data → train model B
Task C → collect data → train model C   (expensive, slow, repetitive)
```

The foundation model way:
```
Train one big model once → prompt it for Task A, B, C, D...
(most tasks need zero additional training)
```

---

## 🧠 How LLMs Are Built (The Three Training Stages)

Understanding how an LLM is made explains a lot about its behavior. There are three stages:

### Stage 1: Pre-training (the expensive foundation)

```
- Feed the model trillions of tokens: web pages, books, code, articles
- Task: predict the next token, over and over
- The model adjusts billions of weights to get better at prediction
- Cost: millions of dollars, weeks of training on thousands of GPUs
```

After pre-training, the model is incredibly knowledgeable but **not yet helpful**. It's like a brilliant person who knows everything but doesn't understand that you want them to *answer your question* — they might just continue your text or ramble. A raw pre-trained model given "What is 2+2?" might respond with "What is 3+3? What is 4+4?" because it saw lists of questions in training.

### Stage 2: Supervised Fine-Tuning (SFT) — teaching it to follow instructions

```
- Show it thousands of high-quality examples: instruction → good response
- "Summarize this article" → [a good summary]
- "Write a Python function to..." → [correct code]
- The model learns the PATTERN of being a helpful assistant
```

Now the model understands it should *respond helpfully* to instructions, not just continue text.

### Stage 3: RLHF (Reinforcement Learning from Human Feedback) — alignment

```
- The model generates multiple responses to a prompt
- Humans rank them: "response A is better than response B"
- A "reward model" learns human preferences
- The LLM is tuned to produce responses humans prefer
```

This is the secret sauce that made ChatGPT feel so good. RLHF is what makes models helpful, harmless, and honest — it aligns their behavior with what humans actually want, including refusing harmful requests and admitting uncertainty.

**Summary:** Pre-training gives *knowledge*, SFT gives *instruction-following*, RLHF gives *alignment*.

---

## 📏 Understanding Model Size (Parameters)

You'll constantly see numbers like "7B" or "70B." These refer to **parameters** — the learned weights inside the model.

| Term | Meaning |
|------|---------|
| **Parameters** | The tunable weights. More generally = more capable, but slower and costlier |
| **7B, 13B, 70B** | Billions of parameters (Llama comes in these sizes) |
| **Training tokens** | How much data it learned from (GPT-4: ~13 trillion tokens) |

```
Small (1-8B params):    Fast, cheap, can run on a laptop/single GPU,
                        good for simple tasks, less "smart"

Medium (13-70B params): Balanced capability and cost

Large (100B+ params):   Most capable, expensive, usually API-only,
                        best for complex reasoning
```

**Important trend:** Bigger isn't always better anymore. Smaller, well-trained models (and techniques like distillation) now rival much larger older models. For many production tasks, a small fast model is the right choice — don't reflexively reach for the biggest one. This matters enormously for cost.

---

## 🎛️ Key Inference Parameters (How You Control Output)

When you call an LLM, several knobs control its behavior. Understanding these is essential:

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a haiku about servers"}],
    temperature=0.7,      # Randomness: 0=deterministic, 1+=creative
    max_tokens=100,       # Cap on output length
    top_p=0.9,            # Nucleus sampling (alternative to temperature)
    frequency_penalty=0,  # Discourage repeating the same words
    presence_penalty=0    # Encourage introducing new topics
)
```

### Temperature (the most important knob)

Temperature controls how the model picks the next token:

```
temperature = 0:    Always pick the most probable token
                    → deterministic, consistent, sometimes repetitive
                    → USE FOR: facts, code, extraction, classification

temperature = 0.7:  Sometimes pick slightly less probable tokens
                    → varied, natural, creative
                    → USE FOR: writing, brainstorming, chat

temperature = 1.0+: Take more risks with less probable tokens
                    → very creative but can become incoherent
                    → USE FOR: creative exploration
```

**Practical rule:** Use `temperature=0` when there's a *right answer* (math, code, data extraction). Use `0.7-1.0` when you want *variety* (creative writing, ideation).

### max_tokens

Caps how long the response can be. Important because:
- Longer output = more cost
- Prevents runaway generation
- Note: if set too low, the model gets cut off mid-sentence

### top_p (nucleus sampling)

An alternative to temperature. It restricts choices to the smallest set of tokens whose probabilities add up to `p`. `top_p=0.9` means "only consider the most likely tokens covering 90% of probability." Usually you tune either temperature *or* top_p, not both.

---

## 🪟 Context Windows (The Model's "Working Memory")

The context window is the maximum amount of text the model can consider at once — this includes your prompt, the conversation history, any retrieved documents, AND the generated output. Everything must fit.

```
┌──── Context Window (the total budget) ────────────────┐
│ System prompt + chat history + your question +         │
│ retrieved docs (RAG) + the model's response            │
└───────────────────────────────────────────────────────┘

If it all exceeds the window, older content gets truncated/dropped.
```

Approximate sizes (2026):
```
GPT-3.5:   ~4K-16K tokens   (a few pages)
GPT-4:     ~128K tokens     (a small book)
Claude:    ~200K tokens     (a large book)
Gemini:    ~1M+ tokens      (multiple books / large codebases)
```

**Why bigger isn't automatically better:**
- Larger context = higher cost (you pay for all those tokens)
- The **"lost in the middle" problem** — models pay most attention to the beginning and end of context, and can miss information buried in the middle. So stuffing everything in doesn't guarantee the model uses it well.

**Practical implication:** Even with huge windows, RAG (retrieving only the *relevant* bits) often beats dumping entire documents into context — it's cheaper and more accurate.

---

## 💰 The Cost Model (Why It Matters)

LLMs charge **per token**, and input and output are usually priced *differently* (output is often more expensive):

```
Cost = (input_tokens × input_price) + (output_tokens × output_price)

Illustrative example:
  Input:  10,000 tokens × $0.01 per 1K = $0.10
  Output:  2,000 tokens × $0.03 per 1K = $0.06
  ─────────────────────────────────────────────
  Total for this ONE call:              $0.16
```

That seems tiny — until you scale:
```
1 million calls/day × $0.16 = $160,000/day = ~$58M/year !!
```

This is why **cost engineering** is a real discipline in GenAI:

| Strategy | How it saves |
|----------|--------------|
| Use smaller models for simple tasks | 10-100x cheaper per token |
| Cache common responses | Skip the LLM call entirely |
| Trim unnecessary context | Fewer input tokens |
| Limit max_tokens | Fewer output tokens |
| Batch requests | Volume efficiency |
| RAG instead of huge context | Send only relevant text |

---

## 🔓 Open vs Closed Models (A Key Decision)

One of the biggest architectural decisions is whether to use a closed API model or a self-hosted open model.

| Factor | Closed (GPT-4, Claude) | Open (Llama, Mistral) |
|--------|------------------------|----------------------|
| Access | API only (over internet) | Download and self-host |
| Control | Vendor controls updates | You control everything |
| Data privacy | Data leaves your infra* | Data never leaves your infra |
| Cost | Pay per token | Pay for GPU infrastructure |
| Customization | Limited fine-tuning | Full fine-tuning freedom |
| Capability | Often state-of-the-art | Catching up fast |
| Ops burden | None (managed) | You manage GPUs, scaling, updates |

*Enterprise API tiers offer contractual "we won't train on your data" guarantees.

**How to decide:**
```
Choose CLOSED when:
- You want the best capability with zero infrastructure
- You don't have sensitive data concerns (or use enterprise tier)
- You want to move fast

Choose OPEN (self-hosted) when:
- Data absolutely cannot leave your environment (compliance, secrets)
- You need heavy customization / fine-tuning
- You have high volume where GPU costs beat per-token costs
- You need to run offline / air-gapped
```

Many organizations use **both** — closed models for general tasks, self-hosted open models for sensitive data.

---

## 🎯 Interview Quick Points

- Foundation models = pre-trained once, adaptable to many tasks
- Three training stages: **pre-training** (knowledge) → **SFT** (instruction-following) → **RLHF** (alignment)
- RLHF is what makes models helpful, harmless, and honest
- Parameters (7B, 70B) indicate size; bigger ≠ always better
- **Temperature** controls randomness: 0 for facts/code, 0.7+ for creativity
- **Context window** = total working memory (prompt + history + docs + output)
- Watch for the **"lost in the middle"** problem in large contexts
- LLMs charge **per token** (input + output priced separately) — costs scale fast
- **Open** = privacy/control/customization; **Closed** = capability/convenience
- Many orgs use both open and closed models
