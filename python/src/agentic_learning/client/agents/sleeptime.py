"""
Agent Sleeptime Client

Provides sleeptime management operations for agents.
"""

from typing import Any, Optional
from letta_client.types import AgentState, SleeptimeManagerParam


# =============================================================================
# Sync Sleeptime Client
# =============================================================================


class SleeptimeClient:
    """
    Synchronous sleeptime management client.

    Provides APIs for managing agent sleeptime configurations.
    """

    def __init__(self, parent_client: Any, letta_client: Any):
        """
        Initialize the sleeptime client.

        Args:
            parent_client (AgenticLearning): Parent client instance
            letta_client (Letta): Underlying Letta client instance
        """
        self._parent = parent_client
        self._letta = letta_client

    def retrieve(self, agent: str) -> Optional[AgentState]:
        """
        Retrieve the sleeptime configuration for the agent.

        Args:
            agent (str): Name of the primary agent to retrieve corresponding sleeptime agent for

        Returns:
            (AgentState | None): Sleeptime agent if found, None otherwise
        """
        primary_agent = self._parent.agents.retrieve(agent=agent)
        if not primary_agent or not primary_agent.multi_agent_group:
            return None
        sleeptime_agent_id = primary_agent.multi_agent_group.agent_ids[0]
        return self._letta.agents.retrieve(
            agent_id=sleeptime_agent_id,
            include=["agent.blocks", "agent.managed_group", "agent.tags"],
        )
    
    def update(self, agent: str, model: Optional[str], frequency: Optional[int]) -> Optional[AgentState]:
        """
        Update the sleeptime configuration for the agent.

        Args:
            agent (str): Name of the primary agent to update corresponding sleeptime agent for
            model (str | None): Model to use for the sleeptime agent
            frequency (int | None): Frequency at which to invoke the sleeptime memory agent (num turns)

        Returns:
            (AgentState | None): Updated sleeptime agent if found, None otherwise
        """
        primary_agent = self._parent.agents.retrieve(agent=agent)
        if not primary_agent or not primary_agent.multi_agent_group:
            return None
        sleeptime_agent_id = primary_agent.multi_agent_group.agent_ids[0]

        if model:
            sleeptime_agent = self._letta.agents.modify(agent_id=sleeptime_agent_id, model=model)
        if frequency:
            self._letta.groups.modify(group_id=primary_agent.multi_agent_group.id, manager_config=SleeptimeManagerParam(sleeptime_agent_frequency=frequency))
            sleeptime_agent = self._letta.agents.retrieve(
                agent_id=sleeptime_agent_id,
                include=["agent.blocks", "agent.managed_group", "agent.tags"],
            )
        
        return sleeptime_agent


# =============================================================================
# Async Sleeptime Client
# =============================================================================


class AsyncSleeptimeClient:
    """
    Asynchronous sleeptime management client.

    Provides async APIs for managing agent sleeptime configurations.
    """

    def __init__(self, parent_client: Any, letta_client: Any):
        """
        Initialize the async sleeptime client.

        Args:
            parent_client (AsyncAgenticLearning): Parent client instance
            letta_client (AsyncLetta): Underlying Letta client instance
        """
        self._parent = parent_client
        self._letta = letta_client

    async def retrieve(self, agent: str) -> Optional[AgentState]:
        """
        Retrieve the sleeptime configuration for the agent.

        Args:
            agent (str): Name of the primary agent to retrieve corresponding sleeptime agent for

        Returns:
            (AgentState | None): Sleeptime configuration object if found, None otherwise
        """
        primary_agent = await self._parent.agents.retrieve(agent=agent)
        if not primary_agent or not primary_agent.multi_agent_group:
            return None
        sleeptime_agent_id = primary_agent.multi_agent_group.agent_ids[0]
        return await self._letta.agents.retrieve(
            agent_id=sleeptime_agent_id,
            include=["agent.blocks", "agent.managed_group", "agent.tags"],
        )
    
    async def update(self, agent: str, model: Optional[str], frequency: Optional[int]) -> Optional[AgentState]:
        """
        Update the sleeptime configuration for the agent.

        Args:
            agent (str): Name of the primary agent to update corresponding sleeptime agent for
            model (str | None): Model to use for the sleeptime agent
            frequency (int | None): Frequency at which to invoke the sleeptime memory agent (num turns)

        Returns:
            (AgentState | None): Updated sleeptime agent if found, None otherwise
        """
        primary_agent = await self._parent.agents.retrieve(agent=agent)
        if not primary_agent or not primary_agent.multi_agent_group:
            return None
        sleeptime_agent_id = primary_agent.multi_agent_group.agent_ids[0]

        if model:
            sleeptime_agent = await self._letta.agents.modify(agent_id=sleeptime_agent_id, model=model)
        if frequency:
            await self._letta.groups.modify(group_id=primary_agent.multi_agent_group.id, manager_config=SleeptimeManagerParam(sleeptime_agent_frequency=frequency))
            sleeptime_agent = await self._letta.agents.retrieve(
                agent_id=sleeptime_agent_id,
                include=["agent.blocks", "agent.managed_group", "agent.tags"],
            )
        
        return sleeptime_agent

