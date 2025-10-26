"""
Anthropic Example - Agentic Learning SDK

This example shows how to use the Agentic Learning SDK with Anthropic's Claude API.
The SDK automatically captures conversations and manages persistent memory.

Prerequisites:
    pip install agentic-learning
    pip install anthropic
    export ANTHROPIC_API_KEY="your-api-key"

Usage:
    python3 anthropic_example.py
"""

import os
import sys
import time
from anthropic import Anthropic
from agentic_learning import learning, AgenticLearning
from agentic_learning.interceptors import auto_install
from utils import print_u, print_a, print_g, print_r, print_messages

# Configure Anthropic
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY environment variable not set")
    print("Please run: export ANTHROPIC_API_KEY='your-api-key'")
    sys.exit(1)

# Install interceptors (this enables automatic memory integration)
installed = auto_install()
print(f"Installed interceptors: {installed}")
print()

# Create shared client for all examples
learning_client = AgenticLearning(base_url="http://localhost:8283")


# ============================================
# Example 1: Store Memory
# ============================================

print("=" * 60)
print("Example 1: Store Memory")
print("=" * 60)
print()

# Create an Anthropic client
client = Anthropic(api_key=api_key)

# Use the learning context - this is all you need!
with learning(agent="anthropic-demo", client=learning_client):
    print_u("My name is Alice.")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": "My name is Alice."}]
    )
    print_a(f"{response.content[0].text}\n")

    time.sleep(5) # wait for memory to persist

    print_u("What's my name?")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": "What's my name?"}]
    )
    print_a(f"{response.content[0].text}\n")

print_g("✓ Conversation automatically saved to Letta!\n")

# ============================================
# Example 2: Streaming
# ============================================

print("=" * 60)
print("Example 2: Streaming")
print("=" * 60)
print()

with learning(agent="anthropic-demo", client=learning_client):
    print_u("Letta is my favorite context management service. Can you send me a summary about the product Letta (fka MemGPT) offers?")
    print_a("", end="", flush=True)

    stream = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Letta is my favorite context management service. Can you send me a summary about the product Letta (fka MemGPT) offers?"}],
        stream=True
    )

    for event in stream:
        if event.type == "content_block_delta":
            if hasattr(event.delta, 'text'):
                print(event.delta.text, end="", flush=True)

    print("\n")

    time.sleep(5) # wait for memory to persist

    print_u("What's my favorite context management service?")
    print_a("", end="", flush=True)

    stream = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": "What's my favorite context management service?"}],
        stream=True
    )

    for event in stream:
        if event.type == "content_block_delta":
            if hasattr(event.delta, 'text'):
                print(event.delta.text, end="", flush=True)

    print("\n")

print_g("✓ Streaming conversation automatically saved to Letta!\n")


# ===============================================
# Example 3: Capture-Only Mode and Memory Recall
# ===============================================

print("=" * 60)
print("Example 3: Capture-Only Mode and Memory Recall")
print("=" * 60)
print()

with learning(agent="anthropic-demo", capture_only=True, client=learning_client):
    print_u("I am a software engineer.")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": "I am a software engineer."}]
    )
    print_a(f"{response.content[0].text}\n")

    time.sleep(5)  # Wait for memory to persist

    print_r("Testing recall without default memory injection\n")
    print_u("What's my professional background?")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": "What's my professional background?"}]
    )
    print_a(f"{response.content[0].text}\n")

print_g("Testing memory recall via learning client\n")
print_u("What's my professional background?")
messages = learning_client.memory.search("anthropic-demo", "What's my professional background?")
print_messages(messages)

print_g("\nListing stored message history\n")
messages = learning_client.messages.list("anthropic-demo", limit=12)
print_messages(messages)

print_g("✓ Memory recall successful!\n")

print("=" * 60)
print("All examples complete!")
print("=" * 60)
