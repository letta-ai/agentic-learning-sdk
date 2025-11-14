/**
 * Google Gemini SDK tests.
 *
 * Tests the Gemini API interceptor with mocked API calls.
 * Uses shared testRunners for common test logic.
 */

import { learning } from '../../src/core';

import { createTestClient, generateAgentName, cleanupAgent, getSleepConfig, resetInterceptors } from './setup';
import { createGeminiMockResponse } from '../shared/mockHelpers';
import * as testRunners from '../shared/testRunners';

// Module-level state for capturing kwargs
let capturedParams: any = null;

// Mock Gemini SDK
const mockGenerateContent = jest.fn();
const mockResponse = createGeminiMockResponse();

// Mock the @google/generative-ai module
jest.mock('@google/generative-ai', () => {
  class MockGenerativeModel {
    modelName: string;
    constructor(modelName: string) {
      this.modelName = modelName;
    }
    async generateContent(prompt: any) {
      return mockGenerateContent(prompt);
    }
  }

  return {
    __esModule: true,
    GoogleGenerativeAI: class {
      getGenerativeModel(config: any) {
        return new MockGenerativeModel(config.model);
      }
    },
  };
});

describe('Google Gemini API Interceptor', () => {
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
    mockGenerateContent.mockReset();
    mockGenerateContent.mockImplementation((prompt) => {
      capturedParams = { contents: prompt };
      return Promise.resolve(mockResponse);
    });
  });

  afterEach(async () => {
    // Cleanup agent
    await cleanupAgent(learningClient, agentName);
  });

  // Helper to make Gemini call
  const makeCall = async (prompt: string) => {
    const { GoogleGenerativeAI } = require('@google/generative-ai');
    const genAI = new GoogleGenerativeAI('fake-key');
    const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });
    return await model.generateContent(prompt);
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
