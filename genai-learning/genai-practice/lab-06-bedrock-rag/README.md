# Lab 06: AWS Bedrock — Managed RAG

## 🎯 Objective
Build RAG on AWS using Bedrock Knowledge Bases — the managed alternative to building the pipeline yourself. Compare it to Lab 04's manual RAG.

## 📋 Prerequisites
```bash
pip install boto3
aws configure   # Set up AWS credentials

# You need:
# - An AWS account with Bedrock access (request model access in console)
# - Model access enabled for Claude and Titan Embeddings
```

## 🧪 Steps

### Step 1: Enable model access
In AWS Console → Bedrock → Model access → request access to Claude and Titan Embeddings.

### Step 2: Direct model invocation
Run `bedrock_invoke.py` to call Claude directly (like Lab 01, but on AWS).

### Step 3: Create a Knowledge Base (Console)
- Upload documents to an S3 bucket
- Bedrock Console → Knowledge Bases → Create
- Point it at your S3 bucket
- It auto-chunks, embeds (Titan), and stores in OpenSearch Serverless

### Step 4: Query the Knowledge Base
Run `bedrock_rag.py` — full RAG in a single API call (`retrieve_and_generate`).

## ✅ Expected Output
```
Direct invocation:
  "A VPC is a virtual network isolated within AWS..."

Knowledge Base RAG:
  "According to the policy, refunds are accepted within 30 days."
  Sources: [s3://my-bucket/policy.pdf]
```

## 🏋️ Exercises
1. Add Bedrock Guardrails (PII redaction, topic blocking)
2. Compare answer quality: manual RAG (Lab 04) vs Bedrock Knowledge Base
3. Try different models (Claude vs Llama) — change one parameter
4. Build a Bedrock Agent with a Lambda tool

## 🔑 Key Concepts Practiced
- AWS Bedrock model invocation
- Managed RAG (Knowledge Bases)
- retrieve_and_generate API
- Comparing managed vs DIY approaches

## 💰 Cost Note
Bedrock charges per token + OpenSearch Serverless has an hourly cost.
Delete the Knowledge Base and OpenSearch collection when done to avoid charges.
