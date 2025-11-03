"""
OpenAI Example - Agentic Learning SDK

This example shows how to use the Agentic Learning SDK with OpenAI's API.
The SDK automatically captures conversations and manages persistent memory.

Prerequisites:
    pip install agentic-learning
    pip install openai
    export OPENAI_API_KEY="your-api-key"

Usage:
    python3 openai_example.py
"""

import os
import sys
import time
from openai import OpenAI
from agentic_learning import learning, AgenticLearning
from utils import print_u, print_a, print_g, print_r, print_messages

# Configure OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY environment variable not set")
    print("Please run: export OPENAI_API_KEY='your-api-key'")
    sys.exit(1)

# Create shared client for all examples
learning_client = AgenticLearning(base_url="http://localhost:8283")


# ============================================
# Example 1: Store Memory
# ============================================

print("=" * 60)
print("Example 1: Store Memory")
print("=" * 60)
print()

# Create an OpenAI client
client = OpenAI(api_key=api_key)

# Use the learning context - this is all you need!
with learning(agent="openai-demo", client=learning_client):
    print_u("My name is Alice.")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "My name is Alice."}]
    )
    print_a(f"{response.choices[0].message.content}\n")

    time.sleep(5) # wait for memory to persist

    print_u("What's my name?")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "What's my name?"}]
    )
    print_a(f"{response.choices[0].message.content}\n")

print_g("✓ Conversation automatically saved to Letta!\n")

# ============================================
# Example 2: Streaming
# ============================================

print("=" * 60)
print("Example 2: Streaming")
print("=" * 60)
print()

with learning(agent="openai-demo", client=learning_client):
    print_u("Letta is my favorite context management service. Can you send me a summary about the product Letta (fka MemGPT) offers?")
    print_a("", end="", flush=True)

    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Letta is my favorite context management service. Can you send me a summary about the product Letta (fka MemGPT) offers?"}],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)

    print("\n")

    time.sleep(5) # wait for memory to persist

    print_u("What's my favorite context management service?")
    print_a("", end="", flush=True)

    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "What's my favorite context management service?"}],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)

    print("\n")

print_g("✓ Streaming conversation automatically saved to Letta!\n")


# ===============================================
# Example 3: Capture-Only Mode and Memory Recall
# ===============================================

print("=" * 60)
print("Example 3: Capture-Only Mode and Memory Recall")
print("=" * 60)
print()

with learning(agent="openai-demo", capture_only=True, client=learning_client):
    print_u("I am a software engineer.")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "I am a software engineer."}]
    )
    print_a(f"{response.choices[0].message.content}\n")

    time.sleep(5)  # Wait for memory to persist

    print_r("Testing recall without default memory injection\n")
    print_u("What's my professional background?")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "What's my professional background?"}]
    )
    print_a(f"{response.choices[0].message.content}\n")

print_g("Testing memory recall via learning client\n")
print_u("What's my professional background?")
messages = learning_client.memory.search("openai-demo", "What's my professional background?")
print_messages(messages)

print_g("\nListing stored message history\n")
messages = learning_client.messages.list("openai-demo", limit=12)
print_messages(messages)

print_g("✓ Memory recall successful!\n")

print("=" * 60)
print("All examples complete!")
print("=" * 60)
