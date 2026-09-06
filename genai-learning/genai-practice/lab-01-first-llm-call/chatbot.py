#!/usr/bin/env python3
"""
Lab 01: Interactive chatbot with conversation memory.
Demonstrates LLM calls, temperature, and maintaining context.
"""

import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def chat():
    """Run an interactive chatbot that remembers the conversation."""
    # System prompt sets the bot's behavior
    messages = [
        {"role": "system", "content": "You are a helpful DevOps assistant. Keep answers concise."}
    ]

    print("DevOps Bot ready! Type 'quit' to exit, '/reset' to clear history.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "quit":
            break
        if user_input == "/reset":
            messages = messages[:1]  # Keep only the system prompt
            print("(history cleared)\n")
            continue
        if not user_input:
            continue

        # Add the user's message to the conversation history
        messages.append({"role": "user", "content": user_input})

        try:
            # The FULL history is sent each time — that's how the bot "remembers"
            response = client.chat.completions.create(
                model="gpt-4o-mini",       # Cheap model, good for learning
                messages=messages,
                temperature=0.7,           # Try 0 vs 1 to see the difference
                max_tokens=300
            )

            answer = response.choices[0].message.content
            print(f"Bot: {answer}\n")

            # Add the bot's reply to history so it has context next turn
            messages.append({"role": "assistant", "content": answer})

            # Show token usage (cost awareness)
            usage = response.usage
            print(f"    [tokens: {usage.prompt_tokens} in + "
                  f"{usage.completion_tokens} out = {usage.total_tokens}]\n")

        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY environment variable first.")
        exit(1)
    chat()
