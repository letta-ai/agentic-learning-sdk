/**
 * OpenAI Interceptor
 *
 * Intercepts OpenAI SDK calls to capture conversations and inject memory.
 * Supports both Chat Completions and Responses APIs.
 */

import { BaseAPIInterceptor } from './base';
import type { Provider } from '../types';
import { getCurrentConfig } from '../core';
import { saveConversationTurn } from './utils';

export class OpenAIInterceptor extends BaseAPIInterceptor {
  readonly PROVIDER: Provider = 'openai';

  /**
   * Check if OpenAI SDK is available
   */
  isAvailable(): boolean {
    try {
      require('openai');
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Install interceptor by patching OpenAI SDK methods
   */
  install(): void {
    try {
      const OpenAIModule = require('openai');

      if (process.env.DEBUG_AGENTIC_LEARNING) {
        console.log('[OpenAI] Installing interceptor...');
      }

      // In production CommonJS, OpenAIModule itself is the constructor function
      // and .Chat doesn't exist - only .default.Chat exists
      // In TypeScript/ES6, both might exist due to transpilation
      // We need to find which one is actually used
      const targets = [];

      // The default export is what's actually used in both cases
      if (OpenAIModule.default?.Chat?.Completions) {
        targets.push({ name: 'default', completions: OpenAIModule.default.Chat.Completions });
      }

      // Also check if there's a direct .Chat (might exist in some module systems)
      if (OpenAIModule.Chat?.Completions && OpenAIModule.Chat.Completions !== OpenAIModule.default?.Chat?.Completions) {
        targets.push({ name: 'direct', completions: OpenAIModule.Chat.Completions });
      }

      if (targets.length === 0) {
        if (process.env.DEBUG_AGENTIC_LEARNING) {
          console.log('[OpenAI] Could not find ChatCompletions class to patch');
        }
        return;
      }

      for (const target of targets) {
        const ChatCompletions = target.completions;

        if (ChatCompletions && ChatCompletions.prototype?.create) {
          // Save original if not already saved
          if (!this.originalMethods.has('completions.create')) {
            this.originalMethods.set('completions.create', ChatCompletions.prototype.create);
          }

          // Patch the create method
          const self = this;
          ChatCompletions.prototype.create = async function (
            this: any,
            params: any,
            options?: any
          ) {
            return self.interceptCreate(this, params, options);
          };

          if (process.env.DEBUG_AGENTIC_LEARNING) {
            console.log(`[OpenAI] Patched ChatCompletions.prototype.create`);
          }
        }
      }

      // Also patch Responses API if available (patch both exports like Chat.Completions)
      try {
        const responsesTargets = [];
        if (OpenAIModule.Responses) {
          responsesTargets.push(OpenAIModule.Responses);
        }
        if (OpenAIModule.default?.Responses) {
          responsesTargets.push(OpenAIModule.default.Responses);
        }

        for (const Responses of responsesTargets) {
          if (Responses && Responses.prototype?.create) {
            if (!this.originalMethods.has('responses.create')) {
              this.originalMethods.set('responses.create', Responses.prototype.create);
            }

            const self = this;
            Responses.prototype.create = async function (
              this: any,
              params: any,
              options?: any
            ) {
              return self.interceptResponsesCreate(this, params, options);
            };
          }
        }
      } catch {
        // Responses API not available, skip
      }
    } catch (error) {
      // SDK not available or incompatible version
    }
  }

  /**
   * Uninstall interceptor and restore original methods
   */
  uninstall(): void {
    try {
      const OpenAI = require('openai');

      // Restore Chat Completions
      const ChatCompletions = OpenAI.Chat?.Completions;
      if (ChatCompletions && this.originalMethods.has('completions.create')) {
        ChatCompletions.prototype.create = this.originalMethods.get('completions.create');
      }

      // Restore Responses API
      try {
        const Responses = OpenAI.Responses;
        if (Responses && this.originalMethods.has('responses.create')) {
          Responses.prototype.create = this.originalMethods.get('responses.create');
        }
      } catch {
        // Responses API not available
      }
    } catch {
      // SDK not available
    }
  }

  /**
   * Intercept Chat Completions create method
   */
  private async interceptCreate(
    context: any,
    params: any,
    options?: any
  ): Promise<any> {
    const config = getCurrentConfig();

    if (!config) {
      // No learning context active - pass through
      const originalMethod = this.originalMethods.get('completions.create');
      if (!originalMethod) {
        throw new Error('Original method not found');
      }
      return originalMethod.call(context, params, options);
    }

    if (process.env.DEBUG_AGENTIC_LEARNING) {
      console.log('[OpenAI] Intercepting for agent:', config.agentName);
    }

    // Extract user message
    const userMessage = this.extractUserMessages(params);

    // Inject memory context if enabled
    params = await this.retrieveAndInjectMemory(config, params);

    // Call original method
    const originalMethod = this.originalMethods.get('completions.create');
    const response = await originalMethod.call(context, params, options);

    // Check if streaming
    if (params.stream) {
      // Handle streaming response - wrap to accumulate chunks
      const wrappedStream = this.wrapStreamingResponse(response, userMessage, params.model || 'gpt-5');
      return wrappedStream;
    } else {
      // Non-streaming - extract and save immediately
      const modelName = this.extractModelName(response);

      await saveConversationTurn(
        this.PROVIDER,
        modelName,
        this.buildRequestMessages(userMessage),
        this.buildResponseDict(response)
      ).catch(() => {
        // Silently fail
      });

      return response;
    }
  }

  /**
   * Intercept Responses API create method
   */
  private async interceptResponsesCreate(
    context: any,
    params: any,
    options?: any
  ): Promise<any> {
    const config = getCurrentConfig();

    if (!config) {
      // No learning context active - pass through
      const originalMethod = this.originalMethods.get('responses.create');
      if (!originalMethod) {
        throw new Error('Original method not found');
      }
      return originalMethod.call(context, params, options);
    }

    // Extract user message (Responses API uses 'input' instead of 'messages')
    const userMessage = params.input || '';

    // Inject memory context if enabled
    params = await this.retrieveAndInjectMemory(config, params);

    // Call original method
    const originalMethod = this.originalMethods.get('responses.create');
    const response = await originalMethod.call(context, params, options);

    // Extract and save
    const modelName = this.extractModelName(response);

    await saveConversationTurn(
      this.PROVIDER,
      modelName,
      this.buildRequestMessages(userMessage),
      this.buildResponseDict(response)
    ).catch(() => {
      // Silently fail
    });

    return response;
  }

  /**
   * Extract user messages from Chat Completions parameters
   */
  extractUserMessages(params: any): string {
    if (!params.messages) {
      return '';
    }

    const messages: string[] = [];
    for (const msg of params.messages) {
      if (msg.role === 'user' && msg.content) {
        messages.push(typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content));
      }
    }

    return messages.join('\n');
  }

  /**
   * Extract assistant message from response
   */
  extractAssistantMessage(response: any): string {
    // Handle both Chat Completions and Responses API
    if (response.choices?.[0]?.message?.content) {
      return response.choices[0].message.content;
    }
    if (response.output) {
      return response.output;
    }
    return '';
  }

  /**
   * Build request messages array for Letta
   */
  buildRequestMessages(userMessage: string): Array<{ role: string; content: string }> {
    return [{ role: 'user', content: userMessage }];
  }

  /**
   * Build response dict for Letta
   */
  buildResponseDict(response: any): { role: string; content: string } {
    return {
      role: 'assistant',
      content: this.extractAssistantMessage(response),
    };
  }

  /**
   * Extract model name from response
   */
  extractModelName(response?: any): string {
    if (response?.model) {
      return response.model;
    }
    return 'gpt-5'; // Fallback default
  }

  /**
   * Inject memory context into OpenAI parameters
   */
  injectMemoryContext(params: Record<string, any>, context: string): Record<string, any> {
    if (!context) {
      return params;
    }

    // For Chat Completions API
    if (params.messages) {
      // Check if there's already a system message
      const hasSystemMessage = params.messages.some((msg: any) => msg.role === 'system');

      if (hasSystemMessage) {
        // Prepend to existing system message
        params.messages = params.messages.map((msg: any) => {
          if (msg.role === 'system') {
            return {
              ...msg,
              content: `${context}\n\n${msg.content}`,
            };
          }
          return msg;
        });
      } else {
        // Add new system message at the beginning
        params.messages = [
          { role: 'system', content: context },
          ...params.messages,
        ];
      }
    }

    // For Responses API
    if (params.input) {
      params.input = `${context}\n\n${params.input}`;
    }

    return params;
  }

  /**
   * Build response from streaming chunks
   */
  protected buildResponseFromChunks(chunks: any[]): any {
    const content = chunks
      .map((chunk) => {
        if (chunk.choices?.[0]?.delta?.content) {
          return chunk.choices[0].delta.content;
        }
        if (chunk.output_delta) {
          return chunk.output_delta;
        }
        return '';
      })
      .join('');

    return {
      choices: [
        {
          message: {
            role: 'assistant',
            content,
          },
        },
      ],
      model: chunks[0]?.model || 'gpt-5',
    };
  }

  /**
   * Wrap streaming response to accumulate chunks and save when done
   */
  private wrapStreamingResponse(stream: any, userMessage: string, modelName: string): any {
    const chunks: any[] = [];
    const self = this;

    // Create async generator wrapper
    const wrappedGenerator = async function* () {
      try {
        for await (const chunk of stream) {
          chunks.push(chunk);
          yield chunk;
        }
      } finally {
        // After stream completes, save the accumulated conversation
        if (chunks.length > 0 && userMessage) {
          self.saveStreamingTurn(chunks, userMessage, modelName);
        }
      }
    };

    // Return the wrapped generator
    return wrappedGenerator();
  }

  /**
   * Save streaming conversation turn after accumulating chunks
   */
  private saveStreamingTurn(chunks: any[], userMessage: string, modelName: string): void {
    if (!userMessage) {
      return;
    }

    // Build complete response from chunks (uses existing method)
    const response = this.buildResponseFromChunks(chunks);

    // Save to Letta
    saveConversationTurn(
      this.PROVIDER,
      modelName,
      this.buildRequestMessages(userMessage),
      this.buildResponseDict(response)
    ).catch(() => {
      // Silently fail
    });
  }
}
