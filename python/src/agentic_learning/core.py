"""
Agentic Learning SDK - Core Context Manager

This module provides a context manager for automatic learning/memory integration
with Letta. It captures conversation turns and saves them to Letta for persistent memory.
"""

import os
from contextvars import ContextVar, Token
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from .client import AgenticLearning, AsyncAgenticLearning
    from .interceptors.base import Provider


_LEARNING_CONFIG: ContextVar[Optional[dict]] = ContextVar('learning_config', default=None)


def get_current_config() -> Optional[dict]:
    """Get the current active learning configuration (context-local)."""
    return _LEARNING_CONFIG.get()


# =============================================================================
# Sync implementation
# =============================================================================


class LearningContext:
    """Sync context manager for Letta learning integration."""

    def __init__(self, client: "AgenticLearning", agent: str, capture_only: bool, memory: List[str], model: str):
        """
        Initialize learning context.

        Args:
            client: AgenticLearning client instance (sync)
            agent: Name of the Letta agent to use for memory storage
            capture_only: Whether to skip auto-injecting memory into prompts
                Set to True to capture conversations without memory injection
            memory: List of Letta memory blocks to configure for the agent
            model: Optional model to use for Letta agent
        """
        self.agent_name = agent
        self.client = client
        self.capture_only = capture_only
        self.memory = memory
        self.model = model
        self._token: Optional[Token] = None

    def __enter__(self):
        """Enter the learning context."""
        self._token = _LEARNING_CONFIG.set({
            "agent_name": self.agent_name,
            "client": self.client,
            "capture_only": self.capture_only,
            "memory": self.memory,
            "model": self.model,
            "pending_user_message": None  # Buffer for batching messages
        })

        # TODO: Install interceptors on first use (auto-detect available SDKs)
        # _ensure_interceptors_installed()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the learning context."""
        if self._token is not None:
            _LEARNING_CONFIG.reset(self._token)

        return False # Don't suppress exceptions


def learning(
    agent: str = "letta_agent",
    client: Optional["AgenticLearning"] = None,
    capture_only: bool = False,
    memory: List[str] = ["human"],
    model: str = "anthropic/claude-sonnet-4-20250514",
) -> LearningContext:
    """
    Create a sync learning context for automatic Letta integration.

    All SDK interactions within this context will automatically:
    1. Capture user messages and assistant responses
    2. Save conversations to Letta for persistent memory
    3. Inject Letta memory into prompts (if capture_only=False)

    Args:
        agent: Name of the Letta agent to use for memory storage. Defaults to 'letta_agent'.
        client: Optional AgenticLearning client instance (sync). If None, will create default client.
        capture_only: Whether to capture conversations without automatic Letta memory injection (default: False)
        memory: Optional list of Letta memory blocks to configure for the agent (default: ["human"])
        model: Optional model to use for Letta agent (default: "anthropic/claude-sonnet-4-20250514")

    Returns:
        LearningContext that can be used as a sync context manager

    Example:
        >>> from agentic_learning import learning
        >>>
        >>> # Simplest usage - one line!
        >>> with learning(agent="my_agent"):
        >>>     # Your SDK calls here
        >>>     pass
        >>>
        >>> # With custom client
        >>> from agentic_learning import AgenticLearning
        >>> client = AgenticLearning()
        >>> with learning(agent="my_agent", client=client):
        >>>     # Your SDK calls here
        >>>     pass
    """
    if client is None:
        from .client import AgenticLearning
        client = AgenticLearning()

    return LearningContext(agent=agent, client=client, capture_only=capture_only, memory=memory, model=model)


# =============================================================================
# Async implementation
# =============================================================================


