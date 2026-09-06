# Advanced RAG Patterns & Architectures

> **Basic RAG works, but production systems need advanced techniques to improve retrieval accuracy, handle complex queries, and scale reliably.**

---

## 📖 Why Basic RAG Isn't Enough

The basic RAG we learned (embed query → search → generate) is a great start, but it fails in predictable ways as you move to production:

```
- Complex multi-part questions:
  "Compare our refund policy with our warranty terms"
  → needs info from TWO different documents

- Ambiguous or short queries:
  "What about the second option?"
  → meaningless without conversation context

- Large, noisy knowledge bases:
  → vector search returns somewhat-relevant but not-quite-right chunks

- Questions needing reasoning across documents:
  → basic RAG retrieves chunks but can't connect them
```

The advanced patterns below each target a specific failure mode. You don't need all of them — you add the ones that fix problems you actually observe.

---

## 🎯 Advanced Retrieval Techniques

### 1. Hybrid Search (Semantic + Keyword)

Pure semantic (vector) search is great for meaning but can miss exact terms like product codes, error codes, or specific names. Keyword search (BM25) catches those. Hybrid combines both.

```
Semantic search:  understands meaning
                  "car" → finds "automobile", "vehicle"
                  BUT might rank "ERR_4021" loosely

Keyword search:   exact term matching
                  "ERR_4021" → finds exact matches
                  BUT misses synonyms

Hybrid = run both, merge results, re-rank
       → catches both meaning AND exact terms
```

**When to use:** Your content has important exact identifiers (SKUs, error codes, proper nouns) alongside natural language.

### 2. Re-ranking (Retrieve Many, Keep the Best)

Vector search is fast but approximate. Re-ranking adds a second, more accurate scoring pass.

```
1. Vector search returns the top 20 candidate chunks (fast, approximate)
2. A re-ranker model scores each chunk's TRUE relevance to the query
3. Keep only the top 5 → send those to the LLM

The re-ranker (a cross-encoder or Cohere Rerank) looks at the query
and each chunk TOGETHER, which is more accurate than comparing
their separate embeddings.
```

**Why it helps:** Embedding similarity is a rough proxy for relevance. A dedicated re-ranker directly evaluates "does this chunk answer this query?" — catching cases where similar-looking chunks aren't actually relevant.

### 3. Query Transformation

Users write messy, ambiguous, or context-dependent queries. Rewrite them before retrieval.

```
Original (ambiguous):  "What about the second one?"
Rewritten (with context): "What are the features of the Premium
                           subscription tier?"

Techniques:
- Query expansion: add related terms
- HyDE: generate a hypothetical answer, then search using IT
        (the fake answer is often closer to real docs than the question)
- Multi-query: generate several phrasings, search with each
```

### 4. Multi-Query RAG

```
User question
    │
    ▼ generate 3-4 variations of the question
Query 1, Query 2, Query 3
    │
    ▼ search with each
Results 1, Results 2, Results 3
    │
    ▼ merge and deduplicate
Richer, more complete context → better answer
```

**When to use:** Broad questions where a single query might miss relevant angles.

---

## 🏗️ Advanced RAG Architectures

### Parent-Child (Small-to-Big) Retrieval

The chunking dilemma: small chunks retrieve precisely but lack context; large chunks have context but retrieve imprecisely. Parent-child gets both.

```
Embed and search on SMALL chunks (precise matching)
BUT return the LARGER parent chunk (full context) to the LLM

Search matches: "The refund window is 30 days"  (precise small chunk)
LLM receives:   the entire refund policy section  (full context)

Best of both: precise retrieval + rich context.
```

### Contextual Retrieval

A chunk can lose meaning when isolated. Add context to each chunk before embedding.

```
Original chunk:      "It costs $99 per month."
                     (Costs what? Meaningless alone.)

Contextualized:      "[From the Premium Plan section]
                      It costs $99 per month."
                     (Now the chunk is self-contained and searchable.)
```

This dramatically improves retrieval for chunks that reference things defined elsewhere.

### Agentic RAG

Instead of a fixed "always retrieve then generate" flow, an agent *decides* how to retrieve:

```
The agent can decide:
- Whether to search at all (some questions don't need it)
- WHICH knowledge base to query (docs? code? tickets?)
- Whether to do MULTIPLE searches (for multi-part questions)
- When it has ENOUGH information to answer
- Whether to reformulate and search again

More flexible and accurate for complex, varied queries — at the
cost of more LLM calls (higher latency/cost).
```

