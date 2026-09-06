#!/usr/bin/env python3
"""
Lab 05: DevOps assistant agent using function calling.
Demonstrates the ReAct loop, tool use, and guardrails.
"""

import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# ═══════════ TOOLS (mocked for the lab) ═══════════
def get_pod_count(service, namespace="default"):
    """Read-only tool — safe to run automatically."""
    mock = {"payment": 3, "frontend": 5, "api": 4}
    return {"service": service, "namespace": namespace, "pods": mock.get(service, 0)}


def get_service_status(service):
    """Read-only tool — safe."""
    mock = {"payment": "healthy", "frontend": "healthy", "api": "degraded"}
    return {"service": service, "status": mock.get(service, "unknown")}


def restart_service(service):
    """DESTRUCTIVE tool — requires human approval (guardrail)."""
    approval = input(f"⚠️  Approve restart of '{service}'? (yes/no): ")
    if approval.lower() != "yes":
        return {"service": service, "result": "restart cancelled by user"}
    return {"service": service, "result": "restarted successfully"}


# Map tool names to functions
TOOL_FUNCTIONS = {
    "get_pod_count": get_pod_count,
    "get_service_status": get_service_status,
    "restart_service": restart_service,
}

# ═══════════ TOOL SCHEMAS (tell the model what's available) ═══════════
TOOLS = [
    {"type": "function", "function": {
        "name": "get_pod_count",
        "description": "Get the number of running pods for a service",
        "parameters": {"type": "object", "properties": {
            "service": {"type": "string"},
            "namespace": {"type": "string"}}, "required": ["service"]}}},
    {"type": "function", "function": {
        "name": "get_service_status",
        "description": "Get the health status of a service",
        "parameters": {"type": "object", "properties": {
            "service": {"type": "string"}}, "required": ["service"]}}},
    {"type": "function", "function": {
        "name": "restart_service",
        "description": "Restart a service (destructive - use with caution)",
        "parameters": {"type": "object", "properties": {
            "service": {"type": "string"}}, "required": ["service"]}}},
]


def run_agent(user_message, max_iterations=5):
    """The ReAct loop: reason -> act (tool) -> observe -> repeat."""
    messages = [
        {"role": "system", "content": "You are a DevOps assistant. Use tools to answer questions about services."},
        {"role": "user", "content": user_message}
    ]

    for _ in range(max_iterations):   # Iteration limit = guardrail
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=TOOLS
        )
        msg = response.choices[0].message
        messages.append(msg)

        # If the model didn't call a tool, it's giving the final answer
        if not msg.tool_calls:
            return msg.content

        # Execute each tool the model requested (the "Act" step)
        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"  [agent calls {fn_name}({args})]")

            result = TOOL_FUNCTIONS[fn_name](**args)   # Run the actual tool

            # Feed the result back (the "Observe" step)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

    return "Reached max iterations without a final answer."


if __name__ == "__main__":
    print("DevOps Agent ready. Try: 'How many pods is payment running?'\n")
    while True:
        q = input("You: ").strip()
        if q.lower() == "quit":
            break
        if q:
            print(f"Agent: {run_agent(q)}\n")
