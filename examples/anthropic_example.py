"""
Anthropic Example - Agentic Learning SDK

This example shows how to use the Agentic Learning SDK with Anthropic's Claude API.
The SDK automatically captures conversations and manages persistent memory.

Prerequisites:
    pip install agentic-learning anthropic
    export ANTHROPIC_API_KEY="your-api-key"
    export LETTA_API_KEY="your-api-key"

Usage:
    python3 anthropic_example.py
"""

import time
from anthropic import Anthropic
from agentic_learning import learning

client = Anthropic()

def ask_claude(message: str):
    print(f"User: {message}\n")

    # That's it - wrap your API calls to enable persistent memory
    with learning(agent="anthropic-demo"):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": message}]
        )
        print(f"Assistant: {response.content[0].text}\n")

# Memory automatically persists across LLM API calls
ask_claude("My name is Alice.")

time.sleep(7) # Memory persists during sleep-time

ask_claude("What's my name?")
