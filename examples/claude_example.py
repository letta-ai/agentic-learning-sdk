"""
Claude Example - Agentic Learning SDK

This example shows how to use the Agentic Learning SDK with Claude Agent SDK.
The SDK automatically captures conversations and manages persistent memory.

Prerequisites:
    pip install agentic-learning
    pip install claude-agent-sdk
    export ANTHROPIC_API_KEY="your-api-key"

Usage:
    python3 claude_example.py
"""

import os
import sys
import time
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock
from agentic_learning import learning_async, AgenticLearning
from agentic_learning.interceptors import auto_install
from utils import print_u, print_a, print_g, print_r, print_messages

# Configure Claude
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY environment variable not set")
    print("Please run: export ANTHROPIC_API_KEY='your-api-key'")
    sys.exit(1)

# Install interceptors (this enables automatic memory integration)
installed = auto_install()
print(f"Installed interceptors: {installed}")
print()

# Create sync client for memory injection (works with async contexts)
learning_client = AgenticLearning(base_url="http://localhost:8283")


# ============================================
# Example 1: Store Memory
# ============================================

async def example_1():
    print("=" * 60)
    print("Example 1: Store Memory")
    print("=" * 60)
    print()

    # Create a Claude SDK client
    options = ClaudeAgentOptions()
    client = ClaudeSDKClient(options)

    # Use the learning context - this is all you need!
    async with learning_async(agent="claude-demo", client=learning_client):
        await client.connect()

        print_u("My name is Alice.")
        await client.query("My name is Alice.")
        print_a("", end="", flush=True)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end="", flush=True)
        print("\n")

        time.sleep(5) # wait for memory to persist

    # Create a separate session
    client = ClaudeSDKClient(options)

    async with learning_async(agent="claude-demo", client=learning_client):
        await client.connect()
    
        print_u("What's my name?")
        await client.query("What's my name?")
        print_a("", end="", flush=True)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end="", flush=True)
        print("\n")

        await client.disconnect()

    print_g("✓ Conversation automatically saved to Letta!\n")


# ============================================
# Example 2: Streaming (already streaming by nature)
# ============================================

async def example_2():
    print("=" * 60)
    print("Example 2: Streaming")
    print("=" * 60)
    print()

    options = ClaudeAgentOptions()
    client = ClaudeSDKClient(options)

    async with learning_async(agent="claude-demo", client=learning_client):
        await client.connect()

        print_u("Letta is my favorite context management service. Can you send me a summary about the product Letta (fka MemGPT) offers?")
        await client.query("Letta is my favorite context management service. Can you send me a summary about the product Letta (fka MemGPT) offers?")
        print_a("", end="", flush=True)

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end="", flush=True)

        print("\n")

        time.sleep(5) # wait for memory to persist

    # Create a separate session
    client = ClaudeSDKClient(options)

    async with learning_async(agent="claude-demo", client=learning_client):
        await client.connect()
    
        print_u("What's my favorite context management service?")
        await client.query("What's my favorite context management service?")
        print_a("", end="", flush=True)

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end="", flush=True)

        print("\n")

        await client.disconnect()

    print_g("✓ Streaming conversation automatically saved to Letta!\n")


# ===============================================
# Example 3: Capture-Only Mode and Memory Recall
# ===============================================

async def example_3():
    print("=" * 60)
    print("Example 3: Capture-Only Mode and Memory Recall")
    print("=" * 60)
    print()

    options = ClaudeAgentOptions()
    client = ClaudeSDKClient(options)

    async with learning_async(agent="claude-demo", capture_only=True, client=learning_client):
        await client.connect()

        print_u("I am a software engineer.")
        await client.query("I am a software engineer.")
        print_a("", end="", flush=True)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end="", flush=True)
        print("\n")

        time.sleep(5)  # Wait for memory to persist

    # Create a separate session
    client = ClaudeSDKClient(options)

    async with learning_async(agent="claude-demo", capture_only=True, client=learning_client):
        await client.connect()

        print_r("Testing recall without default memory injection\n")
        print_u("What's my professional background?")
        await client.query("What's my professional background?")
        print_a("", end="", flush=True)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end="", flush=True)
        print("\n")

        await client.disconnect()

    print_g("Testing memory recall via learning client\n")
    print_u("What's my professional background?")
    messages = learning_client.memory.search("claude-demo", "What's my professional background?")
    print_messages(messages)

    print_g("\nListing stored message history\n")
    messages = learning_client.messages.list("claude-demo", limit=12)
    print_messages(messages)

    print_g("✓ Memory recall successful!\n")


async def main():
    await example_1()
    await example_2()
    await example_3()

    print("=" * 60)
    print("All examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
