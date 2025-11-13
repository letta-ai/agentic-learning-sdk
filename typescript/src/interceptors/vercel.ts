/**
 * Vercel AI SDK Interceptor
 *
 * Intercepts Vercel AI SDK calls by patching provider model prototypes.
 * Works with @ai-sdk/anthropic, @ai-sdk/openai, and other providers.
 * Supports both streaming (doStream) and non-streaming (doGenerate) methods.
 */

import { BaseAPIInterceptor } from './base';
import type { Provider } from '../types';
import { getCurrentConfig } from '../core';
import { saveConversationTurn } from './utils';

// Map of provider packages to their model class names
const PROVIDER_MODEL_CLASSES: Record<string, string[]> = {
  '@ai-sdk/anthropic': ['AnthropicMessagesLanguageModel'],
  '@ai-sdk/openai': ['OpenAIChatLanguageModel', 'OpenAIResponsesLanguageModel'],
  '@ai-sdk/google': ['GoogleGenerativeAILanguageModel'],
};

export class VercelInterceptor extends BaseAPIInterceptor {
  readonly PROVIDER: Provider = 'vercel';
  private patchedClasses: Set<string> = new Set();

  /**
   * Check if any Vercel AI SDK providers are available
   */
  isAvailable(): boolean {
    // Check if any provider packages are loaded in module cache
    try {
      const Module = require('module');
      const cache = (Module as any)._cache || require.cache;

      for (const providerPackage of Object.keys(PROVIDER_MODEL_CLASSES)) {
        const hasProvider = Object.keys(cache).some(k => k.includes(providerPackage));
        if (hasProvider) {
          return true;
        }
      }

      // Fallback: try to require any provider package
      for (const providerPackage of Object.keys(PROVIDER_MODEL_CLASSES)) {
        try {
          require(providerPackage);
          return true;
        } catch {
          // Continue checking other providers
        }
      }
    } catch {
      // Module cache access failed
    }

    return false;
  }

  /**
   * Install interceptor by patching provider model prototypes
   *
   * Strategy: Find provider packages in module cache and patch their model class prototypes.
   * This allows us to intercept doGenerate() and doStream() calls for all providers.
   */
  install(): void {
    let patchedAny = false;

    // Strategy 1: Check module cache for loaded providers
    try {
      const Module = require('module');
      const cache = (Module as any)._cache || require.cache;

      for (const [providerPackage, modelClassNames] of Object.entries(PROVIDER_MODEL_CLASSES)) {
        // Find cached modules for this provider
        for (const key of Object.keys(cache)) {
          if (key.includes(providerPackage) && key.includes('index')) {
            const cachedModule = cache[key];
            if (cachedModule && cachedModule.exports) {
              // Try to find and patch model classes
              if (this.tryPatchProviderModels(cachedModule.exports, modelClassNames, providerPackage)) {
                patchedAny = true;
              }
            }
          }
        }
      }
    } catch (error) {
      // Cache strategy failed, try fallback
    }

    // Strategy 2: Try require() as fallback
    if (!patchedAny) {
      for (const [providerPackage, modelClassNames] of Object.entries(PROVIDER_MODEL_CLASSES)) {
        try {
          const providerModule = require(providerPackage);
          if (this.tryPatchProviderModels(providerModule, modelClassNames, providerPackage)) {
            patchedAny = true;
          }
        } catch (error) {
          // Provider not installed, skip
        }
      }
    }

    (global as any).__VERCEL_INTERCEPTOR_REGISTERED__ = this;
  }

