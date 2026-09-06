#!/usr/bin/env python3
"""
Lab 04: Complete RAG application.
Q&A bot that answers from YOUR documents, grounded with citations.
"""

import os
import chromadb
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# Sample knowledge base (replace with your real docs)
DOCUMENTS = [
    {"id": "policy", "text": "Refund policy: Customers can return items within 30 days of purchase for a full refund, provided they have a receipt."},
    {"id": "shipping", "text": "Shipping: Standard delivery takes 5-7 business days. Express delivery takes 1-2 days for an extra fee."},
    {"id": "support", "text": "Support is available Monday-Friday, 9am-5pm EST. Contact us at help@example.com."},
    {"id": "warranty", "text": "All electronics come with a 1-year manufacturer warranty covering defects."},
]


def build_index():
    """Indexing phase: store documents in the vector DB."""
    db = chromadb.Client().create_collection("knowledge_base")
    db.add(
        documents=[d["text"] for d in DOCUMENTS],
        ids=[d["id"] for d in DOCUMENTS]
    )
    return db


def rag_query(db, question):
    """Query phase: retrieve relevant chunks and generate a grounded answer."""
    # 1. Retrieve the most relevant chunks
    results = db.query(query_texts=[question], n_results=2)
    chunks = results["documents"][0]
    sources = results["ids"][0]

    context = "\n".join(f"[{sid}] {chunk}" for sid, chunk in zip(sources, chunks))

    # 2. Build the augmented prompt (grounded + refusal allowed + citation)
    prompt = f"""Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't have that information in the provided documents."
Cite the source in brackets, e.g. [policy].

Context:
{context}

Question: {question}
Answer:"""

    # 3. Generate (temperature 0 for factual accuracy)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    db = build_index()
    print("RAG Q&A Bot ready. Type 'quit' to exit.\n")

    # Demo questions
    demo = [
        "What is the refund window?",
        "How long does express shipping take?",
        "What is the CEO's favorite color?",   # Not in docs — should refuse
    ]
    for q in demo:
        print(f"Q: {q}")
        print(f"A: {rag_query(db, q)}\n")

    # Interactive mode
    while True:
        q = input("Q: ").strip()
        if q.lower() == "quit":
            break
        if q:
            print(f"A: {rag_query(db, q)}\n")
