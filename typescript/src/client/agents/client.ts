/**
 * Agents Client
 *
 * Manages agent creation, retrieval, and deletion.
 */

import type { AgenticLearning } from '../index';
import { SleeptimeClient } from './sleeptime';

export interface Agent {
  id: string;
  name: string;
  created_at?: string;
  memory?: {
    blocks?: {
      label: string;
      value: string;
    }[];
  }
  multi_agent_group?: {
    id: string;
    [key: string]: any;
  };
  tags?: string[];
  [key: string]: any;
}

export interface CreateAgentOptions {
  agent: string;
  memory?: string[];
  model?: string;
}

function memoryPlaceholder(label: string): string {
  const subject = label !== 'human' ? label : 'them';
  return `This is my section of core memory devoted to information about the ${label}. ` +
         `I don't yet know anything about them. ` +
         `I should update this memory over time as I interact with the human ` +
         `and learn more about ${subject}.`;
}

export class AgentsClient {
  public readonly sleeptime: SleeptimeClient;

  constructor(private parent: AgenticLearning) {
    this.sleeptime = new SleeptimeClient(parent, parent.letta);
  }

  /**
   * Create a new agent.
   *
   * @param options - Agent creation options
   * @param options.agent - Name for the agent (default: "letta-agent")
   * @param options.memory - List of memory block labels to create (default: ["human"])
   * @param options.model - Model to use for the agent (default: "anthropic/claude-sonnet-4-20250514")
   * @returns Created agent object
   */
  async create(options: CreateAgentOptions): Promise<Agent> {
    const memory = options.memory || ['human'];
    const model = options.model || 'anthropic/claude-sonnet-4-20250514';

    // Create memory blocks with placeholders
    const memoryBlocks = memory.map(label => ({
      label,
      value: memoryPlaceholder(label),
    }));

    const agent = await this.parent.letta.agents.create({
      name: options.agent,
      agent_type: 'letta_v1_agent',
      memory_blocks: memoryBlocks,
      model,
      embedding: 'openai/text-embedding-3-small',
      tags: ['agentic-learning-sdk'],
      enable_sleeptime: true,
    });

    // Configure sleeptime manager
    if (agent.multi_agent_group?.id) {
      try {
        await this.parent.letta.groups.modify(agent.multi_agent_group.id, {
          manager_config: {
            manager_type: 'sleeptime' as const,
            sleeptime_agent_frequency: 2,
          },
        });
      } catch (error) {
        // Silently fail if group modification fails
      }
    }

    return agent as Agent;
  }

  /**
   * Update an agent by name.
   *
   * @param agent - Name of the agent to update
   * @param model - Model to use for the agent
   * @returns Updated agent object if found, null otherwise
   */
  async update(agent: string, model: string): Promise<Agent | null> {
    const agentId = await this._retrieveId(agent);
    if (!agentId) {
      return null;
    }

    const updatedAgent = await this.parent.letta.agents.modify(agentId, {
      model,
    });

    return updatedAgent as Agent;
  }

  /**
   * Retrieve an agent by name.
   *
   * @param agent - Name of the agent to retrieve
   * @returns Agent object if found, null otherwise
   */
  async retrieve(agent: string): Promise<Agent | null> {
    try {
      const page = await this.parent.letta.agents.list({
        name: agent,
        tags: ['agentic-learning-sdk'],
        include: ['agent.blocks', 'agent.managed_group', 'agent.tags']
      });
      const agents = page.items || [];
      return agents.length > 0 ? (agents[0] as Agent) : null;
    } catch (error) {
      return null;
    }
  }

  /**
   * Delete an agent by name.
   *
   * @param agent - Name of the agent to delete
   * @returns True if deleted, false if not found
   */
  async delete(agent: string): Promise<boolean> {
    const agentId = await this._retrieveId(agent);
    if (agentId) {
      await this.parent.letta.agents.delete(agentId);
      return true;
    }
    return false;
  }

  /**
   * List all agents created by this SDK.
   *
   * @returns List of agent objects
   */
  async list(): Promise<Agent[]> {
    const page = await this.parent.letta.agents.list({
      tags: ['agentic-learning-sdk'],
      include: ['agent.blocks', 'agent.managed_group', 'agent.tags']
    });
    return (page.items || []) as Agent[];
  }

  /**
   * Retrieve an agent ID by name. Skips expensive joins that are
   * unnecessary for ID fetch.
   *
   * @param agent - Name of the agent to retrieve
   * @returns Agent ID if found, null otherwise
   */
  async _retrieveId(agent: string): Promise<string | null> {
    try {
      const page = await this.parent.letta.agents.list({
        name: agent,
        tags: ['agentic-learning-sdk'],
      });
      const agents = page.items || [];
      return agents.length > 0 ? agents[0].id : null;
    } catch (error) {
      return null;
    }
  }
}