  /**
   * Try to patch provider model prototypes
   */
  private tryPatchProviderModels(
    providerModule: any,
    _modelClassNames: string[],
    _providerPackage: string
  ): boolean {
    try {
      let patched = false;

      // Try to create a model instance to get the class
      const providerFunction = providerModule.anthropic || providerModule.openai || providerModule.google;
      if (!providerFunction) {
        return false;
      }

      // Create a dummy model instance to access the prototype
      let modelInstance;
      try {
        modelInstance = providerFunction('dummy-model', { apiKey: 'dummy-key' });
      } catch (error) {
        // Try without options
        try {
          modelInstance = providerFunction('dummy-model');
        } catch {
          return false;
        }
      }

      if (!modelInstance) {
        return false;
      }

      const proto = Object.getPrototypeOf(modelInstance);
      const className = proto.constructor.name;

      // Check if this class was already patched
      if (this.patchedClasses.has(className)) {
        return true;
      }

      // Patch doGenerate method
      if (proto.doGenerate && typeof proto.doGenerate === 'function') {
        const methodKey = `${className}.doGenerate`;
        if (!this.originalMethods.has(methodKey)) {
          this.originalMethods.set(methodKey, proto.doGenerate);
        }

        const self = this;
        proto.doGenerate = async function (this: any, ...args: any[]) {
          return self.interceptDoGenerate(this, methodKey, args);
        };
        patched = true;
      }

      // Patch doStream method
      if (proto.doStream && typeof proto.doStream === 'function') {
        const methodKey = `${className}.doStream`;
        if (!this.originalMethods.has(methodKey)) {
          this.originalMethods.set(methodKey, proto.doStream);
        }

        const self = this;
        proto.doStream = async function (this: any, ...args: any[]) {
          return self.interceptDoStream(this, methodKey, args);
        };
        patched = true;
      }

      if (patched) {
        this.patchedClasses.add(className);
      }

      return patched;
    } catch (error) {
      // Patching failed
    }
    return false;
  }

  /**
   * Uninstall interceptor and restore original methods
   */
  uninstall(): void {
    // Restore all patched prototype methods
    for (const [_methodKey, _originalMethod] of this.originalMethods.entries()) {
      try {
        // We'd need to keep a reference to the prototype to restore properly
        // For now, just clear the map
      } catch {
        // Continue
      }
    }
    this.originalMethods.clear();
    this.patchedClasses.clear();
  }

  /**
   * Intercept doGenerate (non-streaming)
   */
  private async interceptDoGenerate(context: any, methodKey: string, args: any[]): Promise<any> {
    const config = getCurrentConfig();

    if (!config) {
      // No learning context active - pass through
      const originalMethod = this.originalMethods.get(methodKey);
      if (!originalMethod) {
        throw new Error(`Original method not found: ${methodKey}`);
      }
      return originalMethod.apply(context, args);
    }

    // Extract user message from the request
    const [options] = args;
    const userMessage = this.extractUserMessagesFromOptions(options);

    // Inject memory context if enabled
    const modifiedOptions = await this.retrieveAndInjectMemoryIntoOptions(config, options);
    args[0] = modifiedOptions;

    // Call original method
    const originalMethod = this.originalMethods.get(methodKey);
    const response = await originalMethod.apply(context, args);

    // Extract and save conversation
    const modelName = context.modelId || 'unknown';

    await saveConversationTurn(
      this.PROVIDER,
      modelName,
      this.buildRequestMessages(userMessage),
      this.buildResponseDictFromGenerate(response)
    ).catch(() => {
      // Silently fail
    });

    return response;
  }

  /**
   * Intercept doStream (streaming)
   */
  private async interceptDoStream(context: any, methodKey: string, args: any[]): Promise<any> {
    const config = getCurrentConfig();

    if (!config) {
      // No learning context active - pass through
      const originalMethod = this.originalMethods.get(methodKey);
      if (!originalMethod) {
        throw new Error(`Original method not found: ${methodKey}`);
      }
      return originalMethod.apply(context, args);
    }

    // Extract user message from the request
    const [options] = args;
    const userMessage = this.extractUserMessagesFromOptions(options);

    // Inject memory context if enabled
    const modifiedOptions = await this.retrieveAndInjectMemoryIntoOptions(config, options);
    args[0] = modifiedOptions;

    // Call original method
    const originalMethod = this.originalMethods.get(methodKey);
    const streamResult = await originalMethod.apply(context, args);

    // Wrap the stream to capture the full response
    const modelName = context.modelId || 'unknown';
    const wrappedStream = this.wrapProviderStreamingResponse(streamResult, userMessage, modelName);

    return wrappedStream;
  }

