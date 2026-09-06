# Lab 05: AI Agent with Tools — DevOps Assistant

## 🎯 Objective
Build an AI agent that uses tools (function calling) to answer questions it can't answer alone — demonstrating the ReAct pattern, tool use, and guardrails.

## 📋 Prerequisites
```bash
pip install openai python-dotenv
export OPENAI_API_KEY=sk-your-key
```

## 🧪 Steps

### Step 1: Define tools
Create Python functions the agent can call (get pod count, get service status, calculator). These are mocked for the lab.

### Step 2: Describe tools to the model
Provide tool schemas so the model knows what's available and when to use them.

### Step 3: The agent loop
The model decides which tool to call → your code runs it → feed result back → model answers. This is the ReAct loop.

### Step 4: Add a guardrail
Mark a "restart_service" tool as requiring human approval — the agent must ask before using it.

## ✅ Expected Output
```
You: How many pods is the payment service running?
Agent: [calls get_pod_count(service="payment")]
Agent: The payment service is currently running 3 pods.

You: Restart the payment service
Agent: ⚠️ This is a destructive action. Approve restart of 'payment'? (yes/no)
```

## 🏋️ Exercises
1. Add a tool that "reads logs" and have the agent diagnose an issue
2. Add spend/iteration limits (max 5 tool calls per request)
3. Connect a real tool (e.g., actual `kubectl` via subprocess — read-only!)
4. Add memory so the agent remembers earlier findings

## ⚠️ Safety Note
The `restart_service` tool in this lab is MOCKED. If you connect real tools:
- Only automate READ-ONLY actions
- Require human approval for anything destructive
- Never let the agent touch production without guardrails

## 🔑 Key Concepts Practiced
- Function calling / tool use
- The ReAct loop (reason → act → observe)
- Agent guardrails (human approval)
- Iteration limits (in exercises)
