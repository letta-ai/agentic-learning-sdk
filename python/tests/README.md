# Agentic Learning SDK - Tests

Lightweight integration tests that verify interceptors work correctly with real Letta server.

## Test Strategy

- **Mock**: LLM SDK calls (OpenAI, Anthropic, Gemini, etc.)
- **Real**: AgenticLearning client calls to Letta server (local or hosted)
- **Focus**: Interceptor mechanics, memory injection, conversation capture

## Setup

```bash
# Install test dependencies
pip install pytest pytest-mock

# Install SDK in development mode (or set PYTHONPATH)
pip install -e python/
# OR
export PYTHONPATH="/path/to/agentic-learning-sdk/python/src:$PYTHONPATH"
```

### Local Server (Default)

```bash
# Start local Letta server in separate terminal
letta server

# Run tests against local server (default)
# From repo root:
pytest python/tests/
# Or from python directory:
cd python && pytest tests/
```

### Cloud Server

```bash
# Set environment variables for cloud testing
export LETTA_TEST_MODE="cloud"
export LETTA_API_KEY="your-letta-api-key"

# Run tests against cloud
pytest python/tests/
```

## Running Tests

```bash
# Run all tests (uses local server by default)
# From repo root:
pytest python/tests/
# Or from python directory:
cd python && pytest tests/

# Run specific provider
pytest python/tests/test_openai.py -v

# Run with more detailed output
pytest python/tests/ -vv -s

# Run with coverage (requires pytest-cov)
pip install pytest-cov
pytest python/tests/ --cov=agentic_learning --cov-report=html
```

## Test Structure

All test logic is defined once in `base_interceptor_tests.py`. Each provider test file only provides provider-specific fixtures:

```
tests/
├── conftest.py                    # Shared fixtures (Letta client, cleanup)
├── base_interceptor_tests.py     # Base test class (all test logic here)
├── test_openai.py                 # OpenAI Chat Completions fixtures
├── test_openai_responses.py       # OpenAI Responses API fixtures
├── test_anthropic.py              # Anthropic fixtures
├── test_gemini.py                 # Gemini fixtures
└── test_claude.py                 # Claude SDK (skipped - async only)
```

## Test Cases

Each provider runs the same 5 tests:

1. **test_conversation_saved_to_letta** - Verify conversations captured and saved
2. **test_memory_injection** - Verify memory retrieved and injected into LLM calls
3. **test_capture_only_mode** - Verify capture_only doesn't inject memory
4. **test_memory_injection_with_existing_system_message** - Verify memory merges with system messages
5. **test_interceptor_cleanup** - Verify interceptor properly installed/uninstalled

## Adding Tests for New Providers

To add tests for a new provider:

1. Create `tests/test_<provider>.py`
2. Import `BaseInterceptorTests` from `base_interceptor_tests.py`
3. Define provider-specific fixtures:
   - `mock_llm_client` - Mocked LLM client
   - `mock_llm_response` - Mock response object
   - `make_llm_call` - Function to make LLM calls
   - `make_llm_call_with_system` - Function to make calls with system messages
   - `get_captured_kwargs` - Function to retrieve captured kwargs
4. Create test class that inherits from `BaseInterceptorTests`

See existing test files for examples.

## Notes

- Tests use real Letta server (reliable hosted service)
- Each test uses a unique agent name to avoid conflicts
- Test agents are automatically cleaned up after tests
- LLM calls are mocked to avoid API costs and ensure determinism
- Async tests skipped for now (Claude SDK only supports async)