  /**
   * Wrap provider streaming response to accumulate text and save when done
   */
  private wrapProviderStreamingResponse(streamResult: any, userMessage: string, modelName: string): any {
    const self = this;
    let accumulatedText = '';

    // The stream result from doStream returns an async generator
    // We need to wrap it to accumulate the text chunks
    const originalStream = streamResult;

    const wrappedGenerator = async function* () {
      try {
        for await (const chunk of originalStream) {
          // Accumulate text from chunks
          if (chunk.type === 'text-delta' && chunk.textDelta) {
            accumulatedText += chunk.textDelta;
          }
          yield chunk;
        }
      } finally {
        // After stream completes, save the accumulated conversation
        if (accumulatedText && userMessage) {
          self.saveProviderStreamingTurn(accumulatedText, userMessage, modelName);
        }
      }
    };

    return wrappedGenerator();
  }

  /**
   * Save provider streaming conversation turn after accumulating chunks
   */
  private saveProviderStreamingTurn(text: string, userMessage: string, modelName: string): void {
    if (!userMessage) {
      return;
    }

    // Save to Letta
    saveConversationTurn(
      this.PROVIDER,
      modelName,
      this.buildRequestMessages(userMessage),
      {
        role: 'assistant',
        content: text,
      }
    ).catch(() => {
      // Silently fail
    });
  }

  /**
   * Extract user messages from provider options
   */
  private extractUserMessagesFromOptions(options: any): string {
    if (!options || !options.prompt) {
      return '';
    }

    const messages: string[] = [];

    for (const msg of options.prompt) {
      if (msg.role === 'user') {
        if (typeof msg.content === 'string') {
          messages.push(msg.content);
        } else if (Array.isArray(msg.content)) {
          // Multi-modal content - extract text parts
          const textParts = msg.content
            .filter((c: any) => c.type === 'text')
            .map((c: any) => c.text || '');
          messages.push(textParts.join(' '));
        }
      }
    }

    return messages.join('\n');
  }

  /**
   * Inject memory context into provider options
   */
  private async retrieveAndInjectMemoryIntoOptions(config: any, options: any): Promise<any> {
    // Check if capture_only mode is enabled
    if (config.captureOnly) {
      return options;
    }

    const client = config.client;
    const agentName = config.agentName;

    if (!client || !agentName) {
      return options;
    }

    try {
      // Retrieve memory context
      const memoryContext = await client.memory.context.retrieve(agentName);

      if (!memoryContext) {
        return options;
      }

      // Inject memory context into system message
      if (!options.prompt) {
        return options;
      }

      // Add system message at the beginning if not present
      const hasSystem = options.prompt.some((msg: any) => msg.role === 'system');

      if (hasSystem) {
        // Prepend to existing system message
        options.prompt = options.prompt.map((msg: any) => {
          if (msg.role === 'system') {
            return {
              ...msg,
              content: memoryContext + '\n\n' + msg.content,
            };
          }
          return msg;
        });
      } else {
        // Add new system message
        options.prompt = [
          { role: 'system', content: memoryContext },
          ...options.prompt,
        ];
      }

      return options;
    } catch (error) {
      return options;
    }
  }

  /**
   * Build response dict from doGenerate response
   */
  private buildResponseDictFromGenerate(response: any): { role: string; content: string } {
    let text = '';

    if (response.text) {
      text = response.text;
    } else if (response.content) {
      // Extract text from content array
      for (const part of response.content) {
        if (part.type === 'text' && part.text) {
          text += part.text;
        }
      }
    }

    return {
      role: 'assistant',
      content: text,
    };
  }

  /**
   * Required abstract methods from BaseAPIInterceptor
   */

  extractUserMessages(): string {
    // Not used - we extract from provider options instead
    return '';
  }

  extractAssistantMessage(response: any): string {
    return this.buildResponseDictFromGenerate(response).content;
  }

  buildRequestMessages(userMessage: string): Array<{ role: string; content: string }> {
    return [{ role: 'user', content: userMessage }];
  }

  buildResponseDict(response: any): { role: string; content: string } {
    return this.buildResponseDictFromGenerate(response);
  }

  extractModelName(response?: any, modelSelf?: any): string {
    if (modelSelf?.modelId) {
      return modelSelf.modelId;
    }
    if (response?.modelId) {
      return response.modelId;
    }
    return 'unknown';
  }

  injectMemoryContext(kwargs: Record<string, any>, _context: string): Record<string, any> {
    // Not used - we inject into provider options instead
    return kwargs;
  }

  protected buildResponseFromChunks(chunks: any[]): any {
    // Not used for provider-level patching
    const text = chunks.join('');
    return { text };
  }
}
