"""
Memory Context Client

Provides context management operations for memory.
"""

from typing import Any, List, Optional

from letta_client.types import BlockResponse


# =============================================================================
# Sync Memory Context Client
# =============================================================================


class ContextClient:
    """
    Synchronous context management client.

    Provides APIs for managing memory context configurations.
    """

    def __init__(self, parent_client: Any, letta_client: Any):
        """
        Initialize the context client.

        Args:
            parent_client (AgenticLearning): Parent client instance
            letta_client (Letta): Underlying Letta client instance
        """
        self._parent = parent_client
        self._letta = letta_client

    def retrieve(self, agent: str) -> Optional[str]:
        """
        Retrieve the memory context for the agent.

        Args:
            agent (str): Name of the agent to retrieve memory context for

        Returns:
            (str | None): Memory context string for prompt injection
        """
        blocks = self._parent.memory.list(agent)
        if not blocks:
            return None
        try:
            return _format_memory_blocks(blocks)
        except Exception:
            return _format_memory_blocks_fallback(blocks)


# =============================================================================
# Async Memory Context Client
# =============================================================================


class AsyncContextClient:
    """
    Asynchronous context management client.

    Provides async APIs for managing memory context configurations.
    """

    def __init__(self, parent_client: Any, letta_client: Any):
        """
        Initialize the async context client.

        Args:
            parent_client (AsyncAgenticLearning): Parent client instance
            letta_client (AsyncLetta): Underlying Letta client instance
        """
        self._parent = parent_client
        self._letta = letta_client

    async def retrieve(self, agent: str) -> Optional[str]:
        """
        Retrieve the memory context for the agent.

        Args:
            agent (str): Name of the agent to retrieve memory context for

        Returns:
            (str | None): Memory context string for prompt injection
        """
        blocks = await self._parent.memory.list(agent)
        if not blocks:
            return None
        try:
            return _format_memory_blocks(blocks)
        except Exception:
            return _format_memory_blocks_fallback(blocks)


# =============================================================================
# Helper Functions
# =============================================================================


def _format_memory_blocks(blocks: List[BlockResponse]) -> Optional[str]:
    """
    Format memory blocks into a readable context string.

    Args:
        blocks (list[BlockResponse]): List of memory block objects from Letta

    Returns:
        (str | None): Formatted string containing memory block contents
    """
    if not blocks:
        return None

    formatted_lines = []

    for block in blocks:
        if not block or not block.value:
            continue

        formatted_lines.append(f"<{block.label}>")
        if block.description:
            formatted_lines.append(f"<description>{block.description}</description>")
        formatted_lines.append(f"<value>{block.value}</value>")
        formatted_lines.append(f"</{block.label}>")

    if not formatted_lines:
        return None

    memory_system_message = "\n".join(formatted_lines)
    return f"<memory_blocks>\nThe following memory blocks are currently engaged:\n{memory_system_message}\n</memory_blocks>"

def _format_memory_blocks_fallback(blocks: List[BlockResponse]) -> Optional[str]:
    """
    Format memory blocks into a readable context string.

    Args:
        blocks (list[BlockResponse]): List of memory block objects from Letta

    Returns:
        (str | None): Formatted string containing memory block contents
    """
    if not blocks:
        return None

    formatted_lines = []

    for block in blocks:
        if not block or not block['value']:
            continue

        formatted_lines.append(f"<{block['label']}>")
        if block['description']:
            formatted_lines.append(f"<description>{block['description']}</description>")
        formatted_lines.append(f"<value>{block['value']}</value>")
        formatted_lines.append(f"</{block['label']}>")

    if not formatted_lines:
        return None

    memory_system_message = "\n".join(formatted_lines)
    return f"<memory_blocks>\nThe following memory blocks are currently engaged:\n{memory_system_message}\n</memory_blocks>"