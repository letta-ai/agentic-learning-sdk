/**
 * Agentic Learning SDK - Core Context Manager
 *
 * Provides context management for automatic learning/memory integration
 * with Letta. Captures conversation turns and saves them to Letta for persistent memory.
 */

import { AsyncLocalStorage } from 'async_hooks';
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
  memoryContext?: string | null; // Pre-fetched memory context
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
 * Learning context manager (callback style)
 *
 * Uses AsyncLocalStorage's run() method for optimal performance.
 * Automatically manages context lifecycle - no manual exit() needed.
 *
 * Matches Python's `with learning(...)` pattern:
 * ```typescript
 * await learning({
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
export async function learning<T>(
  options: {
    agent: string;
    client?: AgenticLearning;
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

  // Create default client if not provided
  const client = options.client || new (require('./client').AgenticLearning)();

  // Pre-fetch memory context if not in captureOnly mode
  let memoryContext: string | null = null;
  if (!options.captureOnly) {
    try {
      if (process.env.DEBUG_AGENTIC_LEARNING) {
        console.log(`[AgenticLearning] Fetching memory context for agent: ${options.agent}`);
      }
      memoryContext = await client.memory.context.retrieve(options.agent);
      if (process.env.DEBUG_AGENTIC_LEARNING) {
        console.log(`[AgenticLearning] Memory context retrieved:`, memoryContext ? `${memoryContext.substring(0, 100)}...` : 'null');
      }
    } catch (error) {
      if (process.env.DEBUG_AGENTIC_LEARNING) {
        console.error(`[AgenticLearning] Error fetching memory:`, error);
      }
      // Ignore errors - memory injection will be skipped
    }
  }

  const config: LearningConfig = {
    agentName: options.agent,
    client: client,
    captureOnly: options.captureOnly || false,
    memory: options.memory || ['human'], // Default to ['human'] like Python SDK
    model: options.model,
    memoryContext, // Store pre-fetched memory context
  };

  // Use AsyncLocalStorage.run() for automatic context management
  return learningContext.run(config, fn);
}

