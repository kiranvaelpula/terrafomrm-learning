# RAG - Retrieval Augmented Generation

> **RAG combines an LLM with a knowledge retrieval system, so the model answers using YOUR data — reducing hallucinations and enabling up-to-date, domain-specific responses.**

---

## 📖 Why RAG Exists (The Problem It Solves)

LLMs are impressive, but they have three fundamental limitations that make them risky for real applications:

**1. Knowledge cutoff.** A model is frozen at its training date. Ask GPT about an event from last week, and it either doesn't know or guesses. It literally has no information past its training cutoff.

**2. No access to your private data.** The model was trained on public internet text. It has never seen your company's internal wiki, your product documentation, your codebase, or your customer records. So it can't answer questions about them.

**3. Hallucination.** When a model doesn't know something, it doesn't say "I don't know" by default — it generates the most *plausible-sounding* answer, which may be completely fabricated.

```
Without RAG:
  User: "What's our company's refund policy?"
  LLM:  "Our refund policy allows returns within 14 days..."
        ↑ COMPLETELY MADE UP. The model never saw your policy.
          It sounds confident but it's fiction.

With RAG:
  User: "What's our company's refund policy?"
  System: [retrieves the ACTUAL policy document from your knowledge base]
  LLM:  "According to the policy, returns are accepted within 30 days
         with a receipt." ← Based on your REAL document.
```

**RAG is the single most important technique for building trustworthy GenAI applications**, because it grounds the model's answers in real, retrievable sources.

---

## 🏗️ How RAG Works (Step by Step)

RAG has two phases: an **indexing** phase (done once, ahead of time) and a **query** phase (done for each question).

### Indexing Phase (preparation)

```
Your documents (PDFs, wiki, docs, code)
      │
      ▼ 1. Split into chunks
Chunk 1, Chunk 2, ... Chunk N
      │
      ▼ 2. Convert each chunk to an embedding (vector)
Vector 1, Vector 2, ... Vector N
      │
      ▼ 3. Store in a vector database
Vector DB (ready to search)
```

### Query Phase (per question)

```
  ┌──────────────────┐
  │  User question    │  "What's our refund policy?"
  └────────┬─────────┘
           ▼ 1. Embed the question into a vector
  ┌──────────────────┐
  │  Query vector     │
  └────────┬─────────┘
           ▼ 2. Search vector DB for most similar chunks
  ┌──────────────────────────┐
  │  Top-K relevant chunks    │  (the actual refund policy text)
  └────────┬─────────────────┘
           ▼ 3. Build an augmented prompt
  ┌────────────────────────────────────────┐
  │ "Answer using ONLY this context:         │
  │  [retrieved refund policy chunks]        │
  │  Question: What's our refund policy?"     │
  └────────┬─────────────────────────────────┘
           ▼ 4. Send to the LLM
  ┌──────────────────┐
  │       LLM         │
  └────────┬─────────┘
           ▼
  Grounded answer based on YOUR real data
```

The key move is step 3: instead of asking the model to answer from memory, you *give it the relevant information* and ask it to answer based on that. This is like the difference between a closed-book exam (model relies on memory, may hallucinate) and an open-book exam (model reads the actual source, answers accurately).

---

## 🛠️ Complete RAG Implementation (Explained)

```python
from openai import OpenAI
import chromadb

client = OpenAI()

# ═══════════════ INDEXING (done once) ═══════════════
vector_db = chromadb.Client().create_collection("company_docs")

documents = [
    "Refund policy: Customers can return items within 30 days for a full refund.",
    "Shipping: Standard delivery takes 5-7 business days.",
    "Support hours: Monday-Friday, 9am-5pm EST.",
]
# Chroma auto-embeds these and stores them
vector_db.add(documents=documents, ids=["d1", "d2", "d3"])


# ═══════════════ QUERY TIME (per question) ═══════════════
def rag_answer(question):
    # Step 1 & 2: Retrieve the most relevant chunks
    results = vector_db.query(query_texts=[question], n_results=2)
    context = "\n".join(results['documents'][0])

    # Step 3: Build the augmented prompt
    #   - Explicitly instruct it to use ONLY the context
    #   - Give it permission to say "I don't know" (reduces hallucination)
    prompt = f"""Answer the question using ONLY the context below.
If the answer isn't in the context, say "I don't have that information."

Context:
{context}

Question: {question}
Answer:"""

    # Step 4: Generate — temperature 0 for factual accuracy
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

print(rag_answer("How long do I have to return something?"))
# → "Customers can return items within 30 days for a full refund."
#   Note: the question used different words ("return something")
#   than the doc ("return items") — semantic search still matched it.
```

