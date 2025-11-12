# Agentic Learning SDK

Add persistent memory to any LLM agent with one line of code. This Agentic Learning SDK automatically captures conversations, manages context, and enables agents to remember information across sessions.

```python
with learning(agent="my_agent"):
    response = client.chat.completions.create(...)  # Memory handled automatically
```

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![npm shield](https://img.shields.io/npm/v/@letta-ai/agentic-learning)](https://www.npmjs.com/package/@letta-ai/agentic-learning)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

## Features

- **🔌 Drop-in Integration** - Works with Anthropic, Claude Agents SDK, OpenAI (Chat Completions & Responses), and Gemini
- **💾 Persistent Memory** - Conversations automatically saved and recalled across sessions
- **🎯 Zero Configuration** - No prompt engineering or manual context management required
- **⚡ Streaming Support** - Full support for streaming responses
- **🔍 Memory Search** - Query past conversations with semantic search
- **🎛️ Flexible Modes** - Auto-inject memory, capture-only, or hybrid approaches

## Quick Start

### Installation

```bash
pip install agentic-learning
```

### Basic Usage

```bash
# Set your API keys
export OPENAI_API_KEY="your-openai-key"
export LETTA_API_KEY="your-letta-key"
```

```python
from openai import OpenAI
from agentic_learning import learning

client = OpenAI()

# Add memory to your agent with one line
with learning(agent="my_assistant"):
    # Your LLM call - conversation is automatically captured
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": "My name is Alice"}]
    )

    # Agent remembers prior context
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "What's my name?"}]
    )
    # Returns: "Your name is Alice"
```

That's it - this SDK automatically:
- ✅ Captures all conversations
- ✅ Injects relevant memory into prompts
- ✅ Saves to persistent storage (Letta)
- ✅ Recalls information across sessions

## Supported Providers

| Provider | Package | Status | Py Example | TS Example |
|----------|---------|--------|------------|------------|
| **Anthropic** | `anthropic` | ✅ Stable | [anthropic_example.py](examples/anthropic_example.py) | [anthropic_example.ts](examples/anthropic_example.ts) |
| **Claude Agents SDK** | `claude-agent-sdk` | ✅ Stable | [claude_example.py](examples/claude_example.py) | [claude_example.ts](examples/claude_example.ts) |
| **OpenAI Chat Completions** | `openai` | ✅ Stable | [openai_example.py](examples/openai_example.py) | [openai_example.ts](examples/openai_example.ts) |
| **OpenAI Responses API** | `openai` | ✅ Stable | [openai_responses_example.py](examples/openai_responses_example.py) | [openai_responses_example.ts](examples/openai_responses_example.ts) |
| **Gemini** | `google-generativeai` | ✅ Stable | [gemini_example.py](examples/gemini_example.py) | [gemini_example.ts](examples/gemini_example.ts) |
| **Vercel AI SDK** | `ai-sdk` | ✅ Experimental | | [vercel_example.ts](examples/vercel_example.ts) |

See [examples/README.md](examples/README.md) for detailed documentation.

## Core Concepts

### Learning Context

Wrap any LLM calls in a `learning()` context to enable conversation capture and dynamic memory:

```python
with learning(agent="agent_name"):
    # All SDK calls inside this block have memory enabled
    response = llm_client.generate(...)
```

**Note:** Memory is scoped by agent name. Each agent maintains its own isolated memory, so `agent="sales_bot"` and `agent="support_bot"` have separate conversation histories and context.

### Memory Injection

The SDK automatically retrieves relevant memory and injects it into your prompts:

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

Store conversations without injecting memory (useful for logging or background processing):

```python
with learning(agent="agent_name", capture_only=True):
    # Conversations saved but not injected into prompts
    response = client.chat.completions.create(...)

# Later, list entire conversation history
learning_client = AgenticLearning()
messages = learning_client.messages.list("agent_name")
```

### Memory Search

Query past conversations with semantic search:

```python
# Search for relevant conversations
messages = learning_client.memory.search(
    agent="agent_name",
    query="What are my project requirements?"
)
```

## How It Works

The SDK uses **automatic interception** of LLM SDK calls:

1. **Intercepts** - Patches LLM SDK methods to capture conversations
2. **Enriches** - Retrieves relevant memory and injects into prompts
3. **Stores** - Saves conversations to Letta for persistent storage
4. **Recalls** - Automatically loads relevant context in future sessions

```
┌─────────────────-┐
│     Your Code    │
│  client.create() │
└────────┬────────-┘
         │
         ▼
┌─────────────────-┐
│ Agentic Learning │  ← Intercepts call
│   Interceptor    │  ← Injects memory
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
│  (Persistent DB) │  ← Memory update
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

- Python 3.9+
- Letta API key (sign up at [letta.com](https://www.letta.com/))
- At least one LLM SDK:
  - `openai>=1.0.0`
  - `anthropic>=0.18.0`
  - `google-generativeai>=0.3.0`
  - `claude-agent-sdk>=0.1.0`

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

```bash
# Clone repository
git clone https://github.com/letta-ai/agentic_learning_sdk.git
cd agentic_learning_sdk

# Install in development mode
pip install -e python/

# Run examples
cd examples
python3 openai_example.py
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
