# GenAI Basics — Interview Questions

---

## Q1: What is the difference between Generative AI and traditional AI?
**A:** Traditional (discriminative) AI classifies or predicts — e.g., "is this spam?". Generative AI creates new content — text, images, code — by learning patterns from training data.

## Q2: What is an LLM?
**A:** A Large Language Model — a foundation model trained on massive text data that understands and generates human language. It works by predicting the next token repeatedly.

## Q3: What is a token?
**A:** A chunk of text the model processes — roughly 4 characters or ¾ of a word. Models charge per token and have token-based context limits.

## Q4: What is a foundation model?
**A:** A large model pre-trained on broad data that can be adapted (via prompting or fine-tuning) to many downstream tasks, instead of training a separate model per task.

## Q5: What is the Transformer architecture?
**A:** The neural network architecture behind modern GenAI (from "Attention Is All You Need," 2017). Its key innovation is the attention mechanism, which weighs the importance of each word relative to others to understand context.

## Q6: What is a hallucination?
**A:** When an LLM confidently generates false or fabricated information. It's a major risk because the output looks plausible. Mitigated with RAG, grounding, and verification.

## Q7: What does temperature control?
**A:** The randomness of output. Low (0-0.3) = deterministic, focused, good for facts/code. High (0.7-1.0) = creative, varied, good for brainstorming.

## Q8: What is a context window?
**A:** The maximum amount of text (input + output) a model can process at once, measured in tokens. Larger windows handle bigger documents but cost more.

## Q9: What is prompt engineering?
**A:** Crafting inputs to get better LLM outputs without training. Techniques include zero-shot, few-shot, chain-of-thought, role prompting, and structured output requests.

## Q10: What is chain-of-thought prompting?
**A:** Asking the model to reason step by step ("Let's think step by step"). It significantly improves accuracy on complex reasoning tasks by making the model show its work.

## Q11: What are embeddings?
**A:** Numeric vector representations of text that capture meaning. Similar meanings produce similar vectors, enabling semantic search regardless of exact wording.

## Q12: What is a vector database?
**A:** A database that searches by similarity (nearest neighbors) rather than exact match. Stores embeddings and finds the most semantically similar entries. Examples: Pinecone, Chroma, pgvector.

## Q13: How is an LLM trained?
**A:** Three stages: (1) Pre-training on trillions of tokens, (2) Supervised fine-tuning on instruction-response pairs, (3) RLHF (Reinforcement Learning from Human Feedback) to align it to be helpful and safe.

## Q14: What's the difference between open and closed models?
**A:** Closed models (GPT-4, Claude) are API-only, most capable, no infra needed. Open models (Llama, Mistral) can be self-hosted for data privacy, full control, and customization.

## Q15: What is prompt injection?
**A:** A security attack where users craft input to override the system's instructions (e.g., "ignore previous instructions"). Defended by treating user input as untrusted data, using delimiters, and adding guardrails.
