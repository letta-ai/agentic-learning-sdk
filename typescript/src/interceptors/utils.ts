/**
 * Interceptor Utilities
 *
 * Helper functions for interceptor implementations.
 */

import type { Provider } from '../types';
import { getCurrentConfig } from '../core';

/**
 * Save a conversation turn to Letta
 *
 * @param provider Provider of the messages (e.g. "gemini", "claude", "anthropic", "openai")
 * @param model Model name
 * @param requestMessages List of request messages
 * @param responseDict Response from provider
 */
export async function saveConversationTurn(
  provider: Provider,
  model: string,
  requestMessages: Array<{ role: string; content: string }> = [],
  responseDict: { role: string; content: string } = { role: 'assistant', content: '' }
): Promise<void> {
  const config = getCurrentConfig();
  if (!config) {
    return;
  }

  const agent = config.agentName;
  const client = config.client;

  if (!client) {
    return;
  }

  try {
    if (process.env.DEBUG_AGENTIC_LEARNING) {
      console.log('[AgenticLearning] Saving conversation turn for agent:', agent);
    }

    // Get or create agent
    let agentState = await client.agents.retrieve(agent);

    if (!agentState) {
      if (process.env.DEBUG_AGENTIC_LEARNING) {
        console.log('[AgenticLearning] Agent not found, creating new agent');
      }
      agentState = await client.agents.create({
        agent,
        memory: config.memory,
        model: config.model,
      });
    }

    if (process.env.DEBUG_AGENTIC_LEARNING) {
      console.log('[AgenticLearning] Capturing messages to Letta');
    }

    // Use messages.capture method
    await client.messages.capture(agent, {
      provider,
      requestMessages,
      responseDict,
      model,
    });

    if (process.env.DEBUG_AGENTIC_LEARNING) {
      console.log('[AgenticLearning] ✓ Conversation saved successfully');
    }
  } catch (error) {
    // Silently fail - don't crash the application
    if (process.env.DEBUG_AGENTIC_LEARNING || process.env.NODE_ENV === 'development') {
      console.error('[AgenticLearning] Failed to save conversation:', error);
    }
  }
}
