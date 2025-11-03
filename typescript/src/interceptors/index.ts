/**
 * Agentic Learning Interceptors
 *
 * Automatic SDK integration for capturing conversations and injecting memory.
 */

export { BaseAPIInterceptor } from './base';
export type { Provider, IBaseInterceptor } from './base';
export { install, registerInterceptor, uninstallAll } from './registry';
export { OpenAIInterceptor } from './openai';
export { AnthropicInterceptor } from './anthropic';
export { GeminiInterceptor } from './gemini';
export { ClaudeInterceptor } from './claude';

// Register available interceptors
import { OpenAIInterceptor } from './openai';
import { AnthropicInterceptor } from './anthropic';
import { GeminiInterceptor } from './gemini';
import { ClaudeInterceptor } from './claude';
import { registerInterceptor } from './registry';

registerInterceptor(OpenAIInterceptor);
registerInterceptor(AnthropicInterceptor);
registerInterceptor(GeminiInterceptor);
registerInterceptor(ClaudeInterceptor);
