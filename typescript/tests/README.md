# Test Suite - Agentic Learning SDK (TypeScript)

## Quick Start

### Prerequisites

Install the SDK test dependencies:

```bash
cd typescript
npm install --save-dev \
  openai \
  @anthropic-ai/sdk \
  @google/generative-ai \
  ai \
  @ai-sdk/anthropic \
  @ai-sdk/openai
```

### Run All Tests

```bash
# With cloud Letta (default)
LETTA_API_KEY=your-key \
ANTHROPIC_API_KEY=your-key \
npm test

# Or explicitly specify cloud mode
LETTA_ENV=cloud \
LETTA_API_KEY=your-key \
ANTHROPIC_API_KEY=your-key \
npm test

# With local Letta server
LETTA_ENV=local \
npm test
```

### Run Specific Test Types

```bash
# Run only unit tests
npm test -- tests/unit/

# Run only integration tests
npm test -- tests/integration/

# Run specific provider tests
npm test -- openai.test.ts

# Run only passing tests (skip known issues)
npm test -- --testPathPattern="(openai|anthropic|gemini).test.ts"
```

### Run Integration Tests (Real API Calls)

Integration tests require API keys and make real API calls (costs money):

```bash
# Run all integration tests
LETTA_API_KEY=your-key \
ANTHROPIC_API_KEY=your-key \
OPENAI_API_KEY=your-key \
GOOGLE_API_KEY=your-key \
npm test -- tests/integration/

# Run specific provider integration test
LETTA_API_KEY=your-key \
OPENAI_API_KEY=your-key \
npm test -- tests/integration/openai.test.ts
```

## Current Test Status

### Unit Tests Passing (16/16 - 100%)

Unit tests use **Jest mocks** with **mocked LLM calls** (no API keys required):

| Provider | Tests | Status |
|----------|-------|--------|
| **OpenAI Chat** | 4/4 | ✅ |
| **OpenAI Responses** | 4/4 | ✅ |
| **Anthropic** | 4/4 | ✅ |
| **Gemini** | 4/4 | ✅ |

### Integration Tests Passing (24/24 - 100%)

Integration tests use **real SDK code** with **real LLM API calls** (requires API keys, costs money):

| Provider | Tests | Status |
|----------|-------|--------|
| **OpenAI Chat** | 4/4 | ✅ |
| **Anthropic** | 4/4 | ✅ |
| **Vercel AI SDK** | 4/4 | ✅ |
| **OpenAI Responses** | 4/4 | ✅ |
| **Gemini** | 4/4 | ✅ |
| **Claude Agent SDK** | 4/4 | ✅ (runs via tsx) |

**Note**: Claude Agent SDK tests run via tsx (not Jest) since Claude SDK is ESM-only.

### **Total: 40/40 Tests Passing (100%)**

**Note**: Integration tests are skipped if API keys are not provided.

## Test Architecture Overview

Our test suite follows a **"readable over clever"** philosophy - we prioritize maintainability and clarity over code reuse.

### Directory Structure

```
tests/
├── README.md                    # This file - contributor guide
├── TEST_SUITE_SUMMARY.md        # Detailed technical documentation
├── shared/                      # Reusable test logic
│   ├── testRunners.ts          # 4 core test functions
│   └── mockHelpers.ts          # Mock response creators
├── unit/                        # Unit tests with mocked SDKs
│   ├── setup.ts                # Test fixtures and reset logic
│   ├── openai.test.ts          # ✅ 4 tests passing
│   ├── openai_responses.test.ts # ✅ 4 tests passing
│   ├── anthropic.test.ts       # ✅ 4 tests passing
│   └── gemini.test.ts          # ✅ 4 tests passing
└── integration/                 # Integration tests with real APIs
    ├── setup.ts                # Test fixtures for integration tests
    ├── openai.test.ts          # ✅ 4 tests passing
    ├── anthropic.test.ts       # ✅ 4 tests passing
    ├── vercel.test.ts          # ✅ 4 tests passing
    ├── openai_responses.test.ts # ✅ 4 tests passing
    ├── gemini.test.ts          # ✅ 4 tests passing
    └── claude.test.mts         # ✅ 4 tests passing (uses tsx, not Jest)
```

