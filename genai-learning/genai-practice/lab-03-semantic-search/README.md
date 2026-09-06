# Lab 03: Embeddings & Semantic Search

## 🎯 Objective
Build a semantic search tool. Search documents by *meaning*, not keywords — demonstrating embeddings and vector similarity.

## 📋 Prerequisites
```bash
pip install openai chromadb python-dotenv
export OPENAI_API_KEY=sk-your-key
```

## 🧪 Steps

### Step 1: Generate embeddings
Convert a few sentences to vectors and print their similarity. See that similar meanings have high similarity scores.

### Step 2: Store in a vector database
Add documents to Chroma (it auto-embeds them).

### Step 3: Semantic search
Query with words that DON'T appear in the documents — and still get the right match because embeddings capture meaning.

## ✅ Expected Output
```
Query: "I can't log into my account"
Best match: "To reset your password, click Forgot Password"
(matched by MEANING — the words don't overlap!)

Similarity scores:
  "password reset" vs "forgot login"  → 0.87
  "password reset" vs "pizza recipe"  → 0.04
```

## 🏋️ Exercises
1. Load documents from a real folder of `.txt` files
2. Return the top 3 matches with their similarity scores
3. Add metadata (category, date) and filter searches by it
4. Compare search results using different embedding models

## 🔑 Key Concepts Practiced
- Generating embeddings
- Cosine similarity
- Vector databases (Chroma)
- Semantic vs keyword search
- Chunking (in the exercises)
