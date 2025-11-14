# Test Suite - Agentic Learning SDK (Python)

## Overview

The Python test suite uses a **readable, maintainable structure** with shared test logic and explicit test files. The suite includes both unit tests (real SDK + mocked LLM HTTP) and integration tests (real SDK + real API calls).

## Test Status

### ✅ All Unit Tests Passing (16/16)

Unit tests use **real SDK code** with **mocked LLM HTTP** (no actual LLM API calls):

| Provider | Tests | Status |
|----------|-------|--------|
| **OpenAI Chat** | 4/4 | ✅ |
| **Anthropic** | 4/4 | ✅ |
| **Gemini** | 4/4 | ✅ |
| **OpenAI Responses** | 4/4 | ✅ |

### Integration Tests Passing (20/20 - 100%)

Integration tests use **real SDK code** with **real LLM API calls** (requires LLM API keys):

| Provider | Tests | Status |
|----------|-------|--------|
| **OpenAI Chat** | 4/4 | ✅ |
| **Anthropic** | 4/4 | ✅ |
| **OpenAI Responses** | 4/4 | ✅ |
| **Gemini** | 4/4 | ✅ |
| **Claude Agent SDK** | 4/4 | ✅ (async) |

### **Total: 36/36 Tests Passing (100%)**

**Note**: Integration tests are skipped if API keys are not provided (via pytest.skip).

---

## Quick Start

### Run All Tests

```bash
# With cloud Letta (default)
LETTA_API_KEY=your-key \
ANTHROPIC_API_KEY=your-key \
.venv/bin/python3 -m pytest tests/ -v

# Or explicitly specify local mode
LETTA_ENV=local \
ANTHROPIC_API_KEY=your-key \
.venv/bin/python3 -m pytest tests/ -v
```

### Run Specific Test Suites

```bash
# Run only unit tests (mocked LLM HTTP)
LETTA_API_KEY=your-key \
.venv/bin/python3 -m pytest tests/unit/ -v

# Run only integration tests (real LLM API calls, requires provider API keys)
LETTA_API_KEY=your-key \
ANTHROPIC_API_KEY=your-key \
OPENAI_API_KEY=your-key \
GOOGLE_API_KEY=your-key \
.venv/bin/python3 -m pytest tests/integration/ -v

# Run specific provider tests
LETTA_API_KEY=your-key \
OPENAI_API_KEY=your-key \
.venv/bin/python3 -m pytest tests/ -m openai -v

LETTA_API_KEY=your-key \
ANTHROPIC_API_KEY=your-key \
.venv/bin/python3 -m pytest tests/ -m anthropic -v

# Run Claude Agent SDK tests (integration only, async)
LETTA_API_KEY=your-key \
ANTHROPIC_API_KEY=your-key \
.venv/bin/python3 -m pytest tests/ -m claude -v
```

### Configurable Sleep Times

Tests use configurable sleep durations to wait for async Letta processing, since Letta uses sleeptime agents:

```bash
TEST_SLEEP_LONG=5.0 \
TEST_SLEEP_MEMORY=2.0 \
TEST_SLEEP_SHORT=3.0 \
.venv/bin/python3 -m pytest tests/unit/ -v
```

---

## Test Architecture

### Directory Structure

```
tests/
├── README.md                    # This file - comprehensive test documentation
├── conftest.py                  # Root fixtures (learning_client, cleanup_agent, sleep_config)
├── pytest.ini                   # Test markers and configuration
├── shared/                      # Reusable test logic
│   ├── __init__.py
│   ├── test_runners.py          # 4 reusable test functions
│   └── mock_helpers.py          # Mock creation utilities
├── unit/                        # Unit tests with mocked LLM API calls
│   ├── __init__.py
│   ├── conftest.py              # Interceptor reset fixture (critical for test isolation)
│   ├── test_openai.py           # OpenAI Chat Completions tests (4/4 passing)
│   ├── test_anthropic.py        # Anthropic Messages API tests (4/4 passing)
│   ├── test_gemini.py           # Google Gemini tests (4/4 passing)
│   └── test_openai_responses.py # OpenAI Responses API tests (4/4 passing)
└── integration/                 # Integration tests with real LLM API calls
    ├── __init__.py
    ├── conftest.py              # Interceptor reset fixture
    ├── test_openai.py           # OpenAI Chat Completions tests (4/4 passing)
    ├── test_anthropic.py        # Anthropic Messages API tests (4/4 passing)
    ├── test_gemini.py           # Google Gemini tests (4/4 passing)
    ├── test_openai_responses.py # OpenAI Responses API tests (4/4 passing)
    └── test_claude.py           # Claude Agent SDK tests (4/4 passing, async)
```

### The 4 Core Tests

Every provider test suite runs the same 4 tests via shared test runners from `tests/shared/test_runners.py`:

1. **`conversation_saved()`** - Verifies conversations are captured and saved to Letta
2. **`memory_injection()`** - Verifies memory context is injected into LLM calls
3. **`capture_only()`** - Verifies capture-only mode doesn't inject memory, but still saves conversations
4. **`interceptor_cleanup()`** - Verifies interceptor only captures within learning context

### Unit Tests vs Integration Tests

The test suite includes two complementary test strategies:

