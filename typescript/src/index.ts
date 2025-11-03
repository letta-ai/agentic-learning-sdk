/**
 * Agentic Learning SDK for TypeScript
 *
 * Automatic memory integration with Letta for LLM applications.
 */

// Export main client
export { AgenticLearning } from './client';
export type { AgenticLearningOptions } from './client';

// Export context managers
export { learning, withLearning, getCurrentConfig, saveConversationTurn } from './core';

// Export interceptors (this also triggers registration via side effects)
export { install, registerInterceptor, uninstallAll } from './interceptors';
export { BaseAPIInterceptor } from './interceptors';
export type { Provider, IBaseInterceptor } from './interceptors';

// Export client types
export type { Agent, CreateAgentOptions } from './client/agents/client';
export type { MemoryBlock, CreateMemoryOptions } from './client/memory/client';
export type { Message, ListMessagesOptions } from './client/messages/client';

/**
 * Enable interception for an Anthropic client instance
 *
 * Due to module resolution issues with ts-node, call this after creating your Anthropic client:
 * ```
 * import Anthropic from '@anthropic-ai/sdk';
 * import { enableAnthropicInterception } from '@letta/agentic-learning';
 *
 * const client = new Anthropic({ apiKey });
 * enableAnthropicInterception(client);
 * ```
 */
export function enableAnthropicInterception(client: any): void {
  if ((global as any).__ANTHROPIC_INTERCEPTOR__) {
    (global as any).__ANTHROPIC_INTERCEPTOR__.lazyInstall(client);
  } else {
    console.warn('[AgenticLearning] Anthropic interceptor not found. Make sure to call install() first.');
  }
}
