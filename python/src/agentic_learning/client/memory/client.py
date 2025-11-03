"""
Memory Client

Provides memory block management operations with name-based APIs.
"""

from typing import Any, List, Optional
from .context import ContextClient, AsyncContextClient
from ..utils import memory_placeholder

from letta_client.types import BlockResponse
from letta_client.types.agents.message import Message


# =============================================================================
# Sync Memory Client
# =============================================================================


class MemoryClient:
    """
    Synchronous memory management client.

    Provides simplified APIs for managing memory blocks by name instead of ID.
    """

    def __init__(self, parent_client: Any, letta_client: Any):
        """
        Initialize the memory client.

        Args:
            parent_client (AgenticLearning): Parent AgenticLearning client instance
            letta_client (Letta): Underlying Letta client instance
        """
        self._parent = parent_client
        self._letta = letta_client
        self.context = ContextClient(parent_client, letta_client)

    def create(
        self,
        agent: str,
        label: str,
        value: str = "",
        description: str = ""
    ) -> Optional[BlockResponse]:
        """
        Create a new memory block.

        Args:
            agent (str): Name of the agent to create memory block for
            label (str): Label for the memory block
            value (str): Initial value for the memory block (default: placeholder string)
            description (str): Description to guide the agent on how to use this block

        Returns:
            (BlockResponse | None): Created memory block object, or None if agent not found
        """
        agent_id = self._parent.agents._retrieve_id(agent=agent)
        if not agent_id:
            return None
        
        block = self._letta.blocks.create(
            label=label,
            value=value or memory_placeholder(label),
            description=description,
        )
        self._letta.agents.blocks.attach(agent_id=agent_id, block_id=block.id)
        
        return block

    def upsert(
        self,
        agent: str,
        label: str,
        value: str = "",
        description: str = ""
    ) -> Optional[BlockResponse]:
        """
        Upsert a new memory block.

        Args:
            agent (str): Name of the agent to create memory block for
            label (str): Label for the memory block
            value (str): Initial value for the memory block (default: placeholder string)
            description (str): Description to guide the agent on how to use this block

        Returns:
            (BlockResponse | None): Created memory block object, or None if agent not found
        """
        agent = self._parent.agents.retrieve(agent=agent)
        if not agent:
            return None
        
        blocks = [b for b in agent.memory.blocks if b.label == label]
        if not blocks:
            block = self.create(
                agent=agent, label=label, value=value, description=description
            )
        else:
            block = block[0]
            block = self._letta.blocks.modify(
                block_id=block.id,  
                value=value or memory_placeholder(label),
                description=description,   
            )
        
        return block

    def retrieve(self, agent: str, label: str) -> Optional[BlockResponse]:
        """
        Retrieve a memory block by label.

        Args:
            agent (str): Name of the agent to retrieve memory block for
            label: Label of the memory block to retrieve

        Returns:
            (BlockResponse | None): Memory block object if found, None otherwise
        """
        agent = self._parent.agents.retrieve(agent=agent)
        if not agent:
            return None

        block = [block for block in agent.blocks if block.label == label]
        if not block:
            return None

        return block[0]

    def list(self, agent: str) -> List[BlockResponse]:
        """
        List all memory blocks for the agent.

        Args:
            agent (str): Name of the agent to list memory blocks for

        Returns:
            (list[BlockResponse]): List of memory block objects
        """
        agent = self._parent.agents.retrieve(agent=agent)
        if not agent:
            return []

        return agent.memory.blocks

    def delete(self, agent: str, label: str) -> bool:
        """
        Delete a memory block by label.

        Args:
            agent (str): Name of the agent to delete memory block for
            label (str): Label of the memory block to delete

        Returns:
            (bool) True if deleted, False if not found
        """
        agent = self._parent.agents.retrieve(agent=agent)
        if not agent:
            return False

        block = [block for block in agent.blocks if block.label == label]
        if not block:
            return False

        self._letta.blocks.delete(block_id=block[0].id)
        return True
    
    def search(self, agent: str, prompt: str) -> List[Message]:
        """
        Query conversation using semantic search.

        Args:
            agent (str): Name of the agent to delete memory block for
            prompt (str): The prompt to ask the agent.

        Returns:
            (List[Message]): Message response from agent
        """
        sleeptime_agent = self._parent.agents.sleeptime.retrieve(agent=agent)
        if not sleeptime_agent:
            return []

        response = self._letta.agents.messages.send(
            agent_id=sleeptime_agent.id,
            messages=[{
                "role": "user",
                "content": f"Search memory for the following: {prompt}"
            }]
        )
        return response.messages
    

    def remember(self, agent: str, prompt: str) -> Optional[str]:
        """
        Prompt agent to update memory directly.

        Args:
            agent (str): Name of the agent to delete memory block for
            prompt (str): The prompt to trigger memory update.

        Returns:
            (str): Updated memory context string used for injection
        """
        sleeptime_agent = self._parent.agents.sleeptime.retrieve(agent=agent)
        if not sleeptime_agent:
            return []

        self._letta.agents.messages.send(
            agent_id=sleeptime_agent.id,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return self._parent.memory.context.retrieve(agent=agent)


# =============================================================================
# Async Memory Client
# =============================================================================


class AsyncMemoryClient:
    """
    Asynchronous memory management client.

    Provides simplified async APIs for managing memory blocks by name instead of ID.
    """

    def __init__(self, parent_client: Any, letta_client: Any):
        """
        Initialize the async memory client.

        Args:
            parent_client (AsyncAgenticLearning): Parent client instance
            letta_client (AsyncLetta): Underlying Letta client instance
        """
        self._parent = parent_client
        self._letta = letta_client
        self.context = AsyncContextClient(parent_client, letta_client)

    async def create(
        self,
        agent: str,
        label: str,
        value: str = "",
        description: str = "",
    ) -> Optional[BlockResponse]:
        """
        Create a new memory block.

        Args:
            agent (str): Name of the agent to create memory block for
            label (str): Label for the memory block
            value (str): Initial value for the memory block
            description (str): Description to guide the agent on how to use this block

        Returns:
            (BlockResponse | None): Created memory block object
        """
        agent_id = await self._parent.agents._retrieve_id(agent=agent)
        if not agent_id:
            return None
        
        block = await self._letta.blocks.create(
           label=label,
           value=value or memory_placeholder(label),
           description=description,
        )
        await self._letta.agents.blocks.attach(agent_id=agent_id, block_id=block.id)
                
        return block
    
    async def upsert(
        self,
        agent: str,
        label: str,
        value: str = "",
        description: str = "",
    ) -> Optional[BlockResponse]:
        """
        Create a new memory block.

        Args:
            agent (str): Name of the agent to create memory block for
            label (str): Label for the memory block
            value (str): Initial value for the memory block
            description (str): Description to guide the agent on how to use this block

        Returns:
            (BlockResponse | None): Created memory block object
        """
        agent = await self._parent.agents.retrieve(agent=agent)
        if not agent:
            return None
        
        blocks = [b for b in agent.memory.blocks if b.label == label]
        if not blocks:
            block = await self.create(
                agent=agent, label=label, value=value, description=description
            )
        else:
            block = block[0]
            block = await self._letta.blocks.modify(
                block_id=block.id,  
                value=value or memory_placeholder(label),
                description=description,   
            )
        
        return block

    async def retrieve(self, agent: str, label: str) -> Optional[BlockResponse]:
        """
        Retrieve a memory block by label.

        Args:
            agent (str): Name of the agent to retrieve memory block for
            label (str): Label of the memory block to retrieve

        Returns:
            (BlockResponse | None): Memory block object if found, None otherwise
        """
        agent = await self._parent.agents.retrieve(agent=agent)
        if not agent:
            return None
        
        block = [block for block in agent.blocks if block.label == label]
        if not block:
            return None

        return block[0]

    async def list(self, agent: str) -> List[BlockResponse]:
        """
        List all memory blocks for the agent.

        Args:
            agent (str): Name of the agent to list memory blocks for

        Returns:
            (list[BlockResponse]): List of memory block objects
        """
        agent = await self._parent.agents.retrieve(agent=agent)
        if not agent:
            return []

        return agent.memory.blocks

    async def delete(self, agent: str, label: str) -> bool:
        """
        Delete a memory block by label.

        Args:
            agent (str): Name of the agent to delete memory block for
            label (str): Label of the memory block to delete

        Returns:
            (bool): True if deleted, False if not found
        """
        agent = await self._parent.agents.retrieve(agent=agent)
        if not agent:
            return False
        
        block = [block for block in agent.blocks if block.label == label]
        if not block:
            return False

        await self._letta.blocks.delete(block[0].id)
        return True
    
    async def search(self, agent: str, prompt: str) -> List[Message]:
        """
        Query conversation using semantic search.

        Args:
            agent (str): Name of the agent to delete memory block for
            prompt (str): The prompt to ask the agent.

        Returns:
            (List[Message]): Message response from agent
        """
        sleeptime_agent = await self._parent.agents.sleeptime.retrieve(agent=agent)
        if not sleeptime_agent:
            return []
        
        response = await self._letta.agents.messages.create(
            agent_id=sleeptime_agent.id,
            messages=[{
                "role": "user",
                "content": f"Search memory for the following: {prompt}"
            }]
        )
        return response.messages
    
    async def remember(self, agent: str, prompt: str) -> Optional[str]:
        """
        Prompt agent to update memory directly.

        Args:
            agent (str): Name of the agent to delete memory block for
            prompt (str): The prompt to trigger memory update.

        Returns:
            (str): Updated memory context string used for injection
        """
        sleeptime_agent = await self._parent.agents.retrieve(agent=agent)
        if not sleeptime_agent:
            return None
        
        await self._letta.agents.messages.create(
            agent_id=sleeptime_agent.id,
            messages=[{
                "role": "user",
                "content": f"Remember the following message: {prompt}"
            }]
        )
        return self._parent.memory.context.retrieve(agent=agent)