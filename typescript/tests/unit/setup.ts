/**
 * Unit Test Setup and Fixtures
 *
 * Common utilities and setup for unit tests with mocked APIs.
 */

import { AgenticLearning } from '../../src/client';
import { getDefaultSleepConfig } from '../shared/mockHelpers';

/**
 * Create a test learning client
 * Defaults to cloud Letta server
 * Set LETTA_ENV=local to use local server (http://localhost:8283)
 */
export function createTestClient(): AgenticLearning {
  const testMode = process.env.LETTA_ENV?.toLowerCase() || 'cloud';

  if (testMode === 'local') {
    return new AgenticLearning({ baseUrl: 'http://localhost:8283' });
  } else {
    return new AgenticLearning();
  }
}

/**
 * Generate a unique agent name for testing
 */
export function generateAgentName(): string {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 10000);
  return `test-agent-${timestamp}-${random}`;
}

/**
 * Cleanup agent after test
 */
export async function cleanupAgent(
  client: AgenticLearning,
  agentName: string
): Promise<void> {
  try {
    await client.agents.delete(agentName);
  } catch (error) {
    console.warn(`Warning: Could not cleanup agent ${agentName}:`, error);
  }
}

/**
 * Get sleep configuration from environment or defaults
 */
export function getSleepConfig() {
  return getDefaultSleepConfig();
}

/**
 * Reset interceptor state for test isolation
 * This is critical to ensure interceptors are reinstalled after mocks modify methods
 */
export function resetInterceptors() {
  // Import and reset the interceptor installation flag
  const core = require('../../src/core');
  if (core._interceptorsInstalled !== undefined) {
    core._interceptorsInstalled = false;
  }
}
