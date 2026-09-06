# LLMOps - Running GenAI in Production

> **LLMOps is MLOps for LLMs — the practices, tooling, and infrastructure to deploy, monitor, evaluate, and maintain GenAI applications reliably in production.**

---

## 📖 Why LLMOps Is Its Own Discipline

Getting a GenAI demo working is easy. Running it reliably in production, at scale, for real users, without surprises — that's hard, and it's what LLMOps addresses.

The reason it needs its own discipline is that LLMs break many assumptions that traditional software and even traditional ML rely on:

| Traditional MLOps | LLMOps |
|-------------------|--------|
| **Deterministic** — same input, same output | **Non-deterministic** — same input, varied output |
| Clear accuracy metrics (precision, recall) | Quality is subjective, hard to measure |
| You train and own the model | Often calling a third-party API you don't control |
| Batch predictions | Real-time streaming generation |
| Numeric/categorical outputs | Free-form text (hard to validate) |
| Cost = compute (predictable) | Cost = per-token (can explode unexpectedly) |

Think about testing: in normal software, you assert `output == expected`. But an LLM might phrase a correct answer a hundred different ways — so `==` doesn't work. This one difference cascades into needing entirely new approaches to testing, monitoring, and quality control.

---

## 🏗️ LLMOps Architecture

A production GenAI system is more than just "call the model." Here's what surrounds it:

```
┌─────────────────────────────────────────────────────────┐
│                    LLM Application                         │
│                                                            │
│  User → API Gateway → Orchestration Layer                  │
│                            │                               │
│         ┌──────────────────┼──────────────────┐          │
│         ▼                  ▼                  ▼           │
│    Prompt Mgmt      Model Router         Vector DB (RAG)   │
│    (versioned)      (pick the model)     (knowledge)       │
│         │                  │                  │           │
│         └──────────────────┼──────────────────┘          │
│                            ▼                               │
│              LLM (Bedrock / OpenAI / self-hosted)          │
│                            │                               │
│         ┌──────────────────┼──────────────────┐          │
│         ▼                  ▼                  ▼           │
│    Guardrails        Caching            Observability      │
│    (safety)          (cost/speed)       (logs/metrics)     │
└─────────────────────────────────────────────────────────┘
```