### Unit Tests vs Integration Tests

The test suite includes two complementary test strategies:

**Unit Tests** (`tests/unit/`):
- ✅ Real SDK code executes
- ✅ LLM SDK calls are mocked (no requests to OpenAI/Anthropic/Google)
- ✅ Letta API calls are REAL (requires Letta server - cloud or local)
- ✅ No LLM API keys required (fake keys work with Jest mocks)
- ✅ Requires LETTA_API_KEY (for cloud) or local Letta server
- ✅ No LLM API costs (but cloud Letta has usage limits)
- ✅ Faster execution (~2 minutes)
- **Purpose**: Test interceptor works correctly with real SDK internals, no LLM costs
- **Uses**: Jest mocks for LLM SDK methods

**Integration Tests** (`tests/integration/`):
- ✅ Real SDK code executes
- ✅ Real LLM API calls (actual network requests to OpenAI/Anthropic/Google)
- ✅ Real Letta API calls (requires Letta server - cloud or local)
- ⚠️ Requires valid LLM API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)
- ⚠️ Requires LETTA_API_KEY (for cloud) or local Letta server
- ⚠️ Costs money (uses real LLM API credits)
- ⚠️ Slower execution (~2-3 minutes depending on API latency)
- **Purpose**: End-to-end validation with actual LLM services
- **Note**: Tests are skipped if LLM API keys not provided

**Both test suites reuse the exact same test runner functions from `shared/testRunners.ts`!** This demonstrates the flexibility and reusability of the test architecture.

### The 4 Core Tests

Every provider test suite runs the same 4 tests via shared test runners:

1. **`conversationSaved`** - Verifies conversations are captured and saved to Letta
2. **`memoryInjection`** - Verifies memory context is injected into LLM calls
3. **`captureOnly`** - Verifies capture-only mode doesn't inject memory
4. **`interceptorCleanup`** - Verifies interceptor only captures within learning context

### How It Works

```typescript
// Each provider test file follows this pattern:

// 1. Mock the SDK
jest.mock('openai', () => { /* mock implementation */ });

// 2. Create test fixtures
beforeEach(() => {
  resetInterceptors();  // Critical for test isolation!
  learningClient = createTestClient();
  agentName = generateAgentName();
});

// 3. Run shared test logic
test('conversation saved to Letta', async () => {
  await learning({ agent: agentName, client: learningClient }, async () => {
    await testRunners.conversationSaved(
      learningClient,
      agentName,
      makeCall,
      sleepConfig,
      'Alice'  // Expected content to find in saved messages
    );
  });
});
```

## Adding a New Provider Test

Want to add tests for a new provider? Follow these steps:

### 1. Create the Test File

```typescript
// tests/unit/my-provider.test.ts

import { learning } from '../../src/core';
import { createTestClient, generateAgentName, cleanupAgent, getSleepConfig, resetInterceptors } from './setup';
import * as testRunners from '../shared/testRunners';

// Mock the SDK
jest.mock('my-provider-sdk', () => {
  // Create mock classes that mimic the real SDK structure
  // See openai.test.ts for a complete example
});

describe('My Provider Interceptor', () => {
  let learningClient: ReturnType<typeof createTestClient>;
  let agentName: string;
  const sleepConfig = getSleepConfig();

  beforeEach(() => {
    resetInterceptors();
    learningClient = createTestClient();
    agentName = generateAgentName();
    // Setup your mocks
  });

  afterEach(async () => {
    await cleanupAgent(learningClient, agentName);
  });

  // Helper to make LLM calls
  const makeCall = async (prompt: string) => {
    // Your SDK-specific call here
  };

  // Now add the 4 standard tests...
  test('conversation saved to Letta', async () => { /* ... */ });
  test('memory injection', async () => { /* ... */ });
  test('capture only mode', async () => { /* ... */ });
  test('interceptor cleanup', async () => { /* ... */ });
});
```

