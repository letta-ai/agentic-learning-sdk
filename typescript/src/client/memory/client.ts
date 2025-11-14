/**
 * Memory Client
 *
 * Manages memory blocks and context retrieval for agents.
 */

import type { AgenticLearning } from '../index';
import { MemoryContextClient } from './context';
import type { Message } from '../messages/client';

export interface MemoryBlock {
  id: string;
  label: string;
  value: string;
  description?: string;
}

export interface CreateMemoryOptions {
  agent: string;
  label: string;
  value: string;
  description?: string;
}

export class MemoryClient {
  public readonly context: MemoryContextClient;

  constructor(private parent: AgenticLearning) {
    this.context = new MemoryContextClient(parent);
  }

  /**
   * Create a new memory block.
   *
   * @param options - Memory block creation options
   * @param options.agent - Name of the agent to create memory block for
   * @param options.label - Label for the memory block
   * @param options.value - Initial value for the memory block (default: placeholder string)
   * @param options.description - Description to guide the agent on how to use this block
   * @returns Created memory block object, or null if agent not found
   */
  async create(options: CreateMemoryOptions): Promise<MemoryBlock | null> {
    // First get the agent to get its ID
    const agentState = await this.parent.agents.retrieve(options.agent);
    if (!agentState) {
      return null;
    }

    // Create the block
    const block = await this.parent.letta.blocks.create({
      label: options.label,
      value: options.value,
      description: options.description,
    });

    // Attach it to the agent
    if (!block.id) {
      throw new Error('Block created without ID');
    }
    await this.parent.letta.agents.blocks.attach(block.id, {
      agent_id: agentState.id
    });

    return block as MemoryBlock;
  }

  /**
   * Upsert a memory block (create or update).
   *
   * @param options - Memory block upsert options
   * @param options.agent - Name of the agent to upsert memory block for
   * @param options.label - Label for the memory block
   * @param options.value - Value for the memory block (default: placeholder string)
   * @param options.description - Description to guide the agent on how to use this block
   * @returns Created or updated memory block object, or null if agent not found
   */
  async upsert(options: CreateMemoryOptions): Promise<MemoryBlock | null> {
    const agentState = await this.parent.agents.retrieve(options.agent);
    if (!agentState) {
      return null;
    }

    const blocks = (agentState as any).blocks || (agentState as any).memory?.blocks || [];
    const existingBlock = blocks.find((b: any) => b.label === options.label);

    if (!existingBlock) {
      return await this.create(options);
    } else {
      const updatedBlock = await this.parent.letta.blocks.update(existingBlock.id, {
        value: options.value,
        description: options.description,
      });
      return updatedBlock as MemoryBlock;
    }
  }

  /**
   * Retrieve a memory block by label.
   *
   * @param agent - Name of the agent to retrieve memory block for
   * @param label - Label of the memory block to retrieve
   * @returns Memory block object if found, null otherwise
   */
  async retrieve(agent: string, label: string): Promise<MemoryBlock | null> {
    const agentState = await this.parent.agents.retrieve(agent);
    if (!agentState) {
      return null;
    }

    const blocks = (agentState as any).blocks || (agentState as any).memory?.blocks || [];
    const block = blocks.find((b: any) => b.label === label);
    return block || null;
  }

  /**
   * List all memory blocks for the agent.
   *
   * @param agent - Name of the agent to list memory blocks for
   * @returns List of memory block objects
   */
  async list(agent: string): Promise<MemoryBlock[]> {
    const agentState = await this.parent.agents.retrieve(agent);

    if (!agentState) {
      return [];
    }

    // Return memory blocks from agent state
    // In letta-client 1.0.0+, blocks are at the top level (agentState.blocks)
    // The old memory.blocks path is deprecated but kept for backwards compatibility
    const blocks = (agentState as any).blocks || (agentState as any).memory?.blocks || [];
    return blocks;
  }

  /**
   * Delete a memory block by label.
   *
   * @param agent - Name of the agent to delete memory block for
   * @param label - Label of the memory block to delete
   * @returns True if deleted, false if not found
   */
  async delete(agent: string, label: string): Promise<boolean> {
    const agentState = await this.parent.agents.retrieve(agent);
    if (!agentState) {
      return false;
    }

    const blocks = (agentState as any).blocks || (agentState as any).memory?.blocks || [];
    const block = blocks.find((b: any) => b.label === label);
    if (!block) {
      return false;
    }

    await this.parent.letta.blocks.delete(block.id);
    return true;
  }

  /**
   * Query conversation using semantic search.
   *
   * @param agent - Name of the agent to search memory for
   * @param prompt - The prompt to ask the agent
   * @returns Message response from agent
   */
  async search(agent: string, prompt: string): Promise<Message[]> {
    const sleeptimeAgent = await this.parent.agents.sleeptime.retrieve(agent);

    if (!sleeptimeAgent) {
      return [];
    }

    try {
      const response = await this.parent.letta.agents.messages.create(sleeptimeAgent.id, {
        messages: [
          {
            role: 'user',
            content: `Search memory for the following: ${prompt}`,
          },
        ],
      });

      // Return messages directly from Letta SDK - no remapping needed
      return response.messages || [];
    } catch (error) {
      return [];
    }
  }

  /**
   * Prompt agent to update memory directly.
   *
   * @param agent - Name of the agent
   * @param prompt - The prompt to trigger memory update
   * @returns Updated memory context string used for injection
   */
  async remember(agent: string, prompt: string): Promise<string | null> {
    const sleeptimeAgent = await this.parent.agents.sleeptime.retrieve(agent);
    if (!sleeptimeAgent) {
      return null;
    }

    await this.parent.letta.agents.messages.create(sleeptimeAgent.id, {
      messages: [
        {
          role: 'user',
          content: prompt,
        },
      ],
    });

    return await this.context.retrieve(agent);
  }
}
