"""
Gemini Example - Agentic Learning SDK

This example shows how to use the Agentic Learning SDK with Google's Gemini API.
The SDK automatically captures conversations and manages persistent memory.

Prerequisites:
    pip install agentic-learning
    pip install google-generativeai
    export GEMINI_API_KEY="your-api-key"

Usage:
    python3 gemini_example.py
"""

import os
import sys
import time
import google.generativeai as genai
from agentic_learning import learning, AgenticLearning
from agentic_learning.interceptors import auto_install
from utils import print_u, print_a, print_g, print_r, print_messages

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable not set")
    print("Please run: export GEMINI_API_KEY='your-api-key'")
    sys.exit(1)

genai.configure(api_key=api_key)

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

# Create a Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")

# Use the learning context - this is all you need!
with learning(agent="gemini-demo", client=learning_client):
    print_u("My name is Alice.")
    response = model.generate_content("My name is Alice.")
    print_a(f"{response.text}\n")

    time.sleep(5) # wait for memory to persist

    print_u("What's my name?")
    response = model.generate_content("What's my name?")
    print_a(f"{response.text}\n")

print_g("✓ Conversation automatically saved to Letta!\n")

# ============================================
# Example 2: Streaming
# ============================================

print("=" * 60)
print("Example 2: Streaming")
print("=" * 60)
print()

with learning(agent="gemini-demo", client=learning_client):
    print_u("Letta is my favorite context management service. Can you send me a summary about the product Letta (fka MemGPT) offers?")
    print_a("", end="", flush=True)

    response = model.generate_content(
        "Letta is my favorite context management service. Can you send me a summary about the product Letta (fka MemGPT) offers?",
        stream=True
    )

    for chunk in response:
        if hasattr(chunk, 'text'):
            print(chunk.text, end="", flush=True)

    print()

    time.sleep(5) # wait for memory to persist

    print_u("What's my favorite context management service?")
    print_a("", end="", flush=True)

    response = model.generate_content(
        "What's my favorite context management service?",
        stream=True
    )

    for chunk in response:
        if hasattr(chunk, 'text'):
            print(chunk.text, end="", flush=True)

    print()

print_g("✓ Streaming conversation automatically saved to Letta!\n")


# ===============================================
# Example 3: Capture-Only Mode and Memory Recall
# ===============================================

print("=" * 60)
print("Example 3: Capture-Only Mode and Memory Recall")
print("=" * 60)
print()

with learning(agent="gemini-demo", capture_only=True, client=learning_client):
    print_u("I am a software engineer.")
    response = model.generate_content("I am a software engineer.")
    print_a(f"{response.text}\n")

    time.sleep(5)  # Wait for memory to persist

    print_r("Testing recall without default memory injection\n")
    print_u("What's my professional background?")
    response = model.generate_content("What's my professional background?")
    print_a(f"{response.text}\n")

print_g("Testing memory recall via learning client\n")
print_u("What's my professional background?")
messages = learning_client.memory.search("gemini-demo", "What's my professional background?")
print_messages(messages)

print_g("\nListing stored message history\n")
messages = learning_client.messages.list("gemini-demo", limit=12)
print_messages(messages)

print_g("✓ Memory recall successful!\n")

print("=" * 60)
print("All examples complete!")
print("=" * 60)
