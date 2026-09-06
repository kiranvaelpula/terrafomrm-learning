# AWS Bedrock & Cloud GenAI Services

> **AWS Bedrock is a fully-managed service that provides access to multiple foundation models through a single API, plus tools for RAG, agents, and guardrails.**

---

## 📖 What is AWS Bedrock? (And Why It Exists)

If you want to use GenAI in an enterprise, you face some challenges:
- You want the best models, but they come from different vendors (Anthropic, Meta, Amazon, Mistral) — do you integrate with each separately?
- You have sensitive data that can't leave your compliance boundary
- You need RAG, guardrails, and agents — do you build all that yourself?

**AWS Bedrock** solves these. It's a single managed service that gives you:
- Access to *many* foundation models through *one* API
- Your data stays within your AWS account (privacy/compliance)
- Built-in tools for RAG, guardrails, and agents

```
Your App ──▶ Bedrock API ──┬──▶ Claude (Anthropic)
                            ├──▶ Llama (Meta)
                            ├──▶ Titan (Amazon)
                            ├──▶ Mistral
                            └──▶ others

One API, many models. Switch models by changing one parameter,
not rewriting your integration.
```

The big win: you're not locked into one vendor, and you can pick the best (or cheapest) model per task without re-architecting.

---

## 🎯 Core Bedrock Features

| Feature | What it does | Replaces building... |
|---------|--------------|---------------------|
| **Model access** | Multiple FMs via unified API | Separate vendor integrations |
| **Knowledge Bases** | Managed RAG (chunk, embed, retrieve) | Your own RAG pipeline |
| **Agents** | Managed agents with tool use | Your own agent framework |
| **Guardrails** | Content filtering, PII redaction | Your own safety layer |
| **Fine-tuning** | Customize models on your data | Your own training infra |
| **Model evaluation** | Compare models on your tasks | Manual benchmarking |

The theme: Bedrock provides managed versions of the things you'd otherwise build yourself.

---

## 🛠️ Basic Bedrock Invocation

The simplest use — call a model directly:

```python
import boto3
import json

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

# Invoke Claude
response = bedrock.invoke_model(
    modelId='anthropic.claude-3-sonnet-20240229-v1:0',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {"role": "user", "content": "Explain what a VPC is in 2 sentences."}
        ]
    })
)

result = json.loads(response['body'].read())
print(result['content'][0]['text'])
```

To switch to a different model (say, Llama or Titan), you mostly change the `modelId` and adjust the body format — the integration pattern stays the same.

---

## 📚 Bedrock Knowledge Bases (Managed RAG)

Instead of building the whole RAG pipeline (chunking, embedding, vector DB, retrieval), Bedrock Knowledge Bases automate it:

```
S3 (your documents)
      │
      ▼
Bedrock Knowledge Base automatically:
  - Chunks the documents
  - Generates embeddings (using Titan Embeddings)
  - Stores vectors (OpenSearch Serverless / Aurora pgvector)
      │
      ▼
Query → retrieves relevant chunks → LLM generates grounded answer
        (all in a single API call)
```

The entire RAG flow we built manually in the RAG chapter — Bedrock does it for you:

```python
# retrieve_and_generate = full RAG in one call
bedrock_agent = boto3.client('bedrock-agent-runtime')

response = bedrock_agent.retrieve_and_generate(
    input={'text': 'What is our refund policy?'},
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': 'ABCD1234',
            'modelArn': 'anthropic.claude-3-sonnet-20240229-v1:0'
        }
    }
)
print(response['output']['text'])   # Grounded answer, with citations
```

**Why use this vs building your own RAG?** Less code, automatic chunking/embedding, managed vector store, built-in citations. The trade-off is less fine-grained control over chunking and retrieval strategy.

---

## 🛡️ Bedrock Guardrails

Guardrails enforce safety and compliance policies on both what goes *in* (user input) and what comes *out* (model output):

```
Guardrails can:
- Block denied topics       (e.g., don't give legal/medical advice)
- Filter harmful content    (hate, violence, sexual, misconduct)
- Redact PII                (SSNs, emails, phone numbers, credit cards)
- Block specific words      (competitor names, banned terms)
- Apply to BOTH input and output
```

