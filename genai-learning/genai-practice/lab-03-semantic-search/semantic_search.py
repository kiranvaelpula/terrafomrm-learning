#!/usr/bin/env python3
"""
Lab 03: Semantic search using embeddings and a vector database.
Search by MEANING, not keywords.
"""

import os
import numpy as np
from openai import OpenAI
import chromadb

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def get_embedding(text):
    """Convert text to a vector."""
    resp = client.embeddings.create(model="text-embedding-3-small", input=text)
    return resp.data[0].embedding


def cosine_similarity(a, b):
    """Similarity between two vectors (1=identical, 0=unrelated)."""
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def demo_similarity():
    """Part 1: Show that similar meanings = similar vectors."""
    print("=== Similarity Demo ===")
    v1 = get_embedding("password reset")
    v2 = get_embedding("forgot login credentials")
    v3 = get_embedding("pizza recipe")

    print(f"'password reset' vs 'forgot login'  → {cosine_similarity(v1, v2):.2f}")
    print(f"'password reset' vs 'pizza recipe'  → {cosine_similarity(v1, v3):.2f}\n")


def demo_search():
    """Part 2: Semantic search with a vector database."""
    print("=== Semantic Search Demo ===")

    # Set up vector DB (Chroma auto-embeds using its default model)
    db = chromadb.Client().create_collection("support")
    db.add(
        documents=[
            "To reset your password, click 'Forgot Password' on the login page.",
            "Our office is open 9am-5pm Monday through Friday.",
            "Standard shipping takes 5-7 business days.",
        ],
        ids=["d1", "d2", "d3"]
    )

    # Query with words that DON'T appear in any document
    query = "I can't log into my account"
    results = db.query(query_texts=[query], n_results=1)

    print(f"Query: '{query}'")
    print(f"Best match: '{results['documents'][0][0]}'")
    print("(Matched by MEANING — note the words barely overlap!)\n")


if __name__ == "__main__":
    demo_similarity()
    demo_search()
