/**
 * Mock helpers for provider tests.
 *
 * Provides utilities for mocking LLM API calls and capturing request parameters.
 */

/**
 * Create OpenAI mock response
 */
export function createOpenAIMockResponse(text = 'Mock response', model = 'gpt-5') {
  return {
    choices: [
      {
        message: {
          role: 'assistant',
          content: text,
        },
      },
    ],
    model,
  };
}

/**
 * Create OpenAI Responses API mock response
 */
export function createOpenAIResponsesMockResponse(text = 'Mock response', model = 'gpt-5') {
  return {
    output: text,
    model,
  };
}

/**
 * Create Anthropic mock response
 */
export function createAnthropicMockResponse(
  text = 'Mock response',
  model = 'claude-sonnet-4-20250514'
) {
  return {
    content: [
      {
        type: 'text',
        text,
      },
    ],
    model,
    role: 'assistant',
  };
}

/**
 * Create Gemini mock response
 */
export function createGeminiMockResponse(text = 'Mock response') {
  return {
    text,
    candidates: [
      {
        content: {
          parts: [{ text }],
        },
      },
    ],
  };
}

/**
 * Create Vercel AI SDK mock response
 */
export function createVercelMockResponse(text = 'Mock response', model = 'claude-sonnet-4-20250514') {
  return {
    text,
    model,
  };
}

/**
 * Get default sleep configuration
 * Defaults match Python test suite for cloud Letta API
 */
export function getDefaultSleepConfig() {
  return {
    longWait: parseInt(process.env.TEST_SLEEP_LONG || '7000'),
    memoryCreate: parseInt(process.env.TEST_SLEEP_MEMORY || '3000'),
    shortWait: parseInt(process.env.TEST_SLEEP_SHORT || '4000'),
  };
}
