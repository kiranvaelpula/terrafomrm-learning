# AI Agents

> **AI agents are LLM-powered systems that can reason, plan, use tools, and take actions autonomously to accomplish multi-step goals — going beyond simple question-answering.**

---

## 📖 What is an AI Agent? (The Leap from Chatbot to Agent)

A plain LLM call is **one-shot**: you send a prompt, you get text back. It can't do anything in the world — it can only produce words.

An **agent** is fundamentally different. It can:
- **Reason** about a goal and break it into steps
- **Use tools** (call APIs, run code, search the web, query databases)
- **Observe** the results of its actions
- **Loop** — adjust its plan based on what it learns, until the goal is done

The difference is the leap from *talking* to *doing*.

```
Plain LLM:  "What's 4,827 × 3,916?"
            → "18,904,332" (LLMs are bad at arithmetic — likely WRONG)

Agent:      "What's 4,827 × 3,916?"
            → Reasons: "I should use a calculator, not guess"
            → Action: calculator(4827, 3916)
            → Observation: 18,902,532
            → "The answer is 18,902,532" (CORRECT — it used a tool)
```

The agent recognized its own weakness (math) and used a tool to compensate. That self-directed use of tools is the essence of agency.

---

## 🏗️ Agent Architecture (The Components)

```
┌───────────────────────────────────────────────┐
│                     AGENT                        │
│                                                  │
│   ┌──────────────┐                              │
│   │     LLM       │ ← the "brain": reasons,      │
│   │  (reasoning)  │   plans, decides what to do  │
│   └──────┬───────┘                              │
│          │ decides on an action                  │
│          ▼                                        │
│   ┌──────────────┐      ┌──────────────┐        │
│   │    Tools      │      │    Memory     │       │
│   │  (actions)    │      │   (context)   │       │
│   └──────────────┘      └──────────────┘        │
│   - Web search           - Conversation history   │
│   - Calculator           - Results of past actions│
│   - API calls            - Retrieved documents    │
│   - Code execution       - Working notes          │
│   - Database queries                              │
└───────────────────────────────────────────────┘
```

- **The LLM** is the reasoning engine — it decides *what to do next*.
- **Tools** are how the agent affects the world — each tool is a function the agent can call.
- **Memory** lets the agent remember what it has done and learned across steps (without it, each step would be amnesiac).

---

## 🔄 The ReAct Pattern (Reasoning + Acting)

The most common and important agent pattern is **ReAct** — the agent alternates between reasoning and acting in a loop.

```
Goal: "What's the weather in the city where our main office is located?"

┌─ Thought: I don't know where the main office is. Let me look it up.
│  Action:  search_company_database("main office location")
│  Observation: "Main office: Seattle, WA"
│
├─ Thought: Now I need the current weather in Seattle.
│  Action:  get_weather("Seattle")
│  Observation: "58°F, cloudy"
│
└─ Thought: I now have everything I need.
   Answer:  "The weather at the main office in Seattle is 58°F and cloudy."
```

The loop is: **Thought → Action → Observation → (repeat) → Answer.**

Why this is powerful: no single tool could answer this question. The agent had to *chain* two lookups, using the result of the first (Seattle) to drive the second (weather). This kind of multi-step problem-solving is what agents unlock.

---

## 🔧 Tools / Function Calling (How Agents Act)

Modern LLMs support **function calling** — you describe the available tools, and the model decides when and how to call them, returning structured arguments.

```python
from openai import OpenAI
client = OpenAI()

# Step 1: Describe the tools available to the agent
tools = [{
    "type": "function",
    "function": {
        "name": "get_pod_count",
        "description": "Get the number of running pods for a service",
        "parameters": {
            "type": "object",
            "properties": {
                "service":   {"type": "string", "description": "service name"},
                "namespace": {"type": "string", "description": "k8s namespace"}
            },
            "required": ["service"]
        }
    }
}]

# Step 2: The model decides whether to call a tool
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user",
               "content": "How many pods is the payment service running in prod?"}],
    tools=tools
)

# Step 3: The model returns a structured tool call:
#   get_pod_count(service="payment", namespace="prod")
# Step 4: YOUR code executes that function, gets the real result
# Step 5: You feed the result back to the model
# Step 6: The model gives the final natural-language answer
```