class AsyncLearningContext:
    """Async context manager for Letta learning integration."""

    def __init__(self, client: "AsyncAgenticLearning", agent: str, capture_only: bool, memory: List[str], model: str):
        """
        Initialize async learning context.

        Args:
            client: AsyncAgenticLearning client instance (async)
            agent: Name of the Letta agent to use for memory storage
            capture_only: Whether to skip auto-injecting memory into prompts
                Set to True to capture conversations without memory injection
            memory: List of Letta memory blocks to configure for the agent
            model: Optional model to use for Letta agent
        """
        self.agent_name = agent
        self.client = client
        self.capture_only = capture_only
        self.memory = memory
        self.model = model
        self._token: Optional[Token] = None

    async def __aenter__(self):
        """Enter the learning context."""
        self._token = _LEARNING_CONFIG.set({
            "agent_name": self.agent_name,
            "client": self.client,
            "capture_only": self.capture_only,
            "memory": self.memory,
            "model": self.model,
            "pending_user_message": None  # Buffer for batching messages
        })

        # TODO: Install interceptors on first use (auto-detect available SDKs)
        # _ensure_interceptors_installed()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the learning context."""
        if self._token is not None:
            _LEARNING_CONFIG.reset(self._token)

        return False # Don't suppress exceptions


def learning_async(
    agent: str = "letta_agent",
    client: Optional["AsyncAgenticLearning"] = None,
    capture_only: bool = False,
    memory: List[str] = ["human"],
    model: str = "anthropic/claude-sonnet-4-20250514",
) -> AsyncLearningContext:
    """
    Create an async learning context for automatic Letta integration.

    All SDK interactions within this context will automatically:
    1. Capture user messages and assistant responses
    2. Save conversations to Letta for persistent memory
    3. Inject Letta memory into prompts (if capture_only=False)

    Args:
        agent: Name of the Letta agent to use for memory storage. Defaults to 'letta_agent'.
        client: Optional AsyncAgenticLearning client instance (async). If None, will create default client.
        capture_only: Whether to capture conversations without automatic Letta memory injection (default: False)
        memory: Optional list of Letta memory blocks to configure for the agent (default: ["human"])
        model: Optional model to use for Letta agent (default: "anthropic/claude-sonnet-4-20250514")

    Returns:
        AsyncLearningContext that can be used as an async context manager

    Example:
        >>> from agentic_learning import learning_async
        >>>
        >>> # Simplest usage - one line!
        >>> async with learning_async(agent="my_agent"):
        >>>     # Your SDK calls here
        >>>     pass
        >>>
        >>> # With custom client
        >>> from agentic_learning import AsyncAgenticLearning
        >>> client = AsyncAgenticLearning()
        >>> async with learning_async(agent="my_agent", client=client):
        >>>     # Your SDK calls here
        >>>     pass
    """
    if client is None:
        from .client import AsyncAgenticLearning
        client = AsyncAgenticLearning()

    return AsyncLearningContext(agent=agent, client=client, capture_only=capture_only, memory=memory, model=model)


def _save_conversation_turn(
    provider: "Provider",
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
                model=config["model"],
            )

        # Get base URL from client or use placeholder
        base_url = client.base_url or 'https://api.letta.com'
        capture_url = f"{base_url}/v1/agents/{agent_state.id}/messages/capture"

        # Build request payload
        payload = {
            "provider": provider,
            "request_messages": request_messages or [],
            "response_dict": response_dict or {},
            "model": model
        }

        # Make POST request to Letta capture endpoint
        import httpx
        
        # Get auth token from client
        token = os.getenv("LETTA_API_KEY", None)
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        with httpx.Client(timeout=30.0) as http_client:
            response = http_client.post(capture_url, json=payload, headers=headers)
            response.raise_for_status()

    except Exception:
        pass


async def _save_conversation_turn_async(
    provider: "Provider",
    model: str,
    request_messages: List[dict] = None,
    response_dict: Dict[str, str] = None,
):
    """
    Save a conversation turn to Letta in a single API call (async version).

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
        agent_state = await client.agents.retrieve(agent=agent)

        if not agent_state:
            agent_state = await client.agents.create(
                agent=agent,
                memory=config["memory"],
                model=config["model"],
            )

        # Get base URL from client or use placeholder
        base_url = client.base_url or 'https://api.letta.com'
        capture_url = f"{base_url}/v1/agents/{agent_state.id}/messages/capture"

        # Build request payload
        payload = {
            "provider": provider,
            "request_messages": request_messages or [],
            "response_dict": response_dict or {},
            "model": model,
        }

        # Make async POST request to Letta capture endpoint
        import httpx
        
        # Get auth token from client
        token = os.getenv("LETTA_API_KEY", None)
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            response = await http_client.post(capture_url, json=payload, headers=headers)
            response.raise_for_status()

    except Exception:
        pass
    
