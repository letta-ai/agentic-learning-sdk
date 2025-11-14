/**
 * OpenAI Chat Completions tests.
 *
 * Tests the OpenAI interceptor with mocked API calls.
 * Uses shared testRunners for common test logic.
 */

import { learning } from '../../src/core';
import { createTestClient, generateAgentName, cleanupAgent, getSleepConfig, resetInterceptors } from './setup';
import { createOpenAIMockResponse } from '../shared/mockHelpers';
import * as testRunners from '../shared/testRunners';

// Module-level state for capturing kwargs
let capturedParams: any = null;

// Mock OpenAI SDK
const mockCreate = jest.fn();
const mockResponse = createOpenAIMockResponse();

// Mock the OpenAI module with proper structure for interceptor
jest.mock('openai', () => {
  // Create a mock Completions class with prototype
  class MockCompletions {
    create(params: any, options?: any) {
      return mockCreate(params, options);
    }
  }

  class MockChat {
    completions: MockCompletions;
    constructor() {
      this.completions = new MockCompletions();
    }
  }

  class MockOpenAI {
    chat: MockChat;
    constructor() {
      this.chat = new MockChat();
    }
  }

  // Export both the class and the static structure for interceptor
  return {
    __esModule: true,
    default: MockOpenAI,
    Chat: {
      Completions: MockCompletions,
    },
  };
});

describe('OpenAI Chat Completions Interceptor', () => {
  let learningClient: ReturnType<typeof createTestClient>;
  let agentName: string;
  const sleepConfig = getSleepConfig();

  beforeEach(() => {
    // Reset interceptors for test isolation
    resetInterceptors();

    // Create learning client
    learningClient = createTestClient();
    agentName = generateAgentName();

    // Reset mock
    capturedParams = null;
    mockCreate.mockReset();
    mockCreate.mockImplementation((params) => {
      capturedParams = params;
      return Promise.resolve(mockResponse);
    });
  });

  afterEach(async () => {
    // Cleanup agent
    await cleanupAgent(learningClient, agentName);
  });

  // Helper to make OpenAI call
  const makeCall = async (prompt: string) => {
    const OpenAI = require('openai').default;
    const openai = new OpenAI();
    return await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [{ role: 'user', content: prompt }],
    });
  };

  // Helper to get captured params
  const getCapturedParams = () => capturedParams;

  test('conversation saved to Letta', async () => {
    await learning({ agent: agentName, client: learningClient }, async () => {
      await testRunners.conversationSaved(
        learningClient,
        agentName,
        makeCall,
        sleepConfig,
        'Alice'
      );
    });
  });

  test('memory injection', async () => {
    await learning({ agent: agentName, client: learningClient }, async () => {
      await testRunners.memoryInjection(
        learningClient,
        agentName,
        makeCall,
        getCapturedParams,
        sleepConfig,
        'Bob'
      );
    });
  });

  test('capture only mode', async () => {
    await learning({ agent: agentName, client: learningClient, captureOnly: true }, async () => {
      await testRunners.captureOnly(
        learningClient,
        agentName,
        makeCall,
        getCapturedParams,
        sleepConfig
      );
    });
  });

  test('interceptor cleanup', async () => {
    // Make call inside learning context
    await learning({ agent: agentName, client: learningClient }, async () => {
      await makeCall('Test message');
    });

    // Make call OUTSIDE learning context
    await makeCall('Uncaptured message');

    // Verify using test runner
    await testRunners.interceptorCleanup(
      learningClient,
      agentName,
      async () => {}, // Already called
      async () => {}, // Already called
      sleepConfig
    );
  });
});
