"""
Interceptor Utilities

Shared utilities for SDK interceptors.
"""

from typing import AsyncGenerator, Generator


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