```python
response = bedrock.invoke_model(
    modelId='anthropic.claude-3-sonnet-20240229-v1:0',
    guardrailIdentifier='gr-abc123',
    guardrailVersion='1',
    body=json.dumps({...})
)
# PII gets redacted automatically, denied topics get blocked,
# harmful content is filtered — without you writing that logic
```

This is important for compliance-heavy industries (healthcare, finance) where you *must* prevent the model from leaking PII or giving prohibited advice.

---

## 🤖 Bedrock Agents

Managed agents that use tools (implemented as Lambda functions) to take actions:

```
User request → Bedrock Agent
                   │
                   ├─ reasons about the task
                   ├─ calls "Action Groups" (your Lambda functions)
                   ├─ queries Knowledge Bases (for info)
                   └─ returns the completed result

Example: "Book a meeting room for 3pm tomorrow"
  → Agent calls check_availability Lambda
  → Agent calls book_room Lambda
  → Confirms to the user
```

Bedrock handles the agent loop (the ReAct-style reasoning), you just provide the tools as Lambdas and the knowledge bases. This is the managed alternative to building agents with LangChain yourself.

---

## ☁️ Cloud GenAI Services Comparison

Bedrock isn't the only option — each major cloud has its GenAI platform:

| Provider | Service | Models | Notes |
|----------|---------|--------|-------|
| **AWS** | Bedrock | Claude, Llama, Titan, Mistral | Multi-model, one API |
| **AWS** | SageMaker JumpStart | Open models | Deploy/fine-tune yourself |
| **Azure** | Azure OpenAI Service | GPT-4, GPT-4o, embeddings | OpenAI models on Azure |
| **Google** | Vertex AI | Gemini, open models | Google's platform |

If your organization is on AWS, Bedrock is the natural choice. On Azure, you'd typically use Azure OpenAI. On GCP, Vertex AI.

---

## 💡 Amazon Q (AWS's GenAI Assistants)

AWS also offers ready-made GenAI assistants built on this foundation:

| Product | Use |
|---------|-----|
| **Amazon Q Developer** | Coding assistant, AWS help (formerly CodeWhisperer) — like Copilot |
| **Amazon Q Business** | Enterprise chat over your company's data |

These are end-user products, whereas Bedrock is the platform you build custom applications on.

---

## 🔐 Why Use Bedrock vs a Direct API (like OpenAI)?

A common decision: call OpenAI's API directly, or go through Bedrock?

| Factor | Bedrock | Direct API (e.g., OpenAI) |
|--------|---------|---------------------------|
| Data privacy | Stays in your AWS account | Leaves to third party* |
| Model choice | Multiple models, one API | Single vendor |
| AWS integration | Native (IAM, VPC, CloudWatch, S3) | External integration |
| Compliance | Inherits AWS compliance certs | Vendor-dependent |
| Guardrails/RAG | Built-in, managed | Build yourself |
| Best models | Broad selection | Whatever that vendor offers |

*Enterprise API tiers offer data guarantees.

**Rule of thumb:** If you're an AWS shop with compliance needs, Bedrock keeps everything inside your AWS boundary with native IAM/VPC controls. If you just want a specific model with minimal setup, a direct API might be simpler.

---

## 🎯 Interview Quick Points

- Bedrock = managed access to multiple foundation models via one API
- Data stays in your AWS account (a key privacy/compliance advantage)
- Switch models by changing the `modelId` — no vendor lock-in
- **Knowledge Bases** = fully managed RAG (chunk, embed, retrieve, cite)
- **Guardrails** = content filtering, PII redaction, topic blocking (input + output)
- **Agents** = managed agents using Lambda-based tools (Action Groups)
- `invoke_model` for direct calls; `retrieve_and_generate` for RAG in one call
- **Amazon Q Developer** = coding assistant; **Q Business** = enterprise chat
- Alternatives: Azure OpenAI Service, Google Vertex AI, SageMaker JumpStart
- Use Bedrock over direct APIs for privacy, compliance, and AWS-native integration
