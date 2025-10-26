"""
Agentic Learning SDK

Drop-in SDK for adding persistent memory and learning to any agent.

This package automatically captures conversations and manages persistent memory
through Letta, supporting multiple LLM SDKs including OpenAI, Anthropic, Gemini,
and Claude Agent SDK.

Quickstart (One Line!) - Sync:
    >>> from agentic_learning import learning
    >>>
    >>> with learning(agent="my_agent"):
    >>>     # Your SDK calls here automatically have memory!
    >>>     pass

Quickstart (One Line!) - Async:
    >>> from agentic_learning import learning_async
    >>>
    >>> async with learning_async(agent="my_agent"):
    >>>     # Your SDK calls here automatically have memory!
    >>>     pass

Usage with Custom Letta Client - Sync:
    >>> from agentic_learning import learning
    >>> from letta_client import Letta
    >>>
    >>> letta = Letta(base_url="http://localhost:8283", token=None)
    >>>
    >>> with learning(agent="my_agent", client=letta):
    >>>     # Your SDK calls here
    >>>     pass

Usage with Custom Letta Client - Async:
    >>> from agentic_learning import learning_async
    >>> from letta_client import AsyncLetta
    >>>
    >>> letta = AsyncLetta(base_url="http://localhost:8283", token=None)
    >>>
    >>> async with learning_async(agent="my_agent", client=letta):
    >>>     # Your SDK calls here
    >>>     pass

Usage with AgenticLearning Client - Sync:
    >>> from agentic_learning import AgenticLearning
    >>>
    >>> client = AgenticLearning()
    >>> agent = client.agents.create(name="my_agent")
    >>> agent = client.agents.retrieve(name="my_agent")
    >>> agents = client.agents.list()

Usage with AgenticLearning Client - Async:
    >>> from agentic_learning import AsyncAgenticLearning
    >>>
    >>> client = AsyncAgenticLearning()
    >>> agent = await client.agents.create(name="my_agent")
    >>> agent = await client.agents.retrieve(name="my_agent")
    >>> agents = await client.agents.list()
"""

from .core import (
    learning,
    learning_async,
)
from .client import (
    AgenticLearning,
    AsyncAgenticLearning,
)

__version__ = "0.1.0"

__all__ = [
    # Context managers
    "learning",
    "learning_async",
    # Client classes
    "AgenticLearning",
    "AsyncAgenticLearning",
]
