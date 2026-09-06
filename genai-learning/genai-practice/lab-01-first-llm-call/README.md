# Lab 01: Your First LLM Call

## 🎯 Objective
Make your first LLM API call and build a simple interactive chatbot. Learn the request/response structure, temperature, and conversation history.

## 📋 Prerequisites
```bash
pip install openai python-dotenv
export OPENAI_API_KEY=sk-your-key
```

## 🧪 Steps

### Step 1: Simplest possible call
Run `chatbot.py` (see solution). You'll send one message and get one response.

### Step 2: Experiment with temperature
Change `temperature` from 0 to 1 and re-run the same prompt several times:
- `temperature=0` → same answer every time (deterministic)
- `temperature=1` → varied answers (creative)

### Step 3: Add conversation memory
Notice the chatbot remembers earlier messages because we send the full history each call.

## ✅ Expected Output
```
You: What is Kubernetes?
Bot: Kubernetes is an open-source container orchestration platform...

You: Who created it?
Bot: It was originally created by Google...   ← remembers "it" = Kubernetes
```

## 🏋️ Exercises
1. Add a system prompt to make the bot answer only about DevOps topics
2. Add a `/reset` command to clear conversation history
3. Track and print total tokens used per conversation
4. Add error handling for API failures (see error-handling module)

## 🔑 Key Concepts Practiced
- API request/response structure
- `temperature` parameter
- Conversation history (context)
- System vs user vs assistant roles
