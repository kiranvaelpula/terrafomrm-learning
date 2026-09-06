# Embeddings and Vector Databases

> **Embeddings convert text (or images) into numerical vectors that capture meaning, enabling semantic search — the foundation of RAG and modern AI search.**

---

## 📖 What is an Embedding? (Building Intuition)

Computers don't understand words — they understand numbers. So how do we make a computer grasp that "dog" and "puppy" are related, but "dog" and "car" aren't?

The answer is **embeddings**: we convert each piece of text into a list of numbers (a **vector**) in a way that captures its *meaning*. The magic is that texts with similar meaning end up with similar numbers.

```
"dog"   → [0.20, -0.50, 0.80, ...]   (e.g., 1536 numbers)
"puppy" → [0.19, -0.48, 0.79, ...]   (very close to "dog" — similar meaning)
"car"   → [-0.70, 0.30, -0.10, ...]  (far from "dog" — different meaning)
```

### The Spatial Analogy

Imagine a giant map where every possible piece of text is a point. On this map:
- "dog," "puppy," and "canine" cluster together in one neighborhood
- "car," "vehicle," and "automobile" cluster in another
- The distance between points reflects how different their meanings are

An embedding is just the *coordinates* of a piece of text on this "meaning map." Except instead of 2 dimensions (like a real map), it uses hundreds or thousands of dimensions to capture all the nuances of meaning.

```
"How do I reset my password?"
"I forgot my login credentials"
"I can't get into my account"
   ↑ Three different phrasings, but they land in the SAME neighborhood
     on the meaning map → similar vectors
```

This is the breakthrough: **embeddings capture meaning, not just words.**

---

## 🎯 Why Embeddings Matter

Traditional keyword search matches exact words and fails on meaning:

```
Query: "car"
Keyword search finds: documents containing the literal word "car"
Keyword search MISSES: "automobile", "vehicle", "sedan", "SUV"
                       (same meaning, different words)

Semantic search (embeddings) finds ALL of them
   because they're near "car" on the meaning map.
```

This unlocks a huge range of applications:

| Application | How embeddings help |
|-------------|---------------------|
| **Semantic search** | Find by meaning, not exact keywords |
| **RAG** | Find the most relevant docs to feed an LLM |
| **Recommendations** | "Items similar to this one" |
| **Clustering** | Group similar documents automatically |
| **Classification** | Categorize by semantic similarity |
| **Deduplication** | Find near-duplicate content |
| **Anomaly detection** | Find text that's unlike everything else |

---

## 🧮 How Similarity is Measured

Once text is a vector, how do we measure how "close" two vectors are? The standard method is **cosine similarity**, which measures the *angle* between two vectors (ignoring their length).

```
Cosine similarity ranges from -1 to 1:

   1.0  → identical direction (same meaning)
   0.0  → perpendicular (unrelated)
  -1.0  → opposite direction (opposite meaning)

Examples:
"password reset"  vs  "forgot login"   → 0.89  (very similar)
"password reset"  vs  "billing issue"  → 0.35  (somewhat related — both support)
"password reset"  vs  "pizza recipe"   → 0.03  (unrelated)
```

**Why the angle, not distance?** Because it focuses on *direction* (meaning) rather than *magnitude* (which can be affected by text length). Two documents about the same topic point in the same direction even if one is longer.

---

## 🗄️ Vector Databases (Searching by Meaning)

Here's the problem: if you have a million documents (a million vectors), how do you quickly find the 5 most similar to a query? Comparing against all million one by one is too slow.

**Vector databases** solve this. They're specialized databases built to store vectors and find "nearest neighbors" (most similar vectors) extremely fast, using clever indexing algorithms (like HNSW — Hierarchical Navigable Small World graphs).

```
Regular database:  "Find rows WHERE name = 'John'"   (exact match)
Vector database:   "Find the 5 vectors most SIMILAR to this one" (similarity)
```

### The Workflow

```
SETUP (once):
  Documents → convert each to an embedding → store vectors in the DB

QUERY (each time):
  1. Convert the query to a vector
  2. Vector DB finds the nearest stored vectors (most similar)
  3. Return those documents
```

### Popular Vector Databases

