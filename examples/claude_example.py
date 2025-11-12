"""
Claude Example - Agentic Learning SDK

This example shows how to use the Agentic Learning SDK with Claude Agent SDK.
The SDK automatically captures conversations and manages persistent memory.

Prerequisites:
    pip install agentic-learning claude-agent-sdk
    export ANTHROPIC_API_KEY="your-api-key"
    export LETTA_API_KEY="your-api-key"

Usage:
    python3 claude_example.py
"""

import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock
from agentic_learning import learning

options = ClaudeAgentOptions()
client = ClaudeSDKClient(options)

async def ask_claude(message: str):
    print(f"User: {message}\n")
    print("Assistant: ", end="", flush=True)

    # That's it - wrap your API calls to enable persistent memory
    async with learning(agent="claude-demo"):
        await client.connect()
        await client.query(message)

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end="", flush=True)
        print("\n")
        await client.disconnect()

async def main():
    # Memory automatically persists across LLM API calls
    await ask_claude("My name is Alice.")

    await asyncio.sleep(7) # Memory persists during sleep-time

    await ask_claude("What's my name?")

asyncio.run(main())
