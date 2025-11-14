"""
Agentic Learning SDK - Core Context Manager

This module provides a unified context manager for automatic learning/memory integration
with Letta. It captures conversation turns and saves them to Letta for persistent memory.
"""

from contextvars import ContextVar, Token
from typing import List, Optional, Union


_LEARNING_CONFIG: ContextVar[Optional[dict]] = ContextVar('learning_config', default=None)

# Track whether interceptors have been installed
_INTERCEPTORS_INSTALLED = False


def get_current_config() -> Optional[dict]:
    """Get the current active learning configuration (context-local)."""
    return _LEARNING_CONFIG.get()


def _ensure_interceptors_installed():
    """
    Ensure SDK interceptors are installed (one-time setup).

    This auto-detects available SDKs and installs interceptors for them.
    Only runs once per process.
    """
    global _INTERCEPTORS_INSTALLED

    if _INTERCEPTORS_INSTALLED:
        return

    from .interceptors import install
    install()

    _INTERCEPTORS_INSTALLED = True


# =============================================================================
# Unified Dual-Mode Context Manager
# =============================================================================


class LearningContext:
    """
    Unified context manager for Letta learning integration.

    Supports both sync (with) and async (async with) usage patterns.
    """

    def __init__(
        self,
        agent: str,
        client: Optional[Union["AgenticLearning", "AsyncAgenticLearning"]],
        capture_only: bool,
        memory: List[str],
    ):
        """
        Initialize learning context.

        Args:
            agent: Name of the Letta agent to use for memory storage
            client: AgenticLearning or AsyncAgenticLearning client instance
            capture_only: Whether to skip auto-injecting memory into prompts
            memory: List of Letta memory block labels to configure for the agent
        """
        self.agent_name = agent
        self.client = client
        self.capture_only = capture_only
        self.memory = memory
        self._token: Optional[Token] = None

    def __enter__(self):
        """Enter the learning context (sync)."""
        _ensure_interceptors_installed()

        if self.client is None:
            from .client import AgenticLearning
            self.client = AgenticLearning()

        self._token = _LEARNING_CONFIG.set({
            "agent_name": self.agent_name,
            "client": self.client,
            "capture_only": self.capture_only,
            "memory": self.memory,
            "pending_user_message": None,
            "pending_tasks": [] 
        })

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the learning context (sync)."""
        if self._token is not None:
            _LEARNING_CONFIG.reset(self._token)

        return False

    async def __aenter__(self):
        """Enter the learning context (async)."""
        _ensure_interceptors_installed()

        if self.client is None:
            from .client import AsyncAgenticLearning
            self.client = AsyncAgenticLearning()

        self._token = _LEARNING_CONFIG.set({
            "agent_name": self.agent_name,
            "client": self.client,
            "capture_only": self.capture_only,
            "memory": self.memory,
            "pending_user_message": None,
            "pending_tasks": []  
        })

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the learning context (async)."""
        # Wait for any pending capture tasks (from Claude interceptor) to complete
        # before resetting context. This ensures the capture logic has access to config.
        config = _LEARNING_CONFIG.get()
        if config:
            pending_tasks = config.get("pending_tasks", [])
            if pending_tasks:
                # Give pending tasks a short grace period to complete
                import asyncio
                try:
                    await asyncio.wait(pending_tasks, timeout=5.0)
                except asyncio.TimeoutError:
                    # Tasks didn't complete in time
                    pass

        if self._token is not None:
            _LEARNING_CONFIG.reset(self._token)

        return False


def learning(
    agent: str = "letta_agent",
    client: Optional[Union["AgenticLearning", "AsyncAgenticLearning"]] = None,
    capture_only: bool = False,
    memory: List[str] = ["human"],
) -> LearningContext:
    """
    Create a learning context for automatic Letta integration.

    Works with both sync and async code patterns:
    - Use with 'with' for synchronous code
    - Use with 'async with' for asynchronous code

    All SDK interactions within this context will automatically:
    1. Capture user messages and assistant responses
    2. Save conversations to Letta for persistent memory
    3. Inject Letta memory into prompts (if capture_only=False)

    Args:
        agent: Name of the Letta agent to use for memory storage. Defaults to 'letta_agent'.
        client: Optional AgenticLearning or AsyncAgenticLearning client instance.
                If None, will create appropriate client based on usage (sync vs async).
        capture_only: Whether to capture conversations without automatic Letta memory injection (default: False)
        memory: Optional list of Letta memory blocks to configure for the agent (default: ["human"])

    Returns:
        LearningContext that can be used with both 'with' and 'async with'

    Examples:

        >>> from agentic_learning import learning
        >>> import anthropic
        >>>
        >>> client = anthropic.Anthropic()
        >>> with learning(agent="my_agent"):
        >>>     response = client.messages.create(
        >>>         model="claude-sonnet-4-20250514",
        >>>         messages=[{"role": "user", "content": "Hello"}]
        >>>     )

        With custom memory blocks:

        >>> with learning(agent="sales_bot", memory=["customer", "product"]):
        >>>     # Your LLM API calls here
        >>>     pass
    """
    return LearningContext(
        agent=agent,
        client=client,
        capture_only=capture_only,
        memory=memory,
    )
