# Agentic Learning SDK

Add continual learning to any LLM agent with one line of code. This SDK enables agents to learn from every conversation and recall context across sessions—making your agents truly stateful.

```python
from openai import OpenAI
from agentic_learning import learning

client = OpenAI()

with learning(agent="my_agent"):
    response = client.chat.completions.create(...)  # LLM is now stateful!
```

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![npm shield](https://img.shields.io/npm/v/@letta-ai/agentic-learning)](https://www.npmjs.com/package/@letta-ai/agentic-learning)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

## Quick Start

### Python Installation

```bash
pip install agentic-learning
```

### TypeScript Installation

```bash
npm install @letta-ai/agentic-learning
```

### Basic Usage (Python)

```bash
# Set your API keys
export OPENAI_API_KEY="your-openai-key"
export LETTA_API_KEY="your-letta-key"
```

```python
from openai import OpenAI
from agentic_learning import learning

client = OpenAI()

# Add continual learning with one line
with learning(agent="my_assistant"):
    # Your LLM call - conversation is automatically captured
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": "My name is Alice"}]
    )

    # Agent remembers prior context
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": "What's my name?"}]
    )
    # Returns: "Your name is Alice"
```

That's it - this SDK automatically:
- ✅ Learns from every conversation
- ✅ Recalls relevant context when needed
- ✅ Remembers across sessions
- ✅ Works with your existing LLM code

### Basic Usage (TypeScript)

```bash
# Set your API keys
export OPENAI_API_KEY="your-openai-key"
export LETTA_API_KEY="your-letta-key"
```

```typescript
import { learning } from '@letta-ai/agentic-learning';
import OpenAI from 'openai';

const client = new OpenAI();

// Add continual learning with one line
await learning({ agent: "my_assistant" }, async () => {
    // Your LLM call - conversation is automatically captured
    const response = await client.chat.completions.create({
        model: "gpt-5",
        messages: [{ role: "user", content: "My name is Alice" }]
    });

    // Agent remembers prior context
    const response2 = await client.chat.completions.create({
        model: "gpt-5",
        messages: [{ role: "user", content: "What's my name?" }]
    });
    // Returns: "Your name is Alice"
});
```

## Supported Providers

| Provider | Package | Status | Py Example | TS Example |
|----------|---------|--------|------------|------------|
| **Anthropic** | `anthropic` | ✅ Stable | [anthropic_example.py](examples/anthropic_example.py) | [anthropic_example.ts](examples/anthropic_example.ts) |
| **Claude Agent SDK** | `@anthropic-ai/claude-agent-sdk` | ✅ Stable | [claude_example.py](examples/claude_example.py) | [claude_example.ts](examples/claude_example.ts) |
| **OpenAI Chat Completions** | `openai` | ✅ Stable | [openai_example.py](examples/openai_example.py) | [openai_example.ts](examples/openai_example.ts) |
| **OpenAI Responses API** | `openai` | ✅ Stable | [openai_responses_example.py](examples/openai_responses_example.py) | [openai_responses_example.ts](examples/openai_responses_example.ts) |
| **Gemini** | `google-generativeai` | ✅ Stable | [gemini_example.py](examples/gemini_example.py) | [gemini_example.ts](examples/gemini_example.ts) |
| **Vercel AI SDK** | `ai` | ✅ Stable | N/A (TS only) | [vercel_example.ts](examples/vercel_example.ts) |

See [examples/README.md](examples/README.md) for detailed documentation.

## Core Concepts

### Learning Context

Wrap any LLM calls in a `learning()` context to enable continual learning:

```python
with learning(agent="agent_name"):
    # All SDK calls inside this block have learning enabled
    response = llm_client.generate(...)
```

**Note:** Learning is scoped by agent name. Each agent learns independently, so `agent="sales_bot"` and `agent="support_bot"` maintain separate memories.

### Context Injection

The SDK automatically retrieves relevant context from past conversations:

```python
# First session
with learning(agent="sales_bot", memory=["customer"]):
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "I'm interested in Product X"}]
    )

# Later session - agent remembers any information related to "customer"
with learning(agent="sales_bot", memory=["customer"]):
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Tell me more about that product"}]
    )
    # Agent knows you're asking about Product X
```

### Capture-Only Mode

Store conversations without injecting context (useful for logging or background processing):

```python
with learning(agent="agent_name", capture_only=True):
    # Conversations saved for learning but not injected into prompts
    response = client.chat.completions.create(...)

# Later, list entire conversation history
learning_client = AgenticLearning()
messages = learning_client.messages.list("agent_name")
```

### Knowledge Search

Query what your agent has learned with semantic search:

```python
# Search for relevant conversations
messages = learning_client.memory.search(
    agent="agent_name",
    query="What are my project requirements?"
)
```

## How It Works

The SDK uses **automatic interception** of LLM SDK calls:

1. **Intercepts** - Captures conversations automatically
2. **Learns** - Extracts and stores knowledge from interactions
3. **Recalls** - Retrieves relevant context when needed
4. **Injects** - Seamlessly adds context to your prompts

```
┌─────────────────-┐
│     Your Code    │
│  client.create() │
└────────┬────────-┘
         │
         ▼
┌─────────────────-┐
│ Agentic Learning │  ← Intercepts call
│   Interceptor    │  ← Injects context
└────────┬───────-─┘
         │
         ▼
┌───────────────-──┐
│     LLM API      │  ← Sees enriched prompt
│  (OpenAI, etc)   │
└────────┬──────-──┘
         │
         ▼
┌────────────────-─┐
│   Letta Server   │  ← Stores conversation
│  (Persistent DB) │  ← Learning update
└─────────────────-┘
```

## Architecture

### Interceptors

The SDK provides interceptors for different integration patterns:

- **API-Level Interceptors** (OpenAI, Anthropic, Gemini) - Patch HTTP API methods
- **Transport-Level Interceptors** (Claude Agent SDK) - Patch subprocess transport layer

All interceptors share common logic through `BaseAPIInterceptor`, making it easy to add new providers.

### Client Architecture

```python
AgenticLearning()
├── agents          # Agent management
│   ├── create()
│   ├── update()
│   ├── retrieve()
│   ├── list()
│   ├── delete()
│   └── sleeptime   # Background memory processing
├── memory          # Memory block management
│   ├── create()
│   ├── upsert()
│   ├── retrieve()
│   ├── list()
│   ├── search()    # Semantic search
│   ├── remember()  # Store memories
│   └── context     # Memory context retrieval
└── messages        # Message history
    ├── capture()   # Save conversation turn
    ├── list()
    └── create()    # Send message to LLM

```

## Requirements

### Python
- Python 3.9+
- Letta API key (sign up at [letta.com](https://www.letta.com/))
- At least one LLM SDK:
  - `openai>=1.0.0`
  - `anthropic>=0.18.0`
  - `google-generativeai>=0.3.0`
  - `@anthropic-ai/claude-agent-sdk>=0.1.0`

### TypeScript/JavaScript
- Node.js 18+
- Letta API key (sign up at [letta.com](https://www.letta.com/))
- At least one LLM SDK:
  - `openai>=4.0.0`
  - `@anthropic-ai/sdk>=0.30.0`
  - `@google/generative-ai>=0.21.0`
  - `@anthropic-ai/claude-agent-sdk>=0.1.0`
  - `ai>=3.0.0` (Vercel AI SDK)

### Local Development (Optional)

For local development, you can run Letta server locally:

```bash
# Install Letta
pip install letta

# Start server (default: http://localhost:8283)
letta server
```

See [Letta documentation](https://docs.letta.com/) for more details.

## Development Setup

### Python Development

```bash
# Clone repository
git clone https://github.com/letta-ai/agentic_learning_sdk.git
cd agentic_learning_sdk

# Install in development mode
pip install -e python/

# Run tests
cd python
.venv/bin/python3 -m pytest tests/ -v

# Run examples
cd ../examples
python3 openai_example.py
```

### TypeScript Development

```bash
# Clone repository
git clone https://github.com/letta-ai/agentic_learning_sdk.git
cd agentic_learning_sdk/typescript

# Install dependencies
npm install

# Build
npm run build

# Run tests
npm test

# Run examples
cd ../examples
npx tsx openai_example.ts
```

## Advanced Usage

### Custom Letta Server URL

```python
learning_client = AgenticLearning(base_url="http://custom-host:8283")
```

### Agent Configuration

```python
# Create agent with custom memory blocks
agent = learning_client.agents.create(
    agent="my_agent",
    memory=["human", "persona", "project_context"],
    model="anthropic/claude-sonnet-4-20250514"
)

# Create custom memory block
learning_client.memory.create(
    agent="my_agent",
    label="user_preferences",
    value="Prefers concise technical responses"
)
```

### Async Support

```python
from agentic_learning import learning_async, AsyncAgenticLearning

async_client = AsyncAgenticLearning()

async with learning_async(agent="my_agent", client=async_client):
    response = await async_llm_client.generate(...)
```

## Testing

This SDK includes comprehensive test suites for both Python and TypeScript:

### Python Tests
- **36/36 tests passing (100%)**
- Unit tests with mocked LLM HTTP calls
- Integration tests with real API calls
- See [python/tests/README.md](python/tests/README.md) for details

### TypeScript Tests
- **40/40 tests passing (100%)**
- Unit tests with Jest mocks
- Integration tests with real API calls
- See [typescript/tests/README.md](typescript/tests/README.md) for details

Both test suites cover all supported providers and validate:
- ✅ Conversation capture and storage
- ✅ Memory injection into prompts
- ✅ Capture-only mode
- ✅ Interceptor cleanup

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Adding a New Provider

1. Create a new interceptor in `python/src/agentic_learning/interceptors/`
2. Extend `BaseAPIInterceptor` (for API-level) or `BaseInterceptor` (for transport-level)
3. Implement SDK-specific methods:
   - `extract_user_messages()`
   - `extract_assistant_message()`
   - `inject_memory_context()`
   - `_build_response_from_chunks()`
4. Register in `__init__.py`
5. Add example to `examples/`

See existing interceptors for reference implementations.

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

## Links

- 🏠 [Homepage](https://github.com/letta-ai/agentic-learning-sdk)
- 📚 [Examples](examples/)
- 🐛 [Issue Tracker](https://github.com/letta-ai/agentic-learning-sdk/issues)
- 💬 [Letta Discord](https://discord.gg/letta)
- 📖 [Letta Documentation](https://docs.letta.com/)

## Acknowledgments

Built with [Letta](https://www.letta.com/) - the leading platform for building stateful AI agents with long-term memory.
