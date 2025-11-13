/**
 * Claude Agent SDK Interceptor
 *
 * Intercepts Claude Agent SDK calls by patching ProcessTransport prototype.
 * Works with @anthropic-ai/claude-agent-sdk for TypeScript.
 */

import { BaseAPIInterceptor } from './base';
import type { Provider } from '../types';
import { getCurrentConfig } from '../core';
import { saveConversationTurn } from './utils';

interface SDKMessage {
  type: string;
  message?: any;
  [key: string]: any;
}

export class ClaudeInterceptor extends BaseAPIInterceptor {
  readonly PROVIDER: Provider = 'claude';
  private patchedTransport = false;

  /**
   * Check if @anthropic-ai/claude-agent-sdk is available
   */
  isAvailable(): boolean {
    try {
      // Strategy 1: Check if already loaded in cache
      const Module = require('module');
      const cache = (Module as any)._cache || require.cache;

      const hasClaude = Object.keys(cache).some(k =>
        k.includes('@anthropic-ai/claude-agent-sdk') &&
        (k.includes('sdk.') || k.includes('index.'))
      );

      if (hasClaude) {
        return true;
      }

      // Strategy 2: Try to require it directly (works if in accessible node_modules)
      try {
        require('@anthropic-ai/claude-agent-sdk');
        return true;
      } catch {
        // Not in accessible path
      }

      // Strategy 3: Always return true and use lazy installation
      // This allows interceptor to install hooks even if SDK not loaded yet
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Install interceptor by patching ProcessTransport prototype
   */
  install(): void {
    if (this.patchedTransport) {
      return; // Already installed
    }

    try {
      // Strategy 1: Try to patch if SDK already in cache
      const Module = require('module');
      const cache = (Module as any)._cache || require.cache;

      // Find the SDK module in cache
      const sdkKey = Object.keys(cache).find(k =>
        k.includes('@anthropic-ai/claude-agent-sdk') &&
        (k.includes('sdk.') || k.includes('index.'))
      );

      if (sdkKey) {
        const claudeSDK = cache[sdkKey]?.exports;
        if (claudeSDK && claudeSDK.query) {
          // SDK found in cache, patch it now
          this.patchClaudeSDK(claudeSDK, cache, sdkKey);
          return;
        }
      }

      // Strategy 2: SDK not loaded yet - install require hook to patch when it loads
      this.installRequireHook();

    } catch (error) {
      if (process.env.DEBUG_AGENTIC_LEARNING) {
        console.error('[Claude] Failed to patch:', error);
      }
    }
  }

  /**
   * Install a require hook to patch SDK when it's loaded
   */
  private installRequireHook(): void {
    const Module = require('module');
    const originalRequire = Module.prototype.require;
    const self = this;

    Module.prototype.require = function(this: any, id: string) {
      const module = originalRequire.apply(this, arguments);

      // Check if this is the Claude SDK
      if (id.includes('@anthropic-ai/claude-agent-sdk') && !self.patchedTransport) {
        if (process.env.DEBUG_AGENTIC_LEARNING) {
          console.log('[Claude] SDK loaded via require hook, patching now...');
        }

        // Get cache and patch
        const cache = (Module as any)._cache || require.cache;
        const sdkKey = Object.keys(cache).find(k =>
          k.includes('@anthropic-ai/claude-agent-sdk') &&
          (k.includes('sdk.') || k.includes('index.'))
        );

        if (sdkKey && cache[sdkKey]?.exports) {
          self.patchClaudeSDK(cache[sdkKey].exports, cache, sdkKey);
        }
      }

      return module;
    };

    if (process.env.DEBUG_AGENTIC_LEARNING) {
      console.log('[Claude] Installed require hook for lazy loading');
    }
  }

  /**
   * Patch the Claude SDK (shared logic for both strategies)
   */
  private patchClaudeSDK(claudeSDK: any, cache: any, sdkKey: string): void {
    const self = this;

    // Wrap query() with a Proxy to inject memory before it's called
    const originalExports = cache[sdkKey].exports;
    const proxiedExports = new Proxy(originalExports, {
      get(target, prop) {
        const value = target[prop];

        if (prop === 'query' && typeof value === 'function') {
          return function(params: any) {
            const config = getCurrentConfig();

            // Inject pre-fetched memory into systemPrompt option
            if (config && !config.captureOnly && config.memoryContext) {
              if (!params.options) {
                params.options = {};
              }
              params.options.systemPrompt = config.memoryContext;

              if (process.env.DEBUG_AGENTIC_LEARNING) {
                console.log('[Claude] Injecting memory into systemPrompt');
              }
            }

            return value.call(target, params);
          };
        }

        return value;
      }
    });

    cache[sdkKey].exports = proxiedExports;

    // Get ProcessTransport class for message capture patching
    let ProcessTransportClass: any = null;
    try {
      const dummyQuery = claudeSDK.query({ prompt: 'test', options: {} });
      if (dummyQuery?.transport) {
        ProcessTransportClass = dummyQuery.transport.constructor;

        // Clean up dummy query
        if (dummyQuery.transport.close) {
          try {
            const closeResult = dummyQuery.transport.close();
            if (closeResult?.catch) closeResult.catch(() => {});
          } catch {}
        }
      }
    } catch {
      return;
    }

    if (!ProcessTransportClass?.prototype) {
      return;
    }

    const proto = ProcessTransportClass.prototype;

    // Store original methods
    if (!this.originalMethods.has('write')) {
      this.originalMethods.set('write', proto.write);
    }
    if (!this.originalMethods.has('readMessages')) {
      this.originalMethods.set('readMessages', proto.readMessages);
    }

    // Patch write to capture user messages
    const originalWrite = this.originalMethods.get('write');
    proto.write = async function(this: any, data: string) {
      const config = getCurrentConfig();
      if (config) {
        self.captureUserMessage(data, config);
      }
      return originalWrite.call(this, data);
    };

    // Patch readMessages to capture assistant responses
    const originalReadMessages = this.originalMethods.get('readMessages');
    proto.readMessages = function(this: any) {
      const config = getCurrentConfig();
      const messageIterator = originalReadMessages.call(this);
      return config ? self.wrapMessageIterator(messageIterator, config) : messageIterator;
    };

    this.patchedTransport = true;
    (global as any).__CLAUDE_INTERCEPTOR_REGISTERED__ = this;

    if (process.env.DEBUG_AGENTIC_LEARNING) {
      console.log('[Claude] Successfully patched Claude Agent SDK');
    }
  }

  /**
   * Capture user message from transport write
   */
  private captureUserMessage(data: string, config: any): void {
    try {
      const message: SDKMessage = JSON.parse(data);

      if (message.type === 'user' && message.message) {
        const content = this.extractContentFromMessage(message.message);
        if (content) {
          // Store user message in config for later pairing with assistant response
          config.pendingUserMessage = content;
        }
      }
    } catch (error) {
      // Silently ignore parsing errors
    }
  }

  /**
   * Extract text content from message
   */
  private extractContentFromMessage(message: any): string {
    if (typeof message.content === 'string') {
      return message.content;
    }

    if (Array.isArray(message.content)) {
      const textParts: string[] = [];
      for (const block of message.content) {
        if (block.type === 'text' && block.text) {
          textParts.push(block.text);
        }
      }
      return textParts.join('');
    }

    return '';
  }

  /**
   * Wrap message iterator to capture assistant responses
   */
  private async *wrapMessageIterator(
    originalIterator: AsyncIterableIterator<SDKMessage>,
    config: any
  ): AsyncIterableIterator<SDKMessage> {
    const accumulatedText: string[] = [];

    try {
      for await (const message of originalIterator) {
        // Accumulate assistant text
        if (message.type === 'assistant' && message.message) {
          const content = this.extractContentFromMessage(message.message);
          if (content) {
            accumulatedText.push(content);
          }
        }

        // Always yield the message for streaming
        yield message;
      }
    } finally {
      // After iteration completes, save the conversation
      const userMessage = config.pendingUserMessage;
      const assistantMessage = accumulatedText.join('');

      if (userMessage || assistantMessage) {
        // Save conversation turn
        saveConversationTurn(
          this.PROVIDER,
          'claude',
          userMessage ? this.buildRequestMessages(userMessage) : [],
          {
            role: 'assistant',
            content: assistantMessage,
          }
        ).catch(() => {
          // Silently fail
        });

        // Clear pending message
        config.pendingUserMessage = null;
      }
    }
  }

  /**
   * Uninstall interceptor and restore original methods
   */
  uninstall(): void {
    try {
      // Get the SDK from cache
      const Module = require('module');
      const cache = (Module as any)._cache || require.cache;

      const sdkKey = Object.keys(cache).find(k =>
        k.includes('@anthropic-ai/claude-agent-sdk') &&
        (k.includes('sdk.') || k.includes('index.'))
      );

      if (!sdkKey) {
        return;
      }

      const claudeSDK = cache[sdkKey]?.exports;

      if (claudeSDK && claudeSDK.query) {
        const dummyQuery = claudeSDK.query({
          prompt: 'test',
          options: {}
        });

        if (dummyQuery && dummyQuery.transport) {
          const proto = dummyQuery.transport.constructor.prototype;

          // Restore original methods
          if (this.originalMethods.has('write')) {
            proto.write = this.originalMethods.get('write');
          }
          if (this.originalMethods.has('readMessages')) {
            proto.readMessages = this.originalMethods.get('readMessages');
          }
          if (this.originalMethods.has('initialize')) {
            proto.initialize = this.originalMethods.get('initialize');
          }

          // Clean up
          if (dummyQuery.transport.close) {
            try {
              const closeResult = dummyQuery.transport.close();
              if (closeResult && typeof closeResult.catch === 'function') {
                closeResult.catch(() => {});
              }
            } catch (error) {
              // Ignore
            }
          }
        }
      }

      this.patchedTransport = false;
      this.originalMethods.clear();
    } catch {
      // SDK not available
    }
  }

  /**
   * Required abstract methods from BaseAPIInterceptor
   */

  extractUserMessages(): string {
    return '';
  }

  extractAssistantMessage(): string {
    return '';
  }

  buildRequestMessages(userMessage: string): Array<{ role: string; content: string }> {
    return [{ role: 'user', content: userMessage }];
  }

  buildResponseDict(response: any): { role: string; content: string } {
    return {
      role: 'assistant',
      content: response?.content || '',
    };
  }

  extractModelName(): string {
    return 'claude';
  }

  injectMemoryContext(options: Record<string, any>, context: string): Record<string, any> {
    if (!context) {
      return options;
    }

    // Inject into system prompt
    if (options.systemPrompt) {
      if (typeof options.systemPrompt === 'string') {
        options.systemPrompt = `${context}\n\n${options.systemPrompt}`;
      }
    } else {
      options.systemPrompt = context;
    }

    return options;
  }

  protected buildResponseFromChunks(): any {
    return { content: '' };
  }
}