| Database | Type | Best for |
|----------|------|----------|
| **Pinecone** | Managed cloud | Easy start, no ops |
| **Weaviate** | Open source / cloud | Feature-rich, hybrid search |
| **Chroma** | Open source, local | Prototyping, small projects |
| **pgvector** | PostgreSQL extension | Use your existing Postgres DB |
| **Milvus** | Open source | Large scale, self-hosted |
| **AWS OpenSearch** | Managed (AWS) | k-NN search, AWS integration |
| **Redis** | In-memory | Ultra-fast, with vector module |

**Choosing:** For prototypes, Chroma (local, zero setup). If you already run Postgres, pgvector avoids adding new infra. For managed scale, Pinecone or OpenSearch.

---

## 🛠️ Practical Example

### Generating and comparing embeddings

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

def get_embedding(text):
    """Convert text into a vector (list of numbers capturing meaning)."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding    # e.g., 1536 numbers

def cosine_similarity(a, b):
    """Measure how similar two vectors are (1=identical, 0=unrelated)."""
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Compare meanings
v1 = get_embedding("How do I reset my password?")
v2 = get_embedding("I forgot my login credentials")
v3 = get_embedding("What's the weather today?")

print(cosine_similarity(v1, v2))  # ~0.85 — similar meaning
print(cosine_similarity(v1, v3))  # ~0.10 — unrelated
```

### Storing and searching in a vector DB (Chroma)

```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("support_docs")

# Add documents — Chroma auto-generates embeddings for you
collection.add(
    documents=[
        "To reset your password, click 'Forgot Password' on the login page.",
        "Our office is open 9am-5pm, Monday through Friday.",
        "Contact support at help@example.com or call 1-800-555-0100."
    ],
    ids=["doc1", "doc2", "doc3"]
)

# Semantic search — note the query uses DIFFERENT words than the doc
results = collection.query(
    query_texts=["I can't log into my account"],
    n_results=1
)
# Returns doc1 (password reset) — matched by MEANING, not keyword overlap.
# The words "log into" and "account" never appear in doc1, yet it matches!
```

This example shows the power: the query "I can't log into my account" matches the password-reset doc even though they share almost no words — because they *mean* the same thing.

---

## 📏 Chunking (Preparing Documents for Embedding)

A real document (say, a 50-page manual) is too big to embed as a single vector — you'd lose all detail, and retrieval would be useless. So we split documents into smaller **chunks**, embed each one, and store them separately.

```
Large document (50 pages)
      │
      ▼ split into chunks (e.g., ~500 tokens each)
Chunk 1 │ Chunk 2 │ Chunk 3 │ ... │ Chunk N
      │
      ▼ embed each chunk
Vector 1, Vector 2, ... Vector N → store all in vector DB
```

### The Chunking Trade-off

```
Small chunks (e.g., 200 tokens):
  + Precise — a match points to exactly the relevant sentence
  − May lack context — the sentence alone might not make sense

Large chunks (e.g., 1000 tokens):
  + More context — surrounding info is included
  − Less precise — the relevant bit is diluted with irrelevant text
```

### Overlap

Chunks usually **overlap** slightly (e.g., 50 tokens) so that a sentence split across a boundary isn't lost:

```
Chunk 1: "...the refund policy allows returns within 30 days. To"
Chunk 2: "within 30 days. To initiate a return, contact support..."
              └── overlap prevents losing the sentence at the boundary
```

### Chunking Strategies

| Strategy | Description |
|----------|-------------|
| Fixed-size | N tokens with fixed overlap — simple, general purpose |
| Sentence/paragraph | Split at natural language boundaries |
| Semantic | Split where the topic shifts |
| Structural | Split by document structure (headings, sections) |

There's no universal best — it depends on your documents. Well-structured docs benefit from structural chunking; prose does well with sentence-based chunking.

---

## 🎯 Interview Quick Points

- Embeddings = numeric vectors capturing the *meaning* of text
- Similar meanings → similar vectors (even with completely different words)
- Think of it as a "meaning map" where related concepts cluster together
- **Cosine similarity** measures how close two vectors are (angle-based, 1=identical)
- **Vector databases** find nearest neighbors (similar vectors) fast, not exact matches
- They use indexing like HNSW for speed at scale
- Powers semantic search, RAG, recommendations, clustering, dedup
- **Chunking** = splitting docs before embedding; trade-off between precision and context
- **Overlap** between chunks prevents losing info at boundaries
- Popular vector DBs: Pinecone, Chroma, pgvector, Weaviate, OpenSearch
- Embeddings are the foundation of RAG (the next major topic)
