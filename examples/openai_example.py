"""
OpenAI Example - Agentic Learning SDK

This example shows how to use the Agentic Learning SDK with OpenAI's API.
The SDK automatically captures conversations and manages persistent memory.

Prerequisites:
    pip install agentic-learning openai
    export OPENAI_API_KEY="your-api-key"
    export LETTA_API_KEY="your-api-key"

Usage:
    python3 openai_example.py
"""

import time
from openai import OpenAI
from agentic_learning import learning

client = OpenAI()

def ask_gpt(message: str):
    print(f"User: {message}\n")

    # That's it - wrap your API calls to enable persistent memory
    with learning(agent="openai-demo"):
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": message}]
        )
        print(f"Assistant: {response.choices[0].message.content}\n")

# Memory automatically persists across LLM API calls
ask_gpt("My name is Alice.")

time.sleep(7) # Memory persists during sleep-time

ask_gpt("What's my name?")