The crucial point: **the LLM doesn't run the tool itself** — it *decides* to call it and produces the arguments. Your code actually executes it and returns the result. This keeps you in control of what the tools do (important for security).

The `description` fields matter a lot — the model uses them to decide when each tool is appropriate. Write clear descriptions.

---

## 🧩 Agent Frameworks

You rarely build agents from scratch. Frameworks handle the loop, tool management, and memory:

| Framework | Notes |
|-----------|-------|
| **LangChain** | Most popular, huge ecosystem, chains + agents |
| **LangGraph** | Graph-based, stateful agent workflows (more control) |
| **LlamaIndex** | Strong for RAG + agents over your data |
| **CrewAI** | Multi-agent collaboration, role-based |
| **AutoGen** | Microsoft, multi-agent conversations |
| **AWS Bedrock Agents** | Fully managed agents on AWS |

**Choosing:** LangChain for flexibility and ecosystem; LangGraph when you need precise control over complex stateful flows; Bedrock Agents if you're on AWS and want managed.

---

## 👥 Multi-Agent Systems

For complex tasks, multiple *specialized* agents can collaborate — like assembling a team of specialists rather than one generalist.

```
        ┌─────────────────┐
        │   Orchestrator   │  Coordinates the team, delegates
        └────────┬─────────┘
       ┌─────────┼─────────┐
       ▼         ▼         ▼
  ┌────────┐┌────────┐┌────────┐
  │Research││ Coder  ││Reviewer│
  │ Agent  ││ Agent  ││ Agent  │
  └────────┘└────────┘└────────┘

Example workflow (building a feature):
  1. Research agent gathers requirements & existing patterns
  2. Coder agent writes the implementation
  3. Reviewer agent checks for bugs/security
  4. Loop back to Coder if issues found
  5. Orchestrator assembles the final result
```

**Why multiple agents?** Each can have a focused role, specific tools, and a tailored prompt — often producing better results than one agent trying to do everything. It also mirrors how human teams divide work.

**Trade-off:** More agents = more complexity, more LLM calls (cost), and more places for things to go wrong. Don't over-engineer — use multi-agent only when the task genuinely benefits.

---

## 🛠️ DevOps Agent Example

```python
# An agent that investigates and remediates incidents

tools = [
    "get_service_logs(service, lines)",      # Read-only — safe
    "get_metrics(service, metric)",          # Read-only — safe
    "scale_service(service, replicas)",      # Action — moderate risk
    "restart_service(service)",              # Action — needs care
    "create_incident_ticket(summary)"        # Action — safe
]

# User: "The payment service is throwing 500 errors, investigate and fix."
#
# Agent's autonomous reasoning:
#   Thought:  Let me check the logs first.
#   Action:   get_service_logs("payment", 100)
#   Observe:  "ERROR: DB connection pool exhausted"
#
#   Thought:  Let me confirm with metrics.
#   Action:   get_metrics("payment", "db_connections")
#   Observe:  "Connections: 100/100 (maxed out)"
#
#   Thought:  The pool is exhausted. Scaling adds capacity.
#   Action:   scale_service("payment", 5)   ← should this need approval?
#   Observe:  "Scaled to 5 replicas"
#
#   Thought:  Document this for the team.
#   Action:   create_incident_ticket("Payment 500s: DB pool exhausted, scaled to 5")
#
#   Answer:   "Root cause was DB connection pool exhaustion. I scaled
#              the service to 5 replicas and created ticket INC-1234."
```

Notice: the agent chained diagnosis → confirmation → remediation → documentation autonomously. But also notice `scale_service` and `restart_service` are *actions with real consequences* — which brings us to the critical topic of guardrails.

---

## 🌍 Real-World Example: AI Coding Assistants

