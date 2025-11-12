"""
Capture Only Example - Agentic Learning SDK

This example shows how to use capture_only mode to record conversations
without automatic memory injection, then retrieve memories manually.

Prerequisites:
    pip install agentic-learning anthropic
    export ANTHROPIC_API_KEY="your-api-key"
    export LETTA_API_KEY="your-api-key"

Usage:
    python3 capture_only_example.py
"""

import time
from anthropic import Anthropic
from agentic_learning import learning, AgenticLearning

client = Anthropic()

def ask_claude(message: str):
    print(f"User: {message}\n")

    # Use capture_only mode to store conversations without modifying LLM behavior
    with learning(agent="capture-only-demo", capture_only=True):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": message}]
        )
        print(f"Assistant: {response.content[0].text}\n")

learning_client = AgenticLearning()

def memory_search(prompt: str):
    print("\n--- Memory Search ---\n")
    print(f"Prompt: {prompt}\n")

    # Search through stored memories
    messages = learning_client.memory.search("capture-only-demo", prompt)
    
    for message in messages:
        if message.message_type == "user_message":
            print(f"User: {message.content}")
        elif message.message_type == "assistant_message":
            print(f"Assistant: {message.content}")

def message_history():
    print("\n--- Message History ---\n")

    # List message history
    messages = learning_client.messages.list("capture-only-demo")
    
    for message in messages:
        if message.message_type == "user_message":
            print(f"User: {message.content}")
        elif message.message_type == "assistant_message":
            print(f"Assistant: {message.content}")

ask_claude("My name is Alice.")

time.sleep(7) # Memory persists during sleep-time

# Without memory injection, Claude doesn't know about previous context
ask_claude("What's my name?")

# Retrieve answer from stored memory
memory_search("What's my name?")

# Retrieve conversation history
message_history()
