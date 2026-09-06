# GenAI Advanced — Interview Questions

---

## Q1: What is LLMOps and how does it differ from MLOps?
**A:** LLMOps is the practice of deploying, monitoring, and maintaining LLM applications in production. It differs from MLOps because outputs are non-deterministic, quality is subjective (no simple accuracy metric), you often use third-party APIs, and cost is per-token (can explode at scale). New concerns: prompt management, hallucination monitoring, token cost control.

## Q2: How do you evaluate an LLM application in production?
**A:** Multiple methods: LLM-as-a-judge (a strong model scores outputs), reference-based metrics (compare to known-good answers), human evaluation (sampled), and task-specific checks (does the JSON parse, does the code run). Evaluate dimensions like accuracy, relevance, groundedness, safety, latency, and cost.

## Q3: How do you control GenAI costs at scale?
**A:** Semantic caching (skip LLM calls for similar queries), model routing (cheap model for simple tasks), prompt compression, max_token limits, rate limiting per user, and batching. Monitor per-token spend since it scales with volume.

## Q4: What is the #1 security risk for LLM applications?
**A:** Prompt injection — malicious input overriding system instructions. Indirect injection (hidden instructions in documents/webpages the AI reads) is especially dangerous. Defend by treating all external content as untrusted data, using delimiters, validating outputs, and least-privilege tool access.

## Q5: Why should you never blindly trust LLM output?
**A:** Insecure output handling. Executing LLM-generated code can run malicious commands; rendering output as HTML can cause XSS. Always validate, sanitize, and sandbox outputs before acting on them.

## Q6: How do you prevent data leakage to third-party LLM APIs?
**A:** Redact PII before sending, use models with no-training-on-your-data guarantees or self-host, apply access controls on RAG sources, encrypt data, and avoid logging sensitive prompts.

## Q7: What is "excessive agency" and how do you mitigate it?
**A:** When an agent has too much power to take actions. Mitigate with least-privilege tool access, human-in-the-loop approval for destructive/high-stakes actions, iteration limits, and spend caps. Never let an agent make irreversible changes autonomously.

## Q8: How do you improve RAG retrieval quality?
**A:** Hybrid search (semantic + keyword), re-ranking (retrieve many, re-score, keep best), query transformation (rewrite ambiguous queries), better chunking strategies, metadata filtering, and parent-child retrieval (match small, return larger context).

## Q9: What is re-ranking in RAG?
**A:** After vector search returns candidate chunks (fast but approximate), a re-ranker model re-scores them for actual relevance to the query, keeping only the best. Re-rankers (cross-encoders, Cohere Rerank) are more accurate than pure vector similarity.

## Q10: How do you evaluate a RAG system?
**A:** Separately measure retrieval and generation. Retrieval: context precision (are chunks relevant?), context recall (did we get all needed info?). Generation: faithfulness (is the answer grounded in context?), answer relevance, hallucination rate. Tools: RAGAS, TruLens.

## Q11: What is agentic RAG?
**A:** Instead of a fixed retrieve-then-generate flow, an agent decides how to retrieve — which knowledge base, whether to search at all, whether to do multiple searches, and when it has enough info. More flexible for complex queries.

## Q12: How do you handle hallucinations in production?
**A:** Ground answers with RAG, set temperature to 0 for facts, instruct the model to say "I don't know," require citations, use self-consistency (generate multiple and check agreement), and add human review for high-stakes outputs.

## Q13: When is RAG not enough, and what do you use instead?
**A:** RAG struggles with aggregation ("how many..."), math, and real-time data. Combine with agents and tools — SQL/analytics for aggregation, calculators or code execution for math, live API calls for real-time. GraphRAG for multi-hop reasoning.

## Q14: How do you manage prompts in production?
**A:** Treat prompts like code — version control them, separate from application code (templates), A/B test variations, track which prompt version produced which output, and be able to roll back bad prompts.

## Q15: How would you design a production GenAI chatbot over company documents?
**A:** RAG architecture: ingest docs to S3, chunk and embed into a vector DB (or Bedrock Knowledge Base), retrieve relevant context per query, generate grounded answers with citations. Add guardrails (PII redaction, topic filtering), access controls on sources, caching for cost, monitoring (latency, cost, feedback), and prompt versioning. Use temperature 0 and "answer only from context" to minimize hallucination.
