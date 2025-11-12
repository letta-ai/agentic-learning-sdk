"""
Quickstart - Agentic Learning SDK

Get started with persistent memory in 30 seconds.

Prerequisites:
    pip install agentic-learning anthropic
    export ANTHROPIC_API_KEY="your-api-key"
    export LETTA_API_KEY="your-api-key"

Usage:
    python3 quickstart.py
"""

from anthropic import Anthropic
from agentic_learning import learning
import time

# Initialize LLM client
client = Anthropic()

def ask_claude(message: str):
    """Send a message to Claude and print the response."""
    print(f"User: {message}\n")

    # That's it - wrap your API calls to enable persistent memory
    with learning(agent="quickstart-demo"):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": message}]
        )
        print(f"Assistant: {response.content[0].text}\n")

# Memory automatically persists across LLM API calls
ask_claude("My name is Alice and I love Python.")

time.sleep(5) # Wait for memory to persist

ask_claude("What's my name and favorite language?")
