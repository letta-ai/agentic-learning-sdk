"""
Interceptor Utilities

Shared utilities for SDK interceptors.
"""

from typing import AsyncGenerator, Dict, Generator, List

from ..types import Provider
from ..core import get_current_config


def wrap_streaming_generator(stream: Generator, callback):
    """
    Wrap a streaming generator to collect chunks and call callback when done.

    Args:
        stream: Original generator
        callback: Function to call with collected content when stream completes

    Yields:
        Each chunk from the original stream
    """
    collected = []
    try:
        for chunk in stream:
            collected.append(chunk)
            yield chunk
    finally:
        # After stream completes (or errors), call callback with collected content
        if collected:
            callback(collected)


async def wrap_streaming_generator_async(stream: AsyncGenerator, callback):
    """
    Wrap an async streaming generator to collect chunks and call callback when done.

    Args:
        stream: Original async generator
        callback: Function to call with collected content when stream completes

    Yields:
        Each chunk from the original stream
    """
    collected = []
    try:
        async for chunk in stream:
            collected.append(chunk)
            yield chunk
    finally:
        # After stream completes (or errors), call callback with collected content
        if collected:
            await callback(collected)


def _save_conversation_turn(
    provider: Provider,
    model: str,
    request_messages: List[dict] = None,
    response_dict: Dict[str, str] = None,
):
    """
    Save a conversation turn to Letta in a single API call.

    Args:
        provider: Provider of the messages (e.g. "gemini", "claude", "anthropic", "openai")
        model: Model name
        request_messages: List of request messages
        response_dict: Response from provider
    """
    config = get_current_config()
    if not config:
        return

    agent = config["agent_name"]
    client = config["client"]

    if not client:
        return

    try:
        # Get or create agent using simplified API
        agent_state = client.agents.retrieve(agent=agent)

        if not agent_state:
            agent_state = client.agents.create(
                agent=agent,
                memory=config["memory"],
            )

        return client.messages.capture(
            agent=agent,
            request_messages=request_messages or [],
            response_dict=response_dict or {},
            model=model,
            provider=provider,
        )

    except Exception as e:
        import sys
        print(f"[Warning] Failed to save conversation turn: {e}", file=sys.stderr)


async def _save_conversation_turn_async(
    provider: Provider,
    model: str,
    request_messages: List[dict] = None,
    response_dict: Dict[str, str] = None,
    register_task: bool = False,
):
    """
    Save a conversation turn to Letta in a single API call (async version).

    Args:
        provider: Provider of the messages (e.g. "gemini", "claude", "anthropic", "openai")
        model: Model name
        request_messages: List of request messages
        response_dict: Response from provider
        register_task: If True, create and register task instead of awaiting directly.
                      Use this for async generators where the context might exit during cleanup.
                      (default: False - executes immediately)
    """
    config = get_current_config()
    if not config:
        return

    agent = config["agent_name"]
    client = config["client"]
    memory = config.get("memory")

    if not client:
        return

    async def save_task():
        try:
            import asyncio
            loop = asyncio.get_event_loop()

            # Get or create agent using sync client in thread pool
            agent_state = await loop.run_in_executor(
                None,
                lambda: client.agents.retrieve(agent=agent)
            )

            if not agent_state:
                agent_state = await loop.run_in_executor(
                    None,
                    lambda: client.agents.create(
                        agent=agent,
                        memory=memory,
                    )
                )

            return await loop.run_in_executor(
                None,
                lambda: client.messages.capture(
                    agent=agent,
                    request_messages=request_messages or [],
                    response_dict=response_dict or {},
                    model=model,
                    provider=provider,
                )
            )

        except Exception as e:
            import sys
            print(f"[Warning] Failed to save conversation turn: {e}", file=sys.stderr)

    if register_task:
        # Create and register the task for later awaiting (used by Claude interceptor)
        import asyncio
        task = asyncio.create_task(save_task())
        config.get("pending_tasks", []).append(task)
    else:
        # Execute immediately (used by other interceptors)
        await save_task()
