"""
Agentic Learning SDK

Drop-in SDK for adding persistent memory and learning to any agent.

This package automatically captures conversations and manages persistent memory
through Letta, supporting multiple LLM SDKs including OpenAI, Anthropic, Gemini,
and Claude Agent SDK.

Quickstart (One Line!):
    >>> from agentic_learning import learning
    >>>
    >>> with learning(agent="my_agent"):
    >>>     # Your SDK calls here automatically have memory!
    >>>     pass

Usage with Custom Letta Client:
    >>> from agentic_learning import learning, AgenticLearning
    >>>
    >>> client = AgenticLearning(base_url="http://localhost:8283")
    >>>
    >>> with learning(agent="my_agent", client=client):
    >>>     # Your SDK calls here
    >>>     pass

Usage with AgenticLearning Client:
    >>> from agentic_learning import AgenticLearning
    >>>
    >>> client = AgenticLearning()
    >>> agent = client.agents.create(name="my_agent")
    >>> agent = client.agents.retrieve(name="my_agent")
    >>> agents = client.agents.list()
"""

from .core import learning
from .client import (
    AgenticLearning,
    AsyncAgenticLearning,
)

__version__ = "0.1.0"

__all__ = [
    # Context manager (works for both sync and async)
    "learning",
    # Client classes
    "AgenticLearning",
    "AsyncAgenticLearning",
]
