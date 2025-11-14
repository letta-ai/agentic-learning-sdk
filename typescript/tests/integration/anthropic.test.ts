/**
 * Anthropic Messages API Integration Tests
 *
 * These tests use the real Anthropic SDK with real API calls.
 * Requires ANTHROPIC_API_KEY environment variable.
 */

import Anthropic from '@anthropic-ai/sdk';
import { learning } from '../../src/core';
import { createTestClient, generateAgentName, cleanupAgent, getSleepConfig } from './setup';
import * as testRunners from '../shared/testRunners';

describe('Anthropic Messages API Integration', () => {
  let learningClient: ReturnType<typeof createTestClient>;
  let agentName: string;
  let anthropic: Anthropic;
  const sleepConfig = getSleepConfig();

  beforeAll(() => {
    // Skip if no API key
    if (!process.env.ANTHROPIC_API_KEY) {
      console.log('Skipping Anthropic integration tests - ANTHROPIC_API_KEY not set');
    }
  });

  beforeEach(() => {
    if (!process.env.ANTHROPIC_API_KEY) {
      return;
    }

    learningClient = createTestClient();
    agentName = generateAgentName();
    anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
  });

  afterEach(async () => {
    if (!process.env.ANTHROPIC_API_KEY) {
      return;
    }
    await cleanupAgent(learningClient, agentName);
  });

  // Helper to make Anthropic call
  const makeCall = async (prompt: string) => {
    return await anthropic.messages.create({
      model: 'claude-3-5-haiku-20241022',
      max_tokens: 1024,
      messages: [{ role: 'user', content: prompt }],
    });
  };

  test('conversation saved to Letta', async () => {
    if (!process.env.ANTHROPIC_API_KEY) {
      console.log('Skipping - ANTHROPIC_API_KEY not set');
      return;
    }

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
    if (!process.env.ANTHROPIC_API_KEY) {
      console.log('Skipping - ANTHROPIC_API_KEY not set');
      return;
    }

    await learningClient.agents.create({ agent: agentName, memory: [] });
    await learningClient.memory.create({
      agent: agentName,
      label: 'human',
      value: "User's name is Bob. User likes TypeScript programming.",
    });
    await new Promise((resolve) => setTimeout(resolve, sleepConfig.memoryCreate));

    await learning({ agent: agentName, client: learningClient }, async () => {
      const response = await makeCall("What's my name?");
      expect(response).toBeTruthy();
    });
  });

  test('capture only mode', async () => {
    if (!process.env.ANTHROPIC_API_KEY) {
      console.log('Skipping - ANTHROPIC_API_KEY not set');
      return;
    }

    const secretInfo = 'Secret information that should not be injected';
    await learningClient.agents.create({ agent: agentName, memory: [] });
    await learningClient.memory.create({
      agent: agentName,
      label: 'human',
      value: secretInfo,
    });
    await new Promise((resolve) => setTimeout(resolve, sleepConfig.memoryCreate));

    await learning({ agent: agentName, client: learningClient, captureOnly: true }, async () => {
      const response = await makeCall('Hello, how are you?');
      expect(response).toBeTruthy();
    });

    // Verify conversation was saved
    await new Promise((resolve) => setTimeout(resolve, sleepConfig.shortWait));
    const messages = await learningClient.messages.list(agentName);
    expect(messages.length).toBeGreaterThan(0);
  });

  test('interceptor cleanup', async () => {
    if (!process.env.ANTHROPIC_API_KEY) {
      console.log('Skipping - ANTHROPIC_API_KEY not set');
      return;
    }

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
      async () => {},
      async () => {},
      sleepConfig
    );
  });
});
