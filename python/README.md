# Agentic Learning SDK (Python)

Add continual learning to any LLM agent with one line of code. This SDK enables agents to learn from every conversation and recall context across sessions—making your agents truly stateful.

```python
from openai import OpenAI
from agentic_learning import learning

client = OpenAI()

with learning(agent="my_agent"):
    response = client.chat.completions.create(...)  # LLM is now stateful!
```

[![PyPI Version](https://img.shields.io/pypi/v/agentic-learning.svg)](https://pypi.org/project/agentic-learning/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](../LICENSE)
[![Tests](https://img.shields.io/badge/tests-36%2F36%20passing-brightgreen)](tests/)

## Installation

```bash
pip install agentic-learning
```

## Quick Start

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

## Supported Providers

| Provider | Package | Status | Example |
|----------|---------|--------|---------|
| **OpenAI Chat** | `openai>=1.0.0` | ✅ Stable | [openai_example.py](../examples/openai_example.py) |
| **OpenAI Responses** | `openai>=1.0.0` | ✅ Stable | [openai_responses_example.py](../examples/openai_responses_example.py) |
| **Anthropic** | `anthropic>=0.18.0` | ✅ Stable | [anthropic_example.py](../examples/anthropic_example.py) |
| **Claude Agent SDK** | `@anthropic-ai/claude-agent-sdk>=0.1.0` | ✅ Stable | [claude_example.py](../examples/claude_example.py) |
| **Gemini** | `google-generativeai>=0.3.0` | ✅ Stable | [gemini_example.py](../examples/gemini_example.py) |

## Key Features

### Memory Across Sessions
```python
# First session
with learning(agent="sales_bot"):
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "I'm interested in Product X"}]
    )

# Later session - agent remembers automatically
with learning(agent="sales_bot"):
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Tell me more about that product"}]
    )
    # Agent knows you're asking about Product X
```

### Capture-Only Mode
```python
# Store conversations without injecting memory
with learning(agent="my_agent", capture_only=True):
    response = client.chat.completions.create(...)
```

### Knowledge Search
```python
from agentic_learning import AgenticLearning

learning_client = AgenticLearning()

# Search agent's memory
messages = learning_client.memory.search(
    agent="my_agent",
    query="What are my project requirements?"
)
```

## Local Development

### Using Local Letta Server

```python
from agentic_learning import AgenticLearning, learning

# Connect to local server
learning_client = AgenticLearning(base_url="http://localhost:8283")

with learning(agent="my_agent", client=learning_client):
    response = client.chat.completions.create(...)
```

Run Letta locally with Docker:
```bash
docker run \
  -v ~/.letta/.persist/pgdata:/var/lib/postgresql/data \
  -p 8283:8283 \
  -e OPENAI_API_KEY="your_key" \
  letta/letta:latest
```

See the [self-hosting guide](https://docs.letta.com/guides/selfhosting) for more options.

### Development Setup

```bash
# Clone repository
git clone https://github.com/letta-ai/agentic-learning-sdk.git
cd agentic-learning-sdk/python

# Install in development mode
pip install -e .

# Run tests
pytest tests/ -v

# Run specific provider tests
pytest tests/ -m openai -v
pytest tests/ -m anthropic -v
```

## Examples

See the [`examples/`](../examples/) directory for complete working examples:

```bash
cd ../examples
pip install -r requirements.txt
python openai_example.py
```

## Documentation

- 📖 [Full Documentation](../README.md) - Complete SDK documentation
- 🧪 [Test Suite](tests/README.md) - 36/36 tests passing (100%)
- 🎯 [Examples](../examples/README.md) - Working examples for all providers
- 💬 [Letta Discord](https://discord.gg/letta) - Community support
- 📚 [Letta Docs](https://docs.letta.com/) - Letta platform documentation

## Requirements

- Python 3.9+
- Letta API key (sign up at [letta.com](https://www.letta.com/))
- At least one LLM provider SDK

## License

Apache 2.0 - See [LICENSE](../LICENSE) for details.

Built with [Letta](https://www.letta.com/) - the leading platform for building stateful AI agents with long-term memory.
