# GenAI Intermediate — Interview Questions

---

## Q1: What is RAG and why is it used?
**A:** Retrieval Augmented Generation combines an LLM with a retrieval system. Relevant documents are fetched and given to the LLM as context. It solves knowledge cutoff, enables private/current data, and reduces hallucination by grounding answers in real sources.

## Q2: Explain the RAG workflow.
**A:** Indexing (once): chunk documents → embed → store in vector DB. Query time: embed the question → search vector DB for relevant chunks → build a prompt with those chunks as context → LLM generates a grounded answer.

## Q3: RAG vs Fine-tuning — when to use which?
**A:** RAG adds knowledge (what the model knows); fine-tuning changes behavior (how it responds — style, format). RAG updates instantly by changing the vector DB; fine-tuning requires retraining. Use RAG for Q&A over docs, fine-tuning for consistent tone/format.

## Q4: What is fine-tuning and when is it appropriate?
**A:** Further training a pre-trained model on your examples to specialize its behavior/style. Appropriate when prompting and RAG aren't enough — e.g., a specific output format or domain tone. Not for adding knowledge (use RAG).

## Q5: What is LoRA?
**A:** Low-Rank Adaptation — a parameter-efficient fine-tuning method. Instead of updating all weights, it freezes the base model and trains small adapter matrices. Achieves ~90% of full fine-tuning quality at a fraction of the cost. QLoRA adds quantization to fit on a single GPU.

## Q6: What is an AI agent?
**A:** An LLM-powered system that reasons, plans, uses tools, and takes actions autonomously to accomplish multi-step goals — beyond one-shot Q&A. It loops through reasoning and acting until the goal is met.

## Q7: Explain the ReAct pattern.
**A:** Reasoning + Acting. The agent alternates: Thought (reason about next step) → Action (use a tool) → Observation (see result), looping until it can answer. This lets the LLM interact with external systems.

## Q8: What is function calling / tool use?
**A:** A capability where you describe available tools to the LLM, and the model decides when to call them, returning structured arguments. Your code executes the tool and feeds results back. It's how agents interact with APIs, databases, and code.

## Q9: What guardrails do AI agents need?
**A:** Human approval for destructive/irreversible actions, max iteration limits (prevent infinite loops), spend/token budgets, input validation, least-privilege tool access, and sandboxed execution. Never let an agent make prod changes or delete data without a human check.

## Q10: What is AWS Bedrock?
**A:** A fully managed service providing access to multiple foundation models (Claude, Llama, Titan, Mistral) through one API. Data stays in your AWS account. Includes managed RAG (Knowledge Bases), Agents, Guardrails, and fine-tuning.

## Q11: What are Bedrock Knowledge Bases?
**A:** Managed RAG — you point it at S3 documents and it automatically chunks, embeds, stores in a vector DB, and handles retrieval + generation. Avoids building the RAG pipeline yourself.

## Q12: What are Bedrock Guardrails?
**A:** Policies applied to inputs and outputs that block denied topics, filter harmful content, and redact PII. They enforce safety and compliance without custom code.

## Q13: How do you reduce hallucinations?
**A:** Use RAG to ground answers in real data, set temperature to 0 for factual tasks, instruct the model to say "I don't know" when uncertain, provide citations, and validate outputs. Prompt the model to answer only from provided context.

## Q14: What is chunking and why does it matter in RAG?
**A:** Splitting documents into smaller pieces before embedding. Chunk size affects retrieval quality — too small loses context, too large reduces precision. Overlap between chunks prevents losing information at boundaries.

## Q15: How do you optimize GenAI costs?
**A:** Use smaller models for simple tasks, cache common responses, trim unnecessary context, use RAG instead of huge context windows, batch requests, and set token limits. Monitor per-token spend since it scales with volume.