Each surrounding component solves a production problem: prompt management (versioning), model routing (cost/quality), caching (cost/latency), guardrails (safety), observability (knowing what's happening).

---

## 📊 Evaluation (The Hardest Part)

You can't just measure "accuracy" like traditional ML. So how do you know if your LLM app is good? Several complementary approaches:

### 1. LLM-as-a-Judge

Use a strong LLM to evaluate outputs — surprisingly effective and scalable.

```python
judge_prompt = """
Rate this AI response on a scale of 1-5 for accuracy and helpfulness.
Provide the score and a one-sentence justification.

Question: {question}
Response: {response}

Score (1-5):
"""
```

**Why it works:** A capable model can reliably judge quality dimensions that would be expensive to have humans check. You can run it on thousands of outputs automatically. **Caveat:** the judge has its own biases (e.g., preferring longer answers), so validate it against human judgment periodically.

### 2. Reference-Based Metrics

Compare outputs to known-good "gold" answers using metrics like semantic similarity (embedding-based), BLEU, or ROUGE. Good when you have reference answers.

### 3. Human Evaluation

The gold standard — humans review outputs. Expensive and slow, so you *sample* (review a subset) rather than checking everything. Essential for high-stakes applications.

### 4. Task-Specific Automated Checks

Often the most practical — check properties you can verify programmatically:

```python
# Structured output — does it parse?
assert json.loads(output)          # Valid JSON?

# Code generation — does it run and pass tests?
assert run_tests(generated_code)

# RAG — is the answer grounded in retrieved context?
assert answer_is_grounded(output, retrieved_docs)

# Safety — no PII leaked?
assert not contains_pii(output)

# Format — follows required structure?
assert output.startswith("SEV")
```

### Evaluation Dimensions

| Dimension | The question it answers |
|-----------|------------------------|
| Accuracy | Is it factually correct? |
| Relevance | Does it actually answer the question? |
| Groundedness | Is it based on provided context (RAG)? |
| Safety | Any harmful, biased, or leaked content? |
| Format | Correct structure/format? |
| Latency | Fast enough for users? |
| Cost | Within token budget? |

---

## 📈 Monitoring & Observability

Once in production, you need to *know what's happening*. Track two categories:

```
OPERATIONAL metrics (is it working?):
- Latency — time to first token, total response time
- Token usage — input + output tokens per request
- Cost — per request, per user, per day
- Error rates, timeouts, rate-limit hits
- Cache hit rate

QUALITY metrics (is it good?):
- Hallucination rate (sampled evaluation)
- User feedback (thumbs up/down)
- Guardrail trigger rate (how often is safety catching things?)
- Retrieval relevance (for RAG)
- Task success rate
```

Specialized observability tools capture the full trace of each request (prompt, retrieved docs, model output, tokens, cost):
```
Tools: LangSmith, Langfuse, Arize Phoenix, Helicone, plus CloudWatch
```

Why dedicated tools? Because debugging a GenAI issue means seeing the *entire chain* — what was retrieved, what prompt was built, what the model returned — not just a log line.

---

## 💰 Cost Management (Critical at Scale)

We saw earlier that token costs can explode. In production, cost engineering is a core LLMOps responsibility:

```python
# 1. SEMANTIC CACHING — reuse answers for similar questions
if cached := semantic_cache.get(query):   # Was a similar query asked recently?
    return cached                           # Skip the LLM call entirely — free!

# 2. MODEL ROUTING — cheap model for easy tasks, expensive for hard
if is_simple(query):
    model = "gpt-4o-mini"    # ~15x cheaper
else:
    model = "gpt-4o"         # Only when the task truly needs it

# 3. PROMPT COMPRESSION — trim unnecessary context (fewer input tokens)
# 4. max_tokens LIMITS — cap output length
# 5. RATE LIMITING per user — prevent abuse and runaway spend
# 6. BATCHING — process multiple items together where possible
```

**Semantic caching** is especially powerful — many users ask the same or similar things ("how do I reset my password"), and serving a cached answer costs nothing and is instant.

**Model routing** reflects a key principle: don't use a sledgehammer for a thumbtack. Most queries are simple and don't need your most expensive model.

---

## 🔄 Prompt Management (Prompts Are Code)

In production, prompts are as important as code — a bad prompt change can break everything. So treat them like code:

```
- Version control prompts (in Git, or a prompt registry)
- A/B test prompt variations to find what works best
- Separate prompts from application code (use templates)
- Track which prompt version produced which output (for debugging)
- Be able to roll back a bad prompt instantly
```

```python
# Versioned prompt templates
PROMPTS = {
    "incident_summary_v2": """You are an SRE. Summarize this incident
in 2 sentences, starting with the severity level: {logs}""",
}
# When you improve the prompt, it becomes v3 — old outputs are still
# traceable to v2, and you can roll back if v3 performs worse.
```

Why this matters: without prompt versioning, a well-meaning "quick tweak" to a prompt can silently degrade quality for all users, with no way to know what changed or revert.

---

## 🚀 Deployment Patterns

| Pattern | Description | Trade-off |
|---------|-------------|-----------|
| **API-based** | Call Bedrock/OpenAI | No infra, but pay per token, data leaves* |
| **Self-hosted** | Run open model (Llama) on your GPUs | Full control/privacy, but you manage GPUs |
| **Serverless** | Lambda + Bedrock, event-driven | Scales to zero, good for sporadic load |
| **Model serving** | vLLM, TGI, SageMaker endpoints | For efficient self-hosted serving |

Self-hosting considerations: GPU cost (expensive and scarce), autoscaling complexity, model update management — but you get full data privacy and control. Serving frameworks like **vLLM** dramatically improve throughput for self-hosted models.

---

## 🧪 Testing GenAI Apps (Preventing Regressions)

When you change a prompt or swap a model, how do you know you didn't break things? Regression tests:

```python
# A suite of test cases with expected properties
test_cases = [
    {"input": "reset password", "must_contain": ["Forgot Password"]},
    {"input": "office hours",    "must_contain": ["9", "5"]},
    {"input": "refund",          "must_contain": ["30 days"]},
]

for case in test_cases:
    output = rag_answer(case["input"])
    for expected in case["must_contain"]:
        assert expected in output, f"REGRESSION: '{expected}' missing for '{case['input']}'"

# Also test:
# - Safety: no PII leaks, refuses harmful requests
# - Format: returns valid JSON when required
# - Refusals: says "I don't know" when info isn't available
```

Because outputs vary, you don't test for exact string matches — you test for *properties* (contains the right info, has the right format, doesn't leak PII). Run this suite whenever you change prompts or models, ideally in CI/CD.

---

## 🎯 Interview Quick Points

- LLMOps = MLOps for LLMs (deploy, monitor, evaluate, maintain in production)
- Harder than MLOps: non-deterministic output, subjective quality, per-token cost
- You can't use `output == expected` — outputs vary, so test for *properties*
- **Evaluation:** LLM-as-a-judge, reference metrics, human review (sampled), task checks
- **Monitor** both operational (latency, cost, errors) and quality (hallucination, feedback)
- **Cost control:** semantic caching, model routing, prompt compression, token limits
- **Prompt management:** version like code, A/B test, roll back bad changes
- Deployment: API-based (managed) vs self-hosted (control/privacy, but GPU ops)
- **vLLM/TGI** improve self-hosted serving throughput
- Run regression tests (property-based) when changing prompts or models
