"""
Quickstart Async - Agentic Learning SDK

Get started with persistent memory in async Python.

Prerequisites:
    pip install agentic-learning anthropic
    export ANTHROPIC_API_KEY="your-api-key"
    export LETTA_API_KEY="your-api-key"

Usage:
    python3 quickstart_async.py
"""

import asyncio
from anthropic import AsyncAnthropic
from agentic_learning import learning

client = AsyncAnthropic()

async def ask_claude(message: str):
    print(f"User: {message}\n")

    async with learning(agent="quickstart-demo"):
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": message}]
        )
        print(f"Assistant: {response.content[0].text}\n")

async def main():
    # Memory automatically persists across LLM API calls
    await ask_claude("My name is Alice and I love Python.")

    await asyncio.sleep(5) # Wait for memory to persist

    await ask_claude("What's my name and favorite language?")

if __name__ == "__main__":
    asyncio.run(main())
