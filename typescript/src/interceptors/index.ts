/**
 * Agentic Learning Interceptors
 *
 * Automatic SDK integration for capturing conversations and injecting memory.
 */

export { BaseAPIInterceptor } from './base';
export type { IBaseInterceptor } from './base';
export type { Provider } from '../types';
export { install, registerInterceptor, uninstallAll } from './registry';
export { OpenAIInterceptor } from './openai';
export { AnthropicInterceptor } from './anthropic';
export { GeminiInterceptor } from './gemini';
export { ClaudeInterceptor } from './claude';
export { VercelInterceptor } from './vercel';

// Register available interceptors
import { OpenAIInterceptor } from './openai';
import { AnthropicInterceptor } from './anthropic';
import { GeminiInterceptor } from './gemini';
import { ClaudeInterceptor } from './claude';
import { VercelInterceptor } from './vercel';
import { registerInterceptor } from './registry';

registerInterceptor(OpenAIInterceptor);
registerInterceptor(AnthropicInterceptor);
registerInterceptor(GeminiInterceptor);
registerInterceptor(ClaudeInterceptor);
registerInterceptor(VercelInterceptor);
