/**
 * Anthropic SDK tests.
 *
 * Tests the Anthropic Messages API interceptor with mocked API calls.
 * Uses shared testRunners for common test logic.
 */

import { learning } from '../../src/core';

import { createTestClient, generateAgentName, cleanupAgent, getSleepConfig, resetInterceptors } from './setup';
import { createAnthropicMockResponse } from '../shared/mockHelpers';
import * as testRunners from '../shared/testRunners';

// Module-level state for capturing kwargs
let capturedParams: any = null;

// Mock Anthropic SDK
const mockCreate = jest.fn();
const mockResponse = createAnthropicMockResponse();

// Mock the Anthropic module
jest.mock('@anthropic-ai/sdk', () => {
  class MockMessages {
    create(params: any) {
      return mockCreate(params);
    }
  }

  class MockAnthropic {
    messages: MockMessages;
    constructor() {
      this.messages = new MockMessages();
    }
  }

  return {
    __esModule: true,
    default: MockAnthropic,
  };
});

describe('Anthropic Messages API Interceptor', () => {
  let learningClient: ReturnType<typeof createTestClient>;
  let agentName: string;
  const sleepConfig = getSleepConfig();

  beforeEach(() => {
    // Reset interceptors for test isolation
    resetInterceptors();

    // Install interceptors

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

  // Helper to make Anthropic call
  const makeCall = async (prompt: string) => {
    const Anthropic = require('@anthropic-ai/sdk').default;
    const anthropic = new Anthropic();
    return await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1024,
      messages: [{ role: 'user', content: prompt }],
    });
  };

  // Helper to get captured params
  const getCapturedParams = () => capturedParams;

  test('conversation saved to Letta', async () => {
    await learning({
      agent: agentName,
      client: learningClient,
    }, async () => {
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
    await learning({
      agent: agentName,
      client: learningClient,
    }, async () => {
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
    await learning({
      agent: agentName,
      client: learningClient,
      captureOnly: true,
    }, async () => {
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
