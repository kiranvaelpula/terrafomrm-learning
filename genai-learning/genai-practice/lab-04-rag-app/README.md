# Lab 04: RAG Application — Q&A Over Your Docs

## 🎯 Objective
Build a complete RAG system: a Q&A bot that answers questions using YOUR documents, with grounding and citations. **This is the key milestone lab.**

## 📋 Prerequisites
```bash
pip install openai chromadb python-dotenv
export OPENAI_API_KEY=sk-your-key
```

## 🧪 Steps

### Step 1: Prepare a knowledge base
Put some `.txt` or `.md` files in a `docs/` folder (or use the sample docs in the code).

### Step 2: Index the documents
Chunk → embed → store in the vector DB (the indexing phase).

### Step 3: Query with RAG
Embed the question → retrieve relevant chunks → build augmented prompt → generate a grounded answer.

### Step 4: Verify grounding
Ask a question NOT covered by the docs — the bot should say "I don't have that information" instead of hallucinating.

## ✅ Expected Output
```
Q: What is the refund window?
A: The refund window is 30 days from the date of purchase. [source: policy.txt]

Q: What is the CEO's favorite color?
A: I don't have that information in the provided documents.
   ← It refused to hallucinate!
```

## 🏋️ Exercises
1. Load real docs from a folder instead of hardcoded strings
2. Add chunking for large documents (split into ~500-token pieces)
3. Return citations (which document each answer came from)
4. Add conversation memory (multi-turn RAG)
5. Measure retrieval quality — is the right chunk being retrieved?
6. Add metadata filtering (only search docs from a certain category)

## 🔑 Key Concepts Practiced
- The full RAG pipeline (index + query)
- Grounding answers in real data
- Preventing hallucination ("say I don't know")
- Chunking (in exercises)
- Citations (in exercises)

## 💡 This is the Foundation
RAG is the most common production GenAI pattern. Master this lab and you can build most enterprise GenAI applications (internal knowledge bots, doc Q&A, customer support).
