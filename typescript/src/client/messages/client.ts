/**
 * Messages Client
 *
 * Manages conversation messages for agents.
 */

import type { AgenticLearning } from '../index';
import type { Agents } from '@letta-ai/letta-client/resources/agents';
import { MessagesContextClient } from './context';
import type { Provider } from '../../types';

// Use the Letta SDK's message type directly
export type Message = Agents.LettaMessageUnion;

export interface ListMessagesOptions {
  before?: string;
  after?: string;
  limit?: number;
}

export class MessagesClient {
  public readonly context: MessagesContextClient;

  constructor(private parent: AgenticLearning) {
    this.context = new MessagesContextClient(parent);
  }

  /**
   * List all messages for the agent.
   *
   * @param agent - Name of the agent to list messages for
   * @param options - Pagination options
   * @param options.before - Optional message ID cursor for pagination
   * @param options.after - Optional message ID cursor for pagination
   * @param options.limit - Maximum number of messages to return (default: 50)
   * @returns Paginated list of message objects
   */
  async list(agent: string, options: ListMessagesOptions = {}): Promise<Message[]> {
    // First get the agent to get its ID
    const agentState = await this.parent.agents.retrieve(agent);
    if (!agentState) {
      return [];
    }

    const result = await this.parent.letta.agents.messages.list(agentState.id, {
      before: options.before,
      after: options.after,
      limit: options.limit,
    });

    // Extract items from page result if available
    return result?.items || result || [];
  }

  /**
   * Capture conversation messages without invoking the agent's LLM.
   *
   * @param agent - Name of the agent to capture messages for
   * @param options - Capture options
   * @param options.provider - Provider used for the request
   * @param options.requestMessages - List of request messages
   * @param options.responseDict - Response from downstream LLM provider
   * @param options.model - Model name used for the request
   * @returns JSON response with success status
   */
  async capture(
    agent: string,
    options: {
      provider: Provider;
      requestMessages: Array<{ role: string; content: string }>;
      responseDict: { role: string; content: string };
      model: string;
    }
  ): Promise<any> {
    // First get the agent to get its ID
    const agentState = await this.parent.agents.retrieve(agent);
    if (!agentState) {
      return null;
    }

    // Use direct fetch for capture endpoint
    const captureUrl = `${this.parent.baseUrl}/v1/agents/${agentState.id}/messages/capture`;

    // Get auth token from environment
    const token = process.env.LETTA_API_KEY || null;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(captureUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        provider: options.provider,
        request_messages: options.requestMessages,
        response_dict: options.responseDict,
        model: options.model,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to capture conversation: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Send new messages to the agent, invoking the agent's LLM.
   *
   * @param agent - Name of the agent to send messages to
   * @param messages - List of message dictionaries with 'role' and 'content'
   * @returns List of message objects
   */
  async create(agent: string, messages: Array<{ role: 'user' | 'assistant' | 'system'; content: string }>): Promise<Message[]> {
    // First get the agent to get its ID
    const agentState = await this.parent.agents.retrieve(agent);
    if (!agentState) {
      return [];
    }

    const response = await this.parent.letta.agents.messages.send(agentState.id, {
      messages: messages as any,
    });

    // Extract messages from response
    return response?.messages || [];
  }

  /**
   * Get a specific message by ID.
   *
   * @param agent - Name of the agent
   * @param messageId - ID of the message to retrieve
   * @returns Message object if found, null otherwise
   */
  async retrieve(agent: string, messageId: string): Promise<Message | null> {
    try {
      const agentState = await this.parent.agents.retrieve(agent);
      if (!agentState) {
        return null;
      }

      // For now, get all messages and find the one we want
      // since the Letta client doesn't expose a retrieve method
      const messages = await this.list(agent);
      return messages.find(m => m.id === messageId) || null;
    } catch (error) {
      return null;
    }
  }
}