### GraphRAG

Build a knowledge graph (entities and their relationships) from your documents, then retrieve *connected* information — not just similar chunks.

```
Regular RAG: finds chunks similar to the query
GraphRAG:    understands relationships

Question: "Which projects did engineers who worked on Project X
           also contribute to?"
→ This needs to traverse relationships (person → project → person → project),
  which similarity search alone can't do. GraphRAG handles it.
```

**When to use:** Questions that require connecting multiple facts / multi-hop reasoning.

---

## 📊 RAG Evaluation Framework

You must evaluate RAG in two parts — because failure can happen at retrieval OR generation:

```
RETRIEVAL metrics (did we find the right info?):
- Context Precision: are the retrieved chunks actually relevant?
- Context Recall: did we retrieve ALL the info needed to answer?
- MRR (Mean Reciprocal Rank): is the best chunk ranked near the top?

GENERATION metrics (did we use it correctly?):
- Faithfulness: is the answer grounded in the retrieved context
                (or did the model add its own/wrong info)?
- Answer Relevance: does the answer address the question?
- Hallucination rate: did it make things up despite having context?
```

This separation is diagnostic: if retrieval precision is low, fix chunking/search. If retrieval is good but faithfulness is low, fix the prompt or model.

```python
# RAGAS — a popular RAG evaluation framework
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision

results = evaluate(
    dataset,   # your questions + retrieved contexts + answers + ground truth
    metrics=[faithfulness, answer_relevancy, context_precision]
)
# Tools: RAGAS, TruLens, LangSmith
```

---

## 🔧 Chunking Strategies (Advanced)

| Strategy | Description | Best for |
|----------|-------------|----------|
| Fixed-size | N tokens with overlap | Simple, general purpose |
| Semantic | Split where meaning/topic shifts | Coherent, self-contained chunks |
| Recursive | Split by structure: headers → paragraphs → sentences | Structured documents |
| Document-based | One chunk per logical section | Well-formatted docs (FAQs, manuals) |
| Sentence-window | Embed single sentences, return surrounding window | Maximum precision + context |

There's no universal best — match the strategy to your document structure. Experiment and measure retrieval quality.

---

## 🚀 Production RAG Optimizations

```
PERFORMANCE:
- Approximate Nearest Neighbor (ANN) indexes like HNSW for fast search at scale
- Cache frequent queries and their results
- Run retrieval and generation asynchronously where possible

QUALITY:
- Metadata filtering (date, source, department, permissions)
- Deduplicate near-identical chunks (avoid redundant context)
- Freshness — re-index when source documents change
- Fallback behavior when retrieval finds nothing relevant
  (don't force an answer from irrelevant chunks)

COST:
- Cache embeddings — don't re-embed unchanged documents
- Batch embedding generation
- Right-size retrieval (don't over-fetch chunks you won't use)
```

---

## 🎯 When RAG Isn't the Answer

RAG is for retrieving relevant *text*. It struggles with:

```
- Aggregation: "How many customers complained last month?"
  → This needs a database query / analytics, not text retrieval

- Math/computation: "What's our total revenue growth rate?"
  → Needs calculation (tool use), not retrieval

- Real-time data: "What's the current server load?"
  → Needs a live API call, not a stored document

- Multi-hop reasoning across many entities
  → GraphRAG or agentic approaches

Solution: combine RAG with agents and tools.
An agent can decide to query a database (SQL), call an API,
run a calculation, OR do RAG — whichever the question needs.
```

This is the frontier: RAG + agents + tools working together, where the system dynamically chooses the right approach per query.

---

## 🎯 Interview Quick Points

- Basic RAG fails on complex/ambiguous queries and noisy knowledge bases
- **Hybrid search** = semantic + keyword (catches meaning AND exact terms)
- **Re-ranking** = retrieve many, re-score accurately, keep the best
- **Query transformation** = rewrite ambiguous queries; HyDE, multi-query
- **Parent-child** = match small chunks, return larger context (best of both)
- **Contextual retrieval** = add context to chunks before embedding
- **Agentic RAG** = agent decides how/when/what to retrieve
- **GraphRAG** = knowledge graph for multi-hop/relationship questions
- Evaluate retrieval (precision/recall) AND generation (faithfulness) separately
- Tools: RAGAS, TruLens for RAG evaluation
- RAG isn't for aggregation/math/real-time — combine with agents and tools
