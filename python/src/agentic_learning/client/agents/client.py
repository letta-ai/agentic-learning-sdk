"""
Agent Client

Provides agent management operations with name-based APIs.
"""

from typing import Any, List, Optional

from letta_client.types import AgentState, SleeptimeManagerParam
from .sleeptime import SleeptimeClient, AsyncSleeptimeClient
from ..utils import memory_placeholder


# =============================================================================
# Sync Agent Client
# =============================================================================


class AgentsClient:
    """
    Synchronous agent management client.

    Provides simplified APIs for managing agents by name instead of ID.
    """

    def __init__(self, parent_client: Any, letta_client: Any):
        """
        Initialize the agent client.

        Args:
            parent_client (AgenticLearning): Parent client instance
            letta_client (Letta): Underlying Letta client instance
        """
        self._parent = parent_client
        self._letta = letta_client
        self.sleeptime = SleeptimeClient(parent_client, letta_client)

    def create(
        self,
        agent: str = "letta-agent",
        memory: List[str] = ["human"],
        model: str = "anthropic/claude-sonnet-4-20250514",
    ) -> AgentState:
        """
        Create a new agent.

        Args:
            agent (str): Name for the agent (default: "letta-agent")
            memory (list[str]): List of memory block labels to create (default: ["human"])
            model (str): Model to use for the agent (default: "anthropic/claude-sonnet-4-20250514")

        Returns:
            (AgentState): Created agent object
        """
        agent = self._letta.agents.create(
            name=agent,
            agent_type="letta_v1_agent",
            memory_blocks=[{"label": label, "value": memory_placeholder(label)} for label in memory],
            model=model,
            embedding="openai/text-embedding-3-small",
            tags=["agentic-learning-sdk"],
            enable_sleeptime=True,
        )
        self._letta.groups.modify(
            group_id=agent.multi_agent_group.id,
            manager_config=SleeptimeManagerParam(
                sleeptime_agent_frequency=2,
            ),
        )
        return agent
    
    def update(self, agent: str, model: Optional[str]) -> AgentState:
        """
        Update an agent by name.

        Args:
            agent (str): Name of the agent to update
            model (str | None): Model to use for the agent

        Returns:
            (AgentState | None): Agent object if found, None otherwise
        """
        agent_id = self._retrieve_id(agent=agent)
        if not agent_id:
            return None

        return self._letta.agents.update(
            agent_id=agent_id,
            model=model,
        )

    def retrieve(self, agent: str) -> Optional[AgentState]:
        """
        Retrieve an agent by name.

        Args:
            agent (str): Name of the agent to retrieve

        Returns:
            (AgentState | None): Agent object if found, None otherwise
        """
        agents = self._letta.agents.list(
            name=agent,
            tags=["agentic-learning-sdk"],
            include=["agent.blocks", "agent.managed_group", "agent.tags"],
        )
        return agents.items[0] if agents.items else None

    def list(self) -> List[AgentState]:
        """
        List all agents created by this SDK.

        Returns:
            (list[AgentState]): List of agent objects
        """
        result = self._letta.agents.list(
            tags=["agentic-learning-sdk"],
            include=["agent.blocks", "agent.managed_group", "agent.tags"],
        )
        return result.items

    def delete(self, agent: str) -> bool:
        """
        Delete an agent by name.

        Args:
            agent (str): Name of the agent to delete

        Returns:
            (bool): True if deleted, False if not found
        """
        agent_id = self._retrieve_id(agent=agent)
        if agent_id:
            self._letta.agents.delete(agent_id=agent_id)
            return True
        return False
    
    def _retrieve_id(self, agent: str) -> Optional[str]:
        """
        Retrieve an agent ID by name. Skips expensive joins that are
        unnecessary for ID fetch.

        Args:
            agent (str): Name of the agent to retrieve

        Returns:
            (str | None): Agent ID if found, None otherwise
        """
        agents = self._letta.agents.list(
            name=agent,
            tags=["agentic-learning-sdk"],
        )
        return agents.items[0].id if agents.items else None


# =============================================================================
# Async Agent Client
# =============================================================================


class AsyncAgentsClient:
    """
    Asynchronous agent management client.

    Provides simplified async APIs for managing agents by name instead of ID.
    """

    def __init__(self, parent_client: Any, letta_client: Any):
        """
        Initialize the async agent client.

        Args:
            parent_client (AsyncAgenticLearning): Parent client instance
            letta_client (AsyncLetta): Underlying Letta client instance
        """
        self._parent = parent_client
        self._letta = letta_client
        self.sleeptime = AsyncSleeptimeClient(parent_client, letta_client)

    async def create(
        self,
        agent: str = "letta-agent",
        memory: List[str] = ["human"],
        model: str = "anthropic/claude-sonnet-4-20250514",
    ) -> Any:
        """
        Create a new agent.

        Args:
            agent (str): Name for the agent (default: "letta-agent")
            memory (list[str]): List of memory block labels to create (default: ["human"])
            model (str): Model to use for the agent (default: "anthropic/claude-sonnet-4-20250514")

        Returns:
            (AgentState): Created agent object
        """
        agent = await self._letta.agents.create(
            name=agent,
            memory_blocks=[{"label": label, "value": memory_placeholder(label)} for label in memory],
            model=model,
            embedding="openai/text-embedding-3-small",
            tags=["agentic-learning-sdk"],
            enable_sleeptime=True,
        )
        await self._letta.groups.modify(
            group_id=agent.multi_agent_group.id,
            manager_config=SleeptimeManagerParam(
                sleeptime_agent_frequency=2,
            ),
        )
        return agent
    
    async def update(self, agent: str, model: Optional[str]) -> AgentState:
        """
        Update an agent by name.

        Args:
            agent (str): Name of the agent to update
            model (str | None): Model to use for the agent

        Returns:
            (AgentState | None): Agent object if found, None otherwise
        """
        agent_id = await self._retrieve_id(agent=agent)
        if not agent_id:
            return None

        return await self._letta.agents.update(
            agent_id=agent_id,
            model=model,
        )

    async def retrieve(self, agent: str) -> Optional[AgentState]:
        """
        Retrieve an agent by name.

        Args:
            agent (str): Name of the agent to retrieve

        Returns:
            (AgentState | None): Agent object if found, None otherwise
        """
        agents = await self._letta.agents.list(
            name=agent,
            tags=["agentic-learning-sdk"],
            include=["agent.blocks", "agent.managed_group", "agent.tags"],
        )
        return agents.items[0] if agents.items else None

    async def list(self) -> List[AgentState]:
        """
        List all agents created by this SDK.

        Returns:
            (list[AgentState]): List of agent objects
        """
        result = await self._letta.agents.list(
            tags=["agentic-learning-sdk"],
            include=["agent.blocks", "agent.managed_group", "agent.tags"],
        )
        return result.items

    async def delete(self, agent: str) -> bool:
        """
        Delete an agent by name.

        Args:
            agent (str): Name of the agent to delete

        Returns:
            (bool): True if deleted, False if not found
        """
        agent_id = await self._retrieve_id(agent=agent)
        if agent_id:
            await self._letta.agents.delete(agent_id=agent_id)
            return True
        return False
    
    async def _retrieve_id(self, agent: str) -> Optional[str]:
        """
        Retrieve an agent ID by name. Skips expensive joins that are
        unnecessary for ID fetch.

        Args:
            agent (str): Name of the agent to retrieve

        Returns:
            (str | None): Agent ID if found, None otherwise
        """
        agents = await self._letta.agents.list(
            name=agent,
            tags=["agentic-learning-sdk"],
        )
        return agents.items[0].id if agents.items else None
