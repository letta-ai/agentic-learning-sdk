/**
 * Reusable test logic for all provider interceptor tests.
 *
 * Each function encapsulates a single test case that can be called
 * from provider-specific test files. This approach balances code reuse
 * with readability - each test file explicitly calls these functions,
 * making the test structure clear and maintainable.
 *
 * All test functions follow the same pattern:
 * 1. Accept all necessary parameters/fixtures as arguments
 * 2. Execute test logic
 * 3. Make assertions
 * 4. Return void or throw on assertion failure
 */

import { AgenticLearning } from '../../src/client';

/**
 * Sleep utility for async waiting
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export interface SleepConfig {
  longWait: number;
  memoryCreate: number;
  shortWait: number;
}

/**
 * Test that conversations are captured and saved to Letta.
 *
 * @param learningClient AgenticLearning client instance
 * @param agentName Unique agent name (will be cleaned up)
 * @param makeCall Function that makes LLM API call - signature: (prompt: string) => Promise<any>
 * @param sleepConfig Sleep durations config
 * @param expectedContent String that should appear in saved messages
 */
export async function conversationSaved(
  learningClient: AgenticLearning,
  agentName: string,
  makeCall: (prompt: string) => Promise<any>,
  sleepConfig: SleepConfig,
  expectedContent: string
): Promise<void> {
  const agent = await learningClient.agents.create({ agent: agentName });
  expect(agent).toBeTruthy();

  // Make call - handled by caller in learning context
  await makeCall(`My name is ${expectedContent}`);

  // Wait for async processing
  await sleep(sleepConfig.longWait);

  // Verify messages were saved
  const messages = await learningClient.messages.list(agentName);
  expect(messages.length).toBeGreaterThan(0);

  // Check expected content appears in messages
  const messageContents: string[] = [];
  for (const msg of messages) {
    if (msg.message_type === 'reasoning_message') {
      messageContents.push((msg as any).reasoning || '');
    } else if (msg.message_type === 'assistant_message' || msg.message_type === 'user_message') {
      const content = (msg as any).content;
      if (typeof content === 'string') {
        messageContents.push(content);
      }
    }
  }

  const hasExpected = messageContents.some((content) => content.includes(expectedContent));
  expect(hasExpected).toBe(true);
}

/**
 * Test that memory is injected into LLM calls.
 *
 * @param learningClient AgenticLearning client instance
 * @param agentName Unique agent name
 * @param makeCall Function that makes LLM API call - signature: (prompt: string) => Promise<any>
 * @param capturedState Function that returns captured kwargs/state - signature: () => any
 * @param sleepConfig Sleep durations config
 * @param expectedInPrompt String or array of strings that should appear in captured prompt
 */
export async function memoryInjection(
  learningClient: AgenticLearning,
  agentName: string,
  makeCall: (prompt: string) => Promise<any>,
  capturedState: () => any,
  sleepConfig: SleepConfig,
  expectedInPrompt: string | string[]
): Promise<void> {
  await learningClient.agents.create({ agent: agentName, memory: [] });

  const memoryValue = Array.isArray(expectedInPrompt) ? expectedInPrompt[0] : expectedInPrompt;
  await learningClient.memory.create({
    agent: agentName,
    label: 'human',
    value: `User's name is ${memoryValue}. User likes TypeScript programming.`,
  });
  await sleep(sleepConfig.memoryCreate);

  // Make call with learning context - handled by caller
  await makeCall("What's my name?");

  // Verify memory was injected
  const captured = capturedState();
  expect(captured).toBeTruthy();

  const capturedStr = JSON.stringify(captured);

  // Check for either the memory content or memory markers
  const expectedStrings = Array.isArray(expectedInPrompt) ? expectedInPrompt : [expectedInPrompt];
  expectedStrings.push('<human>'); // Memory marker

  const hasExpected = expectedStrings.some((exp) => capturedStr.includes(exp));
  expect(hasExpected).toBe(true);
}

/**
 * Test that capture_only mode saves conversations but doesn't inject memory.
 *
 * @param learningClient AgenticLearning client instance
 * @param agentName Unique agent name
 * @param makeCall Function that makes LLM API call - signature: (prompt: string) => Promise<any>
 * @param capturedState Function that returns captured kwargs/state - signature: () => any
 * @param sleepConfig Sleep durations config
 */
export async function captureOnly(
  learningClient: AgenticLearning,
  agentName: string,
  makeCall: (prompt: string) => Promise<any>,
  capturedState: () => any,
  sleepConfig: SleepConfig
): Promise<void> {
  const secretInfo = 'Secret information that should not be injected';

  await learningClient.agents.create({ agent: agentName, memory: [] });
  await learningClient.memory.create({
    agent: agentName,
    label: 'human',
    value: secretInfo,
  });
  await sleep(sleepConfig.memoryCreate);

  // Make call with capture_only=true - handled by caller
  await makeCall('Hello, how are you?');

  // Verify memory was NOT injected
  const captured = capturedState();
  const capturedStr = JSON.stringify(captured);
  expect(capturedStr).not.toContain('Secret information');

  // Verify conversation was still saved
  await sleep(sleepConfig.shortWait);
  const messages = await learningClient.messages.list(agentName);
  expect(messages.length).toBeGreaterThan(0);
}

/**
 * Test that interceptor only captures within learning context (not after).
 *
 * @param learningClient AgenticLearning client instance
 * @param agentName Unique agent name
 * @param makeCallInside Function to make call inside learning context
 * @param makeCallOutside Function to make call outside learning context
 * @param sleepConfig Sleep durations config
 */
export async function interceptorCleanup(
  learningClient: AgenticLearning,
  agentName: string,
  _makeCallInside: () => Promise<any>,
  _makeCallOutside: () => Promise<any>,
  sleepConfig: SleepConfig
): Promise<void> {
  // Calls are made by caller (inside and outside learning context)

  await sleep(sleepConfig.shortWait);

  // Verify only the first message was captured
  const messages = await learningClient.messages.list(agentName);
  expect(messages.length).toBeGreaterThan(0);

  const messageContents = messages
    .map((msg) => {
      if (msg.message_type === 'assistant_message' || msg.message_type === 'user_message') {
        return (msg as any).content || '';
      }
      return '';
    })
    .filter(Boolean);

  const hasUncaptured = messageContents.some((content) =>
    content.includes('Uncaptured message')
  );
  expect(hasUncaptured).toBe(false);
}