Two crucial details that make this production-grade:
1. **"Answer using ONLY the context"** — stops the model from mixing in its own (possibly wrong) knowledge.
2. **"If not in context, say I don't have that information"** — gives the model an escape hatch instead of forcing it to hallucinate.

---

## 🎯 RAG vs Fine-Tuning (A Critical Distinction)

This is one of the most common points of confusion — and a frequent interview question.

| Aspect | RAG | Fine-Tuning |
|--------|-----|-------------|
| Purpose | Add **knowledge** (facts, data) | Change **behavior** (style, format, tone) |
| Analogy | Giving someone reference books | Sending someone to training school |
| Data freshness | Real-time — update the DB | Frozen at training time |
| Cost | Low (no training) | High (GPU training) |
| Update speed | Instant (add to vector DB) | Slow (retrain the model) |
| Hallucination | Reduces it (grounded in sources) | Doesn't fix it |
| Best for | Q&A over docs, current info, private data | Consistent tone/format, specialized tasks |

**The mental model:**
```
RAG changes WHAT the model knows (its information).
Fine-tuning changes HOW the model behaves (its style/skills).
```

Example: If you want a bot that answers questions about your product docs → **RAG** (it needs your knowledge). If you want a bot that always responds in your company's specific brand voice and JSON format → **fine-tuning** (it needs a behavior). If you want both → combine them.

**Interview gold:** "You can't fix hallucination or add fresh knowledge with fine-tuning — that's what RAG is for. Fine-tuning teaches behavior, not facts."

---

## 🔧 Improving RAG Quality

Basic RAG works, but real systems need tuning. Here are the main levers:

| Technique | What it does | When to use |
|-----------|--------------|-------------|
| **Better chunking** | Right-sized chunks with overlap | Retrieval feels off |
| **Hybrid search** | Combine keyword + semantic search | Exact terms matter (codes, names) |
| **Re-ranking** | Re-score retrieved chunks for relevance | Retrieved chunks are noisy |
| **Query rewriting** | Rephrase the user's query for retrieval | Ambiguous or short queries |
| **Metadata filtering** | Filter by date, source, permissions | Multi-source or access control |
| **Citations** | Return source docs so users verify | Trust and compliance |

```python
# Metadata filtering — retrieve only recent security docs
results = vector_db.query(
    query_texts=["password policy"],
    n_results=3,
    where={"department": "security", "year": {"$gte": 2025}}  # Filter
)
```

Metadata filtering is also how you enforce **access control** — a user should only retrieve chunks from documents they're allowed to see.

---

## ⚠️ Common RAG Problems (And Fixes)

| Problem | Likely Cause | Fix |
|---------|--------------|-----|
| Retrieves irrelevant chunks | Poor chunking or embeddings | Tune chunk size, add re-ranking |
| Answer lacks context | Chunks too small | Increase chunk size or overlap |
| Slow responses | Large/unoptimized vector DB | Use ANN index (HNSW), filtering |
| Still hallucinating | LLM ignoring the context | Stronger prompt, temperature 0 |
| Outdated answers | Stale vector DB | Re-index when documents change |
| Retrieves nothing relevant | Query mismatch | Query rewriting, hybrid search, fallback |

**A subtle but important point:** RAG is only as good as its retrieval. If retrieval returns the wrong chunks, even a perfect LLM gives a wrong answer. Most RAG debugging is actually *retrieval* debugging — check what chunks are being retrieved before blaming the model.

---

## 🏛️ RAG Architecture on AWS

```
S3 (documents)
   │
   ▼
Ingestion (chunk + embed)  ← Lambda, or Bedrock Knowledge Base (automated)
   │
   ▼
Vector store  ← OpenSearch Serverless / Aurora with pgvector
   │
   ▼
Bedrock (LLM)  ← retrieves relevant context, generates grounded answer
   │
   ▼
API Gateway → User
```

**AWS Bedrock Knowledge Bases** automate this entire pipeline — you point it at an S3 bucket of documents, and it handles chunking, embedding, storage, and retrieval for you. We cover this in the Bedrock chapter.

---

## 🎯 Interview Quick Points

- RAG = **retrieve** relevant data + feed it to the LLM as context
- Solves the three big LLM problems: knowledge cutoff, no private data, hallucination
- Analogy: turns a closed-book exam into an open-book exam
- Flow: embed query → search vector DB → augment prompt → generate
- **RAG adds knowledge; fine-tuning changes behavior** (know this cold)
- RAG updates instantly by updating the vector DB — no retraining
- Use temperature 0 and "answer only from context" + "say I don't know" for accuracy
- RAG quality = retrieval quality — debug retrieval first
- Improve with better chunking, hybrid search, re-ranking, citations, metadata filtering
- AWS Bedrock Knowledge Bases automate RAG end-to-end
