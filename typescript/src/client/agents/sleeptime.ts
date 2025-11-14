/**
 * Agent Sleeptime Client
 *
 * Provides sleeptime management operations for agents.
 */

import type { AgenticLearning } from '../index';
import type { Agent } from './client';

export class SleeptimeClient {
  constructor(
    private parent: AgenticLearning,
    private letta: any
  ) {}

  /**
   * Retrieve the sleeptime configuration for the agent.
   *
   * @param agent - Name of the primary agent to retrieve corresponding sleeptime agent for
   * @returns Sleeptime agent if found, null otherwise
   */
  async retrieve(agent: string): Promise<Agent | null> {
    const primaryAgent = await this.parent.agents.retrieve(agent);

    // Note: TypeScript Letta client uses camelCase (multiAgentGroup), not snake_case
    const multiAgentGroup = (primaryAgent as any)?.multiAgentGroup;
    if (!primaryAgent || !multiAgentGroup) {
      return null;
    }

    const sleeptimeAgentId = multiAgentGroup.agentIds?.[0];

    if (!sleeptimeAgentId) {
      return null;
    }

    try {
      const sleeptimeAgent = await this.letta.agents.retrieve(sleeptimeAgentId, {
        includeRelationships: ['memory', 'multi_agent_group', 'tags'],
      });
      return sleeptimeAgent as Agent;
    } catch (error) {
      return null;
    }
  }

  /**
   * Update the sleeptime configuration for the agent.
   *
   * @param agent - Name of the primary agent to update corresponding sleeptime agent for
   * @param model - Model to use for the sleeptime agent
   * @param frequency - Frequency at which to invoke the sleeptime memory agent (num turns)
   * @returns Updated sleeptime agent if found, null otherwise
   */
  async update(agent: string, model?: string, frequency?: number): Promise<Agent | null> {
    const primaryAgent = await this.parent.agents.retrieve(agent);
    const multiAgentGroup = (primaryAgent as any)?.multiAgentGroup;

    if (!primaryAgent || !multiAgentGroup) {
      return null;
    }

    const sleeptimeAgentId = multiAgentGroup.agentIds?.[0];
    if (!sleeptimeAgentId) {
      return null;
    }

    let sleeptimeAgent: any = null;

    // Update model if provided
    if (model) {
      sleeptimeAgent = await this.letta.agents.update(sleeptimeAgentId, {
        model,
      });
    }

    // Update frequency if provided
    if (frequency) {
      await this.letta.groups.update(multiAgentGroup.id, {
        managerConfig: {
          managerType: 'sleeptime' as const,
          sleeptimeAgentFrequency: frequency,
        },
      });

      // Re-fetch agent to get updated configuration
      sleeptimeAgent = await this.letta.agents.retrieve(sleeptimeAgentId, {
        includeRelationships: ['memory', 'multi_agent_group', 'tags'],
      });
    }

    return sleeptimeAgent as Agent;
  }
}
