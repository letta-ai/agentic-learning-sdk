"""
Streaming Example - Agentic Learning SDK

This example shows how to use streaming with the Agentic Learning SDK.
The SDK automatically captures streamed conversations and manages persistent memory.

Prerequisites:
    pip install agentic-learning anthropic
    export ANTHROPIC_API_KEY="your-api-key"
    export LETTA_API_KEY="your-api-key"

Usage:
    python3 streaming_example.py
"""

import time
from anthropic import Anthropic
from agentic_learning import learning

client = Anthropic()

def ask_claude(message: str):
    print(f"User: {message}\n")
    print("Assistant: ", end="", flush=True)

    # That's it - wrap your API calls to enable persistent memory
    with learning(agent="streaming-demo"):
        stream = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": message}],
            stream=True
        )

        for event in stream:
            if event.type == "content_block_delta":
                if hasattr(event.delta, 'text'):
                    print(event.delta.text, end="", flush=True)

        print("\n")

# Memory automatically persists across LLM API calls
ask_claude("Letta is my favorite context management service. Can you send me a summary about the product Letta (fka MemGPT) offers?")

time.sleep(7) # Memory persists during sleep-time

ask_claude("What is my favorite context management service?")
