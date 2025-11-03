"""
Messages Context Client

Provides context management operations for messages.
"""

from typing import Any, List, Literal, Optional

from letta_client.types.agents.message import Message


# =============================================================================
# Sync Messages Context Client
# =============================================================================


class ContextClient:
    """
    Synchronous context management client.

    Provides APIs for managing message context configurations.
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

    def retrieve(
        self,
        agent: str,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: int = 50,
        order: Literal["asc", "desc"] = "desc",
    ) -> List[dict]:
        """
        Retrieve the message context for the agent.

        Args:
            agent (str): Name of the agent to retrieve message context for
            before (str | None): Optional message ID cursor for pagination
            after (str | None): Optional message ID cursor for pagination
            limit (int): Maximum number of messages to return (default: 50)
            order (Literal["asc", "desc"]): Order of messages ("asc" or "desc" - default: "desc")

        Returns:
            (list[dict]): List of message dicts if found, empty list otherwise
        """
        messages = self._parent.messages.list(
            agent=agent,
            before=before,
            after=after,
            limit=limit,
            order=order,
        )
        return _collapse_and_order_messages(
            messages=[_convert_message_to_dict(message) for message in messages],
            order=order,
        )
    

# =============================================================================
# Async Messages Context Client
# =============================================================================


class AsyncContextClient:
    """
    Asynchronous context management client.

    Provides async APIs for managing message context configurations.
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

    async def retrieve(
        self,
        agent: str,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: int = 50,
        order: Literal["asc", "desc"] = "desc",
    ) -> List[dict]:
        """
        Retrieve the message context for the agent.

        Args:
            agent (str): Name of the agent to retrieve message context for
            before (str | None): Optional message ID cursor for pagination
            after (str | None): Optional message ID cursor for pagination
            limit (int): Maximum number of messages to return (default: 50)
            order (Literal["asc", "desc"]): Order of messages ("asc" or "desc" - default: "desc")

        Returns:
            (list[dict]): List of message dicts if found, empty list otherwise
        """
        messages = await self._parent.messages.list(
            agent=agent,
            before=before,
            after=after,
            limit=limit,
            order=order,
        )
        return _collapse_and_order_messages(
            messages=[_convert_message_to_dict(message) for message in messages],
            order=order,
        )


# =============================================================================
# Helper Functions
# =============================================================================


def _convert_message_to_dict(message: Message):
    if isinstance(message.content, str):
        content = message.content
    else:
        content = "\n".join([part.text for part in message.content if hasattr(part, "text")])
    if content.strip() and (message.message_type == "user_message" or message.message_type == "assistant_message"):
        return {
            "role": message.message_type,
            "content": content
        }
    return None


def _collapse_and_order_messages(messages: List[Message], order: Literal["asc", "desc"] = "desc"):
    for i, message in enumerate(messages):
        if message is None:
            del messages[len(messages) - i - 1]
        elif i > 0 and messages[len(messages) - i - 1]["role"] == messages[len(messages) - i]["role"]:
            messages[len(messages) - i - 1]["content"] += "\n" + messages[len(messages) - i]["content"]
            del messages[len(messages) - i]
    if order == "desc":
        return list(reversed(messages))
    return messages
    


