/**
 * AgenticLearning Client
 *
 * Wrapper around Letta client providing simplified memory and agent management APIs.
 */

import Letta from '@letta-ai/letta-client';
import { AgentsClient } from './agents/client';
import { MemoryClient } from './memory/client';
import { MessagesClient } from './messages/client';

export interface AgenticLearningOptions {
  /** Base URL for Letta API (default: https://api.letta.com) */
  baseUrl?: string;
  /** API key for authentication */
  apiKey?: string;
}

/**
 * Synchronous client for Agentic Learning SDK.
 *
 * Provides simplified APIs for managing Letta agents with name-based lookups.
 */
export class AgenticLearning {
  public readonly letta: Letta;
  public readonly baseUrl: string;

  public readonly agents: AgentsClient;
  public readonly memory: MemoryClient;
  public readonly messages: MessagesClient;

  /**
   * Initialize the Agentic Learning client.
   *
   * @param options - Client configuration options
   * @param options.baseUrl - Letta server base URL. Defaults to LETTA_BASE_URL env var or https://api.letta.com
   * @param options.apiKey - Optional authentication token for Letta server. Defaults to LETTA_API_KEY env var or null
   */
  constructor(options: AgenticLearningOptions = {}) {
    // Check for API key in environment if not provided
    const apiKey = options.apiKey || process.env.LETTA_API_KEY;

    // Default to cloud endpoint or use provided base URL
    this.baseUrl = options.baseUrl || process.env.LETTA_BASE_URL || 'https://api.letta.com';

    // Create underlying Letta client
    this.letta = new Letta({
      baseURL: this.baseUrl,
      apiKey: apiKey || undefined,
      projectID: 'default-project',
    });

    // Initialize sub-clients
    this.agents = new AgentsClient(this);
    this.memory = new MemoryClient(this);
    this.messages = new MessagesClient(this);
  }
}

export type { AgentsClient } from './agents/client';
export type { MemoryClient } from './memory/client';
export type { MessagesClient } from './messages/client';
