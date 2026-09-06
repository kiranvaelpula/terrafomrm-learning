# GenAI Hands-On Labs

Practical, implementable labs to build real GenAI applications. Each lab builds on concepts from the learning modules.

## 🧪 Labs Overview

| Lab | Topic | What You'll Build | Difficulty |
|-----|-------|-------------------|------------|
| 01 | First LLM Call | A simple chatbot script | Beginner |
| 02 | Prompt Engineering | A structured log analyzer | Beginner |
| 03 | Embeddings & Semantic Search | A document search tool | Intermediate |
| 04 | RAG Application | Q&A bot over your own docs | Intermediate |
| 05 | AI Agent with Tools | A DevOps assistant agent | Advanced |
| 06 | AWS Bedrock RAG | Managed RAG on AWS | Advanced |

## 🔧 Prerequisites

```bash
# Python 3.9+
python3 --version

# Create a virtual environment
python3 -m venv genai-env
source genai-env/bin/activate      # Linux/macOS
# genai-env\Scripts\activate       # Windows

# Install common dependencies
pip install openai chromadb requests python-dotenv boto3
```

## 🔑 API Keys Setup

```bash
# Create a .env file (NEVER commit this!)
cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
# For AWS labs:
AWS_REGION=us-east-1
EOF

# Add .env to .gitignore
echo ".env" >> .gitignore
```

**Cost note:** These labs use paid APIs but cost only cents to run. Use `gpt-4o-mini` (cheap) for learning. Set usage limits in your OpenAI/AWS console.

## 📁 Lab Structure

Each lab folder contains:
- `README.md` — objective, steps, expected output
- Starter code and solution
- Exercises to extend it

## 🎯 Learning Path

```
Lab 01 (LLM basics)
   → Lab 02 (prompting)
      → Lab 03 (embeddings)
         → Lab 04 (RAG) ← the key milestone
            → Lab 05 (agents)
               → Lab 06 (AWS Bedrock)
```

Start with Lab 01 and progress in order — each builds on the previous.
