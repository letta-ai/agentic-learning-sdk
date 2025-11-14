"""
Messages Client

Provides message management operations with name-based APIs.
"""

import os
from typing import Any, List, Literal, Optional

from letta_client.types.agents.message import Message

from .context import ContextClient, AsyncContextClient


# =============================================================================
# Sync Messages Client
# =============================================================================


class MessagesClient:
    """
    Synchronous messages management client.

    Provides simplified APIs for managing agent messages by name instead of ID.
    """

    def __init__(self, parent_client: Any, letta_client: Any):
        """
        Initialize the messages client.

        Args:
            parent_client (AgenticLearning): Parent client instance
            letta_client (Letta): Underlying Letta client instance
        """
        self._parent = parent_client
        self._letta = letta_client
        self.context = ContextClient(parent_client, letta_client)

    def list(
        self,
        agent: str,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: int = 50,
        order: Literal["asc", "desc"] = "desc",
        order_by: Literal["created_at"] = "created_at",
    ) -> List[Message]:
        """
        List all messages for the agent.

        Args:
            agent (str): Name of the agent to list messages for
            before (str | None): Optional message ID cursor for pagination
            after (str | None): Optional message ID cursor for pagination
            limit (int): Maximum number of messages to return (default: 50)
            order (Literal["asc", "desc"]): Order of messages (default: "desc")
            order_by (Literal["created_at"]: Order by field (default: "created_at")

        Returns:
            (List[Message]): Paginated list of message objects
        """
        agent_id = self._parent.agents._retrieve_id(agent=agent)
        if not agent_id:
            return []
        result = self._letta.agents.messages.list(
            agent_id=agent_id,
            before=before,
            after=after,
            limit=limit,
            order=order,
            order_by=order_by
        )
        return result.items
    
    def capture(
        self,
        agent: str,
        request_messages: List[dict],
        response_dict: dict,
        model: str,
        provider: str,
    ) -> None:
        """
        Create new messages for the agent.

        Args:
            agent (str): Name of the agent to capture messages for
            request_messages (List[dict]): List of dictionaries with 'role' and 'content' fields
            response_dict (dict): Response from downstream llm provider
            model (str): Name of the model used for the request
            provider (str): Provider used for the request

        Returns:
            (str): JSON response with success status
        """
        agent_id = self._parent.agents._retrieve_id(agent=agent)
        if not agent_id:
            return None

        # Get base URL from client or use placeholder
        base_url = self._parent.base_url or 'https://api.letta.com'
        message_capture_url = f"{base_url}/v1/agents/{agent_id}/messages/capture"

        # Build request payload
        payload = {
            "provider": provider,
            "request_messages": request_messages or [],
            "response_dict": response_dict or {},
            "model": model,
        }

        # Make sync POST request to Letta capture endpoint
        import httpx

        # Get auth token from client
        token = os.getenv("LETTA_API_KEY", None)
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        with httpx.Client(timeout=30.0) as http_client:
            response = http_client.post(message_capture_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    def create(self, agent: str, messages: List[dict]) -> List[Message]:
        """
        Send new messages to the agent, invoking the agent's LLM.

        Args:
            agent (str): Name of the agent to send messages to
            messages (List[dict]): List of dictionaries with 'role' and 'content' fields

        Returns:
            (List[Message]): List of message objects
        """
        agent_id = self._parent.agents._retrieve_id(agent=agent)
        if not agent_id:
            return None
        response = self._letta.agents.messages.create(
            agent_id=agent_id,
            messages=messages
        )
        return response.messages


# =============================================================================
# Async Messages Client
# =============================================================================


class AsyncMessagesClient:
    """
    Asynchronous messages management client.

    Provides simplified async APIs for managing agent messages by name instead of ID.
    """

    def __init__(self, parent_client: Any, letta_client: Any):
        """
        Initialize the async messages client.

        Args:
            parent_client (AsyncAgenticLearning): Parent client instance
            letta_client (AsyncLetta): Underlying Letta client instance
        """
        self._parent = parent_client
        self._letta = letta_client
        self.context = AsyncContextClient(parent_client, letta_client)

    async def list(
        self,
        agent: str,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: int = 50,
        order: Literal["asc", "desc"] = "desc",
        order_by: Literal["created_at"] = "created_at",
    ) -> List[Message]:
        """
        List all messages for the agent.

        Args:
            agent (str): Name of the agent to list messages for
            before (str | None): Optional message ID cursor for pagination
            after (str | None): Optional message ID cursor for pagination
            limit (int): Maximum number of messages to return (default: 50)
            order (Literal["asc", "desc"]): Order of messages (default: "desc")
            order_by (Literal["created_at"]: Order by field (default: "created_at")

        Returns:
            (List[Message]): List of message objects
        """
        agent_id = await self._parent.agents._retrieve_id(agent=agent)
        if not agent_id:
            return []
        result = await self._letta.agents.messages.list(
            agent_id=agent_id,
            before=before,
            after=after,
            limit=limit,
            order=order,
            order_by=order_by
        )
        return result.items

    async def capture(
        self,
        agent: str,
        request_messages: List[dict],
        response_dict: dict,
        model: str,
        provider: str,
    ) -> str:
        """
        Create new messages for the agent.

        Args:
            agent (str): Name of the agent to capture messages for
            request_messages (List[dict]): List of dictionaries with 'role' and 'content' fields
            response_dict (dict): Response from downstream llm provider
            model (str): Name of the model used for the request
            provider (str): Provider used for the request

        Returns:
            (str): JSON response with success status
        """
        agent_id = await self._parent.agents._retrieve_id(agent=agent)
        if not agent_id:
            return None

        # Get base URL from client or use placeholder
        base_url = self._parent.base_url or 'https://api.letta.com'
        message_capture_url = f"{base_url}/v1/agents/{agent_id}/messages/capture"

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
            response = await http_client.post(message_capture_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def create(
        self,
        agent: str,
        messages: List[dict],
    ) -> List[Message]:
        """
        Send new messages to the agent, invoking the agent's LLM.

        Args:
            agent (str): Name of the agent to send messages to
            messages (List[dict]): List of dictionaries with 'role' and 'content' fields

        Returns:
            (List[Message]): List of message objects
        """
        agent_id = await self._parent.agents._retrieve_id(agent=agent)
        if not agent_id:
            return None
        response = await self._letta.agents.messages.create(
            agent_id=agent_id,
            messages=messages
        )
        return response.messages