**Unit Tests** (`tests/unit/`):
- ✅ Real SDK code executes
- ✅ LLM HTTP calls are mocked (no requests to OpenAI/Anthropic/Google)
- ✅ Letta HTTP calls are REAL (requires Letta server - cloud or local)
- ✅ No LLM API keys required (fake keys work)
- ✅ Requires LETTA_API_KEY (for cloud) or local Letta server
- ✅ No LLM API costs (but cloud Letta has usage limits)
- ✅ Fastest execution (~3-4 minutes for full suite)
- **Purpose**: Test interceptor works correctly with real SDK internals, no LLM costs
- **Uses**: `pytest-httpx` for mocking LLM HTTP calls

**Integration Tests** (`tests/integration/`):
- ✅ Real SDK code executes
- ✅ Real LLM API calls (actual network requests to OpenAI/Anthropic/Google)
- ✅ Real Letta API calls (requires Letta server - cloud or local)
- ⚠️ Requires valid LLM API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)
- ⚠️ Requires LETTA_API_KEY (for cloud) or local Letta server
- ⚠️ Costs money (uses real LLM API credits)
- ⚠️ Slower execution (~5-10 minutes depending on API latency)
- **Purpose**: End-to-end validation with actual LLM services
- **Note**: Tests are skipped if LLM API keys not provided

**Both test suites reuse the exact same test runner functions from `shared/test_runners.py`!** This demonstrates the flexibility and reusability of the test architecture.

---

## Key Implementation Details

### Provider Test Pattern

Each provider test file follows this pattern:

```python
@pytest.mark.unit  # or @pytest.mark.integration
@pytest.mark.openai  # Provider-specific marker
class TestOpenAIUnit:
    """OpenAI Chat Completions unit tests."""

    def test_conversation_saved(self, learning_client, cleanup_agent, make_llm_call, sleep_config):
        """Test conversations are captured and saved to Letta."""
        test_runners.conversation_saved(
            learning_client=learning_client,
            agent_name=cleanup_agent,
            make_call=make_llm_call,
            sleep_config=sleep_config,
            expected_content="Alice"
        )

    # ... 3 more tests calling test_runners
```

### Key Fixtures

#### Root Fixtures (`tests/conftest.py`)

- **`learning_client`** - AgenticLearning client (cloud or local)
- **`cleanup_agent`** - Unique agent name with auto-cleanup
- **`sleep_config`** - Configurable sleep durations via env vars

#### Unit-Specific Fixtures (`tests/unit/conftest.py`)

- **`reset_interceptors`** (autouse) - **Critical for test isolation!** Resets interceptor installation flag before each test to ensure interceptors are reinstalled after mock fixtures modify methods.

#### Provider-Specific Fixtures (each `test_*.py`)

**Unit Tests:**
- **`{provider}_client`** - Real SDK client (but HTTP will be mocked)
- **`make_llm_call`** - Function to make mocked API call
- **`httpx_mock`** - pytest-httpx fixture for mocking HTTP

**Integration Tests:**
- **`{provider}_client`** - Real SDK client with real API key
- **`make_llm_call`** - Function to make real API call

### Test Isolation Fix

**Problem**: Interceptors are installed once per process globally. Mock fixtures patch SDK methods and restore them during cleanup, which removes interceptor wrappers. This caused tests run in sequence to fail.

**Solution**: The `reset_interceptors` fixture (autouse) in `tests/unit/conftest.py` resets `_INTERCEPTORS_INSTALLED` flag before each test, forcing interceptor reinstallation:

```python
@pytest.fixture(autouse=True)
def reset_interceptors():
    """Reset interceptor installation state before each test."""
    import agentic_learning.core as core
    original_installed = core._INTERCEPTORS_INSTALLED
    core._INTERCEPTORS_INSTALLED = False  # Force reinstall
    yield
    core._INTERCEPTORS_INSTALLED = original_installed
```

This ensures:
1. Test 1 installs mock → enters learning context → interceptor wraps mock ✅
2. Test 1 cleanup restores method (removes interceptor)
3. Test 2 resets flag → installs new mock → enters learning context → interceptor wraps new mock ✅

### Memory Injection Flow

1. Test creates agent and memory
2. Test sleeps to allow cloud API processing
3. Test enters `learning()` context
4. Interceptor retrieves memory from Letta
5. Interceptor injects memory into LLM kwargs
6. Mock/Real call captures kwargs (now includes memory)
7. Test verifies memory is present in captured kwargs

---

## Test Markers

Use pytest markers to run specific test subsets:

- `-m unit` - All unit tests (real SDK with mocked LLM HTTP)
- `-m integration` - All integration tests (real SDK with real API calls)
- `-m openai` - OpenAI provider tests (both unit and integration)
- `-m anthropic` - Anthropic provider tests (both unit and integration)
- `-m gemini` - Gemini provider tests (both unit and integration)
- `-m openai_responses` - OpenAI Responses API tests (both unit and integration)
- `-m claude` - Claude Agent SDK tests (integration only, async)
- `-m asyncio` - Async tests (Claude)

---

## Performance

Test suite runtimes:

- **Unit tests only**: ~3-4 minutes (16 tests, mocked LLM HTTP, cloud Letta)
- **Integration tests only**: ~5-10 minutes (20 tests, real API calls, all passing)
- **Full suite (unit + integration)**: ~8-14 minutes (36 tests, all passing)

Optimization options:
- **Unit tests**: Use local Letta server (`LETTA_ENV=local`) or reduce sleep times
- **Integration tests**: Use cheaper models (gpt-5, claude-3-5-haiku, etc.) - already configured
- Run specific provider/suite tests only
- Use pytest-xdist for parallel execution: `.venv/bin/python3 -m pytest tests/ -n auto`

---

**Happy Testing!** 🧪

If you encounter issues or have suggestions for improving this test suite, please open an issue or PR on GitHub.
