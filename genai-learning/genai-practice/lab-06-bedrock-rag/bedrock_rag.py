#!/usr/bin/env python3
"""
Lab 06 (Part 2): Managed RAG with Bedrock Knowledge Bases.
Full RAG (retrieve + generate) in a single API call.

Prerequisite: Create a Knowledge Base in the Bedrock console first,
then set KNOWLEDGE_BASE_ID below.
"""

import boto3
import os

bedrock_agent = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID", "REPLACE_WITH_YOUR_KB_ID")
MODEL_ARN = "anthropic.claude-3-sonnet-20240229-v1:0"


def rag_query(question):
    """Full RAG in one call: retrieve relevant chunks + generate answer."""
    response = bedrock_agent.retrieve_and_generate(
        input={"text": question},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                "modelArn": MODEL_ARN
            }
        }
    )

    answer = response["output"]["text"]

    # Extract citations (which documents the answer came from)
    citations = []
    for citation in response.get("citations", []):
        for ref in citation.get("retrievedReferences", []):
            source = ref.get("location", {}).get("s3Location", {}).get("uri", "unknown")
            citations.append(source)

    return answer, citations


if __name__ == "__main__":
    if KNOWLEDGE_BASE_ID == "REPLACE_WITH_YOUR_KB_ID":
        print("Set KNOWLEDGE_BASE_ID first (create a KB in the Bedrock console).")
        exit(1)

    answer, sources = rag_query("What is the refund policy?")
    print(f"Answer: {answer}")
    print(f"Sources: {sources}")
