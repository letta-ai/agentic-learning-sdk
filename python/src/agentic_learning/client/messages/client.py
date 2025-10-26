"""
Messages Client

Provides message management operations with name-based APIs.
"""

from typing import Any, List, Literal, Optional

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
    ) -> List[Any]:
        """
        List all messages for the agent.

        Args:
            agent (str): Name of the agent to list messages for
            before (str | None): Optional message ID cursor for pagination
            after (str | None): Optional message ID cursor for pagination
            limit (int): Maximum number of messages to return (default: 50)
            # TODO: add order / order_by

        Returns:
            Paginated list of message objects # TODO: add return type
        """
        agent_id = self._parent.agents._retrieve_id(agent=agent)
        if not agent_id:
            return []
        return self._letta.agents.messages.list(agent_id=agent_id, before=before, after=after, limit=limit)

    def create(self, agent_id: str, request_messages: List[dict]) -> Any:
        """
        Create new messages for the agent.

        Args:
            agent_id (str): ID of the agent to create messages for
            request_messages (List[dict]): List of message dictionaries with 'role' and 'content'

        Returns:
            Response from Letta
        """
        return self._letta.agents.messages.create(
            agent_id=agent_id,
            messages=request_messages
        )


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
    ) -> List[Any]:
        """
        List all messages for the agent.

        Args:
            agent (str): Name of the agent to list messages for
            before (str | None): Optional message ID cursor for pagination
            after (str | None): Optional message ID cursor for pagination
            limit (int): Maximum number of messages to return (default: 50)
            # TODO: add order and order_by param

        Returns:
            List of message objects # TODO: fix return type
        """
        agent_id = await self._parent.agents._retrieve_id(agent=agent)
        if not agent_id:
            return []
        return await self._letta.agents.messages.list(agent_id=agent_id, before=before, after=after, limit=limit)

    async def create(
        self, 
        agent: str, 
        request_messages: List[dict],
        response_dict: dict,
        model_name: str,
        provider: str,
    ) -> None:
        """
        Create new messages for the agent.

        Args:
            agent_id (str): ID of the agent to create messages for
            request_messages (List[dict]): List of message dictionaries with 'role' and 'content'

        Returns:
            response # TODO: update return type
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
            "model": model_name,
        }

        # Make async POST request to Letta capture endpoint
        import httpx
        
        # Get auth token from client
        token = os.getenv("LETTA_API_KEY", None)
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            response = await http_client.post(message_capture_url, json=payload, headers=headers)
            response.raise_for_status()
