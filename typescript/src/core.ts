/**
 * Agentic Learning SDK - Core Context Manager
 *
 * Provides context management for automatic learning/memory integration
 * with Letta. Captures conversation turns and saves them to Letta for persistent memory.
 */

import { AsyncLocalStorage } from 'async_hooks';
import type { Provider } from './interceptors/base';
import type { AgenticLearning } from './client';

/**
 * Learning configuration stored in async context
 */
interface LearningConfig {
  agentName: string;
  client: AgenticLearning;
  captureOnly: boolean;
  memory: string[];
  model?: string;
}

// Async-safe context storage using Node.js AsyncLocalStorage
// This ensures proper context isolation across concurrent async operations
const learningContext = new AsyncLocalStorage<LearningConfig>();

// Track if interceptors have been auto-installed
let interceptorsInstalled = false;

/**
 * Get the current active learning configuration
 *
 * This is async-safe and will return the correct context even in
 * complex concurrent scenarios with multiple overlapping learning() calls.
 */
export function getCurrentConfig(): LearningConfig | null {
  return learningContext.getStore() || null;
}

/**
 * Learning context manager
 *
 * Creates an async-safe learning context that automatically captures
 * LLM conversations and manages memory with Letta.
 *
 * Usage:
 * ```typescript
 * const context = learning({
 *   agent: 'my-agent',
 *   client: learningClient
 * });
 *
 * try {
 *   // Your LLM calls here - automatically captured!
 *   await client.chat.completions.create(...);
 * } finally {
 *   context.exit();
 * }
 * ```
 *
 * @param options Configuration for the learning context
 * @returns Context object with exit() method
 */
export function learning(options: {
  agent: string;
  client: AgenticLearning;
  captureOnly?: boolean;
  memory?: string[];
  model?: string;
}): {
  exit: () => void;
} {
  // Auto-install interceptors on first use
  if (!interceptorsInstalled) {
    const { install } = require('./interceptors');
    install();
    interceptorsInstalled = true;
  }

  // Save the previous context (for nested contexts)
  const previousStore = learningContext.getStore();

  const config: LearningConfig = {
    agentName: options.agent,
    client: options.client,
    captureOnly: options.captureOnly || false,
    memory: options.memory || [],
    model: options.model,
  };

  // Enter the new context using AsyncLocalStorage
  learningContext.enterWith(config);

  return {
    exit: () => {
      // Restore previous context (or clear if none)
      if (previousStore) {
        learningContext.enterWith(previousStore);
      } else {
        learningContext.disable();
      }
    },
  };
}

/**
 * Async learning context manager with callback
 *
 * Uses AsyncLocalStorage's run() method for optimal performance.
 * Automatically manages context lifecycle - no manual exit() needed.
 *
 * Matches Python's `with learning(...)` pattern:
 * ```typescript
 * await withLearning({
 *   agent: 'my-agent',
 *   client: learningClient
 * }, async () => {
 *   // Your async LLM calls here - automatically captured!
 *   const response = await client.chat.completions.create(...);
 *   return response;
 * });
 * ```
 *
 * @param options Configuration for the learning context
 * @param fn Async function to execute within the learning context
 * @returns Promise resolving to the function's return value
 */
export async function withLearning<T>(
  options: {
    agent: string;
    client: AgenticLearning;
    captureOnly?: boolean;
    memory?: string[];
    model?: string;
  },
  fn: () => Promise<T>
): Promise<T> {
  // Auto-install interceptors on first use
  if (!interceptorsInstalled) {
    const { install } = require('./interceptors');
    install();
    interceptorsInstalled = true;
  }

  const config: LearningConfig = {
    agentName: options.agent,
    client: options.client,
    captureOnly: options.captureOnly || false,
    memory: options.memory || [],
    model: options.model,
  };

  // Use AsyncLocalStorage.run() for automatic context management
  return learningContext.run(config, fn);
}

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
    // Get or create agent
    let agentState = await client.agents.retrieve(agent);

    if (!agentState) {
      agentState = await client.agents.create({
        agent,
        memory: config.memory,
        model: config.model,
      });
    }

    // Use direct fetch for capture endpoint (not yet in Letta client)
    const captureUrl = `${client.baseUrl}/v1/agents/${agentState.id}/messages/capture`;

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
        provider,
        request_messages: requestMessages,
        response_dict: responseDict,
        model,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to capture conversation: ${response.statusText}`);
    }
  } catch (error) {
    // Silently fail - don't crash the application
    if (process.env.NODE_ENV === 'development') {
      console.warn('[AgenticLearning] Failed to save conversation:', error);
    }
  }
}