### 2. Copy Test Patterns

The easiest approach is to copy an existing passing test file:
- For function-based APIs: use `openai.test.ts` as a template
- For class-based APIs: use `anthropic.test.ts` as a template

### 3. Create Mock Helpers

Add a mock response creator in `shared/mockHelpers.ts`:

```typescript
export function createMyProviderMockResponse(text = 'Mock response', model = 'my-model') {
  return {
    // Match your provider's response structure
    output: text,
    model,
  };
}
```

## Understanding Test Isolation

**Critical Concept**: Interceptors install globally once per process. Mocks can break this.

### The Problem

1. Test 1 installs mock SDK → enters `learning()` → interceptor wraps the mock ✅
2. Test 1 cleanup restores original method (removes interceptor wrapper) ❌
3. Test 2 installs new mock → enters `learning()` → interceptor NOT re-installed (flag still set) ❌

### The Solution

`resetInterceptors()` in `setup.ts` resets the installation flag before each test:

```typescript
export function resetInterceptors() {
  const core = require('../../src/core');
  if (core._interceptorsInstalled !== undefined) {
    core._interceptorsInstalled = false;  // Force reinstall
  }
}
```

**Always call `resetInterceptors()` in your `beforeEach` block!**

## Debugging Failing Tests

### Enable Debug Logging

```bash
DEBUG_AGENTIC_LEARNING=1 npm test -- my-test.test.ts
```

This shows:
- Interceptor installation details
- Memory injection flow
- Provider-specific patching

### Common Issues

#### 1. "Expected messages.length > 0, received 0"

**Cause**: Interceptor didn't capture the conversation.

**Debug**:
- Check if your mock has the correct structure
- Verify `resetInterceptors()` is called in `beforeEach`
- Enable debug logging to see if interceptor installed

#### 2. "Memory not found in captured params"

**Cause**: Memory injection didn't work.

**Debug**:
- Increase sleep times: `TEST_SLEEP_MEMORY=5000 npm test`
- Check if `captureOnly: false` (default)
- Verify mock captures parameters correctly

## Configuring Test Behavior

### Sleep Durations

Tests wait for async Letta processing. Adjust if tests are flaky:

```bash
# Default values (optimized for cloud Letta)
TEST_SLEEP_LONG=7000      # After agent creation (ms)
TEST_SLEEP_MEMORY=3000    # After memory creation (ms)
TEST_SLEEP_SHORT=4000     # After message capture (ms)

# Make tests faster (may cause flakiness)
TEST_SLEEP_LONG=2000 TEST_SLEEP_MEMORY=1000 TEST_SLEEP_SHORT=1500 npm test

# Make tests more reliable (slower)
TEST_SLEEP_LONG=10000 TEST_SLEEP_MEMORY=5000 TEST_SLEEP_SHORT=6000 npm test
```

### Letta Mode

```bash
# Cloud Letta (default - uses api.letta.com)
LETTA_API_KEY=your-key npm test

# Local Letta server (uses http://localhost:8283)
LETTA_ENV=local npm test
```

## Comparison with Python Test Suite

| Aspect | Python | TypeScript |
|--------|--------|------------|
| **Unit Tests** | 16/16 (100%) | 16/16 (100%) |
| **Integration Tests** | 20/20 (100%) | 24/24 (100%) |
| **Total** | 36/36 (100%) | 40/40 (100%) |
| **Architecture** | Identical | Identical |
| **Test Logic** | Same 4 test runners | Same 4 test runners |
| **Providers Tested** | 5 (includes Claude via pytest) | 6 (includes Vercel + Claude via tsx) |
| **Unique Tests** | Claude Agent SDK (pytest) | Vercel AI SDK (TypeScript/JS only) + Claude (tsx) |
| **Philosophy** | Readable over clever | Readable over clever |