The AI coding assistants many developers use every day — **Kiro, GitHub Copilot, Cursor, Claude Code** — are concrete, production examples of agentic GenAI. They demonstrate every concept in this chapter:

| Agent Concept | How coding assistants use it |
|---------------|------------------------------|
| **LLM brain** | Powered by a foundation model (an LLM) that reasons about your request |
| **Tools** | Read/write files, run shell commands, search the codebase, run tests, git operations |
| **ReAct loop** | Think ("I need to see the config") → Act (read file) → Observe (file contents) → repeat |
| **Context/RAG** | Retrieve and read relevant files from your repo to ground responses in your actual code |
| **Memory** | Track the conversation and prior actions across a task |
| **Guardrails** | Confirm before destructive actions (deleting files, force-pushing), safety boundaries |

```
You: "Fix the failing test in the auth module"

Agent (like Kiro):
  Thought:  I need to find the failing test.
  Action:   search_codebase("auth test")
  Observe:  found test_auth.py
  Thought:  Let me read it and the code it tests.
  Action:   read_file("test_auth.py"), read_file("auth.py")
  Observe:  [file contents] — sees the bug
  Thought:  The token expiry check is inverted. I'll fix it.
  Action:   edit_file("auth.py", fix)
  Action:   run_command("pytest test_auth.py")
  Observe:  tests pass
  Answer:   "Fixed the inverted token expiry check in auth.py. Tests pass."
```

This is exactly the ReAct pattern with tools — the assistant reasons, uses tools to read/edit/test, observes results, and loops until the task is done. It's why these tools *do* work rather than just *describe* work.

**Kiro specifically** is an agentic AI development environment — it's an LLM plus tools (file editing, command execution, codebase search) plus context retrieval plus guardrails, wrapped into a coding assistant. If you're using Kiro to build this very learning module, you're watching an AI agent in action.

---

## ⚠️ Agent Risks & Guardrails (Non-Negotiable)

Agents take **actions**, which makes them powerful *and* dangerous. A hallucinating chatbot gives a wrong answer; a hallucinating agent might delete a database. Guardrails aren't optional.

| Risk | What could go wrong | Guardrail |
|------|---------------------|-----------|
| **Destructive actions** | Deletes data, breaks prod | Require human approval for high-impact ops |
| **Infinite loops** | Agent loops forever, burning money | Max iteration limits |
| **Runaway cost** | Thousands of LLM calls | Token/spend budgets per task |
| **Wrong tool use** | Calls tool with bad arguments | Validate tool inputs/outputs |
| **Prompt injection → bad action** | Malicious input triggers harmful action | Sanitize inputs, sandbox execution |
| **Over-permissioned** | Agent can do more than it should | Least-privilege tool access |

**The Golden Rule of Agents:**
```
NEVER let an agent execute irreversible or destructive actions
(delete data, production changes, spend money, send communications)
WITHOUT a human-in-the-loop approval step.

Read-only tools:  usually safe to automate
Write/destructive: require human confirmation
```

In the DevOps example above, `get_service_logs` (read-only) is safe to run automatically. But `restart_service` or `scale_service` in production should ideally pause for human approval — or be restricted to non-prod environments.

---

## 🎯 Interview Quick Points

- Agents = LLMs that reason, plan, use **tools**, and take actions autonomously
- The leap from chatbot to agent is *doing* vs just *talking*
- **ReAct pattern** = loop of Thought → Action → Observation until done
- **Function calling** = the LLM decides to call a tool; YOUR code executes it
- The LLM produces the tool call; it doesn't run tools itself (you stay in control)
- **Memory** lets agents carry context across steps
- **Multi-agent systems** = specialized agents collaborating (use when it genuinely helps)
- Frameworks: LangChain, LangGraph, CrewAI, Bedrock Agents
- **AI coding assistants (Kiro, Copilot, Cursor)** are real-world agentic GenAI — LLM + tools + context + guardrails
- **Guardrails are mandatory** — agents take real actions
- Golden rule: human approval for any destructive/irreversible action
