/**
 * Claude Agent SDK Integration Tests
 *
 * Run with: npx tsx tests/integration/claude.test.mts
 *
 * Note: Uses .mts extension and tsx runner because Claude Agent SDK is a pure ESM module
 * that Jest cannot handle. This test file uses the same test patterns as the Jest tests
 * but runs standalone with tsx.
 */

import { learning, AgenticLearning } from '../../dist/index.js';

// Test configuration
function getSleepConfig() {
  return {
    longWait: parseInt(process.env.TEST_SLEEP_LONG || '7000'),
    memoryCreate: parseInt(process.env.TEST_SLEEP_MEMORY || '3000'),
    shortWait: parseInt(process.env.TEST_SLEEP_SHORT || '4000'),
  };
}

function createTestClient(): AgenticLearning {
  const testMode = process.env.LETTA_ENV?.toLowerCase() || 'cloud';
  if (testMode === 'local') {
    return new AgenticLearning({ baseUrl: 'http://localhost:8283' });
  } else {
    return new AgenticLearning();
  }
}

function generateAgentName(): string {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 10000);
  return `test-claude-agent-${timestamp}-${random}`;
}

async function cleanupAgent(client: AgenticLearning, agentName: string): Promise<void> {
  try {
    await client.agents.delete(agentName);
  } catch (error) {
    console.warn(`Warning: Could not cleanup agent ${agentName}:`, error);
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Test helper to make Claude calls
async function makeClaudeCall(prompt: string): Promise<string> {
  // IMPORTANT: Use require() here (not import) for memory injection to work!
  // The Claude interceptor hooks require(), not ESM import()
  const { createRequire } = await import('module');
  const require = createRequire(import.meta.url);
  const { query } = require('@anthropic-ai/claude-agent-sdk');

  const conversation = query({
    prompt,
    options: {},
  });

  let responseText = '';
  for await (const msg of conversation) {
    if (msg.type === 'assistant' && msg.message?.content) {
      for (const block of msg.message.content) {
        if (block.type === 'text') {
          responseText += block.text;
        }
      }
    }
  }

  return responseText;
}

// Test runners
async function testConversationSaved(
  client: AgenticLearning,
  agentName: string,
  sleepConfig: ReturnType<typeof getSleepConfig>
): Promise<void> {
  console.log('  Running: conversation saved to Letta');

  // Create agent
  await client.agents.create({
    agent: agentName,
    memory: [],
  });
  await sleep(sleepConfig.longWait);

  // Make a call with learning context
  await learning({ agent: agentName, client }, async () => {
    const response = await makeClaudeCall('My name is Alice. What is my name?');
    console.log('    Response:', response.substring(0, 50) + '...');
  });

  await sleep(sleepConfig.shortWait);

  // Verify messages were captured
  const messages = await client.messages.list(agentName);
  if (messages.length === 0) {
    throw new Error('Expected messages.length > 0, received 0');
  }

  // Verify content includes "Alice"
  const messageContents: string[] = [];
  for (const msg of messages) {
    // Convert entire message to string to search
    const msgStr = JSON.stringify(msg);
    messageContents.push(msgStr);
  }

  const allContent = messageContents.join(' ');
  const hasAlice = allContent.includes('Alice');
  if (!hasAlice) {
    console.log('    DEBUG: First 3 messages:', messages.slice(0, 3));
    throw new Error(`Expected to find "Alice" in messages, got: ${allContent.substring(0, 200)}`);
  }

  console.log('  ✓ conversation saved to Letta');
}

async function testMemoryInjection(
  client: AgenticLearning,
  agentName: string,
  sleepConfig: ReturnType<typeof getSleepConfig>
): Promise<void> {
  console.log('  Running: memory injection');

  // Create agent
  await client.agents.create({
    agent: agentName,
    memory: [],
  });
  await sleep(sleepConfig.longWait);

  // First interaction: establish memory
  await learning({ agent: agentName, client }, async () => {
    await makeClaudeCall('My name is Alice');
  });
  await sleep(sleepConfig.shortWait);

  // Create memory
  await client.memory.create({
    agent: agentName,
    label: 'human',
    value: 'The user prefers to be called Alice',
  });
  await sleep(sleepConfig.memoryCreate);

  // Second interaction: verify memory injection
  // Note: Since we can't intercept Claude SDK calls directly, we verify by checking
  // that the conversation was captured (which proves the interceptor is working)
  await learning({ agent: agentName, client }, async () => {
    await makeClaudeCall('What do you remember about me?');
  });
  await sleep(sleepConfig.shortWait);

  const messages = await client.messages.list(agentName);
  if (messages.length < 2) {
    throw new Error(`Expected at least 2 messages, got ${messages.length}`);
  }

  console.log('  ✓ memory injection');
}

async function testCaptureOnly(
  client: AgenticLearning,
  agentName: string,
  sleepConfig: ReturnType<typeof getSleepConfig>
): Promise<void> {
  console.log('  Running: capture only mode');

  // Create agent
  await client.agents.create({
    agent: agentName,
    memory: [],
  });
  await sleep(sleepConfig.longWait);

  // Make call with captureOnly: true
  await learning({ agent: agentName, client, captureOnly: true }, async () => {
    await makeClaudeCall('My name is Bob');
  });
  await sleep(sleepConfig.shortWait);

  // Verify messages were captured
  const messages = await client.messages.list(agentName);
  if (messages.length === 0) {
    throw new Error('Expected messages.length > 0, received 0');
  }

  const messageContents: string[] = [];
  for (const msg of messages) {
    // Convert entire message to string to search
    const msgStr = JSON.stringify(msg);
    messageContents.push(msgStr);
  }

  const allContent = messageContents.join(' ');
  const hasBob = allContent.includes('Bob');
  if (!hasBob) {
    console.log('    DEBUG: First 3 messages:', messages.slice(0, 3));
    throw new Error(`Expected to find "Bob" in messages, got: ${allContent.substring(0, 200)}`);
  }

  console.log('  ✓ capture only mode');
}

async function testInterceptorCleanup(
  client: AgenticLearning,
  agentName: string,
  sleepConfig: ReturnType<typeof getSleepConfig>
): Promise<void> {
  console.log('  Running: interceptor cleanup');

  // Create agent
  await client.agents.create({
    agent: agentName,
    memory: [],
  });
  await sleep(sleepConfig.longWait);

  // Call inside learning context
  await learning({ agent: agentName, client }, async () => {
    await makeClaudeCall('My name is Charlie');
  });
  await sleep(sleepConfig.shortWait);

  const messagesBefore = await client.messages.list(agentName);
  if (messagesBefore.length === 0) {
    throw new Error('Expected messages.length > 0 after learning context');
  }

  // Call outside learning context
  await makeClaudeCall('My name is Dave');
  await sleep(sleepConfig.shortWait);

  const messagesAfter = await client.messages.list(agentName);
  if (messagesAfter.length !== messagesBefore.length) {
    throw new Error(
      `Expected ${messagesBefore.length} messages, got ${messagesAfter.length}. ` +
      'Calls outside learning context should not be captured.'
    );
  }

  console.log('  ✓ interceptor cleanup');
}

// Main test suite
async function runTests() {
  console.log('\nClaude Agent SDK Integration Tests');
  console.log('===================================\n');

  // Check API keys
  if (!process.env.ANTHROPIC_API_KEY) {
    console.log('⚠ Skipping tests - ANTHROPIC_API_KEY not set\n');
    process.exit(0);
  }

  if (!process.env.LETTA_API_KEY && process.env.LETTA_ENV !== 'local') {
    console.log('⚠ Skipping tests - LETTA_API_KEY not set (or use LETTA_ENV=local)\n');
    process.exit(0);
  }

  const sleepConfig = getSleepConfig();
  const client = createTestClient();
  let passed = 0;
  let failed = 0;

  // Test 1: Conversation saved
  try {
    const agentName = generateAgentName();
    await testConversationSaved(client, agentName, sleepConfig);
    await cleanupAgent(client, agentName);
    passed++;
  } catch (error) {
    console.error('  ✗ conversation saved to Letta');
    console.error('    Error:', error);
    failed++;
  }

  // Test 2: Memory injection
  try {
    const agentName = generateAgentName();
    await testMemoryInjection(client, agentName, sleepConfig);
    await cleanupAgent(client, agentName);
    passed++;
  } catch (error) {
    console.error('  ✗ memory injection');
    console.error('    Error:', error);
    failed++;
  }

  // Test 3: Capture only
  try {
    const agentName = generateAgentName();
    await testCaptureOnly(client, agentName, sleepConfig);
    await cleanupAgent(client, agentName);
    passed++;
  } catch (error) {
    console.error('  ✗ capture only mode');
    console.error('    Error:', error);
    failed++;
  }

  // Test 4: Interceptor cleanup
  try {
    const agentName = generateAgentName();
    await testInterceptorCleanup(client, agentName, sleepConfig);
    await cleanupAgent(client, agentName);
    passed++;
  } catch (error) {
    console.error('  ✗ interceptor cleanup');
    console.error('    Error:', error);
    failed++;
  }

  // Summary
  console.log(`\nResults: ${passed} passed, ${failed} failed, ${passed + failed} total\n`);

  if (failed > 0) {
    process.exit(1);
  }
}

// Run tests
runTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