Both test suites use the exact same architecture and test logic - they're "reunified" in design.

**Note**: Python includes Claude Agent SDK tests with pytest (async support), TypeScript tests Claude via tsx runner (Jest doesn't support ESM-only modules). TypeScript also includes Vercel AI SDK tests (TypeScript/JS only) and OpenAI Responses unit tests. Python has OpenAI Responses tests only in integration (not unit).

## Known Issues

### Unit Tests for Vercel AI SDK

Vercel AI SDK **does not have unit tests** due to Jest mock complexity:

- **Vercel AI SDK**: Uses prototype patching on provider model classes that Jest mocks can't properly replicate

**Vercel has full integration test coverage (4/4 tests) and works perfectly with real SDKs!**

### Claude Agent SDK (Full Integration via tsx)

Claude Agent SDK cannot be tested with Jest due to being an ESM-only module. Jest doesn't support dynamic imports of ESM modules without extensive configuration changes.

**Testing Approach**: Claude Agent SDK has full integration test coverage via tsx:
```bash
# Run Claude Agent SDK integration tests
LETTA_API_KEY=your-key \
ANTHROPIC_API_KEY=your-key \
npm run test:claude
```

**Test Status** (4/4 passing - 100%):
- ✅ Conversation saved test passes
- ✅ Memory injection test passes
- ✅ Capture only test passes
- ✅ Interceptor cleanup test passes

The test file (`tests/integration/claude.test.mts`) uses:
- ✅ .mts extension for proper ESM support
- ✅ `createRequire()` to use CommonJS `require()` (critical for interceptor!)
- ✅ tsx runner instead of Jest
- ✅ Same test patterns as other providers

**Important Implementation Detail**: The Claude interceptor hooks CommonJS `require()`, not ESM `import()`. The test uses `createRequire(import.meta.url)` to create a require function in the ESM context, allowing the interceptor to patch the SDK properly when it's loaded.

**Working Example**: Also available for interactive testing:
```bash
# Test Claude Agent SDK interactively
LETTA_API_KEY=your-key \
ANTHROPIC_API_KEY=your-key \
npx tsx examples/claude_example.ts
```

## Performance

Test suite runtimes:

- **Unit tests only**: ~2 minutes (16 tests, 100% passing, mocked LLM calls, cloud Letta)
- **Integration tests (Jest)**: ~80 seconds (20/20 tests passing, real API calls)
- **Claude tests (tsx)**: ~60 seconds (4/4 tests passing, runs separately via tsx)
- **Full suite (unit + integration + Claude)**: ~4-5 minutes (40/40 tests passing, 100%)

Optimization options:
- **Unit tests**: Use local Letta server (`LETTA_ENV=local`) or reduce sleep times
- **Integration tests**: Use cheaper models (already configured: gpt-4o-mini, claude-3-5-haiku, etc.)

## Contributing

### Before Submitting a PR

1. **Run the full test suite**: `npm test`
2. **Verify your tests pass**: Your new tests should work
3. **Follow the patterns**: Use existing tests as templates
4. **Document skipped tests**: If you skip tests, explain why in comments
5. **Update documentation**: Add your provider to this README

### Code Style

- Use TypeScript strict mode
- Follow existing naming conventions
- Add JSDoc comments to test functions
- Keep mocks in the test file (not separate files)

### Questions?

- Check `TEST_SUITE_SUMMARY.md` for detailed technical docs
- Look at `openai.test.ts` for a complete working example
- Open a GitHub issue for questions

## Resources

- **Detailed Docs**: See `TEST_SUITE_SUMMARY.md` for comprehensive technical documentation
- **Quick Reference**: See `README_TESTS.md` for quick setup commands
- **Shared Test Runners**: See `shared/testRunners.ts` for test implementation details
- **Mock Helpers**: See `shared/mockHelpers.ts` for mock response structures

---

**Happy Testing!** 🧪

If you encounter issues or have suggestions for improving this test suite, please open an issue or PR on GitHub.
